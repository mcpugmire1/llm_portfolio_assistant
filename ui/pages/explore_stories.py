"""
My Work Page - Refactored & Bug-Free

Browse 100+ project case studies with advanced filtering.
Includes semantic search, faceted filters, and pagination.

FIXES:
- Domain Category now actually filters results
- Pill X buttons properly remove filters
- Clear all properly resets all dropdowns
- Extracted duplicate code (detail panel, pagination)
- Centralized state management
- [2025-01] Fixed filter state consistency issues (industry/capability/era)
- [2025-01] Fixed page size dropdown resetting
- [2025-01] Fixed prefilter keys not clearing on reset
"""

import os

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import streamlit.components.v1.components  # noqa: F401 — pre-import so the

# submodule attribute exists when streamlit-aggrid references
# components.components.MarshallComponentException. Streamlit 1.50.0 doesn't
# auto-import the submodule; AgGrid 0.3.4.post3 assumes it does.
from dotenv import load_dotenv

from config.debug import DEBUG
from services.query_logger import log_query
from services.rag_service import semantic_search
from services.semantic_router import (
    is_portfolio_query_semantic,
    router_rejection_reason,
)
from ui.components.how_i_built_dialog import render_how_i_built_dialog
from ui.components.story_detail import render_story_detail
from ui.components.thinking_indicator import render_thinking_indicator
from ui.components.timeline_view import render_timeline_view
from ui.components.why_agy_dialog import render_why_agy_dialog
from ui.image_assets import AGY_EXPLORE_STORIES_B64
from utils.filters import matches_filters
from utils.ui_helpers import render_no_match_banner, safe_container
from utils.validation import is_nonsense

load_dotenv()

# =============================================================================
# CONSTANTS
# =============================================================================

DATA_FILE = os.getenv("STORIES_JSONL", "echo_star_stories_nlp.jsonl")

# Pagination
TABLE_PAGE_SIZE_DEFAULT = 10
TABLE_PAGE_SIZE_OPTIONS = [10, 20, 50]
CARDS_PAGE_SIZE = 9
CARDS_PER_ROW = 3

# UI
TABLE_HEIGHT = 750
TABLE_ROW_HEIGHT = 70
MAX_ACHIEVEMENTS_SHOWN = 4

# AgGrid availability check
try:
    _HAS_AGGRID = True
except Exception:
    _HAS_AGGRID = False


# =============================================================================
# HELPER FUNCTIONS - State Management
# =============================================================================


def reset_all_filters(stories: list[dict]):
    """Reset all filters and widget state to defaults - COMPREHENSIVE FIX"""

    # STEP 1: READ current version counters BEFORE deleting anything
    version_counters = {}
    for filter_type in [
        "q",
        "personas",
        "clients",
        "domains",
        "roles",
        "tags",
        "domain_cat",
        "industry",
        "capability",
        "era",
    ]:
        version_key = f"_widget_version_{filter_type}"
        current = st.session_state.get(version_key, 0)
        version_counters[filter_type] = current + 1  # Increment for next version

    # STEP 2: Delete ALL session state except critical keys
    preserve_keys = {
        "active_tab",
        "active_story",
        "active_story_obj",
        "explore_view_mode",
        "page_size_select",
        "_prev_explore_view_mode",
        # Preserves breadcrumb back-link state. When a user arrives at My
        # Work from a landing page (Banking / Cross-Industry), that landing
        # sets session_state["return_to_landing"]. Without this preserve entry,
        # clicking Reset Filters silently drops the back-link — the breadcrumb
        # chip vanishes even though the user came in via a landing flow.
        # Test: tests/unit/test_explore_stories.py::TestResetFiltersPreservesReturnToLanding
        "return_to_landing",
    }

    keys_to_delete = []
    for key in list(st.session_state.keys()):
        if key not in preserve_keys:
            keys_to_delete.append(key)

    for key in keys_to_delete:
        del st.session_state[key]

    # STEP 3: Recreate filters from scratch - ALL KEYS
    st.session_state["filters"] = {
        "personas": [],
        "clients": [],
        "domains": [],
        "roles": [],
        "tags": [],
        "q": "",
        "has_metric": False,
        "era": "",
        "industry": "",
        "capability": "",
    }

    # STEP 4: Set INCREMENTED version counters (using values we saved earlier)
    for filter_type, new_version in version_counters.items():
        version_key = f"_widget_version_{filter_type}"
        st.session_state[version_key] = new_version

    # STEP 5: Reset other state
    st.session_state["_last_domain_group"] = "All"
    st.session_state["page_offset"] = 0
    st.session_state["last_results"] = stories

    # STEP 6: Clear any lingering prefilter keys (belt and suspenders)
    for key in [
        "prefilter_industry",
        "prefilter_capability",
        "prefilter_domains",
        "prefilter_roles",
        "prefilter_view_mode",
        "prefilter_era",
    ]:
        st.session_state.pop(key, None)

    # STEP 7: Clear deeplink flag to allow re-triggering
    st.session_state.pop("_deeplink_story", None)

    # STEP 8: Clear search cache
    st.session_state.pop("__last_search_results__", None)
    st.session_state.pop("__last_search_confidence__", None)
    st.session_state.pop("__last_search_query__", None)

    # CRITICAL: Preserve the active tab
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = "My Work"


def remove_filter_value(filter_key: str, value: str):
    """Remove a specific value from a filter list and sync widget state"""
    F = st.session_state["filters"]

    # Handle search query specially
    if filter_key == "q":
        F["q"] = ""
        version_key = "_widget_version_q"
        st.session_state[version_key] = st.session_state.get(version_key, 0) + 1
        return

    # Handle string filters (not lists)
    if filter_key in ("era", "industry", "capability"):
        F[filter_key] = ""
        version_key = f"_widget_version_{filter_key}"
        current_version = st.session_state.get(version_key, 0)
        st.session_state[version_key] = current_version + 1
        widget_key = f"facet_{filter_key}"
        for v in range(current_version + 2):
            versioned_key = f"{widget_key}_v{v}"
            if versioned_key in st.session_state:
                del st.session_state[versioned_key]
        # Clear search cache and re-trigger search
        st.session_state.pop("__last_search_results__", None)
        st.session_state.pop("__last_search_confidence__", None)
        st.session_state.pop("__last_search_query__", None)
        if F.get("q"):
            st.session_state["__search_triggered__"] = True
        return

    # Remove from filter state (existing multi-select logic)
    if filter_key in F and isinstance(F[filter_key], list):
        if value in F[filter_key]:
            F[filter_key].remove(value)

    # Increment widget version to force recreation with fresh state
    version_key = f"_widget_version_{filter_key}"
    current_version = st.session_state.get(version_key, 0)
    st.session_state[version_key] = current_version + 1

    # Delete ALL versions of the widget keys (existing multi-select logic)
    widget_map = {
        "clients": "facet_clients",
        "domains": ["facet_domains_all", "facet_subdomains"],
        "roles": "facet_roles",
        "tags": "facet_tags",
        "personas": "facet_personas",
    }

    widget_keys_raw = widget_map.get(filter_key, [])
    widget_keys = (
        [widget_keys_raw] if isinstance(widget_keys_raw, str) else list(widget_keys_raw)
    )

    # Delete both the base key AND any versioned keys that exist
    for widget_key in widget_keys:
        if widget_key in st.session_state:
            del st.session_state[widget_key]
        for v in range(current_version + 2):
            versioned_key = f"{widget_key}_v{v}"
            if versioned_key in st.session_state:
                del st.session_state[versioned_key]

    # Clear search cache and re-trigger search
    st.session_state.pop("__last_search_results__", None)
    st.session_state.pop("__last_search_confidence__", None)
    st.session_state.pop("__last_search_query__", None)
    if F.get("q"):
        st.session_state["__search_triggered__"] = True


def build_domain_options(
    domains: list[str],
) -> tuple[list[str], list[tuple[str, str, str]]]:
    """Parse domain strings into categories and build options list"""
    domain_parts = [
        (d.split(" / ")[0], (d.split(" / ")[1] if " / " in d else ""), d)
        for d in domains
    ]
    groups = sorted({cat for cat, sub, full in domain_parts if full})
    return groups, domain_parts


# =============================================================================
# HELPER FUNCTIONS - Story Navigation
# ============================================================================
def get_context_story(stories: list[dict]) -> dict | None:
    """Get the currently selected story for detail view"""
    obj = st.session_state.get("active_story_obj")
    if isinstance(obj, dict) and (obj.get("id") or obj.get("Title")):
        return obj

    sid = st.session_state.get("active_story")
    if sid:
        for s in stories:
            if str(s.get("id")) == str(sid):
                return s

    at = (st.session_state.get("active_story_title") or "").strip().lower()
    ac = (st.session_state.get("active_story_client") or "").strip().lower()
    if at:
        for s in stories:
            stitle = (s.get("Title") or "").strip().lower()
            sclient = (s.get("Client") or "").strip().lower()
            if stitle == at and (not ac or sclient == ac):
                return s

    if at:
        for s in stories:
            stitle = (s.get("Title") or "").strip().lower()
            if at in stitle or stitle in at:
                return s

    lr = st.session_state.get("last_results") or []
    for x in lr:
        if not isinstance(x, dict):
            continue
        cand = x.get("story") if isinstance(x.get("story"), dict) else x
        if not isinstance(cand, dict):
            continue
        xid = str(cand.get("id") or cand.get("story_id") or "").strip()
        xt = (cand.get("Title") or "").strip().lower()
        xc = (cand.get("Client") or "").strip().lower()
        if (sid and xid and str(xid) == str(sid)) or (
            at and xt == at and (not ac or xc == ac)
        ):
            return cand

    return None


# =============================================================================
# HELPER FUNCTIONS - UI Components
# =============================================================================
def _render_confidence_banner(
    query: str,
    confidence: str,
    results: list[dict],
    *,
    filter_narrowed_pool: bool = False,
):
    """Render the tiered confidence banner for search results.

    Args:
        query: The search query string
        confidence: "high", "low", or "none"
        results: List of result dicts (with Title field) - needed to detect exact title match
        filter_narrowed_pool: True when a non-query filter was active. Suppresses
            the generic "Found N" render on the high branch; the exact-match render
            and the count line below the grid still fire.
    """
    BANNER_STYLE = "background: var(--banner-info-bg); border-left: 4px solid var(--banner-info-border); padding: 12px 16px; margin: 16px 0;"
    TEXT_COLOR_SUCCESS = "var(--banner-info-text)"
    TEXT_COLOR_CAUTION = "var(--banner-info-text)"
    TEXT_STYLE_COMMON = "font-size: 14px; font-weight: 600;"

    icon = "🐾"
    text_style_final = f"color: {TEXT_COLOR_SUCCESS}; {TEXT_STYLE_COMMON}"
    result_count = len(results)

    if confidence == "high":
        # Check if top result is an exact title match
        top_title = results[0].get("Title", "") if results else ""
        is_exact_match = query.lower().strip() == top_title.lower().strip()

        if is_exact_match:
            # Exact title search - highlight the match
            related_count = result_count - 1
            if related_count == 0:
                message = f"Found your story: \"{query}\""
            elif related_count == 1:
                message = "Found your story + 1 related story"
            else:
                message = f"Found your story + {related_count} related stories"
        else:
            # Generic search - show total count
            if filter_narrowed_pool:
                return
            plural = "story" if result_count == 1 else "stories"
            message = f"Found {result_count} matching {plural} for \"{query}\""
    elif confidence == "low":
        icon = "🐾"
        message = f"Showing closest matches for \"{query}\". Relevance may be low."
        text_style_final = f"color: {TEXT_COLOR_CAUTION}; {TEXT_STYLE_COMMON}"
    else:  # confidence == "none"
        message = f"No strong matches for \"{query}\". Matt may not have worked with this client or topic."

    st.markdown(
        f"""
    <div style="{BANNER_STYLE}">
        <span style="{text_style_final}"><span style="margin-right: 6px;">{icon}</span>{message}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )


def _should_suppress_page_ui(search_result: dict) -> bool:
    """MATTGPT-230: suppress the story count, grid, affordance lines, filter
    chips, and story detail whenever the fallback engaged -- regardless of
    whether keyword matches were found.

    Rationale: keyword rows are fallback output too. Lexical matches ranked by
    nothing, presented with the same count and pagination as semantic results,
    are the same false-confidence problem the ticket exists to fix. One rule,
    one state: reason set means breather only.

    Healthy states render normally (healthy zero-results keeps the browsable
    grid + filter feedback; healthy hits render as usual).
    """
    return search_result.get("reason") == "fallback:pinecone_unavailable"


def _render_degraded_banner() -> None:
    """MATTGPT-230: render honest-copy banner during Pinecone downtime.

    Reuses the -162 "quick breather" copy from Ask Agy so the same failure mode
    speaks with the same voice across surfaces. Replaces the misleading "closest
    matches, relevance may be low" framing that turned an outage into an
    apparent content gap. Keyword rows still render below when present -- row
    count carries the sub-shape, not the copy.
    """
    st.markdown(
        """
    <div style="background: var(--banner-info-bg); border-left: 4px solid var(--banner-info-border); padding: 12px 16px; margin: 16px 0; border-radius: 0 8px 8px 0;">
        <span style="color: var(--banner-info-text); font-size: 14px; font-weight: 600;"><span style="margin-right: 6px;">🐾</span>I need a quick breather: please try again in a moment!</span>
    </div>
    """,
        unsafe_allow_html=True,
    )


def _default_view(stories: list[dict], F: dict) -> list[dict]:
    """Return the fallback story view when a rejected query needs a default.

    MATTGPT-224: called from the shared rejection-render block and from
    the initial view seed near line 902. A rejected query is equivalent
    to no query -- apply the visitor's non-query filters (Client, Industry,
    etc) if any are set, else return the default sorted corpus with
    positioning stories excluded. F.get("q") is explicitly excluded so
    the rejected query text is not applied as a keyword filter.

    Uses `any(filters_without_q.values())` rather than a hardcoded key
    list so it cannot drift when a filter key is added or removed later.
    Equivalent to PATH 3's has_filters check for the current F shape.

    Positioning-story exclusion uses Theme == "Professional Narrative"
    per the -169 / DNA canonical hook.
    """
    filters_without_q = {k: v for k, v in F.items() if k != "q"}
    if any(filters_without_q.values()):
        return [s for s in stories if matches_filters(s, filters_without_q)]
    return sorted(
        [s for s in stories if s.get("Theme") != "Professional Narrative"],
        key=lambda s: s.get("Start_Date", ""),
        reverse=True,
    )


def render_filter_chips(filters: dict, stories: list[dict]) -> bool:
    """Render active filter chips. Returns True if state changed."""
    chips = []
    if filters.get("q"):
        chips.append(("Search", f'"{filters["q"]}"', ("q", None)))
    if filters.get("has_metric"):
        chips.append(("Flag", "Has metric", ("has_metric", None)))

    # Primary filters (single-select)
    if filters.get("industry"):
        chips.append(("Industry", filters["industry"], ("industry", None)))
    if filters.get("capability"):
        chips.append(("Capability", filters["capability"], ("capability", None)))
    if filters.get("era"):
        chips.append(("Era", filters["era"], ("era", None)))

    # Advanced filters (multi-select)
    for label, key in [
        ("Client", "clients"),
        ("Domain", "domains"),
        ("Role", "roles"),
        ("Tag", "tags"),
    ]:
        for v in filters.get(key, []):
            chips.append((label, v, (key, v)))

    if not chips:
        return False

    # Pure CSS inline layout: buttons inside a keyed container, styled via CSS flex
    to_remove = []
    clear_all = False

    with st.container(key="chip_row"):
        for _i, (_, text, (k, v)) in enumerate(chips):
            if st.button(f"\u2715 {text}", key=f"chip_{_i}"):
                to_remove.append((k, v))
        if st.button("\u2715 Clear all", key="chip_clear_all"):
            clear_all = True

    if clear_all:
        reset_all_filters(stories)
        st.rerun()
        return True

    if to_remove:
        for k, v in to_remove:
            if k == "q":
                remove_filter_value("q", None)
                # Clear cached search results
                st.session_state.pop("__last_search_results__", None)
                st.session_state.pop("__last_search_confidence__", None)
                st.session_state.pop("__last_search_query__", None)
            elif k == "has_metric":
                filters["has_metric"] = False
            else:
                remove_filter_value(k, v)

        st.session_state["page_offset"] = 0

        # CRITICAL: Preserve the active tab before rerunning
        if "active_tab" not in st.session_state:
            st.session_state["active_tab"] = "My Work"

        st.rerun()
        return True

    return False


def render_pagination(total_results: int, page_size: int, offset: int, view_mode: str):
    """Render numbered pagination controls (shared by views)"""
    total_pages = (total_results + page_size - 1) // page_size
    current_page = (offset // page_size) + 1

    if total_pages <= 1:
        return

    # Build page numbers list
    page_numbers: list[int | str]
    if total_pages <= 7:
        page_numbers = list(range(1, total_pages + 1))
    else:
        if current_page <= 4:
            page_numbers = [*list(range(1, 6)), "...", total_pages]
        elif current_page >= total_pages - 3:
            page_numbers = [1, "...", *list(range(total_pages - 4, total_pages + 1))]
        else:
            page_numbers = [
                1,
                "...",
                current_page - 1,
                current_page,
                current_page + 1,
                "...",
                total_pages,
            ]

    # Build pagination HTML
    buttons_html = ""

    # Prev button
    if current_page > 1:
        buttons_html += f'<button id="pg-prev-{view_mode}">‹ Prev</button>'
    else:
        buttons_html += '<button disabled>‹ Prev</button>'

    # Page numbers
    for page_num in page_numbers:
        if page_num == "...":
            buttons_html += '<span class="page-info">...</span>'
        elif page_num == current_page:
            buttons_html += f'<button class="active">{page_num}</button>'
        else:
            buttons_html += (
                f'<button id="pg-{view_mode}-{page_num}">{page_num}</button>'
            )

    # Next button
    if current_page < total_pages:
        buttons_html += f'<button id="pg-next-{view_mode}">Next ›</button>'
    else:
        buttons_html += '<button disabled>Next ›</button>'

    # Page info
    buttons_html += (
        f'<span class="page-info">Page {current_page} of {total_pages}</span>'
    )

    st.markdown(
        f"""
    <div class="es-pagination">
        {buttons_html}
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Hidden Streamlit buttons for triggering page changes
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("", key=f"pg_trigger_prev_{view_mode}"):
            st.session_state["page_offset"] = offset - page_size
            st.rerun()

    with col2:
        if st.button("", key=f"pg_trigger_next_{view_mode}"):
            st.session_state["page_offset"] = offset + page_size
            st.rerun()

    # Page number triggers - create for ALL possible pages user might click
    for page_num in page_numbers:
        if page_num != "..." and page_num != current_page:
            if st.button("", key=f"pg_trigger_{view_mode}_p{page_num}"):
                st.session_state["page_offset"] = (int(page_num) - 1) * page_size
                st.rerun()

    # JS wiring
    import streamlit.components.v1 as components

    components.html(
        f"""
    <script>
    (function() {{
        setTimeout(function() {{
            var parentDoc = window.parent.document;

            // Use event delegation on the pagination container
            parentDoc.addEventListener('click', function(e) {{
                var btn = e.target.closest('.es-pagination button');
                if (!btn || btn.disabled || btn.classList.contains('active')) return;

                e.preventDefault();

                // Check if it's prev/next
                if (btn.id === 'pg-prev-{view_mode}') {{
                    var trigger = parentDoc.querySelector('[class*="st-key-pg_trigger_prev_{view_mode}"] button');
                    if (trigger) trigger.click();
                    return;
                }}
                if (btn.id === 'pg-next-{view_mode}') {{
                    var trigger = parentDoc.querySelector('[class*="st-key-pg_trigger_next_{view_mode}"] button');
                    if (trigger) trigger.click();
                    return;
                }}

                // Page number button
                if (btn.id && btn.id.startsWith('pg-{view_mode}-')) {{
                    var pageNum = btn.id.split('-').pop();
                    var trigger = parentDoc.querySelector('[class*="st-key-pg_trigger_{view_mode}_p' + pageNum + '"] button');
                    if (trigger) trigger.click();
                }}
            }});
        }}, 100);
    }})();
    </script>
    """,
        height=0,
    )


# =============================================================================
# MAIN RENDER FUNCTION
# =============================================================================


def render_explore_stories(
    stories: list[dict],
    industries: list[str],
    capabilities: list[str],
    clients: list[str],
    domains: list[str],
    roles: list[str],
    tags: list[str],
    personas_all: list[str],
):
    """
    Render the My Work page with filters and project listings.

    FIXES:
    - Domain Category now actually filters
    - Pill X buttons work correctly
    - Clear all resets everything properly
    """
    # Note: Mobile CSS is injected globally via navbar.py

    if st.session_state.get("active_dialog") == "why_agy":
        render_why_agy_dialog()
        st.session_state.pop("active_dialog", None)
    elif st.session_state.get("active_dialog") == "how_i_built":
        render_how_i_built_dialog()
        st.session_state.pop("active_dialog", None)

    # Hero header with Agy avatar (gray headphones)
    st.markdown(
        f"""
<div class="conversation-header">
    <div class="conversation-header-content">
        <div style="position: relative; display: inline-block; flex-shrink: 0;">
            <img class="conversation-agy-avatar" src="{AGY_EXPLORE_STORIES_B64}" width="64" height="64" style="width: 64px; height: 64px; border-radius: 50%; border: 3px solid white !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;" alt="Agy"/>
            <span class="why-agy-badge--header" id="why-agy-badge-my-work">i</span>
        </div>
        <div class="conversation-header-text">
            <h1>Matt's Project Portfolio</h1>
            <p>100+ transformation stories. Trust Agy 🐾 to find the ones that fit.</p>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
    if st.button("trigger", key="why_agy_my_work_trigger"):
        st.session_state["active_dialog"] = "why_agy"
        st.rerun()
    components.html(
        """
<script>
(function() {
    function wireBadge() {
        var parentDoc = window.parent.document;
        var badge = parentDoc.getElementById('why-agy-badge-my-work');
        var btn = parentDoc.querySelector('[class*="st-key-why_agy_my_work_trigger"] button');
        if (badge && btn && !badge.dataset.wired) {
            badge.dataset.wired = 'true';
            badge.addEventListener('pointerdown', function(e) {
                e.preventDefault();
                btn.click();
            });
            return true;
        }
        return false;
    }
    if (!wireBadge()) {
        var attempts = 0;
        var iv = setInterval(function() {
            if (wireBadge() || ++attempts > 10) clearInterval(iv);
        }, 200);
    }
})();
</script>
""",
        height=0,
    )

    st.markdown("<a id='stories_top'></a>", unsafe_allow_html=True)

    F = st.session_state["filters"]

    # Initialize pre-filters from landing pages (Phase 4)
    # Track whether any prefilter was consumed so we can reset scroll once at
    # the end. Streamlit preserves scrollTop on stMain across reruns, so a
    # landing-card click (which scrolled the user down) lands on My
    # Work with the hero above the viewport. The pre-May-2026 fix lived
    # only inside prefilter_era AND targeted the legacy `section.main`
    # selector (which no longer exists in current Streamlit) — silently
    # no-op'd for Era *and* never fired for the other prefilters.
    _prefilter_applied = False
    if "prefilter_industry" in st.session_state:
        F["industry"] = st.session_state.pop("prefilter_industry")
        _prefilter_applied = True
    if "prefilter_capability" in st.session_state:
        F["capability"] = st.session_state.pop("prefilter_capability")
        # Clear domains when setting capability
        F["domains"] = []
        _prefilter_applied = True
    if "prefilter_domains" in st.session_state:
        F["domains"] = st.session_state.pop("prefilter_domains")
        # Clear capability when setting domains
        F["capability"] = ""
        _prefilter_applied = True
    if "prefilter_roles" in st.session_state:
        F["roles"] = st.session_state.pop("prefilter_roles")
        _prefilter_applied = True
    if "prefilter_view_mode" in st.session_state:
        st.session_state["explore_view_mode"] = st.session_state.pop(
            "prefilter_view_mode"
        )
        _prefilter_applied = True
    if "prefilter_era" in st.session_state:
        F["era"] = st.session_state.pop("prefilter_era")
        _prefilter_applied = True

    if _prefilter_applied:
        # Target [data-testid='stMain'] — the legacy `section.main` selector
        # this code used to reference doesn't exist in current Streamlit.
        # Landing pages (banking_landing.py, cross_industry_landing.py,
        # ask_mattgpt/landing_view.py) use the same selector for their
        # on-arrival scroll reset; keep them aligned.
        components.html(
            "<script>"
            "const main = window.parent.document.querySelector('[data-testid=\"stMain\"]');"
            "if (main) main.scrollTop = 0;"
            "</script>",
            height=0,
        )

    # ==================================================================
    # BREADCRUMB STRIP (between hero and filter box)
    # ==================================================================
    _return_landing = st.session_state.get("return_to_landing")
    if _return_landing:
        _bc_label = "← Banking" if _return_landing == "banking" else "← Cross Industry"
        st.markdown(
            f"""
            <span id="breadcrumb-chip" style="display: inline-flex; align-items: center; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 500; cursor: pointer; border: 1px solid var(--border-color); background: var(--bg-card); color: var(--accent-purple); transition: all 0.15s ease; margin-top: -1rem;">
                <a id="breadcrumb-return" style="color: inherit; text-decoration: none; cursor: pointer;">{_bc_label}</a>
            </span>
            <style>
            #breadcrumb-chip:hover {{ border-color: var(--accent-purple); background: var(--accent-purple-bg); color: var(--accent-purple-hover); box-shadow: 0 2px 6px rgba(139, 92, 246, 0.15); }}
            [class*="st-key-breadcrumb_return_landing"] {{ display: none !important; }}
            </style>
            """,
            unsafe_allow_html=True,
        )
        if st.button("", key="breadcrumb_return_landing"):
            _landing_tab = (
                "Banking" if _return_landing == "banking" else "Cross-Industry"
            )
            st.session_state.pop("return_to_landing", None)
            st.session_state["active_tab"] = _landing_tab
            st.session_state["filters"] = {
                "personas": [],
                "clients": [],
                "domains": [],
                "roles": [],
                "tags": [],
                "q": "",
                "has_metric": False,
                "era": "",
                "industry": "",
                "capability": "",
            }
            st.rerun()
        components.html(
            """<script>
            setTimeout(function() {
                var chip = window.parent.document.getElementById('breadcrumb-chip');
                if (chip && !chip.dataset.wired) {
                    chip.dataset.wired = 'true';
                    chip.onclick = function() {
                        var btn = window.parent.document.querySelector('[class*="st-key-breadcrumb_return_landing"] button');
                        if (btn) btn.click();
                    };
                }
            }, 200);
            </script>""",
            height=0,
        )

    # ==================================================================
    # FILTERS SECTION - REDESIGNED (Phase 4)
    # ==================================================================
    with safe_container(border=True):
        # PRIMARY FILTERS ROW: Search (with inline button) | Industry | Capability
        search_col, industry_col, capability_col = st.columns([2, 1, 1])

        with search_col:
            search_version = st.session_state.get("_widget_version_q", 0)

            # Use a form to capture 'Enter' key press as a deliberate submission
            with st.form(
                key=f"search_form_v{search_version}",
                clear_on_submit=False,
                border=False,
            ):
                # Inline search input + button
                input_col, btn_col = st.columns([0.88, 0.12])
                with input_col:
                    F["q"] = st.text_input(
                        "Find stories",
                        value=F.get("q", ""),
                        placeholder="Try modern platforms, product innovation...",
                        key=f"facet_q_v{search_version}",
                    )
                with btn_col:
                    # Add spacing to align with input
                    st.markdown(
                        "<div style='height: 23px;'></div>", unsafe_allow_html=True
                    )
                    submitted = st.form_submit_button("🔍", use_container_width=True)

                if submitted:
                    st.session_state["__search_triggered__"] = True

        with industry_col:
            # Industry filter (single select dropdown)
            industry_version = st.session_state.get("_widget_version_industry", 0)
            industry_options = ["All"] + industries
            current_industry = F.get("industry", "")
            industry_index = (
                industry_options.index(current_industry)
                if current_industry in industry_options
                else 0
            )
            selected_industry = st.selectbox(
                "Industry",
                options=industry_options,
                index=industry_index,
                key=f"facet_industry_v{industry_version}",
            )
            F["industry"] = "" if selected_industry == "All" else selected_industry

        with capability_col:
            # Capability filter (single select dropdown)
            capability_version = st.session_state.get("_widget_version_capability", 0)
            capability_options = ["All"] + capabilities
            current_capability = F.get("capability", "")
            capability_index = (
                capability_options.index(current_capability)
                if current_capability in capability_options
                else 0
            )
            selected_capability = st.selectbox(
                "Capability",
                options=capability_options,
                index=capability_index,
                key=f"facet_capability_v{capability_version}",
            )
            F["capability"] = (
                "" if selected_capability == "All" else selected_capability
            )

        # MOBILE FILTERS TOGGLE — shown only on mobile via CSS (MATTGPT-119)
        is_r2_open = st.session_state.get("es_mobile_r2_open", False)
        toggle_label = "Filters ▴" if is_r2_open else "Filters ▾"
        if st.button(toggle_label, key="es_mobile_filters_toggle"):
            st.session_state["es_mobile_r2_open"] = not is_r2_open
            st.rerun()

        # ROW 2 — always visible on desktop; on mobile shown/hidden via key swap (MATTGPT-065, MATTGPT-119)
        r2_key = "r2_row_open" if is_r2_open else "r2_row"
        with st.container(key=r2_key):
            c1, c2, c3, c4 = st.columns([1, 1, 1, 0.4])

            with c1:
                clients_version = st.session_state.get("_widget_version_clients", 0)
                client_options = ["All"] + clients
                current_client_val = (F.get("clients") or [""])[0]
                client_index = (
                    client_options.index(current_client_val)
                    if current_client_val in client_options
                    else 0
                )
                sel_client = st.selectbox(
                    "Client",
                    options=client_options,
                    index=client_index,
                    key=f"r2_client_v{clients_version}",
                )
                F["clients"] = [] if sel_client == "All" else [sel_client]

            with c2:
                roles_version = st.session_state.get("_widget_version_roles", 0)
                role_options = ["All"] + roles
                current_role_val = (F.get("roles") or [""])[0]
                role_index = (
                    role_options.index(current_role_val)
                    if current_role_val in role_options
                    else 0
                )
                sel_role = st.selectbox(
                    "Role",
                    options=role_options,
                    index=role_index,
                    key=f"r2_role_v{roles_version}",
                )
                F["roles"] = [] if sel_role == "All" else [sel_role]

            with c3:
                domains_version = st.session_state.get("_widget_version_domains", 0)
                domain_options = ["All"] + domains
                current_domain_val = (F.get("domains") or [""])[0]
                domain_index = (
                    domain_options.index(current_domain_val)
                    if current_domain_val in domain_options
                    else 0
                )
                sel_domain = st.selectbox(
                    "Domain",
                    options=domain_options,
                    index=domain_index,
                    key=f"r2_domain_v{domains_version}",
                )
                F["domains"] = [] if sel_domain == "All" else [sel_domain]

            with c4:
                if st.button("Reset filters", key="r2_reset", use_container_width=True):
                    reset_all_filters(stories)
                    st.rerun()
    # =========================================================================
    # SEARCH & FILTERING LOGIC (Guarded and Cached)
    # =========================================================================

    # Check if search was intentionally triggered (by form submission)
    search_triggered = st.session_state.pop("__search_triggered__", False)
    current_query = F["q"].strip()

    # MATTGPT-230: initialize so the suppression check below is safe on every
    # path. Only PATH 1b assigns a real dict; PATH 2 and PATH 3 leave it empty,
    # and the pure helper returns False on an empty dict.
    search_result: dict = {}
    # MATTGPT-098: default view excludes Professional Narrative stories
    # (matching Timeline's EXCLUDED_ERA convention at timeline_view.py:42)
    # and sorts by Start_Date descending (most-recent-first). User can still
    # sort by clicking AgGrid column headers; this only changes the default
    # state. Narrative stories remain in the corpus + reachable via search
    # / Sub-category filter / direct deep-link, just not in the default view.
    # Delegates to _default_view so the exclusion field (Theme per -169)
    # stays consistent with the rejection-block fallback below. Passes {}
    # because this is the pre-search seed -- the paths below apply the
    # visitor's actual filters.
    view = _default_view(stories, {})

    # Cache keys for readability
    LAST_RESULTS = "__last_search_results__"
    LAST_CONFIDENCE = "__last_search_confidence__"
    LAST_QUERY = "__last_search_query__"

    if current_query and search_triggered:
        # --- PATH 1a: Rejection detection (runs only on new submit) ---
        # MATTGPT-224: no longer calls st.stop() or renders banner here.
        # Sets session-state keys that survive across reruns. The shared
        # rejection-render block below handles banner + default view both
        # on this run and on every subsequent rerun where current_query
        # still matches the stored rejected query. page_offset resets to
        # 0 here (on new rejection) rather than in the shared block --
        # putting it in the shared block would reset the offset on every
        # rerun and prevent pagination.

        # SURGICAL FIX: Clear active_story ONLY when search query actually changes
        # This prevents showing stale story detail from a previous search
        # but preserves active_story for: filter changes, view switching, "Ask Agy About This"
        previous_query = st.session_state.get("__last_q__", "")
        if current_query != previous_query:
            st.session_state.pop("active_story", None)
            st.session_state.pop("active_story_obj", None)
            st.session_state.pop("active_story_title", None)
            st.session_state.pop("active_story_client", None)

        nonsense_check = is_nonsense(current_query)
        intent_family = None

        if nonsense_check:
            # is_nonsense() returns the bare category string (e.g.,
            # "jokes_riddles"). render_no_match_banner expects the
            # "rule:<category>" prefix for the BANNER_COPY["rule"] branch
            # (mirrors the Ask Agy convention at backend_service.py:1463).
            # May 23, 2026 fix.
            st.session_state["__query_rejected__"] = current_query
            st.session_state["__query_rejected_reason__"] = f"rule:{nonsense_check}"
            st.session_state["page_offset"] = 0
            st.session_state.pop(LAST_RESULTS, None)
            st.session_state.pop(LAST_CONFIDENCE, None)
            st.session_state.pop(LAST_QUERY, None)
        else:
            # Semantic router gate — catch personal/out_of_scope before Pinecone.
            # MATTGPT-219 (out_of_scope) + MATTGPT-234 (personal): both branches
            # gated on HARD_ACCEPT via router_rejection_reason. Below that the
            # query falls through to Pinecone; any real off-topic case is caught
            # by the overlap:0.00 gate downstream.
            _, semantic_score, _, intent_family = is_portfolio_query_semantic(
                current_query
            )
            reject_reason = router_rejection_reason(intent_family, semantic_score)
            if reject_reason:
                log_query(
                    current_query,
                    "My Work",
                    intent_family=intent_family,
                    redirect_reason=f"semantic_router:{reject_reason}",
                )
                st.session_state["__query_rejected__"] = current_query
                st.session_state["__query_rejected_reason__"] = (
                    f"semantic_router:{reject_reason}"
                )
                st.session_state["page_offset"] = 0
                st.session_state.pop(LAST_RESULTS, None)
                st.session_state.pop(LAST_CONFIDENCE, None)
                st.session_state.pop(LAST_QUERY, None)

    # --- Central rejection check (MATTGPT-224) ---
    # Session-state signal survives across reruns until current_query
    # changes. Every rerun (filter change, pagination, view switch,
    # row click) that keeps the same current_query hits this check and
    # re-renders the banner + default view. Gate requires BOTH keys
    # present -- a missing reason means the state is inconsistent, and
    # inconsistent state is safer treated as not-rejected than guessed.
    stored_rejected = st.session_state.get("__query_rejected__")
    stored_reason = st.session_state.get("__query_rejected_reason__")
    query_is_rejected = bool(
        current_query and stored_reason and stored_rejected == current_query
    )

    if query_is_rejected:
        # Clear F["q"] so downstream code (render_filter_chips at :1150,
        # PATH 3's has_filters logic, _default_view's filter chain) all
        # see the rejected query as absent. One line covers the chip,
        # the helper, and the has_filters flag. F["q"] gets re-populated
        # from the search-input widget on the next rerun (line 798), so
        # this clear is per-rerun scoped -- the widget still shows what
        # the visitor typed; only the filter state is corrected.
        F["q"] = ""
        render_no_match_banner(
            reason=stored_reason,
            query=current_query,
            overlap=None,
            suppressed=True,
            filters=F,
            context="explore",
        )
        # A rejected query is equivalent to no query -- apply the visitor's
        # other filters (Client, Industry, etc.) but never the rejected
        # query text as a keyword. _default_view strips F["q"] internally.
        view = _default_view(stories, F)
        st.session_state["__last_q__"] = current_query
        # page_offset intentionally NOT reset here -- resets only on new
        # rejection (PATH 1a branches above), otherwise pagination breaks.

    elif current_query and search_triggered:
        # --- PATH 1b: Non-rejection Pinecone search body ---
        # Run expensive semantic search
        search_container = st.empty()
        with search_container:
            render_thinking_indicator()
        try:
            search_result = semantic_search(current_query, filters=F, stories=stories)
            view = search_result["results"]
            confidence = search_result["confidence"]

            # Cache results
            st.session_state[LAST_RESULTS] = view
            st.session_state[LAST_CONFIDENCE] = confidence
            st.session_state[LAST_QUERY] = current_query
            log_query(
                current_query,
                "My Work",
                intent_family=intent_family,
                confidence=confidence,
                result_count=len(view),
            )

        finally:
            search_container.empty()

        # Check if filters blocked all results but matches exist elsewhere
        relaxed_count = search_result.get("relaxed_count", 0)
        active_filters = search_result.get("active_filters", [])

        # MATTGPT-230: Pinecone unavailable takes precedence over the other
        # banner branches -- the relaxed_count math assumes Pinecone ran, and
        # the confidence banner would misframe an outage as a content gap.
        if search_result.get("reason") == "fallback:pinecone_unavailable":
            _render_degraded_banner()
        elif relaxed_count > 0 and not view:
            # Show helpful banner with option to clear restrictive filters
            filter_names = " + ".join([f[1] for f in active_filters])
            st.markdown(
                f"""
                <div style="background: var(--banner-info-bg); border-left: 4px solid var(--banner-info-border); padding: 12px 16px; margin: 16px 0; border-radius: 0 8px 8px 0;">
                    <span style="color: var(--banner-info-text); font-size: 14px;">
                        <span style="margin-right: 6px;">🐾</span>No matches. Matt has {relaxed_count} "{current_query}" stories, but none in {filter_names}.
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif confidence == "none":
            # MATTGPT-234 Move 1: route zero-confidence Pinecone results
            # through the rejection-path treatment. Without this, a fall-
            # through query (bananas after -234, or any query Pinecone
            # returns nothing confident for) rendered the "No strong
            # matches" line over an empty grid, phantom row, and empty
            # detail slot. Same shape as the router-rejection path at
            # :1054: clear F["q"], render_no_match_banner, browsable
            # corpus via _default_view. Sets __query_rejected__ so
            # subsequent reruns (filter change, view switch, pagination)
            # keep the same shape via the shared rejection block above.
            # Interim state: "trail-lost, try rephrasing" copy is wrong-
            # voice for fell-through queries; correct copy split waits on
            # MATTGPT-239's confidence floor.
            st.session_state["__query_rejected__"] = current_query
            st.session_state["__query_rejected_reason__"] = "low_confidence"
            F["q"] = ""
            render_no_match_banner(
                reason="low_confidence",
                query=current_query,
                overlap=None,
                suppressed=True,
                filters=F,
                context="explore",
            )
            view = _default_view(stories, F)
        else:
            filter_narrowed_pool = any(v for k, v in F.items() if k != "q")
            _render_confidence_banner(
                current_query,
                confidence,
                view,
                filter_narrowed_pool=filter_narrowed_pool,
            )

        st.session_state["page_offset"] = 0
        st.session_state["__last_q__"] = current_query

    elif current_query and st.session_state.get(LAST_QUERY) == current_query:
        # --- PATH 2: Reuse Cached Results (Filter Interaction - NO Pinecone Call) ---
        # User interacted with a filter (Advanced Filter, Industry, etc.).
        # Search term is the same as the last submitted query, so reuse the cached set.

        # Retrieve cached results and confidence
        cached_view = st.session_state.get(LAST_RESULTS, [])
        confidence = st.session_state.get(LAST_CONFIDENCE, "none")

        if confidence == "none":
            cached_view = []

        # Apply filters EXCEPT keyword query - Pinecone already did semantic matching.
        # Re-applying keyword filter would remove valid semantic matches that don't
        # contain the exact query tokens (e.g., "Truist" search returning RBC stories).
        filters_without_q = {k: v for k, v in F.items() if k != "q"}
        view = [s for s in cached_view if matches_filters(s, filters_without_q)]

        # MATTGPT-224 fold-in: pass filtered view (post-UI-filter) rather
        # than cached_view (pre-UI-filter) so the "Found N matching stories"
        # count matches the "Showing 1-N of N stories" count immediately
        # below. Previously: banner said "Found 25" while count-below said
        # "Showing 1-4 of 4" for the same page.
        _render_confidence_banner(
            current_query,
            confidence,
            view,
            filter_narrowed_pool=any(filters_without_q.values()),
        )

    else:
        # --- PATH 3: No Active Query (F["q"] is empty) or Query changed but not submitted ---
        # This path handles initial load, "Clear all" clicks, and filter-only searches.

        # Clear cache if the query is empty
        st.session_state.pop(LAST_RESULTS, None)
        st.session_state.pop(LAST_CONFIDENCE, None)
        st.session_state.pop(LAST_QUERY, None)

        # Filter the entire story set locally
        has_filters = any(
            [
                F.get("q"),
                F.get("industry"),
                F.get("capability"),
                F.get("clients"),
                F.get("domains"),
                F.get("roles"),
                F.get("tags"),
                F.get("era"),
                F.get("has_metric"),
            ]
        )

        if has_filters:
            view = [s for s in stories if matches_filters(s, F)]
        else:
            # MATTGPT-098: default view (no filters active) applies the
            # Professional Narrative exclusion + Start_Date desc sort.
            # Kept in sync with _default_view helper -- both must use the
            # same exclusion field. Exclusion uses Theme per the -169 /
            # DNA canonical hook (Category was silently-correct by 100%
            # overlap on the current corpus).
            view = sorted(
                [s for s in stories if s.get("Theme") != "Professional Narrative"],
                key=lambda s: s.get("Start_Date", ""),
                reverse=True,
            )

        # Filter-only feedback banner (no search query active)
        if has_filters and not F.get("q"):
            # Build description of active filters
            active_filter_names = []
            if F.get("industry"):
                active_filter_names.append(F["industry"])
            if F.get("capability"):
                active_filter_names.append(F["capability"])
            if F.get("clients"):
                active_filter_names.append(", ".join(F["clients"]))
            if F.get("domains"):
                active_filter_names.append(", ".join(F["domains"]))
            if F.get("roles"):
                active_filter_names.append(", ".join(F["roles"]))

            filter_desc = (
                " + ".join(active_filter_names)
                if active_filter_names
                else "these filters"
            )

            if len(view) == 0:
                st.markdown(
                    f"""
                    <div style="background: var(--banner-info-bg); border-left: 4px solid var(--accent-purple); padding: 12px 16px; margin: 16px 0; border-radius: 0 8px 8px 0;">
                        <span style="color: var(--accent-purple-text); font-size: 14px;">
                            <span style="margin-right: 6px;">🐾</span>No stories match {filter_desc}.
                        </span>
                        <br><span style="color: var(--accent-purple-text); font-size: 13px; opacity: 0.8;">Try removing a filter or broadening your search.</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="background: var(--banner-info-bg); border-left: 4px solid var(--accent-purple); padding: 12px 16px; margin: 16px 0; border-radius: 0 8px 8px 0;">
                        <span style="color: var(--accent-purple-text); font-size: 14px;">
                            <span style="margin-right: 6px;">🐾</span>Showing {len(view)} {filter_desc} stories.
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Final step for all paths
    st.session_state["last_results"] = view
    st.session_state["__results_count__"] = len(view)
    # =========================================================================
    # END SEARCH & FILTERING LOGIC
    # =========================================================================

    # MATTGPT-230: whenever the fallback engaged, the breather is the only
    # honest thing to render. Suppress filter chips, count, grid, affordance
    # lines, and story detail regardless of whether keyword matches were found.
    # Keyword rows are fallback output too -- rendering them with the same
    # count and pagination as semantic results is the same false-confidence
    # problem the ticket exists to fix.
    #
    # Filter chips specifically: the filter panel above the banner still shows
    # Client/Industry/etc state and provides the removal affordance, so chips
    # would be a redundant echo. State is not lost -- it is just not doubly
    # rendered in an outage state.
    if _should_suppress_page_ui(search_result):
        from ui.components.footer import render_footer

        render_footer()
        return

    render_filter_chips(F, stories)

    # =========================================================================
    # VIEW MODE SETUP
    # =========================================================================

    total_results = len(view)

    if "explore_view_mode" not in st.session_state:
        st.session_state["explore_view_mode"] = "Table"
    if "page_offset" not in st.session_state:
        st.session_state["page_offset"] = 0

    prev_view_mode = st.session_state.get("_prev_explore_view_mode", "Table")
    view_mode = st.session_state.get("explore_view_mode", "Table")

    # Check if arriving via deeplink - skip view mode reset in that case
    deeplink_story_id = st.query_params.get("story")

    if view_mode != prev_view_mode and not deeplink_story_id:
        # Only reset offset on view mode change if NOT arriving via deeplink
        st.session_state["page_offset"] = 0
        st.session_state["_prev_explore_view_mode"] = view_mode
    elif view_mode != prev_view_mode:
        # Deeplink arrival - just update the mode tracker, don't reset offset
        st.session_state["_prev_explore_view_mode"] = view_mode

    # =========================================================================
    # DEEPLINK PAGINATION FIX
    # When arriving via ?story=id, calculate offset so the story is visible
    # Search through full `stories` list (not filtered `view`) since deeplinks
    # should work regardless of any filters that might be applied
    # =========================================================================
    if deeplink_story_id:
        current_offset = st.session_state.get("page_offset", 0)
        # Find the story's index in the FULL stories list
        for idx, s in enumerate(stories):
            if str(s.get("id")) == str(deeplink_story_id):
                # Calculate correct offset for Cards view (CARDS_PAGE_SIZE = 9)
                page_number = idx // CARDS_PAGE_SIZE
                correct_offset = page_number * CARDS_PAGE_SIZE
                # Ensure we have the story object for get_context_story()
                st.session_state["active_story_obj"] = s
                # Only rerun if offset needs to change (prevents infinite loop)
                if current_offset != correct_offset:
                    st.session_state["page_offset"] = correct_offset
                    st.rerun()
                break

    page_size_option = st.session_state.get("page_size_select", TABLE_PAGE_SIZE_DEFAULT)
    page_size = page_size_option if view_mode == "Table" else CARDS_PAGE_SIZE
    offset = int(st.session_state.get("page_offset", 0))

    # Bounds check pagination offset for all views
    if offset >= total_results and total_results > 0:
        offset = 0
        st.session_state["page_offset"] = 0

    if total_results == 0:
        start = 0
        end = 0
    else:
        start = offset + 1
        end = min(offset + page_size, total_results)

    # Hide SHOW controls on Cards/Timeline (keeps column width, hides visually)
    if view_mode != "Table":
        st.markdown(
            """
        <style>
        .st-key-page_size_select { visibility: hidden; }
        </style>
        """,
            unsafe_allow_html=True,
        )

    col1, col2, col3, spacer, col4 = st.columns([2.2, 0.18, 0.5, 0.12, 1.2])

    with col1:
        results_html = f"""
        <div class="es-results-count" style="display: flex; align-items: center; min-height: 44px; color: var(--text-color); font-size: 14px; white-space: nowrap;">
            <span>Showing</span>&nbsp;<strong>{start}&ndash;{end}</strong>&nbsp;<span>of</span>&nbsp;<strong>{total_results}</strong>&nbsp;<span>stories</span>
        </div>
        """
        st.markdown(results_html, unsafe_allow_html=True)

    with col2:
        visibility = "visible" if view_mode == "Table" else "hidden"
        st.markdown(
            f'<div style="display: flex; align-items: center; min-height: 44px; font-size: 14px; font-weight: 500; visibility: {visibility};"><span class="es-show-label">SHOW:</span></div>',
            unsafe_allow_html=True,
        )

    with col3:
        current_size = st.session_state.get("page_size_select", TABLE_PAGE_SIZE_DEFAULT)
        try:
            current_index = TABLE_PAGE_SIZE_OPTIONS.index(current_size)
        except (ValueError, TypeError):
            current_index = 0

        page_size_option = st.selectbox(
            "page_size",
            options=TABLE_PAGE_SIZE_OPTIONS,
            index=current_index,
            key="page_size_select",
            label_visibility="collapsed",
        )

    with col4:
        view_mode = st.segmented_control(
            "View",
            options=["Table", "Cards", "Timeline"],  # Added "Timeline"
            key="explore_view_mode",
            label_visibility="collapsed",
        )

    page_size = page_size_option if view_mode == "Table" else CARDS_PAGE_SIZE
    offset = int(st.session_state.get("page_offset", 0))

    if DEBUG:
        print(f"DEBUG Explore: view_mode={view_mode}, page_size={page_size}")

    # =========================================================================
    # TABLE VIEW
    # =========================================================================

    if view_mode == "Table":
        # Mobile swipe hint (hidden on tablet/desktop via CSS)
        st.markdown(
            """
            <div class="es-table-swipe-hint">
                <span>← Swipe to see more columns →</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        def _row(s: dict) -> dict:
            return {
                "ID": s.get("id", ""),
                "Title": s.get("Title", ""),
                "Client": s.get("Client", ""),
                "Role": s.get("Role", ""),
                "Start_Date": s.get("Start_Date", ""),
            }

        view_paginated = view[offset : offset + page_size]
        rows = [_row(s) for s in view_paginated]
        df = pd.DataFrame(rows)
        show_cols = [
            c for c in ["Title", "Client", "Role", "Start_Date"] if c in df.columns
        ]

        show_df = df[show_cols] if show_cols else df

        # KNOWN: st.dataframe selection color is canvas-drawn. primaryColor in config.toml
        # does not reach GDG's theme in Streamlit 1.50.0. CSS hue-rotate is the best
        # available workaround — clean in light mode, slightly imperfect in dark mode.
        # Deeper fixes (GDG CSS vars, JS setProperty) don't survive GDG's render cycle.
        st.markdown(
            """<style>
            [data-testid="stDataFrame"] canvas {
                filter: hue-rotate(262deg) saturate(88%);
            }
            [data-testid="stDataFrame"] > div {
                background: var(--table-row-bg) !important;
                border: 1px solid var(--border-color) !important;
                border-radius: 12px !important;
            }
            button[aria-label="Show/hide columns"] {
                display: none !important;
            }
            </style>""",
            unsafe_allow_html=True,
        )

        if not st.session_state.get("active_story"):
            st.markdown(
                "<p style='font-size:13px; color:var(--text-secondary); margin:0 0 8px 0;'>"
                '<span style="margin-right: 6px;">🐾</span>Check any row to read the full story.</p>',
                unsafe_allow_html=True,
            )

        # Dynamic height: size to the rows actually shown so there's no dead
        # zone. show_df is the filtered+paginated slice, so len() reflects both
        # the active filter and the SHOW page-size (10/20/50).
        _ROW_PX = 35  # confirm against actual render
        _HEADER_PX = 38  # confirm against actual render
        _dyn_height = _HEADER_PX + max(1, len(show_df)) * _ROW_PX + 2

        # iteration-2 (poc/mattgpt-144): native selection wired to detail.
        selection = st.dataframe(
            show_df,
            hide_index=True,
            width="stretch",
            height=_dyn_height,
            on_select="rerun",
            selection_mode="single-row",
            key="stories_df",
            column_config={
                "Title": st.column_config.TextColumn("Title", width="large"),
                "Client": st.column_config.TextColumn("Client", width="medium"),
                "Role": st.column_config.TextColumn("Role", width="medium"),
                "Start_Date": st.column_config.TextColumn("Start Date", width="small"),
            },
        )

        _sel_rows = selection["selection"]["rows"]
        if _sel_rows:
            _idx = _sel_rows[0]
            if 0 <= _idx < len(view_paginated):
                st.session_state["active_story"] = view_paginated[_idx].get("id")
                st.session_state.pop("active_story_obj", None)
                st.session_state.pop("active_story_title", None)
                st.session_state.pop("active_story_client", None)

        render_pagination(total_results, page_size, offset, "table")
        detail = get_context_story(stories)
        render_story_detail(detail, "table", stories)

    # =========================================================================
    # CARDS VIEW
    # =========================================================================

    elif view_mode == "Cards":
        offset = int(st.session_state.get("page_offset", 0))
        if offset < 0:
            offset = 0
        if offset >= total_results and total_results > 0:
            offset = 0
            st.session_state["page_offset"] = 0

        view_window = view[offset : offset + page_size]

        if not view_window:
            st.info("No stories match your filters yet.")
            if st.button("Clear filters", key="clear_filters_empty"):
                reset_all_filters(stories)
                st.rerun()
        else:
            # Get currently selected story ID
            selected_story_id = st.session_state.get("active_story")

            num_rows = (len(view_window) + CARDS_PER_ROW - 1) // CARDS_PER_ROW

            for row in range(num_rows):
                cols = st.columns(CARDS_PER_ROW)
                row_story_ids = []  # Track story IDs in this row

                for col_idx in range(CARDS_PER_ROW):
                    i = row * CARDS_PER_ROW + col_idx
                    if i >= len(view_window):
                        continue

                    s = view_window[i]
                    with cols[col_idx]:
                        title = s.get("Title", "Untitled")
                        client = s.get("Client", "Unknown")
                        role = s.get("Role", "Unknown")
                        domain = (
                            (s.get("Sub-category") or "").split(" / ")[-1]
                            if s.get("Sub-category")
                            else "Unknown"
                        )
                        summary = s.get("5PSummary", "")

                        story_id = str(s.get("id", i))
                        row_story_ids.append(story_id)

                        # Check if this card is selected
                        is_selected = selected_story_id == story_id

                        if is_selected:
                            card_html = f"""
                            <div class="es-fixed-height-card selected" data-story-id="{story_id}" style="margin-bottom: 20px; cursor: pointer;">
                                <div class="es-card-close-state">
                                    <span class="close-x">✕</span>
                                    <span class="close-text">Close</span>
                                </div>
                            </div>
                            """
                        else:
                            card_html = f"""
                            <div class="es-fixed-height-card" data-story-id="{story_id}" style="margin-bottom: 20px; cursor: pointer;">
                                <div class="es-card-header">
                                    <div class="es-card-title">{title}</div>
                                    <span class="es-card-client-badge">{client}</span>
                                </div>
                                <p class="es-card-desc">{summary}</p>
                                <div class="es-card-meta">
                                    <span class="es-role-badge">{role}</span>
                                    <span class="es-domain-tag">{domain}</span>
                                </div>
                            </div>
                            """
                        st.markdown(card_html, unsafe_allow_html=True)

                        # Hidden Streamlit button with toggle behavior
                        if st.button("", key=f"card_btn_{story_id}"):
                            if st.session_state.get("active_story") == story_id:
                                # Click same card = close
                                st.session_state["active_story"] = None
                            else:
                                # Click different card = select it
                                st.session_state["active_story"] = story_id
                            # Clear other active story sources to prevent conflicts
                            st.session_state.pop("active_story_obj", None)
                            st.session_state.pop("active_story_title", None)
                            st.session_state.pop("active_story_client", None)
                            st.rerun()

                # After each row: render detail if selected story is in this row
                if selected_story_id and selected_story_id in row_story_ids:
                    detail = get_context_story(stories)
                    if detail:
                        render_story_detail(detail, "cards", stories)

            render_pagination(total_results, page_size, offset, "cards")

            # JavaScript to wire HTML card clicks to Streamlit buttons

            components.html(
                """
                <script>
                (function() {
                    var parentDoc = window.parent.document;

                    parentDoc.addEventListener('click', function(e) {
                        var card = e.target.closest('.es-fixed-height-card');
                        if (!card) return;

                        var storyId = card.getAttribute('data-story-id');
                        if (!storyId) return;

                        e.preventDefault();

                        var normalizedId = storyId.replace(/\\|/g, '-');
                        var stBtn = parentDoc.querySelector('[class*="st-key-card_btn_' + normalizedId + '"] button');
                        if (stBtn) {
                            stBtn.click();
                        }
                    });
                })();
                </script>
                """,
                height=0,
            )
    # =========================================================================
    # TIMELINE VIEW
    # =========================================================================

    elif view_mode == "Timeline":
        # Timeline shows all filtered stories grouped by date range
        # No pagination - all stories visible in chronological groups
        # Timeline shows all roles grouped - clear any role filter
        F["roles"] = []

        if not view:
            st.info("No stories match your filters yet.")
            if st.button("Clear filters", key="clear_filters_timeline"):
                reset_all_filters(stories)
                st.rerun()
        else:
            # Render the timeline component

            render_timeline_view(view)

            # Story detail panel (if a story is selected)
            detail = get_context_story(stories)
            render_story_detail(detail, "timeline", stories)

    # === ADD FOOTER ===
    from ui.components.footer import render_footer

    render_footer()
