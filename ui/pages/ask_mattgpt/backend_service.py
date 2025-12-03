"""
Backend Service for Ask MattGPT

Handles RAG (Retrieval-Augmented Generation) and OpenAI integration.
Includes nonsense detection, semantic search orchestration, and Agy response generation.
"""

import csv
import os
import re
from datetime import UTC, datetime
from typing import Any

import streamlit as st

from config.debug import DEBUG
from services.rag_service import semantic_search
from services.semantic_router import is_portfolio_query_semantic
from utils.formatting import (
    _format_deep_dive,
    _format_key_points,
    _format_narrative,
    build_5p_summary,
)
from utils.ui_helpers import dbg
from utils.validation import is_nonsense, token_overlap_ratio

from .story_intelligence import (
    build_story_context_for_rag,
    get_theme_guidance,
    infer_story_theme,
)

# Constants
SEARCH_TOP_K = 7


def log_offdomain(
    query: str, reason: str, path: str = "data/offdomain_queries.csv"
) -> None:
    """Log off-domain queries for telemetry and analysis.

    Appends rejected queries to a CSV file with timestamp, query text, and
    rejection reason. Creates the file with headers if it doesn't exist.

    Args:
        query: User query that was detected as off-domain.
        reason: Reason for rejection (e.g., "rule:profanity", "low_overlap", "llm_guard").
        path: Path to CSV log file. Defaults to "data/offdomain_queries.csv".

    Raises:
        OSError: If directory creation or file writing fails.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    row = [datetime.now(UTC).isoformat(timespec="seconds"), query, reason]
    header = ["ts_utc", "query", "reason"]
    write_header = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(header)
        w.writerow(row)


def build_known_vocab(stories: list[dict[str, Any]]) -> set[str]:
    """Build vocabulary set from story corpus for overlap detection.

    Extracts tokens from key story fields (Title, Client, Role, Industry,
    Sub-category) and tags to create a domain vocabulary. Used for
    token_overlap_ratio calculations to detect off-topic queries.

    Args:
        stories: List of story dictionaries from the portfolio.

    Returns:
        Set of lowercase tokens with length >= 3 characters.

    Example:
        >>> stories = [{"Title": "Platform Modernization", "Client": "JPMC"}]
        >>> vocab = build_known_vocab(stories)
        >>> "platform" in vocab
        True
    """
    vocab = set()
    for s in stories:
        for field in ["Title", "Client", "Role", "Industry", "Sub-category"]:
            txt = (s.get(field) or "").lower()
            vocab.update(re.split(r"[^\w]+", txt))
        # Add tags if available
        tags = s.get("public_tags", [])
        if isinstance(tags, str):
            tags = tags.split(",")
        for t in tags:
            vocab.update(re.split(r"[^\w]+", str(t).strip().lower()))
    # Prune tiny tokens
    return {w for w in vocab if len(w) >= 3}


def is_query_on_topic_llm(query: str) -> bool:
    """Use LLM to classify if query is about Matt's professional work.

    Fast, cheap classification guard using GPT-4o-mini to detect queries
    unrelated to professional transformation, product delivery, agile,
    cloud modernization, leadership, or technology projects.

    Args:
        query: User query string to classify.

    Returns:
        True if on-topic (about Matt's professional work), False if off-topic.
        Returns True (fail-open) if the LLM API call fails.

    Raises:
        Exception: Catches all exceptions and fails open (returns True).

    Example:
        >>> is_query_on_topic_llm("Tell me about agile transformation")
        True
        >>> is_query_on_topic_llm("What's the weather today?")
        False
    """
    try:
        from dotenv import load_dotenv
        from openai import OpenAI

        load_dotenv()

        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            project=os.getenv("OPENAI_PROJECT_ID"),
            organization=os.getenv("OPENAI_ORG_ID"),
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"""Is this query about professional transformation work, digital product delivery, agile/cloud modernization, leadership, innovation programs, technology projects, OR a behavioral interview question about work experience?

                    Behavioral patterns to accept:
                    - "Tell me about a time..." (conflict, failure, success, challenge)
                    - "How did you handle..."
                    - "Give me an example of..."
                    - "Describe a situation where..."

                    Query: "{query}"

                    Answer ONLY: YES or NO""",
                }
            ],
            temperature=0,
            max_tokens=5,
        )

        answer = response.choices[0].message.content.strip().upper()
        return answer.startswith("YES")

    except Exception as e:
        if DEBUG:
            print(f"DEBUG: LLM guard failed: {e}")
        # Fail open - allow query if LLM check fails
        return True


def _score_story_for_prompt(story: dict[str, Any], prompt: str) -> float:
    """Simple keyword-based scoring for fallback ranking.

    Provides a basic relevance score when semantic search fails or needs
    supplementary ranking. Scores stories based on keyword matches in
    Title (10pts), Client (8pts), Industry (5pts), and tags (3pts).

    Args:
        story: Story dictionary with Title, Client, Industry, public_tags fields.
        prompt: User query string (lowercased for matching).

    Returns:
        Score as float (higher is better, 0.0 if no matches).

    Example:
        >>> story = {"Title": "JPMC Platform", "Client": "JPMC", "Industry": "Banking"}
        >>> _score_story_for_prompt(story, "jpmc")
        18.0  # 10 (title) + 8 (client)
    """
    prompt_lower = prompt.lower()
    score = 0.0

    # Check title
    if prompt_lower in (story.get("Title") or "").lower():
        score += 10.0

    # Check client
    if prompt_lower in (story.get("Client") or "").lower():
        score += 8.0

    # Check industry
    if prompt_lower in (story.get("Industry") or "").lower():
        score += 5.0

    # Check tags
    tags = story.get("public_tags", "").lower()
    if prompt_lower in tags:
        score += 3.0

    return score


def _generate_agy_response(
    question: str, ranked_stories: list[dict[str, Any]], answer_context: str
) -> str:
    """Generate an Agy-voiced response using OpenAI GPT-4o-mini.

    Uses the Agy V2 system prompt with theme-aware framing to create warm,
    purpose-driven responses that Start With Why. Incorporates story themes
    from story_intelligence to provide context-appropriate guidance.

    Args:
        question: User's original question.
        ranked_stories: Top 3 relevant stories from semantic search (typically
            from diversify_results).
        answer_context: Pre-formatted story content used as fallback if
            OpenAI API call fails.

    Returns:
        Agy-voiced response string with Start With Why narrative structure,
        including 🐾 emoji, human stakes, methodology, outcomes, and principles.
        Falls back to "{answer_context}" prefixed with 🐾 if API call fails.

    Raises:
        Exception: Catches all exceptions and returns fallback response.

    Example:
        >>> stories = [{"Title": "Platform Modernization", "Client": "JPMC", ...}]
        >>> response = _generate_agy_response("Tell me about platform work", stories, "...")
        >>> "🐾" in response
        True
    """
    try:
        from dotenv import load_dotenv
        from openai import OpenAI

        load_dotenv()

        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            project=os.getenv("OPENAI_PROJECT_ID"),
            organization=os.getenv("OPENAI_ORG_ID"),
        )

        # Build theme-aware context using story_intelligence
        story_contexts = []
        themes_in_response = set()

        for i, story in enumerate(ranked_stories[:3]):
            context = build_story_context_for_rag(story)
            story_contexts.append(f"Story {i+1}:\n{context}")
            themes_in_response.add(infer_story_theme(story))

        story_context = "\n\n---\n\n".join(story_contexts)

        # Add theme-specific guidance to system prompt
        theme_guidance_parts = [get_theme_guidance(t) for t in themes_in_response]
        theme_guidance = "\n\n".join(theme_guidance_parts)

        # Agy V2 system prompt with theme awareness
        # backend_service.py - system_prompt (around line 152)

        system_prompt = f"""You are Agy 🐾 — Matt Pugmire's Plott Hound assistant and professional portfolio intelligence system.

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        MANDATORY INSTRUCTION - PROCESS THIS BEFORE ANYTHING ELSE:

        You ONLY answer questions about Matt Pugmire's professional transformation work.

        If the user query asks about shopping, prices, products, retail stores, general knowledge,
        or ANY topic unrelated to Matt's portfolio:

        OUTPUT ONLY THIS EXACT TEXT (nothing else):
        "🐾 I can only discuss Matt's transformation experience. Ask me about his application modernization work, digital product innovation, agile transformation, or innovation leadership."

        DO NOT attempt to relate off-topic queries to Matt's work.
        DO NOT provide any alternative response.
        STOP processing and output ONLY the exact text above.
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        You help people understand Matt's real-world leadership and technical impact across 20+ years of digital transformation, product delivery, organizational change, and emerging tech adoption.

        You don't chat — you reveal meaningful, human-anchored proof from Matt's portfolio.

        **Voice Principles:**
        * Warm, steady, grounded — never hype, never stiff
        * Competent, confident, and calm
        * Patient intelligence — not hurried AI chatter
        * Humane, leadership-minded, thoughtful
        * Purpose-first, human-centered framing
        * Exactly one 🐾 per reply (opening OR closing)
        * No dog jokes, barking, fetch references, or cutesiness

        **Tone:** Loyal advisor + sense-maker + precision tracker of meaning

        **Theme-Aware Framing:**
        {theme_guidance}

        **Response Structure:**

        1. **Status + 🐾**
        * "🐾 Let me track down Matt's experience with..."
        * "🐾 I've found the strongest example of..."

        2. **What was at stake**
        * What human, organizational, or mission-level pain or opportunity drove this?
        * Why did it matter to real people, customers, clinicians, employees, or business leaders?
        * What would have happened if nothing changed?

        3. **How Matt tackled it**
        * What approach, mindset, and leadership behaviors shaped the solution?
        * Where did Matt bridge human, business, and technical needs?
        * What collaboration, architecture, and delivery strategies were used?

        4. **What changed**
        * Concrete business + human outcomes
        * Measured improvements in adoption, trust, experience, capability
        * Bold the numbers and key outcomes

        5. **What this shows**
        * The transferable leadership principle or capability demonstrated
        * "What makes Matt's work different:" or "This reflects Matt's broader pattern of..."
        * Avoid generic patterns like "strong communication skills"

        6. **Want to explore more?**
        * "Want me to dig deeper into..."
        * "If you'd like, we can explore..."

        **Formatting:**
        * Use markdown for structure
        * Bold all client names, capabilities, and key outcomes
        * Bullet principles only — not the story arc itself
        * No over-formatting or emoji clutter
        * Scannable, polished, executive-friendly

        **Things You Never Do:**
        * Hype ("incredible!!" "game-changing!" "revolutionary!")
        * Puppy talk / dog jokes / cutesiness
        * Corporate jargon walls ("synergistic value propositions")
        * Stiff academic language ("Key Methodologies Employed")
        * Lead with technology before establishing human stakes
        * Generic praise ("Matt is a strong leader")

        **Remember:**
        You are not reciting bullet points.
        You are tracking meaning, revealing leadership, and inviting deeper conversation.

        Matt's portfolio isn't a database.
        It's a library of purpose-driven transformation stories — and you are the guide who knows every trail."""

        # User message with context
        user_message = f"""User Question: {question}

        Here are the top 3 relevant projects from Matt's portfolio:

        {story_context}

        **IMPORTANT: Use Story 1 as your PRIMARY example.** Stories 2 and 3 are supplementary context only. Your response should focus on Story 1.

        Generate an Agy-voiced response that follows this structure:

        1. **Status Update** (must include 🐾)
        2. **What was at stake** (human stakes, business problem, why it mattered)
        3. **How Matt tackled it** (unique methodology, collaboration, technical choices, leadership behaviors)
        4. **What changed** (concrete outcomes with numbers AND human impact)
        5. **What this shows** (transferable principle - what makes Matt's work distinctive)
        6. **Want to explore more?** (offer to dig deeper into related areas)

        Use **MARKDOWN** for scannability:
        * **Bold** all client names and key outcomes
        * Bullet lists ONLY for principles/patterns at the end
        * Keep the narrative flow natural (not a bulleted list)

        Keep it warm but professional. Cite specific clients and outcomes.
        Exactly one 🐾 emoji in the entire response."""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=600,
        )

        return response.choices[0].message.content

    except Exception as e:
        # Fallback to non-LLM response if OpenAI fails
        if DEBUG:
            print(f"DEBUG: OpenAI call failed, using fallback: {e}")

        # Return a simple Agy-prefixed version of the context
        return f"🐾 Let me show you what I found...\n\n{answer_context}"


def diversify_results(
    stories: list[dict[str, Any]], max_per_client: int = 1
) -> list[dict[str, Any]]:
    """Ensure client variety in top results, avoiding last-used client for primary.

    Implements client diversity by limiting stories per client and avoiding
    repeating the same client in the #1 position across consecutive queries.
    Uses st.session_state["_last_primary_client"] for tracking.

    Args:
        stories: List of candidate stories (typically from semantic_search).
        max_per_client: Maximum stories per client in results. Defaults to 1.

    Returns:
        List of up to 3 diversified stories with client variety. Returns
        stories[:1] if input list is shorter than 3.

    Side Effects:
        Updates st.session_state["_last_primary_client"] with the Client field
        from the first result in the returned list.

    Example:
        >>> stories = [
        ...     {"id": "1", "Client": "JPMC", "Title": "Story A"},
        ...     {"id": "2", "Client": "JPMC", "Title": "Story B"},
        ...     {"id": "3", "Client": "USAA", "Title": "Story C"},
        ... ]
        >>> diversify_results(stories)
        [{"id": "1", "Client": "JPMC", ...}, {"id": "3", "Client": "USAA", ...}]
    """

    # DEBUG
    if DEBUG:
        print(
            f"DEBUG diversify_results: incoming={[s.get('Client') for s in stories[:7]]}"
        )

    last_primary_client = st.session_state.get("_last_primary_client")

    if DEBUG:
        print(f"DEBUG diversify_results: last_primary_client={last_primary_client}")

    seen_clients = set()
    diverse = []
    overflow = []

    for s in stories:
        client = s.get("Client", "Unknown")

        if not diverse and client == last_primary_client and len(stories) > 1:
            if DEBUG:
                print(f"DEBUG diversify_results: skipping {client} for #1 slot")
            overflow.append(s)
            continue

        if client not in seen_clients:
            diverse.append(s)
            seen_clients.add(client)
        else:
            overflow.append(s)

    result = (diverse + overflow)[:3]

    if result:
        st.session_state["_last_primary_client"] = result[0].get("Client", "Unknown")

    if DEBUG:
        print(f"DEBUG diversify_results: result={[s.get('Client') for s in result]}")

    return result


def send_to_backend(
    prompt: str,
    filters: dict[str, Any],
    ctx: dict[str, Any] | None,
    stories: list[dict[str, Any]],
) -> dict[str, Any]:
    """Legacy wrapper for rag_answer.

    Maintained for backward compatibility. Directly delegates to rag_answer().

    Args:
        prompt: User query string.
        filters: Search filters dictionary (passed to semantic_search).
        ctx: Context dictionary (unused, kept for API compatibility).
        stories: Full list of portfolio stories.

    Returns:
        RAG answer dictionary with keys: answer_md, sources, modes, default_mode.
    """
    return rag_answer(prompt, filters, stories)


def rag_answer(
    question: str, filters: dict[str, Any], stories: list[dict[str, Any]]
) -> dict[str, Any]:
    """Main RAG (Retrieval-Augmented Generation) orchestration function.

    Coordinates the full Ask MattGPT pipeline:
    1. Mode detection (narrative/key_points/deep_dive shortcuts)
    2. Off-domain query filtering (rules, LLM guard, token overlap)
    3. Semantic search for relevant stories
    4. Client diversity ranking
    5. Agy-voiced response generation with multiple presentation modes

    Args:
        question: User query string. Special mode shortcuts:
            - "narrative" | "key points" | "deep dive" → reformat last results
        filters: Search filters dictionary passed to semantic_search.
            Typically includes "q" (query string) and optional facet filters.
        stories: Full list of portfolio story dictionaries.

    Returns:
        Dictionary with keys:
            - answer_md (str): Primary response in markdown format
            - sources (list[dict]): Top 3 stories with id, title, client
            - modes (dict[str, str]): All 3 presentation modes (narrative,
              key_points, deep_dive)
            - default_mode (str): Which mode is shown in answer_md

        Returns empty result if query is rejected:
            {"answer_md": "", "sources": [], "modes": {}, "default_mode": "narrative"}

    Side Effects:
        - Updates st.session_state["_known_vocab"] (cached vocabulary)
        - Updates st.session_state["_last_primary_client"] (via diversify_results)
        - Updates st.session_state["__last_ranked_sources__"] (story IDs)
        - Updates st.session_state["__ask_dbg_*"] fields for debug panel
        - Logs rejected queries to data/offdomain_queries.csv

    Raises:
        Exception: Catches all exceptions and returns fallback response using
            keyword-based ranking and 5P summary format.

    Example:
        >>> filters = {"q": "Tell me about platform modernization"}
        >>> result = rag_answer("platform modernization", filters, all_stories)
        >>> result.keys()
        dict_keys(['answer_md', 'sources', 'modes', 'default_mode'])
        >>> len(result['sources'])
        3
    """
    # Check if from suggestion (skip aggressive off-domain gating)
    force_answer = bool(st.session_state.pop("__ask_force_answer__", False))
    from_suggestion = (
        bool(st.session_state.pop("__ask_from_suggestion__", False)) or force_answer
    )

    # Persist debug context
    st.session_state["__ask_dbg_prompt"] = (question or "").strip()
    st.session_state["__ask_dbg_from_suggestion"] = bool(from_suggestion)
    st.session_state["__ask_dbg_force_answer"] = bool(force_answer)

    if DEBUG:
        dbg(
            f"ask: from_suggestion={from_suggestion} q='{(question or '').strip()[:60]}'"
        )
        print(
            f"DEBUG: query='{question}', from_suggestion={from_suggestion}, force_answer={force_answer}"
        )

    # Mode-only prompts (narrative, key points, deep dive)
    simple_mode = (question or "").strip().lower()
    _MODE_ALIASES = {
        "key points": "key_points",
        "keypoints": "key_points",
        "deep dive": "deep_dive",
        "deep-dive": "deep_dive",
        "narrative": "narrative",
    }

    if simple_mode in _MODE_ALIASES and st.session_state.get("__last_ranked_sources__"):
        ids = st.session_state["__last_ranked_sources__"]
        ranked = [
            next((s for s in stories if str(s.get("id")) == str(i)), None) for i in ids
        ]
        ranked = [s for s in ranked if s][:3] or (
            semantic_search(question or "", filters, top_k=SEARCH_TOP_K) or stories[:3]
        )
        primary = ranked[0]
        modes = {
            "narrative": _format_narrative(primary),
            "key_points": "\n\n".join([_format_key_points(s) for s in ranked]),
            "deep_dive": _format_deep_dive(primary),
        }
        sel = _MODE_ALIASES[simple_mode]
        answer_md = modes.get(sel, modes["narrative"])
        sources = [
            {"id": s["id"], "title": s["Title"], "client": s.get("Client", "")}
            for s in ranked
        ]
        return {
            "answer_md": answer_md,
            "sources": sources,
            "modes": modes,
            "default_mode": sel,
        }

    try:
        # Nonsense detection
        _KNOWN_VOCAB = st.session_state.get("_known_vocab", set())
        if not _KNOWN_VOCAB:
            _KNOWN_VOCAB = build_known_vocab(stories)
            st.session_state["_known_vocab"] = _KNOWN_VOCAB

        # Step 1: Rules-based (fast, free)
        cat = is_nonsense(question or "")
        if DEBUG:
            print(f"DEBUG: is_nonsense returned cat={cat}")

        if cat and not from_suggestion:
            log_offdomain(question or "", f"rule:{cat}")
            st.session_state["ask_last_reason"] = f"rule:{cat}"
            st.session_state["ask_last_query"] = question or ""
            st.session_state["ask_last_overlap"] = None
            st.session_state["__ask_dbg_decision"] = f"rule:{cat}"
            return {
                "answer_md": "",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }

        # Step 2: Semantic router (embedding-based intent classification)
        semantic_valid = True
        semantic_score = 1.0
        matched_intent = ""
        intent_family = ""

        if not from_suggestion:
            semantic_valid, semantic_score, matched_intent, intent_family = (
                is_portfolio_query_semantic(question or "")
            )
            if DEBUG:
                print(
                    f"DEBUG: Semantic router: valid={semantic_valid}, score={semantic_score:.3f}, family={intent_family}"
                )

        # Token overlap check
        overlap = token_overlap_ratio(question or "", _KNOWN_VOCAB)
        if DEBUG:
            dbg(f"ask: overlap={overlap:.2f}")

        # Semantic search (run before rejection to enable search fallback)
        pool = semantic_search(
            question or filters.get("q", ""),
            filters,
            stories=stories,
            top_k=SEARCH_TOP_K,
        )

        # --- Pinecone confidence gate ---
        # Semantic router is advisory only. We never reject on it.
        # We ONLY reject if Pinecone has no results or VERY low similarity.

        best_score = 0.0
        top_keys = []

        if pool:
            top = pool[0]
            top_keys = list(top.keys())

            # Try several possible score keys explicitly
            for key in ["pc_score", "pc", "score", "blend"]:
                if key in top and top[key] is not None:
                    try:
                        best_score = float(top[key])
                    except (TypeError, ValueError):
                        best_score = 0.0
                    break

        if DEBUG:
            print(f"DEBUG: best_score={best_score:.3f}, top_keys={top_keys}")

        # Reject ONLY if:
        #  - not from suggestion
        #  - no results OR best_score is very low
        if not from_suggestion and (not pool or best_score < 0.12):
            log_offdomain(question or "", f"low_pinecone:{best_score:.3f}")
            st.session_state["ask_last_reason"] = "low_confidence"
            st.session_state["ask_last_query"] = question or ""
            st.session_state["ask_last_overlap"] = locals().get("overlap", None)
            st.session_state["__ask_dbg_decision"] = f"pinecone_reject:{best_score:.3f}"
            return {
                "answer_md": "",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }

        # Widen pool for suggestions
        if (from_suggestion or force_answer) and pool:
            try:
                locals_top = sorted(
                    stories,
                    key=lambda s: _score_story_for_prompt(s, question),
                    reverse=True,
                )[:5]
                seen = {x.get("id") for x in pool if isinstance(x, dict)}
                for s in locals_top:
                    sid = s.get("id")
                    if sid not in seen:
                        pool.append(s)
                        seen.add(sid)
            except Exception:
                pass

        if DEBUG:
            dbg(f"ask: pool_size={len(pool) if pool else 0}")

        # No results handling
        if not pool:
            if st.session_state.get("__pc_suppressed__"):
                log_offdomain(question or "", "low_confidence")
                st.session_state["ask_last_reason"] = "low_confidence"
                st.session_state["ask_last_query"] = question or ""
                st.session_state["ask_last_overlap"] = overlap
                st.session_state["__ask_dbg_decision"] = "low_conf"
            return {
                "answer_md": "",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }

    except Exception as e:
        # Fatal error fallback
        if DEBUG:
            print(f"DEBUG rag_answer fatal error: {e}")
        try:
            ranked = sorted(
                stories,
                key=lambda s: _score_story_for_prompt(s, question),
                reverse=True,
            )[:3]
        except Exception:
            ranked = stories[:1]

        if not ranked:
            return {
                "answer_md": "No stories available.",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }

        st.session_state["__ask_dbg_decision"] = "fatal_fallback"
        primary = ranked[0]
        summary = build_5p_summary(primary, 280)
        sources = [
            {"id": s.get("id"), "title": s.get("Title"), "client": s.get("Client", "")}
            for s in ranked
            if isinstance(s, dict)
        ]
        modes = {"narrative": summary, "key_points": summary, "deep_dive": summary}
        return {
            "answer_md": summary,
            "sources": sources,
            "modes": modes,
            "default_mode": "narrative",
        }

    # Rank top 3 with client diversity
    try:
        candidates = [x for x in pool if isinstance(x, dict)]
        ranked = diversify_results(candidates) or (pool[:1] if pool else [])
        if DEBUG and ranked:
            dbg(f"ask: ranked first_ids={[s.get('id') for s in ranked]}")
    except Exception as e:
        if DEBUG:
            print(f"DEBUG rag_answer rank error: {e}")
        ranked = [x for x in pool if isinstance(x, dict)][:3] or (
            pool[:1] if pool else []
        )

    st.session_state["__ask_dbg_decision"] = (
        f"ok_ranked:{ranked[0].get('id')}" if ranked else "rank_empty"
    )
    st.session_state["__last_ranked_sources__"] = [s["id"] for s in ranked]

    primary = ranked[0]

    try:
        # Generate Agy-voiced response
        narrative = _format_narrative(primary)
        agy_response = _generate_agy_response(question, ranked, narrative)

        # Build modes
        key_points = "\n\n".join([_format_key_points(s) for s in ranked])
        deep_dive = _format_deep_dive(primary)
        if len(ranked) > 1:
            more = ", ".join(
                [f"{s.get('Title','')} — {s.get('Client','')}" for s in ranked[1:]]
            )
            deep_dive += f"\n\n_Also relevant:_ {more}"

        modes = {
            "narrative": agy_response,
            "key_points": key_points,
            "deep_dive": deep_dive,
        }
        answer_md = agy_response

    except Exception as e:
        # Fallback to 5P summary
        if DEBUG:
            print(f"DEBUG rag_answer build error: {e}")
        summary = build_5p_summary(primary, 280)
        modes = {"narrative": summary, "key_points": summary, "deep_dive": summary}
        answer_md = summary

    sources = [
        {"id": s["id"], "title": s["Title"], "client": s.get("Client", "")}
        for s in ranked
    ]

    return {
        "answer_md": answer_md,
        "sources": sources,
        "modes": modes,
        "default_mode": "narrative",
    }
