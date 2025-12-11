"""
Mobile Responsive CSS - EXPLORE STORIES ONLY

STRATEGY: Surgical, scoped CSS that won't break desktop.
- All rules inside @media (max-width: 767px)
- Uses .explore-page wrapper class for scoping
- Targets specific elements with high specificity
- NO generic selectors that could leak

================================================================================
BREAKPOINTS
================================================================================
| Breakpoint | Width         | Navigation          | Layout                    |
|------------|---------------|---------------------|---------------------------|
| Mobile     | < 768px       | Hamburger menu      | Single column             |
| Tablet     | 768-1023px    | Compact horizontal  | 2 columns                 |
| Desktop    | ≥ 1024px      | Full horizontal     | 2-3 columns               |

================================================================================
TEST DEVICES
================================================================================
- iPhone SE: 375px (smallest modern phone)
- iPhone 14/15: 390-393px
- iPhone Max: 428-430px
- iPad Mini: 768px
- iPad: 810px
- iPad Pro / Small laptop: 1024px
- Desktop: 1280px+

================================================================================
RESPONSIVE VALUES (per wireframe spec)
================================================================================
| Element              | Mobile   | Tablet | Desktop |
|----------------------|----------|--------|---------|
| Hero padding         | 24px 16px| 32px   | 2rem    |
| Hero title           | 24px     | 28px   | 2rem    |
| Hero subtitle        | 14px     | 14px   | 1.1rem  |
| Filter inputs        | stacked  | row    | row     |
| Cards grid           | 1-col    | 2-col  | 3-col   |
| Card padding         | 20px     | 24px   | 24px    |
| Card title           | 16px     | 18px   | 18px    |
| Table Domain col     | hidden   | visible| visible |
| Touch targets        | 44px min | 44px   | default |

================================================================================
WIREFRAME SPEC SUMMARY (from mobile_wireframes.html)
================================================================================
- Hero: 24px 16px padding, 24px title, 14px subtitle
- Filters: Stack vertically, full width inputs, 16px padding
- Cards: Single column, 20px padding, 16px title, 260px min-height
- Table: Horizontal scroll, hide Domain column, 550px min-width
- Pagination: Wrap, 12px font, centered
"""


def get_explore_mobile_css() -> str:
    """
    Mobile CSS for Explore Stories page ONLY.
    Import this in explore_stories.py and inject once.
    """
    return """<style>
/* ============================================================================
   EXPLORE STORIES - MOBILE RESPONSIVE (<768px)
   ============================================================================
   RULE: Every selector MUST be inside this media query.
   RULE: Use .explore-page wrapper for scoping.
   RULE: Prefer class selectors over data-testid where possible.
   ============================================================================ */

@media (max-width: 767px) {

    /* ========================================
       HERO SECTION
       Wireframe: 24px 16px padding, 24px title
       ======================================== */

    .explore-page .conversation-header {
        padding: 24px 16px !important;
        margin: 0 !important;
    }

    .explore-page .conversation-header-content {
        flex-direction: column !important;
        text-align: center !important;
        gap: 12px !important;
    }

    .explore-page .conversation-agy-avatar {
        width: 64px !important;
        height: 64px !important;
        border-width: 3px !important;
    }

    .explore-page .conversation-header-text h1 {
        font-size: 24px !important;
        margin-bottom: 4px !important;
    }

    .explore-page .conversation-header-text p {
        font-size: 14px !important;
    }

    /* ========================================
       FILTERS SECTION
       Wireframe: Stack vertically, 16px padding
       ======================================== */

    /* Filter container */
    .explore-page .stContainer,
    .explore-page div[data-testid="stContainer"] {
        padding: 16px !important;
    }

    /* Force filter columns to stack */
    .explore-page .filter-row,
    .explore-page div[data-testid="stHorizontalBlock"]:has(div[data-testid="stSelectbox"]) {
        flex-direction: column !important;
        gap: 12px !important;
    }

    /* Make each filter column full width */
    .explore-page div[data-testid="stHorizontalBlock"]:has(div[data-testid="stSelectbox"]) > div[data-testid="stColumn"] {
        flex: 1 1 100% !important;
        min-width: 100% !important;
        width: 100% !important;
    }

    /* Filter labels */
    .explore-page label[data-testid="stWidgetLabel"] {
        font-size: 13px !important;
    }

    /* Filter inputs - proper touch targets */
    .explore-page div[data-testid="stSelectbox"] > div > div,
    .explore-page div[data-testid="stMultiSelect"] > div > div,
    .explore-page div[data-testid="stTextInput"] input {
        min-height: 44px !important;
        font-size: 15px !important;
    }

    /* Search form row - keep search input + button on same row */
    .explore-page div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        align-items: flex-end !important;
        gap: 8px !important;
    }

    /* Search input - take most space */
    .explore-page div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] > div:first-child {
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }

    /* Search button - compact */
    .explore-page div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] > div:last-child {
        flex: 0 0 auto !important;
    }

    .explore-page div[data-testid="stFormSubmitButton"] button {
        padding: 8px 12px !important;
        min-width: 44px !important;
        width: 44px !important;
        height: 44px !important;
    }

    /* Button row - Advanced Filters + Reset */
    .explore-page [class*="st-key-btn_toggle_advanced"] button,
    .explore-page [class*="st-key-btn_reset_filters"] button {
        padding: 10px 14px !important;
        font-size: 13px !important;
        white-space: nowrap !important;
    }

    /* ========================================
       RESULTS HEADER
       Wireframe: justify-between, 12px 16px padding
       ======================================== */

    .explore-page .results-header {
        padding: 12px 16px !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
    }

    .explore-page .results-count {
        font-size: 14px !important;
    }

    /* View toggle (Table/Cards) - compact */
    .explore-page [data-testid="stSegmentedControl"] {
        justify-content: flex-end !important;
    }

    .explore-page [data-testid="stSegmentedControl"] button {
        padding: 6px 12px !important;
        font-size: 13px !important;
    }

    /* ========================================
       TABLE VIEW
       Wireframe: Horizontal scroll, hide Domain
       ======================================== */

    /* AgGrid container - enable horizontal scroll */
    .explore-page .ag-root-wrapper {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
    }

    /* Force minimum width for readability */
    .explore-page .ag-header,
    .explore-page .ag-body-viewport {
        min-width: 550px !important;
    }

    /* Title column - needs more space */
    .explore-page .ag-header-cell[col-id="Title"],
    .explore-page .ag-cell[col-id="Title"] {
        min-width: 180px !important;
        white-space: normal !important;
        line-height: 1.4 !important;
    }

    /* Hide Domain column on mobile */
    .explore-page .ag-header-cell[col-id="Domain"],
    .explore-page .ag-cell[col-id="Domain"] {
        display: none !important;
    }

    /* Reduce row height slightly */
    .explore-page .ag-row {
        min-height: 48px !important;
    }

    /* Cell padding - more compact */
    .explore-page .ag-cell {
        padding: 8px 10px !important;
        font-size: 13px !important;
    }

    /* Header cells - smaller */
    .explore-page .ag-header-cell {
        padding: 10px !important;
        font-size: 11px !important;
    }

    /* Client badge smaller */
    .explore-page .client-badge {
        padding: 3px 8px !important;
        font-size: 11px !important;
    }

    /* Constrain table height */
    .explore-page div[data-testid="stAgGrid"] {
        max-height: 400px !important;
    }

    /* Swipe hint for table */
    .explore-page .table-swipe-hint {
        display: block !important;
        text-align: center;
        font-size: 12px;
        color: var(--text-muted);
        padding: 8px;
    }

    /* ========================================
       CARDS VIEW
       Wireframe: Single column, 20px padding
       ======================================== */

    /* Cards grid - single column */
    .explore-page .story-cards-grid {
        grid-template-columns: 1fr !important;
        padding: 16px !important;
        gap: 16px !important;
    }

    /* Individual card */
    .explore-page .fixed-height-card {
        padding: 20px !important;
        height: auto !important;
        min-height: 260px !important;
        margin: 0 !important;
    }

    /* Card title */
    .explore-page .card-title {
        font-size: 16px !important;
        line-height: 1.4 !important;
        margin-bottom: 8px !important;
    }

    /* Card client badge */
    .explore-page .card-client-badge {
        font-size: 11px !important;
        padding: 3px 8px !important;
    }

    /* Card description */
    .explore-page .card-desc {
        font-size: 14px !important;
        -webkit-line-clamp: 3 !important;
    }

    /* Card footer - stack on mobile */
    .explore-page .card-footer {
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 8px !important;
    }

    .explore-page .card-role {
        font-size: 12px !important;
    }

    .explore-page .card-domain-tag {
        font-size: 11px !important;
    }

    /* View details button - full width */
    .explore-page .card-btn-view-details {
        width: 100% !important;
        text-align: center !important;
        padding: 12px 16px !important;
        font-size: 14px !important;
    }

    /* Hide Streamlit card buttons (already positioned off-screen) */
    .explore-page [class*="st-key-card_btn_"] {
        position: absolute !important;
        left: -9999px !important;
        height: 0 !important;
        overflow: hidden !important;
    }

    /* ========================================
       PAGINATION
       Wireframe: Wrap, smaller buttons
       ======================================== */

    .explore-page .pagination {
        flex-wrap: wrap !important;
        gap: 6px !important;
        padding: 16px 12px !important;
        justify-content: center !important;
    }

    .explore-page .pagination button {
        padding: 8px 10px !important;
        font-size: 12px !important;
        min-width: 36px !important;
    }

    .explore-page .pagination .page-info {
        width: 100% !important;
        text-align: center !important;
        order: -1 !important;
        margin-bottom: 8px !important;
        font-size: 12px !important;
    }

    /* ========================================
       FILTER CHIPS (Active filters)
       ======================================== */

    .explore-page .active-chip-row {
        flex-wrap: wrap !important;
        gap: 8px !important;
        padding: 12px 16px !important;
    }

    .explore-page .active-chip-row button {
        font-size: 12px !important;
        padding: 6px 10px !important;
    }

    /* ========================================
       STORY DETAIL PANE
       Full width on mobile
       ======================================== */

    .explore-page .story-detail-pane {
        width: 100% !important;
        margin: 16px 0 !important;
        padding: 20px 16px !important;
    }

    .explore-page .story-detail-pane h2 {
        font-size: 20px !important;
    }

    .explore-page .story-detail-pane h3 {
        font-size: 16px !important;
    }

    .explore-page .story-detail-pane p,
    .explore-page .story-detail-pane li {
        font-size: 14px !important;
        line-height: 1.6 !important;
    }

    /* STAR sections */
    .explore-page .star-section {
        padding: 16px !important;
        margin-bottom: 12px !important;
    }

    /* Technologies pills */
    .explore-page .tech-pills {
        flex-wrap: wrap !important;
        gap: 6px !important;
    }

    .explore-page .tech-pill {
        font-size: 12px !important;
        padding: 4px 10px !important;
    }

    /* Ask Agy button - full width */
    .explore-page [class*="st-key-ask_from_detail"] button {
        width: 100% !important;
        padding: 14px 20px !important;
    }

    /* ========================================
       GENERAL MOBILE FIXES
       ======================================== */

    /* All buttons - proper touch targets */
    .explore-page .stButton > button {
        min-height: 44px !important;
    }

    /* Tighter vertical spacing */
    .explore-page div[data-testid="stVerticalBlock"] > div {
        margin-bottom: 8px !important;
    }

}

/* ============================================================================
   TABLET RESPONSIVE (768px - 1023px)
   ============================================================================ */

@media (min-width: 768px) and (max-width: 1023px) {

    /* Hero - horizontal layout OK, slightly smaller */
    .explore-page .conversation-header-text h1 {
        font-size: 28px !important;
    }

    /* Filters - can stay in row on tablet */
    .explore-page div[data-testid="stHorizontalBlock"]:has(div[data-testid="stSelectbox"]) {
        flex-direction: row !important;
    }

    /* Cards - 2 columns on tablet */
    .explore-page .story-cards-grid {
        grid-template-columns: repeat(2, 1fr) !important;
    }

    /* Table - show Domain column on tablet */
    .explore-page .ag-header-cell[col-id="Domain"],
    .explore-page .ag-cell[col-id="Domain"] {
        display: table-cell !important;
    }

    /* Hide swipe hint on tablet */
    .explore-page .table-swipe-hint {
        display: none !important;
    }
}

/* ============================================================================
   DESKTOP (1024px+) - NO CHANGES
   Desktop is the baseline - all existing CSS applies unchanged
   ============================================================================ */
</style>
"""
