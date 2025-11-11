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

from typing import List, Dict
import streamlit as st

from ui.pages.ask_mattgpt.landing_view import render_landing_page
from ui.pages.ask_mattgpt.conversation_view import render_conversation_view
from ui.pages.ask_mattgpt.utils import is_empty_conversation
from ui.pages.ask_mattgpt.shared_state import init_ask_mattgpt_state


def render_ask_mattgpt(stories: List[Dict]):
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

    # Determine which view to show
    # Show landing if:
    # 1. No transcript exists, OR
    # 2. Transcript is empty or only has bootstrap message
    show_landing = is_empty_conversation()

    # Handle landing query processing (if user submitted from landing page)
    if st.session_state.get("processing_suggestion") and st.session_state.get("pending_query"):
        # User submitted from landing - transition to conversation view
        show_landing = False

    # Route to appropriate view
    if show_landing:
        render_landing_page(stories)
    else:
        render_conversation_view(stories)


# Export main function
__all__ = ["render_ask_mattgpt"]
