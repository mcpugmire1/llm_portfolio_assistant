import streamlit as st

# app_next.py — Next-gen UI (Home / Stories / Ask / About)
# - Clean, centered layout without sidebar
# - Pinecone-first (guarded) + local fallback search
# - Debounced “Ask MattGPT” with starter chips
# - Compact List view by default, Card view optional
# - Badges + strongest-metric summary
# Standard library
import json
import os
import re
import textwrap
import time

# Third-party
import pandas as pd
from dotenv import load_dotenv

# Local imports - components
from ui.pages.home import render_home_page
from ui.components.navbar import render_navbar
from ui.styles.global_styles import apply_global_styles

# Local imports - utilities
from config.debug import DEBUG
from config.settings import get_conf

# =========================
# UI — Home / Stories / Ask / About

load_dotenv()

VECTOR_BACKEND = (get_conf("VECTOR_BACKEND", "faiss") or "faiss").lower()
OPENAI_API_KEY = get_conf("OPENAI_API_KEY")
PINECONE_API_KEY = get_conf("PINECONE_API_KEY")
PINECONE_INDEX_NAME = get_conf("PINECONE_INDEX_NAME")  # no default
PINECONE_NAMESPACE = get_conf("PINECONE_NAMESPACE")  # no default
PINECONE_ALLOW_CREATE = str(
    get_conf("PINECONE_ALLOW_CREATE", "false")
).strip().lower() in {"1", "true", "yes", "on"}
PINECONE_TRY_DEFAULT_NS = str(
    get_conf("PINECONE_TRY_DEFAULT_NS", "false")
).strip().lower() in {"1", "true", "yes", "on"}

# Guard: Require Pinecone config ONLY if VECTOR_BACKEND == "pinecone"
if VECTOR_BACKEND == "pinecone":
    missing = []
    if not PINECONE_API_KEY:
        missing.append("PINECONE_API_KEY")
    if not PINECONE_INDEX_NAME:
        missing.append("PINECONE_INDEX_NAME")
    if not PINECONE_NAMESPACE:
        missing.append("PINECONE_NAMESPACE")
    if missing:
        raise RuntimeError(
            f"Missing required Pinecone config: {', '.join(missing)}. Set them in st.secrets or .env"
        )

# Lazy Pinecone init only if selected
pinecone_index = None
if VECTOR_BACKEND == "pinecone":
    try:
        from pinecone import Pinecone

        pc = Pinecone(api_key=PINECONE_API_KEY)
        pinecone_index = pc.Index(PINECONE_INDEX_NAME)
    except Exception as e:
        # Do NOT downgrade to FAISS silently; keep backend as pinecone and retry lazily later.
        st.warning(f"Pinecone init failed at startup; will retry lazily. ({e})")
        pinecone_index = None

st.set_page_config(
    page_title="Matt Pugmire | Director of Technology Delivery | Digital Transformation Leader",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar - we use top navbar instead
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

# --- Tab names and nav helpers (must be defined before any use of goto) ---
TAB_NAMES = ["Home", "Explore Stories", "Ask MattGPT", "About Matt"]
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


# Choose nav mode:
USE_SIDEBAR_NAV = False  # Using top navbar instead

# single source of truth for the current tab
st.session_state.setdefault("active_tab", "Home")
# Coerce any legacy/old values that may still be in session state
if st.session_state.get("active_tab") == "Stories":
    st.session_state["active_tab"] = "Explore Stories"


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


# Safe alias that mirrors F() but is immune to shadowing elsewhere
def field_value(s: dict, key: str, default: str | list | None = None):
    # Inline copy of F() to avoid name collisions
    if key in s:
        return s[key]
    pc = key[:1].upper() + key[1:]
    if pc in s:
        return s[pc]

    if key == "domain":
        cat = s.get("Category") or s.get("Domain")
        sub = s.get("Sub-category") or s.get("SubCategory")
        if cat and sub:
            return f"{cat} / {sub}"
        return cat or sub or default

    if key == "tags":
        if "tags" in s and isinstance(s["tags"], list):
            return s["tags"]
        pub = s.get("public_tags")
        if isinstance(pub, list):
            return pub
        if isinstance(pub, str):
            return [t.strip() for t in pub.split(",") if t.strip()]
        return default or []

    alias = {
        "who": "Person",
        "where": "Place",
        "why": "Purpose",
        "how": "Process",
        "what": "Performance",
    }
    if key in alias and alias[key] in s:
        return s[alias[key]]

    return default


# =========================
# Config / constants
# =========================
DATA_FILE = os.getenv("STORIES_JSONL", "echo_star_stories_nlp.jsonl")  # optional

import json, os, re
from pathlib import Path


def _ensure_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        # trim whitespace bullets
        return [x.strip(" -\t") for x in v if str(x).strip()]
    # split on newlines or "•"/"-" bullets
    text = str(v)
    parts = re.split(r"\n|•|-  ", text)
    return [p.strip(" -\t") for p in parts if p and p.strip()]


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
    stories = []
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
            for field in ["Situation", "Task", "Action", "Result", "Process", "Performance", "Competencies", "Use Case(s)"]:
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
from services.rag_service import initialize_vocab
initialize_vocab(STORIES)


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
# Helpers
# =========================



def render_no_match_banner(
    reason: str,
    query: str,
    overlap: float | None = None,
    suppressed: bool = False,
    filters: dict | None = None,
    *,
    key_prefix: str = "banner",
):
    """
    Unified yellow warning banner for 'no confident match' situations.
    Always shows a consistent message, suggestions, and optionally a Clear Filters button.
    """
    msg = "I couldn’t find anything confidently relevant to that query."
    debug_note = ""
    if DEBUG and reason:
        debug_note = f"  \n_Reason: {reason}"
        if overlap is not None:
            debug_note += f" (overlap={overlap:.2f})"
        debug_note += "_"
    msg += debug_note
    st.warning(msg)

    # Chips act as clean semantic prompts (no tag/domain filters)
    suggestions = [
        (
            "Payments modernization",
            "Tell me about your work modernizing payments platforms.",
        ),
        (
            "Generative AI in healthcare",
            "Tell me about applying Generative AI in healthcare.",
        ),
        (
            "Cloud-native architecture",
            "Tell me about your cloud-native architecture work.",
        ),
        (
            "Innovation in digital products",
            "Tell me about driving innovation in digital products.",
        ),
    ]
    cols = st.columns(len(suggestions))
    for i, (label, prompt_text) in enumerate(suggestions):
        with cols[i]:
            if st.button(
                label, key=f"{key_prefix}_suggest_no_match_{i}_{hash(label)%10000}"
            ):
                # Inject a new user turn with a concise prompt; rely on semantic search only
                st.session_state["__inject_user_turn__"] = prompt_text
                # Mark that this came from a suggestion chip to relax off-domain gating once
                st.session_state["__ask_from_suggestion__"] = True
                # Guarantee we build a compact answer panel even if retrieval is empty
                st.session_state["__ask_force_answer__"] = True
                st.session_state["ask_input"] = prompt_text
                st.session_state["active_tab"] = "Ask MattGPT"
                # Defer banner clearing to after a successful answer, avoiding duplicates
                st.session_state["__clear_banner_after_answer__"] = True
                st.rerun()

    # Show Clear Filters button if filters exist and are non-empty
    if filters:
        # Check if any filter is set (excluding 'q' and 'has_metric' for len check)
        any_active = any(
            (isinstance(v, list) and v)
            or (isinstance(v, str) and v.strip())
            or (isinstance(v, bool) and v)
            for k, v in filters.items()
            if k
            in ["personas", "clients", "domains", "roles", "tags", "has_metric", "q"]
        )
        if any_active:
            if st.button("Clear filters", key=f"{key_prefix}_clear_filters_no_match"):
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




def build_facets(stories):
    """Build filter option lists from story data using raw JSONL field names."""
    # Primary filters (NEW for Phase 4 redesign)
    industries = sorted({s.get("Industry", "") for s in stories if s.get("Industry")})
    capabilities = sorted({s.get("Solution / Offering", "") for s in stories if s.get("Solution / Offering")})

    # Advanced filters
    clients = sorted({s.get("Client", "") for s in stories if s.get("Client")})
    # domains now comes from Sub-category field (used to be synthetic Category / Sub-category)
    domains = sorted({s.get("Sub-category", "") for s in stories if s.get("Sub-category")})
    roles = sorted({s.get("Role", "") for s in stories if s.get("Role")})
    # tags comes from public_tags (already parsed to list in loader)
    tags = sorted({t for s in stories for t in (s.get("public_tags") or [])})
    # personas field doesn't exist in current data
    personas = []
    return industries, capabilities, clients, domains, roles, tags, personas

# =========================
# UI — Home / Stories / Ask / About
# =========================
industries, capabilities, clients, domains, roles, tags, personas_all = build_facets(STORIES)

if st.session_state["active_tab"] == "Home":
    from ui.pages.home import render_home_page
    render_home_page()

# --- BANKING LANDING ---
elif st.session_state["active_tab"] == "Banking":
    from ui.pages.banking_landing import render_banking_landing
    render_banking_landing()

# --- CROSS-INDUSTRY LANDING ---
elif st.session_state["active_tab"] == "Cross-Industry":
    from ui.pages.cross_industry_landing import render_cross_industry_landing
    render_cross_industry_landing()

# --- REFACTORED STORIES ---
elif st.session_state["active_tab"] == "Explore Stories":
    from ui.pages.explore_stories import render_explore_stories
    render_explore_stories(STORIES, industries, capabilities, clients, domains, roles, tags, personas_all)

# --- ASK MATTGPT ---
elif st.session_state["active_tab"] == "Ask MattGPT":
    from ui.pages.ask_mattgpt import render_ask_mattgpt
    render_ask_mattgpt(STORIES)

# --- ABOUT ---
elif st.session_state["active_tab"] == "About Matt":
    from ui.pages.about_matt import render_about_matt
    render_about_matt()
