"""
BDD Step Definitions for Home Page Category Cards.

Wired scenarios:
- Card 3 (Product Innovation prefilter) — regression for the May 12, 2026
  broken-prefilter bug.
- Ask Agy Anything chips (3 of 5 scenarios) — regression-worthy subset of
  the May 13, 2026 chip CX rollout: chip click sets seed_prompt + flags,
  Ask Agy button does NOT prefill, and chips render with the ↗ affordance.

Documented-but-pending scenarios (Cards 1, 2, 4, 5, 6 and Ask Agy chip
scenarios 3+4) are acceptance criteria; step defs roll in under MATTGPT-060.

Install Playwright with: pip install playwright && playwright install chromium
Run with: pytest tests/bdd -k home
"""

import re

from pytest_bdd import given, parsers, scenario, then, when

# =============================================================================
# WAIT UTILITIES (mirrors test_explore_stories.py)
# =============================================================================

SHORT_WAIT = 200  # ms — quick UI updates
MEDIUM_WAIT = 500  # ms — component renders


# Literal chip question strings for the Ask Agy Anything section. Order is
# load-bearing — chip 0 maps to the hidden Streamlit button card_btn_ask_chip_0
# (CIC scale), chip 1 to card_btn_ask_chip_1 (startup-pace teams), chip 2 to
# card_btn_ask_chip_2 (resistance). The click handler in
# ui/components/category_cards.py renders chips in this same order.
#
# Single-contract triple: if these strings change, update ALL THREE locations
# together — home.feature scenarios, tests/unit/test_category_cards.py
# CHIP_QUESTIONS, and tests/eval_rag_quality.py entries 62-64. The three
# files form one contract; out-of-sync edits break either the BDD wiring or
# the eval quality pinning.
CHIP_QUESTIONS = [
    "How did Matt scale a Cloud Innovation Center from 0 to 150+ engineers?",
    "How does Matt build teams that ship like startups in enterprise?",
    "How does Matt manage resistance when leading enterprise transformation programs?",
]


def wait_for_streamlit_rerun(page):
    """Wait for Streamlit to complete a rerun after an action."""
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


# =============================================================================
# CARD 3 SCENARIO — Product Innovation prefilter regression test
# Loads only this scenario from home.feature. Other scenarios in the same
# feature file are documented acceptance criteria and will run once their
# step defs land (see MATTGPT-060).
# =============================================================================


@scenario(
    "../features/home.feature",
    "Card 3 — Product Innovation prefilters to product Sub-categories",
)
def test_card3_product_innovation_prefilter():
    """Regression test for the May 12, 2026 broken-prefilter bug.

    Prior to fix: card set prefilter_capability='Product Leadership' which is
    not a valid Solution/Offering value. The Capability dropdown widget
    silently sanitized the invalid value to "All", showing 113 unfiltered
    stories. The card's promise was broken — a recruiter saw the entire
    corpus instead of the curated product slice.

    After fix: card sets prefilter_domains with 5 valid Sub-category values
    targeting product work (~10 stories). Result count should be far less
    than 113, and at least one expected product domain chip must be visible.
    """


# =============================================================================
# GIVEN — Navigation
# =============================================================================


@given("the user navigates to the home page")
def navigate_to_home(browser_page, app_url):
    """Home is the default tab when the app loads — no navigation needed.

    Waits for the "View Product Work" anchor to render, which signals the
    category cards section has finished loading.
    """
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    # The Card 3 anchor is a stable target proving category cards have rendered.
    browser_page.wait_for_selector("a#btn-product", timeout=30000)


# =============================================================================
# WHEN — Card click
# =============================================================================


@when('the user clicks "View Product Work" on the Product Innovation card')
def click_view_product_work(browser_page):
    """Click Card 3.

    The visible link is <a id="btn-product">; its click is bridged via JS in
    category_cards.py to a hidden st.button(key="card_btn_product"). We click
    the hidden Streamlit button directly with force=True — bypasses the JS
    bridge and isolates the test to the prefilter business logic (the JS
    bridge is a separate concern with its own coverage).
    """
    btn = browser_page.locator("[class*='st-key-card_btn_product'] button").first
    btn.dispatch_event("click")
    wait_for_streamlit_rerun(browser_page)


# =============================================================================
# THEN — State assertions
# =============================================================================


@then(parsers.parse('the active tab should be "{tab_name}"'))
def assert_active_tab(browser_page, tab_name):
    """Verify navigation landed on the expected tab.

    For Explore Stories: the .results-count element is unique to that page,
    so its presence is a reliable proxy for active_tab == "Explore Stories".
    """
    if tab_name == "Explore Stories":
        browser_page.wait_for_selector(".results-count", timeout=15000)
    else:
        # Other tabs (Banking, Cross-Industry, Home) — assertion stubbed
        # until those scenarios get full step defs (MATTGPT-060).
        pass


@then(parsers.parse("the result count should be less than {limit:d}"))
def assert_result_count_below(browser_page, limit):
    """Verify the prefilter narrowed results below the unfiltered corpus size.

    The .results-count text renders as "Showing N–M of TOTAL projects". We
    extract TOTAL and assert it's below the limit. If the prefilter silently
    fails (the May 12 bug shape), TOTAL would be 113 — the full corpus —
    and this assertion fires.
    """
    count_el = browser_page.locator(".results-count").first
    count_el.wait_for(state="visible", timeout=10000)
    text = count_el.inner_text()
    # Pattern: "Showing 1–10 of 10 projects" — extract the number after "of".
    match = re.search(r"of\s+(\d+)\s+project", text)
    assert match, f"Could not parse total count from results-count text: {text!r}"
    actual = int(match.group(1))
    assert actual < limit, (
        f"Expected result count < {limit}, got {actual}. "
        f"Card 3 prefilter did not apply — the entire corpus is showing. "
        f"This is the May 12, 2026 regression shape."
    )


# =============================================================================
# ASK AGY ANYTHING — suggested-question chips (May 13, 2026)
# Three regression scenarios wired up; two documented-only (chip cleanup
# after fire, default landing render) — they exercise post-rerun chat state
# that's covered indirectly by the seed_prompt unit test and existing
# conversation_view tests.
# =============================================================================


@scenario(
    "../features/home.feature",
    "Ask Agy button navigates without pre-loading a question",
)
def test_ask_agy_button_no_prefill():
    """The "Ask Agy 🐾" primary button is the no-pre-population path —
    navigates to Ask MattGPT and lands on the landing view, not a fired query.
    Pre-implementation: button still exists in current category_cards.py, so
    this should pass against current code. Post-chip-implementation: keeps
    the button distinct from the chips it sits next to.
    """


@scenario(
    "../features/home.feature",
    "Clicking a suggested chip auto-fires the question on Ask MattGPT",
)
def test_chip_click_sets_seed_prompt():
    """Core regression for the chip CX. After click, session state must
    carry the literal question as seed_prompt and the __ask_from_suggestion__
    flag — mirrors story_detail.on_ask_this_story exactly. conversation_view
    handles the rest via its existing seed_prompt consumer.
    """


@scenario(
    "../features/home.feature",
    "Suggested chips render with directional affordance",
)
def test_chips_render_with_arrow():
    """Visual presence check. Three chips must render, each with the ↗
    affordance, and they must look distinct from the Ask Agy primary button.
    Pre-implementation: this fails RED (no chips yet). Post-implementation:
    passes GREEN.
    """


# Pending step defs (MATTGPT-060):
# - "Session state cleared after auto-fire" — requires Streamlit rerun
#   inspection across page transitions; covered by the conversation_view
#   .pop() chain unit-tested elsewhere.
# - "Ask MattGPT renders default landing when no chip was clicked" — covered
#   by the default render path in landing_view.py.


@when('the user clicks "Ask Agy 🐾" on the Ask Agy Anything card')
def click_ask_agy_button(browser_page):
    """Click the primary "Ask Agy 🐾" button in the Quick Question card.

    The visible link is <a id="btn-ask-agy">; click bridged via JS in
    category_cards.py to the hidden st.button(key="card_btn_ask_agy"). We
    click the hidden Streamlit button directly with force=True — bypasses
    the JS bridge and isolates the test to the navigation logic.
    """
    btn = browser_page.locator("[class*='st-key-card_btn_ask_agy'] button").first
    btn.dispatch_event("click")
    wait_for_streamlit_rerun(browser_page)


@when(parsers.parse('the user clicks the suggested chip "{question}"'))
def click_suggested_chip(browser_page, question):
    """Click one of the three suggested-question chips by its text.

    Implementation pattern (locked by this test): chips render as visible
    HTML <button class="chip"> elements bridged via JS to hidden Streamlit
    buttons keyed card_btn_ask_chip_0, card_btn_ask_chip_1, card_btn_ask_chip_2
    in CHIP_QUESTIONS order. This mirrors the rest of category_cards.py
    (Banking/Product/Modernization/etc. all use the same visible-anchor +
    hidden-st.button + JS-bridge pattern).

    Click approach: bypass the JS bridge by clicking the hidden Streamlit
    button directly. Why: the JS bridge lives inside a components.html iframe
    that can be destroyed/recreated by Streamlit reruns (the May 12, 2026
    dead-closure incident — see utils/landing_cards.py header for full
    rationale). Clicking the hidden button isolates this test to chip-click
    business logic and keeps it from flaking on JS-bridge wiring. The JS
    bridge itself is covered by the visible-affordance scenario
    (test_chips_render_with_arrow) and by the parallel pattern's coverage
    in test_banking_landing.py / test_cross_industry_landing.py.

    Caller passes the literal question text; we resolve it to the index via
    CHIP_QUESTIONS lookup. If the chip strings ever change, update them in
    ALL THREE places — home.feature, this file's CHIP_QUESTIONS, and
    tests/eval_rag_quality.py entries 62-64 — they form a single contract.
    """
    idx = CHIP_QUESTIONS.index(question)
    btn = browser_page.locator(
        f"[class*='st-key-card_btn_ask_chip_{idx}'] button"
    ).first
    btn.dispatch_event("click")
    wait_for_streamlit_rerun(browser_page)


@then(
    "no seed prompt should be present in session state",
)
def assert_no_seed_prompt(browser_page):
    """Negative assertion for the Ask Agy button path.

    Streamlit session state isn't directly readable from Playwright, so we
    use the proxy: the Ask MattGPT page renders the landing view (input box +
    suggestion chips) instead of an auto-fired conversation transcript. If
    seed_prompt were set, the page would skip the landing and show a
    transcript with the question as the first user turn.
    """
    # Landing view markers pinned to ui/pages/ask_mattgpt/landing_view.py:
    #   - .welcome-title — "Hi, I'm Agy 🐾" heading rendered only on landing
    #   - .suggested-title — "TRY ASKING:" label above the suggestion chips
    # If a query auto-fired, the page skips landing (see
    # ui/pages/ask_mattgpt/__init__.py:48) and these elements never render.
    landing = browser_page.locator(".welcome-title, .suggested-title").first
    landing.wait_for(state="visible", timeout=15000)
    chat = browser_page.locator(".stChatMessage").count()
    assert chat == 0, (
        "Ask Agy button click landed on a conversation with a fired query — "
        "seed_prompt was set when it shouldn't have been. The button path "
        "must NOT pre-populate; only chips do."
    )


@then(parsers.parse('the seed prompt in session state should be "{expected}"'))
def assert_seed_prompt_value(browser_page, expected):
    """Verify the chip-click handler set seed_prompt to the literal question.

    Proxy via the rendered chat: after rerun, conversation_view pops
    seed_prompt and the user turn shows the literal question. We assert the
    question text appears in a .stChatMessage (user role).
    """
    msg = browser_page.locator(f".stChatMessage:has-text('{expected[:40]}')").first
    msg.wait_for(state="visible", timeout=15000)
    assert msg.count() > 0, (
        f"No chat message with the expected question text was rendered. "
        f"The chip-click handler may not have set seed_prompt to "
        f"{expected!r}, or the conversation_view consumer didn't fire it. "
        f"Mirror ui/components/story_detail.py::on_ask_this_story."
    )


@then("the suggestion flag should be set in session state")
def assert_suggestion_flag(browser_page):
    """Verify __ask_from_suggestion__ was set so the nonsense filter doesn't
    misfire on a legitimate chip query. Proxy: the chat response renders
    successfully (no "I'm not sure I understood" redirect banner).
    """
    # Wait for an assistant message — its presence means the query went
    # through the RAG pipeline, not the nonsense-redirect path.
    assistant_msg = browser_page.locator(".stChatMessage").nth(1)
    assistant_msg.wait_for(state="visible", timeout=30000)
    # Negative: nonsense-redirect banner shouldn't be there.
    redirect = browser_page.locator("text=/I.?m not sure I understood/i").count()
    assert redirect == 0, (
        "Chip query was redirected by the nonsense filter — the suggestion "
        "flag (__ask_from_suggestion__) was not set, or wasn't honored. "
        "See backend_service.py:1413 for the consumer."
    )


@then("three suggested-question chips should be visible on the Ask Agy Anything card")
def assert_three_chips_visible(browser_page):
    """Visual presence check. Three .chip buttons on the Home page."""
    chips = browser_page.locator("button.chip")
    chips.first.wait_for(state="visible", timeout=15000)
    count = chips.count()
    assert count == 3, (
        f"Expected 3 suggested-question chips on Home, found {count}. "
        f"Implementation drift from the May 13 2026 chip CX spec."
    )


@then("each chip should display the ↗ directional affordance")
def assert_chips_have_arrow(browser_page):
    """The ::before pseudo-element renders ↗ on each chip. Computed-style
    inspection via JS is the only way to assert pseudo-element content.
    """
    chips = browser_page.locator("button.chip")
    count = chips.count()
    for i in range(count):
        arrow = chips.nth(i).evaluate("el => getComputedStyle(el, '::before').content")
        assert "↗" in arrow or "\\2197" in arrow, (
            f"Chip #{i} is missing the ↗ ::before content. "
            f"Got: {arrow!r}. CSS rule in category_cards.py CSS block "
            f"must declare .chip::before {{ content: '↗'; }}."
        )


@then('each chip should be visually distinct from the "Ask Agy 🐾" primary button')
def assert_chips_distinct_from_button(browser_page):
    """The Ask Agy button is white-on-purple solid; chips are semi-transparent
    white-on-purple outlined. Easiest distinct check: chip background-color
    has alpha < 1 (rgba), button background-color is opaque white.
    """
    chip_bg = browser_page.locator("button.chip").first.evaluate(
        "el => getComputedStyle(el).backgroundColor"
    )
    btn_bg = browser_page.locator("a#btn-ask-agy").first.evaluate(
        "el => getComputedStyle(el).backgroundColor"
    )
    assert chip_bg != btn_bg, (
        f"Chip and Ask Agy button share background-color ({chip_bg}). "
        f"Chips must be visually distinct (semi-transparent rgba vs solid "
        f"white) to prevent recruiters from misreading the chips as the "
        f"primary CTA."
    )


@then(parsers.parse('a filter chip "{value}" should be visible'))
def assert_filter_chip_visible(browser_page, value):
    """Verify the expected prefilter value rendered as an active filter chip.

    Filter chips render as elements with "✕ {value}" text. The existing
    pattern in test_explore_stories.py uses two fallback selectors (button or
    p element) to handle different render paths. We mirror that.
    """
    chip = browser_page.locator(f"button:has-text('✕'):has-text('{value}')").first
    if chip.count() == 0:
        chip = browser_page.locator(f"p:has-text('✕'):has-text('{value}')").first
    assert chip.count() > 0, (
        f"No filter chip with text {value!r} is visible on Explore Stories. "
        f"Card 3 prefilter did not apply the expected Sub-category — the "
        f"page may show 'All' as the active filter state instead."
    )
