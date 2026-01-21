"""
Semantic Router for Query Intent Classification

Uses embedding similarity to determine if a query is relevant to Matt's portfolio.
More reliable than LLM-based guards which are inconsistent.

Features:
- Intent families for organized debugging
- Dual threshold (hard accept / soft accept / reject)
- Returns best matching intent for telemetry
- Caches embeddings to disk
"""

import os

import numpy as np

# =============================================================================
# THRESHOLDS
# =============================================================================
HARD_ACCEPT = 0.80  # Clearly on-topic, no question
SOFT_ACCEPT = 0.72  # Accept but log as borderline for review
# Below SOFT_ACCEPT = router rejects (but search fallback may still work)

# =============================================================================
# CANONICAL INTENTS BY FAMILY
# =============================================================================
VALID_INTENTS = {
    "background": [
        "Give me a quick overview of Matt's experience",
        "Tell me about Matt's background",
        "Tell me about Matt's background and leadership journey",
        "Walk me through Matt's career",
        "What has Matt accomplished in his career?",
        "What has Matt accomplished?",
        "Who is Matt Pugmire?",
        "Who is Matt?",
        "What's Matt's professional experience?",
    ],
    "behavioral": [
        "Tell me about a time Matt failed",
        "Tell me about a time you failed",
        "Tell me about a time Matt resolved team conflict",
        "Tell me about a time you disagreed with leadership",
        "Describe a situation where Matt had to influence stakeholders",
        "How do you handle conflict?",
        "Give me an example of leadership",
        "Give me an example of when Matt showed leadership",
        "Tell me about a difficult situation you handled",
        "Describe a difficult situation Matt handled",
        "How did Matt handle a challenging project?",
        "Tell me about a time you had to make a tough decision",
        "Describe a failure and what you learned",
        "How do you handle disagreements with your manager?",
        "Tell me about a challenge Matt overcame",
    ],
    "delivery": [
        "How did Matt achieve 4x faster delivery?",
        "How does Matt ensure teams deliver faster and with higher quality?",
        "How did Matt accelerate team delivery?",
        "Show me Matt's biggest delivery transformation wins",
        "Show me Matt's biggest delivery wins",
        "What results has Matt achieved?",
    ],
    "team_scaling": [
        "How did Matt scale teams from 4 to 150+?",
        "How did Matt build high-performing teams?",
        "Tell me about Matt's team building experience",
        "How does Matt grow engineering organizations?",
    ],
    "leadership": [
        "What's Matt's leadership style?",
        "What's Matt's approach to leadership?",
        "How does Matt lead teams?",
        "What's Matt's management philosophy?",
        "How does Matt coach and develop people?",
    ],
    "technical": [
        "What is Matt's experience with modern engineering and cloud platforms?",
        "Show me Matt's platform engineering work",
        "Tell me about Matt's cloud modernization projects",
        "Tell me about Matt's cloud projects",
        "What's Matt's experience with microservices?",
        "Show me Matt's GenAI work",
        "What's Matt's GenAI experience?",
        "What's Matt's technical background?",
        "Tell me about Matt's architecture experience",
    ],
    "domain_payments": [
        "Show me Matt's payments modernization work",
        "Tell me about Matt's financial services experience",
        "What's Matt's experience in banking?",
        "Show me Matt's work with JPMC",
    ],
    "domain_healthcare": [
        "Show me healthcare projects",
        "What's Matt's experience in life sciences?",
    ],
    "stakeholders": [
        "How does Matt handle difficult stakeholders?",
        "Tell me about Matt's stakeholder management",
        "How does Matt work with executives?",
        "How does Matt manage up?",
    ],
    "innovation": [
        "What's Matt's approach to innovation leadership?",
        "Tell me about Matt's innovation center work",
        "How does Matt drive innovation?",
        "Tell me about the Accenture Innovation Center",
    ],
    "agile_transformation": [
        "How did Matt scale agile across organizations?",
        "Tell me about Matt's agile transformation work",
        "Tell me about Matt's transformation work",
        "What's Matt's experience with digital transformation?",
        "How does Matt approach organizational change?",
    ],
    # =================================================================
    # NARRATIVE FAMILY (Jan 2026 - Sovereign Narrative Update)
    # These intents map to Professional Narrative stories that express
    # Matt's identity, philosophy, and career journey. Added to ensure
    # the semantic router recognizes these biographical queries.
    # =================================================================
    "narrative": [
        "Tell me about Matt's leadership journey",
        "About Matt's leadership journey",
        "What's Matt's career intent?",
        "What is Matt looking for next?",
        "Career Intent – What I'm Looking For Next",
        "How does Matt approach complex problems?",
        "How I Approach Complex, Ambiguous Problems",
        "What's Matt's leadership philosophy?",
        "How does Matt lead?",
        "Leadership Philosophy – How I Lead",
        "Why is Matt exploring opportunities?",
        "Transition Story – Why I'm Exploring Opportunities",
        "Where does Matt do his best work?",
        "Work Philosophy – Where I Do My Best Work",
        "What did Matt learn about risk ownership?",
        "What I Learned About Assumptions and Risk Ownership",
        "Why is early failure important?",
        "Why Early Failure Is a Feature, Not a Bug, in Innovation",
        "What did Matt learn about sustainable leadership?",
        "What I Learned About Sustainable Leadership",
        "Matt's career transition after Accenture",
        "Making an Intentional Career Transition After Accenture",
    ],
}

# Flatten for embedding generation
ALL_VALID_INTENTS = []
INTENT_TO_FAMILY = {}
for family, intents in VALID_INTENTS.items():
    for intent in intents:
        ALL_VALID_INTENTS.append(intent)
        INTENT_TO_FAMILY[intent] = family

# Queries that should be rejected
INVALID_INTENTS = [
    "What's the weather today?",
    "Who won the Super Bowl?",
    "Write me a poem about cats",
    "Explain quantum physics",
    "What's the capital of France?",
    "Tell me a joke",
    "What's Bitcoin worth?",
    "How do I cook pasta?",
]

# =============================================================================
# CACHE
# =============================================================================
_intent_embeddings_cache: dict | None = None


def _get_embedding(text: str) -> list[float]:
    """Get embedding for a single text using OpenAI."""
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv()

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        project=os.getenv("OPENAI_PROJECT_ID"),
        organization=os.getenv("OPENAI_ORG_ID"),
    )

    response = client.embeddings.create(input=text, model="text-embedding-3-small")

    return response.data[0].embedding


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    a_np = np.array(a)
    b_np = np.array(b)
    return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))


def _get_intent_embeddings() -> dict[str, list[float]]:
    """Get cached embeddings for all valid intents."""
    global _intent_embeddings_cache

    if _intent_embeddings_cache is not None:
        return _intent_embeddings_cache

    # Check for cached file first
    cache_path = "data/intent_embeddings.json"
    if os.path.exists(cache_path):
        try:
            import json

            with open(cache_path) as f:
                data = json.load(f)
            # Handle both old format (flat) and new format (nested with "embeddings" key)
            if "embeddings" in data:
                _intent_embeddings_cache = data["embeddings"]
            else:
                _intent_embeddings_cache = data
            return _intent_embeddings_cache
        except Exception:
            pass

    # Generate embeddings
    _intent_embeddings_cache = {}
    for intent in ALL_VALID_INTENTS:
        _intent_embeddings_cache[intent] = _get_embedding(intent)

    # Cache to disk
    try:
        os.makedirs("data", exist_ok=True)
        import json

        with open(cache_path, 'w') as f:
            json.dump(_intent_embeddings_cache, f)
    except Exception:
        pass

    return _intent_embeddings_cache


def is_portfolio_query_semantic(
    query: str,
    hard_threshold: float = HARD_ACCEPT,
    soft_threshold: float = SOFT_ACCEPT,
) -> tuple[bool, float, str, str]:
    """
    Check if query is relevant to Matt's portfolio using embedding similarity.

    Args:
        query: User's query string
        hard_threshold: Score above this = clearly valid (default 0.80)
        soft_threshold: Score above this = valid but borderline (default 0.72)

    Returns:
        Tuple of (is_valid, max_similarity_score, best_matching_intent, intent_family)

    Example:
        >>> is_valid, score, intent, family = is_portfolio_query_semantic("Tell me about Matt's background")
        >>> is_valid
        True
        >>> family
        "background"
    """
    try:
        query_embedding = _get_embedding(query)
        intent_embeddings = _get_intent_embeddings()

        max_similarity = 0.0
        best_intent = ""

        for intent, intent_emb in intent_embeddings.items():
            similarity = _cosine_similarity(query_embedding, intent_emb)
            if similarity > max_similarity:
                max_similarity = similarity
                best_intent = intent

        family = INTENT_TO_FAMILY.get(best_intent, "unknown")
        is_valid = max_similarity >= soft_threshold

        # Log borderline cases for review
        if soft_threshold <= max_similarity < hard_threshold:
            _log_borderline(query, max_similarity, best_intent, family)

        return is_valid, max_similarity, best_intent, family

    except Exception as e:
        # Fail open if embedding fails
        print(f"Semantic router error: {e}")
        return True, 1.0, "", "error_fallback"


def _log_borderline(query: str, score: float, intent: str, family: str):
    """Log borderline queries for later review."""
    import csv
    from datetime import UTC, datetime

    path = "data/borderline_queries.csv"
    try:
        os.makedirs("data", exist_ok=True)
        write_header = not os.path.exists(path)

        with open(path, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(["timestamp", "query", "score", "matched_intent", "family"])
            w.writerow(
                [
                    datetime.now(UTC).isoformat(timespec="seconds"),
                    query,
                    f"{score:.3f}",
                    intent,
                    family,
                ]
            )
    except Exception:
        pass  # Don't break the app for logging


def warm_cache():
    """Pre-compute and cache intent embeddings."""
    from config.debug import DEBUG

    if DEBUG:
        print("Warming semantic router cache...")
    embeddings = _get_intent_embeddings()
    if DEBUG:
        print(
            f"Cached {len(embeddings)} intent embeddings across {len(VALID_INTENTS)} families"
        )


def get_intent_families() -> list[str]:
    """Get list of all intent family names."""
    return list(VALID_INTENTS.keys())


def get_intents_by_family(family: str) -> list[str]:
    """Get canonical intents for a specific family."""
    return VALID_INTENTS.get(family, [])


# =============================================================================
# CLI for testing
# =============================================================================
if __name__ == "__main__":
    warm_cache()

    print("\n" + "=" * 70)
    print("TESTING SEMANTIC ROUTER")
    print("=" * 70)

    test_queries = [
        # Should pass (various families)
        "Tell me about Matt's background",
        "Tell me about a time you failed",
        "How did Matt scale teams?",
        "What's Matt's leadership style?",
        "Show me payments work",
        # Should fail
        "What's the weather?",
        "Write me a poem",
        # Edge cases (typos, vague, overly polite)
        "Tell me abot Matts backgroun",
        "Matt's leadership?",
        "Could you maybe tell me a little about Matt's experience?",
    ]

    for q in test_queries:
        is_valid, score, intent, family = is_portfolio_query_semantic(q)
        status = "✅" if is_valid else "❌"
        zone = (
            "HARD"
            if score >= HARD_ACCEPT
            else ("SOFT" if score >= SOFT_ACCEPT else "REJECT")
        )
        print(f"{status} [{zone:6}] {score:.3f} | {family:20} | {q}")
        if is_valid:
            print(
                f"   └─ matched: \"{intent[:50]}...\""
                if len(intent) > 50
                else f"   └─ matched: \"{intent}\""
            )
