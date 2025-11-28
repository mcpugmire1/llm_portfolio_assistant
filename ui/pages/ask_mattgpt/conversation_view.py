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
        st.session_state["show_how_modal"] = not st.session_state.get(
            "show_how_modal", False
        )
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
                height=1000,
            )

            st.markdown("---")

            # Technical Details
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
                height=440,
            )

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

    print(f"DEBUG CHIP: seed={seed}, injected={injected}, pending={pending}")
    print(f"DEBUG CHIP: processing_state={processing_state}")

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
                _push_conversational_answer(answer_text, sources)
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
        user_input_local = st.chat_input(
            "💬 Ask a follow-up question...", key="ask_chat_input1"
        )

        # Add "Powered by" text below input
        st.markdown(
            '<div class="conversation-powered-by">Powered by OpenAI GPT-4o-mini with semantic search across 120+ project case studies</div>',
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
                _push_conversational_answer(answer_text, sources)
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
