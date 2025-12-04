# app_next.py — Next-gen UI (Home / Stories / Ask / About)
# - Clean, centered layout without sidebar
# - Pinecone-first (guarded) + local fallback search
# - Debounced “Ask MattGPT” with starter chips
# - Compact List view by default, Card view optional
# - Badges + strongest-metric summary

import os, re, time, textwrap, json
from typing import List, Optional
from urllib.parse import quote_plus

# =========================
# UI — Home / Stories / Ask / About


def render_sources_chips(sources: list[dict], title: str = "Sources"):
    """Render the existing Sources row as clickable chips that deep-link to Explore."""
    if not sources:
        return
    st.markdown(f"**{title}**")
    chips = []
    for s in sources:
        sid = quote_plus(str(s.get("id", "")))
        client = (s.get("client") or "").strip()
        title_txt = (s.get("title") or "").strip()
        label = f"{title_txt} — {client}" if client else title_txt
        chips.append(
            f"<a href='?view=explore&story_id={sid}' class='badge'>🔎 {label}</a>"
        )
    st.markdown(
        f"<div class='badge-row'>{''.join(chips)}</div>", unsafe_allow_html=True
    )


import pandas as pd
import streamlit as st

# --- Shared config: prefer st.secrets, fallback to .env ---
import os
from dotenv import load_dotenv
import streamlit as st

# === DEBUG UTIL (safe to keep; no-op when DEBUG=False) ===
DEBUG = True


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
        st.warning(f"Pinecone init failed, falling back to FAISS. ({e})")
        VECTOR_BACKEND = "faiss"

# optional: row-click table
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

    _HAS_AGGRID = True
except Exception:
    _HAS_AGGRID = False

st.set_page_config(page_title="MattGPT — Matt's Story", page_icon="🤖", layout="wide")

# optional: Bootstrap mono icons (for option_menu)
st.markdown(
    "<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css'>",
    unsafe_allow_html=True,
)
# optional: ChatGPT-style sidebar menu
try:
    from streamlit_option_menu import option_menu

    _HAS_OPTION_MENU = True
except Exception:
    _HAS_OPTION_MENU = False

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
                st.session_state["seed_prompt"] = q
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


# =========================
# Config / constants
# =========================
PINECONE_MIN_SIM = 0.22  # suppress low-confidence semantic hits
_DEF_DIM = 384  # stub embedding size to keep demo self-contained
DATA_FILE = os.getenv("STORIES_JSONL", "echo_star_stories_nlp.jsonl")  # optional

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
        existing = {i.name for i in _PC.list_indexes().indexes}
        if _PINECONE_INDEX not in existing:
            _PC.create_index(name=_PINECONE_INDEX, dimension=_DEF_DIM, metric="cosine")
        _PC_INDEX = _PC.Index(_PINECONE_INDEX)
        return _PC_INDEX
    except Exception:
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
    """Normalize JSONL records (Title-cased keys) into the lowercase schema the UI expects."""
    stories = []
    p = Path(path)
    if not p.exists():
        # try the enriched filename as a fallback
        alt = p.with_name("echo_star_stories.jsonl")
        if alt.exists():
            p = alt
        else:
            return stories

    with p.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            raw = json.loads(line)
            # Build normalized record
            title = raw.get("Title", "").strip() or "Untitled"
            client = raw.get("Client", "").strip() or "Unknown"
            role = raw.get("Role", "") or ""
            cat = raw.get("Category", "") or ""
            subcat = raw.get("Sub-category", "") or ""
            domain = " / ".join([x for x in [cat, subcat] if x]).strip()

            who = raw.get("Person", "") or ""
            where = raw.get("Place", "") or ""
            why = raw.get("Purpose", "") or ""

            # STAR/5P lists (accept strings or arrays)
            situation = _ensure_list(raw.get("Situation"))
            task = _ensure_list(raw.get("Task"))
            action = _ensure_list(raw.get("Action"))
            result = _ensure_list(raw.get("Result"))

            process = _ensure_list(raw.get("Process"))
            performance = _ensure_list(raw.get("Performance"))

            tags = _split_tags(raw.get("public_tags"))

            sid = raw.get("id") or f"{_slug(title)}|{_slug(client)}"

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
                    "5PSummary": raw.get("5PSummary", "").strip(),
                }
            )
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
st.session_state.setdefault("last_sources", [])
st.session_state.setdefault("last_results", STORIES)
st.session_state.setdefault("show_ask_panel", False)
st.session_state.setdefault("ask_input", "")

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

# =========================
# Tiny CSS polish
# =========================
st.markdown(
    """
<style>
/* Keep the detail card visible when the left table scrolls */
.sticky-detail { position: sticky; top: 72px; }
            
/* Harmonize table/detail font sizes and tighten table look */
.ag-theme-streamlit .ag-cell,
.ag-theme-streamlit .ag-header-cell-text { font-size: 1.0rem; line-height: 1.35; }
.detail-pane > div[class*="stContainer"] {
  padding-top: 6px;
  border-top: 1px solid rgba(255,255,255,0.08);
}

/* Make left grid feel a bit denser without looking crowded */
.ag-theme-streamlit .ag-row { height: 34px; }
            
/* Row container spacing (slightly tighter) */
.story-block { margin: 8px 0 10px 0; }

/* Unified title styling */
.story-title { font-weight: 700; font-size: 1.15rem; line-height: 1.25; margin: 0 0 4px 0; }
.story-subtitle { color: inherit; opacity: .8; margin: 0 0 4px 0; }

/* ---- 5P one‑liner as a subtle quote block ---- */
/* Defaults (light) */
:root{
  --q-bg: rgba(0,0,0,0.03);
  --q-accent: #6B7280;
  --fivep-lh: 1.45;    /* line-height used for height calc */
  --fivep-lines: 3;    /* default lines in compact list */
}

/* Quote box */
.fivep-quote{
  position: relative;
  padding: 10px 12px;
  margin: 10px 0;                /* tight vertical rhythm */
  background: var(--q-bg);
  border-radius: 8px;
  font-size: 1rem;
  line-height: var(--fivep-lh);
  word-break: break-word;
  overflow-wrap: anywhere;
  white-space: normal;
  box-sizing: border-box;
  max-width: 100%;
}
/* neutralize inner paragraph margins Streamlit adds */
.fivep-quote p { margin: 0; }

/* Unclamped (Cards view) — never clip */
.fivep-unclamped{
  display: block;
  overflow: visible;
  text-overflow: initial;
  -webkit-line-clamp: unset;
  -webkit-box-orient: unset;
}

/* 2‑line clamp utility (not used by 5P but kept for reuse) */
.fivep-lines-2{
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Compact list clamp — reserve space so it never feels chopped */
.fivep-lines-3{
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: var(--fivep-lines);
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: calc(1em * var(--fivep-lh) * var(--fivep-lines));
}

/* Give wider screens a LITTLE more room (not 6) */
@media (min-width: 900px){
  :root{ --fivep-lines: 4; }
}

/* Compact variant spacing only for List view */
.fivep-compact{ padding: 8px 12px; font-size: .98rem; }
.compact-left .fivep-quote{ margin: 6px 0 8px; }

/* Dark mode */
@media (prefers-color-scheme: dark){
  :root { --q-bg: rgba(255,255,255,0.06); --q-accent: #9CA3AF; }
  .fivep-quote { opacity: .97; }
}

/* Safety: prevent parent containers from clipping bubble shadows/quotes */
.story-block, .stMarkdown, .stContainer { overflow: visible; }

/* Meta line (client • role • domain) */
.meta-block {
  background: rgba(0,0,0,0.03);
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 0.85rem;
  margin: 2px 0;
}
@media (prefers-color-scheme: dark) {
  .meta-block { background: rgba(255,255,255,0.05); }
}

/* ---- Compact list layout ---- */
.compact-row { display:flex; gap:14px; align-items:flex-start; }
.compact-left { flex: 1 1 auto; min-width:0; }
.compact-right { width: 148px; display:flex; align-items:center; justify-content:flex-end; }

/* Optional teaser summary (if used elsewhere) */
.compact-summary{
  line-height: 1.35;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 6px 0;
  font-weight: 500;
  opacity: .95;
}

/* ---- Static pretty badges (non-clickable) ---- */
.badge-row{
  display:flex;
  flex-wrap:wrap;
  gap:6px;
  margin:4px 0 0;
}
.badge{
  display:inline-flex;
  align-items:center;
  gap:6px;
  font-size:13px;
  line-height:1.1;
  padding:4px 9px;
  border-radius:999px;
  border:1px solid rgba(0,0,0,0.10);
  background:rgba(0,0,0,0.04);
  white-space:nowrap;
}
a.badge { text-decoration: none; color: inherit; }
a.badge:hover { filter: brightness(0.97); }
.badge .dot{
  width:7px; height:7px; border-radius:50%; display:inline-block;
}
@media (prefers-color-scheme: dark){
  .badge{
    background:rgba(255,255,255,0.06);
    border-color:rgba(255,255,255,0.12);
  }
}

/* Field labels + card summary */
.field-label{
  display:block; font-weight:700; text-transform:uppercase; letter-spacing:.02em;
  font-size:0.82rem; opacity:.85; margin:6px 0 2px;
}
.card-summary{ font-size:1rem; line-height:1.4; opacity:.92; margin:6px 0 10px; }
.story-block .stMarkdown p { margin: 0.2rem 0; }

/* Starter chips (Ask tab) */
#starter-chips { margin-top: 6px; }
#starter-chips .stButton>button {
  border-radius: 12px; background: transparent; border: 1px solid rgba(0,0,0,0.18);
  padding: 10px 16px; box-shadow: none; font-weight: 600;
}
#starter-chips .stButton>button:hover { background: rgba(0,0,0,0.05); border-color: rgba(0,0,0,0.28); }
#starter-chips .stButton { margin-bottom: 8px; }

/* Sticky filter bar + active chips */
.sticky-filters { position: sticky; top: 8px; z-index: 9; }

                    
.active-chip-row { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin: 6px 0; }
.active-chip-row button {
  border-radius: 999px !important;
  padding: 4px 10px !important;
  border: 1px solid rgba(255,255,255,0.18) !important;
  background: rgba(255,255,255,0.03) !important;
}
.active-chip-row button:hover {
  background: rgba(255,255,255,0.06) !important;
  border-color: rgba(255,255,255,0.30) !important;
}
.results-count { font-weight:600; margin-right:8px; }

/* Quick actions (sidebar) — match app font and lighten) */
#quick-actions { font-family: inherit !important; }

/* --- QUICK ACTIONS STYLE: subtler, tighter box --- */
#quick-actions {
  background: rgba(0,0,0,0.025);
  border-radius: 14px;
  padding: 14px;
  margin: 14px 0 14px 0;
  border: 1px solid rgba(0,0,0,0.08);
  box-shadow: none;
}
#quick-actions .stButton > button {
  margin-bottom: 14px;
  padding: 12px 15px;
  border-radius: 12px;
  border: 1px solid rgba(0,0,0,0.13);
  background: rgba(0,0,0,0.02);
  font-weight: 600;
  box-shadow: none;
}
#quick-actions .stButton > button:hover {
  background: rgba(0,0,0,0.05);
  border-color: rgba(0,0,0,0.23);
}
#quick-actions .stButton {
  margin-bottom: 12px;
}

.quick-actions-header {
  font-size: 1.15rem;
  font-weight: 700;
  /* text-transform: uppercase; */  /* Removed to allow natural casing */
  /* letter-spacing: 0.03em; */     /* Remove for visual alignment */
  margin: 10px 0 10px 0;
  opacity: 0.9;
}

/* Sidebar nav hover */
.st-emotion-cache-1v0mbdj a:hover,
.st-emotion-cache-1v0mbdj button:hover {
  background: rgba(255,255,255,0.06) !important;
  border-radius: 8px;
  transition: background 0.2s ease-in-out;
}

/* Home pills hover lift + glow (target option_menu nav-links) */
/* Home pills base style */
.nav-link {
  transition: transform 0.25s ease, background 0.25s ease, box-shadow 0.25s ease !important;
  will-change: transform, background, box-shadow;
  cursor: pointer !important;
}

/* Home pills hover */
.nav-link:hover,
div[data-testid="stHorizontalBlock"] .nav-link:hover {
  transform: scale(1.08) !important;
  background: rgba(255,255,255,0.08) !important;
  box-shadow: 0 4px 10px rgba(0,0,0,0.25) !important;
  border-radius: 10px !important;
}

  /* Force hover effects for Home pills buttons */
  .stButton > button:hover {
    transform: scale(1.08) !important;
    background: rgba(255,255,255,0.08) !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.25) !important;
    border-radius: 10px !important;
    transition: all 0.25s ease !important;
  }
/* Dark mode polish */
@media (prefers-color-scheme: dark) {
  .badge { background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.12); }
  .card-summary{ opacity:.95; }
  #starter-chips .stButton>button {
    border-color: rgba(255,255,255,0.22); background: rgba(255,255,255,0.03);
  }
  #starter-chips .stButton>button:hover {
    background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.35);
  }
  .story-title { opacity: .98; }
  #quick-actions {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: none;
  }
  #quick-actions .stButton > button {
    border: 1px solid rgba(255,255,255,0.16);
    background: rgba(255,255,255,0.02);
  }
  #quick-actions .stButton > button:hover {
    background: rgba(255,255,255,0.06);
    border-color: rgba(255,255,255,0.26);
  }
}
            
/* Selected row highlight & hover */
.ag-theme-streamlit .ag-row.ag-row-selected { 
  background: rgba(99, 102, 241, 0.12) !important;  /* indigo-500-ish */
}
.ag-theme-streamlit .ag-row:hover {
  background: rgba(255,255,255,0.06) !important;
}
</style>
<style>
/* Force Home pills hover (override inline styles from option_menu) */
.nav-item > a.nav-link:hover {
  background: rgba(255,255,255,0.08) !important;
  transform: scale(1.08) !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.35) !important;
  border-radius: 10px !important;
  border: 1px solid rgba(255,255,255,0.2) !important;
  transition: all 0.25s ease-in-out !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# Helpers
# =========================
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


def _dot_for(label: str) -> str:
    if not label:
        return "•"
    idx = sum(ord(c) for c in label) % len(_DOT_EMOJI)
    return _DOT_EMOJI[idx]


def render_badges_static(s: dict, max_tags: int = 6):
    """
    Pretty, non-clickable pill badges (domain + tags), with +N more, matching the original look.
    """
    domain = s.get("domain") or ""
    tag_list = list(s.get("tags") or [])
    shown_tags = tag_list[:max_tags]
    hidden = max(0, len(tag_list) - len(shown_tags))

    parts = []
    if domain:
        dom_short = domain.split(" / ")[-1] if " / " in domain else domain
        parts.append(
            f'<span class="badge"><span class="dot" style="background:{_badge_color(domain)}"></span>{dom_short}</span>'
        )
    for t in shown_tags:
        parts.append(
            f'<span class="badge"><span class="dot" style="background:{_badge_color(t)}"></span>{t}</span>'
        )
    if hidden:
        parts.append(f'<span class="badge">+{hidden} more</span>')

    st.markdown(
        f'<div class="badge-row">{"".join(parts)}</div>', unsafe_allow_html=True
    )


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
    toks = [t for t in re.split(r"[^\w]+", (query or "").lower()) if len(t) >= 3]
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

    suggestions = [
        "Payments modernization",
        "Generative AI in healthcare",
        "Cloud-native architecture",
        "Innovation in digital products",
    ]
    cols = st.columns(len(suggestions))
    for i, tip in enumerate(suggestions):
        with cols[i]:
            if st.button(tip, key=f"suggest_no_match_{i}"):
                F = st.session_state.get(
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
                F["q"] = tip
                st.session_state["filters"] = F
                st.session_state["page_offset"] = 0
                st.session_state["__nonsense_reason__"] = None
                goto("Explore Stories")

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
            if st.button("Clear filters", key="clear_filters_no_match"):
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
        story = next((s for s in STORIES if s.get("id") == story_id), None)
        if story:
            snip = fallback_builder(story)

    # Tidy + truncate for UI neatness
    snip = " ".join(str(snip).split())
    if len(snip) > 220:
        snip = snip[:217] + "..."

    return f"🔎 Matched on: {snip} (score { _fmt_score(score) })"


def story_card(s, idx=0):
    st.markdown('<div class="story-block">', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f"<div class='story-title'>{s.get('title','')}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="fivep-quote fivep-unclamped">{build_5p_summary(s)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(_matched_caption(s.get("id", "")))
        st.markdown(
            f'<div class="meta-block">{s.get("client","")} • {s.get("role","")} • {s.get("domain","")}</div>',
            unsafe_allow_html=True,
        )
        render_badges_static(s)

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
                # --- New: Anchored view switcher for THIS story ---
                with st.container(border=True):
                    mode_key = f"__detail_mode__{s.get('id','x')}"
                    st.session_state.setdefault(mode_key, "narrative")

                    # Use a horizontal radio instead of nested columns (avoids Streamlit nesting limits)
                    _opts_labels = ["Narrative", "Key points", "Deep dive"]
                    _opts_keys = ["narrative", "key_points", "deep_dive"]
                    _current = st.session_state.get(mode_key, "narrative")
                    _idx = _opts_keys.index(_current) if _current in _opts_keys else 0

                    choice = st.radio(
                        "View",
                        _opts_labels,
                        index=_idx,
                        key=f"detail_view_radio_{s.get('id','x')}",
                        horizontal=True,
                    )
                    st.session_state[mode_key] = _opts_keys[_opts_labels.index(choice)]

                    selected = st.session_state.get(mode_key, "narrative")
                    modes = story_modes(s)
                    st.markdown(modes.get(selected, _format_narrative(s)))

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

        with row_right:
            if st.button(
                "Ask MattGPT about this",
                key=f"ask_{s.get('id','x')}_{idx}",
                help="Switches to Ask tab with this story preloaded so you can ask follow-ups",
            ):
                on_ask_this_story(s)

    st.markdown("</div>", unsafe_allow_html=True)


def compact_row(s, idx=0):
    st.markdown('<div class="story-block">', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="compact-row">', unsafe_allow_html=True)

        # LEFT
        st.markdown('<div class="compact-left">', unsafe_allow_html=True)
        # Title prominent (unified style)
        st.markdown(
            f"<div class='story-title'>{s['title']}</div>", unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='fivep-quote fivep-compact'><span class='fivep-lines-3'>{build_5p_summary(s)}</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="meta-block">{s["client"]} • {s["role"]} • {s.get("domain","")}</div>',
            unsafe_allow_html=True,
        )
        render_badges_static(s)

        # Pinecone reason + score (with 5P fallback if snippet missing)
        st.caption(_matched_caption(s.get("id", "")))

        st.markdown("</div>", unsafe_allow_html=True)  # /compact-left

        # RIGHT
        st.markdown('<div class="compact-right">', unsafe_allow_html=True)
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
    sid = st.session_state.get("active_story")
    if not sid:
        return None
    for s in STORIES:
        if s.get("id") == sid:
            return s
    return None


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
    if F is None:
        F = st.session_state.get(
            "filters",
            {
                "personas": [],
                "clients": [],
                "domains": [],
                "roles": [],
                "tags": [],
                "has_metric": False,
                "q": "",
            },
        )
    if F["personas"] and not (set(F["personas"]) & set(s.get("personas", []))):
        return False
    if F["clients"] and s.get("client") not in F["clients"]:
        return False
    if F["domains"] and s.get("domain") not in F["domains"]:
        return False
    if F["roles"] and s.get("role") not in F["roles"]:
        return False
    if F["tags"] and not (set(F["tags"]) & set(s.get("tags", []))):
        return False
    if F["has_metric"] and not story_has_metric(s):
        return False
    q = (F["q"] or "").strip().lower()
    if q:
        hay = " ".join(
            [
                s.get("title", ""),
                s.get("client", ""),
                s.get("role", ""),
                s.get("domain", ""),
                s.get("who", ""),
                s.get("where", ""),
                s.get("why", ""),
                " ".join(s.get("how", [])),
                " ".join(s.get("what", [])),
                " ".join(s.get("tags", [])),
            ]
        ).lower()
        if q not in hay and not any(q in t.lower() for t in s.get("tags", [])):
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
    pc_score: float, kw_score: float, *, w_pc: float = 0.7, w_kw: float = 0.3
) -> float:
    """Blend vector similarity (0..1) with keyword overlap (0..1)."""
    try:
        return float(w_pc) * float(pc_score or 0.0) + float(w_kw) * float(
            kw_score or 0.0
        )
    except Exception:
        return pc_score or 0.0


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


def pinecone_semantic_search(
    query: str, filters: dict, top_k: int = 5
) -> Optional[List[dict]]:
    idx = _init_pinecone()
    if not idx or not query:
        return None
    pc_filter = {}
    if filters.get("domains"):
        pc_filter["domain"] = {"$in": filters["domains"]}
    if filters.get("clients"):
        pc_filter["client"] = {"$in": filters["clients"]}
    try:
        qvec = _embed(query)
        print(
            f"DEBUG Embeddings: qvec_dim={len(qvec)}  model=MiniLM({'yes' if _get_embedder() else 'stub'})"
        )
        # DEBUG: confirm index + namespace
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
        # --- DEBUG logging block ---
        print("DEBUG Pinecone raw matches:", res.matches)
        for m in res.matches:
            try:
                meta = (m.metadata or {}) if hasattr(m, "metadata") else {}
                sid = meta.get("id")
                score = float(getattr(m, "score", 0.0) or 0.0)
                snippet = meta.get("summary")
                print(
                    f"DEBUG Pinecone hit: id={sid}, score={score:.3f}, snippet={snippet}"
                )
            except Exception as e:
                print("DEBUG Pinecone hit parse error:", e)
        # --- end DEBUG logging block ---
        hits = []
        st.session_state["__pc_last_ids__"].clear()
        st.session_state["__pc_snippets__"].clear()

        for m in res.matches:
            meta = (m.metadata or {}) if hasattr(m, "metadata") else {}
            sid = meta.get("id")
            score = float(getattr(m, "score", 0.0) or 0.0)
            if not sid:
                # attempt fallback: some indexes store id only in m.id
                sid = getattr(m, "id", None)
            if not sid:
                continue
            story = next((s for s in STORIES if s.get("id") == sid), None)
            if not story:
                continue
            kw = _keyword_score_for_story(story, query)
            blended = _hybrid_score(score, kw)
            hits.append(
                {
                    "story": story,
                    "pc_score": score,
                    "kw_score": kw,
                    "score": blended,
                    "snippet": meta.get("summary"),
                }
            )

        # sort by blended score desc for stability
        hits.sort(key=lambda h: h.get("score", 0.0), reverse=True)
        return hits
    except Exception:
        return None


def semantic_search(
    query: str,
    filters: dict,
    *,
    enforce_overlap: bool = False,
    min_overlap: float = 0.0,
):
    """Pinecone-first with confidence threshold; fallback to local filters; persists snippet/score for UI.
    For dev mode, disables strict overlap gating and score thresholds so queries always return something.
    """
    q = (query or "").strip()
    hits = pinecone_semantic_search(q, filters)
    st.session_state["__pc_suppressed__"] = False

    if hits is not None and hits:
        threshold = 0.25  # lower to avoid over-suppressing legitimate matches
        confident = [h for h in hits if h.get("score", 0.0) >= threshold]
        if not confident:
            # Soft failover: mark suppressed but continue with local keyword fallback
            st.session_state["__pc_suppressed__"] = True
            print(
                f"DEBUG Pinecone: all {len(hits)} hits below threshold {threshold}; falling back to local keyword results"
            )
            local_fallback = [s for s in STORIES if matches_filters(s, filters)]
            # Persist ranked source ids for mode switching even on fallback
            st.session_state["__last_ranked_sources__"] = [
                s["id"] for s in local_fallback
            ][:10]
            # Clear snippet/score caches since we don't trust Pinecone in this branch
            st.session_state["__pc_last_ids__"].clear()
            st.session_state["__pc_snippets__"].clear()
            return local_fallback

        # persist per‑story display info using Pinecone score (for caption) but rank by blended
        st.session_state["__pc_suppressed__"] = False
        st.session_state["__pc_last_ids__"] = {
            h["story"]["id"]: h.get("pc_score", h.get("score", 0.0)) for h in confident
        }
        st.session_state["__pc_snippets__"] = {
            h["story"]["id"]: (h.get("snippet") or build_5p_summary(h["story"]))
            for h in confident
        }
        # also persist the ranked list for Ask mode switching
        st.session_state["__last_ranked_sources__"] = [
            h["story"]["id"] for h in confident
        ]
        print(
            f"DEBUG Pinecone: returning {len(confident)} confident hits above {threshold}"
        )
        return [h["story"] for h in confident if matches_filters(h["story"], filters)]

    # Always return local keyword fallback
    return [s for s in STORIES if matches_filters(s, filters)]


# --- Compatibility shim: legacy callers expect `retrieve_stories(query, top_k)` ---
def retrieve_stories(query: str, top_k: int = 6, *, filters: dict | None = None):
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
    Weighted scoring: strong weight for title/tags, lighter for body; slight penalty for no overlap.
    """
    score = 0.0
    # Strong base credit if a clear metric exists
    if story_has_metric(s):
        score += 1.0

    p = (prompt or "").lower()
    if not p:
        return score

    # Build searchable haystacks with different weights
    title_hay = " ".join(
        [s.get("title", ""), s.get("client", ""), s.get("domain", "")]
    ).lower()
    tags_hay = " ".join(s.get("tags", []) or []).lower()
    how_what = " ".join((s.get("how", []) or []) + (s.get("what", []) or [])).lower()

    tokens = [t for t in re.split(r"[^\w]+", p) if t]
    if not tokens:
        return score

    # Heavier weight for title/tags matches, lighter for body text
    title_hits = sum(1 for t in set(tokens) if t in title_hay)
    tag_hits = sum(1 for t in set(tokens) if t in tags_hay)
    body_hits = sum(1 for t in set(tokens) if t in how_what)

    score += 0.6 * title_hits
    score += 0.5 * tag_hits
    score += 0.2 * body_hits

    # Small penalty if we found zero overlaps at all
    if title_hits + tag_hits + body_hits == 0:
        score -= 0.4

    return score


def rag_answer(question: str, filters: dict):
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
        ranked = [next((s for s in STORIES if s.get("id") == i), None) for i in ids]
        ranked = [s for s in ranked if s][:3] or (
            semantic_search(question or "", filters) or STORIES[:3]
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

    # 0) Rule-based nonsense check (fast)
    cat = is_nonsense(question or "")
    if cat:
        log_offdomain(question or "", f"rule:{cat}")
        render_no_match_banner(
            reason=f"rule:{cat}",
            query=question or "",
            overlap=None,
            suppressed=False,
            filters=filters,
        )
        return {
            "answer_md": (
                "That one’s outside the scope of this portfolio. I focus on platform strategy, innovation, modernization, AI enablement, and delivery at scale."
            ),
            "sources": [],
            "modes": {},
            "default_mode": "narrative",
        }

    # 0.5) Off-domain heuristic via known vocab overlap (fast, language-agnostic)
    overlap = token_overlap_ratio(question or "", _KNOWN_VOCAB)
    if overlap < 0.03:
        log_offdomain(question or "", f"overlap:{overlap:.2f}")
        render_no_match_banner(
            reason=f"low_overlap",
            query=question or "",
            overlap=overlap,
            suppressed=False,
            filters=filters,
        )
        return {
            "answer_md": (
                "That one’s outside the scope of this portfolio. I focus on platform strategy, innovation, modernization, AI enablement, and delivery at scale."
            ),
            "sources": [],
            "modes": {},
            "default_mode": "narrative",
        }
    # 1) Pinecone-first retrieval (existing)
    pool = semantic_search(question or filters.get("q", ""), filters)

    # 2) No results? handle low-confidence vs empty-after-filters (existing paths)
    if not pool:
        if st.session_state.get("__pc_suppressed__"):
            log_offdomain(question or "", "low_confidence")
            render_no_match_banner(
                reason="low_confidence",
                query=question or "",
                overlap=overlap,
                suppressed=True,
                filters=filters,
            )
            return {
                "answer_md": (
                    "That one’s outside the scope of this portfolio. I focus on platform strategy, innovation, modernization, AI enablement, and delivery at scale."
                ),
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

    # 3) Vocab overlap safety: if overlap is ~zero AND Pinecone had suppressed matches earlier, abstain
    if token_overlap_ratio(
        question or "", _KNOWN_VOCAB
    ) < 0.05 and st.session_state.get("__pc_suppressed__"):
        log_offdomain(question or "", "no_overlap+low_conf")
        render_no_match_banner(
            reason="no_overlap+low_conf",
            query=question or "",
            overlap=overlap,
            suppressed=True,
            filters=filters,
        )
        return {
            "answer_md": (
                "That one’s outside the scope of this portfolio. I focus on platform strategy, innovation, modernization, AI enablement, and delivery at scale."
            ),
            "sources": [],
            "modes": {},
            "default_mode": "narrative",
        }

    # … then continue with your existing ranking + modes construction …

    # 4) Rank a small top‑N using light prompt overlap to prefer the best match
    ranked = sorted(
        pool, key=lambda s: _score_story_for_prompt(s, question), reverse=True
    )[:3]
    st.session_state["__last_ranked_sources__"] = [s["id"] for s in ranked]

    primary = ranked[0]
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

    # Conversational CTA (no explicit STAR/5P labels)
    cta = (
        "I can share this as a short narrative, highlight the key points, or go deeper into the details — "
        "just ask for **narrative**, **key points**, or **deep dive**."
    )
    answer_md = narrative + "\n\n" + cta

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
    st.session_state["last_answer"] = resp.get("answer_md") or resp.get("answer", "")
    st.session_state["last_sources"] = resp.get("sources", [])
    st.session_state["answer_modes"] = resp.get("modes", {})
    st.session_state["answer_mode"] = resp.get("default_mode", "narrative")


# --- Inline Ask MattGPT panel (for Stories) ---
def render_ask_panel(ctx: Optional[dict]):
    """Inline Ask MattGPT panel rendered inside the Stories detail column."""
    st.markdown("---")
    st.markdown("#### Ask MattGPT")
    if ctx:
        st.caption(
            f"Context: {ctx.get('title','')} — {ctx.get('client','')} • {ctx.get('role','')} • {ctx.get('domain','')}"
        )
    with st.expander("What is Ask MattGPT?", expanded=False):
        st.markdown(
            """
            Ask follow‑ups about the selected story. Use a starter question or type your own,
            then click **Generate answer**. The reply shows which stories it used.
            """
        )

    starters = [
        "Summarize this in 3 key bullets.",
        "What challenges were overcome?",
        "What trade-offs did we make and why?",
        "How could we replicate this elsewhere?",
    ]
    st.markdown('<div id="starter-chips">', unsafe_allow_html=True)
    cols = st.columns(min(3, len(starters)))
    for i, tip in enumerate(starters):
        with cols[i % len(cols)]:
            if st.button(tip, key=f"starter_inline_{i}", use_container_width=True):
                st.session_state["ask_input"] = tip
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

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
                resp = send_to_backend(prompt, st.session_state.get("filters", {}), ctx)
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
        with st.container(border=True):
            modes = st.session_state.get("answer_modes", {}) or {}
            current_mode = st.session_state.get("answer_mode", "narrative")

            # View switcher (only if we actually have mode content)
            if modes:
                cols = st.columns(3)
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

            # Choose content: selected mode if available, otherwise the raw last_answer
            content_md = (
                modes.get(current_mode)
                if modes
                else st.session_state.get("last_answer", "")
            )
            if content_md:
                st.markdown(content_md)

            # Sources row (clickable chips)
            sources = st.session_state.get("last_sources", [])
            if sources:
                render_sources_chips(sources, title="Sources")


# === Ask MattGPT helpers ===


def render_ask_starters(starters: list[str], key_prefix: str = "askstarter"):
    """Reusable starter chips row."""
    st.markdown('<div id="starter-chips">', unsafe_allow_html=True)
    cols = st.columns(min(3, len(starters)))
    for i, tip in enumerate(starters):
        with cols[i % len(cols)]:
            if st.button(tip, key=f"{key_prefix}_{i}", use_container_width=True):
                st.session_state["ask_input"] = tip
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_answer_block():
    """Reusable block that shows the last answer + mode switcher + sources."""
    if not st.session_state.get("last_answer"):
        return

    st.markdown("#### Answer")
    with st.container(border=True):
        modes = st.session_state.get("answer_modes", {}) or {}
        current_mode = st.session_state.get("answer_mode", "narrative")

        # Mode switcher
        if modes:
            cols = st.columns(3)
            for label, key in [
                ("Narrative", "narrative"),
                ("Key Points", "key_points"),
                ("Deep Dive", "deep_dive"),
            ]:
                with cols[["narrative", "key_points", "deep_dive"].index(key)]:
                    if st.button(label, key=f"ask_mode_{key}"):
                        st.session_state["answer_mode"] = key
                        st.rerun()
            st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

        # Content
        content_md = (
            modes.get(current_mode)
            if modes
            else st.session_state.get("last_answer", "")
        )
        if content_md:
            st.markdown(content_md)

        # Sources row
        sources = st.session_state.get("last_sources", [])
        if sources:
            render_sources_chips(sources, title="Sources")


def render_ask_tab():
    """Dedicated Ask tab UI using the shared helpers."""
    st.subheader("Ask MattGPT")
    st.caption(
        "Hi! Ask me for a story, summary, or paste a JD and I’ll tailor an answer."
    )

    starters = [
        "Tell me about leading a global payments transformation.",
        "How did you apply GenAI in a healthcare project?",
        "How have you driven innovation in your career?",
    ]
    render_ask_starters(starters, key_prefix="tabstarter")

    # Prompt input
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
        if st.button("Generate answer", key="ask_send_tab"):
            with st.spinner("Answering…"):
                resp = send_to_backend(
                    prompt, st.session_state.get("filters", {}), None
                )
            set_answer(resp)
    with c2:
        if st.button("Clear", key="ask_clear_tab"):
            st.session_state["seed_prompt"] = ""
            st.session_state["ask_input"] = ""
            st.session_state["last_answer"] = ""
            st.session_state["last_sources"] = []
            st.rerun()

    render_answer_block()


# =========================
# UI — Home / Stories / Ask / About
# =========================
clients, domains, roles, tags, personas_all = build_facets(STORIES)

# --- HOME ---
if st.session_state["active_tab"] == "Home":
    st.subheader("Welcome")
    st.caption("Pick a path to get started.")

    # Centered action buttons (option_menu pills with mono icons)
    from streamlit_option_menu import option_menu as _home_option_menu

    # Remember the last explicit choice the user made on the Home pills
    st.session_state.setdefault("__home_sel__", "Explore Stories")
    # Guard so the pills don't auto-navigate on the very first render
    st.session_state.setdefault("__home_first_mount__", True)
    _home_options = ["Explore Stories", "Ask MattGPT", "About Matt"]
    try:
        def_idx = _home_options.index(st.session_state["__home_sel__"])
    except ValueError:
        def_idx = 0

    sel = _home_option_menu(
        menu_title=None,
        options=_home_options,
        icons=["book", "chat-dots", "person"],
        default_index=def_idx,
        orientation="horizontal",
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
                "border": "none",
                "box-shadow": "1px",
                "margin-right": "12px",
            },
            "nav-link-selected": {
                "font-size": "1rem",
                "padding": "10px 14px",
                "border-radius": "8px",
                "color": "inherit",
                "white-space": "nowrap",
                "background-color": "transparent",
                "font-weight": "600",
                "border": "none",
                "box-shadow": "1px",
            },
        },
    )

    # Always navigate on selection (even if the same pill is clicked),
    # but skip on the very first render so the page doesn't auto-jump.
    if st.session_state.get("__home_first_mount__", True):
        # Record the selection and allow the user to click one of the pills
        st.session_state["__home_sel__"] = sel
        st.session_state["__home_first_mount__"] = False
    else:
        st.session_state["__home_sel__"] = sel
        st.session_state["active_tab"] = sel
        st.rerun()

    st.markdown(
        """
    ## About this app
    This is my interactive portfolio assistant — blending storytelling, strategy, and AI.  
    It showcases my career journey, career stories, and impact highlights.

    ### What you can do
    - **Explore Stories**: Browse curated projects with filters and details.  
    - **Ask MattGPT**: Get AI-powered answers about my work, challenges, and outcomes.  
    - **About Matt**: Learn about my background, leadership style, and values.  

    ### Why I built this
    1. To demonstrate hands-on GenAI/LLM engineering skills.  
    2. To showcase practical expertise in building portfolio assistants.  
    3. To highlight how I bridge **strategy, engineering, and storytelling**.
    """
    )


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

    with st.container(border=True):
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
    view = []
    if F["q"].strip():
        ov = token_overlap_ratio(F["q"], _KNOWN_VOCAB)
        reason = is_nonsense(F["q"]) or (ov < 0.03 and f"overlap:{ov:.2f}")
        if reason:
            st.session_state["__nonsense_reason__"] = reason
            st.session_state["__pc_suppressed__"] = True
            st.session_state["last_results"] = STORIES[:5]
            show_out_of_scope(reason, route="Explore Stories", query=F["q"], overlap=ov)
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
            st.markdown(
                '<div class="sticky-detail detail-pane">', unsafe_allow_html=True
            )
            detail = get_context_story()
            if detail:
                story_card(detail, idx=0)
                if st.button("Ask MattGPT about this", key="ask_from_detail"):
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
                story_card(s, offset + i)

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
    st.subheader("Ask MattGPT")

    # Context banner (if a story is selected on Stories tab)
    ctx = get_context_story()
    if ctx:
        st.caption(
            f"Context: {ctx.get('title','')} — {ctx.get('client','')} • {ctx.get('role','')} • {ctx.get('domain','')}"
        )

    # Initialize chat history once
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": "Hi! Ask me for a story, a summary, or paste a JD and I'll tailor an answer.",
            }
        ]

    # Seed from any prior Ask chips
    if st.session_state.get("seed_prompt"):
        # Push the seed as a user message and clear it so we don't loop
        seed = st.session_state.pop("seed_prompt")
        st.session_state.chat_messages.append({"role": "user", "content": seed})
        # Generate an immediate answer
        resp = send_to_backend(seed, st.session_state.get("filters", {}), ctx)
        ans = _sanitize_answer(resp.get("answer_md", ""))
        st.session_state.chat_messages.append({"role": "assistant", "content": ans})
        st.session_state["last_answer"] = ans
        st.session_state["last_sources"] = resp.get("sources", [])

    # Render chat transcript
    for m in st.session_state.chat_messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Chat input (ChatGPT-like). Note: no default text is supported by Streamlit.
    user_input = st.chat_input("Ask for a story, summary, or paste a JD to tailor…")
    if user_input:
        # Append user
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # --- Command router for simple follow-up commands ---
        cmd = re.sub(r"\s+", " ", user_input.strip().lower())
        cmd_map = {
            "narrative": "narrative",
            "key points": "key_points",
            "keypoints": "key_points",
            "deep dive": "deep_dive",
            "deep-dive": "deep_dive",
            "details": "deep_dive",
        }
        if cmd in cmd_map and (
            ctx
            or st.session_state.get("active_story")
            or st.session_state.get("last_sources")
        ):
            # Resolve target story: prefer current context; fall back to last primary source
            target = ctx
            if not target:
                sid = st.session_state.get("active_story")
                if not sid:
                    srcs = st.session_state.get("last_sources") or []
                    if srcs:
                        sid = srcs[0].get("id")
                if sid:
                    target = next((x for x in STORIES if x.get("id") == sid), None)

            if target:
                # Build mode texts for this specific story
                modes_local = story_modes(target)
                key = cmd_map[cmd]
                heading = {
                    "narrative": "Narrative",
                    "key_points": "Key points",
                    "deep_dive": "Deep dive",
                }[key]

                # Compose and render this turn immediately
                answer_md = (
                    f"**{heading} for _{target.get('title','')} — {target.get('client','')}_**\n\n"
                    + modes_local.get(key, "")
                )
                with st.chat_message("assistant"):
                    st.markdown(answer_md)

                # Persist modes so the global view switcher can toggle without re-retrieval
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

                # End this turn early (skip generic retrieval below)
                st.stop()

        # Assistant typing
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                resp = send_to_backend(
                    user_input, st.session_state.get("filters", {}), ctx
                )
                answer_md = _sanitize_answer(resp.get("answer_md", ""))
                st.markdown(answer_md)

                # Show sources inline for convenience
            sources = resp.get("sources", [])
            if sources:
                with st.expander("View details from these stories"):
                    for src in sources:
                        s = next((x for x in STORIES if x.get("id") == src["id"]), None)
                        if not s:
                            continue
                        with st.container(border=True):
                            st.markdown(
                                f"**{s.get('title','')}** — {s.get('client','')}"
                            )
                            st.caption(f"{s.get('role','')} • {s.get('domain','')}")
                            # Short summary paragraph so they know what they’ll get
                            st.markdown(build_5p_summary(s))
                            # “Show details” toggle
                            if st.button(
                                f"Show details — {s.get('title','')}",
                                key=f"src_detail_{s['id']}",
                            ):
                                st.session_state["active_story"] = s["id"]
                                st.session_state["show_ask_panel"] = True
                                goto("Explore Stories")

        # Persist the assistant turn
        st.session_state.chat_messages.append(
            {"role": "assistant", "content": answer_md}
        )
        # Offer view switcher for the last answer (if modes available)
        modes = st.session_state.get("answer_modes", {})
        if modes:
            st.markdown("###### View")
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("Narrative", key="view_narrative"):
                    st.session_state["answer_mode"] = "narrative"
            with c2:
                if st.button("Key points", key="view_keypoints"):
                    st.session_state["answer_mode"] = "key_points"
            with c3:
                if st.button("Deep dive", key="view_deepdive"):
                    st.session_state["answer_mode"] = "deep_dive"

            # Show the selected mode as a follow-up assistant bubble (no new retrieval)
            mode_key = st.session_state.get("answer_mode", "narrative")
            mode_text = modes.get(mode_key)
            if mode_text:
                with st.chat_message("assistant"):
                    resp = send_to_backend(
                        user_input, st.session_state.get("filters", {}), ctx
                    )
                    ans = _sanitize_answer(
                        resp.get("answer_md", resp.get("answer", ""))
                    )
                    st.markdown(ans)
                    set_answer(resp)

# --- ABOUT ---
elif st.session_state["active_tab"] == "About Matt":
    st.subheader("About Matt")
    st.caption("A human-centered portfolio + AI assistant.")
    st.markdown(
        """
**What this is** — A simple place to browse outcomes (Stories) and ask follow‑ups (Ask MattGPT).

**How to use it**
- **Stories:** Filter by audience, client, domain, role, tags, or search keywords.
- **Ask MattGPT:** Click **Ask MattGPT about this** on any story to preload context, then type a question.
  Debounce will auto-run when you pause typing; you can also press **Send**.

**What’s next**
- Real embeddings + Pinecone metadata snippets
- Cleaner card/list theming
- Optional keep‑alive
"""
    )
