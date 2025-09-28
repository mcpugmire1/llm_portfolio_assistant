# app_next.py — Next-gen UI (Home / Stories / Ask / About)
# - Clean, centered layout without sidebar
# - Pinecone-first (guarded) + local fallback search
# - Debounced “Ask MattGPT” with starter chips
# - Compact List view by default, Card view optional
# - Badges + strongest-metric summary

import os, re, time, textwrap, json
from typing import List, Optional
from urllib.parse import quote_plus

from ui.components import css_once, render_home_hero_and_stats, render_home_starters

# =========================
# UI — Home / Stories / Ask / About


def render_sources_chips(
    sources: list[dict],
    title: str = "Sources",
    *,
    stay_here: bool = False,
    key_prefix: str = "",
):
    """Render Sources as compact, 2-line chips.
    - stay_here=True: switch the active story + modes inline on Ask (no tab jump)
    - stay_here=False: legacy behavior (navigate to Explore Stories)
    """
    if not sources:
        return

    # Normalize + prune empties, but accept story_id as fallback and try to infer from title/client if missing
    items = []
    for s in sources:
        # prefer 'id', fall back to 'story_id' (common from LLM/backend)
        sid = str(s.get("id") or s.get("story_id") or "").strip()
        client = (s.get("client") or "").strip()
        title_txt = (s.get("title") or "").strip()
        # If no id was provided, try to infer from STORIES by title/client
        if not sid and (title_txt or client):
            cand = None
            low_title = title_txt.lower()
            low_client = client.lower()
            for x in STORIES:
                xt = (x.get("title") or "").strip().lower()
                xc = (x.get("client") or "").strip().lower()
                if (
                    low_title
                    and xt == low_title
                    and (not low_client or xc == low_client)
                ):
                    cand = x
                    break
            if cand:
                sid = str(cand.get("id") or "").strip()
        # Skip if we still don't have an id and no visible label
        if not sid and not (title_txt or client):
            continue
        # Keep the item even if id is still blank, so click can resolve by title/client
        items.append(
            {
                "id": sid or "",
                "client": client,
                "title": title_txt,
            }
        )
    if not items:
        return

    # tighter, non-<p> header + zero top gap container
    st.markdown(f"<div class='section-tight'>{title}</div>", unsafe_allow_html=True)
    st.markdown(
        "<div data-mpg-srcchips class='pill-container sources-tight sources-grid'>",
        unsafe_allow_html=True,
    )

    # Lay out chips in rows using Streamlit columns (3-up per row)
    per_row = 3
    container = st.container()
    batch: list[dict] = []

    def _chip_label(item: dict, idx: int) -> tuple[str, str]:
        sep = " \u2009— "
        base = (
            f"{item['client']}{sep}{item['title']}" if item["client"] else item["title"]
        )
        short = _shorten_middle(base, 72)
        safe_id = item.get("id") or _slug(base) or str(idx)
        _scores = st.session_state.get("__pc_last_ids__", {}) or {}
        sc = _scores.get(str(safe_id) or str(item.get("id") or ""))
        pct = f"{float(sc)*100:.0f}%" if isinstance(sc, (int, float)) else None
        label = f"{pct} Match • {short}" if pct else short
        return label, safe_id

    for i, s in enumerate(items, 1):
        batch.append(s)
        if len(batch) == per_row or i == len(items):
            cols = container.columns(len(batch))
            for col, item in zip(cols, batch):
                with col:
                    label, safe_id = _chip_label(item, i)
                    btn_key = f"{key_prefix}srcchip_{safe_id}"
                    if st.button(
                        label,
                        key=btn_key,
                        use_container_width=False,
                        help="Semantic relevance to your question (higher = stronger match)",
                    ):
                        st.session_state["active_story"] = item.get("id") or ""
                        st.session_state["active_story_title"] = item.get("title")
                        st.session_state["active_story_client"] = item.get("client")
                        st.session_state["show_ask_panel"] = True
                        
                        # ➜ ADD THIS (one-shot lock)
                        st.session_state["__ctx_locked__"] = True

                        if stay_here:
                            # resolve and pin the selected story context
                            target = None
                            sid_norm = (item.get("id") or "").strip()
                            if sid_norm:
                                target = next(
                                    (
                                        x
                                        for x in STORIES
                                        if str(x.get("id")) == str(sid_norm)
                                    ),
                                    None,
                                )
                            if not target:
                                tgt_title = (item.get("title") or "").strip().lower()
                                tgt_client = (item.get("client") or "").strip().lower()
                                if tgt_title:
                                    for x in STORIES:
                                        xt = (x.get("title") or "").strip().lower()
                                        xc = (x.get("client") or "").strip().lower()
                                        if xt == tgt_title and (
                                            not tgt_client or xc == tgt_client
                                        ):
                                            target = x
                                            break
                            if not target:
                                lr = st.session_state.get("last_results") or []
                                for x in lr:
                                    cand = (
                                        x.get("story") if isinstance(x, dict) else None
                                    )
                                    if not isinstance(cand, dict):
                                        cand = x if isinstance(x, dict) else None
                                    if not isinstance(cand, dict):
                                        continue
                                    xid = str(
                                        cand.get("id") or cand.get("story_id") or ""
                                    ).strip()
                                    xt = (cand.get("title") or "").strip().lower()
                                    xc = (cand.get("client") or "").strip().lower()
                                    if (sid_norm and xid and xid == sid_norm) or (
                                        (
                                            item.get("title")
                                            and xt
                                            == (item.get("title") or "").strip().lower()
                                        )
                                        and (
                                            not item.get("client")
                                            or xc
                                            == (item.get("client") or "")
                                            .strip()
                                            .lower()
                                        )
                                    ):
                                        target = cand
                                        break
                            if target:
                                st.session_state["active_story_obj"] = target
                                st.session_state["answer_modes"] = story_modes(target)
                                cur = st.session_state.get("answer_mode", "narrative")
                                st.session_state["answer_mode"] = (
                                    cur
                                    if cur in ("narrative", "key_points", "deep_dive")
                                    else "narrative"
                                )
                                st.session_state["last_sources"] = [
                                    {
                                        "id": target.get("id")
                                        or target.get("story_id"),
                                        "title": target.get("title"),
                                        "client": target.get("client"),
                                    }
                                ]
                            else:
                                st.session_state["last_sources"] = [
                                    {
                                        "id": item.get("id") or item.get("story_id"),
                                        "title": item.get("title"),
                                        "client": item.get("client"),
                                    }
                                ]
                        else:
                            st.session_state["active_tab"] = "Explore Stories"
                        st.rerun()
            batch = []

    st.markdown("</div>", unsafe_allow_html=True)


# --- Mock-style non-interactive source badges (stays on Ask) ---
def render_sources_badges(
    sources: list[dict], title: str = "Sources", key_prefix: str = "srcbad_"
):
    """Backward-compatible alias: render interactive chips and stay on Ask."""
    return render_sources_chips(
        sources, title=title, stay_here=True, key_prefix=key_prefix
    )


import pandas as pd
import streamlit as st


# Streamlit compatibility helper for bordered containers (older Streamlit lacks border kw)
def safe_container(*, border: bool = False):
    try:
        return st.container(border=border)
    except TypeError:
        return st.container()


ASSIST_AVATAR = "🤖"  # keep the retro robot
USER_AVATAR = "🗣️"  # or "🙋", "🧑", "👋", "👥", "🧑‍💻", etc.
# --- Shared config: prefer st.secrets, fallback to .env ---
import os
from dotenv import load_dotenv
import streamlit as st

# === DEBUG UTIL (safe to keep; no-op when DEBUG=False) ===
DEBUG = False


def dbg(*args):
    if DEBUG:
        try:
            st.sidebar.write("🧪", *args)
        except Exception:
            pass


load_dotenv()


def get_conf(key: str, default: str | None = None):
    try:
        v = st.secrets.get(key)
        if v is not None:
            return v
    except Exception:
        pass
    return os.getenv(key, default)


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

st.set_page_config(page_title="MattGPT — Matt's Story", page_icon="🤖", layout="wide")

# ensure external UI CSS is injected once (safe no-op if it’s empty)
css_once()

# ---- first-mount guard: let CSS finish applying, then paint once more ----
if not st.session_state.get("__first_mount_rerun__", False):
    st.session_state["__first_mount_rerun__"] = True
    st.rerun()
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


# --------- Simple, reliable state-driven navigation (DISABLED for now to avoid default_index errors) ---------
ENABLE_TOP_QUICK_NAV = (
    False  # keep buttons on Home instead; prevents accidental tab jumps & flicker
)
if ENABLE_TOP_QUICK_NAV and st.session_state.get("active_tab", "Home") == "Home":
    # Use option_menu only when explicitly enabled; must pass an integer default_index
    from streamlit_option_menu import option_menu  # safe repeat import

    prev = st.session_state.get("__top_sel__", "Explore Stories")
    def_idx = ["Explore Stories", "Ask MattGPT", "About Matt"].index(prev)

    with st.container():
        sel = option_menu(
            menu_title=None,
            options=["Explore Stories", "Ask MattGPT", "About Matt"],
            icons=["book", "chat-dots", "person"],
            default_index=def_idx,  # option_menu requires an int
            orientation="horizontal",
            styles={
                "container": {"padding": "0", "background": "transparent"},
                "icon": {"color": "inherit", "font-size": "1.0rem"},
                "nav-link": {
                    "font-size": "1rem",
                    "padding": "10px 16px",
                    "border-radius": "10px",
                    "color": "inherit",
                    "white-space": "nowrap",
                    "background-color": "transparent",
                    "font-weight": "600",
                    "border": "1px solid rgba(255,255,255,0.16)",
                    "margin-right": "18px",
                },
                "nav-link-selected": {
                    "font-size": "1rem",
                    "padding": "10px 16px",
                    "border-radius": "10px",
                    "color": "inherit",
                    "white-space": "nowrap",
                    "background-color": "transparent",
                    "font-weight": "600",
                    "border": "1px solid rgba(255,255,255,0.16)",
                },
            },
        )
        # Only navigate when user *changes* the selection
        if sel != prev:
            st.session_state["__top_sel__"] = sel
            goto(sel)


# Choose nav mode:
USE_SIDEBAR_NAV = True  # set False to use top button nav (classic look)

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

    st.stop()


# === Sidebar navigation (icon buttons; no radios, no flicker) ===
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
                # Reset Home’s first-mount guard so the Home page doesn’t immediately
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
                # Treat like a suggestion chip to use the same relaxed, intent-boosted flow
                st.session_state["__inject_user_turn__"] = q
                st.session_state["__ask_from_suggestion__"] = True
                st.session_state["__ask_force_answer__"] = True
                st.session_state["active_tab"] = "Ask MattGPT"
                st.rerun()
        st.divider()
# ------------------------------------------------------------

# --- Top nav (classic, ChatGPT‑ish pills) ---
if not USE_SIDEBAR_NAV:
    st.markdown(" ")
    current = st.session_state.get("active_tab", "Home")
    labels = [
        ("🏠 Home", "Home"),
        ("📚 Explore Stories", "Explore Stories"),
        ("💬 Ask MattGPT", "Ask MattGPT"),
        ("👤 About Matt", "About Matt"),
    ]
    cols = st.columns(len(labels), gap="medium")
    for i, (label, name) in enumerate(labels):
        with cols[i]:
            if st.button(
                label,
                use_container_width=True,
                key=f"topnav_{name}",
                disabled=(name == current),
            ):
                st.session_state["active_tab"] = name
                st.rerun()
    st.markdown("---")


# --- Audience derivation from Person (5Ps) ---
def _derive_personas(person: str | list | None) -> list[str]:
    """
    Map raw 5P 'Person' text to concise audience tags.
    Non-destructive: returns a small set of normalized labels.
    """
    if not person:
        return []

    # Accept list or string (some rows may already be arrays)
    if isinstance(person, list):
        raw = " ; ".join(str(x) for x in person if str(x).strip())
    else:
        raw = str(person)

    txt = raw.lower()

    # Keyword → label rules (order matters; keep this small & opinionated)
    rules = [
        (["cxo", "c-suite", "executive", "vp", "svp", "evp", "chief "], "Execs"),
        (
            ["product", "pm ", "pmm", "head of product", "product leader"],
            "Product Leaders",
        ),
        (
            ["engineering", "platform", "sre", "devops", "cto", "tech lead"],
            "Eng Leaders",
        ),
        (["data", "ml", "ai", "science", "model", "analytics"], "Data/AI"),
        (["security", "privacy", "compliance", "governance", "risk"], "Compliance"),
        (["operations", "ops", "contact center", "service"], "Operations"),
        (["sales", "marketing", "go-to-market", "g tm", "g2m"], "Go-To-Market"),
        (["finance", "treasury", "payments", "banking"], "Finance/Payments"),
        (["customer", "member", "patient", "end user"], "End Users"),
    ]

    out = set()
    for kws, label in rules:
        if any(k in txt for k in kws):
            out.add(label)

    # If nothing matched, try to create a reasonable fallback:
    # pull capitalized role tokens from the original (keeps noise low)
    if not out:
        # very light fallback: if text includes "lead", "manager", "director", map to leaders
        if any(k in txt for k in ["lead", "manager", "director"]):
            out.add("Leaders")
        else:
            out.add("Stakeholders")

    return sorted(out)


def F(s: dict, key: str, default: str | list | None = None):
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


def _format_narrative(s: dict) -> str:
    """1-paragraph, recruiter-friendly narrative from a single story."""
    title = s.get("title", "")
    client = s.get("client", "")
    domain = s.get("domain", "")
    goal = (s.get("why") or "").strip().rstrip(".")
    how = ", ".join((s.get("how") or [])[:2]).strip().rstrip(".")
    metric = strongest_metric_line(s)
    bits = []
    if title or client:
        bits.append(
            f"I led **{title}** at **{client}**"
            if title
            else f"I led work at **{client}**"
        )
    if domain:
        bits[-1] += f" in **{domain}**."
    if goal:
        bits.append(f"The aim was {goal.lower()}.")
    if how:
        bits.append(f"We focused on {how.lower()}.")
    if metric:
        bits.append(f"Impact: **{metric}**.")
    return " ".join(bits) or build_5p_summary(s, 280)


def _format_key_points(s: dict) -> str:
    """3–4 bullets: scope, approach, outcomes."""
    metric = strongest_metric_line(s)
    lines = []
    lines.append(f"- **Scope:** {s.get('title','')} — {s.get('client','')}".strip(" —"))
    top_how = (s.get("how") or [])[:2]
    if top_how:
        lines.append("- **Approach:** " + " / ".join(top_how))
    outs = s.get("what") or []
    if metric:
        lines.append(f"- **Outcome:** {metric}")
    elif outs:
        lines.append(f"- **Outcome:** {outs[0]}")
    dom = s.get("domain")
    if dom:
        lines.append(f"- **Domain:** {dom}")
    return "\n".join(lines)


def _format_deep_dive(s: dict) -> str:
    """Detail without saying STAR/5P explicitly: What was happening / Goal / What we did / Results."""
    st_blocks = s.get("star", {}) or {}
    situation = st_blocks.get("situation") or []
    task = st_blocks.get("task") or []
    action = st_blocks.get("action") or []
    result = st_blocks.get("result") or []
    parts = []
    if situation:
        parts.append(
            "**What was happening**\n" + "\n".join([f"- {x}" for x in situation])
        )
    if task:
        parts.append("**Goal**\n" + "\n".join([f"- {x}" for x in task]))
    if action:
        parts.append("**What we did**\n" + "\n".join([f"- {x}" for x in action]))
    if result:
        parts.append("**Results**\n" + "\n".join([f"- {x}" for x in result]))
    return "\n\n".join(parts) or build_5p_summary(s, 320)


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


def _safe_json(obj):
    try:
        # pinecone client may expose one of these:
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "dict"):  # pydantic v1
            return obj.dict()
    except Exception:
        pass
    import json

    try:
        return json.loads(json.dumps(obj, default=str))
    except Exception:
        return {"_raw": str(obj)}


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
W_PC = 0.6  # semantic (Pinecone vector match)
W_KW = 0.4  # keyword/token overlap

# Centralized retrieval pool size for semantic search / Pinecone
SEARCH_TOP_K = 30
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
    """Normalize JSONL records (Title‑cased keys) into the lowercase schema the UI expects.

    Changes:
    - NO fallback to a different filename: if the requested path doesn't exist, return [].
    - REQUIRE a stable `id`: if missing, skip the row (prevents mismatch with Pinecone vector IDs).
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
                raw = json.loads(line)
            except Exception as e:
                st.warning(f"JSON parse error at line {line_no}: {e}")
                continue

            # Enforce a stable ID so Pinecone hits can map back to STORIES
            raw_id = raw.get("id")
            if raw_id in (None, "", 0):
                skipped_no_id += 1
                continue
            sid = str(raw_id).strip()

            # Build normalized record
            title = (raw.get("Title") or "").strip() or "Untitled"
            client = (raw.get("Client") or "").strip() or "Unknown"
            role = raw.get("Role") or ""
            cat = raw.get("Category") or ""
            subcat = raw.get("Sub-category") or ""
            domain = " / ".join([x for x in [cat, subcat] if x]).strip()

            who = raw.get("Person") or ""
            where = raw.get("Place") or ""
            why = raw.get("Purpose") or ""

            # STAR/5P lists (accept strings or arrays)
            situation = _ensure_list(raw.get("Situation"))
            task = _ensure_list(raw.get("Task"))
            action = _ensure_list(raw.get("Action"))
            result = _ensure_list(raw.get("Result"))

            process = _ensure_list(raw.get("Process"))
            performance = _ensure_list(raw.get("Performance"))

            tags = _split_tags(raw.get("public_tags"))

            stories.append(
                {
                    "id": sid,
                    "title": title,
                    "client": client,
                    "role": role,
                    "domain": domain,
                    # Derive concise audience labels from 5P 'Person'
                    "personas": _derive_personas(
                        raw.get("Person") or raw.get("person")
                    ),
                    "who": who,
                    "where": where,
                    "why": why,
                    "how": process,  # map 5P Process → UI "how"
                    "what": performance,  # map 5P Performance → UI "what"
                    "star": {
                        "situation": situation,
                        "task": task,
                        "action": action,
                        "result": result,
                    },
                    "tags": tags,
                    "content": raw.get("content", ""),
                    "5PSummary": (raw.get("5PSummary") or "").strip(),
                }
            )

    if DEBUG:
        if skipped_no_id:
            st.caption(
                f"DEBUG • Loaded {len(stories)} stories from {p.name}; skipped {skipped_no_id} rows without an 'id' (kept Pinecone mapping stable)."
            )
        else:
            st.caption(f"DEBUG • Loaded {len(stories)} stories from {p.name}.")

    return stories


# Minimal demo stories (fallback)
DEMO_STORIES = [
    {
        "id": "rbc-payments",
        "title": "Global Payments Modernization",
        "client": "RBC",
        "role": "Product & Delivery Lead",
        "domain": "Payments / Treasury",
        "personas": ["Product Leaders", "Banking Stakeholders"],
        "who": "Corporate banking customers & operations teams",
        "where": "RBC – Commercial Banking",
        "why": "Increase straight-through processing and reduce settlement delays",
        "how": [
            "Introduced OKR-driven roadmapping",
            "Implemented event-driven architecture",
            "Scaled CI/CD across teams",
        ],
        "what": [
            "Reduced wire transfer delays by 30%",
            "Improved SLA adherence to 99.5%",
        ],
        "star": {
            "situation": [
                "Legacy payments flows caused reconciliation delays and operations pain across regions."
            ],
            "task": [
                "Define a modernization roadmap and deliver near-term wins while aligning stakeholders."
            ],
            "action": [
                "Introduced OKR-driven roadmap and prioritized high-impact flows",
                "Implemented event-driven services and hardened CI/CD",
            ],
            "result": [
                "30% fewer wire transfer delays",
                "SLA adherence improved to 99.5%",
                "Stakeholder satisfaction up measurably",
            ],
        },
        "tags": ["Payments", "OKRs", "Event-Driven"],
    },
    {
        "id": "kp-rai",
        "title": "Responsible AI Governance",
        "client": "Kaiser Permanente",
        "role": "AI Program Lead",
        "domain": "AI/ML / Governance",
        "personas": ["Product Leaders", "Data Science Leaders", "Compliance"],
        "who": "Clinical operations & compliance stakeholders",
        "where": "Healthcare (Fortune 100)",
        "why": "Protect patient privacy while enabling predictive care",
        "how": [
            "Risk taxonomy & model registry",
            "Human-in-the-loop review",
            "Policy gating in CI/CD",
        ],
        "what": [
            "Zero high-severity compliance incidents post-launch",
            "Audit time reduced by 40%",
        ],
        "star": {
            "situation": [
                "Multiple ML pilots lacked centralized governance and clear risk controls."
            ],
            "task": [
                "Stand up a Responsible AI program that satisfied privacy and audit requirements."
            ],
            "action": [
                "Built risk taxonomy and model registry",
                "Added human-in-the-loop reviews and policy gates in CI/CD",
            ],
            "result": [
                "Zero high-severity compliance incidents post-launch",
                "Audit prep time reduced by 40%",
            ],
        },
        "tags": ["Responsible AI", "Governance", "Privacy"],
    },
]

# After DEMO_STORIES is defined:
STORIES = load_star_stories(DATA_FILE) or DEMO_STORIES

# --- FAST DEBUG: data source + counts ---
# Stories are already loaded earlier:
# STORIES = load_star_stories(DATA_FILE) or DEMO_STORIES

_loaded_from = (
    "JSONL" if (os.path.exists(DATA_FILE) and load_star_stories(DATA_FILE)) else "DEMO"
)
# dbg(f"[data] Source={_loaded_from}  file={DATA_FILE!r}  stories={len(STORIES)}")
if not STORIES:
    st.error("No stories loaded. Check STORIES_JSONL path or JSONL format.")


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


def show_persona_tags(s: dict):
    """Simple alias for personas/tags badges for a single story (non-interactive)."""
    return render_badges_static(s)


def show_sources(
    srcs: list[dict],
    *,
    interactive: bool = False,
    key_prefix: str = "src_",
    title: str = "Sources",
):
    """Render Sources row using a single call site.
    - interactive=True  -> clickable chips (Ask)
    - interactive=False -> static badges (Explore/Details)
    """
    if not srcs:
        return
    if interactive:
        return render_sources_chips(
            srcs, title=title, stay_here=True, key_prefix=key_prefix
        )
    return render_sources_badges_static(srcs, title=title, key_prefix=key_prefix)


METRIC_RX = re.compile(
    r"(\b\d{1,3}\s?%|\$\s?\d[\d,\.]*\b|\b\d+x\b|\b\d+(?:\.\d+)?\s?(pts|pp|bps)\b)", re.I
)
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


def render_answer_card_clean_pills(
    primary_story: dict, modes: dict, answer_mode_key: str = "answer_mode"
):
    """
    Render a single card with Title + (Narrative|Key Points|Deep Dive) pills + body + sources,
    visually consistent with mock_ask_hybrid.py. Uses existing modes dict from story_modes().
    """
    # # If the user clicked a Source chip or "Ask about this", we set __ctx_locked__.
# Only override the primary story when that lock is present.
    if st.session_state.get("__ctx_locked__"):
        _ctx_story = get_context_story()
        if _ctx_story and str(_ctx_story.get("id")) != str(primary_story.get("id")):
            primary_story = _ctx_story
            st.session_state["active_story_obj"] = _ctx_story
            try:
                modes = story_modes(primary_story)
            except Exception:
                pass
    title = field_value(primary_story, "title", "")
    one_liner_html = (
        f"<div class='fivep-quote fivep-unclamped'>{build_5p_summary(primary_story, 9999)}</div>"
        if primary_story
        else ""
    )
    client = field_value(primary_story, "client", "")
    role = field_value(primary_story, "role", "")
    domain = field_value(primary_story, "domain", "")
    bits = [b for b in [client, role, domain] if b]
    subtitle_html = f"<div class='meta-block'>{' • '.join(bits)}</div>" if bits else ""

    st.markdown(
        "<div class='card'>"
        f"<div class='h1'>{title}</div>"
        f"{one_liner_html}"
        f"{subtitle_html}"
        "</div>",
        unsafe_allow_html=True,
    )

    # Pills control (same labels as mock; drive the app's 'answer_mode')
    labels = [
        ("narrative", "Narrative"),
        ("key_points", "Key Points"),
        ("deep_dive", "Deep Dive"),
    ]
    current = st.session_state.get(answer_mode_key, "narrative")

    # If your Streamlit supports segmented control:
    if hasattr(st, "segmented_control"):
        label_map = {b: a for a, b in labels}
        default_label = next((b for a, b in labels if a == current), "Narrative")
        chosen = st.segmented_control(
            "",
            [b for _, b in labels],
            selection_mode="single",
            default=default_label,
            key=f"seg_{answer_mode_key}",
        )
        new_mode = label_map.get(chosen, "narrative")
        if new_mode != current:
            st.session_state[answer_mode_key] = new_mode
            st.rerun()
    else:
        # Left-aligned pill row (no Streamlit columns => no centering/flex bugs)
        st.markdown(
            f'<div class="pill-container" data-mode="{current}">',
            unsafe_allow_html=True,
        )
        for key, text in labels:
            class_name = {
                "narrative": "pill-narrative",
                "key_points": "pill-keypoints",
                "deep_dive": "pill-deepdive",
            }[key]
            st.markdown(f'<div class="{class_name}">', unsafe_allow_html=True)
            if st.button(text, key=f"pill_clean_{key}", disabled=(current == key)):
                st.session_state[answer_mode_key] = key
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Divider + Body
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    body_md = modes.get(st.session_state.get(answer_mode_key, "narrative"), "")
    if body_md:
        st.markdown(body_md)
    else:
        st.markdown("_No content available for this view._")

    # --- Sources row (interactive) ---
    # Prefer last_sources from session if present; otherwise build a minimal list from the current story + related
    _srcs = st.session_state.get("last_sources") or []
    if not _srcs and primary_story:
        _srcs = [
            {
                "id": primary_story.get("id"),
                "title": primary_story.get("title"),
                "client": primary_story.get("client"),
            }
        ]
        try:
            for r in _related_stories(primary_story, max_items=2):
                _srcs.append(
                    {
                        "id": r.get("id"),
                        "title": r.get("title"),
                        "client": r.get("client"),
                    }
                )
        except Exception:
            pass
    if _srcs:
        show_sources(_srcs, interactive=True, key_prefix="asksrc_", title="Sources")


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


def render_sources_badges_static(
    sources: list[dict], title: str = "Sources", key_prefix: str = "srcbad_"
):
    """Render non-interactive mock-style badges under a small 'Sources' header.
    This avoids nested layout/columns and matches the mock_ask_hybrid DOM exactly.
    """
    if not sources:
        return

    # Normalize + prune empties
    items = []
    for s in sources:
        sid = str(s.get("id") or s.get("story_id") or "").strip()
        client = (s.get("client") or "").strip()
        title_txt = (s.get("title") or "").strip()
        if not (sid or client or title_txt):
            continue
        items.append({"id": sid, "client": client, "title": title_txt})
    if not items:
        return

    def _pick_icon(label: str) -> str:
        low = label.lower()
        if any(w in low for w in ["payment", "treasury", "bank"]):
            return "bi-bank"
        if any(w in low for w in ["health", "care", "patient", "kaiser"]):
            return "bi-hospital"
        if any(w in low for w in ["cloud", "kubernetes", "microservice"]):
            return "bi-cloud"
        if any(w in low for w in ["ai", "ml", "model", "genai", "rai"]):
            return "bi-cpu"
        return "bi-journal-text"

    # Tight section header (no extra paragraph margins)
    st.markdown(f"<div class='section-tight'>{title}</div>", unsafe_allow_html=True)

    chips_html = []
    _scores = st.session_state.get("__pc_last_ids__", {}) or {}
    for s in items:
        label_full = f"{s['client']} — {s['title']}" if s['client'] else s['title']
        _score_key = str(s.get("id") or "")
        sc = _scores.get(_score_key)
        pct = f"{float(sc)*100:.0f}%" if isinstance(sc, (int, float)) else None

        text = _shorten_middle(label_full, 96)
        if pct:
            text = f"{pct} Match • {text}"

        # Static badge (no icon) to match the mock capsule style
        chips_html.append(
            f"<span class='badge' title='Semantic relevance'>{text}</span>"
        )

    st.markdown(
        f"<div class='badge-row'>{''.join(chips_html)}</div>", unsafe_allow_html=True
    )


# --- Prefer external UI renderers when available; fall back to locals ---
# In DEBUG, always use the local renderers to make behavior deterministic.
if not DEBUG:
    _ext_chips = globals().get("_ext_render_sources_chips")
    if callable(_ext_chips):
        render_sources_chips = _ext_chips  # override safely

    _ext_badges = globals().get("_ext_render_sources_badges_static")
    if callable(_ext_badges):
        render_sources_badges_static = _ext_badges  # override safely

# Optional: tiny debug note to confirm which renderer is active
try:
    _which_src = (
        "external"
        if getattr(render_sources_chips, "__module__", "").startswith("ui.components")
        else "local"
    )
    # st.caption(f"DEBUG • Sources renderer: {_which_src}")
except Exception:
    pass


def render_list(items: Optional[List[str]]):
    for x in items or []:
        st.write(f"- {x}")


def render_outcomes(items: Optional[List[str]]):
    for line in items or []:
        out = line
        for m in METRIC_RX.finditer(line or ""):
            token = m.group(0)
            out = out.replace(token, f"**{token}**")
        st.write(f"- {out}")


def _extract_metric_value(text: str):
    if not text:
        return None
    best = None
    for m in METRIC_RX.finditer(text):
        tok = m.group(0)
        if "%" in tok:
            try:
                num = float(tok.replace("%", "").strip())
            except Exception:
                num = 0.0
            score = 1000 + num
        else:
            digits = "".join([c for c in tok if c.isdigit() or c == "."])
            try:
                num = float(digits)
            except Exception:
                num = 0.0
            score = num
        item = (score, text)
        if best is None or item[0] > best[0]:
            best = item
    return best


def strongest_metric_line(s: dict) -> Optional[str]:
    candidates = []
    for line in s.get("what") or []:
        v = _extract_metric_value(line or "")
        if v:
            candidates.append(v)
    for line in s.get("star", {}).get("result") or []:
        v = _extract_metric_value(line or "")
        if v:
            candidates.append(v)
    if not candidates:
        return None
    return max(candidates, key=lambda t: t[0])[1]


def build_5p_summary(s: dict, max_chars: int = 220) -> str:
    """
    Neutral, recruiter-friendly one-liner:
    Goal: <why>. Approach: <top 1-2 how>. Outcome: <strongest metric>.
    Uses curated 5PSummary if present; otherwise composes a clean line.
    """
    curated = (s.get("5PSummary") or s.get("5p_summary") or "").strip()
    if curated:
        # Keep curated text, but trim if super long for list views
        return (
            curated if len(curated) <= max_chars else (curated[: max_chars - 1] + "…")
        )

    goal = (s.get("why") or "").strip().rstrip(".")
    approach = ", ".join((s.get("how") or [])[:2]).strip().rstrip(".")
    metric_line = strongest_metric_line(s)
    outcome = (metric_line or "").strip().rstrip(".")

    parts = []
    if goal:
        parts.append(f"**Goal:** {goal}.")
    if approach:
        parts.append(f"**Approach:** {approach}.")
    if outcome:
        parts.append(f"**Outcome:** {outcome}.")

    text = " ".join(parts).strip()
    if not text:
        # last resort, try WHAT list
        what = "; ".join(s.get("what", [])[:2])
        text = what or "Impact-focused delivery across stakeholders."

    # Clamp for compact list cells
    return text if len(text) <= max_chars else (text[: max_chars - 1] + "…")


# --- Nonsense rules (JSONL) + known vocab -------------------
import csv
from datetime import datetime

_NONSENSE_RULES = []


def _load_nonsense_rules(path: str = "nonsense_filters.jsonl"):
    rules = []
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rules.append(json.loads(line))
                    except Exception as e:
                        dbg(f"[rules] JSON error on line {i}: {e}")
        else:
            dbg(f"[rules] file not found: {path}")
    except Exception as e:
        dbg(f"[rules] load exception: {e}")
    dbg(f"[rules] loaded: {len(rules)}")
    if rules[:2]:
        dbg("[rules] first items →", rules[:2])
    return rules


def is_nonsense(query: str) -> Optional[str]:
    """Return category string if query matches a nonsense rule, else None."""
    global _NONSENSE_RULES
    if not _NONSENSE_RULES:
        _NONSENSE_RULES = _load_nonsense_rules()
    q = (query or "").strip()
    if not q:
        return None
    for r in _NONSENSE_RULES:
        pat = r.get("pattern")
        if not pat:
            continue
        try:
            if re.search(pat, q, re.IGNORECASE):
                return r.get("category") or "other"
        except re.error:
            # bad regex in file — skip
            continue
    return None


# Known vocab built from stories (call once after STORIES is loaded)
_KNOWN_VOCAB = set()

# Very small stopword set to avoid false overlap on generic words like 'how'
_STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "if",
    "then",
    "else",
    "of",
    "in",
    "on",
    "for",
    "to",
    "from",
    "by",
    "with",
    "about",
    "how",
    "what",
    "why",
    "when",
    "where",
    "who",
    "whom",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "do",
    "does",
    "did",
    "done",
    "much",
    "at",
    "as",
    "into",
    "over",
    "under",
}


def build_known_vocab(stories: list[dict]):
    vocab = set()
    for s in stories:
        for field in ["title", "client", "role", "domain"]:
            txt = (s.get(field) or "").lower()
            vocab.update(re.split(r"[^\w]+", txt))
        for t in s.get("tags") or []:
            vocab.update(re.split(r"[^\w]+", str(t).lower()))
    # prune tiny tokens
    return {w for w in vocab if len(w) >= 3}


def token_overlap_ratio(query: str, vocab: set[str]) -> float:
    toks = [
        t
        for t in re.split(r"[^\w]+", (query or "").lower())
        if len(t) >= 3 and t not in _STOPWORDS
    ]
    if not toks:
        return 0.0
    hits = sum(1 for t in toks if t in vocab)
    return hits / max(1, len(set(toks)))


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


# --- Static badges (personas + tags) — mock-style row -----------------------


def render_badges_static(s: dict):
    """Render a single flowing row of small badges for personas + tags.
    Matches the mock badge styling already defined in CSS (.badge-row, .badge).
    Safe no-op if nothing to show.
    """
    try:
        personas = s.get("personas") or []
        tags = s.get("tags") or []
    except Exception:
        personas, tags = [], []

    # Normalize to strings and prune empties
    personas = [str(p).strip() for p in personas if str(p).strip()]
    tags = [str(t).strip() for t in tags if str(t).strip()]

    if not personas and not tags:
        return

    chips = []

    # Personas first
    for p in personas:
        dot = _dot_for(p)
        chips.append(f"<span class='badge' title='Persona'>{dot} {p}</span>")

    # Then tags
    for t in tags:
        dot = _dot_for(t)
        chips.append(f"<span class='badge' title='Tag'>{dot} {t}</span>")

    html = "".join(chips)
    st.markdown(f"<div class='badge-row'>{html}</div>", unsafe_allow_html=True)


def story_card(s, idx=0, show_ask_cta=True):
    st.markdown('<div class="story-block">', unsafe_allow_html=True)
    with safe_container(border=True):
        st.markdown(
            f"<div class='story-title'>{field_value(s,'title','')}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="fivep-quote fivep-unclamped">{build_5p_summary(s, 999)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(_matched_caption(s.get("id", "")))
        st.markdown(
            f'<div class="meta-block">{field_value(s,"client","")} • {field_value(s,"role","")} • {field_value(s,"domain","")}</div>',
            unsafe_allow_html=True,
        )
        show_persona_tags(s)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<span class="field-label">Who</span>', unsafe_allow_html=True)
            st.write(s.get("who", "—"))
            st.markdown('<span class="field-label">Why</span>', unsafe_allow_html=True)
            st.write(s.get("why", "—"))
        with c2:
            st.markdown(
                '<span class="field-label">Where</span>', unsafe_allow_html=True
            )
            st.write(s.get("where", "—"))
            st.markdown(
                '<span class="field-label">How (Approach)</span>',
                unsafe_allow_html=True,
            )
            render_list(s.get("how", []))

        st.markdown(
            '<span class="field-label">What (Outcomes)</span>', unsafe_allow_html=True
        )
        render_outcomes(s.get("what", []))

        row_left, row_right = st.columns([3, 1])
        details_key = f"details_open__{s.get('id','x')}"
        is_open = st.session_state.get(details_key, False)

        with row_left:
            label = ("▾ " if is_open else "▸ ") + "See how it unfolded"
            if st.button(label, key=f"toggle_details_{s.get('id','x')}_{idx}"):
                st.session_state[details_key] = not is_open
                st.rerun()
            if st.session_state.get(details_key):
                # --- Unified pills renderer (mock_ask_hybrid style) ---
                with safe_container(border=True):
                    mode_key = f"__detail_mode__{s.get('id','x')}"
                    st.session_state.setdefault(mode_key, "narrative")
                    render_answer_card_clean_pills(
                        s, story_modes(s), answer_mode_key=mode_key
                    )

                # Separator + Related
                rel = _related_stories(s, max_items=3)
                if rel:
                    st.markdown("---")
                    st.caption("Other projects you might want to reference")
                    for r in rel:
                        label = f"🔎 {r.get('title','')} — {r.get('client','')}"
                        if st.button(label, key=f"rel_{r.get('id','x')}"):
                            st.session_state["active_story"] = r.get("id")
                            st.session_state["show_ask_panel"] = True
                            st.rerun()
                # --- Sources badges (STATIC, non-interactive in details) ---
                srcs = [
                    {
                        "id": s.get("id"),
                        "title": s.get("title"),
                        "client": s.get("client"),
                    }
                ]
                try:
                    for r in _related_stories(s, max_items=2):
                        srcs.append(
                            {
                                "id": r.get("id"),
                                "title": r.get("title"),
                                "client": r.get("client"),
                            }
                        )
                except Exception:
                    pass
                show_sources(
                    srcs, interactive=False, key_prefix="detailsrc_", title="Sources"
                )

        with row_right:
            if show_ask_cta:
                if st.button(
                    "Ask MattGPT about this",
                    key=f"ask_{s.get('id','x')}_{idx}",
                    help="Switches to Ask tab with this story preloaded so you can ask follow-ups",
                ):
                    on_ask_this_story(s)

    st.markdown("</div>", unsafe_allow_html=True)


def compact_row(s, idx=0, show_ask_cta=True):
    st.markdown('<div class="story-block">', unsafe_allow_html=True)
    with safe_container(border=True):
        st.markdown('<div class="compact-row">', unsafe_allow_html=True)

        # LEFT
        st.markdown('<div class="compact-left">', unsafe_allow_html=True)
        # Title prominent (unified style)
        st.markdown(
            f"<div class='story-title'>{field_value(s,'title','')}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='fivep-quote fivep-compact'><span class='fivep-lines-3'>{build_5p_summary(s,9999)}</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="meta-block">{field_value(s,"client","")} • {field_value(s,"role","")} • {field_value(s,"domain","")}</div>',
            unsafe_allow_html=True,
        )
        show_persona_tags(s)

        # Pinecone reason + score (with 5P fallback if snippet missing)
        st.caption(_matched_caption(s.get("id", "")))
        # --- Sources badges (STATIC, non-interactive in compact row) ---
        srcs = [
            {
                "id": s.get("id"),
                "title": s.get("title"),
                "client": s.get("client"),
            }
        ]
        try:
            for r in _related_stories(s, max_items=2):
                srcs.append(
                    {
                        "id": r.get("id"),
                        "title": r.get("title"),
                        "client": r.get("client"),
                    }
                )
        except Exception:
            pass
        show_sources(srcs, interactive=False, key_prefix="compactsrc_", title="Sources")

        st.markdown("</div>", unsafe_allow_html=True)  # /compact-left

        # RIGHT
        st.markdown('<div class="compact-right">', unsafe_allow_html=True)
        if show_ask_cta:
            if st.button(
                "Ask MattGPT",
                key=f"mock_ask_{s['id']}_{idx}",
                help="Switches to Ask tab with this story preloaded so you can ask follow-ups",
            ):
                on_ask_this_story(s)
        st.markdown("</div>", unsafe_allow_html=True)  # /compact-right

        st.markdown("</div>", unsafe_allow_html=True)  # /compact-row
    st.markdown("</div>", unsafe_allow_html=True)  # /story-block


def get_context_story():
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


def _choose_story_for_ask(top_story: dict | None) -> dict | None:
    """Prefer Pinecone (top_story) unless a one-shot context lock is set."""
    if st.session_state.get("__ctx_locked__"):
        ctx = get_context_story()
        return ctx or top_story
    return top_story


def build_facets(stories):
    clients = sorted({s.get("client", "") for s in stories if s.get("client")})
    domains = sorted({s.get("domain", "") for s in stories if s.get("domain")})
    roles = sorted({s.get("role", "") for s in stories if s.get("role")})
    tags = sorted({t for s in stories for t in (s.get("tags") or [])})
    personas = sorted({p for s in stories for p in (s.get("personas") or [])})
    return clients, domains, roles, tags, personas


def story_has_metric(s):
    for line in s.get("what") or []:
        if METRIC_RX.search(line or ""):
            return True
    for line in s.get("star", {}).get("result") or []:
        if METRIC_RX.search(line or ""):
            return True
    return False


def matches_filters(s, F=None):
    # Normalize incoming filters (Ask may pass `{}` intentionally)
    if F is None:
        F = st.session_state.get("filters", {}) or {}
    personas = F.get("personas", []) or []
    clients = F.get("clients", []) or []
    domains = F.get("domains", []) or []
    roles = F.get("roles", []) or []
    tags = F.get("tags", []) or []
    has_metric = bool(F.get("has_metric", False))
    if personas and not (set(personas) & set(s.get("personas", []))):
        return False
    if clients and s.get("client") not in clients:
        return False
    if domains and s.get("domain") not in domains:
        return False
    if roles and s.get("role") not in roles:
        return False
    if tags:
        want = {str(t).strip().lower() for t in tags}
        have = {str(t).strip().lower() for t in (s.get("tags", []) or [])}
        if not (want & have):
            return False
    if has_metric and not story_has_metric(s):
        return False
    # Keyword query: token-based match (all words must be present)
    q_raw = (F.get("q") or "").strip()
    if q_raw:
        # Try token containment first (robust to order and punctuation)
        q_toks = _tokenize(q_raw)
        hay_joined = " ".join(
            [
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
            ]
        )
        if q_toks:
            hay_toks = set(_tokenize(hay_joined))
            if not all(t in hay_toks for t in q_toks):
                return False
        else:
            # Very short or non-word input: fall back to substring check
            if q_raw.lower() not in hay_joined.lower():
                return False
    return True


# =========================
# Embedding + Pinecone query
# =========================

# Try to use the same model as build_custom_embeddings.py (all-MiniLM-L6-v2, 384-dim)
_EMBEDDER = None


def _get_embedder():
    global _EMBEDDER
    if _EMBEDDER is not None:
        return _EMBEDDER
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore

        _EMBEDDER = SentenceTransformer("all-MiniLM-L6-v2")
        if DEBUG:
            print(
                "DEBUG Embeddings: using SentenceTransformer(all-MiniLM-L6-v2) with normalize_embeddings=True"
            )
    except Exception as e:
        _EMBEDDER = None
        print(
            f"WARNING: sentence-transformers not available ({e}); falling back to stub embedder (low quality)"
        )
    return _EMBEDDER


# --- Hybrid retrieval helpers (no hard-coding) ---
_WORD_RX = re.compile(r"[A-Za-z0-9+#\-_.]+")


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _WORD_RX.findall(text or "") if len(t) >= 3]


def _keyword_score_for_story(s: dict, query: str) -> float:
    """
    Lightweight BM25-ish overlap using title/client/domain/tags + curated 5P one-liner.
    Returns 0..1 (normalized by unique query tokens).
    """
    q_toks = set(_tokenize(query))
    if not q_toks:
        return 0.0
    hay_parts = [
        s.get("title", ""),
        s.get("client", ""),
        s.get("role", ""),
        s.get("domain", ""),
        " ".join(s.get("tags", []) or []),
        build_5p_summary(s, 400),
        " ".join(s.get("how", []) or []),
        " ".join(s.get("what", []) or []),
    ]
    hay = " ".join(hay_parts)
    h_toks = set(_tokenize(hay))
    hits = q_toks & h_toks
    # soft weighting: title/domain twice
    title_dom = " ".join([s.get("title", ""), s.get("domain", "")])
    td_hits = q_toks & set(_tokenize(title_dom))
    score = len(hits) + len(td_hits)  # double-count td_hits
    return min(1.0, score / max(1, len(q_toks) * 2))


def _hybrid_score(
    pc_score: float, kw_score: float, w_pc: float = W_PC, w_kw: float = W_KW
):
    """
    Blend Pinecone similarity and keyword overlap into one score.
    Args:
        pc_score: float similarity from Pinecone (0..1+ depending on metric)
        kw_score: float keyword/token overlap helper (0..1)
    """
    try:
        pc = float(pc_score or 0.0)
    except Exception:
        pc = 0.0
    try:
        kw = float(kw_score or 0.0)
    except Exception:
        kw = 0.0

    blended = (pc * float(w_pc)) + (kw * float(w_kw))

    return blended


def _embed(text: str) -> List[float]:
    """
    Query-time embeddings that MATCH the build script:
    - Model: all-MiniLM-L6-v2 (384-dim)
    - Normalization: normalize_embeddings=True
    Falls back to the old stub only if sentence-transformers is unavailable.
    """
    model = _get_embedder()
    if model is not None:
        try:
            # sentence-transformers returns a numpy array; ensure list[float]
            v = model.encode(text or "", normalize_embeddings=True)
            return [float(x) for x in (v.tolist() if hasattr(v, "tolist") else list(v))]
        except Exception as e:
            print(f"WARNING: MiniLM encode failed ({e}); using stub embedding")

    # Fallback: deterministic stub (keeps app running, but scores will be poor)
    import math

    vec = [0.0] * _DEF_DIM
    if not text:
        return vec
    for i, ch in enumerate(text.encode("utf-8")):
        vec[i % _DEF_DIM] += (ch % 13) / 13.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _extract_match_fields(m) -> tuple[str, float, dict]:
    """
    Normalize a Pinecone match object or dict into (sid, score, metadata).
    Returns (None, 0.0, {}) if fields are missing.
    """
    try:
        if isinstance(m, dict):
            meta = m.get("metadata") or {}
            sid = meta.get("id") or m.get("id")
            score = float(m.get("score") or 0.0)
        else:
            meta = getattr(m, "metadata", None) or {}
            sid = meta.get("id") or getattr(m, "id", None)
            score = float(getattr(m, "score", 0.0) or 0.0)
    except Exception:
        return None, 0.0, {}
    return sid, score, meta


def pinecone_semantic_search(
    query: str, filters: dict, top_k: int = SEARCH_TOP_K
) -> Optional[List[dict]]:
    idx = _init_pinecone()
    if not idx or not query:
        if DEBUG:
            print(
                f"DEBUG Pinecone: skipped (idx={'present' if idx else 'none'}, query_len={len(query or '')})"
            )
        return None

    # Build filter for Pinecone
    pc_filter = {}
    if filters.get("domains"):
        pc_filter["domain"] = {"$in": filters["domains"]}
    if filters.get("clients"):
        pc_filter["client"] = {"$in": filters["clients"]}

    try:
        qvec = _embed(query)
        if DEBUG:
            print(
                f"DEBUG Embeddings: qvec_dim={len(qvec)}  model=MiniLM({'yes' if _get_embedder() else 'stub'})"
            )
            print(
                f"DEBUG Pinecone query → index={_PINECONE_INDEX or PINECONE_INDEX_NAME}, namespace={PINECONE_NAMESPACE}"
            )

        res = idx.query(
            vector=qvec,
            top_k=top_k,
            include_metadata=True,
            namespace=PINECONE_NAMESPACE,
            filter=pc_filter or None,
        )

        matches = getattr(res, "matches", []) or []

        # --- DEBUG: snapshot Pinecone info to session (compact) ---
        if DEBUG:
            try:
                preview = []
                for m in matches[:8]:
                    sid, score, meta = _extract_match_fields(m)
                    found = any(str(s.get("id")) == str(sid) for s in STORIES)
                    title = (meta or {}).get("title") or ""
                    client = (meta or {}).get("client") or ""
                    if title and client:
                        title = f"{client} — {title}"
                    if len(title) > 72:
                        title = title[:69] + "…"
                    preview.append(
                        {
                            "id": str(sid or ""),
                            "score": float(score or 0.0),
                            "title": title,
                            "in_STORIES": bool(found),
                        }
                    )

                try:
                    raw_stats = idx.describe_index_stats()
                except Exception:
                    raw_stats = {}
                stats_compact = _summarize_index_stats(_safe_json(raw_stats))

                st.session_state["__pc_debug__"] = {
                    "index": _PINECONE_INDEX or PINECONE_INDEX_NAME,
                    "namespace": PINECONE_NAMESPACE or "",
                    "match_count": len(matches),
                    "preview": preview,
                    "weights": {"W_PC": W_PC, "W_KW": W_KW},
                    "min_sim": PINECONE_MIN_SIM,
                    "stats": stats_compact,
                }
            except Exception as e:
                print("DEBUG: Pinecone snapshot error:", e)
        # --- end DEBUG snapshot ---

        hits = []
        st.session_state["__pc_last_ids__"].clear()
        st.session_state["__pc_snippets__"].clear()

        for m in matches:
            sid, score, meta = _extract_match_fields(m)
            if not sid:
                continue

            story = next((s for s in STORIES if str(s.get("id")) == str(sid)), None)
            if not story:
                continue

            snip = meta.get("summary") or meta.get("snippet") or ""
            if snip:
                st.session_state["__pc_snippets__"][str(sid)] = snip
            st.session_state["__pc_last_ids__"][str(sid)] = score

            kw = _keyword_score_for_story(story, query)
            blended = _hybrid_score(score, kw)

            if DEBUG:
                try:
                    title_dbg = (story.get("title") or "")[:60]
                    client_dbg = story.get("client") or ""
                    print(
                        f"DEBUG Hit: id={sid} pc={score:.3f} kw={kw:.3f} blend={blended:.3f}  [{client_dbg}] {title_dbg}"
                    )
                except Exception:
                    pass

            hits.append(
                {
                    "story": story,
                    "pc_score": score,
                    "kw_score": kw,
                    "score": blended,
                    "snippet": snip,
                }
            )

        st.session_state["last_results"] = hits
        st.session_state["last_sources"] = [
            {
                "id": h["story"].get("id"),
                "title": h["story"].get("title"),
                "client": h["story"].get("client"),
            }
            for h in hits[:5]
        ]

        hits.sort(key=lambda h: h.get("score", 0.0), reverse=True)

        strong = [
            h for h in hits if (h.get("pc_score", 0.0) or 0.0) >= PINECONE_MIN_SIM
        ]
        if strong:
            st.session_state["__pc_suppressed__"] = False
            return strong
        st.session_state["__pc_suppressed__"] = True
        return hits[:3]

    except Exception as e:
        if DEBUG:
            print(f"DEBUG Pinecone query error: {e}")
        return None


def semantic_search(
    query: str,
    filters: dict,
    *,
    enforce_overlap: bool = False,
    min_overlap: float = 0.0,
    top_k: int = SEARCH_TOP_K,
):
    """
    Pinecone-first semantic retrieval with gentle gating; strict UI filters applied after.
    Falls back to local keyword filtering if Pinecone returns nothing.
    Persists session state needed for chips/badges and transparency UI.
    """
    q = (query or "").strip()

    # 1) Always try Pinecone first
    hits = pinecone_semantic_search(q, filters, top_k=top_k) or []
    st.session_state["__pc_suppressed__"] = False

    # 2) If Pinecone gave us candidates, keep those crossing the raw PC gate
    if hits:
        # Raw Pinecone gate; 'score' is blended, 'pc_score' is raw vector sim
        raw_gate = float(globals().get("PINECONE_MIN_SIM", 0.15))
        confident = [h for h in hits if (h.get("pc_score", 0.0) or 0.0) >= raw_gate]

        # If nothing crossed, mark suppressed but still carry a small set forward
        if not confident:
            st.session_state["__pc_suppressed__"] = True
            confident = hits[:3]  # gentle fallback already handled inside pinecone fn

        # Persist per-story Pinecone info for chips/captions (use raw PC % in chips)
        try:
            st.session_state["__pc_last_ids__"] = {
                h["story"]["id"]: float(h.get("pc_score", h.get("score", 0.0)) or 0.0)
                for h in confident
            }
            st.session_state["__pc_snippets__"] = {
                h["story"]["id"]: (h.get("snippet") or build_5p_summary(h["story"]))
                for h in confident
            }
            st.session_state["__last_ranked_sources__"] = [
                h["story"]["id"] for h in confident
            ]
            st.session_state["__dbg_pc_hits"] = len(hits)
            # Also keep a compact top-5 for the Sources row if caller hasn’t set it
            st.session_state.setdefault(
                "last_sources",
                [
                    {
                        "id": h["story"]["id"],
                        "title": h["story"]["title"],
                        "client": h["story"].get("client", ""),
                    }
                    for h in confident[:5]
                ],
            )
        except Exception:
            pass

        # 3) Apply strict UI filters after retrieval
        filtered = [
            h["story"] for h in confident if matches_filters(h["story"], filters)
        ]
        if filtered:
            return filtered

        # If UI filters eliminate everything, return the confident set’s stories
        return [h["story"] for h in confident]

    # 4) If Pinecone returned nothing, optionally enforce overlap, else local fallback
    if enforce_overlap:
        ov = token_overlap_ratio(q, _KNOWN_VOCAB)
        if ov < float(min_overlap or 0.0) and not st.session_state.get(
            "__ask_from_suggestion__"
        ):
            # No semantic hits and below overlap bar → empty (caller may show banner)
            st.session_state["__dbg_pc_hits"] = 0
            st.session_state["__pc_last_ids__"].clear()
            st.session_state["__pc_snippets__"].clear()
            return []

    # Local keyword fallback (keeps app responsive during indexing issues)
    local = [s for s in STORIES if matches_filters(s, filters)]
    st.session_state["__dbg_pc_hits"] = 0
    st.session_state["__pc_last_ids__"].clear()
    st.session_state["__pc_snippets__"].clear()
    st.session_state["__last_ranked_sources__"] = [s["id"] for s in local[:10]]
    return local


# --- Compatibility shim: legacy callers expect `retrieve_stories(query, top_k)` ---
def retrieve_stories(
    query: str, top_k: int = SEARCH_TOP_K, *, filters: dict | None = None
):
    """
    Thin wrapper around semantic_search to maintain backwards compatibility with older code.
    - Uses current sidebar filters from session_state unless an explicit `filters` dict is passed.
    - Forces the search keyword to `query` for this call only.
    - Returns up to `top_k` results in the same story dict shape used across the app.
    """
    # Start from current filters or a safe default
    F = dict(
        filters
        or st.session_state.get(
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
    )

    # Override the free-text query for this call
    F["q"] = (query or "").strip()

    # Delegate to the Pinecone-first search with local fallback
    results = semantic_search(F["q"], F) or []

    # Limit to top_k results
    return results[: max(1, int(top_k))]


# =========================
# Ask backend (stub)
# =========================


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


def _render_ask_transcript():
    """Render in strict order so avatars / order never jump."""
    for i, m in enumerate(st.session_state.get("ask_transcript", [])):
        # Static snapshot card entry
        if m.get("type") == "card":
            with st.chat_message("assistant", avatar=ASSIST_AVATAR):
                # Snapshot with the same visual shell as the live answer card
                st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                with safe_container(border=True):
                    title = m.get("title", "")
                    one_liner = m.get("one_liner", "")
                    sid = m.get("story_id")
                    story = next(
                        (s for s in STORIES if str(s.get("id")) == str(sid)), None
                    )
                    # If the user clicked a Source after this snapshot was created,
                    use_ctx = bool(st.session_state.get("__ctx_locked__"))
                    _ctx = get_context_story() if use_ctx else None
                    if isinstance(_ctx, dict) and (_ctx.get("id") or _ctx.get("title")):
                        story = _ctx or story
                    # If we resolved to a different story via Source click, update the header text, too
                    if isinstance(story, dict):
                        title = story.get("title", title)
                        try:
                            one_liner = build_5p_summary(story, 9999)
                        except Exception:
                            one_liner = one_liner
                    if title:
                        st.markdown(f"### {title}")
                    if one_liner:
                        st.markdown(
                            f"<div class='fivep-quote fivep-unclamped'>{one_liner}</div>",
                            unsafe_allow_html=True,
                        )

                    # View pills (Narrative / Key Points / Deep Dive) — clean CX
                    mode_key = f"card_mode_{i}"
                    st.session_state.setdefault(mode_key, "narrative")
                    if story:
                        modes = story_modes(story)
                        labels = [
                            ("narrative", "Narrative"),
                            ("key_points", "Key Points"),
                            ("deep_dive", "Deep Dive"),
                        ]
                        current = st.session_state.get(mode_key, "narrative")

                        # Prefer segmented control when available
                        if hasattr(st, "segmented_control"):
                            label_map = {b: a for a, b in labels}
                            default_label = next(
                                (b for a, b in labels if a == current), "Narrative"
                            )
                            chosen = st.segmented_control(
                                "",
                                [b for _, b in labels],
                                selection_mode="single",
                                default=default_label,
                                key=f"seg_{mode_key}",  # ← unique per card
                            )
                            new_mode = label_map.get(chosen, "narrative")
                            if new_mode != current:
                                st.session_state[mode_key] = new_mode
                                st.rerun()
                        else:
                            # Fallback: left‑aligned pill buttons styled by .pill-container CSS
                            st.markdown(
                                f'<div class="pill-container" data-mode="{current}">',
                                unsafe_allow_html=True,
                            )
                            for key, text in labels:
                                class_name = {
                                    "narrative": "pill-narrative",
                                    "key_points": "pill-keypoints",
                                    "deep_dive": "pill-deepdive",
                                }[key]
                                st.markdown(
                                    f'<div class="{class_name}">',
                                    unsafe_allow_html=True,
                                )
                                if st.button(
                                    text,
                                    key=f"snap_pill_{i}_{key}",
                                    disabled=(current == key),
                                ):
                                    st.session_state[mode_key] = key
                                    st.rerun()
                                st.markdown('</div>', unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)

                        st.markdown("<hr class='hr'/>", unsafe_allow_html=True)
                        sel = st.session_state.get(mode_key, "narrative")
                        body = modes.get(sel, modes.get("narrative", ""))
                        st.markdown(body)

                    # Sources inside the bubble for symmetry (interactive chips)
                    srcs = m.get("sources", []) or []
                    if srcs:
                        st.markdown(
                            '<div class="sources-tight">', unsafe_allow_html=True
                        )
                        render_sources_chips(
                            srcs,
                            title="Sources",
                            stay_here=True,
                            key_prefix=f"snap_{i}_",
                        )
                        st.markdown("</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            continue

        # Default chat bubble (user/assistant text)
        role = "assistant" if m.get("role") == "assistant" else "user"
        avatar = ASSIST_AVATAR if role == "assistant" else USER_AVATAR
        with st.chat_message(role, avatar=avatar):
            st.markdown(m.get("text", ""))


def _push_card_snapshot_from_state():
    """Append a static answer card snapshot to the transcript based on current state."""
    modes = st.session_state.get("answer_modes", {}) or {}
    sources = st.session_state.get("last_sources", []) or []
    sel = st.session_state.get("answer_mode", "narrative")
    if not sources:
        return
    sid = str(sources[0].get("id", ""))
    primary = next((s for s in STORIES if str(s.get("id")) == sid), None)
    if not primary:
        return
    content_md = modes.get(sel) if modes else st.session_state.get("last_answer", "")
    entry = {
        "type": "card",
        "story_id": primary.get("id"),
        "title": primary.get("title"),
        "one_liner": build_5p_summary(primary, 9999),
        "content": content_md,
        "sources": sources,
    }
    st.session_state["ask_transcript"].append(entry)


# --- Friendly topic extractor for nicer openers ---
def _friendly_topic(q: str) -> str:
    """
    Turn a raw question into a short, natural topic phrase so our opener
    doesn't echo the full prompt awkwardly (e.g., "Tell me about …").
    Returns phrases like "on global payments transformation" or
    "with cloud‑native architecture".
    """
    if not q:
        return "on this topic"
    t = (q or "").strip().rstrip(".?! ")

    # Normalize common lead‑ins
    low = t.lower()
    patterns = [
        ("tell me about leading ", "leading "),
        ("tell me about ", ""),
        ("what's your experience with ", "with "),
        ("what’s your experience with ", "with "),
        ("how did you ", "how I "),
        ("describe how you ", "how I "),
    ]
    for pre, repl in patterns:
        if low.startswith(pre):
            t = repl + t[len(pre) :]
            low = t.lower()
            break

    # If it doesn't start with a preposition/gerund, add a light "on "
    if not re.match(r"^(with|in|on|leading|across)\b", low):
        t = "on " + t

    # Collapse whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _score_story_for_prompt(s: dict, prompt: str) -> float:
    """
    Weighted scoring with token intersection to avoid substring noise (e.g., 'ai' in 'chain').
    - Strong weight for title/client/domain tokens
    - Medium weight for tags
    - Light weight for body (how/what)
    - Small penalty when there is zero overlap
    """
    score = 0.0
    # Strong base credit if a clear metric exists
    if story_has_metric(s):
        score += 1.0

    q_toks = set(_tokenize(prompt or ""))
    if not q_toks:
        return score

    # Tokenize fields
    title_dom_toks = set(
        _tokenize(
            " ".join(
                [
                    s.get("title", ""),
                    s.get("client", ""),
                    s.get("domain", ""),
                    s.get("where", ""),
                ]
            )
        )
    )
    tag_toks = set(_tokenize(" ".join(s.get("tags", []) or [])))
    body_toks = set(
        _tokenize(
            " ".join(
                (s.get("how", []) or [])
                + (s.get("what", []) or [])
                + ([s.get("why", "")] if s.get("why") else [])
            )
        )
    )

    # Overlaps
    title_hits = len(q_toks & title_dom_toks)
    tag_hits = len(q_toks & tag_toks)
    body_hits = len(q_toks & body_toks)

    score += 0.6 * title_hits
    score += 0.5 * tag_hits
    score += 0.2 * body_hits

    if (title_hits + tag_hits + body_hits) == 0:
        score -= 0.4

    return score


# --- Intent boosting for suggestion chips ------------------------------------
_INTENT_SETS = {
    "genai": {
        "genai",
        "generative",
        "llm",
        "model",
        "models",
        "nlp",
        "rai",
        "mlops",
        "registry",
        "governance",
        "responsible",
        "healthcare",
    },
    "cloud": {
        "cloud",
        "cloud-native",
        "kubernetes",
        "k8s",
        "microservices",
        "container",
        "serverless",
        "platform",
        "api",
        "apis",
        "aws",
        "azure",
        "gcp",
    },
    "payments": {
        "payment",
        "payments",
        "treasury",
        "bank",
        "banking",
        "wire",
        "ach",
        "fx",
        "finance",
        "fintech",
    },
    "innovation": {
        "innovation",
        "innovate",
        "prototype",
        "prototyping",
        "incubation",
        "experimentation",
        "discovery",
    },
}


def _intent_topics(prompt: str) -> set[str]:
    toks = set(_tokenize(prompt or ""))
    hits = set()
    for key, words in _INTENT_SETS.items():
        if toks & words:
            hits.add(key)
    return hits


def _intent_boost_for_story(story: dict, topics: set[str]) -> float:
    if not topics:
        return 0.0
    txt_fields = " ".join(
        [
            story.get("title", ""),
            story.get("client", ""),
            story.get("domain", ""),
            story.get("where", ""),
            " ".join(story.get("tags", []) or []),
            " ".join(story.get("how", []) or []),
            " ".join(story.get("what", []) or []),
        ]
    )
    stoks = set(_tokenize(txt_fields))
    boost = 0.0
    for key in topics:
        if stoks & _INTENT_SETS.get(key, set()):
            # Stronger, deterministic boost per matched topic for chips
            boost += 2.5
    return boost


# --- Qualifier awareness (e.g., healthcare with GenAI) -----------------------
_QUAL_HEALTH = {
    "health",
    "healthcare",
    "health-care",
    "clinical",
    "patient",
    "patients",
    "hospital",
    "provider",
    "ehr",
    "emr",
    "hipaa",
    "phi",
    "hippa",
    "kp",
    "kaiser",
    "permanente",
}

# Qualifiers for product/digital product context
_QUAL_PRODUCTS = {
    "product",
    "products",
    "digital",
    "app",
    "apps",
    "application",
    "applications",
    "mobile",
    "web",
    "ux",
    "ui",
    "experience",
    "customer",
    "journey",
    "mvp",
    "poc",
    "prototype",
    "prototyping",
    "ideation",
    "innovation",
    "experimentation",
}


def _qualifier_categories(prompt: str) -> set[str]:
    toks = set(_tokenize(prompt or ""))
    cats = set()
    if toks & _QUAL_HEALTH:
        cats.add("health")
    if toks & _QUAL_PRODUCTS:
        cats.add("product")
    return cats


def _story_has_qualifier(story: dict, cats: set[str]) -> bool:
    if not cats:
        return False
    txt = " ".join(
        [
            story.get("title", ""),
            story.get("client", ""),
            story.get("domain", ""),
            story.get("where", ""),
            " ".join(story.get("tags", []) or []),
            " ".join(story.get("how", []) or []),
            " ".join(story.get("what", []) or []),
        ]
    )
    stoks = set(_tokenize(txt))
    if "health" in cats and (stoks & _QUAL_HEALTH):
        return True
    if "product" in cats and (stoks & _QUAL_PRODUCTS):
        return True
    return False


def rag_answer(question: str, filters: dict):
    # If this prompt was injected by a suggestion chip, skip aggressive off-domain gating
    force_answer = bool(st.session_state.pop("__ask_force_answer__", False))
    from_suggestion = (
        bool(st.session_state.pop("__ask_from_suggestion__", False)) or force_answer
    )
    # Persist debug context for the Ask caption
    st.session_state["__ask_dbg_prompt"] = (question or "").strip()
    st.session_state["__ask_dbg_from_suggestion"] = bool(from_suggestion)
    st.session_state["__ask_dbg_force_answer"] = bool(force_answer)
    # Do not clear banner flags here. We clear them after a successful answer render
    # to ensure the current banner stays visible if anything goes wrong.
    if DEBUG:
        dbg(
            f"ask: from_suggestion={from_suggestion} q='{(question or '').strip()[:60]}'"
        )
    # Mode-only prompts should switch view over the last ranked set, not trigger new retrieval
    simple_mode = (question or "").strip().lower()
    _MODE_ALIASES = {
        "key points": "key_points",
        "keypoints": "key_points",
        "deep dive": "deep_dive",
        "deep-dive": "deep_dive",
        "narrative": "narrative",
    }
    if simple_mode in _MODE_ALIASES and st.session_state.get("__last_ranked_sources__"):
        ids = st.session_state["__last_ranked_sources__"]
        ranked = [
            next((s for s in STORIES if str(s.get("id")) == str(i)), None) for i in ids
        ]
        ranked = [s for s in ranked if s][:3] or (
            semantic_search(question or "", filters, top_k=SEARCH_TOP_K) or STORIES[:3]
        )
        primary = ranked[0]
        modes = {
            "narrative": _format_narrative(primary),
            "key_points": "\n\n".join([_format_key_points(s) for s in ranked]),
            "deep_dive": _format_deep_dive(primary)
            + (
                (
                    "\n\n_Also relevant:_ "
                    + ", ".join(
                        [
                            f"{s.get('title','')} — {s.get('client','')}"
                            for s in ranked[1:]
                        ]
                    )
                )
                if len(ranked) > 1
                else ""
            ),
        }
        sel = _MODE_ALIASES[simple_mode]
        answer_md = modes.get(sel, modes["narrative"])
        sources = [
            {"id": s["id"], "title": s["title"], "client": s.get("client", "")}
            for s in ranked
        ]
        return {
            "answer_md": answer_md,
            "sources": sources,
            "modes": modes,
            "default_mode": sel,
        }

    try:
        # 0) Rule-based nonsense check (fast)
        cat = is_nonsense(question or "")
        if cat and not from_suggestion:
            # Log and set a one-shot flag for the Ask view to render the banner in the right place.
            log_offdomain(question or "", f"rule:{cat}")
            st.session_state["ask_last_reason"] = f"rule:{cat}"
            st.session_state["ask_last_query"] = question or ""
            st.session_state["ask_last_overlap"] = None
            # Decision tag for debug
            st.session_state["__ask_dbg_decision"] = f"rule:{cat}"
            # Return an empty answer so the Ask view shows only the banner
            return {
                "answer_md": "",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }

        # 0.5) Compute overlap for telemetry only (do not gate yet)
        overlap = token_overlap_ratio(question or "", _KNOWN_VOCAB)
        if DEBUG:
            dbg(
                f"ask: overlap={overlap:.2f} __pc_suppressed__={st.session_state.get('__pc_suppressed__')}"
            )

        # 1) Pinecone-first retrieval
        pool = semantic_search(
            question or filters.get("q", ""), filters, top_k=SEARCH_TOP_K
        )

        # If Pinecone returned nothing, *then* decide if we want to show a low-overlap banner
        if not pool and (overlap < 0.15) and not from_suggestion:
            log_offdomain(question or "", f"overlap:{overlap:.2f}")
            st.session_state["ask_last_reason"] = "low_overlap"
            st.session_state["ask_last_query"] = question or ""
            st.session_state["ask_last_overlap"] = overlap
            st.session_state["__ask_dbg_decision"] = f"low_overlap:{overlap:.2f}"
            return {
                "answer_md": "",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }
        # If this was triggered by a suggestion, widen the candidate pool by
        # blending in top local keyword matches so the reranker can surface
        # off-namespace or semantically-adjacent stories (e.g., cloud-native).
        if (from_suggestion or force_answer) and pool:
            try:
                locals_top = sorted(
                    STORIES,
                    key=lambda s: _score_story_for_prompt(s, question),
                    reverse=True,
                )[:5]
                seen = {x.get('id') for x in pool if isinstance(x, dict)}
                for s in locals_top:
                    sid = s.get('id')
                    if sid not in seen:
                        pool.append(s)
                        seen.add(sid)
            except Exception:
                pass
        if DEBUG:
            dbg(f"ask: pool_size={len(pool) if pool else 0}")

        # Intent-first narrowing for suggestion chips: prefer stories that match the chip intent
        if (from_suggestion or force_answer) and pool:
            topics = _intent_topics(question or "")
            try:
                subset = [s for s in pool if _intent_boost_for_story(s, topics) > 0]
            except Exception:
                subset = []
            if subset:
                pool = subset
                if DEBUG:
                    dbg(
                        f"ask: intent_subset size={len(pool)} topics={sorted(list(topics))}"
                    )

        # 2) No results? Prefer building an answer for suggestion-driven prompts
        if not pool:
            if from_suggestion or force_answer:
                # Intent-first fallback: pick top stories that match the chip intent
                topics = _intent_topics(question or "")
                try:
                    scored = []
                    for s in STORIES:
                        boost = _intent_boost_for_story(s, topics)
                        if boost <= 0:
                            continue
                        local = _score_story_for_prompt(s, question)
                        scored.append((boost, local, s))
                    scored.sort(key=lambda t: (-t[0], -t[1]))
                    ranked = [t[2] for t in scored][:3]
                except Exception:
                    ranked = []
                if ranked:
                    # Decision tag and fast return using fallback ranking
                    st.session_state["__ask_dbg_decision"] = (
                        f"chip_intent_fallback:{ranked[0].get('id')}"
                    )
                    st.session_state["__last_ranked_sources__"] = [
                        s["id"] for s in ranked
                    ]
                    primary = ranked[0]
                    try:
                        narrative = _format_narrative(primary)
                        kp_lines = [_format_key_points(s) for s in ranked]
                        key_points = "\n\n".join(kp_lines)
                        deep_dive = _format_deep_dive(primary)
                        if len(ranked) > 1:
                            more = ", ".join(
                                [
                                    f"{s.get('title','')} — {s.get('client','')}"
                                    for s in ranked[1:]
                                ]
                            )
                            deep_dive += f"\n\n_Also relevant:_ {more}"
                        modes = {
                            "narrative": narrative,
                            "key_points": key_points,
                            "deep_dive": deep_dive,
                        }
                        answer_md = narrative
                    except Exception as e:
                        if DEBUG:
                            print(f"DEBUG rag_answer build error (chip fallback): {e}")
                        summary = build_5p_summary(primary, 280)
                        modes = {
                            "narrative": summary,
                            "key_points": summary,
                            "deep_dive": summary,
                        }
                        answer_md = summary
                    sources = [
                        {
                            "id": s["id"],
                            "title": s["title"],
                            "client": s.get("client", ""),
                        }
                        for s in ranked
                    ]
                    return {
                        "answer_md": answer_md,
                        "sources": sources,
                        "modes": modes,
                        "default_mode": "narrative",
                    }
                # Otherwise, fall back to all stories and continue to normal ranking
                pool = [s for s in STORIES if matches_filters(s, filters)] or STORIES
            elif st.session_state.get("__pc_suppressed__"):
                log_offdomain(question or "", "low_confidence")
                # One‑shot banner stamp for Ask view (rendered later in Ask section)
                st.session_state["ask_last_reason"] = "low_confidence"
                st.session_state["ask_last_query"] = question or ""
                st.session_state["ask_last_overlap"] = overlap
                st.session_state["__ask_dbg_decision"] = "low_conf"
                return {
                    "answer_md": "",
                    "sources": [],
                    "modes": {},
                    "default_mode": "narrative",
                }
            else:
                return {
                    "answer_md": "No stories match those filters yet. Clear a few filters or try a broader keyword.",
                    "sources": [],
                    "modes": {},
                    "default_mode": "narrative",
                }

        # 3) Vocab overlap safety: only after Pinecone path ran
        if (
            (overlap < 0.05)
            and st.session_state.get("__pc_suppressed__")
            and not from_suggestion
        ):
            log_offdomain(question or "", "no_overlap+low_conf")
            st.session_state["ask_last_reason"] = "no_overlap+low_conf"
            st.session_state["ask_last_query"] = question or ""
            st.session_state["ask_last_overlap"] = overlap
            st.session_state["__ask_dbg_decision"] = "no_overlap+low_conf"
            return {
                "answer_md": "",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }
    except Exception as e:
        # Catch-all guard so Ask never throws to the UI
        if DEBUG:
            print(f"DEBUG rag_answer fatal error before build: {e}")
        # Safe fallback ranking over local stories
        try:
            ranked = sorted(
                STORIES,
                key=lambda s: _score_story_for_prompt(s, question),
                reverse=True,
            )[:3]
        except Exception:
            ranked = STORIES[:1]
        if not ranked:
            return {
                "answer_md": "No stories available.",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }
        st.session_state["__ask_dbg_decision"] = "fatal_fallback"
        primary = ranked[0]
        summary = build_5p_summary(primary, 280)
        sources = [
            {"id": s.get("id"), "title": s.get("title"), "client": s.get("client", "")}
            for s in ranked
            if isinstance(s, dict)
        ]
        modes = {"narrative": summary, "key_points": summary, "deep_dive": summary}
        return {
            "answer_md": summary,
            "sources": sources,
            "modes": modes,
            "default_mode": "narrative",
        }

    # … then continue with your existing ranking + modes construction …

    # 4) Rank top‑N while preserving Pinecone order; apply intent boost only for suggestion chips
    try:
        if from_suggestion or force_answer:
            topics = _intent_topics(question or "")
            quals = _qualifier_categories(question or "")
            with_idx = list(enumerate(pool))
            # compute boost, local score, and qualifier match
            scored = []
            for idx, s in with_idx:
                try:
                    boost = _intent_boost_for_story(s, topics)
                    local = _score_story_for_prompt(s, question)
                    has_qual = _story_has_qualifier(s, quals)
                except Exception:
                    boost, local, has_qual = 0.0, 0.0, False
                # Base score from intent boost and local score
                score = boost + local
                # Qualifier-aware adjustment: if qualifiers present in prompt,
                # promote stories matching them; demote those that don't.
                if quals:
                    if has_qual:
                        score += 3.5
                    else:
                        score -= 3.0
                scored.append((score, idx, has_qual, boost, local, s))

            # If qualifiers exist, try to keep only items that match them; otherwise use all
            if quals:
                scored_with = [t for t in scored if t[2]]  # has_qual=True
                if scored_with:
                    scored = scored_with

            # Sort by score desc, then original order for stability
            scored.sort(key=lambda t: (-t[0], t[1]))

            # Diversity nudge across client/domain
            picked = []
            seen_clients = set()
            seen_domains = set()
            for score, idx, has_qual, boost, local, s in scored:
                c = (s.get("client") or "").strip().lower()
                d = (s.get("domain") or "").strip().lower()
                if picked:
                    # prefer diversity if available and enough candidates remain
                    if c in seen_clients or d in seen_domains:
                        # Look ahead for a diverse alternative within a small window
                        continue
                picked.append(s)
                seen_clients.add(c)
                seen_domains.add(d)
                if len(picked) >= 3:
                    break
            # If we didn't reach 3 due to diversity, fill from remaining in order
            if len(picked) < 3:
                for _, idx, _, _, _, s in scored:
                    if s not in picked:
                        picked.append(s)
                        if len(picked) >= 3:
                            break
            ranked = (
                picked[:3] if picked else [x for x in pool if isinstance(x, dict)][:3]
            )

            if DEBUG:
                try:
                    dbg(
                        f"ask: topics={sorted(list(topics))} quals={sorted(list(quals))} first_ids={[s.get('id') for s in ranked]}"
                    )
                except Exception:
                    pass
        else:
            # Keep Pinecone/semantic order; only take top 3
            ranked = [x for x in pool if isinstance(x, dict)][:3] or (
                pool[:1] if pool else []
            )
    except Exception as e:
        # Defensive: if ranking fails, take first 1–3 items in the pool order
        if DEBUG:
            print(f"DEBUG rag_answer rank error: {e}")
        ranked = [x for x in pool if isinstance(x, dict)][:3] or (
            pool[:1] if pool else []
        )
    if DEBUG and ranked:
        dbg(
            f"ask: primary='{ranked[0].get('title','')}' sources={[s.get('id') for s in ranked]}"
        )
    st.session_state["__ask_dbg_decision"] = (
        f"ok_ranked:{ranked[0].get('id')}" if ranked else "rank_empty"
    )
    st.session_state["__last_ranked_sources__"] = [s["id"] for s in ranked]

    primary = ranked[0]
    try:
        narrative = _format_narrative(primary)

        # Key points: include top 2–3 stories as bullets for breadth
        kp_lines = [_format_key_points(s) for s in ranked]
        key_points = "\n\n".join(kp_lines)

        # Deep dive: use the primary story; optionally cite others for comparison
        deep_dive = _format_deep_dive(primary)
        if len(ranked) > 1:
            more = ", ".join(
                [f"{s.get('title','')} — {s.get('client','')}" for s in ranked[1:]]
            )
            deep_dive += f"\n\n_Also relevant:_ {more}"

        modes = {
            "narrative": narrative,
            "key_points": key_points,
            "deep_dive": deep_dive,
        }
        # Use the narrative itself as the assistant bubble; omit CTA text
        answer_md = narrative
    except Exception as e:
        # Defensive fallback so Ask never crashes: use 5P summary only
        if DEBUG:
            print(f"DEBUG rag_answer build error: {e}")
        summary = build_5p_summary(primary, 280)
        modes = {"narrative": summary, "key_points": summary, "deep_dive": summary}
        answer_md = summary

    sources = [
        {"id": s["id"], "title": s["title"], "client": s.get("client", "")}
        for s in ranked
    ]
    return {
        "answer_md": answer_md,
        "sources": sources,
        "modes": modes,
        "default_mode": "narrative",
    }


def send_to_backend(prompt: str, filters: dict, ctx: Optional[dict]):
    return rag_answer(prompt, filters)


def set_answer(resp: dict):
    # State-only update; UI renders chips separately to avoid double-render / layout conflicts
    st.session_state["last_answer"] = resp.get("answer_md") or resp.get("answer", "")
    st.session_state["last_sources"] = resp.get("sources", []) or []
    st.session_state["answer_modes"] = resp.get("modes", {}) or {}
    st.session_state["answer_mode"] = resp.get("default_mode", "narrative")


# --- Inline Ask MattGPT panel (for Stories) ---
def render_answer_panel(answer_key: str = "ask"):
    """
    Compact answer card styled like mock_ask_hybrid (shared for panel and bubble).
    """
    modes = st.session_state.get("answer_modes", {}) or {}
    chosen = st.session_state.get("answer_mode", "narrative")
    last_answer = st.session_state.get("last_answer", "") or ""
    last_srcs = st.session_state.get("last_sources", []) or []

    primary = None
    if last_srcs:
        sid = str(last_srcs[0].get("id", ""))
        primary = next((s for s in STORIES if str(s.get("id")) == sid), None)

    # Header card (title + one‑liner)
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        if primary:
            st.markdown(
                f"<div class='h1'>{primary.get('title','')}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='impact'>{build_5p_summary(primary, 999)}</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # Pills — left-aligned flex row; disable the active pill for clear state
    st.markdown(f"<div class='pill-row' data-mode='{chosen}'>", unsafe_allow_html=True)

    # Narrative
    st.markdown("<div class='pill-narrative'>", unsafe_allow_html=True)
    if st.button(
        "Narrative",
        key=f"{answer_key}_pill_narrative",
        disabled=(chosen == "narrative"),
    ):
        st.session_state["answer_mode"] = "narrative"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Key Points
    st.markdown("<div class='pill-keypoints'>", unsafe_allow_html=True)
    if st.button(
        "Key Points",
        key=f"{answer_key}_pill_keypoints",
        disabled=(chosen == "key_points"),
    ):
        st.session_state["answer_mode"] = "key_points"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Deep Dive
    st.markdown("<div class='pill-deepdive'>", unsafe_allow_html=True)
    if st.button(
        "Deep Dive",
        key=f"{answer_key}_pill_deep_dive",
        disabled=(chosen == "deep_dive"),
    ):
        st.session_state["answer_mode"] = "deep_dive"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    # Body for chosen mode
    body_md = modes.get(chosen, last_answer)
    st.markdown(body_md)

    # Sources row — interactive chips that stay on Ask
    if last_srcs:
        st.markdown('<div class="sources-tight">', unsafe_allow_html=True)
        render_sources_chips(
            last_srcs, title="Sources", stay_here=True, key_prefix=f"{answer_key}_"
        )
        st.markdown('</div>', unsafe_allow_html=True)


def render_ask_panel(ctx: Optional[dict]):
    """Inline Ask MattGPT panel rendered inside the Stories detail column."""
    st.markdown("---")
    st.markdown("#### Ask MattGPT")
    # Compact context breadcrumb (minimal) + hover/click details
    if ctx:
        client = (ctx.get("client") or "").strip()
        # Prefer the sub-domain after " / " so the crumb stays short
        domain_full = (ctx.get("domain") or "").strip()
        domain_short = domain_full.split(" / ")[-1] if " / " in domain_full else domain_full
        title = (ctx.get("title") or "").strip()
        role = (ctx.get("role") or "").strip()
        # One-time CSS for breadcrumb + details
        if not st.session_state.get("_ctx_css_done"):
            st.markdown(
                """
                <style>
                .ctx-crumb{font-size:.9rem;opacity:.85;margin:.25rem 0 .5rem 0}
                .ctx-crumb small{opacity:.85}
                details.ctx-details summary{cursor:pointer; list-style:none; margin:.25rem 0}
                details.ctx-details summary::-webkit-details-marker{display:none}
                details.ctx-details summary::after{content:"▸"; margin-left:.35rem; opacity:.6}
                details.ctx-details[open] summary::after{content:"▾"}
                details.ctx-details .ctx-body{font-size:.9rem; opacity:.9; padding:.25rem 0 0 0}
                </style>
                """,
                unsafe_allow_html=True,
            )
            st.session_state["_ctx_css_done"] = True

        # Hover tooltip carries the long form; crumb is short
        long_txt = f"{title} — {client} • {role} • {domain_full}".strip(" •-")
        short_txt = f"💼 {client} | {domain_short}".strip(" |")
        st.markdown(
            f"<div class='ctx-crumb' title='{long_txt}'><small>{short_txt}</small></div>",
            unsafe_allow_html=True,
        )
        # Click-to-expand full details (optional)
        st.markdown(
            f"""
            <details class="ctx-details">
              <summary><small>Show details</small></summary>
              <div class="ctx-body">
                <strong>Title:</strong> {title or "—"}<br/>
                <strong>Client:</strong> {client or "—"}<br/>
                <strong>Role:</strong> {role or "—"}<br/>
                <strong>Domain:</strong> {domain_full or "—"}
              </div>
            </details>
            """,
            unsafe_allow_html=True,
        )
    with st.expander("What is Ask MattGPT?", expanded=False):
        st.markdown(
            """
            Ask follow‑ups about the selected story. Use a starter question or type your own,
            then click **Generate answer**. The reply shows which stories it used.
            """
        )

    prompt = st.text_area(
        "Ask MattGPT",
        value=st.session_state.get(
            "ask_input", st.session_state.get("seed_prompt", "")
        ),
        key="ask_input",
        height=120,
        placeholder="Type your question…",
    )
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Generate answer", key="ask_send_inline"):
            with st.spinner("Answering…"):
                # Ask is pure semantic; ignore Explore filters here
                resp = send_to_backend(prompt, {}, ctx)
            set_answer(resp)
    with c2:
        if st.button("Clear", key="ask_clear_inline"):
            st.session_state["seed_prompt"] = ""
            st.session_state["ask_input"] = ""
            st.session_state["last_answer"] = ""
            st.session_state["last_sources"] = []
            st.rerun()

    if st.session_state.get("last_answer"):
        st.markdown("#### Answer")
        with safe_container(border=True):
            # Prefer a user-selected story from Sources; otherwise fall back to the first source
            chosen_story = get_context_story() if st.session_state.get("__ctx_locked__") else None
            if not chosen_story:
                _srcs = st.session_state.get("last_sources") or []
                if _srcs:
                    first = _srcs[0]
                    # Resolve by id first, then by title/client
                    sid = str(first.get("id") or first.get("story_id") or "").strip()
                    if sid:
                        chosen_story = next(
                            (x for x in STORIES if str(x.get("id")) == sid), None
                        )
                    if not chosen_story:
                        t = (first.get("title") or "").strip().lower()
                        c = (first.get("client") or "").strip().lower()
                        for x in STORIES:
                            xt = (x.get("title") or "").strip().lower()
                            xc = (x.get("client") or "").strip().lower()
                            if xt == t and (not c or xc == c):
                                chosen_story = x
                                break

            if isinstance(chosen_story, dict):
                # Render the unified pills card: title + pills + body + clickable Sources
                render_answer_card_clean_pills(
                    chosen_story,
                    story_modes(chosen_story),
                    answer_mode_key="answer_mode",
                )
            else:
                # Fallback: keep legacy body if we couldn't resolve a structured story
                modes = st.session_state.get("answer_modes", {}) or {}
                current_mode = st.session_state.get("answer_mode", "narrative")

                if modes:
                    cols = st.columns([1, 1, 1, 12])
                    with cols[0]:
                        if st.button("Narrative", key="ask_mode_narrative"):
                            st.session_state["answer_mode"] = "narrative"
                            st.rerun()
                    with cols[1]:
                        if st.button("Key Points", key="ask_mode_key_points"):
                            st.session_state["answer_mode"] = "key_points"
                            st.rerun()
                    with cols[2]:
                        if st.button("Deep Dive", key="ask_mode_deep_dive"):
                            st.session_state["answer_mode"] = "deep_dive"
                            st.rerun()
                    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

                content_md = (
                    modes.get(current_mode)
                    if modes
                    else st.session_state.get("last_answer", "")
                )
                if content_md:
                    st.markdown(content_md)

                sources = st.session_state.get("last_sources", [])
                if sources:
                    render_sources_chips(
                        sources, title="Sources", stay_here=True, key_prefix="inline_"
                    )


# === Ask MattGPT helpers ===

# =========================
# UI — Home / Stories / Ask / About
# =========================
clients, domains, roles, tags, personas_all = build_facets(STORIES)

# --- HOME ---
if st.session_state["active_tab"] == "Home":
    
    # Check if a button just changed the tab by looking for the flag
    # that components.py sets when a starter card is clicked
    #Check if we should skip the option_menu (because a button was just clicked)
    
        # Just render the home content without the option_menu
        css_once()
        render_home_hero_and_stats()
        render_home_starters()
   

# --- STORIES ---
elif st.session_state["active_tab"] == "Explore Stories":
    # --- normalize legacy tab names ---
    legacy = {"Stories": "Explore Stories"}
    cur = st.session_state.get("active_tab", "Home")
    if cur in legacy:
        st.session_state["active_tab"] = legacy[cur]
    st.markdown("<a id='stories_top'></a>", unsafe_allow_html=True)
    st.markdown('<div class="sticky-filters">', unsafe_allow_html=True)
    F = st.session_state["filters"]

    with safe_container(border=True):
        c1, c2, c3 = st.columns([1, 1, 1])

        # --- Col 1: Audience + Client
        with c1:
            F["personas"] = st.multiselect(
                "Audience",
                personas_all,
                default=F["personas"],
                key="facet_personas",
                help="Who would find this story most relevant?",
            )
            F["clients"] = st.multiselect(
                "Client", clients, default=F["clients"], key="facet_clients"
            )

        # --- Col 2: Friendlier Domain picker (Category -> Sub-domain)
        with c2:
            domain_parts = [
                (d.split(" / ")[0], (d.split(" / ")[1] if " / " in d else ""), d)
                for d in domains
            ]
            groups = sorted({cat for cat, sub, full in domain_parts if full})

            selected_group = st.selectbox(
                "Domain category", ["All"] + groups, key="facet_domain_group"
            )

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
                    help="Start typing to filter. Stored value remains the full 'Category / Sub' path.",
                )
            else:
                subdomain_options = [
                    full for cat, sub, full in domain_parts if cat == selected_group
                ]
                prev = [d for d in F.get("domains", []) if d in subdomain_options]
                F["domains"] = st.multiselect(
                    "Sub‑domain",
                    options=sorted(subdomain_options),
                    default=prev,
                    key="facet_subdomains",
                    format_func=_fmt_sub,
                )

        # --- Col 3: Role, Tags, Metric flag
        with c3:
            F["roles"] = st.multiselect(
                "Role", roles, default=F["roles"], key="facet_roles"
            )
            F["tags"] = st.multiselect(
                "Tags", tags, default=F["tags"], key="facet_tags"
            )
            F["has_metric"] = st.toggle(
                "Has metric in outcomes", value=F["has_metric"], key="facet_has_metric"
            )

        # Keyword box
        F["q"] = st.text_input(
            "Search keywords",
            value=F["q"],
            placeholder="title, client, outcomes…",
            key="facet_q",
        )

        cols = st.columns([1, 4])
        with cols[0]:
            if st.button("Reset filters", key="btn_reset_filters"):
                st.session_state["filters"] = {
                    "personas": [],
                    "clients": [],
                    "domains": [],
                    "roles": [],
                    "tags": [],
                    "q": "",
                    "has_metric": False,
                }
                # reset domain group selector & paging so UI doesn't look 'stuck'
                st.session_state["facet_domain_group"] = "All"
                st.session_state["page_offset"] = 0
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Always run semantic search (no debounce, no skip) ---
    # --- Always run semantic search (no debounce, no skip) ---
    view = []
    if F["q"].strip():
        ov = token_overlap_ratio(F["q"], _KNOWN_VOCAB)
        reason = is_nonsense(F["q"]) or (ov < 0.03 and f"overlap:{ov:.2f}")
        if reason:
            st.session_state["__nonsense_reason__"] = reason
            st.session_state["__pc_suppressed__"] = True
            st.session_state["last_results"] = STORIES[:5]

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
            view = semantic_search(F["q"], F)
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
        # No query: fall back to last results or all stories
        view = st.session_state.get("last_results", STORIES)

    st.session_state["__results_count__"] = len(view)

    chips = []
    if F.get("q"):
        chips.append(("Search", f"“{F['q']}”", ("q", None)))
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
    st.markdown(
        f'<span class="results-count">{len(view)} results</span>',
        unsafe_allow_html=True,
    )

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
        st.rerun()

    # --- Sort + layout toggle (stay INSIDE the Stories block) ---
    # --- Slim toolbar (results • metric-first • layout) ---
    st.caption(f"**{len(view)} results**")
    layout_mode = "List (master‑detail)"  # force list view for now

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

    rows = [_row(s) for s in view]
    df = pd.DataFrame(rows)
    show_cols = [c for c in ["Title", "Client", "Role", "Domain"] if c in df.columns]
    show_df = df[show_cols] if show_cols else df

    if layout_mode.startswith("List"):
        # -------- Master–detail (wide grid, compact detail) --------
        left, right = st.columns(
            [26, 12], gap="large"
        )  # wider grid; slightly narrower detail

        with left:
            if not _HAS_AGGRID:
                st.warning(
                    "Row‑click selection requires **st‑aggrid**. Install with: `pip install streamlit-aggrid`"
                )
                st.dataframe(
                    show_df,
                    hide_index=True,
                    use_container_width=True,
                    height=min(820, 36 * (len(show_df) + 2)),
                    column_config={
                        "Title": st.column_config.TextColumn(width="large"),
                        "Client": st.column_config.TextColumn(width="medium"),
                        "Role": st.column_config.TextColumn(width="medium"),
                        "Domain": st.column_config.TextColumn(width="large"),
                    },
                )
                # Ensure right pane has something
                id_list = df["ID"].tolist() if "ID" in df.columns else []
                cur = st.session_state.get("active_story")
                if id_list and (not cur or cur not in id_list):
                    st.session_state["active_story"] = id_list[0]
            else:
                df_view = df[["ID"] + show_cols] if show_cols else df

                gob = GridOptionsBuilder.from_dataframe(df_view)
                gob.configure_default_column(
                    resizable=True, sortable=True, filter=True, flex=1, min_width=160
                )
                gob.configure_column("ID", hide=True)
                gob.configure_selection(selection_mode="single", use_checkbox=False)
                opts = gob.build()
                opts["suppressRowClickSelection"] = False
                opts["rowSelection"] = "single"

                grid = AgGrid(
                    df_view,
                    gridOptions=opts,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    allow_unsafe_jscode=True,
                    theme="streamlit",
                    height=min(860, 36 * (len(df_view) + 2)),
                    fit_columns_on_grid_load=True,
                )

                # Normalize selection across versions
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
                else:
                    cur = st.session_state.get("active_story")
                    id_series = (
                        df_view["ID"].tolist() if "ID" in df_view.columns else []
                    )
                    if id_series and (not cur or cur not in id_series):
                        st.session_state["active_story"] = id_series[0]

        with right:
            with safe_container(border=True):
                st.markdown(
                    '<div class="sticky-detail detail-pane">', unsafe_allow_html=True
                )
                detail = get_context_story()
                if detail:
                    # Keep the details and the CTA inside the same container so it doesn't float
                    story_card(detail, idx=0, show_ask_cta=False)
                    if st.button(
                        "Ask MattGPT about this",
                        key=f"ask_from_detail_{detail.get('id','x')}",
                        use_container_width=True,
                        help="Switch to Ask with this story as context",
                    ):
                        on_ask_this_story(detail)  # on_ask_this_story sets active tab
                        st.stop()
                else:
                    st.info("Select a story on the left to view details.")
                st.markdown("</div>", unsafe_allow_html=True)

    else:
        # -------- Cards mode (unchanged except caption trimmed) --------
        total = len(view)
        page_size = int(st.session_state.get("page_size", 25))
        offset = int(st.session_state.get("page_offset", 0))
        if offset < 0:
            offset = 0
        if offset >= total and total > 0:
            offset = 0
            st.session_state["page_offset"] = 0

        view_window = view[offset : offset + page_size]

        if not view_window:
            if F["q"] and st.session_state["__pc_suppressed__"]:
                st.warning(
                    "Tried semantic search but didn’t find anything confidently relevant. Try rephrasing or pick a filter."
                )
                for i, tip in enumerate(
                    ["Payments modernization", "Generative AI", "Governance", "OKRs"]
                ):
                    if st.button(tip, key=f"suggest_{i}"):
                        F["q"] = tip
                        st.rerun()
            else:
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
            st.caption(f"Showing {start}–{end} of {total}")

            for i, s in enumerate(view_window):
                story_card(s, offset + i, show_ask_cta=False)

            mc1, mc2 = st.columns([1, 1])
            with mc1:
                if offset + page_size < total:
                    if st.button("Show more stories", key="btn_show_more"):
                        st.session_state["page_offset"] = offset + page_size
                        st.rerun()
            with mc2:
                st.markdown("[Back to top](#stories_top)")

# --- ASK MATTGPT ---
elif st.session_state["active_tab"] == "Ask MattGPT":
    # Add a header row with the title and the How it Works link
    col1, col2 = st.columns([5, 1])
    with col1:
        st.subheader("Ask MattGPT")
    with col2:
        if st.button("🔧 How it works", key="how_works_top"):
             # Add a subtle overlay effect
            st.markdown("""
            <style>
            /* Subtle background dim effect */
            .stApp > div:first-child {
                background-color: rgba(0, 0, 0, 0.1);
            }
            </style>
            """, unsafe_allow_html=True)
            st.session_state["show_how_modal"] = not st.session_state.get("show_how_modal", False)
            st.rerun()
    
    # Show the modal if toggled
    if st.session_state.get("show_how_modal", False):
        # Create a proper modal container without using expander
        st.markdown("---")
        
        # Header with close button
        col1, col2 = st.columns([10, 1])
        with col1:
            st.markdown("## 🔧 How MattGPT Works")
        with col2:
            if st.button("✕", key="close_how"):
                st.session_state["show_how_modal"] = False
                st.rerun()
        
        # Content in a bordered container
        with st.container():
            # Quick stats bar
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Stories Indexed", "115")
            with col2:
                st.metric("Avg Response Time", "1.2s")
            with col3:
                st.metric("Retrieval Accuracy", "87%")
            with col4:
                st.metric("Vector Dimensions", "384")
            
            st.markdown("---")
            
            # Architecture overview
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### Architecture Overview
                
                **🎯 Semantic Search Pipeline**
                - Sentence-BERT embeddings (all-MiniLM-L6-v2)
                - 384-dimensional vector space
                - Pinecone vector database with metadata filtering
                
                **🔄 Hybrid Retrieval**
                - 60% semantic similarity weight
                - 40% keyword matching weight
                - Intent recognition for query understanding
                """)
            
            with col2:
                st.markdown("""
                ### Data & Processing
                
                **📊 Story Corpus**
                - 115+ structured narratives from Fortune 500 projects
                - STAR/5P framework encoding
                - Rich metadata: client, domain, outcomes, metrics
                
                **💬 Response Generation**
                - Context-aware retrieval (top-k=30)
                - Multi-mode synthesis (Narrative/Key Points/Deep Dive)
                - Source attribution with confidence scoring
                """)
            
            # Query Flow
            st.markdown("### Query Flow")
            st.code("""
                Your Question 
                    ↓
                [Embedding + Intent Analysis]
                    ↓
                [Pinecone Vector Search + Keyword Matching]
                    ↓
                [Hybrid Scoring & Ranking]
                    ↓
                [Top 3 Stories Retrieved]
                    ↓
                [Response Synthesis with Sources]
                            """, language="text")
                        
            st.markdown("---")
    
    # Rest of your Ask MattGPT content continues...
    # Rest of your Ask MattGPT content continues as normal
    # Context banner, transcript, etc...
                
    # Context banner if Ask was launched from a Story
    ctx = get_context_story()
    _show_ctx = bool(ctx) and (
        st.session_state.get("__ctx_locked__") or st.session_state.get("__asked_once__")
    )

    if _show_ctx:
        client = (ctx.get("client") or "").strip()
        domain_full = (ctx.get("domain") or "").strip()
        domain_short = domain_full.split(" / ")[-1] if " / " in domain_full else domain_full
        title = (ctx.get("title") or "").strip()
        role = (ctx.get("role") or "").strip()
        if not st.session_state.get("_ctx_css_done"):
            st.markdown(
                """
                <style>
                .ctx-crumb{font-size:.9rem;opacity:.85;margin:.25rem 0 .5rem 0}
                .ctx-crumb small{opacity:.85}
                details.ctx-details summary{cursor:pointer; list-style:none; margin:.25rem 0}
                details.ctx-details summary::-webkit-details-marker{display:none}
                details.ctx-details summary::after{content:"▸"; margin-left:.35rem; opacity:.6}
                details.ctx-details[open] summary::after{content:"▾"}
                details.ctx-details .ctx-body{font-size:.9rem; opacity:.9; padding:.25rem 0 0 0}
                </style>
                """,
                unsafe_allow_html=True,
            )
            st.session_state["_ctx_css_done"] = True

        long_txt = f"{title} — {client} • {role} • {domain_full}".strip(" •-")
        short_txt = f"💼 {client} | {domain_short}".strip(" |")

        left, right = st.columns([1, 0.12], gap="small")
        with left:
            st.markdown(
                f"<div class='ctx-crumb' title='{long_txt}'><small>{short_txt}</small></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <details class="ctx-details">
                  <summary><small>Show details</small></summary>
                  <div class="ctx-body">
                    <strong>Title:</strong> {title or "—"}<br/>
                    <strong>Client:</strong> {client or "—"}<br/>
                    <strong>Role:</strong> {role or "—"}<br/>
                    <strong>Domain:</strong> {domain_full or "—"}
                  </div>
                </details>
                """,
                unsafe_allow_html=True,
            )
       # with right:
        #    if st.button("×", key="btn_clear_ctx", help="Clear context"):
         #       _clear_ask_context()

    # Lightweight DEBUG status for Ask (visible only when DEBUG=True)
    if DEBUG:
        try:
            _dbg_flags = {
                "vector": VECTOR_BACKEND,
                "index": PINECONE_INDEX_NAME or "-",
                "ns": PINECONE_NAMESPACE or "-",
                "pc_suppressed": bool(st.session_state.get("__pc_suppressed__")),
                "has_last": bool(st.session_state.get("last_sources")),
                "pending_snap": bool(st.session_state.get("__pending_card_snapshot__")),
                # NEW: report external renderer overrides
                "ext_chips": (
                    "yes"
                    if callable(globals().get("_ext_render_sources_chips"))
                    else "no"
                ),
                "ext_badges": (
                    "yes"
                    if callable(globals().get("_ext_render_sources_badges_static"))
                    else "no"
                ),
            }
            st.caption("🧪 " + ", ".join(f"{k}={v}" for k, v in _dbg_flags.items()))
            # Second line: last prompt + ask decision
            lp = (st.session_state.get("__ask_dbg_prompt") or "").strip()
            lp = (lp[:60] + "…") if len(lp) > 60 else lp
            st.caption(
                "🧪 "
                + f"prompt='{lp}' from_suggestion={st.session_state.get('__ask_dbg_from_suggestion')}"
                + f" force={st.session_state.get('__ask_dbg_force_answer')} pc_hits={st.session_state.get('__dbg_pc_hits')}"
                + f" decision={st.session_state.get('__ask_dbg_decision')}"
                + f" reason={st.session_state.get('ask_last_reason')}"
            )
        except Exception:
            pass

    # 1) Bootstrap a stable transcript (one-time)
    _ensure_ask_bootstrap()

    # 2) Unify seeds and chip-clicks: inject as a real user turn if present
    seed = st.session_state.pop("seed_prompt", None)
    injected = st.session_state.pop("__inject_user_turn__", None)
    pending = seed or injected
    if pending:
        # If a live card was pending snapshot, capture it now before injecting the new turn
        if st.session_state.get("__pending_card_snapshot__"):
            _push_card_snapshot_from_state()
            st.session_state["__pending_card_snapshot__"] = False
        _push_user_turn(pending)
        with st.spinner("Thinking…"):
            try:
                # Ask is pure semantic; ignore Explore filters here
                resp = send_to_backend(pending, {}, ctx)
            except Exception as e:
                _push_assistant_turn("Sorry, I couldn't generate an answer right now.")
                st.error(f"Backend error: {e}")
                st.rerun()
            else:
                set_answer(resp)
                # If no banner is active, append a static card snapshot now so it
                # appears in-order as a chat bubble; also suppress the bottom live card once.
                if not st.session_state.get(
                    "ask_last_reason"
                ) and not st.session_state.get("__sticky_banner__"):
                    _push_card_snapshot_from_state()
                    st.session_state["__suppress_live_card_once__"] = True
                # If a chip click requested banner clear, perform it now after answer set
                if st.session_state.pop("__clear_banner_after_answer__", False):
                    st.session_state.pop("ask_last_reason", None)
                    st.session_state.pop("ask_last_query", None)
                    st.session_state.pop("ask_last_overlap", None)
                st.rerun()

    # 3) Render transcript so far (strict order, no reflow)
    _render_ask_transcript()

    # 4) One‑shot nonsense/off‑domain banner appears AFTER transcript
    rendered_banner = False
    if st.session_state.get("ask_last_reason"):
        with st.chat_message("assistant", avatar=ASSIST_AVATAR):
            render_no_match_banner(
                reason=st.session_state.get("ask_last_reason", ""),
                query=st.session_state.get("ask_last_query", ""),
                overlap=st.session_state.get("ask_last_overlap", None),
                suppressed=st.session_state.get("__pc_suppressed__", False),
                filters=st.session_state.get("filters", {}),
                key_prefix="askinline",
            )
        rendered_banner = True
        # Clear flags so the banner doesn't re-render on every rerun
        st.session_state.pop("ask_last_reason", None)
        st.session_state.pop("ask_last_query", None)
        st.session_state.pop("ask_last_overlap", None)
        # Persist as sticky so it remains visible between user turns unless dismissed
        st.session_state.setdefault(
            "__sticky_banner__",
            {
                "reason": (
                    dec
                    if (dec := (st.session_state.get("__ask_dbg_decision") or ""))
                    else "no_match"
                ),
                "query": st.session_state.get("__ask_dbg_prompt", ""),
                "overlap": None,
                "suppressed": bool(st.session_state.get("__pc_suppressed__", False)),
            },
        )
    elif True:
        # Forced fallback: if gating decided no‑match but the flag was not set,
        # render a banner anyway so the user sees actionable chips.
        dec = (st.session_state.get("__ask_dbg_decision") or "").strip().lower()
        no_match_decision = (
            dec.startswith("rule:")
            or dec.startswith("low_overlap")
            or dec == "low_conf"
            or dec == "no_overlap+low_conf"
        )
        if no_match_decision and not st.session_state.get("last_sources"):
            with st.chat_message("assistant", avatar=ASSIST_AVATAR):
                render_no_match_banner(
                    reason=dec or "no_match",
                    query=st.session_state.get("__ask_dbg_prompt", ""),
                    overlap=st.session_state.get("ask_last_overlap", None),
                    suppressed=st.session_state.get("__pc_suppressed__", False),
                    filters=st.session_state.get("filters", {}),
                    key_prefix="askinline_forced",
                )
            rendered_banner = True

    # Sticky banner temporarily disabled to stabilize chip clicks
    st.session_state["__sticky_banner__"] = None

    # 5) Compact answer panel (title • unclamped 5P • view pills • sources)
    _m = st.session_state.get("answer_modes", {}) or {}
    _srcs = st.session_state.get("last_sources", []) or []
    _primary = None
    if _srcs:
        _sid = str(_srcs[0].get("id", ""))
        _primary = next((s for s in STORIES if str(s.get("id")) == _sid), None)
    # Suppress the bottom live card when:
    #  - a banner was rendered this run; or
    #  - we already have at least one static card snapshot in the transcript
    has_snapshot_card = any(
        (isinstance(x, dict) and x.get("type") == "card")
        for x in st.session_state.get("ask_transcript", [])
    )
    if (
        not rendered_banner
        and not has_snapshot_card
        and not st.session_state.get("__suppress_live_card_once__")
        and (_m or _primary or st.session_state.get("last_answer"))
    ):
        # Always render the bottom live card so pills are available.
        # Snapshot holds only header + one-liner + sources to avoid duplicate body text.
        render_answer_card_clean_pills(
            _primary or {"title": "Answer"}, _m, "answer_mode"
        )
    # Reset one-shot suppression flag after a render cycle
    if st.session_state.get("__suppress_live_card_once__"):
        st.session_state["__suppress_live_card_once__"] = False


    # 6) Handle a new chat input (command aliases or normal question)
    # Render the chat input only on the Ask MattGPT tab
    if st.session_state.get("active_tab") == "Ask MattGPT":
        user_input_local = st.chat_input("Ask anything…", key="ask_chat_input1")
    else:
        user_input_local = None
    if user_input_local:
        # If a live card is pending snapshot from the previous answer, snapshot it now
        if st.session_state.get("__pending_card_snapshot__"):
            _push_card_snapshot_from_state()
            st.session_state["__pending_card_snapshot__"] = False

        # Append user's turn immediately to keep order deterministic
        _push_user_turn(user_input_local)

        # Command aliases (view switches) should not trigger new retrieval
        cmd = re.sub(r"\s+", " ", user_input_local.strip().lower())
        cmd_map = {
            "narrative": "narrative",
            "key points": "key_points",
            "keypoints": "key_points",
            "deep dive": "deep_dive",
            "deep-dive": "deep_dive",
            "details": "deep_dive",
        }
        # If a quick command is used without any story context, show a friendly tip
        has_context = bool(
            ctx
            or st.session_state.get("active_story")
            or st.session_state.get("last_sources")
        )
        if cmd in cmd_map and not has_context:
            _push_assistant_turn(
                "Quick mode commands like “key points” work after a story is in context — either select a story or ask a question first so I can cite sources. For now, try asking a full question."
            )
            st.rerun()
        if cmd in cmd_map and (
            ctx
            or st.session_state.get("active_story")
            or st.session_state.get("last_sources")
        ):
            # Resolve a target story: explicit context > last active story > last answer’s primary source
            target = ctx
            if not target:
                sid = st.session_state.get("active_story")
                if not sid:
                    srcs = st.session_state.get("last_sources") or []
                    if srcs:
                        sid = srcs[0].get("id")
                if sid:
                    target = next(
                        (x for x in STORIES if str(x.get("id")) == str(sid)), None
                    )

            if target:
                modes_local = story_modes(target)
                key = cmd_map[cmd]
                heading = {
                    "narrative": "Narrative",
                    "key_points": "Key points",
                    "deep_dive": "Deep dive",
                }[key]
                answer_md = (
                    f"**{heading} for _{target.get('title','')} — {target.get('client','')}_**\n\n"
                    + modes_local.get(key, "")
                )

                # Prime compact answer state (no assistant bubble)
                st.session_state["answer_modes"] = modes_local
                st.session_state["answer_mode"] = key
                st.session_state["last_answer"] = answer_md
                st.session_state["last_sources"] = [
                    {
                        "id": target.get("id"),
                        "title": target.get("title"),
                        "client": target.get("client"),
                    }
                ]
                # Show the answer card below the transcript
                _push_assistant_turn(answer_md)
                # Do NOT snapshot for command aliases; they don't represent a new question
                st.rerun()

        # Normal question → ask backend, persist state, append assistant turn
        # One-shot context lock: if a story was explicitly selected (chip/CTA),
        # use that story as context for THIS turn only, then clear the lock.
        # --- Determine context for THIS turn (one-shot lock) ---
        ctx_for_this_turn = ctx
        if st.session_state.pop("__ctx_locked__", False):  # consume the lock
            try:
                locked_ctx = get_context_story()
            except Exception:
                locked_ctx = None
            if locked_ctx:
                ctx_for_this_turn = locked_ctx

        # --- Ask backend + render result ---
        with st.spinner("Thinking…"):
            try:
                # Consume the suggestion flag (one-shot); we don't need its value here
                st.session_state.pop("__ask_from_suggestion__", None)

                # Ask is pure semantic; ignore Explore filters here
                resp = send_to_backend(user_input_local, {}, ctx_for_this_turn)

            except Exception as e:
                _push_assistant_turn("Sorry, I couldn't generate an answer right now.")
                st.error(f"Backend error: {e}")
                st.rerun()

            else:
                set_answer(resp)

                # Add a static snapshot so the answer appears in-order as a bubble,
                # and suppress the bottom live card once to avoid duplication.
                if not st.session_state.get("ask_last_reason") and not st.session_state.get("__sticky_banner__"):
                    _push_card_snapshot_from_state()
                    st.session_state["__suppress_live_card_once__"] = True

                st.rerun()
 
# --- ABOUT ---
elif st.session_state["active_tab"] == "About Matt":
   # First, ensure CSS is loaded
    css_once()  # This should load your existing styles
    
    # If that doesn't work, inject the specific styles needed
    st.markdown("""
    <style>
    .hero-section {
        text-align: center;
            padding: 60px 30px;
            background: var(--background-color);  
            color: var(--text-color);  /* Instead of white */
            border-radius: 16px;
            margin-bottom: 50px;
            position: relative;
            overflow: hidden;
    }
    
    .stat-card {
        background: #2d2d2d;
        padding: 32px 24px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #3a3a3a;
        transition: transform 0.3s ease;
        margin-bottom: 24px;
        box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);  /* Always visible shadow */
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(74, 144, 226, 0.2);
    }
    
    .stat-number {
        font-size: 36px;
        font-weight: 700;
        color: #4a90e2;
        display: block;
        margin-bottom: 8px;
    }
    
    .stat-label {
        color: #b0b0b0;
        font-size: 16px;
    }
    
    .section-title {
        font-size: 32px;
        font-weight: 600;
        text-align: center;
        margin: 60px 0 40px 0;
        color: #ffffff;
    }
    
    .fixed-height-card {
        background: var(--secondary-background-color);
        padding: 28px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
        min-height: 250px;
        box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);  /* Always visible shadow */
    }

    .fixed-height-card:hover {
        transform: translateY(-4px);
        border-color: var(--border-color);
        box-shadow: 0 12px 35px rgba(128, 128, 128, 0.35);  /* Brighter shadow on hover */
    }
    .card-desc {
        color: #b0b0b0;
        margin-bottom: 8px;
        line-height: 1.5;
        font-size: 14px;
    }
    .skill-bar {
        height: 6px;
        background: var(--border-color);
        border-radius: 3px;
        margin-bottom: 16px;
        position: relative;
    }

    .skill-fill {
        height: 100%;
        background: #4a90e2;
        border-radius: 3px;
        transition: width 0.3s ease;
    }

    .philosophy-card {
        background: var(--secondary-background-color);
        padding: 32px;
        border-radius: 16px;
        text-align: center;
        border: 1px solid var(--border-color);
        min-height: 180px;
    }

    .philosophy-icon {
        font-size: 48px;
        margin-bottom: 16px;
        box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);  /* Always visible shadow */
        }

    .timeline-marker {
        width: 64px;
        height: 64px;
        background: #4a90e2;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        flex-shrink: 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='hero-section'>
        <h1 style='font-size: 48px; font-weight: 700; margin-bottom: 24px;'>Matt's Journey</h1>
        <p style='font-size: 20px; color: #b0b0b0; max-width: 800px; margin: 0 auto;'>
            Helping Fortune 500 companies both modernize legacy systems and launch net new cloud-native products — blending modern architecture, 
            product mindset, and innovative engineering practices to deliver scalable digital platforms and experiences.
        </p>
    </div>
    """, unsafe_allow_html=True)
    

    #Pure HTML stats that bypass Streamlit's CSS
    st.markdown(
        """
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin: 50px 0;">
            <div style="background: var(--secondary-background-color); padding: 32px 24px; border-radius: 12px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);">
                <span style="font-size: 36px; font-weight: 700; color: #4a90e2; display: block; margin-bottom: 8px;">20+</span>
                <span style="color: #999999; font-size: 16px;">Years Experience</span>
            </div>
            <div style="background: var(--secondary-background-color); padding: 32px 24px; border-radius: 12px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);">
                <span style="font-size: 36px; font-weight: 700; color: #4a90e2; display: block; margin-bottom: 8px;">300+</span>
                <span style="color: #999999; font-size: 16px;">Professionals Upskilled</span>
            </div>
            <div style="background: var(--secondary-background-color); padding: 32px 24px; border-radius: 12px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);">
                <span style="font-size: 36px; font-weight: 700; color: #4a90e2; display: block; margin-bottom: 8px;">200+</span>
                <span style="color: #999999; font-size: 16px;">Engineers Certified</span>
            </div>
            <div style="background: var(--secondary-background-color); padding: 32px 24px; border-radius: 12px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);">
                <span style="font-size: 36px; font-weight: 700; color: #4a90e2; display: block; margin-bottom: 8px;">2</span>
                <span style="color: #999999; font-size: 16px;">Innovation Centers Built & Scaled to 150+</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h2 class='section-title'>Career Evolution</h2>", unsafe_allow_html=True)
    
    # Timeline using fixed-height-card styling
    timeline_data = [
        ("🚀", "2019-2023", "Director, Cloud Innovation @ Accenture", 
         "Led 150+ professionals • Generated $300M+ revenue • 4x faster delivery • 25% retention improvement"),
        ("☁️", "2016-2019", "Cloud Architecture Lead @ Liquid Studio",
         "AWS enablement • 200+ certifications • Rapid prototyping • 30% faster time-to-market"),
        ("💳", "2009-2016", "Sr Technology Manager @ Accenture",
         "$500M+ transformation • 12 countries • Payment platforms • 3x sales increase"),
        ("⚡", "2005-2009", "Startups & Consulting",
         "Built products 0→1 • Team building • Product-market fit • Successful exits")
    ]
    
    for icon, period, role, desc in timeline_data:
        col1, col2 = st.columns([1, 11])
        with col1:
            #class="timeline-marker
            st.markdown(f"<div class='timeline-marker'>{icon}</div>", unsafe_allow_html=True)

            #st.markdown(f"<div style='font-size: 40px; text-align: center; margin-top: 20px;'>{icon}</div>", 
                      # unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='fixed-height-card' style='margin-bottom: 16px; min-height: auto;'>
                <div style='color: #4a90e2; font-size: 14px; margin-bottom: 8px;'>{period}</div>
                <h3 style='font-size: 20px; font-weight: 600; margin-bottom: 8px;'>{role}</h3>
                <p style='color: #b0b0b0; font-size: 14px;'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Core Competencies with skill bars
    st.markdown("<h2 class='section-title'>Core Competencies</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='fixed-height-card'>
            <h3 style='color: var(--text-color); font-size: 20px; margin-bottom: 24px;'>Digital Product & Innovation</h3>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Product Mindset</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 95%;'></div></div>
            </div>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Modern Engineering</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 90%;'></div></div>
            </div>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Innovation Strategy</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 85%;'></div></div>
            </div>
            <div>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Digital Transformation</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 95%;'></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='fixed-height-card'>
            <h3 style='color: var(--text-color); font-size: 20px; margin-bottom: 24px;'>Technical Architecture</h3>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Cloud Modernization</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 95%;'></div></div>
            </div>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Microservices</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 85%;'></div></div>
            </div>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>DevOps & CI/CD</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 85%;'></div></div>
            </div>
            <div>
                <p style='color: var(--text-color); margin-bottom: 8px;'>API Strategy</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 90%;'></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='fixed-height-card'>
            <h3 style='color: var(--text-color); font-size: 20px; margin-bottom: 24px;'>Industry Expertise</h3>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Financial Services</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 95%;'></div></div>
            </div>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Healthcare & Life Sciences</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 80%;'></div></div>
            </div>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Enterprise Technology</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 90%;'></div></div>
            </div>
            <div>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Startup Operations</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 75%;'></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Leadership Philosophy
    st.markdown("""
    <div class='philosophy-card' style='margin: 60px 0;'>
        <h2 style='font-size: 28px; margin-bottom: 16px;'>Leadership Philosophy</h2>
        <p style='color: #b0b0b0; margin-bottom: 40px;'>Principles that guide how I approach transformation, team building, and complex challenges</p>
    </div>
    """, unsafe_allow_html=True)
    cols = st.columns(4)
    philosophy_items = [
        ("🎯", "Outcome-Driven", "Measure success by business impact, not activity"),
        ("🚀", "Iterate Fast", "Small experiments beat big plans"),
        ("👥", "People First", "Technology serves humans, not the other way around"),
        ("🔄", "Learn Continuously", "Every failure is data for the next attempt")
    ]
    
    for col, (icon, title, desc) in zip(cols, philosophy_items):
        with col:
            st.markdown(f"""
            <div style='text-align: center;'>
                <div class='philosophy-icon'>{icon}</div>
                <h4 style='font-size: 18px; margin-bottom: 8px;'>{title}</h4>
                <p style='font-size: 14px; color: #b0b0b0;'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
   
    # Let's Connect section with better UI/UX
    st.markdown("<h2 class='section-title'>Let's Connect</h2>", unsafe_allow_html=True)

    # Professional summary with visual appeal
    st.markdown("""
    <div style='text-align: center; max-width: 800px; margin: 0 auto 40px auto;'>
        <p style='font-size: 18px; color: var(--text-color); margin-bottom: 24px;'>
            Open to Director/VP roles in platform modernization and innovation strategy
        </p>
        <div style='display: flex; justify-content: center; gap: 40px; margin-bottom: 32px;box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);'>
            <div style='text-align: center;'>
                <span style='font-size: 24px;'>🏢</span>
                <p style='font-size: 14px; color: #999; margin-top: 8px;'>Office Preferred</p>
            </div>
            <div style='text-align: center;'>
                <span style='font-size: 24px;'>🤝</span>
                <p style='font-size: 14px; color: #999; margin-top: 8px;'>Team Collaboration</p>
            </div>
            <div style='text-align: center;'>
                <span style='font-size: 24px;'>📍</span>
                <p style='font-size: 14px; color: #999; margin-top: 8px;'>Open to Relocation</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Contact cards in a grid
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown("""
        <div class='fixed-height-card' style='text-align: center; min-height: 180px; cursor: pointer; transition: all 0.3s;'>
            <span style='font-size: 32px;'>📧</span>
            <h4 style='margin: 16px 0 8px 0; color: var(--text-color);'>Email</h4>
            <p style='color: #4a90e2; font-size: 14px;'>mcpugmire@gmail.com</p>
            <p style='color: #999; font-size: 12px; margin-top: 8px;'>Direct inquiries</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Copy Email", key="copy_email", use_container_width=True):
            st.code("mcpugmire@gmail.com")

    with col2:
        st.markdown("""
        <div class='fixed-height-card' style='text-align: center; min-height: 180px; cursor: pointer; transition: all 0.3s;'>
            <span style='font-size: 32px;'>💼</span>
            <h4 style='margin: 16px 0 8px 0; color: var(--text-color);'>LinkedIn</h4>
            <p style='color: #4a90e2; font-size: 14px;'>matt-pugmire</p>
            <p style='color: #999; font-size: 12px; margin-top: 8px;'>Professional network</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open LinkedIn", key="open_linkedin", use_container_width=True):
            st.markdown("[→ linkedin.com/in/matt-pugmire](https://linkedin.com/in/matt-pugmire/)")

    with col3:
        st.markdown("""
        <div class='fixed-height-card' style='text-align: center; min-height: 180px; cursor: pointer; transition: all 0.3s;'>
            <span style='font-size: 32px;'>☕</span>
            <h4 style='margin: 16px 0 8px 0; color: var(--text-color);'>Coffee Chat</h4>
            <p style='color: #4a90e2; font-size: 14px;'>In-person meeting</p>
            <p style='color: #999; font-size: 12px; margin-top: 8px;'>Let's meet face-to-face</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Schedule Coffee", key="coffee_chat", use_container_width=True):
            st.info("Reach out via email or LinkedIn to schedule an in-person meeting")
