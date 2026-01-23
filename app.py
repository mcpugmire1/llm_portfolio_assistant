"""
app.py — MattGPT Portfolio Router

Minimal Streamlit router for the MattGPT portfolio application.
Loads data, bootstraps session state, and delegates to page modules.

Architecture documentation: See ARCHITECTURE.md
Design specification: https://github.com/mcpugmire1/mattgpt-design-spec
"""

# Standard library
import json
import os
from pathlib import Path

import streamlit as st

# Third-party
from dotenv import load_dotenv

# Local imports - utilities
from config.debug import DEBUG
from services.rag_service import initialize_vocab
from ui.components.navbar import render_navbar

# Local imports - components
from ui.pages.home import render_home_page
from ui.styles.global_styles import apply_global_styles

# =========================
# UI — Home / Stories / Ask / About

load_dotenv()

st.set_page_config(
    page_title="MattGPT | Matt Pugmire",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed",  # Hide sidebar - we use top navbar instead
)

# Apply global styles once per session
apply_global_styles()

# Render navbar (shows on all pages)
render_navbar(current_tab=st.session_state.get("active_tab", "Home"))

# ---- first-mount guard ----
if not st.session_state.get("__first_mount_rerun__", False):
    st.session_state["__first_mount_rerun__"] = True
    st.rerun()

# Initialize session state for active tab
st.session_state.setdefault("active_tab", "Home")

if DEBUG:
    with st.sidebar.expander("📊 Pinecone debug (last query)", expanded=True):
        dbg_state = st.session_state.get("__pc_debug__", {}) or {}
        if not dbg_state:
            st.caption("No query yet.")
        else:
            st.write({k: v for k, v in dbg_state.items() if k != "stats"})
            st.write("Index stats:")
            st.json(dbg_state.get("stats", {}))

# --- Tab navigation helpers ---
_ALIASES = {"Stories": "Explore Stories"}


def normalize_tab(name: str) -> str:
    return _ALIASES.get(name, name)


def goto(tab_name: str):
    tab = normalize_tab(tab_name)
    st.session_state["active_tab"] = tab
    # If we are navigating to Home, ensure the Home pills do NOT auto-jump
    # by marking the first render as a fresh mount.
    if tab == "Home":
        st.session_state["__home_first_mount__"] = True
    # Stop this render immediately; the next run will paint the new tab.
    st.stop()


# Coerce any legacy/old values that may still be in session state
if st.session_state.get("active_tab") == "Stories":
    st.session_state["active_tab"] = "Explore Stories"


# =========================
# Config / constants
# =========================
DATA_FILE = os.getenv("STORIES_JSONL", "echo_star_stories_nlp.jsonl")  # optional


def _ensure_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return [x for x in v if str(x).strip()]
    return [str(v)] if str(v).strip() else []


def _split_tags(s):
    if not s:
        return []
    if isinstance(s, list):
        return [str(x).strip() for x in s if str(x).strip()]
    return [t.strip() for t in str(s).split(",") if t.strip()]


def load_star_stories(path: str):
    """Load JSONL records as-is, preserving all fields from source data.

    This is a "dumb loader" - no business logic, no transformation, no synthetic fields.
    Just loads what's in the JSONL file.

    Changes:
    - NO fallback to a different filename: if the requested path doesn't exist, return [].
    - REQUIRE a stable `id`: if missing, skip the row (prevents mismatch with Pinecone vector IDs).
    - Preserves ALL fields from JSONL (including Solution / Offering, Category, Sub-category, etc.)
    - Emit small warnings for visibility.
    """
    stories: list[dict] = []
    p = Path(path)
    if not p.exists():
        st.warning(f"Stories file not found: {path!r}. No fallback will be used.")
        return stories

    skipped_no_id = 0
    with p.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                story = json.loads(line)
            except Exception as e:
                st.warning(f"JSON parse error at line {line_no}: {e}")
                continue

            # Enforce a stable ID so Pinecone hits can map back to STORIES
            story_id = story.get("id")
            if story_id in (None, "", 0):
                skipped_no_id += 1
                continue

            # Ensure id is a string
            story["id"] = str(story_id).strip()

            # Normalize list fields (accept strings or arrays) - this is data cleaning, not business logic
            for field in [
                "Situation",
                "Task",
                "Action",
                "Result",
                "Process",
                "Performance",
                "Competencies",
                "Use Case(s)",
            ]:
                if field in story:
                    story[field] = _ensure_list(story[field])

            # Parse public_tags from comma-separated string to list - this is data cleaning
            if "public_tags" in story and isinstance(story["public_tags"], str):
                story["public_tags"] = _split_tags(story["public_tags"])

            stories.append(story)

    if DEBUG:
        if skipped_no_id:
            st.caption(
                f"DEBUG • Loaded {len(stories)} stories from {p.name}; skipped {skipped_no_id} rows without an 'id' (kept Pinecone mapping stable)."
            )
        else:
            st.caption(f"DEBUG • Loaded {len(stories)} stories from {p.name}.")

    return stories


# Load stories from JSONL
STORIES = load_star_stories(DATA_FILE)
if not STORIES:
    st.error(f"❌ Failed to load stories from {DATA_FILE}. Check file path and format.")
    st.stop()

# Initialize search vocabulary at startup
initialize_vocab(STORIES)

# Sync portfolio metadata (MATT_DNA, SYNTHESIS_THEMES) from story data
# This ensures grounding prompt and themes never drift from JSONL
# NOTE: Deferred import to avoid circular dependency (backend_service ← conversation_view ← __init__)
from ui.pages.ask_mattgpt.backend_service import sync_portfolio_metadata  # noqa: E402

sync_portfolio_metadata(STORIES)


# =========================
# Session state
# =========================
st.session_state.setdefault(
    "filters",
    {
        "personas": [],
        "clients": [],
        "domains": [],
        "roles": [],
        "tags": [],
        "q": "",
        "has_metric": False,
        "era": "",  # ADD
        "industry": "",
        "capability": "",
    },
)

st.session_state.setdefault("active_story", None)
st.session_state.setdefault("seed_prompt", "")
st.session_state.setdefault("last_answer", "")
st.session_state.setdefault(
    "answer_modes", {}
)  # for the Narrative/Key points/Deep dive content
st.session_state.setdefault("answer_mode", "narrative")
st.session_state.setdefault("last_sources", [])
st.session_state.setdefault("last_results", STORIES)
st.session_state.setdefault("show_ask_panel", False)
st.session_state.setdefault("ask_input", "")
st.session_state.setdefault("ask_transcript", [])
st.session_state.setdefault("__inject_user_turn__", None)
st.session_state.setdefault("__pending_card_snapshot__", False)
st.session_state.setdefault("__sticky_banner__", None)
st.session_state.setdefault("__suppress_live_card_once__", False)

# For Pinecone snippets + low-confidence banner
st.session_state.setdefault("__pc_last_ids__", {})  # {story_id: score}
st.session_state.setdefault("__pc_snippets__", {})  # {story_id: snippet}
st.session_state.setdefault("__pc_suppressed__", False)

# Paging state defaults
st.session_state.setdefault("page_size", 25)
st.session_state.setdefault("page_offset", 0)

# =========================
# Deep-link handling: ?story=story-id
# =========================
if 'story' in st.query_params:
    story_from_url = st.query_params['story']
    if st.session_state.get('_deeplink_story') != story_from_url:
        st.session_state['active_story'] = story_from_url
        st.session_state['active_tab'] = 'Explore Stories'
        st.session_state['explore_view_mode'] = 'Cards'
        st.session_state['_deeplink_story'] = story_from_url
        st.rerun()

# =========================
# Helpers
# =========================


def _clear_explore_state():
    """Reset all Explore Stories state for a fresh slate on navigation away."""
    st.session_state.pop("return_to_landing", None)
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
    st.session_state["page_offset"] = 0
    st.session_state["active_story"] = None
    # Clear cached search results
    st.session_state.pop("__last_search_results__", None)
    st.session_state.pop("__last_search_confidence__", None)
    st.session_state.pop("__last_search_query__", None)


def build_facets(stories):
    """Build filter option lists from story data using raw JSONL field names."""
    # Primary filters (NEW for Phase 4 redesign)
    industries = sorted({s.get("Industry", "") for s in stories if s.get("Industry")})
    capabilities = sorted(
        {
            s.get("Solution / Offering", "")
            for s in stories
            if s.get("Solution / Offering")
        }
    )

    # Advanced filters
    clients = sorted({s.get("Client", "") for s in stories if s.get("Client")})
    # domains now comes from Sub-category field (used to be synthetic Category / Sub-category)
    domains = sorted(
        {s.get("Sub-category", "") for s in stories if s.get("Sub-category")}
    )
    roles = sorted({s.get("Role", "") for s in stories if s.get("Role")})
    # tags comes from public_tags (already parsed to list in loader)
    tags = sorted({t for s in stories for t in (s.get("public_tags") or [])})
    # personas field doesn't exist in current data
    personas = []
    return industries, capabilities, clients, domains, roles, tags, personas


# =========================
# UI — Home / Stories / Ask / About
# =========================
industries, capabilities, clients, domains, roles, tags, personas_all = build_facets(
    STORIES
)

if st.session_state["active_tab"] == "Home":
    _clear_explore_state()
    from ui.pages.home import render_home_page

    render_home_page(STORIES)

# --- BANKING LANDING ---
elif st.session_state["active_tab"] == "Banking":
    _clear_explore_state()
    from ui.pages.banking_landing import render_banking_landing

    render_banking_landing(STORIES)

# --- CROSS-INDUSTRY LANDING ---
elif st.session_state["active_tab"] == "Cross-Industry":
    _clear_explore_state()
    from ui.pages.cross_industry_landing import render_cross_industry_landing

    render_cross_industry_landing(STORIES)

# --- REFACTORED STORIES ---
elif st.session_state["active_tab"] == "Explore Stories":
    from ui.pages.explore_stories import render_explore_stories

    render_explore_stories(
        STORIES,
        industries,
        capabilities,
        clients,
        domains,
        roles,
        tags,
        personas_all,
    )

# --- ASK MATTGPT ---
elif st.session_state["active_tab"] == "Ask MattGPT":
    _clear_explore_state()
    from ui.pages.ask_mattgpt import render_ask_mattgpt

    render_ask_mattgpt(STORIES)

# --- ABOUT ---
elif st.session_state["active_tab"] == "About Matt":
    _clear_explore_state()
    from ui.pages.about_matt import render_about_matt

    render_about_matt()

# --- INVALID TAB FALLBACK ---
else:
    st.error(f"❌ Unknown page: {st.session_state['active_tab']}")
    st.info(
        "Valid pages: Home, Explore Stories, Ask MattGPT, About Matt, Banking, Cross-Industry"
    )
    # Reset to home
    st.session_state["active_tab"] = "Home"
    st.rerun()
