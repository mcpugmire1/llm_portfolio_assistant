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
from typing import List, Optional
from urllib.parse import quote_plus

# Third-party
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Local imports - components
from ui.legacy_components import css_once, render_home_hero_and_stats, render_home_starters
from ui.components.navbar import render_navbar
from ui.styles.global_styles import apply_global_styles

# Local imports - utilities
from config.debug import DEBUG
from config.settings import get_conf
from utils.ui_helpers import safe_container, dbg
from services.pinecone_service import _safe_json
from utils.formatting import (
    _format_narrative, 
    _format_key_points, 
    _format_deep_dive,
    build_5p_summary,
    strongest_metric_line,
    story_has_metric,
)
from utils.validation import is_nonsense, token_overlap_ratio, _tokenize


# =========================
# UI — Home / Stories / Ask / About

ASSIST_AVATAR = "🤖"  # keep the retro robot
USER_AVATAR = "🗣️"  # or "🙋", "🧑", "👋", "👥", "🧑‍💻", etc.

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

# optional: row-click table
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

    _HAS_AGGRID = True
except Exception:
    _HAS_AGGRID = False

st.set_page_config(
    page_title="MattGPT — Matt's Story",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar - we use top navbar instead
)

# Apply global styles once per session
apply_global_styles()

# ensure external UI CSS is injected once (safe no-op if it's empty)
css_once()

# ---- first-mount guard: let CSS finish applying, then paint once more ----
if not st.session_state.get("__first_mount_rerun__", False):
    st.session_state["__first_mount_rerun__"] = True
    st.rerun()

# Initialize session state for active tab
st.session_state.setdefault("active_tab", "Home")

# Render top navigation bar
render_navbar(current_tab=st.session_state.get("active_tab", "Home"))
# optional: ChatGPT-style sidebar menu
try:
    from streamlit_option_menu import option_menu

    _HAS_OPTION_MENU = True
except Exception:
    _HAS_OPTION_MENU = False

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

#
# Optional external renderer hooks (may be injected by other modules)
_ext_render_sources_chips = globals().get("_ext_render_sources_chips")
_ext_render_sources_badges_static = globals().get("_ext_render_sources_badges_static")


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


# === Sidebar navigation (option_menu with mono line icons) ===
if USE_SIDEBAR_NAV:
    with st.sidebar:
        st.header("MattGPT")

        if _HAS_OPTION_MENU:
            _OPTIONS = ["Home", "Explore Stories", "Ask MattGPT", "About Matt"]
            current = normalize_tab(st.session_state.get("active_tab", "Home"))
            def_idx = _OPTIONS.index(current) if current in _OPTIONS else 0

            selected = option_menu(
                menu_title=None,
                options=_OPTIONS,
                icons=["house", "book", "chat-dots", "person"],  # Bootstrap mono icons
                default_index=def_idx,
                orientation="vertical",
                styles={
                    "container": {"padding": "0", "background": "transparent"},
                    "icon": {"color": "inherit", "font-size": "1.1rem"},
                    "nav-link": {
                        "font-size": "1rem",
                        "padding": "10px 14px",
                        "border-radius": "8px",
                        "color": "inherit",
                        "white-space": "nowrap",
                        "background-color": "transparent",
                        "font-weight": "600",
                    },
                    "nav-link-selected": {
                        "font-size": "1rem",
                        "padding": "10px 14px",
                        "border-radius": "8px",
                        "color": "inherit",
                        "white-space": "nowrap",
                        "background-color": "transparent",
                        "font-weight": "600",
                    },
                },
            )

            if normalize_tab(selected) != current:
                new_tab = normalize_tab(selected)
                st.session_state["active_tab"] = new_tab
                # Reset Home's first-mount guard so the Home page doesn't immediately
                # redirect back to the last pill selection.
                if new_tab == "Home":
                    st.session_state["__home_first_mount__"] = True
                st.rerun()

        else:
            # Fallback if option_menu isn't installed: minimal text + glyphs
            ICONS = {
                "Home": "⌂",
                "Explore Stories": "📖",
                "Ask MattGPT": "💭",
                "About Matt": "👤",
            }
            current = st.session_state.get("active_tab", "Home")
            for name in ["Home", "Explore Stories", "Ask MattGPT", "About Matt"]:
                label = f"{ICONS.get(name,'')}  {name}"
                if st.button(
                    label,
                    key=f"nav_{name}",
                    use_container_width=True,
                    disabled=(name == current),
                ):
                    goto(name)

        st.divider()

        st.markdown(
            '<div class="quick-actions-header">Try it out</div>', unsafe_allow_html=True
        )

        ex = [
            "Tell me about leading a global payments transformation.",
            "How did you apply GenAI in a healthcare project?",
            "How have you driven innovation in your career?",
        ]
        for i, q in enumerate(ex):
            if st.button(q, key=f"exq_{i}", use_container_width=True):
                # Treat like fresh typed questions - pure semantic search
                st.session_state["__inject_user_turn__"] = q
                # Don't set force_answer - let semantic search rank naturally
                # Clear context lock so these trigger fresh searches
                st.session_state.pop("__ctx_locked__", None)
                st.session_state.pop("active_context", None)
                st.session_state["active_tab"] = "Ask MattGPT"
                st.rerun()
        st.divider()
# ------------------------------------------------------------



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


def STAR(s: dict) -> dict:
    return {
        "situation": s.get("Situation", []) or s.get("situation", []),
        "task": s.get("Task", []) or s.get("task", []),
        "action": s.get("Action", []) or s.get("action", []),
        "result": s.get("Result", []) or s.get("result", []),
    }


def FIVEP_SUMMARY(s: dict) -> str:
    return s.get("5PSummary") or s.get("5p_summary") or ""


# =========================
# Story modes and related helpers
# =========================
def story_modes(s: dict) -> dict:
    """Return the three anchored views for a single story."""
    return {
        "narrative": _format_narrative(s),
        "key_points": _format_key_points(s),
        "deep_dive": _format_deep_dive(s),
    }


def _related_stories(s: dict, max_items: int = 3) -> list[dict]:
    """
    Very light 'related' heuristic: prefer same client, then same domain/tags.
    Excludes the current story. Returns up to max_items stories.
    """
    cur_id = s.get("id")
    dom = s.get("domain", "")
    client = s.get("client", "")
    tags = set(s.get("tags", []) or [])
    # simple scoring
    scored = []
    for t in STORIES:
        if t.get("id") == cur_id:
            continue
        score = 0
        if client and t.get("client") == client:
            score += 3
        if dom and t.get("domain") == dom:
            score += 2
        if tags:
            score += len(tags & set(t.get("tags", []) or []))
        if score:
            scored.append((score, t))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored[:max_items]]


def _summarize_index_stats(stats: dict) -> dict:
    """Return a compact view of Pinecone index stats."""
    if not isinstance(stats, dict):
        return {}
    namespaces = stats.get("namespaces") or {}
    dims = stats.get("dimension")
    total_vecs = 0
    by_ns = {}
    for ns, info in namespaces.items():
        count = (info or {}).get("vector_count") or 0
        by_ns[ns or ""] = int(count)
        total_vecs += int(count)
    return {
        "dimension": int(dims) if dims else None,
        "total_vectors": int(total_vecs),
        "namespaces": by_ns,  # {"default": 115, "": 0, ...}
    }


# =========================
# Config / constants
# =========================
PINECONE_MIN_SIM = 0.15  # gentler gate: surface more semantically-close hits
_DEF_DIM = 384  # stub embedding size to keep demo self-contained
DATA_FILE = os.getenv("STORIES_JSONL", "echo_star_stories_nlp.jsonl")  # optional

# 🔧 Hybrid score weights (tune these!)
W_PC = 0.8  # semantic (Pinecone vector match)
W_KW = 0.2  # keyword/token overlap

# Centralized retrieval pool size for semantic search / Pinecone
SEARCH_TOP_K = 100  # Increased to capture more industry-specific results


# =========================
# Safe Pinecone wiring (optional)
# =========================
try:
    from pinecone import Pinecone  # type: ignore
except Exception:
    Pinecone = None  # keeps the app running without Pinecone installed

_PINECONE_API_KEY = get_conf("PINECONE_API_KEY")
_PINECONE_INDEX = PINECONE_INDEX_NAME or get_conf("PINECONE_INDEX_NAME")
_PC = None
_PC_INDEX = None

# NOTE: When adding upserts, always pass namespace=PINECONE_NAMESPACE to .upsert()/.update()


def _init_pinecone():
    """Lazy init of Pinecone client + index (no-op if unavailable)."""
    global _PC, _PC_INDEX
    if _PC_INDEX is not None:
        return _PC_INDEX
    if not (_PINECONE_API_KEY and Pinecone):
        return None
    try:
        _PC = Pinecone(api_key=_PINECONE_API_KEY)
        # Inspect existing indexes (and their dimensions) once
        idx_list = _PC.list_indexes().indexes
        existing = {i.name: i for i in idx_list}
        if _PINECONE_INDEX not in existing:
            if DEBUG:
                print(
                    f"DEBUG Pinecone: index '{_PINECONE_INDEX}' missing. allow_create={PINECONE_ALLOW_CREATE or DEBUG}"
                )
            if PINECONE_ALLOW_CREATE or DEBUG:
                _PC.create_index(
                    name=_PINECONE_INDEX, dimension=_DEF_DIM, metric="cosine"
                )
            else:
                # Do not create in prod unless explicitly allowed
                return None
        else:
            # Validate dimension if available
            try:
                dim = getattr(existing[_PINECONE_INDEX], "dimension", None)
                if dim and int(dim) != int(_DEF_DIM):
                    if DEBUG:
                        print(
                            f"DEBUG Pinecone: index dim mismatch (have={dim}, want={_DEF_DIM}); refusing to use."
                        )
                    return None
            except Exception:
                pass

        _PC_INDEX = _PC.Index(_PINECONE_INDEX)
        return _PC_INDEX
    except Exception as e:
        if DEBUG:
            print(f"DEBUG Pinecone init error: {e}")
        return None


# =========================
# Load data (JSONL optional) with safe fallback
# =========================
def _load_jsonl(path: str) -> Optional[List[dict]]:
    try:
        if not os.path.exists(path):
            return None
        out = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                out.append(json.loads(line))
        return out or None
    except Exception:
        return None


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


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).strip().lower()).strip("-") or "x"


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

# --- Query-param navigation: /?view=explore&story_id=<id>
params = st.query_params
if params.get("view") == "explore" and params.get("story_id"):
    st.session_state["active_story"] = params.get("story_id")
    st.session_state["active_tab"] = "Explore Stories"
    st.rerun()

# For Pinecone snippets + low-confidence banner
st.session_state.setdefault("__pc_last_ids__", {})  # {story_id: score}
st.session_state.setdefault("__pc_snippets__", {})  # {story_id: snippet}
st.session_state.setdefault("__pc_suppressed__", False)

# Paging state defaults
st.session_state.setdefault("page_size", 25)
st.session_state.setdefault("page_offset", 0)

# Ensure no stray chat_input outside Ask tab
# (REMOVED global user_input_local = st.chat_input("Ask anything…", key="ask_chat_input1"))


# =========================
# Helpers
# =========================

# --- Unified tiny façade to simplify badge rendering (keep old fns working) ---




_BADGE_PALETTE = [
    "#4F46E5",
    "#059669",
    "#DC2626",
    "#D97706",
    "#0EA5E9",
    "#7C3AED",
    "#16A34A",
    "#EA580C",
    "#A855F7",
    "#0891B2",
]

## debounce logic removed


def _badge_color(label: str) -> str:
    if not label:
        return "#6B7280"
    idx = sum(ord(c) for c in label) % len(_BADGE_PALETTE)
    return _BADGE_PALETTE[idx]


_DOT_EMOJI = [
    "🟦",
    "🟩",
    "🟥",
    "🟧",
    "🟦",
    "🟪",
    "🟩",
    "🟧",
    "🟪",
    "🟦",
]  # stable palette-ish


def _clear_ask_context():
    """Remove any sticky context so the next ask is general-purpose."""
    st.session_state.pop("active_story", None)
    st.session_state.pop("__ctx_locked__", None)
    # Optional: also clear any preloaded seed text
    st.session_state.pop("seed_prompt", None)
    # Do NOT clear last_sources; that belongs to the last answer
    st.rerun()


# --- Clean Answer Card (mock_ask_hybrid style) -------------------------------



def _dot_for(label: str) -> str:
    if not label:
        return "•"
    idx = sum(ord(c) for c in label) % len(_DOT_EMOJI)
    return _DOT_EMOJI[idx]


def _shorten_middle(text: str, max_len: int = 64) -> str:
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    keep = max_len - 1
    left = keep // 2
    right = keep - left
    return text[:left] + "… " + text[-right:]



def render_list(items: Optional[List[str]]):
    for x in items or []:
        st.write(f"- {x}")



# --- Nonsense rules (JSONL) + known vocab -------------------
import csv
from datetime import datetime


# Known vocab built from stories (call once after STORIES is loaded)
_KNOWN_VOCAB = set()


def build_known_vocab(stories: list[dict]):
    vocab = set()
    for s in stories:
        # Use lowercase field names from normalized stories
        for field in ["title", "client", "role", "domain", "division", "industry", "who", "where", "why"]:
            txt = (s.get(field) or "").lower()
            vocab.update(re.split(r"[^\w]+", txt))
        for t in s.get("tags") or []:
            vocab.update(re.split(r"[^\w]+", str(t).lower()))
    # prune tiny tokens
    return {w for w in vocab if len(w) >= 3}



# simple CSV logger
def log_offdomain(query: str, reason: str, path: str = "data/offdomain_queries.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    row = [datetime.utcnow().isoformat(timespec="seconds"), query, reason]
    header = ["ts_utc", "query", "reason"]
    write_header = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(header)
        w.writerow(row)


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


# Build known-vocab now that build_known_vocab() is defined
_KNOWN_VOCAB = build_known_vocab(STORIES)


# --- Helper: sanitize legacy CTA in answers ---
def _sanitize_answer(text: str) -> str:
    """Remove legacy STAR/5P CTA and replace with neutral wording."""
    if not text:
        return text
    legacy = "Want a deeper dive or a 60-second spoken version? Ask for STAR/5P or a tailored summary."
    replacement = "Want more detail or a 60‑second version? Switch the view above or ask for a tailored summary."
    return text.replace(legacy, replacement)


# --- Pinecone UI helpers: matched snippet + score ---
def _fmt_score(score) -> str:
    try:
        return f"{float(score):.2f}"
    except Exception:
        return "n/a"


def _matched_caption(story_id: str, fallback_builder=build_5p_summary) -> str:
    """
    Build 'Matched on: … (score …)' using Pinecone snippet + score, with a clean fallback.
    - Uses session_state['__pc_snippets__'][id] for snippet (if present)
    - Uses session_state['__pc_last_ids__'][id] for score (if present)
    - Falls back to build_5p_summary(story) if no Pinecone snippet is available
    """
    snippets = st.session_state.get("__pc_snippets__", {}) or {}
    scores = st.session_state.get("__pc_last_ids__", {}) or {}

    snip = (snippets.get(story_id) or "").strip()
    score = scores.get(story_id)
    # If we don't have a Pinecone snippet, try to build a 5P fallback from the local story
    if not snip:
        story = next((s for s in STORIES if str(s.get("id")) == str(story_id)), None)
        if story:
            snip = fallback_builder(story)

    # Tidy + truncate for UI neatness
    snip = " ".join(str(snip).split())
    if len(snip) > 220:
        snip = snip[:217] + "..."

    return f"🔎 Matched on: {snip} (score { _fmt_score(score) })"




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


# --- Minimal linear transcript helpers (Ask) ---
def _ensure_ask_bootstrap():
    """Guarantee the Ask transcript starts with the assistant opener once per session."""
    if "ask_transcript" not in st.session_state:
        st.session_state["ask_transcript"] = []
    if not st.session_state["ask_transcript"]:
        st.session_state["ask_transcript"].append(
            {"role": "assistant", "text": "Ask anything."}
        )


def _push_user_turn(text: str):
    st.session_state["ask_transcript"].append({"role": "user", "text": text})
    st.session_state["__asked_once__"] = True


def _push_assistant_turn(text: str):
    st.session_state["ask_transcript"].append({"role": "assistant", "text": text})


def _clear_ask_context():
    """Remove any sticky story context so the next Ask is general-purpose."""
    st.session_state.pop("active_story", None)
    st.session_state.pop("__ctx_locked__", None)
    st.session_state.pop("seed_prompt", None)
    st.rerun()

# === Ask MattGPT helpers ===

# =========================
# UI — Home / Stories / Ask / About
# =========================
industries, capabilities, clients, domains, roles, tags, personas_all = build_facets(STORIES)

# --- HOME ---
if st.session_state["active_tab"] == "Home":

    # Check if a button just changed the tab by looking for the flag
    # that components.py sets when a starter card is clicked
    # Check if we should skip the option_menu (because a button was just clicked)

    # Just render the home content without the option_menu
    css_once()
    render_home_hero_and_stats()
    render_home_starters()

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
