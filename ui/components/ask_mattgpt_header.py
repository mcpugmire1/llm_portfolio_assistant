"""
Ask Agy Header Component

Unified header component for both Landing and Conversation views.
Includes header, "How Agy searches" button, modal wrapper, and status bar.

Usage:
    from ui.components.ask_mattgpt_header import (
        get_header_css,
        render_header,
        render_status_bar,
        render_modal_wrapper_start,
        render_modal_wrapper_end,
        render_button_wiring_js
    )

    # At top of page
    st.markdown(get_header_css(), unsafe_allow_html=True)

    # Render header with button
    render_header(include_button=True)

    # Modal (if open)
    if st.session_state.get("show_how_modal", False):
        st.markdown(render_modal_wrapper_start(), unsafe_allow_html=True)
        # Modal content here
        st.markdown(render_modal_wrapper_end(), unsafe_allow_html=True)

    # Status bar
    st.markdown(render_status_bar(), unsafe_allow_html=True)
"""

import streamlit as st
import streamlit.components.v1 as components


def get_header_css() -> str:
    """
    Returns CSS for the Ask Agy header, modal, and status bar.

    Features:
    - 64px avatar with dark mode halo
    - Glass morphism button
    - Sexy modal with gradient transition
    - Flush status bar (no gaps)
    """
    return """
    <style>
    /* ============================================================================
       ASK MATTGPT/ASK AGY HEADER - Used by both Landing and Conversation views
       ============================================================================ */

    /* Base header styles - shared between views */
    .ask-header-landing,
    .ask-header-conversation {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 32px;
        min-height: 184px;
        box-sizing: border-box;
        color: white;
    }

    /* Landing page header */
    .ask-header-landing {
        /* HEADER POSITION — DO NOT TOUCH WITHOUT READING THIS:
        margin-top is calibrated to the MattGPT custom navbar height (72px, bottom=112px).
        Value: -32px pulls the header up so it tucks under the navbar, matching the
        conversation-header pages (My Work, Role Match, Banking, Cross-Industry) which
        all use -32px. Changing this breaks visual symmetry across all 7 pages.
        Audit baseline: avatar.topFromNavBottom=16px on all pages. June 2026. */

        margin-top: -32px !important;
        /* padding-top: 32px matches the conversation-header baseline — do not reduce
        or content will sit at the bottom of the header. See June 2026 header audit. */

        padding-top: 32px !important;
        margin-bottom: 0 !important;
        }

    /* Conversation view header */
    .ask-header-conversation {
        /* margin-top: -48px (not -32px like landing) — conversation view's stElementContainer
        sits 16px lower in the DOM than landing due to extra stVerticalBlock gap.
        Status bar overlap was a separate issue, fixed by zeroing status bar negative margins.
        Do not unify with landing value. Audit confirmed June 2026. */
        margin-top: -48px !important;
        padding-top: 32px !important;
        min-height: 184px !important;
        margin-bottom: 0 !important;
    }

    /* Header content wrapper */
    .header-content {
        display: flex;
        align-items: center;
        gap: 24px;
        width: 100%;
        max-width: 1200px;
        margin: 0;
    }

    /* Dark mode halo effect for header avatar */
    [data-theme="dark"] .header-agy-avatar,
    body.dark-theme .header-agy-avatar {
        filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
    }

    /* Header avatar - matches other pages */
    .header-agy-avatar {
        flex-shrink: 0;
        width: 120px !important;
        height: 120px !important;
        border-radius: 50% !important;
        border: 4px solid white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }

    /* Header text */
    .header-text h1 {
        font-size: 32px;
        margin: 0 0 8px 0;
        color: white;
        font-weight: 700;
    }

    .header-text p {
        font-size: 1.1rem;
        margin: 8px 0 0 0;
        opacity: 0.95;
        color: white;
    }



    /* ============================================================================
       HOW AGY SEARCHES BUTTON - Glass morphism style
       ============================================================================ */

    .how-agy-btn {
        padding: 10px 18px;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.3);
        color: white;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        white-space: nowrap;
        flex-shrink: 0;
    }

    .how-agy-btn:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .how-agy-btn:active {
        transform: translateY(0);
    }

    /* Close state - slightly different style */
    .how-agy-btn.how-agy-btn-close {
        background: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.5);
    }

    .how-agy-btn.how-agy-btn-close:hover {
        background: rgba(255, 255, 255, 0.4);
    }

    /* Hide the Streamlit trigger buttons */
    [class*="st-key-how_agy_trigger"],
    [class*="st-key-why_agy_header_trigger"] {
        display: none !important;
    }
    /* Also zero the outer stElementContainer wrappers — the inner button being
       position:absolute leaves the wrapper as a flex item that still contributes
       height to the layout. :has() removes the wrapper from flow entirely. */
    div[data-testid="stElementContainer"]:has([class*="st-key-how_agy_trigger"]),
    div[data-testid="stElementContainer"]:has([class*="st-key-why_agy_header_trigger"]) {
        display: none !important;

    }

    [data-testid="stMarkdown"]:has(.status-bar) {
        margin-top: -2px !important;
    }
    [data-testid="stMarkdownContainer"]:has(.status-bar) {
        margin-top: -2px !important;
    }

    /* ============================================================================
       MODAL - Clean container, no header bleed
       ============================================================================ */

    .how-agy-modal-wrapper {
        background: var(--bg-card, #ffffff);
        margin: 0 !important;
        padding: 0 20px 20px 20px;
        position: relative;
        overflow: hidden;
    }

    .how-agy-modal-container {
        background: var(--bg-card, #ffffff);
        border-radius: 16px;
        box-shadow:
            0 20px 60px rgba(0, 0, 0, 0.3),
            0 0 0 1px rgba(139, 92, 246, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        overflow: hidden;
        position: relative;
        max-width: 1000px;
        margin: 0 auto;
        animation: modalSlideIn 0.3s ease-out;
    }

    @keyframes modalSlideIn {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Modal header with gradient accent */
    .how-agy-modal-header {
        background: linear-gradient(135deg,
            rgba(102, 126, 234, 0.08) 0%,
            rgba(118, 75, 162, 0.08) 100%);
        padding: 20px 24px;
        border-bottom: 1px solid var(--border-color, #e5e7eb);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .how-agy-modal-header h2 {
        margin: 0;
        font-size: 22px;
        font-weight: 700;
        color: var(--text-heading, #1f2937);
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .how-agy-modal-header h2::before {
        content: '🔍';
        font-size: 24px;
    }

    /* Close button */
    .how-agy-modal-close {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        border: none;
        background: var(--bg-surface, #f3f4f6);
        color: var(--text-secondary, #6b7280);
        font-size: 20px;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .how-agy-modal-close:hover {
        background: var(--bg-hover, #e5e7eb);
        color: var(--text-primary, #1f2937);
    }

    /* Modal body */
    .how-agy-modal-body {
        padding: 24px;
        max-height: 70vh;
        overflow-y: auto;
    }

    /* Custom scrollbar for modal */
    .how-agy-modal-body::-webkit-scrollbar {
        width: 8px;
    }

    .how-agy-modal-body::-webkit-scrollbar-track {
        background: var(--bg-surface, #f3f4f6);
        border-radius: 4px;
    }

    .how-agy-modal-body::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #667eea, #764ba2);
        border-radius: 4px;
    }

    .how-agy-modal-body::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #5a6fd6, #6a4190);
    }

    /* Dark mode modal adjustments */
    body.dark-theme .how-agy-modal-wrapper,
    [data-theme="dark"] .how-agy-modal-wrapper {
        background: var(--bg-card, #1f2937);
    }

    body.dark-theme .how-agy-modal-container,
    [data-theme="dark"] .how-agy-modal-container {
        box-shadow:
            0 20px 60px rgba(0, 0, 0, 0.5),
            0 0 0 1px rgba(139, 92, 246, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }

    /* ============================================================================
       STATUS BAR - Flush with header/modal
       ============================================================================ */

    .status-bar {
        display: flex !important;
        gap: 24px !important;
        justify-content: center !important;
        padding: 12px 30px !important;
        background: var(--status-bar-bg, #f8f9fa) !important;
        border-bottom: 1px solid var(--status-bar-border, #e0e0e0) !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }

    .status-item {
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        font-size: 13px !important;
        color: var(--text-secondary, #6B7280) !important;
        white-space: nowrap !important;
    }

    .status-value {
        font-weight: 600;
        color: var(--text-primary, #1F2937);
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background: #10B981;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* ============================================================================
       REMOVE GAPS - Kill any Streamlit-added spacing
       ============================================================================ */

    [data-testid="stMarkdown"]:has(.ask-header-landing),
    [data-testid="stMarkdown"]:has(.ask-header-conversation),
    [data-testid="stMarkdown"]:has(.how-agy-modal-wrapper),
    [data-testid="stMarkdown"]:has(.status-bar) {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    [data-testid="stMarkdown"]:has(.ask-header-landing) + [data-testid="stMarkdown"],
    [data-testid="stMarkdown"]:has(.ask-header-conversation) + [data-testid="stMarkdown"],
    [data-testid="stMarkdown"]:has(.how-agy-modal-wrapper) + [data-testid="stMarkdown"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Hide the trigger button containers AND remove their space */
    [class*="st-key-how_agy_trigger"],
    [class*="st-key-why_agy_header_trigger"] {
        display: none !important;
    }
    div[data-testid="stElementContainer"]:has([class*="st-key-how_agy_trigger"]),
    div[data-testid="stElementContainer"]:has([class*="st-key-why_agy_header_trigger"]) {
        display: none !important;
    }

    /* Kill gaps on all elements between header and status bar */
    .ask-header-landing + *,
    .ask-header-conversation + * {
        margin-top: 0 !important;
    }

    /* Status bar sits flush below header — no negative pull-up.
       Negative margin was causing 35px overlap into the header band,
       making the purple area look cramped. Zeroed June 2026 audit. */
    .status-bar {
        margin-top: 0 !important;
        position: relative !important;
        overflow: visible !important;
        padding-bottom: 15px !important;
        padding-left: 15px !important;
        padding-right: 15px !important;
    }

     /* ============================================================================
       MOBILE RESPONSIVE (<768px) — must come AFTER global .status-bar reset above
       so mobile margin-top: 40px wins the cascade on narrow viewports.
       ============================================================================ */
    @media (max-width: 768px) {
            .status-bar {
                margin-left: -16px !important;
                margin-right: -16px !important;
                padding-left: 16px !important;
                padding-right: 16px !important;
                margin-top: 14px !important;
            }

        .ask-header-landing {
            padding: 20px 16px 20px 16px !important;
            min-height: 145.59px !important;
            margin: 60px -16px 0px -16px !important;
            overflow: visible !important;
        }

       .ask-header-conversation {
            padding: 20px 16px 20px 16px !important;
            min-height: 145.59px !important;
            margin: 60px -16px 0px -16px !important;  /* clear nav + edge-to-edge */
            overflow: visible !important;
            position: relative !important;
        }

        .header-content {
            flex-direction: row !important;
            align-items: flex-start !important;
            text-align: left !important;
            gap: 12px !important;
            flex-wrap: wrap !important;
            position: relative;
            justify-content: flex-start !important;
            padding-left: 10px !important;
        }

        .header-content > div:first-child {
            gap: 12px !important;
        }

        .header-agy-avatar {
            width: 64px !important;
            height: 64px !important;
            border: 4px solid white !important;
        }


        .header-text h1 {
            font-size: 20px !important;
            margin-top: 20px !important;
            margin-bottom: 4px !important;
            white-space: nowrap !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }

        .header-text p {
            margin-top: 22px !important;
            font-size: 13px !important;
            line-height: 1.4 !important;
        }


        .ask-header-landing .how-agy-btn,
        .ask-header-conversation .how-agy-btn {
            font-size: 11px !important;
            padding: 3px 10px !important;
            height: auto !important;
            min-height: unset !important;
            margin-top: 2px !important;
        }


        .ask-header-conversation .how-agy-btn {
            position: absolute !important;
            top: 2px !important;
            right: 16px !important;
            margin: 0 !important;

        }

        .how-agy-modal-wrapper {
            margin-top: 20px !important;
        }

        div[data-testid="stMarkdownContainer"] > div.how-agy-modal-wrapper {
            margin-top: 8px !important;
        }

        [data-testid="stMarkdownContainer"]:has(.how-agy-modal-wrapper) {
            margin-top: 8px !important;
        }

        .how-agy-btn {
            position: absolute !important;
            top: 1px !important;
            right: 16px !important;
            font-size: 10px !important;
            padding: 4px 8px !important;
            margin: 0 !important;
        }

    }

    /* Extend background DOWN to cover purple header bleed-through */
    .status-bar::before {
        content: '' !important;
        position: absolute !important;
        bottom: -3px !important;
        left: 0 !important;
        right: 0 !important;
        height: 2px !important;
        background: var(--status-bar-bg, #f8f9fa) !important;
        z-index: -1 !important;
    }

    /* Nuclear option: remove all vertical block gaps in the header area */
    [data-testid="stVerticalBlock"]:has(.ask-header-landing) > div,
    [data-testid="stVerticalBlock"]:has(.ask-header-conversation) > div {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    /* Target stElementContainer wrappers around header and status bar */
    [data-testid="stElementContainer"]:has(.ask-header-landing),
    [data-testid="stElementContainer"]:has(.ask-header-conversation) {
        margin: 0 !important;
        padding: 0 !important;
    }

    [data-testid="stElementContainer"]:has(.status-bar) {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding: 0 !important;
    }


    /* Kill the gap AFTER the header container */
    [data-testid="stElementContainer"]:has(.ask-header-landing) + [data-testid="stElementContainer"],
    [data-testid="stElementContainer"]:has(.ask-header-conversation) + [data-testid="stElementContainer"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Status bar container — no negative pull-up (zeroed June 2026 audit) */
    [data-testid="stElementContainer"]:has(.status-bar) {
        margin-top: 0 !important;
        overflow: visible !important;
        padding-bottom: 5px !important;
    }

    /* KILL THE IFRAME CONTAINER GAP */
    [data-testid="stElementContainer"]:has(iframe[title="st.iframe"]) {
        margin: 0 !important;
        padding: 0 !important;
        height: 0 !important;
        min-height: 0 !important;
        overflow: hidden !important;
        display: block !important;
        line-height: 0 !important;
    }

    /* Also target by the emotion-cache class pattern for iframes */
    .stElementContainer:has(.stIFrame) {
        margin: 0 !important;
        padding: 0 !important;
        height: 0 !important;
        line-height: 0 !important;
    }
    </style>
    """


def render_header(include_button: bool = True, view: str = "landing") -> None:
    """
    Render the Ask Agy header.

    Args:
        include_button: Whether to include the "How Agy searches" button
        view: "landing" or "conversation" - determines which CSS class to use
    """
    # Inject header CSS (self-contained)
    st.markdown(get_header_css(), unsafe_allow_html=True)

    # Hidden Streamlit button — opens How Agy Searches dialog via active_dialog flag.
    # No longer toggles show_how_modal; dialog close is handled by @st.dialog (X/Escape/backdrop).
    # Button label is always "How Agy searches" — no ✕ Close state needed.
    if st.button("trigger", key="how_agy_trigger"):
        st.session_state["active_dialog"] = "how_agy"
        st.rerun()

    # Hidden trigger for Why Agy badge — wired via JS bridge below.
    if st.button("", key="why_agy_header_trigger"):
        st.session_state["active_dialog"] = "why_agy"
        st.rerun()

    # Build button HTML — always shows "How Agy searches" (no open/close state)
    button_html = ""
    if include_button:
        button_html = (
            '<button class="how-agy-btn" id="how-agy-btn">🔍 How Agy searches</button>'
        )

    # Determine header class based on view
    header_class = (
        "ask-header-landing" if view == "landing" else "ask-header-conversation"
    )

    # Header HTML
    header_html = (
        f"""
        <div class="{header_class}">
            <div class="header-content" style="display: flex; justify-content: space-between; ">
                <div style="display: flex; align-items: flex-start; gap: 24px;">
                    <div style="position: relative; display: inline-block; flex-shrink: 0;">
                        <img class="header-agy-avatar"
                            src="/app/static/agy_avatar.png"
                            width="120" height="120"
                            alt="Agy"/>
                        <span class="why-agy-badge--header" id="why-agy-badge-header">i</span>
                    </div>
                    <div class="header-text">
                        <h1>Ask Agy</h1>
                        <p>Meet Agy 🐾, tracking down insights across 100+ stories.</p>
                    </div>
                </div>
                """
        + button_html
        + """
            </div>
        </div>
    """
    )

    st.markdown(header_html, unsafe_allow_html=True)

    # Wire the HTML button to the Streamlit button
    if include_button:
        render_button_wiring_js()

    # Wire the badge to its hidden trigger (always, not conditional on include_button)
    components.html(
        """
        <script>
        (function() {
            function wireBadge() {
                var parentDoc = window.parent.document;
                var badge = parentDoc.getElementById('why-agy-badge-header');
                var btn = parentDoc.querySelector('[class*="st-key-why_agy_header_trigger"] button');
                if (badge && btn && !badge.dataset.wired) {
                    badge.dataset.wired = 'true';
                    // pointerdown fires immediately on both mouse and touch —
                    // avoids the 300ms click delay on mobile that makes the badge
                    // appear unresponsive on tap.
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


def render_button_wiring_js() -> None:
    """Render the JavaScript that wires the HTML button to Streamlit state."""
    components.html(
        """
        <script>
        (function() {
            function wireButton() {
                var parentDoc = window.parent.document;
                var htmlBtn = parentDoc.getElementById('how-agy-btn');
                var stBtn = parentDoc.querySelector('[class*="st-key-how_agy_trigger"] button');

                if (htmlBtn && stBtn && !htmlBtn.dataset.wired) {
                    htmlBtn.dataset.wired = 'true';

                    htmlBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        stBtn.click();
                    });

                    return true;
                }
                return false;
            }

            // Try immediately, then retry
            if (!wireButton()) {
                var attempts = 0;
                var interval = setInterval(function() {
                    attempts++;
                    if (wireButton() || attempts > 10) {
                        clearInterval(interval);
                    }
                }, 200);
            }
        })();
        </script>
        """,
        height=0,
    )


def render_modal_wrapper_start() -> str:
    """
    Returns the opening HTML for the modal wrapper.
    Just provides the gradient background - content handles its own structure.
    """
    return """
    <div class="how-agy-modal-wrapper">
    """


def render_modal_wrapper_end() -> str:
    """Returns the closing HTML for the modal wrapper."""
    return """
    </div>
    """


def render_modal_close_wiring_js() -> None:
    """Render the JavaScript that wires the modal close button to Streamlit state."""
    components.html(
        """
        <script>
        (function() {
            function wireCloseButton() {
                var parentDoc = window.parent.document;
                var closeBtn = parentDoc.getElementById('how-agy-modal-close');
                var stBtn = parentDoc.querySelector('[class*="st-key-how_agy_trigger"] button');

                if (closeBtn && stBtn && !closeBtn.dataset.wired) {
                    closeBtn.dataset.wired = 'true';

                    closeBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        stBtn.click();
                    });

                    return true;
                }
                return false;
            }

            // Try immediately, then retry
            if (!wireCloseButton()) {
                var attempts = 0;
                var interval = setInterval(function() {
                    attempts++;
                    if (wireCloseButton() || attempts > 10) {
                        clearInterval(interval);
                    }
                }, 200);
            }
        })();
        </script>
        """,
        height=0,
    )


def render_status_bar() -> str:
    """Returns the status bar HTML."""
    return """
    <div class="status-bar">
        <div class="status-item">
            <span class="status-dot"></span>
            <span>Semantic search <span class="status-value">active</span></span>
        </div>
        <div class="status-item">
            <span>Pinecone index <span class="status-value">ready</span></span>
        </div>
        <div class="status-item">
            <span>100+ stories <span class="status-value">indexed</span></span>
        </div>
    </div>
    """
