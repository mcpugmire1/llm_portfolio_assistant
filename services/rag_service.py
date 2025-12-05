"""RAG (Retrieval-Augmented Generation) service - semantic search orchestration."""

import streamlit as st

from config.debug import DEBUG
from services.pinecone_service import (
    SEARCH_TOP_K,
    pinecone_semantic_search,
)
from utils.formatting import build_5p_summary
from utils.validation import _tokenize

# Known vocab (built from stories)
_KNOWN_VOCAB: set[str] = set()

# =============================================================================
# CONFIDENCE THRESHOLDS (centralized)
# =============================================================================
CONFIDENCE_HIGH = 0.25  # Strong match - show "Found X stories"
CONFIDENCE_LOW = 0.15  # Borderline - show "Relevance may be low"
# Below CONFIDENCE_LOW = "none" - show "No strong matches"


def initialize_vocab(stories: list[dict]):
    """Build vocabulary from story corpus. Call once at startup."""
    global _KNOWN_VOCAB
    if _KNOWN_VOCAB:
        return  # Already built

    for s in stories:
        # Add tokens from key fields
        for field in ["title", "client", "domain", "5PSummary"]:
            if s.get(field):
                _KNOWN_VOCAB.update(_tokenize(str(s[field])))

        # Add tags
        if s.get("tags"):
            for tag in s["tags"]:
                _KNOWN_VOCAB.update(_tokenize(str(tag)))

    if DEBUG:
        print(f"📚 Built vocab: {len(_KNOWN_VOCAB)} unique tokens")


def semantic_search(
    query: str,
    filters: dict,
    *,
    enforce_overlap: bool = False,
    min_overlap: float = 0.0,
    stories: list,
    top_k: int = SEARCH_TOP_K,
) -> dict:
    """
    Pinecone-first semantic retrieval with confidence gating.

    Returns:
        {
            "results": List of relevant stories (each with "pc" score attached),
            "confidence": "high" | "low" | "none",
            "top_score": float (highest Pinecone similarity score),
        }
    """
    # Import matches_filters here to avoid circular dependency
    from utils.filters import matches_filters
    from utils.validation import token_overlap_ratio

    q = (query or "").strip()

    # Default return for empty query
    if not q:
        return {"results": [], "confidence": "none", "top_score": 0.0}

    # 1) Try Pinecone first
    hits = pinecone_semantic_search(q, filters, stories, top_k=top_k) or []
    st.session_state["__pc_suppressed__"] = False

    # 2) No hits from Pinecone
    if not hits:
        # Fallback to local keyword filtering if overlap check passes
        if enforce_overlap:
            ov = token_overlap_ratio(q, _KNOWN_VOCAB)
            if ov < float(min_overlap or 0.0) and not st.session_state.get(
                "__ask_from_suggestion__"
            ):
                st.session_state["__dbg_pc_hits"] = 0
                return {"results": [], "confidence": "none", "top_score": 0.0}

        # Local keyword fallback
        local = [s for s in stories if matches_filters(s, filters)]
        st.session_state["__dbg_pc_hits"] = 0
        st.session_state["__last_ranked_sources__"] = [s["id"] for s in local[:10]]

        # Local results get "low" confidence (no semantic validation)
        return {
            "results": local,
            "confidence": "low" if local else "none",
            "top_score": 0.0,
        }

    # 3) Calculate confidence from top Pinecone score
    top_score = max(h.get("pc_score", 0.0) or 0.0 for h in hits)

    if top_score >= CONFIDENCE_HIGH:
        confidence = "high"
    elif top_score >= CONFIDENCE_LOW:
        confidence = "low"
    else:
        confidence = "none"

    if DEBUG:
        print(f"DEBUG Confidence: top_score={top_score:.3f} -> {confidence}")

    # 4) Filter and prepare results based on confidence
    if confidence == "none":
        # Don't return garbage results
        st.session_state["__pc_suppressed__"] = True
        st.session_state["__dbg_pc_hits"] = len(hits)
        return {"results": [], "confidence": "none", "top_score": top_score}

    # 5) For high/low confidence, filter stories above minimum threshold
    confident_hits = [
        h for h in hits if (h.get("pc_score", 0.0) or 0.0) >= CONFIDENCE_LOW
    ]

    if not confident_hits:
        st.session_state["__pc_suppressed__"] = True
        confident_hits = hits[:3]  # Fallback to top 3

    # Persist scores for UI display
    try:
        st.session_state["__pc_last_ids__"] = {
            h["story"]["id"]: float(h.get("pc_score", 0.0) or 0.0)
            for h in confident_hits
        }
        st.session_state["__pc_snippets__"] = {
            h["story"]["id"]: (h.get("snippet") or build_5p_summary(h["story"]))
            for h in confident_hits
        }
        st.session_state["__last_ranked_sources__"] = [
            h["story"]["id"] for h in confident_hits
        ]
        st.session_state["__dbg_pc_hits"] = len(hits)
    except Exception:
        pass

    # 6) Apply UI filters and attach scores to stories
    filtered_stories = []
    for h in confident_hits:
        story = h["story"].copy()  # Don't mutate original
        story["pc"] = h.get("pc_score", 0.0) or 0.0
        if matches_filters(story, filters):
            filtered_stories.append(story)

    # If filters removed everything, return unfiltered confident hits
    if not filtered_stories:
        for h in confident_hits:
            story = h["story"].copy()
            story["pc"] = h.get("pc_score", 0.0) or 0.0
            filtered_stories.append(story)

    return {
        "results": filtered_stories,
        "confidence": confidence,
        "top_score": top_score,
    }
