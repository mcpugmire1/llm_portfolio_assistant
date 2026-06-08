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
            div[data-testid="stHorizontalBlock"]:not(:has([class*="st-key-topnav_"])):not(:has([data-testid="stButtonGroup"])):not(:has(.st-key-landing_input)) {
                flex-direction: column !important;
                gap: 0 !important;
            }
            div[data-testid="stHorizontalBlock"]:not(:has([class*="st-key-topnav_"])):not(:has([data-testid="stButtonGroup"])):not(:has(.st-key-landing_input)) > div[data-testid="stColumn"] {
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
            .conversation-agy-avatar {
                width: 64px !important;
                height: 64px !important;
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
        .hib-runtime-wrapper::before { content: ''; position: absolute; left: 15px; top: 32px; bottom: 32px; width: 2px; background: var(--border-color); z-index: 0; }
        .hib-runtime-step { display: flex; gap: 16px; align-items: flex-start; padding-bottom: 16px; position: relative; z-index: 1; }
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
        .hib-block { border: 0.5px solid var(--border-color); border-radius: 10px; padding: 14px 16px; margin-top: 16px; max-width: 900px; margin-left: auto; margin-right: auto; }
        .hib-godeeper-lead { font-size: 12px; color: var(--text-secondary); margin: 4px 0 10px; }
        .hib-godeeper-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .hib-godeeper-card { border: 0.5px solid var(--border-color); border-radius: 10px; padding: 14px 16px; }
        .hib-godeeper-top { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
        .hib-godeeper-top svg { color: var(--text-primary); flex-shrink: 0; }
        .hib-godeeper-ttl { font-size: 13px; font-weight: 500; color: var(--text-primary); }
        .hib-godeeper-desc { font-size: 11px; color: var(--text-secondary); line-height: 1.5; margin: 0 0 8px; }
        .hib-godeeper-link { font-size: 11px; color: var(--accent-purple); font-weight: 500; display: inline-flex; align-items: center; gap: 4px; text-decoration: none; }
        .hib-godeeper-link:hover { text-decoration: underline; }
        .hib-cta-block { padding: 14px 16px; background: var(--bg-surface); border-radius: 10px; border-left: 2px solid #7e5fd4; margin-top: 16px; max-width: 900px; margin-left: auto; margin-right: auto; }
        .hib-cta-h { font-size: 14px; font-weight: 500; color: var(--text-primary); margin: 0 0 6px; }
        .hib-cta-sub { font-size: 12px; color: var(--text-secondary); margin: 0 0 10px; line-height: 1.5; }
        .hib-cta-prompts { display: flex; flex-direction: column; gap: 6px; }
        .hib-cta-prompt { background: var(--bg-card, #fff); border: 0.5px solid rgba(120, 80, 220, 0.3); border-radius: 8px; padding: 9px 12px; font-size: 11px; color: #6d4cc4; display: flex; align-items: center; justify-content: space-between; cursor: pointer; transition: background 0.15s ease; user-select: none; }
        .hib-cta-prompt:hover { background: var(--accent-purple-bg); }

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
}

.about-header-content {
    display: flex;
    align-items: center;
    gap: 24px;
    max-width: 1200px;
    margin: 0;
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
    padding: 32px;
    margin-bottom: 24px;
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
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
    gap: 12px;
    margin-top: 16px;
}

@media (max-width: 768px) {
    .tech-grid { grid-template-columns: repeat(2, 1fr); }
}

.tech-item {
    background: var(--bg-surface, #f8f9fa);
    border: 2px solid var(--border-color, #e0e0e0);
    border-radius: 8px;
    padding: 16px 12px;
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
    gap: 24px;
    margin: 24px 0;
    align-items: center;
}

@media (max-width: 768px) {
    .flow-grid { grid-template-columns: repeat(2, 1fr); }
}

.flow-step {
    background: var(--bg-surface, #f8f9fa);
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 8px;
    padding: 16px 12px;
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
    gap: 24px;
    max-width: 900px;
    margin: 0 auto;
}

@media (max-width: 768px) {
    .details-grid { grid-template-columns: 1fr; }
}

.detail-card {
    background: var(--bg-card, white);
    border: 2px solid var(--border-color, #e0e0e0);
    border-radius: 12px;
    padding: 24px;
    transition: all 0.2s ease;
}

.detail-card:hover {
    border-color: var(--accent-purple, #8B5CF6);
}

.detail-card h4 {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-heading, #2c3e50);
    margin: 0 0 16px 0;
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
    padding: 8px 0;
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
 * how_i_built.py and other pages) are left untouched.
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
    margin-bottom: 4px;
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
        padding: 20px 16px 29px 16px !important;
        min-height: auto !important;
        margin-top: 60px !important;  /* clear 60px fixed mobile nav */
    }

    .about-header-content {
        flex-direction: row !important;
        text-align: left !important;
        gap: 12px !important;
        align-items: flex-start !important;
    }

    .about-header-content img {
        width: 64px !important;
        height: 64px !important;
    }

    .about-header-text h1 {
        font-size: 22px !important;
    }

    .about-header-text p {
        font-size: 12px !important;
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
        font-size: 16px !important;
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
        grid-template-columns: 1fr !important;
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

        </style>
        """,
        unsafe_allow_html=True,
    )
