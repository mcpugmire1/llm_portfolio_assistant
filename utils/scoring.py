"""Scoring utilities for search results.

This module provides hybrid scoring functionality that combines semantic
(Pinecone vector) similarity with keyword-based (BM25-ish) overlap scoring
for story search results.
"""

from typing import Any

from utils.formatting import build_5p_summary
from utils.validation import _tokenize

# Import weight constants
W_PC = 1.0  # semantic (Pinecone vector match)
W_KW = 0.0  # keyword/token overlap


def _keyword_score_for_story(s: dict[str, Any], query: str) -> float:
    """Calculate keyword overlap score for story using BM25-ish approach.

    Computes token overlap between query and story fields (title, client,
    domain, tags, competencies, 5P summary, process, performance). Applies
    soft weighting by counting title/domain matches twice. Normalizes by
    query token count.

    Args:
        s: Story dictionary with fields:
            - Title (str): Story title
            - Client (str): Client name
            - Role (str): Role on project
            - Sub-category (str): Domain/category
            - Competencies (list[str], optional): Skills/competencies
            - public_tags (list[str], optional): Public tags
            - Process (list[str], optional): How bullets
            - Performance (list[str], optional): Results bullets
        query: Search query string to match against.

    Returns:
        Float score between 0.0 and 1.0. Higher means better keyword match.
        Score is normalized by (unique query tokens * 2) to account for
        title/domain double-counting.

    Example:
        >>> story = {"Title": "Platform Modernization", "Client": "JPMC",
        ...          "Sub-category": "Platform Engineering"}
        >>> _keyword_score_for_story(story, "platform modernization jpmc")
        1.0
        >>> _keyword_score_for_story(story, "unrelated query")
        0.0
    """
    q_toks = set(_tokenize(query))
    if not q_toks:
        return 0.0

    hay_parts = [
        s.get("Title", ""),
        s.get("Client", ""),
        s.get("Role", ""),
        s.get("Sub-category", ""),
        " ".join(s.get("Competencies", []) or []),  # ← ADD THIS Direct keyword matches
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
) -> float:
    """Blend Pinecone similarity and keyword overlap into hybrid score.

    Combines semantic similarity (from Pinecone vector search) with keyword
    overlap (BM25-ish token matching) using weighted sum. Handles edge cases
    like None values and invalid types gracefully.

    Args:
        pc_score: Pinecone semantic similarity score (typically 0.0-1.0).
            None or invalid values default to 0.0.
        kw_score: Keyword overlap score from _keyword_score_for_story()
            (0.0-1.0). None or invalid values default to 0.0.
        w_pc: Weight for Pinecone score. Defaults to W_PC (1.0).
        w_kw: Weight for keyword score. Defaults to W_KW (0.0, disabled
            by default as semantic search is preferred).

    Returns:
        Float hybrid score. With default weights (1.0, 0.0), returns just
        the Pinecone score. With custom weights, returns weighted sum:
        (pc_score * w_pc) + (kw_score * w_kw)

    Example:
        >>> _hybrid_score(0.8, 0.6)  # Default: semantic only
        0.8
        >>> _hybrid_score(0.8, 0.6, w_pc=0.7, w_kw=0.3)  # Blended
        0.74
        >>> _hybrid_score(None, 0.5)  # Handles None
        0.0
    """
    try:
        pc = float(pc_score or 0.0)
    except Exception:
        pc = 0.0
    try:
        kw = float(kw_score or 0.0)
    except Exception:
        kw = 0.0

    return (pc * float(w_pc)) + (kw * float(w_kw))
