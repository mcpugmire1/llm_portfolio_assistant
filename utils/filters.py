"""Story filtering utilities."""

from utils.formatting import story_has_metric
from utils.validation import _tokenize


def matches_filters(s, F=None):
    """
    Check if story matches active filters.

    Uses raw JSONL field names (Title-case) since loader no longer transforms data.

    Args:
        s: Story dict (with raw JSONL fields)
        F: Filters dict (defaults to st.session_state["filters"])

    Returns:
        True if story passes all active filters
    """
    import streamlit as st

    # Normalize incoming filters
    if F is None:
        F = st.session_state.get("filters", {}) or {}

    # Primary filters (NEW for Phase 4 redesign)
    industry = F.get("industry", "") or ""  # Single-select Industry filter
    capability = F.get("capability", "") or ""  # Single-select Capability filter

    # Advanced filters
    personas = F.get("personas", []) or []
    clients = F.get("clients", []) or []
    domains = F.get("domains", []) or []  # Now filtering on Sub-category
    roles = F.get("roles", []) or []
    tags = F.get("tags", []) or []
    has_metric = bool(F.get("has_metric", False))

    # Industry filter (NEW) - uses "Industry" field from JSONL
    if industry and s.get("Industry") != industry:
        return False

    # Capability filter (NEW) - uses "Solution / Offering" field from JSONL
    if capability and s.get("Solution / Offering") != capability:
        return False

    # Persona filter (not used - field doesn't exist in data)
    if personas and not (set(personas) & set(s.get("personas", []))):
        return False

    # Client filter - uses "Client" field from JSONL
    if clients and s.get("Client") not in clients:
        return False

    # Domain filter - now uses "Sub-category" field from JSONL
    if domains and s.get("Sub-category") not in domains:
        return False

    # Role filter - uses "Role" field from JSONL
    if roles and s.get("Role") not in roles:
        return False

    # Tags filter - uses "public_tags" field (already parsed to list)
    if tags:
        want = {str(t).strip().lower() for t in tags}
        have = {str(t).strip().lower() for t in (s.get("public_tags", []) or [])}
        if not (want & have):
            return False

    # Metric filter
    if has_metric and not story_has_metric(s):
        return False

    # Keyword query: token-based match
    q_raw = (F.get("q") or "").strip()
    if q_raw:
        q_toks = _tokenize(q_raw)
        hay_joined = " ".join(
            [
                s.get("Title", ""),
                s.get("Client", ""),
                s.get("Role", ""),
                s.get("Sub-category", ""),
                s.get("Person", ""),
                s.get("Place", ""),
                s.get("Purpose", ""),
                " ".join(s.get("Process", []) or []),
                " ".join(s.get("Performance", []) or []),
                " ".join(s.get("public_tags", []) or []),
            ]
        )

        if q_toks:
            hay_toks = set(_tokenize(hay_joined))
            if not all(t in hay_toks for t in q_toks):
                return False
        else:
            # Fallback: substring check
            if q_raw.lower() not in hay_joined.lower():
                return False

    return True
