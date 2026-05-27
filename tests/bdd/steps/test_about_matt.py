"""
BDD Step Definitions for About Matt — Content polish bundle (MATTGPT-068).

Red (step defs) gate state: step definitions bound, scenarios run end-to-end
against the unchanged About Matt page. All 7 are expected to fail with
AssertionError (not StepDefinitionNotFoundError, not ImportError, not
raw TimeoutError before any assertion runs). The Green commit will add the
production code that flips these to passing.

DOM-observable assertions only — Playwright cannot read st.session_state.
For click-routing (Scenario 3), we assert navigation visible + user message
echo + assistant response streaming, which is functionally equivalent to
asserting seed_prompt + active_tab + __ask_from_suggestion__ session-state
mutation.

ABOUT_MATT_SEED_QUESTIONS does not exist in production yet (it lands in
Green). The Scenario 2 step that references it does a lazy import inside
the step body so the file imports cleanly at collection time, and the
missing constant surfaces as an AssertionError at runtime — which is
exactly the Red (step defs) state we want.

Run with: pytest tests/bdd/steps/test_about_matt.py -v
Requires: streamlit run app.py on localhost:8501.
"""

from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/about_matt.feature")

# =============================================================================
# CONSTANTS
# =============================================================================

SHORT_WAIT = 200  # ms — quick UI updates after a Streamlit rerun
LONG_TIMEOUT = 15000  # ms — Streamlit rerun + initial render
NAV_TIMEOUT = 10000  # ms — top-nav click landing
CLICK_TIMEOUT = 5000  # ms — element-must-exist click target

# Legacy <li> sample-question lines from about_matt.py:1199-1204. Per
# CLAUDE.md "no hardcoded strings in guards" — kept here as a named
# constant so the assertion target is a single, reviewable list. Once
# Green removes them from production, this constant is the contract a
# future change would need to satisfy to prove the strings stay gone.
LEGACY_SAMPLE_QUESTION_LINES = [
    '"How did Matt scale engineering teams from 4 to 150+ people?"',
    '"What were the biggest challenges at the Accenture Innovation Center?"',
    '"Show me examples of agile transformation with measurable outcomes"',
    '"Tell me about a time Matt resolved conflict between senior engineers"',
]


def _wait_for_streamlit_rerun(page):
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


# =============================================================================
# GIVEN — Navigation to About Matt
# =============================================================================


@given("the user navigates to the About Matt page")
def navigate_to_about_matt(browser_page, app_url):
    """Open the app and click the About Matt tab in the top nav.

    The .about-header div is unique to About Matt (ui/pages/about_matt.py
    line 842) and is the first element rendered on the page — its visibility
    confirms the active_tab switch landed and the page rendered.

    Click pattern: dispatch_event("click") on the hidden Streamlit button
    (rather than .click()) mirrors test_home.py:114 and test_home.py:226 —
    bypasses any JS bridge in the navbar component and isolates the test
    to the Streamlit button → rerun cycle. See test_home.py docstring at
    click_view_product_work for full rationale.

    Both navigation operations are wrapped so that any selector mismatch
    surfaces as an AssertionError (Red gate proof requirement) rather than
    a raw Playwright TimeoutError that would muddy the failure mode.
    """
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    try:
        nav_btn = browser_page.locator("[class*='st-key-topnav_About'] button").first
        nav_btn.wait_for(state="visible", timeout=NAV_TIMEOUT)
        nav_btn.dispatch_event("click")
    except Exception as exc:
        raise AssertionError(
            "About Matt top-nav button not found within "
            f"{NAV_TIMEOUT}ms. Selector "
            "'[class*=\"st-key-topnav_About\"] button' did not match a "
            "visible element — navbar key pattern may have changed. "
            f"Underlying error: {exc}"
        ) from exc
    _wait_for_streamlit_rerun(browser_page)
    try:
        browser_page.wait_for_selector(".about-header", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "About Matt page did not render within "
            f"{LONG_TIMEOUT}ms after clicking the top-nav button. "
            "Expected .about-header div not visible — page structure may "
            f"have changed. Underlying error: {exc}"
        ) from exc


# =============================================================================
# SCENARIO 1 — Four sample question buttons in See It In Action card
# (Was Scenario 2 before the May 27, 2026 amendments dropped anchor nav
# and reverted the stats-bar parity decision.)
# =============================================================================


def _see_it_in_action_card(page):
    """Locator for the See It In Action CTA card.

    Implementation note (May 27, 2026 amendment): the card is rendered via
    st.container(key="about_matt_cta_card"), which Streamlit emits with a
    class containing st-key-about_matt_cta_card. The container takes the
    visual .cta-card styling AND scopes the four sample-question buttons
    as DOM children — that lets the chip-containment test assert true DOM
    nesting (per the wireframe), not just visual proximity.
    """
    return page.locator("[class*='st-key-about_matt_cta_card']").first


# Gherkin uses the literal word "four" rather than the digit 4; bound as a
# literal string-match step rather than parametrized. The expected count is
# locked at 4 per MATTGPT-068 (one button per ABOUT_MATT_SEED_QUESTIONS entry).
EXPECTED_SAMPLE_QUESTION_COUNT = 4


@then("four sample question buttons should be visible in the See It In Action card")
def assert_sample_question_button_count(browser_page):
    card = _see_it_in_action_card(browser_page)
    try:
        card.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            ".cta-card with 'See It In Action' heading not visible within "
            f"{LONG_TIMEOUT}ms. Underlying error: {exc}"
        ) from exc
    # Scope the button query INSIDE the card container — per the May 27, 2026
    # wireframe amendment, the chips must be DOM-nested inside the CTA card,
    # not visual-only siblings. card.locator(...) enforces that contract.
    btns = card.locator("[class*='st-key-about_matt_sample_q_'] button")
    actual = btns.count()
    assert actual == EXPECTED_SAMPLE_QUESTION_COUNT, (
        f"Expected {EXPECTED_SAMPLE_QUESTION_COUNT} sample-question buttons "
        f"(keys like st-key-about_matt_sample_q_<idx>) DOM-nested inside the "
        f"See It In Action card container, found {actual}. Per MATTGPT-068 "
        f"(May 27 wireframe amendment), the four <li> prompts at "
        f"about_matt.py:1199-1204 must become four st.button calls rendered "
        f"inside the st.container(key='about_matt_cta_card') wrapper."
    )


@then("each button label should match a string in ABOUT_MATT_SEED_QUESTIONS")
def assert_button_labels_match_constant(browser_page):
    try:
        from ui.pages.about_matt import ABOUT_MATT_SEED_QUESTIONS
    except ImportError as exc:
        raise AssertionError(
            "ABOUT_MATT_SEED_QUESTIONS is not defined in ui/pages/about_matt.py. "
            "Per MATTGPT-068, the four sample-question strings must be exposed "
            "as a module-level constant so BDD + eval can import them. "
            f"Import error: {exc}"
        ) from exc
    card = _see_it_in_action_card(browser_page)
    btns = card.locator("[class*='st-key-about_matt_sample_q_'] button")
    labels = [btns.nth(i).inner_text().strip() for i in range(btns.count())]
    extras = [label for label in labels if label not in ABOUT_MATT_SEED_QUESTIONS]
    assert not extras, (
        f"Button labels not present in ABOUT_MATT_SEED_QUESTIONS: {extras}. "
        f"All buttons must source their label from the constant."
    )
    assert len(labels) == len(ABOUT_MATT_SEED_QUESTIONS), (
        f"Button count ({len(labels)}) does not match "
        f"ABOUT_MATT_SEED_QUESTIONS length ({len(ABOUT_MATT_SEED_QUESTIONS)})."
    )


@then("the four legacy <li> sample-question lines should not be present as plain text")
def assert_legacy_li_lines_absent(browser_page):
    card = _see_it_in_action_card(browser_page)
    li_texts = card.locator("li").all_inner_texts()
    leftovers = [
        line
        for line in LEGACY_SAMPLE_QUESTION_LINES
        if any(line in t for t in li_texts)
    ]
    assert not leftovers, (
        f"Legacy <li> sample-question lines still rendering as plain text "
        f"inside .cta-card: {leftovers}. Per MATTGPT-068, these must be "
        f"replaced by st.button calls."
    )


# =============================================================================
# SCENARIO 2 — Click routes to Ask MattGPT and auto-fires the question
# =============================================================================


@when("the user clicks the first sample question button")
def click_first_sample_question(browser_page):
    btn = browser_page.locator("[class*='st-key-about_matt_sample_q_0'] button").first
    try:
        btn.wait_for(state="visible", timeout=CLICK_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "First sample question button "
            "(key='about_matt_sample_q_0') not found within "
            f"{CLICK_TIMEOUT}ms. Per MATTGPT-068, this button must exist. "
            f"Underlying error: {exc}"
        ) from exc
    # dispatch_event("click") matches test_home.py — bypasses any JS bridge
    # and isolates the test to the Streamlit click → rerun cycle.
    btn.dispatch_event("click")
    _wait_for_streamlit_rerun(browser_page)


@then("the Ask MattGPT conversation view should be visible")
def assert_ask_mattgpt_conversation_visible(browser_page):
    # .stChatMessage is unique to the Ask MattGPT conversation view —
    # the landing view doesn't render chat messages. Its presence proves
    # the active_tab switch + seed-prompt auto-fire both happened.
    try:
        browser_page.wait_for_selector(".stChatMessage", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "Ask MattGPT conversation view did not render within "
            f"{LONG_TIMEOUT}ms after clicking a sample question. Per "
            "MATTGPT-068, click routing must set active_tab='Ask MattGPT' "
            "and trigger seed_prompt auto-fire so a chat transcript appears. "
            f"Underlying error: {exc}"
        ) from exc


@then("a user message matching that button's label should be visible in the chat")
def assert_user_message_matches_button_label(browser_page):
    try:
        from ui.pages.about_matt import ABOUT_MATT_SEED_QUESTIONS
    except ImportError as exc:
        raise AssertionError(
            "ABOUT_MATT_SEED_QUESTIONS not defined in ui/pages/about_matt.py — "
            "cannot verify that the chat shows the matching prompt. "
            f"Import error: {exc}"
        ) from exc
    expected = ABOUT_MATT_SEED_QUESTIONS[0]
    # First 40 chars are enough to identify the message uniquely.
    snippet = expected[:40].replace("'", "\\'")
    msg = browser_page.locator(f".stChatMessage:has-text('{snippet}')").first
    try:
        msg.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            f"User message matching first sample-question label "
            f"({expected!r}) did not appear in the chat. Seed-prompt "
            f"auto-fire did not run as expected. Underlying error: {exc}"
        ) from exc


@then("an assistant response should begin streaming in the chat")
def assert_assistant_response_streams(browser_page):
    # Two .stChatMessage elements = user turn + assistant turn. The
    # assistant turn appearing within the timeout proves the backend RAG
    # pipeline kicked off (streaming or completed).
    try:
        browser_page.wait_for_function(
            "() => document.querySelectorAll('.stChatMessage').length >= 2",
            timeout=LONG_TIMEOUT,
        )
    except Exception as exc:
        raise AssertionError(
            "Assistant response did not begin streaming within "
            f"{LONG_TIMEOUT}ms after the user message appeared. Seed-prompt "
            "auto-fire may have set the prompt but failed to trigger backend "
            f"processing. Underlying error: {exc}"
        ) from exc


# =============================================================================
# SCENARIO 3 — Redundant CTA footer copy removed
# =============================================================================


@then(parsers.parse('the text "{needle}" should not appear on the page'))
def assert_text_absent(browser_page, needle):
    body_text = browser_page.locator("body").inner_text()
    assert needle not in body_text, (
        f"Text {needle!r} is still present on the About Matt page. "
        f"Per MATTGPT-068, the redundant CTA footer copy at "
        f"about_matt.py:1205-1208 must be removed once sample questions are "
        f"clickable."
    )


# =============================================================================
# SCENARIO 4 — DevOps & Quality merged into CI/CD Pipeline card
# =============================================================================


def _detail_card_by_heading(page, heading):
    return page.locator(
        ".detail-card", has=page.locator(f"h4:has-text('{heading}')")
    ).first


@then(parsers.parse('no detail card with the heading "{heading}" should be visible'))
def assert_detail_card_absent(browser_page, heading):
    headings = browser_page.locator(".detail-card h4").all_inner_texts()
    assert heading not in headings, (
        f"A .detail-card with heading {heading!r} is still visible "
        f"(headings found: {headings}). Per MATTGPT-068, the DevOps & "
        f"Quality card must be merged into the CI/CD Pipeline card."
    )


@then(parsers.parse('the "{heading}" detail card should be visible'))
def assert_detail_card_visible(browser_page, heading):
    card = _detail_card_by_heading(browser_page, heading)
    try:
        card.wait_for(state="visible", timeout=CLICK_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            f"Expected .detail-card with heading {heading!r} to be visible. "
            f"Underlying error: {exc}"
        ) from exc


@then(parsers.parse('the "{heading}" detail card should mention {keyword}'))
def assert_detail_card_mentions(browser_page, heading, keyword):
    card = _detail_card_by_heading(browser_page, heading)
    text = card.inner_text().lower()
    assert keyword.lower() in text, (
        f"Detail card {heading!r} does not mention {keyword!r}. Per "
        f"MATTGPT-068, the merged CI/CD Pipeline card must carry the "
        f"former DevOps & Quality bullets (testing, monitoring, security)."
    )


# =============================================================================
# SCENARIO 5 — RAG pipeline code block wrapped in collapsed <details>
# =============================================================================


def _code_block_details_locator(page):
    # The code block is .code-block (about_matt.py:1062). Per MATTGPT-068,
    # it must be wrapped in <details> with a <summary>. We look for a
    # <details> ancestor of .code-block.
    return page.locator("details:has(.code-block)").first


@then("the 5-Stage RAG Pipeline code block should be wrapped in a <details> element")
def assert_code_block_wrapped(browser_page):
    actual = browser_page.locator("details:has(.code-block)").count()
    assert actual >= 1, (
        "The .code-block element is not wrapped in a <details> element. "
        "Per MATTGPT-068, the 5-Stage RAG Pipeline code at "
        "about_matt.py:1062-1091 must live inside "
        "<details><summary>Show code</summary>...</details>."
    )


@then('that <details> element should not have the "open" attribute')
def assert_details_collapsed(browser_page):
    if browser_page.locator("details:has(.code-block)").count() < 1:
        raise AssertionError(
            "Cannot assert collapsed state — no <details> wrapping "
            ".code-block exists. The wrapping itself must land first."
        )
    details = _code_block_details_locator(browser_page)
    is_open = details.get_attribute("open")
    assert is_open is None, (
        f"<details> wrapping .code-block has open={is_open!r}. Per "
        f"MATTGPT-068, the code block must be collapsed by default so "
        f"non-technical readers can skip past it."
    )


@then("a <summary> element should be visible as the affordance to expand the code")
def assert_summary_visible(browser_page):
    if browser_page.locator("details:has(.code-block)").count() < 1:
        raise AssertionError(
            "Cannot assert <summary> visibility — no <details> wrapping "
            ".code-block exists. The wrapping itself must land first."
        )
    summary = browser_page.locator("details:has(.code-block) summary").first
    try:
        summary.wait_for(state="visible", timeout=3000)
    except Exception as exc:
        raise AssertionError(
            "<details> wrapping .code-block has no visible <summary> "
            f"element. The expand affordance is missing. Underlying error: {exc}"
        ) from exc
