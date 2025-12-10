"""
Mobile Responsive CSS Overrides

ADDITIVE ONLY: Media queries for mobile/tablet responsiveness.
Does not modify existing desktop CSS (1024px+).

Based on mattgpt-mobile-mockup.jsx design spec.

BREAKPOINTS:
- Mobile: <768px (optimize for iPhone SE 375px)
- Tablet: 768-1023px
- Desktop: 1024px+ (existing, unchanged)
"""


def get_mobile_css() -> str:
    """
    Mobile-first responsive CSS using media queries.
    Matches values from mattgpt-mobile-mockup.jsx.

    RESPONSIVE VALUES:
    | Element              | Mobile   | Tablet | Desktop |
    |----------------------|----------|--------|---------|
    | Header avatar        | 48px     | 64px   | 64px    |
    | Chat avatar          | 40px     | 60px   | 60px    |
    | Chat padding         | 14px     | 18px   | 24px    |
    | Grids                | 1-col    | 2-col  | 3-col   |
    | "How Agy Searches"   | Icon only| Full   | Full    |
    | Navbar               | Stacked  | Row    | Row     |
    | Status bar           | Short    | Full   | Full    |
    """
    return """
        <style>
        /* ============================================================================
           MOBILE RESPONSIVE OVERRIDES (<768px)
           ============================================================================ */

        @media (max-width: 767px) {
            /* ========================================
               HEADER - LANDING & CONVERSATION
               ======================================== */

            /* Header Avatar: 48px (mobile) */
            .header-agy-avatar {
                width: 48px !important;
                height: 48px !important;
                border: 2px solid white !important;
            }

            /* Main avatar (landing view hero) */
            .main-avatar img {
                width: 64px !important;
                height: 64px !important;
            }

            /* Header layout - stack vertically on mobile */
            .ask-header {
                flex-direction: column !important;
                text-align: center !important;
                padding: 16px !important;
                gap: 12px !important;
            }

            .header-content {
                flex-direction: column !important;
                text-align: center !important;
                gap: 12px !important;
            }

            .header-text h1 {
                font-size: 20px !important;
                margin: 8px 0 4px 0 !important;
            }

            .header-text p {
                font-size: 13px !important;
            }

            /* "How Agy Searches" button - Icon only on mobile */
            .how-it-works-btn,
            button[key="toggle_how_agy"] {
                padding: 8px 12px !important;
                font-size: 13px !important;
                min-width: 44px !important;
                height: 44px !important;
            }

            /* Hide text, show icon only */
            button[key="toggle_how_agy"] p {
                font-size: 0 !important;
            }

            button[key="toggle_how_agy"]::before {
                content: "🔍" !important;
                font-size: 18px !important;
            }

            /* ========================================
               STATUS BAR - SHORT VERSION
               ======================================== */

            .status-bar {
                padding: 8px 12px !important;
                gap: 12px !important;
                font-size: 11px !important;
            }

            /* Hide verbose status items on mobile */
            .status-item span {
                font-size: 11px !important;
            }

            /* Show short version: "130+ stories • Search active" */
            .status-item:nth-child(1)::after {
                content: " • " !important;
            }

            .status-item:nth-child(2),
            .status-item:nth-child(3) {
                display: none !important;
            }

            /* ========================================
               LANDING VIEW - MOBILE
               ======================================== */

            /* Main intro section */
            .main-intro-section {
                padding: 24px 16px 16px !important;
            }

            /* White card container */
            .st-key-intro_section {
                margin: 80px auto 0 !important;
                padding: 16px !important;
                border-radius: 16px !important;
            }

            /* Typography */
            .welcome-title {
                font-size: 20px !important;
                margin: 16px 0 8px !important;
            }

            .intro-text-primary {
                font-size: 15px !important;
                margin-bottom: 12px !important;
                padding: 0 8px !important;
            }

            .intro-text-secondary {
                font-size: 14px !important;
                margin-bottom: 24px !important;
                padding: 0 8px !important;
            }

            .suggested-title {
                font-size: 12px !important;
                padding: 0 16px !important;
            }

            /* ========================================
               SUGGESTION BUTTONS - 1 COLUMN GRID
               ======================================== */

            /* Override 2×3 grid to single column */
            div[data-testid="stHorizontalBlock"]:has(button[key^="suggested_"]) {
                grid-template-columns: 1fr !important;
                grid-template-rows: repeat(6, auto) !important;
                width: calc(100% - 32px) !important;
                max-width: calc(100% - 32px) !important;
                margin: 0 auto 24px !important;
                gap: 8px !important;
            }

            /* Reset grid positions for single column */
            .st-key-suggested_0 { grid-row: 1 !important; grid-column: 1 !important; }
            .st-key-suggested_1 { grid-row: 2 !important; grid-column: 1 !important; }
            .st-key-suggested_2 { grid-row: 3 !important; grid-column: 1 !important; }
            .st-key-suggested_3 { grid-row: 4 !important; grid-column: 1 !important; }
            .st-key-suggested_4 { grid-row: 5 !important; grid-column: 1 !important; }
            .st-key-suggested_5 { grid-row: 6 !important; grid-column: 1 !important; }

            /* Buttons full width */
            button[key^="suggested_"] {
                padding: 10px 12px !important;
                font-size: 13px !important;
                width: 100% !important;
            }

            button[key^="suggested_"] p {
                font-size: 13px !important;
            }

            /* ========================================
               INPUT FORM - MOBILE
               ======================================== */

            /* Input container */
            .landing-input-container {
                padding: 0 16px !important;
                margin: 24px auto 0 !important;
            }

            [data-testid="stHorizontalBlock"]:has(.st-key-landing_input) {
                flex-direction: column !important;
                gap: 8px !important;
                padding: 0 12px !important;
            }

            /* Input field */
            div[data-testid="stTextInput"] input {
                padding: 12px 14px !important;
                font-size: 14px !important;
                border-radius: 8px !important;
            }

            /* Ask Agy button - shorter text on mobile */
            button[key="landing_ask"] {
                padding: 12px 16px !important;
                font-size: 14px !important;
                min-height: 44px !important;
                width: 100% !important;
            }

            button[key="landing_ask"]::after {
                content: "Ask Agy 🐾" !important;
            }

            /* Powered by text */
            .powered-by-text {
                font-size: 10px !important;
                margin-top: 8px !important;
            }

            /* ========================================
               CONVERSATION VIEW - MOBILE
               ======================================== */

            /* Chat avatars: 40px (mobile) */
            .stChatMessage > div.st-emotion-cache-18qnold,
            .stChatMessage > .e1ypd8m72,
            .stChatMessage > img.st-emotion-cache-p4micv,
            .stChatMessage > img.e1ypd8m74,
            .stChatMessage > img[alt="assistant avatar"] {
                width: 40px !important;
                height: 40px !important;
                min-width: 40px !important;
                min-height: 40px !important;
                font-size: 18px !important;
            }

            /* Chat message padding: 14px (mobile) */
            [data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])) {
                padding: 14px !important;
                font-size: 14px !important;
                line-height: 1.5 !important;
            }

            [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
                padding: 12px !important;
                font-size: 14px !important;
            }

            /* Chat bubbles - narrower on mobile */
            [data-testid="stChatMessage"] {
                gap: 10px !important;
                margin-bottom: 12px !important;
            }

            /* Message max width */
            .stChatMessage > div:last-child {
                max-width: 85% !important;
            }

            /* ========================================
               CHAT INPUT - MOBILE
               ======================================== */

            [data-testid="stChatInput"] {
                padding: 12px 16px !important;
            }

            /* Input textarea */
            textarea[data-testid="stChatInputTextArea"] {
                padding: 12px 14px !important;
                font-size: 14px !important;
                min-height: 44px !important;
                max-height: 44px !important;
                border-radius: 8px !important;
            }

            /* Submit button - icon only on mobile */
            button[data-testid="stChatInputSubmitButton"] {
                padding: 12px 14px !important;
                min-width: 44px !important;
                width: 44px !important;
            }

            /* Replace text with icon */
            button[data-testid="stChatInputSubmitButton"]::after {
                content: "↑" !important;
                font-size: 18px !important;
                font-weight: 700 !important;
            }

            /* Powered by text - mobile */
            .conversation-powered-by {
                font-size: 10px !important;
                bottom: 18px !important;
                max-width: 90% !important;
            }

            /* ========================================
               RELATED STORIES GRID - 1 COLUMN
               ======================================== */

            /* Single column on mobile */
            div[data-testid="stHorizontalBlock"]:has([class*="related-"]),
            div[data-testid="stColumns"]:has([class*="related-"]) {
                flex-direction: column !important;
            }

            [data-testid="stColumn"]:has([class*="related-"]) {
                width: 100% !important;
                max-width: 100% !important;
            }

            /* ========================================
               CAPABILITY CARDS - 1 COLUMN
               ======================================== */

            /* Category cards stack on mobile */
            div[data-testid="stColumns"] {
                flex-direction: column !important;
                gap: 12px !important;
            }

            [data-testid="stColumn"] {
                width: 100% !important;
                min-width: 100% !important;
            }

            /* ========================================
               MODALS - FULL SCREEN
               ======================================== */

            /* "How Agy Searches" modal - full screen on mobile */
            .modal-container,
            div[data-testid="stModal"] {
                width: 100vw !important;
                max-width: 100vw !important;
                height: 100vh !important;
                max-height: 100vh !important;
                margin: 0 !important;
                border-radius: 0 !important;
            }

            .modal-content {
                padding: 16px !important;
                max-height: calc(100vh - 80px) !important;
                overflow-y: auto !important;
            }

            /* Modal steps - stack vertically */
            .modal-steps {
                flex-direction: column !important;
                gap: 12px !important;
            }

            .modal-step {
                width: 100% !important;
            }

            /* ========================================
               NAVBAR - STACKED (IF CUSTOM)
               ======================================== */

            /* If using custom navbar */
            .custom-navbar {
                flex-direction: column !important;
                gap: 8px !important;
                padding: 8px 12px !important;
            }

            .nav-tab {
                padding: 10px 12px !important;
                text-align: center !important;
                font-size: 14px !important;
            }

            /* ========================================
               METRICS - STACK ON MOBILE
               ======================================== */

            .stApp div[data-testid="metric-container"] {
                padding: 20px 16px !important;
            }

            .stApp div[data-testid="metric-container"] [data-testid="metric-value"] {
                font-size: 28px !important;
            }

            .stApp div[data-testid="metric-container"] [data-testid="metric-label"] {
                font-size: 13px !important;
            }

            /* ========================================
               TOUCH TARGETS - MINIMUM 44PX
               ======================================== */

            button,
            a,
            [role="button"],
            input[type="checkbox"],
            input[type="radio"] {
                min-height: 44px !important;
                min-width: 44px !important;
            }

            /* ========================================
               THINKING INDICATOR - MOBILE
               ======================================== */

            .transition-indicator-bottom {
                bottom: 80px !important;
                padding: 8px 16px !important;
                font-size: 12px !important;
            }

            .thinking-ball {
                width: 36px !important;
                height: 36px !important;
            }
        }

        /* ============================================================================
           TABLET RESPONSIVE OVERRIDES (768px - 1023px)
           ============================================================================ */

        @media (min-width: 768px) and (max-width: 1023px) {
            /* ========================================
               HEADER - TABLET
               ======================================== */

            /* Header avatar: 64px (tablet/desktop) */
            .header-agy-avatar {
                width: 64px !important;
                height: 64px !important;
            }

            .main-avatar img {
                width: 96px !important;
                height: 96px !important;
            }

            /* Header stays horizontal on tablet */
            .ask-header {
                flex-direction: row !important;
                padding: 20px 24px !important;
            }

            .header-text h1 {
                font-size: 24px !important;
            }

            .header-text p {
                font-size: 14px !important;
            }

            /* "How Agy Searches" - full text on tablet */
            button[key="toggle_how_agy"] {
                padding: 10px 16px !important;
            }

            button[key="toggle_how_agy"] p {
                font-size: 13px !important;
            }

            /* ========================================
               STATUS BAR - FULL TEXT
               ======================================== */

            .status-bar {
                padding: 10px 24px !important;
                gap: 20px !important;
            }

            .status-item {
                font-size: 12px !important;
            }

            /* Show all status items on tablet */
            .status-item:nth-child(2),
            .status-item:nth-child(3) {
                display: flex !important;
            }

            /* ========================================
               GRIDS - 2 COLUMNS
               ======================================== */

            /* Suggestion buttons: 2×3 grid on tablet */
            div[data-testid="stHorizontalBlock"]:has(button[key^="suggested_"]) {
                grid-template-columns: 1fr 1fr !important;
                grid-template-rows: repeat(3, auto) !important;
                width: calc(100% - 48px) !important;
                max-width: calc(100% - 48px) !important;
            }

            /* Restore 2-column positions */
            .st-key-suggested_0 { grid-row: 1 !important; grid-column: 1 !important; }
            .st-key-suggested_1 { grid-row: 1 !important; grid-column: 2 !important; }
            .st-key-suggested_2 { grid-row: 2 !important; grid-column: 1 !important; }
            .st-key-suggested_3 { grid-row: 2 !important; grid-column: 2 !important; }
            .st-key-suggested_4 { grid-row: 3 !important; grid-column: 1 !important; }
            .st-key-suggested_5 { grid-row: 3 !important; grid-column: 2 !important; }

            button[key^="suggested_"] {
                font-size: 14px !important;
            }

            /* Related stories: 2 columns */
            div[data-testid="stColumns"]:has([class*="related-"]) > [data-testid="stColumn"] {
                flex: 0 0 48% !important;
                max-width: 48% !important;
            }

            /* Capability cards: 2 columns */
            div[data-testid="stColumns"] {
                flex-direction: row !important;
                flex-wrap: wrap !important;
            }

            [data-testid="stColumn"] {
                flex: 0 0 48% !important;
                min-width: 48% !important;
            }

            /* ========================================
               CHAT - TABLET
               ======================================== */

            /* Chat avatars: 60px (tablet/desktop) */
            .stChatMessage > div.st-emotion-cache-18qnold,
            .stChatMessage > .e1ypd8m72,
            .stChatMessage > img.st-emotion-cache-p4micv,
            .stChatMessage > img.e1ypd8m74,
            .stChatMessage > img[alt="assistant avatar"] {
                width: 60px !important;
                height: 60px !important;
                min-width: 60px !important;
                min-height: 60px !important;
            }

            /* Chat padding: 18px (tablet) */
            [data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])) {
                padding: 18px !important;
                font-size: 15px !important;
            }

            [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
                padding: 14px !important;
                font-size: 15px !important;
            }

            /* ========================================
               INPUT - TABLET
               ======================================== */

            [data-testid="stChatInput"] {
                padding: 16px 24px !important;
            }

            textarea[data-testid="stChatInputTextArea"] {
                padding: 14px 18px !important;
                font-size: 15px !important;
            }

            /* Submit button - full text on tablet */
            button[data-testid="stChatInputSubmitButton"] {
                padding: 14px 24px !important;
                width: auto !important;
            }

            button[data-testid="stChatInputSubmitButton"]::after {
                content: "Ask Agy 🐾" !important;
            }

            /* ========================================
               MODALS - TABLET
               ======================================== */

            .modal-container {
                width: 90vw !important;
                max-width: 700px !important;
                height: auto !important;
                max-height: 90vh !important;
                border-radius: 16px !important;
            }

            .modal-steps {
                flex-direction: row !important;
                gap: 16px !important;
            }

            .modal-step {
                flex: 1 !important;
            }
        }

        /* ============================================================================
           DESKTOP (1024px+) - NO CHANGES
           Existing desktop styles remain unchanged
           ============================================================================ */

        @media (min-width: 1024px) {
            /* All existing desktop CSS from styles.py and global_styles.py applies */
            /* No overrides needed - desktop is the baseline */
        }
        </style>
    """
