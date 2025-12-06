"""
Theme Utilities for MattGPT

Provides theme detection and CSS variable injection for light/dark mode support.
Uses JavaScript to detect Streamlit's actual rendered theme.
"""

import streamlit as st


def get_current_theme() -> str:
    """
    Return 'light' or 'dark' based on Streamlit theme setting.

    Uses st.get_option("theme.base") which returns the user's theme preference.
    Defaults to 'light' if not set or detection fails.
    """
    try:
        theme = st.get_option("theme.base")
        return theme if theme in ("light", "dark") else "light"
    except Exception:
        return "light"


def get_theme_variables_css() -> str:
    """
    Return CSS variable definitions that automatically switch based on theme.

    Uses JavaScript to detect Streamlit's actual theme by checking the background
    color of the body element. Adds a 'dark-theme' class to body when dark mode
    is detected, which then triggers the dark CSS variables.

    Returns:
        HTML containing <style> block and <script> for theme detection
    """
    return """
    <style>
    /* Light mode (default) */
    :root {
        /* Backgrounds */
        --bg-primary: #FFFFFF;
        --bg-card: #FFFFFF;
        --bg-surface: #F9FAFB;
        --bg-input: #FFFFFF;
        --bg-hover: #F3F4F6;

        /* Text colors */
        --text-primary: #1F2937;
        --text-secondary: #6B7280;
        --text-muted: #9CA3AF;
        --text-heading: #111827;

        /* Borders */
        --border-color: #E5E7EB;
        --border-light: #F3F4F6;
        --border-focus: #8B5CF6;

        /* Accent colors (purple theme) */
        --accent-purple: #8B5CF6;
        --accent-purple-hover: #7C3AED;
        --accent-purple-light: rgba(139, 92, 246, 0.1);
        --accent-purple-bg: rgba(139, 92, 246, 0.08);

        /* Status colors */
        --success-color: #10B981;
        --warning-color: #F59E0B;
        --error-color: #EF4444;
        --info-color: #3B82F6;

        /* Shadows */
        --shadow-color: rgba(0, 0, 0, 0.1);
        --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        --hover-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);

        /* Chat bubbles */
        --chat-ai-bg: #FFFFFF;
        --chat-user-bg: #E3F2FD;
        --chat-ai-border: #8B5CF6;

        /* Filter pills */
        --pill-bg: #F3F4F6;
        --pill-text: #374151;
        --pill-hover-bg: #E5E7EB;

        /* Table */
        --table-header-bg: #ECF0F1;
        --table-row-bg: #FFFFFF;
        --table-row-alt-bg: #F9FAFB;
        --table-row-hover-bg: #F3F4F6;

        /* Status bar */
        --status-bar-bg: #F8F9FA;
        --status-bar-border: #E0E0E0;

        /* Banner backgrounds */
        --banner-info-bg: #F3E8FF;
        --banner-info-border: #8B5CF6;
        --banner-info-text: #6B21A8;
    }

    /* Dark mode - applied when body has 'dark-theme' class */
    body.dark-theme {
        /* Backgrounds */
        --bg-primary: #0E1117;
        --bg-card: #1E1E2E;
        --bg-surface: #262633;
        --bg-input: #2D2D3D;
        --bg-hover: #363647;

        /* Text colors */
        --text-primary: #E5E7EB;
        --text-secondary: #9CA3AF;
        --text-muted: #6B7280;
        --text-heading: #F3F4F6;

        /* Borders */
        --border-color: #374151;
        --border-light: #4B5563;
        --border-focus: #8B5CF6;

        /* Accent colors (purple theme) */
        --accent-purple: #8B5CF6;
        --accent-purple-hover: #7C3AED;
        --accent-purple-light: rgba(139, 92, 246, 0.2);
        --accent-purple-bg: rgba(139, 92, 246, 0.15);

        /* Status colors */
        --success-color: #10B981;
        --warning-color: #F59E0B;
        --error-color: #EF4444;
        --info-color: #3B82F6;

        /* Shadows */
        --shadow-color: rgba(0, 0, 0, 0.3);
        --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        --hover-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);

        /* Chat bubbles */
        --chat-ai-bg: #1E1E2E;
        --chat-user-bg: #2D3748;
        --chat-ai-border: #8B5CF6;

        /* Filter pills */
        --pill-bg: #374151;
        --pill-text: #E5E7EB;
        --pill-hover-bg: #4B5563;

        /* Table */
        --table-header-bg: #1E1E2E;
        --table-row-bg: #0E1117;
        --table-row-alt-bg: #1A1A24;
        --table-row-hover-bg: #262633;

        /* Status bar */
        --status-bar-bg: #1E1E2E;
        --status-bar-border: #374151;

        /* Banner backgrounds */
        --banner-info-bg: rgba(139, 92, 246, 0.15);
        --banner-info-border: #8B5CF6;
        --banner-info-text: #C4B5FD;
    }
    </style>
    """


def get_streamlit_overrides_css() -> str:
    """
    Return CSS overrides for Streamlit native elements.

    These styles target Streamlit's internal components that don't inherit
    CSS variables by default. Dark mode specific styles use body.dark-theme
    scoping to match the JS-detected theme.

    Returns:
        A <style> block with Streamlit element overrides
    """
    return """
    <style>
        /* DataFrames and tables */
        [data-testid="stDataFrame"] {
            background: var(--bg-card) !important;
        }

        [data-testid="stDataFrame"] th {
            background: var(--table-header-bg) !important;
            color: var(--text-primary) !important;
        }

        [data-testid="stDataFrame"] td {
            background: var(--table-row-bg) !important;
            color: var(--text-primary) !important;
        }

        /* Select boxes */
        .stSelectbox > div > div {
            background: var(--bg-input) !important;
            color: var(--text-primary) !important;
            border-color: var(--border-color) !important;
        }

        .stSelectbox [data-baseweb="select"] {
            background: var(--bg-input) !important;
        }

        .stSelectbox [data-baseweb="select"] > div {
            background: var(--bg-input) !important;
            color: var(--text-primary) !important;
        }

        /* Multiselect */
        .stMultiSelect > div > div {
            background: var(--bg-input) !important;
            border-color: var(--border-color) !important;
        }

        .stMultiSelect [data-baseweb="select"] {
            background: var(--bg-input) !important;
        }

        /* Text inputs */
        .stTextInput input {
            background: var(--bg-input) !important;
            color: var(--text-primary) !important;
            border-color: var(--border-color) !important;
        }

        .stTextInput input:focus {
            border-color: var(--border-focus) !important;
        }

        .stTextInput input::placeholder {
            color: var(--text-muted) !important;
        }

        /* Text areas */
        .stTextArea textarea {
            background: var(--bg-input) !important;
            color: var(--text-primary) !important;
            border-color: var(--border-color) !important;
        }

        /* Chat input */
        [data-testid="stChatInput"] {
            background: var(--bg-card) !important;
            border-color: var(--border-color) !important;
        }

        [data-testid="stChatInput"] textarea {
            background: var(--bg-input) !important;
            color: var(--text-primary) !important;
        }

        /* Chat messages */
        [data-testid="stChatMessage"] {
            background: var(--chat-ai-bg) !important;
        }

        /* Expanders */
        .streamlit-expanderHeader {
            background: var(--bg-surface) !important;
            color: var(--text-primary) !important;
        }

        .streamlit-expanderContent {
            background: var(--bg-card) !important;
            border-color: var(--border-color) !important;
        }

        /* Containers with borders */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--bg-card) !important;
            border-color: var(--border-color) !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--bg-surface) !important;
        }

        .stTabs [data-baseweb="tab"] {
            color: var(--text-secondary) !important;
        }

        .stTabs [aria-selected="true"] {
            color: var(--text-primary) !important;
        }

        /* Dark mode specific overrides - scoped to body.dark-theme */
        body.dark-theme [data-baseweb="popover"] {
            background: var(--bg-card) !important;
        }

        body.dark-theme [data-baseweb="menu"] {
            background: var(--bg-card) !important;
        }

        body.dark-theme [data-baseweb="menu"] li {
            background: var(--bg-card) !important;
            color: var(--text-primary) !important;
        }

        body.dark-theme [data-baseweb="menu"] li:hover {
            background: var(--bg-hover) !important;
        }

        /* Form borders in dark mode need more contrast */
        body.dark-theme .stSelectbox > div > div,
        body.dark-theme .stMultiSelect > div > div,
        body.dark-theme .stTextInput > div > div {
            border-color: var(--border-light) !important;
        }

        /* AgGrid styling (works in both modes via CSS variables) */
        .ag-theme-streamlit {
            --ag-background-color: var(--bg-card) !important;
            --ag-header-background-color: var(--table-header-bg) !important;
            --ag-row-hover-color: var(--table-row-hover-bg) !important;
            --ag-foreground-color: var(--text-primary) !important;
        }

        .ag-theme-streamlit .ag-header {
            background: var(--table-header-bg) !important;
        }

        .ag-theme-streamlit .ag-row {
            background: var(--table-row-bg) !important;
        }

        .ag-theme-streamlit .ag-row:hover {
            background: var(--table-row-hover-bg) !important;
        }

        .ag-theme-streamlit .ag-cell {
            color: var(--text-primary) !important;
        }
    </style>
    """


def inject_theme_css():
    """
    Convenience function to inject all theme CSS at once.

    Call this at the top of your main app after page config.
    Injects CSS variables via markdown, and JS detection via components.html.
    """
    st.markdown(get_theme_variables_css(), unsafe_allow_html=True)
    st.markdown(get_streamlit_overrides_css(), unsafe_allow_html=True)

    # JS must go through components.html to actually execute
    theme_detection_js = """
    <script>
    (function() {
        function detectTheme() {
            var bodyBg = window.parent.document.body.style.backgroundColor ||
                         window.parent.getComputedStyle(window.parent.document.body).backgroundColor;

            var isDark = bodyBg === 'rgb(14, 17, 23)' ||
                         bodyBg === 'rgb(17, 20, 24)';

            if (isDark) {
                window.parent.document.body.classList.add('dark-theme');
            } else if (bodyBg === 'rgb(255, 255, 255)') {
                window.parent.document.body.classList.remove('dark-theme');
            }
        }

        // Poll until theme is detected
        var attempts = 0;
        var pollInterval = setInterval(function() {
            detectTheme();
            attempts++;
            if (attempts >= 50) clearInterval(pollInterval);
        }, 100);

        // Watch for changes
        var observer = new MutationObserver(detectTheme);
        observer.observe(window.parent.document.body, {
            attributes: true,
            attributeFilter: ['style']
        });
    })();
    </script>
    """
    st.components.v1.html(theme_detection_js, height=0)
