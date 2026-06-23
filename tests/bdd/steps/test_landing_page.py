"""
BDD Step Definitions for Ask Agy Landing Page (MATTGPT-139)

Covers: desktop HTML chips, mobile st.button path, input area, responsive layout.
Fixtures (browser_page, app_url) come from conftest.py -- do not redefine here.
Run with: pytest tests/bdd/steps/test_landing_page.py -v
"""

from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/landing_page.feature")

_ASK_AGY_DESKTOP_NAV = ".st-key-topnav_Ask-Agy button"
_ASK_AGY_MOBILE_NAV = "#mobile-nav-ask"
_MOBILE_BREAKPOINT = 768
_LANDING_INPUT = "[class*='st-key-landing_input'] input[type='text']"
_LANDING_SUBMIT = "[class*='st-key-landing_ask'] button"
# JS bridge fires at 100/300/600/1000ms after chips render; wait for last fire.
_JS_BRIDGE_SETTLE_MS = 1200


def _wait_for_navbar_stable(page, timeout: int = 30000) -> None:
    """Wait until all desktop navbar buttons are present after streamlit_js_eval rerun.

    Matches test_ask_mattgpt.py:_wait_for_navbar_stable -- streamlit_js_eval fires
    on first load, causes a rerun, and briefly removes the navbar from the DOM.
    """
    page.wait_for_function(
        """
        () => {
            const classes = [
                'st-key-topnav_Home',
                'st-key-topnav_My-Work',
                'st-key-topnav_Ask-Agy',
                'st-key-topnav_Role-Match',
                'st-key-topnav_My-Profile'
            ];
            return classes.every(c => document.querySelector('.' + c) !== null);
        }
        """,
        timeout=timeout,
    )


def _wait_for_streamlit_rerun(page):
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)


# =============================================================================
# GIVEN
# =============================================================================


@given(parsers.parse("the viewport is {width:d}px wide"))
def set_viewport_before_nav(browser_page, width):
    # Must fire before navigate_to_landing so _browser_screen_size captures
    # window.innerWidth at the correct width. See app.py:141 -- captured once
    # per session on first load; post-navigation resize has no effect on routing.
    browser_page.set_viewport_size({"width": width, "height": 800})


@given("the user navigates to the Ask Agy page")
def navigate_to_landing(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    viewport_width = browser_page.viewport_size["width"]
    if viewport_width < _MOBILE_BREAKPOINT:
        browser_page.locator("#mobile-hamburger").click()
        browser_page.locator("#mobile-nav-dropdown").wait_for(
            state="visible", timeout=5000
        )
        browser_page.locator(_ASK_AGY_MOBILE_NAV).click()
    else:
        _wait_for_navbar_stable(browser_page)
        browser_page.locator(_ASK_AGY_DESKTOP_NAV).first.click()
        _wait_for_streamlit_rerun(browser_page)
    browser_page.wait_for_selector("[class*='st-key-landing_input']", timeout=15000)
    # Settle for JS bridge -- chips fire setTimeouts at 100/300/600/1000ms after render.
    browser_page.wait_for_timeout(_JS_BRIDGE_SETTLE_MS)


@given(parsers.parse('the user types "{text}" in the input'))
def type_in_input(browser_page, text):
    # press_sequentially fires real key events React picks up in headless mode.
    # fill() sets DOM value but Streamlit's React doesn't see it. See submit_query
    # in test_ask_mattgpt.py for the full history of failed approaches.
    inp = browser_page.locator(_LANDING_INPUT)
    inp.first.click()
    inp.first.press_sequentially(text, delay=20)


# =============================================================================
# WHEN
# =============================================================================


@when(parsers.parse("the viewport is {width:d}px wide"))
def resize_viewport_post_nav(browser_page, width):
    # CSS-only mid-test resize. Does NOT affect is_mobile routing (_browser_screen_size
    # is already locked from navigation). Use only for scenarios testing CSS layout
    # at a specific width, not code-path selection. Distinct from the Given step above.
    browser_page.set_viewport_size({"width": width, "height": 800})


@when("the user clicks the first suggestion chip")
def click_first_chip(browser_page):
    # Bridge settle already done in navigate_to_landing; click is safe here.
    browser_page.locator(".suggested-chip").first.click()


@when(parsers.parse('the user clicks the "{button_text}" button'))
def click_named_button(browser_page, button_text):
    browser_page.locator(f"button:has-text('{button_text}')").first.click()


@when("the user presses Enter")
def press_enter(browser_page):
    browser_page.locator(_LANDING_INPUT).first.press("Enter")


# =============================================================================
# THEN -- VISUAL ELEMENTS
# =============================================================================


@then("the page should display Agy's avatar")
def verify_avatar(browser_page):
    assert browser_page.locator(".main-avatar img").is_visible()


@then(parsers.parse('the page should display "{text}" heading'))
def verify_heading(browser_page, text):
    assert browser_page.locator(f'h2:has-text("{text}")').is_visible()


@then("the page should explain Agy is a Plott Hound")
def verify_plott_hound(browser_page):
    assert browser_page.locator("text=Plott Hound").is_visible()


@then(parsers.parse('the status bar should show "{text}"'))
def verify_status_text(browser_page, text):
    assert browser_page.locator(f"text={text}").is_visible()


@then("the status bar should show story count")
def verify_story_count(browser_page):
    assert browser_page.locator("text=/\\d+\\+? stories/").first.is_visible()


# =============================================================================
# THEN -- DESKTOP CHIPS
# =============================================================================


@then("there should be exactly 6 suggestion chips in the chip grid")
def verify_six_chips(browser_page):
    assert browser_page.locator(".suggested-chip").count() == 6


@then("each chip should have an emoji icon")
def verify_chip_emojis(browser_page):
    chips = browser_page.locator(".suggested-chip")
    for i in range(chips.count()):
        text = chips.nth(i).inner_text()
        assert any(ord(c) > 127 for c in text), f"Chip {i} missing emoji: {text}"


@then("the chip grid should use a 2-column CSS grid layout")
def verify_chip_grid_columns(browser_page):
    columns = browser_page.locator(".suggested-chips-grid").evaluate(
        "el => getComputedStyle(el).gridTemplateColumns"
    )
    # Asserts track count == 2, not that track values are equal.
    # A 1fr 1fr grid resolves to e.g. "400px 400px" -- two space-separated values.
    assert len(columns.split()) == 2, f"Expected 2-column grid, got: {columns}"


@then(
    parsers.parse(
        'the suggestion chips should be HTML button elements with class "{cls}"'
    )
)
def verify_chip_element_type(browser_page, cls):
    assert browser_page.locator(f"button.{cls}").count() == 6


@then("no visible Streamlit button widget should exist in the chip grid")
def verify_no_visible_streamlit_buttons(browser_page):
    # Hidden receivers are pushed off-screen via CSS (left: -9999px).
    # Playwright considers off-screen elements visible if they have a bounding box;
    # assert x < 0 (off left edge) instead of is_visible().
    for i in range(6):
        btn = browser_page.locator(f'[class*="st-key-suggested_{i}"] button')
        if btn.count() > 0:
            box = btn.first.bounding_box()
            assert (
                box is None or box["x"] < 0
            ), f"Streamlit receiver button {i} appears on-screen (x={box['x'] if box else 'no box'})"


@then("the thinking indicator should appear")
def verify_thinking_indicator(browser_page):
    browser_page.wait_for_selector(".thinking-modal", timeout=8000)


@then("the conversation view should load")
def verify_conversation_view(browser_page):
    browser_page.wait_for_selector("[data-testid='stChatMessage']", timeout=30000)


@then("the hidden receiver buttons should have the disabled attribute")
def verify_receivers_disabled(browser_page):
    # Wait for processing to be confirmed active, then assert disabled on all 6 receivers.
    browser_page.wait_for_selector(".thinking-modal", timeout=8000)
    for i in range(6):
        btn = browser_page.locator(f'[class*="st-key-suggested_{i}"] button')
        assert (
            btn.first.get_attribute("disabled") is not None
        ), f"Receiver button {i} is not disabled during processing"


# =============================================================================
# THEN -- MOBILE BUTTONS
# =============================================================================


@then("there should be exactly 6 Streamlit suggestion buttons")
def verify_six_mobile_buttons(browser_page):
    # :visible excludes hidden desktop receivers pushed off-screen via CSS.
    assert (
        browser_page.locator('[class*="st-key-suggested_"] button:visible').count() == 6
    )


@then("the buttons should display short labels not full query text")
def verify_mobile_short_labels(browser_page):
    # :visible excludes hidden desktop receivers. Full query text is always >50 chars;
    # short labels are <=30 chars.
    buttons = browser_page.locator('[class*="st-key-suggested_"] button:visible')
    for i in range(buttons.count()):
        text = buttons.nth(i).inner_text().strip()
        assert (
            len(text) <= 30
        ), f"Button {i} looks like full query text ({len(text)} chars): {text}"


@then(parsers.parse('the first button should contain "{label}"'))
def verify_first_button_label(browser_page, label):
    text = browser_page.locator(
        '[class*="st-key-suggested_0"] button:visible'
    ).inner_text()
    assert label in text, f"Expected '{label}' in first button, got: '{text}'"


# =============================================================================
# THEN -- INPUT AREA
# =============================================================================


@then("the input field should have placeholder text")
def verify_placeholder(browser_page):
    placeholder = browser_page.locator(_LANDING_INPUT).first.get_attribute(
        "placeholder"
    )
    assert placeholder and len(placeholder) > 0


@then("the input should not have a red border")
def verify_no_red_border(browser_page):
    border = browser_page.locator("[data-baseweb='input']").first.evaluate(
        "el => getComputedStyle(el).borderColor"
    )
    assert "255, 75, 75" not in border


@then("the input field and button should remain on the same row")
def verify_same_row(browser_page):
    input_box = browser_page.locator(_LANDING_INPUT).first.bounding_box()
    button_box = browser_page.locator(_LANDING_SUBMIT).first.bounding_box()
    # Same visual row = elements overlap OR are within 30px of each other.
    # Strict overlap fails because Streamlit's column layout leaves a small gap
    # between the input element bottom and the button top (~22px at 800px viewport).
    input_bottom = input_box["y"] + input_box["height"]
    button_bottom = button_box["y"] + button_box["height"]
    gap = max(0, button_box["y"] - input_bottom, input_box["y"] - button_bottom)
    assert gap < 30, (
        f"Input ({input_box['y']:.0f}-{input_bottom:.0f}) and button "
        f"({button_box['y']:.0f}-{button_bottom:.0f}) are {gap:.0f}px apart (max 30)"
    )


@then("the query should be processed")
def verify_query_processed(browser_page):
    browser_page.wait_for_selector("[data-testid='stChatMessage']", timeout=30000)


@then("the submit button should be visible")
def verify_submit_visible(browser_page):
    assert browser_page.locator(_LANDING_SUBMIT).first.is_visible()


@then("the submit button should be disabled")
def verify_submit_disabled(browser_page):
    assert (
        browser_page.locator(_LANDING_SUBMIT).first.get_attribute("disabled")
        is not None
    )


@then(parsers.parse('the submit button should contain "{label}"'))
def verify_submit_label(browser_page, label):
    text = browser_page.locator(_LANDING_SUBMIT).first.inner_text()
    assert label in text, f"Expected '{label}' in button, got: '{text}'"


@then("the submit button should be a primary button")
def verify_submit_primary(browser_page):
    kind = browser_page.locator(_LANDING_SUBMIT).first.get_attribute("kind")
    assert kind == "primary", f"Expected kind='primary', got: '{kind}'"


# =============================================================================
# THEN -- RESPONSIVE DESIGN
# =============================================================================


@then("content should not overflow horizontally")
def verify_no_overflow(browser_page):
    overflow = browser_page.locator("body").evaluate(
        "el => el.scrollWidth > el.clientWidth"
    )
    assert not overflow


@then("the intro section should be centered")
def verify_intro_centered(browser_page):
    box = browser_page.locator(".st-key-intro_section").bounding_box()
    viewport = browser_page.viewport_size
    left_margin = box["x"]
    right_margin = viewport["width"] - (box["x"] + box["width"])
    assert (
        abs(left_margin - right_margin) < 20
    ), f"Left margin ({left_margin:.0f}px) != right margin ({right_margin:.0f}px)"


@then("there should be margin on both sides")
def verify_side_margins(browser_page):
    box = browser_page.locator(".st-key-intro_section").bounding_box()
    viewport = browser_page.viewport_size
    assert box["x"] > 0
    assert viewport["width"] - (box["x"] + box["width"]) > 0
