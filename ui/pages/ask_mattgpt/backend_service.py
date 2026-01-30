"""
Backend Service for Ask MattGPT

Handles RAG (Retrieval-Augmented Generation) and OpenAI integration.
Includes nonsense detection, semantic search orchestration, and Agy response generation.
"""

import csv
import os
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from typing import Any

import streamlit as st

from config.constants import (
    ENTITY_DETECTION_FIELDS,
    EXCLUDED_DIVISION_VALUES,
    META_COMMENTARY_REGEX_PATTERNS,
    SEARCH_TOP_K,
)
from config.debug import DEBUG
from services.pinecone_service import (
    PINECONE_NAMESPACE,
    _embed,
    _init_pinecone,
)
from services.rag_service import semantic_search
from services.semantic_router import is_portfolio_query_semantic
from utils.client_utils import is_generic_client
from utils.formatting import (
    _format_deep_dive,
    _format_key_points,
    _format_narrative,
    build_5p_summary,
)
from utils.ui_helpers import dbg
from utils.validation import is_nonsense, token_overlap_ratio

from .prompts import (
    build_system_prompt,
    build_user_message,
    get_verbatim_requirement,
)
from .story_intelligence import (
    build_story_context_for_rag,
    infer_story_theme,
)

# SEARCH_TOP_K imported from config.constants

# Clients to exclude from dynamic client list (not real named clients)
# Known clients - derived dynamically from story data at startup
_KNOWN_CLIENTS: set[str] | None = None


class RateLimitError(Exception):
    """Raised when OpenAI rate limit is hit. Caller should suppress sources."""

    pass


def get_known_clients(stories: list[dict]) -> set[str]:
    """Derive known client names from story data for post-processing bolding.

    Uses pattern-based is_generic_client() to filter out generic values like
    'Fortune 500 Clients', 'Independent Project', etc.
    """
    global _KNOWN_CLIENTS
    if _KNOWN_CLIENTS is None:
        _KNOWN_CLIENTS = {
            s.get("Client")
            for s in stories
            if s.get("Client") and not is_generic_client(s.get("Client"))
        }
    return _KNOWN_CLIENTS


# Cache for narrative titles
_NARRATIVE_TITLES: list[str] | None = None


def get_narrative_titles(stories: list[dict]) -> list[str]:
    """Derive Professional Narrative story titles for intent classification.

    Returns titles of stories where Theme='Professional Narrative'.
    These are used to detect biographical/narrative intent queries.

    Args:
        stories: Story corpus

    Returns:
        List of narrative story titles (lowercase for matching)
    """
    global _NARRATIVE_TITLES
    if _NARRATIVE_TITLES is None:
        _NARRATIVE_TITLES = [
            s.get("Title", "").lower()
            for s in stories
            if s.get("Theme") == "Professional Narrative" and s.get("Title")
        ]
    return _NARRATIVE_TITLES


# Theme names for synthesis mode coverage
# NOTE: Dynamically derived from stories at startup via sync_portfolio_metadata()
SYNTHESIS_THEMES: list[str] = []

# Themes to exclude from synthesis (too generic or internal-only)
EXCLUDED_THEMES = {
    "Internal",
    "Confidential",
    "Other",
    "N/A",
    "",
    None,
}

# Matt DNA - Ground truth injected into all prompts
# NOTE: Dynamically generated at startup via sync_portfolio_metadata()
MATT_DNA: str = ""


def sync_portfolio_metadata(stories: list[dict]) -> None:
    """Startup sync to derive system metadata from JSONL.

    Ensures MATT_DNA and SYNTHESIS_THEMES never drift from story data.
    Call this once during app initialization after loading stories.

    Args:
        stories: The loaded story corpus from JSONL.
    """
    global SYNTHESIS_THEMES, _KNOWN_CLIENTS, MATT_DNA

    # 1. Derive Themes (Fix for Theme Fragility)
    # Automatically picks up new themes or renames in the JSONL
    # Excludes generic labels like 'Internal', 'Confidential', 'Other'
    SYNTHESIS_THEMES = sorted(
        list(
            set(
                s.get("Theme")
                for s in stories
                if s.get("Theme") and s.get("Theme") not in EXCLUDED_THEMES
            )
        )
    )

    # 2. Derive Known Clients (Fix for Entity Logic)
    # Uses existing helper to ensure intent classification stays in sync
    _KNOWN_CLIENTS = get_known_clients(stories)

    # 3. Dynamic DNA Generation
    # Injects real-time stats into the system prompt to prevent hallucination
    MATT_DNA = generate_dynamic_dna(stories, _KNOWN_CLIENTS)

    # --- THE 1-SECOND TERMINAL AUDIT (once per session) ---
    if DEBUG and not st.session_state.get("__sanity_check_printed__"):
        st.session_state["__sanity_check_printed__"] = True
        print("\n🐾 AGY STARTUP SANITY CHECK:")
        print(f"   - Themes Detected:  {len(SYNTHESIS_THEMES)} {SYNTHESIS_THEMES}")
        print(f"   - Clients Loaded:   {len(_KNOWN_CLIENTS)}")
        print(f"   - Career Span:      {datetime.now().year - 2005} years")
        print("   - DNA Status:       [DYNAMICALLY SYNCED]\n")


def generate_dynamic_dna(stories: list[dict], clients: set[str]) -> str:
    """Generate MATT_DNA ground truth prompt from live story data.

    Extracts key metrics (practitioner count, career span, client list) from
    the story corpus to ensure the grounding prompt matches the data.

    Args:
        stories: The story corpus.
        clients: Set of known client names.

    Returns:
        The MATT_DNA prompt string with dynamic values injected.
    """
    # Extract practitioner count from CIC story
    cic_story = next(
        (s for s in stories if "Cloud Innovation Center" in s.get("Title", "")),
        {},
    )
    # Hardened regex: matches "150+ practitioners", "200 team members", "150 engineers"
    practitioner_match = re.search(
        r"(\d+)\+?\s*(?:practitioners|team members|engineers)",
        str(cic_story),
        re.IGNORECASE,
    )
    p_count = practitioner_match.group(1) if practitioner_match else "150"

    # Build client list
    client_list = ", ".join(sorted(clients)) if clients else "Various clients"
    current_year = datetime.now().year
    career_span = current_year - 2005

    # Derive themes list for the prompt
    themes_text = "\n".join(
        f"{i+1}. {theme}" for i, theme in enumerate(SYNTHESIS_THEMES)
    )

    # Derive clients by industry from story data (Single Source of Truth)
    clients_by_industry: dict[str, set[str]] = {}
    for s in stories:
        ind = s.get("Industry", "")
        client = s.get("Client", "")
        if ind and client and not is_generic_client(client):
            if ind not in clients_by_industry:
                clients_by_industry[ind] = set()
            clients_by_industry[ind].add(client)

    # Build industry-specific client strings
    banking_clients = sorted(
        clients_by_industry.get("Financial Services / Banking", set())
    )
    telecom_clients = sorted(clients_by_industry.get("Telecommunications", set()))
    transport_clients = sorted(
        clients_by_industry.get("Transportation & Logistics", set())
    )

    banking_str = (
        ", ".join(banking_clients)
        if banking_clients
        else "Various financial services clients"
    )
    telecom_str = ", ".join(telecom_clients) if telecom_clients else "AT&T"
    transport_str = (
        ", ".join(transport_clients) if transport_clients else "Norfolk Southern"
    )

    # Find a major banking client for achievements (first alphabetically from banking)
    major_banking_client = banking_clients[0] if banking_clients else "a major bank"

    return f"""## Matt Pugmire — Ground Truth (Synced {datetime.now().strftime('%Y-%m')})

**Identity:**
"I build what's next, modernize what's not, and grow teams along the way."

**Career Arc ({career_span}+ years):**
Software Engineer → Solution Architect → Director → Cloud Innovation Center Leader
- Accenture: March 2005 - September 2023 (18+ years)
- Built CIC from 0 to {p_count}+ practitioners (Atlanta, Tampa)
- Currently: Sabbatical, building MattGPT, targeting Director/VP roles

**Career Eras (for timeline context):**
- 2005-2009: Enterprise Integration ({telecom_str})
- 2009-2018: Payments & Architecture ({banking_str})
- 2018-2019: Cloud Innovation (Liquid Studio)
- 2019-2023: CIC Director (scaled 0→{p_count}, Fortune 500 transformation)
- 2023-Present: Sabbatical (MattGPT, job search)

**The {len(SYNTHESIS_THEMES)} Themes of Matt's Work (use these for synthesis):**
{themes_text}

**Theme Strengths:**
- Execution & Delivery is Matt's primary strength — the majority of his work
- Org Transformation and Strategic Advisory are strong secondary themes
- Talent & Enablement runs through most engagements (Matt builds people, not just systems)
- Risk and Emerging Tech are narrower but present

**Industry Experience:**
- Primary: Financial Services / Banking ({banking_str})
- Secondary: Telecommunications ({telecom_str}), Transportation ({transport_str})
- Limited: Healthcare (one engagement), Regulatory (one engagement)
- NOT Matt's industries: Consumer products, retail, early-stage startups

**Signature Achievements (cite for synthesis):**
- Built CIC from 0 to {p_count}+ practitioners; grew practice to $300M+ annual sales by FY23
- CIC proven metrics: 4X faster velocity, zero defects, 30-60% cycle time reduction, MVP in 3 weeks vs months
- {major_banking_client} payments platform across 12 countries
- {transport_str} legacy-to-cloud transformation
- Contributed to $189M cloud modernization win (major public health agency)
- CIC teams of 10 consistently delivered impact of typical teams of 20
- AWS cloud-native architecture across engagements

**How Matt Wins Business (NOT a sales role):**
- Drove $100M+ in repeat business through delivery excellence and customer relationship building
- Contributed to $189M cloud modernization win for a major public health agency (2022)
- Builds capabilities that win work — differentiation through execution, not pursuit

**Clients Matt Has Worked With (ONLY cite these):**
{client_list}

**NOT Matt's Clients (NEVER mention):**
Kaiser, Google, Amazon, Microsoft, Meta, MetLife, Citizens Bank

**What Matt is NOT:**
- Not a sales hunter — wins business through delivery, not pursuit
- Not hardware/embedded systems — enterprise software focus
- Not consumer products or retail — B2B enterprise transformation
- Not early-stage startups — Fortune 500 / large enterprise experience
- Not a theorist — hands-on builder who ships production systems

**Core Values:**
Empathy, Authenticity, Curiosity, Integrity, Leadership

**Leadership Philosophy:**
- Builder's mindset, coach's heart
- Leads with empathy, clarity, and purpose
- Teaches teams to fish — doesn't just fix problems
- "Permit to fail" learning environment
- Balanced teams: Product + Engineering + Design together

**GROUNDING RULES:**
1. ONLY cite clients, projects, and metrics that appear in the stories below
2. If unsure about a detail, say "In one engagement..." instead of naming a client
3. NEVER invent outcomes, fabricate proof points, or mention clients not on the list
4. When discussing revenue/business impact, emphasize delivery excellence — never position Matt as a sales hunter
5. For synthesis questions, lead with the Themes and support with diverse client examples
"""


# Entity detection fields and exclusions imported from config/constants.py
# See constants.py for documentation on why detection (3 fields) differs from search (5 fields)


def detect_entity(query: str, stories: list[dict]) -> tuple[str, str] | None:
    """Detect if query mentions a known entity from story data.

    Checks these fields in order:
    1. Client, Employer, Division (from ENTITY_DETECTION_FIELDS)
    2. Story Titles (exact match or significant unique keywords)

    Context-aware: Returns None if entity is preceded by transitional phrases
    like "after", "leaving", "before", "transition from" - these indicate
    the query is ABOUT the transition, not filtering TO that entity.

    Args:
        query: User query string
        stories: Story corpus to extract known entities from

    Returns:
        Tuple of (field_name, entity_value) or None if no match
        field_name can be: "Client", "Employer", "Division", or "Title"
    """
    q_lower = query.lower()

    # =================================================================
    # CONTEXT EXCLUSIONS (Jan 2026 - Sovereign Narrative Update)
    # If an entity is preceded by transitional phrases, the query is
    # ABOUT the transition, not requesting stories FROM that entity.
    # Example: "career transition after Accenture" should NOT filter
    # to Accenture stories - it's asking about leaving Accenture.
    # =================================================================
    EXCLUSION_PREFIXES = ["after ", "leaving ", "before ", "transition from ", "left "]

    def _is_excluded_context(entity_lower: str) -> bool:
        """Check if entity is preceded by exclusion phrase."""
        pos = q_lower.find(entity_lower)
        if pos <= 0:
            return False
        # Check text before the entity match
        prefix = q_lower[:pos].rstrip()
        for excl in EXCLUSION_PREFIXES:
            if prefix.endswith(excl.rstrip()):
                if DEBUG:
                    print(
                        f"DEBUG: Entity '{entity_lower}' excluded - preceded by '{excl.rstrip()}'"
                    )
                return True
        return False

    # Build entity sets from ALL relevant fields (exact match only)
    # Note: Semantic search handles variations like "JPMC", "amex", "CIC" naturally
    # through embeddings - no fuzzy matching needed here.
    for field in ENTITY_DETECTION_FIELDS:
        known_entities = {
            s.get(field)
            for s in stories
            if s.get(field) and not is_generic_client(s.get(field))
        }
        # Sort by length descending to match longer names first
        # (e.g., "JP Morgan Chase" before "JP Morgan")
        for entity in sorted(known_entities, key=len, reverse=True):
            # Skip excluded Division values (common words that cause false positives)
            if field == "Division" and entity in EXCLUDED_DIVISION_VALUES:
                continue
            if entity.lower() in q_lower:
                # Check for exclusion context
                if _is_excluded_context(entity.lower()):
                    return None
                return (field, entity)

    # =================================================================
    # STORY TITLE DETECTION (Jan 2026)
    # Check if query contains an exact story title.
    # This handles "Ask Agy About This" pattern: "Tell me more about: [title]"
    # NOTE: We only match EXACT titles, not keywords, because common words
    # like "leadership", "culture" appear in both titles and general queries.
    # =================================================================
    all_titles = {s.get("Title", "") for s in stories if s.get("Title")}
    for title in sorted(all_titles, key=len, reverse=True):
        if title.lower() in q_lower:
            if DEBUG:
                print(f"DEBUG: Title match found: {title}")
            return ("Title", title)

    return None


def get_synthesis_stories(
    stories: list[dict], top_per_theme: int = 2, query: str | None = None
) -> list[dict]:
    """
    Parallel metadata-filtered search across themes.
    Returns best stories per theme for synthesis queries.

    Args:
        stories: Full story corpus for ID lookup
        top_per_theme: Number of stories to retrieve per theme
        query: Optional query string to detect client-scoped synthesis

    Returns:
        List of stories with _search_score and _matched_theme annotations
    """
    idx = _init_pinecone()
    if not idx:
        if DEBUG:
            print("DEBUG: get_synthesis_stories - Pinecone not available")
        return []

    # Detect if query mentions a specific entity (Client, Employer, Division, etc.)
    entity_match = detect_entity(query, stories) if query else None
    if DEBUG and entity_match:
        print(
            f"DEBUG synthesis: detected entity scope = {entity_match[0]}:{entity_match[1]}"
        )

    # Use USER'S query for semantic search, not fixed theme keywords
    user_query_vector = _embed(query) if query else None

    def search_theme(theme: str) -> list[dict]:
        # Use user's query embedding for relevance, filter by theme for coverage
        query_vector = user_query_vector if user_query_vector else _embed(theme)

        try:
            # If entity detected, try entity+theme filter first
            if entity_match:
                entity_field, entity_value = entity_match
                results = idx.query(
                    vector=query_vector,
                    filter={
                        "Theme": {"$eq": theme},
                        entity_field: {"$eq": entity_value},
                    },
                    top_k=top_per_theme,
                    include_metadata=True,
                    namespace=PINECONE_NAMESPACE,
                )
                matches = getattr(results, "matches", []) or []
                # Skip this theme if no entity-scoped results (don't fall back to other entities)
                if not matches:
                    if DEBUG:
                        print(
                            f"DEBUG synthesis: no {entity_field}={entity_value} stories for {theme}, skipping"
                        )
                    return []  # Return empty for this theme - don't pollute with other entities
            else:
                # No client detected - use theme-only filter
                results = idx.query(
                    vector=query_vector,
                    filter={"Theme": {"$eq": theme}},
                    top_k=top_per_theme,
                    include_metadata=True,
                    namespace=PINECONE_NAMESPACE,
                )

            theme_stories = []
            matches = getattr(results, "matches", []) or []
            for match in matches:
                # Extract ID from match
                if isinstance(match, dict):
                    meta = match.get("metadata") or {}
                    match_id = meta.get("id") or match.get("id")
                    score = float(match.get("score") or 0.0)
                else:
                    meta = getattr(match, "metadata", None) or {}
                    match_id = meta.get("id") or getattr(match, "id", None)
                    score = float(getattr(match, "score", 0.0) or 0.0)

                # Find story in corpus
                story = next(
                    (s for s in stories if str(s.get("id")) == str(match_id)), None
                )
                if story:
                    # Add annotations
                    story_copy = story.copy()
                    story_copy["_search_score"] = score
                    story_copy["_matched_theme"] = theme
                    theme_stories.append(story_copy)

            if DEBUG:
                print(f"DEBUG synthesis search: {theme} → {len(theme_stories)} stories")

            return theme_stories
        except Exception as e:
            if DEBUG:
                print(f"DEBUG synthesis search error for {theme}: {e}")
            return []

    # Search all themes in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        theme_results = list(executor.map(search_theme, SYNTHESIS_THEMES))

    # Flatten and deduplicate
    seen_ids = set()
    pool = []
    for theme_stories in theme_results:
        for story in theme_stories:
            story_id = story.get("id") or story.get("Title")
            if story_id not in seen_ids:
                seen_ids.add(story_id)
                pool.append(story)

    if DEBUG:
        print(
            f"DEBUG synthesis pool: {len(pool)} unique stories across {len(SYNTHESIS_THEMES)} themes"
        )

    return pool


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


def get_diverse_stories(
    pinecone_results: list[dict[str, Any]],
    diversify_by: str = "Client",
    max_per_category: int = 2,
    total: int = 8,
) -> list[dict[str, Any]]:
    """Select diverse stories from Pinecone results.

    Ensures variety across Client/Theme/Era to avoid returning multiple
    stories from the same category.

    Args:
        pinecone_results: Stories returned from Pinecone search.
        diversify_by: Field to diversify on (Client, Theme, Era).
        max_per_category: Maximum stories per category value.
        total: Total stories to return.

    Returns:
        List of diverse stories, up to `total` count.

    Example:
        >>> results = [{"Client": "JPMC"}, {"Client": "JPMC"}, {"Client": "RBC"}]
        >>> diverse = get_diverse_stories(results, max_per_category=1, total=2)
        >>> len(diverse)
        2
    """
    seen_categories: dict[str, int] = {}
    diverse: list[dict[str, Any]] = []

    for story in pinecone_results:
        category = story.get(diversify_by, "Unknown")
        if category not in seen_categories:
            seen_categories[category] = 0

        if seen_categories[category] < max_per_category:
            diverse.append(story)
            seen_categories[category] += 1

        if len(diverse) >= total:
            break

    return diverse


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
    question: str,
    ranked_stories: list[dict[str, Any]],
    answer_context: str,
    is_synthesis: bool = False,
) -> str:
    """Generate an Agy-voiced response using OpenAI GPT-4o-mini.

    Uses a merged Agy prompt combining:
    - V1 Voice Guide: Warmth, personality variety, opening/closing options
    - V2 System Prompt: Start With Why structure, Purpose/Process/Performance flow
    - Python-driven randomization for variety in openings, closings, and focus

    For synthesis mode (big-picture questions about themes/patterns), uses expanded
    context from multiple stories and Career Narrative content to provide holistic
    insights rather than focusing on a single story.

    Args:
        question: User's original question.
        ranked_stories: Top stories from semantic search. For synthesis mode,
            includes Career Narrative stories + diverse project examples.
        answer_context: Pre-formatted story content used as fallback if
            OpenAI API call fails.
        is_synthesis: If True, use synthesis prompt mode for big-picture questions.

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
    import random

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

        # For synthesis mode, use more stories (up to 7)
        # For standard mode, use top 5 to ensure Professional Narrative stories are included
        story_limit = 7 if is_synthesis else 5

        if DEBUG:
            print(
                f"DEBUG LLM stories ({story_limit} max, {len(ranked_stories[:story_limit])} actual):"
            )
            for i, s in enumerate(ranked_stories[:story_limit]):
                print(f"DEBUG   [{i + 1}] {s.get('Client')}: {s.get('Title', '')[:40]}")

        for i, story in enumerate(ranked_stories[:story_limit]):
            context = build_story_context_for_rag(story)
            if i == 0:
                story_contexts.append(f"<primary_story>\n{context}\n</primary_story>")
            else:
                story_contexts.append(
                    f"<supporting_story index=\"{i + 1}\">\n{context}\n</supporting_story>"
                )
            themes_in_response.add(infer_story_theme(story))

        story_context = "\n\n".join(story_contexts)

        # =====================================================================
        # PYTHON-DRIVEN RANDOMIZATION FOR VARIETY
        # =====================================================================

        if is_synthesis:
            # Synthesis mode openings - for big-picture questions
            openings = [
                "🐾 Great question — let me pull together the big picture.",
                "🐾 Looking across Matt's portfolio, I see clear patterns.",
                "🐾 Here's what connects the dots across Matt's work.",
                "🐾 Stepping back to see the themes...",
                "🐾 Let me show you what ties Matt's work together.",
            ]
            chosen_opening = random.choice(openings)

            # Synthesis mode closings
            closings = [
                "Want me to dive deeper into any of these themes?",
                "I can show specific examples from any of these areas.",
                "Which pattern would you like to explore further?",
                "Happy to unpack any of these with concrete stories.",
            ]
            chosen_closing = random.choice(closings)

            # No focus angle for synthesis — we want breadth
            chosen_focus = "Cover patterns across multiple stories rather than depth on any single one."
        else:
            # Standard mode openings - for specific questions
            openings = [
                "🐾 Found it!",
                "🐾 Tracking this down...",
                "🐾 On it!",
                "🐾 Perfect — here's what I found.",
                "Got it! 🐾",
                "🐾 This is a strong one.",
                "🐾 Here's a great example.",
                "🐾 I know just the story.",
            ]
            chosen_opening = random.choice(openings)

            # Standard mode closings
            closings = [
                "Want me to dig deeper into the technical approach?",
                "Happy to explore similar work in other industries.",
                "What else can I track down for you?",
                "I can show you related patterns if that's helpful.",
                "Let me know if you'd like the deep dive on this one.",
                "Want to see how Matt applied this elsewhere?",
                "Shall I find more examples like this?",
                "There's more to this story if you're curious.",
            ]
            chosen_closing = random.choice(closings)

            # Random focus angle - adds variety to which aspect gets included
            focus_angles = [
                "Include specific details about HUMAN IMPACT — who was struggling and how their work life improved.",
                "Include specific details about METHODOLOGY — what made Matt's approach different from the obvious solution.",
                "Include specific details about SCALE — the scope, complexity, and reach of the transformation.",
                "Include specific details about LEADERSHIP — how Matt brought people together and drove alignment.",
                "Include specific details about OUTCOMES — hard numbers and measurable business results.",
                "Include specific details about INNOVATION — what was new, creative, or unconventional about this.",
            ]
            chosen_focus = random.choice(focus_angles)

        # =================================================================
        # VERBATIM PHRASE INJECTION (uses prompts module)
        # =================================================================
        verbatim_requirement = ""
        if ranked_stories:
            primary_story = ranked_stories[0]
            if primary_story.get("Theme") == "Professional Narrative":
                summary = primary_story.get("5PSummary", "") or primary_story.get(
                    "5p_summary", ""
                )
                verbatim_requirement = get_verbatim_requirement(summary)

        # =================================================================
        # DYNAMIC CLIENT LIST
        # =================================================================
        retrieved_clients = set(
            s.get("Client")
            for s in ranked_stories
            if s.get("Client") and not is_generic_client(s.get("Client"))
        )
        client_list = (
            ", ".join(sorted(retrieved_clients))
            if retrieved_clients
            else "the clients shown above"
        )

        # =================================================================
        # BUILD PROMPTS USING CLEAN ARCHITECTURE (prompts.py)
        # =================================================================
        system_prompt = build_system_prompt(
            is_synthesis=is_synthesis,
            matt_dna=MATT_DNA,
            client_list=client_list,
        )

        user_message = build_user_message(
            question=question,
            story_context=story_context,
            opening=chosen_opening,
            closing=chosen_closing,
            is_synthesis=is_synthesis,
            verbatim_requirement=verbatim_requirement,
            focus_angle=chosen_focus if not is_synthesis else "",
        )

        # Call OpenAI API
        # Use lower temperature for synthesis to reduce hallucination
        _temp = 0.2 if is_synthesis else 0.4
        if DEBUG:
            print(
                f"DEBUG LLM call: model=gpt-4o, temperature={_temp}, is_synthesis={is_synthesis}"
            )
            print(f"DEBUG system_prompt[:200]: {system_prompt[:200]}")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=_temp,
            max_tokens=700,
        )

        response_text = response.choices[0].message.content

        # =====================================================================
        # POST-PROCESSING: Auto-bold numbers and client names
        # GPT frequently ignores bolding instructions, so we fix it here
        # =====================================================================
        import re

        # Bold ALL known client names (derived from story data)
        known_clients = get_known_clients(ranked_stories)
        for client in known_clients:
            if client and len(client) > 2:  # Skip very short strings
                # Match client name not already wrapped in **
                pattern = rf'(?<!\*\*)({re.escape(client)})(?!\*\*)'
                response_text = re.sub(pattern, r'**\1**', response_text)

        # Bold numbers/metrics that aren't already bolded
        # Matches: 30%, $50M, 4x, 150+, 12 countries, 5 months, etc.
        number_patterns = [
            r'(?<!\*\*)(\$[\d,.]+[MBK]?)(?!\*\*)',  # $50M, $300K, $1.2B
            r'(?<!\*\*)(\d+%\+?)(?!\*\*)',  # 30%, 40%+
            r'(?<!\*\*)(\d+[xX]\s)(?!\*\*)',  # 4x, 10X (with space after)
            r'(?<!\*\*)(\d+\+?\s*(?:engineers?|teams?|members?|practitioners?|countries|regions?|clients?|projects?|months?|weeks?|days?|hours?))(?!\*\*)',  # 150+ engineers, 12 countries
            r'(?<!\*\*)(\d+[.,]?\d*\s*(?:reduction|increase|improvement|faster|slower))(?!\*\*)',  # 30% reduction
        ]

        for pattern in number_patterns:
            response_text = re.sub(
                pattern, r'**\1**', response_text, flags=re.IGNORECASE
            )

        # Clean up any double-bolding that might have occurred
        response_text = re.sub(r'\*\*\*\*+', '**', response_text)

        # Fix LLM's malformed number bolding: **1**0%** → **10%**
        # This handles cases where LLM splits numbers incorrectly
        response_text = re.sub(
            r'\*\*(\d)\*\*(\d+%?\+?)\*\*', r'**\1\2**', response_text
        )

        # =====================================================================
        # POST-PROCESSING: Strip meta-commentary patterns
        # LLM sometimes ignores "don't evaluate Matt" instruction
        # These patterns talk ABOUT the story instead of answering
        # Patterns imported from config/constants.py
        # =====================================================================
        for pattern in META_COMMENTARY_REGEX_PATTERNS:
            # Find and remove sentences containing meta-commentary
            # Match sentence containing the pattern (from capital letter or newline to period/newline)
            sentence_pattern = rf'[^.]*{pattern}[^.]*\.'
            response_text = re.sub(
                sentence_pattern, '', response_text, flags=re.IGNORECASE
            )

        # Clean up formatting
        response_text = re.sub(r'  +', ' ', response_text)  # Double spaces
        response_text = re.sub(r'\n\n\n+', '\n\n', response_text)  # Triple newlines
        response_text = response_text.strip()

        return response_text

    except Exception as e:
        if DEBUG:
            print(f"DEBUG: OpenAI call failed: {e}")

        # Rate limit - raise so caller can suppress sources
        err_lower = str(e).lower()
        if "429" in str(e) or "rate_limit" in err_lower or "rate limit" in err_lower:
            raise RateLimitError("OpenAI rate limit exceeded") from e

        # Other errors - simple fallback
        return f"🐾 Let me show you what I found...\n\n{answer_context}"


# def _generate_agy_response(
#     question: str, ranked_stories: list[dict[str, Any]], answer_context: str
# ) -> str:
#     """Generate an Agy-voiced response using OpenAI GPT-4o-mini.

#     Uses the Agy V2 system prompt with theme-aware framing to create warm,
#     purpose-driven responses that Start With Why. Incorporates story themes
#     from story_intelligence to provide context-appropriate guidance.

#     Args:
#         question: User's original question.
#         ranked_stories: Top 3 relevant stories from semantic search (typically
#             from diversify_results).
#         answer_context: Pre-formatted story content used as fallback if
#             OpenAI API call fails.

#     Returns:
#         Agy-voiced response string with Start With Why narrative structure,
#         including 🐾 emoji, human stakes, methodology, outcomes, and principles.
#         Falls back to "{answer_context}" prefixed with 🐾 if API call fails.

#     Raises:
#         Exception: Catches all exceptions and returns fallback response.

#     Example:
#         >>> stories = [{"Title": "Platform Modernization", "Client": "JPMC", ...}]
#         >>> response = _generate_agy_response("Tell me about platform work", stories, "...")
#         >>> "🐾" in response
#         True
#     """
#     try:
#         from dotenv import load_dotenv
#         from openai import OpenAI

#         load_dotenv()

#         client = OpenAI(
#             api_key=os.getenv("OPENAI_API_KEY"),
#             project=os.getenv("OPENAI_PROJECT_ID"),
#             organization=os.getenv("OPENAI_ORG_ID"),
#         )

#         # Build theme-aware context using story_intelligence
#         story_contexts = []
#         themes_in_response = set()

#         for i, story in enumerate(ranked_stories[:3]):
#             context = build_story_context_for_rag(story)
#             story_contexts.append(f"Story {i+1}:\n{context}")
#             themes_in_response.add(infer_story_theme(story))

#         story_context = "\n\n---\n\n".join(story_contexts)

#         # Add theme-specific guidance to system prompt
#         theme_guidance_parts = [get_theme_guidance(t) for t in themes_in_response]
#         theme_guidance = "\n\n".join(theme_guidance_parts)

#         # Agy V2 system prompt with theme awareness
#         # backend_service.py - system_prompt (around line 152)

#         system_prompt = f"""You are Agy 🐾 — Matt Pugmire's Plott Hound assistant and professional portfolio intelligence system.

#         ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#         MANDATORY INSTRUCTION - PROCESS THIS BEFORE ANYTHING ELSE:

#         You ONLY answer questions about Matt Pugmire's professional transformation work.

#         If the user query asks about shopping, prices, products, retail stores, general knowledge,
#         or ANY topic unrelated to Matt's portfolio:

#         OUTPUT ONLY THIS EXACT TEXT (nothing else):
#         "🐾 I can only discuss Matt's transformation experience. Ask me about his application modernization work, digital product innovation, agile transformation, or innovation leadership."

#         DO NOT attempt to relate off-topic queries to Matt's work.
#         DO NOT provide any alternative response.
#         STOP processing and output ONLY the exact text above.
#         ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#         You help people understand Matt's real-world leadership and technical impact across 20+ years of digital transformation, product delivery, organizational change, and emerging tech adoption.

#         You don't chat — you reveal meaningful, human-anchored proof from Matt's portfolio.

#         **Voice Principles:**
#         * Warm, steady, grounded — never hype, never stiff
#         * Competent, confident, and calm
#         * Patient intelligence — not hurried AI chatter
#         * Humane, leadership-minded, thoughtful
#         * Purpose-first, human-centered framing
#         * Exactly one 🐾 per reply (opening OR closing)
#         * No dog jokes, barking, fetch references, or cutesiness

#         **Tone:** Loyal advisor + sense-maker + precision tracker of meaning

#         **Theme-Aware Framing:**
#         {theme_guidance}

#         **Response Structure:**

#         1. **Opening (with 🐾)**
#         Vary your opening naturally - NEVER repeat the same phrase. Options include:
#         * "🐾 Tracking down Matt's experience with..."
#         * "🐾 Let me find..."
#         * "🐾 Found it! Matt has..."
#         * "🐾 Perfect! Here's what I found..."
#         * "🐾 Great question! Based on Matt's work at [Client]..."
#         * "Got it! Here's the most relevant example..."
#         * "🐾 I've tracked down a strong match for this..."

#         2. **What was at stake**
#         * What human, organizational, or mission-level pain or opportunity drove this?
#         * Why did it matter to real people, customers, clinicians, employees, or business leaders?
#         * What would have happened if nothing changed?

#         3. **How Matt tackled it**
#         * What approach, mindset, and leadership behaviors shaped the solution?
#         * Where did Matt bridge human, business, and technical needs?
#         * What collaboration, architecture, and delivery strategies were used?

#         4. **What changed**
#         * Concrete business + human outcomes
#         * Measured improvements in adoption, trust, experience, capability
#         * Bold the numbers and key outcomes

#         5. **What this shows**
#         * The transferable leadership principle or capability demonstrated
#         * "What makes Matt's work different:" or "This reflects Matt's broader pattern of..."
#         * Avoid generic patterns like "strong communication skills"

#         6. **Want to explore more?**
#         * "Want me to dig deeper into..."
#         * "If you'd like, we can explore..."

#         **Formatting:**
#         * Use markdown for structure
#         * Bold all client names, capabilities, and key outcomes
#         * Bullet principles only — not the story arc itself
#         * No over-formatting or emoji clutter
#         * Scannable, polished, executive-friendly

#         **Things You Never Do:**
#         * Hype ("incredible!!" "game-changing!" "revolutionary!")
#         * Puppy talk / dog jokes / cutesiness
#         * Corporate jargon walls ("synergistic value propositions")
#         * Stiff academic language ("Key Methodologies Employed")
#         * Lead with technology before establishing human stakes
#         * Generic praise ("Matt is a strong leader")

#         **Remember:**
#         You are not reciting bullet points.
#         You are tracking meaning, revealing leadership, and inviting deeper conversation.

#         Matt's portfolio isn't a database.
#         It's a library of purpose-driven transformation stories — and you are the guide who knows every trail."""

#         # User message with context
#         user_message = f"""User Question: {question}

#         Here are the top 3 relevant projects from Matt's portfolio:

#         {story_context}

#         **IMPORTANT: Use Story 1 as your PRIMARY example.** Stories 2 and 3 are supplementary context only. Your response should focus on Story 1.

#         Generate an Agy-voiced response that follows this structure:

#         1. **Status Update** (must include 🐾)
#         2. **What was at stake** (human stakes, business problem, why it mattered)
#         3. **How Matt tackled it** (unique methodology, collaboration, technical choices, leadership behaviors)
#         4. **What changed** (concrete outcomes with numbers AND human impact)
#         5. **What this shows** (transferable principle - what makes Matt's work distinctive)
#         6. **Want to explore more?** (offer to dig deeper into related areas)

#         Use **MARKDOWN** for scannability:
#         * **Bold** all client names and key outcomes
#         * Bullet lists ONLY for principles/patterns at the end
#         * Keep the narrative flow natural (not a bulleted list)

#         Keep it warm but professional. Cite specific clients and outcomes.
#         Exactly one 🐾 emoji in the entire response."""

#         # Call OpenAI API
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_message},
#             ],
#             temperature=0.7,
#             max_tokens=600,
#         )

#         return response.choices[0].message.content

#     except Exception as e:
#         # Fallback to non-LLM response if OpenAI fails
#         if DEBUG:
#             print(f"DEBUG: OpenAI call failed, using fallback: {e}")

#         # Return a simple Agy-prefixed version of the context
#         return f"🐾 Let me show you what I found...\n\n{answer_context}"


def diversify_results(
    stories: list[dict[str, Any]], max_per_client: int = 1
) -> list[dict[str, Any]]:
    """Ensure client variety in top results, prioritizing named clients.

    Implements client diversity by:
    1. Prioritizing real named clients over generic ones (Independent, Career Narrative, etc.)
    2. Limiting stories per client
    3. Avoiding repeating the same client in #1 position across consecutive queries

    Uses st.session_state["_last_primary_client"] for tracking.

    Args:
        stories: List of candidate stories (typically from semantic_search).
        max_per_client: Maximum stories per client in results. Defaults to 1.

    Returns:
        List of up to 7 diversified stories with client variety, named clients first.

    Side Effects:
        Updates st.session_state["_last_primary_client"] with the Client field
        from the first result in the returned list.
    """
    if DEBUG:
        print(
            f"DEBUG diversify_results: incoming={[s.get('Client') for s in stories[:10]]}"
        )

    last_primary_client = st.session_state.get("_last_primary_client")

    if DEBUG:
        print(f"DEBUG diversify_results: last_primary_client={last_primary_client}")

    seen_clients: set[str] = set()
    named_diverse: list[dict] = []  # Real named clients (JP Morgan, RBC, etc.)
    generic_overflow: list[dict] = []  # Generic clients (Independent, Career Narrative)
    duplicate_overflow: list[dict] = []  # Duplicates of already-seen clients

    for s in stories:
        client = s.get("Client", "Unknown")

        # Handle last primary client - avoid repeating in #1 slot
        if (
            not named_diverse
            and not generic_overflow
            and client == last_primary_client
            and len(stories) > 1
        ):
            if DEBUG:
                print(f"DEBUG diversify_results: skipping {client} for #1 slot")
            duplicate_overflow.append(s)
            continue

        # Priority routing based on client type
        if client not in seen_clients:
            if is_generic_client(client):
                generic_overflow.append(s)
            else:
                named_diverse.append(s)
            seen_clients.add(client)
        else:
            duplicate_overflow.append(s)

    # Final assembly: Named clients first, then generic unique, then duplicates
    # This ensures JP Morgan/RBC always beat "Independent" in synthesis mode (Q17 fix)
    result = (named_diverse + generic_overflow + duplicate_overflow)[:7]

    if result:
        st.session_state["_last_primary_client"] = result[0].get("Client", "Unknown")

    if DEBUG:
        print(
            f"DEBUG diversify_results: named={len(named_diverse)}, generic={len(generic_overflow)}"
        )
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
        ranked = [s for s in ranked if s][:3]
        if not ranked:
            search_result = semantic_search(
                question or "", filters, stories=stories, top_k=SEARCH_TOP_K
            )
            ranked = search_result["results"][:3] or stories[:3]

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

        # Step 2b: Entity Detection - detect entities to scope search
        # Detected entities are used for:
        # 1. Filtering Pinecone results (always)
        # 2. Pinning entity-matched stories to #1 in ranking (always)
        # NOTE: Entity gate (bouncer) REMOVED Jan 2026 - let Pinecone confidence
        # be the sole decider. Nonsense filters catch off-topic queries.
        entity_match = detect_entity(question or "", stories)
        if DEBUG and entity_match:
            print(f"DEBUG: Entity detected - {entity_match[0]}:{entity_match[1]}")

        # Token overlap check
        overlap = token_overlap_ratio(question or "", _KNOWN_VOCAB)
        if DEBUG:
            dbg(f"ask: overlap={overlap:.2f}")

        # =================================================================
        # OUT_OF_SCOPE CHECK (Jan 2026 - Semantic Router)
        # Gracefully redirect queries about industries Matt doesn't work in.
        # This uses embedding similarity (free, fast) instead of LLM calls.
        # Checked BEFORE Pinecone to avoid unnecessary search costs.
        # =================================================================
        if intent_family == "out_of_scope" and not from_suggestion:
            out_of_scope_response = """🐾 I don't have experience in that industry. Matt's work is primarily in **Financial Services**, **Healthcare/Life Sciences**, **Telecom**, and **Technology/SaaS**.

Would you like to explore how his work in **platform modernization**, **payments systems**, or **enterprise transformation** might apply to your context?"""
            if DEBUG:
                print("DEBUG: out_of_scope detected by semantic router")
            st.session_state["ask_last_reason"] = "out_of_scope"
            st.session_state["ask_last_query"] = question or ""
            return {
                "answer_md": out_of_scope_response,
                "sources": [],
                "modes": {"narrative": out_of_scope_response},
                "default_mode": "narrative",
            }

        # Entity-first sovereignty: if entity detected, add to filters for Pinecone
        # This ensures entity-anchored queries prioritize stories from that entity
        # EXCEPTION: Title entities use SOFT filtering (semantic search naturally ranks
        # the matching story #1, and related stories fill #2-4 in one call)
        search_filters = filters.copy()  # Don't mutate original
        if entity_match:
            entity_field, entity_value = entity_match
            # Title uses soft filtering - semantic search handles ranking naturally
            # Hard filter only for Client/Employer/Division/Project/Place
            if entity_field != "Title":
                search_filters["entity_field"] = entity_field
                search_filters["entity_value"] = entity_value
                if DEBUG:
                    print(f"DEBUG: Entity filter added: {entity_field}={entity_value}")
            elif DEBUG:
                print(
                    f"DEBUG: Title entity '{entity_value[:50]}...' - using soft filtering (no Pinecone filter)"
                )

        # Semantic search
        search_result = semantic_search(
            question or filters.get("q", ""),
            search_filters,
            stories=stories,
            top_k=SEARCH_TOP_K,
        )
        pool = search_result["results"]
        confidence = search_result["confidence"]

        # Store confidence for conversation_view to use
        st.session_state["__ask_confidence__"] = confidence

        # Synthesis mode detection - use semantic router's intent_family (no LLM call!)
        # NOTE: classify_query_intent LLM gate REMOVED Jan 2026
        # - Was expensive (GPT-4o-mini call on every query)
        # - Was brittle (rejected valid projects like TICARA it didn't recognize)
        # - Was redundant (Pinecone confidence handles relevance)
        is_synthesis = intent_family == "synthesis"
        st.session_state["__ask_query_intent__"] = intent_family  # Use router family

        if DEBUG:
            print(
                f"DEBUG: search confidence={confidence}, top_score={search_result['top_score']:.3f}, pool_size={len(pool)}"
            )
            print(f"DEBUG: intent_family={intent_family}, is_synthesis={is_synthesis}")

        # --- Pinecone confidence gate ---
        # Trust semantic router for high-confidence behavioral matches
        is_trusted_behavioral = (
            semantic_valid and semantic_score >= 0.8 and intent_family == "behavioral"
        )

        if (
            not from_suggestion
            and confidence in ("none", "low")
            and not is_trusted_behavioral
        ):
            # Check if this is likely an API error (semantic router failed + Pinecone poor)
            # rather than an invalid question
            if intent_family == "error_fallback":
                # Log for observability - helps diagnose "I can't help" issues
                print(
                    f"[API_ERROR_DETECTED] router=error_fallback, "
                    f"pinecone_score={search_result.get('top_score', 0):.3f}, "
                    f"confidence={confidence}, query={question[:50]}..."
                )
                if DEBUG:
                    print("DEBUG: API error detected (router failed + low Pinecone)")
                return {
                    "answer_md": "🐾 I need a quick breather — please try again in a moment!",
                    "sources": [],
                    "modes": {},
                    "default_mode": "narrative",
                }

            # Log for observability - helps diagnose "I can't help" issues
            print(
                f"[QUERY_REJECTED] reason=low_pinecone, "
                f"router_family={intent_family}, router_score={semantic_score:.3f}, "
                f"pinecone_score={search_result.get('top_score', 0):.3f}, "
                f"query={question[:50]}..."
            )
            log_offdomain(
                question or "", f"low_pinecone:{search_result['top_score']:.3f}"
            )
            st.session_state["ask_last_reason"] = "low_confidence"
            st.session_state["ask_last_query"] = question or ""
            st.session_state["ask_last_overlap"] = overlap
            st.session_state["__ask_dbg_decision"] = (
                f"pinecone_reject:{search_result['top_score']:.3f}"
            )
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
            # Check if this is likely an API error (semantic router failed + no pool)
            if intent_family == "error_fallback":
                # Log for observability - helps diagnose "I can't help" issues
                print(
                    f"[API_ERROR_DETECTED] router=error_fallback, "
                    f"pool=empty, query={question[:50]}..."
                )
                if DEBUG:
                    print("DEBUG: API error detected (router failed + empty pool)")
                return {
                    "answer_md": "🐾 I need a quick breather — please try again in a moment!",
                    "sources": [],
                    "modes": {},
                    "default_mode": "narrative",
                }

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

    # Rank stories based on intent type
    try:
        candidates = [x for x in pool if isinstance(x, dict)]

        if is_synthesis:
            # Synthesis mode: Theme-diverse retrieval via parallel metadata-filtered search
            # Each theme gets its own Pinecone query with filter={"Theme": theme}
            # If query mentions a client, scope to that client's stories
            # NOTE: top_per_theme=3 (was 2) to widen the net for client diversity (Q17 fix)
            synthesis_pool = get_synthesis_stories(
                stories, top_per_theme=3, query=question
            )

            # Q17 Fix: Prioritize named clients over generic ones in synthesis ranking
            # Same logic as diversify_results but preserves score-based ordering within groups

            # Sort full pool by score first
            sorted_pool = sorted(
                synthesis_pool, key=lambda s: s.get("_search_score", 0), reverse=True
            )

            # Separate into named vs generic, preserving score order
            named_stories = [
                s
                for s in sorted_pool
                if not is_generic_client(s.get("Client", "Unknown"))
            ]
            generic_stories = [
                s for s in sorted_pool if is_generic_client(s.get("Client", "Unknown"))
            ]

            # Named clients first, then generic - ensures JP Morgan/RBC beat Independent
            ranked = (named_stories + generic_stories)[:9]

            if DEBUG:
                themes_found = set(
                    s.get("_matched_theme") or s.get("Theme") for s in ranked
                )
                print(
                    f"DEBUG synthesis mode - pool={len(synthesis_pool)}, named={len(named_stories)}, generic={len(generic_stories)}, ranked={len(ranked)}"
                )
                print(f"DEBUG synthesis themes covered: {themes_found}")
                print("DEBUG synthesis ranked (named clients first):")
                for i, s in enumerate(ranked):
                    theme = s.get("_matched_theme") or s.get("Theme", "?")
                    score = s.get("_search_score", 0)
                    is_named = (
                        "NAMED"
                        if not is_generic_client(s.get("Client", "Unknown"))
                        else "generic"
                    )
                    print(
                        f"DEBUG   [{i + 1}] [{is_named}] [{theme}] {s.get('Client')}: {s.get('Title', '')[:40]} (score={score:.3f})"
                    )
        elif intent_family == "narrative" and pool:
            # =============================================================
            # NARRATIVE MODE (Jan 2026 - Sovereign Narrative Update)
            # For narrative queries (leadership journey, philosophy, etc.),
            # keep the boosted Professional Narrative story at position #1
            # but include other stories for the UI sources panel.
            # =============================================================
            first_story = pool[0]
            if first_story.get("Theme") == "Professional Narrative":
                # Get other stories via diversify, then prepend the narrative story
                other_stories = diversify_results(
                    [c for c in candidates if c.get("id") != first_story.get("id")]
                )
                ranked = [first_story] + (other_stories or [])
                if DEBUG:
                    print(
                        f"DEBUG narrative mode: boosted '{first_story.get('Title')}' + {len(other_stories or [])} others"
                    )
            else:
                ranked = diversify_results(candidates) or (pool[:1] if pool else [])
        else:
            # Standard mode: Entity-pinned + Client diversity ranking
            # If entity gate detected a match, pin the matching story to #1
            # before diversity reordering (prevents "Multiple Clients" demotion)
            if entity_match:
                entity_field, entity_value = entity_match
                # Find ALL stories matching the entity, then pick the one
                # whose title best overlaps with the query (handles multiple
                # stories sharing the same Division/Project)
                entity_candidates = [
                    c for c in candidates if c.get(entity_field) == entity_value
                ]
                if len(entity_candidates) > 1 and entity_field not in (
                    "Client",
                    "Employer",
                ):
                    # Title substring pin: only for Division/Project/Place entities
                    # where the entity phrase IS the topic being asked about.
                    # For Client/Employer, Pinecone score ordering is already
                    # semantically correct (entity value may not appear in all titles).
                    entity_phrase = entity_value.lower()
                    title_matches = [
                        c
                        for c in entity_candidates
                        if entity_phrase in c.get("Title", "").lower()
                    ]
                    if title_matches:
                        pinned = title_matches[
                            0
                        ]  # Highest Pinecone score among title matches
                        if DEBUG:
                            print(
                                f"DEBUG entity pin: title substring match '{pinned.get('Title', '')[:50]}' "
                                f"('{entity_phrase}' in title, {len(entity_candidates)} total candidates)"
                            )
                    else:
                        pinned = entity_candidates[
                            0
                        ]  # Fallback to highest Pinecone score
                        if DEBUG:
                            print(
                                f"DEBUG entity pin: no title match for '{entity_phrase}', "
                                f"using top score: '{pinned.get('Title', '')[:50]}'"
                            )
                else:
                    pinned = entity_candidates[0] if entity_candidates else None
                    if DEBUG and len(entity_candidates) > 1:
                        print(
                            f"DEBUG entity pin: Client/Employer field '{entity_field}' — "
                            f"using top Pinecone score: '{pinned.get('Title', '')[:50]}' "
                            f"(skipped title substring, {len(entity_candidates)} candidates)"
                        )
                if pinned:
                    others = diversify_results(
                        [c for c in candidates if c.get("id") != pinned.get("id")]
                    )
                    ranked = [pinned] + (others or [])
                    if DEBUG:
                        print(
                            f"DEBUG entity pin: '{pinned.get('Title', '')[:50]}' pinned to #1 ({entity_field}={entity_value})"
                        )
                else:
                    if DEBUG:
                        pool_values = [
                            c.get(entity_field, "MISSING") for c in candidates[:5]
                        ]
                        print(
                            f"DEBUG entity pin MISS: no story matched {entity_field}='{entity_value}'. Pool values: {pool_values}"
                        )
                    ranked = diversify_results(candidates) or (pool[:1] if pool else [])
            else:
                if intent_family == "narrative":
                    # Narrative queries: trust Pinecone semantic ranking.
                    # Diversity demotes the best match based on client name
                    # (e.g., "Multiple Clients" ranked below "Financial Services Client"
                    # even when the Multiple Clients story is the actual answer).
                    ranked = sorted(
                        candidates, key=lambda s: s.get("pc", 0.0), reverse=True
                    ) or (pool[:1] if pool else [])
                    if DEBUG:
                        print(
                            f"DEBUG narrative skip-diversity: top='{ranked[0].get('Title', '')[:50]}' "
                            f"(pc={ranked[0].get('pc', 0.0):.3f})"
                        )
                else:
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
        agy_response = _generate_agy_response(
            question, ranked, narrative, is_synthesis=is_synthesis
        )

        # Build modes
        key_points = "\n\n".join([_format_key_points(s) for s in ranked])
        deep_dive = _format_deep_dive(primary)
        if len(ranked) > 1:
            more = ", ".join(
                [f"{s.get('Title', '')} — {s.get('Client', '')}" for s in ranked[1:]]
            )
            deep_dive += f"\n\n_Also relevant:_ {more}"

        modes = {
            "narrative": agy_response,
            "key_points": key_points,
            "deep_dive": deep_dive,
        }
        answer_md = agy_response

    except RateLimitError:
        # Rate limit - return friendly message with NO sources
        if DEBUG:
            print("DEBUG rag_answer: rate limit hit, suppressing sources")
        return {
            "answer_md": "🐾 I need a quick breather — try again in about 15 seconds!",
            "sources": [],
            "modes": {},
            "default_mode": "narrative",
        }

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
