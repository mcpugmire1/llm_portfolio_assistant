"""
Footer Component

Reusable footer with contact information and availability.
Used across all pages for consistency.
"""

import streamlit as st
from config.theme import COLORS, SPACING

def render_footer():
    """
    Render footer with contact information and CTAs.

    Displays:
    - Job search headline
    - Availability status
    - Email, LinkedIn, and Ask Agy buttons
    """

    footer_html = f"""
    <div style="
        background: {COLORS['dark_slate']};
        color: white;
        padding: {SPACING['footer_padding']};
        text-align: center;
        margin-top: 80px;
    ">
        <h2 style="
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 24px;
            color: white;
            line-height: 1.2;
        ">
            Let's Connect
        </h2>

        <p style="
            font-size: 16px;
            margin-bottom: 16px;
            color: rgba(255, 255, 255, 0.95);
            line-height: 1.6;
            max-width: 850px;
            margin-left: auto;
            margin-right: auto;
        ">
            Exploring Director/VP opportunities in <strong>Product Leadership</strong>,
            <strong>Platform Engineering</strong>, and <strong>Organizational Transformation</strong>
        </p>

        <p style="
            font-size: 14px;
            margin-bottom: 40px;
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.5;
        ">
            Available for immediate start • Remote or Atlanta-based • Open to consulting engagements
        </p>

        <div style="
            display: flex;
            gap: 18px;
            justify-content: center;
            flex-wrap: wrap;
            align-items: center;
        ">
            <a href="mailto:mcpugmire@gmail.com" style="
                padding: {SPACING['button_padding']};
                background: {COLORS['primary_purple']};
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                transition: all 0.2s ease;
            ">
                📧 mcpugmire@gmail.com
            </a>

            <a href="https://www.linkedin.com/in/mattpugmire/" target="_blank" style="
                padding: {SPACING['button_padding']};
                background: rgba(255,255,255,0.08);
                color: white;
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                transition: all 0.2s ease;
            ">
                💼 LinkedIn
            </a>

            <a href="#ask-mattgpt" style="
                padding: {SPACING['button_padding']};
                background: rgba(255,255,255,0.08);
                color: white;
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                transition: all 0.2s ease;
            ">
                🐾 Ask Agy
            </a>
        </div>
    </div>
    """

    st.markdown(footer_html, unsafe_allow_html=True)
