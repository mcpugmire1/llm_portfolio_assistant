"""
Hero Section Component

Large gradient hero with portfolio overview and CTAs.
"""

import streamlit as st
import streamlit.components.v1 as components


def render_hero():
    """
    Render hero section with logo, headline, and CTA buttons.

    Includes:
    - MattGPT logo
    - Job title and tagline
    - Explore Stories and Ask Agy buttons
    """

    st.markdown(
        """
        <style>
            /* Hide the trigger buttons */
            [class*="st-key-hero_explore"],
            [class*="st-key-hero_ask"] {
                display: none !important;
            }

            /* Pull hero up to sit flush under navbar */
            .hero-gradient-wrapper {
                background: var(--gradient-purple-hero);
                border-radius: 0px;
                margin: -32px 0 0 0 !important;
                padding: 0;
                width: 100%;
            }

            .hero-content {
                max-width: 1200px;
                margin: 0 auto;
                text-align: center;
                padding: 50px 40px;
                color: white;
            }

            .hero-btn {
                display: inline-block;
                padding: 14px 32px;
                border-radius: 8px;
                font-weight: 600;
                text-decoration: none !important;
                transition: all 0.2s ease;
                cursor: pointer;
                border: 2px solid white;
            }

            /* Also add these states to ensure no underlines ever */
            .hero-btn:hover,
            .hero-btn:active,
            .hero-btn:focus,
            .hero-btn:visited {
                text-decoration: none !important;
            }

            .hero-btn-primary {
                background: white;
                color: var(--purple-gradient-start);
            }

            .hero-btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(255,255,255,0.3);
            }

            .hero-btn-secondary {
                background: rgba(255,255,255,0.2);
                color: white;
            }

            .hero-btn-secondary:hover {
                background: rgba(255,255,255,0.3);
                transform: translateY(-2px);
            }

            /* ========================================
               MOBILE RESPONSIVE (<768px)
               ======================================== */
            /* ========================================
               MOBILE RESPONSIVE (<768px)
               ======================================== */
            @media (max-width: 767px) {
                .hero-content {
                    padding: 20px 16px !important;
                }
                .hero-gradient-wrapper {
                    margin-top: -20px !important;

                }

                /* Logo - much smaller */
                .hero-content > div:first-of-type {
                    margin-bottom: 16px !important;
                }
                .hero-content img[alt="MattGPT with Agy"] {
                    max-width: 140px !important;
                }

                /* Greeting text */
                .hero-content > div:nth-of-type(2) {
                    font-size: 14px !important;
                    margin-bottom: 8px !important;
                }

                /* Title */
                .hero-content h1 {
                    font-size: 22px !important;
                    margin-bottom: 10px !important;
                }

                /* First paragraph - keep but smaller */
                .hero-content p:first-of-type {
                    font-size: 13px !important;
                    line-height: 1.4 !important;
                    margin-bottom: 12px !important;
                    padding: 0 8px !important;
                }

                /* Second paragraph (Agy) - hide on mobile */
                .hero-content p:nth-of-type(2) {
                    display: none !important;
                }

                /* Button container - row on mobile */
                .hero-content > div:last-of-type {
                    flex-direction: row !important;
                    gap: 10px !important;
                    padding: 0 !important;
                    align-items: center !important;
                    justify-content: center !important;
                    margin-top: 8px !important;
                }

                /* Buttons - compact for side by side */
                .hero-btn {
                    width: auto !important;
                    padding: 10px 16px !important;
                    font-size: 13px !important;
                }
            }
        </style>
        <div class="hero-gradient-wrapper">
            <div class="hero-content">
                <div style="display: flex; justify-content: center; margin-bottom: 32px;">
                    <img src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/AgyMattCartoon-Transparent.png"
                         alt="Matt and Agy"
                         style="max-width: 360px; width: 100%; height: auto; filter: drop-shadow(0 8px 24px rgba(0,0,0,0.3));">
                </div>
                <div style="font-size: 22px; margin-bottom: 12px; color: white; opacity: 0.95;">
                    <span>👋</span>
                    <span> Hi, I'm Matt Pugmire</span>
                </div>
                <h1 style="font-size: 42px; font-weight: 700; margin-bottom: 16px; color: white;">Digital Transformation Leader</h1>
                <p style="font-size: 18px; color: white; opacity: 0.95; max-width: 700px; margin: 0 auto 22px; line-height: 1.6;">
                    20+ years driving innovation, agile delivery, and technology leadership across Fortune 500 companies.
                </p>
                 <p style="font-size: 16px; color: white; opacity: 0.95; max-width: 700px; margin: 0 auto 20px; line-height: 1.6;">
                    I trained my AI counterpart, <strong>Agy</strong> — a loyal Plott Hound with a nose for patterns — to surface insights across 130+ real transformation projects.
                 </p>
                <div style="display: flex; gap: 16px; justify-content: center; align-items: center; flex-wrap: wrap;">
                    <a id="btn-explore" class="hero-btn hero-btn-primary">
                        Explore Stories
                    </a>
                    <a id="btn-ask" class="hero-btn hero-btn-secondary">
                        Ask Agy 🐾
                    </a>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # JavaScript to wire up the HTML buttons
    components.html(
        """
    <script>
    (function() {
        setTimeout(function() {
            const parentDoc = window.parent.document;

            const btnExplore = parentDoc.getElementById('btn-explore');
            const btnAsk = parentDoc.getElementById('btn-ask');

            if (btnExplore) {
                btnExplore.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-hero_explore"] button');
                    if (stBtn) stBtn.click();
                };
            }

            if (btnAsk) {
                btnAsk.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-hero_ask"] button');
                    if (stBtn) stBtn.click();
                };
            }
        }, 200);
    })();
    </script>
    """,
        height=0,
    )

    # Hidden Streamlit buttons that get triggered by the HTML buttons
    if st.button("", key="hero_explore"):
        st.session_state["active_tab"] = "Explore Stories"
        st.rerun()

    if st.button("", key="hero_ask"):
        st.session_state["active_tab"] = "Ask MattGPT"
        st.rerun()


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
        """
        <style>
        .stats-bar {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            border-bottom: 2px solid var(--border-color);
            margin-bottom: 30px;
            margin-top: -15px;
        }

        .stat {
            padding: 2px;
            text-align: center;
            border-right: 1px solid var(--border-color);
        }

        .stat:last-child {
            border-right: none;
        }

        .stat-number {
            font-size: 36px;
            font-weight: 700;
            color: var(--purple-gradient-start);
            margin-bottom: 8px;
            display: block;
        }

        .stat-label {
            font-size: 14px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        @media (max-width: 768px) {
            .stats-bar {
                grid-template-columns: repeat(4, 1fr) !important;
                padding: 8px 0 !important;
            }
            .stat {
                padding: 6px 2px !important;
            }
            .stat-number {
                font-size: 18px !important;
                margin-bottom: 2px !important;
            }
            .stat-label {
                font-size: 8px !important;
                letter-spacing: 0 !important;
            }
        }

        @media (max-width: 380px) {
            .stat-number {
                font-size: 16px !important;
            }
            .stat-label {
                font-size: 7px !important;
            }
        }
        </style>
        <div class="stats-bar">
            <div class="stat">
                <div class="stat-number">20+</div>
                <div class="stat-label">Years Experience</div>
            </div>
            <div class="stat">
                <div class="stat-number">130+</div>
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
    """Render styled section title with emoji icon."""
    st.markdown(
        f"""
        <style>
            .section-header h2 {{
                font-size: 36px;
                font-weight: 700;
                color: var(--text-heading);
                margin: 40px 0 24px 0;
            }}
            @media (max-width: 767px) {{
                .section-header {{
                    margin: 0 !important;
                    padding: 0 !important;
                }}
                .section-header h2 {{
                    font-size: 18px !important;
                    margin: 8px 0 8px 0 !important;
                    white-space: nowrap !important;
                }}
                .section-header h2 span:first-child {{
                    font-size: 16px !important;
                }}
                /* Kill Streamlit's wrapper padding */
                .section-header [data-testid="stHeadingWithActionElements"] {{
                    padding: 0 !important;
                    margin: 0 !important;
                }}
                .section-header .st-emotion-cache-ua1rfn {{
                    padding: 0 !important;
                    margin: 0 !important;
                }}
                /* Hide the anchor link icon */
                .section-header [data-testid="stHeaderActionElements"] {{
                    display: none !important;
                }}
            }}
        </style>
        <div class="section-header" style="text-align: center;">
            <h2>
                <span>🎯</span>
                <span>{title}</span>
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
