"""
Navigation Bar Component

Dark navy navigation bar matching wireframe specifications.
Uses Streamlit container with CSS scoping to prevent bleeding.
"""

import streamlit as st
from config.theme import COLORS, SPACING

def render_navbar(current_tab: str = "Home"):
    """
    Render top navigation bar with tab selection.

    Args:
        current_tab: Currently active tab name

    Returns:
        None (updates session state and triggers rerun on navigation)
    """

    # Navbar-specific CSS - target the container by its unique characteristics
    st.markdown(f"""
    <style>
    /* Target the navigation container by looking for the specific button pattern */
    /* This selector finds the horizontal block that contains our 4 navigation buttons */
    div[data-testid="stHorizontalBlock"]:has(button[key*="topnav_"]) {{
        background: {COLORS['dark_navy']} !important;
        padding: {SPACING['nav_padding']} !important;
        margin: -1rem -1rem 1rem -1rem !important;
        border-radius: 0 !important;
    }}

    /* Target columns within the nav container */
    div[data-testid="stHorizontalBlock"]:has(button[key*="topnav_"]) > div[data-testid="column"] {{
        background: {COLORS['dark_navy']} !important;
    }}

    /* Style ONLY navigation buttons (identified by key prefix) */
    button[key^="topnav_"] {{
        background: transparent !important;
        color: white !important;
        border: none !important;
        font-weight: 500 !important;
        box-shadow: none !important;
    }}

    /* Hover state for nav buttons */
    button[key^="topnav_"]:hover {{
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }}

    /* Active/disabled state for nav buttons */
    button[key^="topnav_"]:disabled {{
        background: {COLORS['dark_navy_hover']} !important;
        color: white !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Use Streamlit container to group navigation elements
    with st.container():
        # Navigation tabs
        labels = [
            ("Home", "Home"),
            ("Explore Stories", "Explore Stories"),
            ("Ask MattGPT", "Ask MattGPT"),
            ("About Matt", "About Matt"),
        ]

        cols = st.columns(len(labels), gap="small")

        for i, (label, name) in enumerate(labels):
            with cols[i]:
                if st.button(
                    label,
                    use_container_width=True,
                    key=f"topnav_{name}",
                    type="secondary",
                    disabled=(name == current_tab),
                ):
                    st.session_state["active_tab"] = name
                    st.rerun()
