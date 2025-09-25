# ui/components.py
from __future__ import annotations
import streamlit as st

def css_once():
    flag = "__ui_css_once__"
    if st.session_state.get(flag):
        return
    st.session_state[flag] = True

    # 1) Load Bootstrap Icons once, globally
    st.markdown(
        "<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css'>",
        unsafe_allow_html=True,
    )

    # 2) Then inject your unified pill/chip CSS
    st.markdown("""
<style>
/* ====== Pills & Sources: single source of truth ====== */

/* Define a single token and reuse it in **both** places */
:root { --pill-font-size: 0.90rem; --pill-pad-y: 4px; --pill-pad-x: 10px; }  /* shared tokens used by pills + source chips */
/* Sidebar reset so sample buttons aren’t pill-sized */
                
[data-testid="stSidebar"] div.stButton > button{
  width:100% !important;
  justify-content:flex-start !important;
  min-width:0 !important;
  border-radius:8px !important;
  padding:8px 12px !important;
  font-weight:500 !important;
  background:rgba(255,255,255,.06) !important;
  border:1px solid rgba(255,255,255,.14) !important;
}
/* Fallback (MAIN AREA ONLY): give Streamlit buttons the pill look */
[data-testid="stAppViewContainer"] div.stButton > button {
  border-radius:999px!important;
  padding:var(--pill-pad-y) var(--pill-pad-x)!important;
  font-weight:600!important;
  font-size:var(--pill-font-size)!important;  /* using the token */
  line-height:1.2!important;
  border:1px solid rgba(255,255,255,.22)!important;
  background:rgba(255,255,255,.04)!important;
  box-shadow:none!important;
  width:auto!important;
  min-width:140px!important;
  height:auto!important;
  white-space:nowrap!important;
  overflow:hidden!important;
  text-overflow:ellipsis!important;
  font-family:inherit!important;
  cursor:pointer!important;
}
/* Fallback for newer baseButton path (MAIN AREA ONLY) */
[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"] {
  border-radius:999px!important;
  padding:var(--pill-pad-y) var(--pill-pad-x)!important;
  font-weight:600!important;
  font-size:var(--pill-font-size)!important;
  line-height:1.2!important;
  border:1px solid rgba(255,255,255,.22)!important;
  background:rgba(255,255,255,.04)!important;
  box-shadow:none!important;
  width:auto!important;
  min-width:140px!important;
  height:auto!important;
  white-space:nowrap!important;
  overflow:hidden!important;
  text-overflow:ellipsis!important;
  font-family:inherit!important;
  cursor:pointer!important;
}
                
/* Pills (reference) */
.pill-container .stButton > button{
  border-radius:999px!important;
  padding:var(--pill-pad-y) var(--pill-pad-x)!important;
  font-weight:600!important;
  font-size:var(--pill-font-size)!important;
  line-height:1.2!important;
  border:1px solid rgba(255,255,255,.22)!important;
  background:rgba(255,255,255,.04)!important;
  box-shadow:none!important;
  min-width:140px!important;
  height:auto!important;
  font-family:inherit!important;
}
.pill-container .stButton > button:hover{
  background:rgba(255,255,255,.08)!important;
  border-color:rgba(255,255,255,.30)!important;
}
.pill-container .stButton > button:focus-visible{
  outline:2px solid rgba(255,255,255,.35)!important;
  outline-offset:1px!important;
}

/* Sources chips — EXACT same look as pills (covers both render paths and anchor fallback) */
[data-mpg-srcchips] a,
[data-mpg-srcchips] button,
[data-mpg-srcchips] div.stButton > button,
[data-mpg-srcchips] [data-testid="baseButton-secondary"] {
  border-radius: 999px !important;
  padding: var(--pill-pad-y) var(--pill-pad-x) !important;
  font-weight: 600 !important;
  font-size: var(--pill-font-size) !important;
  line-height: 1.2 !important;
  border: 1px solid rgba(255,255,255,.22) !important;
  background: rgba(255,255,255,.04) !important;
  box-shadow: none !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: auto !important;
  min-width: 140px !important;
  height: auto !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  font-family: inherit !important;
  cursor: pointer !important;
}

[data-mpg-srcchips] a:hover,
[data-mpg-srcchips] button:hover,
[data-mpg-srcchips] div.stButton > button:hover,
[data-mpg-srcchips] [data-testid="baseButton-secondary"]:hover {
  background: rgba(255,255,255,.08) !important;
  border-color: rgba(255,255,255,.30) !important;
}

[data-mpg-srcchips] a:focus-visible,
[data-mpg-srcchips] button:focus-visible,
[data-mpg-srcchips] div.stButton > button:focus-visible,
[data-mpg-srcchips] [data-testid="baseButton-secondary"]:focus-visible {
  outline: 2px solid rgba(255,255,255,.35) !important;
  outline-offset: 1px !important;
}

/* --- Fallback: style the Streamlit button that follows our marker span --- */
/* Classic st.button path */
.srcchip-flag ~ div.stButton > button {
  border-radius: 999px !important;
  padding: var(--pill-pad-y) var(--pill-pad-x) !important;
  font-weight: 600 !important;
  font-size: var(--pill-font-size) !important;
  line-height: 1.2 !important;
  border: 1px solid rgba(255,255,255,.22) !important;
  background: rgba(255,255,255,.04) !important;
  box-shadow: none !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: auto !important;
  min-width: 140px !important;
  height: auto !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  font-family: inherit !important;
  cursor: pointer !important;
}
.srcchip-flag ~ div.stButton > button:hover {
  background: rgba(255,255,255,.08) !important;
  border-color: rgba(255,255,255,.30) !important;
}
.srcchip-flag ~ div.stButton > button:focus-visible {
  outline: 2px solid rgba(255,255,255,.35) !important;
  outline-offset: 1px !important;
}

/* Newer baseButton path Streamlit uses on Cloud */
.srcchip-flag ~ [data-testid="baseButton-secondary"],
.srcchip-flag ~ button[data-testid="baseButton-secondary"] {
  border-radius: 999px !important;
  padding: var(--pill-pad-y) var(--pill-pad-x) !important;
  font-weight: 600 !important;
  font-size: var(--pill-font-size) !important;
  line-height: 1.2 !important;
  border: 1px solid rgba(255,255,255,.22) !important;
  background: rgba(255,255,255,.04) !important;
  box-shadow: none !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: auto !important;
  min-width: 140px !important;
  height: auto !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  font-family: inherit !important;
  cursor: pointer !important;
}
.srcchip-flag ~ [data-testid="baseButton-secondary"]:hover,
.srcchip-flag ~ button[data-testid="baseButton-secondary"]:hover {
  background: rgba(255,255,255,.08) !important;
  border-color: rgba(255,255,255,.30) !important;
}
.srcchip-flag ~ [data-testid="baseButton-secondary"]:focus-visible,
.srcchip-flag ~ button[data-testid="baseButton-secondary"]:focus-visible {
  outline: 2px solid rgba(255,255,255,.35) !important;
  outline-offset: 1px !important;
}

/* === Ultra‑robust fallback: main content buttons that are Source chips ===
   Streamlit sometimes wraps st.button differently (classic vs. baseButton).
   These selectors target any MAIN‑AREA button whose aria‑label contains
   "Match", which we only use for Sources chips. (Sidebar is excluded by
   scoping to stAppViewContainer.) */
[data-testid="stAppViewContainer"] button[aria-label*="Match"],
[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"][aria-label*="Match"] {
  border-radius: 999px !important;
  padding: var(--pill-pad-y) var(--pill-pad-x) !important;
  font-weight: 600 !important;
  font-size: var(--pill-font-size) !important;
  line-height: 1.2 !important;
  border: 1px solid rgba(255,255,255,.22) !important;
  background: rgba(255,255,255,.04) !important;
  box-shadow: none !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: auto !important;
  min-width: 140px !important;
  height: auto !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  font-family: inherit !important;
  cursor: pointer !important;
}
[data-testid="stAppViewContainer"] button[aria-label*="Match"]:hover,
[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"][aria-label*="Match"]:hover {
  background: rgba(255,255,255,.08) !important;
  border-color: rgba(255,255,255,.30) !important;
}
[data-testid="stAppViewContainer"] button[aria-label*="Match"]:focus-visible,
[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"][aria-label*="Match"]:focus-visible {
  outline: 2px solid rgba(255,255,255,.35) !important;
  outline-offset: 1px !important;
}

/* FINAL SAFETY NET: force main-area buttons to the pill look.
   Streamlit sometimes renders st.button as classic `div.stButton > button` or
   as the newer `[data-testid="baseButton-secondary"]`. Limiting to
   stAppViewContainer prevents sidebar buttons from being affected. */
[data-testid="stAppViewContainer"] div.stButton > button,
[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"] {
  border-radius: 999px !important;
  padding: var(--pill-pad-y) var(--pill-pad-x) !important;
  font-weight: 600 !important;
  font-size: var(--pill-font-size) !important;
  line-height: 1.2 !important;
  border: 1px solid rgba(255,255,255,.22) !important;
  background: rgba(255,255,255,.04) !important;
  box-shadow: none !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: auto !important;
  min-width: 140px !important;
  height: auto !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  font-family: inherit !important;
  cursor: pointer !important;
}

[data-testid="stAppViewContainer"] div.stButton > button:hover,
[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"]:hover {
  background: rgba(255,255,255,.08) !important;
  border-color: rgba(255,255,255,.30) !important;
}

[data-testid="stAppViewContainer"] div.stButton > button:focus-visible,
[data-testid="stAppViewContainer"] [data-testid="baseButton-secondary"]:focus-visible {
  outline: 2px solid rgba(255,255,255,.35) !important;
  outline-offset: 1px !important;
}

/* Layout helper for chips container (safe no-op if unused) */
.sources-grid { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:6px; }

/* --- Sidebar sample buttons: force compact, left-aligned, full-width --- */
/* Cover both Streamlit render paths: classic stButton and baseButton-secondary */
[data-testid="stSidebar"] .stButton,
[data-testid="stSidebar"] button,
[data-testid="stSidebar"] [data-testid="baseButton-secondary"] {
  width: 100% !important;
}

[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] [data-testid="baseButton-secondary"],
[data-testid="stSidebar"] button {
  display: flex !important;
  justify-content: flex-start !important;
  align-items: center !important;

  /* shape + spacing (NOT pills) */
  border-radius: 8px !important;
  padding: 10px 12px !important;
  min-width: 0 !important;
  height: auto !important;

  /* visual */
  font-weight: 500 !important;
  font-size: 0.95rem !important;
  background: rgba(255,255,255,.06) !important;
  border: 1px solid rgba(255,255,255,.14) !important;
  box-shadow: none !important;
  white-space: normal !important;   /* allow wrapping on narrow sidebars */
  text-align: left !important;
}

/* tidy vertical rhythm */
[data-testid="stSidebar"] .stButton { margin-bottom: 8px !important; }              
/* Tight label above chips */
.section-tight{ font-weight:700; margin:4px 0 2px!important; }

/* Static badges reuse same “pill look” */
.badge-row{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:6px; }
.pill-look{
  border-radius:999px!important; padding:var(--pill-pad-y) var(--pill-pad-x)!important; font-weight:600!important;
  font-size:var(--pill-font-size)!important; line-height:1.2!important;
  border:1px solid rgba(255,255,255,.22)!important; background:rgba(255,255,255,.04)!important;
  box-shadow:none!important; min-width:140px!important; height:auto!important;
  white-space:nowrap!important; overflow:hidden!important; text-overflow:ellipsis!important;
  display:inline-block; margin:0 8px 8px 0;
  font-family:inherit!important;
}
/* Ensure Bootstrap Icons keep their font even if we reset others */
.bi {
  font-family: "bootstrap-icons" !important;
  font-style: normal !important;
  font-weight: normal !important;
  line-height: 1;
  vertical-align: -0.125em; /* looks nicer next to text */
}
</style>
""", unsafe_allow_html=True)

# -------- helpers --------
def _shorten_middle(text: str, max_len: int = 72) -> str:
    if not text: return ""
    if len(text) <= max_len: return text
    keep = max_len - 1
    left = keep // 2
    right = keep - left
    return text[:left] + "… " + text[-right:]

def _pick_icon_inline(client: str, title: str) -> str:
    label = f"{client} {title}".lower()
    if any(w in label for w in ["payment", "treasury", "bank", "rbc"]):
        return "bi-bank"
    if any(w in label for w in ["health", "care", "patient", "kaiser"]):
        return "bi-hospital"
    if any(w in label for w in ["cloud", "kubernetes", "microservice"]):
        return "bi-cloud"
    if any(w in label for w in ["ai", "ml", "model", "genai", "rai"]):
        return "bi-cpu"
    if any(w in label for w in ["innovation", "prototype", "cic", "liquid studio"]):
        return "bi-lightning"
    if any(w in label for w in ["sales", "growth", "pipeline"]):
        return "bi-graph-up"
    if any(w in label for w in ["talent", "hiring", "org", "scale"]):
        return "bi-diagram-3"
    return "bi-journal-text"

# -------- interactive Sources (Ask) --------
def render_sources_chips(
    sources: list[dict],
    title: str = "Sources",
    *,
    stay_here: bool = False,
    key_prefix: str = "",
):
    """
    Render clickable Sources chips that match the pill visuals.
    Clicking a chip selects the story and switches to Ask (unless stay_here=True).
    """
    css_once()
    if not sources:
        return

    # Normalize inputs
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

    st.markdown(f"<div class='section-tight'>{title}</div>", unsafe_allow_html=True)

    # Open a scoped container so our CSS can target buttons reliably
    st.markdown("<div data-mpg-srcchips class='pill-container sources-tight sources-grid'>", unsafe_allow_html=True)

    # Stable horizontal layout: render in rows of columns
    per_row = 3
    pc_scores = st.session_state.get("__pc_last_ids__", {}) or {}

    def _label_for(s: dict) -> str:
        base = f"{s['client']} — {s['title']}" if s["client"] else s["title"]
        short = _shorten_middle(base, 72)
        score = pc_scores.get(str(s.get('id') or ""))
        if isinstance(score, (int, float)):
            return f"{score*100:.0f}% Match • {short}"
        return short

    container = st.container()
    row: list[dict] = []
    for i, s in enumerate(items):
        row.append(s)
        if len(row) == per_row:
            cols = container.columns(len(row))
            for col, item in zip(cols, row):
                with col:
                    if st.button(
                        _label_for(item),
                        key=f"{key_prefix}srcchip_{item.get('id') or _label_for(item)}",
                        use_container_width=False,
                        help="Semantic relevance to your question (higher = stronger match)",
                    ):
                        # Select story and switch context
                        st.session_state["active_story"] = item.get("id") or ""
                        st.session_state["active_story_title"] = item.get("title")
                        st.session_state["active_story_client"] = item.get("client")
                        st.session_state["show_ask_panel"] = True
                        if stay_here:
                            st.rerun()
                        else:
                            st.session_state["active_tab"] = "Ask MattGPT"
                            st.rerun()
            row = []

    # Flush any remainder in the last row
    if row:
        cols = container.columns(len(row))
        for col, item in zip(cols, row):
            with col:
                if st.button(
                    _label_for(item),
                    key=f"{key_prefix}srcchip_{item.get('id') or _label_for(item)}",
                    use_container_width=False,
                    help="Semantic relevance to your question (higher = stronger match)",
                ):
                    st.session_state["active_story"] = item.get("id") or ""
                    st.session_state["active_story_title"] = item.get("title")
                    st.session_state["active_story_client"] = item.get("client")
                    st.session_state["show_ask_panel"] = True
                    if stay_here:
                        st.rerun()
                    else:
                        st.session_state["active_tab"] = "Ask MattGPT"
                        st.rerun()

    # Close the scoped container
    st.markdown("</div>", unsafe_allow_html=True)

# -------- static badges (Explore/Details) --------
def render_sources_badges_static(
    sources: list[dict], title: str = "Sources", key_prefix: str = "srcbad_"
):
    if not sources:
        return

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

    st.markdown(f"<div class='section-tight'>{title}</div>", unsafe_allow_html=True)
    # Use the same pill visuals (non-clickable)
    html = []
    for s in items:
        client = s.get("client", "")
        title_txt = s.get("title", "")
        icon = s.get("icon") or _pick_icon_inline(client, title_txt)
        base = f"{client} — {title_txt}" if client else title_txt
        txt = _shorten_middle(base, 96)
        html.append(f"<span class='pill-look'><i class='bi {icon}'></i>{txt}</span>")
    st.markdown(f"<div class='badge-row'>{''.join(html)}</div>", unsafe_allow_html=True)

def render_sources_row_html(sources: list[dict], title: str = "Sources"):
    if not sources:
        return
    items = [s for s in sources if (s.get("client") or s.get("title"))]
    chips = "".join(
        f"<span class='pill-look' style='display:inline-flex;align-items:center;margin:0 8px 8px 0;'>"
        f"{(s.get('client','') + ' — ' if s.get('client') else '')}{s.get('title','')}"
        f"</span>"
        for s in items
    )
    st.markdown(f"<div class='section-tight'>{title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='badge-row'>{chips}</div>", unsafe_allow_html=True)