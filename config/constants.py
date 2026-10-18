"""
Centralized Constants - Single Source of Truth

This file contains all application constants that must be consistent across the codebase.
NEVER duplicate these values in other files - always import from here.

Categories:
- Model names (LLM, embeddings)
- Thresholds (semantic router, RAG confidence, Pinecone)
- Banned/meta-commentary phrases (voice quality)
- Entity detection fields

To change a threshold or add a banned phrase, edit THIS file only.

Related:
- These constants are used at runtime. For data-derived values (like client lists),
  see the pattern in utils/client_utils.py which derives from story data.
"""

# =============================================================================
# MODEL NAMES
# =============================================================================
# These can be overridden via .env if needed (e.g., for cost testing)
# Usage: model = get_conf("CHAT_MODEL") or DEFAULT_CHAT_MODEL

DEFAULT_CHAT_MODEL = "gpt-4o"  # Primary LLM for responses
DEFAULT_CLASSIFICATION_MODEL = (
    "gpt-4o-mini"  # Lightweight model for intent classification
)
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dimensions

# =============================================================================
# SEMANTIC ROUTER THRESHOLDS
# =============================================================================
# Calibrated Jan 2026 from score analysis
# Garbage queries: 0.17-0.27 | Legitimate queries: 0.46-0.84

HARD_ACCEPT = 0.80  # Clearly on-topic, no question
SOFT_ACCEPT = 0.40  # Accept but log as borderline for review
# These are advisory. The router's valid flag does not reject queries:
# backend_service.py uses it only in is_trusted_behavioral, which can
# rescue a low-confidence query from the Pinecone gate but never causes
# a rejection. Explore Stories discards the flag entirely. The only
# rejection path is CONFIDENCE_LOW below.

# =============================================================================
# RAG CONFIDENCE THRESHOLDS
# =============================================================================
# Used by rag_service.py for confidence gating

CONFIDENCE_HIGH = 0.25  # Strong match - show "Found X stories"
CONFIDENCE_LOW = 0.20  # Raised from 0.15 to filter phantom similarity noise

# =============================================================================
# HYBRID SCORE WEIGHTS
# =============================================================================
# Single source of truth. utils/scoring.py and services/pinecone_service.py
# both import from here. Do not redefine locally.

W_PC = 1.0  # Pinecone semantic similarity weight
W_KW = 0.15  # Keyword overlap weight (raised from 0.0 Aug 8, 2026 -- f5641e7)

# =============================================================================
# PINECONE THRESHOLDS
# =============================================================================

PINECONE_MIN_SIM = 0.15  # Minimum similarity for Pinecone results
SEARCH_TOP_K = 25  # Stories to fetch from Pinecone (headroom for reranking/filtering)

# Intent families where "Matt"/"Matt's" is substituted with "he"/"his" in the
# retrieval query so self-referential name tokens don't bias embeddings toward
# Independent Project stories. The LLM receives the original query verbatim.
SUBSTITUTION_FAMILIES = frozenset({"technical", "team_scaling", "agile_transformation"})

# Ask Agy conversation history: prior transcript messages sent to the response
# LLM as user/assistant turns (two exchanges). The model writes its
# search_stories queries with them in view; the nonsense rules and the router
# see only the current question.
ASK_HISTORY_MAX_MESSAGES = 4

# Ask Agy answering model, called on the Responses API and streamed (the
# lever2_sol arm of MATTGPT-282 run 2). Pinned by name: the models list has
# no dated snapshot of it. It rejects temperature and max_tokens; reasoning
# tokens count against the output cap.
ASK_ANSWER_MODEL = "gpt-6.1-sol"
ASK_ANSWER_REASONING_EFFORT = "medium"
ASK_ANSWER_MAX_OUTPUT_TOKENS = 4000

# Longest wait, in seconds, on any one read of an Ask Agy answer stream
# (httpx's read timeout: the wait for the headers, then each wait between
# chunks). The longest silence measured was 3.52 s at p99 and 3.67 s at most
# over 279 calls (MATTGPT-275 gap probe), all before the first answer text;
# after it, 0.62 s at most. A stream that breaks before any text is sent
# again once (_stream_response()).
ASK_ANSWER_READ_TIMEOUT_S = 30

# Ask Agy tool loop: search rounds the model may take before its answer. After
# this many search_stories rounds, one more call is made with tool_choice
# "none" so the model must answer from what it has.
ASK_TOOL_MAX_ROUNDS = 3

# =============================================================================
# META-COMMENTARY PATTERNS
# =============================================================================
# LLM talking ABOUT the story instead of answering.
# These are HARD FAIL for marketing/landing page queries.
#
# Used by:
# - backend_service.py for post-processing cleanup (uses REGEX version)
# - eval_rag_quality.py for test validation (uses plain string version)

# Plain string patterns for substring matching (eval tests)
META_COMMENTARY_PATTERNS = [
    "this demonstrates",
    "this reflects",
    "this illustrates",
    "this showcases",
    "this highlights",
    "matt's ability to",
    "his ability to",
    "demonstrates his",
    "reflects his",
    "in essence",
    "in summary",
    "essentially",
    "this story shows",
    "this example demonstrates",
    "this reveals",
]

# Regex patterns with word boundaries for post-processing cleanup
META_COMMENTARY_REGEX_PATTERNS = [
    r"\bhis ability to\b",
    r"\bMatt's ability to\b",
    r"\bthis demonstrates\b",
    r"\bthis reflects\b",
    r"\bthis showcases\b",
    r"\bthis illustrates\b",
    r"\bdemonstrates his\b",
    r"\breflects his\b",
    r"\breflect his\b",
    r"\bdemonstrates a pattern\b",
    r"\bis evident\b",
    r"\bshowcases his\b",
    r"\bthese experiences highlight\b",
    r"\bhighlight Matt's\b",
]

# MATTGPT-250 item 4: profile categories Agy cites with a
# [[profile:<category>]] marker. These are the data/matt_profile.json keys
# load_matt_profile() renders. The marker instruction in rule 0a, the
# marker extractor, and the Sources fact row all read this tuple; the
# fact card display names come from PROFILE_FACT_DISPLAY_NAMES.
PROFILE_FACT_CATEGORIES = (
    "certifications",
    "education",
    "languages",
    "location_availability",
)
PROFILE_FACT_DISPLAY_NAMES = {
    "certifications": "Certifications",
    "education": "Education",
    "languages": "Languages",
    "location_availability": "Location & Availability",
}

# MATTGPT-250 step 2: Location & Availability fields, in display order, as
# (JSON key under data/matt_profile.json["logistics"], visitor label).
# Read by Role Match's _iter_location_cells() and by load_matt_profile(),
# so the screen block and the shared loader cannot drift.
PROFILE_LOCATION_AVAILABILITY_FIELDS = (
    ("location", "Location"),
    ("work_model", "Work model"),
    ("availability", "Availability"),
    ("authorization", "Authorization"),
)

# =============================================================================
# ENTITY SEARCH FIELDS
# =============================================================================
# Pinecone metadata fields an entity filter searches across.
#
# NOTE: Field names are lowercase to match Pinecone metadata schema.

ENTITY_SEARCH_FIELDS = ["client", "employer", "division", "project", "place", "title"]

# Pinecone metadata casing rules (from CLAUDE.md):
# - Lowercase values: division, employer, project, industry, complexity
# - PascalCase values: client, role, title, domain
PINECONE_LOWERCASE_FIELDS = {"division", "employer", "project", "place"}

# =============================================================================
# MONITORING BOT SIGNATURES
# =============================================================================
# User-Agent substrings for known monitoring/keep-alive bots.
# Requests matching any of these are excluded from page_load logging.
# Add new signatures here when new monitoring tools are configured.
# Note: UptimeRobot free tier sends empty User-Agent (no signature).
# It's caught by the empty User-Agent guard in app.py, not this list.
# The signature is kept here in case UptimeRobot changes behavior or
# is upgraded to a paid plan that sends identifiable headers.

# Chrome/103.0.0.0 is a stale user agent (released June 2022) seen
# hitting the app from Windows/UTC with no referrer: an automated
# crawler masquerading as a real browser. First observed Apr 11, 2026.
MONITORING_BOT_SIGNATURES = ["UptimeRobot", "HeadlessChrome", "Chrome/103.0.0.0"]

# =============================================================================
# QUERY LOG
# =============================================================================
# Zone for the Sheet's Timestamp column, so Cloud (UTC host) and local rows
# read the same wall-clock time.
QUERY_LOG_TIMEZONE = "America/New_York"

# =============================================================================
# PRIVATE VIEW (Phase 4, MATTGPT-012)
# =============================================================================
# Constants for the private view password gate (slice 1) and the agentic
# bypass header (slice 2). See BACKLOG.md MATTGPT-012 for the design contract.
# Named-constant convention: no magic strings in guard logic.

PRIVATE_MODE_KEY = "__private_mode__"  # st.session_state key
PRIVATE_BYPASS_TOKEN_ENV = "MATTGPT_PRIVATE_BYPASS_TOKEN"  # env / st.secrets key
PRIVATE_BYPASS_HEADER = "X-Mattgpt-Bypass-Token"  # request header (slice 2)


def get_private_bypass_token() -> str | None:
    """Return the configured private-view bypass token, or None if unset.

    Reads via get_conf() (st.secrets first, then os.environ). Used by both
    the password popover (slice 1) and the bypass header (slice 2). Callers
    must fail closed when this returns None.
    """
    from config.settings import get_conf

    return get_conf(PRIVATE_BYPASS_TOKEN_ENV)


# =============================================================================
# CAPABILITY_SUBTITLES
# =============================================================================
# Editorial-description layer for Solution/Offering values surfaced on landing
# pages (Banking, Cross-Industry). Mirrors the ERA_SUBTITLES pattern in
# ui/components/timeline_view.py: short descriptive phrase per category, falls
# through to empty string when a key is missing (cards render without
# description in that case).
#
# Curation = editorial polish; the card UNIVERSE is data-derived (which
# Solution/Offering values have stories), not driven by this dict.
#
# Contract: every key MUST be a valid Solution/Offering value in the current
# story data. Enforced by tests/unit/test_capability_subtitles.py, so CI fails
# loudly if any key drifts from the master data.
# =============================================================================

CAPABILITY_SUBTITLES: dict[str, str] = {
    # Banking + Cross-Industry shared
    "Global Payments & Treasury Solutions": "Payment platforms, treasury systems, real-time processing",
    "Modern Engineering Practices & Solutions": "DevOps, CI/CD, cloud-native engineering, modern toolchains",
    "Technology Strategy & Advisory": "Architecture roadmaps, strategic planning, technology vision",
    "Agile Transformation & Delivery": "Scaling agile practices, delivery acceleration, team transformation",
    "Program Management & Governance": "Large-scale program delivery, governance frameworks, PMO",
    "Data & Analytics Solutions": "Data platforms, analytics, business intelligence",
    "Cross-Functional Collaboration & Team Enablement": "Team alignment, collaboration frameworks, culture change",
    "Business Process Optimization": "Process reengineering, workflow automation, efficiency",
    "Enterprise Integration & API Management": "API platforms, integration architecture, service mesh",
    "Digital Product Development": "Mobile banking, customer experiences, digital channels",
    "DevOps & Continuous Delivery": "Automation, deployment pipelines, continuous integration",
    "Application Modernization": "Legacy modernization, microservices, platform engineering",
    # Banking-specific values previously orphaned (no card existed for them)
    "Security & Compliance Solutions": "Regulatory frameworks, audit support, risk management",
    "VPP Adoption Enablement & Developer Toolkit": "Developer experience, tooling, productivity platforms",
    "Program Recovery & Vendor Delivery Management": "Troubled program recovery, vendor governance, delivery rescue",
    "Enterprise Application Integration": "System connectivity, middleware, message brokers",
    # Cross-Industry-specific
    "Client Enablement & Sustainable Innovation": "Knowledge transfer, capability building, sustainable practices",
    "Product Management & Innovation Labs": "Innovation programs, experimentation, lean startup methodology",
    "User-Centered Design & Experience": "UX research, design thinking, customer journey mapping",
    "Platform Optimization & Cloud-Native Development": "Platform engineering, developer experience, service catalogs",
    "Modern Product Engineering Methodology": "Product thinking, rapid prototyping, product-market fit",
    "AI & Machine Learning Solutions": "AI strategy, ML platforms, intelligent automation",
    "Rapid Prototyping & Innovation Enablement": "Design sprints, MVP prototyping, innovation coaching",
}

# =============================================================================
# WRITING RULES
# =============================================================================
# Sent to the model call that writes Ask Agy's answers, through
# build_answer_instructions(). It took answers with a dash from 42 of 55 to
# 4 of 55, each of those a number range (MATTGPT-275 four-arm dash run);
# normalize_dashes() in backend_service.py stays as the backstop on Ask
# Agy's output. Role Match's prompts don't carry it: on gpt-4o its
# model-written text had no dash with or without the rule.
NO_DASH_RULE = (
    "Don't use em dashes or en dashes; use a comma, a colon, parentheses or a "
    "separate sentence, whichever fits."
)

# Sent on the line after NO_DASH_RULE, through build_answer_instructions().
# On "Which was bigger?" after a Fiserv and JP Morgan ACCESS comparison (a
# 45-person team against 40+, and reach figures only one side has), passing
# answers went from 3 of 10 to 10 of 10, with the c01 and c12 t1 controls
# unchanged at 10 of 10 (MATTGPT-275 control isolation run).
COMPARISON_RULE = (
    "When asked which of two things was bigger or better, compare only on a "
    "measure the stories give for both, in the same units. If their figures "
    "can't settle it (an open-ended figure against an exact one, or two "
    "different measures), say the stories don't establish which is larger."
)
