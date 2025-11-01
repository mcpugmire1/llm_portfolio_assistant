"""
Home Page - MattGPT Landing

Hero section with portfolio overview, category cards, and CTAs.
This is the main landing page users see when they first visit.
"""

import streamlit as st
from ui.components.hero import render_hero, render_stats_bar, render_section_title
from ui.components.category_cards import render_category_cards
from ui.components.footer import render_footer

def render_home_page():
    """
    Render the homepage with hero, stats, category cards, and footer.

    Structure:
    1. Hero section with logo and CTAs
    2. Portfolio statistics bar
    3. Section title
    4. Category exploration cards
    5. Footer with contact information
    """

    # Hero section
    render_hero()

    # Stats bar
    render_stats_bar()

    # Section title
    render_section_title("What would you like to explore?")

    # DEBUG: Visible test to confirm home.py is loading
    st.markdown("### 🟢 GREEN CIRCLE = home.py is loading!")

    # EMERGENCY FIX: Inject button CSS directly here (bypassing cached import)
    st.markdown("""
    <style>
    /* Homepage category buttons - INJECTED DIRECTLY TO BYPASS CACHE */
    button.st-emotion-cache-7lqsib.e8vg11g2[data-testid="stBaseButton-secondary"],
    [class*="st-key-btn_"] button {
        background-color: white !important;
        background: white !important;
        color: #8B5CF6 !important;
        border: 2px solid #e5e5e5 !important;
        border-radius: 8px !important;
        padding: 11px 20px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    button.st-emotion-cache-7lqsib.e8vg11g2[data-testid="stBaseButton-secondary"]:hover,
    [class*="st-key-btn_"] button:hover {
        background-color: #8B5CF6 !important;
        background: #8B5CF6 !important;
        color: white !important;
        border-color: #8B5CF6 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3), 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }

    /* Ask Agy bottom CTA - purple gradient */
    .st-key-btn_6 button {
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px 28px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25) !important;
    }
    .st-key-btn_6 button:hover {
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Category cards
    render_category_cards()

    # === ADD FOOTER ===
    from ui.components.footer import render_footer
    render_footer()
