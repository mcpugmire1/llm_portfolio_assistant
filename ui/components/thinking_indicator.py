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


def render_thinking_indicator(message=None, mount="overlay"):
    """Render animated thinking indicator.

    mount="overlay" (default): centered fixed-position modal with a
    full-viewport backdrop scrim. Used by Ask Agy conversation, Ask
    Agy landing, and Explore Stories.

    mount="inline": no scrim, no fixed positioning -- the modal
    renders in normal flow at its call site. Used by Role Match to
    render the indicator inside the results column. Preserves nav
    and form interactivity during the assessment; the scrim's
    incidental click-blocking is replaced by explicit disabled=
    guards on Clear and Submit."""
    if message is None:
        message = get_thinking_message()

    if mount == "inline":
        backdrop = ""
        modal_classes = "thinking-modal thinking-inline"
    else:
        backdrop = '<div class="thinking-backdrop"></div>'
        modal_classes = "thinking-modal"

    st.markdown(
        f"""
        {backdrop}
        <div class="{modal_classes}">
            <div class="thinking-ball">🎾</div>
            <span class="thinking-text">
                <span class="thinking-paw">🐾</span>{message}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
