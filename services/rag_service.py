"""RAG (Retrieval-Augmented Generation) service - semantic search orchestration."""

import streamlit as st

from config.debug import DEBUG
from services.pinecone_service import (
    SEARCH_TOP_K,
    pinecone_semantic_search,
)
from utils.formatting import build_5p_summary
from utils.validation import _tokenize


def _safe_session_set(key: str, value):
    """Safely set session state, no-op outside Streamlit context."""
    try:
        st.session_state[key] = value
    except Exception:
        pass


# Known vocab (built from stories)
_KNOWN_VOCAB: set[str] = set()

# =============================================================================
# CONFIDENCE THRESHOLDS (centralized)
# =============================================================================
CONFIDENCE_HIGH = 0.25  # Strong match - show "Found X stories"
CONFIDENCE_LOW = (
    0.20  # Raised from 0.15 to filter phantom similarity noise (e.g., "peanut butter")
)
# Below CONFIDENCE_LOW = "none" - show "No strong matches"

# =============================================================================
# PROFESSIONAL NARRATIVE BOOSTING (Jan 2026 - Sovereign Narrative Update)
# Dynamically derives title fragments from story data instead of hardcoded list.
# Handles title formats like "About Matt – My Leadership Journey" by stripping
# prefixes and extracting key phrases for query matching.
# =============================================================================


def _get_narrative_fragments(stories: list[dict]) -> list[tuple[str, dict]]:
    """Extract title fragments from Professional Narrative stories.

    Returns list of (lowercase_title, story) tuples for matching.
    Derives fragments dynamically instead of hardcoding.
    """
    return [
        (s.get("Title", "").lower(), s)
        for s in stories
        if s.get("Theme") == "Professional Narrative" and s.get("Title")
    ]


def boost_narrative_matches(
    query: str, results: list[dict], stories: list[dict]
) -> list[dict]:
    """Force-include Professional Narrative stories when query matches title.

    For biographical queries like "Tell me about Matt's leadership journey",
    ensures the matching Professional Narrative story is at the top of results
    even if semantic search ranked other stories higher.

    Now derives fragments dynamically from story titles rather than hardcoded list.

    Args:
        query: User's query string
        results: Current search results from semantic_search
        stories: Full story corpus (to find complete story objects)

    Returns:
        Results list with matching Professional Narrative story boosted to top
    """
    q_lower = query.lower()

    # Get narrative stories with their titles (dynamic, not hardcoded)
    narrative_stories = _get_narrative_fragments(stories)

    for title_lower, story in narrative_stories:
        # Extract key phrases from title - handle various title formats
        # e.g., "About Matt – My Leadership Journey" → "leadership journey"
        # e.g., "Career Intent – What I'm Looking For Next" → "career intent", "looking for next"
        key_phrase = title_lower

        # Remove common title prefixes
        for prefix in [
            "about matt – ",
            "about matt - ",
            "my ",
            "matt's ",
            "the ",
            "what i learned about ",
        ]:
            if key_phrase.startswith(prefix):
                key_phrase = key_phrase[len(prefix) :]
                break

        # Extract BOTH parts of split titles like "Transition Story – Why I'm Exploring Opportunities"
        # prefix_phrase = "transition story", subtitle_phrase = "why i'm exploring opportunities"
        prefix_phrase = None
        subtitle_phrase = None
        if " – " in title_lower:
            parts = title_lower.split(" – ")
            prefix_phrase = parts[0].strip()
            subtitle_phrase = parts[1].strip() if len(parts) > 1 else None
        elif " - " in title_lower:
            parts = title_lower.split(" - ")
            prefix_phrase = parts[0].strip()
            subtitle_phrase = parts[1].strip() if len(parts) > 1 else None

        # Check for matches - any key phrase in query
        matched = False
        if key_phrase in q_lower or title_lower in q_lower:
            matched = True
        elif prefix_phrase and prefix_phrase in q_lower:
            matched = True
        elif subtitle_phrase and subtitle_phrase in q_lower:
            matched = True
        # Also check for partial subtitle match (e.g., "exploring opportunities" in "why i'm exploring opportunities")
        elif subtitle_phrase:
            # Extract core phrase from subtitle by removing common starters
            # Jan 2026 - Normalize curly apostrophe (U+2019) to straight (') for matching
            # Story data uses Unicode curly apostrophe but starters use ASCII
            core_subtitle = subtitle_phrase.replace("\u2019", "'")
            for starter in ["why i'm ", "what i'm ", "how i ", "where i "]:
                if core_subtitle.startswith(starter):
                    core_subtitle = core_subtitle[len(starter) :]
                    break
            if core_subtitle in q_lower:
                matched = True

        if matched:
            # Remove if already in results, then insert at top
            results = [r for r in results if r.get("id") != story.get("id")]
            results.insert(0, story)
            if DEBUG:
                print(
                    f"DEBUG boost_narrative: boosted '{story.get('Title')}' for query match"
                )
            break

    return results


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
            "relaxed_count": int (optional - count of results without industry/capability filters),
            "active_filters": list (optional - which filters caused 0 results),
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
        _safe_session_set("__pc_suppressed__", True)
        confident_hits = hits[:3]  # Fallback to top 3

    # Persist scores for UI display
    _safe_session_set(
        "__pc_last_ids__",
        {
            h["story"]["id"]: float(h.get("pc_score", 0.0) or 0.0)
            for h in confident_hits
        },
    )
    _safe_session_set(
        "__pc_snippets__",
        {
            h["story"]["id"]: (h.get("snippet") or build_5p_summary(h["story"]))
            for h in confident_hits
        },
    )
    _safe_session_set(
        "__last_ranked_sources__", [h["story"]["id"] for h in confident_hits]
    )
    _safe_session_set("__dbg_pc_hits", len(hits))

    # 6) Apply UI filters and attach scores to stories
    # Jan 2026 - Strip q from filters: Pinecone already did semantic matching on query.
    # Passing q to matches_filters() causes double-filtering (keyword match on semantic results).
    ui_filters = {k: v for k, v in filters.items() if k != "q"} if filters else {}
    filtered_stories = []
    for h in confident_hits:
        story = h["story"].copy()  # Don't mutate original
        story["pc"] = h.get("pc_score", 0.0) or 0.0
        if matches_filters(story, ui_filters):
            filtered_stories.append(story)

    # 7) If filters removed everything, check what we'd get without industry/capability
    if not filtered_stories and (filters.get("industry") or filters.get("capability")):
        # Also strip q here - same reason as above
        relaxed_filters = {
            k: v for k, v in filters.items() if k not in ("industry", "capability", "q")
        }
        relaxed_count = 0
        for h in confident_hits:
            story = h["story"].copy()
            if matches_filters(story, relaxed_filters):
                relaxed_count += 1

        # Build list of which filters are active
        active_filters = []
        if filters.get("industry"):
            active_filters.append(("industry", filters["industry"]))
        if filters.get("capability"):
            active_filters.append(("capability", filters["capability"]))

        return {
            "results": [],
            "confidence": confidence,
            "top_score": top_score,
            "relaxed_count": relaxed_count,
            "active_filters": active_filters,
        }

    return {
        "results": filtered_stories,
        "confidence": confidence,
        "top_score": top_score,
    }
