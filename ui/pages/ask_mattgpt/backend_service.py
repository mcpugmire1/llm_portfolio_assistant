"""
Backend Service for Ask Agy

Handles RAG (Retrieval-Augmented Generation) and OpenAI integration.
Includes nonsense detection, semantic search orchestration, and Agy response generation.
"""

import csv
import json
import logging
import os
import random
import re
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import httpx
import streamlit as st

from config.constants import (
    ASK_ANSWER_MAX_OUTPUT_TOKENS,
    ASK_ANSWER_MODEL,
    ASK_ANSWER_READ_TIMEOUT_S,
    ASK_ANSWER_REASONING_EFFORT,
    ASK_HISTORY_MAX_MESSAGES,
    ASK_TOOL_MAX_ROUNDS,
    META_COMMENTARY_REGEX_PATTERNS,
    PROFILE_FACT_CATEGORIES,
    SEARCH_TOP_K,
)
from config.debug import DEBUG
from services import matt_profile
from services.jd_assessor import load_matt_profile
from services.query_logger import log_query
from services.rag_service import semantic_search
from services.semantic_router import (
    is_portfolio_query_semantic,
    router_rejection_reason,
)
from utils.client_utils import is_generic_client
from utils.validation import is_nonsense

from .prompts import (
    build_tool_system_prompt,
    get_verbatim_requirement,
)
from .story_intelligence import build_story_context_for_rag

logger = logging.getLogger(__name__)

# SEARCH_TOP_K imported from config.constants

# Clients to exclude from dynamic client list (not real named clients)
# Known clients - derived dynamically from story data at startup
_KNOWN_CLIENTS: set[str] | None = None


class RateLimitError(Exception):
    """Raised when OpenAI rate limit is hit. Caller should suppress sources."""

    pass


# Shown when the model call fails for any reason other than a rate limit.
# No story text and no sources: a failed turn has no grounded answer to cite.
ANSWER_ERROR_MESSAGE = "Sorry, I couldn't generate an answer right now."


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

# Career-span constants derived from corpus dates at startup via
# sync_portfolio_metadata() (MATTGPT-161). Available to consumers that need
# the math (e.g., Role Match assessor reasoning about JD tenure requirements).
# NOT rendered into MATT_DNA prose -- the ageism-signal rule applied to the
# resume, About page, and matt_profile.json extends to the LLM grounding
# surface. When MATTGPT-181 lands with pre-2005 stories, _CAREER_START_YEAR
# moves from 2005 to 2000 and _CAREER_SPAN_YEARS updates automatically.
_CAREER_START_YEAR: int = 0
_CAREER_END_YEAR: int = 0
_CAREER_SPAN_YEARS: int = 0


def sync_portfolio_metadata(stories: list[dict]) -> None:
    """Startup sync to derive system metadata from JSONL.

    Ensures MATT_DNA and SYNTHESIS_THEMES never drift from story data.
    Call this once during app initialization after loading stories.

    Args:
        stories: The loaded story corpus from JSONL.
    """
    global \
        SYNTHESIS_THEMES, \
        _KNOWN_CLIENTS, \
        MATT_DNA, \
        _CAREER_START_YEAR, \
        _CAREER_END_YEAR, \
        _CAREER_SPAN_YEARS

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

    # 3. Derive career-span constants from corpus dates (MATTGPT-161).
    # min(Start_Date) and max(End_Date) as YYYY-MM strings are safe under
    # string sort because the format is zero-padded. Not rendered into
    # MATT_DNA prose; consumed by callers that need the math.
    _CAREER_START_YEAR = int(min(s["Start_Date"] for s in stories)[:4])
    _CAREER_END_YEAR = int(max(s["End_Date"] for s in stories)[:4])
    _CAREER_SPAN_YEARS = _CAREER_END_YEAR - _CAREER_START_YEAR

    # 4. Dynamic DNA Generation
    # Injects real-time stats into the system prompt to prevent hallucination
    MATT_DNA = generate_dynamic_dna(stories, _KNOWN_CLIENTS)

    # --- THE 1-SECOND TERMINAL AUDIT (once per session) ---
    if DEBUG and not st.session_state.get("__sanity_check_printed__"):
        st.session_state["__sanity_check_printed__"] = True
        print("\n🐾 AGY STARTUP SANITY CHECK:")
        print(f"   - Themes Detected:  {len(SYNTHESIS_THEMES)} {SYNTHESIS_THEMES}")
        print(f"   - Clients Loaded:   {len(_KNOWN_CLIENTS)}")
        print(
            f"   - Career Span:      {_CAREER_SPAN_YEARS} years ({_CAREER_START_YEAR}-{_CAREER_END_YEAR})"
        )
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

    # Derive clients grouped by employer (Aug 24 2026). Flat client list let
    # the model infer employment from whichever client name dominated a story
    # (verified: "his role at Sparkfly" on a Wellfound story; "At AT&T, Matt
    # served as a Solution Architect" on an Accenture story). Grouping by
    # employer establishes the mapping explicitly so the model can distinguish
    # client engagement from employer.
    #
    # Employers whose only Client value equals the Employer itself
    # (Cendian Chemical Logistics, American InterContinental University) are
    # omitted from this block -- they had no external clients, and the Career
    # Arc row already establishes them as employers.
    clients_by_employer: dict[str, set[str]] = {}
    for s in stories:
        emp = s.get("Employer", "")
        client = s.get("Client", "")
        if not emp or not client or client == emp:
            continue
        # Filter placeholder client values (Fortune 500 Clients, Independent
        # Project). These are intentional -- they stand in for NDA and
        # multi-client work -- so they belong in the corpus but not in a
        # per-client list.
        if is_generic_client(client):
            continue
        # Filter Professional Narrative arc stories. The Employer field
        # carries two meanings: who employed Matt during the work, and what
        # period the story covers. For engagement stories those coincide.
        # For arc stories they do not -- "Why Hire Matt?" summarizes 18 years
        # at Accenture; "Transition Story" spans 2023-09 to 2026-08 under
        # Employer=Accenture. The schema cannot express this, so any
        # derivation driven by Employer must exclude Professional Narrative.
        # Verified Aug 21 2026 during MATTGPT-161 pre-flight.
        if s.get("Theme") == "Professional Narrative":
            continue
        clients_by_employer.setdefault(emp, set()).add(client)

    clients_by_employer_lines = "\n".join(
        f"- {emp}: {', '.join(sorted(clients_by_employer[emp]))}"
        for emp in sorted(clients_by_employer.keys())
        if clients_by_employer[emp]
    )

    # Derive themes list for the prompt
    themes_text = "\n".join(
        f"{i+1}. {theme}" for i, theme in enumerate(SYNTHESIS_THEMES)
    )

    # Industry Experience, derived entirely from the Industry field
    # (MATTGPT-279): every industry with its story count, most stories first,
    # and the non-generic clients of its stories. "Cross Industry" is not an
    # industry. No tier labels or fallback names, so a new story's industry
    # reaches the model without a code change.
    stories_by_industry: dict[str, int] = {}
    clients_by_industry: dict[str, set[str]] = {}
    for s in stories:
        ind = s.get("Industry", "")
        if not ind or ind == "Cross Industry":
            continue
        stories_by_industry[ind] = stories_by_industry.get(ind, 0) + 1
        client = s.get("Client", "")
        if client and not is_generic_client(client):
            clients_by_industry.setdefault(ind, set()).add(client)

    industry_lines = []
    for ind in sorted(stories_by_industry, key=lambda i: (-stories_by_industry[i], i)):
        n = stories_by_industry[ind]
        line = f"- {ind}: {n} {'story' if n == 1 else 'stories'}"
        if clients_by_industry.get(ind):
            line += f" ({', '.join(sorted(clients_by_industry[ind]))})"
        industry_lines.append(line)
    industry_experience_lines = "\n".join(industry_lines)
    # Matt's own words, rendered under the profile's label so the model can
    # quote them as his self-description, not as verified facts. Role Match's
    # grounding (jd_assessor.load_matt_profile) does not carry them.
    try:
        self_desc = matt_profile.load_profile_dict().get("self_description") or {}
    except Exception:
        self_desc = {}
        logger.exception("MATT_DNA self-description block skipped: profile read failed")
    self_description_block = ""
    if self_desc.get("label") and self_desc.get("statements"):
        statement_lines = "\n".join(f"- {s}" for s in self_desc["statements"])
        self_description_block = f"**{self_desc['label']}:**\n{statement_lines}\n\n"

    return f"""## Matt Pugmire: Ground Truth (Synced {datetime.now().strftime('%Y-%m')})

**Career Arc:**
Software Engineer → Solution Architect → Director → Cloud Innovation Center Leader
- Wellfound Technology: 2000-2001, 2002-2003
- American InterContinental University: 2003-2004 (adjunct, taught alongside full-time work)
- Cendian Chemical Logistics: 2003-2005
- Accenture: March 2005 - September 2023
- Built CIC from 0 to {p_count}+ practitioners (Atlanta, Tampa)
- Currently: Sabbatical, building MattGPT. In active search for a role where building the product engineering organization, establishing the culture, and delivering results are part of the same job.

**The {len(SYNTHESIS_THEMES)} Themes of Matt's Work (use these for synthesis):**
{themes_text}

**Theme Strengths:**
- Execution & Delivery is Matt's primary strength
- Org Transformation is a strong secondary theme
- Strategic Advisory, Talent & Enablement, Emerging Tech and Risk are narrower but present

**Industry Experience (stories per industry):**
{industry_experience_lines}

**Signature Achievements (cite for synthesis):**
- Built CIC from 0 to {p_count}+ practitioners
- CIC proven metrics: 4X faster velocity, zero defects
- CIC teams of 10 consistently delivered impact of typical teams of 20
- AWS cloud-native architecture across engagements

**How Matt Wins Business (NOT a sales role):**
- Drove $100M+ in repeat business through delivery excellence and customer relationship building
- Builds capabilities that win work: differentiation through execution, not pursuit

**Clients by Employer (ONLY cite these):**
{clients_by_employer_lines}

{self_description_block}**Leadership Philosophy:**
- Leads with empathy, clarity, and purpose
- "Permit to fail" learning environment
- Balanced teams: Product + Engineering + Design together

**GROUNDING RULES:**
1. ONLY cite clients, projects, and metrics that appear in the stories below
2. If unsure about a detail, say "In one engagement..." instead of naming a client
3. NEVER invent outcomes, fabricate proof points, or mention clients not on the list
4. When discussing revenue/business impact, emphasize delivery excellence, and never position Matt as a sales hunter
5. For synthesis questions, lead with the Themes and support with diverse client examples
"""


# See constants.py for why detection uses fewer fields than search


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


# MATTGPT-250 item 4: a run of one or more [[...]] tokens, with the spaces
# or tabs before it and any comma/space separators between tokens, removed
# as one unit ("? [[profile:education]], [[profile:languages]]" -> "?").
# Known [[profile:<category>]] markers become fact-row categories; every
# token, known or not, is removed so no marker residue reaches the visitor.
_MARKER_RE = re.compile(r"[ \t]*\[\[[^\[\]]*\]\](?:[ \t]*,?[ \t]*\[\[[^\[\]]*\]\])*")
_PROFILE_MARKER_RE = re.compile(r"\[\[\s*profile:\s*([a-z_]+)\s*\]\]", re.IGNORECASE)


def _extract_profile_markers(text: str) -> tuple[str, list[str]]:
    """Strip [[...]] markers from raw LLM output and return the cited
    profile categories in first-cited order.

    A line holding only markers is dropped together with the blank line
    before it, so no blank-line gap is left. An inline marker is removed
    with its leading whitespace ("SAFe [[profile:certifications]] and
    Oracle" -> "SAFe and Oracle"). Unknown markers ([[profile:patents]],
    [[profile-only]]) are removed without adding a category. Text with no
    markers is returned byte-identical.
    """
    categories: list[str] = []
    for match in _PROFILE_MARKER_RE.finditer(text):
        category = match.group(1).lower()
        if category in PROFILE_FACT_CATEGORIES and category not in categories:
            categories.append(category)

    kept_lines: list[str] = []
    for line in text.split("\n"):
        if line.strip() and not _MARKER_RE.sub("", line).strip():
            if kept_lines and not kept_lines[-1].strip():
                kept_lines.pop()
            continue
        kept_lines.append(line)
    return _MARKER_RE.sub("", "\n".join(kept_lines)), categories


# The model's em and en dashes, replaced by one deterministic rule (the repo
# and Agy's answers use none). Each pattern touches only the dash and the
# spaces and commas next to it.
_DIGIT_RANGE_DASH_RE = re.compile(r"(?<=\d)[ \t]*\u2013[ \t]*(?=\d)")
_WORD_JOIN_DASH_RE = re.compile(r"(?<=\w)\u2013(?=\w)")
_CLAUSE_DASH_RE = re.compile(
    r"(?:,[ \t]*)?(?:[ \t]*\u2014[ \t]*|[ \t]+\u2013[ \t]+)(?:,[ \t]*)?"
)
# Held back at the end of streamed text until the next character shows how
# the dash resolves (a space already shown before a dash would read "grew ,").
_DASH_HOLD_CHARS = " \t,\u2014\u2013"


def _clause_dash(match: re.Match) -> str:
    following = match.string[match.end() : match.end() + 1]
    return "" if following in ("", ".", "!", "?", "\n") else ", "


def normalize_dashes(text: str) -> str:
    """Em dash (spaced or not) -> ", "; en dash between digits -> " to ";
    spaced en dash -> ", "; unspaced en dash between words -> "-". A
    replacement comma absorbs an adjacent comma and is dropped before
    . ! ? or a line end. Other en dashes are left as written."""
    text = _DIGIT_RANGE_DASH_RE.sub(" to ", text)
    text = _WORD_JOIN_DASH_RE.sub("-", text)
    return _CLAUSE_DASH_RE.sub(_clause_dash, text)


def _postprocess_agy_text(
    response_text: str, stories: list[dict[str, Any]]
) -> tuple[str, list[str]]:
    """Clean the model's answer text for display. Returns (text, cited_categories).

    Replaces dashes first (normalize_dashes(), as the stream does), strips
    profile markers (MATTGPT-250 item 4), then bolds the clients
    of the given stories and number patterns, strips meta-commentary,
    tidies whitespace, and escapes $ last.
    """
    # First, on the model's own text, as the stream applies it.
    response_text = normalize_dashes(response_text)
    response_text, cited_categories = _extract_profile_markers(response_text)

    # =====================================================================
    # POST-PROCESSING: Auto-bold numbers and client names
    # GPT frequently ignores bolding instructions, so we fix it here
    # =====================================================================

    # Bold ALL known client names (derived from story data)
    known_clients = get_known_clients(stories)

    # Bold numbers/metrics that aren't already bolded
    # Matches: 30%, $50M, 4x, 150+, 12 countries, 5 months, etc.
    #
    # MATTGPT-250: leading lookbehind `(?<![\*\d])` rejects any match
    # start that sits mid-number or immediately after `**`. The prior
    # `(?<!\*\*)` only guarded the exact "**" prefix, which admitted
    # mid-number starts on pre-bolded input (e.g. "**16 weeks**" ->
    # "**1**6 week**s**", "**40%+**" -> "**4**0%**+**").
    # MATTGPT-275: `(?<!\d[,.])` and a whole-number match keep "135,000+"
    # and "99.97%" from being split at the comma or the decimal point.
    number = r'\d[\d,]*(?:\.\d+)?'
    number_patterns = [
        r'(?<![\*\d])(\$[\d,.]+[MBK]?)(?!\*\*)',  # $50M, $300K, $1.2B
        rf'(?<![\*\d])(?<!\d[,.])({number}%\+?)(?!\*\*)',  # 30%, 40%+, 99.97%
        r'(?<![\*\d])(\d+[xX])(?=\s)(?!\*\*)',  # 4x, 10X (lookahead for space, don't capture it)
        rf'(?<![\*\d])(?<!\d[,.])({number}\+?\s*(?:engineers?|teams?|members?|practitioners?|professionals?|countries|regions?|clients?|projects?|months?|weeks?|days?|hours?))(?!\*\*)',  # 150+ engineers, 12 countries, 135,000+ clients
        rf'(?<![\*\d])(?<!\d[,.])({number}\s*(?:reduction|increase|improvement|faster|slower))(?!\*\*)',  # 30% reduction
    ]

    # MATTGPT-275: bold only outside the spans the model already bolded.
    # Matching inside one splits it ("**135,000+ clients**" ->
    # "**135,**000+ client**s**"); the lookbehinds above can't prevent that
    # when the match starts after a space inside the span
    # ("**3 years and 10 months**").
    parts = re.split(r'(\*\*[^*\n]+?\*\*)', response_text)
    for i in range(0, len(parts), 2):
        segment = parts[i]
        for client in known_clients:
            if client and len(client) > 2:  # Skip very short strings
                # Match client name not already wrapped in **
                pattern = rf'(?<!\*\*)({re.escape(client)})(?!\*\*)'
                segment = re.sub(pattern, r'**\1**', segment)
        for pattern in number_patterns:
            segment = re.sub(pattern, r'**\1**', segment, flags=re.IGNORECASE)
        parts[i] = segment
    response_text = ''.join(parts)

    # Clean up any double-bolding that might have occurred
    response_text = re.sub(r'\*\*\*\*+', '**', response_text)

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
        response_text = re.sub(sentence_pattern, '', response_text, flags=re.IGNORECASE)

    # Clean up formatting
    response_text = re.sub(r'  +', ' ', response_text)  # Double spaces
    response_text = re.sub(r'\n\n\n+', '\n\n', response_text)  # Triple newlines
    response_text = response_text.strip()

    # Escape dollar signs to prevent Streamlit's markdown renderer
    # from interpreting $...$ as LaTeX math notation.
    # Must run AFTER all other post-processing (bolding, meta-strip, etc.)
    response_text = response_text.replace("$", "\\$")

    return response_text, cited_categories


# Agy's opener lines and focus angles, chosen at random per answer by
# _choose_opening_and_focus(); the tool path also shows the opener lines to
# the model as examples of how Agy opens.
SYNTHESIS_OPENERS = [
    "🐾 Looking across Matt's portfolio, I see clear patterns.",
    "🐾 Here's what connects the dots across Matt's work.",
    "🐾 Stepping back to see the themes...",
    "🐾 Let me show you what ties Matt's work together.",
]
STANDARD_OPENERS = [
    "🐾 Found it!",
    "🐾 Tracking this down...",
    "🐾 On it!",
    "🐾 Perfect, here's what I found.",
    "Got it! 🐾",
    "🐾 This is a strong one.",
    "🐾 Here's a great example.",
    "🐾 I know just the story.",
]
FOCUS_ANGLES = [
    "Include specific details about HUMAN IMPACT: who was struggling and how their work life improved.",
    "Include specific details about METHODOLOGY: what made Matt's approach different from the obvious solution.",
    "Include specific details about SCALE: the scope, complexity, and reach of the transformation.",
    "Include specific details about LEADERSHIP: how Matt brought people together and drove alignment.",
    "Include specific details about OUTCOMES: hard numbers and measurable business results.",
    "Include specific details about INNOVATION: what was new, creative, or unconventional about this.",
]
SYNTHESIS_BREADTH = (
    "Cover patterns across multiple stories rather than depth on any single one."
)


def _choose_opening_and_focus(is_synthesis: bool) -> tuple[str, str]:
    """Pick Agy's opener and focus angle at random. Returns (opening, focus).

    Synthesis answers get a synthesis opener and the breadth instruction;
    standard answers get a standard opener and a random focus angle.
    """
    if is_synthesis:
        return random.choice(SYNTHESIS_OPENERS), SYNTHESIS_BREADTH
    return random.choice(STANDARD_OPENERS), random.choice(FOCUS_ANGLES)


def _openai_client():
    """OpenAI client for Ask Agy's answer calls, from the app's env vars.

    Imported at call time so tests can patch openai.OpenAI. Each read waits
    at most ASK_ANSWER_READ_TIMEOUT_S; the connect timeout stays the SDK's
    5 s.
    """
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv()
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        project=os.getenv("OPENAI_PROJECT_ID"),
        organization=os.getenv("OPENAI_ORG_ID"),
        timeout=httpx.Timeout(ASK_ANSWER_READ_TIMEOUT_S, connect=5.0),
    )


def _nonsense_rejection(
    question: str, from_suggestion: bool, obs: dict[str, Any]
) -> dict[str, Any] | None:
    """Rules-based nonsense check. Returns the rejection result, or None.

    On a rule match (and not from a suggestion chip) it logs the query, sets
    ask_last_reason, ask_last_query and ask_last_overlap for the UI banner,
    records rejection_reason in obs, and returns the empty rejection result.
    """
    cat = is_nonsense(question or "")
    if DEBUG:
        print(f"DEBUG: is_nonsense returned cat={cat}")

    if cat and not from_suggestion:
        log_offdomain(question or "", f"rule:{cat}")
        log_query(question or "", "Ask Agy", redirect_reason=f"rule:{cat}")
        st.session_state["ask_last_reason"] = f"rule:{cat}"
        st.session_state["ask_last_query"] = question or ""
        st.session_state["ask_last_overlap"] = None
        st.session_state["__ask_dbg_decision"] = f"rule:{cat}"
        obs["rejection_reason"] = f"rule:{cat}"
        return {
            "answer_md": "",
            "sources": [],
            "modes": {},
            "default_mode": "narrative",
            **obs,
        }
    return None


def _router_rejection(
    question: str,
    intent_family: str,
    semantic_score: float,
    from_suggestion: bool,
    obs: dict[str, Any],
) -> dict[str, Any] | None:
    """Semantic-router out_of_scope / personal redirect. Returns it, or None.

    Gracefully redirect queries the router is confident don't belong.
    Embedding similarity (free, fast) instead of LLM calls, checked
    BEFORE Pinecone to avoid unnecessary search costs.
    MATTGPT-219 (out_of_scope) + MATTGPT-234 (personal): both branches
    gated on HARD_ACCEPT via router_rejection_reason. Below that the
    router isn't confident; the query falls through to Pinecone and
    any real off-topic case is caught by the overlap:0.00 gate with
    correct rejection copy. See helper docstring for full rationale.
    """
    rejection_family = router_rejection_reason(intent_family, semantic_score)
    if rejection_family == "out_of_scope" and not from_suggestion:
        out_of_scope_response = """🐾 I don't have experience in that industry. Matt's work is primarily in **Financial Services**, **Healthcare/Life Sciences**, **Telecom**, and **Technology/SaaS**.

Would you like to explore how his work in **platform modernization**, **payments systems**, or **enterprise transformation** might apply to your context?"""
        if DEBUG:
            print("DEBUG: out_of_scope detected by semantic router")
        log_query(
            question or "",
            "Ask Agy",
            intent_family="out_of_scope",
            redirect_reason="semantic_router:out_of_scope",
        )
        st.session_state["ask_last_reason"] = "semantic_router:out_of_scope"
        st.session_state["ask_last_query"] = question or ""
        obs["rejection_reason"] = "semantic_router:out_of_scope"
        return {
            "answer_md": out_of_scope_response,
            "sources": [],
            "modes": {"narrative": out_of_scope_response},
            "default_mode": "narrative",
            **obs,
        }

    # PERSONAL CHECK (Mar 2026 - Semantic Router)
    # Warm redirect for personal questions (age, family, salary, identity).
    # Gate shared with out_of_scope above via router_rejection_reason.
    if rejection_family == "personal" and not from_suggestion:
        personal_response = """🐾 I'm focused on Matt's professional experience, including the projects, teams, and outcomes.

Ask me about his **transformation work**, **platform engineering**, or **how he builds teams** and I'll dig up the details."""
        if DEBUG:
            print("DEBUG: personal query detected by semantic router")
        log_query(
            question or "",
            "Ask Agy",
            intent_family="personal",
            redirect_reason="semantic_router:personal",
        )
        st.session_state["ask_last_reason"] = "semantic_router:personal"
        st.session_state["ask_last_query"] = question or ""
        obs["rejection_reason"] = "semantic_router:personal"
        return {
            "answer_md": personal_response,
            "sources": [],
            "modes": {"narrative": personal_response},
            "default_mode": "narrative",
            **obs,
        }
    return None


# Ask Agy tool loop (MATTGPT-275). Every turn's first call is a forced search:
# the model writes the query from the question and the conversation.
# Responses API function-tool shape.
_SEARCH_STORIES_TOOL = {
    "type": "function",
    "name": "search_stories",
    "description": (
        "Semantic search over Matt's STAR career stories. Returns the top 5 stories."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "A standalone search query."}
        },
        "required": ["query"],
    },
    "strict": False,
}

_STREAM_END_EVENTS = ("response.completed", "response.incomplete")


def _run_search_tool(
    arguments: str, stories: list[dict[str, Any]]
) -> tuple[str, list[dict[str, Any]], float]:
    """Run one search_stories call. Returns (tool output, stories, top score).

    Each returned story is rendered with build_story_context_for_rag(); a
    Professional Narrative story also carries its verbatim requirement.
    """
    try:
        query = json.loads(arguments or "{}").get("query", "")
    except json.JSONDecodeError:
        query = ""
    result = semantic_search(query, {}, stories=stories, top_k=SEARCH_TOP_K)
    found = (result.get("results") or [])[:5]
    blocks = []
    for story in found:
        block = f'<story title="{story.get("Title", "")}">\n{build_story_context_for_rag(story)}\n</story>'
        if story.get("Theme") == "Professional Narrative":
            summary = story.get("5PSummary", "") or story.get("5p_summary", "")
            block += get_verbatim_requirement(summary)
        blocks.append(block)
    return (
        "\n\n".join(blocks) or "No stories found.",
        found,
        result.get("top_score") or 0.0,
    )


def _stream_response(
    client: Any, on_delta: Callable[[str], None] | None, **request: Any
) -> Any:
    """One streamed Responses API call. Answer text goes to on_delta as it
    arrives, with normalize_dashes() applied: a dash, and the spaces and
    commas next to it, is held back until the next character shows how it
    resolves, so the stream shows the finished answer's wording and never
    takes text back. Returns the final response. An incomplete response
    (output cap reached) is returned with whatever it produced; a failed one
    raises.

    The SDK retries the request, not a stream that breaks after it starts
    (MATTGPT-303). A stream that breaks before any answer text arrives is
    sent again once; after text, the visitor has seen part of the answer,
    so the break raises and the turn ends on ANSWER_ERROR_MESSAGE.
    """
    final = None
    raw = ""
    shown = ""

    def _show(at_end: bool) -> None:
        nonlocal shown
        text = normalize_dashes(raw if at_end else raw.rstrip(_DASH_HOLD_CHARS))
        if on_delta is not None and len(text) > len(shown):
            on_delta(text[len(shown) :])
            shown = text

    for attempt in (1, 2):
        try:
            for event in client.responses.create(stream=True, **request):
                kind = getattr(event, "type", "")
                if kind == "response.output_text.delta":
                    raw += event.delta
                    _show(at_end=False)
                elif kind in _STREAM_END_EVENTS:
                    _show(at_end=True)
                    final = event.response
                elif kind in ("response.failed", "error"):
                    raise RuntimeError(f"Ask Agy answer call failed: {kind}")
            break
        except httpx.TransportError as e:
            if raw or attempt == 2:
                raise
            logger.warning(
                "Ask Agy stream broke before any answer text (%s: %s); sending it again",
                type(e).__name__,
                e,
            )
    if final is None:
        raise RuntimeError("Ask Agy answer stream ended without a response")
    return final


def agy_answer(
    question: str,
    stories: list[dict[str, Any]],
    history: list[dict[str, str]] | None = None,
    on_delta: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Answer an Ask Agy question through the tool-calling loop (MATTGPT-275).

    The nonsense rules and the router's out_of_scope / personal redirects
    still run first. The model then gets build_tool_system_prompt() (persona,
    MATT_DNA, profile, the tool note and the per-answer instructions;
    synthesis voice when the router says synthesis), the conversation, and
    the question as asked. Its first call must search; it may search again
    up to ASK_TOOL_MAX_ROUNDS rounds in all, then one more call must answer.
    Search confidence does not gate the answer.

    Every call is a streamed Responses API call on ASK_ANSWER_MODEL. Answer
    text deltas reach on_delta as they arrive; the returned answer_md is the
    whole text after _postprocess_agy_text(), with the stories the searches
    returned, which are also the sources (stream, then swap).

    Returns the dict the UI renders (answer_md, sources, modes, default_mode).
    """
    force_answer = bool(st.session_state.pop("__ask_force_answer__", False))
    from_suggestion = (
        bool(st.session_state.pop("__ask_from_suggestion__", False)) or force_answer
    )
    obs: dict[str, Any] = {
        "intent_family": None,
        "confidence": None,
        "entity_match": None,
        "rejection_reason": None,
    }

    rejected = _nonsense_rejection(question, from_suggestion, obs)
    if rejected:
        return rejected

    intent_family, semantic_score = "", 1.0
    if not from_suggestion:
        _valid, semantic_score, _matched, intent_family = is_portfolio_query_semantic(
            question or ""
        )
        obs["intent_family"] = intent_family
    rejected = _router_rejection(
        question, intent_family, semantic_score, from_suggestion, obs
    )
    if rejected:
        return rejected

    is_synthesis = intent_family == "synthesis"
    # Source cards use the 3-card layout: they are the stories the model used.
    st.session_state["__ask_query_intent__"] = None

    profile_facts = load_matt_profile()
    _opening, focus = _choose_opening_and_focus(is_synthesis)
    items: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": build_tool_system_prompt(
                is_synthesis=is_synthesis,
                matt_dna=MATT_DNA,
                profile_facts=profile_facts,
                opener_examples=SYNTHESIS_OPENERS + STANDARD_OPENERS,
                focus_angle=focus,
            ),
        },
        *(history or []),
        {"role": "user", "content": question},
    ]

    used: list[dict[str, Any]] = []
    top_score = 0.0
    text = ""
    try:
        client = _openai_client()
        for round_no in range(ASK_TOOL_MAX_ROUNDS + 1):
            last_round = round_no == ASK_TOOL_MAX_ROUNDS
            if last_round:
                tool_choice = "none"
            elif round_no == 0:
                tool_choice = "required"
            else:
                tool_choice = "auto"
            response = _stream_response(
                client,
                on_delta,
                model=ASK_ANSWER_MODEL,
                reasoning={"effort": ASK_ANSWER_REASONING_EFFORT},
                max_output_tokens=ASK_ANSWER_MAX_OUTPUT_TOKENS,
                input=items,
                tools=[_SEARCH_STORIES_TOOL],
                tool_choice=tool_choice,
            )
            calls = [
                o for o in response.output if getattr(o, "type", "") == "function_call"
            ]
            if not calls or last_round:
                text = response.output_text or ""
                break
            if response.output_text:
                items.append({"role": "assistant", "content": response.output_text})
            items.extend(
                {
                    "type": "function_call",
                    "call_id": c.call_id,
                    "name": c.name,
                    "arguments": c.arguments,
                }
                for c in calls
            )
            for c in calls:
                output, found, score = _run_search_tool(c.arguments, stories)
                top_score = max(top_score, score)
                seen = {s.get("id") for s in used}
                used.extend(s for s in found if s.get("id") not in seen)
                items.append(
                    {
                        "type": "function_call_output",
                        "call_id": c.call_id,
                        "output": output,
                    }
                )
            if st.session_state.pop("__embed_failure__", False):
                return {
                    "answer_md": "🐾 I need a quick breather: please try again in a moment!",
                    "sources": [],
                    "modes": {},
                    "default_mode": "narrative",
                    **obs,
                }
    except Exception as e:
        err_lower = str(e).lower()
        if "429" in str(e) or "rate_limit" in err_lower or "rate limit" in err_lower:
            return {
                "answer_md": "🐾 I need a quick breather: try again in about 15 seconds!",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
                **obs,
            }
        if DEBUG:
            print(f"DEBUG agy_answer fatal error: {e}")
        logger.exception("agy_answer fatal error: %s", e)
        return {
            "answer_md": ANSWER_ERROR_MESSAGE,
            "sources": [],
            "modes": {},
            "default_mode": "narrative",
            "degraded": True,
            **obs,
        }

    answer_md, profile_categories = _postprocess_agy_text(text, used)
    sources = [
        {"id": s["id"], "title": s.get("Title", ""), "client": s.get("Client", "")}
        for s in used
    ]

    log_query(
        question or "",
        "Ask Agy",
        intent_family=intent_family,
        result_count=len(sources),
        top_score=top_score,
    )

    return {
        "answer_md": answer_md,
        "sources": sources,
        "profile_categories": profile_categories,
        "modes": {"narrative": answer_md},
        "default_mode": "narrative",
        "degraded": False,
        **obs,
    }


def send_to_backend(
    prompt: str,
    filters: dict[str, Any],
    ctx: dict[str, Any] | None,
    stories: list[dict[str, Any]],
    on_delta: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Ask Agy's entry point from the UI.

    Delegates to agy_answer() (MATTGPT-275), passing the recent conversation
    from st.session_state["ask_transcript"] as history.

    Args:
        prompt: User query string.
        filters: Unused (agy_answer's search tool takes no facet filters);
            kept for API compatibility.
        ctx: Context dictionary (unused, kept for API compatibility).
        stories: Full list of portfolio stories.
        on_delta: Called with each piece of answer text as it streams in.

    Returns:
        Answer dictionary with keys: answer_md, sources, profile_categories,
        modes, default_mode.
    """
    history = _build_history_messages(st.session_state.get("ask_transcript", []))
    return agy_answer(prompt, stories, history=history, on_delta=on_delta)


def _build_history_messages(transcript: list[dict]) -> list[dict[str, str]]:
    """Turn ask_transcript entries into prior chat messages for the Agy call.

    Entries carry the role as "role" (push_user_turn, push_assistant_turn) or
    "Role" (push_conversational_answer, banners); both are read. Entries with
    no text, such as rejection banners, are skipped. The current question is
    already the last entry when send_to_backend() runs, so a trailing user
    message is dropped. Keeps the last ASK_HISTORY_MAX_MESSAGES messages.
    """
    messages: list[dict[str, str]] = []
    for entry in transcript or []:
        role = entry.get("role") or entry.get("Role")
        text = entry.get("text")
        if role in ("user", "assistant") and text:
            messages.append({"role": role, "content": text})
    if messages and messages[-1]["role"] == "user":
        messages.pop()
    return messages[-ASK_HISTORY_MAX_MESSAGES:]
