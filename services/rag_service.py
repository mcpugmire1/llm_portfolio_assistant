"""RAG (Retrieval-Augmented Generation) service - semantic search orchestration."""

import re
import streamlit as st
from typing import List, Optional
from config.debug import DEBUG
from utils.validation import _tokenize
from utils.formatting import build_5p_summary
from services.pinecone_service import (
    pinecone_semantic_search,
    W_PC,
    W_KW,
    PINECONE_MIN_SIM,
    SEARCH_TOP_K,
)

# Known vocab (built from stories)
_KNOWN_VOCAB = set()


def semantic_search(
    query: str,
    filters: dict,
    *,
    enforce_overlap: bool = False,
    min_overlap: float = 0.0,
    stories: list,
    top_k: int = SEARCH_TOP_K,
):
    """
    Pinecone-first semantic retrieval with gentle gating.
    Falls back to local keyword filtering if Pinecone returns nothing.
    """
    # Import matches_filters here to avoid circular dependency
    from utils.filters import matches_filters
    from utils.validation import token_overlap_ratio
    
    q = (query or "").strip()
    
    # 1) Try Pinecone first
    hits = pinecone_semantic_search(q, filters, stories, top_k=top_k) or []
    st.session_state["__pc_suppressed__"] = False
    
    # 2) If Pinecone gave candidates, apply confidence gate
    if hits:
        raw_gate = float(PINECONE_MIN_SIM)
        confident = [h for h in hits if (h.get("pc_score", 0.0) or 0.0) >= raw_gate]
        
        if not confident:
            st.session_state["__pc_suppressed__"] = True
            confident = hits[:3]
        
        # Persist scores for UI display
        try:
            st.session_state["__pc_last_ids__"] = {
                h["story"]["id"]: float(h.get("score", 0.0) or 0.0)
                for h in confident
            }
            st.session_state["__pc_snippets__"] = {
                h["story"]["id"]: (h.get("snippet") or build_5p_summary(h["story"]))
                for h in confident
            }
            st.session_state["__last_ranked_sources__"] = [
                h["story"]["id"] for h in confident
            ]
            st.session_state["__dbg_pc_hits"] = len(hits)
        except Exception:
            pass
        
        # Apply UI filters
        filtered = [h["story"] for h in confident if matches_filters(h["story"], filters)]
        if filtered:
            return filtered
        
        return [h["story"] for h in confident]
    
    # 3) No Pinecone results - enforce overlap if requested
    if enforce_overlap:
        ov = token_overlap_ratio(q, _KNOWN_VOCAB)
        if ov < float(min_overlap or 0.0) and not st.session_state.get("__ask_from_suggestion__"):
            st.session_state["__dbg_pc_hits"] = 0
            st.session_state["__pc_last_ids__"].clear()
            st.session_state["__pc_snippets__"].clear()
            return []
    
    # Local keyword fallback
    local = [s for s in stories if matches_filters(s, filters)]
    st.session_state["__dbg_pc_hits"] = 0
    st.session_state["__pc_last_ids__"].clear()
    st.session_state["__pc_snippets__"].clear()
    st.session_state["__last_ranked_sources__"] = [s["id"] for s in local[:10]]
    return local