"""
Explore Stories Page

Browse 115 project case studies with advanced filtering.
Includes semantic search, faceted filters, and pagination.
"""

import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import json
import re
from datetime import datetime
from typing import List, Optional
import os, re, time, textwrap, json
import pandas as pd
from config.debug import DEBUG
from config.settings import get_conf
from utils.ui_helpers import dbg, safe_container
from utils.validation import is_nonsense, token_overlap_ratio, _tokenize
from utils.ui_helpers import render_no_match_banner
from utils.formatting import story_has_metric, strongest_metric_line, build_5p_summary, _format_key_points, METRIC_RX
from utils.filters import matches_filters
from services.pinecone_service import (
    _init_pinecone,
    _safe_json, 
    _summarize_index_stats,
    PINECONE_MIN_SIM,      # ← Only once
    PINECONE_NAMESPACE,
    PINECONE_INDEX_NAME,
    SEARCH_TOP_K,
    W_PC,
    W_KW,
    _DEF_DIM,
    _PINECONE_INDEX,
    VECTOR_BACKEND,
)
from services.rag_service import semantic_search, _KNOWN_VOCAB

# --- Shared config: prefer st.secrets, fallback to .env ---
import os
from dotenv import load_dotenv
import streamlit as st

# --- Nonsense rules (JSONL) + known vocab -------------------
import csv
from datetime import datetime


load_dotenv()


DATA_FILE = os.getenv("STORIES_JSONL", "echo_star_stories_nlp.jsonl")  # optional

# Streamlit compatibility helper for bordered containers (older Streamlit lacks border kw)
def safe_container(*, border: bool = False):
    try:
        return st.container(border=border)
    except TypeError:
        return st.container()

# optional: row-click table
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

    _HAS_AGGRID = True
except Exception:
    _HAS_AGGRID = False


def on_ask_this_story(s: dict):
    """Set context to a specific story and open the Ask MattGPT tab preloaded with a seed prompt."""
    st.session_state["active_story"] = s.get("id")
    st.session_state["seed_prompt"] = (
        f"How were these outcomes achieved for {s.get('client','')} — {s.get('title','')}? "
        "Focus on tradeoffs, risks, and replicable patterns."
    )
    # Navigate to Ask tab
    st.session_state["active_tab"] = "Ask MattGPT"
    st.session_state["ask_input"] = st.session_state.get("seed_prompt", "")

    # ➜ ADD THIS (one-shot lock)
    st.session_state["__ctx_locked__"] = True
    st.session_state["__ask_from_suggestion__"] = True

    st.rerun()  # Rerun to scroll to top of Ask MattGPT page

def get_context_story(STORIES):
    # Highest priority: an explicitly stored story object
    obj = st.session_state.get("active_story_obj")
    if isinstance(obj, dict) and (obj.get("id") or obj.get("title")):
        return obj

    sid = st.session_state.get("active_story")
    if sid:
        for s in STORIES:
            if str(s.get("id")) == str(sid):
                return s

    # Fallback: match by title/client when id mapping isn’t stable
    at = (st.session_state.get("active_story_title") or "").strip().lower()
    ac = (st.session_state.get("active_story_client") or "").strip().lower()
    if at:
        for s in STORIES:
            stitle = (s.get("title") or "").strip().lower()
            sclient = (s.get("client") or "").strip().lower()
            if stitle == at and (not ac or sclient == ac):
                return s
        # Last resort: substring/startswith
        for s in STORIES:
            stitle = (s.get("title") or "").strip().lower()
            if at in stitle or stitle in at:
                return s
    # Fallback: attempt to resolve from last_results payloads
    lr = st.session_state.get("last_results") or []
    sid = st.session_state.get("active_story")
    at = (st.session_state.get("active_story_title") or "").strip().lower()
    ac = (st.session_state.get("active_story_client") or "").strip().lower()
    for x in lr:
        if not isinstance(x, dict):
            continue
        cand = x.get("story") if isinstance(x.get("story"), dict) else x
        if not isinstance(cand, dict):
            continue
        xid = str(cand.get("id") or cand.get("story_id") or "").strip()
        xt = (cand.get("title") or "").strip().lower()
        xc = (cand.get("client") or "").strip().lower()
        if (sid and xid and str(xid) == str(sid)) or (
            at and xt == at and (not ac or xc == ac)
        ):
            return cand
    return None

def render_explore_stories(stories, clients, domains, roles, tags, personas_all):
    """
    Render the Explore Stories page with filters and project listings.
    
    Args:
        stories: List of story dictionaries (STORIES from app.py)
        clients: List of unique client names
        domains: List of unique domain names  
        roles: List of unique roles
        tags: List of unique tags
        personas_all: List of all personas
    """
    st.title("Project Case Studies")
    st.markdown('<p>See how digital transformation happens in practice. Browse case studies, then click Ask MattGPT for the inside story.</p>', unsafe_allow_html=True)

    # --- Explore Stories CSS ---
    st.markdown("""
    <style>
        /* Filter Section - Much More Compact */
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

        [data-testid="stVerticalBlock"] {
            gap: 8px !important;
        }

        .stButton {
            margin-top: 0px !important;
            margin-bottom: 0px !important;
        }

         /* RESULTS ROW - Target 3rd column ONLY in 5-column layout */
        div[data-testid="stHorizontalBlock"]:has(> div:nth-child(5)) > div:nth-child(3) {
            flex: 0 0 75px !important;
            max-width: 75px !important;
            min-width: 75px !important;
        }

        div[data-testid="stHorizontalBlock"]:has(> div:nth-child(5)) > div:nth-child(3) div[data-testid="stSelectbox"],
        div[data-testid="stHorizontalBlock"]:has(> div:nth-child(5)) > div:nth-child(3) div[data-baseweb="select"],
        div[data-testid="stHorizontalBlock"]:has(> div:nth-child(5)) > div:nth-child(3) div[data-baseweb="select"] > div {
            width: 75px !important;
            min-width: 75px !important;
            max-width: 75px !important;
        }

        /* Results Summary */
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            padding: 0 4px;
        }

        .results-count {
            color: var(--text-color);
            font-size: 14px;
            font-weight: 600;
        }

        /* Card Grid */
        .story-cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }

        .story-card {
            background: var(--secondary-background-color);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
        }

        .story-card:hover {
            border-color: #4a90e2;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }

        .card-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-color);
            line-height: 1.4;
            margin-bottom: 8px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .card-client {
            color: #4a90e2;
            font-weight: 500;
            font-size: 14px;
            margin-bottom: 12px;
        }

        .card-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 12px;
        }

        .card-role {
            background: var(--background-color);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            color: var(--text-color);
            text-transform: uppercase;
            font-weight: 500;
        }

        .card-domain {
            color: #999999;
            font-size: 12px;
            text-align: right;
            max-width: 150px;
            line-height: 1.3;
        }

        .card-summary {
            color: #c0c0c0;
            font-size: 13px;
            line-height: 1.5;
            margin-top: 8px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .fixed-height-card {
            background: var(--secondary-background-color) !important;
            padding: 20px 24px !important;
            border-radius: 12px !important;
            border: 1px solid var(--border-color) !important;
            transition: all 0.3s ease !important;
            height: 320px !important;
            display: flex !important;
            flex-direction: column !important;
            box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2) !important;
        }

        .fixed-height-card:hover {
            transform: translateY(-4px) !important;
            border-color: var(--border-color) !important;
            box-shadow: 0 8px 25px rgba(74,144,226,.15) !important;
        }

        .card-desc {
            color: #b0b0b0 !important;
            margin-bottom: 0 !important;
            line-height: 1.5 !important;
            font-size: 14px !important;
            overflow: hidden !important;
            display: -webkit-box !important;
            -webkit-line-clamp: 5 !important;
            -webkit-box-orient: vertical !important;
        }

        /* Mobile Responsive Design */
        @media (max-width: 768px) {
            div[data-testid="column"]:has(div[data-baseweb="segmented-control"]) {
                display: none !important;
            }

            div[data-testid="column"]:has(div[data-testid="stSelectbox"]) {
                display: none !important;
            }

            div[data-testid="column"] > div > div {
                font-size: 13px !important;
            }

            div[data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
                gap: 12px !important;
            }

            div[data-testid="column"] {
                width: 100% !important;
                min-width: 100% !important;
            }

            .stButton > button {
                min-height: 44px !important;
                font-size: 16px !important;
                padding: 12px 20px !important;
            }

            div[data-testid="column"] .stButton > button {
                min-height: 44px !important;
                padding: 10px 18px !important;
                font-size: 15px !important;
            }

            .story-cards-grid {
                grid-template-columns: 1fr !important;
                gap: 16px !important;
            }

            .fixed-height-card {
                height: auto !important;
                min-height: 280px !important;
            }

            .ag-theme-streamlit {
                display: none !important;
            }

            section[data-testid="stSidebar"] {
                transform: translateX(-100%) !important;
            }

            button[kind="header"] {
                display: block !important;
            }
            /* RESULTS ROW - Page size dropdown width constraint */
            div[data-testid="stHorizontalBlock"] > div:nth-child(3) {
                flex: 0 0 75px !important;
                max-width: 75px !important;
                min-width: 75px !important;
            }

            div[data-testid="stHorizontalBlock"] > div:nth-child(3) div[data-testid="stSelectbox"],
            div[data-testid="stHorizontalBlock"] > div:nth-child(3) div[data-baseweb="select"],
            div[data-testid="stHorizontalBlock"] > div:nth-child(3) div[data-baseweb="select"] > div {
                width: 75px !important;
                min-width: 75px !important;
                max-width: 75px !important;
            }

            /* BUT: Remove constraint from Domain Category and Tags */
            div[data-testid="stSelectbox"]:has(select[id*="facet_domain_group"]) {
                width: auto !important;
                max-width: none !important;
                min-width: auto !important;
                flex: 1 !important;
            }

            div[data-testid="stSelectbox"]:has(select[id*="facet_domain_group"]) div[data-baseweb="select"] {
                width: 100% !important;
                max-width: none !important;
            }

        }
    </style>
    """, unsafe_allow_html=True)

    # --- normalize legacy tab names ---
    legacy = {"Stories": "Explore Stories"}
    cur = st.session_state.get("active_tab", "Home")
    if cur in legacy:
        st.session_state["active_tab"] = legacy[cur]
    st.markdown("<a id='stories_top'></a>", unsafe_allow_html=True)
    F = st.session_state["filters"]

    with safe_container(border=True):
        # Row 1: Search and Audience
         # Row 1: 3 columns with Domain category getting 60% of the space
        c1, c2, c3 = st.columns([1, 0.8, 1.5])
        
        with c1:
            F["q"] = st.text_input(
                "Search keywords",
                value=F["q"],
                placeholder="Search by title, client, or keywords...",
                key="facet_q",
            )
        
        with c2:
            F["personas"] = st.multiselect(
                "Audience",
                personas_all,
                default=F["personas"],
                key="facet_personas",
            )
        
        with c3:
            domain_parts = [
                (d.split(" / ")[0], (d.split(" / ")[1] if " / " in d else ""), d)
                for d in domains
            ]
            groups = sorted({cat for cat, sub, full in domain_parts if full})

            selected_group = st.selectbox(
                "Domain category", 
                ["All"] + groups, 
                key="facet_domain_group"
            )

        # Row 2: Flatten to a single row with 4 columns to avoid nested column styling issue
        c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1])

        with c1:
            # Domain multiselect based on category
            def _fmt_sub(full_value: str) -> str:
                return (
                    full_value.split(" / ")[-1] if " / " in full_value else full_value
                )

            if selected_group == "All":
                F["domains"] = st.multiselect(
                    "Domain",
                    options=domains,
                    default=F["domains"],
                    key="facet_domains_all",
                    format_func=_fmt_sub,
                )
            else:
                subdomain_options = [
                    full for cat, sub, full in domain_parts if cat == selected_group
                ]
                prev = [d for d in F.get("domains", []) if d in subdomain_options]
                F["domains"] = st.multiselect(
                    "Domain",
                    options=sorted(subdomain_options),
                    default=prev,
                    key="facet_subdomains",
                    format_func=_fmt_sub,
                )

        with c2:
            F["clients"] = st.multiselect(
                "Client", clients, default=F["clients"], key="facet_clients"
            )

        with c3:
            F["roles"] = st.multiselect(
                "Role", roles, default=F["roles"], key="facet_roles"
            )

        with c4:
            F["tags"] = st.multiselect(
                "Tags", tags, default=F["tags"], key="facet_tags"
            )
            
        # Reset button
        cols = st.columns([1, 4])
        with cols[0]:
            def reset_filters():
                st.session_state["filters"] = {
                    "personas": [],
                    "clients": [],
                    "domains": [],
                    "roles": [],
                    "tags": [],
                    "q": "",
                    "has_metric": False,
                }
                # Delete ALL widget state keys so they don't override the reset values
                widget_keys = [
                    "facet_q",
                    "facet_personas",
                    "facet_clients",
                    "facet_domain_group",
                    "facet_domains_all",
                    "facet_subdomains",
                    "facet_roles",
                    "facet_tags",
                    "facet_has_metric"
                ]
                for key in widget_keys:
                    if key in st.session_state:
                        del st.session_state[key]

                # Reset paging
                st.session_state["page_offset"] = 0
                # Clear last results so all stories show
                st.session_state["last_results"] = stories

            st.button("Reset filters", key="btn_reset_filters", on_click=reset_filters)

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Always run semantic search (no debounce, no skip) ---
    view = []
    if F["q"].strip():
        ov = token_overlap_ratio(F["q"], _KNOWN_VOCAB)
        reason = is_nonsense(F["q"]) or (ov < 0.03 and f"overlap:{ov:.2f}")
        if reason:
            st.session_state["__nonsense_reason__"] = reason
            st.session_state["__pc_suppressed__"] = True
            st.session_state["last_results"] = stories[:5]

            # NEW: unified banner (replaces show_out_of_scope)
            render_no_match_banner(
                reason=reason,
                query=F["q"],
                overlap=ov,
                suppressed=True,
                filters=F,
            )
            st.stop()
        else:
            view = semantic_search(F["q"], stories, F)
            st.session_state["last_results"] = view
            st.session_state["__nonsense_reason__"] = None
            st.session_state["page_offset"] = 0
            st.session_state["__last_q__"] = F["q"]
            if not view:
                st.info("No stories match your filters yet.")
                if st.button("Clear filters", key="clear_filters_empty_top"):
                    st.session_state["filters"] = {
                        "personas": [],
                        "clients": [],
                        "domains": [],
                        "roles": [],
                        "tags": [],
                        "q": "",
                        "has_metric": False,
                    }
                    st.session_state["facet_domain_group"] = "All"
                    st.session_state["page_offset"] = 0
                    st.rerun()
                st.stop()
    else:
        # No search query: apply UI filters to all stories
        # Check if any filters are active
        has_filters = any([
            F.get("personas"),
            F.get("clients"),
            F.get("domains"),
            F.get("roles"),
            F.get("tags"),
            F.get("has_metric")
        ])

        if has_filters:
            # Apply filters to all stories
            view = [s for s in stories if matches_filters(s, F)]
        else:
            # No filters at all: show all stories
            view = stories

        st.session_state["last_results"] = view

    st.session_state["__results_count__"] = len(view)

    # Show sticky success banner right after filter container
    # Using custom CSS to make it sticky at top on mobile
    if F.get("q", "").strip() and len(view) > 0:
        st.markdown(f"""
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
        @media (max-width: 768px) {{
            .search-success-banner {{
                position: sticky;
                top: 0;
                z-index: 100;
                margin: 0 0 16px 0;
                border-radius: 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
        }}
        </style>
        <div class="search-success-banner">
            ✓ Found {len(view)} matching {'story' if len(view) == 1 else 'stories'} for "{F['q']}"
        </div>
        """, unsafe_allow_html=True)

    chips = []
    if F.get("q"):
        chips.append(("Search", f'"{F["q"]}"', ("q", None)))
    if F.get("has_metric"):
        chips.append(("Flag", "Has metric", ("has_metric", None)))
    for label, key in [
        ("Audience", "personas"),
        ("Client", "clients"),
        ("Domain", "domains"),
        ("Role", "roles"),
        ("Tag", "tags"),
    ]:
        for v in F.get(key, []):
            chips.append((label, v, (key, v)))

    st.markdown('<div class="active-chip-row">', unsafe_allow_html=True)

    to_remove = []
    clear_all = False

    for i, (_, text, (k, v)) in enumerate(chips):
        if st.button(f"✕ {text}", key=f"chip_{k}_{i}"):
            to_remove.append((k, v))

    if chips and st.button("Clear all", key="chip_clear_all"):
        clear_all = True

    st.markdown("</div>", unsafe_allow_html=True)

    changed = False
    if clear_all:
        F.update(
            {
                "personas": [],
                "clients": [],
                "domains": [],
                "roles": [],
                "tags": [],
                "q": "",
                "has_metric": False,
            }
        )
        st.session_state["page_offset"] = 0
        st.session_state["last_results"] = stories
        changed = True
    elif to_remove:
        for k, v in to_remove:
            if k == "q":
                if F.get("q"):
                    F["q"] = ""
                    changed = True
            elif k == "has_metric":
                if F.get("has_metric"):
                    F["has_metric"] = False
                    changed = True
            else:
                before = list(F.get(k, []))
                after = [x for x in before if x != v]
                if len(after) != len(before):
                    F[k] = after
                    changed = True

    if changed:
        st.session_state["page_offset"] = 0

        # If clearing all filters, delete widget state keys so they don't repopulate
        if clear_all:
            widget_keys_to_clear = [
                "facet_q",
                "facet_personas",
                "facet_clients",
                "facet_domain_group",
                "facet_domains_all",
                "facet_subdomains",
                "facet_roles",
                "facet_tags",
                "facet_has_metric"
            ]
            for key in widget_keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]

        st.rerun()

    # --- Results header with view toggle (matching wireframe) ---
    total_results = len(view)

    # Get current view mode from session state or default to Table
    if "explore_view_mode" not in st.session_state:
        st.session_state["explore_view_mode"] = "Table"

    # Initialize page offset if not set
    if "page_offset" not in st.session_state:
        st.session_state["page_offset"] = 0

    # Track previous view mode to detect changes
    prev_view_mode = st.session_state.get("_prev_explore_view_mode", "Table")

    # Calculate pagination values first
    page_size_option = st.session_state.get("page_size_select", 10)
    view_mode = st.session_state.get("explore_view_mode", "Table")

    # Reset page offset if view mode changed
    if view_mode != prev_view_mode:
        st.session_state["page_offset"] = 0
        st.session_state["_prev_explore_view_mode"] = view_mode
    layout_mode = "List (master‑detail)" if view_mode == "Table" else "Cards"
    page_size = page_size_option if view_mode == "Table" else 9
    offset = int(st.session_state.get("page_offset", 0))
    start = offset + 1
    end = min(offset + page_size, total_results)

    # Results summary row - all on one line matching wireframe
    col1, col2, col3, spacer, col4 = st.columns([2.2, 0.18, 0.5, 0.12, 1.2])

    with col1:
        st.markdown(f"""
        <div style="display: flex; align-items: flex-end; min-height: 40px; color: var(--text-color); font-size: 14px;">
            Showing &nbsp;<strong>{start}–{end}</strong>&nbsp; of &nbsp;<strong>{total_results}</strong>&nbsp; projects
        </div>
        """, unsafe_allow_html=True)
    with col2:
         st.markdown('<div style="display: flex; align-items: flex-end; min-height: 40px; font-size: 14px; font-weight: 500; white-space: nowrap;">SHOW:</div>', unsafe_allow_html=True)

    with col3:
        page_size_option = st.selectbox(
            "page_size",
            options=[10, 20, 55],
            index=0,
            key="page_size_select",
            label_visibility="collapsed",
        )

    with col4:
        st.markdown('<div style="padding-top: 6px;flex-end">', unsafe_allow_html=True)
        view_mode = st.segmented_control(
            "View",
            options=["Table", "Cards"],
            key="explore_view_mode",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)


    # Recalculate with actual values
    layout_mode = "List (master‑detail)" if view_mode == "Table" else "Cards"
    page_size = page_size_option if view_mode == "Table" else 9
    offset = int(st.session_state.get("page_offset", 0))
    start = offset + 1
    end = min(offset + page_size, total_results)

    if DEBUG:
        print(f"DEBUG Explore: view_mode={view_mode}, layout_mode={layout_mode}")

    # ---- Build grid model (keep ID internally, hide in UI) ----
    def _row(s: dict) -> dict:
        dom = (s.get("domain") or "").split(" / ")[-1]
        return {
            "ID": s.get("id", ""),  # used for selection; hidden in UI
            "Title": s.get("title", ""),
            "Client": s.get("client", ""),
            "Role": s.get("role", ""),
            "Domain": dom,
        }

    # Paginate the view for table
    view_paginated = view[offset:offset + page_size]
    rows = [_row(s) for s in view_paginated]
    df = pd.DataFrame(rows)
    show_cols = [c for c in ["Title", "Client", "Role", "Domain"] if c in df.columns]
    show_df = df[show_cols] if show_cols else df

    if layout_mode.startswith("List"):
        # -------- Table view with AgGrid (clickable rows) --------
        if not _HAS_AGGRID:
            st.warning("Row-click selection requires **st-aggrid**. Install with: `pip install streamlit-aggrid`")
            st.dataframe(show_df, hide_index=True, use_container_width=True)
        else:
            df_view = df[["ID"] + show_cols] if show_cols else df

            gob = GridOptionsBuilder.from_dataframe(df_view)
            gob.configure_default_column(resizable=True, sortable=True, filter=True)

            # Configure column widths to match wireframe exactly (45%, 20%, 15%, 20%)
            # Using flex for proportional/percentage-based widths
            gob.configure_column("ID", hide=True)
            gob.configure_column("Title", flex=9)  # 45% (9/20)
            gob.configure_column("Client", flex=4)  # 20% (4/20)
            gob.configure_column("Role", flex=3)  # 15% (3/20)
            gob.configure_column("Domain", flex=4)  # 20% (4/20)

            gob.configure_selection(selection_mode="single", use_checkbox=False)

            # Disable AgGrid's built-in pagination
            gob.configure_pagination(enabled=False)

            opts = gob.build()
            opts["suppressRowClickSelection"] = False
            opts["rowSelection"] = "single"
            opts["rowHeight"] = 70  # Set explicit row height

            grid = AgGrid(
                df_view,
                gridOptions=opts,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                allow_unsafe_jscode=True,
                theme="streamlit",
                fit_columns_on_grid_load=True,
                height=750,  # Fixed height enables vertical scrolling
            )

            # Handle selection
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
            # Don't auto-select first row - let user choose what to view

        # Numbered pagination controls for table (matching wireframe exactly)
        total_pages = (total_results + page_size - 1) // page_size
        current_page = (offset // page_size) + 1

        if total_pages > 1:
            st.markdown("""
            <style>
            .pagination-info {
                color: var(--text-color);
                opacity: 0.7;
                font-size: 14px;
            }
            /* Style pagination buttons to match segmented control wireframe */
            div[data-testid="column"] .stButton > button {
                border-radius: 8px !important;
                border: 1.5px solid #e0e0e0 !important;
                background: transparent !important;
                color: var(--text-color) !important;
                padding: 8px 16px !important;  /* Increased from 6px 14px */
                font-size: 14px !important;    /* Increased from 13px */
                font-weight: 500 !important;
                min-height: 40px !important;   /* Increased from 36px */
                min-width: 60px !important;    /* NEW - makes buttons more uniform */
                margin: 0 4px !important;      /* NEW - adds gap between buttons */
                transition: all 0.2s ease !important;
            }
            div[data-testid="column"] .stButton > button:hover {
                border-color: #ff4b4b !important;
                background: rgba(255, 75, 75, 0.08) !important;
                color: var(--text-color) !important;
            }
            /* Active page button style */
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
            /* Disabled button style */
            .pagination-disabled {
                text-align: center;
                color: #888;
                opacity: 0.4;
                padding: 6px 14px;
                font-size: 13px;
            }
            </style>
            """, unsafe_allow_html=True)

            # Calculate which page numbers to show (max 5 numbers + ellipsis)
            if total_pages <= 7:
                page_numbers = list(range(1, total_pages + 1))
            else:
                if current_page <= 4:
                    page_numbers = list(range(1, 6)) + ["...", total_pages]
                elif current_page >= total_pages - 3:
                    page_numbers = [1, "..."] + list(range(total_pages - 4, total_pages + 1))
                else:
                    page_numbers = [1, "...", current_page - 1, current_page, current_page + 1, "...", total_pages]

            # Build pagination layout: First | Previous | Numbers | Next | Last | Page info
            num_buttons = len(page_numbers) + 4  # +4 for First, Previous, Next, Last
            cols = st.columns([0.6, 0.6] + [0.35] * len(page_numbers) + [0.6, 0.6, 1.2])

            col_idx = 0

            # First button
            with cols[col_idx]:
                disabled_first = current_page <= 1
                if not disabled_first:
                    if st.button("First", key="btn_first_table", use_container_width=True):
                        st.session_state["page_offset"] = 0
                        st.rerun()
                else:
                    st.markdown("<div class='pagination-disabled'>First</div>", unsafe_allow_html=True)
            col_idx += 1

            # Previous button
            with cols[col_idx]:
                disabled_prev = current_page <= 1
                if not disabled_prev:
                    if st.button("Prev", key="btn_prev_table", use_container_width=True):
                        st.session_state["page_offset"] = offset - page_size
                        st.rerun()
                else:
                    st.markdown("<div class='pagination-disabled'>Prev</div>", unsafe_allow_html=True)
            col_idx += 1

            # Page number buttons
            for page_num in page_numbers:
                with cols[col_idx]:
                    if page_num == "...":
                        st.markdown("<div style='text-align: center; padding: 6px; color: #666;'>...</div>", unsafe_allow_html=True)
                    elif page_num == current_page:
                        st.markdown(f"<div class='pagination-active'>{page_num}</div>", unsafe_allow_html=True)
                    else:
                        if st.button(str(page_num), key=f"btn_page_table_{page_num}", use_container_width=True):
                            st.session_state["page_offset"] = (page_num - 1) * page_size
                            st.rerun()
                col_idx += 1

            # Next button
            with cols[col_idx]:
                disabled_next = current_page >= total_pages
                if not disabled_next:
                    if st.button("Next", key="btn_next_table", use_container_width=True):
                        st.session_state["page_offset"] = offset + page_size
                        st.rerun()
                else:
                    st.markdown("<div class='pagination-disabled'>Next</div>", unsafe_allow_html=True)
            col_idx += 1

            # Last button
            with cols[col_idx]:
                disabled_last = current_page >= total_pages
                if not disabled_last:
                    if st.button("Last", key="btn_last_table", use_container_width=True):
                        st.session_state["page_offset"] = (total_pages - 1) * page_size
                        st.rerun()
                else:
                    st.markdown("<div class='pagination-disabled'>Last</div>", unsafe_allow_html=True)
            col_idx += 1

            # Page info (right side)
            with cols[col_idx]:
                st.markdown(f"<div class='pagination-info' style='text-align: right; padding: 6px;'>Page {current_page} of {total_pages}</div>", unsafe_allow_html=True)

        # Detail panel at bottom (compact version matching wireframe)
        st.markdown("<hr style='margin: 16px 0 12px 0; border: none; border-top: 1px solid var(--border-color);'>", unsafe_allow_html=True)
        detail = get_context_story(stories)
        if detail:
            with safe_container(border=True):
                # Title
                st.markdown(f"<h3 style='margin-bottom: 4px; color: var(--text-color);'>{detail.get('title', 'Untitled')}</h3>", unsafe_allow_html=True)

                # Metadata line
                client = detail.get('client', 'Unknown')
                role = detail.get('role', 'Unknown')
                domain = detail.get('domain', 'Unknown')
                st.markdown(f"<div style='color: var(--text-color); opacity: 0.7; font-size: 14px; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid var(--border-color);'><strong>Client:</strong> {client} &nbsp;&nbsp; <strong>Role:</strong> {role} &nbsp;&nbsp; <strong>Domain:</strong> {domain}</div>", unsafe_allow_html=True)

                # Summary paragraph
                summary = detail.get('5PSummary', '') or build_5p_summary(detail, 999)
                if summary:
                    st.markdown(f"<p style='color: var(--text-color); line-height: 1.6; margin-bottom: 20px;'>{summary}</p>", unsafe_allow_html=True)

                # Key Achievements
                outcomes = detail.get('what', []) or detail.get('Result', [])
                if outcomes and isinstance(outcomes, list) and len(outcomes) > 0:
                    st.markdown("<div style='margin-bottom: 16px;'><strong style='color: var(--text-color);'>Key Achievements:</strong></div>", unsafe_allow_html=True)
                    for outcome in outcomes[:4]:  # Limit to 4 achievements
                        if outcome:
                            st.markdown(f"<div style='margin-left: 20px; margin-bottom: 8px; color: var(--text-color);'>• {outcome}</div>", unsafe_allow_html=True)

                # Ask button
                if st.button(
                    "Ask MattGPT about this",
                    key=f"ask_from_detail_{detail.get('id','x')}",
                    type="primary",
                    use_container_width=False,
                ):
                    on_ask_this_story(detail)
                    st.stop()
        else:
            st.info("Click a row above to view details.")

    else:
        # -------- Cards Grid View --------
        total = len(view)
        # Cards view respects the page_size dropdown (but shows in grid format)
        offset = int(st.session_state.get("page_offset", 0))
        if offset < 0:
            offset = 0
        if offset >= total and total > 0:
            offset = 0
            st.session_state["page_offset"] = 0

        view_window = view[offset : offset + page_size]

        if not view_window:
            st.info("No stories match your filters yet.")
            if st.button("Clear filters", key="clear_filters_empty"):
                st.session_state["filters"] = {
                    "personas": [],
                    "clients": [],
                    "domains": [],
                    "roles": [],
                    "tags": [],
                    "q": "",
                    "has_metric": False,
                }
                st.session_state["facet_domain_group"] = "All"
                st.session_state["page_offset"] = 0
                st.rerun()
        else:
            start = offset + 1
            end = min(offset + page_size, total)

            # Inject card styles right before rendering
            st.markdown("""
            <style>
            .fixed-height-card {
                background: var(--secondary-background-color) !important;
                padding: 28px !important;  /* Increase from 20px */
                border-radius: 12px !important;
                border: 1px solid var(--border-color) !important;
                transition: all 0.3s ease !important;
                height: 380px !important;  /* Increase from 320px */
                display: flex !important;
                flex-direction: column !important;
                box-shadow: 0 4px 12px rgba(0,0,0,.25) !important;
            }
            /* Style View Details buttons to match wireframe */
            .fixed-height-card ~ div button {
                background: transparent !important;
                border: 1.5px solid var(--border-color) !important;
                color: var(--text-color) !important;
            }
            .fixed-height-card:hover {
                transform: translateY(-4px) !important;
                border-color: var(--border-color) !important;
                box-shadow: 0 8px 25px rgba(74,144,226,.15) !important;
            }
            .card-desc {
                color: #b0b0b0 !important;
                margin-bottom: 0 !important;
                line-height: 1.5 !important;
                font-size: 14px !important;
                overflow: hidden !important;
                display: -webkit-box !important;
                -webkit-line-clamp: 5 !important;
                -webkit-box-orient: vertical !important;
            }
            /* Pagination styles */
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
            .pagination-info {
                color: var(--text-color);
                opacity: 0.7;
                font-size: 14px;
            }
            /* View Details button styling to match wireframe */
            .card-button-wrapper button {
                background: transparent !important;
                border: 1.5px solid #e74c3c !important;
                color: #e74c3c !important;
                border-radius: 8px !important;
                padding: 12px 24px !important;
                font-size: 15px !important;
                font-weight: 600 !important;
                transition: all 0.2s ease !important;
            }

            .card-button-wrapper button:hover {
                background: rgba(231, 76, 60, 0.1) !important;
                border-color: #c0392b !important;
            }
            </style>
            """, unsafe_allow_html=True)

            # Dynamic grid based on page size (3 columns per row)
            cards_per_row = 3
            num_rows = (len(view_window) + cards_per_row - 1) // cards_per_row

            for row in range(num_rows):
                cols = st.columns(cards_per_row)

                for col_idx in range(cards_per_row):
                    i = row * cards_per_row + col_idx
                    if i >= len(view_window):
                        continue

                    s = view_window[i]
                    with cols[col_idx]:
                        title = s.get('title', 'Untitled')
                        client = s.get('client', 'Unknown')
                        role = s.get('role', 'Unknown')
                        domain = (s.get("domain") or "").split(" / ")[-1] if s.get("domain") else 'Unknown'
                        summary = s.get("5PSummary", "")

                        st.markdown(f"""
                        <div class="fixed-height-card" style="margin-bottom: 20px;">
                            <h3 style="font-size: 22px; font-weight: 700; margin-bottom: 16px; line-height: 1.3; color: var(--text-color);">{title}</h3>
                            <div style="color: #5b9dd9; font-size: 15px; font-weight: 600; margin-bottom: 10px;">{client}</div>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                                <span style="font-size: 10px; color: #718096; text-transform: uppercase; font-weight: 700; letter-spacing: 0.8px;">{role}</span>
                                <span style="background: rgba(91, 157, 217, 0.12); color: #5b9dd9; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600;">{domain}</span>
                            </div>
                            <p class="card-desc">{summary}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Right before the button, add this wrapper
                        st.markdown('<div class="card-button-wrapper">', unsafe_allow_html=True)

                        story_id = str(s.get('id', i))
                        if st.button("View Details", key=f"card_{story_id}", use_container_width=True):
                            st.session_state["active_story"] = story_id
                            st.rerun()

                        st.markdown('</div>', unsafe_allow_html=True)

            # Numbered pagination controls for cards (matching Table pagination)
            total_pages = (total + page_size - 1) // page_size
            current_page = (offset // page_size) + 1

            if total_pages > 1:
                # Calculate which page numbers to show (max 5 numbers + ellipsis)
                if total_pages <= 7:
                    page_numbers = list(range(1, total_pages + 1))
                else:
                    if current_page <= 4:
                        page_numbers = list(range(1, 6)) + ["...", total_pages]
                    elif current_page >= total_pages - 3:
                        page_numbers = [1, "..."] + list(range(total_pages - 4, total_pages + 1))
                    else:
                        page_numbers = [1, "...", current_page - 1, current_page, current_page + 1, "...", total_pages]

                # Build pagination layout: First | Previous | Numbers | Next | Last | Page info
                cols = st.columns([0.6, 0.6] + [0.35] * len(page_numbers) + [0.6, 0.6, 1.2])

                col_idx = 0

                # First button
                with cols[col_idx]:
                    disabled_first = current_page <= 1
                    if not disabled_first:
                        if st.button("First", key="btn_first_cards", use_container_width=True):
                            st.session_state["page_offset"] = 0
                            st.rerun()
                    else:
                        st.markdown("<div class='pagination-disabled'>First</div>", unsafe_allow_html=True)
                col_idx += 1

                # Previous button
                with cols[col_idx]:
                    disabled_prev = current_page <= 1
                    if not disabled_prev:
                        if st.button("Prev", key="btn_prev_cards", use_container_width=True):
                            st.session_state["page_offset"] = offset - page_size
                            st.rerun()
                    else:
                        st.markdown("<div class='pagination-disabled'>Prev</div>", unsafe_allow_html=True)
                col_idx += 1

                # Page number buttons
                for page_num in page_numbers:
                    with cols[col_idx]:
                        if page_num == "...":
                            st.markdown("<div style='text-align: center; padding: 6px; color: #666;'>...</div>", unsafe_allow_html=True)
                        elif page_num == current_page:
                            st.markdown(f"<div class='pagination-active'>{page_num}</div>", unsafe_allow_html=True)
                        else:
                            if st.button(str(page_num), key=f"btn_page_cards_{page_num}", use_container_width=True):
                                st.session_state["page_offset"] = (page_num - 1) * page_size
                                st.rerun()
                    col_idx += 1

                # Next button
                with cols[col_idx]:
                    disabled_next = current_page >= total_pages
                    if not disabled_next:
                        if st.button("Next", key="btn_next_cards", use_container_width=True):
                            st.session_state["page_offset"] = offset + page_size
                            st.rerun()
                    else:
                        st.markdown("<div class='pagination-disabled'>Next</div>", unsafe_allow_html=True)
                col_idx += 1

                # Last button
                with cols[col_idx]:
                    disabled_last = current_page >= total_pages
                    if not disabled_last:
                        if st.button("Last", key="btn_last_cards", use_container_width=True):
                            st.session_state["page_offset"] = (total_pages - 1) * page_size
                            st.rerun()
                    else:
                        st.markdown("<div class='pagination-disabled'>Last</div>", unsafe_allow_html=True)
                col_idx += 1

                # Page info (right side)
                with cols[col_idx]:
                    st.markdown(f"<div class='pagination-info' style='text-align: right; padding: 6px;'>Page {current_page} of {total_pages}</div>", unsafe_allow_html=True)

            # Detail panel at bottom (compact version matching wireframe)
            st.markdown("<hr style='margin: 16px 0 12px 0; border: none; border-top: 1px solid var(--border-color);'>", unsafe_allow_html=True)
            detail = get_context_story(stories)
            if detail:
                with safe_container(border=True):
                    # Title
                    st.markdown(f"<h3 style='margin-bottom: 4px; color: var(--text-color);'>{detail.get('title', 'Untitled')}</h3>", unsafe_allow_html=True)

                    # Metadata line
                    client = detail.get('client', 'Unknown')
                    role = detail.get('role', 'Unknown')
                    domain = detail.get('domain', 'Unknown')
                    st.markdown(f"<div style='color: var(--text-color); opacity: 0.7; font-size: 14px; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid var(--border-color);'><strong>Client:</strong> {client} &nbsp;&nbsp; <strong>Role:</strong> {role} &nbsp;&nbsp; <strong>Domain:</strong> {domain}</div>", unsafe_allow_html=True)

                    # Summary paragraph
                    summary = detail.get('5PSummary', '') or build_5p_summary(detail, 999)
                    if summary:
                        st.markdown(f"<p style='color: var(--text-color); line-height: 1.6; margin-bottom: 20px;'>{summary}</p>", unsafe_allow_html=True)

                    # Key Achievements
                    outcomes = detail.get('what', []) or detail.get('Result', [])
                    if outcomes and isinstance(outcomes, list) and len(outcomes) > 0:
                        st.markdown("<div style='margin-bottom: 16px;'><strong style='color: var(--text-color);'>Key Achievements:</strong></div>", unsafe_allow_html=True)
                        for outcome in outcomes[:4]:  # Limit to 4 achievements
                            if outcome:
                                st.markdown(f"<div style='margin-left: 20px; margin-bottom: 8px; color: var(--text-color);'>• {outcome}</div>", unsafe_allow_html=True)

                    # Ask button
                    if st.button(
                        "Ask MattGPT about this",
                        key="ask_mattgpt_detail_cards",
                        type="primary",
                        use_container_width=False,
                    ):
                        on_ask_this_story(detail)
            else:
                st.info("Click a card above to view details.")