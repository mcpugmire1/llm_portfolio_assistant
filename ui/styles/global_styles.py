"""
Global CSS Styles

Shared styles applied across all pages:
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
    if st.session_state.get("_matt_css_done"):
        return
    st.session_state["_matt_css_done"] = True

    st.markdown(
        """
        <style>
        /* ========================================
           STREAMLIT OVERRIDES
           ======================================== */

        /* Show header with transparent background to keep hamburger menu */
        header[data-testid="stHeader"] {
            background: transparent !important;
            display: block !important;
            visibility: visible !important;
        }

        /* Keep toolbar visible for hamburger menu */
        header[data-testid="stHeader"] [data-testid="stToolbar"] {
            display: flex !important;
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

        /* Remove default top padding */
        .main > div:first-child {
            padding-top: 0 !important;
        }

        /* Consistent navbar alignment across all pages */
        .stMainBlockContainer {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }

        .stMainBlockContainer > div[data-testid="stVerticalBlock"]:first-child {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }

        /* Override Streamlit's default background for bordered containers */
        /* In light mode, Streamlit uses a slightly darker shade for containers */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: transparent !important;
            border: 1px solid rgba(0, 0, 0, 0.1) !important;
        }

        /* Ensure the wrapper's parent also doesn't add background */
        div[data-testid="element-container"]:has(div[data-testid="stVerticalBlockBorderWrapper"]) {
            background: transparent !important;
        }

        /* ========================================
           METRICS STYLING
           ======================================== */

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

        /* ========================================
           BUTTONS
           ======================================== */

        .stButton > button {
            background: white !important;
            border: 2px solid white !important;
            color: #667eea !important;
            padding: 14px 28px !important;
            border-radius: 8px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            margin-top: 10px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
        }

        .stButton > button:hover {
            background: rgba(255, 255, 255, 0.95) !important;
            color: #667eea !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
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
           NAVBAR STYLING
           ======================================== */

        /* Target ALL elements in the first horizontal block (navbar area) */
        .main > div:first-child > div:first-child > div:first-child div[data-testid="stHorizontalBlock"]:first-of-type {
            background: #2c3e50 !important;
            padding: 16px 40px !important;
            margin: -1rem -1rem 1rem -1rem !important;
            border-radius: 0 !important;
        }

        /* Target columns in first horizontal block */
        .main > div:first-child > div:first-child > div:first-child div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"] {
            background: #2c3e50 !important;
        }

        /* Style first 4 buttons (navigation) */
        .main > div:first-child > div:first-child > div:first-child div[data-testid="stHorizontalBlock"]:first-of-type button {
            background: transparent !important;
            color: white !important;
            border: none !important;
            font-weight: 500 !important;
            box-shadow: none !important;
        }

        /* Hover state */
        .main > div:first-child > div:first-child > div:first-child div[data-testid="stHorizontalBlock"]:first-of-type button:hover {
            background: rgba(255, 255, 255, 0.1) !important;
            color: white !important;
        }

        /* Active/disabled state */
        .main > div:first-child > div:first-child > div:first-child div[data-testid="stHorizontalBlock"]:first-of-type button:disabled {
            background: #34495e !important;
            color: white !important;
            font-weight: 600 !important;
            opacity: 1 !important;
        }

        /* ========================================
           AGGRID TABLE STYLING
           ======================================== */

        .ag-theme-streamlit {
            background: #262626 !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
            border: 1px solid #333 !important;
            margin-top: 8px !important;
            margin-bottom: 8px !important;
        }

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

        .ag-theme-streamlit .ag-row {
            background: #262626 !important;
            border-bottom: 1px solid #333 !important;
            border-left: 3px solid transparent !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
            min-height: 70px !important;
        }

        .ag-theme-streamlit .ag-row:hover {
            background: #2d2d2d !important;
            border-left: 3px solid #667eea !important;
        }

        .ag-theme-streamlit .ag-cell {
            padding: 24px 20px !important;
            font-size: 14px !important;
            line-height: 1.6 !important;
            border-right: none !important;
        }

        /* Hide AgGrid pagination */
        .ag-theme-streamlit .ag-paging-panel {
            display: none !important;
        }

        /* ========================================
           RESPONSIVE
           ======================================== */

        @media (max-width: 768px) {
            .matt-hero h1 { font-size: 32px; }
            .matt-hero p { font-size: 18px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
