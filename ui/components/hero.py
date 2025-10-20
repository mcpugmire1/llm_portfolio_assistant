"""
Hero Section Component

Large gradient hero with portfolio overview and CTAs.
"""

import streamlit as st
from config.theme import COLORS, GRADIENTS

def render_hero():
    """
    Render hero section with logo, headline, and CTA buttons.

    Includes:
    - MattGPT logo
    - Job title and tagline
    - Explore Stories and Ask Agy buttons
    """

    st.markdown(
        f"""
        <style>
        .hero-gradient-wrapper {{
            background: {GRADIENTS['purple_hero']};
            border-radius: 0px;
            margin: 0;
            padding: 0;
            width: 100%;
        }}
        .hero-content {{
            max-width: 1200px;
            margin: 0 auto;
            text-align: center;
            padding: 60px 40px;
            color: white;
        }}
        </style>
        <div class="hero-gradient-wrapper">
            <div class="hero-content">
                <div style="display: flex; justify-content: center; margin-bottom: 32px;">
                    <img src="https://raw.githubusercontent.com/mcpugmire1/mattgpt-design-spec/main/brand-kit/logos/MattGPT_Agy_Transparent.png"
                         alt="MattGPT with Agy"
                         style="max-width: 400px; width: 100%; height: auto; filter: drop-shadow(0 8px 24px rgba(0,0,0,0.3));">
                </div>
                <div style="font-size: 18px; margin-bottom: 12px; color: white; opacity: 0.95;">
                    <span>👋</span>
                    <span> Hi, I'm Matt Pugmire</span>
                </div>
                <h1 style="font-size: 42px; font-weight: 700; margin-bottom: 16px; color: white;">Digital Transformation Leader</h1>
                <p style="font-size: 18px; color: white; opacity: 0.95; max-width: 700px; margin: 0 auto 32px; line-height: 1.6;">
                    20+ years driving innovation, agile delivery, and technology leadership across Fortune 500 companies.
                    Explore my portfolio of 115+ projects or chat with Agy 🐾 to learn about my experience.
                </p>
                <div style="display: flex; gap: 16px; justify-content: center; align-items: center; flex-wrap: wrap;">
                    <a href="#explore" style="display: inline-block; padding: 14px 32px; background: white; color: {COLORS['purple_gradient_start']}; border: 2px solid white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
                        Explore Stories
                    </a>
                    <a href="#ask" style="display: inline-block; padding: 14px 32px; background: rgba(255,255,255,0.2); color: white; border: 2px solid white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
                        Ask Agy 🐾
                    </a>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stats_bar():
    """
    Render portfolio statistics bar.

    Displays 4 key metrics:
    - Years of experience
    - Projects delivered
    - Professionals trained
    - Enterprise clients
    """

    st.markdown(
        f"""
        <style>
        .stats-bar {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            border-bottom: 2px solid {COLORS['border_gray']};
            margin-bottom: 50px;
        }}

        .stat {{
            padding: 30px;
            text-align: center;
            border-right: 1px solid {COLORS['border_gray']};
        }}

        .stat:last-child {{
            border-right: none;
        }}

        .stat-number {{
            font-size: 36px;
            font-weight: 700;
            color: {COLORS['purple_gradient_start']};
            margin-bottom: 8px;
            display: block;
        }}

        .stat-label {{
            font-size: 14px;
            color: #999999;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        @media (max-width: 768px) {{
            .stats-bar {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .stat:nth-child(2) {{
                border-right: none;
            }}
        }}

        @media (max-width: 480px) {{
            .stats-bar {{
                grid-template-columns: 1fr;
            }}
            .stat {{
                border-right: none;
                border-bottom: 1px solid {COLORS['border_gray']};
            }}
            .stat:last-child {{
                border-bottom: none;
            }}
        }}
        </style>
        <div class="stats-bar">
            <div class="stat">
                <div class="stat-number">20+</div>
                <div class="stat-label">Years Experience</div>
            </div>
            <div class="stat">
                <div class="stat-number">115</div>
                <div class="stat-label">Projects Delivered</div>
            </div>
            <div class="stat">
                <div class="stat-number">300+</div>
                <div class="stat-label">Professionals Trained</div>
            </div>
            <div class="stat">
                <div class="stat-number">15+</div>
                <div class="stat-label">Enterprise Clients</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_title(title: str):
    """Render styled section title."""
    st.markdown(
        f'<h2 class="matt-section-title">{title}</h2>',
        unsafe_allow_html=True,
    )
