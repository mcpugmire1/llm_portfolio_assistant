"""
Category Cards Component

Homepage exploration cards for different portfolio categories.
Includes gradient industry cards and white capability cards.
Uses HTML buttons with JS triggers for consistent styling across themes.
"""

import streamlit as st


def render_category_cards():
    """Render homepage category cards grid - responsive with CSS Grid."""

    # Inject card and button styles
    st.markdown(
        """
    <style>
    /* === CARD BUTTON STYLES === */

    /* Buttons inside purple gradient cards */
    .card-btn-gradient {
        display: inline-block;
        padding: 12px 24px;
        background: rgba(255, 255, 255, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.4);
        border-radius: 8px;
        color: white !important;
        font-weight: 600;
        font-size: 14px;
        text-decoration: none !important;
        cursor: pointer;
        transition: all 0.2s ease;
        backdrop-filter: blur(4px);
    }

    .card-btn-gradient:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.6);
        transform: translateY(-2px);
        text-decoration: none !important;
    }

    /* Buttons inside capability cards (theme-aware) */
    .card-btn-outline {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background: var(--bg-surface);
        border: 2px solid var(--border-color);
        border-radius: 6px;
        color: var(--accent-purple) !important;
        font-weight: 600;
        font-size: 13px;
        text-decoration: none !important;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .card-btn-outline:hover {
        background: var(--accent-purple);
        border-color: var(--accent-purple);
        color: white !important;
        text-decoration: none !important;
    }

    /* Ask Agy button - always purple filled */
    .card-btn-primary {
        display: inline-block;
        padding: 14px 28px;
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
        border: none;
        border-radius: 8px;
        color: white !important;
        font-weight: 600;
        font-size: 15px;
        text-decoration: none !important;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25);
    }

    .card-btn-primary:hover {
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);
        text-decoration: none !important;
    }

    /* Capability card container (theme-aware) */
    .capability-card {
        background: var(--bg-card);
        color: var(--text-primary);
        padding: 32px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        height: 320px;
        display: flex;
        flex-direction: column;
    }

    .capability-card h3 {
        color: var(--text-heading);
        font-size: 20px;
        font-weight: 700;
        margin: 0 0 12px 0;
    }

    .capability-card .description {
        color: var(--text-secondary);
        margin-bottom: 16px;
        line-height: 1.6;
        font-size: 15px;
        flex-grow: 1;
    }

    .capability-card .hints {
        color: var(--text-muted);
        font-style: italic;
        font-size: 14px;
        line-height: 1.5;
        margin-bottom: 16px;
    }

    .capability-card .highlight {
        color: var(--accent-purple);
        font-weight: 600;
        margin-bottom: 12px;
        font-size: 15px;
    }

    /* Hide the trigger buttons */
    [class*="st-key-card_btn_"] {
        display: none !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="matt-container">', unsafe_allow_html=True)

    # === ROW 1: Industry cards (purple gradient) ===
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        <div style="background: var(--gradient-purple-hero); color: white; padding: 32px; border-radius: 12px; height: 380px; display: flex; flex-direction: column;">
            <div style="font-size: 48px; margin-bottom: 16px;">🏦</div>
            <h3 style="color: white; font-size: 24px; font-weight: 700; margin: 0 0 8px 0;">Financial Services / Banking</h3>
            <div style="color: rgba(255,255,255,0.9); font-size: 16px; font-weight: 600; margin-bottom: 16px;">55 projects</div>
            <div style="color: rgba(255,255,255,0.95); margin-bottom: 16px; line-height: 1.5; font-size: 15px;">Banking modernization, payments, compliance, core banking systems</div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px; flex-grow: 1; align-items: flex-start; margin-bottom: 20px;">
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500;">JPMorgan Chase (33)</span>
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500;">American Express (3)</span>
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500;">Capital One (2)</span>
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500;">Fiserv (7)</span>
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500;">HSBC (2)</span>
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500;">RBC (11)</span>
            </div>
            <div>
                <a id="btn-banking" class="card-btn-gradient">See Banking Projects →</a>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        # Hidden Streamlit button
        if st.button("", key="card_btn_banking"):
            st.session_state["active_tab"] = "Banking"
            st.rerun()

    with col2:
        st.markdown(
            """
        <div style="background: var(--gradient-purple-hero); color: white; padding: 32px; border-radius: 12px; height: 380px; display: flex; flex-direction: column;">
            <div style="font-size: 48px; margin-bottom: 16px;">🌐</div>
            <h3 style="color: white; font-size: 24px; font-weight: 700; margin: 0 0 8px 0;">Cross-Industry Transformation</h3>
            <div style="color: rgba(255,255,255,0.9); font-size: 16px; font-weight: 600; margin-bottom: 16px;">51 projects</div>
            <div style="color: rgba(255,255,255,0.95); margin-bottom: 16px; line-height: 1.5; font-size: 15px;">Multi-sector consulting, platform engineering, organizational transformation</div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px; flex-grow: 1; align-items: flex-start; margin-bottom: 20px;">
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500;">Accenture (13)</span>
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500;">Multiple Clients (33)</span>
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500;">Healthcare (3)</span>
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500;">Transportation (5)</span>
            </div>
            <div>
                <a id="btn-cross-industry" class="card-btn-gradient">Browse Transformations →</a>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        # Hidden Streamlit button
        if st.button("", key="card_btn_cross_industry"):
            st.session_state["active_tab"] = "Cross-Industry"
            st.rerun()

    # Row spacing
    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)

    # === ROW 2: Capability cards ===
    col3, col4 = st.columns(2)

    with col3:
        st.markdown(
            """
        <div class="capability-card">
            <div style="font-size: 40px; margin-bottom: 16px;">🚀</div>
            <h3>Product Innovation &amp; Strategy</h3>
            <div class="description">Cloud-native products from zero. Lean, rapid prototyping, OKRs, MVPs</div>
            <div class="hints">"How do you do hypothesis-driven development?" • "How do you shift to product thinking?"</div>
            <div>
                <a id="btn-product" class="card-btn-outline">View Case Studies →</a>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("", key="card_btn_product"):
            if st.session_state.get("active_tab") == "Home":
                st.session_state["prefilter_domains"] = [
                    "Product Management",
                    "Product Strategy & Innovation",
                    "Client Product Innovation & Co-Creation",
                    "User-Centered Product Strategy & Innovation",
                    "Digital Product Development & Delivery",
                ]
                st.session_state["active_tab"] = "Explore Stories"
                st.rerun()

    with col4:
        st.markdown(
            """
        <div class="capability-card">
            <div style="font-size: 40px; margin-bottom: 16px;">🔧</div>
            <h3>App Modernization</h3>
            <div class="description">Modernizing legacy apps with event-driven design, microservices, and zero-defect delivery</div>
            <div class="hints">"How do you modernize monoliths into microservices?" • "How do you approach application rationalization?"</div>
            <div>
                <a id="btn-modernization" class="card-btn-outline">View Case Studies →</a>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("", key="card_btn_modernization"):
            if st.session_state.get("active_tab") == "Home":
                st.session_state["prefilter_capability"] = "Application Modernization"
                st.session_state["active_tab"] = "Explore Stories"
                st.rerun()

    # Row spacing
    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)

    # === ROW 3: Capability cards ===
    col5, col6 = st.columns(2)

    with col5:
        st.markdown(
            """
        <div class="capability-card">
            <div style="font-size: 40px; margin-bottom: 16px;">💡</div>
            <h3>Consulting &amp; Transformation</h3>
            <div class="description">Fortune 500 advisory, operating models, 3-20x acceleration, New Ways of Working</div>
            <div class="hints">"How do you achieve 4x faster delivery?" • "How do you align cross-functional teams?"</div>
            <div>
                <a id="btn-consulting" class="card-btn-outline">Browse Transformations →</a>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("", key="card_btn_consulting"):
            if st.session_state.get("active_tab") == "Home":
                st.session_state["prefilter_domains"] = [
                    "Agile Planning & Value-Driven Delivery",
                    "Agile Transformation & Leadership Enablement",
                    "AI Governance & Data Privacy",
                    "Client Product Innovation & Co-Creation",
                    "Cross-Functional Collaboration & Alignment",
                    "Leadership & Continuous Improvement",
                    "Platform Adoption & Client Integration",
                    "Process Optimization & Automation",
                    "Product Management",
                    "Product Strategy & Innovation",
                    "Program Management & Governance",
                    "Psychological Safety & Innovation Culture",
                    "Security & Compliance Solutions",
                    "Strategic Client Partnerships",
                    "Strategic Enterprise & Methodology Innovation",
                    "Technical Leadership",
                    "Technology Strategy & Advisory Services",
                    "User-Centered Product Strategy & Innovation",
                ]
                st.session_state["active_tab"] = "Explore Stories"
                st.rerun()

    with col6:
        st.markdown(
            """
        <div class="capability-card">
            <div style="font-size: 40px; margin-bottom: 16px;">👥</div>
            <h3>Teams &amp; Talent Development</h3>
            <div class="description">Innovation centers, servant leadership, upskilling programs</div>
            <div class="hints">"How did you scale the innovation center to 150+ people?" • "How did you equip teams for New IT ways of working?"</div>
            <div>
                <a id="btn-teams" class="card-btn-outline">Check Team Stories →</a>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("", key="card_btn_teams"):
            if st.session_state.get("active_tab") == "Home":
                st.session_state["prefilter_domains"] = [
                    "Client Upskilling & Enablement",
                    "Cross-Functional Team Enablement",
                    "Psychological Safety & Innovation Culture",
                    "Talent Enablement & Growth",
                ]
                st.session_state["active_tab"] = "Explore Stories"
                st.rerun()

    # Row spacing
    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)

    # === ROW 4: Quick Question card ===
    st.markdown(
        """
    <div style="background: var(--gradient-purple-hero); color: white; padding: 32px; border-radius: 12px; min-height: 200px; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 24px; margin-bottom: 20px;">
            <img src="https://raw.githubusercontent.com/mcpugmire1/mattgpt-design-spec/main/brand-kit/chat_avatars/agy_avatar_128_dark.png"
                 alt="Agy" style="width: 64px; height: 64px; border-radius: 50%; border: 3px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
            <div>
                <h3 style="font-size: 24px; font-weight: 700; margin: 0 0 4px 0; color: white;">Quick Question</h3>
                <div style="font-size: 16px; font-weight: 600; color: rgba(255,255,255,0.95);">Ask Agy 🐾 anything</div>
            </div>
        </div>
        <div style="font-size: 16px; margin-bottom: 16px; color: rgba(255,255,255,0.95); line-height: 1.6;">
            From building MattGPT to leading global programs — Agy can help you explore 20+ years of transformation experience.
        </div>
        <div style="font-size: 14px; font-style: italic; color: rgba(255,255,255,0.85); margin-bottom: 20px;">
            "How did you build MattGPT?" • "How do you overcome the challenges of scaling to 150+ engineers?"
        </div>
        <div>
            <a id="btn-ask-agy" class="card-btn-primary">Ask Agy 🐾</a>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button("", key="card_btn_ask_agy"):
        st.session_state["active_tab"] = "Ask MattGPT"
        st.session_state["skip_home_menu"] = True
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # JavaScript to wire up the HTML buttons - same pattern as hero.py
    import streamlit.components.v1 as components

    components.html(
        """
    <script>
    (function() {
    // Theme detection
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
        setTimeout(function() {
            const parentDoc = window.parent.document;

            const btnBanking = parentDoc.getElementById('btn-banking');
            const btnCrossIndustry = parentDoc.getElementById('btn-cross-industry');
            const btnProduct = parentDoc.getElementById('btn-product');
            const btnModernization = parentDoc.getElementById('btn-modernization');
            const btnConsulting = parentDoc.getElementById('btn-consulting');
            const btnTeams = parentDoc.getElementById('btn-teams');
            const btnAskAgy = parentDoc.getElementById('btn-ask-agy');

            if (btnBanking) {
                btnBanking.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-card_btn_banking"] button');
                    if (stBtn) stBtn.click();
                };
            }

            if (btnCrossIndustry) {
                btnCrossIndustry.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-card_btn_cross_industry"] button');
                    if (stBtn) stBtn.click();
                };
            }

            if (btnProduct) {
                btnProduct.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-card_btn_product"] button');
                    if (stBtn) stBtn.click();
                };
            }

            if (btnModernization) {
                btnModernization.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-card_btn_modernization"] button');
                    if (stBtn) stBtn.click();
                };
            }

            if (btnConsulting) {
                btnConsulting.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-card_btn_consulting"] button');
                    if (stBtn) stBtn.click();
                };
            }

            if (btnTeams) {
                btnTeams.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-card_btn_teams"] button');
                    if (stBtn) stBtn.click();
                };
            }

            if (btnAskAgy) {
                btnAskAgy.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-card_btn_ask_agy"] button');
                    if (stBtn) stBtn.click();
                };
            }
        }, 200);
    })();
    </script>
    """,
        height=0,
    )
