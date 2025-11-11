"""
Ask MattGPT Conversation View

Active conversation UI with:
- Purple header with Agy branding
- Chat transcript rendering (user/assistant bubbles)
- Source cards and follow-up suggestions
- Chat input with "Ask Agy" button
- Integration with backend RAG service

Phase 5.1 Complete: All helper functions extracted to conversation_helpers.py
"""

import re
import streamlit as st
import streamlit.components.v1 as components
from typing import List, Dict, Optional

# Import from refactored modules
from ui.pages.ask_mattgpt.backend_service import send_to_backend
from ui.pages.ask_mattgpt.utils import (
    get_context_story,
    story_modes,
    push_user_turn as _push_user_turn,
    push_assistant_turn as _push_assistant_turn,
    push_conversational_answer as _push_conversational_answer,
    ensure_ask_bootstrap as _ensure_ask_bootstrap,
)
from ui.components.footer import render_footer
from ui.components.story_detail import render_story_detail
from config.debug import DEBUG
from utils.ui_helpers import safe_container, dbg

# Import extracted helpers from Phase 5.1
from ui.pages.ask_mattgpt.conversation_helpers import (
    render_compact_context_banner,
    set_answer,
    _render_ask_transcript,
)
from ui.pages.ask_mattgpt.styles import get_conversation_css, get_loading_animation_css

# Environment variables for debugging
try:
    from services.pinecone_service import (
        VECTOR_BACKEND,
        PINECONE_INDEX_NAME,
        PINECONE_NAMESPACE,
    )
except ImportError:
    VECTOR_BACKEND = "unknown"
    PINECONE_INDEX_NAME = "unknown"
    PINECONE_NAMESPACE = "unknown"


def render_conversation_view(stories: List[Dict]):
    """
    Render active conversation view.
    NAVBAR IS RENDERED BY PARENT - NO NAVBAR CSS HERE

    NOTE: This is Phase 5 extraction - massive CSS and UI logic (~2281 lines).
    Full helper function extraction pending in Phase 5.1.
    """

    # ============================================================================
    # INJECT CSS from styles.py
    # ============================================================================
    st.markdown(get_conversation_css(), unsafe_allow_html=True)

    # ============================================================================
    # HEADER - Purple gradient with Agy avatar
    # ============================================================================

    st.markdown(
        """
        <div class="conversation-header">
            <div class="conversation-header-content">
                <img class="conversation-agy-avatar"
                     src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_avatar.png"
                     width="64" height="64" alt="Agy"/>
                <div class="conversation-header-text">
                    <h1>Ask MattGPT</h1>
                    <p>Meet Agy 🐾 — Tracking down insights from 20+ years of transformation experience</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ============================================================================
    # STATUS BAR
    # ============================================================================

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

    # ============================================================================
    # HOW AGY SEARCHES MODAL
    # ============================================================================

    def toggle_how_modal():
        """Centralized toggle for modal visibility state."""
        st.session_state["show_how_modal"] = not st.session_state.get("show_how_modal", False)
        st.rerun()

    if st.button("🔍 How Agy searches", key="how_works_top"):
        toggle_how_modal()

    if st.session_state.get("show_how_modal", False):
        # Auto-scroll to top
        st.markdown(
            """
            <script>
            window.scrollTo({top: 0, behavior: 'smooth'});
            </script>
            """,
            unsafe_allow_html=True,
        )

        # Modal container
        with st.container(border=True):
            # Header with close button
            col1, col2 = st.columns([10, 1])

            with col1:
                st.markdown("## 🔍 How Agy Finds Your Stories")

            with col2:
                if st.button("✕", key="close_how", help="Close"):
                    toggle_how_modal()

            st.markdown("---")

            # 3-step flow visualization
            # TODO: Full HTML content from lines 2022-2285 of original
            st.markdown("**3-Step Search Process:**")
            st.markdown("1. **You Ask** - Natural language query")
            st.markdown("2. **Agy Searches** - Semantic + keyword + smart filtering")
            st.markdown("3. **You Get Results** - Ranked stories with metadata")

    # ============================================================================
    # CONTEXT BANNER (if story selected from Explore)
    # ============================================================================

    ctx = get_context_story(stories)
    _show_ctx = bool(ctx) and (
        st.session_state.get("__ctx_locked__") or st.session_state.get("__asked_once__")
    )

    if _show_ctx and render_compact_context_banner:
        render_compact_context_banner(stories)

    # ============================================================================
    # DEBUG INFO
    # ============================================================================

    if DEBUG:
        try:
            _dbg_flags = {
                "vector": VECTOR_BACKEND,
                "index": PINECONE_INDEX_NAME or "-",
                "ns": PINECONE_NAMESPACE or "-",
                "has_last": bool(st.session_state.get("last_sources")),
            }
            st.caption("🧪 " + ", ".join(f"{k}={v}" for k, v in _dbg_flags.items()))
        except Exception:
            pass

    # ============================================================================
    # TRANSCRIPT BOOTSTRAP
    # ============================================================================

    _ensure_ask_bootstrap()

    # ============================================================================
    # CHIP INJECTION PROCESSING
    # ============================================================================

    # Handle seed prompts and chip clicks
    seed = st.session_state.pop("seed_prompt", None)
    injected = st.session_state.pop("__inject_user_turn__", None)
    pending = seed or injected

    processing_state = st.session_state.get("__processing_chip_injection__")

    if pending and not processing_state:
        # Step 1: Push user turn and set processing
        _push_user_turn(pending)
        st.session_state["__processing_chip_injection__"] = {"query": pending, "step": "pending"}
        st.rerun()

    elif isinstance(processing_state, dict) and processing_state.get("step") == "pending":
        # Step 2: Show indicator
        st.session_state["__processing_chip_injection__"] = {
            "query": processing_state["query"],
            "step": "processing"
        }

    elif isinstance(processing_state, dict) and processing_state.get("step") == "processing":
        # Step 3: Actually process
        pending_query = processing_state["query"]

        try:
            resp = send_to_backend(pending_query, {}, ctx, stories)
        except Exception as e:
            print(f"DEBUG: send_to_backend failed: {e}")
            _push_assistant_turn(f"Error: {str(e)}")
            st.session_state["__processing_chip_injection__"] = False
            st.rerun()
        else:
            if set_answer:
                set_answer(resp)

            # Push conversational answer
            if not st.session_state.get("ask_last_reason"):
                answer_text = resp.get("answer_md") or resp.get("answer", "")
                sources = resp.get("sources", []) or []
                _push_conversational_answer(answer_text, sources)
                st.session_state["__suppress_live_card_once__"] = True
            elif st.session_state.get("ask_last_reason"):
                # Nonsense detected
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

                # Clear flags
                st.session_state.pop("ask_last_reason", None)
                st.session_state.pop("ask_last_query", None)
                st.session_state.pop("ask_last_overlap", None)

            st.session_state["__processing_chip_injection__"] = False
            st.rerun()

    # ============================================================================
    # RENDER TRANSCRIPT
    # ============================================================================

    if _render_ask_transcript:
        _render_ask_transcript(stories)
    else:
        # Fallback: simple transcript rendering
        st.info("Transcript rendering helper pending extraction (Phase 5.1)")

    # ============================================================================
    # THINKING INDICATOR
    # ============================================================================

    show_thinking = isinstance(processing_state, dict) and processing_state.get("step") in ["pending", "processing"]

    if show_thinking:
        st.markdown(
            """
            <div style='position: fixed; bottom: 140px; left: 50%; transform: translateX(-50%);
                        background: #F3F4F6; padding: 12px 24px; border-radius: 24px;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); z-index: 9999;'>
                🐾 Tracking down insights...
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ============================================================================
    # CHAT INPUT HANDLER
    # ============================================================================

    user_input_local = None
    if st.session_state.get("active_tab") == "Ask MattGPT":
        user_input_local = st.chat_input("💬 Ask a follow-up question...", key="ask_chat_input1")

    if user_input_local:
        # Push user turn
        _push_user_turn(user_input_local)

        # Clear context lock for fresh questions
        if not st.session_state.get("__ask_from_suggestion__"):
            st.session_state.pop("__ctx_locked__", None)
            st.session_state.pop("active_context", None)

        # Command aliases (view switches)
        cmd = re.sub(r"\s+", " ", user_input_local.strip().lower())
        cmd_map = {
            "narrative": "narrative",
            "key points": "key_points",
            "keypoints": "key_points",
            "deep dive": "deep_dive",
            "details": "deep_dive",
        }

        # Check for command aliases
        has_context = bool(ctx or st.session_state.get("last_sources"))

        if cmd in cmd_map and not has_context:
            _push_assistant_turn(
                "Quick mode commands like 'key points' work after a story is in context. "
                "Try asking a full question first."
            )
            st.rerun()

        if cmd in cmd_map and has_context:
            # Handle view mode switching
            target = ctx
            if not target:
                srcs = st.session_state.get("last_sources") or []
                if srcs:
                    sid = srcs[0].get("id")
                    target = next((x for x in stories if str(x.get("id")) == str(sid)), None)

            if target:
                modes_local = story_modes(target)
                key = cmd_map[cmd]
                heading = {"narrative": "Narrative", "key_points": "Key points", "deep_dive": "Deep dive"}[key]
                answer_md = f"**{heading}**\n\n" + modes_local.get(key, "")

                st.session_state["answer_mode"] = key
                st.session_state["last_answer"] = answer_md
                _push_assistant_turn(answer_md)
                st.rerun()

        # Normal question processing
        ctx_for_this_turn = ctx
        if st.session_state.pop("__ctx_locked__", False):
            locked_ctx = get_context_story(stories)
            if locked_ctx:
                ctx_for_this_turn = locked_ctx

        # Show loading indicator
        loading_container = st.empty()
        with loading_container:
            with st.chat_message(
                "assistant",
                avatar="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/svg/agy_icon_color.svg",
            ):
                st.markdown("🐾 Tracking down insights...")

        try:
            st.session_state.pop("__ask_from_suggestion__", None)
            resp = send_to_backend(user_input_local, {}, ctx_for_this_turn, stories)
            loading_container.empty()
        except Exception as e:
            loading_container.empty()
            _push_assistant_turn("Sorry, I couldn't generate an answer right now.")
            st.error(f"Backend error: {e}")
            st.rerun()
        else:
            if set_answer:
                set_answer(resp)

            # Push conversational answer
            if not st.session_state.get("ask_last_reason"):
                answer_text = resp.get("answer_md") or resp.get("answer", "")
                sources = resp.get("sources", []) or []
                _push_conversational_answer(answer_text, sources)
                st.session_state["__suppress_live_card_once__"] = True
            elif st.session_state.get("ask_last_reason"):
                # Nonsense detected
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

                # Clear flags
                st.session_state.pop("ask_last_reason", None)
                st.session_state.pop("ask_last_query", None)
                st.session_state.pop("ask_last_overlap", None)

            st.rerun()

    # Footer is hidden in conversation view (CSS handles this)
