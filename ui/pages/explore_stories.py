"""
Explore Stories Page - Refactored & Bug-Free

Browse 130+ project case studies with advanced filtering.
Includes semantic search, faceted filters, and pagination.

FIXES:
- Domain Category now actually filters results
- Pill X buttons properly remove filters
- Clear all properly resets all dropdowns
- Extracted duplicate code (detail panel, pagination)
- Centralized state management
"""

import os

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

from config.debug import DEBUG
from services.rag_service import semantic_search
from ui.components.story_detail import render_story_detail
from ui.components.thinking_indicator import render_thinking_indicator
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
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

    _HAS_AGGRID = True
except Exception:
    _HAS_AGGRID = False


# =============================================================================
# HELPER FUNCTIONS - State Management
# =============================================================================


def reset_all_filters(stories: list[dict]):
    """Reset all filters and widget state to defaults - FIXED VERSION"""

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
    }

    keys_to_delete = []
    for key in list(st.session_state.keys()):
        if key not in preserve_keys:
            keys_to_delete.append(key)

    for key in keys_to_delete:
        del st.session_state[key]

    # STEP 3: Recreate filters from scratch
    st.session_state["filters"] = {
        "personas": [],
        "clients": [],
        "domains": [],
        "roles": [],
        "tags": [],
        "q": "",
        "has_metric": False,
    }

    # STEP 4: Set INCREMENTED version counters (using values we saved earlier)
    for filter_type, new_version in version_counters.items():
        version_key = f"_widget_version_{filter_type}"
        st.session_state[version_key] = new_version

    # STEP 5: Reset other state
    st.session_state["_last_domain_group"] = "All"
    st.session_state["page_offset"] = 0
    st.session_state["last_results"] = stories

    # CRITICAL: Preserve the active tab
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = "Explore Stories"


def remove_filter_value(filter_key: str, value: str):
    """Remove a specific value from a filter list and sync widget state"""
    F = st.session_state["filters"]

    # Handle search query specially
    if filter_key == "q":
        F["q"] = ""
        # The version increment is essential to force a widget refresh
        version_key = "_widget_version_q"
        st.session_state[version_key] = st.session_state.get(version_key, 0) + 1

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
    if not isinstance(widget_keys_raw, list):
        widget_keys = [widget_keys_raw]
    else:
        widget_keys = widget_keys_raw

    # Delete both the base key AND any versioned keys that exist
    for widget_key in widget_keys:
        # Delete base key if it exists
        if widget_key in st.session_state:
            del st.session_state[widget_key]

        # Delete versioned keys (check up to version 100 to be safe)
        for v in range(current_version + 2):
            versioned_key = f"{widget_key}_v{v}"
            if versioned_key in st.session_state:
                del st.session_state[versioned_key]


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
def _render_confidence_banner(query: str, confidence: str, result_count: int):
    """Render the tiered confidence banner for search results."""
    BANNER_STYLE = "background: #F3E8FF; border-left: 4px solid #8B5CF6; padding: 12px 16px; margin: 16px 0;"
    TEXT_COLOR_SUCCESS = "#6B21A8"
    TEXT_COLOR_CAUTION = "#4A1D7A"
    TEXT_STYLE_COMMON = "font-size: 14px; font-weight: 600;"

    icon = "🐾"
    text_style_final = f"color: {TEXT_COLOR_SUCCESS}; {TEXT_STYLE_COMMON}"

    if confidence == "high":
        plural = "story" if result_count == 1 else "stories"
        message = f"Found {result_count} matching {plural} for \"{query}\""
    elif confidence == "low":
        icon = "⚠️"
        message = f"Showing closest matches for \"{query}\". Relevance may be low."
        text_style_final = (
            f"color: {TEXT_COLOR_CAUTION}; {TEXT_STYLE_COMMON}; font-style: italic;"
        )
    else:  # confidence == "none"
        message = f"No strong matches for \"{query}\". Matt may not have worked with this client or topic."

    st.markdown(
        f"""
    <div style="{BANNER_STYLE}">
        <span style="{text_style_final}">{icon} {message}</span>
    </div>
    """,
        unsafe_allow_html=True,
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

    st.markdown('<div class="active-chip-row">', unsafe_allow_html=True)

    to_remove = []
    for _i, (_, text, (k, v)) in enumerate(chips):
        # FIX: Create stable unique key using hash instead of position index
        unique_key = f"chip_{k}_{hash((k, v))}"
        if st.button(f"✕ {text}", key=unique_key):
            to_remove.append((k, v))

    clear_all = False
    if st.button("Clear all", key="chip_clear_all"):
        clear_all = True

    st.markdown("</div>", unsafe_allow_html=True)

    if clear_all:
        reset_all_filters(stories)
        st.rerun()
        return True

    if to_remove:
        for k, v in to_remove:
            if k == "q":
                # Calls remove_filter_value, which correctly handles versioning and F["q"] clearing.
                remove_filter_value("q", None)

                # The redundant version increment block is now gone.

                # Clear cached search results
                st.session_state.pop("__last_search_results__", None)
                st.session_state.pop("__last_search_confidence__", None)
                st.session_state.pop("__last_search_query__", None)
            elif k == "has_metric":
                filters["has_metric"] = False
            elif k == "industry":
                filters["industry"] = ""
                version_key = "_widget_version_industry"
                st.session_state[version_key] = st.session_state.get(version_key, 0) + 1
            elif k == "capability":
                filters["capability"] = ""
                version_key = "_widget_version_capability"
                st.session_state[version_key] = st.session_state.get(version_key, 0) + 1
            else:
                remove_filter_value(k, v)

        st.session_state["page_offset"] = 0

        # CRITICAL: Preserve the active tab before rerunning
        if "active_tab" not in st.session_state:
            st.session_state["active_tab"] = "Explore Stories"

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
    <style>
    .pagination {{
        padding: 20px 0;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 8px;
    }}
    .pagination button {{
        padding: 8px 14px;
        border: 1px solid var(--border-color);
        background: var(--bg-card);
        color: var(--text-secondary);
        cursor: pointer;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 500;
        transition: all 0.2s ease;
    }}
    .pagination button:hover:not(:disabled):not(.active) {{
        background: var(--bg-hover);
    }}
    .pagination button.active {{
        background: var(--accent-purple);
        color: white;
        border-color: var(--accent-purple);
    }}
    .pagination button:disabled {{
        opacity: 0.4;
        cursor: not-allowed;
    }}
    .pagination .page-info {{
        padding: 0 12px;
        color: var(--text-muted);
        font-size: 13px;
    }}
    /* Hide Streamlit pagination triggers */
    [class*="st-key-pg_trigger_"] {{
        position: absolute !important;
        left: -9999px !important;
        height: 0 !important;
        overflow: hidden !important;
    }}
    </style>
    <div class="pagination">
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
                var btn = e.target.closest('.pagination button');
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
    Render the Explore Stories page with filters and project listings.

    FIXES:
    - Domain Category now actually filters
    - Pill X buttons work correctly
    - Clear all resets everything properly
    """
    # Hero header with Agy avatar (gray headphones)
    st.markdown(
        """
<div class="conversation-header">
    <div class="conversation-header-content">
        <img class="conversation-agy-avatar" src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_explore_stories.png" width="64" height="64" style="width: 64px; height: 64px; border-radius: 50%; border: 3px solid white !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;" alt="Agy"/>
        <div class="conversation-header-text">
            <h1>Project Stories & Insights</h1>
            <p>Browse 115+ transformation case studies, or ask Agy 🐾 for the deeper context</p>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    explore_css = """
    <style>
    /* Conversation header styles for hero section */
    .conversation-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 0;
        margin: -2rem 0 0 0;
    }

    .conversation-header-content {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        max-width: 1200px;
        margin: 0;
    }

    .conversation-agy-avatar {
        flex-shrink: 0;
        width: 120px !important;
        height: 120px !important;
        border-radius: 50% !important;
        border: 4px solid white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }

    .conversation-header-text h1 {
        color: white !important;
        margin: 0;
        font-size: 2rem;
    }

    .conversation-header-text p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }

    /* Print styles - make content visible when printing */
    @media print {
        /* Hide Streamlit chrome and unnecessary elements */
        header[data-testid="stHeader"],
        div[data-testid="stDecoration"],
        div[data-testid="stToolbar"],
        div[data-testid="stStatusWidget"],
        button,
        .stButton,
        footer {
            display: none !important;
        }

        /* Show main content */
        .main .block-container,
        [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"],
        div[data-baseweb="block"] {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
        }

        /* Reset backgrounds for print */
        body {
            background: white !important;
        }

        /* Ensure text is black for print */
        * {
            color: black !important;
        }

        /* Page breaks */
        .story-detail-pane {
            page-break-before: always;
        }
    }

    /* =========================================================
       FILTER SECTION SPACING - TIGHTENED
       ========================================================= */

    /* Filter container - reduced padding */
    .main [data-testid="stContainer"] {
        padding: 12px 16px !important;
    }

    /* Reduce vertical gaps inside filter container */
    .main [data-testid="stContainer"] [data-testid="stVerticalBlock"] > div {
        margin-bottom: 2px !important;
    }

    /* Search form - remove extra padding and border */
    .main [data-testid="stForm"] {
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
    }

    /* Form inner vertical block - tighter */
    .main [data-testid="stForm"] [data-testid="stVerticalBlock"] > div {
        margin-bottom: 0 !important;
    }

    /* Search submit button - compact */
    .main [data-testid="stFormSubmitButton"] button {
        padding: 6px 12px !important;
        min-height: 38px !important;
        height: 38px !important;
    }

    /* Advanced/Reset buttons - smaller, quieter */
    [class*="st-key-btn_toggle_advanced"] button,
    [class*="st-key-btn_reset_filters"] button {
        padding: 4px 12px !important;
        font-size: 12px !important;
        background: transparent !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-muted) !important;
        min-height: 32px !important;
    }

    [class*="st-key-btn_toggle_advanced"] button:hover {
        background: var(--bg-hover) !important;
    }

    [class*="st-key-btn_reset_filters"] button:hover {
        background: var(--bg-hover) !important;
    }

    /* Filter container styling - WIREFRAME EXACT */
    .explore-filters {
        background: var(--bg-surface);
        padding: 30px;
        border-bottom: 1px solid var(--border-color);
    }

    /* Search input styling - WIREFRAME EXACT */
    .main .stTextInput > div > div > input {
        width: 100% !important;
        padding: 10px 14px !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        background: var(--bg-input) !important;
        color: var(--text-primary) !important;
    }

    .main .stTextInput > div > div > input:focus {
        border-color: var(--accent-purple) !important;
        outline: none !important;
    }

    /* Search form submit button - compact icon button */
    [class*="search_form"] button[kind="secondaryFormSubmit"],
    [class*="search_form"] button[type="submit"],
    .stForm button[kind="secondaryFormSubmit"] {
        width: 40px !important;
        min-width: 40px !important;
        max-width: 40px !important;
        height: 40px !important;
        padding: 0 !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 6px !important;
        background: var(--bg-card) !important;
        color: var(--text-secondary) !important;
        font-size: 16px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    [class*="search_form"] button[kind="secondaryFormSubmit"]:hover,
    [class*="search_form"] button[type="submit"]:hover,
    .stForm button[kind="secondaryFormSubmit"]:hover {
        border-color: var(--accent-purple) !important;
        background: var(--bg-hover) !important;
    }

    /* Selectbox styling - WIREFRAME EXACT */
    .main .stSelectbox > div > div {
        padding: 8px !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 4px !important;
        font-size: 14px !important;
        background: var(--bg-input) !important;
        color: var(--text-primary) !important;
    }

    .main .stSelectbox > div > div:focus-within {
        border-color: var(--accent-purple) !important;
        outline: none !important;
    }

    /* Multiselect styling - WIREFRAME EXACT */
    .main .stMultiSelect > div > div {
        padding: 8px !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 4px !important;
        font-size: 14px !important;
        background: var(--bg-input) !important;
        color: var(--text-primary) !important;
    }

    .main .stMultiSelect > div > div:focus-within {
        border-color: var(--accent-purple) !important;
    }

    /* Label styling - WIREFRAME EXACT */
    .main label[data-testid="stWidgetLabel"] {
        font-size: 12px !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase !important;
        margin-bottom: 4px !important;
    }

    /* Segmented Control (Table/Cards toggle) - WIREFRAME EXACT */
    /* Override Streamlit's default red (#FF4B4B) on active state */

    /* Direct emotion class override (highest specificity) */
    button.st-emotion-cache-1umuqkm.e8vg11g13,
    button.st-emotion-cache-1umuqkm.e8vg11g13:active,
    button.st-emotion-cache-1umuqkm.e8vg11g13:focus,
    button.st-emotion-cache-1umuqkm.e8vg11g13:hover {
        background: #8B5CF6 !important;
        background-color: #8B5CF6 !important;
        border: 1px solid #8B5CF6 !important;
        color: white !important;
    }

    button.st-emotion-cache-1umuqkm.e8vg11g13 p,
    button.st-emotion-cache-1umuqkm.e8vg11g13 * {
        color: white !important;
    }

    /* Inactive button - emotion class */
    button.st-emotion-cache-2mqt7m.e8vg11g12,
    button.st-emotion-cache-2mqt7m.e8vg11g12:active,
    button.st-emotion-cache-2mqt7m.e8vg11g12:focus {
        background: var(--bg-card) !important;
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-secondary) !important;
    }

    button.st-emotion-cache-2mqt7m.e8vg11g12 p,
    button.st-emotion-cache-2mqt7m.e8vg11g12 * {
        color: var(--text-secondary) !important;
    }

    button.st-emotion-cache-2mqt7m.e8vg11g12:hover {
        background: var(--bg-hover) !important;
        background-color: var(--bg-hover) !important;
    }

    /* Target by kind attribute (stable, fallback) */
    button[kind="segmented_controlActive"],
    button[kind="segmented_controlActive"]:active,
    button[kind="segmented_controlActive"]:focus,
    button[kind="segmented_controlActive"]:hover,
    [data-testid="stBaseButton-segmented_controlActive"] {
        background: #8B5CF6 !important;
        border: 1px solid #8B5CF6 !important;
        color: white !important;
    }

    button[kind="segmented_controlActive"] p,
    button[kind="segmented_controlActive"] div,
    button[kind="segmented_controlActive"] *,
    [data-testid="stBaseButton-segmented_controlActive"] p,
    [data-testid="stBaseButton-segmented_controlActive"] * {
        color: white !important;
    }

    /* Inactive button styling */
    button[kind="segmented_control"],
    button[kind="segmented_control"]:active,
    button[kind="segmented_control"]:focus,
    [data-testid="stBaseButton-segmented_control"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-secondary) !important;
    }

    button[kind="segmented_control"] p,
    button[kind="segmented_control"] div,
    button[kind="segmented_control"] *,
    [data-testid="stBaseButton-segmented_control"] p,
    [data-testid="stBaseButton-segmented_control"] * {
        color: var(--text-secondary) !important;
    }

    /* Hover states */
    button[kind="segmented_control"]:hover {
        background: var(--bg-hover) !important;
        border-color: var(--text-muted) !important;
    }

    /* Target the p element inside stButtonGroup */
    .stButtonGroup p,
    [data-testid="stButtonGroup"] p {
        color: inherit !important;
    }

    /* Table styling - WIREFRAME EXACT */
    .main table {
        border-collapse: collapse !important;
    }
    .main thead {
        background: var(--table-header-bg) !important;
    }
    .main th {
        padding: 12px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        text-transform: uppercase !important;
        border-bottom: 2px solid var(--border-color) !important;
        text-align: left !important;
    }
    .main td {
        padding: 16px 12px !important;
        border-bottom: 1px solid var(--border-color) !important;
        font-size: 14px !important;
        color: var(--text-primary) !important;
    }
    /* Story title in table - purple and clickable */
    .main td a {
        color: var(--accent-purple) !important;
        font-weight: 500 !important;
        text-decoration: none !important;
    }
    .main td a:hover {
        text-decoration: underline !important;
    }

    /* Client badge styling - WIREFRAME EXACT */
    .client-badge {
        display: inline-block !important;
        padding: 4px 10px !important;
        background: var(--accent-purple-bg) !important;
        color: var(--accent-purple) !important;
        border-radius: 12px !important;
        font-size: 12px !important;
        font-weight: 500 !important;
    }

    /* Domain tag styling - WIREFRAME EXACT */
    .domain-tag {
        font-size: 12px !important;
        color: var(--text-muted) !important;
    }

    /* Selected row styling - WIREFRAME EXACT */
    .ag-row-selected {
        background: #F3E8FF !important;
        border-left: 4px solid #8B5CF6 !important;
    }
    .ag-row-selected td {
        font-weight: 500 !important;
    }

    /* Button styling - WIREFRAME EXACT but more compact */
    .main .stButton > button {
        padding: 6px 14px !important;
        border: 1px solid var(--border-color) !important;
        background: var(--bg-card) !important;
        cursor: pointer !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        border-radius: 6px !important;
        color: var(--text-secondary) !important;
        transition: all 0.2s ease !important;
    }

    .main .stButton > button:hover {
        background: var(--bg-hover) !important;
    }

    /* View Details button inside cards */
    .card-btn-view-details {
        display: inline-block;
        padding: 10px 20px;
        background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-purple-hover) 100%);
        border: none;
        border-radius: 8px;
        color: white !important;
        font-weight: 600;
        font-size: 14px;
        text-decoration: none !important;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25), 0 1px 3px var(--shadow-color);
    }

    .card-btn-view-details:hover {
        background: linear-gradient(135deg, var(--accent-purple-hover) 0%, #6D28D9 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4), 0 3px 6px rgba(0, 0, 0, 0.15);
        text-decoration: none !important;
    }

    /* Hide the trigger buttons */
    [class*="st-key-card_btn_"] {
        display: none !important;
    }

    /* Ask Agy button - purple to match wireframe (target via key class) */
    [class*="st-key-ask_from_detail"] .stButton > button[kind="primary"],
    div[class*="st-key-ask_from_detail"] button[data-testid="stBaseButton-primary"] {
        background: var(--accent-purple) !important;
        border: 2px solid var(--accent-purple) !important;
        border-radius: 8px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.2s ease !important;
    }

    [class*="st-key-ask_from_detail"] .stButton > button[kind="primary"]:hover,
    div[class*="st-key-ask_from_detail"] button[data-testid="stBaseButton-primary"]:hover {
        background: var(--accent-purple-hover) !important;
        border-color: var(--accent-purple-hover) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3) !important;
    }

    /* Spacing adjustments (scoped to main content) */
    .main .stMultiSelect, .main .stSelectbox, .main .stTextInput {
        margin-bottom: 0px !important;
        margin-top: 0px !important;
    }

    .main [data-testid="stVerticalBlock"] > div {
        gap: 8px !important;
    }

    .main .stButton {
        margin-top: 0px !important;
        margin-bottom: 0px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(5)) > div:nth-child(3) {
        flex: 0 0 75px !important;
        max-width: 75px !important;
    }
    .story-cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
        gap: 20px;
        margin-bottom: 24px;
    }
    .fixed-height-card {
        background: var(--bg-card) !important;
        padding: 24px !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-color) !important;
        height: 380px !important;
        display: flex !important;
        flex-direction: column !important;
        box-shadow: var(--card-shadow) !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    .fixed-height-card:hover {
        box-shadow: var(--hover-shadow) !important;
        border-color: var(--accent-purple) !important;
        transform: translateY(-2px) !important;
    }
    .fixed-height-card.active {
        border-color: var(--accent-purple) !important;
        box-shadow: 0 0 0 3px var(--accent-purple-light) !important;
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
    }
    .card-title {
        font-size: 18px;
        font-weight: 600;
        margin: 0;
        line-height: 1.4;
        color: var(--text-heading) !important;
        flex: 1;
    }
    .card-client-badge {
        background: var(--accent-purple-bg);
        color: var(--accent-purple);
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
        white-space: nowrap;
        margin-left: 12px;
    }
    .card-desc {
        color: var(--text-secondary) !important;
        line-height: 1.6 !important;
        font-size: 14px !important;
        overflow: hidden !important;
        display: -webkit-box !important;
        -webkit-line-clamp: 3 !important;
        -webkit-box-orient: vertical !important;
        flex-grow: 1 !important;
        margin-bottom: 16px !important;
    }
    .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: auto;
        padding-top: 12px;
        border-top: 1px solid var(--border-color);
    }
    .card-role {
        font-size: 12px;
        color: var(--text-muted);
        font-weight: 500;
    }
    .card-domain-tag {
        background: var(--bg-surface);
        color: var(--text-secondary);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 500;
    }
    @media (max-width: 768px) {
        .story-cards-grid {
            grid-template-columns: 1fr !important;
        }
        .fixed-height-card {
            height: auto !important;
            min-height: 280px !important;
        }
        [class*="st-key-card_btn_"] {
            position: absolute !important;
            left: -9999px !important;
            height: 0 !important;
            overflow: hidden !important;
        }

        /* =============================================
           MOBILE FILTER SECTION - TIGHTENED
           ============================================= */

        /* Filter container - tighter padding */
        .main [data-testid="stContainer"] {
            padding: 12px !important;
        }

        /* Reduce all vertical gaps in filter section */
        .main [data-testid="stContainer"] [data-testid="stVerticalBlock"] > div {
            margin-bottom: 4px !important;
        }

        /* Form internal spacing - minimal */
        .main [data-testid="stForm"] [data-testid="stVerticalBlock"] > div {
            margin-bottom: 2px !important;
        }

        /* Search form submit button - compact, full width OK on mobile */
        .main [data-testid="stFormSubmitButton"] button {
            padding: 8px 16px !important;
            min-height: 40px !important;
        }

        /* Hide the spacer div we added for desktop alignment */
        .main [data-testid="stForm"] [data-testid="stHorizontalBlock"] > div:last-child > div[style*="height: 23px"] {
            display: none !important;
        }

        /* Labels - smaller */
        label[data-testid="stWidgetLabel"] {
            margin-bottom: 2px !important;
            font-size: 12px !important;
        }

        /* Inputs - slightly smaller */
        .main .stTextInput > div > div > input {
            padding: 10px 12px !important;
            font-size: 14px !important;
        }

        .main .stSelectbox > div > div {
            padding: 8px 10px !important;
            font-size: 14px !important;
        }

        /* =============================================
           MOBILE BUTTONS - COMPACT
           ============================================= */

        /* All buttons smaller */
        .main .stButton > button {
            padding: 6px 12px !important;
            font-size: 13px !important;
            min-height: 36px !important;
        }

        /* Advanced/Reset buttons - inline them */
        [class*="st-key-btn_toggle_advanced"] button,
        [class*="st-key-btn_reset_filters"] button {
            padding: 6px 10px !important;
            font-size: 11px !important;
            min-height: 32px !important;
        }

        /* Smaller segmented control */
        [data-testid="stSegmentedControl"] button {
            padding: 6px 12px !important;
            font-size: 12px !important;
        }

        /* =============================================
           MOBILE RESULTS HEADER - COMPACT ROW
           ============================================= */

        /* Force results row to wrap nicely */
        div[data-testid="stHorizontalBlock"]:has([data-testid="stSegmentedControl"]) {
            flex-wrap: wrap !important;
            gap: 8px !important;
            align-items: center !important;
        }

        /* "Showing X of Y" - full width on its own row */
        div[data-testid="stHorizontalBlock"]:has([data-testid="stSegmentedControl"]) > div:first-child {
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }

        /* Hide the "SHOW:" label on mobile - save space */
        div[data-testid="stHorizontalBlock"]:has([data-testid="stSegmentedControl"]) > div:nth-child(2) {
            display: none !important;
        }

        /* Page size dropdown - compact */
        div[data-testid="stHorizontalBlock"]:has([data-testid="stSegmentedControl"]) > div:nth-child(3) {
            flex: 0 0 70px !important;
            min-width: 70px !important;
        }

        /* Hide spacer column */
        div[data-testid="stHorizontalBlock"]:has([data-testid="stSegmentedControl"]) > div:nth-child(4) {
            display: none !important;
        }

        /* Table/Cards toggle - takes remaining space */
        div[data-testid="stHorizontalBlock"]:has([data-testid="stSegmentedControl"]) > div:nth-child(5) {
            flex: 1 1 auto !important;
        }

        /* =============================================
           MOBILE TABLE - HORIZONTAL SCROLL
           ============================================= */

        .ag-root-wrapper {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }

        .ag-header,
        .ag-body-viewport {
            min-width: 500px !important;
        }

        /* Hide Domain column on mobile */
        .ag-header-cell[col-id="Domain"],
        .ag-cell[col-id="Domain"] {
            display: none !important;
        }

        /* Tighter table cells */
        .ag-cell {
            padding: 8px !important;
            font-size: 13px !important;
        }

        .ag-header-cell {
            padding: 8px !important;
            font-size: 11px !important;
        }

        /* =============================================
           MOBILE HERO - STACKED
           ============================================= */

        .conversation-header {
            padding: 20px 16px !important;
        }

        .conversation-header-content {
            flex-direction: column !important;
            text-align: center !important;
            gap: 12px !important;
        }

        .conversation-agy-avatar {
            width: 64px !important;
            height: 64px !important;
        }

        .conversation-header-text h1 {
            font-size: 1.4rem !important;
        }

        .conversation-header-text p {
            font-size: 0.9rem !important;
        }
    }
    </style>
    """
    st.markdown(explore_css, unsafe_allow_html=True)

    legacy = {"Stories": "Explore Stories"}
    cur = st.session_state.get("active_tab", "Home")
    if cur in legacy:
        st.session_state["active_tab"] = legacy[cur]

    st.markdown("<a id='stories_top'></a>", unsafe_allow_html=True)

    F = st.session_state["filters"]

    # Initialize pre-filters from landing pages (Phase 4)
    if "prefilter_industry" in st.session_state:
        F["industry"] = st.session_state.pop("prefilter_industry")
    if "prefilter_capability" in st.session_state:
        F["capability"] = st.session_state.pop("prefilter_capability")
        # Clear domains when setting capability
        F["domains"] = []
    if "prefilter_domains" in st.session_state:
        F["domains"] = st.session_state.pop("prefilter_domains")
        # Clear capability when setting domains
        F["capability"] = ""

    # ==================================================================
    # FILTERS SECTION - REDESIGNED (Phase 4)
    # ==================================================================
    with safe_container(border=True):
        # PRIMARY FILTERS ROW: Search (with inline button) | Industry | Capability
        search_col, industry_col, capability_col = st.columns([2, 1, 1.5])

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
                        "Search keywords",
                        value=F.get("q", ""),
                        placeholder="Search by title, client, or keywords...",
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

        # ADVANCED FILTERS (Collapsed by default)
        show_advanced = st.session_state.get("show_advanced_filters", False)

        # Compact button row - pushed left with empty spacer column
        col_toggle, col_reset, _ = st.columns([0.35, 0.25, 1.4])
        with col_toggle:
            toggle_label = (
                "▾ Advanced Filters" if show_advanced else "▸ Advanced Filters"
            )
            if st.button(toggle_label, key="btn_toggle_advanced"):
                st.session_state["show_advanced_filters"] = not show_advanced
                st.rerun()

        with col_reset:
            if st.button("Reset Filters", key="btn_reset_filters"):
                reset_all_filters(stories)
                st.rerun()

        if show_advanced:
            st.markdown("---")
            c1, c2, c3 = st.columns([1.5, 1, 1.5])

            with c1:
                # Client filter (multiselect)
                clients_version = st.session_state.get("_widget_version_clients", 0)
                F["clients"] = st.multiselect(
                    "Client",
                    clients,
                    default=F.get("clients", []),
                    key=f"facet_clients_v{clients_version}",
                )

            with c2:
                # Role filter (multiselect)
                roles_version = st.session_state.get("_widget_version_roles", 0)
                F["roles"] = st.multiselect(
                    "Role",
                    roles,
                    default=F.get("roles", []),
                    key=f"facet_roles_v{roles_version}",
                )

            with c3:
                # Domain filter (multiselect) - now uses Sub-category directly
                domains_version = st.session_state.get("_widget_version_domains", 0)
                F["domains"] = st.multiselect(
                    "Domain",
                    options=domains,
                    default=F.get("domains", []),
                    key=f"facet_domains_v{domains_version}",
                )
    # =========================================================================
    # SEARCH & FILTERING LOGIC (Guarded and Cached)
    # =========================================================================

    # Check if search was intentionally triggered (by form submission)
    search_triggered = st.session_state.pop("__search_triggered__", False)
    current_query = F["q"].strip()
    view = stories  # Default view: all stories

    # Cache keys for readability
    LAST_RESULTS = "__last_search_results__"
    LAST_CONFIDENCE = "__last_search_confidence__"
    LAST_QUERY = "__last_search_query__"

    if current_query and search_triggered:
        # --- PATH 1: Intentional Search (Run Pinecone) ---
        nonsense_check = is_nonsense(current_query)

        if nonsense_check:
            st.session_state["__nonsense_reason__"] = nonsense_check
            # Clear cache to prevent showing old results if the user cancels this search
            st.session_state.pop(LAST_RESULTS, None)
            st.session_state.pop(LAST_CONFIDENCE, None)
            st.session_state.pop(LAST_QUERY, None)

            # Display rejection banner and stop execution immediately
            render_no_match_banner(
                reason=nonsense_check,
                query=current_query,
                overlap=None,
                suppressed=True,
                filters=F,
                context="explore",
            )
            st.session_state["last_results"] = []
            st.stop()
        else:
            # Run expensive semantic search
            search_container = st.empty()
            with search_container:
                render_thinking_indicator()
            try:
                search_result = semantic_search(
                    current_query, filters=F, stories=stories
                )
                view = search_result["results"]
                confidence = search_result["confidence"]

                # Cache results
                st.session_state[LAST_RESULTS] = view
                st.session_state[LAST_CONFIDENCE] = confidence
                st.session_state[LAST_QUERY] = current_query

            finally:
                search_container.empty()

            _render_confidence_banner(current_query, confidence, len(view))

            if confidence == "none":
                view = []

            st.session_state["__nonsense_reason__"] = None
            st.session_state["page_offset"] = 0
            st.session_state["__last_q__"] = current_query

    elif current_query and st.session_state.get(LAST_QUERY) == current_query:
        # --- PATH 2: Reuse Cached Results (Filter Interaction - NO Pinecone Call) ---
        # User interacted with a filter (Advanced Filter, Industry, etc.).
        # Search term is the same as the last submitted query, so reuse the cached set.

        # Retrieve cached results and confidence
        cached_view = st.session_state.get(LAST_RESULTS, [])
        confidence = st.session_state.get(LAST_CONFIDENCE, "none")

        # Show banner based on cached confidence level
        _render_confidence_banner(current_query, confidence, len(cached_view))

        if confidence == "none":
            cached_view = []

        # Apply filters EXCEPT keyword query - Pinecone already did semantic matching.
        # Re-applying keyword filter would remove valid semantic matches that don't
        # contain the exact query tokens (e.g., "Truist" search returning RBC stories).
        filters_without_q = {k: v for k, v in F.items() if k != "q"}
        view = [s for s in cached_view if matches_filters(s, filters_without_q)]

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
                F.get("has_metric"),
            ]
        )

        if has_filters:
            view = [s for s in stories if matches_filters(s, F)]
        else:
            view = stories

    # Final step for all paths
    st.session_state["last_results"] = view
    st.session_state["__results_count__"] = len(view)
    # =========================================================================
    # END SEARCH & FILTERING LOGIC
    # =========================================================================

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

    if view_mode != prev_view_mode:
        st.session_state["page_offset"] = 0
        st.session_state["_prev_explore_view_mode"] = view_mode

    page_size_option = st.session_state.get("page_size_select", TABLE_PAGE_SIZE_DEFAULT)
    page_size = page_size_option if view_mode == "Table" else CARDS_PAGE_SIZE
    offset = int(st.session_state.get("page_offset", 0))
    start = offset + 1
    end = min(offset + page_size, total_results)

    col1, col2, col3, spacer, col4 = st.columns([2.2, 0.18, 0.5, 0.12, 1.2])

    with col1:
        results_html = f"""
        <div style="display: flex; align-items: center; min-height: 44px; color: var(--text-color); font-size: 14px;">
            Showing &nbsp;<strong>{start}–{end}</strong>&nbsp; of &nbsp;<strong>{total_results}</strong>&nbsp; projects
        </div>
        """
        st.markdown(results_html, unsafe_allow_html=True)

    with col2:
        st.markdown(
            '<div style="display: flex; align-items: center; min-height: 44px; font-size: 14px; font-weight: 500;">SHOW:</div>',
            unsafe_allow_html=True,
        )

    with col3:
        # Remove the extra CSS - just let it be
        page_size_option = st.selectbox(
            "page_size",
            options=TABLE_PAGE_SIZE_OPTIONS,
            index=0,
            key="page_size_select",
            label_visibility="collapsed",
        )

    with col4:
        # Remove the padding-top wrapper
        view_mode = st.segmented_control(
            "View",
            options=["Table", "Cards"],
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
            <div class="table-swipe-hint">
                <span>← Swipe to see more columns →</span>
            </div>
            <style>
            .table-swipe-hint {
                display: none;
                text-align: center;
                padding: 8px 16px;
                background: var(--bg-surface);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                margin-bottom: 12px;
                font-size: 13px;
                color: var(--text-muted);
            }
            @media (max-width: 767px) {
                .table-swipe-hint {
                    display: block;
                }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        def _row(s: dict) -> dict:
            dom = (s.get("Sub-category") or "").split(" / ")[-1]
            return {
                "ID": s.get("id", ""),
                "Title": s.get("Title", ""),
                "Client": s.get("Client", ""),
                "Role": s.get("Role", ""),
                "Domain": dom,
            }

        view_paginated = view[offset : offset + page_size]
        rows = [_row(s) for s in view_paginated]
        df = pd.DataFrame(rows)
        show_cols = [
            c for c in ["Title", "Client", "Role", "Domain"] if c in df.columns
        ]
        show_df = df[show_cols] if show_cols else df

        if not _HAS_AGGRID:
            st.warning(
                "Row-click requires st-aggrid. Install: `pip install streamlit-aggrid`"
            )
            st.dataframe(show_df, hide_index=True, use_container_width=True)
        else:
            df_view = df[["ID"] + show_cols] if show_cols else df
            gob = GridOptionsBuilder.from_dataframe(df_view)
            gob.configure_default_column(resizable=True, sortable=True, filter=True)

            gob.configure_column("ID", hide=True)
            gob.configure_column("Title", flex=9)
            gob.configure_column(
                "Client",
                flex=4,
                cellRenderer="""
                    function(params) {
                        return '<span class="client-badge">' + params.value + '</span>';
                    }
                """,
            )
            gob.configure_column("Role", flex=3)
            gob.configure_column(
                "Domain",
                flex=4,
                cellRenderer="""
                    function(params) {
                        return '<span class="domain-tag">' + params.value + '</span>';
                    }
                """,
            )

            gob.configure_selection(selection_mode="single", use_checkbox=False)
            gob.configure_pagination(enabled=False)

            opts = gob.build()
            opts["suppressRowClickSelection"] = False
            opts["rowSelection"] = "single"
            opts["rowHeight"] = TABLE_ROW_HEIGHT

            grid = AgGrid(
                df_view,
                gridOptions=opts,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                allow_unsafe_jscode=True,
                theme="streamlit",
                fit_columns_on_grid_load=True,
                height=TABLE_HEIGHT,
            )

            if isinstance(grid, dict):
                sr = grid.get("selected_rows") or grid.get("selectedRows") or []
            else:
                sr = getattr(grid, "selected_rows", None)

            if isinstance(sr, pd.DataFrame):
                sel_rows = sr.to_dict("records")
            elif isinstance(sr, list):
                sel_rows = sr
            elif isinstance(sr, dict):
                sel_rows = [sr]
            else:
                sel_rows = []

            if sel_rows:
                st.session_state["active_story"] = sel_rows[0].get("ID")

        render_pagination(total_results, page_size, offset, "table")
        detail = get_context_story(stories)
        render_story_detail(detail, "table", stories)

    # =========================================================================
    # CARDS VIEW
    # =========================================================================

    else:
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
            num_rows = (len(view_window) + CARDS_PER_ROW - 1) // CARDS_PER_ROW

            for row in range(num_rows):
                cols = st.columns(CARDS_PER_ROW)
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

                        # Vary button text based on story attributes for better UX
                        button_texts = [
                            "View Details →",
                            "See Project →",
                            "Learn More →",
                            "Explore Story →",
                            "Read More →",
                        ]
                        button_text = button_texts[i % len(button_texts)]
                        button_id = f"btn-story-{story_id}"

                        card_html = f"""
                        <div class="fixed-height-card" style="margin-bottom: 20px;">
                            <div class="card-header">
                                <div class="card-title">{title}</div>
                                <span class="card-client-badge">{client}</span>
                            </div>
                            <p class="card-desc">{summary}</p>
                            <div class="card-footer">
                                <span class="card-role">{role}</span>
                                <span class="card-domain-tag">{domain}</span>
                            </div>
                            <div style="margin-top: 16px;">
                                <a id="{button_id}" class="card-btn-view-details">{button_text}</a>
                            </div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)

                        # Hidden Streamlit button
                        if st.button("", key=f"card_btn_{story_id}"):
                            st.session_state["active_story"] = story_id
                            st.rerun()

            render_pagination(total_results, page_size, offset, "cards")
            detail = get_context_story(stories)
            render_story_detail(detail, "cards", stories)

            # JavaScript to wire HTML buttons to Streamlit buttons
            # Build button mapping for all story cards
            story_ids = [str(s.get('id', i)) for i, s in enumerate(view_window)]

            # Generate button map entries
            button_map_entries = []
            for story_id in story_ids:
                button_map_entries.append(
                    f"'btn-story-{story_id}': 'card_btn_{story_id}'"
                )

            # JavaScript to wire HTML buttons to Streamlit buttons using event delegation
            components.html(
                """
                <script>
                (function() {
                    var parentDoc = window.parent.document;

                    parentDoc.addEventListener('click', function(e) {
                        var btn = e.target.closest('.card-btn-view-details');
                        if (!btn) return;

                        e.preventDefault();

                        var btnId = btn.id;
                        if (!btnId || !btnId.startsWith('btn-story-')) return;

                        var storyId = btnId.replace('btn-story-', '');
                        console.log('[Story Cards] Clicked story:', storyId);

                        // Replace pipe with hyphen to match Streamlit's class naming
                        var normalizedId = storyId.replace(/\\|/g, '-');
                        console.log('[Story Cards] Normalized ID:', normalizedId);

                        var stBtn = parentDoc.querySelector('[class*="st-key-card_btn_' + normalizedId + '"] button');
                        if (stBtn) {
                            console.log('[Story Cards] Triggering Streamlit button');
                            stBtn.click();
                        } else {
                            console.warn('[Story Cards] Streamlit button not found for:', normalizedId);
                        }
                    });
                })();
                </script>
                """,
                height=0,
            )

    # === ADD FOOTER ===
    from ui.components.footer import render_footer

    render_footer()
