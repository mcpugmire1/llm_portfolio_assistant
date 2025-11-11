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

        /* Purple header - pull up to eliminate white space */
        .ask-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            margin-top: -35px !important;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header-content {
            display: flex;
            align-items: center;
            gap: 24px;
        }

        .header-agy-avatar {
            width: 64px !important;
            height: 64px !important;
            border-radius: 50% !important;
            border: 3px solid white !important;
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

        /* Status bar - constrained to content width */
        .status-bar {
            display: flex !important;
            flex-wrap: nowrap !important;
            gap: 24px !important;
            justify-content: center !important;
            padding: 12px 30px !important;
            background: #f8f9fa !important;
            border-bottom: 1px solid #e0e0e0 !important;
            margin: 0 !important;
            overflow-x: auto !important;
        }

        .status-item {
            display: flex !important;
            align-items: center !important;
            gap: 6px !important;
            font-size: 13px !important;
            color: #6B7280 !important;
            white-space: nowrap !important;
            flex-shrink: 0 !important;
        }

        .status-item span {
            white-space: nowrap !important;
        }

        .status-value {
            font-weight: 600;
            color: #2C363D;
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
            background: white;
            border-radius: 24px 24px 0 0;
            max-width: 900px;
            width: 100%;
            margin: 20px auto 0;
            padding: 48px 32px 32px;
            text-align: center;
        }

        .main-avatar {
            text-align: center;
        }

        .main-avatar img {
            width: 96px;
            height: 96px;
            border-radius: 50%;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        /* Dark mode halo effect for main hero avatar */
        [data-theme="dark"] .main-avatar img {
            filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
        }

        .welcome-title {
            font-size: 28px;
            color: #2c3e50;
            margin: 24px 0 12px;
            text-align: center;
        }

        .intro-text-primary {
            font-size: 18px;
            color: #374151;
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
            color: #6B7280;
            line-height: 1.6;
            max-width: 650px;
            margin: 0 auto 48px !important;
            text-align: center !important;
        }

        .suggested-title {
            font-size: 14px;
            font-weight: 600;
            color: #7f8c8d;
            text-transform: uppercase;
            margin-bottom: 20px;
            text-align: center;
        }

        /* BUTTON CONTAINER - Grid layout */
        div[data-testid="stHorizontalBlock"]:has(button[key^="suggested_"]) {
            display: grid !important;
            grid-template-columns: repeat(2, 1fr) !important;
            grid-template-rows: repeat(3, auto) !important;
            gap: 16px !important;
            max-width: 900px !important;
            width: 100% !important;
            margin: 0 auto !important;
            background: white !important;
            padding: 0 32px 48px !important;
            border-radius: 0 0 24px 24px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
        }

        div[data-testid="stHorizontalBlock"]:has(button[key^="suggested_"]) > div[data-testid="column"] {
            display: contents !important;
        }

        div[data-testid="stHorizontalBlock"]:has(button[key^="suggested_"]) .stElementContainer {
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Suggested question buttons */
        button[key^="suggested_"] {
            background: white !important;
            border: 2px solid #E5E7EB !important;
            border-radius: 12px !important;
            padding: 20px 24px !important;
            text-align: left !important;
            transition: all 0.2s ease !important;
            min-height: 80px !important;
            max-height: 80px !important;
            height: 80px !important;
            display: flex !important;
            align-items: start !important;
            gap: 12px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
            width: 100% !important;
            overflow: hidden !important;
        }

        button[key^="suggested_"]:hover {
            border-color: #8B5CF6 !important;
            background: #F9FAFB !important;
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.12) !important;
            transform: translateY(-2px) !important;
        }

        button[key^="suggested_"] p {
            font-size: 16px !important;
            font-weight: 600 !important;
            color: #2C363D !important;
            line-height: 1.4 !important;
            margin: 0 !important;
            text-align: left !important;
            overflow: hidden !important;
            display: -webkit-box !important;
            -webkit-line-clamp: 2 !important;
            -webkit-box-orient: vertical !important;
        }

        button[key^="suggested_"] div {
            max-height: 80px !important;
        }

        /* Landing input container */
        .landing-input-container {
            max-width: 800px !important;
            width: 100% !important;
            margin: 40px auto 0px !important;
            padding: 0 30px !important;
        }

        /* Powered by text */
        .powered-by-text {
            text-align: center !important;
            font-size: 12px !important;
            color: #95a5a6 !important;
            margin-top: -25px !important;
            margin-bottom: 0 !important;
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
            border: 2px solid #E5E7EB !important;
            border-radius: 16px !important;
            transition: all 0.2s ease !important;
            background: #FAFAFA !important;
            font-family: inherit !important;
            overflow: visible !important;
        }

        div[data-testid="stTextInput"] input:focus {
            outline: none !important;
            border-color: #8B5CF6 !important;
            background: white !important;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
        }

        div[data-testid="stTextInput"] input::placeholder {
            color: #9CA3AF !important;
        }

        /* ASK AGY BUTTON - Purple background with WHITE text */
        button[key="landing_ask"] {
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
        }

        button[key="landing_ask"]:hover:not(:disabled) {
            background: #7C3AED !important;
            color: white !important;
            transform: scale(1.02) !important;
        }

        button[key="landing_ask"]:disabled {
            background: #8B5CF6 !important;
            background-color: #8B5CF6 !important;
            border: none !important;
            opacity: 1 !important;
            cursor: not-allowed !important;
            color: white !important;
            filter: brightness(0.85) !important;
        }

        button[key="landing_ask"]:disabled p {
            color: white !important;
            opacity: 1 !important;
        }

        button[kind="primary"]:disabled {
            background: #8B5CF6 !important;
            background-color: #8B5CF6 !important;
            border: none !important;
            color: white !important;
        }

        button[key="landing_ask"] p {
            color: white !important;
            font-weight: 600 !important;
            margin: 0 !important;
        }

        button[key="landing_ask"] * {
            color: white !important;
        }

        button[key="landing_ask"]:disabled * {
            color: white !important;
        }

        button[key="landing_ask"] div {
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

        /* Status bar */
        .status-bar {
            display: flex !important;
            gap: 24px !important;
            justify-content: center !important;
            padding: 12px 30px !important;
            background: #f8f9fa !important;
            border-bottom: 1px solid #e0e0e0 !important;
        }

        .conversation-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            margin-top: -50px !important;
            color: white;
        }

        /* Chat messages - AI */
        [data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])) {
            background: white !important;
            border-radius: 16px !important;
            padding: 24px !important;
            border-left: 4px solid #8B5CF6 !important;
        }

        /* Chat messages - User */
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: #e3f2fd !important;
            border-radius: 8px !important;
            padding: 16px !important;
        }

        /* Input styling */
        textarea[data-testid="stChatInputTextArea"] {
            padding: 20px 24px !important;
            font-size: 17px !important;
            border: 2px solid #E5E7EB !important;
            border-radius: 16px !important;
        }

        button[data-testid="stChatInputSubmitButton"]::after {
            content: "Ask Agy 🐾" !important;
            color: white !important;
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
            background: #f3f4f6;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .action-btn:hover {
            background: #e5e7eb;
        }

        .action-btn.helpful-active {
            background: #8B5CF6;
            color: white;
            border-color: #8B5CF6;
        }

        /* Thinking indicator */
        .transition-indicator-bottom {
            position: fixed;
            bottom: 140px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;
            background: #F3F4F6 !important;
            color: #374151 !important;
            border: 1px solid #D1D5DB !important;
            padding: 12px 24px;
            border-radius: 24px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        }
        </style>
    """