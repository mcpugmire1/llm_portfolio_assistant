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
            <style>
            .thinking-backdrop {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.4);
                z-index: 99998;
            }}
            @keyframes chaseAnimation {{
                0% {{ content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_1.png'); }}
                33.33% {{ content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_2.png'); }}
                66.66% {{ content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_3.png'); }}
                100% {{ content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_1.png'); }}
            }}
            .thinking-ball {{
                width: 40px;
                height: 40px;
                animation: chaseAnimation 0.9s steps(3) infinite;
            }}
        </style>
        <div class="thinking-backdrop"></div>
        <div style='position: fixed; bottom: 140px; left: 50%; transform: translateX(-50%);
                background: var(--bg-card); padding: 12px 24px; border-radius: 24px;
                border: 1px solid var(--border-color);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3); z-index: 99999;
                display: flex; align-items: center; gap: 12px;'>
        <img class="thinking-ball" src="..." style="width: 40px; height: 40px;" alt=""/>
        <span style='color: var(--text-primary); font-weight: 500; font-size: 15px;'>
            <span style='font-size: 20px; margin-right: 6px;'>🐾</span>{message}
        </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
