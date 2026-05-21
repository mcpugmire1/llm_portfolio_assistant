"""
BDD Step Definitions for Ask MattGPT — Nonsense rejection banner + chip sets.

Implements the 10 scenarios in tests/bdd/features/ask_mattgpt.feature.
Step definitions use Playwright (via the shared browser_page fixture in
conftest.py) to drive the running Streamlit app at localhost:8501.

Constants (RULE_CHIPS, PERSONAL_CHIPS, OUT_OF_SCOPE_CHIPS, BANNER_COPY)
are imported from utils/ui_helpers.py — single source of truth. Chip
copy edits change utils/ui_helpers.py only; this test file picks up the
new values automatically.

Red-B state: step defs bound, scenarios run end-to-end. Assertions fail
because render_no_match_banner does not yet consume the branch-aware
constants — it still renders the generic 4-chip set + catch-all banner
copy for rule:* and low_confidence. The Blue commit replaces the
inline chip list and adds branch-aware copy + low_confidence chip
suppression.

Run with: pytest tests/bdd/steps/test_ask_mattgpt.py -v
(requires `streamlit run app.py` running on localhost:8501)
"""

from pytest_bdd import given, parsers, scenarios, then, when

from utils.ui_helpers import (
    BANNER_COPY,
    OUT_OF_SCOPE_CHIPS,
    PERSONAL_CHIPS,
    RULE_CHIPS,
)

# Auto-bind all 10 scenarios from the .feature file
scenarios("../features/ask_mattgpt.feature")

# =============================================================================
# WAIT CONSTANTS
# =============================================================================

SHORT_WAIT = 200  # ms — quick UI updates
MEDIUM_WAIT = 500  # ms — component renders
LONG_WAIT = 3000  # ms — query response latency


def wait_for_streamlit_rerun(page):
    """Wait for Streamlit to complete a rerun after an action."""
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


def _wait_for_navbar_stable(page, timeout: int = 30000) -> None:
    """Wait until the desktop navbar is fully rendered AND stays rendered.

    Streamlit reruns after first load when streamlit_js_eval sets the
    _browser_screen_size session var (see app.py:104-113). Without this wait,
    a @given step can land between the first render and the post-rerun render
    when the navbar is briefly absent from the DOM.

    Mirrors tests/bdd/steps/test_role_match.py:_wait_for_navbar_stable —
    Streamlit converts spaces in container keys to dashes in CSS class names,
    so `key="topnav_Ask MattGPT"` produces class `st-key-topnav_Ask-MattGPT`.
    """
    page.wait_for_function(
        """
        () => {
            const classes = [
                'st-key-topnav_Home',
                'st-key-topnav_Explore-Stories',
                'st-key-topnav_Ask-MattGPT',
                'st-key-topnav_Role-Match',
                'st-key-topnav_About-Matt'
            ];
            return classes.every(c => document.querySelector('.' + c) !== null);
        }
        """,
        timeout=timeout,
    )


# Desktop navbar selectors — Streamlit converts spaces in container keys
# to dashes in CSS class names.
ASK_MATTGPT_NAV_SELECTOR = ".st-key-topnav_Ask-MattGPT button"
EXPLORE_STORIES_NAV_SELECTOR = ".st-key-topnav_Explore-Stories button"


# =============================================================================
# HELPERS — selectors and DOM reads
# =============================================================================


def submit_query(page, query: str):
    """Type a query into Ask MattGPT and submit.

    Two render paths:
      - First query: landing view → st.text_input(key="landing_input") +
        st.button(key="landing_ask"). Fill input, click Ask Agy button.
      - Follow-up: conversation view → st.chat_input. Fill + press Enter.

    Detect which is present and use the right path.
    """
    chat_input = page.locator("[data-testid='stChatInput'] textarea")
    landing_input = page.locator("[class*='st-key-landing_input'] input[type='text']")

    if chat_input.count() > 0 and chat_input.first.is_visible():
        chat_input.first.fill(query)
        chat_input.first.press("Enter")
    else:
        # Landing view: drive the input via real keyboard events.
        #
        # Empirically verified May 20, 2026 via screenshot diagnostic: this
        # press_sequentially + Tab sequence triggers Streamlit's onChange,
        # which propagates the value to the server, fires the on_change
        # callback (setting landing_input_submitted=True), reruns the script,
        # AND advances the page past the landing view directly into the
        # conversation view with the query submitted. The landing_ask button
        # is bypassed entirely — its click handler is consumed by Streamlit's
        # natural form-submission flow when Tab blurs an on_change input.
        #
        # History of failed approaches (kept for the next person):
        #   - Playwright.fill(): sets DOM value but Streamlit's React doesn't
        #     see the change. Confirmed via diagnostic — input.value was set
        #     but button stayed disabled.
        #   - React-native-value-setter via page.evaluate: DevTools-validated
        #     in headed Chrome but FAILED in Playwright headless. The
        #     dispatched 'input' event didn't trigger React's onChange in the
        #     headless context.
        #   - fill() + Tab/Enter to blur: same outcome as plain fill().
        #
        # press_sequentially fires genuine keydown/keypress/input/keyup events
        # for each character, which React's event listeners pick up reliably
        # in both headed and headless modes.
        landing_input.first.click()  # focus
        landing_input.first.press_sequentially(query, delay=20)
        landing_input.first.press("Tab")  # blur → submit → page advances
    wait_for_streamlit_rerun(page)


def wait_for_banner(page):
    """Wait for the rejection banner to render."""
    page.wait_for_selector(".no-match-banner", timeout=LONG_WAIT)


def get_banner_text(page) -> str:
    """Read the banner's primary message text."""
    banner = page.locator(".no-match-banner-msg").first
    return banner.inner_text()


def get_visible_chip_labels(page) -> list[str]:
    """Return chip labels from the LATEST rejection banner only.

    Chip st.button keys follow the pattern
    `<key_prefix>_suggest_no_match_<i>_<hash>`. In conversation view the
    key_prefix is `transcript_banner_<N>` where N is the transcript
    message index (per conversation_helpers.py:482), incremented for each
    new rejected message. After multiple rejections the scrollback shows
    all banners and their chip sets simultaneously — that's correct
    conversation design (full transcript history). Tests assert against
    the LATEST chip set (highest N), not the entire scrollback.

    See BACKLOG MATTGPT-071 Scope decisions (May 20, 2026) for the
    "test bug, not product bug" rationale.

    Returns chip labels from the chip set tied to the highest
    transcript_banner_<N>. Falls back to all chips if no
    transcript_banner_ prefix is found (e.g., explore_stories context).
    """
    chip_data = page.evaluate(
        """
        () => {
            const chips = [];
            document.querySelectorAll(
                "[class*='_suggest_no_match_'] button"
            ).forEach(btn => {
                const container = btn.closest("[class*='_suggest_no_match_']");
                if (!container) return;
                const stKey = Array.from(container.classList).find(
                    c => c.startsWith('st-key-') && c.includes('_suggest_no_match_')
                );
                if (!stKey) return;
                // Parse N from st-key-transcript_banner_<N>_suggest_no_match_...
                const match = stKey.match(/_(\\d+)_suggest_no_match/);
                const transcriptN = match ? parseInt(match[1]) : -1;
                chips.push({label: btn.innerText, transcriptN: transcriptN});
            });
            return chips;
        }
        """
    )
    if not chip_data:
        return []
    # If we have transcript Ns, scope to highest. Else return all.
    valid_ns = [c["transcriptN"] for c in chip_data if c["transcriptN"] >= 0]
    if not valid_ns:
        return [c["label"] for c in chip_data]
    max_n = max(valid_ns)
    return [c["label"] for c in chip_data if c["transcriptN"] == max_n]


# =============================================================================
# GIVEN — Navigation
# =============================================================================


@given("the user navigates to Ask MattGPT")
def navigate_to_ask_mattgpt(browser_page, app_url):
    """Navigate to the Ask MattGPT page via the desktop navbar.

    Wait for the landing view's input (st.text_input keyed "landing_input")
    to render. Conversation view's st.chat_input only appears after a query
    has been submitted; the landing input is the stable first-render target.
    """
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    _wait_for_navbar_stable(browser_page)
    browser_page.locator(ASK_MATTGPT_NAV_SELECTOR).first.click()
    wait_for_streamlit_rerun(browser_page)
    browser_page.wait_for_selector("[class*='st-key-landing_input']", timeout=15000)


@given("the user navigates to Explore Stories")
def navigate_to_explore_stories(browser_page, app_url):
    """Navigate to Explore Stories via the desktop navbar."""
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    _wait_for_navbar_stable(browser_page)
    browser_page.locator(EXPLORE_STORIES_NAV_SELECTOR).first.click()
    wait_for_streamlit_rerun(browser_page)


# =============================================================================
# GIVEN — Banner-already-showing state setup
# =============================================================================


@given(parsers.parse('the {reason} rejection banner is showing'))
def given_banner_showing(browser_page, reason):
    """Trigger the named rejection branch by submitting a known query.

    Maps reason → trigger query (mirrors the trigger phrases used in
    the Scenario "When" steps):
      rule:*        → "Tell me a joke about Matt's career"
      personal      → "Is Matt married?"
      out_of_scope  → "Tell me about Matt's retail experience"
    """
    triggers = {
        "rule:*": "Tell me a joke about Matt's career",
        "personal": "Is Matt married?",
        "out_of_scope": "Tell me about Matt's retail experience",
    }
    query = triggers.get(reason)
    assert query, f"No known trigger query for reason={reason!r}"
    submit_query(browser_page, query)
    wait_for_banner(browser_page)


# =============================================================================
# WHEN — Submissions
# =============================================================================


@when(parsers.parse('the user submits "{query}"'))
def when_user_submits(browser_page, query):
    submit_query(browser_page, query)
    wait_for_banner(browser_page)


@when("the user submits a query that scores below the confidence threshold")
def when_user_submits_low_confidence(browser_page):
    """High-entropy gibberish that should score below CONFIDENCE_LOW.

    Red-B note: depends on production code recognizing the query as
    low-confidence rather than misclassifying as nonsense or matching
    something semantically. If this proves unstable, Blue may need a
    debug-mode override (URL flag or session-state hook) for
    deterministic testing.
    """
    submit_query(browser_page, "qzwxvnpfrk plmqcvjxk floogerblerg")
    wait_for_banner(browser_page)


@when("the response has been generated")
def when_response_generated(browser_page):
    """Wait for the LLM response to render after a chip click."""
    browser_page.wait_for_timeout(LONG_WAIT * 2)
    browser_page.wait_for_load_state("networkidle")


@when(parsers.parse('the user types "{query}" in the search box'))
def when_user_types_in_search(browser_page, query):
    """Explore Stories search box."""
    search = browser_page.locator("input[type='text']").first
    search.fill(query)


@when("the user presses Enter")
def when_user_presses_enter(browser_page):
    browser_page.keyboard.press("Enter")
    wait_for_streamlit_rerun(browser_page)


# =============================================================================
# WHEN — Chip clicks
# =============================================================================


@when(parsers.parse('the user clicks the first {branch} chip'))
def when_user_clicks_first_chip(browser_page, branch):
    """Click the first chip button in the currently-rendered chip set.

    Chips are st.button elements keyed <key_prefix>_suggest_no_match_0_<hash>.
    The `_0_` infix identifies the first chip (index 0). The key_prefix
    varies by call site (banner / transcript_banner_<n> / etc.) so we match
    on the *_suggest_no_match_0_* infix to be agnostic. Branch is
    informational only — the actual chip set depends on the current
    rejection reason.
    """
    chip_button = browser_page.locator("[class*='_suggest_no_match_0_'] button").first
    chip_button.dispatch_event("click")
    wait_for_streamlit_rerun(browser_page)


# =============================================================================
# THEN — Banner presence assertions
# =============================================================================


@then(parsers.parse('the {reason} rejection banner should be displayed'))
def then_banner_displayed(browser_page, reason):
    """Verify the banner element is present for the given reason."""
    banner = browser_page.locator(".no-match-banner").first
    assert banner.is_visible(), (
        f"{reason} rejection banner not visible. "
        f"Expected .no-match-banner element to be present."
    )


@then("the rejection banner should be displayed")
def then_rejection_banner_displayed(browser_page):
    """Generic version for Explore Stories context."""
    banner = browser_page.locator(".no-match-banner").first
    assert banner.is_visible(), "Rejection banner not visible"


@then("the rule:* rejection banner should NOT be visible")
def then_rule_banner_not_visible(browser_page):
    count = browser_page.locator(".no-match-banner").count()
    assert count == 0, (
        f"Expected no banner after chip click + response; "
        f"found {count} banner(s) still visible. "
        f"__clear_banner_after_answer__ flag may not be firing."
    )


# =============================================================================
# THEN — Banner copy assertions (BANNER_COPY constant)
# =============================================================================


@then(parsers.parse('the banner displays the {reason} copy from BANNER_COPY'))
def then_banner_displays_copy(browser_page, reason):
    """Compare banner text against BANNER_COPY[reason].

    The Gherkin uses 'rule:*' but the dict key is 'rule' (no colon-star).
    Normalize the Gherkin reason → dict key here.
    """
    key = reason.rstrip(":*").rstrip(":")
    if key not in BANNER_COPY:
        # Try the raw form in case the Gherkin matches the key directly
        key = reason
    expected = BANNER_COPY[key]
    actual = get_banner_text(browser_page)
    assert actual == expected, (
        f"BANNER_COPY[{key!r}] mismatch.\n"
        f"  Expected: {expected!r}\n"
        f"  Actual:   {actual!r}"
    )


# =============================================================================
# THEN — Chip visibility assertions (RULE_CHIPS / PERSONAL_CHIPS / OUT_OF_SCOPE_CHIPS)
# =============================================================================


@then("all RULE_CHIPS should be visible")
def then_all_rule_chips_visible(browser_page):
    visible = get_visible_chip_labels(browser_page)
    expected = [label for label, _ in RULE_CHIPS]
    missing = [c for c in expected if c not in visible]
    assert not missing, (
        f"RULE_CHIPS labels not all visible.\n"
        f"  Expected: {expected!r}\n"
        f"  Missing:  {missing!r}\n"
        f"  Visible:  {visible!r}"
    )


@then("all PERSONAL_CHIPS should be visible")
def then_all_personal_chips_visible(browser_page):
    visible = get_visible_chip_labels(browser_page)
    expected = [label for label, _ in PERSONAL_CHIPS]
    missing = [c for c in expected if c not in visible]
    assert not missing, (
        f"PERSONAL_CHIPS labels not all visible.\n"
        f"  Expected: {expected!r}\n"
        f"  Missing:  {missing!r}\n"
        f"  Visible:  {visible!r}"
    )


@then("all OUT_OF_SCOPE_CHIPS should be visible")
def then_all_out_of_scope_chips_visible(browser_page):
    visible = get_visible_chip_labels(browser_page)
    expected = [label for label, _ in OUT_OF_SCOPE_CHIPS]
    missing = [c for c in expected if c not in visible]
    assert not missing, (
        f"OUT_OF_SCOPE_CHIPS labels not all visible.\n"
        f"  Expected: {expected!r}\n"
        f"  Missing:  {missing!r}\n"
        f"  Visible:  {visible!r}"
    )


@then("no RULE_CHIPS should be visible")
def then_no_rule_chips_visible(browser_page):
    """For the sequential-rejection swap scenario — after pivoting to
    personal, no rule:* chips should remain visible."""
    visible = get_visible_chip_labels(browser_page)
    rule_labels = [label for label, _ in RULE_CHIPS]
    leaked = [c for c in rule_labels if c in visible]
    assert not leaked, (
        f"RULE_CHIPS labels should NOT be visible after pivot, but found:\n"
        f"  Leaked: {leaked!r}\n"
        f"  Visible: {visible!r}"
    )


@then("no chips should be visible")
def then_no_chips_visible(browser_page):
    visible = get_visible_chip_labels(browser_page)
    assert len(visible) == 0, f"Expected no chips; found {len(visible)}: {visible!r}"


@then("zero chips should be visible")
def then_zero_chips_visible(browser_page):
    """Equivalent to 'no chips' — phrased differently in low_confidence
    and Explore Stories scenarios for readability."""
    visible = get_visible_chip_labels(browser_page)
    assert len(visible) == 0, f"Expected zero chips; found {len(visible)}: {visible!r}"


# =============================================================================
# THEN — Chip click effect assertions
# =============================================================================


@then("that chip's prompt should appear as the next user message")
def then_chip_prompt_in_chat(browser_page):
    """After a chip click, the chip's prompt should be the latest user message
    in the chat. We can't easily know WHICH chip without tracking state across
    steps, so we assert that there are at least two user messages (the original
    rejected query + the chip-injected prompt).

    The chip-click → __inject_user_turn__ → rerun → conversation_view consumes
    inject → adds user message cycle takes longer than the default 200ms wait
    in `wait_for_streamlit_rerun`. Use `wait_for_function` to poll the live
    DOM until the second message appears, with a 15-second timeout.
    See BACKLOG MATTGPT-071 Scope decisions (May 20, 2026) for the timing
    rationale.
    """
    try:
        browser_page.wait_for_function(
            """
            () => document.querySelectorAll(
                "[data-testid='stChatMessage']"
            ).length >= 2
            """,
            timeout=15000,
        )
    except Exception:
        pass  # fall through to assertion for a clean error message
    user_messages = browser_page.locator("[data-testid='stChatMessage']")
    count = user_messages.count()
    assert count >= 2, (
        f"Expected chat history to contain the original query + the chip "
        f"prompt as a user message after click; found {count} message(s)."
    )


@then("a response should be generated")
def then_response_generated(browser_page):
    """An assistant response should appear after the chip-injected prompt."""
    browser_page.wait_for_timeout(LONG_WAIT)
    messages = browser_page.locator("[data-testid='stChatMessage']")
    assert messages.count() > 0, "Expected at least one chat message"


@then("a rephrase prompt should be displayed")
def then_rephrase_prompt_displayed(browser_page):
    """For low_confidence, the banner copy should hint at rephrasing.
    The locked low_confidence BANNER_COPY includes 'Try rephrasing'.
    """
    banner_text = get_banner_text(browser_page)
    assert (
        "rephras" in banner_text.lower()
    ), f"Expected rephrase hint in low_confidence banner; got: {banner_text!r}"
