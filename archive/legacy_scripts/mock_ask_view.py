import streamlit as st

st.set_page_config(page_title="Ask MattGPT — Mock", layout="wide")
st.session_state.setdefault(
    "ask_mode", "Narrative"
)  # Narrative | Key Points | Deep Dive

# Bootstrap mono icons (same CDN you use)
st.markdown(
    "<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css'>",
    unsafe_allow_html=True,
)

# --- minimal CSS to match your style (card + badges) ---
st.markdown(
    """
<style>
.answer-card {
  border: 1px solid rgba(0,0,0,0.10);
  background: rgba(0,0,0,0.03);
  border-radius: 12px;
  padding: 16px 18px;
  margin: 10px 0 12px 0;
}
@media (prefers-color-scheme: dark) {
  .answer-card { background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.12); }
}
.answer-head { font-weight: 700; font-size: 1.05rem; margin: 0 0 6px 0; }
.answer-impact { font-weight: 600; opacity: .95; margin: 2px 0 8px 0; }
.answer-body { line-height: 1.45; }

.badge-row{ display:flex; flex-wrap:wrap; gap:8px; margin:6px 0 0; }
.badge{
  display:inline-flex; align-items:center; gap:8px;
  font-size: 13px; line-height:1.1;
  padding: 6px 10px; border-radius:999px;
  border:1px solid rgba(0,0,0,0.10); background:rgba(0,0,0,0.04);
  white-space:nowrap;
}
@media (prefers-color-scheme: dark){
  .badge{ background:rgba(255,255,255,0.06); border-color:rgba(255,255,255,0.12); }
}
.section-label { font-weight:700; opacity:.9; margin-top: 8px; }
.mode-row { display:flex; gap:8px; margin: 8px 0 0; }
.mode-btn {
  border:1px solid rgba(0,0,0,0.18); border-radius:999px; padding:6px 10px;
  background:transparent; font-weight:600; cursor:pointer;
}
.mode-btn:hover { background: rgba(0,0,0,0.05); }
@media (prefers-color-scheme: dark){ .mode-btn:hover{ background:rgba(255,255,255,0.06); } }
</style>
""",
    unsafe_allow_html=True,
)

# --- mock data (these 3 are your top Pinecone hits from the logs) ---
answer_title = "Driving Innovation through Cloud Innovation Center and Liquid Studio"
answer_impact = "Impact: Scaled CIC to 150+ hires, enabled 50% faster delivery, grew pipeline to $300M+."
answer_body = (
    "I led cross-functional initiatives at the Cloud Innovation Center (CIC) and Liquid Studio to help enterprise clients "
    "prove value fast. We used hypothesis-driven design and rapid prototyping to validate use-cases, while building a repeatable, "
    "cloud-native delivery model. This accelerated time-to-value and turned pilots into scaled programs."
)

# --- mode-specific content derived from same sources (no new search) ---
mode_bodies = {
    "Narrative": (
        "I built and led Accenture’s Cloud Innovation Center (CIC) and Liquid Studio to help Fortune 500 clients turn ideas into "
        "production-ready outcomes. Purpose: accelerate modernization. Performance: measurable business impact. We embedded "
        "hypothesis‑driven design, rapid prototyping, and lean rituals to validate use cases quickly and scale a repeatable, "
        "cloud‑native delivery model."
    ),
    "Key Points": (
        "**Highlights**\n"
        "- Led prototyping pods that cut concept‑to‑pilot cycle time nearly in half, enabling faster go/no‑go clarity.\n"
        "- Standardized playbooks and executive showcases that converted prototypes into a $300M+ pipeline.\n"
        "- Built and scaled 150+ engineers into balanced delivery pods, sustaining ~95% retention and repeatable quality."
    ),
    "Deep Dive": (
        "**Case Study (CIC exemplar)**\n\n"
        "**What was happening**\n"
        "- Enterprises could demo innovation but struggled to scale it into production.\n\n"
        "**Goal**\n"
        "- Make experimentation real and repeatable via a dedicated center and studio.\n\n"
        "**What we did**\n"
        "- Recruited and scaled cross‑functional pods, embedded lean product rituals, and ran weekly executive showcases.\n\n"
        "**Results**\n"
        "- Faster time‑to‑market, $300M+ pipeline, and a durable innovation engine."
    ),
}

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

# --- render ---
st.markdown("### Ask MattGPT")
st.caption("Prompt: **How have you driven innovation in your career?**")

st.markdown(
    "<div class='answer-card'>"
    f"<div class='answer-head'>{answer_title}</div>"
    f"<div class='answer-impact'>{answer_impact}</div>"
    f"<div class='answer-body'>{answer_body}</div>"
    "</div>",
    unsafe_allow_html=True,
)

# Mode toggles (real view switches; no new search)
if "segmented_control" in dir(st):
    mode = st.segmented_control(
        "",
        options=["Narrative", "Key Points", "Deep Dive"],
        selection_mode="single",
        default=st.session_state.get("ask_mode", "Narrative"),
    )
    if mode != st.session_state.get("ask_mode"):
        st.session_state["ask_mode"] = mode

    # Render the selected mode content right under the card
    st.markdown("<hr style='opacity:.15;margin:8px 0 8px'>", unsafe_allow_html=True)
    st.markdown(
        mode_bodies.get(st.session_state["ask_mode"], mode_bodies["Narrative"]),
        unsafe_allow_html=True,
    )
else:
    # Fallback for older Streamlit: pill-like buttons
    cols = st.columns(3)
    for i, label in enumerate(["Narrative", "Key Points", "Deep Dive"]):
        with cols[i]:
            if st.button(label, key=f"mode_{label}"):
                st.session_state["ask_mode"] = label
    st.markdown("<hr style='opacity:.15;margin:8px 0 8px'>", unsafe_allow_html=True)
    st.markdown(
        mode_bodies.get(st.session_state["ask_mode"], mode_bodies["Narrative"]),
        unsafe_allow_html=True,
    )

st.caption(
    "These sources are the top-ranked stories used to compose the answer (no re-query)."
)
st.markdown("<div class='section-label'>Sources</div>", unsafe_allow_html=True)

# 1) Pretty badges (if HTML/CSS renders)
if isinstance(sources, list) and sources:
    chips = "".join(
        f"<span class='badge'><i class='bi {s.get('icon','bi-dot')}'></i>{s.get('client','')} — {s.get('title','')}</span>"
        for s in sources
        if s and (s.get("client") or s.get("title"))
    )
    if chips:
        st.markdown(f"<div class='badge-row'>{chips}</div>", unsafe_allow_html=True)
    else:
        st.warning("No sources available in this mock. (Expected 3 hard-coded items.)")
else:
    st.warning("No sources available in this mock. (Expected 3 hard-coded items.)")

# Debug panel
with st.expander("Debug: Sources object", expanded=False):
    st.write(
        {
            "type": type(sources).__name__,
            "count": (len(sources) if isinstance(sources, list) else 0),
        }
    )
    st.write(sources)

st.info(
    "This mock shows the intended look/feel only. In the real app, the Sources row is built from the latest Pinecone hits and clicking a source would navigate to Explore Stories."
)
