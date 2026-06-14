"""
Thinking Indicator Component

Renders animated thinking indicator with Agy's tennis ball chase animation.
"""

import random

import streamlit as st

THINKING_MESSAGES = [
    "Tracking down insights...",
    "Digging deeper...",
    "Sniffing out the details...",
    "Fetching more info...",
    "On the trail...",
    "Hunting for the good stuff...",
    "Following the scent...",
    "Nosing through the archives...",
    "Hot on the trail...",
    "Pawing through projects...",
    "Chasing down the answer...",
    "Picking up the scent...",
    "Ears perked, searching...",
    "Tail wagging, almost there...",
    "Good boy mode activated...",
]


def get_thinking_message():
    """Get a random thinking message, avoiding repeats."""
    last = st.session_state.get("_last_thinking_msg")
    choices = [m for m in THINKING_MESSAGES if m != last]
    message = random.choice(choices)
    st.session_state["_last_thinking_msg"] = message
    return message


def render_thinking_indicator(message=None):
    """Render animated thinking indicator with backdrop."""
    if message is None:
        message = get_thinking_message()

    st.markdown(
        f"""
        <div class="thinking-backdrop"></div>
        <div class="thinking-modal">
            <img class="thinking-ball" src="..." alt=""/>
            <span class="thinking-text">
                <span class="thinking-paw">🐾</span>{message}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
