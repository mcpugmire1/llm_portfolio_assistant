"""
Ask MattGPT Page

Interactive chat interface for conversational exploration of Matt's experience.
Uses semantic search and Pinecone to retrieve relevant project stories.
"""

import streamlit as st
from typing import List, Dict, Optional
import json
from datetime import datetime
import os, re, time, textwrap, json
from config.debug import DEBUG
from config.settings import get_conf
from utils.ui_helpers import dbg, safe_container
from utils.validation import is_nonsense, token_overlap_ratio, _tokenize
from utils.ui_helpers import render_no_match_banner
from utils.formatting import story_has_metric, strongest_metric_line, build_5p_summary, _format_key_points, METRIC_RX
from services.pinecone_service import _init_pinecone, PINECONE_MIN_SIM, SEARCH_TOP_K, _safe_json, _summarize_index_stats, PINECONE_NAMESPACE, PINECONE_INDEX_NAME, W_PC, W_KW, _DEF_DIM, _PINECONE_INDEX, VECTOR_BACKEND
from services.rag_service import semantic_search, _KNOWN_VOCAB
from utils.formatting import _format_narrative, _format_key_points, _format_deep_dive
from utils.ui_helpers import render_sources_chips, render_sources_badges_static
from ui.components.how_agy_works import render_how_agy_works

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

    if not st.session_state.get("ask_transcript"):
        render_landing_page(stories)
    else:
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
    st.markdown("""
        <style>
        /* AGGRESSIVE SPACING REMOVAL */
        .main {
            padding-top: 0 !important;
        }
        
        .main .block-container {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        
        section[data-testid="stMain"] {
            padding-top: 0 !important;
        }
        
        div[data-testid="stAppViewContainer"] {
            padding-top: 0 !important;
        }
        
        /* Kill the gap after header */
        header[data-testid="stHeader"] {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }
        
        /* Remove spacing from first markdown element */
        .stMarkdown:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        /* Purple header - pull up slightly if needed */
        .ask-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            margin: -2rem 0 0 0 !important;  /* Slight negative top margin */
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

        /* Status bar */
        .status-bar {
            display: flex;
            gap: 32px;
            justify-content: center;
            padding: 16px 24px;
            background: rgba(255, 255, 255, 0.95);
            border-bottom: 1px solid #E5E7EB;
            margin: 0 !important;
        }

        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: #6B7280;
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
        div[data-testid="stTextInput"] input {
            width: 100% !important;
            padding: 20px 24px !important;
            font-size: 17px !important;
            border: 2px solid #E5E7EB !important;
            border-radius: 16px !important;
            transition: all 0.2s ease !important;
            background: #FAFAFA !important;
            font-family: inherit !important;
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
    """, unsafe_allow_html=True)

    # === PURPLE HEADER ===
    st.markdown("""
    <div class="ask-header">
        <div class="header-content" style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 24px;">
                <img class="header-agy-avatar"
                    src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_avatar_64_dark.png"
                    alt="Agy"/>
                <div class="header-text">
                    <h1>Ask MattGPT</h1>
                    <p>Meet Agy 🐾 — Tracking down insights from 20+ years of transformation experience</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # === STATUS BAR ===
    st.markdown("""
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
    """, unsafe_allow_html=True)

    # === MAIN INTRO SECTION ===
    st.markdown("""
    <div class="main-intro-section">
        <div class="main-avatar">
            <img src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_avatar_96_dark.png" alt="Agy"/>
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
    """, unsafe_allow_html=True)

    # Placeholder for loading message - positioned before "TRY ASKING" section
    loading_placeholder = st.empty()

    st.markdown('<div class="suggested-title">TRY ASKING:</div>', unsafe_allow_html=True)

    # === SUGGESTED QUESTION BUTTONS ===
    qs = [
        ("🚀", "How did Matt transform global payments at scale?"),
        ("🏥", "Show me Matt's GenAI work in healthcare"),
        ("💡", "Track down Matt's innovation leadership stories"),
        ("👥", "How did Matt scale agile across 150+ people?"),
        ("⚡", "Find Matt's platform engineering projects"),
        ("🎯", "Show me how Matt handles stakeholders")
    ]

    c1, c2 = st.columns(2, gap="small")

    # Disable all buttons when any is processing
    disabled = st.session_state.get("processing_suggestion", False)

    for i, (icon, q) in enumerate(qs):
        with c1 if i % 2 == 0 else c2:
            if st.button(f"{icon}  {q}", key=f"suggested_{i}", type="secondary", use_container_width=True, disabled=disabled):
                # Set state and trigger rerun to show loading state
                st.session_state["ask_transcript"] = []
                st.session_state["processing_suggestion"] = True
                st.session_state["pending_query"] = q
                st.session_state["landing_input_value"] = q
                st.session_state["landing_input"] = q
                st.session_state["ask_input_value"] = q
                st.rerun()

    # === INPUT AREA ===
    st.markdown('<div class="landing-input-container">', unsafe_allow_html=True)

    # Use columns to keep input and button on same line
    col_input, col_button = st.columns([6, 1])

    with col_input:
        # The text_input uses the key to automatically sync with session state
        # When we set st.session_state["landing_input"] = question, it appears here
        user_input = st.text_input(
            "Ask me anything — from building MattGPT to leading global programs...",
            key="landing_input",
            label_visibility="collapsed",
            placeholder="Ask me anything — from building MattGPT to leading global programs..."
        )

    with col_button:
        # Disable button if input is empty OR if we're currently processing
        button_disabled = not user_input or disabled
        if st.button("Ask Agy 🐾", key="landing_ask", type="primary", disabled=button_disabled):
            if user_input:
                # Set state and trigger rerun to show loading state
                # NOTE: Set ask_transcript FIRST, then our values (so _ensure doesn't clear them)
                st.session_state["ask_transcript"] = []
                st.session_state["processing_suggestion"] = True
                st.session_state["pending_query"] = user_input
                st.session_state["landing_input_value"] = user_input
                st.session_state["landing_input"] = user_input
                st.session_state["ask_input_value"] = user_input
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<p class="powered-by-text">Powered by OpenAI GPT-4o-mini with semantic search across 120+ project case studies</p>', unsafe_allow_html=True)

    # === PROCESS PENDING QUERY (if in processing state) ===
    # This runs AFTER the UI is rendered, so user sees disabled buttons and styled message
    if st.session_state.get("processing_suggestion") and st.session_state.get("pending_query"):
        query = st.session_state.get("pending_query")

        # Show the styled loading message in the placeholder
        with loading_placeholder:
            st.markdown("""
<div style='background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
            border: 2px solid #667eea40;
            border-radius: 12px;
            padding: 16px 24px;
            margin: 20px 0;
            display: flex;
            align-items: center;
            gap: 12px;'>
    <div style='font-size: 20px; animation: bounce 1s infinite;'>🐾</div>
    <div style='color: #667eea; font-weight: 500;'>Agy is tracking down insights...</div>
</div>
<style>@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }</style>
""", unsafe_allow_html=True)

        # Process the query
        result = send_to_backend(query, {}, None, stories)

        # Add to transcript
        st.session_state["ask_transcript"].append({"Role": "user", "text": query})
        st.session_state["ask_transcript"].append({
            "type": "card",
            "Title": result.get("sources", [{}])[0].get("title", "Response"),
            "story_id": result.get("sources", [{}])[0].get("id"),
            "one_liner": result["answer_md"],
            "sources": result.get("sources", []),
            "confidence": result.get("sources", [{}])[0].get("score", 0.8) if result.get("sources") else 0.8,
            "modes": result.get("modes", {}),
        })

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
    st.markdown("""
        <style>
        /* Keep existing conversation CSS - just remove navbar styles */
        /* Chat interface header */
        .conversation-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            margin: -2rem 0 0 0 !important;  
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
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
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 20px;
            color: white;
            padding: 0.5rem 1.25rem;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .conversation-how-btn:hover {
            background: rgba(255, 255, 255, 0.25);
            border-color: rgba(255, 255, 255, 0.5);
        }

        /* Status bar for conversation view */
        .status-bar-conversation {
            background: #f8f9fa;
            padding: 12px 30px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            gap: 24px;
            align-items: center;
            font-size: 13px;
            margin-bottom: 16px;
        }

        .status-dot-conversation {
            width: 8px;
            height: 8px;
            background: #27ae60;
            border-radius: 50%;
            display: inline-block;
            margin-right: 6px;
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
            width: 16px;
            height: 16px;
            animation: tennisBallCycle 0.9s infinite;
        }

        @keyframes tennisBallCycle {
            0%, 100% { content: '🎾'; }
            33% { content: '🎾'; }
            66% { content: '🎾'; }
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

        /* Override Streamlit chat message styling */
        [data-testid="stChatMessage"][data-testid-assistant] {
            background: white !important;
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
            border-left: 4px solid #8B5CF6 !important;
        }

        [data-testid="stChatMessage"][data-testid-user] {
            background: #e3f2fd !important;
            border-radius: 8px !important;
            padding: 16px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        }

        /* Avatar styling */
        [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
            width: 48px !important;
            height: 48px !important;
            background: white !important;
            border: 2px solid #e0e0e0 !important;
            padding: 4px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        }

        [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] {
            width: 40px !important;
            height: 40px !important;
            background: #7f8c8d !important;
            opacity: 0.5 !important;
        }

        /* Chat input styling */
        [data-testid="stChatInput"] {
            padding: 20px 30px !important;
            background: white !important;
            border-top: 2px solid #e0e0e0 !important;
        }

        [data-testid="stChatInput"] input {
            padding: 14px 18px !important;
            border: 2px solid #ddd !important;
            border-radius: 8px !important;
            font-size: 15px !important;
        }

        [data-testid="stChatInput"] input:focus {
            border-color: #8B5CF6 !important;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
        }

        [data-testid="stChatInput"] button {
            padding: 14px 28px !important;
            background: #8B5CF6 !important;
            color: white !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
        }

        [data-testid="stChatInput"] button:hover {
            background: #7C3AED !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3) !important;
        }

        /* Messages area background */
        .main .block-container {
            background: #fafafa !important;
            padding: 30px !important;
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
            margin: 4px;
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
            background: #10B981;
            color: white;
            border-color: #10B981;
        }

        /* Message spacing */
        .message-avatar-gap {
            gap: 12px;
        }

        .message-spacing {
            margin-bottom: 24px;
        }
        /* Your existing conversation CSS goes here unchanged */
        </style>
    """, unsafe_allow_html=True)
    
    # Page header with purple gradient
    st.markdown("""
    <div class="conversation-header">
        <div class="conversation-header-content">
            <img class="conversation-agy-avatar" src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_avatar_96_dark.png" width="64" height="64" style="width: 64px; height: 64px; border-radius: 50%; border: 3px solid white !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;" alt="Agy"/>
            <div class="conversation-header-text">
                <h1>Ask MattGPT</h1>
                <p>Meet Agy 🐾 — Tracking down insights from 20+ years of transformation experience</p>
            </div>
        </div>
        <button class="conversation-how-btn" onclick="document.querySelector('[key=how_works_top]').click()">
            🔧 How Agy searches
        </button>
    </div>
    """, unsafe_allow_html=True)

     # Anchor at top to force scroll position
    st.markdown('<div id="ask-top"></div>', unsafe_allow_html=True)

    # Force scroll to top using multiple methods
    st.markdown("""
    <script>
    // Immediate scroll
    window.scrollTo(0, 0);
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;

    // Also try after a tiny delay in case content is still loading
    setTimeout(function() {
        window.scrollTo(0, 0);
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
    }, 10);
    </script>
    """, unsafe_allow_html=True)

    # Hidden button for "How it works" (triggered by header button)
    if st.button("🔧 How it works", key="how_works_top"):
        st.session_state["show_how_modal"] = not st.session_state.get(
            "show_how_modal", False
        )
        st.rerun()

    # Status bar matching the spec
    st.markdown("""
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
    """, unsafe_allow_html=True)

    # Show the modal if toggled
    if st.session_state.get("show_how_modal", False):
        # Force scroll to top when modal opens
        st.markdown("""
        <script>
        window.scrollTo({top: 0, behavior: 'smooth'});
        </script>
        """, unsafe_allow_html=True)

        # Create a proper modal container without using expander
        st.markdown("---")

        # Header with close button
        col1, col2 = st.columns([10, 1])
        with col1:
            st.markdown("## 🔧 How MattGPT Works")
        with col2:
            if st.button("✕", key="close_how"):
                st.session_state["show_how_modal"] = False
                st.rerun()

        # Content in a bordered container
        with st.container():
            # Quick stats bar
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Stories Indexed", "120+")
            with col2:
                st.metric("Avg Response Time", "1.2s")
            with col3:
                st.metric("Retrieval Accuracy", "87%")
            with col4:
                st.metric("Vector Dimensions", "384")

            st.markdown("---")

            # Architecture overview
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    """
                ### Solution Architecture Overview
                
                **🎯 Semantic Search Pipeline**
                - Sentence-BERT embeddings (all-MiniLM-L6-v2)
                - 384-dimensional vector space
                - Pinecone vector database with metadata filtering
                
                **🔄 Hybrid Retrieval**
                - 80% semantic similarity weight
                - 20% keyword matching weight
                - Intent recognition for query understanding
                """
                )

            with col2:
                st.markdown(
                    """
                ### Data & Processing
                
                **📊 Story Corpus**
                - 120+ structured narratives from Fortune 500 projects
                - STAR/5P framework encoding
                - Rich metadata: client, domain, outcomes, metrics
                
                **💬 Response Generation**
                - Context-aware retrieval (top-k=30)
                - Multi-mode synthesis (Narrative/Key Points/Deep Dive)
                - Source attribution with confidence scoring
                """
                )

            # Query Flow
            st.markdown("### Query Flow")
            st.code(
                """
                Your Question 
                    ↓
                [Embedding + Intent Analysis]
                    ↓
                [Pinecone Vector Search + Keyword Matching]
                    ↓
                [Hybrid Scoring & Ranking]
                    ↓
                [Top 3 Stories Retrieved]
                    ↓
                [Response Synthesis with Sources]
                            """,
                language="text",
            )

            st.markdown("---")
            st.markdown("### System Architecture")

            try:
                with open("assets/rag_architecture_grid_svg.svg", "r") as f:
                    svg_content = f.read()
                
                # Remove XML declaration and DOCTYPE
                svg_content = svg_content.replace('<?xml version="1.0" encoding="UTF-8" standalone="no"?>', '')
                svg_content = svg_content.replace('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">', '')
                
                # Use HTML component with transparent background and no scroll
                import streamlit.components.v1 as components
                
                components.html(f"""
                <div style='width: 100%; text-align: center;'>
                    {svg_content}
                </div>
                """, height=280, scrolling=False)
                
            except Exception as e:
                st.error(f"Error loading architecture diagram: {e}")

            st.markdown("---")
            

            # Detailed breakdown
            st.markdown("### Architecture Details")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                **Search & Retrieval**
                - **Semantic**: Pinecone cosine similarity (80% weight)
                - **Keyword**: BM25-style token overlap (20% weight)
                - Minimum similarity threshold: 0.15
                - Top-k pool: 30 candidates before ranking
                """)

            with col2:
                st.markdown("""
                **Response Synthesis**
                - Rank top 3 stories by blended score
                - Generate 3 views from same sources:
                - Narrative (1-paragraph summary)
                - Key Points (3-4 bullets)
                - Deep Dive (STAR breakdown)
                - Interactive source chips with confidence %
                """)

            st.markdown("---")

            st.markdown("""
            **Key Differentiators:**
            - Hybrid retrieval ensures both semantic understanding and exact term matching
            - Multi-mode synthesis provides flexible presentation for different use cases
            - Context locking allows follow-up questions on specific stories
            - Off-domain gating with suggestion chips prevents poor matches
            """)

    # Define ctx - MUST be outside and after the modal block
    ctx = get_context_story(stories)
    _show_ctx = bool(ctx) and (
        st.session_state.get("__ctx_locked__") or st.session_state.get("__asked_once__")
    )

    if _show_ctx:
        render_compact_context_banner(stories)

    # Rest of your Ask MattGPT content continues...
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
    if pending:
        # If a live card was pending snapshot, capture it now before injecting the new turn
        if st.session_state.get("__pending_card_snapshot__"):
            _push_card_snapshot_from_state(stories)
            st.session_state["__pending_card_snapshot__"] = False
        _push_user_turn(pending)
        with st.status("Searching Matt's experience...", expanded=True) as status:
            try:
                # Ask is pure semantic; ignore Explore filters here
                resp = send_to_backend(pending, {}, ctx, stories)

                # Show confidence after retrieval
                sources = resp.get("sources", [])
                if sources:
                    first_id = str(sources[0].get("id", ""))
                    scores = st.session_state.get("__pc_last_ids__", {}) or {}
                    conf = scores.get(first_id)
                    if conf:
                        conf_pct = int(float(conf) * 100)
                        st.write(f"✓ Found relevant stories • {conf_pct}% match confidence")

                status.update(label="Answer ready!", state="complete", expanded=False)

            except Exception as e:
                    status.update(label="Error occurred", state="error")
                    print(f"DEBUG: send_to_backend failed: {e}")
                    import traceback
                    traceback.print_exc()
                    _push_assistant_turn(f"Error: {str(e)}")
                    st.rerun()

            else:
                set_answer(resp)
                # If no banner is active, append a static card snapshot now so it
                # appears in-order as a chat bubble; also suppress the bottom live card once.
                if not st.session_state.get(
                    "ask_last_reason"
                ) and not st.session_state.get("__sticky_banner__"):
                    _push_card_snapshot_from_state(stories)
                    st.session_state["__suppress_live_card_once__"] = True
                # If a chip click requested banner clear, perform it now after answer set
                if st.session_state.pop("__clear_banner_after_answer__", False):
                    st.session_state.pop("ask_last_reason", None)
                    st.session_state.pop("ask_last_query", None)
                    st.session_state.pop("ask_last_overlap", None)
                st.rerun()

    # 3) Render transcript so far (strict order, no reflow)
    _render_ask_transcript(stories)

    # Force scroll to top after transcript renders
    st.markdown("""
    <script>
    // Multiple scroll methods with longer delays
    setTimeout(function() {
        window.scrollTo(0, 0);
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
    }, 50);
    setTimeout(function() {
        window.scrollTo(0, 0);
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
    }, 100);
    setTimeout(function() {
        window.scrollTo(0, 0);
    }, 200);
    </script>
    """, unsafe_allow_html=True)

    # 4) One‑shot nonsense/off‑domain banner appears AFTER transcript
    rendered_banner = False
    if st.session_state.get("ask_last_reason"):
        with st.chat_message("assistant"):
            render_no_match_banner(
                reason=st.session_state.get("ask_last_reason", ""),
                query=st.session_state.get("ask_last_query", ""),
                overlap=st.session_state.get("ask_last_overlap", None),
                suppressed=st.session_state.get("__pc_suppressed__", False),
                filters=st.session_state.get("filters", {}),
                key_prefix="askinline",
            )
        rendered_banner = True
        # Clear flags so the banner doesn't re-render on every rerun
        st.session_state.pop("ask_last_reason", None)
        st.session_state.pop("ask_last_query", None)
        st.session_state.pop("ask_last_overlap", None)
        # Persist as sticky so it remains visible between user turns unless dismissed
        st.session_state.setdefault(
            "__sticky_banner__",
            {
                "reason": (
                    dec
                    if (dec := (st.session_state.get("__ask_dbg_decision") or ""))
                    else "no_match"
                ),
                "query": st.session_state.get("__ask_dbg_prompt", ""),
                "overlap": None,
                "suppressed": bool(st.session_state.get("__pc_suppressed__", False)),
            },
        )
    elif True:
        # Forced fallback: if gating decided no‑match but the flag was not set,
        # render a banner anyway so the user sees actionable chips.
        dec = (st.session_state.get("__ask_dbg_decision") or "").strip().lower()
        no_match_decision = (
            dec.startswith("rule:")
            or dec.startswith("low_overlap")
            or dec == "low_conf"
            or dec == "no_overlap+low_conf"
        )
        if no_match_decision and not st.session_state.get("last_sources"):
            with st.chat_message("assistant"):
                render_no_match_banner(
                    reason=dec or "no_match",
                    query=st.session_state.get("__ask_dbg_prompt", ""),
                    overlap=st.session_state.get("ask_last_overlap", None),
                    suppressed=st.session_state.get("__pc_suppressed__", False),
                    filters=st.session_state.get("filters", {}),
                    key_prefix="askinline_forced",
                )
            rendered_banner = True

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
    #  - we already have at least one static card snapshot in the transcript
    has_snapshot_card = any(
        (isinstance(x, dict) and x.get("type") == "card")
        for x in st.session_state.get("ask_transcript", [])
    )
    if (
        not rendered_banner
        and not has_snapshot_card
        and not st.session_state.get("__suppress_live_card_once__")
        and (_m or _primary or st.session_state.get("last_answer"))
    ):
        # Always render the bottom live card so pills are available.
        # Snapshot holds only header + one-liner + sources to avoid duplicate body text.
        render_answer_card_compact(
            _primary or {"title": "Answer"}, _m, stories, "answer_mode"
        )

    # Reset one-shot suppression flag after a render cycle
    if st.session_state.get("__suppress_live_card_once__"):
        st.session_state["__suppress_live_card_once__"] = False

    # 6) Handle a new chat input (command aliases or normal question)
    # Render the chat input only on the Ask MattGPT tab
    if st.session_state.get("active_tab") == "Ask MattGPT":
        user_input_local = st.chat_input("Ask anything…", key="ask_chat_input1")
    else:
        user_input_local = None
    if user_input_local:
        # If a live card is pending snapshot from the previous answer, snapshot it now
        if st.session_state.get("__pending_card_snapshot__"):
            _push_card_snapshot_from_state(stories)
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
        with st.status("Searching Matt's experience...", expanded=True) as status:
            try:
                # Consume the suggestion flag (one-shot); we don't need its value here
                st.session_state.pop("__ask_from_suggestion__", None)

                # Ask is pure semantic; ignore Explore filters here
                resp = send_to_backend(user_input_local, {}, ctx_for_this_turn, stories)

                # Show confidence after retrieval
                sources = resp.get("sources", [])
                if sources:
                    first_id = str(sources[0].get("id", ""))
                    scores = st.session_state.get("__pc_last_ids__", {}) or {}
                    conf = scores.get(first_id)
                    if conf:
                        conf_pct = int(float(conf) * 100)
                        st.write(f"✓ Found relevant stories • {conf_pct}% match confidence")

                status.update(label="Answer ready!", state="complete", expanded=False)

            except Exception as e:
                status.update(label="Error occurred", state="error")
                _push_assistant_turn("Sorry, I couldn't generate an answer right now.")
                st.error(f"Backend error: {e}")
                st.rerun()

            else:
                set_answer(resp)

                # Add a static snapshot so the answer appears in-order as a bubble,
                # and suppress the bottom live card once to avoid duplication.
                if not st.session_state.get(
                    "ask_last_reason"
                ) and not st.session_state.get("__sticky_banner__"):
                    _push_card_snapshot_from_state(stories)
                    st.session_state["__suppress_live_card_once__"] = True

                st.rerun()


    # === ADD FOOTER ===
    from ui.components.footer import render_footer
    render_footer()


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
        pool = semantic_search(question or filters.get("q", ""), filters, stories=stories, top_k=SEARCH_TOP_K)


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
                dbg(f"ask: ranked by semantic similarity, first_ids={[s.get('id') for s in ranked]}")
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
        # Generate Agy-voiced response using GPT-4
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

def _generate_agy_response(question: str, ranked_stories: list[dict], answer_context: str) -> str:
    """
    Generate an Agy-voiced response using OpenAI GPT-4.

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
            organization=os.getenv("OPENAI_ORG_ID")
        )

        # Build context from ranked stories
        story_context = "\n\n---\n\n".join([
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
        ])

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

Here are the top 3 relevant projects from Matt's portfolio:

{story_context}

Generate an Agy-voiced response that:
1. Starts with a search status (e.g., "🐾 Let me track down Matt's experience with...")
2. Answers their question with specific project citations
3. Shows outcomes and patterns across Matt's work
4. Stays professional and credible
5. Offers to go deeper if helpful

Keep it conversational, warm, but professional. Cite specific clients and outcomes."""

        # Call OpenAI API
        # Using gpt-4o-mini: fast, cost-effective, excellent for well-crafted prompts
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
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
        for field in ["title", "client", "role", "domain", "division", "industry", "who", "where", "why"]:
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
        print(f"DEBUG _push_card_snapshot: sid={sid}, confidence={confidence}, scores={scores}")

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


def _clear_ask_context():
    """Remove any sticky story context so the next Ask is general-purpose."""
    st.session_state.pop("active_story", None)
    st.session_state.pop("__ctx_locked__", None)
    st.session_state.pop("seed_prompt", None)
    st.rerun()

def render_followup_chips(primary_story: dict, query: str = "", key_suffix: str = ""):
    """Generate contextual follow-up suggestions based on the answer."""

    if not primary_story:
        return

    # Universal follow-up suggestions that work with card-based retrieval
    # Focus on themes that trigger good semantic searches
    tags = set(str(t).lower() for t in (primary_story.get("tags") or []))

    suggestions = []

    # Theme-based suggestions that trigger relevant searches
    if any(t in tags for t in ["stakeholder", "collaboration", "communication"]):
        suggestions = [
            "How do you handle difficult stakeholders?",
            "Tell me about cross-functional collaboration",
            "What about managing remote teams?"
        ]
    elif any(t in tags for t in ["cloud", "architecture", "platform", "technical"]):
        suggestions = [
            "Show me examples with cloud architecture",
            "How do you modernize legacy systems?",
            "Tell me about technical challenges you've solved"
        ]
    elif any(t in tags for t in ["agile", "process", "delivery"]):
        suggestions = [
            "How do you accelerate delivery?",
            "Tell me about scaling agile practices",
            "Show me examples of process improvements"
        ]
    else:
        # Generic suggestions that work for any story
        suggestions = [
            "Show me examples with measurable impact",
            "How do you drive innovation?",
            "Tell me about leading transformation"
        ]

    if not suggestions:
        return

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    cols = st.columns(len(suggestions[:3]))
    for i, suggest in enumerate(suggestions[:3]):
        with cols[i]:
            # Make key unique by including card index and suggestion index
            unique_key = f"followup_{key_suffix}_{i}" if key_suffix else f"followup_{hash(suggest)%10000}_{i}"
            if st.button(suggest, key=unique_key, use_container_width=True):
                st.session_state["__inject_user_turn__"] = suggest
                # Don't set __ask_from_suggestion__ - treat chips like fresh typed questions
                # This ensures context lock is cleared and we get fresh search results
                st.session_state["__ask_force_answer__"] = True
                st.rerun()

def _render_ask_transcript(stories: list):
    """Render in strict order so avatars / order never jump."""
    for i, m in enumerate(st.session_state.get("ask_transcript", [])):
        # Static snapshot card entry
        if m.get("type") == "card":
            with st.chat_message("assistant"):
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
                    confidence = m.get("confidence")  # Original confidence from snapshot
                    if DEBUG:
                     print(f"DEBUG render: card_id={m.get('story_id')}, current_story_id={story.get('id') if story else None}, confidence={confidence}")

                    # If user clicked a different source, get that story's confidence from stored data
                    if isinstance(story, dict) and str(story.get("id")) != str(m.get("story_id")):
                        # Story was changed via source click - use stored source confidences
                        source_confidences = m.get("source_confidences", {}) or {}
                        story_id = str(story.get("id"))
                        if story_id in source_confidences:
                            confidence = source_confidences[story_id]
                        if DEBUG:
                          print(f"DEBUG render: switched story, new confidence={confidence}")

                    if confidence:
                        conf_pct = int(float(confidence) * 100)
                        # Color gradient: red -> orange -> green
                        if conf_pct >= 70:
                            bar_color = "#238636"  # green
                        elif conf_pct >= 50:
                            bar_color = "#ff8c00"  # orange
                        else:
                            bar_color = "#f85149"  # red

                        st.markdown(f"""
                        <div style='display: flex; align-items: center; gap: 8px; font-size: 12px; color: #7d8590; margin-bottom: 12px;'>
                            <span>Match confidence</span>
                            <div style='width: 60px; height: 4px; background: #21262d; border-radius: 2px; overflow: hidden;'>
                                <div style='height: 100%; width: {conf_pct}%; background: {bar_color}; border-radius: 2px;'></div>
                            </div>
                            <span style='color: {bar_color}; font-weight: 600;'>{conf_pct}%</span>
                        </div>
                        """, unsafe_allow_html=True)

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
                            render_followup_chips(story, st.session_state.get("ask_input", ""), key_suffix=f"snap_{i}")
                st.markdown('</div>', unsafe_allow_html=True)
            continue

        # Default chat bubble (user/assistant text)
        role = "assistant" if m.get("Role") == "assistant" else "user"
        with st.chat_message(role):  # Remove avatar parameter
            st.markdown(m.get("text", ""))

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
    primary_story: dict, modes: dict, stories: List, answer_mode_key: str = "answer_mode",
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
    
    st.markdown(f"""
    <div style='margin-bottom: 8px;'>
        <div style='font-size: 18px; font-weight: 600; margin-bottom: 4px;'>{title}</div>
        <div style='font-size: 13px; color: #888; margin-bottom: 12px;'>{meta_line}</div>
    </div>
    """, unsafe_allow_html=True)
    
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
            disabled = (current == key)
            if st.button(
                text,
                key=f"mode_{answer_mode_key}_{key}",
                disabled=disabled,
                use_container_width=True
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
        _srcs = [{
            "id": primary_story.get("id"),
            "title": primary_story.get("Title"),
            "client": primary_story.get("Client"),
        }]
        try:
            for r in _related_stories(primary_story, max_items=2):
                _srcs.append({
                    "id": r.get("id"),
                    "title": r.get("Title"),
                    "client": r.get("Client"),
                })
        except Exception:
            pass
    
    if _srcs:
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        show_sources(_srcs, interactive=True, key_prefix=f"compact_{answer_mode_key}_", title="Sources", stories=stories)
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
    
    st.markdown(f"""
    <div style='font-size: 13px; color: #888; margin-bottom: 16px; padding: 8px 12px; background: rgba(128,128,128,0.05); border-radius: 6px;'>
        Context: {client} | {domain_short}
    </div>
    """, unsafe_allow_html=True)


# def render_landing_page(stories: list):
#     """
#     Render the Ask MattGPT landing page (empty state) matching the wireframe.
#     Shown when conversation transcript is empty.
#     """
#     import streamlit.components.v1 as components

#     # === 1. ALL CSS IN ONE BLOCK ===
#     st.markdown("""
#     <style>
#        /* NUCLEAR OPTION: Remove ALL spacing from Streamlit containers */
#     .main {
#         padding-top: 0 !important;
#     }
    
#     * Target the main app container - remove top padding */
#     section.main {
#         padding-top: 0 !important;
#     }

#     /* Target the block container - remove top padding/margin */
#     .block-container {
#         padding-top: 0 !important;
#         margin-top: 0 !important;
#     }

#     /* Remove bottom spacing from header */
#     header.st-emotion-cache-12fmjuu.ezrtsby2 {
#         margin-bottom: 0 !important;
#         padding-bottom: 0 !important;
#     }

#     /* More generic - target any header */
#     header[data-testid="stHeader"] {
#         margin-bottom: 0 !important;
#         padding-bottom: 0 !important;
#     }
    
#     /* Target the div that contains the first markdown (purple header) */
#     div[data-testid="stVerticalBlock"] > div:first-child {
#         margin-top: 0 !important;
#         padding-top: 0 !important;
#     }   

                
#     .main .block-container {
#         padding-top: 0 !important;
#         margin-top: 0 !important;
#         padding-bottom: 0 !important;
#     }
    
#     /* Kill the gap after header */
#     header[data-testid="stHeader"] {
#         margin-bottom: 0 !important;
#         padding-bottom: 0 !important;
#     }
    
#     /* Remove spacing from the header's parent container */
#     div[data-testid="stAppViewContainer"] {
#         padding-top: 0 !important;
#     }
    
#     /* Kill spacing on the main content container */
#     section[data-testid="stMain"] {
#         padding-top: 0 !important;
#     }
    
#     /* Remove gap between header and first element */
#     .stMarkdown:first-child {
#         margin-top: 0 !important;
#         padding-top: 0 !important;
#     }

#     /* Lock navbar - FULL WIDTH with proper height */
#     [class*="st-key-topnav_"] {
#         background: #2c3e50 !important;
#         margin: 0 !important;
#         padding: 15px 30px !important;
#         width: 100% !important;
#         min-height: 60px !important;
#     }

#    /* Navbar buttons need proper padding */
#     [class*="st-key-topnav_"] button {
#         background: transparent !important;
#         padding: 8px 16px !important;
#         color: white !important;
#         font-size: 14px !important;
#         min-height: 40px !important;  /* ADD THIS */
#         display: inline-flex !important;  /* ADD THIS */
#         align-items: center !important;  /* ADD THIS */
#     }
#     /* Style the text inside navbar buttons */
#     [class*="st-key-topnav_"] button p {
#         color: white !important;
#         margin: 0 !important;
#         padding: 0 !important;
#         font-size: 14px !important;
#         line-height: 1.4 !important;
#     }
#      /* Only highlight the Ask MattGPT button */
#     [class*="st-key-topnav_"] button[key="nav_ask_mattgpt"] {
#         background: #34495e !important;
#         border-radius: 4px !important;
#     }

#     /* Don't mess with navbar internal spacing */
#     [class*="st-key-topnav_"] div[data-testid="stHorizontalBlock"] {
#         background: transparent !important;
#         gap: 30px !important;
#     }
                
#     /* Pull the purple header up with negative margin */
#     .ask-header {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         padding: 30px;
#         margin-top: -2rem !important;
#         margin-bottom: 0 !important;
#         color: white;
#         display: flex;
#         justify-content: space-between;
#         align-items: center;
#     }


#     .header-content {
#         display: flex;
#         align-items: center;
#         gap: 24px;
#     }

#     .header-agy-avatar {
#         width: 64px !important;
#         height: 64px !important;
#         border-radius: 50% !important;
#         border: 3px solid white !important;
#         box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
#     }

#     .header-text h1 {
#         font-size: 32px;
#         margin: 0 0 8px 0;
#         color: white;
#     }

#     .header-text p {
#         font-size: 16px;
#         margin: 0;
#         opacity: 0.95;
#     }

#     .how-it-works-btn {
#         background: rgba(255, 255, 255, 0.2);
#         backdrop-filter: blur(10px);
#         border: 2px solid rgba(255, 255, 255, 0.3);
#         border-radius: 20px;
#         color: white;
#         padding: 0.5rem 1.25rem;
#         font-size: 14px;
#         font-weight: 500;
#         cursor: pointer;
#         transition: all 0.2s ease;
#     }

#     .how-it-works-btn:hover {
#         background: rgba(255, 255, 255, 0.25);
#         border-color: rgba(255, 255, 255, 0.5);
#     }

#     /* Status bar */
#     .status-bar {
#         display: flex;
#         gap: 32px;
#         justify-content: center;
#         padding: 16px 24px;
#         background: rgba(255, 255, 255, 0.95);
#         border-bottom: 1px solid #E5E7EB;
#         margin: 0 !important;
#     }

#     .status-item {
#         display: flex;
#         align-items: center;
#         gap: 8px;
#         font-size: 14px;
#         color: #6B7280;
#     }

#     .status-value {
#         font-weight: 600;
#         color: #2C363D;
#     }

#     .status-dot {
#         width: 8px;
#         height: 8px;
#         background: #10B981;
#         border-radius: 50%;
#         animation: pulse 2s ease-in-out infinite;
#     }

#     @keyframes pulse {
#         0%, 100% { opacity: 1; }
#         50% { opacity: 0.5; }
#     }

#     /* MAIN INTRO SECTION - Responsive like wireframe */
#     .main-intro-section {
#         background: white;
#         border-radius: 24px 24px 0 0;
#         max-width: 900px;
#         width: 100%;
#         margin: 20px auto 0;
#         padding: 48px 32px 32px;
#     }

#     .main-avatar {
#         text-align: center;
#     }

#     .main-avatar img {
#         width: 96px;
#         height: 96px;
#         border-radius: 50%;
#         box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
#     }

#     .welcome-title {
#         font-size: 28px;
#         color: #2c3e50;
#         margin: 24px 0 12px;
#         text-align: center;
#     }

#     .intro-text-primary {
#         font-size: 18px;
#         color: #374151;
#         line-height: 1.7;
#         font-weight: 500;
#         margin-bottom: 20px;
#         max-width: 650px;
#         margin-left: auto;
#         margin-right: auto;
#         text-align: center;
#     }

#     .intro-text-secondary {
#         font-size: 17px;
#         color: #6B7280;
#         line-height: 1.6;
#         max-width: 650px;
#         margin: 0 auto 48px;
#         text-align: center;
#     }

#     .suggested-title {
#         font-size: 14px;
#         font-weight: 600;
#         color: #7f8c8d;
#         text-transform: uppercase;
#         margin-bottom: 20px;
#         text-align: center;
#     }

#     /* BUTTON CONTAINER - Responsive with max-width like wireframe */
#     div[data-testid="stHorizontalBlock"]:has(button[key^="suggested_"]) {
#         display: grid !important;
#         grid-template-columns: repeat(2, 1fr) !important;
#         grid-template-rows: repeat(3, auto) !important;
#         gap: 16px !important;
#         max-width: 900px !important;
#         width: 100% !important;
#         margin: 0 auto !important;
#         background: white !important;
#         padding: 0 32px 48px !important;
#         border-radius: 0 0 24px 24px !important;
#         box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
#     }

#     /* Kill Streamlit's column divs - flatten the structure */
#     div[data-testid="stHorizontalBlock"]:has(button[key^="suggested_"]) > div[data-testid="column"] {
#         display: contents !important;
#     }

#     /* Remove element containers around buttons */
#     div[data-testid="stHorizontalBlock"]:has(button[key^="suggested_"]) .stElementContainer {
#         background: transparent !important;
#         padding: 0 !important;
#         margin: 0 !important;
#     }

#     /* Suggested question buttons */
#     button[key^="suggested_"] {
#         background: white !important;
#         border: 2px solid #E5E7EB !important;
#         border-radius: 12px !important;
#         padding: 20px 24px !important;
#         text-align: left !important;
#         transition: all 0.2s ease !important;
#         min-height: 85px !important;
#         display: flex !important;
#         align-items: center !important;
#         gap: 12px !important;
#         box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
#         width: 100% !important;
#     }

#     button[key^="suggested_"]:hover {
#         border-color: #8B5CF6 !important;
#         background: #F9FAFB !important;
#         box-shadow: 0 4px 12px rgba(139, 92, 246, 0.12) !important;
#         transform: translateY(-2px) !important;
#     }

#     button[key^="suggested_"] p {
#         font-size: 16px !important;
#         font-weight: 600 !important;
#         color: #2C363D !important;
#         line-height: 1.4 !important;
#         margin: 0 !important;
#         text-align: left !important;
#     }

#     /* Landing input container - Responsive like wireframe */
#     .landing-input-container {
#         max-width: 800px !important;
#         width: 100% !important;
#         margin: 40px auto 20px !important;
#         padding: 0 30px !important;
#     }

#     /* Lock the text input itself */
#     input[key="landing_input"] {
#         width: 100% !important;
#         max-width: 100% !important;
#     }

#     /* Lock input wrapper */
#     div:has(> input[key="landing_input"]) {
#         width: 100% !important;
#         max-width: 100% !important;
#     }

#     /* Lock the stElementContainer around the input */
#     .landing-input-container .stElementContainer {
#         width: 100% !important;
#         max-width: 100% !important;
#     }

#     /* Lock button wrapper in input container */
#     .landing-input-container div:has(> button[key="landing_ask"]) {
#         width: 100% !important;
#         max-width: 100% !important;
#     }

#     /* PURPLE ASK AGY BUTTON */
#     button[key="landing_ask"] {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
#         border: none !important;
#         color: white !important;
#         font-weight: 600 !important;
#         padding: 12px 32px !important;
#         border-radius: 24px !important;
#         font-size: 16px !important;
#         transition: all 0.3s ease !important;
#         box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
#     }

#     button[key="landing_ask"]:hover:not(:disabled) {
#         transform: translateY(-2px) !important;
#         box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
#     }

#     button[key="landing_ask"]:disabled {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
#         opacity: 0.5 !important;
#         cursor: not-allowed !important;
#     }

#     button[key="landing_ask"] p {
#         color: white !important;
#         margin: 0 !important;
#         font-weight: 600 !important;
#     }

#     /* Force remove any background from button wrapper */
#     div:has(> button[key="landing_ask"]) {
#         background: transparent !important;
#     }

#     /* Hide the trigger button - it's only for programmatic clicks */
#     button[key="how_works_landing"] {
#         display: none !important;
#         visibility: hidden !important;
#         position: absolute !important;
#         pointer-events: none !important;
#     }

#     /* Hide its container too */
#     div:has(> button[key="how_works_landing"]) {
#         display: none !important;
#     }
#     </style>
#     """, unsafe_allow_html=True)

#     # === 2. HEADER HTML - NO MARGIN ===
#     st.markdown("""
#     <div class="ask-header">
#         <div class="header-content">
#             <img class="header-agy-avatar" 
#                 src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_avatar_96_dark.png" 
#                 alt="Agy"/>
#             <div class="header-text">
#                 <h1>Ask MattGPT</h1>
#                 <p>Meet Agy 🐾 — Tracking down insights from 20+ years of transformation experience</p>
#             </div>
#         </div>
#         <button class="how-it-works-btn" onclick="document.querySelector('[key=how_works_landing]').click()">
#             🔧 How Agy searches
#         </button>
#     </div>
#     """, unsafe_allow_html=True)

#     # === 3. STATUS BAR HTML ===
#     st.markdown("""
#     <div class="status-bar">
#         <div class="status-item">
#             <span class="status-dot"></span>
#             <span>Semantic search <span class="status-value">active</span></span>
#         </div>
#         <div class="status-item">
#             <span>Pinecone index <span class="status-value">ready</span></span>
#         </div>
#         <div class="status-item">
#             <span>120+ stories <span class="status-value">indexed</span></span>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

#     # === 4. MAIN INTRO SECTION ===
#     st.markdown("""
#     <div class="main-intro-section">
#         <div class="main-avatar">
#             <img src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_avatar_96_dark.png" alt="Agy"/>
#         </div>
#         <h2 class="welcome-title">Hi, I'm Agy 🐾</h2>
#         <p class="intro-text-primary">
#             I'm a Plott Hound — a breed known for tracking skills and determination. 
#             Perfect traits for helping you hunt down insights from Matt's 120+ transformation projects.
#         </p>
#         <p class="intro-text-secondary">
#             Ask me about specific methodologies, leadership approaches, or project outcomes. 
#             I understand context, not just keywords.
#         </p>
#         <div class="suggested-title">TRY ASKING:</div>
#     </div>
#     """, unsafe_allow_html=True)

#     # === 5. SUGGESTED QUESTION BUTTONS ===
#     qs = [
#         ("🚀", "How did Matt transform global payments at scale?"),
#         ("🏥", "Show me Matt's GenAI work in healthcare"),
#         ("💡", "Track down Matt's innovation leadership stories"),
#         ("👥", "How did Matt scale agile across 150+ people?"),
#         ("⚡", "Find Matt's platform engineering projects"),
#         ("🎯", "Show me how Matt handles stakeholders")
#     ]

#     c1, c2 = st.columns(2, gap="small")

#     for i, (icon, q) in enumerate(qs):
#         with c1 if i % 2 == 0 else c2:
#             if st.button(f"{icon}  {q}", key=f"suggested_{i}", type="secondary", use_container_width=True):
#                 st.session_state["ask_input_value"] = q
#                 st.session_state["ask_transcript"] = []
#                 _ensure_ask_bootstrap()
#                 result = send_to_backend(q, {}, None, stories)
#                 st.session_state["ask_transcript"].append({"Role": "user", "text": q})
#                 st.session_state["ask_transcript"].append({
#                     "type": "card",
#                     "Title": result.get("sources", [{}])[0].get("title", "Response"),
#                     "story_id": result.get("sources", [{}])[0].get("id"),
#                     "one_liner": result["answer_md"],
#                     "sources": result.get("sources", []),
#                     "confidence": result.get("sources", [{}])[0].get("score", 0.8) if result.get("sources") else 0.8,
#                     "modes": result.get("modes", {}),
#                 })
#                 st.rerun()

#     # === 6. LARGE INPUT AREA AT BOTTOM ===
#     st.markdown('<div class="landing-input-container">', unsafe_allow_html=True)

#     user_input = st.text_input(
#         "Ask me anything — from building MattGPT to leading global programs...",
#         key="landing_input",
#         label_visibility="collapsed",
#         placeholder="Ask me anything — from building MattGPT to leading global programs..."
#     )

#     if st.button("Ask Agy ➜", key="landing_ask", type="primary", disabled=not user_input):
#         if user_input:
#             st.session_state["ask_input_value"] = user_input
#             st.session_state["ask_transcript"] = []
#             _ensure_ask_bootstrap()
            
#             result = send_to_backend(user_input, {}, None, stories)
            
#             st.session_state["ask_transcript"].append({
#                 "Role": "user",
#                 "text": user_input
#             })
            
#             st.session_state["ask_transcript"].append({
#                 "type": "card",
#                 "Title": result.get("sources", [{}])[0].get("title", "Response"),
#                 "story_id": result.get("sources", [{}])[0].get("id"),
#                 "one_liner": result["answer_md"],
#                 "sources": result.get("sources", []),
#                 "confidence": result.get("sources", [{}])[0].get("score", 0.8) if result.get("sources") else 0.8,
#                 "modes": result.get("modes", {}),
#             })
            
#             st.rerun()

#     st.markdown('</div>', unsafe_allow_html=True)

#     st.caption("Powered by OpenAI GPT-4o-mini with semantic search across 120+ project case studies")

#     # Hidden button for "How Agy searches" functionality
#     if st.button("How it works", key="how_works_landing", help="Learn how Agy searches"):
#         st.session_state["show_how_modal_landing"] = not st.session_state.get("show_how_modal_landing", False)
#         st.rerun()




# def render_conversation_view(stories: list):
#     """
#     Render the conversational chat interface (after first question asked).

#     Wireframe: ask_mattgpt_wireframe.html

#     Args:
#         stories: List of story dictionaries (STORIES from app.py)
#     """

#     # Conversation view CSS styling
#     st.markdown("""
#     <style>
#     /* Chat interface header */
#     .conversation-header {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         padding: 30px;
#         margin: -1rem -1rem 0 -1rem;
#         color: white;
#         display: flex;
#         justify-content: space-between;
#         align-items: center;
#     }

#     .conversation-header-content {
#         display: flex;
#         align-items: center;
#         gap: 24px;
#     }

#    .conversation-agy-avatar {
#         width: 64px !important;
#         height: 64px !important;
#         border-radius: 50% !important;
#         border: 3px solid white !important;
#         box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
# }

#     .conversation-header-text h1 {
#         font-size: 32px;
#         margin: 0 0 8px 0;
#         color: white;
#     }

#     .conversation-header-text p {
#         font-size: 16px;
#         margin: 0;
#         opacity: 0.95;
#     }

#     /* How Agy searches button - glass morphism */
#     .conversation-how-btn {
#         background: rgba(255, 255, 255, 0.2);
#         backdrop-filter: blur(10px);
#         border: 2px solid rgba(255, 255, 255, 0.3);
#         border-radius: 20px;
#         color: white;
#         padding: 0.5rem 1.25rem;
#         font-size: 14px;
#         font-weight: 500;
#         cursor: pointer;
#         transition: all 0.2s ease;
#     }

#     .conversation-how-btn:hover {
#         background: rgba(255, 255, 255, 0.25);
#         border-color: rgba(255, 255, 255, 0.5);
#     }

#     /* Status bar for conversation view */
#     .status-bar-conversation {
#         background: #f8f9fa;
#         padding: 12px 30px;
#         border-bottom: 1px solid #e0e0e0;
#         display: flex;
#         gap: 24px;
#         align-items: center;
#         font-size: 13px;
#         margin-bottom: 16px;
#     }

#     .status-dot-conversation {
#         width: 8px;
#         height: 8px;
#         background: #27ae60;
#         border-radius: 50%;
#         display: inline-block;
#         margin-right: 6px;
#     }

#     .status-label {
#         color: #7f8c8d;
#     }

#     .status-value {
#         color: #2c3e50;
#         font-weight: 600;
#     }

#     /* Thinking indicator */
#     .thinking-indicator {
#         display: inline-flex;
#         align-items: center;
#         gap: 8px;
#         padding: 8px 12px;
#         background: #f0f0f0;
#         border-radius: 6px;
#         font-size: 13px;
#         color: #7f8c8d;
#         margin-bottom: 12px;
#         animation: fadeOutSmooth 0.5s ease-out 2s forwards;
#     }

#     @keyframes fadeOutSmooth {
#         to {
#             opacity: 0;
#             transform: translateY(-8px);
#         }
#     }

#     .thinking-icon {
#         width: 16px;
#         height: 16px;
#         animation: tennisBallCycle 0.9s infinite;
#     }

#     @keyframes tennisBallCycle {
#         0%, 100% { content: '🎾'; }
#         33% { content: '🎾'; }
#         66% { content: '🎾'; }
#     }

#     /* Chat messages styling */
#     .chat-message-ai {
#         background: white;
#         border-radius: 16px;
#         padding: 24px;
#         margin-bottom: 24px;
#         box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
#         border-left: 4px solid #8B5CF6;
#     }

#     .chat-message-user {
#         background: #e3f2fd;
#         border-radius: 8px;
#         padding: 16px;
#         margin-bottom: 24px;
#         box-shadow: 0 1px 3px rgba(0,0,0,0.1);
#     }

#     /* Message text styling */
#     .message-text {
#         font-size: 15px;
#         color: #2c3e50;
#         line-height: 1.6;
#     }

#     .message-text strong {
#         font-weight: bold;
#     }

#     /* Override Streamlit chat message styling */
#     [data-testid="stChatMessage"][data-testid-assistant] {
#         background: white !important;
#         border-radius: 16px !important;
#         padding: 24px !important;
#         box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
#         border-left: 4px solid #8B5CF6 !important;
#     }

#     [data-testid="stChatMessage"][data-testid-user] {
#         background: #e3f2fd !important;
#         border-radius: 8px !important;
#         padding: 16px !important;
#         box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
#     }

#     /* Avatar styling */
#     [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
#         width: 48px !important;
#         height: 48px !important;
#         background: white !important;
#         border: 2px solid #e0e0e0 !important;
#         padding: 4px !important;
#         box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
#     }

#     [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] {
#         width: 40px !important;
#         height: 40px !important;
#         background: #7f8c8d !important;
#         opacity: 0.5 !important;
#     }

#     /* Chat input styling */
#     [data-testid="stChatInput"] {
#         padding: 20px 30px !important;
#         background: white !important;
#         border-top: 2px solid #e0e0e0 !important;
#     }

#     [data-testid="stChatInput"] input {
#         padding: 14px 18px !important;
#         border: 2px solid #ddd !important;
#         border-radius: 8px !important;
#         font-size: 15px !important;
#     }

#     [data-testid="stChatInput"] input:focus {
#         border-color: #8B5CF6 !important;
#         box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
#     }

#     [data-testid="stChatInput"] button {
#         padding: 14px 28px !important;
#         background: #8B5CF6 !important;
#         color: white !important;
#         font-size: 15px !important;
#         font-weight: 600 !important;
#         border-radius: 8px !important;
#     }

#     [data-testid="stChatInput"] button:hover {
#         background: #7C3AED !important;
#         transform: translateY(-1px) !important;
#         box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3) !important;
#     }

#     /* Messages area background */
#     .main .block-container {
#         background: #fafafa !important;
#         padding: 30px !important;
#     }

#     /* Source links section */
#     .source-links-section {
#         border-top: 1px solid #e0e0e0;
#         margin-top: 16px;
#         padding-top: 16px;
#     }

#     .source-links-title {
#         font-size: 12px;
#         text-transform: uppercase;
#         color: #7f8c8d;
#         margin-bottom: 12px;
#         font-weight: 600;
#     }

#     /* Source chips styling */
#     .source-chip {
#         display: inline-flex;
#         align-items: center;
#         gap: 8px;
#         padding: 8px 16px;
#         background: #F3F4F6;
#         border: 2px solid #E5E7EB;
#         border-radius: 8px;
#         font-size: 14px;
#         font-weight: 500;
#         color: #2563EB;
#         text-decoration: none;
#         margin: 4px;
#         transition: all 0.2s ease;
#     }

#     .source-chip:hover {
#         background: #EEF2FF;
#         border-color: #8B5CF6;
#         transform: translateY(-1px);
#     }

#     .source-chip-icon {
#         color: #8B5CF6;
#     }

#     /* Action buttons */
#     .action-buttons {
#         display: flex;
#         gap: 8px;
#         margin-top: 16px;
#     }

#     .action-btn {
#         padding: 6px 12px;
#         background: white;
#         border: 1px solid #e0e0e0;
#         border-radius: 6px;
#         font-size: 12px;
#         color: #555;
#         cursor: pointer;
#         transition: all 0.2s ease;
#     }

#     .action-btn:hover {
#         background: #f5f5f5;
#         border-color: #ccc;
#     }

#     .action-btn.helpful-active {
#         background: #10B981;
#         color: white;
#         border-color: #10B981;
#     }

#     /* Message spacing */
#     .message-avatar-gap {
#         gap: 12px;
#     }

#     .message-spacing {
#         margin-bottom: 24px;
#     }
#     </style>
#     """, unsafe_allow_html=True)

#     # Page header with purple gradient
#     st.markdown("""
#     <div class="conversation-header">
#         <div class="conversation-header-content">
#             <img class="conversation-agy-avatar" src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_avatar_96_dark.png" width="64" height="64" style="width: 64px; height: 64px; border-radius: 50%; border: 3px solid white !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;" alt="Agy"/>
#             <div class="conversation-header-text">
#                 <h1>Ask MattGPT</h1>
#                 <p>Meet Agy 🐾 — Tracking down insights from 20+ years of transformation experience</p>
#             </div>
#         </div>
#         <button class="conversation-how-btn" onclick="document.querySelector('[key=how_works_top]').click()">
#             🔧 How Agy searches
#         </button>
#     </div>
#     """, unsafe_allow_html=True)

#      # Anchor at top to force scroll position
#     st.markdown('<div id="ask-top"></div>', unsafe_allow_html=True)

#     # Force scroll to top using multiple methods
#     st.markdown("""
#     <script>
#     // Immediate scroll
#     window.scrollTo(0, 0);
#     document.documentElement.scrollTop = 0;
#     document.body.scrollTop = 0;

#     // Also try after a tiny delay in case content is still loading
#     setTimeout(function() {
#         window.scrollTo(0, 0);
#         document.documentElement.scrollTop = 0;
#         document.body.scrollTop = 0;
#     }, 10);
#     </script>
#     """, unsafe_allow_html=True)

#     # Hidden button for "How it works" (triggered by header button)
#     if st.button("🔧 How it works", key="how_works_top"):
#         st.session_state["show_how_modal"] = not st.session_state.get(
#             "show_how_modal", False
#         )
#         st.rerun()

#     # Status bar matching the spec
#     st.markdown("""
#     <div class="status-bar">
#         <div class="status-item">
#             <span class="status-dot"></span>
#             <span>Semantic search <span class="status-value">active</span></span>
#         </div>
#         <div class="status-item">
#             <span>Pinecone index <span class="status-value">ready</span></span>
#         </div>
#         <div class="status-item">
#             <span>120+ stories <span class="status-value">indexed</span></span>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

#     # Show the modal if toggled
#     if st.session_state.get("show_how_modal", False):
#         # Force scroll to top when modal opens
#         st.markdown("""
#         <script>
#         window.scrollTo({top: 0, behavior: 'smooth'});
#         </script>
#         """, unsafe_allow_html=True)

#         # Create a proper modal container without using expander
#         st.markdown("---")

#         # Header with close button
#         col1, col2 = st.columns([10, 1])
#         with col1:
#             st.markdown("## 🔧 How MattGPT Works")
#         with col2:
#             if st.button("✕", key="close_how"):
#                 st.session_state["show_how_modal"] = False
#                 st.rerun()

#         # Content in a bordered container
#         with st.container():
#             # Quick stats bar
#             col1, col2, col3, col4 = st.columns(4)
#             with col1:
#                 st.metric("Stories Indexed", "120+")
#             with col2:
#                 st.metric("Avg Response Time", "1.2s")
#             with col3:
#                 st.metric("Retrieval Accuracy", "87%")
#             with col4:
#                 st.metric("Vector Dimensions", "384")

#             st.markdown("---")

#             # Architecture overview
#             col1, col2 = st.columns(2)

#             with col1:
#                 st.markdown(
#                     """
#                 ### Solution Architecture Overview
                
#                 **🎯 Semantic Search Pipeline**
#                 - Sentence-BERT embeddings (all-MiniLM-L6-v2)
#                 - 384-dimensional vector space
#                 - Pinecone vector database with metadata filtering
                
#                 **🔄 Hybrid Retrieval**
#                 - 80% semantic similarity weight
#                 - 20% keyword matching weight
#                 - Intent recognition for query understanding
#                 """
#                 )

#             with col2:
#                 st.markdown(
#                     """
#                 ### Data & Processing
                
#                 **📊 Story Corpus**
#                 - 120+ structured narratives from Fortune 500 projects
#                 - STAR/5P framework encoding
#                 - Rich metadata: client, domain, outcomes, metrics
                
#                 **💬 Response Generation**
#                 - Context-aware retrieval (top-k=30)
#                 - Multi-mode synthesis (Narrative/Key Points/Deep Dive)
#                 - Source attribution with confidence scoring
#                 """
#                 )

#             # Query Flow
#             st.markdown("### Query Flow")
#             st.code(
#                 """
#                 Your Question 
#                     ↓
#                 [Embedding + Intent Analysis]
#                     ↓
#                 [Pinecone Vector Search + Keyword Matching]
#                     ↓
#                 [Hybrid Scoring & Ranking]
#                     ↓
#                 [Top 3 Stories Retrieved]
#                     ↓
#                 [Response Synthesis with Sources]
#                             """,
#                 language="text",
#             )

#             st.markdown("---")
#             st.markdown("### System Architecture")

#             try:
#                 with open("assets/rag_architecture_grid_svg.svg", "r") as f:
#                     svg_content = f.read()
                
#                 # Remove XML declaration and DOCTYPE
#                 svg_content = svg_content.replace('<?xml version="1.0" encoding="UTF-8" standalone="no"?>', '')
#                 svg_content = svg_content.replace('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">', '')
                
#                 # Use HTML component with transparent background and no scroll
#                 import streamlit.components.v1 as components
                
#                 components.html(f"""
#                 <div style='width: 100%; text-align: center;'>
#                     {svg_content}
#                 </div>
#                 """, height=280, scrolling=False)
                
#             except Exception as e:
#                 st.error(f"Error loading architecture diagram: {e}")

#             st.markdown("---")
            

#             # Detailed breakdown
#             st.markdown("### Architecture Details")

#             col1, col2 = st.columns(2)

#             with col1:
#                 st.markdown("""
#                 **Search & Retrieval**
#                 - **Semantic**: Pinecone cosine similarity (80% weight)
#                 - **Keyword**: BM25-style token overlap (20% weight)
#                 - Minimum similarity threshold: 0.15
#                 - Top-k pool: 30 candidates before ranking
#                 """)

#             with col2:
#                 st.markdown("""
#                 **Response Synthesis**
#                 - Rank top 3 stories by blended score
#                 - Generate 3 views from same sources:
#                 - Narrative (1-paragraph summary)
#                 - Key Points (3-4 bullets)
#                 - Deep Dive (STAR breakdown)
#                 - Interactive source chips with confidence %
#                 """)

#             st.markdown("---")

#             st.markdown("""
#             **Key Differentiators:**
#             - Hybrid retrieval ensures both semantic understanding and exact term matching
#             - Multi-mode synthesis provides flexible presentation for different use cases
#             - Context locking allows follow-up questions on specific stories
#             - Off-domain gating with suggestion chips prevents poor matches
#             """)

#     # Define ctx - MUST be outside and after the modal block
#     ctx = get_context_story(stories)
#     _show_ctx = bool(ctx) and (
#         st.session_state.get("__ctx_locked__") or st.session_state.get("__asked_once__")
#     )

#     if _show_ctx:
#         render_compact_context_banner(stories)

#     # Rest of your Ask MattGPT content continues...
#     # Rest of your Ask MattGPT content continues as normal
#     # Context banner, transcript, etc...

#     # with right:
#     #    if st.button("×", key="btn_clear_ctx", help="Clear context"):
#     #       _clear_ask_context()

#     # Lightweight DEBUG status for Ask (visible only when DEBUG=True)
#     if DEBUG:
#         try:
#             _dbg_flags = {
#                 "vector": VECTOR_BACKEND,
#                 "index": PINECONE_INDEX_NAME or "-",
#                 "ns": PINECONE_NAMESPACE or "-",
#                 "pc_suppressed": bool(st.session_state.get("__pc_suppressed__")),
#                 "has_last": bool(st.session_state.get("last_sources")),
#                 "pending_snap": bool(st.session_state.get("__pending_card_snapshot__")),
#                 # NEW: report external renderer overrides
#                 "ext_chips": (
#                     "yes"
#                     if callable(globals().get("_ext_render_sources_chips"))
#                     else "no"
#                 ),
#                 "ext_badges": (
#                     "yes"
#                     if callable(globals().get("_ext_render_sources_badges_static"))
#                     else "no"
#                 ),
#             }
#             st.caption("🧪 " + ", ".join(f"{k}={v}" for k, v in _dbg_flags.items()))
#             # Second line: last prompt + ask decision
#             lp = (st.session_state.get("__ask_dbg_prompt") or "").strip()
#             lp = (lp[:60] + "…") if len(lp) > 60 else lp
#             st.caption(
#                 "🧪 "
#                 + f"prompt='{lp}' from_suggestion={st.session_state.get('__ask_dbg_from_suggestion')}"
#                 + f" force={st.session_state.get('__ask_dbg_force_answer')} pc_hits={st.session_state.get('__dbg_pc_hits')}"
#                 + f" decision={st.session_state.get('__ask_dbg_decision')}"
#                 + f" reason={st.session_state.get('ask_last_reason')}"
#             )
#         except Exception:
#             pass

#     # 1) Bootstrap a stable transcript (one-time)
#     _ensure_ask_bootstrap()

#     # 2) Unify seeds and chip-clicks: inject as a real user turn if present
#     seed = st.session_state.pop("seed_prompt", None)
#     injected = st.session_state.pop("__inject_user_turn__", None)
#     pending = seed or injected
#     if pending:
#         # If a live card was pending snapshot, capture it now before injecting the new turn
#         if st.session_state.get("__pending_card_snapshot__"):
#             _push_card_snapshot_from_state(stories)
#             st.session_state["__pending_card_snapshot__"] = False
#         _push_user_turn(pending)
#         with st.status("Searching Matt's experience...", expanded=True) as status:
#             try:
#                 # Ask is pure semantic; ignore Explore filters here
#                 resp = send_to_backend(pending, {}, ctx, stories)

#                 # Show confidence after retrieval
#                 sources = resp.get("sources", [])
#                 if sources:
#                     first_id = str(sources[0].get("id", ""))
#                     scores = st.session_state.get("__pc_last_ids__", {}) or {}
#                     conf = scores.get(first_id)
#                     if conf:
#                         conf_pct = int(float(conf) * 100)
#                         st.write(f"✓ Found relevant stories • {conf_pct}% match confidence")

#                 status.update(label="Answer ready!", state="complete", expanded=False)

#             except Exception as e:
#                     status.update(label="Error occurred", state="error")
#                     print(f"DEBUG: send_to_backend failed: {e}")
#                     import traceback
#                     traceback.print_exc()
#                     _push_assistant_turn(f"Error: {str(e)}")
#                     st.rerun()

#             else:
#                 set_answer(resp)
#                 # If no banner is active, append a static card snapshot now so it
#                 # appears in-order as a chat bubble; also suppress the bottom live card once.
#                 if not st.session_state.get(
#                     "ask_last_reason"
#                 ) and not st.session_state.get("__sticky_banner__"):
#                     _push_card_snapshot_from_state(stories)
#                     st.session_state["__suppress_live_card_once__"] = True
#                 # If a chip click requested banner clear, perform it now after answer set
#                 if st.session_state.pop("__clear_banner_after_answer__", False):
#                     st.session_state.pop("ask_last_reason", None)
#                     st.session_state.pop("ask_last_query", None)
#                     st.session_state.pop("ask_last_overlap", None)
#                 st.rerun()

#     # 3) Render transcript so far (strict order, no reflow)
#     _render_ask_transcript(stories)

#     # Force scroll to top after transcript renders
#     st.markdown("""
#     <script>
#     // Multiple scroll methods with longer delays
#     setTimeout(function() {
#         window.scrollTo(0, 0);
#         document.documentElement.scrollTop = 0;
#         document.body.scrollTop = 0;
#     }, 50);
#     setTimeout(function() {
#         window.scrollTo(0, 0);
#         document.documentElement.scrollTop = 0;
#         document.body.scrollTop = 0;
#     }, 100);
#     setTimeout(function() {
#         window.scrollTo(0, 0);
#     }, 200);
#     </script>
#     """, unsafe_allow_html=True)

#     # 4) One‑shot nonsense/off‑domain banner appears AFTER transcript
#     rendered_banner = False
#     if st.session_state.get("ask_last_reason"):
#         with st.chat_message("assistant"):
#             render_no_match_banner(
#                 reason=st.session_state.get("ask_last_reason", ""),
#                 query=st.session_state.get("ask_last_query", ""),
#                 overlap=st.session_state.get("ask_last_overlap", None),
#                 suppressed=st.session_state.get("__pc_suppressed__", False),
#                 filters=st.session_state.get("filters", {}),
#                 key_prefix="askinline",
#             )
#         rendered_banner = True
#         # Clear flags so the banner doesn't re-render on every rerun
#         st.session_state.pop("ask_last_reason", None)
#         st.session_state.pop("ask_last_query", None)
#         st.session_state.pop("ask_last_overlap", None)
#         # Persist as sticky so it remains visible between user turns unless dismissed
#         st.session_state.setdefault(
#             "__sticky_banner__",
#             {
#                 "reason": (
#                     dec
#                     if (dec := (st.session_state.get("__ask_dbg_decision") or ""))
#                     else "no_match"
#                 ),
#                 "query": st.session_state.get("__ask_dbg_prompt", ""),
#                 "overlap": None,
#                 "suppressed": bool(st.session_state.get("__pc_suppressed__", False)),
#             },
#         )
#     elif True:
#         # Forced fallback: if gating decided no‑match but the flag was not set,
#         # render a banner anyway so the user sees actionable chips.
#         dec = (st.session_state.get("__ask_dbg_decision") or "").strip().lower()
#         no_match_decision = (
#             dec.startswith("rule:")
#             or dec.startswith("low_overlap")
#             or dec == "low_conf"
#             or dec == "no_overlap+low_conf"
#         )
#         if no_match_decision and not st.session_state.get("last_sources"):
#             with st.chat_message("assistant"):
#                 render_no_match_banner(
#                     reason=dec or "no_match",
#                     query=st.session_state.get("__ask_dbg_prompt", ""),
#                     overlap=st.session_state.get("ask_last_overlap", None),
#                     suppressed=st.session_state.get("__pc_suppressed__", False),
#                     filters=st.session_state.get("filters", {}),
#                     key_prefix="askinline_forced",
#                 )
#             rendered_banner = True

#     # Sticky banner temporarily disabled to stabilize chip clicks
#     st.session_state["__sticky_banner__"] = None

#     # 5) Compact answer panel (title • unclamped 5P • view pills • sources)
#     _m = st.session_state.get("answer_modes", {}) or {}
#     _srcs = st.session_state.get("last_sources", []) or []
#     _primary = None
#     if _srcs:
#         _sid = str(_srcs[0].get("id", ""))
#         _primary = next((s for s in stories if str(s.get("id")) == _sid), None)
#     # Suppress the bottom live card when:
#     #  - a banner was rendered this run; or
#     #  - we already have at least one static card snapshot in the transcript
#     has_snapshot_card = any(
#         (isinstance(x, dict) and x.get("type") == "card")
#         for x in st.session_state.get("ask_transcript", [])
#     )
#     if (
#         not rendered_banner
#         and not has_snapshot_card
#         and not st.session_state.get("__suppress_live_card_once__")
#         and (_m or _primary or st.session_state.get("last_answer"))
#     ):
#         # Always render the bottom live card so pills are available.
#         # Snapshot holds only header + one-liner + sources to avoid duplicate body text.
#         render_answer_card_compact(
#             _primary or {"title": "Answer"}, _m, stories, "answer_mode"
#         )

#     # Reset one-shot suppression flag after a render cycle
#     if st.session_state.get("__suppress_live_card_once__"):
#         st.session_state["__suppress_live_card_once__"] = False

#     # 6) Handle a new chat input (command aliases or normal question)
#     # Render the chat input only on the Ask MattGPT tab
#     if st.session_state.get("active_tab") == "Ask MattGPT":
#         user_input_local = st.chat_input("Ask anything…", key="ask_chat_input1")
#     else:
#         user_input_local = None
#     if user_input_local:
#         # If a live card is pending snapshot from the previous answer, snapshot it now
#         if st.session_state.get("__pending_card_snapshot__"):
#             _push_card_snapshot_from_state(stories)
#             st.session_state["__pending_card_snapshot__"] = False

#         # Append user's turn immediately to keep order deterministic
#         _push_user_turn(user_input_local)

#         # Clear context lock for fresh typed questions (not from suggestion chips)
#         if not st.session_state.get("__ask_from_suggestion__"):
#             st.session_state.pop("__ctx_locked__", None)
#             st.session_state.pop("active_context", None)

#         # Command aliases (view switches) should not trigger new retrieval
#         cmd = re.sub(r"\s+", " ", user_input_local.strip().lower())
#         cmd_map = {
#             "narrative": "narrative",
#             "key points": "key_points",
#             "keypoints": "key_points",
#             "deep dive": "deep_dive",
#             "deep-dive": "deep_dive",
#             "details": "deep_dive",
#         }
#         # If a quick command is used without any story context, show a friendly tip
#         has_context = bool(
#             ctx
#             or st.session_state.get("active_story")
#             or st.session_state.get("last_sources")
#         )
#         if cmd in cmd_map and not has_context:
#             _push_assistant_turn(
#                 "Quick mode commands like “key points” work after a story is in context — either select a story or ask a question first so I can cite sources. For now, try asking a full question."
#             )
#             st.rerun()
#         if cmd in cmd_map and (
#             ctx
#             or st.session_state.get("active_story")
#             or st.session_state.get("last_sources")
#         ):
#             # Resolve a target story: explicit context > last active story > last answer’s primary source
#             target = ctx
#             if not target:
#                 sid = st.session_state.get("active_story")
#                 if not sid:
#                     srcs = st.session_state.get("last_sources") or []
#                     if srcs:
#                         sid = srcs[0].get("id")
#                 if sid:
#                     target = next(
#                         (x for x in stories if str(x.get("id")) == str(sid)), None
#                     )

#             if target:
#                 modes_local = story_modes(target)
#                 key = cmd_map[cmd]
#                 heading = {
#                     "narrative": "Narrative",
#                     "key_points": "Key points",
#                     "deep_dive": "Deep dive",
#                 }[key]
#                 answer_md = (
#                     f"**{heading} for _{target.get('title','')} — {target.get('client','')}_**\n\n"
#                     + modes_local.get(key, "")
#                 )

#                 # Prime compact answer state (no assistant bubble)
#                 st.session_state["answer_modes"] = modes_local
#                 st.session_state["answer_mode"] = key
#                 st.session_state["last_answer"] = answer_md
#                 st.session_state["last_sources"] = [
#                     {
#                         "id": target.get("id"),
#                         "title": target.get("Title"),
#                         "client": target.get("Client"),
#                     }
#                 ]
#                 # Show the answer card below the transcript
#                 _push_assistant_turn(answer_md)
#                 # Do NOT snapshot for command aliases; they don't represent a new question
#                 st.rerun()

#         # Normal question → ask backend, persist state, append assistant turn
#         # One-shot context lock: if a story was explicitly selected (chip/CTA),
#         # use that story as context for THIS turn only, then clear the lock.
#         # --- Determine context for THIS turn (one-shot lock) ---
#         ctx_for_this_turn = ctx
#         if st.session_state.pop("__ctx_locked__", False):  # consume the lock
#             try:
#                 locked_ctx = get_context_story(stories)
#             except Exception:
#                 locked_ctx = None
#             if locked_ctx:
#                 ctx_for_this_turn = locked_ctx

#         # --- Ask backend + render result ---
#         with st.status("Searching Matt's experience...", expanded=True) as status:
#             try:
#                 # Consume the suggestion flag (one-shot); we don't need its value here
#                 st.session_state.pop("__ask_from_suggestion__", None)

#                 # Ask is pure semantic; ignore Explore filters here
#                 resp = send_to_backend(user_input_local, {}, ctx_for_this_turn, stories)

#                 # Show confidence after retrieval
#                 sources = resp.get("sources", [])
#                 if sources:
#                     first_id = str(sources[0].get("id", ""))
#                     scores = st.session_state.get("__pc_last_ids__", {}) or {}
#                     conf = scores.get(first_id)
#                     if conf:
#                         conf_pct = int(float(conf) * 100)
#                         st.write(f"✓ Found relevant stories • {conf_pct}% match confidence")

#                 status.update(label="Answer ready!", state="complete", expanded=False)

#             except Exception as e:
#                 status.update(label="Error occurred", state="error")
#                 _push_assistant_turn("Sorry, I couldn't generate an answer right now.")
#                 st.error(f"Backend error: {e}")
#                 st.rerun()

#             else:
#                 set_answer(resp)

#                 # Add a static snapshot so the answer appears in-order as a bubble,
#                 # and suppress the bottom live card once to avoid duplication.
#                 if not st.session_state.get(
#                     "ask_last_reason"
#                 ) and not st.session_state.get("__sticky_banner__"):
#                     _push_card_snapshot_from_state(stories)
#                     st.session_state["__suppress_live_card_once__"] = True

#                 st.rerun()