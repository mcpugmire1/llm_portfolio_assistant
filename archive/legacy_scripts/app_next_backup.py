# app_next.py — Next-gen UI (Home / Stories / Ask / About)
# - Clean, centered layout without sidebar
# - Pinecone-first (guarded) + local fallback search
# - Debounced “Ask MattGPT” with starter chips
# - Compact List view by default, Card view optional
# - Badges + strongest-metric summary

import json
import os
import re
import time

import pandas as pd
import streamlit as st

# optional: row-click table
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

    _HAS_AGGRID = True
except Exception:
    _HAS_AGGRID = False
st.set_page_config(page_title="MattGPT — Story Cards", page_icon="🎯", layout="wide")

# --------- Simple, reliable state-driven navigation ---------
TAB_NAMES = ["Home", "Stories", "About Matt"]

# single source of truth for the current tab
st.session_state.setdefault("active_tab", "Home")


def goto(tab_name: str):
    # helper you can call from anywhere (buttons, badges, etc.)
    st.session_state["active_tab"] = tab_name
    # queue nav_radio update for the next render cycle (avoids Streamlit widget mutation error)
    st.session_state["set_nav_radio"] = tab_name
    st.rerun()


def on_ask_this_story(s: dict):
    """Set context to a specific story and open the Ask panel inside Stories."""
    st.session_state["active_story"] = s.get("id")
    st.session_state["seed_prompt"] = (
        f"How were these outcomes achieved for {s.get('client','')} — {s.get('title','')}? "
        "Focus on tradeoffs, risks, and replicable patterns."
    )
    # Show inline Ask panel under the detail card
    st.session_state["show_ask_panel"] = True
    # Navigate to Stories (3-tab design)
    st.session_state["active_tab"] = "Stories"
    st.session_state["set_nav_radio"] = "Stories"
    st.session_state["page_offset"] = 0
    st.rerun()


# top nav control (segmented/radio-style)
# Sync any pending nav change before rendering the nav widget
if st.session_state.get("set_nav_radio"):
    # apply the deferred change and remove the temp flag
    st.session_state["nav_radio"] = st.session_state.pop("set_nav_radio")
else:
    # ensure nav_radio exists so radio has a stable default
    st.session_state.setdefault("nav_radio", st.session_state["active_tab"])
_nav_choice = st.radio(
    "Navigation",
    TAB_NAMES,
    index=TAB_NAMES.index(st.session_state["active_tab"]),
    horizontal=True,
    key="nav_radio",
)

# update active tab if user clicks in the nav
if _nav_choice != st.session_state["active_tab"]:
    st.session_state["active_tab"] = _nav_choice
    st.rerun()
# ------------------------------------------------------------


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

_PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
_PINECONE_INDEX = os.getenv("PINECONE_INDEX", "mattgpt-stories")
_PC = None
_PC_INDEX = None


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
def _load_jsonl(path: str) -> list[dict] | None:
    try:
        if not os.path.exists(path):
            return None
        out = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                out.append(json.loads(line))
        return out or None
    except Exception:
        return None


import os
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
.detail-pane { font-size: 1.0rem; }

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
.results-count { font-weight:600; margin-right:8px; }

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


def should_run_after_pause(key: str, value: str, wait: float = 0.6) -> bool:
    ts_key = f"__deb_ts__{key}"
    val_key = f"__deb_val__{key}"
    now = time.time()
    prev_val = st.session_state.get(val_key)
    if value != prev_val:
        st.session_state[val_key] = value
        st.session_state[ts_key] = now
        return False
    return (now - st.session_state.get(ts_key, 0.0)) >= wait


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


def render_list(items: list[str] | None):
    for x in items or []:
        st.write(f"- {x}")


def render_outcomes(items: list[str] | None):
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


def strongest_metric_line(s: dict) -> str | None:
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


def build_5p_summary(s: dict, max_chars: int = 200) -> str:
    """
    Prefer the curated 5P summary that already exists in the source data.
    Fall back to a synthesized one-liner only if the field is absent/empty.
    """
    # Primary: curated summary from JSONL (supports both "5PSummary" and "5p_summary")
    curated = (s.get("5PSummary") or s.get("5p_summary") or "").strip()
    if curated:
        return curated

    # Fallback: synthesize from WHY/HOW/metrics (keeps prior behavior for demo rows)
    why = (s.get("why") or "").strip()
    how = ", ".join((s.get("how") or [])[:2]).strip()
    metric_line = strongest_metric_line(s)

    parts = []
    if why:
        parts.append(
            why if why[:2].lower() in ("to", "in") else (why[:1].lower() + why[1:])
        )
    if how:
        parts.append(f"by {how}")
    if metric_line:
        parts.append(f"resulting in {metric_line}")

    sent = ", ".join([p for p in parts if p]).strip()
    if sent and not sent.endswith("."):
        sent += "."
    return sent


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
                with st.container(border=True):
                    st.markdown(
                        '<span class="field-label">What Was Happening</span>',
                        unsafe_allow_html=True,
                    )
                    render_list(s.get("star", {}).get("situation", []))
                    st.markdown(
                        '<span class="field-label">What We Wanted to Achieve</span>',
                        unsafe_allow_html=True,
                    )
                    render_list(s.get("star", {}).get("task", []))
                    st.markdown(
                        '<span class="field-label">What We Did About It</span>',
                        unsafe_allow_html=True,
                    )
                    render_list(s.get("star", {}).get("action", []))
                    st.markdown(
                        '<span class="field-label">The Difference It Made</span>',
                        unsafe_allow_html=True,
                    )
                    render_list(s.get("star", {}).get("result", []))

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

        # Optional Pinecone snippet if present (metadata.summary)
        snippet = st.session_state["__pc_snippets__"].get(s["id"])
        if snippet:
            st.caption(snippet)

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
def _embed(text: str) -> list[float]:
    """Deterministic stub embedder so the app runs without external models."""
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
) -> list[dict] | None:
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
        res = idx.query(
            vector=qvec, top_k=top_k, include_metadata=True, filter=pc_filter or None
        )
        hits = []
        st.session_state["__pc_last_ids__"].clear()
        st.session_state["__pc_snippets__"].clear()
        for m in res.matches:
            meta = (m.metadata or {}) if hasattr(m, "metadata") else {}
            sid = meta.get("id")
            score = float(getattr(m, "score", 0.0) or 0.0)
            if not sid:
                continue
            # Find the full record locally for now (we’re not storing everything in metadata)
            hit = next((s for s in STORIES if s.get("id") == sid), None)
            if hit:
                hits.append(
                    {"story": hit, "score": score, "snippet": meta.get("summary")}
                )
        return hits
    except Exception:
        return None


def semantic_search(query: str, filters: dict):
    """Pinecone-first with confidence threshold; fallback to local filters; persists snippet/score for UI."""
    hits = pinecone_semantic_search(query, filters)
    st.session_state["__pc_suppressed__"] = False
    if hits is not None:
        confident = [h for h in hits if h["score"] >= PINECONE_MIN_SIM]
        if confident:
            st.session_state["__pc_last_ids__"] = {
                h["story"]["id"]: h["score"] for h in confident
            }
            st.session_state["__pc_snippets__"] = {
                h["story"]["id"]: (h["snippet"] or build_5p_summary(h["story"]))
                for h in confident
            }
            return [
                h["story"] for h in confident if matches_filters(h["story"], filters)
            ]
        else:
            st.session_state["__pc_suppressed__"] = bool(query.strip())
    return [s for s in STORIES if matches_filters(s, filters)]


# =========================
# Ask backend (stub)
# =========================
def rag_answer(question: str, filters: dict):
    # take up to 3 best local matches under current filters (stub for now)
    hits = [s for s in STORIES if matches_filters(s, filters)][:3]
    if not hits:
        return {
            "answer_md": "_I couldn’t find a strong match yet. Try adjusting filters or keywords, or choose a story in **Stories** and come back._",
            "sources": [],
        }
    # Compose a short, scannable answer in Markdown
    bullets = "\n".join(f"- **{h['title']}** — {h['client']}" for h in hits)
    answer_md = (
        "### Draft perspective\n"
        "Based on similar engagements in your portfolio:\n\n"
        f"{bullets}\n\n"
        "_Ask a follow‑up to refine, or open a source below to review details._"
    )
    sources = [
        {"id": h["id"], "title": h["title"], "client": h["client"]} for h in hits
    ]
    return {"answer_md": answer_md, "sources": sources}


def send_to_backend(prompt: str, filters: dict, ctx: dict | None):
    return rag_answer(prompt, filters)


def set_answer(resp: dict):
    st.session_state["last_answer"] = resp.get("answer_md") or resp.get("answer", "")
    st.session_state["last_sources"] = resp.get("sources", [])


# --- Inline Ask MattGPT panel (for Stories) ---
def render_ask_panel(ctx: dict | None):
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
            st.markdown(st.session_state["last_answer"])
            sources = st.session_state.get("last_sources", [])
            if sources:
                st.markdown("**Grounded in**")
                cols2 = st.columns(max(1, min(3, len(sources))))
                for i, src in enumerate(sources):
                    label = f"🔎 {src['title']} — {src.get('client','')}"
                    with cols2[i % len(cols2)]:
                        if st.button(label, key=f"open_src_inline_{src['id']}"):
                            st.session_state["active_story"] = src["id"]
                            st.session_state["show_ask_panel"] = True
                            st.session_state["active_tab"] = "Stories"
                            st.session_state["set_nav_radio"] = "Stories"
                            st.rerun()


# =========================
# UI — Home / Stories / Ask / About
# =========================
clients, domains, roles, tags, personas_all = build_facets(STORIES)

# --- HOME ---
if st.session_state["active_tab"] == "Home":
    st.subheader("Welcome")
    st.caption("Pick a path to get started.")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📖 Explore Stories", use_container_width=True):
            goto("Stories")
    with c2:
        if st.button("💬 Ask MattGPT", use_container_width=True):
            st.session_state["show_ask_panel"] = True
            goto("Stories")
    with c3:
        if st.button("👤 About Matt", use_container_width=True):
            goto("About Matt")

    st.markdown("##### Quick search")

    # ----- Quick search (Home) -----
    q_global = st.text_input(
        "Search across stories",
        value=st.session_state["filters"].get("q", ""),
        placeholder="Try: payments modernization, governance, OKRs…",
        label_visibility="collapsed",
        key="home_global_q",
    )

    if q_global != st.session_state["filters"].get("q", ""):
        # Reset ALL other filters so quick search isn't silently constrained
        st.session_state["filters"] = {
            "personas": [],
            "clients": [],
            "domains": [],
            "roles": [],
            "tags": [],
            "q": q_global,
            "has_metric": False,
        }

        # Reset domain category UI so it doesn't look 'stuck'
        st.session_state["facet_domain_group"] = "All"

        # Make the debounce appear satisfied and seed paging
        st.session_state["__deb_val__story_search"] = q_global
        st.session_state["__deb_ts__story_search"] = time.time() - 1.0
        st.session_state["page_offset"] = 0

        # Precompute results so Stories shows them immediately
        st.session_state["last_results"] = semantic_search(
            q_global, st.session_state["filters"]
        )
        st.session_state["__last_q__"] = q_global

        # Jump to Stories (this triggers a rerun)
        goto("Stories")

# --- STORIES ---
elif st.session_state["active_tab"] == "Stories":
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

    # --- Debounced semantic search (Pinecone-first with fallback) ---
    st.session_state.setdefault("__last_q__", F["q"])
    if should_run_after_pause("story_search", F["q"], wait=0.6):
        view = semantic_search(F["q"], F)
        st.session_state["last_results"] = view
        if F["q"] != st.session_state["__last_q__"]:
            st.session_state["page_offset"] = 0
            st.session_state["__last_q__"] = F["q"]
    else:
        view = st.session_state.get("last_results", [])
        if F["q"] and F["q"] != st.session_state.get("__last_q__", ""):
            st.caption("⏳ searching… (waiting for you to pause)")

    # --- Active chips + result count ---
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
                    on_ask_this_story(detail)
            else:
                st.info("Select a story on the left to view details.")
            if detail and st.session_state.get("show_ask_panel"):
                render_ask_panel(detail)
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
