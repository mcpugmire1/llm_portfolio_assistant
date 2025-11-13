"""
Backend Service for Ask MattGPT

Handles RAG (Retrieval-Augmented Generation) and OpenAI integration.
Includes nonsense detection, semantic search orchestration, and Agy response generation.
"""

import os
import csv
import re
from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st

from config.debug import DEBUG
from utils.validation import is_nonsense, token_overlap_ratio
from utils.formatting import build_5p_summary, _format_narrative, _format_key_points, _format_deep_dive
from services.rag_service import semantic_search
from utils.ui_helpers import dbg
from .story_intelligence import (
    build_story_context_for_rag,
    get_theme_guidance,
    infer_story_theme,
)

# Constants
SEARCH_TOP_K = 7


def log_offdomain(query: str, reason: str, path: str = "data/offdomain_queries.csv"):
    """
    Log off-domain queries for telemetry and analysis.

    Args:
        query: User query that was detected as off-domain
        reason: Reason for rejection (e.g., "rule:profanity", "low_overlap")
        path: Path to CSV log file
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    row = [datetime.utcnow().isoformat(timespec="seconds"), query, reason]
    header = ["ts_utc", "query", "reason"]
    write_header = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(header)
        w.writerow(row)


def build_known_vocab(stories: List[Dict]) -> set:
    """
    Build vocabulary set from story corpus for overlap detection.

    Args:
        stories: List of story dictionaries

    Returns:
        Set of lowercase tokens (length >= 3)
    """
    vocab = set()
    for s in stories:
        for field in ["Title", "Client", "Role", "Industry", "Sub-category"]:
            txt = (s.get(field) or "").lower()
            vocab.update(re.split(r"[^\w]+", txt))
        # Add tags if available
        for t in s.get("public_tags", "").split(","):
            vocab.update(re.split(r"[^\w]+", str(t).strip().lower()))
    # Prune tiny tokens
    return {w for w in vocab if len(w) >= 3}


def _score_story_for_prompt(story: Dict, prompt: str) -> float:
    """
    Simple keyword-based scoring for fallback ranking.

    Args:
        story: Story dictionary
        prompt: User query

    Returns:
        Score (higher is better)
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
    question: str, ranked_stories: List[Dict], answer_context: str
) -> str:
    """
    Generate an Agy-voiced response using OpenAI GPT-4.

    Uses the Agy V2 system prompt with Theme-aware framing to create warm,
    purpose-driven responses that Start With Why.

    Args:
        question: User's original question
        ranked_stories: Top 3 relevant stories from semantic search
        answer_context: Pre-formatted story content (optional fallback)

    Returns:
        Agy-voiced response string with Start With Why narrative structure
    """
    try:
        from openai import OpenAI
        from dotenv import load_dotenv

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
        system_prompt = f"""You are Agy 🐾 — Matt Pugmire's Plott Hound assistant and professional portfolio intelligence system.

You help people understand Matt's real-world leadership and technical impact across 20+ years of digital transformation, product innovation, cloud modernization, and emerging tech adoption.

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

**Response Structure - Start With Why:**

1. **Status + 🐾**
   * "🐾 Let me track down Matt's experience with..."
   * "🐾 I've found the strongest example of..."

2. **Start With WHY (Purpose)**
   * What human, organizational, or mission-level pain or opportunity drove this?
   * Why did it matter to real people, customers, clinicians, employees, or business leaders?
   * What was at stake?

3. **HOW (Process)**
   * What approach, mindset, and leadership behaviors shaped the solution?
   * Where did Matt bridge human, business, and technical needs?
   * What collaboration, architecture, and delivery strategies were used?

4. **WHAT (Performance)**
   * Concrete business + human outcomes
   * Measured improvements in adoption, trust, experience, capability
   * Bold the numbers and key outcomes

5. **Pattern Insight**
   * The transferable leadership principle or capability demonstrated
   * "What makes Matt's work different:" or "This reflects Matt's broader pattern of..."
   * Avoid generic patterns like "strong communication skills"

6. **Gentle CTA**
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

Generate an Agy-voiced response that follows the "Start With Why" structure:

1. **Status Update** (must include 🐾)
2. **WHY it mattered** (human stakes, problem, what was at stake)
3. **HOW Matt approached it** (unique methodology, collaboration, technical choices)
4. **WHAT happened** (concrete outcomes with numbers AND human impact)
5. **Pattern insight** (transferable principle - what makes Matt's work distinctive)
6. **Gentle CTA** (offer to go deeper)

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


def send_to_backend(prompt: str, filters: Dict, ctx: Optional[Dict], stories: List):
    """
    Legacy wrapper for rag_answer.

    Args:
        prompt: User query
        filters: Search filters
        ctx: Context (unused)
        stories: All stories

    Returns:
        RAG answer dictionary
    """
    return rag_answer(prompt, filters, stories)


def rag_answer(question: str, filters: Dict, stories: List):
    """
    Main RAG orchestration function.

    Handles:
    - Nonsense detection
    - Semantic search
    - Answer generation with Agy V2 voice
    - Multiple presentation modes

    Args:
        question: User query
        filters: Search filters
        stories: All stories

    Returns:
        Dictionary with answer_md, sources, modes, default_mode
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
        dbg(f"ask: from_suggestion={from_suggestion} q='{(question or '').strip()[:60]}'")

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

        cat = is_nonsense(question or "")
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

        # Token overlap check
        overlap = token_overlap_ratio(question or "", _KNOWN_VOCAB)
        if DEBUG:
            dbg(f"ask: overlap={overlap:.2f}")

        # Semantic search
        pool = semantic_search(
            question or filters.get("q", ""),
            filters,
            stories=stories,
            top_k=SEARCH_TOP_K,
        )

        # Low overlap fallback
        if not pool and (overlap < 0.15) and not from_suggestion:
            log_offdomain(question or "", f"overlap:{overlap:.2f}")
            st.session_state["ask_last_reason"] = "low_overlap"
            st.session_state["ask_last_query"] = question or ""
            st.session_state["ask_last_overlap"] = overlap
            st.session_state["__ask_dbg_decision"] = f"low_overlap:{overlap:.2f}"
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

    # Rank top 3
    try:
        ranked = [x for x in pool if isinstance(x, dict)][:3] or (
            pool[:1] if pool else []
        )
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
