import streamlit as st

# --- one-time CSS identical to your “pill” look ---
def css_once():
    if st.session_state.get("_chips_css_once"): return
    st.session_state["_chips_css_once"] = True
    st.markdown("""
    <style>
      /* make container behave like your pills row */
      .pill-container.sources-tight{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
      /* give buttons the same look as pills */
      .pill-container.sources-tight .stButton > button{
        border-radius:999px;padding:6px 12px;font-weight:600;font-size:1rem;line-height:1.2;
        border:1px solid rgba(255,255,255,.22);background:rgba(255,255,255,.04);box-shadow:none;
        min-width:140px;height:auto;white-space:nowrap;overflow:hidden;text-overflow:ellipsis
      }
      .pill-container.sources-tight .stButton > button:hover{
        background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.30)
      }
    </style>
    """, unsafe_allow_html=True)

def render_sources_chips(sources, key_prefix="probe_"):
    if not sources: return
    st.markdown("<div class='pill-container sources-tight'>", unsafe_allow_html=True)
    for i, s in enumerate(sources):
        label = f"{s.get('client','')} — {s.get('title','')}".strip(" —")
        if st.button(label, key=f"{key_prefix}{i}"):
            st.session_state["clicked"] = s
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

css_once()
st.title("Chip Probe")
demo = [
    {"id":"1","client":"Accenture","title":"Creating Competency Frameworks"},
    {"id":"2","client":"Multiple Clients","title":"Driving Innovation at the Cloud Innovation Center"},
    {"id":"3","client":"JP Morgan Chase","title":"User-Centered Design and Testing"},
]
render_sources_chips(demo)

st.write("Clicked:", st.session_state.get("clicked"))