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

    # Navbar-specific CSS - target by container class
    st.markdown(f"""
    <style>
    /* Target the horizontal block that contains elements with st-key-topnav_ class */
    div[data-testid="stHorizontalBlock"]:has([class*="st-key-topnav_"]) {{
        background: {COLORS['dark_navy']} !important;
        padding: {SPACING['nav_padding']} !important;
        margin: -1rem -1rem 1rem -1rem !important;
        border-radius: 0 !important;
    }}

    /* Target columns within the nav container */
    div[data-testid="stHorizontalBlock"]:has([class*="st-key-topnav_"]) > div[data-testid="column"] {{
        background: {COLORS['dark_navy']} !important;
    }}

    /* Style navigation buttons by targeting their containers */
    [class*="st-key-topnav_"] button {{
        background: transparent !important;
        color: white !important;
        border: none !important;
        font-weight: 500 !important;
        box-shadow: none !important;
    }}

    /* Hover state */
    [class*="st-key-topnav_"] button:hover {{
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }}

    /* Disabled state */
    [class*="st-key-topnav_"] button:disabled {{
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