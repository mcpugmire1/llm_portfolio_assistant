"""
Why Agy? — @st.dialog component (MATTGPT-101).

Origin story for Agy: Plott Hound naming, breed traits mapped to RAG
behavior, italic closing line honoring Matt's late dog.

Footer st.button sets active_dialog = "how_i_built" so the How I Built
dialog (MATTGPT-102) opens sequentially when that ticket ships.

Pattern mirrors how_agy_dialog.py exactly:
  - _CSS injected via st.markdown
  - st.container(key="why_agy_dialog_content") wrapper for dark theme targeting
  - _DARK_THEME_JS applied at end via components.html
  - Caller uses active_dialog key + elif chain (never if/if)

Dark theme: JS detects body.dark-theme on parent page and applies .dark-theme
to [class*="st-key-why_agy_dialog_content"] — CSS variable overrides cascade
from that wrapper only.
"""

import streamlit as st
import streamlit.components.v1 as components

from ui.image_assets import AGY_MATT_CARTOON_B64

_BODY_HTML = f"""

<div class="why-agy-avatar-row">
    <div class="why-agy-body">
        <p>I'm named for Matt's Plott Hound. Plott Hounds are bred for tracking — determined, loyal, hard to shake once they're on a trail. That's exactly how I work.
        </p>
        <p>Ask me about Matt's work and I'll track down the right story. I'm trained on 100+ stories from his career — not a keyword search, not a resume summary. I find what's relevant, or I tell you honestly when I can't.
        </p>
        <em class="why-agy-closing">It felt right to keep his name part of the work we loved doing together.</em>
    </div>
    <img class="why-agy-illustration"
         src="{AGY_MATT_CARTOON_B64}"
         alt="Matt and Agy"/>
</div>
"""

_CSS = """
<style>
[class*="st-key-why_agy_dialog_content"].dark-theme {
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
}
.why-agy-avatar-row {
    display: flex;
    gap: 20px;
    align-items: flex-start;
    margin-bottom: 8px;
}
.why-agy-body {
    flex: 1;
}
.why-agy-body p {
    font-size: 16px;
    line-height: 1.7;
    color: var(--text-primary);
    margin-bottom: 10px;
}
.why-agy-closing {
    font-size: 14px;
    line-height: 1.7;
    color: var(--text-secondary);
    font-style: italic;
    margin-bottom: 0;
}
.why-agy-illustration {
    width: 100px;
    height: auto;
    flex-shrink: 0;
}
/* Footer button — full-width secondary style matching how_agy_dialog.py */
[class*="st-key-why_agy_to_hib"] { width: 100% !important; }
[class*="st-key-why_agy_to_hib"] button {
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
[class*="st-key-why_agy_to_hib"] button:hover {
    background: var(--accent-purple-bg) !important;
    border-color: var(--accent-purple) !important;
}

[class*="st-key-why_agy_to_hib"] button p {
    font-size: 14px !important;
}

@media (max-width: 480px) {
    [role="dialog"] {
        max-height: 88vh !important;
        overflow-y: auto !important;
    }
    .why-agy-avatar-row {
        flex-direction: column;
        align-items: center;
        gap: 12px;
    }
    .why-agy-illustration {
        max-width: 70px !important;
        width: 70px !important;
    }
    .why-agy-body p {
        font-size: 14px !important;
        line-height: 1.6;
    }
}

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
            var wrapper = window.parent.document.querySelector('[class*="st-key-why_agy_dialog_content"]');
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


@st.dialog("Hi, I'm Agy 🐾")
def render_why_agy_dialog():
    """Why Agy? origin story as @st.dialog — native Streamlit, no iframes.

    Content wrapped in st.container(key="why_agy_dialog_content") so the
    dark theme JS can target it via [class*="st-key-why_agy_dialog_content"].
    """
    st.markdown(_CSS, unsafe_allow_html=True)

    with st.container(key="why_agy_dialog_content"):
        st.markdown(_BODY_HTML, unsafe_allow_html=True)

        st.markdown(
            "<hr style='margin: 20px 0 8px; border-color: var(--border-color);'>",
            unsafe_allow_html=True,
        )
        if st.button(
            "Curious how I was built? Read the technical deep-dive →",
            key="why_agy_to_hib",
        ):
            st.session_state["active_dialog"] = "how_i_built"
            st.rerun()

    components.html(_DARK_THEME_JS, height=0)
