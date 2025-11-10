"""
Ask MattGPT Page

Interactive chat interface for conversational exploration of Matt's experience.
Uses semantic search and Pinecone to retrieve relevant project stories.
"""

import streamlit as st
import streamlit.components.v1 as components  # ADD THIS LINE
from typing import List, Dict, Optional
import json
from datetime import datetime
import os, re, time, textwrap, json
from config.debug import DEBUG
from config.settings import get_conf
from utils.ui_helpers import dbg, safe_container
from utils.validation import is_nonsense, token_overlap_ratio, _tokenize
from utils.ui_helpers import render_no_match_banner
from utils.formatting import (
    story_has_metric,
    strongest_metric_line,
    build_5p_summary,
    _format_key_points,
    METRIC_RX,
)
from services.pinecone_service import (
    _init_pinecone,
    PINECONE_MIN_SIM,
    SEARCH_TOP_K,
    _safe_json,
    _summarize_index_stats,
    PINECONE_NAMESPACE,
    PINECONE_INDEX_NAME,
    W_PC,
    W_KW,
    _DEF_DIM,
    _PINECONE_INDEX,
    VECTOR_BACKEND,
)
from services.rag_service import semantic_search, _KNOWN_VOCAB
from utils.formatting import _format_narrative, _format_key_points, _format_deep_dive
from utils.ui_helpers import render_sources_chips, render_sources_badges_static
from ui.components.story_detail import render_story_detail

# --- Nonsense rules (JSONL) + known vocab -------------------
import csv
from datetime import datetime
import os, re, time, textwrap, json

# ====================
# 1. MAIN ENTRY POINT
# ====================


def render_ask_mattgpt(stories: list):
    """Main entry point for Ask MattGPT page."""
    # NOTE: Don't call _ensure_ask_bootstrap() here - it clears ask_input_value
    # which breaks the pending_query flow

    if DEBUG:
        from utils.ui_helpers import dbg
        transcript_len = len(st.session_state.get("ask_transcript", []))
        has_inject = st.session_state.get("__inject_user_turn__")
        has_processing = st.session_state.get("__processing_chip_injection__")
        dbg(f"[ENTRY] transcript_len={transcript_len}, inject={has_inject}, processing={has_processing}")

    # Clear transition indicator flag only (feature temporarily disabled due to positioning issues)
    # Don't clear processing flags here as they're needed for the normal flow
    if st.session_state.get("show_transition_indicator"):
        del st.session_state["show_transition_indicator"]

    # Force conversation view if coming from story suggestion
    show_conversation = bool(st.session_state.get("ask_transcript"))
    if st.session_state.get("__ask_from_suggestion__"):
        show_conversation = True
        st.session_state["show_ask_panel"] = True
        # Clear the flag after using it
        if "__ask_from_suggestion__" in st.session_state:
            del st.session_state["__ask_from_suggestion__"]

    if not show_conversation:
        if DEBUG:
            dbg("[ENTRY] → LANDING PAGE")
        render_landing_page(stories)
    else:
        if DEBUG:
            dbg("[ENTRY] → CONVERSATION VIEW")
        render_conversation_view(stories)


# ====================
# 2. LANDING PAGE (EMPTY STATE)
# ====================


def render_landing_page(stories: list):
    """
    Render the Ask MattGPT landing page (empty state) matching the wireframe.
    NAVBAR IS RENDERED BY PARENT - NO NAVBAR CSS HERE
    """

    # Initialize processing flag
    if "processing_suggestion" not in st.session_state:
        st.session_state["processing_suggestion"] = False

    # === PAGE-SPECIFIC CSS ONLY ===
    # Note: Navbar positioning is handled by global_styles.py
    st.markdown(
        """
        <style>
        /* Purple header - pull up to eliminate white space */
        .ask-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            margin-top: -35px !important; /* Set to 0 so it aligns perfectly with the 72px padding-top above */
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header-content {
            display: flex;
            align-items: center;
            gap: 24px;
        }

        .header-agy-avatar {
            width: 64px !important;
            height: 64px !important;
            border-radius: 50% !important;
            border: 3px solid white !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        }

        /* Dark mode halo effect for header avatar */
        [data-theme="dark"] .header-agy-avatar {
            filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
        }

        .header-text h1 {
            font-size: 32px;
            margin: 0 0 8px 0;
            color: white;
        }

        .header-text p {
            font-size: 16px;
            margin: 0;
            opacity: 0.95;
        }

        .how-it-works-btn {
            padding: 12px 24px;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            color: white;
            font-weight: 600;
            font-size: 15px;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
            flex-shrink: 0;
        }

        .how-it-works-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            border-color: rgba(255, 255, 255, 0.5);
            transform: translateY(-2px);
        }

        /* Status bar - constrained to content width */
        .status-bar {
            display: flex !important;
            flex-wrap: nowrap !important;
            gap: 24px !important;
            justify-content: center !important;
            padding: 12px 30px !important;
            background: #f8f9fa !important;
            border-bottom: 1px solid #e0e0e0 !important;
            margin: 0 !important;
            overflow-x: auto !important;
        }

        .status-item {
            display: flex !important;
            align-items: center !important;
            gap: 6px !important;
            font-size: 13px !important;
            color: #6B7280 !important;
            white-space: nowrap !important;
            flex-shrink: 0 !important;
        }

        .status-item span {
            white-space: nowrap !important;
        }

        .status-value {
            font-weight: 600;
            color: #2C363D;
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

        /* MAIN INTRO SECTION */
        .main-intro-section {
            background: white;
            border-radius: 24px 24px 0 0;
            max-width: 900px;
            width: 100%;
            margin: 20px auto 0;
            padding: 48px 32px 32px;
            text-align: center;
        }

        .main-avatar {
            text-align: center;
        }

        .main-avatar img {
            width: 96px;
            height: 96px;
            border-radius: 50%;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        /* Dark mode halo effect for main hero avatar */
        [data-theme="dark"] .main-avatar img {
            filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
        }

        .welcome-title {
            font-size: 28px;
            color: #2c3e50;
            margin: 24px 0 12px;
            text-align: center;
        }

        .intro-text-primary {
            font-size: 18px;
            color: #374151;
            line-height: 1.7;
            font-weight: 500;
            margin-bottom: 20px;
            max-width: 650px;
            margin-left: auto !important;
            margin-right: auto !important;
            text-align: center !important;
        }

        .intro-text-secondary {
            font-size: 17px;
            color: #6B7280;
            line-height: 1.6;
            max-width: 650px;
            margin: 0 auto 48px !important;
            text-align: center !important;
        }

        .suggested-title {
            font-size: 14px;
            font-weight: 600;
            color: #7f8c8d;
            text-transform: uppercase;
            margin-bottom: 20px;
            text-align: center;
        }

        /* BUTTON CONTAINER - Grid layout */
        div[data-testid="stHorizontalBlock"]:has(button[key^="suggested_"]) {
            display: grid !important;
            grid-template-columns: repeat(2, 1fr) !important;
            grid-template-rows: repeat(3, auto) !important;
            gap: 16px !important;
            max-width: 900px !important;
            width: 100% !important;
            margin: 0 auto !important;
            background: white !important;
            padding: 0 32px 48px !important;
            border-radius: 0 0 24px 24px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
        }

        div[data-testid="stHorizontalBlock"]:has(button[key^="suggested_"]) > div[data-testid="column"] {
            display: contents !important;
        }

        div[data-testid="stHorizontalBlock"]:has(button[key^="suggested_"]) .stElementContainer {
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Suggested question buttons */
        button[key^="suggested_"] {
            background: white !important;
            border: 2px solid #E5E7EB !important;
            border-radius: 12px !important;
            padding: 20px 24px !important;
            text-align: left !important;
            transition: all 0.2s ease !important;
            min-height: 80px !important;
            max-height: 80px !important;
            height: 80px !important;
            display: flex !important;
            align-items: start !important;
            gap: 12px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
            width: 100% !important;
            overflow: hidden !important;
        }

        button[key^="suggested_"]:hover {
            border-color: #8B5CF6 !important;
            background: #F9FAFB !important;
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.12) !important;
            transform: translateY(-2px) !important;
        }

        button[key^="suggested_"] p {
            font-size: 16px !important;
            font-weight: 600 !important;
            color: #2C363D !important;
            line-height: 1.4 !important;
            margin: 0 !important;
            text-align: left !important;
            overflow: hidden !important;
            display: -webkit-box !important;
            -webkit-line-clamp: 2 !important;
            -webkit-box-orient: vertical !important;
        }

        button[key^="suggested_"] div {
            max-height: 80px !important;
        }


        /* Landing input container */
        .landing-input-container {
            max-width: 800px !important;
            width: 100% !important;
            margin: 40px auto 0px !important;
            padding: 0 30px !important;
        }

        /* Powered by text */
        .powered-by-text {
            text-align: center !important;
            font-size: 12px !important;
            color: #95a5a6 !important;
            margin-top: -25px !important;
            margin-bottom: 0 !important;
            padding: 0 !important;
        }

        /* Nicer input styling from wireframe */
        /* Target Streamlit's actual rendered input using data-testid */
        /* Fix clipped corners by setting overflow visible on parent containers */
        div[data-testid="stTextInput"],
        div[data-testid="stTextInput"] > div {
            overflow: visible !important;
        }

        div[data-testid="stTextInput"] input {
            width: 100% !important;
            padding: 20px 24px !important;
            font-size: 17px !important;
            border: 2px solid #E5E7EB !important;
            border-radius: 16px !important;
            transition: all 0.2s ease !important;
            background: #FAFAFA !important;
            font-family: inherit !important;
            overflow: visible !important;
        }

        div[data-testid="stTextInput"] input:focus {
            outline: none !important;
            border-color: #8B5CF6 !important;
            background: white !important;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
        }

        div[data-testid="stTextInput"] input::placeholder {
            color: #9CA3AF !important;
        }

        /* ASK AGY BUTTON - Purple background with WHITE text */
        button[key="landing_ask"] {
            background: #8B5CF6 !important;
            background-color: #8B5CF6 !important;
            border: none !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 12px 32px !important;
            border-radius: 12px !important;
            font-size: 16px !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
            height: auto !important;
            min-height: 48px !important;
        }

        button[key="landing_ask"]:hover:not(:disabled) {
            background: #7C3AED !important;
            color: white !important;
            transform: scale(1.02) !important;
        }

        button[key="landing_ask"]:disabled {
            background: #8B5CF6 !important;
            background-color: #8B5CF6 !important;
            border: none !important;
            opacity: 1 !important;
            cursor: not-allowed !important;
            color: white !important;
            filter: brightness(0.85) !important;
        }

        button[key="landing_ask"]:disabled p {
            color: white !important;
            opacity: 1 !important;
        }

        /* Override Streamlit's default disabled button styles */
        button[kind="primary"]:disabled {
            background: #8B5CF6 !important;
            background-color: #8B5CF6 !important;
            border: none !important;
            color: white !important;
        }

        button[key="landing_ask"] p {
            color: white !important;
            font-weight: 600 !important;
            margin: 0 !important;
        }

        /* Force white text on all child elements */
        button[key="landing_ask"] * {
            color: white !important;
        }

        button[key="landing_ask"]:disabled * {
            color: white !important;
        }

        /* Target the div wrapper around button text */
        button[key="landing_ask"] div {
            color: white !important;
        }

        /* Bounce animation for loading paw icon */
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-4px); }
        }

        /* Fade in up animation for welcome text */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Apply animation to welcome elements */
        .welcome-title {
            animation: fadeInUp 0.6s ease-out;
        }

        .intro-text-primary {
            animation: fadeInUp 0.6s ease-out 0.2s;
            animation-fill-mode: both;
        }

        .intro-text-secondary {
            animation: fadeInUp 0.6s ease-out 0.4s;
            animation-fill-mode: both;
        }

        /* Hide trigger button */
        button[key="how_works_landing"] {
            display: none !important;
        }

        div:has(> button[key="how_works_landing"]) {
            display: none !important;
        }
                
        /* HOW AGY SEARCHES BUTTON - IN HEADER */
        button[key="toggle_how_agy"] {
            position: absolute !important;
            top: 170px !important;
            right: 40px !important;
            background: rgba(255, 255, 255, 0.2) !important;
            backdrop-filter: blur(10px) !important;
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 12px !important;
            color: white !important;
            padding: 12px 24px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            z-index: 10 !important;
        }
        
        button[key="toggle_how_agy"]:hover {
            background: rgba(255, 255, 255, 0.3) !important;
            border-color: rgba(255, 255, 255, 0.5) !important;
        }
        
        button[key="toggle_how_agy"] p {
            color: white !important;
            font-weight: 600 !important;
        }

        </style>
    """,
        unsafe_allow_html=True,
    )

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


# ====================
# 3. CONVERSATION VIEW
# ====================


def render_conversation_view(stories: list):
    """
    Render active conversation view.
    NAVBAR IS RENDERED BY PARENT - NO NAVBAR CSS HERE
    """

    # === PAGE-SPECIFIC CSS ONLY (NO NAVBAR) ===
    # Navbar positioning is now handled by universal CSS in global_styles.py
    st.markdown(
        """
        <style>
        /* Status bar - constrained to content width */
        .status-bar {
            display: flex !important;
            flex-wrap: nowrap !important;
            gap: 24px !important;
            justify-content: center !important;
            padding: 12px 30px !important;
            background: #f8f9fa !important;
            border-bottom: 1px solid #e0e0e0 !important;
            margin: 0 !important;
            overflow-x: auto !important;
        }

        .status-item {
            display: flex !important;
            align-items: center !important;
            gap: 6px !important;
            font-size: 13px !important;
            color: #6B7280 !important;
            white-space: nowrap !important;
            flex-shrink: 0 !important;
        }

        .status-value {
            font-weight: 600;
            color: #2C363D;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: #10B981;
            border-radius: 50%;
            display: inline-block;
            flex-shrink: 0;
        }

        /* Chat interface header */
        .conversation-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            margin-top: -50px !important;  /* Navbar positioning handled by global_styles.py */
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        }

        .conversation-header-content {
            display: flex;
            align-items: center;
            gap: 24px;
        }

        .conversation-agy-avatar {
                width: 64px !important;
                height: 64px !important;
                border-radius: 50% !important;
                border: 3px solid white !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        }

        /* Dark mode halo effect for conversation avatar */
        [data-theme="dark"] .conversation-agy-avatar {
            filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
        }

        .conversation-header-text h1 {
            font-size: 32px;
            margin: 0 0 8px 0;
            color: white;
        }

        .conversation-header-text p {
            font-size: 16px;
            margin: 0;
            opacity: 0.95;
        }

        /* How Agy searches button - glass morphism */
        .conversation-how-btn {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 20px;
            color: white;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }

        .conversation-how-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            border-color: rgba(255, 255, 255, 0.5);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        /* Status bar for conversation view */
        .status-bar-conversation {
            background: #f8f9fa;
            padding: 12px 30px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            gap: 24px;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            margin-bottom: 20px;
        }

        .status-dot-conversation {
            width: 8px;
            height: 8px;
            background: #27ae60;
            border-radius: 50%;
            display: inline-block;
            margin-right: 6px;
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }

        .status-label {
            color: #7f8c8d;
        }

        .status-value {
            color: #2c3e50;
            font-weight: 600;
        }

        /* Thinking indicator */
        .thinking-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background: #f0f0f0;
            border-radius: 6px;
            font-size: 13px;
            color: #7f8c8d;
            margin-bottom: 12px;
            animation: fadeOutSmooth 0.5s ease-out 2s forwards;
        }

        @keyframes fadeOutSmooth {
            to {
                opacity: 0;
                transform: translateY(-8px);
            }
        }

        .thinking-icon {
            width: 48px;
            height: 48px;
        }

        /* Chat messages styling */
        .chat-message-ai {
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            border-left: 4px solid #8B5CF6;
        }

        .chat-message-user {
            background: #e3f2fd;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        /* Message text styling */
        .message-text {
            font-size: 15px;
            color: #2c3e50;
            line-height: 1.6;
        }

        .message-text strong {
            font-weight: bold;
        }

        /* Override Streamlit chat message styling - AI messages */
        /* Multiple selectors to ensure styling is applied */
        [data-testid="stChatMessage"]:has(img[alt*="Agy"]),
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]),
        [data-testid="stChatMessage"][data-testid-assistant],
        div[data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])) {
            background: white !important;
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
            border-left: 4px solid #8B5CF6 !important;
            margin-bottom: 24px !important;
            border-top: none !important;
            border-right: none !important;
            border-bottom: none !important;
        }

        /* User messages */
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]),
        [data-testid="stChatMessage"][data-testid-user] {
            background: #e3f2fd !important;
            border-radius: 8px !important;
            padding: 16px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
            margin-bottom: 24px !important;
            border: none !important;
        }

        /* Avatar styling - resize using rem units as per Streamlit's design */
        .stChatMessage [data-testid="stImage"] img,
        [data-testid="stChatMessage"] [data-testid="stImage"] img {
            width: 4.5rem !important;  /* Default is 2rem, increased to 4.5rem (~72px) */
            height: 4.5rem !important;
            border-radius: 50% !important;
            border: 2px solid #e0e0e0 !important;
            background: white !important;
            padding: 4px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        }

        /* Alternative selector for avatar container */
        [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
            background: white !important;
            border: 2px solid #e0e0e0 !important;
            padding: 4px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        }

        /* Dark mode halo effect for chat message avatars */
        [data-theme="dark"] [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] img {
            filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
        }

        [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] {
            width: 40px !important;
            height: 40px !important;
            background: #7f8c8d !important;
            opacity: 0.5 !important;
        }

        /* Input Area - Complete Wireframe Match */
        [data-testid="stChatInput"] {
            padding: 20px 30px !important;
            background: white !important;
            border-top: 2px solid #e0e0e0 !important;
            position: sticky !important;
            bottom: 0 !important;
            z-index: 100 !important;
        }

        /* Input Container - Exact Wireframe Structure */
        [data-testid="stChatInput"] > div:first-child {
            display: flex !important;
            gap: 12px !important;
            max-width: 900px !important;
            margin: 0 auto !important;
            align-items: center !important;
        }

        /* Input Field - Maximum Specificity for Textarea */
        textarea[data-testid="stChatInputTextArea"],
        [data-testid="stChatInput"] textarea[class*="st-"],
        [data-testid="stChatInput"] textarea {
            flex: 1 !important;
            padding: 14px 18px !important;
            border: 2px solid #ddd !important;
            border-radius: 8px !important;
            font-size: 15px !important;
            font-family: inherit !important;
            background: white !important;
            transition: all 0.2s ease !important;
            resize: none !important;
            min-height: 48px !important;
            max-height: 48px !important;
        }

        /* Textarea Focus - Maximum Specificity */
        textarea[data-testid="stChatInputTextArea"]:focus,
        [data-testid="stChatInput"] textarea:focus {
            outline: none !important;
            border-color: #8B5CF6 !important;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
            border-radius: 8px !important;
        }

        /* Keep your placeholder rule */
        [data-testid="stChatInputTextArea"]::placeholder,
        [data-testid="stChatInput"] textarea::placeholder,
        [data-testid="stChatInput"] input::placeholder {
            color: #9ca3af !important;
            opacity: 1 !important;
        }

        /* Nuclear targeting of the exact emotion class */
        textarea.st-emotion-cache-1vdwi3c[data-testid="stChatInputTextArea"] {
            border-radius: 8px !important;
            border: 2px solid #ddd !important;
            padding: 14px 18px !important;
            min-height: 48px !important;
            max-height: 48px !important;
        }

        /* Also target any future emotion classes */
        textarea[data-testid="stChatInputTextArea"][class*="st-emotion-cache"] {
            border-radius: 8px !important;
            border: 2px solid #ddd !important;
            padding: 14px 18px !important;
        }

        /* Remove native browser styling that overrides our border-radius */
        textarea[data-testid="stChatInputTextArea"] {
            appearance: none !important;
            -webkit-appearance: none !important;
            -moz-appearance: none !important;
            border-radius: 8px !important;
            border: 2px solid #ddd !important;
            padding: 14px 18px !important;
        }

        /* Button - Maximum Specificity Override */
        button[data-testid="stChatInputSubmitButton"].st-emotion-cache-1vabq37,
        button[data-testid="stChatInputSubmitButton"],
        [data-testid="stChatInput"] button[class*="st-emotion-cache"],
        [data-testid="stChatInput"] button {
            padding: 14px 28px !important;
            background: #8B5CF6 !important;
            background-color: #8B5CF6 !important;
            background-image: none !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            min-width: auto !important;
            width: auto !important;
            height: auto !important;
            min-height: auto !important;
        }

        /* Force rectangular shape */
        button[data-testid="stChatInputSubmitButton"] {
            border-radius: 8px !important;
            padding: 14px 28px !important;
        }

        /* Hide SVG with maximum specificity */
        button[data-testid="stChatInputSubmitButton"] svg,
        button[data-testid="stChatInputSubmitButton"] > svg,
        [data-testid="stChatInput"] button svg {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            width: 0 !important;
            height: 0 !important;
        }

        /* Add text content */
        button[data-testid="stChatInputSubmitButton"]::after {
            content: "Ask Agy 🐾" !important;
            color: white !important;
            font-size: 15px !important;
            font-weight: 600 !important;
        }

        /* Hover state with maximum specificity */
        button[data-testid="stChatInputSubmitButton"]:hover,
        button[data-testid="stChatInputSubmitButton"].st-emotion-cache-1vabq37:hover {
            background: #7C3AED !important;
            background-color: #7C3AED !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3) !important;
        }


        /* Force the main chat input container to be rectangular */
        [data-testid="stChatInput"] {
            border-radius: 0 !important;
            overflow: hidden !important;
        }

        /* Force the immediate inner container to be rectangular */
        [data-testid="stChatInput"] > div:first-child {
            border-radius: 0 !important;
        }

        /* Target any emotion class wrappers around the textarea */
        [data-testid="stChatInput"] div[class*="st-emotion-cache"] {
            border-radius: 0 !important;
        }

        /* Target the specific emotion class we saw in DevTools */
        [data-testid="stChatInput"] .st-emotion-cache-1vdwi3c {
            border-radius: 0 !important;
        }
        /* Target the text input wrapper containers */
        div[data-testid="stTextInput"],
        div[data-testid="stTextInput"] > div,
        div[data-testid="stTextInput"] > div > div {
            border-radius: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
        }

        /* Target the chat input's nested structure */
        [data-testid="stChatInput"] > div:first-child > div:first-child {
            border-radius: 0 !important;
            background: transparent !important;
            padding: 0 !important;
        }

        /* Also target any emotion-cache wrappers around the textarea */
        [data-testid="stChatInput"] div[class*="st-emotion-cache"]:has(textarea) {
            border-radius: 0 !important;
            background: transparent !important;
        }


        /* Targets the inner-most container wrapper that applies the text-input styling */
        [data-testid="stChatInput"] .st-emotion-cache-1ydk24 {
            /* Use the actual emotion class for maximum certainty, if known. 
            If not, try the generic wrapper below: */
            border-left: none !important;
        }

        /* More generic, highly specific wrapper target */
        /* This targets the inner div that usually contains the actual <textarea> element */
        [data-testid="stChatInput"] > div:first-child > div:first-child > div:first-child {
            border-left: none !important;
            border-color: transparent !important; /* Safety measure */
        }

        /* This targets the immediate parent of the textarea where a padding/border might exist */
        textarea[data-testid="stChatInputTextArea"]::before {
            content: none !important;
            border: none !important;
        }

        /* Targets the Fieldset (a common wrapper for Streamlit text inputs) */
        [data-testid="stChatInput"] fieldset, 
        [data-testid="stChatInput"] legend {
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
            /* Ensure no residual color */
            border-left: none !important; 
        }
        
        /* Messages area background */
        .main .block-container {
            background: #fafafa !important;
            padding: 30px !important;
            padding-bottom: 140px !important;
            max-width: 900px !important;
            margin: 0 auto !important;
        }

        /* Smooth scroll behavior */
        html {
            scroll-behavior: smooth;
        }

        /* Add subtle animations to messages */
        [data-testid="stChatMessage"] {
            animation: fadeInUp 0.3s ease-out;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Source links section */
        .source-links-section {
            border-top: 1px solid #e0e0e0;
            margin-top: 16px;
            padding-top: 16px;
        }

        .source-links-title {
            font-size: 12px;
            text-transform: uppercase;
            color: #7f8c8d;
            margin-bottom: 12px;
            font-weight: 600;
        }

        /* Source links container - matches wireframe */
        .source-links {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: wrap !important;
            gap: 8px !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Remove Streamlit's default spacing inside source-links */
        .source-links > div[data-testid="column"],
        .source-links > div[data-testid="stVerticalBlock"],
        .source-links > div[data-testid="element-container"],
        .source-links > div {
            margin: 0 !important;
            padding: 0 !important;
            gap: 0 !important;
        }

        /* Target columns container that appears right after sources-tight */
        .sources-tight + div[data-testid="stHorizontalBlock"],
        .sources-tight + div[data-testid="column"] {
            gap: 8px !important;
            margin-top: 0 !important;
            padding: 0 !important;
        }

        /* Target individual columns within source buttons section */
        .sources-tight + div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            padding: 0 !important;
            margin: 0 !important;
            gap: 0 !important;
        }

        /* Source chips styling */
        .source-chip {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: #F3F4F6;
            border: 2px solid #E5E7EB;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            color: #2563EB;
            text-decoration: none;
            margin: 0;
            transition: all 0.2s ease;
        }

        .source-chip:hover {
            background: #EEF2FF;
            border-color: #8B5CF6;
            transform: translateY(-1px);
        }

        .source-chip-icon {
            color: #8B5CF6;
        }

        /* Action buttons */
        .action-buttons {
            display: flex;
            gap: 8px;
            margin-top: 16px;
        }

        .action-btn {
            padding: 6px 12px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            font-size: 12px;
            color: #555;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .action-btn:hover {
            background: #f5f5f5;
            border-color: #ccc;
        }

        .action-btn.helpful-active {
            background: #10B981 !important;
            color: white !important;
            border-color: #10B981 !important;
        }

        .action-btn.helpful-active::after {
            content: " ✓";
        }

        /* Answer card wrapper for AI responses */
        .answer-card {
            background: white;
            border-radius: 16px;
            padding: 0;
            margin-bottom: 24px;
        }

        /* Message spacing */
        .message-avatar-gap {
            gap: 12px;
        }

        .message-spacing {
            margin-bottom: 24px;
        }

        /* Source chips container styling - matches wireframe message-sources */
        .sources-tight,
        .message-sources {
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid rgb(224, 224, 224);
            background: transparent;
        }

        .section-tight,
        .sources-title {
            font-size: 12px;
            text-transform: uppercase;
            color: #7f8c8d;
            margin-bottom: 12px;
            font-weight: 600;
        }

        .sources-grid {
            display: grid;
            gap: 8px;
        }

        /* Source Links - Exact Wireframe Styling */
        /* Target the actual Streamlit buttons after sources-tight using both ~ and + */
        div[data-testid="stChatMessage"] .sources-tight ~ div button[data-testid="stBaseButton-secondary"],
        div[data-testid="stChatMessage"] .sources-tight + div button[data-testid="stBaseButton-secondary"],
        .source-button-wrapper button[data-testid="stBaseButton-secondary"] {
            background: #F3F4F6 !important;
            background-color: #F3F4F6 !important;
            background-image: none !important;
            border: 2px solid #E5E7EB !important;
            color: #2563EB !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            padding: 8px 16px !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 8px !important;
            margin: 0 !important;
            height: auto !important;
            min-height: auto !important;
            line-height: 1.4 !important;
            box-shadow: none !important;
            width: auto !important;
            text-decoration: none !important;
        }

        /* Text inside buttons */
        div[data-testid="stChatMessage"] .sources-tight ~ div button p,
        div[data-testid="stChatMessage"] .sources-tight + div button p,
        .source-button-wrapper button p {
            color: #2563EB !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1.4 !important;
        }

        /* Markdown container */
        div[data-testid="stChatMessage"] .sources-tight ~ div button div[data-testid="stMarkdownContainer"],
        div[data-testid="stChatMessage"] .sources-tight + div button div[data-testid="stMarkdownContainer"],
        .source-button-wrapper button div[data-testid="stMarkdownContainer"] {
            font-size: 14px !important;
        }

        /* Hover state */
        div[data-testid="stChatMessage"] .sources-tight ~ div button:hover,
        div[data-testid="stChatMessage"] .sources-tight + div button:hover,
        .source-button-wrapper button:hover {
            background: #EEF2FF !important;
            background-color: #EEF2FF !important;
            border-color: #8B5CF6 !important;
            transform: translateY(-1px) !important;
        }

        /* Hint Text - Force Position */
        .input-hint {
            text-align: center !important;
            font-size: 12px !important;
            color: #95a5a6 !important;
            margin-top: 10px !important;
            padding: 10px 0 20px 0 !important;
            position: relative !important;
            z-index: 101 !important;
            background: white !important;
        }

        /* Force hint text outside the sticky container */
        [data-testid="stChatInput"] + .input-hint {
            position: fixed !important;
            bottom: 10px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            z-index: 1000 !important;
        }
        

        /* Hide ONLY Streamlit's built-in status/spinner widgets - NOT our custom status bar */
        [data-testid="stStatusWidget"],
        [data-testid="stStatus"],
        [class*="stStatus"],
        .stSpinner,
        [data-testid="stSpinner"],
        [data-testid="stAlert"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0 !important;
            max-height: 0 !important;
            overflow: hidden !important;
        }

        /* Explicitly SHOW our custom status bars */
        .status-bar,
        .status-bar-container,
        div.status-bar,
        div.status-bar-container {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            height: auto !important;
            max-height: none !important;
        }

        /* Status bar green dot with pulse animation */
        .status-dot {
            width: 8px;
            height: 8px;
            background: #10B981;
            border-radius: 50%;
            display: inline-block;
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.5;
            }
        }

        /* Pill container for view mode buttons */
        .pill-container {
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }

        .pill-narrative, .pill-keypoints, .pill-deepdive {
            display: inline-block;
        }

        /* 5P Summary quote styling */
        .fivep-quote {
            font-style: italic;
            color: #555;
            padding: 12px 16px;
            border-left: 3px solid #8B5CF6;
            background: #f9f9f9;
            margin: 12px 0;
            border-radius: 4px;
            line-height: 1.6;
        }

        .fivep-unclamped {
            /* No max-height restriction */
        }

        /* Badge row for tags and personas */
        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin: 12px 0;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            background: #f5f5f5;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            font-size: 12px;
            color: #555;
        }

        /* Hide footer in conversation view to fix input positioning */
        footer, [role="contentinfo"] {
            display: none !important;
        }

                
        .st-key-how_works_top button[data-testid="stBaseButton-secondary"] {
            background: rgba(102, 126, 234, 0.1) !important;
            border: 2px solid #667eea !important;
            color: #667eea !important;
            border-radius: 6px !important;           /* Smaller radius */
            padding: 8px 16px !important;            /* Less padding */
            font-size: 13px !important;              /* Smaller text */
            font-weight: 500 !important;             /* Less bold */
            transition: all 0.2s ease !important;
        }

        /* Add breathing room around the button container */
        .st-key-how_works_top {
            margin: 16px 0 20px 0 !important;        /* More space above/below */
            padding: 0 20px !important;              /* Side padding */
        }      

        .st-key-how_works_top button[data-testid="stBaseButton-secondary"]:hover {
            background: rgba(102, 126, 234, 0.2) !important;
            border-color: #764ba2 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
        }

        /* Force text color inside */
        .st-key-how_works_top button p {
            color: #667eea !important;
            font-weight: 600 !important;
            margin: 0 !important;
        }
       /* --- NUCLEAR BRUTE-FORCE FOCUS KILLER (Place inside your <style> block) --- */

        /* 1. Reset Global Variables to Neutralize Theme Color */
        :root {
            --st-focus-ring-color: transparent !important;
            --primary-color: #f5f5f5 !important; 
            --st-primary-color: #f5f5f5 !important;
        }

        /* 2. Target the specific element wrappers responsible for the purple glow (using Max Specificity) */
        /* Targets the text input container */
        [data-testid^="stTextInput"] > div > div > div, 
        /* Targets the base input field itself */
        div[data-baseweb="base-input"],
        /* Targets the fieldset wrapper which draws the border */
        [data-testid^="stTextInput"] fieldset {
            /* Apply normal non-focus styling by default */
            border-color: #E5E7EB !important;
            box-shadow: none !important;
            outline: none !important;
        }

        /* 3. Aggressively target the FOCUS/HOVER STATES on all identified wrappers */
        [data-testid^="stTextInput"] :focus,
        [data-testid^="stTextInput"] :hover,
        [data-testid^="stTextInput"] :focus-within,
        div[data-baseweb="base-input"]:focus,
        div[data-baseweb="base-input"]:focus-within,
        div[data-baseweb="base-input"]:hover {
            /* Brute-force: Force it back to the wireframe gray state */
            border-color: #E5E7EB !important;
            box-shadow: none !important;
            outline: none !important;
        }
        /* FINAL OVERRIDE - Most specific possible */
        [data-testid="stChatInput"] div[data-baseweb="input"] > div:first-child,
        [data-testid="stChatInput"] div[data-baseweb="base-input"] > div:first-child,
        [data-testid="stChatInput"] [class*="Input-Container"],
        [data-testid="stChatInput"] div[class*="st-"][class*="emotion"] > div:first-child {
            border-radius: 8px !important;
            overflow: hidden !important;
        }

        /* Force the parent fieldset/wrapper */
        [data-testid="stChatInput"] fieldset,
        [data-testid="stChatInput"] [data-baseweb="input"],
        [data-testid="stChatInput"] [data-baseweb="base-input"] {
            border-radius: 8px !important;
        }

         /* ========================================
       FIX: TEXTAREA BORDER ISSUE (ADD AT VERY BOTTOM)
       ======================================== */
    
        /* KILL the purple left border on input - it's inheriting from chat messages */
        [data-testid="stChatInput"] textarea,
        [data-testid="stChatInputTextArea"],
        [data-testid="stChatInput"] div,
        [data-testid="stChatInput"] fieldset,
        [data-testid="stChatInput"] *:not(button) {
            border-left: 2px solid #ddd !important;  /* Force gray, not purple */
        }

        /* Ensure focus state also uses gray left border */
        [data-testid="stChatInput"] textarea:focus,
        [data-testid="stChatInputTextArea"]:focus {
            border-left: 2px solid #8B5CF6 !important;  /* Purple only on focus */
            border-top: 2px solid #8B5CF6 !important;
            border-right: 2px solid #8B5CF6 !important;
            border-bottom: 2px solid #8B5CF6 !important;
        }

        /* Prevent ANY element inside chat input from having purple left border by default */
        [data-testid="stChatInput"] *:not(:focus) {
            border-left-color: #ddd !important;
        }
        /* ========================================
            FINAL FIX: Kill wrapper borders
            ======================================== */

        /* Target the specific wrapper div that has the gray border */
        [data-testid="stChatInput"] div[class*="exaa2ht1"],
        [data-testid="stChatInput"] div[data-baseweb="textarea"],
        [data-testid="stChatInput"] > div > div:first-child {
            border: none !important;
            border-left: none !important;
            box-shadow: none !important;
            background: transparent !important;
        }

        /* ONLY the textarea gets styled */
        textarea[data-testid="stChatInputTextArea"] {
            border: 2px solid #ddd !important;
            border-radius: 8px !important;
        }

        textarea[data-testid="stChatInputTextArea"]:focus {
            border: 2px solid #8B5CF6 !important;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
        }
        /* ========================================
        TEXTAREA BORDERS - Clean styling
        ======================================== */

        /* MAXIMUM SPECIFICITY - Force borders on textarea */
        [data-testid="stChatInput"] textarea[data-testid="stChatInputTextArea"][class*="st-"],
        textarea[data-testid="stChatInputTextArea"].st-ae {
            border: 2px solid #ddd !important;
            border-radius: 8px !important;
            padding: 14px 18px !important;
            min-height: 48px !important;
            max-height: 48px !important;
            background: white !important;
        }

        /* Focus state with maximum specificity */
        [data-testid="stChatInput"] textarea[data-testid="stChatInputTextArea"]:focus,
        textarea[data-testid="stChatInputTextArea"].st-ae:focus {
            border: 2px solid #8B5CF6 !important;
            border-color: #8B5CF6 !important;
            outline: none !important;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
        }
        /* Match landing page input styling for chat textarea */
    
        /* Fix clipped corners - make parent containers visible */
        [data-testid="stChatInput"],
        [data-testid="stChatInput"] > div,
        [data-testid="stChatInput"] > div > div,
        [data-baseweb="textarea"],
        [data-baseweb="base-input"] {
            overflow: visible !important;
        }
        
        /* Style the textarea to match landing page */
        textarea[data-testid="stChatInputTextArea"] {
            width: 100% !important;
            padding: 20px 24px !important;
            font-size: 17px !important;
            border: 2px solid #E5E7EB !important;
            border-radius: 16px !important;
            transition: all 0.2s ease !important;
            background: #FAFAFA !important;
            font-family: inherit !important;
            overflow: visible !important;
            min-height: 60px !important;
            max-height: 60px !important;
        }
        
        /* Focus state - purple like the landing page */
        textarea[data-testid="stChatInputTextArea"]:focus {
            border-color: #8B5CF6 !important;
            outline: none !important;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
        }
        /* Kill all wrapper borders - only style the textarea */
        [data-testid="stChatInput"] div[class*="exaa2ht"],
        [data-baseweb="textarea"],
        [data-baseweb="base-input"],
        [data-testid="stChatInput"] > div,
        [data-testid="stChatInput"] > div > div {
            border: none !important;
            box-shadow: none !important;
            overflow: visible !important;
            background: transparent !important;
        }

        /* ONLY style the textarea itself */
        textarea[data-testid="stChatInputTextArea"] {
            width: 100% !important;
            padding: 20px 24px !important;
            font-size: 17px !important;
            border: 2px solid #E5E7EB !important;
            border-radius: 16px !important;
            transition: all 0.2s ease !important;
            background: #FAFAFA !important;
            font-family: inherit !important;
            min-height: 60px !important;
            max-height: 60px !important;
        }

        /* Focus state */
        textarea[data-testid="stChatInputTextArea"]:focus {
            border-color: #8B5CF6 !important;
            outline: none !important;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
        }

        button[data-testid="stChatInputSubmitButton"] {
            padding: 14px 28px !important;
            background: #8B5CF6 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            /* Position adjustments */
            transform: translate(-3px, 1.5px) !important;    /* More left - Move down */   
        }
        /* Fix hint - center it below the input */
        [data-testid="stChatInput"]::after {
            content: "Powered by OpenAI GPT-4o-mini with semantic search across 120+ project case studies";
            display: block;
            position: fixed;  /* Fixed positioning */
            bottom: 26px;     /* 10px from bottom of screen */
            left: 50%;
            transform: translateX(-50%);  /* Center it */
            text-align: center;
            font-size: 12px;
            color: #95a5a6;
            padding: 10px 0;
            width: 100%;
            max-width: 900px;
            z-index: 1000;
            }

    </style>
    """,
        unsafe_allow_html=True,
    )

    # Page header with purple gradient - streamlined with button integrated
    st.markdown(
        """
    <div class="conversation-header">
        <div class="conversation-header-content">
            <img class="conversation-agy-avatar" src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_avatar.png" width="64" height="64" style="width: 64px; height: 64px; border-radius: 50%; border: 3px solid white !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;" alt="Agy"/>
            <div class="conversation-header-text">
                <h1>Ask MattGPT</h1>
                <p>Meet Agy 🐾 — Tracking down insights from 20+ years of transformation experience</p>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Status bar matching landing page exactly - moved to be flush with purple header
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

    # # Brand CTA button with specific key-based selector
    # if st.button("🔍 How Agy searches", key="how_works_top"):
    #     st.session_state["show_how_modal"] = not st.session_state.get(
    #         "show_how_modal", False
    #     )
    #     st.rerun()

    """
    Clean "How Agy Searches" Modal Implementation
    Combines stable CSS targeting, accessibility, and proper Streamlit rendering
    """

    # ============================================================================
    # MODAL CONTROL FUNCTION
    # ============================================================================

    def toggle_how_modal():
        """Centralized toggle for modal visibility state."""
        st.session_state["show_how_modal"] = not st.session_state.get(
            "show_how_modal", False
        )
        st.rerun()

    # ============================================================================
    # TRIGGER BUTTON
    # ============================================================================

    if st.button("🔍 How Agy searches", key="how_works_top"):
        toggle_how_modal()

    # ============================================================================
    # MODAL RENDERING
    # ============================================================================
    # Show the panel if toggled
    if st.session_state.get("show_how_modal", False):
        
        # Auto-scroll to top
        st.markdown("""
            <script>
            window.scrollTo({top: 0, behavior: 'smooth'});
            </script>
        """, unsafe_allow_html=True)
        
        # Just style the content nicely - NO backdrop
        st.markdown("""
        <style>
        /* Close button styling */
        button[key="close_how"] {
            background: white !important;
            border: 2px solid #D1D5DB !important;
            border-radius: 8px !important;
            color: #6B7280 !important;
            font-size: 20px !important;
            font-weight: 700 !important;
            padding: 8px 16px !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
        
        button[key="close_how"]:hover {
            background: #F3F4F6 !important;
            border-color: #8B5CF6 !important;
            color: #8B5CF6 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Nice bordered container
        with st.container(border=True):
            # Header with close button
            col1, col2 = st.columns([10, 1])
            
            with col1:
                st.markdown("## 🔍 How Agy Finds Your Stories")
            
            with col2:
                if st.button("✕", key="close_how", help="Close"):
                    toggle_how_modal()
            
            st.markdown("---")
            
            # 3-step flow
            components.html(
                """
                <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                            padding: 28px; 
                            background: linear-gradient(135deg, #FAFAFA 0%, #F9FAFB 100%); 
                            border-radius: 16px; 
                            border: 2px solid #E5E7EB;">
                    
                    <!-- Step 1: You Ask -->
                    <div style="margin-bottom: 48px;">
                        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
                            <div style="background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); 
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
                                        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);">1</div>
                            <h3 style="margin: 0; color: #1F2937; font-size: 24px; font-weight: 700;">You Ask</h3>
                        </div>
                        <div style="margin-left: 64px; 
                                    background: white; 
                                    padding: 24px; 
                                    border-radius: 12px; 
                                    border: 2px solid #E9D5FF; 
                                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                            <div style="color: #4B5563; font-size: 16px; font-style: italic; line-height: 1.6;">
                                "Show me cloud migration projects in financial services"
                            </div>
                        </div>
                    </div>

                    <!-- Arrow -->
                    <div style="text-align: center; color: #A78BFA; font-size: 40px; margin: 20px 0; font-weight: 300;">↓</div>

                    <!-- Step 2: Agy Searches -->
                    <div style="margin-bottom: 48px;">
                        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
                            <div style="background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); 
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
                                        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);">2</div>
                            <h3 style="margin: 0; color: #1F2937; font-size: 24px; font-weight: 700;">Agy Searches</h3>
                        </div>
                        <div style="margin-left: 64px;">
                            <div style="display: flex; gap: 16px; margin-bottom: 16px;">
                                <div style="flex: 1; 
                                            background: white; 
                                            padding: 20px; 
                                            border-radius: 10px; 
                                            border: 2px solid #E9D5FF; 
                                            box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                                    <div style="font-weight: 700; color: #7C3AED; font-size: 16px; margin-bottom: 8px;">
                                        🧠 AI Understanding
                                    </div>
                                    <div style="color: #6B21A8; font-size: 14px; line-height: 1.6;">
                                        Finds stories with similar meaning
                                    </div>
                                </div>
                                <div style="flex: 1; 
                                            background: white; 
                                            padding: 20px; 
                                            border-radius: 10px; 
                                            border: 2px solid #BFDBFE; 
                                            box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                                    <div style="font-weight: 700; color: #2563EB; font-size: 16px; margin-bottom: 8px;">
                                        🔍 Keyword Match
                                    </div>
                                    <div style="color: #1E40AF; font-size: 14px; line-height: 1.6;">
                                        Finds exact terms you used
                                    </div>
                                </div>
                            </div>
                            <div style="background: white; 
                                        padding: 20px; 
                                        border-radius: 10px; 
                                        border: 2px solid #FDE68A; 
                                        box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                                <div style="font-weight: 700; color: #D97706; font-size: 16px; margin-bottom: 8px;">
                                    ⚡ Smart Filtering
                                </div>
                                <div style="color: #92400E; font-size: 14px; line-height: 1.6;">
                                    Applies your industry, skill, and time filters
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Arrow -->
                    <div style="text-align: center; color: #A78BFA; font-size: 40px; margin: 20px 0; font-weight: 300;">↓</div>

                    <!-- Step 3: You Get Results -->
                    <div>
                        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
                            <div style="background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); 
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
                                        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);">3</div>
                            <h3 style="margin: 0; color: #1F2937; font-size: 24px; font-weight: 700;">You Get Results</h3>
                        </div>
                        <div style="margin-left: 64px; 
                                    background: white; 
                                    border: 3px solid #8B5CF6; 
                                    border-radius: 12px; 
                                    padding: 24px; 
                                    box-shadow: 0 8px 20px rgba(139, 92, 246, 0.25);">
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                        color: white; 
                                        padding: 20px; 
                                        border-radius: 10px; 
                                        margin-bottom: 20px; 
                                        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);">
                                <div style="font-weight: 700; font-size: 17px; margin-bottom: 8px;">
                                    Cloud Migration at Fortune 50 Bank
                                </div>
                                <div style="font-size: 15px; opacity: 0.95; line-height: 1.6;">
                                    Led 50-person team migrating 200+ apps to AWS...
                                </div>
                            </div>
                            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                                <span style="background: #EDE9FE; 
                                             color: #7C3AED; 
                                             padding: 8px 16px; 
                                             border-radius: 20px; 
                                             font-size: 13px; 
                                             font-weight: 700; 
                                             border: 2px solid #DDD6FE;">Financial Services</span>
                                <span style="background: #E0E7FF; 
                                             color: #4F46E5; 
                                             padding: 8px 16px; 
                                             border-radius: 20px; 
                                             font-size: 13px; 
                                             font-weight: 700; 
                                             border: 2px solid #C7D2FE;">AWS</span>
                                <span style="background: #DBEAFE; 
                                             color: #2563EB; 
                                             padding: 8px 16px; 
                                             border-radius: 20px; 
                                             font-size: 13px; 
                                             font-weight: 700; 
                                             border: 2px solid #BFDBFE;">2020-2023</span>
                            </div>
                        </div>
                    </div>

                </div>
                """,
                height=1000
            )
            
            st.markdown("---")
            
            # Step 4: Technical Details (matches step 1-3 style)
            components.html(
                """
                <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                    
                    <!-- Step 4 Header -->
                    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
                        <h3 style="margin: 0; color: #1F2937; font-size: 24px; font-weight: 700;">Technical Details</h3>
                    </div>
                    
                    <!-- Content Area -->
                    <div style="margin-left: 64px; padding: 26px; background: linear-gradient(135deg, #FAFAFA 0%, #F9FAFB 100%); border-radius: 16px; border: 2px solid #E5E7EB;">
                        
                        <!-- Two Cards -->
                        <div style="display: flex; gap: 20px; margin-bottom: 24px;">
                            
                            <!-- Search Technology Card -->
                            <div style="flex: 1; 
                                        background: white; 
                                        padding: 24px; 
                                        border-radius: 12px; 
                                        border: 2px solid #E9D5FF; 
                                        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.1);">
                                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 16px;">
                                    <span style="font-size: 24px;">🔍</span>
                                    <h4 style="margin: 0; color: #7C3AED; font-size: 18px; font-weight: 700;">
                                        Search Technology
                                    </h4>
                                </div>
                                <ul style="margin: 0; padding-left: 20px; color: #4B5563; line-height: 1.8; font-size: 14px;">
                                    <li><strong style="color: #6B21A8;">Sentence-BERT</strong> embeddings (384-dim)</li>
                                    <li><strong style="color: #6B21A8;">Pinecone</strong> vector database</li>
                                    <li><strong style="color: #6B21A8;">80% semantic + 20% keyword</strong></li>
                                    <li>Top-30 candidate pool, rank top-3</li>
                                </ul>
                            </div>
                            
                            <!-- Data Structure Card -->
                            <div style="flex: 1; 
                                        background: white; 
                                        padding: 24px; 
                                        border-radius: 12px; 
                                        border: 2px solid #BFDBFE; 
                                        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);">
                                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 16px;">
                                    <span style="font-size: 24px;">📊</span>
                                    <h4 style="margin: 0; color: #2563EB; font-size: 18px; font-weight: 700;">
                                        Data Structure
                                    </h4>
                                </div>
                                <ul style="margin: 0; padding-left: 20px; color: #4B5563; line-height: 1.8; font-size: 14px;">
                                    <li><strong style="color: #1E40AF;">120+ STAR-formatted</strong> stories</li>
                                    <li>Rich metadata (client, skills, outcomes)</li>
                                    <li><strong style="color: #1E40AF;">Multi-mode synthesis</strong> (3 views)</li>
                                    <li>Source attribution with confidence scores</li>
                                </ul>
                            </div>
                            
                        </div>
                        
                        <!-- Performance Stats Bar -->
                        <div style="background: white;
                                    padding: 20px 32px;
                                    border-radius: 12px;
                                    border: 2px solid #D1D5DB;
                                    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                                    display: flex;
                                    justify-content: space-around;
                                    align-items: center;">
                            <div style="text-align: center;">
                                <div style="font-size: 28px; font-weight: 700; color: #8B5CF6; margin-bottom: 4px;">120+</div>
                                <div style="font-size: 13px; color: #6B7280; font-weight: 500;">Stories Indexed</div>
                            </div>
                            <div style="width: 1px; height: 40px; background: #E5E7EB;"></div>
                            <div style="text-align: center;">
                                <div style="font-size: 28px; font-weight: 700; color: #8B5CF6; margin-bottom: 4px;">~1.2s</div>
                                <div style="font-size: 13px; color: #6B7280; font-weight: 500;">Avg Response Time</div>
                            </div>
                            <div style="width: 1px; height: 40px; background: #E5E7EB;"></div>
                            <div style="text-align: center;">
                                <div style="font-size: 28px; font-weight: 700; color: #8B5CF6; margin-bottom: 4px;">87%</div>
                                <div style="font-size: 13px; color: #6B7280; font-weight: 500;">Relevance Accuracy</div>
                            </div>
                        </div>
                        
                    </div>
                    
                </div>
                """,
                height=440
            )


    # Define ctx - MUST be outside and after the modal block
    ctx = get_context_story(stories)
    _show_ctx = bool(ctx) and (
        st.session_state.get("__ctx_locked__") or st.session_state.get("__asked_once__")
    )

    # if st.button("🔍 How Agy searches", key="how_works_top"):
    #     st.session_state["show_how_modal"] = not st.session_state.get(
    #         "show_how_modal", False
    #     )
    #     st.rerun()

    # st.markdown('</div>', unsafe_allow_html=True)

    # # Show the modal if toggled
    # if st.session_state.get("show_how_modal", False):
    #     # Force scroll to top when modal opens
    #     st.markdown(
    #         """
    #     <script>
    #     window.scrollTo({top: 0, behavior: 'smooth'});
    #     </script>
    #     """,
    #         unsafe_allow_html=True,
    #     )

    #     # Create a proper modal container without using expander
    #     st.markdown("---")

    #     # Add modal styling
    #     st.markdown("""
    #     <style>
    #     /* Target the container that has the modal content */
    #     div[data-testid="stVerticalBlock"]:has(div.element-container:has(button[data-testid*="baseButton"][aria-label*="close"])) > div[data-testid="element-container"],
    #     div[data-testid="stVerticalBlock"]:has(h2:contains("How Agy Searches")) {
    #         background: #fafafa;
    #         border: 2px solid #e0e0e0;
    #         border-radius: 16px;
    #         padding: 32px;
    #         box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    #         margin: 24px 0;
    #     }
    #     /* Style the entire modal area more broadly */
    #     .stMarkdown:has(h2:contains("How Agy")) ~ * {
    #         background: inherit;
    #     }
    #     </style>
    #     """, unsafe_allow_html=True)

    #     # Use a bordered container with visual background
    #     modal_container = st.container(border=True)

    #     with modal_container:
    #         # Header with close button
    #         col1, col2 = st.columns([10, 1])
    #         with col1:
    #             st.markdown("## 🔧 How Agy Searches")
    #         with col2:
    #             if st.button("✕", key="close_how"):
    #                 st.session_state["show_how_modal"] = False
    #                 st.rerun()
    #         # Quick stats bar
    #         col1, col2, col3, col4 = st.columns(4)
    #         with col1:
    #             st.metric("Stories Indexed", "120+")
    #         with col2:
    #             st.metric("Avg Response Time", "1.2s")
    #         with col3:
    #             st.metric("Retrieval Accuracy", "87%")
    #         with col4:
    #             st.metric("Vector Dimensions", "384")

    #         st.markdown("---")

    #         # Architecture overview - COLOR CODED SECTIONS
    #         col1, col2 = st.columns(2)

    #         with col1:
    #             components.html(
    #                 """
    #                 <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #EDE9FE 0%, #DDD6FE 100%); padding: 24px 24px 32px 24px; border-radius: 12px; border-left: 4px solid #8B5CF6;">
    #                     <h3 style="color: #6B21A8; margin-top: 0; display: flex; align-items: center; gap: 10px;">
    #                         <span style="font-size: 28px;">🧠</span>
    #                         <span>Solution Architecture</span>
    #                     </h3>

    #                     <div style="margin-bottom: 16px;">
    #                         <div style="font-weight: 600; color: #7C3AED; margin-bottom: 8px;">🎯 Semantic Search Pipeline</div>
    #                         <ul style="margin: 0; padding-left: 20px; color: #5B21B6; line-height: 1.7;">
    #                             <li>Sentence-BERT embeddings (all-MiniLM-L6-v2)</li>
    #                             <li>384-dimensional vector space</li>
    #                             <li>Pinecone vector database with metadata filtering</li>
    #                         </ul>
    #                     </div>

    #                     <div>
    #                         <div style="font-weight: 600; color: #7C3AED; margin-bottom: 8px;">🔄 Hybrid Retrieval</div>
    #                         <ul style="margin: 0; padding-left: 20px; color: #5B21B6; line-height: 1.7;">
    #                             <li>80% semantic similarity weight</li>
    #                             <li>20% keyword matching weight</li>
    #                             <li>Intent recognition for query understanding</li>
    #                         </ul>
    #                     </div>
    #                 </div>
    #                 """,
    #                 height=380
    #             )

    #         with col2:
    #             components.html(
    #                 """
    #                 <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #E0E7FF 0%, #C7D2FE 100%); padding: 24px 24px 32px 24px; border-radius: 12px; border-left: 4px solid #6366F1;">
    #                     <h3 style="color: #3730A3; margin-top: 0; display: flex; align-items: center; gap: 10px;">
    #                         <span style="font-size: 28px;">📊</span>
    #                         <span>Data & Processing</span>
    #                     </h3>

    #                     <div style="margin-bottom: 16px;">
    #                         <div style="font-weight: 600; color: #4F46E5; margin-bottom: 8px;">📚 Story Corpus</div>
    #                         <ul style="margin: 0; padding-left: 20px; color: #312E81; line-height: 1.7;">
    #                             <li>120+ structured narratives from Fortune 500 projects</li>
    #                             <li>STAR/5P framework encoding</li>
    #                             <li>Rich metadata: client, domain, outcomes, metrics</li>
    #                         </ul>
    #                     </div>

    #                     <div>
    #                         <div style="font-weight: 600; color: #4F46E5; margin-bottom: 8px;">💬 Response Generation</div>
    #                         <ul style="margin: 0; padding-left: 20px; color: #312E81; line-height: 1.7;">
    #                             <li>Context-aware retrieval (top-k=30)</li>
    #                             <li>Multi-mode synthesis (Narrative/Key Points/Deep Dive)</li>
    #                             <li>Source attribution with confidence scoring</li>
    #                         </ul>
    #                     </div>
    #                 </div>
    #                 """,
    #                 height=380
    #             )

    #         # VISUAL QUERY FLOW - Replaces plain text code block
    #         components.html(
    #             """
    #             <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%); padding: 32px 32px 40px 32px; border-radius: 12px; border-left: 4px solid #A78BFA; margin-top: 24px;">
    #                 <h3 style="color: #5B21B6; margin-top: 0; display: flex; align-items: center; gap: 10px; margin-bottom: 24px;">
    #                     <span style="font-size: 28px;">⚡</span>
    #                     <span>Query Flow Pipeline</span>
    #                 </h3>

    #                 <div style="display: flex; flex-direction: column; gap: 16px;">
    #                     <!-- Step 1 -->
    #                     <div style="background: white; padding: 16px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; align-items: center; gap: 12px;">
    #                         <div style="background: #8B5CF6; color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0;">1</div>
    #                         <div style="flex-grow: 1;">
    #                             <div style="font-weight: 600; color: #5B21B6; margin-bottom: 4px;">💬 Your Question</div>
    #                             <div style="font-size: 13px; color: #6B21A8;">Natural language input from user</div>
    #                         </div>
    #                     </div>

    #                     <!-- Arrow -->
    #                     <div style="text-align: center; color: #A78BFA; font-size: 24px;">↓</div>

    #                     <!-- Step 2 -->
    #                     <div style="background: white; padding: 16px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; align-items: center; gap: 12px;">
    #                         <div style="background: #8B5CF6; color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0;">2</div>
    #                         <div style="flex-grow: 1;">
    #                             <div style="font-weight: 600; color: #5B21B6; margin-bottom: 4px;">🔍 Embedding + Intent Analysis</div>
    #                             <div style="font-size: 13px; color: #6B21A8;">Convert to 384-dim vector, detect intent type</div>
    #                         </div>
    #                     </div>

    #                     <!-- Arrow -->
    #                     <div style="text-align: center; color: #A78BFA; font-size: 24px;">↓</div>

    #                     <!-- Step 3 -->
    #                     <div style="background: white; padding: 16px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; align-items: center; gap: 12px;">
    #                         <div style="background: #8B5CF6; color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0;">3</div>
    #                         <div style="flex-grow: 1;">
    #                             <div style="font-weight: 600; color: #5B21B6; margin-bottom: 4px;">🎯 Pinecone Vector Search + Keyword Matching</div>
    #                             <div style="font-size: 13px; color: #6B21A8;">Hybrid retrieval: 80% semantic + 20% keyword</div>
    #                         </div>
    #                     </div>

    #                     <!-- Arrow -->
    #                     <div style="text-align: center; color: #A78BFA; font-size: 24px;">↓</div>

    #                     <!-- Step 4 -->
    #                     <div style="background: white; padding: 16px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; align-items: center; gap: 12px;">
    #                         <div style="background: #8B5CF6; color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0;">4</div>
    #                         <div style="flex-grow: 1;">
    #                             <div style="font-weight: 600; color: #5B21B6; margin-bottom: 4px;">📊 Hybrid Scoring & Ranking</div>
    #                             <div style="font-size: 13px; color: #6B21A8;">Rank top 3 from 30 candidate pool</div>
    #                         </div>
    #                     </div>

    #                     <!-- Arrow -->
    #                     <div style="text-align: center; color: #A78BFA; font-size: 24px;">↓</div>

    #                     <!-- Step 5 -->
    #                     <div style="background: white; padding: 16px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; align-items: center; gap: 12px;">
    #                         <div style="background: #8B5CF6; color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0;">5</div>
    #                         <div style="flex-grow: 1;">
    #                             <div style="font-weight: 600; color: #5B21B6; margin-bottom: 4px;">✨ Response Synthesis with Sources</div>
    #                             <div style="font-size: 13px; color: #6B21A8;">Generate 3 response modes with source attribution</div>
    #                         </div>
    #                     </div>
    #                 </div>
    #             </div>
    #             """,
    #             height=800
    #         )

    #         st.markdown("---")
    #         st.markdown("### System Architecture")

    #         try:
    #             with open("assets/rag_architecture_grid_svg.svg", "r") as f:
    #                 svg_content = f.read()

    #             # Remove XML declaration and DOCTYPE
    #             svg_content = svg_content.replace(
    #                 '<?xml version="1.0" encoding="UTF-8" standalone="no"?>', ''
    #             )
    #             svg_content = svg_content.replace(
    #                 '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">',
    #                 '',
    #             )

    #             # Use HTML component with transparent background and no scroll

    #             components.html(
    #                 f"""
    #             <div style='width: 100%; text-align: center;'>
    #                 {svg_content}
    #             </div>
    #             """,
    #                 height=280,
    #                 scrolling=False,
    #             )

    #         except Exception as e:
    #             st.error(f"Error loading architecture diagram: {e}")

    #         st.markdown("---")

    #         # Detailed breakdown
    #         st.markdown("### Architecture Details")

    #         col1, col2 = st.columns(2)

    #         with col1:
    #             st.markdown(
    #                 """
    #             **Search & Retrieval**
    #             - **Semantic**: Pinecone cosine similarity (80% weight)
    #             - **Keyword**: BM25-style token overlap (20% weight)
    #             - Minimum similarity threshold: 0.15
    #             - Top-k pool: 30 candidates before ranking
    #             """
    #             )

    #         with col2:
    #             st.markdown(
    #                 """
    #             **Response Synthesis**
    #             - Rank top 3 stories by blended score
    #             - Generate 3 views from same sources:
    #             - Narrative (1-paragraph summary)
    #             - Key Points (3-4 bullets)
    #             - Deep Dive (STAR breakdown)
    #             - Interactive source chips with confidence %
    #             """
    #             )

    #         st.markdown("---")

    #         st.markdown(
    #             """
    #         **Key Differentiators:**
    #         - Hybrid retrieval ensures both semantic understanding and exact term matching
    #         - Multi-mode synthesis provides flexible presentation for different use cases
    #         - Context locking allows follow-up questions on specific stories
    #         - Off-domain gating with suggestion chips prevents poor matches
    #         """
    #         )

    # # Define ctx - MUST be outside and after the modal block
    # ctx = get_context_story(stories)
    # _show_ctx = bool(ctx) and (
    #     st.session_state.get("__ctx_locked__") or st.session_state.get("__asked_once__")
    # )

    if _show_ctx:
        render_compact_context_banner(stories)

    # Rest of your Ask MattGPT content continues as normal
    # Context banner, transcript, etc...

    # with right:
    #    if st.button("×", key="btn_clear_ctx", help="Clear context"):
    #       _clear_ask_context()

    # Lightweight DEBUG status for Ask (visible only when DEBUG=True)
    if DEBUG:
        try:
            _dbg_flags = {
                "vector": VECTOR_BACKEND,
                "index": PINECONE_INDEX_NAME or "-",
                "ns": PINECONE_NAMESPACE or "-",
                "pc_suppressed": bool(st.session_state.get("__pc_suppressed__")),
                "has_last": bool(st.session_state.get("last_sources")),
                "pending_snap": bool(st.session_state.get("__pending_card_snapshot__")),
                # NEW: report external renderer overrides
                "ext_chips": (
                    "yes"
                    if callable(globals().get("_ext_render_sources_chips"))
                    else "no"
                ),
                "ext_badges": (
                    "yes"
                    if callable(globals().get("_ext_render_sources_badges_static"))
                    else "no"
                ),
            }
            st.caption("🧪 " + ", ".join(f"{k}={v}" for k, v in _dbg_flags.items()))
            # Second line: last prompt + ask decision
            lp = (st.session_state.get("__ask_dbg_prompt") or "").strip()
            lp = (lp[:60] + "…") if len(lp) > 60 else lp
            st.caption(
                "🧪 "
                + f"prompt='{lp}' from_suggestion={st.session_state.get('__ask_dbg_from_suggestion')}"
                + f" force={st.session_state.get('__ask_dbg_force_answer')} pc_hits={st.session_state.get('__dbg_pc_hits')}"
                + f" decision={st.session_state.get('__ask_dbg_decision')}"
                + f" reason={st.session_state.get('ask_last_reason')}"
            )
        except Exception:
            pass

    # 1) Bootstrap a stable transcript (one-time)
    _ensure_ask_bootstrap()

    # 2) Unify seeds and chip-clicks: inject as a real user turn if present
    seed = st.session_state.pop("seed_prompt", None)
    injected = st.session_state.pop("__inject_user_turn__", None)
    pending = seed or injected

    if DEBUG and (seed or injected):
        dbg(f"[POP] seed={seed}, injected={injected}, pending={pending}")

    # Multi-step processing for chip injection to show thinking indicator
    processing_state = st.session_state.get("__processing_chip_injection__")

    if pending and not processing_state:
        # Step 1: Push user turn and set processing to "pending", then rerun to show indicator
        if DEBUG:
            dbg(f"[STEP1] pending={pending}, transcript_len={len(st.session_state.get('ask_transcript', []))}")
        if st.session_state.get("__pending_card_snapshot__"):
            
            st.session_state["__pending_card_snapshot__"] = False
        _push_user_turn(pending)
        if DEBUG:
            dbg(f"[STEP1] after push, transcript_len={len(st.session_state.get('ask_transcript', []))}")
        st.session_state["__processing_chip_injection__"] = {"query": pending, "step": "pending"}
        st.rerun()

    elif isinstance(processing_state, dict) and processing_state.get("step") == "pending":
        # Step 2: Render page with thinking indicator visible, then rerun to actually process
        if DEBUG:
            dbg(f"[STEP2] showing indicator for query={processing_state.get('query')}")
        # Mark as ready to process on next render
        st.session_state["__processing_chip_injection__"] = {"query": processing_state["query"], "step": "processing"}
        # Continue rendering to show transcript and indicator

    elif isinstance(processing_state, dict) and processing_state.get("step") == "processing":
        # Step 3: Now actually process the query
        pending_query = processing_state["query"]
        if DEBUG:
            dbg(f"[STEP3] processing={pending_query}, transcript_len={len(st.session_state.get('ask_transcript', []))}")

        try:
            # Ask is pure semantic; ignore Explore filters here
            resp = send_to_backend(pending_query, {}, ctx, stories)

        except Exception as e:
            print(f"DEBUG: send_to_backend failed: {e}")
            import traceback

            traceback.print_exc()
            _push_assistant_turn(f"Error: {str(e)}")
            st.session_state["__processing_chip_injection__"] = False
            st.rerun()

        else:
            set_answer(resp)
            # Push conversational answer instead of card snapshot (wireframe style)
            if not st.session_state.get("ask_last_reason") and not st.session_state.get(
                "__sticky_banner__"
            ):
                answer_text = resp.get("answer_md") or resp.get("answer", "")
                sources = resp.get("sources", []) or []
                _push_conversational_answer(answer_text, sources)
                st.session_state["__suppress_live_card_once__"] = True
                # If a chip click requested banner clear, perform it now after answer set
                if st.session_state.pop("__clear_banner_after_answer__", False):
                    st.session_state.pop("ask_last_reason", None)
                    st.session_state.pop("ask_last_query", None)
                    st.session_state.pop("ask_last_overlap", None)
            elif st.session_state.get("ask_last_reason"):
                # Nonsense detected - add banner entry to transcript
                reason = st.session_state.get("ask_last_reason", "")
                query = st.session_state.get("ask_last_query", "")
                overlap = st.session_state.get("ask_last_overlap", None)

                st.session_state["ask_transcript"].append({
                    "type": "banner",
                    "Role": "assistant",
                    "reason": reason,
                    "query": query,
                    "overlap": overlap,
                })

                # Clear flags after adding to transcript
                st.session_state.pop("ask_last_reason", None)
                st.session_state.pop("ask_last_query", None)
                st.session_state.pop("ask_last_overlap", None)
            st.session_state["__processing_chip_injection__"] = False
            st.rerun()

    # 3) Render transcript so far (strict order, no reflow)
    _render_ask_transcript(stories)

    # 4) Banner now rendered as part of transcript (type="banner" entries)
    # Flags are cleared when banner entry is added to transcript

    # Sticky banner temporarily disabled to stabilize chip clicks
    st.session_state["__sticky_banner__"] = None

    # 5) Compact answer panel (title • unclamped 5P • view pills • sources)
    _m = st.session_state.get("answer_modes", {}) or {}
    _srcs = st.session_state.get("last_sources", []) or []
    _primary = None
    if _srcs:
        _sid = str(_srcs[0].get("id", ""))
        _primary = next((s for s in stories if str(s.get("id")) == _sid), None)
    # Suppress the bottom live card when:
    #  - a banner was rendered this run; or
    #  - we already have a conversational answer in the transcript
    has_conversational_answer = any(
        (isinstance(x, dict) and x.get("type") == "conversational")
        for x in st.session_state.get("ask_transcript", [])
    )
    if (
        not has_conversational_answer
        and not st.session_state.get("__suppress_live_card_once__")
        and st.session_state.get("last_answer")
    ):
        # Render live conversational answer (wireframe style)
        # This only shows if the answer hasn't been added to transcript yet
        with st.chat_message(
            "assistant",
            avatar="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/svg/agy_icon_color.svg",
        ):
            st.markdown(st.session_state.get("last_answer", ""))

            # Show Related Projects in wireframe style
            if _srcs:
                st.markdown(
                    '''
                <div class="sources-tight">
                    <div class="source-links-title">📚 RELATED PROJECTS</div>
                </div>
                ''',
                    unsafe_allow_html=True,
                )

                # Use columns with forms for complete styling control
                cols = st.columns(len(_srcs[:3]))
                for j, src in enumerate(_srcs[:3]):
                    title = src.get("title") or src.get("Title", "")
                    client = src.get("client") or src.get("Client", "")
                    label = f"{client} - {title}" if client and title else title

                    with cols[j]:
                        with st.form(key=f"live_source_form_{j}"):
                            st.markdown(
                                f"""
                            <style>
                            /* Hide form border */
                            div[data-testid="stForm"] {{
                                border: none !important;
                                padding: 0 !important;
                                margin: 0 !important;
                            }}
                            div[data-testid="stForm"] button {{
                                background: #F3F4F6 !important;
                                border: 2px solid #E5E7EB !important;
                                color: #2563EB !important;
                                font-size: 14px !important;
                                font-weight: 500 !important;
                                padding: 6px 12px !important;
                                border-radius: 8px !important;
                                width: 100% !important;
                                height: auto !important;
                                min-height: 32px !important;
                            }}
                            div[data-testid="stForm"] button p {{
                                color: #2563EB !important;
                                font-size: 14px !important;
                                margin: 0 !important;
                                line-height: 1.4 !important;
                            }}
                            div[data-testid="stForm"] button:hover {{
                                background: #EEF2FF !important;
                                border-color: #8B5CF6 !important;
                            }}
                            </style>
                            """,
                                unsafe_allow_html=True,
                            )

                            if st.form_submit_button(f"🔗 {label}"):
                                # Toggle expander - if same source clicked, close it; otherwise open new one
                                expanded_key = f"live_source_expanded_{j}"
                                current_expanded = st.session_state.get("live_source_expanded")

                                if current_expanded == expanded_key:
                                    # Clicking same source - close it
                                    st.session_state["live_source_expanded"] = None
                                else:
                                    # Open this source (closes any other)
                                    st.session_state["live_source_expanded"] = expanded_key
                                    # Store the source ID for rendering
                                    st.session_state["live_source_expanded_id"] = src.get("id")

                                st.rerun()

                # Render the expanded story detail below all buttons (only one at a time)
                expanded_key = st.session_state.get("live_source_expanded")
                expanded_id = st.session_state.get("live_source_expanded_id")

                if expanded_key and expanded_id:
                    # Find the story object
                    story_obj = next((s for s in stories if str(s.get("id")) == str(expanded_id)), None)

                    if story_obj:
                        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
                        render_story_detail(story_obj, "live_expanded", stories)

            # Action buttons (wireframe style)
            st.markdown(
                '''
            <div class="action-buttons">
                <button class="action-btn" onclick="this.classList.toggle('helpful-active')">
                    👍 Helpful
                </button>
                <button class="action-btn" onclick="navigator.clipboard.writeText(this.closest('[data-testid=stChatMessage]').innerText); this.textContent='✓ Copied!'; setTimeout(() => this.textContent='📋 Copy', 2000);">
                    📋 Copy
                </button>
                <button class="action-btn" onclick="alert('Share functionality coming soon!')">
                    🔗 Share
                </button>
            </div>
            ''',
                unsafe_allow_html=True,
            )

    # Reset one-shot suppression flag after a render cycle
    if st.session_state.get("__suppress_live_card_once__"):
        st.session_state["__suppress_live_card_once__"] = False

    # 5.5) Show thinking indicator at bottom (above input) if processing chip injection OR transitioning from Explore Stories
    processing_state = st.session_state.get("__processing_chip_injection__")
    show_transition = st.session_state.get("show_transition_indicator", False)
    show_thinking = (isinstance(processing_state, dict) and processing_state.get("step") in ["pending", "processing"]) or show_transition
    if DEBUG:
        dbg(f"[INDICATOR] processing_state={processing_state}, show_transition={show_transition}, show_thinking={show_thinking}")

    if show_thinking:
        st.markdown(
            """
<style>
@keyframes chaseAnimationBottom {
    0% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_1.png'); }
    33.33% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_2.png'); }
    66.66% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_3.png'); }
    100% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_1.png'); }
}
.thinking-ball-bottom {
    width: 48px;
    height: 48px;
    animation: chaseAnimationBottom 0.9s steps(3) infinite;
}
.transition-indicator-bottom {
    position: fixed;
    bottom: 140px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
    /* Better contrast for visibility */
    background: #F3F4F6 !important;
    color: #374151 !important;
    border: 1px solid #D1D5DB !important;
    padding: 12px 24px;
    border-radius: 24px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    opacity: 1 !important;
}
</style>
<div class='transition-indicator-bottom' style='display: flex;
            align-items: center;
            gap: 12px;'>
    <img class="thinking-ball-bottom" src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_1.png" alt="Thinking"/>
    <div style='color: #374151 !important; font-weight: 600 !important;'>🐾 Tracking down insights...</div>
</div>
""",
            unsafe_allow_html=True,
        )
        # If we just showed the indicator in "pending" step, trigger rerun to process
        if isinstance(processing_state, dict) and processing_state.get("step") == "processing":
            # We're now in the state where indicator is visible, rerun to actually process
            st.rerun()

    # 6) Handle a new chat input (command aliases or normal question)
    # Render the chat input only on the Ask MattGPT tab
    if st.session_state.get("active_tab") == "Ask MattGPT":
        user_input_local = st.chat_input(
            "💬 Ask a follow-up question...", key="ask_chat_input1"
        )
        # Add hint text below input

    else:
        user_input_local = None
    if user_input_local:
        # If a live card is pending snapshot from the previous answer, snapshot it now
        if st.session_state.get("__pending_card_snapshot__"):
            
            st.session_state["__pending_card_snapshot__"] = False

        # Append user's turn immediately to keep order deterministic
        _push_user_turn(user_input_local)

        # Clear context lock for fresh typed questions (not from suggestion chips)
        if not st.session_state.get("__ask_from_suggestion__"):
            st.session_state.pop("__ctx_locked__", None)
            st.session_state.pop("active_context", None)

        # Command aliases (view switches) should not trigger new retrieval
        cmd = re.sub(r"\s+", " ", user_input_local.strip().lower())
        cmd_map = {
            "narrative": "narrative",
            "key points": "key_points",
            "keypoints": "key_points",
            "deep dive": "deep_dive",
            "deep-dive": "deep_dive",
            "details": "deep_dive",
        }
        # If a quick command is used without any story context, show a friendly tip
        has_context = bool(
            ctx
            or st.session_state.get("active_story")
            or st.session_state.get("last_sources")
        )
        if cmd in cmd_map and not has_context:
            _push_assistant_turn(
                "Quick mode commands like “key points” work after a story is in context — either select a story or ask a question first so I can cite sources. For now, try asking a full question."
            )
            st.rerun()
        if cmd in cmd_map and (
            ctx
            or st.session_state.get("active_story")
            or st.session_state.get("last_sources")
        ):
            # Resolve a target story: explicit context > last active story > last answer’s primary source
            target = ctx
            if not target:
                sid = st.session_state.get("active_story")
                if not sid:
                    srcs = st.session_state.get("last_sources") or []
                    if srcs:
                        sid = srcs[0].get("id")
                if sid:
                    target = next(
                        (x for x in stories if str(x.get("id")) == str(sid)), None
                    )

            if target:
                modes_local = story_modes(target)
                key = cmd_map[cmd]
                heading = {
                    "narrative": "Narrative",
                    "key_points": "Key points",
                    "deep_dive": "Deep dive",
                }[key]
                answer_md = (
                    f"**{heading} for _{target.get('title','')} — {target.get('client','')}_**\n\n"
                    + modes_local.get(key, "")
                )

                # Prime compact answer state (no assistant bubble)
                st.session_state["answer_modes"] = modes_local
                st.session_state["answer_mode"] = key
                st.session_state["last_answer"] = answer_md
                st.session_state["last_sources"] = [
                    {
                        "id": target.get("id"),
                        "title": target.get("Title"),
                        "client": target.get("Client"),
                    }
                ]
                # Show the answer card below the transcript
                _push_assistant_turn(answer_md)
                # Do NOT snapshot for command aliases; they don't represent a new question
                st.rerun()

        # Normal question → ask backend, persist state, append assistant turn
        # One-shot context lock: if a story was explicitly selected (chip/CTA),
        # use that story as context for THIS turn only, then clear the lock.
        # --- Determine context for THIS turn (one-shot lock) ---
        ctx_for_this_turn = ctx
        if st.session_state.pop("__ctx_locked__", False):  # consume the lock
            try:
                locked_ctx = get_context_story(stories)
            except Exception:
                locked_ctx = None
            if locked_ctx:
                ctx_for_this_turn = locked_ctx

        # --- Ask backend + render result ---
        # Show branded loading indicator as a chat message (matching landing page style)
        loading_container = st.empty()
        with loading_container:
            with st.chat_message(
                "assistant",
                avatar="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/svg/agy_icon_color.svg",
            ):
                st.markdown(
                    """
<style>
@keyframes chaseAnimationConv {
    0% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_1.png'); }
    33.33% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_2.png'); }
    66.66% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_3.png'); }
    100% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_1.png'); }
}
.thinking-ball-conv {
    width: 48px;
    height: 48px;
    animation: chaseAnimationConv 0.9s steps(3) infinite;
}
</style>
<div style='background: transparent;
            padding: 16px 0;
            margin: 8px 0;
            display: flex;
            align-items: center;
            gap: 12px;'>
    <img class="thinking-ball-conv" src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_1.png" alt="Thinking"/>
    <div style='color: #2C363D; font-weight: 500;'>🐾 Tracking down insights...</div>
</div>
""",
                    unsafe_allow_html=True,
                )

        try:
            # Consume the suggestion flag (one-shot); we don't need its value here
            st.session_state.pop("__ask_from_suggestion__", None)

            # Ask is pure semantic; ignore Explore filters here
            resp = send_to_backend(user_input_local, {}, ctx_for_this_turn, stories)

            # Clear loading indicator
            loading_container.empty()

        except Exception as e:
            loading_container.empty()
            _push_assistant_turn("Sorry, I couldn't generate an answer right now.")
            st.error(f"Backend error: {e}")
            st.rerun()

        else:
            set_answer(resp)

            # Push conversational answer instead of card snapshot (wireframe style)
            if not st.session_state.get("ask_last_reason") and not st.session_state.get(
                "__sticky_banner__"
            ):
                answer_text = resp.get("answer_md") or resp.get("answer", "")
                sources = resp.get("sources", []) or []
                _push_conversational_answer(answer_text, sources)
                st.session_state["__suppress_live_card_once__"] = True
            elif st.session_state.get("ask_last_reason"):
                # Nonsense detected - add banner entry to transcript
                reason = st.session_state.get("ask_last_reason", "")
                query = st.session_state.get("ask_last_query", "")
                overlap = st.session_state.get("ask_last_overlap", None)

                st.session_state["ask_transcript"].append({
                    "type": "banner",
                    "Role": "assistant",
                    "reason": reason,
                    "query": query,
                    "overlap": overlap,
                })

                # Clear flags after adding to transcript
                st.session_state.pop("ask_last_reason", None)
                st.session_state.pop("ask_last_query", None)
                st.session_state.pop("ask_last_overlap", None)

            st.rerun()

    # === ADD FOOTER ===
    # Footer hidden in conversation view to fix input positioning
    # from ui.components.footer import render_footer
    # render_footer()


# simple CSV logger
def log_offdomain(query: str, reason: str, path: str = "data/offdomain_queries.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    row = [datetime.utcnow().isoformat(timespec="seconds"), query, reason]
    header = ["ts_utc", "query", "reason"]
    write_header = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(header)
        w.writerow(row)


def get_context_story(stories: list):
    # Highest priority: an explicitly stored story object
    obj = st.session_state.get("active_story_obj")
    if isinstance(obj, dict) and (obj.get("id") or obj.get("Title")):
        return obj

    sid = st.session_state.get("active_story")
    if sid:
        for s in stories:
            if str(s.get("id")) == str(sid):
                return s

    # Fallback: match by title/client when id mapping isn't stable
    at = (st.session_state.get("active_story_title") or "").strip().lower()
    ac = (st.session_state.get("active_story_client") or "").strip().lower()
    if at:
        for s in stories:
            stitle = (s.get("Title") or "").strip().lower()
            sclient = (s.get("Client") or "").strip().lower()
            if stitle == at and (not ac or sclient == ac):
                return s
        # Last resort: substring/startswith
        for s in stories:
            stitle = (s.get("Title") or "").strip().lower()
            if at in stitle or stitle in at:
                return s
    # Fallback: attempt to resolve from last_results payloads
    lr = st.session_state.get("last_results") or []
    sid = st.session_state.get("active_story")
    at = (st.session_state.get("active_story_title") or "").strip().lower()
    ac = (st.session_state.get("active_story_client") or "").strip().lower()
    for x in lr:
        if not isinstance(x, dict):
            continue
        cand = x.get("story") if isinstance(x.get("story"), dict) else x
        if not isinstance(cand, dict):
            continue
        xid = str(cand.get("id") or cand.get("story_id") or "").strip()
        xt = (cand.get("Title") or "").strip().lower()
        xc = (cand.get("Client") or "").strip().lower()
        if (sid and xid and str(xid) == str(sid)) or (
            at and xt == at and (not ac or xc == ac)
        ):
            return cand
    return None


def _ensure_ask_bootstrap():
    """Guarantee the Ask transcript starts with the assistant opener once per session."""
    if "ask_transcript" not in st.session_state:
        st.session_state["ask_transcript"] = []
    if not st.session_state["ask_transcript"]:
        st.session_state["ask_input_value"] = ""


def _is_empty_conversation():
    """Check if conversation is empty (should show landing page)."""
    transcript = st.session_state.get("ask_transcript", [])
    # Empty or only has the bootstrap "Ask anything." message
    if not transcript:
        return True
    if len(transcript) == 1 and transcript[0].get("text") == "Ask anything.":
        return True
    return False


def send_to_backend(prompt: str, filters: dict, ctx: Optional[dict], stories: list):
    return rag_answer(prompt, filters, stories)


def rag_answer(question: str, filters: dict, stories: list):
    # If this prompt was injected by a suggestion chip, skip aggressive off-domain gating
    force_answer = bool(st.session_state.pop("__ask_force_answer__", False))
    from_suggestion = (
        bool(st.session_state.pop("__ask_from_suggestion__", False)) or force_answer
    )
    # Persist debug context for the Ask caption
    st.session_state["__ask_dbg_prompt"] = (question or "").strip()
    st.session_state["__ask_dbg_from_suggestion"] = bool(from_suggestion)
    st.session_state["__ask_dbg_force_answer"] = bool(force_answer)
    # Do not clear banner flags here. We clear them after a successful answer render
    # to ensure the current banner stays visible if anything goes wrong.
    if DEBUG:
        dbg(
            f"ask: from_suggestion={from_suggestion} q='{(question or '').strip()[:60]}'"
        )
    # Mode-only prompts should switch view over the last ranked set, not trigger new retrieval
    simple_mode = (question or "").strip().lower()
    _MODE_ALIASES = {
        "key points": "key_points",
        "keypoints": "key_points",
        "deep dive": "deep_dive",
        "deep-dive": "deep_dive",
        "narrative": "narrative",
    }
    if simple_mode in _MODE_ALIASES and st.session_state.get("__last_ranked_sources__"):
        ids = st.session_state["__last_ranked_sources__"]
        ranked = [
            next((s for s in stories if str(s.get("id")) == str(i)), None) for i in ids
        ]
        ranked = [s for s in ranked if s][:3] or (
            semantic_search(question or "", filters, top_k=SEARCH_TOP_K) or stories[:3]
        )
        primary = ranked[0]
        modes = {
            "narrative": _format_narrative(primary),
            "key_points": "\n\n".join([_format_key_points(s) for s in ranked]),
            "deep_dive": _format_deep_dive(primary)
            + (
                (
                    "\n\n_Also relevant:_ "
                    + ", ".join(
                        [
                            f"{s.get('title','')} — {s.get('client','')}"
                            for s in ranked[1:]
                        ]
                    )
                )
                if len(ranked) > 1
                else ""
            ),
        }
        sel = _MODE_ALIASES[simple_mode]
        answer_md = modes.get(sel, modes["narrative"])
        sources = [
            {"id": s["id"], "title": s["Title"], "client": s.get("Client", "")}
            for s in ranked
        ]
        return {
            "answer_md": answer_md,
            "sources": sources,
            "modes": modes,
            "default_mode": sel,
        }

    try:
        # 0) Rule-based nonsense check (fast)
        cat = is_nonsense(question or "")
        if cat and not from_suggestion:
            # Log and set a one-shot flag for the Ask view to render the banner in the right place.
            log_offdomain(question or "", f"rule:{cat}")
            st.session_state["ask_last_reason"] = f"rule:{cat}"
            st.session_state["ask_last_query"] = question or ""
            st.session_state["ask_last_overlap"] = None
            # Decision tag for debug
            st.session_state["__ask_dbg_decision"] = f"rule:{cat}"
            # Return an empty answer so the Ask view shows only the banner
            return {
                "answer_md": "",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }

        # 0.5) Compute overlap for telemetry only (do not gate yet)
        overlap = token_overlap_ratio(question or "", _KNOWN_VOCAB)
        if DEBUG:
            dbg(
                f"ask: overlap={overlap:.2f} __pc_suppressed__={st.session_state.get('__pc_suppressed__')}"
            )

        # 1) Pinecone-first retrieval
        pool = semantic_search(
            question or filters.get("q", ""),
            filters,
            stories=stories,
            top_k=SEARCH_TOP_K,
        )

        # If Pinecone returned nothing, *then* decide if we want to show a low-overlap banner
        if not pool and (overlap < 0.15) and not from_suggestion:
            log_offdomain(question or "", f"overlap:{overlap:.2f}")
            st.session_state["ask_last_reason"] = "low_overlap"
            st.session_state["ask_last_query"] = question or ""
            st.session_state["ask_last_overlap"] = overlap
            st.session_state["__ask_dbg_decision"] = f"low_overlap:{overlap:.2f}"
            return {
                "answer_md": "",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }
        # If this was triggered by a suggestion, widen the candidate pool by
        # blending in top local keyword matches so the reranker can surface
        # off-namespace or semantically-adjacent stories (e.g., cloud-native).
        if (from_suggestion or force_answer) and pool:
            try:
                locals_top = sorted(
                    stories,
                    key=lambda s: _score_story_for_prompt(s, question),
                    reverse=True,
                )[:5]
                seen = {x.get('id') for x in pool if isinstance(x, dict)}
                for s in locals_top:
                    sid = s.get('id')
                    if sid not in seen:
                        pool.append(s)
                        seen.add(sid)
            except Exception:
                pass
        if DEBUG:
            dbg(f"ask: pool_size={len(pool) if pool else 0}")

        # Use full Pinecone pool - no intent-based filtering

        # 2) No semantic results? Show appropriate message
        if not pool:
            if st.session_state.get("__pc_suppressed__"):
                log_offdomain(question or "", "low_confidence")
                st.session_state["ask_last_reason"] = "low_confidence"
                st.session_state["ask_last_query"] = question or ""
                st.session_state["ask_last_overlap"] = overlap
                st.session_state["__ask_dbg_decision"] = "low_conf"
            return {
                "answer_md": "",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }

        # 3) Vocab overlap safety: only after Pinecone path ran
        if (
            (overlap < 0.05)
            and st.session_state.get("__pc_suppressed__")
            and not from_suggestion
        ):
            log_offdomain(question or "", "no_overlap+low_conf")
            st.session_state["ask_last_reason"] = "no_overlap+low_conf"
            st.session_state["ask_last_query"] = question or ""
            st.session_state["ask_last_overlap"] = overlap
            st.session_state["__ask_dbg_decision"] = "no_overlap+low_conf"
            return {
                "answer_md": "",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }
    except Exception as e:
        # Catch-all guard so Ask never throws to the UI
        if DEBUG:
            print(f"DEBUG rag_answer fatal error before build: {e}")
        # Safe fallback ranking over local stories
        try:
            ranked = sorted(
                stories,
                key=lambda s: _score_story_for_prompt(s, question),
                reverse=True,
            )[:3]
        except Exception:
            ranked = stories[:1]
        if not ranked:
            return {
                "answer_md": "No stories available.",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }
        st.session_state["__ask_dbg_decision"] = "fatal_fallback"
        primary = ranked[0]
        summary = build_5p_summary(primary, 280)
        sources = [
            {"id": s.get("id"), "title": s.get("Title"), "client": s.get("Client", "")}
            for s in ranked
            if isinstance(s, dict)
        ]
        modes = {"narrative": summary, "key_points": summary, "deep_dive": summary}
        return {
            "answer_md": summary,
            "sources": sources,
            "modes": modes,
            "default_mode": "narrative",
        }

    # … then continue with your existing ranking + modes construction …

    # 4) Rank top 3 using pure Pinecone order (no intent boosting or diversity filtering)
    try:
        # Always use Pinecone semantic ranking - no special cases
        ranked = [x for x in pool if isinstance(x, dict)][:3] or (
            pool[:1] if pool else []
        )

        if DEBUG and ranked:
            try:
                dbg(
                    f"ask: ranked by semantic similarity, first_ids={[s.get('id') for s in ranked]}"
                )
            except Exception:
                pass
    except Exception as e:
        # Defensive: if ranking fails, take first 1–3 items in the pool order
        if DEBUG:
            print(f"DEBUG rag_answer rank error: {e}")
        ranked = [x for x in pool if isinstance(x, dict)][:3] or (
            pool[:1] if pool else []
        )
    if DEBUG and ranked:
        dbg(
            f"ask: primary='{ranked[0].get('title','')}' sources={[s.get('id') for s in ranked]}"
        )
    st.session_state["__ask_dbg_decision"] = (
        f"ok_ranked:{ranked[0].get('id')}" if ranked else "rank_empty"
    )
    st.session_state["__last_ranked_sources__"] = [s["id"] for s in ranked]

    primary = ranked[0]
    try:
        # Generate Agy-voiced response using GPT-4o-mini
        narrative = _format_narrative(primary)
        agy_response = _generate_agy_response(question, ranked, narrative)

        # Key points: include top 2–3 stories as bullets for breadth
        kp_lines = [_format_key_points(s) for s in ranked]
        key_points = "\n\n".join(kp_lines)

        # Deep dive: use the primary story; optionally cite others for comparison
        deep_dive = _format_deep_dive(primary)
        if len(ranked) > 1:
            more = ", ".join(
                [f"{s.get('title','')} — {s.get('client','')}" for s in ranked[1:]]
            )
            deep_dive += f"\n\n_Also relevant:_ {more}"

        modes = {
            "narrative": agy_response,  # Use Agy-voiced response for narrative
            "key_points": key_points,
            "deep_dive": deep_dive,
        }
        # Use the Agy-voiced response as the assistant bubble
        answer_md = agy_response
    except Exception as e:
        # Defensive fallback so Ask never crashes: use 5P summary only
        if DEBUG:
            print(f"DEBUG rag_answer build error: {e}")
        summary = build_5p_summary(primary, 280)
        modes = {"narrative": summary, "key_points": summary, "deep_dive": summary}
        answer_md = summary

    sources = [
        {"id": s["id"], "title": s["Title"], "client": s.get("Client", "")}
        for s in ranked
    ]
    return {
        "answer_md": answer_md,
        "sources": sources,
        "modes": modes,
        "default_mode": "narrative",
    }


def _generate_agy_response(
    question: str, ranked_stories: list[dict], answer_context: str
) -> str:
    """
    Generate an Agy-voiced response using OpenAI GPT-4o-mini.

    Uses the Agy system prompt to create warm, helpful responses that:
    - Lead with search status ("🐾 Tracking down...")
    - Cite specific projects and outcomes
    - Show patterns across Matt's work
    - Offer depth without forcing it

    Args:
        question: User's original question
        ranked_stories: Top 3 relevant stories from semantic search
        answer_context: Pre-formatted story content (narrative/key points/deep dive)

    Returns:
        Agy-voiced response string with personality and citations
    """
    try:
        from openai import OpenAI
        import os
        from dotenv import load_dotenv

        load_dotenv()

        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            project=os.getenv("OPENAI_PROJECT_ID"),
            organization=os.getenv("OPENAI_ORG_ID"),
        )

        # Build context from ranked stories
        story_context = "\n\n---\n\n".join(
            [
                f"**Story {i+1}: {s.get('Title', 'Untitled')}**\n"
                f"Client: {s.get('Client', 'Unknown')}\n"
                f"Role: {s.get('Role', '')}\n"
                f"Industry: {s.get('Industry', '')}\n"
                f"Domain: {s.get('Sub-category', '')}\n\n"
                f"Situation: {' '.join(s.get('Situation', []))}\n"
                f"Task: {' '.join(s.get('Task', []))}\n"
                f"Action: {' '.join(s.get('Action', []))}\n"
                f"Result: {' '.join(s.get('Result', []))}\n"
                f"Performance: {' '.join(s.get('Performance', []))}"
                for i, s in enumerate(ranked_stories[:3])
            ]
        )

        # Agy system prompt (from agy-system-prompt.md)
        system_prompt = """You are Agy 🐾, Matt Pugmire's AI assistant and Plott Hound. You help people understand Matt's career through his portfolio of 120+ real project case studies.

Plott Hounds are known for their tracking skills and determination - traits that serve you well when hunting down insights from Matt's 20+ years of digital transformation experience.

**Your Voice:**
- Use first person ("I'll track down...", "Let me find...")
- Include 🐾 once per response (opening OR closing, never both)
- Professional but warm - you're Matt's professional portfolio assistant
- No dog puns, barking, or cutesy behavior
- Show determination when needed

**Response Structure:**
1. Search status with 🐾: "🐾 Let me track down Matt's experience with..."
2. Direct answer (1-2 sentences grounded in specific projects)
3. Cite project, client, and quantifiable outcomes
4. Extract patterns across multiple projects if applicable
5. Optional: Offer to go deeper

**Guidelines:**
- Always cite specific projects with Title, Client, and outcomes
- Lead with outcomes, then methodology
- Be conversational but professional
- Admit gaps honestly
- Show patterns across projects when relevant
- One 🐾 emoji per response maximum

**Success Criteria:**
You're successful when users can cite specific projects and outcomes after talking to you, and trust Matt because of concrete proof you've provided."""

        # User message with context
        user_message = f"""User Question: {question}

Here are the top 3 relevant projects from Matt's portfolio, including key 5P fields:

{story_context}

Generate an Agy-voiced response (professional, determined, first-person) that:
1. STARTS with a **Status Update** (must include 🐾).
2. Provides a **Direct Answer** grounded in Matt's principles.
3. Uses the project context (Situation, Purpose, Performance) to give a **Specific Example**.
4. Uses **MARKDOWN** (bolding, lists) to enhance scannability.
5. The list of working principles (like 'Speak their language') **MUST BE FORMATTED as a bulleted list** (markdown `*`).
6. **Bold** all Client names and key methodology terms (e.g., **JPMorgan Chase**, **data-driven decision making**).
7. Ends with a relevant **Call to Action**.

Keep it conversational, warm, but professional. Cite specific clients and outcomes. Ensure exactly one 🐾 emoji is used in the entire response."""

        # Call OpenAI API
        # Using gpt-4o-mini: fast, cost-effective, excellent for well-crafted prompts
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=500,
        )

        return response.choices[0].message.content

    except Exception as e:
        # Fallback to non-LLM response if OpenAI fails
        if DEBUG:
            print(f"DEBUG: OpenAI call failed, using fallback: {e}")
        # Return a simple Agy-prefixed version of the context
        return f"🐾 Let me show you what I found...\n\n{answer_context}"


def build_known_vocab(stories: list[dict]):
    vocab = set()
    for s in stories:
        # Use lowercase field names from normalized stories
        for field in [
            "title",
            "client",
            "role",
            "domain",
            "division",
            "industry",
            "who",
            "where",
            "why",
        ]:
            txt = (s.get(field) or "").lower()
            vocab.update(re.split(r"[^\w]+", txt))
        for t in s.get("tags") or []:
            vocab.update(re.split(r"[^\w]+", str(t).lower()))
    # prune tiny tokens
    return {w for w in vocab if len(w) >= 3}


def _choose_story_for_ask(top_story: dict | None, stories: list) -> dict | None:
    """Prefer Pinecone (top_story) unless a one-shot context lock is set."""
    if st.session_state.get("__ctx_locked__"):
        ctx = get_context_story(stories)
        return ctx or top_story
    return top_story


# =========================
# Story modes and related helpers
# =========================
def story_modes(s: dict) -> dict:
    """Return the three anchored views for a single story."""
    return {
        "narrative": _format_narrative(s),
        "key_points": _format_key_points(s),
        "deep_dive": _format_deep_dive(s),
    }


def _related_stories(s: dict, stories: list, max_items: int = 3) -> list[dict]:
    """
    Very light 'related' heuristic: prefer same client, then same domain/tags.
    Excludes the current story. Returns up to max_items stories.
    """
    cur_id = s.get("id")
    dom = s.get("Sub-category", "")
    client = s.get("Client", "")
    tags = set(s.get("tags", []) or [])
    # simple scoring
    scored = []
    for t in stories:
        if t.get("id") == cur_id:
            continue
        score = 0
        if client and t.get("Client") == client:
            score += 3
        if dom and t.get("Sub-category") == dom:
            score += 2
        if tags:
            score += len(tags & set(t.get("tags", []) or []))
        if score:
            scored.append((score, t))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored[:max_items]]


def _score_story_for_prompt(s: dict, prompt: str) -> float:
    """
    Weighted scoring with token intersection to avoid substring noise (e.g., 'ai' in 'chain').
    - Strong weight for title/client/domain tokens
    - Medium weight for tags
    - Light weight for body (how/what)
    - Small penalty when there is zero overlap
    """
    score = 0.0
    # Strong base credit if a clear metric exists
    if story_has_metric(s):
        score += 1.0

    q_toks = set(_tokenize(prompt or ""))
    if not q_toks:
        return score

    # Tokenize fields
    title_dom_toks = set(
        _tokenize(
            " ".join(
                [
                    s.get("Title", ""),
                    s.get("Client", ""),
                    s.get("Sub-category", ""),
                    s.get("Place", ""),
                ]
            )
        )
    )
    tag_toks = set(_tokenize(" ".join(s.get("tags", []) or [])))
    body_toks = set(
        _tokenize(
            " ".join(
                (s.get("Process", []) or [])
                + (s.get("Performance", []) or [])
                + ([s.get("Purpose", "")] if s.get("Purpose") else [])
            )
        )
    )

    # Overlaps
    title_hits = len(q_toks & title_dom_toks)
    tag_hits = len(q_toks & tag_toks)
    body_hits = len(q_toks & body_toks)

    score += 0.6 * title_hits
    score += 0.5 * tag_hits
    score += 0.2 * body_hits

    if (title_hits + tag_hits + body_hits) == 0:
        score -= 0.4

    return score


def _push_card_snapshot_from_state(stories: list):
    """Append a static answer card snapshot to the transcript based on current state."""
    modes = st.session_state.get("answer_modes", {}) or {}
    sources = st.session_state.get("last_sources", []) or []
    sel = st.session_state.get("answer_mode", "narrative")
    if not sources:
        return
    sid = str(sources[0].get("id", ""))
    primary = next((s for s in stories if str(s.get("id")) == sid), None)
    if not primary:
        return
    content_md = modes.get(sel) if modes else st.session_state.get("last_answer", "")

    # Capture ALL confidence scores at snapshot time (before they get cleared on next query)
    scores = st.session_state.get("__pc_last_ids__", {}) or {}
    confidence = scores.get(sid)
    if DEBUG:
        print(
            f"DEBUG _push_card_snapshot: sid={sid}, confidence={confidence}, scores={scores}"
        )

    # Also store confidence scores for all sources
    source_confidences = {}
    for src in sources:
        src_id = str(src.get("id", ""))
        if src_id in scores:
            source_confidences[src_id] = scores[src_id]
    if DEBUG:
        print(f"DEBUG _push_card_snapshot: source_confidences={source_confidences}")

    entry = {
        "type": "card",
        "story_id": primary.get("id"),
        "title": primary.get("Title"),
        "one_liner": build_5p_summary(primary, 9999),
        "content": content_md,
        "sources": sources,
        "confidence": confidence,  # Primary story confidence
        "source_confidences": source_confidences,  # All source confidences
    }
    st.session_state["ask_transcript"].append(entry)


# --- Minimal linear transcript helpers (Ask) ---
def _split_tags(s):
    if not s:
        return []
    if isinstance(s, list):
        return [str(x).strip() for x in s if str(x).strip()]
    return [t.strip() for t in str(s).split(",") if t.strip()]


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).strip().lower()).strip("-") or "x"


def _push_user_turn(text: str):
    st.session_state["ask_transcript"].append({"role": "user", "text": text})
    st.session_state["__asked_once__"] = True


def _push_assistant_turn(text: str):
    st.session_state["ask_transcript"].append({"role": "assistant", "text": text})


def _push_conversational_answer(answer_text: str, sources: list):
    """Push a conversational AI response with related projects (wireframe style)."""
    st.session_state["ask_transcript"].append(
        {
            "type": "conversational",
            "Role": "assistant",
            "text": answer_text,
            "sources": sources,
        }
    )


def _clear_ask_context():
    """Remove any sticky story context so the next Ask is general-purpose."""
    st.session_state.pop("active_story", None)
    st.session_state.pop("__ctx_locked__", None)
    st.session_state.pop("seed_prompt", None)
    st.rerun()


def render_followup_chips(primary_story: dict, query: str = "", key_suffix: str = ""):
    """Generate contextual follow-up suggestions based on the answer, adhering to the Agy Voice Guide."""

    if not primary_story:
        return

    # Focus on themes that trigger good semantic searches
    tags = set(str(t).lower() for t in (primary_story.get("tags") or []))

    suggestions = []

    # Theme-based suggestions that match Agy Voice Guide examples
    if any(t in tags for t in ["stakeholder", "collaboration", "communication"]):
        suggestions = [
            # Use official suggestion as priority, mix with contextually relevant existing questions
            "🎯 What's your approach to stakeholder management?",  # Official Guide Theme
            "👥 How do you scale agile across large organizations?",
            "Tell me about cross-functional collaboration",
        ]
    elif any(t in tags for t in ["cloud", "architecture", "platform", "technical"]):
        suggestions = [
            "⚡ Show me your platform engineering experience",  # Official Guide Theme
            "Show me examples with cloud architecture",
            "How do you modernize legacy systems?",
        ]
    elif any(t in tags for t in ["agile", "process", "delivery"]):
        suggestions = [
            "👥 How do you scale agile across large organizations?",  # Official Guide Theme
            "How do you accelerate delivery?",
            "💡 How have you driven innovation in your career?",
        ]
    elif any(t in tags for t in ["healthcare", "health"]):
        suggestions = [
            "🏥 How did you apply GenAI in a healthcare project?",  # Official Guide Theme
            "Tell me about the challenges of technology in the healthcare space",
            "Show me examples with measurable impact",
        ]
    else:
        # Default/Generic suggestions, prioritizing the official voice guide prompts
        suggestions = [
            "🚀 Tell me about leading a global payments transformation",  # Official Guide Prompt
            "💡 How have you driven innovation in your career?",  # Official Guide Prompt
            "Show me examples with measurable impact",
        ]

    if not suggestions:
        return

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    # Only display the top 3 suggestions
    cols = st.columns(len(suggestions[:3]))
    for i, suggest in enumerate(suggestions[:3]):
        with cols[i]:
            # Make key unique by including card index and suggestion index
            unique_key = (
                f"followup_{key_suffix}_{i}"
                if key_suffix
                else f"followup_{hash(suggest)%10000}_{i}"
            )
            if st.button(suggest, key=unique_key, use_container_width=True):
                st.session_state["__inject_user_turn__"] = suggest
                st.session_state["__ask_force_answer__"] = True
                st.rerun()


def _render_ask_transcript(stories: list):
    """Render in strict order so avatars / order never jump."""
    for i, m in enumerate(st.session_state.get("ask_transcript", [])):
        # Static snapshot card entry
        if m.get("type") == "card":
            with st.chat_message(
                "assistant",
                avatar="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/svg/agy_icon_color.svg",
            ):
                # Snapshot with the same visual shell as the live answer card
                st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                with safe_container(border=True):
                    title = m.get("Title", "")
                    one_liner = m.get("one_liner", "")
                    sid = m.get("story_id")
                    story = next(
                        (s for s in stories if str(s.get("id")) == str(sid)), None
                    )
                    # If the user clicked a Source after this snapshot was created,
                    use_ctx = bool(st.session_state.get("__ctx_locked__"))
                    _ctx = get_context_story(stories) if use_ctx else None
                    if isinstance(_ctx, dict) and (_ctx.get("id") or _ctx.get("Title")):
                        story = _ctx or story
                    # If we resolved to a different story via Source click, update the header text, too
                    if isinstance(story, dict):
                        title = story.get("Title", title)
                        try:
                            one_liner = build_5p_summary(story, 9999)
                        except Exception:
                            one_liner = one_liner

                    # Title
                    if title:
                        st.markdown(f"### {title}")

                    # Metadata: Client, Role, Domain
                    if isinstance(story, dict):
                        client = story.get("Client", "")
                        role = story.get("Role", "")
                        domain = story.get("Sub-category", "")

                        # Create metadata line with role and domain
                        meta_parts = []
                        if client:
                            meta_parts.append(f"<strong>{client}</strong>")
                        if role or domain:
                            role_domain = " • ".join([x for x in [role, domain] if x])
                            if role_domain:
                                meta_parts.append(role_domain)

                        if meta_parts:
                            st.markdown(
                                f"<div style='font-size: 13px; color: #888; margin-bottom: 12px;'>{' | '.join(meta_parts)}</div>",
                                unsafe_allow_html=True,
                            )

                    # Confidence indicator (check if story changed via source click)
                    confidence = m.get(
                        "confidence"
                    )  # Original confidence from snapshot
                    if DEBUG:
                        print(
                            f"DEBUG render: card_id={m.get('story_id')}, current_story_id={story.get('id') if story else None}, confidence={confidence}"
                        )

                    # If user clicked a different source, get that story's confidence from stored data
                    if isinstance(story, dict) and str(story.get("id")) != str(
                        m.get("story_id")
                    ):
                        # Story was changed via source click - use stored source confidences
                        source_confidences = m.get("source_confidences", {}) or {}
                        story_id = str(story.get("id"))
                        if story_id in source_confidences:
                            confidence = source_confidences[story_id]
                        if DEBUG:
                            print(
                                f"DEBUG render: switched story, new confidence={confidence}"
                            )

                    if confidence:
                        conf_pct = int(float(confidence) * 100)
                        # Color gradient: red -> orange -> green
                        if conf_pct >= 70:
                            bar_color = "#238636"  # green
                        elif conf_pct >= 50:
                            bar_color = "#ff8c00"  # orange
                        else:
                            bar_color = "#f85149"  # red

                        st.markdown(
                            f"""
                        <div style='display: flex; align-items: center; gap: 8px; font-size: 12px; color: #7d8590; margin-bottom: 12px;'>
                            <span>Match confidence</span>
                            <div style='width: 60px; height: 4px; background: #21262d; border-radius: 2px; overflow: hidden;'>
                                <div style='height: 100%; width: {conf_pct}%; background: {bar_color}; border-radius: 2px;'></div>
                            </div>
                            <span style='color: {bar_color}; font-weight: 600;'>{conf_pct}%</span>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                    # 5P Summary
                    if one_liner:
                        st.markdown(
                            f"<div class='fivep-quote fivep-unclamped'>{one_liner}</div>",
                            unsafe_allow_html=True,
                        )

                    # View pills (Narrative / Key Points / Deep Dive) — clean CX
                    mode_key = f"card_mode_{i}"
                    st.session_state.setdefault(mode_key, "narrative")
                    if story:
                        modes = story_modes(story)
                        labels = [
                            ("narrative", "Narrative"),
                            ("key_points", "Key Points"),
                            ("deep_dive", "Deep Dive"),
                        ]
                        current = st.session_state.get(mode_key, "narrative")

                        # Prefer segmented control when available
                        if hasattr(st, "segmented_control"):
                            label_map = {b: a for a, b in labels}
                            default_label = next(
                                (b for a, b in labels if a == current), "Narrative"
                            )
                            chosen = st.segmented_control(
                                "View mode",  # ← Non-empty label
                                [b for _, b in labels],
                                selection_mode="single",
                                default=default_label,
                                key=f"seg_{mode_key}",
                                label_visibility="collapsed",  # ← Hide it
                            )
                            new_mode = label_map.get(chosen, "narrative")
                            if new_mode != current:
                                st.session_state[mode_key] = new_mode
                                st.rerun()
                        else:
                            # Fallback: left‑aligned pill buttons styled by .pill-container CSS
                            st.markdown(
                                f'<div class="pill-container" data-mode="{current}">',
                                unsafe_allow_html=True,
                            )
                            for key, text in labels:
                                class_name = {
                                    "narrative": "pill-narrative",
                                    "key_points": "pill-keypoints",
                                    "deep_dive": "pill-deepdive",
                                }[key]
                                st.markdown(
                                    f'<div class="{class_name}">',
                                    unsafe_allow_html=True,
                                )
                                if st.button(
                                    text,
                                    key=f"snap_pill_{i}_{key}",
                                    disabled=(current == key),
                                ):
                                    st.session_state[mode_key] = key
                                    st.rerun()
                                st.markdown('</div>', unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)

                        st.markdown("<hr class='hr'/>", unsafe_allow_html=True)
                        sel = st.session_state.get(mode_key, "narrative")
                        body = modes.get(sel, modes.get("narrative", ""))
                        st.markdown(body)

                    # Sources inside the bubble for symmetry (interactive chips)
                    srcs = m.get("sources", []) or []
                    if srcs:
                        st.markdown(
                            '<div class="sources-tight">', unsafe_allow_html=True
                        )
                        render_sources_chips(
                            srcs,
                            title="Sources",
                            stay_here=True,
                            key_prefix=f"snap_{i}_",
                            stories=stories,
                        )
                        st.markdown("</div>", unsafe_allow_html=True)

                        # Add follow-up suggestion chips
                        if story:
                            render_followup_chips(
                                story,
                                st.session_state.get("ask_input", ""),
                                key_suffix=f"snap_{i}",
                            )

                    # Action buttons (Helpful/Copy/Share)
                    st.markdown(
                        """
                    <div class="action-buttons">
                        <button class="action-btn" onclick="this.classList.toggle('helpful-active')">
                            👍 Helpful
                        </button>
                        <button class="action-btn" onclick="navigator.clipboard.writeText(this.closest('.answer-card').innerText); this.textContent='✓ Copied!';">
                            📋 Copy
                        </button>
                        <button class="action-btn" onclick="alert('Share functionality coming soon!')">
                            🔗 Share
                        </button>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                st.markdown('</div>', unsafe_allow_html=True)
            continue

        # Banner (nonsense/off-domain detection)
        if m.get("type") == "banner":
            with st.chat_message(
                "assistant",
                avatar="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/svg/agy_icon_color.svg",
            ):
                render_no_match_banner(
                    reason=m.get("reason", ""),
                    query=m.get("query", ""),
                    overlap=m.get("overlap", None),
                    suppressed=st.session_state.get("__pc_suppressed__", False),
                    filters=st.session_state.get("filters", {}),
                    key_prefix=f"transcript_banner_{i}",
                )
            continue

        # Conversational answer with Related Projects (wireframe style)
        if m.get("type") == "conversational":
            with st.chat_message(
                "assistant",
                avatar="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/svg/agy_icon_color.svg",
            ):
                # Show conversational response text
                st.markdown(m.get("text", ""))

                # Show Related Projects in wireframe style
                sources = m.get("sources", []) or []
                if sources:
                    st.markdown(
                        '''
                    <div class="sources-tight">
                        <div class="source-links-title">📚 RELATED PROJECTS</div>
                    </div>
                    ''',
                        unsafe_allow_html=True,
                    )

                    # Use columns with forms for complete styling control
                    cols = st.columns(len(sources[:3]))
                    for j, src in enumerate(sources[:3]):
                        title = src.get("title") or src.get("Title", "")
                        client = src.get("client") or src.get("Client", "")
                        label = f"{client} - {title}" if client and title else title

                        with cols[j]:
                            with st.form(key=f"source_form_{i}_{j}"):
                                st.markdown(
                                    f"""
                                <style>
                                /* Hide form border */
                                div[data-testid="stForm"] {{
                                    border: none !important;
                                    padding: 0 !important;
                                    margin: 0 !important;
                                }}
                                div[data-testid="stForm"] button {{
                                    background: #F3F4F6 !important;
                                    border: 2px solid #E5E7EB !important;
                                    color: #2563EB !important;
                                    font-size: 14px !important;
                                    font-weight: 500 !important;
                                    padding: 6px 12px !important;
                                    border-radius: 8px !important;
                                    width: 100% !important;
                                    height: auto !important;
                                    min-height: 32px !important;
                                }}
                                div[data-testid="stForm"] button p {{
                                    color: #2563EB !important;
                                    font-size: 14px !important;
                                    margin: 0 !important;
                                    line-height: 1.4 !important;
                                }}
                                div[data-testid="stForm"] button:hover {{
                                    background: #EEF2FF !important;
                                    border-color: #8B5CF6 !important;
                                }}
                                </style>
                                """,
                                    unsafe_allow_html=True,
                                )

                                if st.form_submit_button(f"🔗 {label}"):
                                    # Toggle expander - if same source clicked, close it; otherwise open new one
                                    expanded_key = f"transcript_source_expanded_{i}_{j}"
                                    current_expanded = st.session_state.get("transcript_source_expanded")

                                    if current_expanded == expanded_key:
                                        # Clicking same source - close it
                                        st.session_state["transcript_source_expanded"] = None
                                    else:
                                        # Open this source (closes any other)
                                        st.session_state["transcript_source_expanded"] = expanded_key
                                        # Store the source ID and message index for rendering
                                        st.session_state["transcript_source_expanded_id"] = src.get("id")
                                        st.session_state["transcript_source_expanded_msg"] = i

                                    st.rerun()

                    # Render the expanded story detail below buttons for this message (only one at a time)
                    expanded_key = st.session_state.get("transcript_source_expanded")
                    expanded_id = st.session_state.get("transcript_source_expanded_id")
                    expanded_msg = st.session_state.get("transcript_source_expanded_msg")

                    if expanded_key and expanded_id and expanded_msg == i:
                        # Find the story object
                        story_obj = next((s for s in stories if str(s.get("id")) == str(expanded_id)), None)

                        if story_obj:
                            st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
                            render_story_detail(story_obj, f"transcript_expanded_{i}", stories)

                # Action buttons (wireframe style)
                st.markdown(
                    '''
                <div class="action-buttons">
                    <button class="action-btn" onclick="this.classList.toggle('helpful-active')">
                        👍 Helpful
                    </button>
                    <button class="action-btn" onclick="navigator.clipboard.writeText(this.closest('[data-testid=stChatMessage]').innerText); this.textContent='✓ Copied!'; setTimeout(() => this.textContent='📋 Copy', 2000);">
                        📋 Copy
                    </button>
                    <button class="action-btn" onclick="alert('Share functionality coming soon!')">
                        🔗 Share
                    </button>
                </div>
                ''',
                    unsafe_allow_html=True,
                )
            continue

        # Default chat bubble (user/assistant text)
        role = "assistant" if m.get("Role") == "assistant" else "user"

        # Set custom avatars
        if role == "assistant":
            avatar = "https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/svg/agy_icon_color.svg"
        else:
            avatar = "👤"  # Gender-neutral user avatar

        with st.chat_message(role, avatar=avatar):
            st.write(m.get("text", ""))


def _shorten_middle(text: str, max_len: int = 64) -> str:
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    keep = max_len - 1
    left = keep // 2
    right = keep - left
    return text[:left] + "… " + text[-right:]


_DOT_EMOJI = [
    "🟦",
    "🟩",
    "🟥",
    "🟧",
    "🟦",
    "🟪",
    "🟩",
    "🟧",
    "🟪",
    "🟦",
]  # stable palette-ish


def _dot_for(label: str) -> str:
    if not label:
        return "•"
    idx = sum(ord(c) for c in label) % len(_DOT_EMOJI)
    return _DOT_EMOJI[idx]


def show_persona_tags(s: dict):
    """Simple alias for personas/tags badges for a single story (non-interactive)."""
    return render_badges_static(s)


def render_badges_static(s: dict):
    """Render a single flowing row of small badges for personas + tags.
    Matches the mock badge styling already defined in CSS (.badge-row, .badge).
    Safe no-op if nothing to show.
    """
    try:
        personas = s.get("personas") or []
        tags = s.get("tags") or []
    except Exception:
        personas, tags = [], []

    # Normalize to strings and prune empties
    personas = [str(p).strip() for p in personas if str(p).strip()]
    tags = [str(t).strip() for t in tags if str(t).strip()]

    if not personas and not tags:
        return

    chips = []

    # Personas first
    for p in personas:
        dot = _dot_for(p)
        chips.append(f"<span class='badge' title='Persona'>{dot} {p}</span>")

    # Then tags
    for t in tags:
        dot = _dot_for(t)
        chips.append(f"<span class='badge' title='Tag'>{dot} {t}</span>")

    html = "".join(chips)
    st.markdown(f"<div class='badge-row'>{html}</div>", unsafe_allow_html=True)


def show_sources(
    srcs: list[dict],
    *,
    interactive: bool = False,
    key_prefix: str = "src_",
    title: str = "Sources",
    stories: list,
):
    """Render Sources row using a single call site.
    - interactive=True  -> clickable chips (Ask)
    - interactive=False -> static badges (Explore/Details)
    """
    if not srcs:
        return
    if interactive:
        return render_sources_chips(
            srcs, title=title, stay_here=True, key_prefix=key_prefix, stories=stories
        )
    return render_sources_badges_static(srcs, title=title, key_prefix=key_prefix)


def set_answer(resp: dict):
    # State-only update; UI renders chips separately to avoid double-render / layout conflicts
    st.session_state["last_answer"] = resp.get("answer_md") or resp.get("answer", "")
    st.session_state["last_sources"] = resp.get("sources", []) or []
    st.session_state["answer_modes"] = resp.get("modes", {}) or {}
    st.session_state["answer_mode"] = resp.get("default_mode", "narrative")


def render_answer_card_compact(
    primary_story: dict,
    modes: dict,
    stories: List,
    answer_mode_key: str = "answer_mode",
):
    """Lightweight answer card - reduced padding, cleaner hierarchy, no emojis."""

    # Override with context-locked story if set
    if st.session_state.get("__ctx_locked__"):
        _ctx_story = get_context_story(stories)
        if _ctx_story and str(_ctx_story.get("id")) != str(primary_story.get("id")):
            primary_story = _ctx_story
            st.session_state["active_story_obj"] = _ctx_story
            try:
                modes = story_modes(primary_story)
            except Exception:
                pass

    title = field_value(primary_story, "title", "")
    client = field_value(primary_story, "client", "")
    domain = field_value(primary_story, "domain", "")

    # Compact header - single line with subtle separators
    meta_line = " • ".join([x for x in [client, domain] if x])

    st.markdown(
        f"""
    <div style='margin-bottom: 8px;'>
        <div style='font-size: 18px; font-weight: 600; margin-bottom: 4px;'>{title}</div>
        <div style='font-size: 13px; color: #888; margin-bottom: 12px;'>{meta_line}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # View mode pills - smaller, less prominent
    labels = [
        ("narrative", "Summary"),
        ("key_points", "Key Points"),
        ("deep_dive", "Details"),
    ]
    current = st.session_state.get(answer_mode_key, "narrative")

    # Compact pill row
    cols = st.columns([1, 1, 1, 9])
    for i, (key, text) in enumerate(labels):
        with cols[i]:
            disabled = current == key
            if st.button(
                text,
                key=f"mode_{answer_mode_key}_{key}",
                disabled=disabled,
                use_container_width=True,
            ):
                st.session_state[answer_mode_key] = key
                st.rerun()

    st.markdown("<div style='margin: 12px 0;'></div>", unsafe_allow_html=True)

    # Body with less padding
    body_md = modes.get(st.session_state.get(answer_mode_key, "narrative"), "")
    if body_md:
        st.markdown(body_md)
    else:
        st.markdown("_No content available for this view._")

    # Sources - tighter spacing
    _srcs = st.session_state.get("last_sources") or []
    if not _srcs and primary_story:
        _srcs = [
            {
                "id": primary_story.get("id"),
                "title": primary_story.get("Title"),
                "client": primary_story.get("Client"),
            }
        ]
        try:
            for r in _related_stories(primary_story, max_items=2):
                _srcs.append(
                    {
                        "id": r.get("id"),
                        "title": r.get("Title"),
                        "client": r.get("Client"),
                    }
                )
        except Exception:
            pass

    if _srcs:
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        show_sources(
            _srcs,
            interactive=True,
            key_prefix=f"compact_{answer_mode_key}_",
            title="Sources",
            stories=stories,
        )
        st.write("DEBUG: About to call render_followup_chips")

        # Add follow-up suggestions
        render_followup_chips(primary_story, st.session_state.get("ask_input", ""))
        st.write("DEBUG: After render_followup_chips call")


# Safe alias that mirrors F() but is immune to shadowing elsewhere
def field_value(s: dict, key: str, default: str | list | None = None):
    # Inline copy of F() to avoid name collisions
    if key in s:
        return s[key]
    pc = key[:1].upper() + key[1:]
    if pc in s:
        return s[pc]

    if key == "domain":
        cat = s.get("Category") or s.get("Domain")
        sub = s.get("Sub-category") or s.get("SubCategory")
        if cat and sub:
            return f"{cat} / {sub}"
        return cat or sub or default

    if key == "tags":
        if "tags" in s and isinstance(s["tags"], list):
            return s["tags"]
        pub = s.get("public_tags")
        if isinstance(pub, list):
            return pub
        if isinstance(pub, str):
            return [t.strip() for t in pub.split(",") if t.strip()]
        return default or []

    alias = {
        "who": "Person",
        "where": "Place",
        "why": "Purpose",
        "how": "Process",
        "what": "Performance",
    }
    if key in alias and alias[key] in s:
        return s[alias[key]]

    return default


def STAR(s: dict) -> dict:
    return {
        "situation": s.get("Situation", []) or s.get("situation", []),
        "task": s.get("Task", []) or s.get("task", []),
        "action": s.get("Action", []) or s.get("action", []),
        "result": s.get("Result", []) or s.get("result", []),
    }


def FIVEP_SUMMARY(s: dict) -> str:
    return s.get("5PSummary") or s.get("5p_summary") or ""


def _format_narrative(s: dict) -> str:
    """1-paragraph, recruiter-friendly narrative from a single story."""
    title = s.get("Title", "")
    client = s.get("Client", "")
    domain = s.get("Sub-category", "")
    goal = (s.get("Purpose") or "").strip().rstrip(".")
    how = ", ".join((s.get("Process") or [])[:2]).strip().rstrip(".")
    metric = strongest_metric_line(s)
    bits = []
    if title or client:
        bits.append(
            f"I led **{title}** at **{client}**"
            if title
            else f"I led work at **{client}**"
        )
    if domain:
        bits[-1] += f" in **{domain}**."
    if goal:
        bits.append(f"The aim was {goal.lower()}.")
    if how:
        bits.append(f"We focused on {how.lower()}.")
    if metric:
        bits.append(f"Impact: **{metric}**.")
    return " ".join(bits) or build_5p_summary(s, 280)


# Also update your context banner to be minimal
def render_compact_context_banner(stories: list):
    """Single-line context breadcrumb."""
    ctx = get_context_story(stories)
    if not ctx:
        return

    client = (ctx.get("Client") or "").strip()
    domain_full = (ctx.get("Sub-category") or "").strip()
    domain_short = domain_full.split(" / ")[-1] if " / " in domain_full else domain_full

    st.markdown(
        f"""
    <div style='font-size: 13px; color: #888; margin-bottom: 16px; padding: 8px 12px; background: rgba(128,128,128,0.05); border-radius: 6px;'>
        Context: {client} | {domain_short}
    </div>
    """,
        unsafe_allow_html=True,
    )
