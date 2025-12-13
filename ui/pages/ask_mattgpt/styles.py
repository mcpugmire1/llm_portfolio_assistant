"""
Ask MattGPT Styles Module

Centralized CSS styles for Ask MattGPT landing and conversation views.
Extracted from inline styles to improve maintainability.
"""

"""
Ask MattGPT Styles Module

Centralized CSS styles for Ask MattGPT landing and conversation views.
Extracted from inline styles to improve maintainability.
"""


def get_landing_css() -> str:
    """
    CSS styles for Ask MattGPT landing page.

    Includes:
    - Purple header with Agy avatar
    - Status bar styling
    - Welcome/intro section
    - Suggestion chip buttons (2x3 grid)
    - Input form styling
    - Loading animations
    """
    return """
        <style>
        /* ============================================================================
           LANDING PAGE STYLES
           ============================================================================ */

        # /* Purple header - pull up to eliminate white space */
        # .ask-header {
        #     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        #     padding: 30px;
        #     margin-top: -50px !important;
        #     color: white;
        #     display: flex;
        #     justify-content: space-between;
        #     align-items: center;
        # }

        # .header-content {
        #     display: flex;
        #     align-items: center;
        #     gap: 24px;
        # }

        .header-agy-avatar {
            flex-shrink: 0;
            width: 120px !important;
            height: 120px !important;
            border-radius: 50% !important;
            border: 4px solid white !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        }

        /* Dark mode halo effect for header avatar */
        [data-theme="dark"] .header-agy-avatar {
            filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
        }

        .header-text h1 {
            font-size: 32px;
            margin: 0 0 8px 0;
            color: white;
        }

        .header-text p {
            font-size: 16px;
            margin: 0;
            opacity: 0.95;
        }

        .how-it-works-btn {
            padding: 12px 24px;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            color: white;
            font-weight: 600;
            font-size: 15px;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
            flex-shrink: 0;
        }

        .how-it-works-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            border-color: rgba(255, 255, 255, 0.5);
            transform: translateY(-2px);
        }

        # /* Status bar - constrained to content width */
        # .status-bar {
        #     display: flex !important;
        #     flex-wrap: nowrap !important;
        #     gap: 24px !important;
        #     justify-content: center !important;
        #     padding: 12px 30px !important;
        #     background: var(--status-bar-bg) !important;
        #     border-bottom: 1px solid var(--status-bar-border) !important;
        #     margin-top: -15px !important;
        #     margin: 0 !important;
        #     overflow-x: auto !important;
        # }

        .status-item {
            display: flex !important;
            align-items: center !important;
            gap: 6px !important;
            font-size: 13px !important;
            color: var(--text-secondary) !important;
            white-space: nowrap !important;
            flex-shrink: 0 !important;
        }

        .status-item span {
            white-space: nowrap !important;
        }

        .status-value {
            font-weight: 600;
            color: var(--text-primary);
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: #10B981;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        /* MAIN INTRO SECTION */
        .main-intro-section {
            background: transparent;
            border-radius: 0;
            max-width: 100%;
            width: 100%;
            margin: 0;
            padding: 48px 32px 24px;
            text-align: center;
            margin-top: 5px !important;
        }

        [data-testid="stLayoutWrapper"]:has(.st-key-intro_section) {
            margin-top: 20px !important;
        }

        /* THE WHITE CARD - wraps everything */
        .st-key-intro_section {
            max-width: 900px !important;
            margin: 40px auto 0 !important;
            background: var(--bg-card) !important;
            border-radius: 24px !important;
            box-shadow: var(--card-shadow) !important;
            overflow: hidden !important;
            border: 1px solid var(--border-color) !important;

            margin-top: 140px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            margin-bottom: 0 !important;

            /* ADD THIS PADDING TO CREATE THE 10% LEFT/RIGHT SPACE */
            padding-left: 1% !important;
            padding-right: 1% !important;
            padding-bottom: 28px !important;
        }

        .main-avatar {
            text-align: center;
        }

        .main-avatar img {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

       /* Dark mode halo effect for main hero avatar */
        [data-theme="dark"] .main-avatar img,
        body.dark-theme .main-avatar img {
            filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
        }

        .welcome-title {
            font-size: 28px;
            color: var(--text-heading);
            margin: 24px 0 12px;
            text-align: center;
        }

        .intro-text-primary {
            font-size: 18px;
            color: var(--text-primary);
            line-height: 1.7;
            font-weight: 500;
            margin-bottom: 20px;
            max-width: 650px;
            margin-left: auto !important;
            margin-right: auto !important;
            text-align: center !important;
        }

        .intro-text-secondary {
            font-size: 17px;
            color: var(--text-secondary);
            line-height: 1.6;
            max-width: 650px;
            margin: 0 auto 48px !important;
            text-align: center !important;
        }

        .suggested-title {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            margin-bottom: 12px;
            text-align: center;
            padding: 0 32px;
        }

        /* BUTTON CONTAINER - Grid layout (inside white card) */
       div[data-testid="stHorizontalBlock"]:has(button[key^="suggested_"]) {
            display: grid !important;
            grid-template-columns: repeat(2, 1fr) !important; /* Keep columns flexible */
            grid-template-rows: repeat(3, auto) !important;
            gap: 8px !important;

            /* === CORE FIX: Use calc() to force a narrow, centered container === */
            /* This makes the grid content narrower and centered by forcing 32px margins (64px total). */
            width: calc(100% - 64px) !important;
            max-width: calc(100% - 64px) !important;
            margin: 0 auto 48px !important; /* Centers the new narrower block */

            padding: 0 !important;
            background: transparent !important;
            border-radius: 0 !important;
            box-shadow: none !important;
        }
        /* STREAMLIT COLUMN OVERRIDE (CRITICAL - Flexbox Centering) */
        div[data-testid="stHorizontalBlock"]:has(button[key^="suggested_"]) > div[data-testid="column"] > div {
            display: flex !important;
            justify-content: center !important; /* Center the button horizontally */
            width: 100% !important; /* Maintain full width of the cell */
        }

        /* Streamlit Element Container Cleanup */
        div[data-testid="stHorizontalBlock"]:has(button[key^="suggested_"]) > div[data-testid="column"] {
            display: contents !important; /* KEEPING YOUR GRID SETUP */
        }

       div[data-testid="stHorizontalBlock"]:has(button[key^="suggested_"]) .stElementContainer {
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;

            /* === NEW EXTREME FIX === */
            width: 90% !important;
            float: right !important; /* Float it to one side */
            margin-right: 5% !important; /* Force margin on the floating side */
        }

        /* Force grid row positions - column 1 renders first (0,2,4), then column 2 (1,3,5) */
        .st-key-suggested_0 { grid-row: 1 !important; grid-column: 1 !important; }
        .st-key-suggested_2 { grid-row: 2 !important; grid-column: 1 !important; }
        .st-key-suggested_4 { grid-row: 3 !important; grid-column: 1 !important; }
        .st-key-suggested_1 { grid-row: 1 !important; grid-column: 2 !important; }
        .st-key-suggested_3 { grid-row: 2 !important; grid-column: 2 !important; }
        .st-key-suggested_5 { grid-row: 3 !important; grid-column: 2 !important; }

        /* Suggested question buttons - match wireframe .example-q */
        button[key^="suggested_"] {
            background: var(--bg-surface) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 6px !important;
            padding: 10px 14px !important;
            text-align: left !important;
            transition: all 0.2s ease !important;
            min-height: auto !important;
            max-height: none !important;
            height: auto !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            gap: 8px !important;
            box-shadow: none !important;

            width: 100% !important;

            /* Remove any margin overrides */
            margin-left: unset !important;
            margin-right: unset !important;
        }

        button[key^="suggested_"]:hover {
            background: var(--bg-hover) !important;
            transform: translateY(-1px) !important;
        }

        button[key^="suggested_"] p {
            font-size: 14px !important;
            font-weight: 400 !important;
            font-style: italic !important;
            color: var(--text-primary) !important;
            line-height: 1.4 !important;
            margin: 0 !important;
            text-align: left !important;
        }

        button[key^="suggested_"] div {
            text-align: left !important;
            justify-content: flex-start !important;
            width: 100% !important;
        }

        /* Landing input container */
        .landing-input-container {
            max-width: 700px !important;
            width: 100% !important;
            margin: 40px auto 0px !important;
            padding: 0 30px !important;
        }

        /* Target input row via key */
        [data-testid="stHorizontalBlock"]:has(.st-key-landing_input) {
            max-width: 800px !important;
            margin: 24px auto 0 !important;
            gap: 12px !important;
            padding: 0 20px !important;
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
        }

        /* Input column expands, button column shrinks to fit */
        [data-testid="stHorizontalBlock"]:has(.st-key-landing_input) > [data-testid="stColumn"]:first-child {
            flex: 1 1 auto !important;
            min-width: 0 !important;
        }
        [data-testid="stHorizontalBlock"]:has(.st-key-landing_input) > [data-testid="stColumn"]:last-child {
            flex: 0 0 auto !important;
            width: auto !important;
            min-width: auto !important;
        }

        /* Powered by text */
        .powered-by-text {
            text-align: center !important;
            font-size: 11px !important;
            color: var(--text-muted) !important;
            margin-top: 2px !important;
            margin-bottom: 20px !important;
            padding: 0 !important;
        }

        /* Input styling */
        div[data-testid="stTextInput"],
        div[data-testid="stTextInput"] > div {
            overflow: visible !important;
        }

        div[data-testid="stTextInput"] input {
            width: 100% !important;
            padding: 20px 24px !important;
            font-size: 17px !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 16px !important;
            transition: all 0.2s ease !important;
            background: var(--bg-input) !important;
            color: var(--text-primary) !important;
            font-family: inherit !important;
            overflow: visible !important;
        }

        div[data-testid="stTextInput"] input:focus {
            outline: none !important;
            border-color: var(--accent-purple) !important;
            background: var(--bg-card) !important;
            box-shadow: 0 0 0 3px var(--accent-purple-light) !important;
        }

        div[data-testid="stTextInput"] input::placeholder {
            color: var(--text-muted) !important;
        }

        /* KILL RED BORDER - Hide wrapper borders */
        div[data-testid="stTextInputRootElement"],
        div[data-baseweb="input"],
        div[data-baseweb="base-input"] {
            border: none !important;
            background: transparent !important;
        }

        .st-key-landing_input div[data-baseweb="input"],
        .st-key-landing_input div[data-baseweb="input"]:hover,
        .st-key-landing_input div[data-baseweb="input"]:focus-within {
            border: none !important;
            border-color: transparent !important;
        }

        /* Kill Streamlit's atomic border classes */
        .st-key-landing_input .st-bz,
        .st-key-landing_input .st-c0,
        .st-key-landing_input .st-c1,
        .st-key-landing_input .st-c2 {
            border-left-color: transparent !important;
            border-right-color: transparent !important;
            border-top-color: transparent !important;
            border-bottom-color: transparent !important;
        }

        /* ASK AGY BUTTON - Purple background with WHITE text */
        button[key="landing_ask"],
        .st-key-landing_ask button,
        .st-key-landing_ask button[data-testid="stBaseButton-primary"],
        .st-key-landing_ask button[data-testid="stBaseButton-secondary"] {
            background: #8B5CF6 !important;
            background-color: #8B5CF6 !important;
            border: none !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 12px 32px !important;
            border-radius: 12px !important;
            font-size: 16px !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
            height: auto !important;
            min-height: 48px !important;
            white-space: nowrap !important;
            min-width: fit-content !important;
        }

        button[key="landing_ask"]:hover:not(:disabled),
        .st-key-landing_ask button:hover:not(:disabled) {
            background: #7C3AED !important;
            color: white !important;
            transform: scale(1.02) !important;
        }

        button[key="landing_ask"]:disabled,
        .st-key-landing_ask button:disabled {
            background: #8B5CF6 !important;
            background-color: #8B5CF6 !important;
            border: none !important;
            opacity: 1 !important;
            cursor: not-allowed !important;
            color: white !important;
            filter: brightness(0.85) !important;
        }

        button[key="landing_ask"]:disabled p,
        .st-key-landing_ask button:disabled p {
            color: white !important;
            opacity: 1 !important;
        }

        button[kind="primary"]:disabled {
            background: #8B5CF6 !important;
            background-color: #8B5CF6 !important;
            border: none !important;
            color: white !important;
        }

        button[key="landing_ask"] p,
        .st-key-landing_ask button p {
            color: white !important;
            font-weight: 600 !important;
            margin: 0 !important;
        }

        button[key="landing_ask"] *,
        .st-key-landing_ask button * {
            color: white !important;
        }

        button[key="landing_ask"]:disabled *,
        .st-key-landing_ask button:disabled * {
            color: white !important;
        }

        button[key="landing_ask"] div,
        .st-key-landing_ask button div {
            color: white !important;
        }

        /* Animations */
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-4px); }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .welcome-title {
            animation: fadeInUp 0.6s ease-out;
        }

        .intro-text-primary {
            animation: fadeInUp 0.6s ease-out 0.2s;
            animation-fill-mode: both;
        }

        .intro-text-secondary {
            animation: fadeInUp 0.6s ease-out 0.4s;
            animation-fill-mode: both;
        }

        /* Hide trigger button */
        button[key="how_works_landing"] {
            display: none !important;
        }

        div:has(> button[key="how_works_landing"]) {
            display: none !important;
        }

        /* HOW AGY SEARCHES BUTTON - IN HEADER */
        button[key="toggle_how_agy"] {
            position: absolute !important;
            top: 170px !important;
            right: 40px !important;
            background: rgba(255, 255, 255, 0.2) !important;
            backdrop-filter: blur(10px) !important;
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 12px !important;
            color: white !important;
            padding: 12px 24px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            z-index: 10 !important;
        }

        button[key="toggle_how_agy"]:hover {
            background: rgba(255, 255, 255, 0.3) !important;
            border-color: rgba(255, 255, 255, 0.5) !important;
        }

        button[key="toggle_how_agy"] p {
            color: white !important;
            font-weight: 600 !important;
        }
        /* ============================================================================
           MOBILE RESPONSIVE (<768px)
           ============================================================================ */
        @media (max-width: 767px) {
            /* KILL Streamlit container padding */
            div[data-testid="stMainBlockContainer"] {
                padding: 1rem 1rem 2rem 1rem !important;
            }

            /* KILL extra margins on intro section container */
            .st-key-intro_section,
            [data-testid="stVerticalBlock"]:has(.main-intro-section) {
                margin: 0 !important;
                padding: 0 !important;
            }

            /* KILL empty placeholder taking space */
            .stElementContainer:has(.stEmpty),
            [data-testid="stVerticalBlock"] > div:has(.stEmpty) {
                height: 0 !important;
                min-height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
            }

            /* Main intro section - compact */
            .main-intro-section {
                padding: 16px 16px 12px !important;
            }

            .main-avatar img {
                width: 60px !important;
                height: 60px !important;
            }

            .welcome-title {
                font-size: 18px !important;
                margin: 12px 0 6px !important;
            }

            .intro-text-primary {
                font-size: 13px !important;
                line-height: 1.4 !important;
                margin-bottom: 8px !important;
            }

            .intro-text-secondary {
                font-size: 12px !important;
                line-height: 1.3 !important;
                margin-bottom: 16px !important;
            }

            /* "TRY ASKING" title */
            .suggested-title {
                font-size: 10px !important;
                margin-bottom: 6px !important;
                padding: 0 16px !important;
            }

            /* Suggestion chips container - COMPACT */
            div[data-testid="stHorizontalBlock"]:has(button[key^="suggested_"]) {
                grid-template-columns: 1fr !important;
                width: calc(100% - 24px) !important;
                max-width: calc(100% - 24px) !important;
                gap: 4px !important;
                margin-bottom: 12px !important;
            }

            /* Suggestion buttons - MUCH more compact */
            button[key^="suggested_"],
            [class*="st-key-suggested_"] button,
            .stButton button[key^="suggested_"] {
                padding: 8px 12px !important;
                min-height: 36px !important;
                border-radius: 4px !important;
            }

            button[key^="suggested_"] p,
            [class*="st-key-suggested_"] button p,
            .stButton button p {
                font-size: 13px !important;
                line-height: 1.3 !important;
            }

            /* Form buttons (suggestion chips) - force smaller */
            div[data-testid="stForm"] button {
                padding: 8px 12px !important;
                min-height: auto !important;
            }

            div[data-testid="stForm"] button p {
                font-size: 13px !important;
                line-height: 1.3 !important;
            }

            /* KILL gaps in vertical blocks */
            [data-testid="stVerticalBlock"] {
                gap: 4px !important;
            }

            /* Specifically kill gap after input row */
            [data-testid="stHorizontalBlock"]:has(.st-key-landing_input) + *,
            [data-testid="stHorizontalBlock"]:has(.st-key-landing_ask) + * {
                margin-top: 0 !important;
            }

            /* Input container - tighter margins */
            .landing-input-container {
                margin: 8px auto 0 !important;
                padding: 0 16px !important;
            }

            [data-testid="stHorizontalBlock"]:has(.st-key-landing_input) {
                margin: 8px auto 0 !important;
                padding: 0 16px !important;
            }

            /* FORCE input + button to stay on same line */
            /* Target the HorizontalBlock as flex row */
            [data-testid="stHorizontalBlock"]:has(.st-key-landing_input) {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                gap: 8px !important;
                align-items: center !important;
            }

            /* Make columns flex properly */
            [data-testid="stHorizontalBlock"]:has(.st-key-landing_input) > .stColumn {
                display: block !important;
                width: auto !important;
                flex: unset !important;
            }

            /* Input column - fill remaining space */
            .stColumn:has(.st-key-landing_input) {
                flex: 1 1 0% !important;
                min-width: 0 !important;
            }

            /* Button column - shrink to content */
            .stColumn:has(.st-key-landing_ask) {
                flex: 0 0 auto !important;
            }

            /* Make stTextInput inline */
            .st-key-landing_input .stTextInput,
            [data-testid="stTextInput"]:has(#text_input_1) {
                display: block !important;
                width: 100% !important;
            }

            /* Make stButton inline */
            .st-key-landing_ask .stButton,
            .stColumn:has(.st-key-landing_ask) .stButton {
                display: inline-flex !important;
                width: auto !important;
            }

            /* Kill excessive vertical spacing throughout */
            .main-intro-section + div,
            .main-intro-section ~ [data-testid="stVerticalBlock"],
            [data-testid="stVerticalBlock"]:has([data-testid="stForm"]) {
                margin-top: 0 !important;
                padding-top: 0 !important;
            }

            /* Input field */
            .st-key-landing_input input,
            .st-key-landing_input textarea,
            [data-testid="stTextInput"] input {
                font-size: 13px !important;
                padding: 10px 12px !important;
            }

            /* Input placeholder */
            .st-key-landing_input input::placeholder,
            [data-testid="stTextInput"] input::placeholder {
                font-size: 13px !important;
            }

            /* Ask Agy button - compact, inline with input */
            .st-key-landing_submit button,
            .st-key-landing_ask button {
                padding: 10px 14px !important;
                font-size: 13px !important;
                margin-bottom: 0 !important;
                white-space: nowrap !important;
            }

            .st-key-landing_ask button p {
                font-size: 13px !important;
            }

            /* Status bar - compact single line */
            .status-bar {
                padding: 6px 12px !important;
                gap: 6px !important;
                flex-wrap: nowrap !important;
                justify-content: center !important;
            }

            .status-bar span {
                font-size: 10px !important;
                white-space: nowrap !important;
            }

            /* Powered by text - tight under input */
            .powered-by,
            .powered-by-text {
                font-size: 10px !important;
                margin: 0 !important;
                padding-top: 8px !important;
                text-align: center !important;
            }

            /* Kill gaps around powered by container */
            [data-testid="stMarkdown"]:has(.powered-by-text),
            [data-testid="stElementContainer"]:has(.powered-by-text) {
                margin: 0 !important;
                padding: 0 !important;
            }

            /* Kill gap after landing input container */
            .landing-input-container + [data-testid="stMarkdown"],
            .landing-input-container ~ [data-testid="stElementContainer"] {
                margin-top: 0 !important;
            }

            /* KILL empty element containers */
            .stElementContainer:empty,
            [data-testid="stVerticalBlock"] > div:empty {
                display: none !important;
            }

            /* Footer CTA section */
            .footer-cta {
                padding: 24px 16px !important;
            }

            .footer-cta h2 {
                font-size: 22px !important;
            }
        }

        </style>
    """


def get_loading_animation_css() -> str:
    """Loading indicator animation CSS (used in both views)."""
    return """
        <style>
        @keyframes chaseAnimation {
            0% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_1.png'); }
            33.33% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_2.png'); }
            66.66% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_3.png'); }
            100% { content: url('https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/thinking_indicator/chase_48px_1.png'); }
        }
        .thinking-ball {
            width: 48px;
            height: 48px;
            animation: chaseAnimation 0.9s steps(3) infinite;
        }
        </style>
    """


def get_conversation_css() -> str:
    """
    CSS styles for Ask MattGPT conversation view.

    Includes:
    - Conversation header
    - Status bar
    - Chat message bubbles
    - Input styling
    - Action buttons
    - Thinking indicators
    """
    return """
        <style>
        /* ============================================================================
           CONVERSATION VIEW STYLES
           ============================================================================ */

        .status-item {
            display: flex !important;
            align-items: center !important;
            gap: 6px !important;
            font-size: 13px !important;
            color: var(--text-secondary) !important;
            white-space: nowrap !important;
        }

        .status-value {
            font-weight: 600;
            color: var(--text-primary);
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: #10B981;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .header-content {
            display: flex;
            align-items: center;
            gap: 24px;
        }

        .header-agy-avatar {
            flex-shrink: 0;
            width: 120px !important;
            height: 120px !important;
            border-radius: 50% !important;
            border: 4px solid white !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        }

        /* Dark mode halo effect for header avatar */
        [data-theme="dark"] .header-agy-avatar {
            filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
        }

        [class*="st-key-how_works_top"] button[data-testid="stBaseButton-secondary"] {
            background: rgba(102, 126, 234, 0.1) !important;
            border: 2px solid #667eea !important;
            color: #667eea !important;
            border-radius: 6px !important;
            padding: 8px 16px !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stLayoutWrapper"]:has(.stChatMessage) {
            margin-top: 20px !important;
        }

        [class*="st-key-how_works_top"] button:hover {
            background: rgba(102, 126, 234, 0.2) !important;
            border-color: #764ba2 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
        }

        [class*="st-key-how_works_top"] button p {
            color: #667eea !important;
            font-weight: 600 !important;
            margin: 0 !important;
        }


        /* ASK AGY ABOUT THIS BUTTON - Keep purple on all states */
        [class*="st-key-ask_from_detail"] button,
        [class*="st-key-ask_from_detail"] button[kind="primary"],
        [class*="st-key-ask_from_detail"] button[data-testid="stBaseButton-primary"] {
            background: #8B5CF6 !important;
            background-color: #8B5CF6 !important;
            border: none !important;
            color: white !important;
        }

        [class*="st-key-ask_from_detail"] button:hover {
            background: #7C3AED !important;
            background-color: #7C3AED !important;
        }

        [class*="st-key-ask_from_detail"] button:active,
        [class*="st-key-ask_from_detail"] button:focus,
        [class*="st-key-ask_from_detail"] button:focus-visible {
            background: #8B5CF6 !important;
            background-color: #8B5CF6 !important;
            border-color: #8B5CF6 !important;
            outline: none !important;
            box-shadow: none !important;
        }

        [class*="st-key-ask_from_detail"] button p {
            color: white !important;
        }

        /* Chat messages - AI */
        [data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])) {
            background: var(--chat-ai-bg) !important;
            border-radius: 16px !important;
            padding: 24px !important;
            border-left: 4px solid var(--chat-ai-border) !important;
            color: var(--text-primary) !important;
        }

      /* Chat messages - User */
        [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
            background: var(--chat-user-bg) !important;
            border-radius: 8px !important;
            padding: 16px !important;
            color: var(--text-primary) !important;
        }

       /* =============================================
        CHAT AVATARS - User and Agy
        ============================================= */

        /* User avatar - div with emoji */
        .stChatMessage > div.st-emotion-cache-18qnold,
        .stChatMessage > .e1ypd8m72 {
            width: 60px !important;
            height: 60px !important;
            min-width: 40px !important;
            min-height: 40px !important;
            font-size: 20px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            border-radius: 50% !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
        }

        /* Agy avatar - img element */
        .stChatMessage > img.st-emotion-cache-p4micv,
        .stChatMessage > img.e1ypd8m74,
        .stChatMessage > img[alt="assistant avatar"] {
            width: 60px !important;
            height: 60px !important;
            min-width: 40px !important;
            min-height: 40px !important;
            border-radius: 50% !important;
            background: var(--bg-surface, #262633) !important;
            border: 2px solid var(--accent-purple, #8B5CF6) !important;
            box-shadow: 0 2px 8px rgba(139, 92, 246, 0.2) !important;
            padding: 0 !important;
            object-fit: cover !important;
        }


        /* Dark mode glow on Agy */
        [data-theme="dark"] .stChatMessage > img[alt="assistant avatar"],
        body.dark-theme .stChatMessage > img[alt="assistant avatar"] {
            filter: drop-shadow(0 0 8px rgba(139, 92, 246, 0.4));
        }

        /* Input Area - Complete Wireframe Match */
        [data-testid="stChatInput"] {
            padding: 20px 30px !important;
            background: var(--bg-card) !important;
            border-top: 2px solid var(--border-color) !important;
            position: sticky !important;
            bottom: 0 !important;
            z-index: 100 !important;
            border-radius: 0 !important;
            overflow: hidden !important;
        }

        /* Input Container - Exact Wireframe Structure */
        [data-testid="stChatInput"] > div:first-child {
            display: flex !important;
            gap: 12px !important;
            max-width: 900px !important;
            margin: 0 auto !important;
            align-items: center !important;
            border-radius: 0 !important;
        }

        /* Input Field - Maximum Specificity for Textarea */
        textarea[data-testid="stChatInputTextArea"],
        [data-testid="stChatInput"] textarea[class*="st-"],
        [data-testid="stChatInput"] textarea {
            flex: 1 !important;
            padding: 14px 18px !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
            font-size: 15px !important;
            font-family: inherit !important;
            background: var(--bg-input) !important;
            color: var(--text-primary) !important;
            transition: all 0.2s ease !important;
            resize: none !important;
            min-height: 48px !important;
            max-height: 48px !important;
            appearance: none !important;
            -webkit-appearance: none !important;
            -moz-appearance: none !important;
        }

        /* Textarea Focus - Maximum Specificity */
        textarea[data-testid="stChatInputTextArea"]:focus,
        [data-testid="stChatInput"] textarea:focus {
            outline: none !important;
            border-color: var(--accent-purple) !important;
            box-shadow: 0 0 0 3px var(--accent-purple-light) !important;
            border-radius: 8px !important;
        }

        /* Placeholder styling */
        [data-testid="stChatInputTextArea"]::placeholder,
        [data-testid="stChatInput"] textarea::placeholder,
        [data-testid="stChatInput"] input::placeholder {
            color: var(--text-muted) !important;
            opacity: 1 !important;
        }

        /* Nuclear targeting of the exact emotion class */
        textarea.st-emotion-cache-1vdwi3c[data-testid="stChatInputTextArea"],
        textarea[data-testid="stChatInputTextArea"][class*="st-emotion-cache"] {
            border-radius: 8px !important;
            border: 2px solid var(--border-color) !important;
            padding: 14px 18px !important;
            min-height: 48px !important;
            max-height: 48px !important;
        }

        /* Force the immediate inner container to be rectangular */
        [data-testid="stChatInput"] div[class*="st-emotion-cache"] {
            border-radius: 0 !important;
        }

        /* Target the specific emotion class wrapper */
        [data-testid="stChatInput"] .st-emotion-cache-1vdwi3c,
        [data-testid="stChatInput"] .st-emotion-cache-1ydk24 {
            border-radius: 0 !important;
            border-left: none !important;
        }

        /* Target the text input wrapper containers */
        div[data-testid="stTextInput"],
        div[data-testid="stTextInput"] > div,
        div[data-testid="stTextInput"] > div > div {
            border-radius: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
        }

        /* Target the chat input's nested structure */
        [data-testid="stChatInput"] > div:first-child > div:first-child,
        [data-testid="stChatInput"] > div:first-child > div:first-child > div:first-child {
            border-radius: 0 !important;
            background: transparent !important;
            padding: 0 !important;
            border-left: none !important;
            border-color: transparent !important;
        }

        /* Also target any emotion-cache wrappers around the textarea */
        [data-testid="stChatInput"] div[class*="st-emotion-cache"]:has(textarea) {
            border-radius: 0 !important;
            background: transparent !important;
        }

        /* Targets the Fieldset (a common wrapper for Streamlit text inputs) */
        [data-testid="stChatInput"] fieldset,
        [data-testid="stChatInput"] legend {
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
            border-left: none !important;
        }

        /* NUCLEAR OPTION - Target EVERY div inside stChatInput */
        [data-testid="stChatInput"] div,
        [data-testid="stChatInput"] > div,
        [data-testid="stChatInput"] > div > div,
        [data-testid="stChatInput"] > div > div > div,
        [data-testid="stChatInput"] > div > div > div > div,
        [data-testid="stChatInput"] > div > div > div > div > div {
            border-left: none !important;
            border-left-width: 0 !important;
            border-left-color: transparent !important;
        }

        /* Target the parent container of textarea */
        textarea[data-testid="stChatInputTextArea"]:parent {
            border-left: none !important;
        }

        /* Button - Maximum Specificity Override */
        button[data-testid="stChatInputSubmitButton"].st-emotion-cache-1vabq37,
        button[data-testid="stChatInputSubmitButton"],
        [data-testid="stChatInput"] button[class*="st-emotion-cache"],
        [data-testid="stChatInput"] button {
            padding: 14px 28px !important;
            background: #8B5CF6 !important;
            background-color: #8B5CF6 !important;
            background-image: none !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            min-width: auto !important;
            width: auto !important;
            height: auto !important;
            min-height: auto !important;
        }

        /* Hide SVG with maximum specificity */
        button[data-testid="stChatInputSubmitButton"] svg,
        button[data-testid="stChatInputSubmitButton"] > svg,
        [data-testid="stChatInput"] button svg {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            width: 0 !important;
            height: 0 !important;
        }

        /* Add text content */
        button[data-testid="stChatInputSubmitButton"]::after {
            content: "Ask Agy 🐾" !important;
            color: white !important;
            font-size: 15px !important;
            font-weight: 600 !important;
        }

        /* Hover state with maximum specificity */
        button[data-testid="stChatInputSubmitButton"]:hover,
        button[data-testid="stChatInputSubmitButton"].st-emotion-cache-1vabq37:hover {
            background: #7C3AED !important;
            background-color: #7C3AED !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3) !important;
        }
        /* Target BaseWeb wrappers specifically */
        [data-baseweb="textarea"],
        [data-baseweb="base-input"] {
            border: none !important;
            border-left: none !important;
            outline: none !important;
            box-shadow: none !important;
            background: transparent !important;
        }

        /* Target the emotion-cache wrappers */
        .st-emotion-cache-yd4u6l,
        .st-emotion-cache-1eeryuo,
        .exaa2ht0,
        .exaa2ht1 {
            border: none !important;
            border-left: none !important;
            outline: none !important;
            box-shadow: none !important;
        }

        /* Target all those st-* utility classes that might have borders */
        [data-testid="stChatInput"] [class*="st-"] {
            border-left: none !important;
        }

        /* Re-apply border ONLY to textarea */
        [data-testid="stChatInput"] textarea[data-testid="stChatInputTextArea"] {
            border: 2px solid var(--border-color) !important;
            background: var(--bg-input) !important;
        }

        [data-testid="stChatInput"] textarea[data-testid="stChatInputTextArea"]:focus {
            border: 2px solid #8B5CF6 !important;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
        }

        [data-baseweb="textarea"],
        [data-baseweb="base-input"] {
            overflow: visible !important;
            background: transparent !important;
        }

        /* Powered by text for conversation view - fixed below chat input */
        .conversation-powered-by {
            position: fixed !important;
            bottom: 26px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            text-align: center !important;
            font-size: 12px !important;
            color: var(--text-muted) !important;
            padding: 0 !important;
            z-index: 999 !important;
        }

        /* Hide footer in conversation view */
        footer, [role="contentinfo"] {
            display: none !important;
        }

        /* Action buttons */
        .action-buttons {
            display: flex;
            gap: 8px;
            margin-top: 16px;
        }

        .action-btn {
            padding: 8px 16px;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
            color: var(--text-primary);
        }

        .action-btn:hover {
            background: var(--bg-hover);
        }

        .action-btn.helpful-active {
            background: var(--accent-purple);
            color: white;
            border-color: var(--accent-purple);
        }

        /* Thinking indicator */
        .transition-indicator-bottom {
            position: fixed;
            bottom: 140px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;
            background: var(--bg-surface) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            padding: 12px 24px;
            border-radius: 24px;
            box-shadow: var(--card-shadow) !important;
        }
        /* ========================================
        FINAL FIX: Overflow visible + kill wrapper borders
        ======================================== */

        /* Make all containers overflow visible so borders aren't clipped */
        [data-testid="stChatInput"],
        [data-testid="stChatInput"] > div,
        [data-testid="stChatInput"] > div > div,
        [data-testid="stChatInput"] > div > div > div,
        [data-baseweb="textarea"],
        [data-baseweb="base-input"],
        [data-testid="stChatInput"] div[class*="exaa2ht"] {
            overflow: visible !important;
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
        }

        /* ONLY the textarea gets border styling */
        textarea[data-testid="stChatInputTextArea"] {
            border: 2px solid var(--border-color) !important;
            border-radius: 16px !important;
            padding: 20px 24px !important;
            background: var(--bg-input) !important;
            color: var(--text-primary) !important;
        }

        textarea[data-testid="stChatInputTextArea"]:focus {
            border-color: var(--accent-purple) !important;
            box-shadow: 0 0 0 3px var(--accent-purple-light) !important;
            outline: none !important;
        }

        /* Button vertical alignment */
        button[data-testid="stChatInputSubmitButton"] {
            transform: translateY(.5px) !important;
        }

        /* ============================================================================
           MOBILE RESPONSIVE - CONVERSATION VIEW (<768px)
           ============================================================================ */
        @media (max-width: 767px) {
            /* KILL Streamlit's excessive padding */
            div[data-testid="stMainBlockContainer"] {
                padding: 0 !important;
                padding-bottom: 80px !important;
            }

            /* Status bar - compact like landing page */
            .status-bar {
                padding: 6px 12px !important;
                gap: 6px !important;
                flex-wrap: nowrap !important;
                justify-content: center !important;
                font-size: 10px !important;
            }

            .status-bar span {
                font-size: 10px !important;
                white-space: nowrap !important;
            }

            /* Chat messages - smaller avatars */
            .stChatMessage img[data-testid="chatAvatarIcon-user"],
            .stChatMessage img[data-testid="chatAvatarIcon-assistant"],
            .stChatMessage > img {
                width: 36px !important;
                height: 36px !important;
            }

            .stChatMessage {
                padding: 10px 12px !important;
                gap: 10px !important;
                margin-bottom: 8px !important;
            }

            /* Message text - readable on mobile */
            .stChatMessage [data-testid="stMarkdownContainer"] {
                font-size: 14px !important;
                line-height: 1.5 !important;
            }

            /* KILL gaps between elements */
            [data-testid="stVerticalBlock"] {
                gap: 8px !important;
            }

            /* Chat input area - fixed at bottom */
            [data-testid="stChatInput"] {
                padding: 8px 12px !important;
                position: fixed !important;
                bottom: 0 !important;
                left: 0 !important;
                right: 0 !important;
                width: 100% !important;
                box-sizing: border-box !important;
                background: var(--bg-card) !important;
                border-top: 1px solid var(--border-color) !important;
                z-index: 1000 !important;
            }

            /* Input container - horizontal with tight gap */
            [data-testid="stChatInput"] > div:first-child {
                flex-direction: row !important;
                gap: 8px !important;
                align-items: center !important;
            }

            /* Textarea - flex to fill */
            textarea[data-testid="stChatInputTextArea"] {
                flex: 1 !important;
                min-height: 40px !important;
                max-height: 40px !important;
                padding: 10px 14px !important;
                font-size: 14px !important;
                border-radius: 20px !important;
            }

            /* Ask Agy button - compact */
            button[data-testid="stChatInputSubmitButton"],
            [data-testid="stChatInput"] button {
                width: auto !important;
                padding: 10px 16px !important;
                font-size: 13px !important;
                border-radius: 20px !important;
                flex-shrink: 0 !important;
            }

            button[data-testid="stChatInputSubmitButton"]::after {
                font-size: 13px !important;
            }

            /* Powered by text - HIDE on mobile conversation view (shown on landing) */
            [data-testid="stElementContainer"]:has(.conversation-powered-by) {
                display: none !important;
            }

            /* Related projects - compact */
            .related-project-link,
            a[href*="story_id"] {
                padding: 8px 12px !important;
                font-size: 12px !important;
                margin-bottom: 6px !important;
            }

            /* Source cards - compact */
            .source-card {
                padding: 10px !important;
                margin-bottom: 8px !important;
            }

            .source-card h4 {
                font-size: 13px !important;
            }

            .source-card p {
                font-size: 11px !important;
            }

            /* RELATED PROJECTS header */
            h3:has(+ .related-project-link),
            [data-testid="stMarkdownContainer"] h3 {
                font-size: 14px !important;
                margin: 12px 0 8px 0 !important;
            }
        }

        </style>
    """
