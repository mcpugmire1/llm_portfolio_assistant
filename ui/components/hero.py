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
    - Role Match (primary) and Ask Agy (secondary) buttons (MATTGPT-087)
    """

    st.markdown(
        """
        <style>
            /* Hide the trigger buttons */
            [class*="st-key-hero_role_match"],
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
                padding: 25px 30px;
                color: white;
            }

            .hero-content h1 {
                padding: 0 !important;
                margin: 0 0 10px 0 !important;
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
                color: var(--purple-gradient-start) !important;
            }

            .hero-btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(255,255,255,0.3);
            }

            .hero-btn-secondary {
                background: rgba(255,255,255,0.2);
                color: white !important;
                backdrop-filter: blur(4px);
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
                    /* 56px clears the fixed mobile header (z-index 999999).
                       Was -20px (desktop layout artifact) which pulled the
                       hero up into the area covered by the header. */
                    margin-top: 56px !important;
                }

                /* Logo - much smaller */
                .hero-content > div:first-of-type {
                    margin-bottom: 16px !important;
                }
                .hero-content img {
                    max-width: 140px !important;
                }

                /* Greeting text */
                .hero-content > div:nth-of-type(2) {
                    font-size: 14px !important;
                    margin-bottom: 8px !important;
                }

                /* Title */
                .hero-content h1 {
                    font-size: 20px !important;
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
                    display: 1 !important;
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
                .hero-btn-prefix {
                    display: none;
                }
            }
        </style>
        <div class="hero-gradient-wrapper">
            <div class="hero-content">
                <div style="display: flex; justify-content: center; margin-bottom: 16px;">
                    <img src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/matt_agy_hero.png"
                         alt="Matt and Agy"
                         style="max-width: 280px; width: 100%; height: auto; filter: drop-shadow(0 8px 24px rgba(0,0,0,0.3));">
                </div>
                <div style="font-size: 18px; margin-bottom: 1px; color: white; opacity: 0.95;">
                    <span> Hi, I'm Matt Pugmire</span>
                </div>
                <h1 style="font-size: 40px; font-weight: 700; padding-top: 0 !important; margin-top: 0 !important; margin-bottom: 10px; color: white;">Interview me before you interview me.</h1>
                <p style="font-size: 17px; color: white; opacity: 0.95; max-width: 700px; margin: 0 auto 8px; line-height: 1.6;">In active search for a role where building the product engineering organization, establishing the culture, and delivering results are part of the same job.
                </p>
                <p style="font-size: 14px; color: white; opacity: 0.9; max-width: 600px; margin: 6px auto 18px; line-height: 1.55;">That's Agy, my Plott Hound and AI assistant, ready to track down insights from two decades of work.
                </p>
                <div style="display: flex; gap: 16px; justify-content: center; align-items: center; flex-wrap: wrap;">
                    <a id="btn-role-match" class="hero-btn hero-btn-primary">
                        <span class="hero-btn-prefix">Recruiting for a role? </span>Match it →
                    </a>
                    <a id="btn-ask" class="hero-btn hero-btn-secondary">
                        <span class="hero-btn-prefix">Want to dig deeper? </span>Ask Agy 🐾
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

            const btnRoleMatch = parentDoc.getElementById('btn-role-match');
            const btnAsk = parentDoc.getElementById('btn-ask');

            if (btnRoleMatch) {
                btnRoleMatch.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-hero_role_match"] button');
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
    if st.button("", key="hero_role_match"):
        st.session_state["active_tab"] = "Role Match"
        st.rerun()

    if st.button("", key="hero_ask"):
        st.session_state["active_tab"] = "Ask Agy"
        st.rerun()


def render_stats_bar():
    """
    Render portfolio statistics bar.

    Displays 4 stat tiles. The Leadership tile carries function-level
    "Product engineering" framing per MATTGPT-092 (scope/outcome anchor, not a
    title chip), with a "Product eng" mobile variant (≤768px) via the dual
    .stat-desktop / .stat-mobile span pattern. The other three are production
    portfolio metrics:
    - Leadership (Product engineering / "Product eng" on mobile)
    - Projects Delivered (100+)
    - Professionals Trained (300+)
    - Enterprise Clients (15+)
    """

    st.markdown(
        """
        <style>
        .stats-bar {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            border-bottom: 2px solid var(--border-color);
            margin-bottom: 30px;
            margin-top: 1px;
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
            font-size: 18px;
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
        .stat-mobile { display: none; }

        @media (max-width: 768px) {
            .stats-bar {
                grid-template-columns: repeat(4, 1fr) !important;
                padding: 8px 0 !important;
            }
            .stat {
                padding: 6px 2px !important;
            }
            .stat-number {
                font-size: 14px !important;
                margin-bottom: 2px !important;
            }
            .stat-label {
                font-size: 8px !important;
                letter-spacing: 0 !important;
            }
            .stat-desktop { display: none !important; }
            .stat-mobile { display: inline !important; }
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
                <div class="stat-number">
                    <span class="stat-desktop">Product engineering</span>
                    <span class="stat-mobile">Product eng</span>
                </div>
                <div class="stat-label">Leadership</div>
            </div>
            <div class="stat">
                <div class="stat-number">100+</div>
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
            /* MATTGPT-107: tightened section-header per wireframe alignment.
               Drops vertical footprint from ~125px to ~69px by removing the
               32px of phantom Streamlit anchor-element padding, tightening
               margins (40/24 -> 24/16), and hiding the hover anchor-icon.
               The .section-header :has() selectors below scope the
               padding-killing rules to this component only — Banking and
               Cross-Industry landing pages render `.section-header` as a
               <div>, not <h2>, so their layouts are unaffected. */
            .section-header h2 {{
                font-size: 24px;
                font-weight: 500;
                color: var(--text-primary);
                margin: 8px 0 16px 0 !important;
                padding: 0 !important;
            }}
            .section-header [data-testid="stHeadingWithActionElements"] {{
                padding: 0 !important;
                margin: 0 !important;
            }}
            .section-header [data-testid="stHeaderActionElements"] {{
                display: none !important;
            }}

            @media (max-width: 767px) {{
                .section-header {{
                    margin: 0 !important;
                    padding: 0 !important;
                }}
                .section-header h2 {{
                    font-size: 18px !important;
                    margin: 8px 0 !important;
                    white-space: nowrap !important;

                }}
                .section-header h2 span:first-child {{
                    font-size: 16px !important;
                }}
            }}
        </style>
        <div class="section-header" style="text-align: center;">
            <h2>
                <span></span>
                <span>{title}</span>
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
