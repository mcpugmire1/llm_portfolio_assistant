"""
Explore Stories Page - Refactored & Bug-Free

Browse 115 project case studies with advanced filtering.
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
    client = s.get("client", "")
    title = s.get("title", "")
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
    if isinstance(obj, dict) and (obj.get("id") or obj.get("title")):
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
            stitle = (s.get("title") or "").strip().lower()
            sclient = (s.get("client") or "").strip().lower()
            if stitle == at and (not ac or sclient == ac):
                return s

    if at:
        for s in stories:
            stitle = (s.get("title") or "").strip().lower()
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
        xt = (cand.get("title") or "").strip().lower()
        xc = (cand.get("client") or "").strip().lower()
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
    
    for label, key in [
        ("Audience", "personas"),
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
    """Render the story detail panel (shared by table and card views)"""
    hr_style = "margin: 16px 0 12px 0; border: none; border-top: 1px solid var(--border-color);"
    st.markdown(f"<hr style='{hr_style}'>", unsafe_allow_html=True)

    if not detail:
        st.info("Click a row/card above to view details.")
        return

    with safe_container(border=True):
        title = detail.get("title", "Untitled")
        title_style = "margin-bottom: 4px; color: var(--text-color);"
        st.markdown(f"<h3 style='{title_style}'>{title}</h3>", unsafe_allow_html=True)

        client = detail.get("client", "Unknown")
        role = detail.get("role", "Unknown")
        domain = detail.get("domain", "Unknown")
        meta_style = "color: var(--text-color); opacity: 0.7; font-size: 14px; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid var(--border-color);"
        meta_html = (
            f"<div style='{meta_style}'>"
            f"<strong>Client:</strong> {client} &nbsp;&nbsp; "
            f"<strong>Role:</strong> {role} &nbsp;&nbsp; "
            f"<strong>Domain:</strong> {domain}"
            f"</div>"
        )
        st.markdown(meta_html, unsafe_allow_html=True)

        summary = detail.get("5PSummary", "") or build_5p_summary(detail, 999)
        if summary:
            summary_style = "color: var(--text-color); line-height: 1.6; margin-bottom: 20px;"
            st.markdown(f"<p style='{summary_style}'>{summary}</p>", unsafe_allow_html=True)

        outcomes = detail.get("what", []) or detail.get("Result", [])
        if outcomes and isinstance(outcomes, list) and len(outcomes) > 0:
            st.markdown(
                "<div style='margin-bottom: 16px;'><strong style='color: var(--text-color);'>Key Achievements:</strong></div>",
                unsafe_allow_html=True,
            )
            for outcome in outcomes[:MAX_ACHIEVEMENTS_SHOWN]:
                if outcome:
                    item_style = "margin-left: 20px; margin-bottom: 8px; color: var(--text-color);"
                    st.markdown(f"<div style='{item_style}'>• {outcome}</div>", unsafe_allow_html=True)

        btn_key = f"ask_from_detail_{key_suffix}_{detail.get('id', 'x')}"
        if st.button("Ask MattGPT about this", key=btn_key, type="primary", use_container_width=False):
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
        div[data-testid="column"] .stButton > button {
            border-radius: 8px !important;
            border: 1.5px solid #e0e0e0 !important;
            background: transparent !important;
            color: var(--text-color) !important;
            padding: 8px 16px !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            min-height: 40px !important;
            min-width: 60px !important;
            margin: 0 4px !important;
            transition: all 0.2s ease !important;
        }
        /* NUCLEAR: Force ALL multiselect pills to be blue ALWAYS */
        [data-testid="stMultiSelect"] [data-baseweb="tag"],
        [data-baseweb="tag"],
        .stMultiSelect [data-baseweb="tag"],
        div[data-baseweb="tag"],
        span[data-baseweb="tag"] {
            background-color: #4a90e2 !important;
            background: #4a90e2 !important;
            border-color: #4a90e2 !important;
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
            background-color: #3a7bc8 !important;
            background: #3a7bc8 !important;
        }

        /* Override Streamlit's default red/orange pills */
        .stMultiSelect span[data-baseweb="tag"][style*="background"],
        [data-baseweb="tag"][style*="background"] {
            background-color: #4a90e2 !important;
            background: #4a90e2 !important;
        }
v
        div[data-testid="column"] .stButton > button:hover {
            border-color: #ff4b4b !important;
            background: rgba(255, 75, 75, 0.08) !important;
        }
        .pagination-active {
            border-radius: 8px;
            border: 1.5px solid #ff4b4b;
            background: rgba(255, 75, 75, 0.1);
            color: #ff4b4b;
            padding: 6px 14px;
            font-size: 13px;
            font-weight: 600;
            text-align: center;
            min-height: 36px;
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
    st.title("Project Case Studies")
    intro_text = "<p>See how digital transformation happens in practice. Browse case studies, then click Ask MattGPT for the inside story.</p>"
    st.markdown(intro_text, unsafe_allow_html=True)

    explore_css = """
    <style>
    .explore-filters {
        background: #2a2a2a;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 12px;
        border: 1px solid #333;
    }
    .stMultiSelect, .stSelectbox, .stTextInput {
        margin-bottom: 0px !important;
        margin-top: 0px !important;
    }
    label[data-testid="stWidgetLabel"] {
        margin-bottom: 4px !important;
    }
    [data-testid="stVerticalBlock"] > div {
        gap: 8px !important;
    }
    .stButton {
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
        background: var(--secondary-background-color) !important;
        padding: 28px !important;
        border-radius: 12px !important;
        border: 1px solid var(--border-color) !important;
        height: 380px !important;
        display: flex !important;
        flex-direction: column !important;
        box-shadow: 0 4px 12px rgba(0,0,0,.25) !important;
        transition: all 0.3s ease !important;
    }
    .fixed-height-card:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 25px rgba(74,144,226,.15) !important;
    }
    .card-desc {
        color: #b0b0b0 !important;
        line-height: 1.5 !important;
        font-size: 14px !important;
        overflow: hidden !important;
        display: -webkit-box !important;
        -webkit-line-clamp: 5 !important;
        -webkit-box-orient: vertical !important;
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

    # ==================================================================
    # FILTERS SECTION
    # ==================================================================
    with safe_container(border=True):
        c1, c2, c3 = st.columns([1, 0.8, 1.5])
        
        with c1:
            # VERSION: Search keywords
            search_version = st.session_state.get("_widget_version_q", 0)
            F["q"] = st.text_input(
                "Search keywords",
                value=F["q"],
                placeholder="Search by title, client, or keywords...",
                key=f"facet_q_v{search_version}",
            )
        
        with c2:
            # VERSION: Audience (personas)
            personas_version = st.session_state.get("_widget_version_personas", 0)
            F["personas"] = st.multiselect(
                "Audience",
                personas_all,
                default=F["personas"],
                key=f"facet_personas_v{personas_version}",
            )
        
        with c3:
            groups, domain_parts = build_domain_options(domains)
            # VERSION: Domain category (selectbox)
            domain_cat_version = st.session_state.get("_widget_version_domain_cat", 0)
            selected_group = st.selectbox(
                "Domain category", 
                ["All"] + groups, 
                key=f"facet_domain_group_v{domain_cat_version}"
            )
        
        c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1])
        
        with c1:
            def _fmt_sub(full_value: str) -> str:
                return full_value.split(" / ")[-1] if " / " in full_value else full_value
            
            # VERSION: Domains
            domains_version = st.session_state.get("_widget_version_domains", 0)
            
            if selected_group == "All":
                F["domains"] = st.multiselect(
                    "Domain",
                    options=domains,
                    default=F["domains"],
                    key=f"facet_domains_all_v{domains_version}",
                    format_func=_fmt_sub,
                )
            else:
                subdomain_options = [full for cat, sub, full in domain_parts if cat == selected_group]
                last_group = st.session_state.get("_last_domain_group", "All")
                
                if selected_group != last_group:
                    F["domains"] = subdomain_options
                    st.session_state["_last_domain_group"] = selected_group
                else:
                    prev = [d for d in F.get("domains", []) if d in subdomain_options]
                    F["domains"] = prev
                
                F["domains"] = st.multiselect(
                    "Domain",
                    options=sorted(subdomain_options),
                    default=F["domains"],
                    key=f"facet_subdomains_v{domains_version}",
                    format_func=_fmt_sub,
                )
        
        with c2:
            # VERSION: Client
            clients_version = st.session_state.get("_widget_version_clients", 0)
            F["clients"] = st.multiselect(
                "Client", 
                clients, 
                default=F["clients"], 
                key=f"facet_clients_v{clients_version}"
            )
        
        with c3:
            # VERSION: Role
            roles_version = st.session_state.get("_widget_version_roles", 0)
            F["roles"] = st.multiselect(
                "Role", 
                roles, 
                default=F["roles"], 
                key=f"facet_roles_v{roles_version}"
            )
        
        with c4:
            # VERSION: Tags
            tags_version = st.session_state.get("_widget_version_tags", 0)
            F["tags"] = st.multiselect(
                "Tags", 
                tags, 
                default=F["tags"], 
                key=f"facet_tags_v{tags_version}"
            )
        
        cols = st.columns([1, 4])
        with cols[0]:
            if st.button("Reset filters", key="btn_reset_filters"):
                reset_all_filters(stories)
                st.rerun()

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
            dom = (s.get("domain") or "").split(" / ")[-1]
            return {
                "ID": s.get("id", ""),
                "Title": s.get("title", ""),
                "Client": s.get("client", ""),
                "Role": s.get("role", ""),
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
            gob.configure_column("Client", flex=4)
            gob.configure_column("Role", flex=3)
            gob.configure_column("Domain", flex=4)

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
                        title = s.get("title", "Untitled")
                        client = s.get("client", "Unknown")
                        role = s.get("role", "Unknown")
                        domain = (s.get("domain") or "").split(" / ")[-1] if s.get("domain") else "Unknown"
                        summary = s.get("5PSummary", "")

                        card_html = f"""
                        <div class="fixed-height-card" style="margin-bottom: 20px;">
                            <h3 style="font-size: 22px; font-weight: 700; margin-bottom: 16px; line-height: 1.3; color: var(--text-color);">{title}</h3>
                            <div style="color: #5b9dd9; font-size: 15px; font-weight: 600; margin-bottom: 10px;">{client}</div>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                                <span style="font-size: 10px; color: #718096; text-transform: uppercase; font-weight: 700; letter-spacing: 0.8px;">{role}</span>
                                <span style="background: rgba(91, 157, 217, 0.12); color: #5b9dd9; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600;">{domain}</span>
                            </div>
                            <p class="card-desc">{summary}</p>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)

                        story_id = str(s.get("id", i))
                        if st.button("View Details", key=f"card_{story_id}", use_container_width=True):
                            st.session_state["active_story"] = story_id
                            st.rerun()

            render_pagination(total_results, page_size, offset, "cards")
            detail = get_context_story(stories)
            render_detail_panel(detail, "cards", stories)