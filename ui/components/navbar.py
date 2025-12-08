"""
Navigation Bar Component

Dark navy navigation bar matching wireframe specifications.
Uses Streamlit container with CSS scoping to prevent bleeding.
"""

import streamlit as st
import streamlit.components.v1 as components


def render_navbar(current_tab: str = "Home"):
    """
    Render top navigation bar with tab selection.

    Args:
        current_tab: Currently active tab name

    Returns:
        None (updates session state and triggers rerun on navigation)
    """

    # Navbar-specific CSS - target by container class
    st.markdown(
        """
    <style>
        div[data-testid="stHorizontalBlock"]:has([class*="st-key-topnav_"]) {
            background: var(--dark-navy) !important;
            padding: 16px 40px !important;  /* 16px top + 16px bottom = 72px height with 40px text */
            margin: 40px 0 0 0 !important;  /* Pull up 40px = 20px breathing room (60px header - 40px pull) */
            height: 72px !important;
            border-radius: 0 !important;
            position: relative !important;
            z-index: 999998 !important;
        }

        /* Target columns within the nav container */
        div[data-testid="stHorizontalBlock"]:has([class*="st-key-topnav_"]) > div[data-testid="column"] {
            background: var(--dark-navy) !important;
        }

        /* Style navigation buttons by targeting their containers */
        [class*="st-key-topnav_"] button {
            background: transparent !important;
            color: white !important;
            border: none !important;
            font-weight: 500 !important;
            box-shadow: none !important;
            padding: 8px 16px !important;
            margin-top: 0 !important;
        }

        /* Hover state */
        [class*="st-key-topnav_"] button:hover {
            background: rgba(255, 255, 255, 0.1) !important;
            color: white !important;
        }

        /* Disabled state */
        [class*="st-key-topnav_"] button:disabled {
            background: var(--dark-navy-hover) !important;
            color: white !important;
            font-weight: 600 !important;
            opacity: 1 !important;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

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
                    # Set flag to clear Ask MattGPT story selection when switching to Explore Stories
                    if name == "Explore Stories":
                        st.session_state["_just_switched_to_explore"] = True
                    st.rerun()
    # Theme detection JS (at the very end)
    components.html(
        """
    <script>
    (function() {
        function detectTheme() {
            var body = window.parent.document.body;
            var bg = window.parent.getComputedStyle(body).backgroundColor;

            if (bg === 'rgb(14, 17, 23)' || bg === 'rgb(17, 20, 24)') {
                body.classList.add('dark-theme');
            } else {
                body.classList.remove('dark-theme');
            }
        }

        setInterval(detectTheme, 500);
        detectTheme();
    })();
    </script>
    """,
        height=0,
    )
