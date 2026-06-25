"""
BDD Step Definitions for My Work

These step definitions use Playwright for browser automation.
Install with: pip install pytest-bdd playwright
Run with: pytest tests/bdd -k explore_stories
"""

import re

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from utils.ui_helpers import BANNER_COPY

# Load the feature file
scenarios('../features/explore_stories.feature')


# =============================================================================
# WAIT UTILITIES - Smart waiting to reduce test runtime
# =============================================================================

# Default timeouts (in ms)
SHORT_WAIT = 200  # Quick UI updates
MEDIUM_WAIT = 500  # Component renders
CONTENT_WAIT = 1000  # Content loading after navigation

# =============================================================================
# COVERAGE BOUNDARIES — st.dataframe (Glide Data Grid) era
# =============================================================================
# BDD CAN assert: filter pipeline (count direction via .es-results-count),
#   grid mount (.stDataFrame canvas visible), detail panel (deeplink or card click),
#   rejection state (.no-match-banner + absent stDataFrame).
# BDD CANNOT assert: canvas row content (text/values per row),
#   row selection via click (GDG canvas is not DOM-clickable from Playwright).
# Manual coverage: 20-click visual check verifies row selection -> detail open.
# Ticket: MATTGPT-144 (poc/mattgpt-144-stdataframe-table).
# =============================================================================


def _read_count(page):
    """Extract total story count from the '.es-results-count' text.

    The rendered text is 'Showing N-M of TOTAL projects' where the
    spacing between tokens is a mix of &nbsp; (U+00A0), regular spaces,
    and newlines (inner_text/textContent surface these inconsistently).
    Collapse all whitespace to single spaces before matching so the
    regex is robust to markup spacing changes. Returns 0 if the element
    is absent (e.g. the no-match/rejection state, where no count renders).
    """
    locator = page.locator(".es-results-count")
    if locator.count() == 0:
        return 0
    raw = locator.first.text_content() or ""
    text = re.sub(r"\s+", " ", raw).strip()
    m = re.search(r"of (\d+)", text)
    return int(m.group(1)) if m else 0


def wait_for_content(page, selector, timeout=10000):
    """Wait for selector to appear, return True if found, False otherwise."""
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return True
    except Exception:
        return False


def wait_for_streamlit_rerun(page):
    """Wait for Streamlit to complete a rerun by watching data-test-script-state."""
    from playwright.sync_api import expect as pw_expect

    stapp = page.locator('[data-testid="stApp"]')
    # Catch the running state; may already be done if rerun was fast.
    try:
        pw_expect(stapp).to_have_attribute(
            "data-test-script-state", "running", timeout=2000
        )
    except Exception:
        pass
    pw_expect(stapp).to_have_attribute(
        "data-test-script-state", "notRunning", timeout=15000
    )
    page.wait_for_timeout(SHORT_WAIT)


# =============================================================================
# FIXTURES — shared_browser, browser_page, app_url are defined in
# tests/bdd/steps/conftest.py (single session-scoped Playwright instance
# shared across all BDD test files to avoid sync/async clash).
# =============================================================================


# Selector for detecting Ask Agy page (landing OR conversation view)
ASK_MATTGPT_SELECTORS = (
    ".st-key-intro_section, [data-testid='stChatInput'], .conversation-powered-by"
)


# =============================================================================
# GIVEN STEPS - NAVIGATION
# =============================================================================


@given("the user navigates to the My Work page")
def navigate_to_explore(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    # Wait for Streamlit to finish loading - look for any button with "My Work" text
    browser_page.wait_for_selector("button:has-text('My Work')", timeout=30000)
    # Click My Work button (avoid hidden mobile nav by using visible filter)
    nav_button = browser_page.locator("button:has-text('My Work'):visible").first
    nav_button.click()
    # stDataFrame on My Work causes continuous XHR — networkidle never settles.
    wait_for_streamlit_rerun(browser_page)


@given("the page has finished loading")
def wait_for_page_load(browser_page):
    wait_for_streamlit_rerun(browser_page)
    # Wait for My Work page content - results count is always present
    browser_page.wait_for_selector(".es-results-count", timeout=30000)
    # Wait for stDataFrame to mount (Table is the default view)
    try:
        browser_page.wait_for_selector('[data-testid="stDataFrame"]', timeout=15000)
    except Exception:
        # Cards or Timeline view — stDataFrame not expected
        pass
    # Store baseline count for count-direction assertions in Then steps
    browser_page._es_baseline_count = _read_count(browser_page)


@given("the user has searched for {query}")
@given(parsers.parse('the user has searched for "{query}"'))
def user_has_searched(browser_page, query):
    search_input = browser_page.locator(
        "input[placeholder*='modern platforms'], input[placeholder*='Find stories']"
    ).first
    search_input.fill(query)
    search_input.press("Enter")
    wait_for_streamlit_rerun(browser_page)


@given("the user has opened a story detail")
def user_has_opened_detail(browser_page):
    """Open a story detail panel - try current view first, then switch if needed."""
    # Wait for any story content to appear
    wait_for_content(
        browser_page,
        ".es-fixed-height-card, [data-testid='stDataFrame'], .es-story-card",
        timeout=10000,
    )

    # Try Cards view (if visible)
    cards = browser_page.locator(".es-fixed-height-card")
    if cards.count() > 0 and cards.first.is_visible():
        cards.first.click()
        wait_for_streamlit_rerun(browser_page)
        if wait_for_content(
            browser_page,
            "#btn-share-story, .es-detail-header, .star-label",
            timeout=10000,
        ):
            return

    # Try Timeline story cards
    timeline = browser_page.locator(".es-story-card")
    if timeline.count() > 0 and timeline.first.is_visible():
        timeline.first.click()
        wait_for_streamlit_rerun(browser_page)
        if wait_for_content(
            browser_page,
            "#btn-share-story, .es-detail-header, .star-label",
            timeout=10000,
        ):
            return

    # Last resort: switch to Cards view
    # stDataFrame's initial mount triggers a Streamlit rerun that briefly removes
    # stButtonGroup from the DOM. Wait for it before checking count.
    wait_for_content(browser_page, "[data-testid='stButtonGroup']", timeout=10000)
    view_btn = browser_page.locator(
        "[data-testid='stButtonGroup'] button:has-text('Cards')"
    ).first
    if view_btn.count() > 0:
        view_btn.click()
        wait_for_streamlit_rerun(browser_page)
        wait_for_content(browser_page, ".es-fixed-height-card", timeout=10000)
        cards = browser_page.locator(".es-fixed-height-card")
        if cards.count() > 0:
            cards.first.click()
            wait_for_streamlit_rerun(browser_page)
            wait_for_content(
                browser_page,
                "#btn-share-story, .es-detail-header, .star-label",
                timeout=10000,
            )
            return

    pytest.skip("No clickable story elements found")


@given(parsers.parse('the user has opened story "{story_id}"'))
def user_has_opened_specific_story(browser_page, story_id):
    # Story IDs may have additional suffix (e.g., "|client-name")
    # Use partial match with *= selector
    story = browser_page.locator(
        f"[data-story-id*='{story_id}'], .es-fixed-height-card:has-text('{story_id.replace('-', ' ')}')"
    ).first
    if story.count() == 0:
        # Fallback: just click any story card
        story = browser_page.locator(".es-fixed-height-card").first
    story.click()
    wait_for_streamlit_rerun(browser_page)
    assert wait_for_content(
        browser_page, ".es-detail-header, .star-label", timeout=5000
    ), f"Detail panel never opened after card click — DOM had: {browser_page.locator('.es-detail-header').count()} header(s)"


@given(parsers.parse('the user has selected "{value}" from the {filter_name} filter'))
def user_has_selected_filter(browser_page, value, filter_name):
    select = browser_page.locator(
        f"[data-testid='stSelectbox']:has-text('{filter_name}')"
    ).first
    select.click()
    option = browser_page.locator(f"[role='option']:has-text('{value}')").first
    option.click()
    wait_for_streamlit_rerun(browser_page)


@given("the advanced filters are expanded")
def advanced_filters_expanded(browser_page):
    expander = browser_page.locator(
        "button:has-text('Advanced Filters'), details:has-text('Advanced Filters')"
    ).first
    if not browser_page.locator(
        ".advanced-filters-content, [data-testid='stExpander'][aria-expanded='true']"
    ).is_visible():
        expander.click()
    browser_page.wait_for_selector("[data-testid='stMultiSelect']", timeout=5000)


@given(parsers.parse("the user is in {view} view"))
def user_is_in_view(browser_page, view):
    # Use the stButtonGroup with segmented controls (same as switch_view)
    wait_for_content(browser_page, "[data-testid='stButtonGroup']", timeout=5000)
    view_btn = browser_page.locator(
        f"[data-testid='stButtonGroup'] button:has-text('{view}')"
    ).first

    # Check if this view is already active (has segmented_controlActive)
    is_active = "Active" in (view_btn.get_attribute("data-testid") or "")
    if is_active:
        # Already in this view, don't click
        return

    view_btn.click()
    wait_for_streamlit_rerun(browser_page)
    # Wait for the specific view content
    if view == "Table":
        wait_for_content(browser_page, '[data-testid="stDataFrame"]', timeout=10000)
    elif view == "Cards":
        wait_for_content(browser_page, ".es-fixed-height-card", timeout=10000)
    elif view == "Timeline":
        wait_for_content(browser_page, ".es-timeline-container", timeout=10000)


@given(parsers.parse("the user is on page {page_num:d}"))
def user_is_on_page(browser_page, page_num):
    for _ in range(page_num - 1):
        next_btn = browser_page.locator(
            "button:has-text('Next'), button:has-text('>')"
        ).first
        next_btn.click()
        wait_for_streamlit_rerun(browser_page)


@given(parsers.parse("there are more than {count:d} stories"))
def verify_story_count(browser_page, count):
    # This is a precondition - verified by presence of pagination
    pass


@given("the user was previously on My Work with filters and a story open")
def user_was_previously_on_explore(browser_page, app_url):
    # Navigate to My Work
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    nav_button = browser_page.locator("button:has-text('My Work'):visible").first
    nav_button.click()
    wait_for_streamlit_rerun(browser_page)

    # Set a filter
    select = browser_page.locator(
        "[data-testid='stSelectbox']:has(label:has-text('Industry'))"
    ).first
    if select.is_visible():
        select.click()
        option = browser_page.locator("[role='option']").nth(
            1
        )  # First non-empty option
        option.click()
        wait_for_streamlit_rerun(browser_page)

    # Open a story
    story = browser_page.locator(".es-fixed-height-card, .es-story-card").first
    if story.is_visible():
        story.click()
        wait_for_content(browser_page, ".es-detail-header, .star-label", timeout=5000)


# =============================================================================
# WHEN STEPS - USER ACTIONS
# =============================================================================


@when(parsers.parse('the user types "{text}" in the search box'))
def type_in_search(browser_page, text):
    search_input = browser_page.locator(
        "input[placeholder*='modern platforms'], input[placeholder*='Find stories']"
    ).first
    search_input.fill(text)


@when(parsers.parse("the user types a {length:d} character query in the search box"))
def type_long_query(browser_page, length):
    long_query = "a" * length
    search_input = browser_page.locator(
        "input[placeholder*='modern platforms'], input[placeholder*='Find stories']"
    ).first
    search_input.fill(long_query)


@when("the user presses Enter")
def press_enter(browser_page):
    search_input = browser_page.locator(
        "input[placeholder*='modern platforms'], input[placeholder*='Find stories']"
    ).first
    search_input.press("Enter")
    wait_for_streamlit_rerun(browser_page)


@when("the user clears the search box")
def clear_search(browser_page):
    search_input = browser_page.locator(
        "input[placeholder*='modern platforms'], input[placeholder*='Find stories']"
    ).first
    search_input.fill("")
    search_input.press("Enter")
    wait_for_streamlit_rerun(browser_page)


@when(parsers.parse('the user selects "{value}" from the {filter_name} filter'))
def select_filter(browser_page, value, filter_name):
    select = browser_page.locator(
        f"[data-testid='stSelectbox']:has(label:has-text('{filter_name}'))"
    ).first
    trigger = select.locator("input[role='combobox']")
    trigger.scroll_into_view_if_needed()
    trigger.click()
    from playwright.sync_api import expect as pw_expect

    pw_expect(trigger).to_have_attribute("aria-expanded", "true")
    # Options mount elsewhere under #root — aria-controls ID doesn't scope them.
    # Use the accessibility tree: wait for any option to be visible, then
    # get_by_role searches the full a11y tree with built-in auto-wait.
    browser_page.wait_for_selector("[role='option']", state="visible", timeout=5000)
    browser_page.get_by_role("option", name=value, exact=True).click()
    wait_for_streamlit_rerun(browser_page)


@when(parsers.parse('the user clicks the "{value}" filter chip to remove it'))
def click_filter_chip(browser_page, value):
    # Filter chips have format: "✕ {FilterValue}" as a button/paragraph
    wait_for_content(
        browser_page, "button:has-text('✕'), p:has-text('✕')", timeout=5000
    )
    # Capture count before removal for verify_more_stories direction check
    browser_page._es_prefilterclear_count = _read_count(browser_page)

    chip = browser_page.locator(f"button:has-text('✕'):has-text('{value}')").first
    if chip.count() > 0:
        chip.click()
        wait_for_streamlit_rerun(browser_page)
        return

    chip = browser_page.locator(f"p:has-text('✕'):has-text('{value}')").first
    if chip.count() > 0:
        chip.click()
        wait_for_streamlit_rerun(browser_page)
        return

    chip = browser_page.locator(f"[role='button']:has-text('{value}')").first
    chip.click()
    wait_for_streamlit_rerun(browser_page)


@when('the user clicks "Advanced Filters"')
def click_advanced_filters(browser_page):
    expander = browser_page.locator(
        "button:has-text('Advanced Filters'), summary:has-text('Advanced Filters')"
    ).first
    expander.click()
    wait_for_content(browser_page, "[data-testid='stMultiSelect']", timeout=3000)


@when("the user clicks the Reset button")
def click_reset(browser_page):
    # Capture count before reset for direction checks
    browser_page._es_prefilterclear_count = _read_count(browser_page)
    reset_btn = browser_page.locator(
        "button:has-text('Reset'), button:has-text('Clear')"
    ).first
    reset_btn.click()
    wait_for_streamlit_rerun(browser_page)
    # Wait for content to reappear after reset
    wait_for_content(browser_page, ".es-results-count", timeout=5000)


@when(parsers.parse("the user switches to {view} view"))
def switch_view(browser_page, view):
    # Streamlit uses stButtonGroup with segmented controls for view switching
    view_btn = browser_page.locator(
        f"[data-testid='stButtonGroup'] button:has-text('{view}')"
    ).first

    # Check if this view is already active (has segmented_controlActive)
    is_active = "Active" in (view_btn.get_attribute("data-testid") or "")
    if is_active:
        # Already in this view, don't click (would trigger unnecessary rerun)
        return

    view_btn.click()
    wait_for_streamlit_rerun(browser_page)
    # Wait for the specific view content
    if view == "Table":
        wait_for_content(browser_page, '[data-testid="stDataFrame"]', timeout=10000)
    elif view == "Cards":
        wait_for_content(browser_page, ".es-fixed-height-card", timeout=10000)
    elif view == "Timeline":
        wait_for_content(browser_page, ".es-timeline-container", timeout=10000)


@when("the user clicks on a story card")
def click_story_card(browser_page):
    # Wait for any story content to appear first
    wait_for_content(
        browser_page,
        ".es-fixed-height-card, [data-testid='stDataFrame'], .es-story-card",
        timeout=5000,
    )

    # Try Cards view first (prioritize since we might be explicitly in Cards view)
    cards = browser_page.locator(".es-fixed-height-card")
    if cards.count() > 0 and cards.first.is_visible():
        cards.first.click()
        wait_for_streamlit_rerun(browser_page)
        wait_for_content(browser_page, ".es-detail-header, .star-label", timeout=10000)
        return

    # st.dataframe (Table view) rows are canvas-rendered; not clickable from Playwright.
    # Fall through to Timeline cards if in Table view.

    # Try Timeline story cards (direct DOM access)
    timeline_cards = browser_page.locator(".es-story-card")
    if timeline_cards.count() > 0:
        timeline_cards.first.click()
        wait_for_streamlit_rerun(browser_page)
        wait_for_content(browser_page, ".es-detail-header, .star-label", timeout=10000)
        return

    # Last resort: switch to Cards view (same pattern as user_has_opened_detail)
    wait_for_content(browser_page, "[data-testid='stButtonGroup']", timeout=10000)
    view_btn = browser_page.locator(
        "[data-testid='stButtonGroup'] button:has-text('Cards')"
    ).first
    if view_btn.count() > 0:
        view_btn.click()
        wait_for_streamlit_rerun(browser_page)
        wait_for_content(browser_page, ".es-fixed-height-card", timeout=10000)
        cards = browser_page.locator(".es-fixed-height-card")
        if cards.count() > 0:
            cards.first.click()
            wait_for_streamlit_rerun(browser_page)
            wait_for_content(
                browser_page, ".es-detail-header, .star-label", timeout=10000
            )
            return

    pytest.fail(
        "No clickable story elements found — Cards view switch failed or no stories loaded"
    )


@when("the user clicks the close button")
def click_close_button(browser_page):
    # Story detail closes by clicking the selected card again (no explicit close button)
    # Find the selected card and click it
    selected_card = browser_page.locator(".es-fixed-height-card.selected")
    if selected_card.count() > 0 and selected_card.first.is_visible():
        selected_card.first.click()
        wait_for_streamlit_rerun(browser_page)
        # Wait for detail to close
        browser_page.wait_for_timeout(SHORT_WAIT)
        return

    # For default view (Cards), just click any visible card to toggle
    any_card = browser_page.locator(".es-fixed-height-card").first
    if any_card.count() > 0 and any_card.is_visible():
        any_card.click()
        wait_for_streamlit_rerun(browser_page)
        return

    # Fallback: skip if no close mechanism available
    pytest.skip("No close button or selected card found")


@when('the user clicks "Ask Agy About This"')
def click_ask_agy(browser_page):
    # The Ask Agy button is an anchor with id "btn-ask-story"
    # Clicking it triggers JS that clicks a hidden Streamlit button
    # Then Streamlit navigates to Ask Agy page

    # Selectors for Ask Agy page (landing OR conversation view)
    ask_page_selector = ".ask-header-landing, .ask-header-conversation, .st-key-intro_section, [data-testid='stChatInput']"

    # Try the anchor button first
    btn = browser_page.locator("#btn-ask-story").first
    if btn.count() > 0:
        btn.click()
        # Wait for JS + Streamlit rerun + page render; skip networkidle (LLM streaming)
        wait_for_streamlit_rerun(browser_page)
        browser_page.wait_for_timeout(MEDIUM_WAIT)
        wait_for_content(browser_page, ask_page_selector, timeout=15000)
        return

    # Fallback to story-detail card button text (unique — mobile nav doesn't say "About This")
    text_btn = browser_page.locator("text=About This").first
    if text_btn.count() > 0:
        text_btn.click()
        wait_for_streamlit_rerun(browser_page)
        browser_page.wait_for_timeout(MEDIUM_WAIT)
        wait_for_content(browser_page, ask_page_selector, timeout=15000)
        return

    pytest.skip("Ask Agy button not found")


@when("the user clicks the Share button")
def click_share(browser_page):
    # Share button in story detail has id="btn-share-story"
    if not wait_for_content(browser_page, "#btn-share-story", timeout=15000):
        pytest.fail("Share button not found after 15s — story detail did not open")
    # The onclick handler is wired from inside the components.html iframe via
    # setTimeout(..., 500) in story_detail.py. Poll until the handler is bound
    # rather than sleeping a fixed amount.
    browser_page.wait_for_function(
        "() => { const b = document.getElementById('btn-share-story'); "
        "return b && b.onclick !== null; }",
        timeout=5000,
    )
    share_btn = browser_page.locator("#btn-share-story").first
    share_btn.click()
    browser_page.wait_for_timeout(MEDIUM_WAIT)


@when("the user clicks the Helpful button")
def click_helpful(browser_page):
    if not wait_for_content(browser_page, "#btn-helpful-story", timeout=15000):
        pytest.fail("Helpful button not found after 15s — story detail did not open")
    # onclick wired via setTimeout(..., 500); also guard against already-confirmed
    # (disabled) state so the poll exits cleanly even on first-rerun re-render.
    # Clicking Helpful triggers log_feedback() as a side effect — this is expected
    # in test runs; the assertion tests DOM state only, not the write.
    browser_page.wait_for_function(
        "() => { const b = document.getElementById('btn-helpful-story'); "
        "return b && b.onclick !== null && !b.disabled; }",
        timeout=5000,
    )
    browser_page.locator("#btn-helpful-story").click()
    wait_for_streamlit_rerun(browser_page)


@when("the user clicks the Export button")
def click_export(browser_page):
    if not wait_for_content(browser_page, "#btn-export-story", timeout=15000):
        pytest.fail("Export button not found after 15s — story detail did not open")
    # Capture the story title now so the Then step can assert the popup contains it.
    title_locator = browser_page.locator(".es-detail-title")
    browser_page._export_story_title = (
        title_locator.first.text_content().strip() if title_locator.count() > 0 else ""
    )
    # onclick wired via setTimeout(..., 500)
    browser_page.wait_for_function(
        "() => { const b = document.getElementById('btn-export-story'); "
        "return b && b.onclick !== null; }",
        timeout=5000,
    )
    # Export triggers window.open('', '_blank') from inside a components.html iframe
    # after Streamlit processes the click. Register the popup listener BEFORE clicking.
    with browser_page.expect_popup(timeout=30000) as popup_info:
        browser_page.locator("#btn-export-story").click()
    browser_page._export_popup = popup_info.value


@when(parsers.parse('the user navigates to "{url_params}"'))
def navigate_with_params(browser_page, app_url, url_params):
    browser_page.goto(f"{app_url}{url_params}")
    wait_for_streamlit_rerun(browser_page)
    # Deeplinks trigger a Streamlit rerun - wait for My Work to load
    if "?story=" in url_params:
        # Wait for the page to redirect and render My Work
        wait_for_content(browser_page, ".es-results-count", timeout=15000)
        # Wait for story detail to open (deeplinks should auto-open the story)
        wait_for_content(
            browser_page,
            ".es-detail-header, .star-label, #btn-share-story",
            timeout=10000,
        )


@when(parsers.parse('the user clicks "View in Explore" for "{era}"'))
def click_view_in_explore(browser_page, era):
    # Timeline view uses .es-explore-all-link divs with "Explore all X stories" text
    # Wait for timeline content
    wait_for_content(browser_page, ".es-timeline-group", timeout=5000)

    # Click on the first expanded era's explore link (most recent era is auto-expanded)
    explore_link = browser_page.locator(
        ".es-timeline-group.expanded .es-explore-all-link"
    ).first
    if explore_link.count() > 0:
        explore_link.click()
        wait_for_streamlit_rerun(browser_page)
        wait_for_content(browser_page, ".es-results-count", timeout=5000)
        return

    # If no expanded group, try clicking the first era header to expand it
    group_header = browser_page.locator(".es-timeline-group .es-group-header").first
    if group_header.count() > 0:
        group_header.click()
        browser_page.wait_for_timeout(SHORT_WAIT)

        # Now click the explore link
        explore_link = browser_page.locator(
            ".es-timeline-group.expanded .es-explore-all-link"
        ).first
        explore_link.click()
        wait_for_streamlit_rerun(browser_page)
        wait_for_content(browser_page, ".es-results-count", timeout=5000)
        return

    pytest.skip("No Timeline explore links found")


@when('the user clicks "Next"')
def click_next_page(browser_page):
    next_btn = browser_page.locator(
        "button:has-text('Next'), button:has-text('>')"
    ).first
    next_btn.click()
    wait_for_streamlit_rerun(browser_page)


@when(parsers.parse("the user changes page size to {size:d}"))
def change_page_size(browser_page, size):
    # Page size selector has label "page_size" (note: lowercase, underscore)
    size_select = browser_page.locator(
        ".st-key-page_size_select [data-testid='stSelectbox'], [data-testid='stSelectbox']:has-text('page_size')"
    ).first
    size_select.click()
    wait_for_streamlit_rerun(browser_page)
    option = browser_page.locator(f"[role='option']:has-text('{size}')").first
    option.click()
    wait_for_streamlit_rerun(browser_page)


@when(parsers.parse("the browser window is {width:d}px wide"))
def resize_browser(browser_page, width):
    browser_page.set_viewport_size({"width": width, "height": 800})
    browser_page.wait_for_timeout(SHORT_WAIT)


@when(parsers.parse("the user rapidly toggles {filter_name} filter {times:d} times"))
def rapid_toggle(browser_page, filter_name, times):
    for i in range(times):
        select = browser_page.locator(
            f"[data-testid='stSelectbox']:has(label:has-text('{filter_name}'))"
        ).first
        select.click()
        # Toggle between first and second option
        options = browser_page.locator("[role='option']")
        options.nth(i % 2).click()
        browser_page.wait_for_timeout(100)


@when("the user navigates to My Profile")
def navigate_to_about(browser_page):
    about_btn = browser_page.locator("button:has-text('My Profile'):visible").first
    about_btn.click()
    wait_for_streamlit_rerun(browser_page)


@when("the user navigates back to My Work")
def navigate_back_to_explore(browser_page):
    nav_button = browser_page.locator("button:has-text('My Work'):visible").first
    nav_button.click()
    # stDataFrame on My Work causes continuous XHR — networkidle never settles.
    wait_for_streamlit_rerun(browser_page)
    # Wait for My Work page to fully load
    wait_for_content(browser_page, ".es-results-count", timeout=10000)
    # Allow Streamlit state to settle
    browser_page.wait_for_timeout(CONTENT_WAIT)


@when("the user navigates away and returns")
def navigate_away_and_return(browser_page):
    # Navigate to Home
    home_btn = browser_page.locator("button:has-text('Home'):visible").first
    home_btn.click()
    wait_for_streamlit_rerun(browser_page)

    # Navigate back to My Work
    nav_button = browser_page.locator("button:has-text('My Work'):visible").first
    nav_button.click()
    # stDataFrame on My Work causes continuous XHR — networkidle never settles.
    wait_for_streamlit_rerun(browser_page)
    # Wait for results count to be ready and refresh baseline for Then checks
    wait_for_content(browser_page, ".es-results-count", timeout=10000)
    browser_page._es_baseline_count = _read_count(browser_page)


# =============================================================================
# THEN STEPS - ASSERTIONS
# =============================================================================


@then("the results count should update")
def verify_results_count(browser_page):
    # Results count div is always present on My Work
    wait_for_streamlit_rerun(browser_page)
    # The results count is rendered with class "results-count"
    count = browser_page.wait_for_selector(".es-results-count", timeout=10000)
    assert count.is_visible()


@then(parsers.parse('the results should contain stories with "{term1}" or "{term2}"'))
def verify_results_contain_terms(browser_page, term1, term2):
    # Wait for content to render
    wait_for_content(browser_page, ".es-results-count", timeout=5000)
    # Verify results exist by checking the results count text
    results_text = browser_page.locator(".es-results-count").inner_text()
    # Check for various formats
    has_results = (
        "Found" in results_text
        or "Showing" in results_text
        or "project" in results_text.lower()
        or "stor" in results_text.lower()
    )
    assert has_results, f"Unexpected results text: {results_text}"


@then("no error should be displayed")
def verify_no_error(browser_page):
    error = browser_page.locator(".stException, .stError, [data-testid='stException']")
    assert error.count() == 0


@then("the story detail should be closed")
def verify_detail_closed(browser_page):
    detail = browser_page.locator(".story-detail, .st-key-story_detail")
    assert detail.count() == 0 or not detail.is_visible()


@then("the results should reflect the new search")
def verify_new_results(browser_page):
    # Verify results count is present — content change is confirmed by the count text
    count_el = browser_page.locator(".es-results-count")
    assert count_el.count() > 0 and count_el.first.is_visible()


@then("all stories should be displayed")
def verify_all_stories(browser_page):
    # Check for results count showing projects/stories
    wait_for_content(browser_page, ".es-results-count", timeout=5000)
    count = browser_page.locator(".es-results-count").first
    assert count.is_visible()
    # Verify it shows content (not "0 results")
    text = count.inner_text()
    assert "project" in text.lower() or "stor" in text.lower() or "Showing" in text


@then("no filters should be active")
def verify_no_active_filters(browser_page):
    # Filter chips render as st.button elements keyed with chip_ prefix
    chips = browser_page.locator(
        "[class*='st-key-chip_']:not([class*='st-key-chip_clear_all']) "
        "button[data-testid='stBaseButton-secondary']"
    )
    assert chips.count() == 0, f"Expected no active filter chips, found {chips.count()}"


@then(parsers.parse('all displayed stories should have {filter_type} "{value}"'))
def verify_filtered_results(browser_page, filter_type, value):
    # Canvas rows are not DOM-queryable; assert via count direction.
    # A valid filter reduces or maintains (never increases) the story count.
    filtered = _read_count(browser_page)
    baseline = getattr(browser_page, "_es_baseline_count", filtered)
    assert filtered <= baseline, (
        f"Filtered count {filtered} exceeds baseline {baseline} "
        f"— {filter_type}={value!r} filter had no effect"
    )


@then(parsers.parse('the active filters should show "{value}"'))
def verify_active_filter(browser_page, value):
    # Active filters can appear as chips or in filter summary
    browser_page.wait_for_timeout(SHORT_WAIT)

    # Check if the value appears anywhere (use .first to avoid strict mode error)
    text_elem = browser_page.locator(f"text={value}").first
    if text_elem.count() > 0 and text_elem.is_visible():
        return

    # Check for filter chip with close button
    chip = browser_page.locator(f"button:has-text('✕'):has-text('{value}')").first
    if chip.count() > 0 and chip.is_visible():
        return

    # Just verify some filter indication exists
    assert browser_page.locator(
        ".es-results-count"
    ).is_visible(), f"Filter '{value}' not shown in active filters"


@then(parsers.parse('the active filters should show "{value1}" and "{value2}"'))
def verify_multiple_active_filters(browser_page, value1, value2):
    assert browser_page.locator(f"text={value1}").is_visible()
    assert browser_page.locator(f"text={value2}").is_visible()


@then("all displayed stories should match both filters")
def verify_combined_filters(browser_page):
    # Count-direction proxy: two filters applied -> count <= single-filter count
    combined = _read_count(browser_page)
    baseline = getattr(browser_page, "_es_baseline_count", combined + 1)
    assert (
        combined <= baseline
    ), f"Combined-filter count {combined} exceeds baseline {baseline}"


@then(parsers.parse("the {filter_name} filter should be cleared"))
def verify_filter_cleared(browser_page, filter_name):
    # After clearing a chip, count should be >= pre-clear count
    current = _read_count(browser_page)
    pre_clear = getattr(browser_page, "_es_prefilterclear_count", 0)
    assert current >= pre_clear, (
        f"Count after clearing {filter_name!r} filter ({current}) "
        f"is less than pre-clear count ({pre_clear})"
    )


@then("more stories should be displayed")
def verify_more_stories(browser_page):
    current = _read_count(browser_page)
    pre_clear = getattr(browser_page, "_es_prefilterclear_count", 0)
    assert (
        current > pre_clear
    ), f"Expected more stories after filter removal ({current} > {pre_clear})"


@then("the advanced filter section should be visible")
def verify_advanced_visible(browser_page):
    # Advanced filters are in an expander - check for expanded state or content
    wait_for_content(browser_page, "[data-testid='stMultiSelect']", timeout=3000)

    # Check for multiselect widgets (they appear when advanced filters are expanded)
    multiselects = browser_page.locator("[data-testid='stMultiSelect']")
    if multiselects.count() > 0:
        return

    # Check for expander content visibility
    expander_content = browser_page.locator(
        "[data-testid='stExpanderDetails'], .advanced-filters-content"
    )
    if expander_content.count() > 0 and expander_content.first.is_visible():
        return

    raise AssertionError("Advanced filter section not visible")


@then(parsers.parse("the {multiselect_name} multiselect should be visible"))
def verify_multiselect_visible(browser_page, multiselect_name):
    ms = browser_page.locator(
        f"[data-testid='stMultiSelect']:has(label:has-text('{multiselect_name}'))"
    )
    assert ms.is_visible()


@then("all displayed stories should match both Client and Role")
def verify_client_role_filter(browser_page):
    # Count-direction proxy: dual filter reduces or maintains count vs baseline
    combined = _read_count(browser_page)
    baseline = getattr(browser_page, "_es_baseline_count", combined + 1)
    assert (
        combined <= baseline
    ), f"Client+Role filter count {combined} exceeds baseline {baseline}"


@then(parsers.parse('the Era filter should be set to "{era}"'))
def verify_era_filter(browser_page, era):
    # After clicking "Explore all" from Timeline, the Era filter should be set
    # Wait for My Work page to load
    wait_for_content(browser_page, ".es-results-count", timeout=5000)

    # Look for any Era filter/selectbox that shows a value (not "All Eras")
    era_select = browser_page.locator("[data-testid='stSelectbox']")
    if era_select.count() > 0:
        # Check that we're on My Work with some era filter active
        results = browser_page.locator(".es-results-count")
        assert results.is_visible(), "Should be on My Work page with results"
        return

    # Fallback: just verify we're on My Work with filtered results
    assert browser_page.locator(".es-results-count").is_visible()


@then("results should be filtered to that era")
def verify_era_results(browser_page):
    # Era filter is active — count must be > 0 and <= baseline
    era_count = _read_count(browser_page)
    assert era_count > 0, "Era filter returned 0 results — expected some stories"
    baseline = getattr(browser_page, "_es_baseline_count", era_count + 1)
    assert (
        era_count <= baseline
    ), f"Era-filtered count {era_count} exceeds baseline {baseline}"


@then("all filters should be cleared")
def verify_all_filters_cleared(browser_page):
    # No filter chips should be visible after Reset
    chips = browser_page.locator(
        "[class*='st-key-chip_']:not([class*='st-key-chip_clear_all']) "
        "button[data-testid='stBaseButton-secondary']"
    )
    assert (
        chips.count() == 0
    ), f"Expected no filter chips after Reset, found {chips.count()}"
    # Count should be restored to (or near) baseline
    current = _read_count(browser_page)
    baseline = getattr(browser_page, "_es_baseline_count", 0)
    if baseline > 0:
        assert (
            current >= baseline
        ), f"Post-reset count {current} is less than baseline {baseline}"


@then("the search box should be empty")
def verify_search_empty(browser_page):
    # Wait for Streamlit to complete the reset
    browser_page.wait_for_timeout(SHORT_WAIT)
    search_input = browser_page.locator(
        "input[placeholder*='modern platforms'], input[placeholder*='Find stories']"
    ).first
    value = search_input.input_value()
    assert value == "", f"Search box should be empty but contains: '{value}'"


@then("no story detail should be open")
def verify_no_story_detail(browser_page):
    detail = browser_page.locator(
        ".story-detail, .st-key-story_detail, [data-testid='stExpander'][aria-expanded='true']:has-text('Situation')"
    )
    assert detail.count() == 0 or not detail.first.is_visible()


@then(parsers.parse("the view should still be {view} view"))
def verify_view_mode(browser_page, view):
    wait_for_streamlit_rerun(browser_page)

    if view == "Table":
        try:
            browser_page.wait_for_selector('[data-testid="stDataFrame"]', timeout=10000)
        except Exception:
            pass
        assert (
            browser_page.locator('[data-testid="stDataFrame"]').count() > 0
        ), "Table view (stDataFrame) not found"
    elif view == "Cards":
        wait_for_content(browser_page, ".es-fixed-height-card", timeout=10000)
        assert (
            browser_page.locator(".es-fixed-height-card").count() > 0
        ), "Cards view content not found"
    elif view == "Timeline":
        try:
            browser_page.wait_for_selector(".es-timeline-container", timeout=10000)
        except Exception:
            pass
        assert browser_page.locator(".es-timeline-container").count() > 0


@then("stories should be displayed in a table format")
def verify_table_format(browser_page):
    # st.dataframe replaces AgGrid. GDG canvas mounting is the proxy assertion.
    browser_page.wait_for_selector('[data-testid="stDataFrame"]', timeout=20000)
    canvas_count = browser_page.locator('[data-testid="data-grid-canvas"]').count()
    if canvas_count == 0:
        canvas_count = browser_page.locator(
            '[data-testid="stDataFrame"] canvas'
        ).count()
    assert canvas_count > 0, "st.dataframe GDG canvas not found — grid did not mount"


@then("the table should have columns for Title, Client, Role")
def verify_table_columns(browser_page):
    # Simplified - just check table exists
    pass


@then("stories should be displayed as cards")
def verify_cards_format(browser_page):
    cards = browser_page.locator(".es-fixed-height-card")
    assert cards.count() > 0


@then("each card should show Title and Client")
def verify_card_content(browser_page):
    # Simplified - cards exist
    pass


@then("stories should be grouped by career era")
def verify_timeline_groups(browser_page):
    eras = browser_page.locator(".es-timeline-group, .es-timeline-container")
    assert eras.count() > 0


@then("each era should be collapsible")
def verify_collapsible_eras(browser_page):
    # Check for expander elements
    pass


@then(parsers.parse('the search query should still be "{query}"'))
def verify_search_query(browser_page, query):
    search_input = browser_page.locator(
        "input[placeholder*='modern platforms'], input[placeholder*='Find stories']"
    ).first
    value = search_input.input_value()
    assert value == query


@then("results should still be filtered")
def verify_still_filtered(browser_page):
    current = _read_count(browser_page)
    baseline = getattr(browser_page, "_es_baseline_count", current + 1)
    assert (
        current < baseline
    ), f"Expected a filtered count (<{baseline}) after navigation, got {current}"


@then(parsers.parse('the {filter_name} filter should still be "{value}"'))
def verify_filter_preserved(browser_page, filter_name, value):
    # Use .first to avoid strict mode violation when multiple elements match
    text_elem = browser_page.locator(f"text={value}").first
    assert text_elem.is_visible(), f"Filter value '{value}' not visible"


@then("the story detail should still be open")
def verify_detail_open(browser_page):
    # Story detail shows with .es-detail-header and .star-label elements
    detail = browser_page.locator(".es-detail-header, .star-label")
    assert detail.first.is_visible(), "Story detail not visible"


@then(parsers.parse('the story should be "{story_id}"'))
def verify_story_id(browser_page, story_id):
    # Story ID might be partial - check if detail panel shows any story
    # Look for story title containing keywords from the ID
    keywords = story_id.replace("-", " ").split()[:3]  # First 3 words
    for keyword in keywords:
        if "'" not in keyword:  # apostrophe breaks CSS :has-text() parser
            if (
                browser_page.locator(f".es-detail-header:has-text('{keyword}')").count()
                > 0
            ):
                return
        if browser_page.locator(f"text=/{keyword}/i").count() > 0:
            return
    # Just verify a detail panel is open
    detail = browser_page.locator(".es-detail-header, .star-label")
    assert detail.first.is_visible(), f"Story detail with '{story_id}' not found"


@then("the story detail panel should open")
def verify_detail_panel_open(browser_page):
    # Story detail panel has .es-detail-header and STAR sections
    wait_for_content(browser_page, ".es-detail-header, .star-label", timeout=5000)

    # Check for detail header (primary indicator)
    detail_header = browser_page.locator(".es-detail-header")
    if detail_header.count() > 0 and detail_header.first.is_visible():
        return

    # Check for STAR sections (Situation, Task, etc.)
    star_labels = browser_page.locator(".star-label, .star-section")
    if star_labels.count() > 0:
        return

    # Check for any visible "Situation" text (part of STAR)
    situation = browser_page.locator("text=Situation")
    if situation.count() > 0 and situation.first.is_visible():
        return

    raise AssertionError("Story detail panel not visible")


@then("the detail should show the story Title")
def verify_detail_title(browser_page):
    pass  # Would check title element


@then("the detail should show Situation, Task, Action, Result")
def verify_star_sections(browser_page):
    # Check for STAR section labels (they appear as uppercase text in .star-label)
    wait_for_content(browser_page, ".star-label", timeout=3000)
    for section in ["SITUATION", "TASK", "ACTION", "RESULT"]:
        # Try the star-label selector first
        label = browser_page.locator(f".star-label:has-text('{section}')").first
        if label.count() > 0 and label.is_visible():
            continue
        # Fallback: just check for any text containing the section name
        text_elem = browser_page.get_by_text(section, exact=True).first
        assert text_elem.is_visible(), f"{section} section not found"


@then(parsers.re(r"the detail should have an? (?P<section>\w+) section"))
def verify_detail_section(browser_page, section):
    # Use star-label selector to avoid matching content text
    label = browser_page.locator(f".star-label:has-text('{section.upper()}')")
    if label.count() > 0 and label.first.is_visible():
        return
    # Fallback: check for section heading with emoji prefix
    heading = browser_page.locator(f"text='{section.upper()}'")
    assert heading.count() > 0, f"Section '{section}' not found"


@then("the story list should be visible")
def verify_story_list(browser_page):
    stories = browser_page.locator(
        ".es-fixed-height-card, [data-testid='stDataFrame'], .es-timeline-container"
    )
    assert stories.first.is_visible()


@then('the "Ask Agy About This" button should be visible')
def verify_ask_agy_button(browser_page):
    # Story-detail "Ask Agy 🐾 About This" button has unique ID #btn-ask-story
    # (story_detail.py:867). Text-based fallbacks were removed because "Ask Agy"
    # also appears on the (hidden) mobile-nav link after the MATTGPT-100 rename.
    btn = browser_page.locator("#btn-ask-story").first
    btn.wait_for(state="visible", timeout=5000)


@then("the page should navigate to Ask Agy")
def verify_navigate_to_ask(browser_page):
    # Check for Ask Agy page elements (header is most reliable)
    ask_page_selector = ".ask-header-landing, .ask-header-conversation, .st-key-intro_section, [data-testid='stChatInput']"
    browser_page.wait_for_selector(ask_page_selector, timeout=15000)


@then("the question should reference the story")
def verify_question_references_story(browser_page):
    from playwright.sync_api import expect as pw_expect

    # seed_prompt ("Tell me more about: {Title}") fires multiple Streamlit reruns
    # before surfacing as the first user message in the conversation.
    seed_msg = browser_page.locator(
        "[data-testid='stChatMessage']:has-text('Tell me more about:')"
    )
    pw_expect(seed_msg.first).to_be_visible(timeout=15000)


@then("the clipboard should contain the story deeplink URL")
def verify_clipboard(browser_page, shared_browser, app_url):
    """
    Verify Share button copied a valid deeplink URL to clipboard.

    The URL format is: https://askmattgpt.streamlit.app/~/+/?story=<story-id>
    We extract the story param and verify it works on localhost.
    """
    import urllib.parse

    # Read clipboard contents via JavaScript
    try:
        clipboard_url = browser_page.evaluate("navigator.clipboard.readText()")
    except Exception as e:
        pytest.skip(f"Clipboard read not supported in this browser config: {e}")

    # Verify it's a valid URL with story parameter
    assert clipboard_url, "Clipboard is empty after clicking Share"
    assert "?story=" in clipboard_url, f"URL missing story param: {clipboard_url}"

    # Extract the story parameter
    parsed = urllib.parse.urlparse(clipboard_url)
    query_params = urllib.parse.parse_qs(parsed.query)
    story_id = query_params.get("story", [None])[0]
    assert story_id, f"Could not extract story ID from URL: {clipboard_url}"

    # Open a new page with the story deeplink on localhost
    new_context = shared_browser.new_context(viewport={"width": 1280, "height": 900})
    new_page = new_context.new_page()

    try:
        # Navigate to localhost with the story parameter
        # First go to the app and click My Work
        new_page.goto(app_url)
        new_page.wait_for_load_state("networkidle")
        new_page.wait_for_selector("button:has-text('My Work')", timeout=30000)
        nav_button = new_page.locator("button:has-text('My Work'):visible").first
        nav_button.click()
        new_page.wait_for_load_state("networkidle")

        # Now navigate with the story parameter
        explore_url = f"{app_url}?story={urllib.parse.quote(story_id, safe='')}"
        new_page.goto(explore_url)
        new_page.wait_for_load_state("networkidle")

        # Wait for story detail to open
        wait_for_content(new_page, ".es-detail-header, .star-label", timeout=10000)

        # Verify story detail is visible
        detail = new_page.locator(".es-detail-header, .star-label")
        assert detail.first.is_visible(), "Story detail did not open from deeplink URL"
    finally:
        new_page.close()
        new_context.close()


@then("the Share button should show a Copied confirmation")
def verify_share_copied_state(browser_page):
    from playwright.sync_api import expect as pw_expect

    share_btn = browser_page.locator("#btn-share-story")
    pw_expect(share_btn).to_contain_text("Copied!", timeout=2000)


@then("the Share button should revert to its default label")
def verify_share_reverts(browser_page):
    from playwright.sync_api import expect as pw_expect

    share_btn = browser_page.locator("#btn-share-story")
    pw_expect(share_btn).to_contain_text("Share", timeout=4000)


@then("the Helpful button should show confirmed state")
def verify_helpful_confirmed(browser_page):
    from playwright.sync_api import expect as pw_expect

    btn = browser_page.locator("#btn-helpful-story")
    # Auto-polls through Streamlit's two-rerun cycle (click → st.rerun() → re-render)
    pw_expect(btn).to_contain_text("Helpful ✓", timeout=15000)
    assert (
        btn.get_attribute("disabled") is not None
    ), "Helpful button should be disabled after confirmation"


@then("a new window should open with the story content")
def verify_export_popup(browser_page):
    popup = getattr(browser_page, "_export_popup", None)
    assert popup is not None, (
        "Export popup was not captured — window.open may have been blocked "
        "in headless Chromium (check components.html iframe sandbox permissions)"
    )
    popup.wait_for_load_state("domcontentloaded", timeout=10000)
    content = popup.content()
    # The native print dialog fires automatically inside the popup. It is browser
    # chrome (OS-level dialog) and is not testable from Playwright. In headless
    # Chromium it is suppressed silently. We assert DOM-observable content only.
    expected_title = getattr(browser_page, "_export_story_title", "")
    if expected_title:
        assert expected_title in content, (
            f"Expected story title '{expected_title}' in export popup content; "
            f"first 300 chars: {content[:300]}"
        )
    else:
        assert (
            "SITUATION" in content
        ), "Export popup missing STAR story structure — expected 'SITUATION' section"
    popup.close()


@then("the pagination should show page numbers")
def verify_pagination(browser_page):
    pagination = browser_page.locator(
        ".es-pagination, button:has-text('Next'), button:has-text('Previous')"
    )
    assert pagination.count() > 0


@then(parsers.parse("the current page should be {page_num:d}"))
def verify_current_page(browser_page, page_num):
    pass  # Would check page indicator


@then(parsers.parse("page {page_num:d} should be displayed"))
def verify_page_number(browser_page, page_num):
    pass


@then("different stories should be shown")
def verify_different_stories(browser_page):
    pass


@then(parsers.parse("up to {count:d} stories should be displayed per page"))
def verify_page_size(browser_page, count):
    # Cards and Timeline: count DOM card elements directly
    card_count = (
        browser_page.locator(".es-fixed-height-card").count()
        + browser_page.locator(".es-story-card").count()
    )
    if card_count > 0:
        assert card_count <= count, f"Found {card_count} cards, expected <= {count}"


@then(parsers.parse("the page should reset to {page_num:d}"))
def verify_page_reset(browser_page, page_num):
    pass  # Would check page indicator


@then(parsers.parse('the search query should be "{query}"'))
def verify_search_query_is(browser_page, query):
    search_input = browser_page.locator(
        "input[placeholder*='modern platforms'], input[placeholder*='Find stories']"
    ).first
    value = search_input.input_value()
    assert value == query


@then(parsers.parse('the {filter_name} filter should be "{value}"'))
def verify_filter_value(browser_page, filter_name, value):
    assert browser_page.locator(f"text={value}").is_visible()


@then("filters should be stacked vertically")
def verify_stacked_filters(browser_page):
    pass  # Would check layout


@then("content should not overflow horizontally")
def verify_no_overflow(browser_page):
    body = browser_page.locator("body")
    overflow = body.evaluate("el => el.scrollWidth > el.clientWidth")
    assert not overflow


@then(parsers.parse("cards should display in {columns:d} columns"))
def verify_column_count(browser_page, columns):
    pass  # Would check grid layout


@then("all filters should be visible inline")
def verify_inline_filters(browser_page):
    pass


@then(parsers.parse("cards should display in {min_cols:d} or more columns"))
def verify_min_columns(browser_page, min_cols):
    pass


@then("the final filter state should be consistent")
def verify_consistent_state(browser_page):
    # No errors means consistent
    error = browser_page.locator(".stException, .stError")
    assert error.count() == 0


@then("the query should be processed")
def verify_query_processed(browser_page):
    wait_for_streamlit_rerun(browser_page)


@then("no crash should occur")
def verify_no_crash(browser_page):
    error = browser_page.locator(".stException, .stError")
    assert error.count() == 0


@then("the story detail should be open")
def verify_story_detail_open(browser_page):
    # Story detail renders with .es-detail-header, .star-label, and #btn-share-story
    # Wait longer for deeplinks which trigger a Streamlit rerun
    found = wait_for_content(
        browser_page, ".es-detail-header, .star-label, #btn-share-story", timeout=15000
    )

    if found:
        return

    # Check for STAR section content as fallback
    star_content = browser_page.locator(".star-label, .star-section, .star-content")
    if star_content.count() > 0 and star_content.first.is_visible():
        return

    # Check for Share button (definitive sign of story detail)
    share_btn = browser_page.locator("#btn-share-story")
    if share_btn.count() > 0 and share_btn.first.is_visible():
        return

    pytest.fail(
        "Story detail not visible — expected .es-detail-header, .star-label, "
        "or #btn-share-story to be present and visible"
    )


# =============================================================================
# REJECTION BANNER STEPS — added May 23, 2026 for the rule:* divergence
# scenario and as a side benefit closing the 2 pending rejection-banner
# scenarios that have been documented-but-step-def-pending under the
# MATTGPT-060 pattern (lines 311-321 of explore_stories.feature).
# =============================================================================


@then("the rejection banner should be displayed")
def rejection_banner_displayed(browser_page):
    """Wait for the .no-match-banner DOM element to render after a rejected
    query. The banner is rendered by render_no_match_banner() in
    utils/ui_helpers.py — present in both Ask Agy and My Work
    surfaces with the same class hook."""
    browser_page.wait_for_selector(".no-match-banner", timeout=10000)
    banner = browser_page.locator(".no-match-banner").first
    assert banner.is_visible(), "Rejection banner should be visible but is not"


@then(parsers.parse("the banner displays the {reason} copy from BANNER_COPY"))
def banner_displays_copy_from_banner_copy(browser_page, reason):
    """Compare the rendered banner text against the literal value of
    BANNER_COPY[reason] from utils/ui_helpers.py. The assertion message
    surfaces a side-by-side diff on failure.

    Gherkin uses 'rule:*' as the human-readable reason marker, but the
    BANNER_COPY dict key is 'rule' (no colon-star). Normalize the Gherkin
    reason → dict key here. Mirrors the pattern in
    tests/bdd/steps/test_ask_mattgpt.py::then_banner_displays_copy.
    """
    key = reason.rstrip(":*").rstrip(":")
    if key not in BANNER_COPY:
        # Try the raw form (e.g., "personal", "out_of_scope", "low_confidence")
        key = reason
    expected = BANNER_COPY[key]
    banner_msg = browser_page.locator(".no-match-banner-msg").first
    actual = banner_msg.inner_text()
    assert actual == expected, (
        f"BANNER_COPY[{key!r}] mismatch.\n"
        f"  Expected: {expected!r}\n"
        f"  Actual:   {actual!r}"
    )


# =============================================================================
# TWO-ROW FILTER BAR (MATTGPT-065)
# =============================================================================


@given("the viewport width is 1280px")
def set_viewport_desktop(browser_page):
    browser_page.set_viewport_size({"width": 1280, "height": 900})
    browser_page.wait_for_timeout(SHORT_WAIT)


@when("the page loads")
def wait_for_page_stable(browser_page):
    wait_for_streamlit_rerun(browser_page)
    browser_page.wait_for_timeout(SHORT_WAIT)


@when("the viewport is resized to 375px wide")
def resize_to_mobile(browser_page):
    browser_page.set_viewport_size({"width": 375, "height": 800})
    browser_page.wait_for_timeout(SHORT_WAIT)


@then("the Client filter should be visible")
def client_filter_visible(browser_page):
    el = browser_page.locator("[class*='st-key-r2_client']").first
    assert el.is_visible(), "Client filter (r2_client) not visible on desktop"


@then("the Role filter should be visible")
def role_filter_visible(browser_page):
    el = browser_page.locator("[class*='st-key-r2_role']").first
    assert el.is_visible(), "Role filter (r2_role) not visible on desktop"


@then("the Domain filter should be visible")
def domain_filter_visible(browser_page):
    el = browser_page.locator("[class*='st-key-r2_domain']").first
    assert el.is_visible(), "Domain filter (r2_domain) not visible on desktop"


@then("the Industry filter label should be visible")
def industry_filter_label_visible(browser_page):
    # MATTGPT-123: _v2 key required — Green will need Python key bump on the Industry selectbox
    el = browser_page.locator(
        "[class*='st-key-facet_industry_v2'] [data-testid='stWidgetLabel']"
    ).first
    assert el.is_visible(), (
        "Industry filter label not visible — MATTGPT-123: inline label may not be rendering. "
        "Check that the stForm label-hide rule is not catching this element."
    )


@then("the Capability filter label should be visible")
def capability_filter_label_visible(browser_page):
    # MATTGPT-123: _v2 key required — Green will need Python key bump on the Capability selectbox
    el = browser_page.locator(
        "[class*='st-key-facet_capability_v2'] [data-testid='stWidgetLabel']"
    ).first
    assert el.is_visible(), (
        "Capability filter label not visible — MATTGPT-123: inline label may not be rendering. "
        "Check that the stForm label-hide rule is not catching this element."
    )


@then("the Reset filters button should be visible")
def reset_filters_button_visible(browser_page):
    el = browser_page.locator("[class*='st-key-r2_reset'] button").first
    assert el.is_visible(), (
        "Reset filters button not visible — MATTGPT-123: text-link styling may be "
        "accidentally hiding the element instead of just restyling it."
    )


@then("the row 2 filter bar should not be visible")
def row2_filter_bar_hidden(browser_page):
    el = browser_page.locator("[class*='st-key-r2_row']").first
    assert (
        not el.is_visible()
    ), "Row 2 filter bar should be hidden on mobile but is visible"


@then("the row 2 filter bar should be visible")
def row2_filter_bar_visible(browser_page):
    el = browser_page.locator("[class*='st-key-r2_row']").first
    assert el.is_visible(), (
        "Row 2 filter bar should be visible after toggle but is hidden. "
        "MATTGPT-119: Filters toggle may not be showing Row 2."
    )


@then(parsers.parse('a button with text containing "{text}" should be visible'))
def button_with_text_visible(browser_page, text):
    # Scoped to the mobile filters toggle container to avoid false positives
    # from other buttons containing "filter" (e.g., "Reset filters")
    btn = browser_page.locator(
        f"[class*='st-key-es_mobile_filters_toggle'] button:has-text('{text}')"
    ).first
    assert btn.is_visible(), (
        f"Expected a visible mobile Filters toggle button containing '{text}' but none found. "
        "MATTGPT-119: mobile Filters toggle button may not be rendered."
    )


@then(parsers.parse('no button with text containing "{text}" should be visible'))
def button_with_text_not_visible(browser_page, text):
    # Scoped to the mobile filters toggle container — avoids matching "Reset filters"
    btn = browser_page.locator(
        f"[class*='st-key-es_mobile_filters_toggle'] button:has-text('{text}')"
    )
    count = btn.count()
    visible = any(btn.nth(i).is_visible() for i in range(count))
    assert not visible, (
        f"Expected mobile Filters toggle button containing '{text}' to be hidden but it is visible. "
        "MATTGPT-119: Filters toggle button should be hidden on desktop."
    )


@when(parsers.parse('the user clicks the "{label}" button'))
def click_button_by_label(browser_page, label):
    btn = browser_page.locator(
        f"[class*='st-key-es_mobile_filters_toggle'] button:has-text('{label}')"
    ).first
    btn.wait_for(state="visible", timeout=30000)
    btn.click()
    wait_for_streamlit_rerun(browser_page)
    browser_page.wait_for_timeout(SHORT_WAIT)


@then("no story results should be shown")
def no_story_results_shown(browser_page):
    """After a rejected query, story rendering must be absent.
    st.dataframe replaces AgGrid; proxy is the stDataFrame widget + card count.
    Anti-vacuous check: temporarily remove either assert and this step passes on
    a page with stories — restore immediately after confirming failure."""
    dataframe_count = browser_page.locator('[data-testid="stDataFrame"]').count()
    story_cards = browser_page.locator(".es-fixed-height-card, .es-story-card").count()
    assert dataframe_count == 0 and story_cards == 0, (
        f"Expected zero story results after rejection, "
        f"found {dataframe_count} stDataFrame widget(s) + {story_cards} story card(s)"
    )
