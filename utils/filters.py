"""Story filtering utilities."""

import re
from utils.validation import _tokenize
from utils.formatting import story_has_metric

def matches_filters(s, F=None):
    """
    Check if story matches active filters.
    
    Args:
        s: Story dict
        F: Filters dict (defaults to st.session_state["filters"])
        
    Returns:
        True if story passes all active filters
    """
    import streamlit as st
    
    # Normalize incoming filters
    if F is None:
        F = st.session_state.get("filters", {}) or {}
    
    personas = F.get("personas", []) or []
    clients = F.get("clients", []) or []
    domains = F.get("domains", []) or []
    roles = F.get("roles", []) or []
    tags = F.get("tags", []) or []
    has_metric = bool(F.get("has_metric", False))
    
    # Persona filter
    if personas and not (set(personas) & set(s.get("personas", []))):
        return False
    
    # Client filter
    if clients and s.get("client") not in clients:
        return False
    
    # Domain filter
    if domains and s.get("domain") not in domains:
        return False
    
    # Role filter
    if roles and s.get("role") not in roles:
        return False
    
    # Tags filter
    if tags:
        want = {str(t).strip().lower() for t in tags}
        have = {str(t).strip().lower() for t in (s.get("tags", []) or [])}
        if not (want & have):
            return False
    
    # Metric filter
    if has_metric and not story_has_metric(s):
        return False
    
    # Keyword query: token-based match
    q_raw = (F.get("q") or "").strip()
    if q_raw:
        q_toks = _tokenize(q_raw)
        hay_joined = " ".join([
            s.get("title", ""),
            s.get("client", ""),
            s.get("role", ""),
            s.get("domain", ""),
            s.get("who", ""),
            s.get("where", ""),
            s.get("why", ""),
            " ".join(s.get("how", []) or []),
            " ".join(s.get("what", []) or []),
            " ".join(s.get("tags", []) or []),
        ])
        
        if q_toks:
            hay_toks = set(_tokenize(hay_joined))
            if not all(t in hay_toks for t in q_toks):
                return False
        else:
            # Fallback: substring check
            if q_raw.lower() not in hay_joined.lower():
                return False
    
    return True