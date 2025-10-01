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
        /* Container */
        .matt-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        /* Hero with gradient */
        .matt-hero {
            text-align: center;
            padding: 60px 30px;
            background: var(--background-color);  
            color: var(--text-color);  /* Instead of white */
            border-radius: 16px;
            margin-bottom: 50px;
            position: relative;
            overflow: hidden;
        }

        .matt-hero::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: radial-gradient(circle at 30% 70%, rgba(74, 144, 226, 0.1) 0%, transparent 50%);
        }

        .matt-hero h1, .matt-hero p {
            position: relative;
            z-index: 1;
        }

        .matt-hero h1 {
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 24px;
            background: linear-gradient(135deg, #4a90e2, #6bb6ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .matt-hero p {
            font-size: 20px;
            color: #b0b0b0;
            max-width: 700px;
            margin: 0 auto;
            line-height: 1.6;
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
            color: #4a90e2 !important;
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
            border-color: #4a90e2;
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
        border-color: #4a90e2;
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
        .matt-card-btn .client-name { color:#5b9dd9; font-size:16px; font-weight:600; margin-bottom:8px; }
        .matt-card-btn .desc { color:#b0b0b0; margin-bottom:20px; line-height:1.5; }
        .matt-card-btn .examples { font-size:14px; color:#888; font-style:italic; }

        * Make buttons look intentional and polished */
        .stButton > button {
            background: rgba(74, 144, 226, 0.1) !important;
            border: 1.5px solid var(--border-color); !important;
            color: #4a90e2 !important;
            padding: 10px 24px !important;
            border-radius: 6px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
            width: 100% !important;
            margin-top: auto !important;
        }

        .stButton > button:hover {
            background: #4a90e2 !important;
            color: white !important;
            transform: translateY(-2px) !important;
        }

        .skill-bar {
            height: 6px;
            background: var(--border-color);  /* Use theme variable instead of hardcoded color */
            border-radius: 3px;
            margin-bottom: 16px;
            position: relative;
        }

        .skill-fill {
            height: 100%;
            background: #4a90e2;  /* Keep the blue accent color */
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
            border-left: 3px solid #4a90e2 !important;
        }

        .ag-theme-streamlit .ag-row-selected {
            background: #1e3a5f !important;
            border-left: 3px solid #4a90e2 !important;
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

        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# 2) Hero + stats (wireframe look)
# ---------------------------------------------------------
def render_home_hero_and_stats():
    css_once()

    st.markdown('<div class="matt-container">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="matt-hero">
            <h1>Hi, I'm MattGPT 👋</h1>
            <p>Technology & Innovation Leader • 20+ years modernizing platforms and launching cloud-native products at scale • Delivered $300M+ in revenue growth and accelerated product development 4x for Fortune 500 enterprises.</p>        
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Pure HTML stats that bypass Streamlit's CSS
    st.markdown(
        """
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin: 50px 0;">
            <div style="background: var(--secondary-background-color); padding: 32px 24px; border-radius: 12px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);">
                <span style="font-size: 36px; font-weight: 700; color: #4a90e2; display: block; margin-bottom: 8px;">$300M+</span>
                <span style="color: #999999; font-size: 16px;">Revenue Growth</span>
            </div>
            <div style="background: var(--secondary-background-color); padding: 32px 24px; border-radius: 12px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);">
                <span style="font-size: 36px; font-weight: 700; color: #4a90e2; display: block; margin-bottom: 8px;">150+</span>
                <span style="color: #999999; font-size: 16px;">Leaders & Engineers Led</span>
            </div>
            <div style="background: var(--secondary-background-color); padding: 32px 24px; border-radius: 12px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);">
                <span style="font-size: 36px; font-weight: 700; color: #4a90e2; display: block; margin-bottom: 8px;">12 Countries</span>
                <span style="color: #999999; font-size: 16px;">Global Rollout</span>
            </div>
            <div style="background: var(--secondary-background-color); padding: 32px 24px; border-radius: 12px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);">
                <span style="font-size: 36px; font-weight: 700; color: #4a90e2; display: block; margin-bottom: 8px;">4x</span>
                <span style="color: #999999; font-size: 16px;">Faster Product Development</span>
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
            "icon": "💳",
            "title": "Financial Services & Payments",
            "desc": ", payments modernization, compliance, core banking",
            "examples": '"How did you deliver the payments workstream within a $500M program?" • "How did you scale Salesforce across 12 countries?"',
            "tab": "Ask MattGPT"
        },
        {
            "icon": "🎯",
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
    
    # Add inline CSS for uniform heights
    st.markdown("""
    <style>
    .fixed-height-card {
        background: var(--secondary-background-color);
        color: var(--text-color); 
        padding: 32px; 
        border-radius: 12px; 
        height: 350px;
        display: flex;
        flex-direction: column;
        transition: all 0.3s ease;
        margin-bottom: 15px;
        border: 1px solid var(--border-color) !important; 
        box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2) !important;
    }
    .fixed-height-card:hover {
        transform: translateY(-4px);
        border-color: #4a90e2;
        box-shadow: 0 8px 24px rgba(74, 144, 226, 0.2);
    }
    .card-desc {
        color: #999999; 
        margin-bottom: 20px; 
        line-height: 1.5; 
        flex-grow: 1;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # First row of cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        card = starter_cards[0]
        st.markdown(f"""
        <div class="fixed-height-card">
            <div style="font-size: 40px; margin-bottom: 20px;">{card['icon']}</div>
            <h3 style="font-size: 22px; font-weight: 600; margin-bottom: 16px; color: var(--text-color);">{card['title']}</h3>
            <p class="card-desc">{card['desc']}</p>
            <p style="font-size: 14px; color: #888888; font-style: italic;">{card['examples']}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Explore Product Work", key="btn_0"):
            st.session_state["__inject_user_turn__"] = "Tell me about your product innovation approach"
            st.session_state["active_tab"] = card["tab"]
            st.session_state.pop("__ctx_locked__", None)
            st.session_state.pop("active_context", None)
            st.session_state["skip_home_menu"] = True
            st.rerun()

    
    with col2:
        card = starter_cards[1]
        st.markdown(f"""
        <div class="fixed-height-card">
            <div style="font-size: 40px; margin-bottom: 20px;">{card['icon']}</div>
            <h3 style="font-size: 22px; font-weight: 600; margin-bottom: 16px; color: var(--text-color);">{card['title']}</h3>
            <p class="card-desc">{card['desc']}</p>
            <p style="font-size: 14px; color: #888; font-style: italic;">{card['examples']}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Architecture Cases", key="btn_1"):
                st.session_state["__inject_user_turn__"] = "How do you modernize legacy applications?"
                st.session_state["active_tab"] = card["tab"]
                st.session_state.pop("__ctx_locked__", None)
                st.session_state.pop("active_context", None)
                st.session_state["skip_home_menu"] = True
                st.rerun()

    
    with col3:
        card = starter_cards[2]
        st.markdown(f"""
        <div class="fixed-height-card">
            <div style="font-size: 40px; margin-bottom: 20px;">{card['icon']}</div>
            <h3 style="font-size: 22px; font-weight: 600; margin-bottom: 16px; color: var(--text-color);">{card['title']}</h3>
            <p class="card-desc">{card['desc']}</p>
            <p style="font-size: 14px; color: #888; font-style: italic;">{card['examples']}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("See Payments Projects", key="btn_2"):
            st.session_state["__inject_user_turn__"] = "Tell me about your payments transformation work"
            st.session_state["active_tab"] = card["tab"]
            st.session_state.pop("__ctx_locked__", None)
            st.session_state.pop("active_context", None)
            st.session_state["skip_home_menu"] = True
            st.rerun()
    
    # Second row of cards
    col4, col5, col6 = st.columns(3)
    
    with col4:
        card = starter_cards[3]
        st.markdown(f"""
        <div class="fixed-height-card">
            <div style="font-size: 40px; margin-bottom: 20px;">{card['icon']}</div>
            <h3 style="font-size: 22px; font-weight: 600; margin-bottom: 16px; color: var(--text-color);">{card['title']}</h3>
            <p class="card-desc">{card['desc']}</p>
            <p style="font-size: 14px; color: #888; font-style: italic;">{card['examples']}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Browse Transformations", key="btn_3"):
            st.session_state["__inject_user_turn__"] = "How do you achieve faster delivery for Fortune 500 clients?"
            st.session_state["active_tab"] = card["tab"]
            st.session_state.pop("__ctx_locked__", None)
            st.session_state.pop("active_context", None)
            st.session_state["skip_home_menu"] = True
            st.rerun()

    
    with col5:
        card = starter_cards[4]
        st.markdown(f"""
        <div class="fixed-height-card">
            <div style="font-size: 40px; margin-bottom: 20px;">{card['icon']}</div>
            <h3 style="font-size: 22px; font-weight: 600; margin-bottom: 16px; color: var(--text-color)fffff;">{card['title']}</h3>
            <p class="card-desc">{card['desc']}</p>
            <p style="font-size: 14px; color: #888; font-style: italic;">{card['examples']}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Check Team Stories", key="btn_4"):
            st.session_state["__inject_user_turn__"] = "How did you scale and develop innovation teams?"
            st.session_state["active_tab"] = card["tab"]
            st.session_state.pop("__ctx_locked__", None)
            st.session_state.pop("active_context", None)
            st.session_state["skip_home_menu"] = True
            st.rerun()

    
    with col6:
        card = starter_cards[5]
        st.markdown(f"""
        <div class="fixed-height-card">
            <div style="font-size: 40px; margin-bottom: 20px;">{card['icon']}</div>
            <h3 style="font-size: 22px; font-weight: 600; margin-bottom: 16px; color: var(--text-color);">{card['title']}</h3>
            <p class="card-desc">{card['desc']}</p>
            <p style="font-size: 14px; color: #888; font-style: italic;">{card['examples']}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ask MattGPT", key="btn_5"):
            # This one just opens Ask MattGPT without a pre-loaded question
            st.session_state["active_tab"] = card["tab"]
            st.session_state["skip_home_menu"] = True
            st.rerun()

    
    st.markdown('</div>', unsafe_allow_html=True)