"""
Banking Landing Page

55 banking projects organized by capability and client.
"""

import streamlit as st
from ui.components.footer import render_footer

def render_banking_landing():
    """Render Banking / Financial Services landing page."""
    # Import legacy function temporarily
    from ui.legacy_components import render_banking_landing_page
    render_banking_landing_page()
