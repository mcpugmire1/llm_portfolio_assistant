"""Story filtering utilities.

This module provides comprehensive story filtering functionality supporting
multiple filter types: industry, capability, client, domain, role, tags,
metrics, and keyword search with token-based matching.
"""

from typing import Any

from utils.formatting import story_has_metric
from utils.validation import _tokenize


def matches_filters(s: dict[str, Any], F: dict[str, Any] | None = None) -> bool:
    """Check if story matches all active filters.

    Applies comprehensive filtering logic including primary filters (industry,
    capability), advanced filters (client, domain, role, tags, metrics), and
    keyword search with token-based matching. All active filters must pass
    (AND logic).

    Filter Types:
        - industry (str): Single-select industry filter (e.g., "Financial Services")
        - capability (str): Single-select capability/offering filter
        - clients (list[str]): Client names to filter (OR logic within list)
        - domains (list[str]): Sub-category/domain filters (OR logic)
        - roles (list[str]): Role filters (OR logic)
        - tags (list[str]): Public tags to match (OR logic, case-insensitive)
        - has_metric (bool): If True, only stories with quantified metrics
        - q (str): Keyword search query (token-based ALL match required)

    Args:
        s: Story dictionary with raw JSONL fields (Title-case):
            - Industry (str): Industry category
            - Solution / Offering (str): Capability/offering
            - Client (str): Client name
            - Sub-category (str): Domain/category
            - Role (str): Role on project
            - public_tags (list[str]): Public tags
            - Title, Purpose, Process, Performance, etc. (for keyword search)
        F: Filters dictionary. If None, reads from st.session_state["filters"].
            Defaults to empty dict if not found.

    Returns:
        True if story passes all active filters, False if any filter fails.

    Side Effects:
        Imports streamlit (only when F is None) to access session state.

    Example:
        >>> story = {"Industry": "Financial Services", "Client": "JPMC",
        ...          "Sub-category": "Platform Engineering"}
        >>> filters = {"industry": "Financial Services", "clients": ["JPMC"]}
        >>> matches_filters(story, filters)
        True
        >>> filters2 = {"industry": "Healthcare"}
        >>> matches_filters(story, filters2)
        False
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
    era = F.get("era", "") or ""  # Era filter for Timeline navigation

    # Industry filter (NEW) - uses "Industry" field from JSONL
    if industry and s.get("Industry") != industry:
        return False

    # Capability filter (NEW) - uses "Solution / Offering" field from JSONL
    if capability and s.get("Solution / Offering") != capability:
        return False

    # Era filter - uses "Era" field from JSONL
    if era and s.get("Era") != era:
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
