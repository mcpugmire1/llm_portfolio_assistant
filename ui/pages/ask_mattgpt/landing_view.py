"""
Ask MattGPT Landing View

Landing page UI for Ask MattGPT with:
- Purple hero header with Agy introduction
- Status bar showing system readiness
- Suggestion chips for quick starts
- Main input form
- Integration with backend service
"""

import streamlit as st
from typing import List, Dict

from ui.pages.ask_mattgpt.backend_service import send_to_backend
from ui.pages.ask_mattgpt.styles import get_landing_css, get_loading_animation_css


def render_landing_page(stories: List[Dict]):
    """
    Render the Ask MattGPT landing page (empty state) matching the wireframe.
    NAVBAR IS RENDERED BY PARENT - NO NAVBAR CSS HERE
    """

    # Initialize processing flag
    if "processing_suggestion" not in st.session_state:
        st.session_state["processing_suggestion"] = False

    # === INJECT CSS ===
    st.markdown(get_landing_css(), unsafe_allow_html=True)

    # === CSS now loaded from styles.py ===

    # === PURPLE HEADER ===
    st.markdown(
        """
    <div class="ask-header">
        <div class="header-content" style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 24px;">
                <img class="header-agy-avatar"
                    src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_avatar.png"
                    alt="Agy"/>
                <div class="header-text">
                    <h1>Ask MattGPT</h1>
                    <p>Meet Agy 🐾 — Tracking down insights from 20+ years of transformation experience</p>
                </div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # === STATUS BAR ===
    st.markdown(
        """
    <div class="status-bar">
        <div class="status-item">
            <span class="status-dot"></span>
            <span>Semantic search <span class="status-value">active</span></span>
        </div>
        <div class="status-item">
            <span>Pinecone index <span class="status-value">ready</span></span>
        </div>
        <div class="status-item">
            <span>120+ stories <span class="status-value">indexed</span></span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # === MAIN INTRO SECTION ===
    st.markdown(
        """
    <div class="main-intro-section">
        <div class="main-avatar">
            <img src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_avatar.png" alt="Agy"/>
        </div>
        <h2 class="welcome-title">Hi, I'm Agy 🐾</h2>
        <p class="intro-text-primary">
            I'm a Plott Hound — a breed known for tracking skills and determination.
            Perfect traits for helping you hunt down insights from Matt's 120+ transformation projects.
        </p>
        <p class="intro-text-secondary">
            Ask me about specific methodologies, leadership approaches, or project outcomes.
            I understand context, not just keywords.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Placeholder for loading message - positioned before "TRY ASKING" section
    loading_placeholder = st.empty()

    # Show loading immediately if processing
    if st.session_state.get("processing_suggestion"):
        with loading_placeholder:
            st.markdown(
                """
<style>
/* Disable text input during processing */
div[data-testid="stTextInput"] input {
    opacity: 0.5 !important;
    pointer-events: none !important;
    cursor: not-allowed !important;
    background: #F3F4F6 !important;
}
@keyframes chaseAnimationEarly {
    0% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_1.png'); }
    33.33% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_2.png'); }
    66.66% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_3.png'); }
    100% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_1.png'); }
}
.thinking-ball-early {
    width: 48px;
    height: 48px;
    animation: chaseAnimationEarly 0.9s steps(3) infinite;
}
</style>
<div style='background: transparent;
            padding: 16px 0;
            margin: 20px 0;
            display: flex;
            align-items: center;
            gap: 12px;'>
    <img class="thinking-ball-early" src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_1.png" alt="Thinking"/>
    <div style='color: #2C363D; font-weight: 500;'>🐾 Tracking down insights...</div>
</div>
""",
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="suggested-title">TRY ASKING:</div>', unsafe_allow_html=True
    )

    # === SUGGESTED QUESTION BUTTONS ===
    qs = [
        ("🚀", "How did Matt transform global payments at scale?"),
        ("🏥", "Show me Matt's GenAI work in healthcare"),
        ("💡", "Track down Matt's innovation leadership stories"),
        ("👥", "How did Matt scale agile across 150+ people?"),
        ("⚡", "Find Matt's platform engineering projects"),
        ("🎯", "Show me how Matt handles stakeholders"),
    ]

    c1, c2 = st.columns(2, gap="small")

    # Disable all buttons when any is processing
    disabled = st.session_state.get("processing_suggestion", False)

    for i, (icon, q) in enumerate(qs):
        with c1 if i % 2 == 0 else c2:
            if st.button(
                f"{icon}  {q}",
                key=f"suggested_{i}",
                type="secondary",
                use_container_width=True,
                disabled=disabled,
            ):
                # Set state and trigger rerun to show loading state
                # NOTE: Don't set "landing_input" - it's controlled by the widget
                st.session_state["ask_transcript"] = []
                st.session_state["processing_suggestion"] = True
                st.session_state["pending_query"] = q
                st.session_state["ask_input_value"] = q
                st.rerun()

    # === INPUT AREA ===
    st.markdown('<div class="landing-input-container">', unsafe_allow_html=True)

    # Use columns to keep input and button on same line
    col_input, col_button = st.columns([6, 1])

    # Check if user pressed Enter in the text input (on_change triggers)
    if st.session_state.get("landing_input_submitted"):
        user_input_value = st.session_state.get("landing_input", "")
        if user_input_value and not st.session_state.get("processing_suggestion"):
            # Set state and trigger rerun to show loading state
            st.session_state["ask_transcript"] = []
            st.session_state["processing_suggestion"] = True
            st.session_state["pending_query"] = user_input_value
            st.session_state["ask_input_value"] = user_input_value
            st.session_state["landing_input_submitted"] = False
            st.rerun()
        st.session_state["landing_input_submitted"] = False

    with col_input:
        user_input = st.text_input(
            "Ask me anything — from building MattGPT to leading global programs...",
            key="landing_input",
            label_visibility="collapsed",
            placeholder="Ask me anything — from building MattGPT to leading global programs...",
            on_change=lambda: st.session_state.update(
                {"landing_input_submitted": True}
            ),
        )

    with col_button:
        # Disable button if input is empty OR if we're currently processing
        button_disabled = not user_input or disabled
        if st.button(
            "Ask Agy 🐾", key="landing_ask", type="primary", disabled=button_disabled
        ):
            if user_input:
                # Set state and trigger rerun to show loading state
                # NOTE: Don't set "landing_input" - it's controlled by the widget
                st.session_state["ask_transcript"] = []
                st.session_state["processing_suggestion"] = True
                st.session_state["pending_query"] = user_input
                st.session_state["ask_input_value"] = user_input
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="powered-by-text">Powered by OpenAI GPT-4o-mini with semantic search across 120+ project case studies</p>',
        unsafe_allow_html=True,
    )

    # === PROCESS PENDING QUERY (if in processing state) ===
    # This runs AFTER the UI is rendered, so user sees disabled buttons and styled message
    if st.session_state.get("processing_suggestion") and st.session_state.get(
        "pending_query"
    ):
        query = st.session_state.get("pending_query")

        # Show the styled loading message in the placeholder
        with loading_placeholder:
            st.markdown(
                """
<style>
@keyframes chaseAnimation {
    0% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_1.png'); }
    33.33% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_2.png'); }
    66.66% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_3.png'); }
    100% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_1.png'); }
}
.thinking-ball {
    width: 48px;
    height: 48px;
    animation: chaseAnimation 0.9s steps(3) infinite;
}
</style>
<div style='background: transparent;
            padding: 16px 0;
            margin: 20px 0;
            display: flex;
            align-items: center;
            gap: 12px;'>
    <img class="thinking-ball" src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_1.png" alt="Thinking"/>
    <div style='color: #2C363D; font-weight: 500;'>🐾 Tracking down insights...</div>
</div>
""",
                unsafe_allow_html=True,
            )

        # Process the query
        result = send_to_backend(query, {}, None, stories)

        # Add to transcript
        st.session_state["ask_transcript"].append({"Role": "user", "text": query})

        # Check if nonsense was detected
        if st.session_state.get("ask_last_reason"):
            # Nonsense detected - add banner entry to transcript
            reason = st.session_state.get("ask_last_reason", "")
            query_text = st.session_state.get("ask_last_query", "")
            overlap = st.session_state.get("ask_last_overlap", None)

            st.session_state["ask_transcript"].append({
                "type": "banner",
                "Role": "assistant",
                "reason": reason,
                "query": query_text,
                "overlap": overlap,
            })

            # Clear flags after adding to transcript
            st.session_state.pop("ask_last_reason", None)
            st.session_state.pop("ask_last_query", None)
            st.session_state.pop("ask_last_overlap", None)
        else:
            # Normal answer - add conversational answer (wireframe style)
            sources = result.get("sources", [])
            answer_text = result.get("answer_md") or result.get("answer", "")

            st.session_state["ask_transcript"].append(
                {
                    "type": "conversational",
                    "Role": "assistant",
                    "text": answer_text,
                    "sources": sources,
                }
            )

        # Clear processing state
        st.session_state["processing_suggestion"] = False
        st.session_state["pending_query"] = None
        loading_placeholder.empty()

        # Rerun to show conversation view
        st.rerun()

    # === ADD FOOTER ===
    from ui.components.footer import render_footer

    render_footer()
