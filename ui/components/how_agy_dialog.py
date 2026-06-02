"""
How Agy Searches — @st.dialog component (MATTGPT-110).

Replaces the inline expander pattern (show_how_modal + render_modal_wrapper_*
+ components.html iframes). Native Streamlit content inside @st.dialog:
clean single scroll, no iframe nesting, no inline page disruption.

Content: run-only narrative (You Ask → Agy Searches → You Get Results).
Technical Details block removed — that content belongs in How I Built.
Footer st.button opens How I Built sequentially via active_dialog flag.

Pattern: active_dialog = "how_agy" | "how_i_built" | None
Sequential dialog rendering (caller must use elif, not if/if):
    if st.session_state.get("active_dialog") == "how_agy":
        render_how_agy_dialog()
    elif st.session_state.get("active_dialog") == "how_i_built":
        render_how_i_built_dialog()
"""

import streamlit as st

_CSS = """
<style>
.step-header { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
.step-num { width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, #8B5CF6, #7C3AED); color: white; font-size: 20px; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 4px 12px rgba(139,92,246,0.4); }
.step-title { font-size: 22px; font-weight: 700; color: #1F2937; margin: 0; }
.step-content { margin-left: 58px; }
.query-card { background: #ffffff; border: 2px solid #E9D5FF; border-radius: 12px; padding: 20px 24px; font-style: italic; font-size: 15px; color: #4B5563; line-height: 1.6; }
.flow-arrow { text-align: center; color: #A78BFA; font-size: 36px; margin: 16px 0; }
.pipeline-flow { background: #ffffff; border: 2px solid #E5E7EB; border-radius: 12px; padding: 14px 20px; display: flex; align-items: center; justify-content: center; gap: 6px; flex-wrap: wrap; margin-bottom: 16px; }
.pill-stage { padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; background: #ffffff; color: #4B5563; border: 1px solid #E5E7EB; }
.pill-arrow { color: #9CA3AF; font-size: 11px; }
.cards-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
.search-card { background: #ffffff; border: 1px solid #E5E7EB; border-radius: 10px; padding: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); }
.search-card.hero { border: 2px solid #8B5CF6; box-shadow: 0 4px 14px rgba(139,92,246,0.15); padding: 20px; margin-bottom: 12px; }
.card-title { font-size: 13px; font-weight: 700; color: #1F2937; margin-bottom: 6px; }
.search-card.hero .card-title { font-size: 15px; }
.card-desc { font-size: 12px; color: #4B5563; line-height: 1.5; }
.search-card.hero .card-desc { font-size: 13px; }
.result-wrapper { border: 3px solid #8B5CF6; border-radius: 12px; padding: 20px; box-shadow: 0 6px 18px rgba(139,92,246,0.2); }
.result-card { background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 10px; padding: 18px; margin-bottom: 16px; }
.result-title { font-size: 16px; font-weight: 700; margin-bottom: 6px; }
.result-desc { font-size: 14px; opacity: 0.95; line-height: 1.6; }
.pills-row { display: flex; gap: 8px; flex-wrap: wrap; }
.tag { padding: 6px 12px; border-radius: 18px; font-size: 12px; font-weight: 500; }
.tag-purple { background: #EDE9FE; color: #7C3AED; }
.tag-blue { background: #E0E7FF; color: #4F46E5; }
.tag-green { background: #D1FAE5; color: #065F46; }
.tag-check { background: #D1FAE5; color: #065F46; display: inline-flex; align-items: center; gap: 4px; padding: 6px 12px; border-radius: 18px; font-size: 12px; font-weight: 500; }
/* Footer button — styled as text link, not bordered button */
[class*="st-key-how_agy_to_hib"] button {
    background: none !important;
    border: none !important;
    color: #8B5CF6 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 0 !important;
    cursor: pointer !important;
    box-shadow: none !important;
}
[class*="st-key-how_agy_to_hib"] button:hover { text-decoration: underline !important; }
</style>
"""


@st.dialog("How Agy searches", width="large")
def render_how_agy_dialog():
    """How Agy Searches as @st.dialog — native Streamlit, no iframes."""
    st.markdown(_CSS, unsafe_allow_html=True)

    # Step 1: You Ask
    st.markdown(
        """<div class="step-header"><div class="step-num">1</div><p class="step-title">You Ask</p></div><div class="step-content"><div class="query-card">"Tell me about a time you dealt with a difficult stakeholder"</div></div><div class="flow-arrow">↓</div>""",
        unsafe_allow_html=True,
    )

    # Step 2: Agy Searches
    st.markdown(
        """<div class="step-header"><div class="step-num">2</div><p class="step-title">Agy Searches</p></div><div class="step-content"><div class="pipeline-flow"><span class="pill-stage">Filters noisy input</span><span class="pill-arrow">→</span><span class="pill-stage">Detects interview intent</span><span class="pill-arrow">→</span><span class="pill-stage">Retrieves stories</span><span class="pill-arrow">→</span><span class="pill-stage">Refuses weak matches</span><span class="pill-arrow">→</span><span class="pill-stage">Synthesizes response</span></div><div class="cards-row"><div class="search-card"><div class="card-title">Filters irrelevant/noisy input</div><div class="card-desc">Homework requests, gibberish, and off-domain queries get bounced before they reach the model — no wasted cost, no off-topic answers</div></div><div class="search-card"><div class="card-title">Detects interview intent</div><div class="card-desc">Recognizes behavioral, technical, leadership, and background questions — and adapts the response style to fit hiring context</div></div></div><div class="search-card hero"><div class="card-title">Retrieves grounded experience stories</div><div class="card-desc">Pulls from Matt's actual 20+ years of work — never invents examples, never paraphrases someone else's resume</div></div><div class="cards-row"><div class="search-card"><div class="card-title">Refuses weak matches / avoids fabrication</div><div class="card-desc">If the closest story isn't a strong fit, says "I don't know" instead of bluffing a stretch answer</div></div><div class="search-card"><div class="card-title">Synthesizes a tailored interview response</div><div class="card-desc">Structures the answer for hiring decisions — situation, action, outcome — grounded in the retrieved stories, with distinctive phrases preserved verbatim</div></div></div></div><div class="flow-arrow">↓</div>""",
        unsafe_allow_html=True,
    )

    # Step 3: You Get Results
    st.markdown(
        """<div class="step-header"><div class="step-num">3</div><p class="step-title">You Get Results</p></div><div class="step-content"><div class="result-wrapper"><div class="result-card"><div class="result-title">Navigating Executive Resistance at Fortune 100 Bank</div><div class="result-desc">Turned a skeptical CTO into a transformation champion through deep listening, small wins, and building trust over 6 months...</div></div><div class="pills-row"><span class="tag tag-purple">Stakeholder Management</span><span class="tag tag-blue">Financial Services</span><span class="tag tag-green">Leadership</span><span class="tag-check">✓ High confidence match</span></div></div></div>""",
        unsafe_allow_html=True,
    )

    # Footer separator + bridge button
    st.markdown(
        "<hr style='margin: 20px 0 8px; border-color: #E5E7EB;'>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<span style='font-size:13px; color:#6B7280;'>Want the technical details?</span>",
        unsafe_allow_html=True,
    )
    if st.button("See how I built it →", key="how_agy_to_hib"):
        st.session_state["active_dialog"] = "how_i_built"
        st.rerun()
