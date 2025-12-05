import json
import os
import re
from typing import Any

import streamlit as st

st.set_page_config(page_title="Ask MattGPT — Hybrid Mock", layout="wide")
st.session_state.setdefault("ask_mode", "Narrative")  # for the Pills view

# Bootstrap mono icons (same as app)
st.markdown(
    "<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css'>",
    unsafe_allow_html=True,
)

# --- data wiring (easy button): load real STAR + 5P if available ---

CANDIDATE_JSONL = [
    "echo_star_stories.jsonl",
    os.path.join(os.path.dirname(__file__), "echo_star_stories.jsonl"),
    os.path.join(os.path.dirname(__file__), "data", "echo_star_stories.jsonl"),
]

_DEF_ICONS = {
    "innovation": "bi-lightning",
    "sales": "bi-graph-up",
    "talent": "bi-diagram-3",
    "health": "bi-hospital",
    "bank": "bi-bank",
}

Story = dict[str, Any]


def _read_jsonl(paths: list[str]) -> list[Story]:
    for p in paths:
        try:
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    return [json.loads(line) for line in f if line.strip()]
        except Exception as e:
            print(f"DEBUG JSONL read failed for {p}: {e}")
    return []


def _first(story: Story, keys: list[str], default: str = "") -> str:
    """Return the first non-empty string value for any of the candidate keys.
    Looks up keys case-insensitively and supports basic numeric-to-string fallback.
    """
    if not story:
        return default
    # direct (original-case) hit first
    for k in keys:
        if k in story and isinstance(story[k], str) and story[k].strip():
            return story[k].strip()
    # build a lowercased view of keys -> values
    lowered: dict[str, str] = {}
    for k, v in story.items():
        if isinstance(v, str) and v.strip():
            lowered[k.lower()] = v.strip()
        elif isinstance(v, (int, float)):
            lowered[k.lower()] = str(v)
    for k in keys:
        v = lowered.get(k.lower())
        if v:
            return v
    return default


def _nest(story: Story, nest_keys: list[str]) -> dict[str, Any]:
    """Return the first dict value for any of the candidate keys (case-insensitive)."""
    if not story:
        return {}
    for k in nest_keys:
        v = story.get(k)
        if isinstance(v, dict):
            return v
    lowered: dict[str, Any] = {
        k.lower(): v for k, v in story.items() if isinstance(v, dict)
    }
    for k in nest_keys:
        v = lowered.get(k.lower())
        if isinstance(v, dict):
            return v
    return {}


def _sentences(text: str, max_items: int = 3) -> list[str]:
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p][:max_items]


# --- Helpers for sentence/shorten ---
def _first_sentence(text: str) -> str:
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return parts[0]


def _shorten(text: str, max_chars: int = 80) -> str:
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars].rsplit(" ", 1)[0]
    return cut + "…"


def _pick_icon(story: Story) -> str:
    txt = " ".join(
        [
            _first(story, ["domain", "category", "tags"], ""),
            _first(story, ["client"], ""),
            _first(story, ["Title", "title"], ""),
        ]
    ).lower()
    if any(w in txt for w in ["liquid studio", "innovation", "prototype", "cic"]):
        return _DEF_ICONS["innovation"]
    if any(w in txt for w in ["sales", "growth", "pipeline"]):
        return _DEF_ICONS["sales"]
    if any(w in txt for w in ["talent", "scale", "hiring", "org"]):
        return _DEF_ICONS["talent"]
    if any(w in txt for w in ["kaiser", "health", "care"]):
        return _DEF_ICONS["health"]
    if any(w in txt for w in ["rbc", "bank", "payments"]):
        return _DEF_ICONS["bank"]
    return "bi-journal-text"


# Load stories (best-effort)
_STORIES = _read_jsonl(CANDIDATE_JSONL)

# Filter to plausible top matches for the prompt (simple keyword heuristic)
PROMPT = "How have you driven innovation in your career?"
KEYWORDS = ["innovation", "cic", "liquid studio", "prototype", "modernization"]


def _score(st: Story) -> int:
    blob = " ".join([str(v) for v in st.values()])[:10000].lower()
    return sum(1 for k in KEYWORDS if k in blob)


_TOP = sorted(_STORIES, key=_score, reverse=True)[:3] if _STORIES else []

# Derive narrative + highlights + case study from real fields if present
primary = _TOP[0] if _TOP else {}

fivep = _nest(primary, ["5p", "fivep", "fiveP", "FiveP"])
star = _nest(primary, ["star", "STAR"]) if primary else {}

purpose = _first(fivep, ["Purpose", "purpose"]) or _first(primary, ["purpose"])
performance = _first(fivep, ["Performance", "performance"]) or _first(
    primary, ["performance"]
)
summary5p = _first(fivep, ["Summary", "summary", "5PSummary", "fivep_summary"])

# STAR fields first (so `action` exists before we build process)
situation = _first(star, ["Situation", "situation"]) or _first(primary, ["situation"])
task = _first(star, ["Task", "task"]) or _first(primary, ["task"])
action = _first(star, ["Action", "action"]) or _first(primary, ["action"])
result = _first(star, ["Result", "result"]) or _first(primary, ["result"])

# Pull a concrete process/how from 5P or Action
process5p = (
    _first(fivep, ["Process", "process", "Approach", "approach", "Method", "method"])
    or _first(primary, ["approach", "Approach"])
    or action
)

narrative_head = _first(
    primary,
    ["Title", "title", "headline"],
    "Driving Innovation through Cloud Innovation Center and Liquid Studio",
)

# Impact line comes from 5P Performance (or STAR Result)
impact_sentence = _first_sentence(performance) or _first_sentence(result)
narrative_impact = f"Impact: {impact_sentence}" if impact_sentence else ""

# Purpose + Process in one flowing sentence
purpose_sentence = _first_sentence(purpose) or _first_sentence(summary5p)
how_sentence = _first_sentence(process5p) if process5p else ""

# Natural narrative body (Purpose + Process in one flowing sentence)
_body_parts = []
if purpose_sentence:
    _body_parts.append(purpose_sentence.rstrip("."))
if how_sentence:
    _body_parts.append(how_sentence.rstrip("."))

narrative_body = ". ".join(_body_parts)
if narrative_body and not narrative_body.endswith("."):
    narrative_body += "."

# Build Highlights from Performance sentences; fall back to Action/Result
_highlights: list[str] = []
for s in _sentences(performance, 3):
    if s:
        _highlights.append(s)
if not _highlights:
    for s in _sentences(result, 3):
        if s:
            _highlights.append(s)
if not _highlights and action:
    _highlights.append(action)

# Sources row from top matches (Client — Title). Accept common variants; fallback to demo chips if empty.
sources = []
for stx in _TOP:
    client = _first(
        stx, ["Client", "client", "company", "org", "organization"], ""
    ).strip()
    raw_title = _first(
        stx, ["Title", "title", "Story_Title", "story_title", "headline", "name"], ""
    )
    if not raw_title:
        continue  # require a usable title for clean chips
    title_clean = _shorten(_first_sentence(raw_title), 72)
    sources.append(
        {
            "id": str(_first(stx, ["id", "story_id", "StoryID"], "")),
            "client": client,
            "title": title_clean,
            "icon": _pick_icon(stx),
        }
    )

# Hardcoded fallback so the mock always renders something useful
if not sources:
    sources = [
        {
            "id": "61",
            "client": "Accenture — Liquid Studio",
            "title": "Innovation Lab & Rapid Prototyping",
            "icon": "bi-lightning",
        },
        {
            "id": "36",
            "client": "Accenture — Cloud Innovation Center",
            "title": "Sales Strategy & Growth",
            "icon": "bi-graph-up",
        },
        {
            "id": "100",
            "client": "Accenture — Cloud Innovation Center",
            "title": "Scaling Talent & Delivery Excellence",
            "icon": "bi-diagram-3",
        },
    ]

# --- minimal CSS (cards, badges, dividers) ---
st.markdown(
    """
<style>
.card { border:1px solid rgba(0,0,0,.10); background:rgba(0,0,0,.03); border-radius:12px; padding:16px 18px; }
@media (prefers-color-scheme: dark){ .card{background:rgba(255,255,255,.06); border-color:rgba(255,255,255,.12);} }
.h1 { font-weight:700; font-size:1.05rem; margin:0 0 6px 0; }
.impact { font-weight:600; opacity:.95; margin:2px 0 8px 0; }
.body { line-height:1.45; }
.badge-row{ display:flex; flex-wrap:wrap; gap:8px; margin:8px 0 0; }
.badge{ display:inline-flex; align-items:center; gap:8px; font-size:13px; line-height:1.1;
  padding:6px 10px; border-radius:999px; border:1px solid rgba(0,0,0,.10); background:rgba(0,0,0,.04); white-space:nowrap; }
@media (prefers-color-scheme: dark){ .badge{ background:rgba(255,255,255,.06); border-color:rgba(255,255,255,.12);} }
.kplist li { margin-bottom:6px; }
.hr { height:1px; background:linear-gradient(to right, rgba(0,0,0,.12), rgba(0,0,0,.04)); margin:10px 0 14px; border:0; }
.section { font-weight:700; opacity:.9; margin:10px 0 6px; }
.subtle { opacity:.75; }
</style>
""",
    unsafe_allow_html=True,
)

prompt = PROMPT


def render_sources_row(title="Sources"):
    items = [s for s in sources if (s.get("client") or s.get("title"))]
    chips = "".join(
        f"<span class='badge'><i class='bi {s['icon']}'></i>{(s.get('client') + ' — ' if s.get('client') else '')}{s.get('title','')}</span>"
        for s in items
    )
    st.markdown(f"<div class='section'>{title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='badge-row'>{chips}</div>", unsafe_allow_html=True)


# ========== LAYOUT ==========
st.markdown("### Ask MattGPT")
st.caption(f"Prompt: **{prompt}**")

(tab2,) = st.tabs(["Pills (clean CX)"])

# --- PILLS: narrative / key points / deep dive (no new search, just view switch) ---
with tab2:
    # Answer card (same top)
    st.markdown(
        "<div class='card'>"
        f"<div class='h1'>{narrative_head}</div>"
        f"<div class='impact'>{narrative_impact}</div>"
        f"<div class='body'>{narrative_body}</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Pills control
    if "segmented_control" in dir(st):
        mode = st.segmented_control(
            "",
            ["Narrative", "Key Points", "Deep Dive"],
            selection_mode="single",
            default=st.session_state.get("ask_mode", "Narrative"),
        )
        if mode != st.session_state.get("ask_mode"):
            st.session_state["ask_mode"] = mode
    else:
        cols = st.columns(3)
        for i, label in enumerate(["Narrative", "Key Points", "Deep Dive"]):
            with cols[i]:
                if st.button(label, key=f"mode_{label}"):
                    st.session_state["ask_mode"] = label

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    mode = st.session_state.get("ask_mode", "Narrative")

    if mode == "Narrative":
        st.markdown("**Story**")
        if narrative_body:
            st.write(narrative_body)
        else:
            st.markdown("- Narrative data missing (Purpose/Process).")
    elif mode == "Key Points":
        st.markdown("**Highlights**")
        if _highlights:
            for h in _highlights:
                st.markdown(f"- {h}")
        else:
            st.markdown(
                "- Led rapid prototyping and lean rituals to accelerate value realization."
            )
    else:
        st.markdown("**Case Study (exemplar)**")
        if any([situation, task, action, result]):
            if situation:
                st.markdown(f"- **Situation:** {situation}")
            if task:
                st.markdown(f"- **Task:** {task}")
            if action:
                st.markdown(f"- **Action:** {action}")
            if result:
                st.markdown(f"- **Result:** {result}")
        else:
            st.markdown(
                "- Detailed STAR data not found in JSONL; add Situation/Task/Action/Result to see the full case study here."
            )

    render_sources_row()
