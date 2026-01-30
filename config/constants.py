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
# Below SOFT_ACCEPT = router rejects (but search fallback may still work)

# =============================================================================
# RAG CONFIDENCE THRESHOLDS
# =============================================================================
# Used by rag_service.py for confidence gating

CONFIDENCE_HIGH = 0.25  # Strong match - show "Found X stories"
CONFIDENCE_LOW = 0.20  # Raised from 0.15 to filter phantom similarity noise

# =============================================================================
# PINECONE THRESHOLDS
# =============================================================================

PINECONE_MIN_SIM = 0.15  # Minimum similarity for Pinecone results
SEARCH_TOP_K = 10  # Stories to fetch from Pinecone (headroom for reranking/filtering)

# =============================================================================
# ENTITY GATE THRESHOLD
# =============================================================================
# Used by backend_service.py to decide if a query passes the semantic gate

ENTITY_GATE_THRESHOLD = 0.30  # Lowered from 0.55 to allow narrative queries (Jan 2026)

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
]

# =============================================================================
# ENTITY DETECTION FIELDS
# =============================================================================
# Used by detect_entity() to check if a query mentions a known entity.
# INTENTIONALLY different from ENTITY_SEARCH_FIELDS.
#
# Why only 3 fields:
# - Project and Place removed Jan 2026 - too many generic values caused false positives
#   (e.g., "innovation" matching Project="Innovation", "Technology" matching Division)
# - Semantic search handles these variations naturally through embeddings
#
# DO NOT "fix" this to match ENTITY_SEARCH_FIELDS - the difference is intentional.
# Detection is CONSERVATIVE (avoid false positives), Search is LIBERAL (maximize recall).

ENTITY_DETECTION_FIELDS = ["Client", "Employer", "Division"]

# =============================================================================
# ENTITY SEARCH FIELDS
# =============================================================================
# Once an entity is confirmed by detect_entity(), search broadly across these fields.
# INTENTIONALLY different from ENTITY_DETECTION_FIELDS.
#
# Why 5 fields here vs 3 in detection:
# - Detection is CONSERVATIVE (avoid false positives like "Technology")
# - Search is LIBERAL (maximize recall once we have a confirmed entity)
#
# DO NOT "fix" this to match ENTITY_DETECTION_FIELDS - the difference is intentional.
#
# NOTE: Field names are lowercase to match Pinecone metadata schema.

ENTITY_SEARCH_FIELDS = ["client", "employer", "division", "project", "place", "title"]

# Pinecone metadata casing rules (from CLAUDE.md):
# - Lowercase values: division, employer, project, industry, complexity
# - PascalCase values: client, role, title, domain
PINECONE_LOWERCASE_FIELDS = {"division", "employer", "project", "place"}

# =============================================================================
# EXCLUDED VALUES
# =============================================================================
# Values that exist in entity fields but should NOT trigger entity detection.
# These are common English words that cause false positives.

EXCLUDED_DIVISION_VALUES = {"Technology"}  # "technology experience" ≠ Division filter
