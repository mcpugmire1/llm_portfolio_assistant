"""
Shared State Management for Ask MattGPT

Provides explicit namespacing and ownership of session state keys.
Prevents state collisions between landing and conversation views.
"""

import streamlit as st


class AskMattGPTState:
    """Manages session state for Ask MattGPT with clear view boundaries."""

    # ========== SHARED STATE ==========
    # Used by both landing and conversation views

    @staticmethod
    def get_transcript() -> list[dict]:
        """Get conversation transcript (shared)."""
        return st.session_state.get("ask_transcript", [])

    @staticmethod
    def set_transcript(value: list[dict]):
        """Set conversation transcript (shared)."""
        st.session_state["ask_transcript"] = value

    @staticmethod
    def clear_transcript():
        """Clear conversation transcript."""
        st.session_state["ask_transcript"] = []

    @staticmethod
    def has_conversation() -> bool:
        """Check if conversation exists."""
        return bool(st.session_state.get("ask_transcript"))

    # ========== LANDING VIEW STATE ==========
    # Only used by landing_view.py

    @staticmethod
    def get_landing_query() -> str:
        """Get landing page input value."""
        return st.session_state.get("landing_query_input", "")

    @staticmethod
    def set_landing_query(value: str):
        """Set landing page input value."""
        st.session_state["landing_query_input"] = value

    @staticmethod
    def is_processing_landing() -> bool:
        """Check if landing page is processing a query."""
        return st.session_state.get("__landing_processing__", False)

    @staticmethod
    def set_processing_landing(value: bool):
        """Set landing page processing state."""
        st.session_state["__landing_processing__"] = value

    # ========== CONVERSATION VIEW STATE ==========
    # Only used by conversation_view.py

    @staticmethod
    def get_conv_input() -> str:
        """Get conversation input value."""
        return st.session_state.get("ask_input_value", "")

    @staticmethod
    def set_conv_input(value: str):
        """Set conversation input value."""
        st.session_state["ask_input_value"] = value

    @staticmethod
    def is_processing_chip() -> bool:
        """Check if processing chip injection."""
        return st.session_state.get("__processing_chip_injection__", False)

    @staticmethod
    def set_processing_chip(value: bool):
        """Set chip injection processing state."""
        st.session_state["__processing_chip_injection__"] = value

    @staticmethod
    def get_inject_user_turn() -> str | None:
        """Get pending user turn injection."""
        return st.session_state.get("__inject_user_turn__")

    @staticmethod
    def set_inject_user_turn(value: str | None):
        """Set pending user turn injection."""
        if value is None:
            st.session_state.pop("__inject_user_turn__", None)
        else:
            st.session_state["__inject_user_turn__"] = value

    # ========== NONSENSE DETECTION STATE ==========
    # Shared between backend and views

    @staticmethod
    def get_nonsense_reason() -> str | None:
        """Get nonsense detection reason."""
        return st.session_state.get("ask_last_reason")

    @staticmethod
    def set_nonsense_reason(value: str | None):
        """Set nonsense detection reason."""
        if value is None:
            st.session_state.pop("ask_last_reason", None)
        else:
            st.session_state["ask_last_reason"] = value

    @staticmethod
    def get_last_query() -> str | None:
        """Get last query that was checked."""
        return st.session_state.get("ask_last_query")

    @staticmethod
    def set_last_query(value: str | None):
        """Set last query that was checked."""
        if value is None:
            st.session_state.pop("ask_last_query", None)
        else:
            st.session_state["ask_last_query"] = value

    @staticmethod
    def get_last_overlap() -> float | None:
        """Get last token overlap ratio."""
        return st.session_state.get("ask_last_overlap")

    @staticmethod
    def set_last_overlap(value: float | None):
        """Set last token overlap ratio."""
        if value is None:
            st.session_state.pop("ask_last_overlap", None)
        else:
            st.session_state["ask_last_overlap"] = value

    @staticmethod
    def clear_nonsense_flags():
        """Clear all nonsense detection flags."""
        st.session_state.pop("ask_last_reason", None)
        st.session_state.pop("ask_last_query", None)
        st.session_state.pop("ask_last_overlap", None)

    # ========== NAVIGATION STATE ==========
    # Controls view switching

    @staticmethod
    def should_show_conversation() -> bool:
        """Determine if conversation view should be shown."""
        # Show conversation if:
        # 1. Transcript exists
        # 2. Coming from suggestion
        # 3. show_ask_panel is set
        return (
            AskMattGPTState.has_conversation()
            or st.session_state.get("__ask_from_suggestion__", False)
            or st.session_state.get("show_ask_panel", False)
        )

    @staticmethod
    def clear_transition_flags():
        """Clear transition-related flags."""
        st.session_state.pop("show_transition_indicator", None)
        st.session_state.pop("__ask_from_suggestion__", None)

    @staticmethod
    def set_show_ask_panel(value: bool):
        """Set show_ask_panel flag."""
        st.session_state["show_ask_panel"] = value

    # ========== EXPLORE STORIES INTEGRATION ==========
    # Manages state when coming from Explore Stories

    @staticmethod
    def get_active_story() -> str | None:
        """Get active story ID."""
        return st.session_state.get("active_story")

    @staticmethod
    def set_active_story(value: str | None):
        """Set active story ID."""
        if value is None:
            st.session_state.pop("active_story", None)
        else:
            st.session_state["active_story"] = value

    @staticmethod
    def get_active_story_obj() -> dict | None:
        """Get active story object."""
        return st.session_state.get("active_story_obj")

    @staticmethod
    def set_active_story_obj(value: dict | None):
        """Set active story object."""
        if value is None:
            st.session_state.pop("active_story_obj", None)
        else:
            st.session_state["active_story_obj"] = value

    @staticmethod
    def get_transcript_source_expanded_id() -> str | None:
        """Get expanded transcript source ID."""
        return st.session_state.get("transcript_source_expanded_id")

    @staticmethod
    def set_transcript_source_expanded_id(value: str | None):
        """Set expanded transcript source ID."""
        if value is None:
            st.session_state.pop("transcript_source_expanded_id", None)
        else:
            st.session_state["transcript_source_expanded_id"] = value

    @staticmethod
    def clear_explore_stories_state():
        """Clear Explore Stories-specific state when entering Ask MattGPT."""
        st.session_state.pop("active_story", None)
        st.session_state.pop("active_story_obj", None)
        st.session_state.pop("transcript_source_expanded_id", None)

    # ========== FILTERS ==========

    @staticmethod
    def get_filters() -> dict:
        """Get current search filters."""
        return st.session_state.get("filters", {})

    @staticmethod
    def set_filters(value: dict):
        """Set search filters."""
        st.session_state["filters"] = value


# Convenience function for initialization
def init_ask_mattgpt_state():
    """Initialize all Ask MattGPT session state with defaults."""
    if "ask_transcript" not in st.session_state:
        st.session_state["ask_transcript"] = []
    if "filters" not in st.session_state:
        st.session_state["filters"] = {}
