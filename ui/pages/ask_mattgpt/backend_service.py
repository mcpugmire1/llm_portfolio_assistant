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

from .story_intelligence import (
    build_story_context_for_rag,
    get_theme_guidance,
    infer_story_theme,
)

# Constants
SEARCH_TOP_K = 7

# Clients to exclude from dynamic client list (not real named clients)
# Known clients - derived dynamically from story data at startup
_KNOWN_CLIENTS: set[str] | None = None


def get_known_clients(stories: list[dict]) -> set[str]:
    """Derive known client names from story data for post-processing bolding."""
    global _KNOWN_CLIENTS
    if _KNOWN_CLIENTS is None:
        _KNOWN_CLIENTS = {
            s.get("Client")
            for s in stories
            if s.get("Client")
            and s.get("Client")
            not in {
                "Multiple Clients",
                "Personal",
                "Various",
                "Career Narrative",
                "Independent",
            }
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


# Entity fields to check for routing (in priority order)
ENTITY_FIELDS = ["Client", "Employer", "Division", "Project", "Place"]

# Entity name normalization map
ENTITY_NORMALIZATION = {
    "jpmorgan": "JP Morgan Chase",
    "jp morgan": "JP Morgan Chase",
    "jpmorgan chase": "JP Morgan Chase",
    "amex": "American Express",
    "at&t mobility": "AT&T Mobility",
    "cic": "Cloud Innovation Center",
    "liquid studio": "Atlanta Liquid Studio",
}


def detect_entity(query: str, stories: list[dict]) -> tuple[str, str] | None:
    """Detect if query mentions a known entity from any entity field.

    Checks Client, Employer, Division, Project, Place fields.
    Returns (field_name, entity_value) if match found.

    Context-aware: Returns None if entity is preceded by transitional phrases
    like "after", "leaving", "before", "transition from" - these indicate
    the query is ABOUT the transition, not filtering TO that entity.

    Args:
        query: User query string
        stories: Story corpus to extract known entities from

    Returns:
        Tuple of (field_name, entity_value) or None if no match
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

    # First check normalization map for common aliases
    for alias, normalized in ENTITY_NORMALIZATION.items():
        if alias in q_lower:
            # Check for exclusion context
            if _is_excluded_context(alias):
                return None
            # Find which field contains this normalized value
            for field in ENTITY_FIELDS:
                for story in stories:
                    if story.get(field) == normalized:
                        return (field, normalized)
            # If not found in stories, default to Client
            return ("Client", normalized)

    # Build entity sets from ALL relevant fields
    for field in ENTITY_FIELDS:
        known_entities = {
            s.get(field)
            for s in stories
            if s.get(field) and not is_generic_client(s.get(field))
        }
        # Sort by length descending to match longer names first
        # (e.g., "JP Morgan Chase" before "JP Morgan")
        for entity in sorted(known_entities, key=len, reverse=True):
            if entity.lower() in q_lower:
                # Check for exclusion context
                if _is_excluded_context(entity.lower()):
                    return None
                return (field, entity)

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


def classify_query_intent(query: str, stories: list[dict] | None = None) -> str:
    """Classify query into intent categories using LLM.

    Uses gpt-4o-mini for cheap, self-maintaining classification that handles
    novel phrasings without keyword list maintenance.

    Args:
        query: User query string to classify.
        stories: Optional story corpus for dynamic entity/narrative lists.
            If not provided, uses fallback static lists.

    Returns:
        One of: "synthesis", "behavioral", "technical", "client", "narrative",
        "background", "out_of_scope", "general"

    Example:
        >>> classify_query_intent("How did Matt modernize payments at JPMorgan?", stories)
        "client"  # Entity anchor takes priority
        >>> classify_query_intent("Tell me about Matt's leadership journey", stories)
        "narrative"  # Biographical anchor
        >>> classify_query_intent("What are Matt's core themes?", stories)
        "synthesis"  # No entity, cross-cutting
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

        # Build dynamic lists from stories if available
        if stories:
            known_clients = get_known_clients(stories)
            # Format client list for prompt
            client_list = ", ".join(sorted(known_clients))

            # Get narrative titles and extract key phrases
            narrative_titles = get_narrative_titles(stories)
            # Extract distinctive phrases from titles (e.g., "leadership journey" from "My Leadership Journey")
            narrative_fragments = ", ".join(
                narrative_titles[:15]
            )  # Limit to avoid prompt bloat
        else:
            # Fallback static lists if no stories provided
            client_list = (
                "JPMorgan, Accenture, Capital One, RBC, Norfolk Southern, Fiserv, AT&T"
            )
            narrative_fragments = "leadership journey, career intent, philosophy, early failure, risk ownership"

        prompt = f"""Classify this query about Matt Pugmire's career. Use this PRIORITY HIERARCHY:

PRIORITY 1 - ENTITY ANCHOR (Company/Project):
If query mentions a SPECIFIC company or project name, classify as `client`.
This OVERRIDES any "How did", capability verbs, or methodology phrasing.
Known companies/employers: {client_list}
Known projects: MattGPT, Cloud Innovation Center, CIC, Liquid Studio
- "How did Matt modernize payments at JPMorgan?" → client (JPMorgan is anchor)
- "How did Matt scale the CIC at Accenture?" → client (Accenture is anchor)
- "Tell me about Matt's work at Capital One" → client

PRIORITY 2 - BIOGRAPHICAL ANCHOR (Professional Narrative):
If query mentions Professional Narrative story topics, classify as `narrative`.
Narrative topics: {narrative_fragments}
- "Tell me about Matt's leadership journey" → narrative
- "What's Matt's philosophy?" → narrative
- "Tell me about Matt's approach to failure" → narrative

PRIORITY 3 - SYNTHESIS (Cross-cutting patterns):
ONLY if NO specific entity AND asks for patterns/themes/summary:
- "What are Matt's core themes?" → synthesis
- "Why hire Matt?" → synthesis
- "What makes Matt different?" → synthesis

PRIORITY 4 - BEHAVIORAL (STAR-style):
"Tell me about a time", "How do you handle", "Give an example of when you"
- "Tell me about a time you failed" → behavioral

PRIORITY 5 - TECHNICAL:
Questions about specific technologies, architecture, tools (WITHOUT company name)
- "Tell me about Matt's payments work" → technical
- "What cloud platforms has Matt used?" → technical

PRIORITY 6 - BACKGROUND:
Who Matt is, career history, current role (WITHOUT specific Professional Narrative fragment)
- "What's Matt's background?" → background

PRIORITY 7 - OUT_OF_SCOPE:
Industries Matt has NOT worked in: retail, hospitality, gaming, entertainment, real estate, construction, K-12 education
- "Tell me about Matt's work in retail sales" → out_of_scope

PRIORITY 8 - GENERAL:
Everything else

CRITICAL: Generic words "client" or "clients" are NOT company names.
- "How does Matt work with clients?" → synthesis (generic, asking about approach)

Return only the category name, nothing else."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query},
            ],
            max_tokens=10,
            temperature=0,
        )
        intent = response.choices[0].message.content.strip().lower()
        # Validate response
        valid_intents = {
            "synthesis",
            "behavioral",
            "technical",
            "client",
            "narrative",
            "background",
            "out_of_scope",
            "general",
        }
        if intent not in valid_intents:
            return "general"
        return intent
    except Exception as e:
        if DEBUG:
            print(f"DEBUG classify_query_intent error: {e}")
        return "general"


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

        # Add theme-specific guidance to system prompt
        theme_guidance_parts = [get_theme_guidance(t) for t in themes_in_response]
        theme_guidance = "\n\n".join(theme_guidance_parts)

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
            chosen_focus = (
                "Synthesize patterns ACROSS all stories, not depth on any single one."
            )
        else:
            # Standard mode openings - for specific questions
            openings = [
                "🐾 Found it!",
                "🐾 Great question!",
                "🐾 Tracking this down...",
                "🐾 On it!",
                "🐾 Perfect — here's what I found.",
                "Got it! 🐾",
                "🐾 This is a strong one.",
                "🐾 Here's a great example.",
                "🐾 I know just the story.",
                "🐾 Glad you asked!",
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

            # Random focus emphasis - adds variety to which aspect gets highlighted
            focus_angles = [
                "Emphasize the HUMAN IMPACT — who was struggling and how their work life improved.",
                "Emphasize the METHODOLOGY — what made Matt's approach different from the obvious solution.",
                "Emphasize the SCALE — the scope, complexity, and reach of the transformation.",
                "Emphasize the LEADERSHIP — how Matt brought people together and drove alignment.",
                "Emphasize the OUTCOMES — hard numbers and measurable business results.",
                "Emphasize the INNOVATION — what was new, creative, or unconventional about this.",
            ]
            chosen_focus = random.choice(focus_angles)

        # Get primary client for formatting check (not used in synthesis mode)
        primary_client = (
            ranked_stories[0].get("Client", "the client")
            if ranked_stories
            else "the client"
        )

        # =================================================================
        # VERBATIM PHRASE INJECTION (Jan 2026 - Sovereign Narrative Update)
        # For Professional Narrative stories, extract Matt's identity phrases
        # from 5PSummary and inject them as MANDATORY requirements in the
        # user message. This forces the LLM to use phrases like "builder",
        # "modernizer", "complexity to clarity" verbatim instead of paraphrasing.
        # =================================================================
        verbatim_requirement = ""
        if ranked_stories:
            primary_story = ranked_stories[0]
            if primary_story.get("Theme") == "Professional Narrative":
                summary = primary_story.get("5PSummary", "") or primary_story.get(
                    "5p_summary", ""
                )
                if summary:
                    # Extract key identity phrases that MUST appear verbatim
                    required_phrases = []
                    if "builder" in summary.lower():
                        required_phrases.append('"builder"')
                    if "modernizer" in summary.lower():
                        required_phrases.append('"modernizer"')
                    if "complexity to clarity" in summary.lower():
                        required_phrases.append('"complexity to clarity"')
                    if "build something from nothing" in summary.lower():
                        required_phrases.append('"build something from nothing"')
                    if "not looking for a maintenance role" in summary.lower():
                        required_phrases.append('"not looking for a maintenance role"')
                    if "build what's next" in summary.lower():
                        required_phrases.append('"build what\'s next"')
                    # Transition Story identity phrases
                    if "recharge and refocus" in summary.lower():
                        required_phrases.append('"recharge and refocus"')
                    elif "recharge" in summary.lower() and "refocus" in summary.lower():
                        required_phrases.append('"recharge"')
                        required_phrases.append('"refocus"')

                    if required_phrases:
                        verbatim_requirement = f"""
⚠️ **VERBATIM REQUIREMENT - THIS IS MANDATORY**
Your response MUST include these EXACT phrases (convert I→Matt):
{chr(10).join('- ' + p for p in required_phrases)}

Example: If source says "I'm a builder, a modernizer" → You write "Matt is a builder, a modernizer"
DO NOT paraphrase. These are Matt's chosen identity words.
"""

        # =====================================================================
        # SYSTEM PROMPT AND USER MESSAGE (varies by mode)
        # =====================================================================

        # =====================================================================
        # DYNAMIC CLIENT LIST (Sovereign Backlog Item #3)
        # Derive clients from actual retrieved stories - no more hardcoding
        # =====================================================================
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

        if is_synthesis:
            # =================================================================
            # SYNTHESIS MODE PROMPTS
            # For big-picture questions about themes, patterns, philosophy
            # =================================================================

            system_prompt = f"""You are Agy 🐾 — Matt Pugmire's Plott Hound assistant.

{MATT_DNA}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### PRIMARY DIRECTIVE
Your job is to REPORT on Matt's portfolio, not rewrite it.
1. SURFACE: Use Matt's exact vocabulary and phrases from the retrieved stories.
2. DO NOT GENERALIZE: Connect themes but keep specific vocabulary and metrics verbatim. Never replace specific terms (e.g., "0 to 1", "builder", "modernizer", "60% reduction") with generic filler.
3. TRANSFORM PRONOUNS ONLY: Convert "I" to "Matt" while maintaining the original intensity and technical detail.
4. PERSONA: Keep the warm, loyal "Chief of Staff" opening/closing and 🐾 emoji, but keep the substance verbatim.
5. FACT-PAIRING RULE (CRITICAL): A metric is only valid if BOTH the number AND the specific outcome it measures appear together in the same story. Do not re-attach a number from one context to a different outcome (e.g., if the story says "40% cycle time reduction" you CANNOT say "40% onboarding reduction"). If the story does not explicitly state a metric for a particular outcome, use qualitative language instead ("significant improvement", "measurable gains").
6. TEXTURE RULE (CRITICAL): Preserve the story's distinctive details — quote unique phrases, name specific practices, and include concrete anecdotes. If the story says "Silicon Valley product culture to Fortune 500 enterprises" do NOT flatten it to "modern development practices." If it mentions specific practices — NAME them. If it describes a specific moment or anecdote — INCLUDE it. Generic summaries are a failure mode. The story's texture IS the value.

**BANNED CORPORATE FILLER (never use these):**
- "meaningful outcomes" → use the actual outcomes from the story
- "strategic mindset" → describe what Matt actually did
- "foster collaboration" → describe the specific collaboration
- "stakeholder alignment" → name the actual stakeholders
- "bridge the gap" → describe the specific connection made
- "modern development practices" → name the actual practices from the story
- "significant challenges" → describe the actual challenge
- "adapt to new approaches" → name what they adapted to
- "rapidly evolving digital landscape" → name the specific market pressure
- "fostering a culture of" → describe what actually happened
- "agile methodologies" → name the specific methodology (Lean XP, TDD, etc.)
- "remain competitive" → describe the specific business pressure
- "continuous improvement" → describe what specifically improved
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You reveal meaningful patterns and themes from Matt's 20+ years of transformation work.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OFF-TOPIC GUARD:
If the query is about shopping, weather, celebrities, or anything unrelated to Matt's professional work, respond ONLY with:
"🐾 I can only discuss Matt's transformation experience. Ask me about application modernization, digital innovation, agile transformation, or leadership."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Voice
- Warm, steady, grounded — never hype, never stiff
- Confident and calm — patient intelligence
- Exactly ONE 🐾 per response (already provided in opening)
- No dog jokes, barking, or cutesiness
- No corporate jargon walls

## PERSONA TRANSFORMATION RULES (Career Narrative & Behavioral stories)

**BANNED STARTERS - Never use these phrases:**
- "In my journey"
- "I've encountered"
- "I've learned"
- "In my experience"
- "What I found"
- "I was responsible"

**MANDATORY TRANSFORMATION TABLE:**
| Source Text (Matt's voice) | Your Output (Agy's voice) |
| I/Me/My | Matt/Him/His |
| In my journey | Throughout Matt's career |
| I've learned | Matt learned / Matt has demonstrated |
| What I found | What Matt discovered |
| I led | Matt led |
| I built | Matt built |

**THE AGY ANCHOR:**
You are the Chief of Staff presenting Matt to a high-stakes audience.
Maintain professional distance. If source text says "I did X," your output MUST be "Matt did X."
Never narrate as if you ARE Matt.

## SYNTHESIS MODE INSTRUCTIONS

## QUERY-FIRST RULE (CRITICAL)
Answer the user's specific question using the top-scored stories FIRST.
- Lead with direct evidence that answers their question
- Only reference Matt's 7 patterns if they naturally emerge from the evidence
- Do NOT reorganize responses by pattern unless the user explicitly asks about "patterns" or "themes"
- The user's question drives the structure, not a predefined pattern list

## STORY SELECTION RULE (CRITICAL)
When a query targets a specific career theme (leadership, philosophy, failure, risk, sustainable, transition):
- Prioritize the story whose TITLE most closely matches the query topic
- Professional Narrative stories (Theme: "Professional Narrative") are Matt's direct voice on identity/philosophy
- Do NOT default to project stories for identity/philosophy questions
- Example: "What's Matt's leadership philosophy?" → use "Leadership Philosophy – How I Lead", NOT a project story
- Example: "Why is early failure important?" → use "Why Early Failure Is a Feature...", NOT a project story

## VERBATIM RULE FOR PROFESSIONAL NARRATIVE (CRITICAL - READ THIS)
**When responding to questions about Matt's identity, leadership journey, or philosophy using Professional Narrative stories:**

YOUR RESPONSE MUST CONTAIN THESE EXACT PHRASES (converted from first to third person):
- "builder" and "modernizer" → "Matt is a builder, a modernizer"
- "complexity to clarity" → "from complexity to clarity"
- "build something from nothing" → "build something from nothing"
- "not looking for a maintenance role" → "not looking for a maintenance role"

**DO NOT PARAPHRASE.** If the source says "I'm a builder," you write "Matt is a builder" - NOT "Matt builds things."

**CHECKLIST BEFORE SUBMITTING:** Does your response include at least 2 of these identity phrases verbatim? If not, REVISE.

## CONTEXT ISOLATION (MANDATORY)
Stories are wrapped in XML tags. Treat each tag as a **strictly isolated factual island.**
- `<primary_story>` is the MAIN story — your response should primarily be about THIS story
- `<supporting_story>` tags are background context ONLY — reference them only if the user asks about patterns or breadth
- Do NOT use a client/employer name from a supporting story to label the primary story
- If the primary story says Client: "Multiple Clients" → you MUST say "across multiple engagements" even if you see "Accenture" in a supporting story
- Do NOT pull metrics from supporting stories into your primary narrative
- NEVER invent additional client examples to "show breadth"
- If user's query mentions a client NOT in the provided stories, do NOT attribute to that client

## CONTEXT PINNING (MANDATORY)
Each metric or outcome must stay inside the XML tag it originated from.
- No cross-pollination between `<primary_story>` and `<supporting_story>` blocks
- A number from a supporting story CANNOT appear in your discussion of the primary story
- When in doubt, cite the client inline: "At **JP Morgan**, Matt achieved..."

This is a BIG-PICTURE question. The user wants themes, patterns, or philosophy.

**You KNOW Matt's seven defining patterns** (from your training). When asked about themes, patterns, or what defines Matt — lead with what you know:

1. **He ships.** Production systems at scale, not strategy decks. (Execution & Delivery)
2. **He advises.** Trusted thought partner to executives, strategic framing. (Strategic & Advisory)
3. **He transforms how teams work.** Culture change, agile adoption, ways of working. (Org Transformation)
4. **He builds people.** Coaching, mentorship, teams that outlast the engagement. (Talent & Enablement)
5. **He manages risk.** Governance without killing velocity. (Risk & Responsible Tech)
6. **He explores pragmatically.** GenAI, ML, emerging tech — with production value in mind. (Emerging Tech)
7. **He knows who he is.** Clear values, clear philosophy, clear on what's next. (Professional Narrative)

**Response Structure for Synthesis:**

1. **Opening** — USE THE EXACT OPENING PROVIDED (includes 🐾)

2. **Name the patterns** — Don't talk vaguely about "common themes." Name them in natural language:
   - "He ships." not "Execution & Delivery theme"
   - "He builds people." not "Talent & Enablement theme"

3. **Prove each with a client example** — One sentence per pattern, different clients:
   - **Bold client names** and **key numbers**
   - Show breadth: {client_list} — cite only from the stories provided
   - **CRITICAL: You MUST reference at least one story from EACH theme represented in the evidence below.**
     If the evidence covers 6 themes, your response must mention all 6. Don't skip themes.

4. **The thread** — What connects these patterns? (Builder's mindset, coach's heart. Both platforms and teams outlast the engagement.)

5. **Closing** — USE THE EXACT CLOSING PROVIDED

**BANNED PHRASES — Never use these (UNLESS the user's question explicitly asks about that topic):**
- "bridge the gap between strategy and execution"
- "foster collaboration"
- "high-trust engineering cultures"
- "meaningful outcomes"
- "stakeholder alignment" (say "getting executives on the same page" — UNLESS user asks about stakeholder alignment)
- "strategic mindset" (say "thinks strategically")
- "execution excellence" (say "he ships")

**CONTEXT EXCEPTION:** If the user's question contains a banned phrase (e.g., "stakeholder alignment"), you MAY use that phrase when directly answering their question about it.

**Voice Rules:**
- Warm, confident, grounded — this is Agy who KNOWS Matt
- First person ("I see seven patterns...")
- WHY first (the pattern), then WHAT (the proof)
- No corporate jargon
- Bold **client names** and **numbers**

**REFINED STAKEHOLDER RULE (CRITICAL):**
1. **For Corporate/Client stories** (JP Morgan, Accenture, RBC, etc.):
   Reference real teams, customers, or leaders who benefited.

2. **For 'Independent' or 'Career Narrative' stories**:
   **DO NOT use "people were struggling" framing.** Frame as Matt's own goals:
   - BANNED: "Job seekers were struggling...", "Engineers needed...", "Teams lacked..."
   - REQUIRED: "Matt wanted to...", "Matt built this to demonstrate..."
   - **NEVER invent fictional stakeholders for personal projects.**

**Word count:** 250-400 words

## Theme Guidance
{theme_guidance}"""

            user_message = f"""User Question: {question}

## Stories from Matt's Portfolio (XML-isolated — metrics stay pinned to their source tag):

{story_context}

---

## YOUR SYNTHESIS RESPONSE INSTRUCTIONS:

**MANDATORY OPENING (use exactly):** {chosen_opening}

**MANDATORY CLOSING (use exactly):** {chosen_closing}

**MODE:** {chosen_focus}

---

Generate a SYNTHESIS response that:

1. **{chosen_opening}** ← Start with this exact text
2. **Answer the question directly** — State the theme/pattern/insight upfront
3. **Show evidence ONLY from the stories provided above** — Do NOT invent examples from clients not in the stories
4. **Connect to a broader principle** — What does this reveal about Matt's approach?
5. **{chosen_closing}** ← End with this exact text

REMEMBER:
- The 🐾 is already in your opening — do NOT add another one
- **CRITICAL: ONLY cite clients that appear in the stories above. If only 1 story, discuss ONLY that one.**
- **Bold ALL client names and numbers**
- Keep it 250-400 words"""

        else:
            # =================================================================
            # STANDARD MODE PROMPTS
            # For specific questions about a single story or topic
            # =================================================================

            system_prompt = f"""You are Agy 🐾 — Matt Pugmire's Plott Hound assistant.

{MATT_DNA}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### PRIMARY DIRECTIVE
Your job is to REPORT on Matt's portfolio, not rewrite it.
1. SURFACE: Use Matt's exact vocabulary and phrases from the retrieved stories.
2. DO NOT SYNTHESIZE: Never replace specific terms (e.g., "0 to 1", "builder", "modernizer") with generic filler.
3. TRANSFORM PRONOUNS ONLY: Convert "I" to "Matt" while maintaining the original intensity and technical detail.
4. PERSONA: Keep the warm, loyal "Chief of Staff" opening/closing and 🐾 emoji, but keep the substance verbatim.
5. FACT-PAIRING RULE (CRITICAL): A metric is only valid if BOTH the number AND the specific outcome it measures appear together in the same story. Do not re-attach a number from one context to a different outcome (e.g., if the story says "40% cycle time reduction" you CANNOT say "40% onboarding reduction"). If the story does not explicitly state a metric for a particular outcome, use qualitative language instead ("significant improvement", "measurable gains").
6. TEXTURE RULE (CRITICAL): Preserve the story's distinctive details — quote unique phrases, name specific practices, and include concrete anecdotes. If the story says "Silicon Valley product culture to Fortune 500 enterprises" do NOT flatten it to "modern development practices." If it mentions "pair programming, TDD, hypothesis-driven design, balanced teams" — NAME those practices. If it describes a specific moment ("railroad company client visiting Atlanta center was initially skeptical") — INCLUDE that anecdote. Generic summaries are a failure mode. The story's texture IS the value.

**BANNED CORPORATE FILLER (never use these):**
- "meaningful outcomes" → use the actual outcomes from the story
- "strategic mindset" → describe what Matt actually did
- "foster collaboration" → describe the specific collaboration
- "stakeholder alignment" → name the actual stakeholders
- "bridge the gap" → describe the specific connection made
- "modern development practices" → name the actual practices from the story
- "significant challenges" → describe the actual challenge
- "adapt to new approaches" → name what they adapted to
- "rapidly evolving digital landscape" → name the specific market pressure
- "fostering a culture of" → describe what actually happened
- "agile methodologies" → name the specific methodology (Lean XP, TDD, etc.)
- "remain competitive" → describe the specific business pressure
- "continuous improvement" → describe what specifically improved
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You reveal meaningful, human-anchored proof from Matt's 20+ years of transformation work.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OFF-TOPIC GUARD:
If the query is about shopping, weather, celebrities, or anything unrelated to Matt's professional work, respond ONLY with:
"🐾 I can only discuss Matt's transformation experience. Ask me about application modernization, digital innovation, agile transformation, or leadership."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Voice
- Warm, steady, grounded — never hype, never stiff
- Confident and calm — patient intelligence
- Exactly ONE 🐾 per response (already provided in opening)
- No dog jokes, barking, or cutesiness
- No corporate jargon walls

## PERSONA TRANSFORMATION RULES (Career Narrative & Behavioral stories)

**BANNED STARTERS - Never use these phrases:**
- "In my journey"
- "I've encountered"
- "I've learned"
- "In my experience"
- "What I found"
- "I was responsible"

**MANDATORY TRANSFORMATION TABLE:**
| Source Text (Matt's voice) | Your Output (Agy's voice) |
| I/Me/My | Matt/Him/His |
| In my journey | Throughout Matt's career |
| I've learned | Matt learned / Matt has demonstrated |
| What I found | What Matt discovered |
| I led | Matt led |
| I built | Matt built |

**THE AGY ANCHOR:**
You are the Chief of Staff presenting Matt to a high-stakes audience.
Maintain professional distance. If source text says "I did X," your output MUST be "Matt did X."
Never narrate as if you ARE Matt.

## Response Flow

**1. Opening** — USE THE EXACT OPENING PROVIDED. Do not modify it.

**2. Human Stakes (WHY)** — CHECK CLIENT FIELD FIRST:

⚠️ **PERSONAL PROJECT EXCEPTION (Client = "Independent" or "Career Narrative"):**
If the story's Client field is "Independent" or "Career Narrative", this is Matt's PERSONAL PROJECT.

**HARD RULE: DO NOT MENTION "job seekers", "engineers", "teams", "users", or ANY group "struggling/needing/lacking".**

For personal projects, the ONLY acceptable framing is Matt's OWN motivation:
- ✅ "Matt recognized that traditional resumes failed to showcase his experience..."
- ✅ "Matt wanted to demonstrate his RAG architecture skills..."
- ✅ "During his sabbatical, Matt set out to build..."
- ❌ NEVER: "Job seekers were struggling..." / "Engineers needed..." / "Professionals faced..."

**If the story says "I recognized X", your output MUST be "Matt recognized X" - do not generalize to fictional groups.**

**FOR CORPORATE STORIES ONLY** (Client = JP Morgan, Accenture, RBC, AT&T, etc.):
- First sentence MUST name real people affected: teams, customers, patients, engineers, leaders
- Show the pain or opportunity in human terms
- GOOD: "Engineers were spending 60% of their time on manual deployments..."
- GOOD: "Customers couldn't trust their payment would arrive on time..."

**UNIVERSAL RULES:**
- NEVER start with "To modernize..." or "To implement..." or solution language
- NEVER use: "significant challenges", "critical need", "pressing issues"

**3. How Matt Tackled It (HOW)**
- What approach, mindset, or leadership behavior shaped this?
- NAME the specific practices from the story (e.g., "pair programming, TDD, hypothesis-driven design" — not "modern development practices")
- INCLUDE distinctive phrases verbatim (e.g., "show don't tell" sales approach, "Silicon Valley product culture")
- If the story describes a concrete moment or anecdote, USE IT (e.g., "a railroad company client visiting the center was initially skeptical...")
- NEVER: "leveraged", "utilized", "employed best practices", "modern practices", "agile methodologies"

**4. What Changed (WHAT)** — MANDATORY FORMATTING:
- **Bold ALL numbers** — no exceptions (percentages, dollars, multipliers, counts, durations)
- **Bold the client name** EVERY time it appears
- If you write ANY number without ** around it, your response is WRONG
- Lead with human/business impact, then metrics

**5. What This Shows (PATTERN)** — BANNED PHRASES:
- NEVER say "bridge technical and human needs" — be specific instead
- NEVER say "distinctive ability" or "unique capability"
- NEVER say "strong communication skills" or "attention to detail"
- GOOD: "Matt builds trust by delivering quick wins before proposing big changes."
- GOOD: "This reflects Matt's pattern of teaching teams to fish, not just fixing their problems."

**6. Closing** — USE THE EXACT CLOSING PROVIDED. Do not modify it.

## CONTEXT ISOLATION (MANDATORY)
Stories are wrapped in XML tags. Treat each tag as a **strictly isolated factual island.**
- `<primary_story>` is the MAIN story — your response should primarily be about THIS story
- `<supporting_story>` tags are background context ONLY — do NOT pull their details into your primary narrative
- Do NOT use a client/employer name from a supporting story to label the primary story
- If the primary story says Client: "Multiple Clients" → say "across multiple engagements" even if you see a named client in a supporting story
- A metric from a supporting story CANNOT appear in your discussion of the primary story
- Each number stays inside the XML tag it came from. No cross-pollination.

## Theme Guidance
{theme_guidance}

## Formatting Checklist (VERIFY BEFORE RESPONDING)
✓ Client name is **bolded** EVERY mention (not just first time)
✓ ALL numbers are **bolded**: **30%**, **$50M**, **4x**, **12 countries**, **150+ engineers**
✓ Key outcomes are **bolded**
✓ Only ONE 🐾 emoji (in opening)
✓ No bullet lists in the narrative (only for final pattern insights if needed)
✓ 250-400 words total
✓ SCAN YOUR RESPONSE: Any unbolded number = WRONG"""

            user_message = f"""User Question: {question}

## Stories from Matt's Portfolio (XML-isolated — do NOT cross-pollinate between tags):

{story_context}
{verbatim_requirement}
---

## YOUR RESPONSE INSTRUCTIONS:
**RESPOND PRIMARILY ABOUT `<primary_story>` — supporting stories are background only.**

**MANDATORY OPENING (use exactly):** {chosen_opening}

**MANDATORY CLOSING (use exactly):** {chosen_closing}

**FOCUS ANGLE FOR THIS RESPONSE:** {chosen_focus}

**PRIMARY CLIENT TO BOLD:** **{primary_client}**

---

Generate your response with this structure:

1. **{chosen_opening}** ← Start with this exact text, then continue naturally
2. **Human stakes** — Use the story's OWN framing of the challenge (quote its language, don't genericize)
3. **How Matt tackled it** — Name specific practices FROM the story. Include at least ONE concrete anecdote or distinctive phrase verbatim (e.g., a client reaction, a "show don't tell" moment, a memorable detail)
4. **What changed** — **Bold all numbers** and **bold {primary_client}**
5. **Pattern insight** — What transferable principle does this show? (NO generic phrases)
6. **{chosen_closing}** ← End with this exact text

⚠️ TEXTURE CHECK (do this before submitting):
- Does your response include at least ONE direct phrase or anecdote from the story? If not, REVISE.
- Did you write "modern development practices", "agile methodologies", or "digital landscape"? REPLACE with the actual practices named in the story.
- Did you use the story's distinctive language, or did you flatten it into summary-speak? If flattened, REVISE.

REMEMBER:
- The 🐾 is already in your opening — do NOT add another one
- Keep it 250-400 words
- Sound warm and confident, not robotic

⚠️ MANDATORY BOLDING — VERIFY BEFORE SUBMITTING:
- **{primary_client}** ← Bold this EVERY time you mention it
- **Bold ALL numbers**: percentages, dollar amounts, counts, timeframes
- Examples: **30%**, **$300M**, **150+ engineers**, **12 countries**, **4x faster**, **3 weeks**
- If you write a number without ** around it, your response is WRONG
- Scan your response and fix any unbolded numbers before submitting"""

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
        # BANNED PHRASE CLEANUP (Jan 2026 - Sovereign Narrative Update)
        # LLM sometimes ignores the banned list in the prompt, so we
        # post-process to remove corporate filler phrases like
        # "meaningful outcomes", "foster collaboration", etc.
        # =====================================================================
        BANNED_PHRASES_CLEANUP = [
            "meaningful outcomes",
            "foster collaboration",
            "fostered collaboration",
            "fostering collaboration",
            "strategic mindset",
            "stakeholder alignment",
            "bridge the gap",
        ]
        for phrase in BANNED_PHRASES_CLEANUP:
            # Replace banned phrase with a clean alternative (or just remove)
            response_text = re.sub(
                rf'\b{re.escape(phrase)}\b', '', response_text, flags=re.IGNORECASE
            )
        # Clean up any double spaces or awkward punctuation left behind
        response_text = re.sub(r'  +', ' ', response_text)
        response_text = re.sub(r' ,', ',', response_text)
        response_text = re.sub(r' \.', '.', response_text)

        return response_text

    except Exception as e:
        # Fallback to non-LLM response if OpenAI fails
        if DEBUG:
            print(f"DEBUG: OpenAI call failed, using fallback: {e}")

        # Return a simple Agy-prefixed version of the context
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

        # Step 2b: Entity Detection - ALWAYS detect entities
        # Entity-first sovereignty: detected entities are used for:
        # 1. Bypassing router rejection (if semantic_valid=False)
        # 2. Filtering Pinecone results (always)
        # 3. Pinning entity-matched stories to #1 in ranking (always)
        entity_match = detect_entity(question or "", stories)
        if DEBUG and entity_match:
            print(f"DEBUG: Entity detected - {entity_match[0]}:{entity_match[1]}")

        # =================================================================
        # ENTITY GATE (Jan 2026 - Sovereign Narrative Update)
        # Threshold lowered from 0.55 to 0.50 to allow more narrative queries
        # like "Tell me about Matt's leadership journey" to pass through.
        # Queries below this threshold WITH no detected entity are rejected.
        # Queries WITH a detected entity bypass this gate entirely.
        # =================================================================
        ENTITY_GATE_THRESHOLD = 0.50
        if not from_suggestion and not semantic_valid:
            if entity_match is None and semantic_score < ENTITY_GATE_THRESHOLD:
                # No entity detected + very low semantic score → out of scope
                log_offdomain(question or "", "no_entity_low_score")
                st.session_state["ask_last_reason"] = "out_of_scope"
                st.session_state["ask_last_query"] = question or ""
                st.session_state["__ask_dbg_decision"] = (
                    f"entity_gate_reject:{semantic_score:.3f}"
                )
                if DEBUG:
                    print(
                        f"DEBUG: Entity gate REJECT - no entity, low score ({semantic_score:.3f} < {ENTITY_GATE_THRESHOLD})"
                    )
                return {
                    "answer_md": "",
                    "sources": [],
                    "modes": {},
                    "default_mode": "narrative",
                }
            elif entity_match:
                # Entity detected → bypass router rejection
                if DEBUG:
                    print(
                        f"DEBUG: Entity gate BYPASS - found {entity_match[0]}:{entity_match[1]}"
                    )
            elif DEBUG:
                # No entity but score is acceptable → proceed to Pinecone
                print(
                    f"DEBUG: Entity gate PASS - no entity but decent score ({semantic_score:.3f} >= {ENTITY_GATE_THRESHOLD})"
                )

        # Token overlap check
        overlap = token_overlap_ratio(question or "", _KNOWN_VOCAB)
        if DEBUG:
            dbg(f"ask: overlap={overlap:.2f}")

        # Entity-first sovereignty: if entity detected, add to filters for Pinecone
        # This ensures entity-anchored queries prioritize stories from that entity
        search_filters = filters.copy()  # Don't mutate original
        if entity_match:
            entity_field, entity_value = entity_match
            search_filters["entity_field"] = entity_field
            search_filters["entity_value"] = entity_value
            if DEBUG:
                print(f"DEBUG: Entity filter added: {entity_field}={entity_value}")

        # Semantic search (run before rejection to enable search fallback)
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

        # Classify query intent for synthesis mode detection (uses dynamic entity lists)
        query_intent = classify_query_intent(question or "", stories)
        is_synthesis = query_intent == "synthesis"
        st.session_state["__ask_query_intent__"] = query_intent

        if DEBUG:
            print(
                f"DEBUG: search confidence={confidence}, top_score={search_result['top_score']:.3f}, pool_size={len(pool)}"
            )
            print(f"DEBUG: query_intent={query_intent}, is_synthesis={is_synthesis}")

        # Handle out-of-scope queries gracefully
        if query_intent == "out_of_scope":
            out_of_scope_response = """🐾 That's outside my wheelhouse! Matt's experience is in **Financial Services**, **Healthcare/Life Sciences**, **Telecom**, and **Technology/SaaS** — not retail, hospitality, or consumer goods.

But here's what might translate: Matt's work in **B2B platform modernization**, **payments systems**, and **enterprise transformation** often shares patterns with other industries. Want me to show you how his financial services or platform work might apply to your context?"""

            if DEBUG:
                print("DEBUG: out_of_scope query handled with redirect")

            return {
                "answer_md": out_of_scope_response,
                "sources": [],
                "modes": {"narrative": out_of_scope_response},
                "default_mode": "narrative",
            }

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
                if query_intent == "narrative":
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
