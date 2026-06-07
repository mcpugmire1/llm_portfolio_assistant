"""
How Agy Searches — @st.dialog component (MATTGPT-110).

Replaces the inline expander pattern (show_how_modal + render_modal_wrapper_*
+ components.html iframes). Native Streamlit content inside @st.dialog:
clean single scroll, no iframe nesting, no inline page disruption.

Content: run-only narrative (You Ask → Agy Searches → You Get Results).
Technical Details block removed — that content belongs in How I Built.
Footer st.button opens How I Built sequentially via active_dialog flag.

Dark theme: JS detects body.dark-theme on parent page and applies .dark-theme
to the st.container(key="how_agy_dialog_content") wrapper — same pattern as
how_agy_modal.py. CSS variable overrides scoped to that wrapper only.

Pattern: active_dialog = "how_agy" | "how_i_built" | None
Sequential dialog rendering (caller must use elif, not if/if):
    if st.session_state.get("active_dialog") == "how_agy":
        render_how_agy_dialog()
    elif st.session_state.get("active_dialog") == "how_i_built":
        render_how_i_built_dialog()
"""

import streamlit as st
import streamlit.components.v1 as components

_CSS = """
<style>
@media (max-width: 768px) {
    [role="dialog"] {
        max-height: 90vh !important;
        overflow-y: auto !important;
    }
}

/* Dark theme variable overrides — scoped to this dialog's container only.
   JS applies .dark-theme to [class*="st-key-how_agy_dialog_content"] when
   body.dark-theme is detected on the parent page. Values mirror
   global_styles.py body.dark-theme block. */
[class*="st-key-how_agy_dialog_content"].dark-theme {
    --bg-card: #1E1E2E;
    --bg-surface: #262633;
    --text-primary: #E5E7EB;
    --text-secondary: #9CA3AF;
    --border-color: #374151;
    --accent-purple: #A78BFA;
    --accent-purple-light: rgba(167,139,250,0.2);
    --accent-purple-bg: rgba(167,139,250,0.15);
    --accent-purple-hover: #9061F9;
    --card-shadow: 0 1px 3px rgba(0,0,0,0.3);
    --pill-bg: #374151;
    --pill-text: #E5E7EB;
}
.step-header { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
.step-num { width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, var(--accent-purple), var(--accent-purple-hover)); color: white; font-size: 20px; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 4px 12px rgba(139,92,246,0.4); }
.step-title { font-size: 22px; font-weight: 700; color: var(--text-primary); margin: 0; }
.step-content { margin-left: 58px; }
.query-card { background: var(--bg-card); border: 2px solid var(--accent-purple-light); border-radius: 12px; padding: 20px 24px; font-style: italic; font-size: 13px; color: var(--text-secondary); line-height: 1.6; }
.flow-arrow { text-align: center; color: var(--accent-purple); font-size: 36px; margin: 16px 0; }
.pipeline-flow { background: var(--bg-card); border: 2px solid var(--border-color); border-radius: 12px; padding: 14px 20px; display: flex; align-items: center; justify-content: center; gap: 6px; flex-wrap: wrap; margin-bottom: 16px; }
.pill-stage { padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; background: var(--bg-card); color: var(--text-secondary); border: 1px solid var(--border-color); }
.pill-arrow { color: var(--text-secondary); font-size: 11px; opacity: 0.5; }
.cards-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
.search-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 16px; box-shadow: var(--card-shadow); }
.search-card.hero { border: 2px solid var(--accent-purple); box-shadow: 0 4px 14px rgba(139,92,246,0.15); padding: 20px; margin-bottom: 12px; }
.card-title { font-size: 13px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px; }
.search-card.hero .card-title { font-size: 15px; }
.card-desc { font-size: 12px; color: var(--text-secondary); line-height: 1.5; }
.search-card.hero .card-desc { font-size: 13px; }
.result-wrapper { border: 3px solid var(--accent-purple); border-radius: 12px; padding: 20px; box-shadow: 0 6px 18px rgba(139,92,246,0.2); }
.result-card { background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 10px; padding: 18px; margin-bottom: 16px; }
.result-title { font-size: 16px; font-weight: 700; margin-bottom: 6px; }
.result-desc { font-size: 14px; opacity: 0.95; line-height: 1.6; }
.pills-row { display: flex; gap: 8px; flex-wrap: wrap; }
.tag { padding: 6px 12px; border-radius: 18px; font-size: 12px; font-weight: 500; }
.tag-purple { background: var(--accent-purple-bg); color: var(--accent-purple); }
.tag-blue { background: var(--pill-bg); color: var(--pill-text); }
.tag-green { background: var(--pill-bg); color: var(--pill-text); }
.tag-check { background: var(--pill-bg); color: var(--pill-text); display: inline-flex; align-items: center; gap: 4px; padding: 6px 12px; border-radius: 18px; font-size: 12px; font-weight: 500; }
.desktop-only { display: flex; }
.mobile-only { display: none; }
@media (max-width: 640px) {
    .desktop-only { display: none !important; }
    .mobile-only { display: block; font-size: 12px !important; color: var(--text-secondary); line-height: 1.8; padding: 10px 14px; }
    .cards-row { grid-template-columns: 1fr; }
    .result-title { font-size: 14px !important; }
    .result-desc { font-size: 12px !important; }
}
/* Footer button — full-width secondary style matching wireframe modal-footer-btn */
[class*="st-key-how_agy_to_hib"] { width: 100% !important; }
[class*="st-key-how_agy_to_hib"] button {
    width: 100% !important;
    border: 1px solid var(--accent-purple-light) !important;
    border-radius: 8px !important;
    background: transparent !important;
    padding: 12px 20px !important;
    justify-content: center !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: var(--accent-purple) !important;
    box-shadow: none !important;
    cursor: pointer !important;
}
[class*="st-key-how_agy_to_hib"] button:hover { background: var(--accent-purple-bg) !important; border-color: var(--accent-purple) !important; }
</style>
"""

_DARK_THEME_JS = """
<script>
(function() {
    function detectTheme() {
        try {
            var parentBody = window.parent.document.body;
            return parentBody.classList.contains('dark-theme') ||
                   parentBody.getAttribute('data-theme') === 'dark';
        } catch(e) {
            return window.matchMedia('(prefers-color-scheme: dark)').matches;
        }
    }

    function applyTheme() {
        try {
            var wrapper = window.parent.document.querySelector('[class*="st-key-how_agy_dialog_content"]');
            if (wrapper) {
                if (detectTheme()) {
                    wrapper.classList.add('dark-theme');
                } else {
                    wrapper.classList.remove('dark-theme');
                }
            }
        } catch(e) {}
    }

    applyTheme();

    try {
        new MutationObserver(applyTheme).observe(window.parent.document.body, {
            attributes: true, attributeFilter: ['class', 'data-theme']
        });
    } catch(e) { setTimeout(applyTheme, 800); }
})();
</script>
"""


@st.dialog("How Agy searches", width="large")
def render_how_agy_dialog():
    """How Agy Searches as @st.dialog — native Streamlit, no iframes.

    Content wrapped in st.container(key="how_agy_dialog_content") so the
    dark theme JS can target it via [class*="st-key-how_agy_dialog_content"].
    """
    st.markdown(_CSS, unsafe_allow_html=True)

    # Scroll dialog content to top on open — needed on mobile where the
    # dialog may render with its internal container scrolled mid-content.
    components.html(
        """<script>
        setTimeout(function() {
            var d = window.parent.document.querySelector('[role="dialog"] > div');
            if (d) d.scrollTop = 0;
        }, 100);
        </script>""",
        height=0,
    )

    with st.container(key="how_agy_dialog_content"):
        # Step 1: You Ask
        st.markdown(
            """<div class="step-header"><div class="step-num">1</div><p class="step-title">You Ask</p></div><div class="step-content"><div class="query-card">"Tell me about a time you dealt with a difficult stakeholder"</div></div><div class="flow-arrow">↓</div>""",
            unsafe_allow_html=True,
        )

        # Step 2: Agy Searches
        st.markdown(
            """<div class="step-header"><div class="step-num">2</div><p class="step-title">Agy Searches</p></div><div class="step-content"><div class="pipeline-flow desktop-only"><span class="pill-stage">Filters noisy input</span><span class="pill-arrow">→</span><span class="pill-stage">Detects interview intent</span><span class="pill-arrow">→</span><span class="pill-stage">Retrieves stories</span><span class="pill-arrow">→</span><span class="pill-stage">Refuses weak matches</span><span class="pill-arrow">→</span><span class="pill-stage">Synthesizes response</span></div><p class="pipeline-summary mobile-only">Filters noisy input · Detects interview intent · Retrieves stories · Refuses weak matches · Synthesizes response</p><div class="cards-row"><div class="search-card"><div class="card-title">Filters irrelevant/noisy input</div><div class="card-desc">Homework requests, gibberish, and off-domain queries get bounced before they reach the model — no wasted cost, no off-topic answers</div></div><div class="search-card"><div class="card-title">Detects interview intent</div><div class="card-desc">Recognizes behavioral, technical, leadership, and background questions — and adapts the response style to fit hiring context</div></div></div><div class="search-card hero"><div class="card-title">Retrieves grounded experience stories</div><div class="card-desc">Pulls from Matt's actual 20+ years of work — never invents examples, never paraphrases someone else's resume</div></div><div class="cards-row"><div class="search-card"><div class="card-title">Refuses weak matches / avoids fabrication</div><div class="card-desc">If the closest story isn't a strong fit, says "I don't know" instead of bluffing a stretch answer</div></div><div class="search-card"><div class="card-title">Synthesizes a tailored interview response</div><div class="card-desc">Structures the answer for hiring decisions — situation, action, outcome — grounded in the retrieved stories, with distinctive phrases preserved verbatim</div></div></div></div><div class="flow-arrow">↓</div>""",
            unsafe_allow_html=True,
        )

        # Step 3: You Get Results
        st.markdown(
            """<div class="step-header"><div class="step-num">3</div><p class="step-title">You Get Results</p></div><div class="step-content"><div class="result-wrapper"><div class="result-card"><div class="result-title">Navigating Executive Resistance at Fortune 100 Bank</div><div class="result-desc">Turned a skeptical CTO into a transformation champion through deep listening, small wins, and building trust over 6 months...</div></div><div class="pills-row"><span class="tag tag-purple">Stakeholder Management</span><span class="tag tag-blue">Financial Services</span><span class="tag tag-green">Leadership</span><span class="tag-check">✓ High confidence match</span></div></div></div>""",
            unsafe_allow_html=True,
        )

        # Footer separator + bridge button
        st.markdown(
            "<hr style='margin: 20px 0 8px; border-color: var(--border-color);'>",
            unsafe_allow_html=True,
        )
        if st.button("See how I built it →", key="how_agy_to_hib"):
            st.session_state["active_dialog"] = "how_i_built"
            st.rerun()

    # Dark theme detection — applies .dark-theme to the container wrapper so
    # CSS variable overrides cascade correctly. Ported from how_agy_modal.py.
    components.html(_DARK_THEME_JS, height=0)
