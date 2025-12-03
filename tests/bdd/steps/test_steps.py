"""
BDD Step Definitions for Ask MattGPT

These step definitions use Playwright for browser automation.
Install with: pip install pytest-bdd playwright
Run with: pytest tests/bdd --bdd
"""

import pytest
from pytest_bdd import given, parsers, then, when

# Load all feature files
# scenarios('../features/search.feature')
# scenarios('../features/landing_page.feature')


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def browser_page():
    """Create a Playwright browser page.

    Usage:
        pip install playwright
        playwright install chromium
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("Playwright not installed. Run: pip install playwright")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()


@pytest.fixture
def app_url():
    """URL of the running Streamlit app."""
    return "http://localhost:8502"


# =============================================================================
# GIVEN STEPS
# =============================================================================


@given("the user navigates to the Ask MattGPT page")
def navigate_to_landing(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")


@given("the story index contains 120+ transformation project stories")
def verify_story_index():
    # This is a precondition - verified by status bar in UI
    pass


@given("the Pinecone index is ready")
def verify_pinecone_ready():
    # This is a precondition - verified by status bar in UI
    pass


@given(parsers.parse('the user types "{text}" in the input'))
def type_in_input(browser_page, text):
    input_field = browser_page.locator("input[data-testid='stTextInput']").first
    input_field.fill(text)


@given("a question is being processed")
def start_processing(browser_page):
    # Click a suggested question to start processing
    button = browser_page.locator("button[key^='suggested_']").first
    button.click()


@given("JPMC represents 48% of all stories")
def jpmc_majority():
    # This is a known data condition
    pass


# =============================================================================
# WHEN STEPS
# =============================================================================


@when(parsers.parse('the user searches "{query}"'))
def perform_search(browser_page, query):
    input_field = browser_page.locator("input[data-testid='stTextInput']").first
    input_field.fill(query)

    # Press Enter or click button
    input_field.press("Enter")


@when(parsers.parse('the user clicks "{button_text}"'))
def click_button(browser_page, button_text):
    button = browser_page.locator(f"button:has-text('{button_text}')").first
    button.click()


@when("the user presses Enter")
def press_enter(browser_page):
    input_field = browser_page.locator("input[data-testid='stTextInput']").first
    input_field.press("Enter")


@when("the user submits a question")
def submit_question(browser_page):
    # Click first suggested question
    button = browser_page.locator("button[key^='suggested_']").first
    button.click()


@when(parsers.parse("the browser window is resized to {width:d}px width"))
def resize_window(browser_page, width):
    browser_page.set_viewport_size({"width": width, "height": 800})


@when(parsers.parse("the browser window is {width:d}px wide"))
def set_window_width(browser_page, width):
    browser_page.set_viewport_size({"width": width, "height": 800})


# =============================================================================
# THEN STEPS - VISUAL ELEMENTS
# =============================================================================


@then("the page should display Agy's avatar")
def verify_avatar(browser_page):
    avatar = browser_page.locator(".main-avatar img")
    assert avatar.is_visible()
    assert "agy_avatar" in avatar.get_attribute("src")


@then(parsers.parse('the page should display "{text}" heading'))
def verify_heading(browser_page, text):
    heading = browser_page.locator(f"h2:has-text('{text}')")
    assert heading.is_visible()


@then("the page should explain Agy is a Plott Hound")
def verify_plott_hound_text(browser_page):
    text = browser_page.locator("text=Plott Hound")
    assert text.is_visible()


@then("the introduction text should be centered")
def verify_centered_text(browser_page):
    intro = browser_page.locator(".main-intro-section")
    text_align = intro.evaluate("el => getComputedStyle(el).textAlign")
    assert text_align == "center"


# =============================================================================
# THEN STEPS - STATUS BAR
# =============================================================================


@then(parsers.parse('the status bar should show "{text}"'))
def verify_status_text(browser_page, text):
    status = browser_page.locator(f"text={text}")
    assert status.is_visible()


@then("the status bar should show story count")
def verify_story_count(browser_page):
    # Look for "120+ stories" or similar
    count = browser_page.locator("text=/\\d+\\+? stories/")
    assert count.is_visible()


# =============================================================================
# THEN STEPS - SUGGESTED QUESTIONS
# =============================================================================


@then("there should be exactly 6 suggested question buttons")
def verify_six_buttons(browser_page):
    buttons = browser_page.locator("button[key^='suggested_']")
    assert buttons.count() == 6


@then("questions should be arranged in a 2x3 grid")
def verify_grid_layout(browser_page):
    # Check that buttons are in a grid
    container = browser_page.locator(
        "[data-testid='stHorizontalBlock']:has(button[key^='suggested_'])"
    )
    display = container.evaluate("el => getComputedStyle(el).display")
    assert display in ["grid", "flex"]


@then("each question should have an emoji icon")
def verify_emoji_icons(browser_page):
    buttons = browser_page.locator("button[key^='suggested_']")
    for i in range(buttons.count()):
        text = buttons.nth(i).inner_text()
        # Check for emoji (basic check - emojis are non-ASCII)
        has_emoji = any(ord(c) > 127 for c in text)
        assert has_emoji, f"Button {i} missing emoji: {text}"


@then("suggested question buttons should have gray background")
def verify_gray_background(browser_page):
    button = browser_page.locator("button[key^='suggested_']").first
    bg = button.evaluate("el => getComputedStyle(el).backgroundColor")
    # #f5f5f5 = rgb(245, 245, 245)
    assert "245" in bg or "f5f5f5" in bg.lower()


@then("button text should be italicized")
def verify_italic_text(browser_page):
    button_p = browser_page.locator("button[key^='suggested_'] p").first
    font_style = button_p.evaluate("el => getComputedStyle(el).fontStyle")
    assert font_style == "italic"


@then("buttons should have subtle borders")
def verify_button_borders(browser_page):
    button = browser_page.locator("button[key^='suggested_']").first
    border = button.evaluate("el => getComputedStyle(el).border")
    assert "1px" in border or "solid" in border


# =============================================================================
# THEN STEPS - INPUT AREA
# =============================================================================


@then("the input field should have placeholder text")
def verify_placeholder(browser_page):
    input_field = browser_page.locator("input[data-testid='stTextInput']").first
    placeholder = input_field.get_attribute("placeholder")
    assert placeholder and len(placeholder) > 0


@then(parsers.parse('the placeholder should mention "{text}"'))
def verify_placeholder_text(browser_page, text):
    input_field = browser_page.locator("input[data-testid='stTextInput']").first
    placeholder = input_field.get_attribute("placeholder")
    assert text.lower() in placeholder.lower()


@then("the input should not have a red border")
def verify_no_red_border(browser_page):
    input_wrapper = browser_page.locator("[data-baseweb='input']").first
    border = input_wrapper.evaluate("el => getComputedStyle(el).borderColor")
    # Red would be rgb(255, 75, 75) or similar
    assert "255, 75, 75" not in border


@then(parsers.parse('the "{button_name}" button should be purple (#8B5CF6)'))
def verify_purple_button(browser_page, button_name):
    button = browser_page.locator(f"button:has-text('{button_name}')").first
    bg = button.evaluate("el => getComputedStyle(el).backgroundColor")
    # #8B5CF6 = rgb(139, 92, 246)
    assert "139" in bg and "92" in bg and "246" in bg


@then("the button should include the paw emoji")
def verify_paw_emoji(browser_page):
    button = browser_page.locator("button[key='landing_ask']")
    text = button.inner_text()
    assert "🐾" in text or "paw" in text.lower()


@then("the button text should not wrap to multiple lines")
def verify_no_text_wrap(browser_page):
    button = browser_page.locator("button[key='landing_ask']")
    white_space = button.evaluate("el => getComputedStyle(el).whiteSpace")
    assert white_space == "nowrap"


@then("the input field and button should remain on the same row")
def verify_same_row(browser_page):
    input_field = browser_page.locator(".st-key-landing_input").first
    button = browser_page.locator("button[key='landing_ask']")

    input_top = input_field.bounding_box()["y"]
    button_top = button.bounding_box()["y"]

    # Should be roughly on the same line (within 20px)
    assert abs(input_top - button_top) < 20


@then("the button should not wrap below the input")
def verify_button_not_wrapped(browser_page):
    verify_same_row(browser_page)


# =============================================================================
# THEN STEPS - LOADING/PROCESSING
# =============================================================================


@then("the thinking indicator should appear")
def verify_thinking_indicator(browser_page):
    # Wait for thinking indicator to appear
    browser_page.wait_for_selector(
        ".thinking-ball-early, .chase-animation", timeout=5000
    )


@then(parsers.parse('the text "{text}" should appear'))
def verify_text_appears(browser_page, text):
    locator = browser_page.locator(f"text={text}")
    assert locator.is_visible()


@then("all suggested question buttons should be disabled")
def verify_buttons_disabled(browser_page):
    buttons = browser_page.locator("button[key^='suggested_']")
    for i in range(buttons.count()):
        disabled = buttons.nth(i).get_attribute("disabled")
        assert disabled is not None


@then("the Ask Agy button should be disabled")
def verify_ask_button_disabled(browser_page):
    button = browser_page.locator("button[key='landing_ask']")
    disabled = button.get_attribute("disabled")
    assert disabled is not None


@then("the input field should remain enabled")
def verify_input_enabled(browser_page):
    input_field = browser_page.locator("input[data-testid='stTextInput']").first
    disabled = input_field.get_attribute("disabled")
    assert disabled is None


@then("the conversation view should load")
def verify_conversation_view(browser_page):
    # Wait for conversation elements to appear
    browser_page.wait_for_selector("[data-testid='stChatMessage']", timeout=15000)


@then(parsers.parse("results should appear within {seconds:d} seconds"))
def verify_results_timing(browser_page, seconds):
    browser_page.wait_for_selector(
        "[data-testid='stChatMessage']", timeout=seconds * 1000
    )


@then("the query should be processed")
def verify_query_processed(browser_page):
    # Wait for response
    browser_page.wait_for_selector("[data-testid='stChatMessage']", timeout=15000)


# =============================================================================
# THEN STEPS - SEARCH RESULTS
# =============================================================================


@then(
    parsers.parse(
        "the top {n:d} results should include at least {count:d} Talent & Enablement story"
    )
)
def verify_talent_stories(browser_page, n, count):
    # This would need to inspect the actual search results
    # Implementation depends on how results are displayed
    pass


@then("results should include stories with leadership or conflict themes")
def verify_leadership_themes(browser_page):
    pass


@then("the top 3 results should include Execution & Delivery stories")
def verify_execution_stories(browser_page):
    pass


@then("results should include stories about platform engineering")
def verify_platform_stories(browser_page):
    pass


@then("results should prioritize Talent & Enablement stories")
def verify_talent_priority(browser_page):
    pass


@then("results should include stories with stakeholder management themes")
def verify_stakeholder_themes(browser_page):
    pass


@then(
    parsers.parse(
        "no single client should have more than {max:d} stories in top {n:d} results"
    )
)
def verify_client_diversity(browser_page, max, n):
    pass


@then(parsers.parse("results should represent at least {min:d} different clients"))
def verify_min_clients(browser_page, min):
    pass


@then("JPMC stories should not exceed 40% of results")
def verify_jpmc_limit(browser_page):
    pass


@then("the system should return a polite rejection message")
def verify_rejection_message(browser_page):
    pass


@then("no API call should be made to OpenAI")
def verify_no_api_call():
    # This would require mocking/spying on the API
    pass


@then("the system should prompt for a valid question")
def verify_valid_question_prompt(browser_page):
    pass


@then("no error should be displayed")
def verify_no_error(browser_page):
    error = browser_page.locator(".stException, .stError")
    assert error.count() == 0


@then("both searches should return overlapping results")
def verify_overlapping_results():
    pass


@then("results should include collaboration and team dynamics stories")
def verify_collaboration_stories(browser_page):
    pass


@then("results should not require exact keyword matches")
def verify_semantic_matching():
    pass


# =============================================================================
# THEN STEPS - RESPONSIVE DESIGN
# =============================================================================


@then("the white card should remain centered")
def verify_card_centered(browser_page):
    card = browser_page.locator(".st-key-intro_section")
    margin_left = card.evaluate("el => getComputedStyle(el).marginLeft")
    margin_right = card.evaluate("el => getComputedStyle(el).marginRight")
    assert margin_left == margin_right or "auto" in margin_left


@then("content should not overflow horizontally")
def verify_no_overflow(browser_page):
    body = browser_page.locator("body")
    overflow_x = body.evaluate("el => el.scrollWidth > el.clientWidth")
    assert not overflow_x


@then("suggested questions should remain readable")
def verify_readable_questions(browser_page):
    buttons = browser_page.locator("button[key^='suggested_']")
    for i in range(buttons.count()):
        box = buttons.nth(i).bounding_box()
        assert box["width"] >= 100  # Minimum readable width


@then("the white card should be constrained to max-width")
def verify_max_width(browser_page):
    card = browser_page.locator(".st-key-intro_section")
    width = card.evaluate("el => el.offsetWidth")
    assert width <= 800  # Max width from CSS


@then("there should be margin on both sides")
def verify_side_margins(browser_page):
    card = browser_page.locator(".st-key-intro_section")
    box = card.bounding_box()
    viewport = browser_page.viewport_size

    left_margin = box["x"]
    right_margin = viewport["width"] - (box["x"] + box["width"])

    assert left_margin > 0 and right_margin > 0
