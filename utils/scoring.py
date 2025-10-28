"""Scoring utilities for search results."""

from utils.validation import _tokenize
from utils.formatting import build_5p_summary

# Import weight constants
W_PC = 0.8  # semantic (Pinecone vector match)
W_KW = 0.2  # keyword/token overlap

def _keyword_score_for_story(s: dict, query: str) -> float:
    """
    Lightweight BM25-ish overlap using title/client/domain/tags + 5P summary.
    Returns 0..1 (normalized by unique query tokens).
    """
    q_toks = set(_tokenize(query))
    if not q_toks:
        return 0.0
    
    hay_parts = [
        s.get("Title", ""),
        s.get("Client", ""),
        s.get("Role", ""),
        s.get("Sub-category", ""),
        " ".join(s.get("public_tags", []) or []),
        build_5p_summary(s, 400),
        " ".join(s.get("Process", []) or []),
        " ".join(s.get("Performance", []) or []),
    ]
    hay = " ".join(hay_parts)
    h_toks = set(_tokenize(hay))
    hits = q_toks & h_toks

    # Soft weighting: title/domain twice
    title_dom = " ".join([s.get("Title", ""), s.get("Sub-category", "")])
    td_hits = q_toks & set(_tokenize(title_dom))
    score = len(hits) + len(td_hits)
    
    return min(1.0, score / max(1, len(q_toks) * 2))

def _hybrid_score(
    pc_score: float, kw_score: float, w_pc: float = W_PC, w_kw: float = W_KW
):
    """Blend Pinecone similarity and keyword overlap into one score."""
    try:
        pc = float(pc_score or 0.0)
    except Exception:
        pc = 0.0
    try:
        kw = float(kw_score or 0.0)
    except Exception:
        kw = 0.0
    
    return (pc * float(w_pc)) + (kw * float(w_kw))