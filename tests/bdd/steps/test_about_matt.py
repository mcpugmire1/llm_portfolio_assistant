"""
BDD Step Definitions for My Profile — Content polish bundle (MATTGPT-068).

Red (step defs) gate state: step definitions bound, scenarios run end-to-end
against the unchanged My Profile page. All 7 are expected to fail with
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


def _wait_for_streamlit_rerun(page):
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


# =============================================================================
# GIVEN — Navigation to My Profile
# =============================================================================


@given("the user navigates to the My Profile page")
def navigate_to_about_matt(browser_page, app_url):
    """Open the app and click the My Profile tab in the top nav.

    The .about-header div is unique to My Profile (ui/pages/about_matt.py
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
        nav_btn = browser_page.locator(
            "[class*='st-key-topnav_My-Profile'] button"
        ).first
        nav_btn.wait_for(state="visible", timeout=NAV_TIMEOUT)
        nav_btn.dispatch_event("click")
    except Exception as exc:
        raise AssertionError(
            "My Profile top-nav button not found within "
            f"{NAV_TIMEOUT}ms. Selector "
            "'[class*=\"st-key-topnav_My-Profile\"] button' did not match a "
            "visible element — navbar key pattern may have changed. "
            f"Underlying error: {exc}"
        ) from exc
    _wait_for_streamlit_rerun(browser_page)
    try:
        browser_page.wait_for_selector(".about-header", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "My Profile page did not render within "
            f"{LONG_TIMEOUT}ms after clicking the top-nav button. "
            "Expected .about-header div not visible — page structure may "
            f"have changed. Underlying error: {exc}"
        ) from exc


# =============================================================================
# SCENARIO 3 — Redundant CTA footer copy removed
# =============================================================================


@then(parsers.parse('the text "{needle}" should not appear on the page'))
def assert_text_absent(browser_page, needle):
    body_text = browser_page.locator("body").inner_text()
    assert needle not in body_text, (
        f"Text {needle!r} is still present on the My Profile page. "
        f"Per MATTGPT-068, the redundant CTA footer copy at "
        f"about_matt.py:1205-1208 must be removed once sample questions are "
        f"clickable."
    )


# =============================================================================
# MATTGPT-093 — My Profile UI refresh step definitions
# Covers: CTA card removal, Career Evolution timeline, competency rename,
# How I Lead section, Signals panel, In my own words, For a referrer,
# profile header subtitle.
# Green targets: st.container(key="am_signals_panel"), key="am_in_my_own_words",
# key="am_for_a_referrer" — CSS selectors below match those keys.
# =============================================================================


# ---------------------------------------------------------------------------
# CTA card / See It In Action removal
# NOTE: "the text ... should not appear on the page" step already defined
# above (line 288, MATTGPT-068 Scenario 3). The "See It In Action" scenario
# reuses it with needle="See It In Action".
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Career Evolution timeline
# ---------------------------------------------------------------------------


@then("the career evolution timeline should have 7 entries")
def assert_timeline_entry_count(browser_page):
    count = browser_page.locator(".timeline .timeline-item").count()
    assert count == 7, (
        f"Expected 7 timeline entries (.timeline .timeline-item), found {count}. "
        f"Per MATTGPT-093, Career Evolution must have exactly 7 rows."
    )


@then(parsers.parse('the career timeline should contain period "{period}"'))
def assert_timeline_contains_period(browser_page, period):
    # Normalize en-dash / em-dash to hyphen for comparison so the Gherkin
    # can use plain hyphens (e.g. "2019-2023") against HTML en-dashes (–).
    texts = browser_page.locator(".timeline .timeline-year").all_inner_texts()
    normalized = [t.replace("–", "-").replace("—", "-") for t in texts]
    assert period in normalized, (
        f"No .timeline-year contains period {period!r} (after dash normalization). "
        f"Found: {texts}. Per MATTGPT-093 spec."
    )


@then(parsers.parse('the career timeline should contain "{text}"'))
def assert_timeline_contains_text(browser_page, text):
    content = browser_page.locator(".timeline").first.inner_text()
    assert (
        text in content
    ), f"Career timeline does not contain {text!r}. Per MATTGPT-093 spec."


@then(parsers.parse('the career timeline should not contain "{text}"'))
def assert_timeline_not_contain_text(browser_page, text):
    content = browser_page.locator(".timeline").first.inner_text()
    assert text not in content, (
        f"Career timeline still contains {text!r}. Per MATTGPT-093, "
        f"this text must be removed."
    )


# ---------------------------------------------------------------------------
# Competency rename
# ---------------------------------------------------------------------------


@then(
    parsers.parse(
        'the competencies grid should contain a card with heading "{heading}"'
    )
)
def assert_competency_card_present(browser_page, heading):
    headings = browser_page.locator(
        ".competencies-grid .competency-card h4"
    ).all_inner_texts()
    assert heading in headings, (
        f"No competency card with heading {heading!r} found. "
        f"Found: {headings}. Per MATTGPT-093."
    )


@then(
    parsers.parse(
        'the competencies grid should not contain a card with heading "{heading}"'
    )
)
def assert_competency_card_absent(browser_page, heading):
    headings = browser_page.locator(
        ".competencies-grid .competency-card h4"
    ).all_inner_texts()
    assert heading not in headings, (
        f"Competency card with heading {heading!r} is still present. "
        f"Found: {headings}. Per MATTGPT-093, this heading must be renamed."
    )


# ---------------------------------------------------------------------------
# How I Lead — section title and card values
# ---------------------------------------------------------------------------


@then(parsers.parse('the section heading "{heading}" should be visible'))
def assert_section_heading_visible(browser_page, heading):
    headings = browser_page.locator(".am-section-title").all_inner_texts()
    # CSS text-transform:uppercase means inner_text() returns uppercased text —
    # compare case-insensitively so the Gherkin can use natural casing.
    assert any(heading.lower() in h.lower() for h in headings), (
        f"Section heading {heading!r} not found among .am-section-title elements. "
        f"Found: {headings}. Per MATTGPT-093 spec."
    )


@then(parsers.parse('the section heading "{heading}" should not be visible'))
def assert_section_heading_absent(browser_page, heading):
    headings = browser_page.locator(".am-section-title").all_inner_texts()
    assert not any(heading.lower() in h.lower() for h in headings), (
        f"Section heading {heading!r} is still present in .am-section-title elements. "
        f"Found: {headings}. Per MATTGPT-093, this heading must be replaced."
    )


@then(parsers.parse('the How I Lead section should contain "{text}"'))
def assert_how_i_lead_contains(browser_page, text):
    # Scoped to .philosophy-grid — the container for leadership value cards.
    content = browser_page.locator(".philosophy-grid").first.inner_text()
    assert text in content, (
        f"How I Lead section (.philosophy-grid) does not contain {text!r}. "
        f"Per MATTGPT-093, the four locked values must be present."
    )


@then(parsers.parse('the How I Lead section should not contain "{text}"'))
def assert_how_i_lead_not_contain(browser_page, text):
    content = browser_page.locator(".philosophy-grid").first.inner_text()
    assert text not in content, (
        f"How I Lead section (.philosophy-grid) still contains {text!r}. "
        f"Per MATTGPT-093, old leadership values must be replaced."
    )


# ---------------------------------------------------------------------------
# Signals panel — replaces stats bar
# ---------------------------------------------------------------------------


@then("the profile stats bar should not be present in the DOM")
def assert_stats_bar_absent(browser_page):
    count = browser_page.locator(".am-stats-bar").count()
    assert count == 0, (
        f".am-stats-bar is still in the DOM ({count} instance(s)). "
        f"Per MATTGPT-093, the stats bar must be replaced by the Signals panel."
    )


@then("the signals panel should be visible")
def assert_signals_panel_visible(browser_page):
    panel = browser_page.locator("[class*='st-key-am_signals_panel']").first
    try:
        panel.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "Signals panel (.st-key-am_signals_panel) not visible. "
            "Per MATTGPT-093, a 6-tile signals panel must replace the stats bar. "
            f"Underlying error: {exc}"
        ) from exc


@then("the signals panel should have 6 tiles")
def assert_signals_panel_tile_count(browser_page):
    count = browser_page.locator(
        "[class*='st-key-am_signals_panel'] .am-signal-tile"
    ).count()
    assert count == 6, (
        f"Signals panel has {count} .am-signal-tile element(s), expected 6. "
        f"Per MATTGPT-093: Level, Most recent, Peak team, Geo, Status, Work mode."
    )


@then(parsers.parse('the signals panel should contain "{text}"'))
def assert_signals_panel_contains(browser_page, text):
    panel = browser_page.locator("[class*='st-key-am_signals_panel']").first
    try:
        panel.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            f"Signals panel not visible — cannot check for {text!r}. "
            f"Underlying error: {exc}"
        ) from exc
    content = panel.inner_text()
    assert (
        text in content
    ), f"Signals panel does not contain {text!r}. Per MATTGPT-093 wireframe spec."


# ---------------------------------------------------------------------------
# In my own words — voice block (scoped to container)
# ---------------------------------------------------------------------------


@then(parsers.parse('the "In my own words" section should contain "{text}"'))
def assert_in_my_own_words_contains(browser_page, text):
    section = browser_page.locator("[class*='st-key-am_in_my_own_words']").first
    try:
        section.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "'In my own words' section (.st-key-am_in_my_own_words) not visible. "
            "Per MATTGPT-093, this voice block section must be present. "
            f"Underlying error: {exc}"
        ) from exc
    content = section.inner_text()
    assert text in content, (
        f"'In my own words' section does not contain {text!r}. "
        f"Per MATTGPT-093 voice block spec."
    )


# ---------------------------------------------------------------------------
# For a referrer — snippet and action buttons (scoped to container)
# ---------------------------------------------------------------------------


@then('the "For a referrer" section should contain a copy snippet block')
def assert_for_a_referrer_has_snippet(browser_page):
    section = browser_page.locator("[class*='st-key-am_for_a_referrer']").first
    try:
        section.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "'For a referrer' section (.st-key-am_for_a_referrer) not visible. "
            "Per MATTGPT-093, this section must be present. "
            f"Underlying error: {exc}"
        ) from exc
    snippet = section.locator(".am-referrer-snippet").first
    try:
        snippet.wait_for(state="visible", timeout=CLICK_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "Copy snippet block (.am-referrer-snippet) not visible inside "
            "'For a referrer' section. Per MATTGPT-093 spec. "
            f"Underlying error: {exc}"
        ) from exc


@then(
    parsers.parse(
        'the "For a referrer" section should contain action button text "{label}"'
    )
)
def assert_action_button_text_in_for_a_referrer(browser_page, label):
    section = browser_page.locator("[class*='st-key-am_for_a_referrer']").first
    try:
        section.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "'For a referrer' section not visible — cannot check for action button text. "
            f"Underlying error: {exc}"
        ) from exc
    content = section.inner_text()
    assert label in content, (
        f"'For a referrer' section does not contain action button text {label!r}. "
        f"Per MATTGPT-093, 'Copy snippet' and 'Download PDF' must be present as HTML inline buttons."
    )


# ---------------------------------------------------------------------------
# Profile header subtitle
# ---------------------------------------------------------------------------


@then(parsers.parse('the profile header should contain "{text}"'))
def assert_profile_header_contains(browser_page, text):
    content = browser_page.locator(".about-header").first.inner_text()
    assert text in content, (
        f"Profile header (.about-header) does not contain {text!r}. "
        f"Per MATTGPT-093, the subtitle must match the locked target text "
        f"for the feature/ui-redesign branch."
    )


# ---------------------------------------------------------------------------
# MATTGPT-118 — Copy snippet clipboard + ✓ Copied! confirmation
# ---------------------------------------------------------------------------


@when(
    'the user clicks the "Copy snippet" action button in the "For a referrer" section'
)
def click_copy_snippet_button(browser_page):
    section = browser_page.locator("[class*='st-key-am_for_a_referrer']").first
    try:
        section.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "'For a referrer' section not visible — cannot click Copy snippet. "
            f"Underlying error: {exc}"
        ) from exc
    btn = section.locator(".prof-act-btn:has-text('Copy snippet')").first
    try:
        btn.wait_for(state="visible", timeout=CLICK_TIMEOUT)
        btn.click()
    except Exception as exc:
        raise AssertionError(
            "Copy snippet .prof-act-btn not found or not clickable inside "
            "'For a referrer' section. MATTGPT-118: the span must have class "
            f"prof-act-btn and contain text 'Copy snippet'. Underlying error: {exc}"
        ) from exc
    browser_page.wait_for_timeout(SHORT_WAIT)


@then(parsers.parse('the "Copy snippet" button should show "{label}" confirmation'))
def assert_copy_snippet_confirmation(browser_page, label):
    section = browser_page.locator("[class*='st-key-am_for_a_referrer']").first
    try:
        section.wait_for(state="visible", timeout=LONG_TIMEOUT)
        section.locator(f".prof-act-btn:has-text('{label}')").first.wait_for(
            state="visible", timeout=CLICK_TIMEOUT
        )
    except Exception as exc:
        raise AssertionError(
            f"Copy snippet button did not show {label!r} confirmation after click. "
            "MATTGPT-118: the JS clipboard handler must change the span label to "
            f"{label!r} on successful copy. Underlying error: {exc}"
        ) from exc
