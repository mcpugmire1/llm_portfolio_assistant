"""
Ask MattGPT Header Component

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
    Returns CSS for the Ask MattGPT header, modal, and status bar.

    Features:
    - 64px avatar with dark mode halo
    - Glass morphism button
    - Sexy modal with gradient transition
    - Flush status bar (no gaps)
    """
    return """
    <style>
    /* ============================================================================
       ASK MATTGPT HEADER - Used by both Landing and Conversation views
       ============================================================================ */

    /* Base header styles - shared between views */
    .ask-header-landing,
    .ask-header-conversation {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Landing page header */
    .ask-header-landing {
        margin-top: -65px !important;
        margin-bottom: 0 !important;
    }

    /* Conversation view header */
    .ask-header-conversation {
        margin-top: -80px !important;
        margin-bottom: 0 !important;
    }

    /* Header content wrapper */
    .header-content {
        display: flex;
        align-items: center;
        gap: 24px;
        width: 100%;
    }

    /* Dark mode halo effect for header avatar */
    [data-theme="dark"] .header-agy-avatar,
    body.dark-theme .header-agy-avatar {
        filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
    }

    /* Header text */
    .header-text h1 {
        font-size: 32px;
        margin: 0 0 8px 0;
        color: white;
        font-weight: 700;
    }

    .header-text p {
        font-size: 16px;
        margin: 0;
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

    /* Hide the Streamlit trigger button */
    [class*="st-key-how_agy_trigger"] {
        position: absolute !important;
        left: -9999px !important;
        opacity: 0 !important;
        pointer-events: none !important;
        height: 0 !important;
        overflow: hidden !important;
    }

    /* ============================================================================
       MODAL - Sexy gradient transition from header
       ============================================================================ */

    .how-agy-modal-wrapper {
        background: linear-gradient(180deg, #764ba2 0%, #5a3d7a 8%, #2d2d44 25%, var(--bg-card, #ffffff) 100%);
        margin: 0 !important;
        padding: 0 20px 20px 20px;
        position: relative;
        overflow: hidden;
    }

    /* Subtle animated gradient overlay */
    .how-agy-modal-wrapper::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 150px;
        background: linear-gradient(135deg,
            rgba(102, 126, 234, 0.1) 0%,
            rgba(118, 75, 162, 0.15) 50%,
            transparent 100%);
        pointer-events: none;
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
        background: linear-gradient(180deg, #764ba2 0%, #4a3660 8%, #1a1a2e 25%, var(--bg-card, #1f2937) 100%);
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

    /* Hide the trigger button container AND remove its space */
    [class*="st-key-how_agy_trigger"] {
        position: absolute !important;
        left: -9999px !important;
        opacity: 0 !important;
        pointer-events: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
    }

    /* Kill gaps on all elements between header and status bar */
    .ask-header-landing + *,
    .ask-header-conversation + * {
        margin-top: 0 !important;
    }

    /* Force status bar flush - pull up to close gap */
    .status-bar {
        margin-top: -15px !important;
    }

    /* Nuclear option: remove all vertical block gaps in the header area */
    [data-testid="stVerticalBlock"]:has(.ask-header-landing) > div,
    [data-testid="stVerticalBlock"]:has(.ask-header-conversation) > div {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    /* Target stElementContainer wrappers around header and status bar */
    [data-testid="stElementContainer"]:has(.ask-header-landing),
    [data-testid="stElementContainer"]:has(.ask-header-conversation),
    [data-testid="stElementContainer"]:has(.status-bar) {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Kill the gap AFTER the header container */
    [data-testid="stElementContainer"]:has(.ask-header-landing) + [data-testid="stElementContainer"],
    [data-testid="stElementContainer"]:has(.ask-header-conversation) + [data-testid="stElementContainer"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Target any element immediately before status bar */
    [data-testid="stElementContainer"]:has(.status-bar) {
        margin-top: -20px !important;
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
    Render the Ask MattGPT header.

    Args:
        include_button: Whether to include the "How Agy searches" button
        view: "landing" or "conversation" - determines which CSS class to use
    """
    # Inject header CSS (self-contained)
    st.markdown(get_header_css(), unsafe_allow_html=True)

    # Hidden Streamlit button for state management
    if st.button("trigger", key="how_agy_trigger"):
        st.session_state["show_how_modal"] = not st.session_state.get(
            "show_how_modal", False
        )
        st.rerun()

    # Build button HTML - text changes based on modal state
    button_html = ""
    if include_button:
        is_open = st.session_state.get("show_how_modal", False)
        if is_open:
            button_html = '<button class="how-agy-btn how-agy-btn-close" id="how-agy-btn">✕ Close</button>'
        else:
            button_html = '<button class="how-agy-btn" id="how-agy-btn">🔍 How Agy searches</button>'

    # Determine header class based on view
    header_class = (
        "ask-header-landing" if view == "landing" else "ask-header-conversation"
    )

    # Header HTML
    header_html = (
        f"""
        <div class="{header_class}">
            <div class="header-content" style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 24px;">
                    <img class="header-agy-avatar"
                        src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_avatar.png"
                        width="64" height="64"
                        style="width: 64px; height: 64px; border-radius: 50%; border: 3px solid white !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;"
                        alt="Agy"/>
                    <div class="header-text">
                        <h1>Ask MattGPT</h1>
                        <p>Meet Agy 🐾 — Tracking down insights from 20+ years of transformation experience</p>
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
                        console.log('[How Agy Button] Clicked');
                        stBtn.click();
                    });

                    console.log('[How Agy Button] Wired successfully');
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
                        console.log('[Modal Close] Clicked');
                        stBtn.click();
                    });

                    console.log('[Modal Close] Wired successfully');
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
            <span>130+ stories <span class="status-value">indexed</span></span>
        </div>
    </div>
    """


def get_how_agy_flow_html() -> str:
    """
    3-step flow visualization for How Agy Works modal.
    Theme-aware: detects dark mode from parent page.

    Updated Dec 2024 to reflect current architecture:
    - Pure semantic search (OpenAI text-embedding-3-small)
    - 3-stage quality pipeline (rules → semantic router → confidence)
    - Client diversity algorithm
    - Behavioral query specialization for interview prep
    """
    return """
    <div id="flow-container">
        <style>
            /* Base/Light theme variables */
            :root {
                --modal-bg: linear-gradient(135deg, #FAFAFA 0%, #F9FAFB 100%);
                --modal-border: #E5E7EB;
                --modal-card-bg: white;
                --modal-text-primary: #1F2937;
                --modal-text-secondary: #4B5563;
                --modal-text-muted: #6B7280;
                --modal-purple-text: #6B21A8;
                --modal-purple-border: #E9D5FF;
                --modal-blue-text: #1E40AF;
                --modal-blue-border: #BFDBFE;
                --modal-green-text: #065F46;
                --modal-green-border: #A7F3D0;
                --modal-orange-text: #92400E;
                --modal-orange-border: #FDE68A;
                --modal-pill-bg: #EDE9FE;
                --modal-pill-text: #7C3AED;
                --modal-pill-border: #DDD6FE;
                --modal-arrow: #A78BFA;
            }

            /* Dark theme overrides */
            .dark-theme {
                --modal-bg: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                --modal-border: #374151;
                --modal-card-bg: #1f2937;
                --modal-text-primary: #f3f4f6;
                --modal-text-secondary: #d1d5db;
                --modal-text-muted: #9ca3af;
                --modal-purple-text: #c4b5fd;
                --modal-purple-border: #4c1d95;
                --modal-blue-text: #93c5fd;
                --modal-blue-border: #1e40af;
                --modal-green-text: #6ee7b7;
                --modal-green-border: #065f46;
                --modal-orange-text: #fcd34d;
                --modal-orange-border: #92400e;
                --modal-pill-bg: #3b2e5a;
                --modal-pill-text: #c4b5fd;
                --modal-pill-border: #5b4b7a;
                --modal-arrow: #a78bfa;
            }

            #flow-wrapper {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                padding: 28px;
                padding-bottom: 40px;
                margin-bottom: 20px;
                background: var(--modal-bg);
                border-radius: 16px;
                border: 2px solid var(--modal-border);
                transition: all 0.3s ease;
            }

            .step-header {
                display: flex;
                align-items: center;
                gap: 16px;
                margin-bottom: 20px;
            }

            .step-number {
                background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
                color: white;
                width: 48px;
                height: 48px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 22px;
                flex-shrink: 0;
                box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);
            }

            .step-title {
                margin: 0;
                color: var(--modal-text-primary);
                font-size: 24px;
                font-weight: 700;
            }

            .step-content {
                margin-left: 64px;
            }

            .query-card {
                background: var(--modal-card-bg);
                padding: 24px;
                border-radius: 12px;
                border: 2px solid var(--modal-purple-border);
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }

            .query-text {
                color: var(--modal-text-secondary);
                font-size: 16px;
                font-style: italic;
                line-height: 1.6;
            }

            .arrow {
                text-align: center;
                color: var(--modal-arrow);
                font-size: 40px;
                margin: 20px 0;
                font-weight: 300;
            }

            /* Pipeline visualization */
            .pipeline-flow {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }

            .pipeline-stage {
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 10px 16px;
                border-radius: 24px;
                font-size: 13px;
                font-weight: 600;
            }

            .pipeline-stage.rules {
                background: #FEF3C7;
                color: #92400E;
                border: 2px solid #FDE68A;
            }

            .pipeline-stage.router {
                background: #D1FAE5;
                color: #065F46;
                border: 2px solid #A7F3D0;
            }

            .pipeline-stage.confidence {
                background: #EDE9FE;
                color: #5B21B6;
                border: 2px solid #DDD6FE;
            }

            .dark-theme .pipeline-stage.rules {
                background: #78350f;
                color: #fef3c7;
                border-color: #92400e;
            }

            .dark-theme .pipeline-stage.router {
                background: #064e3b;
                color: #d1fae5;
                border-color: #065f46;
            }

            .dark-theme .pipeline-stage.confidence {
                background: #4c1d95;
                color: #ede9fe;
                border-color: #5b21b6;
            }

            .pipeline-arrow {
                color: var(--modal-text-muted);
                font-size: 16px;
                font-weight: bold;
            }

            .search-cards {
                display: flex;
                gap: 16px;
                margin-bottom: 16px;
            }

            .search-card {
                flex: 1;
                background: var(--modal-card-bg);
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }

            .search-card.semantic {
                border: 2px solid var(--modal-purple-border);
            }

            .search-card.behavioral {
                border: 2px solid var(--modal-green-border);
            }

            .search-card.diversity {
                border: 2px solid var(--modal-orange-border);
            }

            .card-title {
                font-weight: 700;
                font-size: 15px;
                margin-bottom: 8px;
            }

            .card-title.semantic { color: #7C3AED; }
            .card-title.behavioral { color: #059669; }
            .card-title.diversity { color: #D97706; }

            .dark-theme .card-title.behavioral { color: #6ee7b7; }
            .dark-theme .card-title.diversity { color: #fbbf24; }

            .card-desc {
                font-size: 13px;
                line-height: 1.5;
            }

            .card-desc.semantic { color: var(--modal-purple-text); }
            .card-desc.behavioral { color: var(--modal-green-text); }
            .card-desc.diversity { color: var(--modal-orange-text); }

            .result-wrapper {
                background: var(--modal-card-bg);
                border: 3px solid #8B5CF6;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 8px 20px rgba(139, 92, 246, 0.25);
            }

            .result-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }

            .result-title {
                font-weight: 700;
                font-size: 17px;
                margin-bottom: 8px;
            }

            .result-desc {
                font-size: 15px;
                opacity: 0.95;
                line-height: 1.6;
            }

            .pills {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }

            .pill {
                background: var(--modal-pill-bg);
                color: var(--modal-pill-text);
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 700;
                border: 2px solid var(--modal-pill-border);
            }

            .pill.blue {
                background: #E0E7FF;
                color: #4F46E5;
                border-color: #C7D2FE;
            }

            .pill.green {
                background: #D1FAE5;
                color: #065F46;
                border-color: #A7F3D0;
            }

            .dark-theme .pill.blue {
                background: #312e81;
                color: #a5b4fc;
                border-color: #4338ca;
            }

            .dark-theme .pill.green {
                background: #064e3b;
                color: #6ee7b7;
                border-color: #065f46;
            }

            .step-section {
                margin-bottom: 48px;
            }

            .step-section:last-child {
                margin-bottom: 0;
            }

            .confidence-badge {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: #D1FAE5;
                color: #065F46;
                padding: 6px 12px;
                border-radius: 16px;
                font-size: 12px;
                font-weight: 600;
                margin-top: 12px;
            }

            .dark-theme .confidence-badge {
                background: #064e3b;
                color: #6ee7b7;
            }
        </style>

        <div id="flow-wrapper">
            <!-- Step 1: You Ask -->
            <div class="step-section">
                <div class="step-header">
                    <div class="step-number">1</div>
                    <h3 class="step-title">You Ask</h3>
                </div>
                <div class="step-content">
                    <div class="query-card">
                        <div class="query-text">"Tell me about a time you dealt with a difficult stakeholder"</div>
                    </div>
                </div>
            </div>

            <!-- Arrow -->
            <div class="arrow">↓</div>

            <!-- Step 2: Agy Searches -->
            <div class="step-section">
                <div class="step-header">
                    <div class="step-number">2</div>
                    <h3 class="step-title">Agy Searches</h3>
                </div>
                <div class="step-content">
                    <!-- Pipeline visualization -->
                    <div class="pipeline-flow">
                        <div class="pipeline-stage rules">⚡ Quality Filter</div>
                        <span class="pipeline-arrow">→</span>
                        <div class="pipeline-stage router">🎯 Intent Router</div>
                        <span class="pipeline-arrow">→</span>
                        <div class="pipeline-stage confidence">📊 Confidence Gate</div>
                    </div>

                    <div class="search-cards">
                        <div class="search-card semantic">
                            <div class="card-title semantic">🧠 Semantic Search</div>
                            <div class="card-desc semantic">Finds stories by meaning using AI embeddings, not just keyword matching</div>
                        </div>
                        <div class="search-card behavioral">
                            <div class="card-title behavioral">🎤 Interview Mode</div>
                            <div class="card-desc behavioral">Recognizes behavioral questions and surfaces leadership & soft-skill stories</div>
                        </div>
                    </div>
                    <div class="search-card diversity" style="margin-top: 0;">
                        <div class="card-title diversity">🎲 Result Diversity</div>
                        <div class="card-desc diversity">Shows varied experiences across different clients and industries—no repetitive results</div>
                    </div>
                </div>
            </div>

            <!-- Arrow -->
            <div class="arrow">↓</div>

            <!-- Step 3: You Get Results -->
            <div class="step-section">
                <div class="step-header">
                    <div class="step-number">3</div>
                    <h3 class="step-title">You Get Results</h3>
                </div>
                <div class="step-content">
                    <div class="result-wrapper">
                        <div class="result-card">
                            <div class="result-title">Navigating Executive Resistance at Fortune 100 Bank</div>
                            <div class="result-desc">Turned a skeptical CTO into a transformation champion through deep listening, small wins, and building trust over 6 months...</div>
                        </div>
                        <div class="pills">
                            <span class="pill">Stakeholder Management</span>
                            <span class="pill blue">Financial Services</span>
                            <span class="pill green">Leadership</span>
                        </div>
                        <div class="confidence-badge">
                            <span>✓</span> High confidence match
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        (function() {
            // Detect dark mode from parent page
            function detectTheme() {
                try {
                    var parentBody = window.parent.document.body;
                    var isDark = parentBody.classList.contains('dark-theme') ||
                                 parentBody.getAttribute('data-theme') === 'dark';
                    return isDark;
                } catch(e) {
                    // Cross-origin fallback: check media query
                    return window.matchMedia('(prefers-color-scheme: dark)').matches;
                }
            }

            function applyTheme() {
                var container = document.getElementById('flow-wrapper');
                if (detectTheme()) {
                    container.classList.add('dark-theme');
                } else {
                    container.classList.remove('dark-theme');
                }
            }

            // Apply on load
            applyTheme();

            // Re-check periodically (for dynamic theme switches)
            setInterval(applyTheme, 1000);
        })();
    </script>
    """


def get_technical_details_html() -> str:
    """
    Technical details section for How Agy Works modal.
    Theme-aware: detects dark mode from parent page.

    Updated Dec 2024 to reflect current architecture:
    - OpenAI text-embedding-3-small embeddings
    - 3-stage quality filtering pipeline (rules → semantic router → confidence)
    - Client diversity algorithm for varied results
    - Behavioral query specialization for interview prep
    """
    return """
    <div id="tech-container">
        <style>
            :root {
                --modal-bg: linear-gradient(135deg, #FAFAFA 0%, #F9FAFB 100%);
                --modal-border: #E5E7EB;
                --modal-card-bg: white;
                --modal-text-primary: #1F2937;
                --modal-text-secondary: #4B5563;
                --modal-text-muted: #6B7280;
                --modal-purple-text: #6B21A8;
                --modal-purple-border: #E9D5FF;
                --modal-blue-text: #1E40AF;
                --modal-blue-border: #BFDBFE;
                --modal-green-text: #065F46;
                --modal-green-border: #A7F3D0;
                --modal-orange-text: #92400E;
                --modal-orange-border: #FDE68A;
                --modal-stat-color: #8B5CF6;
                --modal-divider: #E5E7EB;
            }

            .dark-theme {
                --modal-bg: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                --modal-border: #374151;
                --modal-card-bg: #1f2937;
                --modal-text-primary: #f3f4f6;
                --modal-text-secondary: #d1d5db;
                --modal-text-muted: #9ca3af;
                --modal-purple-text: #c4b5fd;
                --modal-purple-border: #4c1d95;
                --modal-blue-text: #93c5fd;
                --modal-blue-border: #1e40af;
                --modal-green-text: #6ee7b7;
                --modal-green-border: #065f46;
                --modal-orange-text: #fcd34d;
                --modal-orange-border: #78350f;
                --modal-stat-color: #a78bfa;
                --modal-divider: #374151;
            }

            #tech-wrapper {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                transition: all 0.3s ease;
            }

            .tech-header {
                display: flex;
                align-items: center;
                gap: 16px;
                margin-bottom: 24px;
            }

            .tech-header h3 {
                margin: 0;
                color: var(--modal-text-primary);
                font-size: 24px;
                font-weight: 700;
            }

            .tech-content {
                padding: 26px;
                padding-bottom: 36px;
                background: var(--modal-bg);
                border-radius: 16px;
                border: 2px solid var(--modal-border);
            }

            .tech-cards {
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
            }

            .tech-card {
                flex: 1;
                background: var(--modal-card-bg);
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }

            .tech-card.search {
                border: 2px solid var(--modal-purple-border);
            }

            .tech-card.quality {
                border: 2px solid var(--modal-green-border);
            }

            .tech-card.diversity {
                border: 2px solid var(--modal-orange-border);
            }

            .tech-card.data {
                border: 2px solid var(--modal-blue-border);
            }

            .tech-card-header {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 12px;
            }

            .tech-card-header span {
                font-size: 22px;
            }

            .tech-card-header h4 {
                margin: 0;
                font-size: 16px;
                font-weight: 700;
            }

            .tech-card.search h4 { color: #7C3AED; }
            .tech-card.quality h4 { color: #059669; }
            .tech-card.diversity h4 { color: #D97706; }
            .tech-card.data h4 { color: #2563EB; }

            .dark-theme .tech-card.quality h4 { color: #6ee7b7; }
            .dark-theme .tech-card.diversity h4 { color: #fbbf24; }

            .tech-card ul {
                margin: 0;
                padding-left: 18px;
                color: var(--modal-text-secondary);
                line-height: 1.7;
                font-size: 13px;
            }

            .tech-card.search strong { color: var(--modal-purple-text); }
            .tech-card.quality strong { color: var(--modal-green-text); }
            .tech-card.diversity strong { color: var(--modal-orange-text); }
            .tech-card.data strong { color: var(--modal-blue-text); }

            .pipeline-flow {
                background: var(--modal-card-bg);
                border: 2px solid var(--modal-border);
                border-radius: 12px;
                padding: 16px 24px;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
                flex-wrap: wrap;
            }

            .pipeline-stage {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 14px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 600;
            }

            .pipeline-stage.rules {
                background: #FEF3C7;
                color: #92400E;
                border: 1px solid #FDE68A;
            }

            .pipeline-stage.router {
                background: #D1FAE5;
                color: #065F46;
                border: 1px solid #A7F3D0;
            }

            .pipeline-stage.confidence {
                background: #EDE9FE;
                color: #5B21B6;
                border: 1px solid #DDD6FE;
            }

            .dark-theme .pipeline-stage.rules {
                background: #78350f;
                color: #fef3c7;
                border-color: #92400e;
            }

            .dark-theme .pipeline-stage.router {
                background: #064e3b;
                color: #d1fae5;
                border-color: #065f46;
            }

            .dark-theme .pipeline-stage.confidence {
                background: #4c1d95;
                color: #ede9fe;
                border-color: #5b21b6;
            }

            .pipeline-arrow {
                color: var(--modal-text-muted);
                font-size: 18px;
            }

            .stats-bar {
                background: var(--modal-card-bg);
                padding: 16px 24px;
                border-radius: 12px;
                border: 2px solid var(--modal-border);
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                display: flex;
                justify-content: space-around;
                align-items: center;
            }

            .stat {
                text-align: center;
            }

            .stat-value {
                font-size: 24px;
                font-weight: 700;
                color: var(--modal-stat-color);
                margin-bottom: 2px;
            }

            .stat-label {
                font-size: 12px;
                color: var(--modal-text-muted);
                font-weight: 500;
            }

            .stat-divider {
                width: 1px;
                height: 36px;
                background: var(--modal-divider);
            }
        </style>

        <div id="tech-wrapper">
            <div class="tech-header">
                <h3>Technical Details</h3>
            </div>
            <div class="tech-content">
                <!-- 3-Stage Pipeline Visualization -->
                <div class="pipeline-flow">
                    <div class="pipeline-stage rules">⚡ Rules Filter</div>
                    <span class="pipeline-arrow">→</span>
                    <div class="pipeline-stage router">🎯 Semantic Router</div>
                    <span class="pipeline-arrow">→</span>
                    <div class="pipeline-stage confidence">📊 Confidence Gate</div>
                </div>

                <!-- Row 1: Search + Quality -->
                <div class="tech-cards">
                    <div class="tech-card search">
                        <div class="tech-card-header">
                            <span>🔍</span>
                            <h4>Semantic Search</h4>
                        </div>
                        <ul>
                            <li><strong>OpenAI text-embedding-3-small</strong></li>
                            <li><strong>Pinecone</strong> vector database</li>
                            <li>Pure semantic similarity (no keyword matching)</li>
                        </ul>
                    </div>

                    <div class="tech-card quality">
                        <div class="tech-card-header">
                            <span>🛡️</span>
                            <h4>3-Stage Quality Pipeline</h4>
                        </div>
                        <ul>
                            <li><strong>Stage 1:</strong> Fast rules-based nonsense detection</li>
                            <li><strong>Stage 2:</strong> Semantic router intent classification</li>
                            <li><strong>Stage 3:</strong> Confidence scoring & gating</li>
                        </ul>
                    </div>
                </div>

                <!-- Row 2: Diversity + Data -->
                <div class="tech-cards">
                    <div class="tech-card diversity">
                        <div class="tech-card-header">
                            <span>🎲</span>
                            <h4>Client Diversity</h4>
                        </div>
                        <ul>
                            <li><strong>Max 1 story per client</strong> in results</li>
                            <li>Prevents repetitive single-client results</li>
                            <li>Smart overflow for quality maintenance</li>
                        </ul>
                    </div>

                    <div class="tech-card data">
                        <div class="tech-card-header">
                            <span>📚</span>
                            <h4>Story Architecture</h4>
                        </div>
                        <ul>
                            <li><strong>STAR format</strong> + 5P framework</li>
                            <li>Category/Sub-category/Theme taxonomy</li>
                            <li><strong>Behavioral interview</strong> specialization</li>
                        </ul>
                    </div>
                </div>

                <!-- Stats Bar -->
                <div class="stats-bar">
                    <div class="stat">
                        <div class="stat-value">130+</div>
                        <div class="stat-label">Stories</div>
                    </div>
                    <div class="stat-divider"></div>
                    <div class="stat">
                        <div class="stat-value">20+</div>
                        <div class="stat-label">Years</div>
                    </div>
                    <div class="stat-divider"></div>
                    <div class="stat">
                        <div class="stat-value">6</div>
                        <div class="stat-label">Industries</div>
                    </div>
                    <div class="stat-divider"></div>
                    <div class="stat">
                        <div class="stat-value">3</div>
                        <div class="stat-label">Quality Stages</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        (function() {
            function detectTheme() {
                try {
                    var parentBody = window.parent.document.body;
                    var isDark = parentBody.classList.contains('dark-theme') ||
                                 parentBody.getAttribute('data-theme') === 'dark';
                    return isDark;
                } catch(e) {
                    return window.matchMedia('(prefers-color-scheme: dark)').matches;
                }
            }

            function applyTheme() {
                var container = document.getElementById('tech-wrapper');
                if (detectTheme()) {
                    container.classList.add('dark-theme');
                } else {
                    container.classList.remove('dark-theme');
                }
            }

            applyTheme();
            setInterval(applyTheme, 1000);
        })();
    </script>
    """
