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

from config.debug import DEBUG
from ui.components.ask_mattgpt_header import (
    render_header,
    render_modal_wrapper_end,
    render_modal_wrapper_start,
    render_status_bar,
)
from ui.components.how_agy_modal import (
    get_how_agy_flow_html,
    get_technical_details_html,
)
from ui.components.thinking_indicator import render_thinking_indicator

# Import from refactored modules
from ui.pages.ask_mattgpt.backend_service import send_to_backend

# Import extracted helpers from Phase 5.1
from ui.pages.ask_mattgpt.conversation_helpers import (
    _render_ask_transcript,
    set_answer,
)
from ui.pages.ask_mattgpt.styles import (
    get_conversation_css,
)
from ui.pages.ask_mattgpt.utils import (
    ensure_ask_bootstrap as _ensure_ask_bootstrap,
    get_context_story,
    push_assistant_turn as _push_assistant_turn,
    push_conversational_answer as _push_conversational_answer,
    push_user_turn as _push_user_turn,
    story_modes,
)

# Environment variables for debugging
try:
    from services.pinecone_service import (
        PINECONE_INDEX_NAME,
        PINECONE_NAMESPACE,
        VECTOR_BACKEND,
    )
except ImportError:
    VECTOR_BACKEND = "unknown"
    PINECONE_INDEX_NAME = "unknown"
    PINECONE_NAMESPACE = "unknown"


def render_conversation_view(stories: list[dict]):
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
    # INJECT JAVASCRIPT to force input styling (Streamlit emotion classes workaround)
    # ============================================================================
    st.markdown(
        """
        <script>
        function forceInputStyling() {
            const chatInput = document.querySelector('[data-testid="stChatInput"]');
            if (chatInput) {
                // Kill borders on everything EXCEPT textarea and button
                chatInput.querySelectorAll('*').forEach(function(el) {
                    if (el.tagName !== 'TEXTAREA' && el.tagName !== 'BUTTON') {
                        el.style.setProperty('border', 'none', 'important');
                        el.style.setProperty('border-left', 'none', 'important');
                        el.style.setProperty('box-shadow', 'none', 'important');
                    }
                });
            }
        }

        setTimeout(forceInputStyling, 100);
        setTimeout(forceInputStyling, 500);
        setTimeout(forceInputStyling, 1000);

        const observer = new MutationObserver(() => setTimeout(forceInputStyling, 50));
        observer.observe(document.body, { childList: true, subtree: true });
        </script>
    """,
        unsafe_allow_html=True,
    )

    # ============================================================================
    # HEADER - Purple gradient with Agy avatar
    # ============================================================================
    # NEW: Single call renders header with integrated button
    # Header with button
    render_header(include_button=True, view="conversation")

    # ============================================================================
    # HOW AGY SEARCHES MODAL
    # ============================================================================
    # Modal (if open)
    if st.session_state.get("show_how_modal", False):
        st.markdown(render_modal_wrapper_start(), unsafe_allow_html=True)
        components.html(get_how_agy_flow_html(), height=1160)
        components.html(get_technical_details_html(), height=740)
        st.markdown(render_modal_wrapper_end(), unsafe_allow_html=True)
        # Remove: render_modal_close_wiring_js()

    # ============================================================================
    # STATUS BAR
    # ============================================================================
    st.markdown(render_status_bar(), unsafe_allow_html=True)

    # ============================================================================
    # CONTEXT (get story for later use)
    # ============================================================================

    ctx = get_context_story(stories)

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
        st.session_state["__processing_chip_injection__"] = {
            "query": pending,
            "step": "pending",
        }
        st.rerun()

    elif (
        isinstance(processing_state, dict) and processing_state.get("step") == "pending"
    ):
        # Step 2: Show indicator and trigger rerun to render it
        st.session_state["__processing_chip_injection__"] = {
            "query": processing_state["query"],
            "step": "processing",
        }
        st.rerun()  # PUT THIS BACK

    elif (
        isinstance(processing_state, dict)
        and processing_state.get("step") == "processing"
    ):
        # Step 3: Actually process WITH indicator
        pending_query = processing_state["query"]

        # Show indicator DURING processing
        indicator_placeholder = st.empty()
        with indicator_placeholder:
            render_thinking_indicator()

        try:
            resp = send_to_backend(pending_query, {}, ctx, stories)
            indicator_placeholder.empty()  # Clear indicator
        except Exception as e:
            indicator_placeholder.empty()
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
                query_intent = st.session_state.get("__ask_query_intent__")
                _push_conversational_answer(answer_text, sources, query_intent)
                st.session_state["__suppress_live_card_once__"] = True
            elif st.session_state.get("ask_last_reason"):
                # Nonsense detected
                reason = st.session_state.get("ask_last_reason", "")
                query = st.session_state.get("ask_last_query", "")
                overlap = st.session_state.get("ask_last_overlap", None)

                st.session_state["ask_transcript"].append(
                    {
                        "type": "banner",
                        "Role": "assistant",
                        "reason": reason,
                        "query": query,
                        "overlap": overlap,
                    }
                )

                # Clear flags
                st.session_state.pop("ask_last_reason", None)
                st.session_state.pop("ask_last_query", None)
                st.session_state.pop("ask_last_overlap", None)

            st.session_state["__processing_chip_injection__"] = False
            st.rerun()

    # ============================================================================
    # THINKING INDICATOR (check BEFORE rendering transcript)
    # ============================================================================

    # Get current processing state
    processing_state = st.session_state.get("__processing_chip_injection__")

    # Check if we're in the middle of processing
    is_processing = isinstance(processing_state, dict) and processing_state.get(
        "step"
    ) in ["pending", "processing"]

    if is_processing:
        render_thinking_indicator()

    # ============================================================================
    # RENDER TRANSCRIPT
    # ============================================================================
    # DEBUG - check transcript order
    if DEBUG:
        print("DEBUG: Transcript order before render:")
        for i, m in enumerate(st.session_state.get("ask_transcript", [])):
            msg_type = m.get("type", "text")
            role = m.get("role", "?")
            text_preview = str(m.get("text", m.get("query", m.get("answer_md", ""))))[
                :60
            ]
            print(f"  [{i}] {role}/{msg_type}: {text_preview}")

    if _render_ask_transcript:
        _render_ask_transcript(stories)
    else:
        # Fallback: simple transcript rendering
        st.info("Transcript rendering helper pending extraction (Phase 5.1)")

    # ============================================================================
    # CHAT INPUT HANDLER
    # ============================================================================

    user_input_local = None
    if st.session_state.get("active_tab") == "Ask MattGPT":
        user_input_local = st.chat_input("Ask a follow-up...", key="ask_chat_input1")

        # Add "Powered by" text below input
        st.markdown(
            '<div class="conversation-powered-by">Powered by OpenAI GPT-4o-mini with semantic search across 130+ project case studies</div>',
            unsafe_allow_html=True,
        )

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
            render_thinking_indicator()

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
                query_intent = st.session_state.get("__ask_query_intent__")
                _push_conversational_answer(answer_text, sources, query_intent)
                st.session_state["__suppress_live_card_once__"] = True
            elif st.session_state.get("ask_last_reason"):
                # Nonsense detected
                reason = st.session_state.get("ask_last_reason", "")
                query = st.session_state.get("ask_last_query", "")
                overlap = st.session_state.get("ask_last_overlap", None)

                st.session_state["ask_transcript"].append(
                    {
                        "type": "banner",
                        "Role": "assistant",
                        "reason": reason,
                        "query": query,
                        "overlap": overlap,
                    }
                )

                # Clear flags
                st.session_state.pop("ask_last_reason", None)
                st.session_state.pop("ask_last_query", None)
                st.session_state.pop("ask_last_overlap", None)

            st.rerun()

    # Footer is hidden in conversation view (CSS handles this)
