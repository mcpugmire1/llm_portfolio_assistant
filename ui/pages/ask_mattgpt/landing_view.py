"""
Ask Agy Landing View

Landing page UI for Ask Agy with:
- Purple hero header with Agy introduction
- Status bar showing system readiness
- Suggestion chips for quick starts
- Main input form
- Integration with backend service
"""

import streamlit as st
import streamlit.components.v1 as components

from ui.components.ask_mattgpt_header import (
    render_header,
    render_status_bar,
)
from ui.components.how_agy_dialog import render_how_agy_dialog
from ui.components.how_i_built_dialog import render_how_i_built_dialog
from ui.components.why_agy_dialog import render_why_agy_dialog
from ui.image_assets import AGY_AVATAR_B64
from ui.pages.ask_mattgpt.styles import get_landing_css


def _hand_off_to_conversation(query: str, force_answer: bool = False) -> None:
    """Start a fresh conversation with this question (widget callback).

    Runs before the script, so the run the tap or Enter starts already routes
    to the conversation view (seed_prompt), which answers below the question.
    Handing off from the landing script instead took extra runs, each ending
    in st.rerun(), and the landing hero blanked and its elements lingered
    under the conversation between them. Suggestion chips set
    __ask_force_answer__ as before; typed questions still meet the nonsense
    filter.
    """
    query = (query or "").strip()
    if not query:
        return
    st.session_state["ask_transcript"] = []
    st.session_state["seed_prompt"] = query
    st.session_state["ask_input_value"] = query
    if force_answer:
        st.session_state["__ask_force_answer__"] = True


def render_landing_page(stories: list[dict]):
    """
    Render the Ask Agy landing page (empty state) matching the wireframe.
    NAVBAR IS RENDERED BY PARENT - NO NAVBAR CSS HERE
    """

    # Scroll to top on page load
    components.html(
        """
        <script>
            setTimeout(function() {
                const main = window.parent.document.querySelector('[data-testid="stMain"]');
                if (main) main.scrollTop = 0;
            }, 100);
        </script>
        """,
        height=0,
    )

    # Initialize processing flag
    if "processing_suggestion" not in st.session_state:
        st.session_state["processing_suggestion"] = False

    # === INJECT CSS ===
    st.markdown(get_landing_css(), unsafe_allow_html=True)

    # === CSS now loaded from styles.py ===

    # === PURPLE HEADER ===
    # Header with button
    render_header(include_button=True, view="landing")

    # How Agy Searches dialog (MATTGPT-110) — @st.dialog, no inline expander.
    # active_dialog flag set by how_agy_trigger button in ask_mattgpt_header.py.
    # Clear flag after call so X/Escape/backdrop dismiss doesn't reopen on next rerun.
    if st.session_state.get("active_dialog") == "why_agy":
        render_why_agy_dialog()
        st.session_state.pop("active_dialog", None)
    elif st.session_state.get("active_dialog") == "how_agy":
        render_how_agy_dialog()
        st.session_state.pop("active_dialog", None)
    elif st.session_state.get("active_dialog") == "how_i_built":
        render_how_i_built_dialog()
        st.session_state.pop("active_dialog", None)

    # === STATUS BAR ===
    st.markdown(render_status_bar(), unsafe_allow_html=True)

    with st.container(key="intro_section"):
        # === MAIN INTRO SECTION ===
        st.markdown(
            f"""
        <div class="main-intro-section">
            <div class="main-avatar" style="position: relative; display: inline-block;">
                <img src="{AGY_AVATAR_B64}" width="120" height="120" alt="Agy"/>
                <span class="why-agy-badge" id="why-agy-badge-landing">i</span>
            </div>
            <h2 class="welcome-title">Hi, I'm Agy 🐾</h2>
            <p class="intro-text-primary">
                Go deeper than a resume. Ask me anything about Matt's 100+ stories. I'll connect the dots.
            </p>
            <p style="font-size: 13px; font-style: italic; color: var(--text-muted); margin-top: 2px; margin-bottom: 0;">
                Named in honor of Matt's Plott Hound companion.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Hidden trigger for Why Agy badge — badge click fires this via JS bridge.
        st.markdown(
            '<style>[class*="st-key-why_agy_landing_body_trigger"] { display: none !important; }</style>',
            unsafe_allow_html=True,
        )
        if st.button("", key="why_agy_landing_body_trigger"):
            st.session_state["active_dialog"] = "why_agy"
            st.rerun()
        components.html(
            """
<script>
(function() {
    function wireBadge() {
        var parentDoc = window.parent.document;
        var badge = parentDoc.getElementById('why-agy-badge-landing');
        var btn = parentDoc.querySelector('[class*="st-key-why_agy_landing_body_trigger"] button');
        if (badge && btn && !badge.dataset.wired) {
            badge.dataset.wired = 'true';
            badge.addEventListener('pointerdown', function(e) {
                e.preventDefault();
                btn.click();
            });
            return true;
        }
        return false;
    }
    if (!wireBadge()) {
        var attempts = 0;
        var iv = setInterval(function() {
            if (wireBadge() || ++attempts > 10) clearInterval(iv);
        }, 200);
    }
})();
</script>
""",
            height=0,
        )

        st.markdown(
            '<div class="suggested-title">TRY ASKING:</div>', unsafe_allow_html=True
        )

        # === SUGGESTED QUESTION BUTTONS ===
        qs = [
            (
                "💳",
                "Payments at JP Morgan",
                "How did Matt modernize payments across 12+ countries at JP Morgan?",
            ),
            (
                "🔬",
                "Failure & experiments",
                "Tell me about Matt's early failure and experimentation approach",
            ),
            (
                "🚀",
                "Startup-speed teams",
                "How does Matt build teams that ship like startups in enterprise?",
            ),
            (
                "🏗️",
                "Cloud Innovation Center",
                "How did Matt establish and expand the Cloud Innovation Center in Atlanta?",
            ),
            (
                "📈",
                "Talent development",
                "How did Matt scale learning and talent development at Accenture?",
            ),
            (
                "💥",
                "Leading through resistance",
                "How does Matt handle resistance and failure in transformations?",
            ),
        ]

        is_mobile = int(st.session_state.get("_browser_screen_size") or "1024") < 768

        # Disable all buttons when any is processing
        disabled = st.session_state.get("processing_suggestion", False)

        with st.container(key="chip_grid"):
            # MATTGPT-139: static HTML chips + hidden st.button receivers + JS bridge.
            # Desktop uses full query text; mobile uses short_label for pill layout.
            # CSS lives in styles.py. JS bridge count parametrized to len(qs).
            if is_mobile:
                chips_html = '<div class="suggested-chips-mobile">'
                for i, (icon, short_label, _q) in enumerate(qs):
                    chips_html += f'<button class="suggested-chip" id="chip-suggested-{i}">{icon}&nbsp;&nbsp;{short_label}</button>'
                chips_html += '</div>'
            else:
                chips_html = '<div class="suggested-chips-grid">'
                for i, (icon, _short_label, q) in enumerate(qs):
                    chips_html += f'<button class="suggested-chip" id="chip-suggested-{i}">{icon}&nbsp;&nbsp;{q}</button>'
                chips_html += '</div>'
            st.markdown(chips_html, unsafe_allow_html=True)

            # Hidden receivers: off-screen via CSS, identical click logic for both paths.
            for i, (_icon, _short_label, q) in enumerate(qs):
                st.button(
                    "",
                    key=f"suggested_{i}",
                    disabled=disabled,
                    on_click=_hand_off_to_conversation,
                    args=(q,),
                    kwargs={"force_answer": True},
                )

            n_chips = len(qs)
            components.html(
                f"""
<script>
(function() {{
    function wireChips() {{
        var parentDoc = window.parent.document;
        for (var i = 0; i < {n_chips}; i++) {{
            var chip = parentDoc.getElementById('chip-suggested-' + i);
            if (chip) {{
                chip.onclick = (function(idx) {{
                    return function() {{
                        var btn = parentDoc.querySelector('[class*="st-key-suggested_' + idx + '"] button');
                        if (btn) btn.click();
                    }};
                }})(i);
            }}
        }}
    }}
    setTimeout(wireChips, 100);
    setTimeout(wireChips, 300);
    setTimeout(wireChips, 600);
    setTimeout(wireChips, 1000);
}})();
</script>
""",
                height=0,
            )

    # === INPUT AREA ===
    st.markdown('<div class="landing-input-container">', unsafe_allow_html=True)

    # Inject mobile CSS directly here to ensure it loads
    st.markdown(
        """
        <style>
        @media (max-width: 767px) {
            /* NUCLEAR OPTION: Override min-width: 100% on columns */
            .st-key-landing_input_row .stColumn {
                min-width: 0 !important;
                min-inline-size: 0 !important;
                flex-basis: auto !important;
            }

            /* Parent horizontal block */
            .st-key-landing_input_row .stHorizontalBlock {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                gap: 8px !important;
                align-items: center !important;
            }

            /* First column - input - grow to fill */
            .st-key-landing_input_row .stColumn:first-child {
                flex: 1 1 auto !important;
                min-width: 0 !important;
                width: auto !important;
            }

            /* Second column - button - shrink to fit */
            .st-key-landing_input_row .stColumn:last-child {
                flex: 0 0 auto !important;
                width: auto !important;
                min-width: 0 !important;
            }

            /* Button styling */
            .st-key-landing_ask,
            .st-key-landing_ask .stButton,
            .st-key-landing_ask button {
                width: auto !important;
                white-space: nowrap !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Use container with key for reliable CSS targeting on mobile
    with st.container(key="landing_input_row"):
        # Use columns to keep input and button on same line
        col_input, col_button = st.columns([5, 1], gap="small")

        with col_input:
            user_input = st.text_input(
                "Ask about Matt's experience...",
                key="landing_input",
                label_visibility="collapsed",
                placeholder="Ask about projects, methods, or outcomes...",
                on_change=lambda: _hand_off_to_conversation(
                    st.session_state.get("landing_input", "")
                ),
            )

        with col_button:
            # Disable button if input is empty OR if we're currently processing
            button_disabled = not user_input or disabled
            st.button(
                "Ask Agy 🐾",
                key="landing_ask",
                type="primary",
                disabled=button_disabled,
                on_click=lambda: _hand_off_to_conversation(
                    st.session_state.get("landing_input", "")
                ),
            )

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="powered-by-text">Powered by OpenAI with semantic search across 100+ case studies</p>',
        unsafe_allow_html=True,
    )

    # === ADD FOOTER ===
    from ui.components.footer import render_footer

    render_footer()
