"""
Ask MattGPT Module - Router

Main entry point for Ask MattGPT feature with clean view routing.

Architecture:
- story_intelligence: Theme inference and context building (Agy V2)
- shared_state: Session state management
- backend_service: RAG orchestration with OpenAI
- utils: Shared helper functions
- landing_view: Empty state with suggestion chips
- conversation_view: Active chat with transcript
- conversation_helpers: Rendering helpers (TODO Phase 5.1)

This router determines whether to show landing or conversation view
based on session state and provides the main render function.
"""

import streamlit as st

from ui.pages.ask_mattgpt.conversation_view import render_conversation_view
from ui.pages.ask_mattgpt.landing_view import render_landing_page
from ui.pages.ask_mattgpt.shared_state import init_ask_mattgpt_state
from ui.pages.ask_mattgpt.utils import is_empty_conversation


def render_ask_mattgpt(stories: list[dict]):
    """
    Main entry point for Ask MattGPT.

    Routes between:
    - Landing view: Empty conversation state (suggestion chips)
    - Conversation view: Active transcript with messages

    Args:
        stories: All available stories for search
    """

    # Initialize session state
    init_ask_mattgpt_state()

    # Force conversation view if:
    # 1. show_ask_panel flag is set (from Explore Stories)
    # 2. seed_prompt is pending (from story detail)
    # 3. Transcript has actual messages
    force_conversation = (
        st.session_state.get("show_ask_panel")
        or st.session_state.get("seed_prompt")
        or not is_empty_conversation()
    )
    show_landing = not force_conversation

    # Route to appropriate view
    if show_landing:
        render_landing_page(stories)
    else:
        render_conversation_view(stories)


# Export main function
__all__ = ["render_ask_mattgpt"]
