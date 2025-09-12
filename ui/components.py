# ui/components.py
from __future__ import annotations
import streamlit as st

# -------- one-time CSS injector (idempotent) --------
def css_once():
    flag = "__ui_css_once__"
    if st.session_state.get(flag):
        return
    st.session_state[flag] = True

    st.markdown("""
<style>
/* ====== Pills & Sources: single source of truth ====== */

/* Define a single token and reuse it in **both** places */
:root { --pill-font-size: 0.95rem; }  /* adjust this until it visually matches your pills exactly */

/* Pills (reference) */
.pill-container .stButton > button{
  border-radius:999px!important;
  padding:6px 12px!important;
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

/* Sources chips – EXACT same rules as pills */
.sources-grid [data-testid="stButton"] > button,
.pill-container.sources-tight :where(div.stButton) > button{
  border-radius:999px!important;
  padding:6px 12px!important;
  font-weight:600!important;
  font-size:var(--pill-font-size)!important;
  line-height:1.2!important;
  border:1px solid rgba(255,255,255,.22)!important;
  background:rgba(255,255,255,.04)!important;
  box-shadow:none!important;
  min-width:140px!important;
  height:auto!important;
  width:auto!important;
  white-space:nowrap!important;
  overflow:hidden!important;
  text-overflow:ellipsis!important;
  font-family:inherit!important;
}
.sources-grid [data-testid="stButton"] > button:hover,
.pill-container.sources-tight :where(div.stButton) > button:hover{
  background:rgba(255,255,255,.08)!important;
  border-color:rgba(255,255,255,.30)!important;
}
.sources-grid [data-testid="stButton"] > button:focus-visible,
.pill-container.sources-tight :where(div.stButton) > button:focus-visible{
  outline:2px solid rgba(255,255,255,.35)!important;
  outline-offset:1px!important;
}

/* Horizontal flow container used by your chips */
.sources-grid{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:6px; }

/* Tight label above chips */
.section-tight{ font-weight:700; margin:4px 0 2px!important; }

/* Static badges reuse same “pill look” */
.badge-row{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:6px; }
.pill-look{
  border-radius:999px!important; padding:6px 12px!important; font-weight:600!important;
  font-size:var(--pill-font-size)!important; line-height:1.2!important;
  border:1px solid rgba(255,255,255,.22)!important; background:rgba(255,255,255,.04)!important;
  box-shadow:none!important; min-width:140px!important; height:auto!important;
  white-space:nowrap!important; overflow:hidden!important; text-overflow:ellipsis!important;
  display:inline-block; margin:0 8px 8px 0;
  font-family:inherit!important;
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
    st.markdown("<div class='sources-grid'>", unsafe_allow_html=True)

    # Stable horizontal layout: render in rows of columns
    per_row = 3
    pc_scores = st.session_state.get("__pc_last_ids__", {}) or {}

    def _label_for(s: dict) -> str:
        base = f"{s['client']} — {s['title']}" if s["client"] else s["title"]
        short = _shorten_middle(base, 72)
        score = pc_scores.get(str(s.get("id") or ""))
        if isinstance(score, (int, float)):
            return f"{score*100:.0f}% Match • {short}"
        return short

    # Batch into rows
    container = st.container()
    row: list[dict] = []
    for i, s in enumerate(items):
        if len(row) == per_row:
            cols = container.columns(len(row))
            for col, item in zip(cols, row):
                with col:
                    if st.button(
                        _label_for(item),
                        key=f"{key_prefix}srcchip_{item.get('id') or _label_for(item)}",
                        use_container_width=False,
                        help="Semantic relevance to your question",
                    ):
                        st.session_state["active_story"] = item.get("id") or ""
                        st.session_state["active_story_title"] = item.get("title")
                        st.session_state["active_story_client"] = item.get("client")
                        st.session_state["show_ask_panel"] = True
                        if stay_here:
                            st.rerun()
                        else:
                            st.session_state["active_tab"] = "Explore Stories"
                            st.rerun()
            row = []
        row.append(s)

    if row:
        cols = container.columns(len(row))
        for col, item in zip(cols, row):
            with col:
                if st.button(
                    _label_for(item),
                    key=f"{key_prefix}srcchip_{item.get('id') or _label_for(item)}",
                    use_container_width=False,
                    help="Semantic relevance to your question",
                ):
                    st.session_state["active_story"] = item.get("id") or ""
                    st.session_state["active_story_title"] = item.get("title")
                    st.session_state["active_story_client"] = item.get("client")
                    st.session_state["show_ask_panel"] = True
                    if stay_here:
                        st.rerun()
                    else:
                        st.session_state["active_tab"] = "Explore Stories"
                        st.rerun()

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