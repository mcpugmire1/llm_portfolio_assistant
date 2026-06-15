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
            --bg-warm: #f7f6f3;
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
            --banner-info-border: #8B5CF6;
            --banner-info-text: #6B21A8;
            --badge-bg: #FFFFFF;

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
            --banner-info-border: #A78BFA;
            --banner-info-text: #C4B5FD;
            --badge-bg: #FFFFFF;

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

        /* Collapse zero-contribution Streamlit wrapper elements so they don't
           generate phantom gap spacing in the parent stVerticalBlock (gap: 16px).
           Covers: style-only markdown injections (MATTGPT-107, promoted global)
           and zero-height iframe injections (components.html height=0).
           Excludes st-key-screen_size_capture — streamlit_js_eval iframe that
           captures viewport width for the Role Match mobile gate. The clean key
           (no double underscores) generates a valid CSS class that :not() can
           target. window.innerWidth in that iframe returns correct viewport width
           since the iframe is not hidden. */
        div[data-testid="stElementContainer"]:has(> div[data-testid="stMarkdown"] > div[data-testid="stMarkdownContainer"] > style:only-child),
        div[data-testid="stElementContainer"]:has(> div[data-testid="stMarkdown"] > div[data-testid="stMarkdownContainer"] > script:only-child),
        div[data-testid="stElementContainer"]:has(> [data-testid="stIFrame"]):not([class*="st-key-screen_size_capture"]) {
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
            min-height: 70px !important;
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

        @media (max-width: 768px) {
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
            /* Columns stack - except nav, results row, and landing input row */
            div[data-testid="stHorizontalBlock"]:not(:has([class*="st-key-topnav_"])):not(:has([data-testid="stButtonGroup"])):not(:has(.st-key-landing_input)):not(:has([data-testid="stFormSubmitButton"])):not(:has([class*="st-key-r2_client_v2"])) {
                flex-direction: column !important;
                gap: 0 !important;
            }
            /* Search form: keep input+button inline.
               flex-wrap: nowrap overrides Streamlit's base wrap rule. */
            [data-testid="stForm"] [data-testid="stHorizontalBlock"] {
                flex-direction: row !important;
                flex-wrap: nowrap !important;
            }
            [data-testid="stForm"] [data-testid="stColumn"]:last-child {
                flex: 0 0 auto !important;
                min-width: 0 !important;
                max-width: none !important;
            }
            div[data-testid="stHorizontalBlock"]:not(:has([class*="st-key-topnav_"])):not(:has([data-testid="stButtonGroup"])):not(:has(.st-key-landing_input)):not(:has([data-testid="stFormSubmitButton"])):not(:has([class*="st-key-r2_client_v2"])) > div[data-testid="stColumn"] {
                width: 100% !important;
                min-width: 100% !important;
                flex: 1 1 100% !important;
                margin: 0 0 16px 0 !important;
            }
            /* Landing input row - keep horizontal on mobile */
            div[data-testid="stHorizontalBlock"]:has(.st-key-landing_input) {
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                gap: 8px !important;
                align-items: center !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.st-key-landing_input) > div[data-testid="stColumn"]:first-child {
                flex: 1 1 auto !important;
                min-width: 0 !important;
                width: auto !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.st-key-landing_input) > div[data-testid="stColumn"]:last-child {
                flex: 0 0 auto !important;
                min-width: 0 !important;
                width: auto !important;
            }
            /* Make input fill its column */
            div[data-testid="stHorizontalBlock"]:has(.st-key-landing_input) .stTextInput,
            div[data-testid="stHorizontalBlock"]:has(.st-key-landing_input) [data-testid="stTextInput"],
            div[data-testid="stHorizontalBlock"]:has(.st-key-landing_input) [data-baseweb="input"] {
                width: 100% !important;
            }
            /* Compact button - shorter padding, smaller text */
            div[data-testid="stHorizontalBlock"]:has(.st-key-landing_input) .st-key-landing_ask button {
                padding: 8px 12px !important;
                white-space: nowrap !important;
                font-size: 13px !important;
            }
            div[data-testid="stHorizontalBlock"]:has(.st-key-landing_input) .st-key-landing_ask button p {
                font-size: 13px !important;
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
               EXPLORE STORIES/MY WORK - Mobile Compact Layout
               ======================================== */

            /* Hero - Compact on mobile */
            .conversation-header {
                padding: 16px !important;
                margin: 60px 0 0 0 !important;
            }
            .conversation-header-content {
                flex-direction: row !important;
                gap: 12px !important;
                align-items: center !important;
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
            .stChatMessage img { width: 50px !important; height: 50px !important; }
        }

        /* ========================================
           WHY AGY BADGE — MATTGPT-101
           ======================================== */
        .why-agy-badge,
        .why-agy-badge--header {
            position: absolute;
            bottom: 4px;
            right: 4px;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            background: var(--dark-navy);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-style: italic;
            font-family: Georgia, serif;
            font-weight: 700;
            font-size: 11px;
            color: var(--badge-bg);
            transition: transform 0.15s ease;
            z-index: 10;
            user-select: none;
            line-height: 1;
        }
        /* Body avatars sit on white/light card — gray border separates from background */
        .why-agy-badge {
            border: 2px solid var(--border-color);
        }
        /* Header avatars sit on purple gradient — white border lifts off the gradient */
        .why-agy-badge--header {
            border: 2px solid var(--badge-bg);
        }
        .why-agy-badge:hover,
        .why-agy-badge--header:hover {
            transform: scale(1.15);
        }
        /* Hero badge — on the illustration wrapper (280px img), not the full section.
           40px from bottom places it near Agy's head area in the lower-right. */
        .hero-illustration-wrapper .why-agy-badge {
            bottom: 40px;
            right: 10px;
        }
        @media (max-width: 768px) {
            .hero-illustration-wrapper .why-agy-badge {
                bottom: 20px;
                right: 5px;
            }
        }
        /* Mobile: avatars scale to 60-64px; -2px/-2px lands badge center at circle edge */
        @media (max-width: 768px) {
            .why-agy-badge,
            .why-agy-badge--header {
                right: -2px;
                bottom: -2px;
            }
        }

        /* ========================================
           HOW I BUILT DIALOG — Per-query runtime pipeline (MATTGPT-102)
           Spine + numbered step pattern, consistent with timeline visual language.
           ======================================== */
        .hib-runtime-wrapper { position: relative; display: flex; flex-direction: column; gap: 0; }
        .hib-runtime-wrapper::before { content: ''; position: absolute; left: 15px; top: 24px; bottom: 24px; width: 2px; background: var(--border-color); z-index: 0; }
        .hib-runtime-step { display: flex; gap: 16px; align-items: flex-start; padding-bottom: 10px; position: relative; z-index: 1; }
        .hib-runtime-num { width: 32px; height: 32px; border-radius: 50%; background: var(--accent-purple); color: white; font-size: 13px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 0 0 3px var(--bg-card), 0 0 0 5px var(--accent-purple-light); }
        .hib-runtime-card { flex: 1; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 12px 16px; }
        .hib-runtime-card h4 { font-size: 13px; font-weight: 600; color: var(--text-primary); margin: 0 0 8px; }
        .hib-runtime-card ul { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 4px; }
        .hib-runtime-card li { font-size: 12px; color: var(--text-secondary); line-height: 1.5; padding-left: 12px; position: relative; }
        .hib-runtime-card li::before { content: "·"; position: absolute; left: 0; color: var(--accent-purple); font-weight: 700; }
        @media (max-width: 768px) {
            .hib-runtime-num { width: 28px; height: 28px; font-size: 12px; }
            .hib-runtime-wrapper::before { left: 13px; }
            .hib-runtime-card { padding: 10px 12px; }
            .hib-runtime-card h4 { font-size: 12px; }
            .hib-runtime-card li { font-size: 11px; }
        }

        /* ========================================
           HOW I BUILT DIALOG — Go-deeper + CTA (MATTGPT-102)
           ======================================== */
        .hib-block { border: 0.5px solid var(--border-color); border-radius: 10px; padding: 14px 16px; margin-top: 16px; margin-left: 0; margin-right: 0; }
        .hib-godeeper-lead { font-size: 12px; color: var(--text-secondary); margin: 4px 0 10px; }
        .hib-godeeper-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .hib-godeeper-card { border: 0.5px solid var(--border-color); border-radius: 10px; padding: 14px 16px; }
        .hib-godeeper-top { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
        .hib-godeeper-top svg { color: var(--text-primary); flex-shrink: 0; }
        .hib-godeeper-ttl { font-size: 13px; font-weight: 500; color: var(--text-primary); }
        .hib-godeeper-desc { font-size: 13px; color: var(--text-secondary); line-height: 1.5; margin: 0 0 8px; }
        .hib-godeeper-link { font-size: 11px; color: var(--accent-purple); font-weight: 500; display: inline-flex; align-items: center; gap: 4px; text-decoration: none; }
        .hib-godeeper-link:hover { text-decoration: underline; }
        .hib-cta-block { padding: 0; border-radius: 0; margin-top: 8px; }
        .hib-cta-block .hib-cta-sub { font-size: 14px; color: var(--text-secondary); margin: 0 0 10px; line-height: 1.5; }
        .hib-cta-block .hib-cta-h { font-size: 13px; font-weight: 500; color: var(--text-secondary); margin: 0 0 8px; letter-spacing: 0.03em; text-transform: uppercase; }

        .hib-cta-prompts { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .hib-cta-prompt { background: var(--accent-purple-bg, rgba(109, 76, 196, 0.04)); border: 1px solid rgba(120, 80, 220, 0.3); border-radius: 8px; padding: 9px 12px; font-size: 13px; color: var(--accent-purple); display: flex; align-items: center; justify-content: space-between; cursor: pointer; transition: background 0.15s ease, border-color 0.15s ease; user-select: none; }
        .hib-cta-prompt:hover {
            background: rgba(139, 92, 246, 0.15);   /* was rgba(109,76,196,0.12) — wrong purple, wrong direction */
            border-color: var(--accent-purple);
            }


        /* My Profile sample-question chip buttons (MATTGPT-068).
           Lives in global styles (not inside render_about_matt) so the CSS is
           re-injected on every Streamlit script rerun and persists across the
           page transition to Ask Agy — keeping the chips correctly styled
           during the stale-frame dim while the new page renders. Moving the
           rules to render_about_matt scope caused a visible de-style flash
           during chip-click → AI thinking transitions. */
        [class*='st-key-about_matt_sample_q_'] button {
            width: 100%;
            text-align: left;
            background: var(--bg-card, #ffffff);
            border: 2px solid var(--banner-info-border) !important;
            color: var(--banner-info-text) !important;
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 500;
            line-height: 1.5;
            cursor: pointer;
            transition: background 0.15s ease, border-color 0.15s ease;
            margin-bottom: 8px;
            justify-content: flex-start !important;
        }
        [class*='st-key-about_matt_sample_q_'] button p,
        [class*='st-key-about_matt_sample_q_'] button div {
            color: var(--banner-info-text) !important;
        }
        [class*='st-key-about_matt_sample_q_'] button p {
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            gap: 4px !important;
        }
        [class*='st-key-about_matt_sample_q_'] button p::after {
            content: '→';
            color: var(--banner-info-text);
            opacity: 0.7;
        }
        [class*='st-key-about_matt_sample_q_'] button:hover {
            background: var(--accent-purple-bg);
        }

        /* How I Built dialog — hidden bridge buttons (MATTGPT-102). Chips are HTML spans; st.button elements are hidden triggers only. */
        [class*='st-key-hib_prompt_'] { display: none !important; }

        /* My Profile — hidden download-PDF bridge button (MATTGPT-118). */
        [class*='st-key-am_download_pdf'] { display: none !important; }

        /* ============================================================
           ABOUT MATT/MY PROFILE PAGE CSS — relocated from render_about_matt()
           inline <style> so it persists through Streamlit reruns
           (MATTGPT-068). Page-scoped classes; collision-prone ones
           namespaced .am-*.
           ============================================================ */
/* ============================================================================
   ABOUT MATT/MY PROFILE PAGE STYLES - Dark Mode Compatible
   ============================================================================ */

/* Header - matches other pages */
.about-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 32px;
    min-height: 184px;
    box-sizing: border-box;
    margin-top: -32px !important;
    margin-bottom: 0 !important;
    color: white;
    position: relative;
}

.about-header-content {
    display: flex;
    align-items: center;
    gap: 24px;
    max-width: 1200px;
    margin: 0;
}

.about-header-avatar {
    flex-shrink: 0 !important;
    width: 120px !important;
    height: 120px !important;
    border-radius: 50% !important;
    border: 4px solid white !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    object-fit: cover !important;
    background: rgba(255, 255, 255, 0.1) !important;
}

.about-header-text h1 {
    font-size: 32px;
    font-weight: 700;
    margin: 0 0 8px 0;
    color: white;
}

.about-header-text p {
    font-size: 16px;
    margin: 0;
    opacity: 0.95;
    color: white;
}

/* Stats bar */
.am-stats-bar {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    border-bottom: 2px solid var(--border-color);
    margin: 164x 0 30px;
}

@media (max-width: 768px) {
    .am-stats-bar { padding: 8px 0; }
}

.am-stat-card {
    padding: 8px 4px;
    text-align: center;
    border-right: 1px solid var(--border-color);
}

.am-stat-card:last-child {
    border-right: none;
}

.am-stat-number {
    font-size: 36px;
    font-weight: 700;
    color: var(--accent-purple, #8B5CF6);
    display: block;
    margin-bottom: 8px;
}

.am-stat-label {
    color: var(--text-muted, #999999);
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: block;
}

/* Signals panel — MATTGPT-093 (replaces stats bar) */
.am-signals-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 16px 0 24px;
}

.am-signal-tile {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 12px 16px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.am-signal-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-secondary);
}

.am-signal-value {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
}

@media (max-width: 768px) {
    .am-signals-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* Referrer snippet block — MATTGPT-093 */
.am-referrer-snippet {
    background: var(--bg-surface);
    border-left: 3px solid var(--accent-purple);
    border-radius: 0 6px 6px 0;
    padding: 14px 18px;
    margin: 12px 0 16px;
    font-size: 14px;
    line-height: 1.6;
    color: var(--text-primary);
}


/* Section titles */
.am-section-title {
    font-size: 32px;
    font-weight: 600;
    text-align: center;
    margin: 60px 0 12px 0;
    color: var(--text-heading, #2c3e50);
}

/* Back-link affordance for secondary surfaces (MATTGPT-102 + future
   no-top-nav secondary surfaces — How I Built, etc.). Subtle text-style
   anchor matching the existing "← Banking" breadcrumb pattern on My Work;
   not a CTA button. Routes through app.py's ?nav=<slug> handler. */
.back-link {
    display: inline-block;
    font-size: 13px;
    font-weight: 500;
    color: rgb(107, 33, 168);
    text-decoration: none;
    background: transparent;
    border: none;
    padding: 0;
    margin: 0 0 16px 0;
}
.back-link:hover {
    text-decoration: underline;
}

.am-section-subtitle {
    font-size: 16px;
    color: var(--text-muted, #7f8c8d);
    text-align: center;
    margin-bottom: 40px;
}

/* Career timeline */
.timeline {
    max-width: 900px;
    margin: 0 auto;
    position: relative;
    padding-left: 40px;
}

.timeline::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: linear-gradient(to bottom, #8B5CF6, #7C3AED);
}

.timeline-item {
    position: relative;
    margin-bottom: 30px;
    padding-left: 30px;
}

.timeline-item::before {
    content: '';
    position: absolute;
    left: -50px;
    top: 4px;
    width: 20px;
    height: 20px;
    background: var(--bg-primary, white);
    border: 4px solid var(--accent-purple, #8B5CF6);
    border-radius: 50%;
}

.timeline-year {
    font-size: 14px;
    font-weight: 700;
    color: var(--accent-purple, #8B5CF6);
    margin-bottom: 8px;
}

.timeline-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-heading, #2c3e50);
    margin-bottom: 6px;
}

.timeline-company {
    font-size: 14px;
    color: var(--text-muted, #7f8c8d);
    margin-bottom: 8px;
}

.timeline-desc {
    font-size: 14px;
    color: var(--text-secondary, #888);
    line-height: 1.6;
}

/* Deep-dive section */
.deep-dive-section {
    background: var(--bg-surface, #f8f9fa);
    padding: 50px 20px;
    margin: 40px -1rem 0 -1rem;
}

.deep-dive-card {
    background: var(--bg-card, white);
    border: 2px solid var(--border-color, #e0e0e0);
    border-left: 4px solid var(--accent-purple, #8B5CF6);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 12px;
    margin-left: 0;
    margin-right: 0;
}

.deep-dive-card h3 {
    color: var(--text-heading, #2c3e50);
}

.deep-dive-card p {
    color: var(--text-secondary, #888);
}

.tech-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-top: 8px;
}

@media (max-width: 768px) {
    .tech-grid { grid-template-columns: repeat(2, 1fr); }
}

.tech-item {
    background: var(--bg-surface, #f8f9fa);
    border: 2px solid var(--border-color, #e0e0e0);
    border-radius: 8px;
    padding: 8px 12px;
    text-align: center;
    color: var(--text-primary, #333);
    transition: all 0.2s ease;
}

.tech-item:hover {
    border-color: var(--accent-purple, #8B5CF6);
}

.flow-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin: 8px 0;
    align-items: center;
}

@media (max-width: 768px) {
    .flow-grid { grid-template-columns: repeat(2, 1fr); }
}

.flow-step {
    background: var(--bg-surface, #f8f9fa);
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 8px;
    padding: 10px 12px;
    text-align: center;
    position: relative;
    color: var(--text-primary, #333);
}

.flow-step:not(:last-child)::after {
    content: '→';
    position: absolute;
    right: -24px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 18px;
    color: var(--accent-purple, #8B5CF6);
    font-weight: bold;
}

.flow-num {
    width: 18px;
    height: 18px;
    background: var(--accent-purple-bg);
    color: var(--accent-purple-text);
    border-radius: 50%;
    font-size: 10px;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 10px;
}

.flow-step-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-heading, #333);
}

.flow-step-desc {
    font-size: 11px;
    color: var(--text-muted, #7f8c8d);
}

/* Code block - works in both modes */
.code-block {
    background: #1e1e2e;
    color: #cdd6f4;
    border-radius: 8px;
    padding: 20px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 12px;
    line-height: 1.6;
    overflow-x: auto;
    white-space: pre-wrap;
    margin-top: 12px;
}

.code-comment {
    color: #6c7086;
}

.code-keyword {
    color: #cba6f7;
}

.code-string {
    color: #a6e3a1;
}

.code-function {
    color: #89b4fa;
}

.details-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    margin: 0;
}

@media (max-width: 768px) {
    .details-grid { grid-template-columns: repeat(2, 1fr); }
}

.detail-card {
    background: var(--bg-card, white);
    border: 2px solid var(--border-color, #e0e0e0);
    border-radius: 12px;
    padding: 12px;
    transition: all 0.2s ease;
}

.detail-card:hover {
    border-color: var(--accent-purple, #8B5CF6);
}

.detail-card h4 {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-heading, #2c3e50);
    margin: 0 0 6px 0;
}

.detail-card ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.detail-card li {
    font-size: 13px;
    color: var(--text-secondary, #888);
    line-height: 1.6;
    padding: 3px 0;
    border-bottom: 1px solid var(--border-light, #f0f0f0);
}

.detail-card li:last-child {
    border-bottom: none;
}

.detail-card li strong {
    color: var(--text-primary, #333);
}

/* See It In Action CTA card — styles applied to the st.container key
   (about_matt_cta_card) so the four sample-question buttons render
   DOM-nested inside the card per the May 27, 2026 wireframe amendment. */
[class*='st-key-about_matt_cta_card'] {
    max-width: 900px;
    margin: 32px auto 0;
    background: var(--bg-card, white);
    border-left: 4px solid var(--accent-purple, #8B5CF6);
    border-radius: 12px;
    padding: 40px;
    box-shadow: var(--card-shadow, 0 4px 12px rgba(0, 0, 0, 0.08));
}

[class*='st-key-about_matt_cta_card'] h3 {
    color: var(--text-heading, #333);
}

[class*='st-key-about_matt_cta_card'] p {
    color: var(--text-secondary, #888);
}

[class*='st-key-about_matt_cta_card'] strong {
    color: var(--text-primary, #333);
}

/* Competencies grid */
.competencies-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    max-width: 1000px;
    margin: 0 auto;
    padding: 0 1rem;
}

@media (max-width: 900px) {
    .competencies-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 600px) {
    .competencies-grid { grid-template-columns: 1fr; }
}

.competency-card {
    background: var(--bg-card, #fafafa);
    border: 2px solid var(--border-color, #e0e0e0);
    border-radius: 12px;
    padding: 24px;
    transition: all 0.2s ease;
}

.competency-card:hover {
    border-color: var(--accent-purple, #8B5CF6);
    transform: translateY(-2px);
}

.competency-card h4 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-heading, #2c3e50);
    margin: 12px 0 16px 0;
}

.competency-card ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.competency-card li {
    font-size: 13px;
    color: var(--text-secondary, #888);
    padding: 6px 0;
}

.competency-card-accent {
    width: 32px;
    height: 3px;
    background: var(--accent-purple, #8B5CF6);
    border-radius: 2px;
    margin-bottom: 12px;
}

/* Philosophy grid - gradient cards work in both modes */
.philosophy-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
    max-width: 900px;
    margin: 0 auto;
    padding: 0 1rem;
}

@media (max-width: 768px) {
    .philosophy-grid { grid-template-columns: 1fr; }
}

.philosophy-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 12px;
    padding: 32px;
    transition: all 0.2s ease;
}

.philosophy-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.philosophy-card h3 {
    font-size: 20px;
    margin: 0 0 16px 0;
    color: white;
}

.philosophy-card p {
    font-size: 15px;
    line-height: 1.7;
    opacity: 0.95;
    margin: 0;
    color: white;
}

/* =============================================================================
 * My Profile — prof-* visual language (MATTGPT-093)
 * New classes scoped to about_matt.py. Existing am-* classes (used by
 * other pages) are left untouched.
 * Where BDD tests reference am-* class names, about_matt.py dual-classes
 * elements — BDD locators find the am-* class, and prof-* CSS wins the
 * cascade because it is defined after the am-* block in this file.
 * ============================================================================= */

/* Reset browser user-agent margin-block on all prof-* paragraph elements.
   Without this, UA stylesheet margin-block-start/end: 1em inflates spacing
   inside signal tiles, voice block, copy block, cards, and timeline rows. */
.prof-signal-lbl, .prof-signal-val,
.prof-voice-p,
.prof-copy-h, .prof-copy-snippet,
.prof-comp-name, .prof-comp-desc,
.prof-phil-h, .prof-phil-p,
.prof-timeline-period, .prof-timeline-role, .prof-timeline-org, .prof-timeline-desc {
    margin-block-start: 0 !important;
    margin-block-end: 0 !important;
}

/* Status badge — "● In active conversations" green pill above name */
.prof-status-badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 500;
    color: #2e7d32;
    background: #e7f4e8;
    border-radius: 12px;
    padding: 3px 9px;
    position: absolute;
    top: 50%;
    right: 32px;
    transform: translateY(-50%);
}

/* !important needed because dual-classed p elements also carry
   .am-section-title (32px centered) — prof-section-h must win */
.prof-section-h {
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    color: var(--text-secondary) !important;
    margin: 0 0 8px !important;
    text-align: left !important;
}

/* Signals: wireframe spec — 3-col grid, no border, bg-surface tiles */
.prof-signals-grid {
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 10px !important;
    margin: 0 !important;
}

/* Scoped selector beats .am-signal-tile without !important wars */
[class*='st-key-am_signals_panel'] .am-signal-tile {
    background: var(--bg-surface) !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 10px 12px !important;
    gap: 3px !important;
}

div[data-testid="stMarkdown"]:has(.prof-section-h),
div[data-testid="stMarkdownContainer"]:has(.prof-section-h) {
    margin-top: 22px !important;
    margin-bottom: 0 !important;
    padding: 0 !important;
}

[class*='st-key-am_signals_panel'] > div {
    padding: 0 !important;
}

/* Root cause B fix — the keyed container div IS the flex parent (gap: 16px lives here,
   not on a child stVerticalBlock). Target the containers directly. */
[class*='st-key-am_signals_panel'],
[class*='st-key-am_in_my_own_words'],
[class*='st-key-am_for_a_referrer'],
[class*='st-key-am_competencies'],
[class*='st-key-am_how_i_lead'],
[class*='st-key-am_career_evolution'] {
    gap: 4px !important;
}

[class*='st-key-am_signals_panel'] [data-testid="stMarkdownContainer"],
[class*='st-key-am_in_my_own_words'] [data-testid="stMarkdownContainer"],
[class*='st-key-am_for_a_referrer'] [data-testid="stMarkdownContainer"],
[class*='st-key-am_competencies'] [data-testid="stMarkdownContainer"],
[class*='st-key-am_how_i_lead'] [data-testid="stMarkdownContainer"],
[class*='st-key-am_career_evolution'] [data-testid="stMarkdownContainer"] {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}

.prof-signal-lbl {
    font-size: 10px !important;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin: 0 0 2px !important;
}

.prof-signal-val {
    font-size: 12px !important;
    font-weight: 500;
    margin: 0;
    color: var(--text-primary);
}

/* Voice block — wireframe: .prof-voice-p per paragraph */
.prof-voice-p {
    font-size: 13px !important;
    line-height: 1.65 !important;
    color: var(--text-primary) !important;
    margin: 0 0 10px !important;
}

.prof-voice-p:last-child {
    margin: 0;
}

/* Referrer copy block: info-bg outer container + white inner snippet */
.prof-copy-block {
    background: var(--accent-purple-bg);
    border-left: 2px solid var(--accent-purple);
    border-radius: 0 6px 6px 0;
    padding: 14px 16px;
    margin: 10px 0 14px;
}

.prof-copy-h {
    font-size: 12px !important;
    font-weight: 500 !important;
    color: var(--accent-purple) !important;
    margin: 0 0 6px 0 !important;
}

/* Inner snippet (dual-classed with am-referrer-snippet for BDD compat) */
.prof-copy-snippet {
    background: var(--bg-card) !important;
    border-left: none !important;
    border-radius: 6px !important;
    padding: 9px 11px !important;
    margin: 6px 0 !important;
    font-size: 12px !important;
    font-style: italic !important;
    line-height: 1.5 !important;
    color: var(--text-secondary) !important;
}

/* Flex row for Copy snippet + Download PDF buttons */
.prof-copy-actions {
    display: flex;
    gap: 6px;
    margin-top: 8px;
    flex-wrap: wrap;
    align-items: center;
}

.prof-act-btn {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    font-weight: 500;
    padding: 5px 10px;
    border: 0.5px solid var(--border-color) !important;
    border-radius: 6px;
    background: var(--bg-card);
    color: var(--text-secondary);
    cursor: default;
    line-height: 1.4;
    white-space: nowrap;
}

/* Competency grid: override max-width/margin/padding/gap */
.prof-comp-grid {
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important;
    max-width: none !important;
    margin: 0 !important;
    padding: 0 !important;
    gap: 8px !important;
}

/* Compound selector (0-2-0) beats .competency-card (0-1-0) on all properties */
.competency-card.prof-comp-card {
    background: var(--bg-surface) !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 11px 12px !important;
    transition: background 0.15s ease;
}

.competency-card.prof-comp-card:hover {
    border-color: transparent !important;
    transform: none !important;
    background: var(--bg-hover) !important;
}

/* Beats .competency-card h4 (0-1-1) with compound selector (0-2-1).
   padding: 0 overrides Streamlit's h4 { padding: 8px 0 16px } default */
.competency-card.prof-comp-card h4,
.competency-card.prof-comp-card .prof-comp-name {
    font-size: 12px !important;
    font-weight: 500 !important;
    color: var(--text-primary) !important;
    margin: 0 0 3px !important;
    padding: 0 !important;
}

.competency-card.prof-comp-card p,
.competency-card.prof-comp-card .prof-comp-desc {
    font-size: 11px !important;
    color: var(--text-secondary) !important;
    line-height: 1.4 !important;
    margin: 0 !important;
}

/* How I Lead — wireframe grid class: .prof-philosophy */
.prof-philosophy {
    display: grid !important;
    grid-template-columns: repeat(2, 1fr) !important;
    gap: 8px !important;
    margin: 0 !important;
    padding: 0 !important;
    max-width: none !important;
}

.prof-phil-card {
    background: var(--bg-surface) !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 11px 13px !important;
}

.prof-phil-h {
    font-size: 12px !important;
    font-weight: 500 !important;
    color: var(--accent-purple) !important;
    margin: 0 0 3px !important;
}

.prof-phil-p {
    font-size: 11px !important;
    line-height: 1.45 !important;
    color: var(--text-primary) !important;
    margin: 0 !important;
}

/* Compound selectors (0-2-0 / 0-2-1) beat Streamlit's internal
   [data-testid="stMarkdownContainer"] p (0-1-1) rule for font-size */
.prof-phil-card .prof-phil-h {
    font-size: 12px !important;
    font-weight: 500 !important;
    color: var(--accent-purple) !important;
    margin: 0 0 3px !important;
}

.prof-phil-card .prof-phil-p {
    font-size: 11px !important;
    line-height: 1.45 !important;
    color: var(--text-primary) !important;
    margin: 0 !important;
}

/* For a referrer: style the Streamlit container as the info-box so
   st.button() elements land visually inside the styled region */
[class*='st-key-am_for_a_referrer'] {
    background: var(--accent-purple-bg);
    border-left: 2px solid var(--accent-purple);
    border-radius: 0 8px 8px 0;
    padding: 14px 16px;
    margin: 10px 0 14px;
}

/* Referrer columns shrink to button content width — removes the large gap
   between Copy snippet and Download PDF that the 1:1:2 column ratio creates */
[class*='st-key-am_for_a_referrer'] [data-testid="stHorizontalBlock"] {
    gap: 8px !important;
    flex-wrap: wrap !important;
}

[class*='st-key-am_for_a_referrer'] [data-testid="column"] {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 0 !important;
    padding: 0 !important;
}

/* Action buttons inside "For a referrer" — wireframe .wf-act-btn spec.
   Scoped to container so this beats Streamlit's global .stButton > button rule */
[class*='st-key-am_for_a_referrer'] .stButton > button {
    font-size: 11px !important;
    font-weight: 500 !important;
    padding: 5px 10px !important;
    border: 0.5px solid var(--border-color) !important;
    border-radius: 6px !important;
    background: var(--bg-card) !important;
    color: var(--text-secondary) !important;
    box-shadow: none !important;
    height: auto !important;
    min-height: 0 !important;
    line-height: 1.4 !important;
    width: auto !important;
    margin-top: 4px !important;
    display: inline-flex !important;
    align-items: center !important;
    max-width: fit-content !important;
}

/* Timeline: matches wireframe — simple left border, solid purple dot */
.prof-timeline {
    padding-left: 6px !important;
    border-left: 2px solid var(--border-color) !important;
    max-width: none !important;
    margin: 0 !important;
}

.prof-timeline::before {
    display: none;
}

.prof-timeline .timeline-item {
    padding: 0 0 12px 16px !important;
    margin-bottom: 0 !important;
}

.prof-timeline .timeline-item::before {
    left: -7px !important;
    top: 4px !important;
    width: 10px !important;
    height: 10px !important;
    border-radius: 50% !important;
    background: var(--accent-purple) !important;
    border: none !important;
}

.prof-timeline-period { font-size: 11px !important; color: var(--accent-purple) !important; font-weight: 500 !important; margin: 0 !important; }
.prof-timeline-role   { font-size: 13px !important; font-weight: 500 !important; margin: 2px 0 1px !important; color: var(--text-primary) !important; }
.prof-timeline-org    { font-size: 11px !important; color: var(--text-secondary) !important; margin: 0 0 3px !important; }
.prof-timeline-desc   { font-size: 11px !important; color: var(--text-primary) !important; margin: 0 !important; line-height: 1.45 !important; }

/* prof-* mobile overrides — use !important to beat existing am-*/timeline-*
   mobile overrides that also use !important */
@media (max-width: 768px) {
    .prof-section-h {
        font-size: 12px !important;
        margin: 0 0 8px !important;
    }
    .prof-signals-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .prof-comp-grid {
        grid-template-columns: repeat(2, 1fr) !important;
        padding: 0 !important;
    }
    .prof-comp-name {
        font-size: 12px !important;
        margin: 0 0 3px !important;
    }
    .prof-comp-desc {
        font-size: 11px !important;
    }
    .prof-philosophy {
        grid-template-columns: 1fr !important;
        gap: 8px !important;
    }
    .prof-phil-h {
        font-size: 12px !important;
    }
    .prof-phil-p {
        font-size: 11px !important;
    }
    .prof-timeline .timeline-item {
        padding: 0 0 10px 14px !important;
    }
    .prof-timeline-role { font-size: 12px !important; }
}

/* Contact section - gradient works in both modes */
.contact-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 60px 20px;
    margin: 60px -1rem 0 -1rem;
    text-align: center;
}

.contact-section h2 {
    font-size: 32px;
    color: white;
    margin-bottom: 16px;
}

.contact-section p {
    color: rgba(255, 255, 255, 0.9);
}

.contact-buttons {
    display: flex;
    gap: 16px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 32px;
}

.contact-btn {
    padding: 14px 28px;
    background: rgba(255, 255, 255, 0.15);
    border: 2px solid white;
    border-radius: 8px;
    color: white;
    text-decoration: none;
    font-size: 15px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.contact-btn:hover {
    background: white;
    color: #8B5CF6;
}

.contact-btn.primary {
    background: white;
    color: #8B5CF6;
}

/* Secret sauce badge */
.secret-sauce-badge {
    display: inline-block;
    background: var(--accent-purple-bg, #e3f2fd);
    color: var(--accent-purple, #1976d2);
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
}

/* Dark mode adjustments */
[data-theme="dark"] .secret-sauce-badge {
    background: rgba(139, 92, 246, 0.2);
    color: #a78bfa;
}

/* Sample-question chip buttons (MATTGPT-068, [class*='st-key-about_matt_sample_q_'])
   live in ui/styles/global_styles.py — not here — so the rules are re-injected
   on every Streamlit script rerun and persist across the page transition to
   Ask Agy. See the comment block in global_styles.py for the full
   rationale (chip-click → AI thinking dim regression). */

/* Collapsible code block (MATTGPT-068) — wraps the 5-Stage RAG Pipeline
   snippet in <details> so non-technical readers can skip past it. */
details:has(.code-block) {
    margin: 16px 0;
}
details:has(.code-block) > summary {
    cursor: pointer;
    display: inline-block;
    padding: 8px 16px;
    background: var(--accent-purple-bg, rgba(139, 92, 246, 0.08));
    color: var(--accent-purple, #8B5CF6);
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    user-select: none;
    list-style: none;
}
details:has(.code-block) > summary::-webkit-details-marker {
    display: none;
}
details:has(.code-block) > summary::before {
    content: '▸ ';
    display: inline-block;
    transition: transform 0.15s ease;
}
details[open]:has(.code-block) > summary::before {
    content: '▾ ';
}

/* ============================================================================
   MOBILE RESPONSIVE STYLES (<768px)
   ============================================================================ */
@media (max-width: 768px) {
    /* Header */
    .about-header {
        padding: 20px 16px 20px 16px !important;
        min-height: 145.59px !important;
        margin-top: 60px !important;  /* clear 60px fixed mobile nav */
    }

    .about-header-content {
        flex-direction: row !important;
        text-align: left !important;
        gap: 12px !important;
        align-items: flex-start !important;
    }

    .about-header-avatar {
        width: 64px !important;
        height: 64px !important;
        border: 4px solid white !important;
    }

    .about-header-text h1 {
        font-size: 22px !important;
    }

    .about-header-text p {
        margin-top: -6px !important;
        font-size: 12px !important;
    }

    .prof-status-badge {
        display: none !important;
    }

    /* Removed: was hiding the second <p> (tagline) on mobile.
       about_matt.py now uses a single <p> for the subtitle — this rule
       was suppressing it. No replacement needed. */

    /* Stats bar */
    .am-stats-bar {
        grid-template-columns: repeat(5, 1fr) !important;
        margin: -4px 0 !important;
        padding: 8px 0 !important;
    }

    .am-stat-card {
        padding: 6px 2px !important;
    }

    .am-stat-number {
        font-size: 18px !important;
        margin-bottom: 2px !important;
    }

    .am-stat-label {
        font-size: 8px !important;
        letter-spacing: 0 !important;
    }

    /* Section titles */
    .am-section-title {
        font-size: 20px !important;
        margin: 32px 0 8px 0 !important;
    }

    .am-section-subtitle {
        font-size: 13px !important;
        margin-bottom: 20px !important;
    }

    /* Timeline */
    .timeline {
        padding-left: 24px !important;
    }

    .timeline::before {
        width: 3px !important;
    }

    .timeline-item {
        padding-left: 20px !important;
        margin-bottom: 20px !important;
    }

    .timeline-item::before {
        left: -34px !important;
        width: 16px !important;
        height: 16px !important;
        border-width: 3px !important;
    }

    .timeline-year {
        font-size: 12px !important;
    }

    .timeline-title {
        font-size: 14px !important;
    }

    .timeline-company {
        font-size: 12px !important;
    }

    .timeline-desc {
        font-size: 12px !important;
    }

    /* Deep-dive section */
    .deep-dive-section {
        padding: 24px 12px !important;
        margin: 24px -1rem 0 -1rem !important;
    }

    .deep-dive-card {
        padding: 16px !important;
        margin-bottom: 16px !important;
        flex-direction: column !important;
    }

    .deep-dive-card img {
        width: 120px !important;
        margin: 0 auto 12px auto !important;
        order: -1;
    }

    .deep-dive-card h3 {
        font-size: 18px !important;
    }

    .deep-dive-card p {
        font-size: 12px !important;
    }

    /* Tech grid */
    .tech-grid {
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 8px !important;
    }

    .tech-item {
        padding: 10px 8px !important;
        font-size: 11px !important;
    }

    /* Flow grid */
    .flow-grid {
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 16px !important;
    }

    .flow-step {
        padding: 12px 8px !important;
    }

    .flow-step:not(:last-child)::after {
        display: none !important;
    }

    .flow-num {
        width: 22px !important;
        height: 22px !important;
        font-size: 10px !important;
    }

    .flow-step-title {
        font-size: 11px !important;
    }

    .flow-step-desc {
        font-size: 9px !important;
    }

    /* Code block */
    .code-block {
        padding: 12px !important;
        font-size: 9px !important;
    }

    /* Details grid */
    .details-grid {
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 12px !important;
    }

    .detail-card {
        padding: 14px !important;
    }

    .detail-card h4 {
        font-size: 14px !important;
    }

    .detail-card ul {
        font-size: 11px !important;
    }

    /* CTA card */
    [class*='st-key-about_matt_cta_card'] {
        padding: 20px 16px !important;
    }

    [class*='st-key-about_matt_cta_card'] h3 {
        font-size: 18px !important;
    }

    [class*='st-key-about_matt_cta_card'] p {
        font-size: 12px !important;
    }

    /* Competencies grid */
    .competencies-grid {
        gap: 12px !important;
        padding: 0 8px !important;
    }

    .competency-card {
        padding: 16px !important;
    }

    .competency-card h4 {
        font-size: 14px !important;
        margin: 8px 0 10px 0 !important;
    }

    .competency-card div {
        font-size: 24px !important;
    }

    .competency-card li {
        font-size: 11px !important;
        padding: 4px 0 !important;
    }

    /* Philosophy grid */
    .philosophy-grid {
        grid-template-columns: 1fr !important;
        gap: 12px !important;
    }

    .philosophy-card {
        padding: 20px !important;
    }

    .philosophy-card h3 {
        font-size: 16px !important;
        margin-bottom: 10px !important;
    }

    .philosophy-card p {
        font-size: 12px !important;
        line-height: 1.5 !important;
    }

    /* Contact section */
    .contact-section {
        padding: 32px 16px !important;
        margin: 32px -1rem 0 -1rem !important;
    }

    .contact-section h2 {
        font-size: 20px !important;
    }

    .contact-section p {
        font-size: 13px !important;
    }

    .contact-buttons {
        gap: 10px !important;
        margin-top: 20px !important;
    }

    .contact-btn {
        padding: 10px 16px !important;
        font-size: 12px !important;
    }
}

/* ── Two-row filter bar (MATTGPT-065) ── */

/* Separator between row 1 and row 2 — confirmed via DevTools: st-key-r2_row is stVerticalBlock */
[class*="st-key-r2_row"] {
    border-top: 0.5px solid var(--border-color) !important;
    padding-top: 8px !important;
}

/* Row 2 compact dropdowns */
[class*="st-key-r2_client"] [data-baseweb="select"] > div:first-child,
[class*="st-key-r2_role"] [data-baseweb="select"] > div:first-child,
[class*="st-key-r2_domain"] [data-baseweb="select"] > div:first-child {
    padding: 5px 10px !important;
}

/* Remove default top margin Streamlit adds to buttons in form/filter rows */
[class*="st-key-r2_reset"] button,
[data-testid="stFormSubmitButton"] button {
    margin-top: 0 !important;
}

/* Reset button — visible border in light and dark mode */
[class*="st-key-r2_reset"] button {
    background: transparent !important;
    border: 1px solid var(--text-secondary) !important;
    border-radius: 4px !important;
    box-shadow: none !important;
    color: var(--text-secondary) !important;
    font-size: 12px !important;
    padding: 4px 10px !important;
    font-weight: 400 !important;
}
[class*="st-key-r2_reset"] button:hover {
    color: var(--text-primary) !important;
    background: var(--bg-hover) !important;
}

/* Bottom-align Row 2 widgets; center-align search form (MATTGPT-123: split from combined rule) */
[class*="st-key-r2_row"] [data-testid="stHorizontalBlock"] {
    align-items: flex-end !important;
}
[data-testid="stForm"] [data-testid="stHorizontalBlock"] {
    align-items: center !important;
}

/* Row 2 column gap — tighter than default 16px */
[class*="st-key-r2_row"] [data-testid="stHorizontalBlock"] {
    gap: 8px !important;
}

/* Mobile Filters toggle button — visible only on mobile (MATTGPT-119) */
[class*="st-key-es_mobile_filters_toggle"] {
    display: none !important;
}
@media (max-width: 767px) {
    [class*="st-key-es_mobile_filters_toggle"] {
        display: block !important;
    }
    [class*="st-key-es_mobile_filters_toggle"] button {
        font-size: 13px !important;
        padding: 4px 12px !important;
        background: transparent !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        color: var(--text-secondary) !important;
        box-shadow: none !important;
    }
}

/* Mobile: hide row 2 by default; show when open (key swap, MATTGPT-119) */
@media (max-width: 767px) {
    [class*="st-key-r2_row"] {
        display: none !important;
    }
    [class*="st-key-r2_row_open"] {
        display: block !important;
    }
}

/* ── MATTGPT-123: mobile filter layout compaction ── */
@media (max-width: 767px) {
    /* FIND STORIES: hide search form label */
    [data-testid="stForm"] [data-testid="stWidgetLabel"] {
        display: none !important;
    }

    /* INDUSTRY / CAPABILITY: label + dropdown inline on one row */
    [class*="st-key-facet_industry_v"] [data-testid="stSelectbox"],
    [class*="st-key-facet_capability_v"] [data-testid="stSelectbox"] {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        gap: 6px !important;
    }
    [class*="st-key-facet_industry_v"] [data-testid="stWidgetLabel"],
    [class*="st-key-facet_capability_v"] [data-testid="stWidgetLabel"] {
        flex: 0 0 auto !important;
        width: auto !important;
        min-height: 0 !important;
        font-size: 12px !important;
        line-height: 1 !important;
        margin-bottom: 0 !important;
        white-space: nowrap !important;
    }
    [class*="st-key-facet_industry_v"] [data-testid="stSelectbox"] > div:last-child,
    [class*="st-key-facet_capability_v"] [data-testid="stSelectbox"] > div:last-child {
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }

    /* ADVANCED FILTERS: hide labels — position in 3-col grid provides context */
    [class*="st-key-r2_client_v"] [data-testid="stWidgetLabel"],
    [class*="st-key-r2_role_v"] [data-testid="stWidgetLabel"],
    [class*="st-key-r2_domain_v"] [data-testid="stWidgetLabel"] {
        display: none !important;
    }

    /* ADVANCED FILTERS: inject field name via ::before on select control */
    [class*="st-key-r2_client_v"] [data-baseweb="select"] > div:first-child::before {
        content: "Client" !important;
        font-size: 10px !important;
        color: rgb(156, 163, 175) !important;
        padding-left: 8px !important;
        padding-right: 4px !important;
        white-space: nowrap !important;
        flex-shrink: 0 !important;
    }
    [class*="st-key-r2_role_v"] [data-baseweb="select"] > div:first-child::before {
        content: "Role" !important;
        font-size: 10px !important;
        color: rgb(156, 163, 175) !important;
        padding-left: 8px !important;
        padding-right: 4px !important;
        white-space: nowrap !important;
        flex-shrink: 0 !important;
    }
    [class*="st-key-r2_domain_v"] [data-baseweb="select"] > div:first-child::before {
        content: "Domain" !important;
        font-size: 10px !important;
        color: rgb(156, 163, 175) !important;
        padding-left: 8px !important;
        padding-right: 4px !important;
        white-space: nowrap !important;
        flex-shrink: 0 !important;
    }

    /* ADVANCED FILTERS: prevent ::before from crushing value div */
    [class*="st-key-r2_client_v"] [data-baseweb="select"] > div:first-child,
    [class*="st-key-r2_role_v"] [data-baseweb="select"] > div:first-child,
    [class*="st-key-r2_domain_v"] [data-baseweb="select"] > div:first-child {
        overflow: hidden !important;
    }

    /* ADVANCED FILTERS: 3-column grid (item 4 — column stacker excluded via 5th :not above) */
    [class*="st-key-r2_row_open"] [data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: 1fr 1fr 1fr !important;
        gap: 6px !important;
        align-items: center !important;
    }
    [class*="st-key-r2_row_open"] [data-testid="stColumn"] {
        min-width: 0 !important;
        width: 100% !important;
    }

    /* COMPACT DROPDOWN PADDING (all filters) */
    [class*="st-key-facet_"] [data-baseweb="select"] > div:first-child,
    [class*="st-key-r2_"] [data-baseweb="select"] > div:first-child {
        padding-top: 5px !important;
        padding-bottom: 5px !important;
    }

    /* RESET FILTERS: demote to text link (item 3) */
    [class*="st-key-r2_reset"] [data-testid="stBaseButton-secondary"] {
        border: none !important;
        background: transparent !important;
        color: rgb(156, 163, 175) !important;
        font-size: 11px !important;
        padding: 2px 8px !important;
        width: auto !important;
        text-decoration: underline !important;
        text-underline-offset: 2px !important;
    }

    /* FILTERS TOGGLE: full-width (item 1 — stLayoutWrapper ancestor also constrained) */
    [class*="st-key-es_mobile_filters_toggle"] [data-testid="stLayoutWrapper"],
    [class*="st-key-es_mobile_filters_toggle"] [data-testid="stElementContainer"],
    [class*="st-key-es_mobile_filters_toggle"] [data-testid="stButton"],
    [class*="st-key-es_mobile_filters_toggle"] button {
        width: 100% !important;
    }

    /* TIGHTEN INTER-ROW GAP */
    [data-testid="stVerticalBlock"]:has([class*="st-key-facet_"]) {
        gap: 6px !important;
    }
    [data-testid="stForm"] {
        margin-top: 3px !important;
        margin-bottom: 0px !important;
    }

    /* SEARCH BUTTON: collapse hidden label gap in submit button column */
    [data-testid="stForm"] [data-testid="stColumn"]:last-child [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
}


/* ── MATTGPT-105: consolidated CSS from render functions ── */

        /* ============================================================
           EXPLORE STORIES / STORY DETAIL / TIMELINE / FOOTER /
           THINKING INDICATOR — CSS promoted from render-function
           injections to global scope (MATTGPT-105).
           Collision-prone selectors prefixed .es-* (explore/detail/
           footer/thinking) or .es-tl-* (timeline-specific).
           Dead selectors deleted (not moved): card-role,
           card-domain-tag, card-close-hint, detail-connector,
           detail-arrow-up, card-btn-view-details, show-dropdown,
           card-footer.
           mobile_overrides.py: out of scope (never imported/applied).
           ============================================================ */

        /* ── Explore Stories: Pagination ── */
.es-pagination {
        padding: 20px 0;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 8px;
    }
    .es-pagination button {
        padding: 8px 14px;
        border: 1px solid var(--border-color);
        background: var(--bg-card);
        color: var(--text-secondary);
        cursor: pointer;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .es-pagination button:hover:not(:disabled):not(.active) {
        background: var(--bg-hover);
    }
    .es-pagination button.active {
        background: var(--accent-purple);
        color: white;
        border-color: var(--accent-purple);
    }
    .es-pagination button:disabled {
        opacity: 0.4;
        cursor: not-allowed;
    }
    .es-pagination .page-info {
        padding: 0 12px;
        color: var(--text-muted);
        font-size: 13px;
    }
    /* Hide Streamlit pagination triggers */
    [class*="st-key-pg_trigger_"] {
        position: absolute !important;
        left: -9999px !important;
        height: 0 !important;
        overflow: hidden !important;
    }
    @media (max-width: 480px) {
        .es-pagination {
            flex-wrap: wrap;
            gap: 4px;
            justify-content: center;
        }
        .es-pagination button {
            min-width: 32px;
            padding: 4px 6px;
            font-size: 11px;
        }
        .es-pagination .page-info {
            width: 100%;
            text-align: center;
            font-size: 11px;
        }
    }

        /* ── Explore Stories: Why Agy My Work trigger button hide ── */
[class*="st-key-why_agy_my_work_trigger"] {
    position: absolute !important;
    left: -9999px !important;
    height: 0 !important;
    overflow: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}
div[data-testid="stElementContainer"]:has([class*="st-key-why_agy_my_work_trigger"]) {
    position: absolute !important;
    left: -9999px !important;
    height: 0 !important;
    overflow: hidden !important;
}

        /* ── Explore Stories: Core CSS ── */
/* =============================================================================
       MY WORK CSS - CLEANED UP
       Redundancies removed, device-specific rules preserved
       ============================================================================= */

    /* =============================================================================
       HERO SECTION
       ============================================================================= */
    .conversation-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        min-height: 184px;
        box-sizing: border-box;
        border-radius: 0;
        margin: -2rem 0 0 0;
    }

    .conversation-header-content {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        max-width: 1200px;
        margin: 0;
    }

    .conversation-agy-avatar {
        flex-shrink: 0;
        width: 120px !important;
        height: 120px !important;
        border-radius: 50% !important;
        border: 4px solid white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }

    .main-avatar img,
    .header-agy-avatar {
        animation: agiAvatarReveal 0.15s ease-out 0.15s both;
    }
    @keyframes agiAvatarReveal {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    .conversation-header-text h1 {
        color: white !important;
        margin: 0;
        font-size: 2rem;
    }

    .conversation-header-text p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }

    /* =============================================================================
       PRINT STYLES
       ============================================================================= */
    @media print {
        header[data-testid="stHeader"],
        div[data-testid="stDecoration"],
        div[data-testid="stToolbar"],
        div[data-testid="stStatusWidget"],
        button,
        .stButton,
        footer {
            display: none !important;
        }

        .main .block-container,
        [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"],
        div[data-baseweb="block"] {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
        }

        body {
            background: white !important;
        }

        * {
            color: black !important;
        }

        .story-detail-pane {
            page-break-before: always;
        }
    }

    /* =============================================================================
       FILTER SECTION - BASE STYLES
       ============================================================================= */
    .main [data-testid="stContainer"] {
        padding: 12px 16px !important;
    }

    .main [data-testid="stContainer"] [data-testid="stVerticalBlock"] > div {
        margin-bottom: 2px !important;
    }

    .main [data-testid="stForm"] {
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
    }

    .main [data-testid="stForm"] [data-testid="stVerticalBlock"] > div {
        margin-bottom: 0 !important;
    }

    .main [data-testid="stFormSubmitButton"] button {
        padding: 6px 12px !important;
        min-height: 38px !important;
        height: 38px !important;
    }

    /* Advanced/Reset buttons */
    [class*="st-key-btn_toggle_advanced"] button,
    [class*="st-key-btn_reset_filters"] button {
        padding: 4px 12px !important;
        font-size: 12px !important;
        background: transparent !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-muted) !important;
        min-height: 32px !important;
    }

    [class*="st-key-btn_toggle_advanced"] button:hover,
    [class*="st-key-btn_reset_filters"] button:hover {
        background: var(--bg-hover) !important;
    }

    .explore-filters {
        background: var(--bg-surface);
        padding: 30px;
        border-bottom: 1px solid var(--border-color);
    }

    /* Filter chip row - force horizontal flex layout */
    .st-key-chip_row,
    .st-key-chip_row > div,
    .st-key-chip_row > div > div {
        display: flex !important;
        flex-wrap: wrap !important;
        flex-direction: row !important;
        gap: 6px !important;
        align-items: center !important;
    }
    .st-key-chip_row [data-testid="element-container"] {
        width: auto !important;
        flex: none !important;
    }

    /* Filter chip buttons - pill styling */
    .st-key-chip_row [class*="st-key-chip_"] button {
        border-radius: 16px !important;
        font-size: 12px !important;
        padding: 4px 10px !important;
        font-weight: 500 !important;
        white-space: nowrap !important;
        transition: all 0.15s ease !important;
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
    }
    .st-key-chip_row [class*="st-key-chip_"] button p {
        font-size: 12px !important;
        padding: 0 !important;
        margin: 0 !important;
        color: inherit !important;
    }
    .st-key-chip_row [class*="st-key-chip_"] button:hover {
        border-color: #EF4444 !important;
        color: #DC2626 !important;
        background: #FEF2F2 !important;
    }
    /* "Clear all" chip - surface bg to distinguish */
    .st-key-chip_row .st-key-chip_clear_all button {
        background: var(--bg-surface) !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border-color) !important;
    }
    .st-key-chip_row .st-key-chip_clear_all button:hover {
        border-color: #EF4444 !important;
        color: #DC2626 !important;
        background: #FEF2F2 !important;
    }


    /* =============================================================================
       FORM INPUTS - BASE STYLES
       ============================================================================= */

    [data-baseweb="input"],
    [data-baseweb="base-input"],
    [data-baseweb="input"] input {
            min-height: 44px !important;
            height: 44px !important;
        }

    /* Prevent textarea wrapper from being clipped by the rule above */
    .stTextArea [data-baseweb="base-input"] {
        height: auto !important;
        min-height: auto !important;
    }

    .main .stTextInput > div > div > input {
        height: 44px !important;
        min-height: 44px !important;
        width: 100% !important;
        padding: 10px 14px !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        background: var(--bg-input) !important;
        color: var(--text-primary) !important;
    }

    .main .stTextInput > div > div > input:focus {
        border-color: var(--accent-purple) !important;
        outline: none !important;
    }

    /* Search form submit button */
    [class*="search_form"] button[kind="secondaryFormSubmit"],
    [class*="search_form"] button[type="submit"],
    .stForm button[kind="secondaryFormSubmit"] {
        width: 40px !important;
        min-width: 40px !important;
        max-width: 40px !important;
        height: 40px !important;
        padding: 0 !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 6px !important;
        background: var(--bg-card) !important;
        color: var(--text-secondary) !important;
        font-size: 16px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    [class*="search_form"] button[kind="secondaryFormSubmit"]:hover,
    [class*="search_form"] button[type="submit"]:hover,
    .stForm button[kind="secondaryFormSubmit"]:hover {
        border-color: var(--accent-purple) !important;
        background: var(--bg-hover) !important;
    }

    /* Selectbox */
    .main .stSelectbox > div > div {
        padding: 8px !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 4px !important;
        font-size: 14px !important;
        background: var(--bg-input) !important;
        color: var(--text-primary) !important;
    }

    .main .stSelectbox > div > div:focus-within {
        border-color: var(--accent-purple) !important;
        outline: none !important;
    }

    /* Multiselect */
    .main .stMultiSelect > div > div {
        padding: 8px !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 4px !important;
        font-size: 14px !important;
        background: var(--bg-input) !important;
        color: var(--text-primary) !important;
    }

    .main .stMultiSelect > div > div:focus-within {
        border-color: var(--accent-purple) !important;
    }

    /* Labels */
    .main label[data-testid="stWidgetLabel"] {
        font-size: 12px !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase !important;
        margin-bottom: 4px !important;
    }

    /* =============================================================================
       SEGMENTED CONTROL (Table/Cards/Timeline toggle)
       ============================================================================= */

    /* Active button - emotion class override */
    button.st-emotion-cache-1umuqkm.e8vg11g13,
    button.st-emotion-cache-1umuqkm.e8vg11g13:active,
    button.st-emotion-cache-1umuqkm.e8vg11g13:focus,
    button.st-emotion-cache-1umuqkm.e8vg11g13:hover {
        background: #8B5CF6 !important;
        background-color: #8B5CF6 !important;
        border: 1px solid #8B5CF6 !important;
        color: white !important;
    }

    button.st-emotion-cache-1umuqkm.e8vg11g13 p,
    button.st-emotion-cache-1umuqkm.e8vg11g13 * {
        color: white !important;
    }

    /* Inactive button - emotion class */
    button.st-emotion-cache-2mqt7m.e8vg11g12,
    button.st-emotion-cache-2mqt7m.e8vg11g12:active,
    button.st-emotion-cache-2mqt7m.e8vg11g12:focus {
        background: var(--bg-card) !important;
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-secondary) !important;
    }

    button.st-emotion-cache-2mqt7m.e8vg11g12 p,
    button.st-emotion-cache-2mqt7m.e8vg11g12 * {
        color: var(--text-secondary) !important;
    }

    button.st-emotion-cache-2mqt7m.e8vg11g12:hover {
        background: var(--bg-hover) !important;
        background-color: var(--bg-hover) !important;
    }

    /* Active button - kind attribute fallback */
    button[kind="segmented_controlActive"],
    button[kind="segmented_controlActive"]:active,
    button[kind="segmented_controlActive"]:focus,
    button[kind="segmented_controlActive"]:hover,
    [data-testid="stBaseButton-segmented_controlActive"] {
        background: #8B5CF6 !important;
        border: 1px solid #8B5CF6 !important;
        color: white !important;
    }

    button[kind="segmented_controlActive"] p,
    button[kind="segmented_controlActive"] div,
    button[kind="segmented_controlActive"] *,
    [data-testid="stBaseButton-segmented_controlActive"] p,
    [data-testid="stBaseButton-segmented_controlActive"] * {
        color: white !important;
    }

    /* Inactive button - kind attribute fallback */
    button[kind="segmented_control"],
    button[kind="segmented_control"]:active,
    button[kind="segmented_control"]:focus,
    [data-testid="stBaseButton-segmented_control"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-secondary) !important;
    }

    button[kind="segmented_control"] p,
    button[kind="segmented_control"] div,
    button[kind="segmented_control"] *,
    [data-testid="stBaseButton-segmented_control"] p,
    [data-testid="stBaseButton-segmented_control"] * {
        color: var(--text-secondary) !important;
    }

    button[kind="segmented_control"]:hover {
        background: var(--bg-hover) !important;
        border-color: var(--text-muted) !important;
    }

    .stButtonGroup p,
    [data-testid="stButtonGroup"] p {
        color: inherit !important;
    }

    /* =============================================================================
       TABLE STYLES
       ============================================================================= */
    .main table {
        border-collapse: collapse !important;
    }
    .main thead {
        background: var(--table-header-bg) !important;
    }
    .main th {
        padding: 12px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        text-transform: uppercase !important;
        border-bottom: 2px solid var(--border-color) !important;
        text-align: left !important;
    }
    .main td {
        padding: 16px 12px !important;
        border-bottom: 1px solid var(--border-color) !important;
        font-size: 14px !important;
        color: var(--text-primary) !important;
    }
    .main td a {
        color: var(--accent-purple) !important;
        font-weight: 500 !important;
        text-decoration: none !important;
    }
    .main td a:hover {
        text-decoration: underline !important;
    }

    .es-client-badge {
        display: inline-block !important;
        padding: 4px 10px !important;
        background: var(--accent-purple-bg) !important;
        color: var(--accent-purple) !important;
        border-radius: 12px !important;
        font-size: 12px !important;
        font-weight: 500 !important;
    }

    .es-domain-tag {
        font-size: 12px !important;
        color: var(--text-muted) !important;
    }

    .ag-row-selected {
        background: #F3E8FF !important;
        border-left: 4px solid #8B5CF6 !important;
    }
    .ag-row-selected td {
        font-weight: 500 !important;
    }

    /* =============================================================================
       BUTTON STYLES
       ============================================================================= */
    .main .stButton > button {
        padding: 6px 14px !important;
        border: 1px solid var(--border-color) !important;
        background: var(--bg-card) !important;
        cursor: pointer !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        border-radius: 6px !important;
        color: var(--text-secondary) !important;
        transition: all 0.2s ease !important;
    }

    .main .stButton > button:hover {
        background: var(--bg-hover) !important;
    }



    /* Hide card trigger buttons */
    [class*="st-key-card_btn_"] {
        position: absolute !important;
        left: -9999px !important;
        height: 0 !important;
        overflow: hidden !important;
    }

    /* Hide timeline trigger buttons */
    [class*="st-key-timeline_story_"],
    [class*="st-key-timeline_explore_"],
    [class*="st-key-timeline_toggle_"] {
        position: absolute !important;
        left: -9999px !important;
        height: 0 !important;
        overflow: hidden !important;
    }

    /* Ask Agy button */
    [class*="st-key-ask_from_detail"] .stButton > button[kind="primary"],
    div[class*="st-key-ask_from_detail"] button[data-testid="stBaseButton-primary"] {
        background: var(--accent-purple) !important;
        border: 2px solid var(--accent-purple) !important;
        border-radius: 8px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.2s ease !important;
    }

    [class*="st-key-ask_from_detail"] .stButton > button[kind="primary"]:hover,
    div[class*="st-key-ask_from_detail"] button[data-testid="stBaseButton-primary"]:hover {
        background: var(--accent-purple-hover) !important;
        border-color: var(--accent-purple-hover) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3) !important;
    }

    /* =============================================================================
       CARDS GRID
       ============================================================================= */
    .story-cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
        gap: 20px;
        margin-bottom: 24px;
    }

    .es-fixed-height-card {
        background: var(--bg-card) !important;
        padding: 24px !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-color) !important;
        height: 380px !important;
        display: flex !important;
        flex-direction: column !important;
        box-shadow: var(--card-shadow) !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }

    .es-fixed-height-card:hover {
        box-shadow: var(--hover-shadow) !important;
        border-color: var(--accent-purple) !important;
        transform: translateY(-2px) !important;
    }

    .es-fixed-height-card.active {
        border-color: var(--accent-purple) !important;
        box-shadow: 0 0 0 3px var(--accent-purple-light) !important;
    }

    .es-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
    }

    .es-card-title {
        font-size: 18px;
        font-weight: 600;
        margin: 0;
        line-height: 1.4;
        color: var(--text-heading) !important;
        flex: 1;
    }

    .es-card-client-badge {
        background: var(--accent-purple-bg);
        color: var(--accent-purple);
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
        white-space: nowrap;
        margin-left: 12px;
    }

    .es-card-desc {
        color: var(--text-secondary) !important;
        line-height: 1.6 !important;
        font-size: 14px !important;
        overflow: hidden !important;
        display: -webkit-box !important;
        -webkit-line-clamp: 3 !important;
        -webkit-box-orient: vertical !important;
        flex-grow: 1 !important;
        margin-bottom: 16px !important;
    }



    .es-card-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 12px;
        border-top: 1px solid var(--border-color);
        margin-top: auto;
    }

    .es-role-badge {
        font-size: 11px;
        font-weight: 500;
        color: var(--text-secondary);
        max-width: 180px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .es-domain-tag {
        font-size: 11px;
        color: var(--text-muted);
        text-align: right;
        max-width: 150px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* Selected card state */
    .es-fixed-height-card.selected {
        border-color: var(--accent-purple) !important;
        box-shadow: 0 0 0 3px var(--accent-purple-light) !important;
    }






    /* Selected card becomes Close button */
    .es-card-close-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        min-height: 280px;
        color: var(--accent-purple);
    }

    .es-card-close-state .close-x {
        font-size: 36px;
        font-weight: 300;
        margin-bottom: 8px;
    }

    .es-card-close-state .close-text {
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* =============================================================================
       SPACING ADJUSTMENTS
       ============================================================================= */
    .main .stMultiSelect, .main .stSelectbox, .main .stTextInput {
        margin-bottom: 0px !important;
        margin-top: 0px !important;
    }

    .main [data-testid="stVerticalBlock"] > div {
        gap: 8px !important;
    }

    .main .stButton {
        margin-top: 0px !important;
        margin-bottom: 0px !important;
    }

    /* Scope to explore page content only — exclude navbar */
    div[data-testid="stHorizontalBlock"]:not(:has([class*="st-key-topnav_"])):has(> div:nth-child(5)) > div:nth-child(3) {
        flex: 0 0 75px !important;
        max-width: 75px !important;
    }

    /* =============================================================================
       SHOW DROPDOWN - ALL BREAKPOINTS (CONSOLIDATED)
       ============================================================================= */
    [class*="st-key-page_size_select"] {
        max-width: 80px !important;
        min-width: 70px !important;
        width: 80px !important;
    }

    [class*="st-key-page_size_select"] > div {
        min-width: 70px !important;
        max-width: 80px !important;
    }

    /* Results row - force single line */
    [data-testid="stHorizontalBlock"]:has([class*="st-key-page_size_select"]) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 12px !important;
    }

    [data-testid="stHorizontalBlock"]:has([class*="st-key-page_size_select"]) > [data-testid="stColumn"] {
        flex: 0 0 auto !important;
        width: auto !important;
        min-width: 0 !important;
    }

    [data-testid="stHorizontalBlock"]:has([class*="st-key-page_size_select"]) > [data-testid="stColumn"]:first-child {
        flex: 1 1 auto !important;
    }

    /* =============================================================================
       TABLET (768px - 1024px)
       ============================================================================= */
    @media (min-width: 768px) and (max-width: 1024px) {
        /* Hide form submit button */
        [data-testid="stForm"] [data-testid="stColumn"]:last-child {
            display: none !important;
        }

        /* Keep filter columns horizontal */
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            flex-direction: row !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            flex: 1 1 0 !important;
            min-width: 0 !important;
        }

        /* Results row - hide SHOW label and spacer */
        [data-testid="stHorizontalBlock"]:has([data-testid="stButtonGroup"]) > [data-testid="stColumn"]:nth-child(2),
        [data-testid="stHorizontalBlock"]:has([data-testid="stButtonGroup"]) > [data-testid="stColumn"]:nth-child(4) {
            display: none !important;
        }
    }

    /* =============================================================================
       MOBILE (< 768px)
       ============================================================================= */
    @media (max-width: 767px) {
        /* -----------------------------------------
           HERO - Compact
           ----------------------------------------- */
        .conversation-header {
            padding: 20px 16px !important;
            min-height: 145.59px !important;
            margin: 60px 0 0 0 !important;  /* clear 60px fixed mobile nav */
        }

        .conversation-header-content {
            flex-direction: row !important;
            text-align: left !important;
            gap: 12px !important;
            align-items: flex-start !important;
        }

        .conversation-agy-avatar {
            width: 64px !important;
            height: 64px !important;
            border: 4px solid white !important;
        }

        .conversation-header-text h1 {
            font-size: 20px !important;
        }

        .conversation-header-text p {
            font-size: 13px !important;
        }

        /* -----------------------------------------
           FILTER SECTION
           ----------------------------------------- */
        [data-testid="stVerticalBlockBorderWrapper"] {
            padding: 12px !important;
        }

        /* Hide all labels */
        [data-testid="stVerticalBlockBorderWrapper"] label,
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stWidgetLabel"] {
            display: none !important;
            position: absolute !important;
            left: -9999px !important;
        }

        /* Filter columns layout */
        [data-testid="stHorizontalBlock"]:has([class*="st-key-facet_"]):not(:has([data-testid="stFormSubmitButton"])) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: wrap !important;
            gap: 8px !important;
        }

        /* Search - full width */
        [data-testid="stColumn"]:has([class*="st-key-facet_q"]) {
            flex: 0 0 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
            width: 100% !important;
            margin: 0 0 4px 0 !important;
        }

        /* Fix dropdown text truncation */
        .stSelectbox [data-baseweb="select"] > div {
            min-width: 100% !important;
            overflow: visible !important;
        }

        .stSelectbox [data-baseweb="select"] span {
            overflow: visible !important;
            text-overflow: unset !important;
        }

        /* Industry - 50% */
        [data-testid="stColumn"]:has([class*="st-key-facet_industry"]) {
            flex: 0 0 calc(50% - 4px) !important;
            min-width: calc(50% - 4px) !important;
            max-width: calc(50% - 4px) !important;
            width: calc(50% - 4px) !important;
            margin: 0 !important;
        }

        /* Capability - 50% */
        [data-testid="stColumn"]:has([class*="st-key-facet_capability"]) {
            flex: 0 0 calc(50% - 4px) !important;
            min-width: calc(50% - 4px) !important;
            max-width: calc(50% - 4px) !important;
            width: calc(50% - 4px) !important;
            margin: 0 !important;
        }

        /* Search form column sizing — rule moved to mobile stacking block above (source-order fix) */
        [data-testid="stForm"] [data-testid="stColumn"]:first-child {
            flex: 1 1 auto !important;
            min-width: 0 !important;
        }

        /* Hide spacer div, chips, expander */
        [data-testid="stForm"] div[style*="height: 23px"],
        .st-key-chip_row,
        [data-testid="stExpander"] {
            display: none !important;
        }

        /* Compact inputs */
        .stTextInput > div > div > input {
            padding: 12px 14px !important;
            font-size: 15px !important;
            border-radius: 8px !important;
        }

        .stSelectbox > div > div {
            padding: 10px 12px !important;
            font-size: 15px !important;
            min-height: 44px !important;
            border-radius: 8px !important;
        }

        .stSelectbox [data-baseweb="select"] > div {
            display: flex !important;
            align-items: center !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {
            gap: 8px !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] > div {
            margin-bottom: 0 !important;
        }

        /* -----------------------------------------
           RESULTS ROW
           ----------------------------------------- */
        [data-testid="stHorizontalBlock"]:has([data-testid="stButtonGroup"]) {
            flex-direction: row !important;
            align-items: center !important;
            gap: 8px !important;
        }

        [data-testid="stHorizontalBlock"]:has([data-testid="stButtonGroup"]) > [data-testid="stColumn"]:nth-child(2),
        [data-testid="stHorizontalBlock"]:has([data-testid="stButtonGroup"]) > [data-testid="stColumn"]:nth-child(3),
        [data-testid="stHorizontalBlock"]:has([data-testid="stButtonGroup"]) > [data-testid="stColumn"]:nth-child(4) {
            display: none !important;
        }

        [data-testid="stHorizontalBlock"]:has([data-testid="stButtonGroup"]) > [data-testid="stColumn"]:first-child {
            flex: 1 !important;
            min-width: 0 !important;
            margin: 0 !important;
        }

        [data-testid="stHorizontalBlock"]:has([data-testid="stButtonGroup"]) > [data-testid="stColumn"]:last-child {
            flex: 0 0 auto !important;
            min-width: 120px !important;
            width: auto !important;
            margin: 0 !important;
        }

        /* Button group horizontal */
        [data-testid="stButtonGroup"],
        [data-testid="stButtonGroup"] > div,
        .stButtonGroup,
        .stButtonGroup > div {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            display: flex !important;
            width: auto !important;
        }

        [data-testid="stButtonGroup"] button {
            padding: 6px 10px !important;
            font-size: 12px !important;
            min-width: auto !important;
            width: auto !important;
            white-space: nowrap !important;
        }
        /* Results count - prevent wrapping */
        .es-results-count {
            font-size: 12px !important;
            white-space: nowrap !important;
        }

        /* Fix selectbox showing "..." - ensure minimum width */
        .stSelectbox [data-baseweb="select"] {
            min-width: 100% !important;
        }

        /* Hide SHOW label on mobile */
        [data-testid="stHorizontalBlock"]:has([class*="st-key-page_size_select"]) > [data-testid="stColumn"]:nth-child(2) {
            display: none !important;
        }
        /* -----------------------------------------
        TABLE
        ----------------------------------------- */
        .ag-root-wrapper {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }

        .ag-header,
        .ag-body-viewport {
            min-width: 600px !important;
        }

        .ag-header-cell[col-id="Domain"],
        .ag-cell[col-id="Domain"],
        div[col-id="Domain"] {
            display: none !important;
            width: 0 !important;
            min-width: 0 !important;
            max-width: 0 !important;
            padding: 0 !important;
            border: none !important;
            overflow: hidden !important;
        }

        .ag-cell {
            padding: 8px !important;
            font-size: 13px !important;
        }

        .ag-header-cell {
            padding: 8px !important;
            font-size: 11px !important;
        }

        /* -----------------------------------------
           CARDS
           ----------------------------------------- */
        .story-cards-grid {
            grid-template-columns: 1fr !important;
        }

        .es-fixed-height-card {
            height: auto !important;
            min-height: 280px !important;
        }

        /* -----------------------------------------
           PAGINATION
           ----------------------------------------- */
        .es-pagination {
            flex-wrap: wrap !important;
            gap: 6px !important;
            padding: 12px 0 !important;
        }

        .es-pagination button {
            padding: 8px 12px !important;
            font-size: 12px !important;
        }

        .es-pagination .page-info {
            width: 100% !important;
            text-align: center !important;
            order: -1 !important;
            padding: 0 0 8px 0 !important;
        }
    }

        /* ── Explore Stories: Table swipe hint ── */
.es-table-swipe-hint {
                display: none;
                text-align: center;
                padding: 8px 16px;
                background: var(--bg-surface);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                margin-bottom: 12px;
                font-size: 13px;
                color: var(--text-muted);
            }
            @media (max-width: 767px) {
                .es-table-swipe-hint {
                    display: block;
                }
            }

        /* ── Story Detail: Header ── */
/* Action buttons - matches wireframe exactly */
    .es-detail-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 2px solid var(--border-color, #e0e0e0);
        background: linear-gradient(180deg, var(--accent-purple-bg) 0%, transparent 100%);
        padding-top: 16px;
        scroll-margin-top: 80px;
    }

    .es-detail-title-section {
        flex: 1;
    }

    .es-detail-title {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: var(--accent-purple-text) !important;
        margin-bottom: 12px !important;
        line-height: 1.3 !important;
    }

    .es-detail-meta {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        align-items: center;
    }

    .es-detail-meta-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
        color: var(--text-muted, #7f8c8d);
    }

    .es-detail-meta-item strong {
        color: var(--text-primary, #2c3e50);
    }

    .es-detail-actions {
        display: flex;
        gap: 8px;
        flex-shrink: 0;
    }

    .es-detail-action-btn {
        padding: 8px 16px;
        border: 2px solid var(--border-color, #e0e0e0);
        background: var(--bg-card, white);
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        color: var(--text-secondary, #555);
        cursor: pointer;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .es-detail-action-btn:hover {
        border-color: var(--accent-purple, #8B5CF6);
        color: var(--accent-purple, #8B5CF6);
    }

    /* Hide Streamlit trigger buttons */
    [class*="st-key-share_"],
    [class*="st-key-export_"],
    [class*="st-key-helpful_"] {
        position: absolute !important;
        left: -9999px !important;
        height: 0 !important;
        overflow: hidden !important;
    }

    /* Helpful button confirmed state */
    .es-detail-action-btn.helpful-confirmed {
        background: var(--success-color) !important;
        border-color: var(--success-color) !important;
        color: white !important;
        cursor: default;
        opacity: 1;
    }
    .es-detail-action-btn.helpful-confirmed:hover {
        border-color: var(--success-color) !important;
        color: white !important;
    }

    /* Mobile: optimized for scanning, not reading */
    @media (max-width: 768px) {
        .es-detail-header {
            flex-direction: column;
            gap: 12px;
        }

        .es-detail-title {
            font-size: 18px !important;
        }

        .es-detail-meta {
            gap: 6px 12px;
            font-size: 12px;
        }

        .es-detail-meta-item {
            font-size: 12px;
        }

        .es-detail-meta-item .meta-icon {
            display: none;
        }

        .es-detail-meta-item:not(:first-child)::before {
            content: "•";
            margin-right: 6px;
            color: var(--text-muted);
        }

        /* Hide Share/Export on mobile - these are desktop actions */
        .es-detail-actions {
            display: none !important;
        }

        /* STAR sections: truncate to 3 lines on mobile */
        .es-star-content {
            display: -webkit-box !important;
            -webkit-line-clamp: 3 !important;
            -webkit-box-orient: vertical !important;
            overflow: hidden !important;
        }

        /* Tighter spacing between STAR sections on mobile */
        .es-star-section {
            margin-bottom: 16px !important;
        }
    }

    /* Ensure star-content has no extra margin */
    .es-star-content {
        margin: 0 !important;
        padding: 0 !important;
    }

        /* ── Story Detail: Card button primary / pagination ── */
.es-card-btn-primary {
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
        }

        .es-card-btn-primary:hover {
            background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);
            text-decoration: none !important;
        }
        [class*="st-key-ask_story_"] {
            display: none !important;
        }
        [class*="st-key-btn_page_"] .stButton > button,
        [class*="st-key-btn_first_"] .stButton > button,
        [class*="st-key-btn_prev_"] .stButton > button,
        [class*="st-key-btn_next_"] .stButton > button,
        [class*="st-key-btn_last_"] .stButton > button {
            padding: 8px 16px !important;
            font-size: 13px !important;
            border-radius: 6px !important;
            border: 1px solid var(--border-color) !important;
            background: var(--bg-card) !important;
            color: var(--text-secondary) !important;
            margin-top: 0 !important;
            box-shadow: none !important;
            width: auto !important;
        }

        /* ── Footer ── */
/* Hide the footer trigger button */
    [class*="st-key-footer_ask"] {
        display: none !important;
    }

    /* Mobile responsive footer */
    @media (max-width: 767px) {
        .footer-connect {
            padding: 24px 16px !important;
            margin-top: 24px !important;
        }
        .footer-connect h3 {
            font-size: 20px !important;
            margin-bottom: 8px !important;
        }
        .footer-connect .footer-desc {
            font-size: 13px !important;
            margin-bottom: 6px !important;
        }
        .footer-connect .footer-avail {
            font-size: 11px !important;
            margin-bottom: 16px !important;
        }
        .footer-connect .footer-buttons {
            gap: 8px !important;
        }
        .footer-connect .footer-buttons a {
            padding: 10px 16px !important;
            font-size: 12px !important;
        }
    }

        /* ── Timeline View ── */
/* =============================================================================
       TIMELINE VIEW - COLLAPSIBLE GROUPS (ERA-BASED)
       Uses app's existing CSS variables from global_styles.py
       ============================================================================= */

    .es-timeline-container {
        position: relative;
        max-width: 900px;
        margin: 0 auto;
        padding-left: 220px;
        font-family: "Source Sans Pro", -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main vertical line */
    .es-timeline-container::before {
        content: '';
        position: absolute;
        left: 200px;
        top: 20px;
        bottom: 20px;
        width: 3px;
        background: linear-gradient(to bottom, #8b5cf6, #a78bfa, #c4b5fd);
        border-radius: 2px;
    }

    /* Timeline Group */
    .es-timeline-group {
        position: relative;
        margin-bottom: 24px;
    }

    /* Group Header */
    .es-group-header {
        position: relative;
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 8px 0;
        cursor: pointer;
        user-select: none;
    }

    /* Timeline dot */
    .es-timeline-dot {
        position: absolute;
        left: -24px;
        width: 14px;
        height: 14px;
        background: var(--bg-card);
        border: 3px solid var(--accent-purple);
        border-radius: 50%;
        z-index: 2;
        transition: all 0.2s;
    }

    .es-timeline-group.expanded .es-timeline-dot {
        background: var(--accent-purple);
        box-shadow: 0 0 0 4px var(--accent-purple-light);
    }

    .es-group-header:hover .es-timeline-dot {
        transform: scale(1.2);
    }

    /* Era Badge - positioned to left of timeline */
    .es-era-badge {
        position: absolute;
        left: -220px;
        width: 190px;
        text-align: right;
        padding-right: 20px;
        line-height: 1.3;
    }

    .es-era-title {
        display: block;
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 4px;
    }

    .es-era-dates {
        display: block;
        font-size: 12px;
        color: var(--accent-purple);
        font-weight: 500;
    }

    /* Group info box */
    .es-group-info {
        display: flex;
        flex-direction: column;
        gap: 4px;
        padding: 12px 16px;
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        transition: all 0.2s;
        min-width: 200px;
    }

    .es-group-info-header {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .es-group-header:hover .es-group-info {
        border-color: var(--accent-purple);
        background: var(--bg-hover);
    }

    .es-expand-icon {
        font-size: 12px;
        color: var(--text-muted);
        transition: transform 0.2s;
    }

    .es-timeline-group.expanded .es-expand-icon {
        transform: rotate(90deg);
    }

    .es-story-count {
        font-size: 14px;
        color: var(--text-secondary);
    }

    .es-story-count strong {
        color: var(--text-primary);
    }

    .es-era-subtitle {
        font-size: 12px;
        color: var(--text-muted);
        font-style: italic;
    }

    /* Stories container - hidden by default */
    .es-stories-container {
        display: none;
        padding-left: 20px;
        padding-top: 12px;
    }

    .es-timeline-group.expanded .es-stories-container {
        display: block;
    }

    /* Individual story card */
    .es-story-card {
        position: relative;
        padding: 16px 20px;
        margin-bottom: 12px;
        margin-left: 30px;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
    }

    .es-story-card::before {
        content: '';
        position: absolute;
        left: -30px;
        top: 50%;
        width: 20px;
        height: 2px;
        background: var(--border-color);
    }

    .es-story-card::after {
        content: '';
        position: absolute;
        left: -14px;
        top: 50%;
        transform: translateY(-50%);
        width: 8px;
        height: 8px;
        background: var(--bg-card);
        border: 2px solid var(--accent-purple-light);
        border-radius: 50%;
    }

    .es-story-card:hover {
        border-color: var(--accent-purple);
        background: var(--bg-hover);
        box-shadow: var(--hover-shadow);
        transform: translateX(4px);
    }

    .es-story-card.selected {
        border-color: var(--accent-purple);
        background: var(--accent-purple-bg);
        box-shadow: 0 0 0 3px var(--accent-purple-light);
    }

    .es-story-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 8px;
    }

    .es-story-title {
        font-size: 15px;
        font-weight: 600;
        color: var(--text-primary);
        line-height: 1.4;
        flex: 1;
    }

    .es-tl-client-badge {
        background: var(--accent-purple-bg);
        color: var(--accent-purple);
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;
        white-space: nowrap;
    }

    .es-story-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        color: var(--text-muted);
    }

    .es-tl-role-badge {
        background: var(--bg-surface);
        color: var(--text-secondary);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 500;
    }

    .es-story-meta-divider {
        color: var(--border-color);
    }

    /* Explore all link */
    .es-explore-all-link {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-left: 30px;
        margin-top: 8px;
        padding: 10px 16px;
        font-size: 13px;
        font-weight: 500;
        color: var(--accent-purple);
        background: transparent;
        border: 1px dashed var(--accent-purple-light);
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s;
    }

    .es-explore-all-link:hover {
        background: var(--accent-purple-bg);
        color: var(--accent-purple-hover);
    }

    /* =============================================================================
       MOBILE RESPONSIVE - Single-column layout
       Standard pattern: line on left, all content to right
       ============================================================================= */

    @media (max-width: 767px) {
        .es-timeline-container {
            padding-left: 40px;
            max-width: 100%;
        }

        .es-timeline-container::before {
            left: 15px;
        }

        /* Era badge moves above the card, not to the left */
        .es-era-badge {
            position: relative;
            left: 0;
            width: 100%;
            text-align: left;
            padding-right: 0;
            padding-left: 0;
            margin-bottom: 4px;
        }

        .es-era-title {
            font-size: 14px;
            font-weight: 600;
            display: inline;
        }

        .es-era-dates {
            font-size: 12px;
            display: inline;
            margin-left: 8px;
        }

        .es-timeline-dot {
            left: -29px;
            width: 12px;
            height: 12px;
        }

        .es-group-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 4px;
        }

        .es-group-info {
            width: 100%;
        }

        .es-timeline-group {
            margin-bottom: 20px;
        }

        .es-story-card {
            padding: 12px 16px;
            margin-left: 0;
            margin-right: 0;
        }

        .es-story-card::before,
        .es-story-card::after {
            display: none;
        }

        /* Stack header vertically on mobile */
        .es-story-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
        }

        .es-story-title {
            font-size: 14px;
            /* Limit to 2 lines */
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .es-tl-client-badge {
            font-size: 10px;
            padding: 3px 8px;
            max-width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* Stack meta vertically too */
        .es-story-meta {
            flex-wrap: wrap;
            gap: 4px 8px;
        }

        .es-explore-all-link {
            margin-left: 0;
            font-size: 12px;
            padding: 10px 12px;
        }
    }

    /* =============================================================================
       HIDDEN TRIGGER BUTTONS
       ============================================================================= */

    [class*="st-key-timeline_story_"],
    [class*="st-key-timeline_explore_"],
    [class*="st-key-timeline_toggle_"] {
        position: absolute !important;
        left: -9999px !important;
        height: 0 !important;
        overflow: hidden !important;
    }

        /* ── Thinking Indicator ── */
.thinking-backdrop {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.4);
                z-index: 99998;
            }
            [data-theme="dark"] .thinking-backdrop {
                background: rgba(0, 0, 0, 0.6);
            }
            @keyframes chaseAnimation {
                0% { content: url('/app/static/chase_48px_1.png'); }
                33.33% { content: url('/app/static/chase_48px_2.png'); }
                66.66% { content: url('/app/static/chase_48px_3.png'); }
                100% { content: url('/app/static/chase_48px_1.png'); }
            }
            .thinking-ball {
                width: 40px;
                height: 40px;
                animation: chaseAnimation 0.9s steps(3) infinite;
            }
            .thinking-modal {
                position: fixed;
                bottom: 140px;
                left: 50%;
                transform: translateX(-50%);
                background: var(--bg-card);
                padding: 12px 24px;
                border-radius: 24px;
                border: 1px solid var(--border-color);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                z-index: 99999;
                display: flex;
                align-items: center;
                gap: 12px;
                white-space: nowrap;
            }
            .thinking-text {
                color: var(--text-primary);
                font-weight: 500;
                font-size: 15px;
            }
            .thinking-paw {
                font-size: 20px;
                margin-right: 6px;
            }
            @media (max-width: 767px) {
                .thinking-modal {
                    padding: 10px 16px;
                    gap: 8px;
                    bottom: 100px;
                    max-width: 90vw;
                    white-space: normal;
                }
                .thinking-ball {
                    width: 32px;
                    height: 32px;
                    flex-shrink: 0;
                }
                .thinking-text {
                    font-size: 13px;
                    line-height: 1.3;
                }
                .thinking-paw {
                    font-size: 16px;
                    margin-right: 4px;
                }
            }

        </style>
        """,
        unsafe_allow_html=True,
    )
