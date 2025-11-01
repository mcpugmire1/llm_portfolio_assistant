"""
Explore Stories Page - Refactored & Bug-Free

Browse 120+ project case studies with advanced filtering.
Includes semantic search, faceted filters, and pagination.

FIXES:
- Domain Category now actually filters results
- Pill X buttons properly remove filters
- Clear all properly resets all dropdowns
- Extracted duplicate code (detail panel, pagination)
- Centralized state management
"""

import os
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

from config.debug import DEBUG
from config.settings import get_conf
from services.pinecone_service import (
    PINECONE_INDEX_NAME,
    PINECONE_MIN_SIM,
    PINECONE_NAMESPACE,
    SEARCH_TOP_K,
    VECTOR_BACKEND,
    W_KW,
    W_PC,
    _DEF_DIM,
    _PINECONE_INDEX,
    _init_pinecone,
    _safe_json,
    _summarize_index_stats,
)
from services.rag_service import _KNOWN_VOCAB, semantic_search
from utils.filters import matches_filters
from utils.formatting import (
    METRIC_RX,
    _format_key_points,
    build_5p_summary,
    story_has_metric,
    strongest_metric_line,
)
from utils.ui_helpers import dbg, render_no_match_banner, safe_container
from utils.validation import _tokenize, is_nonsense, token_overlap_ratio
from streamlit_js_eval import streamlit_js_eval

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

def reset_all_filters(stories: List[dict]):
    """Reset all filters and widget state to defaults - FIXED VERSION"""
    
    # STEP 1: READ current version counters BEFORE deleting anything
    version_counters = {}
    for filter_type in ["q", "personas", "clients", "domains", "roles", "tags", "domain_cat"]:
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
        "_prev_explore_view_mode"
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
    
    # Remove from filter state
    if filter_key in F and isinstance(F[filter_key], list):
        if value in F[filter_key]:
            F[filter_key].remove(value)
    
    # Increment widget version to force recreation with fresh state
    version_key = f"_widget_version_{filter_key}"
    current_version = st.session_state.get(version_key, 0)
    st.session_state[version_key] = current_version + 1
    
    # Delete ALL versions of the widget keys (both base and versioned)
    widget_map = {
        "clients": "facet_clients",
        "domains": ["facet_domains_all", "facet_subdomains"],
        "roles": "facet_roles",
        "tags": "facet_tags",
        "personas": "facet_personas",
    }
    
    widget_keys = widget_map.get(filter_key, [])
    if not isinstance(widget_keys, list):
        widget_keys = [widget_keys]
    
    # Delete both the base key AND any versioned keys that exist
    for widget_key in widget_keys:
        # Delete base key if it exists
        if widget_key in st.session_state:
            del st.session_state[widget_key]
        
        # Delete versioned keys (check up to version 100 to be safe)
        for v in range(current_version + 2):  # Check current and previous versions
            versioned_key = f"{widget_key}_v{v}"
            if versioned_key in st.session_state:
                del st.session_state[versioned_key]


def build_domain_options(domains: List[str]) -> Tuple[List[str], List[Tuple[str, str, str]]]:
    """Parse domain strings into categories and build options list"""
    domain_parts = [
        (d.split(" / ")[0], (d.split(" / ")[1] if " / " in d else ""), d)
        for d in domains
    ]
    groups = sorted({cat for cat, sub, full in domain_parts if full})
    return groups, domain_parts


# =============================================================================
# HELPER FUNCTIONS - Story Navigation
# =============================================================================


def on_ask_this_story(s: dict):
    """Set context to a specific story and open Ask MattGPT tab"""
    st.session_state["active_story"] = s.get("id")
    client = s.get("Client", "")
    title = s.get("Title", "")
    st.session_state["seed_prompt"] = (
        f"How were these outcomes achieved for {client} — {title}? "
        "Focus on tradeoffs, risks, and replicable patterns."
    )
    st.session_state["active_tab"] = "Ask MattGPT"
    st.session_state["ask_input"] = st.session_state.get("seed_prompt", "")
    st.session_state["__ctx_locked__"] = True
    st.session_state["__ask_from_suggestion__"] = True
    st.rerun()


def get_context_story(stories: List[dict]) -> Optional[dict]:
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
        if (sid and xid and str(xid) == str(sid)) or (at and xt == at and (not ac or xc == ac)):
            return cand

    return None


# =============================================================================
# HELPER FUNCTIONS - UI Components
# =============================================================================


def render_filter_chips(filters: dict, stories: List[dict]) -> bool:
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
    for i, (_, text, (k, v)) in enumerate(chips):
        # FIX: Create stable unique key using hash instead of position index
        # This prevents the wrong pill from being removed when indices shift
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
                filters["q"] = ""
            elif k == "has_metric":
                filters["has_metric"] = False
            elif k == "industry":
                filters["industry"] = ""
            elif k == "capability":
                filters["capability"] = ""
            else:
                remove_filter_value(k, v)
        
        st.session_state["page_offset"] = 0
        
        # CRITICAL: Preserve the active tab before rerunning
        if "active_tab" not in st.session_state:
            st.session_state["active_tab"] = "Explore Stories"
        
        st.rerun()
        return True
    
    return False


def render_detail_panel(detail: Optional[dict], key_suffix: str, stories: List[dict]):
    """Render the story detail panel with full STAR narrative and sidebar (matches wireframe)"""
    hr_style = "margin: 16px 0 12px 0; border: none; border-top: 3px solid #8B5CF6;"
    st.markdown(f"<hr style='{hr_style}'>", unsafe_allow_html=True)

    if not detail:
        st.info("Click a row/card above to view details.")
        return

    # Extract data
    title = detail.get("Title", "Untitled")
    client = detail.get("Client", "Unknown")
    role = detail.get("Role", "Unknown")
    domain = detail.get("Sub-category", "Unknown")
    start_date = detail.get("Start_Date", "")
    end_date = detail.get("End_Date", "")

    # STAR sections
    situation = detail.get("Situation", [])
    task = detail.get("Task", [])
    action = detail.get("Action", [])
    result = detail.get("Result", [])

    # Sidebar data
    public_tags = detail.get("public_tags", []) or []
    competencies = detail.get("Competencies", []) or []
    performance = detail.get("Performance", []) or []

    # Format dates
    date_range = ""
    if start_date or end_date:
        date_range = f"{start_date or '?'} - {end_date or '?'}"

    with safe_container(border=True):
        # HEADER: Title + Metadata + Action Buttons
        header_col1, header_col2 = st.columns([4, 1])

        with header_col1:
            st.markdown(f"<h2 style='font-size: 24px; font-weight: 700; color: var(--text-color); margin-bottom: 12px; line-height: 1.3;'>{title}</h2>", unsafe_allow_html=True)

            # Metadata with icons
            meta_html = f"""
            <div style="display: flex; gap: 20px; flex-wrap: wrap; align-items: center; font-size: 14px; color: #7f8c8d; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span>🏢</span>
                    <strong style="color: var(--text-color);">{client}</strong>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span>👤</span>
                    <strong style="color: var(--text-color);">{role}</strong>
                </div>
                {'<div style="display: flex; align-items: center; gap: 8px;"><span>📅</span><span>' + date_range + '</span></div>' if date_range else ''}
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span>🏷️</span>
                    <span>{domain}</span>
                </div>
            </div>
            """
            st.markdown(meta_html, unsafe_allow_html=True)

        with header_col2:
            # Share and Export buttons (MVP implementation per UX spec)
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("🔗", key=f"share_{key_suffix}_{detail.get('id', 'x')}", help="Share (Copy link)", use_container_width=True):
                    # MVP: Provide instructions since Streamlit doesn't support clipboard API
                    st.toast("💡 To share: Copy the URL from your browser address bar", icon="ℹ️")
            with btn_col2:
                if st.button("📄", key=f"export_{key_suffix}_{detail.get('id', 'x')}", help="Export (Print)", use_container_width=True):
                    st.toast("Print dialog opened. Save as PDF.", icon="ℹ️")
                    # Use streamlit-js-eval to trigger browser print dialog
                    streamlit_js_eval(js_expressions="window.print()", key=f"print_{key_suffix}")

        st.markdown("<hr style='border: none; border-top: 2px solid #e0e0e0; margin: 20px 0;'>", unsafe_allow_html=True)

        # TWO-COLUMN LAYOUT: STAR sections (left) + Sidebar (right)
        main_col, sidebar_col = st.columns([2, 1])

        with main_col:
            # SITUATION
            if situation and len(situation) > 0:
                st.markdown("""
                <div style="margin-bottom: 24px;">
                    <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                        <span>📍</span><span>SITUATION</span>
                    </div>
                    <div style="font-size: 14px; color: var(--text-color); line-height: 1.7;">
                """, unsafe_allow_html=True)
                for s in situation:
                    if s:
                        st.markdown(f"<p>{s}</p>", unsafe_allow_html=True)
                st.markdown("</div></div>", unsafe_allow_html=True)

            # TASK
            if task and len(task) > 0:
                st.markdown("""
                <div style="margin-bottom: 24px;">
                    <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                        <span>🎯</span><span>TASK</span>
                    </div>
                    <div style="font-size: 14px; color: var(--text-color); line-height: 1.7;">
                """, unsafe_allow_html=True)
                for t in task:
                    if t:
                        st.markdown(f"<p>{t}</p>", unsafe_allow_html=True)
                st.markdown("</div></div>", unsafe_allow_html=True)

            # ACTION
            if action and len(action) > 0:
                st.markdown("""
                <div style="margin-bottom: 24px;">
                    <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                        <span>⚡</span><span>ACTION</span>
                    </div>
                    <div style="font-size: 14px; color: var(--text-color); line-height: 1.7;">
                        <ul style="margin: 12px 0; padding-left: 20px;">
                """, unsafe_allow_html=True)
                for a in action:
                    if a:
                        st.markdown(f"<li style='margin-bottom: 8px;'>{a}</li>", unsafe_allow_html=True)
                st.markdown("</ul></div></div>", unsafe_allow_html=True)

            # RESULT
            if result and len(result) > 0:
                st.markdown("""
                <div style="margin-bottom: 24px;">
                    <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                        <span>🏆</span><span>RESULT</span>
                    </div>
                    <div style="font-size: 14px; color: var(--text-color); line-height: 1.7;">
                        <ul style="margin: 12px 0; padding-left: 20px;">
                """, unsafe_allow_html=True)
                for r in result:
                    if r:
                        st.markdown(f"<li style='margin-bottom: 8px;'>{r}</li>", unsafe_allow_html=True)
                st.markdown("</ul></div></div>", unsafe_allow_html=True)

        with sidebar_col:
            # TECHNOLOGIES & PRACTICES (Tags)
            if public_tags and len(public_tags) > 0:
                st.markdown("""
                <div style="margin-bottom: 24px; padding-bottom: 24px; border-bottom: 1px solid #e0e0e0;">
                    <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #7f8c8d; margin-bottom: 12px;">
                        TECHNOLOGIES & PRACTICES
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                """, unsafe_allow_html=True)
                for tag in public_tags[:10]:  # Limit to 10 tags
                    if tag:
                        st.markdown(f'<span style="background: #ecf0f1; padding: 6px 12px; border-radius: 12px; font-size: 12px; color: #555; font-weight: 500;">{tag}</span>', unsafe_allow_html=True)
                st.markdown("</div></div>", unsafe_allow_html=True)

            # CORE COMPETENCIES (List)
            if competencies and len(competencies) > 0:
                st.markdown("""
                <div style="margin-bottom: 24px; padding-bottom: 24px; border-bottom: 1px solid #e0e0e0;">
                    <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #7f8c8d; margin-bottom: 12px;">
                        CORE COMPETENCIES
                    </div>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                """, unsafe_allow_html=True)
                for comp in competencies:
                    if comp:
                        st.markdown(f'<li style="padding: 8px 0; font-size: 13px; color: #555; border-bottom: 1px solid #ecf0f1;">{comp}</li>', unsafe_allow_html=True)
                st.markdown("</ul></div>", unsafe_allow_html=True)

            # KEY METRICS (Green boxes with extracted numbers)
            metrics = []
            for perf in performance:
                if perf and ("%" in perf or "x" in perf.lower() or "month" in perf.lower() or "week" in perf.lower()):
                    # Extract first number/percentage for display
                    import re
                    match = re.search(r'(\d+[%xX]?|\d+\+?)', perf)
                    if match:
                        metrics.append((match.group(1), perf[:50]))

            if metrics:
                st.markdown("""
                <div style="margin-bottom: 24px;">
                    <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #7f8c8d; margin-bottom: 12px;">
                        KEY METRICS
                    </div>
                """, unsafe_allow_html=True)
                for value, label in metrics[:4]:  # Limit to 4 metrics
                    st.markdown(f"""
                    <div style="background: #f8f9fa; padding: 12px; border-radius: 6px; border-left: 3px solid #27ae60; margin-bottom: 12px;">
                        <div style="font-size: 18px; font-weight: 700; color: #27ae60; margin-bottom: 4px;">{value}</div>
                        <div style="font-size: 11px; color: #7f8c8d; text-transform: uppercase;">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        # ASK AGY ABOUT THIS (Full-width CTA at bottom)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <p style="text-align: center; margin-bottom: 20px; color: #555; font-size: 14px;">💬 Want to know more about this project?</p>
        """, unsafe_allow_html=True)

        # Ask button centered using columns
        _, col_center, _ = st.columns([1.5, 1, 1.5])
        with col_center:
            btn_key = f"ask_from_detail_{key_suffix}_{detail.get('id', 'x')}"
            if st.button("Ask Agy 🐾 About This", key=btn_key, type="primary", use_container_width=True):
                on_ask_this_story(detail)


def render_pagination(total_results: int, page_size: int, offset: int, view_mode: str):
    """Render numbered pagination controls (shared by views)"""
    total_pages = (total_results + page_size - 1) // page_size
    current_page = (offset // page_size) + 1

    if total_pages <= 1:
        return

    pagination_css = """
        <style>
        .pagination-info {
            color: var(--text-color);
            opacity: 0.7;
            font-size: 14px;
        }
        /* Pagination buttons - WIREFRAME EXACT */
        div[data-testid="column"] .stButton > button {
            padding: 8px 14px !important;
            border: 2px solid #ddd !important;
            background: white !important;
            cursor: pointer !important;
            border-radius: 4px !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            color: #555 !important;
            transition: all 0.2s ease !important;
        }
        /* NUCLEAR: Force ALL multiselect pills to purple to match wireframe */
        [data-testid="stMultiSelect"] [data-baseweb="tag"],
        [data-baseweb="tag"],
        .stMultiSelect [data-baseweb="tag"],
        div[data-baseweb="tag"],
        span[data-baseweb="tag"] {
            background-color: #8B5CF6 !important;
            background: #8B5CF6 !important;
            border-color: #8B5CF6 !important;
        }

        /* Text color in pills */
        [data-testid="stMultiSelect"] [data-baseweb="tag"] *,
        [data-baseweb="tag"] *,
        [data-baseweb="tag"] span {
            color: white !important;
        }

        /* X button (close icon) */
        [data-testid="stMultiSelect"] [data-baseweb="tag"] svg,
        [data-baseweb="tag"] svg,
        [data-baseweb="tag"] svg path {
            fill: white !important;
            color: white !important;
        }

        /* Hover state */
        [data-testid="stMultiSelect"] [data-baseweb="tag"]:hover,
        [data-baseweb="tag"]:hover {
            background-color: #7C3AED !important;
            background: #7C3AED !important;
        }

        /* Override Streamlit's default red/orange pills */
        .stMultiSelect span[data-baseweb="tag"][style*="background"],
        [data-baseweb="tag"][style*="background"] {
            background-color: #8B5CF6 !important;
            background: #8B5CF6 !important;
        }

        div[data-testid="column"] .stButton > button:hover {
            background: #f5f5f5 !important;
        }
        /* Pagination active state - WIREFRAME EXACT */
        .pagination-active {
            background: #8B5CF6;
            color: white;
            border: 2px solid #8B5CF6;
            padding: 8px 14px;
            border-radius: 4px;
            font-size: 13px;
            font-weight: 600;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .pagination-disabled {
            text-align: center;
            color: #888;
            opacity: 0.4;
            padding: 6px 14px;
            font-size: 13px;
        }
        </style>
        """
    st.markdown(pagination_css, unsafe_allow_html=True)

    if total_pages <= 7:
        page_numbers = list(range(1, total_pages + 1))
    else:
        if current_page <= 4:
            page_numbers = list(range(1, 6)) + ["...", total_pages]
        elif current_page >= total_pages - 3:
            page_numbers = [1, "..."] + list(range(total_pages - 4, total_pages + 1))
        else:
            page_numbers = [1, "...", current_page - 1, current_page, current_page + 1, "...", total_pages]

    cols = st.columns([0.6, 0.6] + [0.35] * len(page_numbers) + [0.6, 0.6, 1.2])
    col_idx = 0

    with cols[col_idx]:
        if current_page > 1:
            if st.button("First", key=f"btn_first_{view_mode}", use_container_width=True):
                st.session_state["page_offset"] = 0
                st.rerun()
        else:
            st.markdown("<div class='pagination-disabled'>First</div>", unsafe_allow_html=True)
    col_idx += 1

    with cols[col_idx]:
        if current_page > 1:
            if st.button("Prev", key=f"btn_prev_{view_mode}", use_container_width=True):
                st.session_state["page_offset"] = offset - page_size
                st.rerun()
        else:
            st.markdown("<div class='pagination-disabled'>Prev</div>", unsafe_allow_html=True)
    col_idx += 1

    for page_num in page_numbers:
        with cols[col_idx]:
            if page_num == "...":
                st.markdown("<div style='text-align: center; padding: 6px; color: #666;'>...</div>", unsafe_allow_html=True)
            elif page_num == current_page:
                st.markdown(f"<div class='pagination-active'>{page_num}</div>", unsafe_allow_html=True)
            else:
                if st.button(str(page_num), key=f"btn_page_{view_mode}_{page_num}", use_container_width=True):
                    st.session_state["page_offset"] = (page_num - 1) * page_size
                    st.rerun()
        col_idx += 1

    with cols[col_idx]:
        if current_page < total_pages:
            if st.button("Next", key=f"btn_next_{view_mode}", use_container_width=True):
                st.session_state["page_offset"] = offset + page_size
                st.rerun()
        else:
            st.markdown("<div class='pagination-disabled'>Next</div>", unsafe_allow_html=True)
    col_idx += 1

    with cols[col_idx]:
        if current_page < total_pages:
            if st.button("Last", key=f"btn_last_{view_mode}", use_container_width=True):
                st.session_state["page_offset"] = (total_pages - 1) * page_size
                st.rerun()
        else:
            st.markdown("<div class='pagination-disabled'>Last</div>", unsafe_allow_html=True)
    col_idx += 1

    with cols[col_idx]:
        page_info_html = f"<div class='pagination-info' style='text-align: right; padding: 6px;'>Page {current_page} of {total_pages}</div>"
        st.markdown(page_info_html, unsafe_allow_html=True)


# =============================================================================
# MAIN RENDER FUNCTION
# =============================================================================


def render_explore_stories(
    stories: List[dict],
    industries: List[str],
    capabilities: List[str],
    clients: List[str],
    domains: List[str],
    roles: List[str],
    tags: List[str],
    personas_all: List[str],
):
    """
    Render the Explore Stories page with filters and project listings.

    FIXES:
    - Domain Category now actually filters
    - Pill X buttons work correctly
    - Clear all resets everything properly
    """
    # Hero header - pure HTML to prevent auto-scroll (matches home page pattern)
    # Margin: negative top only (-1rem 0), no side margins to match navbar width
    st.markdown('''
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 60px 40px 80px 40px; margin: -1rem 0 40px 0; border-radius: 0; min-height: 350px;">
        <div style="max-width: 1200px; margin: 0 auto; text-align: center; color: white;">
            <h1 style="font-size: 42px; font-weight: 700; margin-bottom: 16px; color: white !important;">Project Case Studies</h1>
            <p style="font-size: 18px; opacity: 0.95; max-width: 700px; margin: 0 auto; line-height: 1.6;">
                See how digital transformation happens in practice. Browse case studies, then click Ask MattGPT for the inside story.
            </p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    explore_css = """
    <style>
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

    /* Filter container styling - WIREFRAME EXACT */
    .explore-filters {
        background: #fafafa;
        padding: 30px;
        border-bottom: 1px solid #e0e0e0;
    }

    /* Search input styling - WIREFRAME EXACT */
    .main .stTextInput > div > div > input {
        width: 100% !important;
        padding: 12px 16px !important;
        border: 2px solid #ddd !important;
        border-radius: 6px !important;
        font-size: 14px !important;
    }

    .main .stTextInput > div > div > input:focus {
        border-color: #8B5CF6 !important;
        outline: none !important;
    }

    /* Selectbox styling - WIREFRAME EXACT */
    .main .stSelectbox > div > div {
        padding: 10px !important;
        border: 2px solid #ddd !important;
        border-radius: 4px !important;
        font-size: 14px !important;
        background: white !important;
    }

    .main .stSelectbox > div > div:focus-within {
        border-color: #8B5CF6 !important;
        outline: none !important;
    }

    /* Multiselect styling - WIREFRAME EXACT */
    .main .stMultiSelect > div > div {
        padding: 10px !important;
        border: 2px solid #ddd !important;
        border-radius: 4px !important;
        font-size: 14px !important;
        background: white !important;
    }

    .main .stMultiSelect > div > div:focus-within {
        border-color: #8B5CF6 !important;
    }

    /* Label styling - WIREFRAME EXACT */
    .main label[data-testid="stWidgetLabel"] {
        font-size: 12px !important;
        font-weight: 600 !important;
        color: #555 !important;
        text-transform: uppercase !important;
        margin-bottom: 6px !important;
    }

    /* Segmented Control (Table/Cards toggle) - WIREFRAME EXACT */
    [data-testid="stSegmentedControl"] button {
        padding: 8px 16px !important;
        border: 2px solid #ddd !important;
        background: white !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #555 !important;
    }
    [data-testid="stSegmentedControl"] button[data-baseweb="button"][aria-pressed="true"] {
        background: #8B5CF6 !important;
        color: white !important;
        border-color: #8B5CF6 !important;
    }

    /* Table styling - WIREFRAME EXACT */
    .main table {
        border-collapse: collapse !important;
    }
    .main thead {
        background: #ecf0f1 !important;
    }
    .main th {
        padding: 12px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        color: #2c3e50 !important;
        text-transform: uppercase !important;
        border-bottom: 2px solid #bdc3c7 !important;
        text-align: left !important;
    }
    .main td {
        padding: 16px 12px !important;
        border-bottom: 1px solid #e0e0e0 !important;
        font-size: 14px !important;
        color: #2c3e50 !important;
    }
    /* Story title in table - purple and clickable */
    .main td a {
        color: #8B5CF6 !important;
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
        background: #e3f2fd !important;
        color: #1976d2 !important;
        border-radius: 12px !important;
        font-size: 12px !important;
        font-weight: 500 !important;
    }

    /* Domain tag styling - WIREFRAME EXACT */
    .domain-tag {
        font-size: 12px !important;
        color: #7f8c8d !important;
    }

    /* Selected row styling - WIREFRAME EXACT */
    .ag-row-selected {
        background: #F3E8FF !important;
        border-left: 4px solid #8B5CF6 !important;
    }
    .ag-row-selected td {
        font-weight: 500 !important;
    }

    /* Button styling - WIREFRAME EXACT */
    .main .stButton > button {
        padding: 8px 16px !important;
        border: 2px solid #ddd !important;
        background: white !important;
        cursor: pointer !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        color: #555 !important;
        transition: all 0.2s ease !important;
    }

    .main .stButton > button:hover {
        background: #f5f5f5 !important;
    }

    /* Primary button (View Details) - Premium subtle style - NUCLEAR SELECTOR */
    div[class*="st-key-card_"] button[data-testid="stBaseButton-primary"],
    div[class*="st-key-card_"] .stButton > button[kind="primary"],
    [data-testid="column"] [class*="st-key-card_"] button {
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%) !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25), 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    div[class*="st-key-card_"] button[data-testid="stBaseButton-primary"]:hover,
    div[class*="st-key-card_"] .stButton > button[kind="primary"]:hover,
    [data-testid="column"] [class*="st-key-card_"] button:hover {
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4), 0 3px 6px rgba(0, 0, 0, 0.15) !important;
    }

    /* Ask Agy button - purple to match wireframe (target via key class) */
    [class*="st-key-ask_from_detail"] .stButton > button[kind="primary"],
    div[class*="st-key-ask_from_detail"] button[data-testid="stBaseButton-primary"] {
        background: #8B5CF6 !important;
        border: 2px solid #8B5CF6 !important;
        border-radius: 8px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.2s ease !important;
    }

    [class*="st-key-ask_from_detail"] .stButton > button[kind="primary"]:hover,
    div[class*="st-key-ask_from_detail"] button[data-testid="stBaseButton-primary"]:hover {
        background: #7C3AED !important;
        border-color: #7C3AED !important;
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
        background: white !important;
        padding: 24px !important;
        border-radius: 8px !important;
        border: 1px solid #e5e7eb !important;
        height: 380px !important;
        display: flex !important;
        flex-direction: column !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    .fixed-height-card:hover {
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.15) !important;
        border-color: #8B5CF6 !important;
        transform: translateY(-2px) !important;
    }
    .fixed-height-card.active {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
    }
    .card-desc {
        color: #4a5568 !important;
        line-height: 1.6 !important;
        font-size: 14px !important;
        overflow: hidden !important;
        display: -webkit-box !important;
        -webkit-line-clamp: 3 !important;
        -webkit-box-orient: vertical !important;
        flex-grow: 1 !important;
    }
    @media (max-width: 768px) {
        .story-cards-grid {
            grid-template-columns: 1fr !important;
        }
        .fixed-height-card {
            height: auto !important;
            min-height: 280px !important;
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

    # ==================================================================
    # FILTERS SECTION - REDESIGNED (Phase 4)
    # ==================================================================
    with safe_container(border=True):
        # PRIMARY FILTERS (Always Visible)
        c1, c2, c3 = st.columns([2, 1, 1.5])

        with c1:
            # Search keywords
            search_version = st.session_state.get("_widget_version_q", 0)
            F["q"] = st.text_input(
                "Search keywords",
                value=F.get("q", ""),
                placeholder="Search by title, client, or keywords...",
                key=f"facet_q_v{search_version}",
            )

        with c2:
            # Industry filter (NEW - single select dropdown)
            industry_version = st.session_state.get("_widget_version_industry", 0)
            industry_options = ["All"] + industries
            current_industry = F.get("industry", "")
            industry_index = industry_options.index(current_industry) if current_industry in industry_options else 0
            selected_industry = st.selectbox(
                "Industry",
                options=industry_options,
                index=industry_index,
                key=f"facet_industry_v{industry_version}",
            )
            F["industry"] = "" if selected_industry == "All" else selected_industry

        with c3:
            # Capability filter (NEW - single select dropdown)
            capability_version = st.session_state.get("_widget_version_capability", 0)
            capability_options = ["All"] + capabilities
            current_capability = F.get("capability", "")
            capability_index = capability_options.index(current_capability) if current_capability in capability_options else 0
            selected_capability = st.selectbox(
                "Capability",
                options=capability_options,
                index=capability_index,
                key=f"facet_capability_v{capability_version}",
            )
            F["capability"] = "" if selected_capability == "All" else selected_capability

        # ADVANCED FILTERS (Collapsed by default)
        show_advanced = st.session_state.get("show_advanced_filters", False)

        col_toggle, col_spacer, col_reset = st.columns([1, 3, 0.8])
        with col_toggle:
            toggle_label = "▾ Advanced Filters" if show_advanced else "▸ Advanced Filters"
            if st.button(toggle_label, key="btn_toggle_advanced"):
                st.session_state["show_advanced_filters"] = not show_advanced
                st.rerun()

        with col_reset:
            if st.button("Reset filters", key="btn_reset_filters"):
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
                    key=f"facet_clients_v{clients_version}"
                )

            with c2:
                # Role filter (multiselect)
                roles_version = st.session_state.get("_widget_version_roles", 0)
                F["roles"] = st.multiselect(
                    "Role",
                    roles,
                    default=F.get("roles", []),
                    key=f"facet_roles_v{roles_version}"
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
    # SEARCH & FILTERING LOGIC
    # =========================================================================

    view = []
    if F["q"].strip():
        ov = token_overlap_ratio(F["q"], _KNOWN_VOCAB)
        nonsense_check = is_nonsense(F["q"])
        overlap_check = (ov < 0.03 and f"overlap:{ov:.2f}")
        reason = nonsense_check or overlap_check
        
        if reason:
            st.session_state["__nonsense_reason__"] = reason
            st.session_state["__pc_suppressed__"] = True
            st.session_state["last_results"] = stories[:5]
            render_no_match_banner(reason=reason, query=F["q"], overlap=ov, suppressed=True, filters=F)
            st.stop()
        else:
            # FIX: Call with correct signature
            view = semantic_search(F["q"], filters=F, stories=stories)
            st.session_state["last_results"] = view
            st.session_state["__nonsense_reason__"] = None
            st.session_state["page_offset"] = 0
            st.session_state["__last_q__"] = F["q"]
    else:
        has_filters = any([
            F.get("industry"),  # NEW: Primary filter
            F.get("capability"),  # NEW: Primary filter
            F.get("personas"),
            F.get("clients"),
            F.get("domains"),
            F.get("roles"),
            F.get("tags"),
            F.get("has_metric"),
        ])
        if has_filters:
            view = [s for s in stories if matches_filters(s, F)]
        else:
            view = stories
        st.session_state["last_results"] = view

    st.session_state["__results_count__"] = len(view)

    if F.get("q", "").strip() and len(view) > 0:
        plural = "story" if len(view) == 1 else "stories"
        banner_html = f"""
        <style>
        .search-success-banner {{
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 12px 16px;
            border-radius: 6px;
            margin: 16px 0;
            font-size: 14px;
        }}
        </style>
        <div class="search-success-banner">
            ✓ Found {len(view)} matching {plural} for "{F['q']}"
        </div>
        """
        st.markdown(banner_html, unsafe_allow_html=True)

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
            unsafe_allow_html=True
        )

    with col3:
        # Remove the extra CSS - just let it be
        page_size_option = st.selectbox(
            "page_size",
            options=TABLE_PAGE_SIZE_OPTIONS,
            index=0,
            key="page_size_select",
            label_visibility="collapsed"
        )

    with col4:
        # Remove the padding-top wrapper
        view_mode = st.segmented_control(
            "View",
            options=["Table", "Cards"],
            key="explore_view_mode",
            label_visibility="collapsed"
        )

    page_size = page_size_option if view_mode == "Table" else CARDS_PAGE_SIZE
    offset = int(st.session_state.get("page_offset", 0))

    if DEBUG:
        print(f"DEBUG Explore: view_mode={view_mode}, page_size={page_size}")

    # =========================================================================
    # TABLE VIEW
    # =========================================================================

    if view_mode == "Table":
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
        show_cols = [c for c in ["Title", "Client", "Role", "Domain"] if c in df.columns]
        show_df = df[show_cols] if show_cols else df

        if not _HAS_AGGRID:
            st.warning("Row-click requires st-aggrid. Install: `pip install streamlit-aggrid`")
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
                """
            )
            gob.configure_column("Role", flex=3)
            gob.configure_column(
                "Domain",
                flex=4,
                cellRenderer="""
                    function(params) {
                        return '<span class="domain-tag">' + params.value + '</span>';
                    }
                """
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
        render_detail_panel(detail, "table", stories)

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
                        domain = (s.get("Sub-category") or "").split(" / ")[-1] if s.get("Sub-category") else "Unknown"
                        summary = s.get("5PSummary", "")

                        card_html = f"""
                        <div class="fixed-height-card" style="margin-bottom: 20px;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                                <h3 style="font-size: 18px; font-weight: 600; margin: 0; line-height: 1.4; color: #1a202c; flex: 1;">{title}</h3>
                                <span style="background: #e6f2ff; color: #2563eb; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 500; white-space: nowrap; margin-left: 12px;">{client}</span>
                            </div>
                            <p class="card-desc" style="margin-bottom: 16px;">{summary}</p>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: auto; padding-top: 12px; border-top: 1px solid #e5e7eb;">
                                <span style="font-size: 12px; color: #64748b; font-weight: 500;">{role}</span>
                                <span style="background: #f3f4f6; color: #374151; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 500;">{domain}</span>
                            </div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)

                        story_id = str(s.get("id", i))

                        # Vary button text based on story attributes for better UX
                        button_texts = [
                            "View Details →",
                            "See Project →",
                            "Learn More →",
                            "Explore Story →",
                            "Read More →"
                        ]
                        button_text = button_texts[i % len(button_texts)]

                        if st.button(button_text, key=f"card_{story_id}", use_container_width=False):
                            st.session_state["active_story"] = story_id
                            st.rerun()

            render_pagination(total_results, page_size, offset, "cards")
            detail = get_context_story(stories)
            render_detail_panel(detail, "cards", stories)

            # JAVASCRIPT: Force purple button styles for card buttons (same workaround as home page)
            import streamlit.components.v1 as components
            components.html("""
            <script>
            (function() {
                function applyPurpleCardButtons() {
                    const parentDoc = window.parent.document;
                    const cardButtons = parentDoc.querySelectorAll('[class*="st-key-card_"] button[data-testid="stBaseButton-secondary"]');

                    cardButtons.forEach(function(button) {
                        if (!button.dataset.purpled) {
                            button.dataset.purpled = 'true';
                            button.style.cssText = 'background: white !important; background-color: white !important; background-image: none !important; border: 2px solid #e5e5e5 !important; color: #8B5CF6 !important; padding: 10px 18px !important; font-size: 14px !important; font-weight: 600 !important; border-radius: 8px !important; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;';

                            button.addEventListener('mouseenter', function() {
                                this.style.cssText = 'background: #8B5CF6 !important; background-color: #8B5CF6 !important; background-image: none !important; border: 2px solid #8B5CF6 !important; color: white !important; padding: 10px 18px !important; font-size: 14px !important; font-weight: 600 !important; border-radius: 8px !important; transform: translateY(-2px) !important; box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3), 0 2px 4px rgba(0, 0, 0, 0.1) !important;';
                            });
                            button.addEventListener('mouseleave', function() {
                                this.style.cssText = 'background: white !important; background-color: white !important; background-image: none !important; border: 2px solid #e5e5e5 !important; color: #8B5CF6 !important; padding: 10px 18px !important; font-size: 14px !important; font-weight: 600 !important; border-radius: 8px !important; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;';
                            });
                        }
                    });
                }

                // Run immediately and repeatedly to catch all buttons
                applyPurpleCardButtons();
                setTimeout(applyPurpleCardButtons, 100);
                setTimeout(applyPurpleCardButtons, 500);
                setTimeout(applyPurpleCardButtons, 1000);

                // Keep checking periodically for dynamically added buttons
                setInterval(applyPurpleCardButtons, 2000);
            })();
            </script>
            """, height=0)
    
    # === ADD FOOTER ===
    from ui.components.footer import render_footer
    render_footer()
    # # =========================================================================
    # # LET'S CONNECT FOOTER - WIREFRAME EXACT
    # # =========================================================================
    # st.markdown("""
    # <div style="background: #2c3e50; color: white; padding: 48px 40px; text-align: center; margin-top: 40px; border-radius: 8px;">
    #     <h3 style="font-size: 28px; margin-bottom: 12px; color: white;">Let's Connect</h3>
    #     <p style="font-size: 16px; margin-bottom: 8px; opacity: 0.9;">
    #         Exploring Director/VP opportunities in <strong>Product Leadership</strong>, <strong>Platform Engineering</strong>, and <strong>Organizational Transformation</strong>
    #     </p>
    #     <p style="font-size: 14px; margin-bottom: 32px; opacity: 0.75;">
    #         Available for immediate start • Remote or Atlanta-based • Open to consulting engagements
    #     </p>
    #     <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;">
    #         <a href="mailto:mcpugmire@gmail.com" style="padding: 12px 28px; background: #8B5CF6; color: white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
    #             📧 mcpugmire@gmail.com
    #         </a>
    #         <a href="https://www.linkedin.com/in/matt-pugmire/" target="_blank" style="padding: 12px 28px; background: rgba(255,255,255,0.1); color: white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
    #             💼 LinkedIn
    #         </a>
    #         <a href="#ask" style="padding: 12px 28px; background: rgba(255,255,255,0.1); color: white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
    #             🐾 Ask Agy
    #         </a>
    #     </div>
    # </div>
    # """, unsafe_allow_html=True)