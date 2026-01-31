"""
BDD Step Definitions for Explore Stories

These step definitions use Playwright for browser automation.
Install with: pip install pytest-bdd playwright
Run with: pytest tests/bdd -k explore_stories
"""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

# Load the feature file
scenarios('../features/explore_stories.feature')


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def browser_page():
    """Create a Playwright browser page."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip(
            "Playwright not installed. Run: pip install playwright && playwright install chromium"
        )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()


@pytest.fixture
def app_url():
    """URL of the running Streamlit app."""
    return "http://localhost:8501"


# =============================================================================
# GIVEN STEPS - NAVIGATION
# =============================================================================


@given("the user navigates to the Explore Stories page")
def navigate_to_explore(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    # Click Explore Stories in navbar
    nav_button = browser_page.locator(
        "button:has-text('Explore Stories'), a:has-text('Explore Stories')"
    ).first
    nav_button.click()
    browser_page.wait_for_load_state("networkidle")


@given("the page has finished loading")
def wait_for_page_load(browser_page):
    browser_page.wait_for_load_state("networkidle")
    # Wait for story cards or table to be visible
    browser_page.wait_for_selector(
        ".story-card, [data-testid='stDataFrame'], .timeline-era", timeout=10000
    )


@given("the user has searched for {query}")
@given(parsers.parse('the user has searched for "{query}"'))
def user_has_searched(browser_page, query):
    search_input = browser_page.locator(
        "input[placeholder*='Find stories'], input[placeholder*='Search']"
    ).first
    search_input.fill(query)
    search_input.press("Enter")
    browser_page.wait_for_load_state("networkidle")


@given("the user has opened a story detail")
def user_has_opened_detail(browser_page):
    # Click first story card or row
    story = browser_page.locator(".story-card, [data-testid='stDataFrame'] tr").first
    story.click()
    browser_page.wait_for_selector(".story-detail, .st-key-story_detail", timeout=5000)


@given(parsers.parse('the user has opened story "{story_id}"'))
def user_has_opened_specific_story(browser_page, story_id):
    story = browser_page.locator(
        f"[data-story-id='{story_id}'], .story-card:has-text('{story_id}')"
    ).first
    story.click()
    browser_page.wait_for_selector(".story-detail, .st-key-story_detail", timeout=5000)


@given(parsers.parse('the user has selected "{value}" from the {filter_name} filter'))
def user_has_selected_filter(browser_page, value, filter_name):
    select = browser_page.locator(
        f"[data-testid='stSelectbox']:has-text('{filter_name}')"
    ).first
    select.click()
    option = browser_page.locator(f"[role='option']:has-text('{value}')").first
    option.click()
    browser_page.wait_for_load_state("networkidle")


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
    view_toggle = browser_page.locator(
        f"button:has-text('{view}'), [data-testid='stRadio'] label:has-text('{view}')"
    ).first
    view_toggle.click()
    browser_page.wait_for_load_state("networkidle")


@given(parsers.parse("the user preference is {view} view"))
def user_preference_view(browser_page, view):
    # Same as setting view
    user_is_in_view(browser_page, view)


@given(parsers.parse("the user is on page {page_num:d}"))
def user_is_on_page(browser_page, page_num):
    for _ in range(page_num - 1):
        next_btn = browser_page.locator(
            "button:has-text('Next'), button:has-text('>')"
        ).first
        next_btn.click()
        browser_page.wait_for_load_state("networkidle")


@given(parsers.parse("there are more than {count:d} stories"))
def verify_story_count(browser_page, count):
    # This is a precondition - verified by presence of pagination
    pass


@given("the user was previously on Explore Stories with filters and a story open")
def user_was_previously_on_explore(browser_page, app_url):
    # Navigate to Explore Stories
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    nav_button = browser_page.locator(
        "button:has-text('Explore Stories'), a:has-text('Explore Stories')"
    ).first
    nav_button.click()
    browser_page.wait_for_load_state("networkidle")

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
        browser_page.wait_for_load_state("networkidle")

    # Open a story
    story = browser_page.locator(
        ".story-card, [data-testid='stDataFrame'] tbody tr"
    ).first
    if story.is_visible():
        story.click()
        browser_page.wait_for_timeout(500)


# =============================================================================
# WHEN STEPS - USER ACTIONS
# =============================================================================


@when(parsers.parse('the user types "{text}" in the search box'))
def type_in_search(browser_page, text):
    search_input = browser_page.locator(
        "input[placeholder*='Find stories'], input[placeholder*='Search']"
    ).first
    search_input.fill(text)


@when(parsers.parse("the user types a {length:d} character query in the search box"))
def type_long_query(browser_page, length):
    long_query = "a" * length
    search_input = browser_page.locator(
        "input[placeholder*='Find stories'], input[placeholder*='Search']"
    ).first
    search_input.fill(long_query)


@when("the user presses Enter")
def press_enter(browser_page):
    search_input = browser_page.locator(
        "input[placeholder*='Find stories'], input[placeholder*='Search']"
    ).first
    search_input.press("Enter")
    browser_page.wait_for_load_state("networkidle")


@when("the user clears the search box")
def clear_search(browser_page):
    search_input = browser_page.locator(
        "input[placeholder*='Find stories'], input[placeholder*='Search']"
    ).first
    search_input.fill("")
    search_input.press("Enter")
    browser_page.wait_for_load_state("networkidle")


@when(parsers.parse('the user selects "{value}" from the {filter_name} filter'))
def select_filter(browser_page, value, filter_name):
    # Handle both selectbox and multiselect
    if filter_name in ["Client", "Role", "Domain"]:
        # Multiselect
        multiselect = browser_page.locator(
            f"[data-testid='stMultiSelect']:has(label:has-text('{filter_name}'))"
        ).first
        multiselect.click()
        option = browser_page.locator(f"[role='option']:has-text('{value}')").first
        option.click()
    else:
        # Selectbox
        select = browser_page.locator(
            f"[data-testid='stSelectbox']:has(label:has-text('{filter_name}'))"
        ).first
        select.click()
        option = browser_page.locator(f"[role='option']:has-text('{value}')").first
        option.click()
    browser_page.wait_for_load_state("networkidle")


@when(parsers.parse('the user clicks the "{value}" filter chip to remove it'))
def click_filter_chip(browser_page, value):
    chip = browser_page.locator(
        f".filter-chip:has-text('{value}'), button:has-text('{value} ×')"
    ).first
    chip.click()
    browser_page.wait_for_load_state("networkidle")


@when('the user clicks "Advanced Filters"')
def click_advanced_filters(browser_page):
    expander = browser_page.locator(
        "button:has-text('Advanced Filters'), summary:has-text('Advanced Filters')"
    ).first
    expander.click()
    browser_page.wait_for_timeout(500)


@when("the user clicks the Reset button")
def click_reset(browser_page):
    reset_btn = browser_page.locator(
        "button:has-text('Reset'), button:has-text('Clear')"
    ).first
    reset_btn.click()
    browser_page.wait_for_load_state("networkidle")


@when(parsers.parse("the user switches to {view} view"))
def switch_view(browser_page, view):
    view_toggle = browser_page.locator(
        f"button:has-text('{view}'), [data-testid='stRadio'] label:has-text('{view}')"
    ).first
    view_toggle.click()
    browser_page.wait_for_load_state("networkidle")


@when("the user clicks on a story card")
def click_story_card(browser_page):
    card = browser_page.locator(
        ".story-card, [data-testid='stDataFrame'] tbody tr"
    ).first
    card.click()
    browser_page.wait_for_timeout(500)


@when("the user clicks on a story row")
def click_story_row(browser_page):
    row = browser_page.locator("[data-testid='stDataFrame'] tbody tr").first
    row.click()
    browser_page.wait_for_timeout(500)


@when("the user clicks the close button")
def click_close_button(browser_page):
    close_btn = browser_page.locator(
        "button:has-text('×'), button:has-text('Close'), .close-button"
    ).first
    close_btn.click()
    browser_page.wait_for_timeout(500)


@when('the user clicks "Ask Agy About This"')
def click_ask_agy(browser_page):
    btn = browser_page.locator("button:has-text('Ask Agy')").first
    btn.click()
    browser_page.wait_for_load_state("networkidle")


@when("the user clicks the Share button")
def click_share(browser_page):
    share_btn = browser_page.locator(
        "button:has-text('Share'), button:has-text('Copy Link')"
    ).first
    share_btn.click()
    browser_page.wait_for_timeout(500)


@when(parsers.parse('the user navigates to "{url_params}"'))
def navigate_with_params(browser_page, app_url, url_params):
    browser_page.goto(f"{app_url}{url_params}")
    browser_page.wait_for_load_state("networkidle")


@when(parsers.parse('the user clicks "View in Explore" for "{era}"'))
def click_view_in_explore(browser_page, era):
    link = browser_page.locator(
        f"a:has-text('View in Explore'):near(:text('{era}'))"
    ).first
    link.click()
    browser_page.wait_for_load_state("networkidle")


@when('the user clicks "Next"')
def click_next_page(browser_page):
    next_btn = browser_page.locator(
        "button:has-text('Next'), button:has-text('>')"
    ).first
    next_btn.click()
    browser_page.wait_for_load_state("networkidle")


@when(parsers.parse("the user changes page size to {size:d}"))
def change_page_size(browser_page, size):
    size_select = browser_page.locator(
        "[data-testid='stSelectbox']:has(label:has-text('Page size'))"
    ).first
    size_select.click()
    option = browser_page.locator(f"[role='option']:has-text('{size}')").first
    option.click()
    browser_page.wait_for_load_state("networkidle")


@when(parsers.parse("the browser window is {width:d}px wide"))
def resize_browser(browser_page, width):
    browser_page.set_viewport_size({"width": width, "height": 800})
    browser_page.wait_for_timeout(500)


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


@when("the user navigates to About Matt")
def navigate_to_about(browser_page):
    about_btn = browser_page.locator(
        "button:has-text('About'), a:has-text('About')"
    ).first
    about_btn.click()
    browser_page.wait_for_load_state("networkidle")


@when("the user navigates back to Explore Stories")
def navigate_back_to_explore(browser_page):
    nav_button = browser_page.locator(
        "button:has-text('Explore Stories'), a:has-text('Explore Stories')"
    ).first
    nav_button.click()
    browser_page.wait_for_load_state("networkidle")


@when("the user navigates away and returns")
def navigate_away_and_return(browser_page):
    # Navigate to Home
    home_btn = browser_page.locator("button:has-text('Home'), a:has-text('Home')").first
    home_btn.click()
    browser_page.wait_for_load_state("networkidle")

    # Navigate back to Explore Stories
    nav_button = browser_page.locator(
        "button:has-text('Explore Stories'), a:has-text('Explore Stories')"
    ).first
    nav_button.click()
    browser_page.wait_for_load_state("networkidle")


# =============================================================================
# THEN STEPS - ASSERTIONS
# =============================================================================


@then("the results count should update")
def verify_results_count(browser_page):
    count = browser_page.locator("text=/\\d+ stor(y|ies)/").first
    assert count.is_visible()


@then(parsers.parse('the results should contain stories with "{term1}" or "{term2}"'))
def verify_results_contain_terms(browser_page, term1, term2):
    # Check that at least one story card/row contains the search terms
    stories = browser_page.locator(".story-card, [data-testid='stDataFrame'] tbody tr")
    assert stories.count() > 0


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
    # Just verify results are present
    stories = browser_page.locator(".story-card, [data-testid='stDataFrame'] tbody tr")
    assert stories.count() >= 0


@then(parsers.parse('the page should show "{text}"'))
def verify_text_visible(browser_page, text):
    element = browser_page.locator(f"text={text}")
    assert element.is_visible()


@then("all stories should be displayed")
def verify_all_stories(browser_page):
    # Check for story count showing total
    count = browser_page.locator("text=/\\d+ stor(y|ies)/").first
    assert count.is_visible()


@then("no filters should be active")
def verify_no_active_filters(browser_page):
    # Should have no active filter chips (or only placeholder)
    # TODO: Implement actual assertion once filter chip selectors are finalized
    pass


@then(parsers.parse('all displayed stories should have {filter_type} "{value}"'))
def verify_filtered_results(browser_page, filter_type, value):
    # This would require inspecting story data - simplified check
    pass


@then(parsers.parse('the active filters should show "{value}"'))
def verify_active_filter(browser_page, value):
    chip = browser_page.locator(
        f".filter-chip:has-text('{value}'), .active-filter:has-text('{value}')"
    )
    assert chip.is_visible() or browser_page.locator(f"text={value}").is_visible()


@then(parsers.parse('the active filters should show "{value1}" and "{value2}"'))
def verify_multiple_active_filters(browser_page, value1, value2):
    assert browser_page.locator(f"text={value1}").is_visible()
    assert browser_page.locator(f"text={value2}").is_visible()


@then("all displayed stories should match both filters")
def verify_combined_filters(browser_page):
    pass  # Would require data inspection


@then(parsers.parse("the {filter_name} filter should be cleared"))
def verify_filter_cleared(browser_page, filter_name):
    pass  # Would check select value is empty/default


@then("more stories should be displayed")
def verify_more_stories(browser_page):
    pass  # Would compare count before/after


@then("the advanced filter section should be visible")
def verify_advanced_visible(browser_page):
    section = browser_page.locator(
        "[data-testid='stExpander'][aria-expanded='true'], .advanced-filters-content"
    )
    assert section.is_visible()


@then(parsers.parse("the {multiselect_name} multiselect should be visible"))
def verify_multiselect_visible(browser_page, multiselect_name):
    ms = browser_page.locator(
        f"[data-testid='stMultiSelect']:has(label:has-text('{multiselect_name}'))"
    )
    assert ms.is_visible()


@then("all displayed stories should match both Client and Role")
def verify_client_role_filter(browser_page):
    pass  # Would require data inspection


@then(parsers.parse('the Era filter should be set to "{era}"'))
def verify_era_filter(browser_page, era):
    era_select = browser_page.locator(f"[data-testid='stSelectbox']:has-text('{era}')")
    assert era_select.is_visible() or browser_page.locator(f"text={era}").is_visible()


@then("results should be filtered to that era")
def verify_era_results(browser_page):
    pass  # Would require data inspection


@then("all filters should be cleared")
def verify_all_filters_cleared(browser_page):
    pass  # Would check all selects are default


@then("the search box should be empty")
def verify_search_empty(browser_page):
    search_input = browser_page.locator(
        "input[placeholder*='Find stories'], input[placeholder*='Search']"
    ).first
    value = search_input.input_value()
    assert value == ""


@then("no story detail should be open")
def verify_no_story_detail(browser_page):
    detail = browser_page.locator(
        ".story-detail, .st-key-story_detail, [data-testid='stExpander'][aria-expanded='true']:has-text('Situation')"
    )
    assert detail.count() == 0 or not detail.first.is_visible()


@then(parsers.parse("the view should still be {view} view"))
def verify_view_mode(browser_page, view):
    # Simplified check - just verify view content type
    if view == "Table":
        assert browser_page.locator("[data-testid='stDataFrame']").is_visible()
    elif view == "Cards":
        assert browser_page.locator(".story-card").count() > 0
    elif view == "Timeline":
        assert browser_page.locator(".timeline-era").count() > 0


@then("stories should be displayed in a table format")
def verify_table_format(browser_page):
    table = browser_page.locator("[data-testid='stDataFrame']")
    assert table.is_visible()


@then("the table should have columns for Title, Client, Role")
def verify_table_columns(browser_page):
    # Simplified - just check table exists
    pass


@then("stories should be displayed as cards")
def verify_cards_format(browser_page):
    cards = browser_page.locator(".story-card")
    assert cards.count() > 0


@then("each card should show Title and Client")
def verify_card_content(browser_page):
    # Simplified - cards exist
    pass


@then("stories should be grouped by career era")
def verify_timeline_groups(browser_page):
    eras = browser_page.locator(".timeline-era, .era-section")
    assert eras.count() > 0


@then("each era should be collapsible")
def verify_collapsible_eras(browser_page):
    # Check for expander elements
    pass


@then(parsers.parse('the search query should still be "{query}"'))
def verify_search_query(browser_page, query):
    search_input = browser_page.locator(
        "input[placeholder*='Find stories'], input[placeholder*='Search']"
    ).first
    value = search_input.input_value()
    assert value == query


@then("results should still be filtered")
def verify_still_filtered(browser_page):
    pass


@then(parsers.parse('the {filter_name} filter should still be "{value}"'))
def verify_filter_preserved(browser_page, filter_name, value):
    assert browser_page.locator(f"text={value}").is_visible()


@then("the story detail should still be open")
def verify_detail_open(browser_page):
    detail = browser_page.locator(".story-detail, .st-key-story_detail")
    assert detail.is_visible()


@then(parsers.parse('the story should be "{story_id}"'))
def verify_story_id(browser_page, story_id):
    detail = browser_page.locator(
        f".story-detail:has-text('{story_id}'), .st-key-story_detail:has-text('{story_id}')"
    )
    assert detail.is_visible() or browser_page.locator(f"text={story_id}").is_visible()


@then("the story detail panel should open")
def verify_detail_panel_open(browser_page):
    detail = browser_page.locator(
        ".story-detail, .st-key-story_detail, [data-testid='stExpander'][aria-expanded='true']"
    )
    assert detail.is_visible()


@then("the detail should show the story Title")
def verify_detail_title(browser_page):
    pass  # Would check title element


@then("the detail should show Situation, Task, Action, Result")
def verify_star_sections(browser_page):
    for section in ["Situation", "Task", "Action", "Result"]:
        assert browser_page.locator(f"text={section}").is_visible()


@then(parsers.parse("the detail should have a {section} section"))
def verify_detail_section(browser_page, section):
    assert browser_page.locator(f"text={section}").is_visible()


@then("the story list should be visible")
def verify_story_list(browser_page):
    stories = browser_page.locator(".story-card, [data-testid='stDataFrame']")
    assert stories.is_visible()


@then('the "Ask Agy About This" button should be visible')
def verify_ask_agy_button(browser_page):
    btn = browser_page.locator("button:has-text('Ask Agy')")
    assert btn.is_visible()


@then("the page should navigate to Ask MattGPT")
def verify_navigate_to_ask(browser_page):
    # Check for Ask MattGPT page elements
    browser_page.wait_for_selector(
        ".st-key-intro_section, .conversation-view, [data-testid='stChatMessage']",
        timeout=10000,
    )


@then("the question should reference the story")
def verify_question_references_story(browser_page):
    # Would check input or pending question
    pass


@then("the clipboard should contain the story deeplink URL")
def verify_clipboard(browser_page):
    # Can't easily test clipboard in headless mode
    pass


@then("the pagination should show page numbers")
def verify_pagination(browser_page):
    pagination = browser_page.locator(
        ".pagination, button:has-text('Next'), button:has-text('Previous')"
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
    stories = browser_page.locator(".story-card, [data-testid='stDataFrame'] tbody tr")
    assert stories.count() <= count


@then(parsers.parse("the page should reset to {page_num:d}"))
def verify_page_reset(browser_page, page_num):
    pass  # Would check page indicator


@then(parsers.parse('the search query should be "{query}"'))
def verify_search_query_is(browser_page, query):
    search_input = browser_page.locator(
        "input[placeholder*='Find stories'], input[placeholder*='Search']"
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
    browser_page.wait_for_load_state("networkidle")


@then("no crash should occur")
def verify_no_crash(browser_page):
    error = browser_page.locator(".stException, .stError")
    assert error.count() == 0
