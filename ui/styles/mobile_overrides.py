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
    return """<style>
        /* ============================================================================
           MOBILE RESPONSIVE OVERRIDES (<768px)
           ============================================================================ */

        @media (max-width: 767px) {
            /* ========================================
               CRITICAL: Push content below fixed header
               Mobile header is 56px fixed at top
               ======================================== */

            .stApp > header + div,
            .main .block-container,
            section[data-testid="stSidebar"] + div > div {
                padding-top: 56px !important;
            }

            /* CRITICAL: Kill Streamlit's massive container padding */
            div[data-testid="stMainBlockContainer"] {
                padding: 1rem 1rem 2rem 1rem !important;
            }

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
                margin: 16px auto 0 !important;
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

            /* Replace text with icon */cc
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

            /* ========================================
               HOME PAGE - HERO SECTION
               ======================================== */

            /* Hero gradient wrapper */
            .hero-gradient-wrapper {
                margin-top: 0 !important;
            }

            .hero-content {
                padding: 32px 20px !important;
            }

            /* Logo image container */
            .hero-content > div:first-child,
            .hero-content div[style*="justify-content: center"][style*="margin-bottom"] {
                margin-bottom: 20px !important;
            }

            /* Logo image - target by structure */
            .hero-content > div:first-child img,
            .hero-content div img[alt*="MattGPT"],
            .hero-content img[src*="MattGPT"] {
                max-width: 280px !important;
                width: 100% !important;
            }

            /* Hero greeting text - target div with emoji */
            .hero-content > div:nth-child(2),
            .hero-content div[style*="font-size: 22px"],
            .hero-content div:has(span:first-child):not(:has(a)) {
                font-size: 18px !important;
            }

            /* Hero title - target h1 with maximum specificity */
            .hero-gradient-wrapper .hero-content h1[id][style],
            .hero-gradient-wrapper .hero-content div[data-testid="stHeadingWithActionElements"] h1[id],
            .hero-content h1,
            .hero-content h1[style] {
                font-size: 28px !important;
                margin-bottom: 12px !important;
                line-height: 1.2 !important;
            }

            /* Hero paragraphs - target all p tags */
            .hero-content p,
            .hero-content p[style] {
                font-size: 15px !important;
                line-height: 1.5 !important;
                margin-bottom: 16px !important;
                padding: 0 12px !important;
            }

            /* Hero button container - last div with links */
            .hero-content > div:last-child,
            .hero-content div[style*="display: flex"][style*="gap: 16px"] {
                flex-direction: column !important;
                gap: 12px !important;
                padding: 0 20px !important;
            }

            /* Hero buttons */
            .hero-btn {
                width: 100% !important;
                max-width: 100% !important;
                padding: 14px 24px !important;
                font-size: 15px !important;
            }

            /* ========================================
               HOME PAGE - STATS BAR
               ======================================== */

            /* Stats bar - already has media query in hero.py at 480px */
            /* Inherits: grid-template-columns: 1fr at 480px */

            .stats-bar {
                margin-top: -8px !important;
                margin-bottom: 20px !important;
            }

            .stat {
                padding: 16px 12px !important;
            }

            .stat-number {
                font-size: 32px !important;
            }

            .stat-label {
                font-size: 13px !important;
            }

            /* ========================================
               HOME PAGE - CATEGORY CARDS
               ======================================== */

            /* Reduce Streamlit's default vertical gaps on home page */
            [data-testid="stVerticalBlock"] {
                gap: 0.5rem !important;
            }

            /* Section title - compact */
            .section-header {
                margin: 0 !important;
                padding: 0 !important;
            }
            .section-header h2 {
                font-size: 18px !important;
                margin: 8px 0 8px 0 !important;
                white-space: nowrap !important;
            }
            /* Kill Streamlit container padding around section header */
            .stElementContainer:has(.section-header) {
                margin: 0 !important;
                padding: 0 !important;
            }
            .stMarkdown:has(.section-header) {
                margin: 0 !important;
                padding: 0 !important;
            }
            [data-testid="stMarkdownContainer"]:has(.section-header) {
                margin: 0 !important;
                padding: 0 !important;
            }

            /* Streamlit columns become single column automatically */
            /* Target the industry cards (purple gradient) */
            div[data-testid="column"]:has(a#btn-banking),
            div[data-testid="column"]:has(a#btn-cross-industry),
            div[data-testid="column"]:has(a#btn-product),
            div[data-testid="column"]:has(a#btn-modernization),
            div[data-testid="column"]:has(a#btn-experience),
            div[data-testid="column"]:has(a#btn-talent) {
                margin-bottom: 16px !important;
            }

            /* Purple gradient industry cards - use structural selectors */
            /* Target cards in 2-column layout that contain specific buttons */
            div[data-testid="column"]:has(a#btn-banking) > div,
            div[data-testid="column"]:has(a#btn-cross-industry) > div {
                padding: 24px 20px !important;
            }

            /* Card emoji icons */
            div[data-testid="column"]:has(a#btn-banking) > div > div:first-child,
            div[data-testid="column"]:has(a#btn-cross-industry) > div > div:first-child {
                font-size: 40px !important;
                margin-bottom: 12px !important;
            }

            /* Card titles */
            div[data-testid="column"]:has(a#btn-banking) h3,
            div[data-testid="column"]:has(a#btn-cross-industry) h3 {
                font-size: 20px !important;
                margin-bottom: 8px !important;
            }

            /* Card descriptions */
            div[data-testid="column"]:has(a#btn-banking) > div > div:nth-child(4),
            div[data-testid="column"]:has(a#btn-cross-industry) > div > div:nth-child(4) {
                font-size: 14px !important;
                margin-bottom: 12px !important;
            }

            /* Capability cards */
            .capability-card {
                padding: 24px !important;
                height: auto !important;
                min-height: 280px !important;
            }

            .capability-card h3 {
                font-size: 18px !important;
            }

            .capability-card .description {
                font-size: 14px !important;
            }

            .capability-card .hints {
                font-size: 13px !important;
            }

            /* ========================================
               EXPLORE STORIES PAGE
               ======================================== */

            /* Hero section - wireframe: 24px 16px padding */
            .explore-hero,
            div[style*="gradient"][style*="padding: 32px"] {
                padding: 24px 16px !important;
            }

            .explore-hero h1,
            div[style*="gradient"] h1 {
                font-size: 24px !important;
                margin-bottom: 8px !important;
            }

            .explore-hero p,
            div[style*="gradient"] p {
                font-size: 14px !important;
                opacity: 0.9 !important;
            }

            /* ========================================
               EXPLORE STORIES - COMPACT FILTER LAYOUT
               Goal: 3 rows max
               1. Search input (full width)
               2. Industry | Capability (side by side)
               3. Advanced | Reset (side by side)
               ======================================== */

            /* Container padding - tight */
            div[data-testid="stContainer"] {
                padding: 8px 12px !important;
            }

            /* HIDE search form submit button - Enter key works */
            .stFormSubmitButton,
            div[data-testid="stFormSubmitButton"] {
                display: none !important;
            }

            /* HIDE the spacer div in form */
            div[data-testid="stForm"] div[style*="height: 23px"] {
                display: none !important;
            }

            /* HIDE labels on mobile - placeholders are enough */
            div[data-testid="stContainer"] label[data-testid="stWidgetLabel"] {
                display: none !important;
            }

            /* FORCE horizontal blocks to stay horizontal */
            div[data-testid="stContainer"] [data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                gap: 8px !important;
            }

            /* FORCE columns to flex equally */
            div[data-testid="stContainer"] [data-testid="stColumn"] {
                flex: 1 1 0% !important;
                min-width: 0 !important;
                width: auto !important;
                max-width: none !important;
            }

            /* Compact inputs */
            div[data-testid="stContainer"] .stTextInput input {
                padding: 8px 12px !important;
                font-size: 14px !important;
                min-height: 38px !important;
            }

            /* Compact dropdowns */
            div[data-testid="stContainer"] .stSelectbox > div > div {
                padding: 6px 8px !important;
                font-size: 13px !important;
                min-height: 38px !important;
            }

            /* Compact buttons */
            div[data-testid="stContainer"] .stButton button {
                padding: 6px 10px !important;
                font-size: 12px !important;
                min-height: 32px !important;
            }

            /* Results header row */
            [data-testid="stSegmentedControl"] {
                justify-content: flex-end !important;
            }

            [data-testid="stSegmentedControl"] button {
                padding: 6px 12px !important;
                font-size: 13px !important;
            }

            /* ========================================
               TABLE VIEW - MOBILE
               ======================================== */

            /* AgGrid container - horizontal scroll wrapper */
            .ag-root-wrapper {
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch !important;
            }

            /* Ensure the grid content can scroll */
            .ag-body-horizontal-scroll-viewport {
                overflow-x: auto !important;
            }

            /* Table minimum width to force scroll - wider for readability */
            .ag-header,
            .ag-body-viewport {
                min-width: 600px !important;
            }

            /* Title column - needs more space */
            .ag-header-cell[col-id="Title"],
            .ag-cell[col-id="Title"] {
                min-width: 200px !important;
            }

            /* Client column */
            .ag-header-cell[col-id="Client"],
            .ag-cell[col-id="Client"] {
                min-width: 100px !important;
            }

            /* Hide Domain column on mobile - target by field name */
            .ag-header-cell[col-id="Domain"],
            .ag-cell[col-id="Domain"] {
                display: none !important;
            }

            /* Reduce row height on mobile */
            .ag-row {
                min-height: 48px !important;
            }

            /* Table cell padding - more compact */
            .ag-cell {
                padding: 6px 10px !important;
                font-size: 13px !important;
                line-height: 1.3 !important;
            }

            /* Table header - smaller */
            .ag-header-cell {
                padding: 8px 10px !important;
                font-size: 11px !important;
            }

            /* Title column - don't truncate too much */
            .ag-cell[col-id="Title"] {
                white-space: normal !important;
                line-height: 1.4 !important;
            }

            /* Client badge smaller */
            .client-badge {
                padding: 2px 8px !important;
                font-size: 11px !important;
            }

            /* Reduce table height on mobile */
            div[data-testid="stAgGrid"] {
                max-height: 400px !important;
            }

            /* ========================================
               CARDS VIEW - MOBILE
               ======================================== */

            /* Cards grid - single column */
            .story-cards-grid {
                grid-template-columns: 1fr !important;
                padding: 16px !important;
                gap: 16px !important;
            }

            /* Story card - wireframe: 20px padding, full width */
            .fixed-height-card {
                padding: 20px !important;
                height: auto !important;
                min-height: 280px !important;
                margin: 0 !important;
            }

            /* Card title */
            .card-title,
            .fixed-height-card h3 {
                font-size: 16px !important;
                line-height: 1.4 !important;
                margin-bottom: 8px !important;
            }

            /* Card client badge */
            .card-client-badge {
                font-size: 11px !important;
                padding: 3px 8px !important;
            }

            /* Card description */
            .card-desc {
                font-size: 14px !important;
                -webkit-line-clamp: 4 !important;
            }

            /* Card footer */
            .card-footer {
                flex-direction: column !important;
                align-items: flex-start !important;
                gap: 8px !important;
            }

            .card-role {
                font-size: 12px !important;
            }

            .card-domain-tag {
                font-size: 11px !important;
            }

            /* View details button - full width */
            .card-btn-view-details {
                width: 100% !important;
                text-align: center !important;
                padding: 12px 16px !important;
                font-size: 14px !important;
            }

            /* Hidden card buttons */
            [class*="st-key-card_btn_"] {
                position: absolute !important;
                left: -9999px !important;
                height: 0 !important;
                overflow: hidden !important;
            }

            /* ========================================
               PAGINATION - MOBILE
               ======================================== */

            .pagination {
                flex-wrap: wrap !important;
                gap: 6px !important;
                padding: 16px 12px !important;
            }

            .pagination button {
                padding: 8px 10px !important;
                font-size: 12px !important;
                min-width: 36px !important;
            }

            .pagination .page-info {
                width: 100% !important;
                text-align: center !important;
                order: -1 !important;
                margin-bottom: 8px !important;
            }

            /* ========================================
               FILTER CHIPS - MOBILE
               ======================================== */

            .active-chip-row {
                flex-wrap: wrap !important;
                gap: 8px !important;
                padding: 12px 16px !important;
            }

            .active-chip-row button {
                font-size: 12px !important;
                padding: 6px 10px !important;
            }

            /* ========================================
               STORY DETAIL PANE - MOBILE
               ======================================== */

            /* Full width on mobile, no sidebar */
            .story-detail-pane,
            div[data-testid="stExpander"] {
                width: 100% !important;
                margin: 16px 0 !important;
            }

            .story-detail-pane h2 {
                font-size: 20px !important;
            }

            .story-detail-pane h3 {
                font-size: 16px !important;
            }

            .story-detail-pane p,
            .story-detail-pane li {
                font-size: 14px !important;
                line-height: 1.6 !important;
            }

            /* STAR sections - stack */
            .star-section {
                padding: 16px !important;
                margin-bottom: 12px !important;
            }

            /* Technologies pills - wrap */
            .tech-pills {
                flex-wrap: wrap !important;
                gap: 6px !important;
            }

            .tech-pill {
                font-size: 12px !important;
                padding: 4px 10px !important;
            }

            /* Ask Agy button - full width */
            [class*="st-key-ask_from_detail"] button {
                width: 100% !important;
                padding: 14px 20px !important;
            }

            /* ========================================
               ABOUT MATT PAGE
               ======================================== */

            /* About header section - using actual class names */
            .about-header {
                padding: 32px 20px !important;
            }

            .about-header-content img {
                width: 80px !important;
                height: 80px !important;
            }

            .about-header-text h1 {
                font-size: 28px !important;
                margin: 16px 0 8px !important;
            }

            .about-header-text p {
                font-size: 15px !important;
                line-height: 1.5 !important;
            }

            /* Stats bar - using actual class names from about_matt.py */
            .stat-card {
                padding: 20px 16px !important;
            }

            .stat-card .stat-number {
                font-size: 32px !important;
            }

            .stat-card .stat-label {
                font-size: 13px !important;
            }

            /* Timeline - using actual class names */
            .timeline {
                gap: 16px !important;
            }

            .timeline-item {
                padding: 20px 16px !important;
                margin-bottom: 16px !important;
            }

            .timeline-year {
                font-size: 13px !important;
                margin-bottom: 8px !important;
            }

            .timeline-title {
                font-size: 18px !important;
                margin-bottom: 4px !important;
            }

            .timeline-company {
                font-size: 14px !important;
                margin-bottom: 8px !important;
            }

            .timeline-desc {
                font-size: 14px !important;
                line-height: 1.6 !important;
            }

            /* Section titles */
            .section-title {
                font-size: 22px !important;
                margin-bottom: 12px !important;
            }

            .section-subtitle {
                font-size: 14px !important;
                margin-bottom: 16px !important;
            }

            /* Tech grid - already has media query at 768px */
            .tech-grid {
                gap: 12px !important;
                padding: 0 8px !important;
            }

            .tech-item {
                padding: 12px !important;
                font-size: 13px !important;
            }

            /* Competencies */
            .competencies-grid {
                gap: 8px !important;
            }

            .competency-pill {
                padding: 10px 16px !important;
                font-size: 13px !important;
            }

            /* Deep dive section */
            .deep-dive-section {
                padding: 24px 16px !important;
            }

            .deep-dive-section h2 {
                font-size: 22px !important;
            }

            .deep-dive-section h3 {
                font-size: 18px !important;
            }

            .deep-dive-section p,
            .deep-dive-section li {
                font-size: 14px !important;
                line-height: 1.6 !important;
            }

            /* ========================================
               FOOTER - ALL PAGES
               ======================================== */

            .footer-container {
                padding: 24px 16px !important;
            }

            .footer-container p {
                font-size: 13px !important;
            }

            .footer-links {
                flex-direction: column !important;
                gap: 12px !important;
            }

            .footer-links a {
                font-size: 14px !important;
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
               EXPLORE STORIES - TABLET
               ======================================== */

            /* Note: Tablet layout handled by Streamlit's default behavior */

            /* Table - show Domain column on tablet */
            .ag-header-cell[col-id="Domain"],
            .ag-cell[col-id="Domain"] {
                display: table-cell !important;
            }

            /* Hide swipe hint on tablet (already hidden via inline media query, but ensure) */
            .table-swipe-hint {
                display: none !important;
            }

            /* Reset table height on tablet */
            div[data-testid="stAgGrid"] {
                max-height: none !important;
            }

            /* Cards - 2 columns on tablet */
            .story-cards-grid {
                grid-template-columns: repeat(2, 1fr) !important;
            }

            /* Card footer - row layout on tablet */
            .card-footer {
                flex-direction: row !important;
                align-items: center !important;
            }

            /* View details button - auto width on tablet */
            .card-btn-view-details {
                width: auto !important;
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
           LANDING PAGES (Banking & Cross-Industry) - MOBILE
           ============================================================================ */

        /* Mobile: 320px - 767px */
        @media (max-width: 767px) {
            /* Landing page header - stack vertically */
            .conversation-header {
                padding: 20px 16px !important;
                min-height: auto !important;
                margin: 0 !important;
            }

                # .conversation-header-content {
                #     flex-direction: row !important;
                #     align-items: flex-start !important;
                #     text-align: left !important;
                #     gap: 12px !important;
                # }

            .conversation-agy-avatar {
                width: 64px !important;
                height: 64px !important;
                border: 3px solid white !important;
            }

            .conversation-header-text h1 {
                font-size: 1.5rem !important;
                line-height: 1.3 !important;
            }

            .conversation-header-text p {
                font-size: 0.95rem !important;
                line-height: 1.5 !important;
            }

            /* Stats bar - single column on very small screens */
            .stats-bar {
                grid-template-columns: repeat(3, 1fr) !important;
                gap: 0 !important;
                padding: 12px 0 !important;
            }

            .stat {
                padding: 8px 4px !important;
            }

            .stat-number {
                font-size: 24px !important;
            }

            .stat-label {
                font-size: 10px !important;
            }

            /* Client pills - scrollable row */
            .client-pills {
                flex-wrap: nowrap !important;
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch !important;
                padding-bottom: 8px !important;
                gap: 8px !important;
                margin-bottom: 24px !important;
            }

            .client-pill {
                flex-shrink: 0 !important;
                padding: 6px 12px !important;
                font-size: 12px !important;
            }

            /* Section headers */
            .section-header {
                font-size: 18px !important;
                margin-top: 16px !important;
                margin-bottom: 12px !important;
            }

            .subtitle {
                font-size: 13px !important;
                margin-bottom: 16px !important;
            }

            /* Capability cards - adjust spacing */
            .capability-card {
                padding: 16px !important;
                margin-bottom: 12px !important;
            }

            .card-icon {
                font-size: 24px !important;
                margin-bottom: 8px !important;
            }

            .card-title {
                font-size: 15px !important;
            }

            .card-count {
                font-size: 12px !important;
            }

            .card-desc {
                font-size: 12px !important;
                margin-bottom: 10px !important;
            }

            .card-btn-outline {
                padding: 8px 14px !important;
                font-size: 12px !important;
            }

            /* CTA section */
            .cta-section {
                padding: 24px 16px !important;
                margin: 24px 0 !important;
            }

            .cta-heading {
                font-size: 20px !important;
            }

            .cta-subtext {
                font-size: 14px !important;
            }

            .card-btn-primary {
                padding: 12px 24px !important;
                font-size: 14px !important;
            }
        }

        /* Very small screens - stack stats */
        @media (max-width: 380px) {
            .stats-bar {
                grid-template-columns: 1fr !important;
            }

            .stat {
                border-right: none !important;
                border-bottom: 1px solid var(--border-color) !important;
                padding: 12px 0 !important;
            }

            .stat:last-child {
                border-bottom: none !important;
            }

            .stat-number {
                font-size: 28px !important;
            }

            .stat-label {
                font-size: 12px !important;
            }
        }

        /* Tablet: 768px - 1023px */
        @media (min-width: 768px) and (max-width: 1023px) {
            .conversation-header {
                padding: 24px !important;
            }

            .conversation-agy-avatar {
                width: 80px !important;
                height: 80px !important;
            }

            .conversation-header-text h1 {
                font-size: 1.75rem !important;
            }

            .capability-card {
                padding: 18px !important;
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
