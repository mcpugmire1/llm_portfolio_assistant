"""
Global CSS Styles

Shared styles applied across all pages:
- CSS Variables (design system)
- Streamlit overrides (hide header/menu)
- Metrics styling
- Form controls
- AgGrid table styling
- Buttons and interactive elements
"""

import streamlit as st


def apply_global_styles():
    """
    Apply global CSS once per session.

    Returns early if already applied to avoid redundant style injection.
    """
    st.markdown(
        """
        <style>
        /* ========================================
           CSS VARIABLES - DESIGN SYSTEM
           ======================================== */
        :root {
            /* Brand */
            --accent-purple: #8B5CF6;
            --accent-purple-hover: #7C3AED;
            --accent-purple-bg: rgba(139, 92, 246, 0.08);
            --accent-purple-light: rgba(139, 92, 246, 0.2);
            --accent-purple-text: #8B5CF6;  /* Same as accent-purple for light mode */

            /* Backgrounds */
            --bg-card: #FFFFFF;
            --bg-surface: #F9FAFB;
            --bg-primary: #FFFFFF;
            --bg-hover: #F3F4F6;
            --bg-input: #FFFFFF;

            /* Text */
            --text-heading: #111827;
            --text-primary: #1F2937;
            --text-secondary: #6B7280;
            --text-muted: #9CA3AF;
            --text-color: #1F2937;

            /* Borders & Shadows */
            --border-color: #E5E7EB;
            --border-light: #F3F4F6;
            --card-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            --hover-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);

            /* Components */
            --pill-bg: #F3F4F6;
            --pill-text: #4B5563;
            --success-color: #10B981;
            --banner-info-bg: rgba(139, 92, 246, 0.05);

            /* Tables */
            --table-header-bg: #F9FAFB;
            --table-row-bg: #FFFFFF;
            --table-row-hover-bg: #F9FAFB;

            /* Chat/Status */
            --status-bar-bg: #F9FAFB;
            --status-bar-border: #E5E7EB;
            --chat-ai-bg: #F9FAFB;
            --chat-ai-border: #8B5CF6;
            --chat-user-bg: #FBFBFC;

            /* Gradients */
            --gradient-purple-hero: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

            /* Legacy colors (navbar, hero, stats) */
            --purple-gradient-start: #667eea;
            --dark-navy: #2c3e50;
            --dark-navy-hover: #34495e;
        }
        /* ========================================
        DARK MODE OVERRIDES
        ======================================== */
        body.dark-theme {
            /* Backgrounds */
            --bg-card: #1E1E2E;
            --bg-surface: #262633;
            --bg-primary: #0E1117;
            --bg-hover: #2D2D3D;
            --bg-input: #1E1E2E;

            /* Text */
            --text-heading: #F9FAFB;
            --text-primary: #E5E7EB;
            --text-secondary: #9CA3AF;
            --text-muted: #6B7280;
            --text-color: #E5E7EB;
            --accent-purple-text: #A78BFA;  /* Lighter purple for dark backgrounds */

            /* Borders & Shadows */
            --border-color: #374151;
            --border-light: #2D2D3D;
            --card-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
            --hover-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);

            /* Components */
            --pill-bg: #374151;
            --pill-text: #E5E7EB;
            --banner-info-bg: rgba(139, 92, 246, 0.15);

            /* Tables */
            --table-header-bg: #1E1E2E;
            --table-row-bg: #0E1117;
            --table-row-hover-bg: #262633;

            /* Chat/Status */
            --status-bar-bg: #1E1E2E;
            --status-bar-border: #374151;
            --chat-ai-bg: #1E1E2E;
            --chat-user-bg: #282435;
        }
        /* ========================================
           STREAMLIT OVERRIDES
           ======================================== */

        /* Keep header functional but force all backgrounds transparent */
        header[data-testid="stHeader"],
        header[data-testid="stHeader"] *,
        header[data-testid="stHeader"] > div,
        header[data-testid="stHeader"] div[data-testid="stHeaderActionElements"],
        div[data-testid="stToolbar"] {
            background: rgba(0,0,0,0) !important;
            background-color: rgba(0,0,0,0) !important;
            backdrop-filter: none !important;
        }

        /* Keep header visible (just transparent) */
        header[data-testid="stHeader"] {
            display: block !important;
            visibility: visible !important;
        }

        /* Hide the "Deploy" button but keep hamburger */
        header[data-testid="stHeader"] .stDeployButton,
        header[data-testid="stHeader"] button[kind="header"]:has(svg):not(:has([data-testid="baseButton-header"])) {
            display: none !important;
        }

        /* Keep #MainMenu visible for settings access */
        footer {
            visibility: hidden !important;
        }

        /* Hide status widgets but NOT the header */
        div[data-testid="stStatusWidget"]:not(header *) {
            display: none !important;
        }

        /* Hide decorations but NOT in header */
        .stApp [data-testid="stAppViewContainer"] > div[data-testid="stDecoration"]:not(header *) {
            display: none !important;
        }
        /* Hide Streamlit toasts and notifications */
        [data-testid="stNotification"],
        [data-testid="stToast"],
        div[data-baseweb="toast"],
        .st-emotion-cache-notification {
            display: none !important;
        }
        /* Hide ONLY Streamlit's default alert/info boxes, NOT our custom markdown */
        .stAlert:not(:has(img[class*="thinking-ball"])),
        [data-testid="stAlert"]:not(:has(img[class*="thinking-ball"])),
        div[data-baseweb="notification"]:not(:has(img[class*="thinking-ball"])),
        div[kind="info"]:not(:has(img[class*="thinking-ball"])) {
            display: none !important;
        }

        /* ========================================
           UNIVERSAL LAYOUT RESET
           ======================================== */


        /* Remove ALL default Streamlit top spacing */
        div[data-testid="stAppViewContainer"],
        .main,
        .main .block-container,
        .stMainBlockContainer,
        div[data-testid="stMainBlockContainer"],
        div.stMainBlockContainer.block-container,
        div[data-testid="stVerticalBlock"] {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }

        /* Remove spacing from first elements */
        .main > div:first-child {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }

        .stMainBlockContainer > div[data-testid="stVerticalBlock"]:first-child {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }


        /* Neutralize Streamlit containers wrapping custom headers */
        div[data-testid="stMarkdown"]:has(.ask-header),
        div[data-testid="element-container"]:has(.ask-header),
        div[data-testid="stMarkdown"]:has(.hero-section),
        div[data-testid="element-container"]:has(.hero-section),
        div[data-testid="stMarkdown"]:has(.conversation-header),
        div[data-testid="element-container"]:has(.conversation-header),
        div[data-testid="stMarkdown"]:has(.hero-gradient-wrapper),
        div[data-testid="element-container"]:has(.hero-gradient-wrapper) {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        /* Override Streamlit's default background for bordered containers */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
        }

        div[data-testid="element-container"]:has(div[data-testid="stVerticalBlockBorderWrapper"]) {
            background: transparent !important;
        }

        /* ========================================
           METRICS STYLING
           ======================================== */

        .stApp div[data-testid="metric-container"] {
            background: var(--bg-card) !important;
            padding: 28px 20px !important;
            border-radius: 12px !important;
            border: 1px solid var(--border-color) !important;
            text-align: center !important;
            box-shadow: var(--card-shadow) !important;
            transition: transform 0.3s ease !important;
        }

        .stApp div[data-testid="metric-container"]:hover {
            transform: translateY(-4px) !important;
        }

        .stApp div[data-testid="metric-container"] [data-testid="metric-value"] {
            color: var(--accent-purple) !important;
            font-size: 34px !important;
            font-weight: 700 !important;
            margin-bottom: 4px !important;
        }

        .stApp div[data-testid="metric-container"] [data-testid="metric-label"] {
            color: var(--text-secondary) !important;
            font-size: 14px !important;
            margin-top: 4px !important;
        }

        /* ========================================
           BUTTONS
           ======================================== */

        .stButton > button {
            background: var(--bg-card) !important;
            border: 2px solid var(--border-color) !important;
            color: var(--accent-purple) !important;
            padding: 14px 28px !important;
            border-radius: 8px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            margin-top: 10px !important;
            box-shadow: var(--card-shadow) !important;
        }

        .stButton > button:hover {
            background: var(--bg-hover) !important;
            color: var(--accent-purple) !important;
            transform: translateY(-2px) !important;
            box-shadow: var(--hover-shadow) !important;
        }

        /* ========================================
           FORM CONTROLS
           ======================================== */

        /* Fix selectbox width issues */
        section[data-testid="stAppViewContainer"] div[data-baseweb="select"] {
            max-width: none !important;
            min-width: 100% !important;
        }

        section[data-testid="stAppViewContainer"] div[data-baseweb="select"] > div {
            max-width: none !important;
            width: 100% !important;
        }

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

        section[data-testid="stAppViewContainer"] div[data-baseweb="popover"] {
            max-width: none !important;
            width: auto !important;
        }

        section[data-testid="stAppViewContainer"] ul[role="listbox"] {
            max-width: none !important;
            min-width: 350px !important;
            width: auto !important;
        }

        section[data-testid="stAppViewContainer"] li[role="option"] {
            white-space: nowrap !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }

        /* Bottom-align filter controls */
        [data-testid="column"] {
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
        }

        /* ========================================
           AGGRID TABLE STYLING
           ======================================== */

        .ag-theme-streamlit {
            background: var(--bg-card) !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: var(--card-shadow) !important;
            border: 1px solid var(--border-color) !important;
            margin-top: 8px !important;
            margin-bottom: 8px !important;
        }

        .ag-theme-streamlit .ag-header {
            background: var(--table-header-bg) !important;
            border-bottom: 2px solid var(--border-color) !important;
        }

        .ag-theme-streamlit .ag-header-cell {
            background: var(--table-header-bg) !important;
            border-right: none !important;
            padding: 16px 20px !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            color: var(--text-primary) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }

        .ag-theme-streamlit .ag-row {
            background: var(--table-row-bg) !important;
            border-bottom: 1px solid var(--border-color) !important;
            border-left: 3px solid transparent !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
            min-height: 70px !important;
        }

        .ag-theme-streamlit .ag-row:hover {
            background: var(--table-row-hover-bg) !important;
            border-left: 3px solid var(--accent-purple) !important;
        }

        .ag-theme-streamlit .ag-cell {
            padding: 24px 20px !important;
            font-size: 14px !important;
            line-height: 1.6 !important;
            border-right: none !important;
            color: var(--text-primary) !important;
        }

        /* Hide AgGrid pagination */
        .ag-theme-streamlit .ag-paging-panel {
            display: none !important;
        }

        /* ========================================
           RESPONSIVE - MOBILE OVERRIDES INLINED
           ======================================== */

        @media (max-width: 767px) {
            /* Global: Prevent horizontal scroll */
            html, body, [data-testid="stAppViewContainer"], .main {
                overflow-x: hidden !important;
                max-width: 100vw !important;
            }
            .main .block-container, .stMainBlockContainer, div[data-testid="stMainBlockContainer"] {
                padding-left: 16px !important;
                padding-right: 16px !important;
                max-width: 100% !important;
            }
            /* Columns stack - except nav */
            div[data-testid="stHorizontalBlock"]:not(:has([class*="st-key-topnav_"])) {
                flex-direction: column !important;
                gap: 0 !important;
            }
            div[data-testid="stHorizontalBlock"]:not(:has([class*="st-key-topnav_"])) > div[data-testid="stColumn"] {
                width: 100% !important;
                min-width: 100% !important;
                flex: 1 1 100% !important;
                margin: 0 0 16px 0 !important;
            }
            /* Card spacing */
            .card-mobile-spacing { margin-bottom: 16px !important; }
            div[data-testid="stElementContainer"]:has(div[style="height: 24px;"]) { display: none !important; }
            div[style="height: 24px;"] { display: none !important; height: 0 !important; }
            /* Purple cards auto height */
            div[style*="background: var(--gradient-purple-hero)"][style*="height: 380px"] {
                height: auto !important;
                min-height: 280px !important;
            }
            .capability-card { height: auto !important; min-height: 260px !important; }
            /* Header */
            .ask-header { flex-direction: column !important; text-align: center !important; padding: 20px 16px !important; gap: 12px !important; }
            .header-agy-avatar { width: 64px !important; height: 64px !important; }
            .header-text h1 { font-size: 22px !important; }
            /* Chat */
            .stChatMessage img, [data-testid="stChatMessage"] img { width: 40px !important; height: 40px !important; }
            [data-testid="stChatMessage"] { padding: 14px !important; gap: 12px !important; }
            /* Touch targets */
            button, a[role="button"] { min-height: 44px !important; }
            /* Stats bar - 2x2 grid on mobile */
            .stats-bar {
                grid-template-columns: repeat(2, 1fr) !important;
                gap: 0 !important;
            }
            .stat { padding: 16px 8px !important; }
            .stat-number { font-size: 28px !important; }
            .stat-label { font-size: 12px !important; }

            /* ========================================
               EXPLORE STORIES - Mobile Compact Layout
               ======================================== */

            /* Hero - Compact on mobile */
            .conversation-header {
                padding: 16px !important;
                margin: -1rem 0 0 0 !important;
            }
            .conversation-header-content {
                flex-direction: row !important;
                gap: 12px !important;
                align-items: center !important;
            }
            .conversation-agy-avatar {
                width: 56px !important;
                height: 56px !important;
                flex-shrink: 0 !important;
            }
            .conversation-header-text h1 {
                font-size: 1.25rem !important;
                line-height: 1.2 !important;
            }
            .conversation-header-text p {
                font-size: 0.85rem !important;
                margin-top: 4px !important;
            }

            /* Filters - Tighter layout */
            .explore-filters {
                padding: 16px !important;
            }

            /* Search row - input + button inline */
            .explore-filters [data-testid="stHorizontalBlock"]:first-of-type {
                flex-direction: row !important;
                gap: 8px !important;
            }
            .explore-filters [data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="stColumn"] {
                margin: 0 !important;
            }
            .explore-filters [data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="stColumn"]:first-child {
                flex: 1 1 auto !important;
                min-width: 0 !important;
                width: auto !important;
            }
            .explore-filters [data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="stColumn"]:last-child {
                flex: 0 0 auto !important;
                min-width: auto !important;
                width: auto !important;
            }

            /* Filter dropdowns - 2 column grid */
            .explore-filters .stSelectbox {
                margin-bottom: 8px !important;
            }

            /* Advanced filters / Reset - inline */
            .explore-filters [data-testid="stExpander"] {
                margin-top: 8px !important;
            }

            /* Reduce gap between filters and results */
            [data-testid="stVerticalBlock"] > div:has(.explore-filters) + div {
                margin-top: 0 !important;
            }

            /* Results header - Showing X of Y, page size selector */
            .main [data-testid="stHorizontalBlock"]:has(.stSelectbox[data-testid*="page"]) {
                flex-direction: row !important;
                align-items: center !important;
                gap: 8px !important;
            }

            /* Table/Cards toggle - compact */
            [data-testid="stSegmentedControl"] {
                margin: 8px 0 !important;
            }
            [data-testid="stSegmentedControl"] button {
                padding: 6px 12px !important;
                font-size: 12px !important;
            }

            /* Table - horizontal scroll wrapper */
            .main [data-testid="stDataFrame"],
            .main .ag-root-wrapper {
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch !important;
            }

            /* Story Detail Pane - Compact mobile */
            .story-detail-pane {
                padding: 16px !important;
            }
            .story-detail-pane h2 {
                font-size: 1.25rem !important;
                line-height: 1.3 !important;
            }

            /* Metrics in story detail - stack vertically */
            .story-detail-pane [data-testid="stHorizontalBlock"] {
                gap: 8px !important;
            }

            /* Action buttons in detail pane - full width */
            .story-detail-pane .stButton button {
                width: 100% !important;
                justify-content: center !important;
            }

            /* Hide spacer divs */
            div[data-testid="stVerticalBlock"] > div:empty,
            div[data-testid="stVerticalBlockBorderWrapper"] > div:empty {
                display: none !important;
            }
        }

        @media (min-width: 768px) and (max-width: 1023px) {
            /* Tablet: 2-col layout */
            div[data-testid="stHorizontalBlock"]:not(:has([class*="st-key-topnav_"])) { flex-wrap: wrap !important; }
            div[data-testid="stHorizontalBlock"]:not(:has([class*="st-key-topnav_"])) > div[data-testid="stColumn"] {
                flex: 0 0 48% !important;
                min-width: 48% !important;
            }
            .header-agy-avatar { width: 80px !important; height: 80px !important; }
            .stChatMessage img { width: 50px !important; height: 50px !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
