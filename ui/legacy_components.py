# components.py

import streamlit as st


# ---------------------------------------------------------
# 1) CSS — lightweight, wireframe-matching, theme-aware
# ---------------------------------------------------------
def css_once():
    if st.session_state.get("_matt_css_done"):
        return
    st.session_state["_matt_css_done"] = True

    st.markdown(
        """
        <style>
        /* Minimize header height but keep toolbar visible for hamburger menu */
        header[data-testid="stHeader"] {
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
        }

        /* Position toolbar in top-right corner */
        header[data-testid="stHeader"] [data-testid="stToolbar"] {
            position: fixed !important;
            top: 10px !important;
            right: 10px !important;
            z-index: 999999 !important;
        }

        footer {
            visibility: hidden !important;
        }

        /* Dark Navigation Bar - handled in app.py with specific selectors */
        /* Removed broad selectors that were affecting all horizontal blocks */

        /* Container */
        .matt-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        /* Hero with full gradient background - wireframe style */
        .matt-hero {
            text-align: center;
            padding: 60px 40px !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border-radius: 16px !important;
            margin-bottom: 50px !important;
            position: relative;
            overflow: hidden;
        }

        .hero-image {
            display: flex;
            justify-content: center;
            margin-bottom: 32px;
        }

        .hero-greeting {
            font-size: 18px;
            margin-bottom: 12px;
            opacity: 0.95;
            color: white !important;
        }

        .matt-hero h1 {
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 16px;
            color: white !important;
        }

        .matt-hero .tagline {
            font-size: 18px;
            color: white !important;
            opacity: 0.95;
            max-width: 700px;
            margin: 0 auto 32px;
            line-height: 1.6;
        }

        .matt-hero p {
            color: white !important;
        }

        .hero-buttons {
            display: flex;
            gap: 16px;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
        }

        .hero-btn {
            transition: all 0.2s ease;
        }

        .hero-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        /* Section title */
        .matt-section-title {
            font-size: 32px;
            font-weight: 600;
            text-align: center;
            margin: 60px 0 40px 0;
        }

        /* FORCE metrics styling with highest specificity */
        .stApp div[data-testid="metric-container"] {
            background: #2d2d2d !important;
            padding: 28px 20px !important;
            border-radius: 12px !important;
            border: 1px solid #3a3a3a !important;
            text-align: center !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important;
            transition: transform 0.3s ease !important;
        }

        .stApp div[data-testid="metric-container"]:hover {
            transform: translateY(-4px) !important;
        }

        .stApp div[data-testid="metric-container"] [data-testid="metric-value"] {
            color: #667eea !important;
            font-size: 34px !important;
            font-weight: 700 !important;
            margin-bottom: 4px !important;
        }

        .stApp div[data-testid="metric-container"] [data-testid="metric-label"] {
            color: #b0b0b0 !important;
            font-size: 14px !important;
            margin-top: 4px !important;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .matt-hero h1 { font-size: 32px; }
            .matt-hero p { font-size: 18px; }
        }

        /* Starter cards as native HTML buttons (full control, no Streamlit theming) */
        .matt-starters-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 24px;
            margin-bottom: 60px;
        }

        .matt-card-btn {
            width: 100%;
            background: #2d2d2d;
            border: 1px solid #3a3a3a;
            border-radius: 12px;
            padding: 32px;
            text-align: left;
            color: #fff;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,.25);
            transition: transform .3s ease, box-shadow .3s ease, border-color .3s ease;
        }

        .matt-card-btn:hover {
            transform: translateY(-4px);
            border-color: #667eea;
            box-shadow: 0 8px 25px rgba(74,144,226,.15);
            background: #353535;
        }

        .matt-card-btn .icon { display:block; font-size:40px; margin-bottom:20px; }
        .matt-card-btn .title { font-size:22px; font-weight:600; margin-bottom:16px; }
        .matt-card-btn .desc  { color:#b0b0b0; margin-bottom:20px; line-height:1.5; }
        .matt-card-btn .examples { font-size:14px; color:#888; font-style:italic; }

        /* Normalize the form wrapper so it doesn’t add spacing */
        .matt-starter-form { margin: 0; }

        /* Reset button appearance so we fully control the look */
        .matt-card-btn {
        -webkit-appearance: none;
        appearance: none;
        outline: none;
        border: 1px solid #3a3a3a;
        background: #2d2d2d;
        color: #fff;
        border-radius: 12px;
        padding: 32px;
        width: 100%;
        text-align: left;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,.25);
        transition: transform .3s ease, box-shadow .3s ease, border-color .3s ease, background .3s ease;
        }
        .matt-card-btn:hover {
        transform: translateY(-4px);
        border-color: #667eea;
        box-shadow: 0 8px 25px rgba(74,144,226,.15);
        background: #353535;
        }
        .matt-card-btn:focus { outline: none; }

        /* Make the *buttons* themselves the grid children */
        .matt-starter-form .matt-starters-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 24px;
        margin-bottom: 60px;
        }

        /* Typography inside the card */
        .matt-card-btn .icon { display:block; font-size:40px; margin-bottom:20px; }
        .matt-card-btn .title { font-size:22px; font-weight:600; margin-bottom:16px; }
        .matt-card-btn .client-name { color:#764ba2; font-size:16px; font-weight:600; margin-bottom:8px; }
        .matt-card-btn .desc { color:#b0b0b0; margin-bottom:20px; line-height:1.5; }
        .matt-card-btn .examples { font-size:14px; color:#888; font-style:italic; }

        /* Buttons on gradient cards - PURPLE THEME */
        .stButton > button {
            background: white !important;
            border: 2px solid #e5e5e5 !important;
            color: #8B5CF6 !important;
            padding: 14px 28px !important;
            border-radius: 8px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            width: 100% !important;
            margin-top: 10px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
        }

        .stButton > button:hover {
            background: #8B5CF6 !important;
            color: white !important;
            border-color: #8B5CF6 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3), 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        }

        /* Home category buttons - EVERY CLASS FROM DEV TOOLS */
        div.st-key-btn_0.st-emotion-cache-zh2fnc button.st-emotion-cache-7lqsib.e8vg11g2,
        div.st-key-btn_1.st-emotion-cache-zh2fnc button.st-emotion-cache-7lqsib.e8vg11g2,
        div.st-key-btn_2.st-emotion-cache-zh2fnc button.st-emotion-cache-7lqsib.e8vg11g2,
        div.st-key-btn_3.st-emotion-cache-zh2fnc button.st-emotion-cache-7lqsib.e8vg11g2,
        div.st-key-btn_4.st-emotion-cache-zh2fnc button.st-emotion-cache-7lqsib.e8vg11g2,
        div.st-key-btn_5.st-emotion-cache-zh2fnc button.st-emotion-cache-7lqsib.e8vg11g2 {
            background: white !important;
            background-color: white !important;
            background-image: none !important;
            border: 2px solid #e5e5e5 !important;
            border-width: 2px !important;
            border-style: solid !important;
            border-color: #e5e5e5 !important;
            color: #8B5CF6 !important;
        }
        div.st-key-btn_0.st-emotion-cache-zh2fnc button.st-emotion-cache-7lqsib.e8vg11g2:hover,
        div.st-key-btn_1.st-emotion-cache-zh2fnc button.st-emotion-cache-7lqsib.e8vg11g2:hover,
        div.st-key-btn_2.st-emotion-cache-zh2fnc button.st-emotion-cache-7lqsib.e8vg11g2:hover,
        div.st-key-btn_3.st-emotion-cache-zh2fnc button.st-emotion-cache-7lqsib.e8vg11g2:hover,
        div.st-key-btn_4.st-emotion-cache-zh2fnc button.st-emotion-cache-7lqsib.e8vg11g2:hover,
        div.st-key-btn_5.st-emotion-cache-zh2fnc button.st-emotion-cache-7lqsib.e8vg11g2:hover {
            background: #8B5CF6 !important;
            background-color: #8B5CF6 !important;
            background-image: none !important;
            color: white !important;
            border: 2px solid #8B5CF6 !important;
            border-color: #8B5CF6 !important;
        }

        /* Ask Agy CTA button - purple gradient */
        [class*="st-key-btn_6"] button,
        button[data-testid*="btn_6"] {
            background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25) !important;
        }
        [class*="st-key-btn_6"] button:hover,
        button[data-testid*="btn_6"]:hover {
            background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
            box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4) !important;
        }
    </style>

    <script>
    // JavaScript nuclear option - forcibly override button styles with inline styles
    function applyPurpleButtonStyles() {
        for (let i = 0; i <= 5; i++) {
            const container = document.querySelector('.st-key-btn_' + i);
            if (container) {
                const button = container.querySelector('button[data-testid="stBaseButton-secondary"]');
                if (button && !button.dataset.purpleStyled) {
                    button.dataset.purpleStyled = 'true';

                    button.style.setProperty('background', 'white', 'important');
                    button.style.setProperty('background-color', 'white', 'important');
                    button.style.setProperty('background-image', 'none', 'important');
                    button.style.setProperty('border', '2px solid #e5e5e5', 'important');
                    button.style.setProperty('color', '#8B5CF6', 'important');

                    button.addEventListener('mouseenter', function() {
                        this.style.setProperty('background', '#8B5CF6', 'important');
                        this.style.setProperty('background-color', '#8B5CF6', 'important');
                        this.style.setProperty('color', 'white', 'important');
                        this.style.setProperty('border-color', '#8B5CF6', 'important');
                    });
                    button.addEventListener('mouseleave', function() {
                        this.style.setProperty('background', 'white', 'important');
                        this.style.setProperty('background-color', 'white', 'important');
                        this.style.setProperty('color', '#8B5CF6', 'important');
                        this.style.setProperty('border-color', '#e5e5e5', 'important');
                    });
                }
            }
        }
    }

    setTimeout(applyPurpleButtonStyles, 100);
    setTimeout(applyPurpleButtonStyles, 500);
    setTimeout(applyPurpleButtonStyles, 1000);

    const observer = new MutationObserver(applyPurpleButtonStyles);
    observer.observe(document.body, { childList: true, subtree: true });
    </script>

    <style>
        .skill-bar {
            height: 6px;
            background: var(--border-color);  /* Use theme variable instead of hardcoded color */
            border-radius: 3px;
            margin-bottom: 16px;
            position: relative;
        }

        .skill-fill {
            height: 100%;
            background: #667eea;  /* Keep the blue accent color */
            border-radius: 3px;
        }

        /* ========================================
           EXPLORE STORIES - CARD VIEW STYLING
           ======================================== */

        /* Remove any CSS that isn't working - the .fixed-height-card inline styles handle it */

        /* ========================================
           EXPLORE STORIES - AGGRID TABLE STYLING
           Match the wireframe design exactly
           ======================================== */

        /* AgGrid container wrapper - add prominence */
        .ag-theme-streamlit {
            background: #262626 !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
            border: 1px solid #333 !important;
            margin-top: 8px !important;
            margin-bottom: 8px !important;
        }

        /* AgGrid header styling */
        .ag-theme-streamlit .ag-header {
            background: #2f2f2f !important;
            border-bottom: 2px solid #404040 !important;
        }

        .ag-theme-streamlit .ag-header-cell {
            background: #2f2f2f !important;
            border-right: none !important;
            padding: 16px 20px !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            color: #ffffff !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }

        .ag-theme-streamlit .ag-header-cell-text {
            color: #ffffff !important;
        }

        /* AgGrid body and rows */
        .ag-theme-streamlit .ag-root-wrapper {
            background: #262626 !important;
            border: none !important;
        }

        .ag-theme-streamlit .ag-row {
            background: #262626 !important;
            border-bottom: 1px solid #333 !important;
            border-left: 3px solid transparent !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
        }

        .ag-theme-streamlit .ag-row:hover {
            background: #2d2d2d !important;
            border-left: 3px solid #667eea !important;
        }

        .ag-theme-streamlit .ag-row-selected {
            background: #1e3a5f !important;
            border-left: 3px solid #667eea !important;
        }

        .ag-theme-streamlit .ag-row-selected:hover {
            background: #1e3a5f !important;
        }

        /* AgGrid cells */
        .ag-theme-streamlit .ag-cell {
            padding: 24px 20px !important;
            font-size: 14px !important;
            line-height: 1.6 !important;
            color: var(--text-color) !important;
            border-right: none !important;
        }

        /* Ensure cell text is 14px */
        .ag-theme-streamlit .ag-cell-value {
            font-size: 14px !important;
        }

        /* Increase row height */
        .ag-theme-streamlit .ag-row {
            min-height: 70px !important;
        }

        /* Remove center container borders */
        .ag-theme-streamlit .ag-center-cols-container {
            border: none !important;
        }

        /* Scrollbar styling */
        .ag-theme-streamlit .ag-body-viewport::-webkit-scrollbar {
            width: 8px;
        }

        .ag-theme-streamlit .ag-body-viewport::-webkit-scrollbar-track {
            background: #2a2a2a;
            border-radius: 4px;
        }

        .ag-theme-streamlit .ag-body-viewport::-webkit-scrollbar-thumb {
            background: #4a4a4a;
            border-radius: 4px;
            transition: background 0.2s ease;
        }

        .ag-theme-streamlit .ag-body-viewport::-webkit-scrollbar-thumb:hover {
            background: #5a5a5a;
        }

        /* Hide AgGrid's built-in pagination controls completely */
        .ag-theme-streamlit .ag-paging-panel {
            display: none !important;
        }

        .ag-theme-streamlit .ag-status-bar {
            display: none !important;
        }

        /* ========================================
           EXPLORE STORIES - DETAIL PANEL STYLING
           Make the detail panel more prominent
           ======================================== */

        /* Style the detail panel container (after the --- divider) */
        [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"]:has([data-testid="stMarkdownContainer"]) {
            background: #262626;
            border-radius: 12px;
            padding: 32px;
            margin-top: 24px;
            border: 1px solid #333;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }

        /* Detail panel header section */
        .detail-panel-header {
            border-bottom: 2px solid #404040;
            padding-bottom: 20px;
            margin-bottom: 24px;
        }

        .detail-panel-title {
            font-size: 24px !important;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 12px;
        }

        /* Increase font sizes in detail panel */
        [data-testid="stMarkdownContainer"] h3 {
            font-size: 20px !important;
            font-weight: 600;
            color: #ffffff;
            margin-top: 20px;
            margin-bottom: 12px;
        }

        [data-testid="stMarkdownContainer"] p {
            font-size: 15px;
            line-height: 1.7;
            color: #e0e0e0;
        }

        /* Make detail panel content more spacious */
        [data-testid="stMarkdownContainer"] li {
            margin-bottom: 10px;
            line-height: 1.7;
            font-size: 14px;
        }

        /* Fix selectbox - only in main app content, not settings panel */
        section[data-testid="stAppViewContainer"] div[data-baseweb="select"] {
            max-width: none !important;
            min-width: 100% !important;
        }

        section[data-testid="stAppViewContainer"] div[data-baseweb="select"] > div {
            max-width: none !important;
            width: 100% !important;
        }

        /* Fix the value container (what shows when closed) */
        section[data-testid="stAppViewContainer"] div[data-baseweb="select"] div[class*="ValueContainer"] {
            max-width: none !important;
            overflow: visible !important;
        }

        section[data-testid="stAppViewContainer"] div[data-baseweb="select"] div[class*="SingleValue"] {
            max-width: none !important;
            overflow: visible !important;
            text-overflow: clip !important;
            white-space: normal !important;
        }

        /* Fix dropdown menu container and list width - only in main app */
        section[data-testid="stAppViewContainer"] div[data-baseweb="popover"] {
            max-width: none !important;
            width: auto !important;
        }

        section[data-testid="stAppViewContainer"] ul[role="listbox"] {
            max-width: none !important;
            min-width: 350px !important;
            width: auto !important;
        }

        /* Fix individual dropdown options - only in main app */
        section[data-testid="stAppViewContainer"] li[role="option"] {
            white-space: nowrap !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }

        /* Bottom-align filter controls in row */
        [data-testid="column"] {
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# 2) Hero + stats (wireframe look)
# ---------------------------------------------------------
def render_home_hero_and_stats():
    css_once()

    # Hero with gradient background - square edges, centered content, full-width gradient
    st.markdown(
        """
        <style>
        .hero-gradient-wrapper {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 0px;  /* Square edges */
            margin: -1rem 0 0 0;  /* Negative top margin to pull up to navbar */
            padding: 0;
            width: 100%;
        }
        .hero-content {
            max-width: 1200px;
            margin: 0 auto;
            text-align: center;
            padding: 60px 40px;
            color: white;
        }
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
                    Explore my portfolio of 120+ projects or chat with Agy 🐾 to learn about my experience.
                </p>
                <div style="display: flex; gap: 16px; justify-content: center; align-items: center; flex-wrap: wrap;">
                    <a href="#explore" style="display: inline-block; padding: 14px 32px; background: white; color: #667eea; border: 2px solid white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
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

    # Stats bar - wireframe style with borders, no cards
    st.markdown(
        """
        <style>
        .stats-bar {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            border-bottom: 2px solid #e0e0e0;
            margin-bottom: 50px;
        }

        .stat {
            padding: 30px;
            text-align: center;
            border-right: 1px solid #e0e0e0;
        }

        .stat:last-child {
            border-right: none;
        }

        .stat-number {
            font-size: 36px;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 8px;
            display: block;
        }

        .stat-label {
            font-size: 14px;
            color: #999999;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        @media (max-width: 768px) {
            .stats-bar {
                grid-template-columns: repeat(2, 1fr);
            }
            .stat:nth-child(2) {
                border-right: none;
            }
        }

        @media (max-width: 480px) {
            .stats-bar {
                grid-template-columns: 1fr;
            }
            .stat {
                border-right: none;
                border-bottom: 1px solid #e0e0e0;
            }
            .stat:last-child {
                border-bottom: none;
            }
        }
        </style>
        <div class="stats-bar">
            <div class="stat">
                <div class="stat-number">20+</div>
                <div class="stat-label">Years Experience</div>
            </div>
            <div class="stat">
                <div class="stat-number">120+</div>
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

    st.markdown(
        '<h2 class="matt-section-title">What would you like to explore?</h2>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# 3) Starters grid (6 cards, clicks route to tabs)
# ---------------------------------------------------------
def render_home_starters():
    starter_cards = [
        {
            "icon": "🏦",
            "title": "Financial Services / Banking",
            "desc": "Banking modernization, payments, compliance, core banking systems",
            "examples": '"JP Morgan Chase (22)" • "RBC (11)" • "Fiserv (7)" • "American Express (3)" • "Capital One (2)" • "HSBC (2)"',
            "tab": "**cross_industry_landing_page88"
        },
        {
            "icon": "🌐",
            "title": "Cross-Industry Transformation",
            "desc": "Multi-sector consulting, platform engineering, organizational transformation",
            "examples": '"Accenture (13)" • "JP Morgan Chase (1)" • "Multiple Clients (38)" • "U.S. Regulatory Agency (1)"',
            "tab": "**cross_industry_landing_page**"
        },
        {
            "icon": "🚀",
            "title": "Product Innovation & Strategy",
            "desc": "Cloud-native products from zero. Lean, rapid prototyping, OKRs, MVPs",
            "examples": '"How do you do hypothesis-driven development?" • "How do you shift to product thinking?"',
            "tab": "Ask MattGPT"
        },
        {
            "icon": "🔧",
            "title": "App Modernization",    
            "desc": "Modernizing legacy apps with event-driven design, microservices, and zero-defect delivery",
            "examples": '"How do you modernize monoliths into microservices?" • "How do you approach application rationalization?"',
            "tab": "Ask MattGPT"
        },
        {
            "icon": "💡",
            "title": "Consulting & Transformation",
            "desc": "Fortune 500 advisory, operating models, 3-20x acceleration, New Ways of Working",
            "examples": '"How do you achieve 4x faster delivery?" • "How do you align cross-functional teams?"',
            "tab": "Ask MattGPT"
        },
        {
            "icon": "👥",
            "title": "Teams & Talent Development",
            "desc": "300+ professionals trained, innovation centers, servant leadership",
            "examples": '"How did you scale the innovation center to 150+ people?" • "How did you equip teams for New IT ways of working?"',
            "tab": "Ask MattGPT"
        },
        {
            "icon": "💬",
            "title": "Quick Question",
            "desc": "Ask me anything — from building MattGPT to leading global programs.",
            "examples": '"How did you build MattGPT?" • "How do you overcome the challenges of scaling to 150+ engineers?"',
            "tab": "Ask MattGPT"
        }
    ]
    
    st.markdown('<div class="matt-container">', unsafe_allow_html=True)
    
    # Add inline CSS for cards - wireframe style
    st.markdown("""
    <style>
    /* Industry cards - gradient background, white text */
    .industry-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 32px;
        border-radius: 12px;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        transition: all 0.3s ease;
        margin-bottom: 20px;
        border: none !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
    }
    .industry-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
    }
    .industry-card h3 {
        color: white !important;
        font-size: 24px !important;
        font-weight: 700 !important;
        margin-bottom: 8px !important;
    }
    .industry-card .project-count {
        color: rgba(255,255,255,0.9);
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 16px;
    }
    .industry-card .card-desc {
        color: rgba(255, 255, 255, 0.95);
        margin-bottom: 16px;
        line-height: 1.5;
        font-size: 15px;
    }
    .industry-card .tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 20px;
        flex-grow: 1;
    }
    .industry-card .tag {
        background: rgba(255,255,255,0.25);
        color: white;
        padding: 6px 12px;
        border-radius: 16px;
        font-size: 13px;
        font-weight: 500;
    }

    /* Capability cards - white background, dark text */
    .capability-card {
        background: white;
        color: #333;
        padding: 32px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        transition: all 0.3s ease;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
    }
    .capability-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12) !important;
        border-color: #667eea;
    }
    .capability-card h3 {
        color: #333 !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        margin-bottom: 12px !important;
    }
    .capability-card .card-desc {
        color: #666;
        margin-bottom: 16px;
        line-height: 1.6;
        font-size: 15px;
        flex-grow: 1;
    }
    .capability-card .card-examples {
        color: #999;
        font-style: italic;
        font-size: 14px;
        line-height: 1.5;
        margin-bottom: 16px;
    }

    /* Quick Question card - gradient like industry cards */
    .quick-question-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 32px;
        border-radius: 12px;
        min-height: 200px;
        transition: all 0.3s ease;
        margin-bottom: 20px;
        border: none !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
    }
    .quick-question-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # First row - Industry cards (2 columns, gradient background)
    col1, col2 = st.columns(2)

    with col1:
        card = starter_cards[0]
        st.markdown(f"""
        <div class="industry-card">
            <div style="font-size: 48px; margin-bottom: 16px;">{card['icon']}</div>
            <h3>{card['title']}</h3>
            <div class="project-count">47 projects</div>
            <div class="card-desc">{card['desc']}</div>
            <div class="tags">
                <span class="tag">JP Morgan Chase (22)</span>
                <span class="tag">RBC (11)</span>
                <span class="tag">Fiserv (7)</span>
                <span class="tag">American Express (3)</span>
                <span class="tag">Capital One (2)</span>
                <span class="tag">HSBC (2)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("See Banking Projects →", key="btn_0", use_container_width=False):
            st.session_state["active_tab"] = "Banking"
            st.rerun()


    with col2:
        card = starter_cards[1]
        st.markdown(f"""
        <div class="industry-card">
            <div style="font-size: 48px; margin-bottom: 16px;">{card['icon']}</div>
            <h3>{card['title']}</h3>
            <div class="project-count">53 projects</div>
            <div class="card-desc">{card['desc']}</div>
            <div class="tags">
                <span class="tag">Accenture (13)</span>
                <span class="tag">Multiple Clients (38)</span>
                <span class="tag">JP Morgan Chase (1)</span>
                <span class="tag">U.S. Regulatory Agency (1)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Browse Transformations →", key="btn_1", use_container_width=False):
            st.session_state["active_tab"] = "Cross-Industry"
            st.rerun()


    # Second row - Capability cards (white background)
    col3, col4 = st.columns(2)

    with col3:
        card = starter_cards[2]
        st.markdown(f"""
        <div class="capability-card">
            <div style="font-size: 40px; margin-bottom: 16px;">{card['icon']}</div>
            <h3>{card['title']}</h3>
            <div class="card-desc">{card['desc']}</div>
            <div class="card-examples">{card['examples']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Explore Product Work →", key="btn_2", use_container_width=False):
            st.session_state["__inject_user_turn__"] = "Tell me about your product innovation approach"
            st.session_state["active_tab"] = card["tab"]
            st.session_state.pop("__ctx_locked__", None)
            st.session_state.pop("active_context", None)
            st.session_state["skip_home_menu"] = True
            st.rerun()

    with col4:
        card = starter_cards[3]
        st.markdown(f"""
        <div class="capability-card">
            <div style="font-size: 40px; margin-bottom: 16px;">{card['icon']}</div>
            <h3>{card['title']}</h3>
            <div class="card-desc">{card['desc']}</div>
            <div class="card-examples">{card['examples']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Case Studies →", key="btn_3", use_container_width=False):
            st.session_state["__inject_user_turn__"] = "How do you modernize legacy applications?"
            st.session_state["active_tab"] = card["tab"]
            st.session_state.pop("__ctx_locked__", None)
            st.session_state.pop("active_context", None)
            st.session_state["skip_home_menu"] = True
            st.rerun()


    # Third row - Capability cards (white background)
    col5, col6 = st.columns(2)

    with col5:
        card = starter_cards[4]
        st.markdown(f"""
        <div class="capability-card">
            <div style="font-size: 40px; margin-bottom: 16px;">{card['icon']}</div>
            <h3>{card['title']}</h3>
            <div class="card-desc">{card['desc']}</div>
            <div class="card-examples">{card['examples']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Browse Transformations →", key="btn_4", use_container_width=False):
            st.session_state["__inject_user_turn__"] = "How do you achieve faster delivery for Fortune 500 clients?"
            st.session_state["active_tab"] = card["tab"]
            st.session_state.pop("__ctx_locked__", None)
            st.session_state.pop("active_context", None)
            st.session_state["skip_home_menu"] = True
            st.rerun()

    with col6:
        card = starter_cards[5]
        st.markdown(f"""
        <div class="capability-card">
            <div style="font-size: 40px; margin-bottom: 16px;">{card['icon']}</div>
            <h3>{card['title']}</h3>
            <div class="card-desc" style="color: #667eea; font-weight: 600; margin-bottom: 12px;">300+ professionals trained</div>
            <div class="card-desc">{card['desc']}</div>
            <div class="card-examples">{card['examples']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Check Team Stories →", key="btn_5", use_container_width=False):
            st.session_state["__inject_user_turn__"] = "How did you scale and develop innovation teams?"
            st.session_state["active_tab"] = card["tab"]
            st.session_state.pop("__ctx_locked__", None)
            st.session_state.pop("active_context", None)
            st.session_state["skip_home_menu"] = True
            st.rerun()

    # Full-width "Quick Question" card at bottom
    card = starter_cards[6]
    st.markdown(f"""
    <div class="quick-question-card">
        <div style="display: flex; align-items: center; gap: 24px; margin-bottom: 20px;">
            <img src="https://raw.githubusercontent.com/mcpugmire1/mattgpt-design-spec/main/brand-kit/chat_avatars/agy_avatar_128_dark.png"
                 alt="Agy"
                 style="width: 64px; height: 64px; border-radius: 50%; border: 3px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
            <div>
                <h3 style="font-size: 24px; font-weight: 700; margin-bottom: 4px; color: white;">{card['title']}</h3>
                <div style="font-size: 16px; font-weight: 600; color: rgba(255,255,255,0.95);">Ask Agy 🐾 anything</div>
            </div>
        </div>
        <div style="font-size: 16px; margin-bottom: 16px; color: rgba(255,255,255,0.95); line-height: 1.6;">
            From building MattGPT to leading global programs — Agy can help you explore 20+ years of transformation experience.
        </div>
        <div style="font-size: 14px; font-style: italic; color: rgba(255,255,255,0.85); margin-bottom: 20px;">
            {card['examples']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ask Agy 🐾", key="btn_6", use_container_width=False):
        # This one just opens Ask MattGPT without a pre-loaded question
        st.session_state["active_tab"] = card["tab"]
        st.session_state["skip_home_menu"] = True
        st.rerun()


    st.markdown('</div>', unsafe_allow_html=True)

    # JAVASCRIPT: Force purple button styles using components.html
    import streamlit.components.v1 as components
    components.html("""
    <script>
    (function() {
        function applyPurpleButtons() {
            const iframeDoc = window.parent.document;

            // Category buttons 0-5: white with purple text
            for (let i = 0; i <= 5; i++) {
                const container = iframeDoc.querySelector('.st-key-btn_' + i);
                if (container) {
                    const button = container.querySelector('button');
                    if (button && !button.dataset.purpled) {
                        button.dataset.purpled = 'true';
                        button.style.cssText = 'background: white !important; background-color: white !important; background-image: none !important; border: 2px solid #e5e5e5 !important; color: #8B5CF6 !important;';

                        button.onmouseenter = function() {
                            this.style.cssText = 'background: #8B5CF6 !important; background-color: #8B5CF6 !important; background-image: none !important; border: 2px solid #8B5CF6 !important; color: white !important;';
                        };
                        button.onmouseleave = function() {
                            this.style.cssText = 'background: white !important; background-color: white !important; background-image: none !important; border: 2px solid #e5e5e5 !important; color: #8B5CF6 !important;';
                        };
                    }
                }
            }

            // Ask Agy button (btn_6): purple gradient - BIGGER SIZE
            const agyContainer = iframeDoc.querySelector('.st-key-btn_6');
            if (agyContainer) {
                const agyButton = agyContainer.querySelector('button');
                if (agyButton && !agyButton.dataset.purpled) {
                    agyButton.dataset.purpled = 'true';
                    agyButton.style.cssText = 'background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%) !important; background-color: #8B5CF6 !important; border: none !important; color: white !important; padding: 14px 28px !important; font-size: 15px !important; font-weight: 600 !important; border-radius: 8px !important; box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25) !important;';

                    agyButton.onmouseenter = function() {
                        this.style.cssText = 'background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important; background-color: #7C3AED !important; border: none !important; color: white !important; padding: 14px 28px !important; font-size: 15px !important; font-weight: 600 !important; border-radius: 8px !important; box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4) !important; transform: translateY(-2px) !important;';
                    };
                    agyButton.onmouseleave = function() {
                        this.style.cssText = 'background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%) !important; background-color: #8B5CF6 !important; border: none !important; color: white !important; padding: 14px 28px !important; font-size: 15px !important; font-weight: 600 !important; border-radius: 8px !important; box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25) !important;';
                    };
                }
            }
        }

        setTimeout(applyPurpleButtons, 100);
        setTimeout(applyPurpleButtons, 500);
        setTimeout(applyPurpleButtons, 1000);
        setTimeout(applyPurpleButtons, 2000);
    })();
    </script>
    """, height=0)

    # Footer
    footer_html = """
    <div style="background: #2c3e50; color: white; padding: 48px 40px; text-align: center; margin-top: 60px; border-radius: 16px;">
        <h3 style="font-size: 28px; margin-bottom: 12px; color: white;">Let's Connect</h3>
        <p style="font-size: 16px; margin-bottom: 8px; opacity: 0.9;">
            Exploring Director/VP opportunities in <strong>Product Leadership</strong>, <strong>Platform Engineering</strong>, and <strong>Organizational Transformation</strong>
        </p>
        <p style="font-size: 14px; margin-bottom: 32px; opacity: 0.75;">
            Available for immediate start • Remote or Atlanta-based • Open to consulting engagements
        </p>
        <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;">
            <a href="mailto:mcpugmire@gmail.com" style="padding: 12px 28px; background: #8B5CF6; color: white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
                📧 mcpugmire@gmail.com
            </a>
            <a href="https://www.linkedin.com/in/matt-pugmire/" target="_blank" style="padding: 12px 28px; background: rgba(255,255,255,0.1); color: white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
                💼 LinkedIn
            </a>
            <a href="#ask" style="padding: 12px 28px; background: rgba(255,255,255,0.1); color: white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
                🐾 Ask Agy
            </a>
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)


def render_banking_landing_page():
    """Render Banking / Financial Services landing page using Streamlit components"""

    # Inject CSS for this page
    st.markdown("""
    <style>
    /* Landing page specific styles */
    .stApp {
        background: white !important;
    }
    .main .block-container {
        max-width: 1400px !important;
        padding: 2rem 1rem !important;
        background: white !important;
    }
    h1 {
        color: #2c3e50 !important;
        font-size: 28px !important;
        margin-bottom: 8px !important;
    }
    .subtitle {
        color: #7f8c8d;
        font-size: 14px;
        margin-bottom: 30px;
    }
    .section-header {
        font-size: 20px;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 30px;
        margin-bottom: 16px;
    }
    /* Client pills */
    .client-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 40px;
    }
    .client-pill {
        background: white;
        border: 1px solid #d0d0d0;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 13px;
        color: #555;
        display: inline-block;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .client-pill:hover {
        border-color: #8B5CF6;
        color: #8B5CF6;
        background: rgba(139, 92, 246, 0.05);
    }
    /* Category cards */
    .capability-card {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 10px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        height: 100%;
    }
    .capability-card:hover {
        border-color: #7c3aed;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.15);
        transform: translateY(-3px);
    }
    .card-icon {
        font-size: 32px;
        margin-bottom: 14px;
        display: block;
    }
    .card-title {
        font-size: 18px;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 8px;
        line-height: 1.3;
    }
    .card-count {
        font-size: 14px;
        color: #7c3aed;
        font-weight: 700;
        margin-bottom: 10px;
        display: block;
    }
    .card-desc {
        font-size: 14px;
        color: #6b7280;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("Financial Services / Banking")

    # Subtitle - "ask Agy" is emphasized (not clickable, use CTA button below)
    st.markdown('''
    <p class="subtitle">55 projects across 16 specialized areas — or
    <span style="color: #8B5CF6; font-weight: 700;">ask Agy 🐾</span>
    to find what you're looking for</p>
    ''', unsafe_allow_html=True)

    st.markdown("---")

    # Clients section
    st.markdown('<h2 class="section-header">Clients</h2>', unsafe_allow_html=True)

    clients_html = """
    <div class="client-pills">
        <span class="client-pill">JPMorgan Chase (33)</span>
        <span class="client-pill">RBC (11)</span>
        <span class="client-pill">Fiserv (7)</span>
        <span class="client-pill">American Express (3)</span>
        <span class="client-pill">Capital One (2)</span>
        <span class="client-pill">HSBC (2)</span>
    </div>
    """
    st.markdown(clients_html, unsafe_allow_html=True)

    # Categories section
    st.markdown('<h2 class="section-header">Explore by Capability</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 14px; color: #7f8c8d; margin-bottom: 24px;">Browse 55 banking projects organized by specialty area</p>', unsafe_allow_html=True)

    # Banking categories data
    banking_categories = [
        ("⚡", "Agile Transformation & Delivery", 8, "Scaling agile practices, delivery acceleration, team transformation"),
        ("🔧", "Modern Engineering Practices & Solutions", 8, "DevOps, CI/CD, cloud-native engineering, modern toolchains"),
        ("💰", "Global Payments & Treasury Solutions", 7, "Payment platforms, treasury systems, real-time processing"),
        ("🎯", "Technology Strategy & Advisory", 5, "Architecture roadmaps, strategic planning, technology vision"),
        ("📊", "Program Management & Governance", 4, "Large-scale program delivery, governance frameworks, PMO"),
        ("📱", "Digital Product Development", 3, "Mobile banking, customer experiences, digital channels"),
        ("📈", "Data & Analytics Solutions", 3, "Data platforms, analytics, business intelligence"),
        ("🔄", "Business Process Optimization", 3, "Process reengineering, workflow automation, efficiency"),
        ("🤝", "Cross-Functional Collaboration & Team Enablement", 3, "Team alignment, collaboration frameworks, culture change"),
        ("☁️", "Cloud Transformation & Migration", 2, "Cloud strategy, migrations, hybrid cloud architectures"),
        ("🚀", "Application Modernization", 2, "Legacy modernization, microservices, platform engineering"),
        ("🎓", "Client Enablement & Sustainable Innovation", 1, "Knowledge transfer, capability building, innovation programs"),
        ("🔌", "Enterprise Integration & API Management", 2, "API platforms, integration architecture, service mesh"),
        ("🔒", "Security & Compliance Solutions", 2, "Regulatory compliance, security architecture, risk management"),
        ("🚢", "DevOps & Continuous Delivery", 1, "Automation, deployment pipelines, continuous integration"),
        ("📦", "VPP Adoption Enablement Developer Toolkit", 1, "Developer experience, tooling, productivity platforms"),
    ]

    # Render cards in 3-column grid (clickable to navigate to Explore Stories)
    for i in range(0, len(banking_categories), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(banking_categories):
                icon, title, count, desc = banking_categories[i + j]
                with cols[j]:
                    # Make card clickable by wrapping in container with button
                    st.markdown(f"""
                    <div class="capability-card" style="cursor: pointer;">
                        <div class="card-icon">{icon}</div>
                        <div class="card-title">{title}</div>
                        <div class="card-count">{count} projects</div>
                        <div class="card-desc">{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Invisible button for navigation
                    if st.button("", key=f"banking_card_{i}_{j}", help=f"View {title} projects"):
                        st.session_state["active_tab"] = "Explore Stories"
                        st.rerun()

    # CTA section
    st.markdown("<br><br>", unsafe_allow_html=True)

    cta_html = """
    <div class="cta-section">
        <h2 class="cta-heading">Need a different way to explore?</h2>
        <p class="cta-subtext">Ask Agy 🐾 about Matt's banking experience — get conversational answers tailored to your needs</p>
    </div>
    <style>
    .cta-section {
        background: #f8f9fa;
        padding: 48px 32px;
        text-align: center;
        border-radius: 12px;
        border: 1px solid #e5e5e5;
        margin: 40px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .cta-heading {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #1a202c !important;
        margin-bottom: 16px !important;
    }
    .cta-subtext {
        font-size: 16px;
        color: #6b7280;
        margin-bottom: 0px;
        line-height: 1.6;
    }
    </style>
    """
    st.markdown(cta_html, unsafe_allow_html=True)

    # Center the button using columns
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Ask Agy 🐾", key="banking_cta", use_container_width=True):
            st.session_state["active_tab"] = "Ask MattGPT"
            st.rerun()

    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)

    footer_html = """
    <div style="background: #334155; color: white; padding: 80px 40px; text-align: center; margin-top: 80px;">
        <h2 style="font-size: 32px; font-weight: 700; margin-bottom: 24px; color: white; line-height: 1.2;">Let's Connect</h2>
        <p style="font-size: 16px; margin-bottom: 16px; color: rgba(255, 255, 255, 0.95); line-height: 1.6; max-width: 850px; margin-left: auto; margin-right: auto;">
            Exploring Director/VP opportunities in <strong>Product Leadership</strong>, <strong>Platform Engineering</strong>, and <strong>Organizational Transformation</strong>
        </p>
        <p style="font-size: 14px; margin-bottom: 40px; color: rgba(255, 255, 255, 0.8); line-height: 1.5;">
            Available for immediate start • Remote or Atlanta-based • Open to consulting engagements
        </p>
        <div style="display: flex; gap: 18px; justify-content: center; flex-wrap: wrap; align-items: center;">
            <a href="mailto:mcpugmire@gmail.com" style="padding: 15px 32px; background: #8b5cf6; color: white; border-radius: 8px; font-size: 16px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; transition: all 0.2s ease;">
                📧 mcpugmire@gmail.com
            </a>
            <a href="https://www.linkedin.com/in/mattpugmire/" target="_blank" style="padding: 15px 32px; background: rgba(255,255,255,0.08); color: white; border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; font-size: 16px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; transition: all 0.2s ease;">
                💼 LinkedIn
            </a>
            <a href="#ask-mattgpt" style="padding: 15px 32px; background: rgba(255,255,255,0.08); color: white; border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; font-size: 16px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; transition: all 0.2s ease;">
                🐾 Ask Agy
            </a>
        </div>
    </div>
    <style>
    .landing-footer {
        background: #334155;
        color: white;
        padding: 72px 40px;
        text-align: center;
        margin-top: 80px;
        border-radius: 0;
        margin-left: -1rem;
        margin-right: -1rem;
    }
    .footer-heading {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: white !important;
        margin-bottom: 20px !important;
        margin-top: 0 !important;
        line-height: 1.2 !important;
    }
    .footer-subheading {
        font-size: 16px;
        color: rgba(255, 255, 255, 0.95);
        margin-bottom: 12px;
        line-height: 1.6;
        max-width: 850px;
        margin-left: auto;
        margin-right: auto;
    }
    .footer-subheading strong {
        font-weight: 700;
        color: white;
    }
    .footer-availability {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 40px;
        margin-top: 10px;
        line-height: 1.5;
    }
    .footer-buttons {
        display: flex;
        gap: 18px;
        justify-content: center;
        flex-wrap: wrap;
        align-items: center;
    }
    .footer-btn {
        padding: 15px 32px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        white-space: nowrap;
        color: white !important;
    }
    .footer-btn svg {
        fill: white !important;
        stroke: white !important;
    }
    .footer-btn-primary {
        background: #8b5cf6;
        color: white !important;
        border: none;
    }
    .footer-btn-primary:hover {
        background: #7c3aed;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(139, 92, 246, 0.4);
        color: white !important;
    }
    .footer-btn-secondary {
        background: rgba(255, 255, 255, 0.08);
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .footer-btn-secondary:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.25);
        transform: translateY(-2px);
        color: white !important;
    }
    @media (max-width: 768px) {
        .footer-buttons {
            flex-direction: column;
            align-items: stretch;
        }
        .footer-btn {
            width: 100%;
            max-width: 320px;
        }
    }
    </style>
    """
    st.markdown(footer_html, unsafe_allow_html=True)


def render_banking_landing_page_OLD():
    """Render Banking / Financial Services landing page matching wireframe"""

    # Build clients pills HTML
    clients = [
        ("JPMorgan Chase", 33),
        ("RBC", 11),
        ("Fiserv", 7),
        ("American Express", 3),
        ("Capital One", 2),
        ("HSBC", 2),
    ]

    clients_html = ""
    for client, count in clients:
        clients_html += f'<div class="client-pill">{client} ({count})</div>\n'

    # Build category cards HTML
    banking_categories = [
        ("⚡", "Agile Transformation & Delivery", 8, "Scaling agile practices, delivery acceleration, team transformation"),
        ("🔧", "Modern Engineering Practices & Solutions", 8, "DevOps, CI/CD, cloud-native engineering, modern toolchains"),
        ("💰", "Global Payments & Treasury Solutions", 7, "Payment platforms, treasury systems, real-time processing"),
        ("🎯", "Technology Strategy & Advisory", 5, "Architecture roadmaps, strategic planning, technology vision"),
        ("📊", "Program Management & Governance", 4, "Large-scale program delivery, governance frameworks, PMO"),
        ("📱", "Digital Product Development", 3, "Mobile banking, customer experiences, digital channels"),
        ("📈", "Data & Analytics Solutions", 3, "Data platforms, analytics, business intelligence"),
        ("🔄", "Business Process Optimization", 3, "Process reengineering, workflow automation, efficiency"),
        ("🤝", "Cross-Functional Collaboration & Team Enablement", 3, "Team alignment, collaboration frameworks, culture change"),
        ("☁️", "Cloud Transformation & Migration", 2, "Cloud strategy, migrations, hybrid cloud architectures"),
        ("🚀", "Application Modernization", 2, "Legacy modernization, microservices, platform engineering"),
        ("🎓", "Client Enablement & Sustainable Innovation", 1, "Knowledge transfer, capability building, innovation programs"),
        ("🔌", "Enterprise Integration & API Management", 2, "API platforms, integration architecture, service mesh"),
        ("🔒", "Security & Compliance Solutions", 2, "Regulatory compliance, security architecture, risk management"),
        ("🚢", "DevOps & Continuous Delivery", 1, "Automation, deployment pipelines, continuous integration"),
        ("📦", "VPP Adoption Enablement Developer Toolkit", 1, "Developer experience, tooling, productivity platforms"),
    ]

    cards_html = ""
    for icon, title, count, desc in banking_categories:
        cards_html += f"""
        <div class="category-card">
            <span class="category-icon">{icon}</span>
            <h3 class="category-title">{title}</h3>
            <p class="category-count">{count} projects</p>
            <p class="category-desc">{desc}</p>
        </div>
        """

    # Render complete page as single HTML block
    page_html = f"""
    <style>
        .landing-page-header {{
            padding: 30px 0;
            border-bottom: 2px solid #e0e0e0;
            margin-bottom: 30px;
        }}
        .landing-page-header h1 {{
            font-size: 28px;
            color: #2c3e50;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        .landing-page-header p {{
            color: #7f8c8d;
            font-size: 14px;
        }}
        .ask-agy-link {{
            color: #667eea;
            font-weight: 600;
            text-decoration: underline;
            text-decoration-color: rgba(102, 126, 234, 0.3);
            text-underline-offset: 2px;
        }}
        .section-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 16px;
            color: #2c3e50;
        }}
        .section-subtitle {{
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 24px;
        }}
        .clients-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 40px;
        }}
        .client-pill {{
            background: white;
            border: 1px solid #d0d0d0;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            color: #555;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
        }}
        .client-pill:hover {{
            border-color: #667eea;
            color: #667eea;
            background: rgba(102, 126, 234, 0.05);
        }}
        .categories-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }}
        @media (max-width: 1200px) {{
            .categories-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        @media (max-width: 768px) {{
            .categories-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        .category-card {{
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 24px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .category-card:hover {{
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
            transform: translateY(-2px);
        }}
        .category-icon {{
            font-size: 28px;
            margin-bottom: 12px;
            display: block;
        }}
        .category-title {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 6px;
            color: #2c3e50;
        }}
        .category-count {{
            font-size: 14px;
            color: #667eea;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        .category-desc {{
            font-size: 13px;
            color: #7f8c8d;
            line-height: 1.5;
            margin: 0;
        }}
        .cta-box {{
            background: #f8f9fa;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 32px;
            text-align: center;
            margin-top: 30px;
            margin-bottom: 20px;
        }}
        .cta-box h3 {{
            font-size: 18px;
            color: #2c3e50;
            margin-bottom: 12px;
        }}
        .cta-box p {{
            font-size: 14px;
            color: #7f8c8d;
            line-height: 1.6;
            margin: 0;
        }}
    </style>

    <div class="landing-page-header">
        <h1>Financial Services / Banking</h1>
        <p>55 projects across 16 specialized areas — or <span class="ask-agy-link">ask Agy 🐾</span> to find what you're looking for</p>
    </div>

    <h2 class="section-title">Clients</h2>
    <div class="clients-container">
        {clients_html}
    </div>

    <h2 class="section-title">Explore by Capability</h2>
    <p class="section-subtitle">Browse 55 banking projects organized by specialty area</p>

    <div class="categories-grid">
        {cards_html}
    </div>

    <div class="cta-box">
        <h3>Can't find what you're looking for?</h3>
        <p>Ask Agy 🐾 to help you explore Matt's banking experience — just describe what you're looking for in your own words</p>
    </div>
    """

    st.markdown(page_html, unsafe_allow_html=True)

    if st.button("Ask Agy 🐾", key="banking_cta", use_container_width=False):
        st.session_state["active_tab"] = "Ask MattGPT"
        st.rerun()

    # Footer
    footer_html = """
    <div style="background: #2c3e50; color: white; padding: 48px 40px; text-align: center; margin-top: 60px; border-radius: 16px;">
        <h3 style="font-size: 28px; margin-bottom: 12px; color: white;">Let's Connect</h3>
        <p style="font-size: 16px; margin-bottom: 8px; opacity: 0.9;">
            Exploring Director/VP opportunities in <strong>Product Leadership</strong>, <strong>Platform Engineering</strong>, and <strong>Organizational Transformation</strong>
        </p>
        <p style="font-size: 14px; margin-bottom: 32px; opacity: 0.75;">
            Available for immediate start • Remote or Atlanta-based • Open to consulting engagements
        </p>
        <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;">
            <a href="mailto:mcpugmire@gmail.com" style="padding: 12px 28px; background: #8B5CF6; color: white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
                📧 mcpugmire@gmail.com
            </a>
            <a href="https://www.linkedin.com/in/matt-pugmire/" target="_blank" style="padding: 12px 28px; background: rgba(255,255,255,0.1); color: white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
                💼 LinkedIn
            </a>
            <a href="#ask" style="padding: 12px 28px; background: rgba(255,255,255,0.1); color: white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
                🐾 Ask Agy
            </a>
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

def render_cross_industry_landing_page():
    """Render Cross-Industry Transformation landing page using Streamlit components"""

    # Inject CSS for this page
    st.markdown("""
    <style>
    /* Landing page specific styles */
    .stApp {
        background: white !important;
    }
    .main .block-container {
        max-width: 1400px !important;
        padding: 2rem 1rem !important;
        background: white !important;
    }
    h1 {
        color: #2c3e50 !important;
        font-size: 28px !important;
        margin-bottom: 8px !important;
    }
    .subtitle {
        color: #7f8c8d;
        font-size: 14px;
        margin-bottom: 30px;
    }
    .section-header {
        font-size: 20px;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 30px;
        margin-bottom: 16px;
    }
    /* Client pills */
    .client-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 40px;
    }
    .client-pill {
        background: white;
        border: 1px solid #d0d0d0;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 13px;
        color: #555;
        display: inline-block;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .client-pill:hover {
        border-color: #8B5CF6;
        color: #8B5CF6;
        background: rgba(139, 92, 246, 0.05);
    }
    /* Category cards */
    .capability-card {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 10px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        height: 100%;
    }
    .capability-card:hover {
        border-color: #7c3aed;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.15);
        transform: translateY(-3px);
    }
    .card-icon {
        font-size: 32px;
        margin-bottom: 14px;
        display: block;
    }
    .card-title {
        font-size: 18px;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 8px;
        line-height: 1.3;
    }
    .card-count {
        font-size: 14px;
        color: #7c3aed;
        font-weight: 700;
        margin-bottom: 10px;
        display: block;
    }
    .card-desc {
        font-size: 14px;
        color: #6b7280;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("Cross-Industry Transformation")

    # Subtitle - "ask Agy" is styled like a link but users can use the CTA button below
    st.markdown('''
    <p class="subtitle">51 projects across 15+ transformation capabilities — or
    <a href="#ask-mattgpt" style="color: #8B5CF6; font-weight: 600; text-decoration: underline; cursor: pointer;"
       onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'Ask MattGPT'}, '*'); return false;">
       ask Agy 🐾
    </a> to find what you're looking for</p>
    ''', unsafe_allow_html=True)

    st.markdown("---")

    # Industries section
    st.markdown('<h2 class="section-header">Industries Served</h2>', unsafe_allow_html=True)

    industries_html = """
    <div class="client-pills">
        <span class="client-pill">Banking & Financial Services</span>
        <span class="client-pill">Healthcare & Life Sciences</span>
        <span class="client-pill">Manufacturing</span>
        <span class="client-pill">Retail & Consumer Goods</span>
        <span class="client-pill">Transportation & Logistics</span>
        <span class="client-pill">Telecommunications</span>
        <span class="client-pill">Public Sector</span>
        <span class="client-pill">Technology & Software</span>
    </div>
    """
    st.markdown(industries_html, unsafe_allow_html=True)

    # Categories section
    st.markdown('<h2 class="section-header">Explore by Transformation Capability</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 14px; color: #7f8c8d; margin-bottom: 24px;">Browse 51 cross-industry projects organized by transformation approach and methodology</p>', unsafe_allow_html=True)

    # Cross-industry categories data
    cross_industry_categories = [
        ("⚡", "Agile Transformation & Delivery", 8, "Scaling agile practices, SAFe, Scrum at scale, delivery acceleration across industries"),
        ("🔧", "Modern Engineering Practices & Solutions", 8, "DevOps, CI/CD, test automation, engineering excellence, quality practices"),
        ("🤝", "Cross-Functional Collaboration & Team Enablement", 8, "Breaking down silos, team alignment, collaboration frameworks, culture change"),
        ("🎓", "Client Enablement & Sustainable Innovation", 7, "Knowledge transfer, capability building, innovation centers, sustainable practices"),
        ("🎯", "Technology Strategy & Advisory", 5, "Architecture roadmaps, strategic planning, technology vision, enterprise architecture"),
        ("📊", "Program Management & Governance", 4, "Large-scale delivery, governance frameworks, PMO setup, risk management"),
        ("🚢", "DevOps & Continuous Delivery", 3, "Deployment automation, pipeline engineering, continuous integration, release management"),
        ("📱", "Digital Product Development", 3, "Product thinking, user-centered design, rapid prototyping, product-market fit"),
        ("🚀", "Application Modernization", 3, "Legacy transformation, microservices migration, platform engineering"),
        ("🔄", "Business Process Optimization", 3, "Process reengineering, workflow automation, efficiency improvements, lean practices"),
        ("📈", "Data & Analytics Solutions", 3, "Data platforms, business intelligence, analytics enablement, data governance"),
        ("☁️", "Cloud Transformation & Migration", 2, "Cloud strategy, lift-and-shift, cloud-native transformation, hybrid architectures"),
        ("🌩️", "Platform Services & Cloud-Native Development", 2, "Platform engineering, developer experience, internal platforms, service catalogs"),
        ("💡", "Product Management & Innovation Labs", 2, "Innovation programs, experimentation, lean startup methodology, product discovery"),
        ("🎨", "User-Centered Design & Experience", 2, "UX research, design thinking, customer journey mapping, experience design"),
    ]

    # Render cards in 3-column grid (clickable to navigate to Explore Stories)
    for i in range(0, len(cross_industry_categories), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(cross_industry_categories):
                icon, title, count, desc = cross_industry_categories[i + j]
                with cols[j]:
                    # Make card clickable by wrapping in container with button
                    st.markdown(f"""
                    <div class="capability-card" style="cursor: pointer;">
                        <div class="card-icon">{icon}</div>
                        <div class="card-title">{title}</div>
                        <div class="card-count">{count} projects</div>
                        <div class="card-desc">{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Invisible button for navigation
                    if st.button("", key=f"cross_industry_card_{i}_{j}", help=f"View {title} projects"):
                        st.session_state["active_tab"] = "Explore Stories"
                        st.rerun()

    # CTA section
    st.markdown("<br><br>", unsafe_allow_html=True)

    cta_html = """
    <div class="cta-section">
        <h2 class="cta-heading">Need a different way to explore?</h2>
        <p class="cta-subtext">Ask Agy 🐾 about Matt's cross-industry transformation experience — get conversational answers tailored to your needs</p>
    </div>
    <style>
    .cta-section {
        background: #f8f9fa;
        padding: 48px 32px;
        text-align: center;
        border-radius: 12px;
        border: 1px solid #e5e5e5;
        margin: 40px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .cta-heading {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #1a202c !important;
        margin-bottom: 16px !important;
    }
    .cta-subtext {
        font-size: 16px;
        color: #6b7280;
        margin-bottom: 0px;
        line-height: 1.6;
    }
    </style>
    """
    st.markdown(cta_html, unsafe_allow_html=True)

    # Center the button using columns
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Ask Agy 🐾", key="cross_industry_cta", use_container_width=True):
            st.session_state["active_tab"] = "Ask MattGPT"
            st.rerun()

    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)

    footer_html = """
    <div style="background: #334155; color: white; padding: 80px 40px; text-align: center; margin-top: 80px;">
        <h2 style="font-size: 32px; font-weight: 700; margin-bottom: 24px; color: white; line-height: 1.2;">Let's Connect</h2>
        <p style="font-size: 16px; margin-bottom: 16px; color: rgba(255, 255, 255, 0.95); line-height: 1.6; max-width: 850px; margin-left: auto; margin-right: auto;">
            Exploring Director/VP opportunities in <strong>Product Leadership</strong>, <strong>Platform Engineering</strong>, and <strong>Organizational Transformation</strong>
        </p>
        <p style="font-size: 14px; margin-bottom: 40px; color: rgba(255, 255, 255, 0.8); line-height: 1.5;">
            Available for immediate start • Remote or Atlanta-based • Open to consulting engagements
        </p>
        <div style="display: flex; gap: 18px; justify-content: center; flex-wrap: wrap; align-items: center;">
            <a href="mailto:mcpugmire@gmail.com" style="padding: 15px 32px; background: #8b5cf6; color: white; border-radius: 8px; font-size: 16px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; transition: all 0.2s ease;">
                📧 mcpugmire@gmail.com
            </a>
            <a href="https://www.linkedin.com/in/mattpugmire/" target="_blank" style="padding: 15px 32px; background: rgba(255,255,255,0.08); color: white; border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; font-size: 16px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; transition: all 0.2s ease;">
                💼 LinkedIn
            </a>
            <a href="#ask-mattgpt" style="padding: 15px 32px; background: rgba(255,255,255,0.08); color: white; border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; font-size: 16px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; transition: all 0.2s ease;">
                🐾 Ask Agy
            </a>
        </div>
    </div>
    <style>
    .landing-footer {
        background: #334155;
        color: white;
        padding: 72px 40px;
        text-align: center;
        margin-top: 80px;
        border-radius: 0;
        margin-left: -1rem;
        margin-right: -1rem;
    }
    .footer-heading {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: white !important;
        margin-bottom: 20px !important;
        margin-top: 0 !important;
        line-height: 1.2 !important;
    }
    .footer-subheading {
        font-size: 16px;
        color: rgba(255, 255, 255, 0.95);
        margin-bottom: 12px;
        line-height: 1.6;
        max-width: 850px;
        margin-left: auto;
        margin-right: auto;
    }
    .footer-subheading strong {
        font-weight: 700;
        color: white;
    }
    .footer-availability {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 40px;
        margin-top: 10px;
        line-height: 1.5;
    }
    .footer-buttons {
        display: flex;
        gap: 18px;
        justify-content: center;
        flex-wrap: wrap;
        align-items: center;
    }
    .footer-btn {
        padding: 15px 32px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        white-space: nowrap;
        color: white !important;
    }
    .footer-btn svg {
        fill: white !important;
        stroke: white !important;
    }
    .footer-btn-primary {
        background: #8b5cf6;
        color: white !important;
        border: none;
    }
    .footer-btn-primary:hover {
        background: #7c3aed;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(139, 92, 246, 0.4);
        color: white !important;
    }
    .footer-btn-secondary {
        background: rgba(255, 255, 255, 0.08);
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .footer-btn-secondary:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.25);
        transform: translateY(-2px);
        color: white !important;
    }
    @media (max-width: 768px) {
        .footer-buttons {
            flex-direction: column;
            align-items: stretch;
        }
        .footer-btn {
            width: 100%;
            max-width: 320px;
        }
    }
    </style>
    """
    st.markdown(footer_html, unsafe_allow_html=True)


def render_cross_industry_landing_page_OLD():
    """Render Cross-Industry Transformation landing page matching wireframe"""

    # Build industries pills HTML
    industries = [
        "Banking & Financial Services",
        "Healthcare & Life Sciences",
        "Manufacturing",
        "Retail & Consumer Goods",
        "Transportation & Logistics",
        "Telecommunications",
        "Public Sector",
        "Technology & Software",
    ]

    industries_html = ""
    for industry in industries:
        industries_html += f'<div class="client-pill">{industry}</div>\n'

    # Build category cards HTML
    cross_industry_categories = [
        ("⚡", "Agile Transformation & Delivery", 8, "Scaling agile practices, SAFe, Scrum at scale, delivery acceleration across industries"),
        ("🔧", "Modern Engineering Practices & Solutions", 8, "DevOps, CI/CD, test automation, engineering excellence, quality practices"),
        ("🤝", "Cross-Functional Collaboration & Team Enablement", 8, "Breaking down silos, team alignment, collaboration frameworks, culture change"),
        ("🎓", "Client Enablement & Sustainable Innovation", 7, "Knowledge transfer, capability building, innovation centers, sustainable practices"),
        ("🎯", "Technology Strategy & Advisory", 5, "Architecture roadmaps, strategic planning, technology vision, enterprise architecture"),
        ("📊", "Program Management & Governance", 4, "Large-scale delivery, governance frameworks, PMO setup, risk management"),
        ("🚢", "DevOps & Continuous Delivery", 3, "Deployment automation, pipeline engineering, continuous integration, release management"),
        ("📱", "Digital Product Development", 3, "Product thinking, user-centered design, rapid prototyping, product-market fit"),
        ("🚀", "Application Modernization", 3, "Legacy transformation, microservices migration, platform engineering"),
        ("🔄", "Business Process Optimization", 3, "Process reengineering, workflow automation, efficiency improvements, lean practices"),
        ("📈", "Data & Analytics Solutions", 3, "Data platforms, business intelligence, analytics enablement, data governance"),
        ("☁️", "Cloud Transformation & Migration", 2, "Cloud strategy, lift-and-shift, cloud-native transformation, hybrid architectures"),
        ("🌩️", "Platform Services & Cloud-Native Development", 2, "Platform engineering, developer experience, internal platforms, service catalogs"),
        ("💡", "Product Management & Innovation Labs", 2, "Innovation programs, experimentation, lean startup methodology, product discovery"),
        ("🎨", "User-Centered Design & Experience", 2, "UX research, design thinking, customer journey mapping, experience design"),
    ]

    cards_html = ""
    for icon, title, count, desc in cross_industry_categories:
        cards_html += f"""
        <div class="category-card">
            <span class="category-icon">{icon}</span>
            <h3 class="category-title">{title}</h3>
            <p class="category-count">{count} projects</p>
            <p class="category-desc">{desc}</p>
        </div>
        """

    # Render complete page as single HTML block
    page_html = f"""
    <style>
        .landing-page-header {{
            padding: 30px 0;
            border-bottom: 2px solid #e0e0e0;
            margin-bottom: 30px;
        }}
        .landing-page-header h1 {{
            font-size: 28px;
            color: #2c3e50;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        .landing-page-header p {{
            color: #7f8c8d;
            font-size: 14px;
        }}
        .ask-agy-link {{
            color: #667eea;
            font-weight: 600;
            text-decoration: underline;
            text-decoration-color: rgba(102, 126, 234, 0.3);
            text-underline-offset: 2px;
        }}
        .section-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 16px;
            color: #2c3e50;
        }}
        .section-subtitle {{
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 24px;
        }}
        .clients-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 40px;
        }}
        .client-pill {{
            background: white;
            border: 1px solid #d0d0d0;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            color: #555;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
        }}
        .client-pill:hover {{
            border-color: #667eea;
            color: #667eea;
            background: rgba(102, 126, 234, 0.05);
        }}
        .categories-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }}
        @media (max-width: 1200px) {{
            .categories-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        @media (max-width: 768px) {{
            .categories-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        .category-card {{
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 24px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .category-card:hover {{
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
            transform: translateY(-2px);
        }}
        .category-icon {{
            font-size: 28px;
            margin-bottom: 12px;
            display: block;
        }}
        .category-title {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 6px;
            color: #2c3e50;
        }}
        .category-count {{
            font-size: 14px;
            color: #667eea;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        .category-desc {{
            font-size: 13px;
            color: #7f8c8d;
            line-height: 1.5;
            margin: 0;
        }}
        .cta-box {{
            background: #f8f9fa;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 32px;
            text-align: center;
            margin-top: 30px;
            margin-bottom: 20px;
        }}
        .cta-box h3 {{
            font-size: 18px;
            color: #2c3e50;
            margin-bottom: 12px;
        }}
        .cta-box p {{
            font-size: 14px;
            color: #7f8c8d;
            line-height: 1.6;
            margin: 0;
        }}
    </style>

    <div class="landing-page-header">
        <h1>Cross-Industry Transformation</h1>
        <p>51 projects across 15+ transformation capabilities — or <span class="ask-agy-link">ask Agy 🐾</span> to find what you're looking for</p>
    </div>

    <h2 class="section-title">Industries Served</h2>
    <div class="clients-container">
        {industries_html}
    </div>

    <h2 class="section-title">Explore by Transformation Capability</h2>
    <p class="section-subtitle">Browse 51 cross-industry projects organized by transformation approach and methodology</p>

    <div class="categories-grid">
        {cards_html}
    </div>

    <div class="cta-box">
        <h3>Need a different way to explore?</h3>
        <p>Ask Agy 🐾 about Matt's cross-industry transformation experience — get conversational answers tailored to your needs</p>
    </div>
    """

    st.markdown(page_html, unsafe_allow_html=True)

    if st.button("Ask Agy 🐾", key="cross_industry_cta", use_container_width=False):
        st.session_state["active_tab"] = "Ask MattGPT"
        st.rerun()

    # Footer
    footer_html = """
    <div style="background: #2c3e50; color: white; padding: 48px 40px; text-align: center; margin-top: 60px; border-radius: 16px;">
        <h3 style="font-size: 28px; margin-bottom: 12px; color: white;">Let's Connect</h3>
        <p style="font-size: 16px; margin-bottom: 8px; opacity: 0.9;">
            Exploring Director/VP opportunities in <strong>Product Leadership</strong>, <strong>Platform Engineering</strong>, and <strong>Organizational Transformation</strong>
        </p>
        <p style="font-size: 14px; margin-bottom: 32px; opacity: 0.75;">
            Available for immediate start • Remote or Atlanta-based • Open to consulting engagements
        </p>
        <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;">
            <a href="mailto:mcpugmire@gmail.com" style="padding: 12px 28px; background: #8B5CF6; color: white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
                📧 mcpugmire@gmail.com
            </a>
            <a href="https://www.linkedin.com/in/matt-pugmire/" target="_blank" style="padding: 12px 28px; background: rgba(255,255,255,0.1); color: white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
                💼 LinkedIn
            </a>
            <a href="#ask" style="padding: 12px 28px; background: rgba(255,255,255,0.1); color: white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
                🐾 Ask Agy
            </a>
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)
