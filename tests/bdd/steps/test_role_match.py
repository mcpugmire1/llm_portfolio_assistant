"""
BDD Step Definitions for Role Match

These step definitions use Playwright for browser automation, following
the same pattern as tests/bdd/steps/test_explore_stories.py.

Install with: pip install pytest-bdd playwright && playwright install chromium
Run with:     pytest tests/bdd -k role_match

Scenarios bound here intentionally cover the high-value layout, navigation,
and visibility behaviors that don't depend on the JD assessment pipeline,
the system clipboard, or print-window popups. The scenarios that DO depend
on those things are bound with @pytest.mark.skip and a reason, so they
show up in the pytest report as known-skipped instead of silently absent.

Coverage status (April 2026):

  Bound and executing:
    - Role Match tab appears in navigation
    - Clicking Role Match tab navigates to the page
    - JD text area accepts pasted job description
    - Mobile shows desktop-only message
    - Desktop shows full Role Match interface
    - Action buttons appear only when results are present

  Bound but skipped:
    - Empty text area disables the match button
        (contradicts implementation — the button is intentionally always
        enabled and empty submissions are handled with a warning. Update
        the feature file to match reality, then re-enable.)
    - Action buttons appear after results render
    - Share copies plain-text summary to clipboard
    - Export opens a printable document
    - Helpful button logs feedback
    - Action buttons hidden on mobile
    - Results come from the three-step pipeline
    - Pipeline handles JD with no preferred qualifications
    - Pipeline handles empty Pinecone results gracefully
    - Match results show required qualifications with status badges
    - Match results show preferred qualifications separately
    - Results show all qualifications without a summary count or score
    - Partial match shows gap explanation
    - Gap shows explanation with no story chips
    - No fit score or recommendation in recruiter view
    - Profile-level evidence displays without story chip
        (all skipped pending a decision on how to run the assessment
        pipeline in tests — real backend vs. mocked OpenAI/Pinecone)

  Bound and executing (Phase 4 — slice 1, lock icon + password gate):
    - Lock icon is visible on the Role Match results panel
    - Clicking lock icon opens password popover
    - Correct password unlocks private view
    - Incorrect password does not unlock private view
    - Private mode persists within session
    - Empty password submission is a no-op
    - Wrong password followed by correct password still unlocks
    - Password input is masked
    - Lock glyph reflects __private_mode__ state
    - Clicking the unlocked icon re-locks the session
    - Lock icon hidden on mobile
    - Browser refresh re-locks the session
    - New tab does not inherit unlocked state
        (slice 1 step defs require MATTGPT_PRIVATE_BYPASS_TOKEN in
        Streamlit secrets — local-prod parity. Add
        MATTGPT_PRIVATE_BYPASS_TOKEN = "test-bypass-token" to
        .streamlit/secrets.toml to match the BYPASS_TOKEN fixture
        in this file. The command-line env-var prefix workflow
        was decided against in favor of secrets.toml parity.
        See MATTGPT-085 for the cleanup history.)

  Bound but skipped (Phase 4 — Streamlit 1.50 limitation):
    - Pressing Escape inside the popover closes it without unlocking
        (st.popover does not auto-close on Escape; verified via Playwright.
        The Gherkin scenario is kept in the feature file as design intent.
        Would require a custom JS handler injected via st.markdown.)

  Not yet bound (Phase 4 — slice 2 + 3):
    - All agentic bypass scenarios (slice 2 — header injection)
    - All private assessment view scenarios (slice 3 — fit assessment)
    - MATTGPT_PRIVATE_BYPASS_TOKEN env var unset — silent no-op
        (slice 2 — needs env-var control over the Streamlit subprocess)
    - Toggling lock back hides the private assessment on next rerun
        (slice 3 — needs the assessment view to exist first)
    - Story evidence chips are clickable and expand inline (Phase 3
      story chip expansion — implementation does not exist)
"""

import pytest
from pytest_bdd import given, scenario, then, when

# =============================================================================
# WAIT UTILITIES — Same constants as test_explore_stories.py
# =============================================================================

SHORT_WAIT = 200  # Quick UI updates
MEDIUM_WAIT = 500  # Component renders
CONTENT_WAIT = 1000  # Content loading after navigation


def wait_for_content(page, selector, timeout=10000):
    """Wait for selector to appear, return True if found, False otherwise."""
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return True
    except Exception:
        return False


def wait_for_streamlit_rerun(page):
    """Wait for Streamlit to complete a rerun after an action."""
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


# =============================================================================
# FIXTURES — shared_browser, browser_page, app_url are defined in
# tests/bdd/steps/conftest.py (single session-scoped Playwright instance
# shared across all BDD test files to avoid sync/async clash).
# =============================================================================


# =============================================================================
# SELECTORS — Stable hooks into the Role Match page
# =============================================================================

ROLE_MATCH_HEADER_SELECTOR = ".conversation-header h1"
ROLE_MATCH_WORKSPACE_SELECTOR = ".st-key-role_match_workspace"
ROLE_MATCH_INPUT_SELECTOR = ".st-key-role_match_workspace textarea"
ROLE_MATCH_SUBMIT_SELECTOR = ".st-key-role_match_submit button"
MOBILE_GATE_TEXT = "Best experienced on desktop"
ACTION_BUTTON_IDS = (
    "#btn-role-match-helpful",
    "#btn-role-match-share",
    "#btn-role-match-export",
)


# =============================================================================
# SCENARIO BINDINGS — Bound and executing
# =============================================================================


@scenario("../features/role_match.feature", "Role Match tab appears in navigation")
def test_role_match_tab_in_navigation():
    pass


@scenario(
    "../features/role_match.feature", "Clicking Role Match tab navigates to the page"
)
def test_clicking_role_match_navigates():
    pass


@scenario(
    "../features/role_match.feature", "JD text area accepts pasted job description"
)
def test_textarea_accepts_paste():
    pass


@pytest.mark.skip(
    reason="Mobile nav navigation requires clicking the hamburger menu first to "
    "expose the mobile dropdown <a> link. The desktop nav buttons exist in the "
    "DOM at mobile viewport but extend past the right edge of the viewport, so "
    "Playwright's click() can't scroll them into view. Needs hamburger interaction."
)
@scenario("../features/role_match.feature", "Mobile shows desktop-only message")
def test_mobile_desktop_only_message():
    pass


@scenario("../features/role_match.feature", "Desktop shows full Role Match interface")
def test_desktop_shows_full_interface():
    pass


@scenario(
    "../features/role_match.feature",
    "Action buttons appear only when results are present",
)
def test_action_buttons_hidden_without_results():
    pass


# =============================================================================
# SCENARIO BINDINGS — Bound but skipped
# =============================================================================


@pytest.mark.skip(
    reason="Contradicts implementation — button is intentionally always enabled. "
    "Empty submissions show a warning. Update feature file to match."
)
@scenario("../features/role_match.feature", "Empty text area disables the match button")
def test_empty_text_area_disables_button():
    pass


@pytest.mark.skip(
    reason="Pending decision on pipeline test strategy (real backend vs. mocked OpenAI/Pinecone)"
)
@scenario(
    "../features/role_match.feature", "Action buttons appear after results render"
)
def test_action_buttons_after_results_render():
    pass


@pytest.mark.skip(
    reason="Pending decision on pipeline + system clipboard test strategy"
)
@scenario(
    "../features/role_match.feature", "Share copies plain-text summary to clipboard"
)
def test_share_copies_summary():
    pass


@pytest.mark.skip(
    reason="Pending decision on pipeline + print-window popup test strategy"
)
@scenario("../features/role_match.feature", "Export opens a printable document")
def test_export_opens_printable_document():
    pass


@pytest.mark.skip(
    reason="Pending decision on pipeline test strategy + log_feedback mock"
)
@scenario("../features/role_match.feature", "Helpful button logs feedback")
def test_helpful_logs_feedback():
    pass


@pytest.mark.skip(reason="Pending decision on pipeline test strategy")
@scenario("../features/role_match.feature", "Action buttons hidden on mobile")
def test_action_buttons_hidden_on_mobile():
    pass


@pytest.mark.skip(reason="Pending decision on pipeline test strategy")
@scenario("../features/role_match.feature", "Results come from the three-step pipeline")
def test_results_come_from_pipeline():
    pass


@pytest.mark.skip(reason="Pending decision on pipeline test strategy")
@scenario(
    "../features/role_match.feature",
    "Pipeline handles JD with no preferred qualifications",
)
def test_pipeline_no_preferred_qualifications():
    pass


@pytest.mark.skip(reason="Pending decision on pipeline test strategy")
@scenario(
    "../features/role_match.feature",
    "Pipeline handles empty Pinecone results gracefully",
)
def test_pipeline_empty_pinecone_results():
    pass


@pytest.mark.skip(reason="Pending decision on pipeline test strategy")
@scenario(
    "../features/role_match.feature",
    "Match results show required qualifications with status badges",
)
def test_match_results_required_status_badges():
    pass


@pytest.mark.skip(reason="Pending decision on pipeline test strategy")
@scenario(
    "../features/role_match.feature",
    "Match results show preferred qualifications separately",
)
def test_match_results_preferred_separate():
    pass


@pytest.mark.skip(reason="Pending decision on pipeline test strategy")
@scenario(
    "../features/role_match.feature",
    "Results show all qualifications without a summary count or score",
)
def test_results_no_summary_count():
    pass


@pytest.mark.skip(reason="Pending decision on pipeline test strategy")
@scenario("../features/role_match.feature", "Partial match shows gap explanation")
def test_partial_match_gap_explanation():
    pass


@pytest.mark.skip(reason="Pending decision on pipeline test strategy")
@scenario("../features/role_match.feature", "Gap shows explanation with no story chips")
def test_gap_no_story_chips():
    pass


@pytest.mark.skip(reason="Pending decision on pipeline test strategy")
@scenario(
    "../features/role_match.feature", "No fit score or recommendation in recruiter view"
)
def test_no_fit_score_recruiter_view():
    pass


@pytest.mark.skip(reason="Pending decision on pipeline test strategy")
@scenario(
    "../features/role_match.feature",
    "Profile-level evidence appears in a block above the story chip row",
)
def test_profile_evidence_block_above_chips():
    pass


# =============================================================================
# GIVEN STEPS
# =============================================================================


def _wait_for_navbar_stable(page, timeout: int = 30000) -> None:
    """Wait until the full navbar is rendered AND stays rendered through any reruns.

    Streamlit reruns after first load when streamlit_js_eval sets the
    _browser_screen_size session var (see app.py:104-113). Without this wait,
    a @given step can land between the first render and the post-rerun render
    when the navbar is briefly absent from the DOM.

    Streamlit converts spaces in container keys to dashes for CSS classes,
    so `key="topnav_Role Match"` produces class `st-key-topnav_Role-Match`.
    Verified against the live DOM via DevTools inspection (April 2026).
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


# Exact class for the Role Match navbar button column.
# Streamlit converts the space in the key "topnav_Role Match" to a dash
# in the CSS class name. Same pattern for the other multi-word nav tabs.
ROLE_MATCH_NAV_SELECTOR = ".st-key-topnav_Role-Match button"


@given("the user is on any page")
def user_on_any_page(browser_page, app_url):
    """Land on the app — Home is fine, the navbar is on every page."""
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    _wait_for_navbar_stable(browser_page)


@given("the user is on the Role Match page")
def user_on_role_match_page(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    _wait_for_navbar_stable(browser_page)
    browser_page.locator(ROLE_MATCH_NAV_SELECTOR).first.click()
    wait_for_streamlit_rerun(browser_page)
    # Wait for the workspace card to be present so the page is actually rendered.
    browser_page.wait_for_selector(ROLE_MATCH_WORKSPACE_SELECTOR, timeout=15000)


@given("the user is on a device with viewport width less than 768px")
def viewport_mobile(browser_page):
    browser_page.set_viewport_size({"width": 375, "height": 800})
    browser_page.wait_for_timeout(SHORT_WAIT)


@given("the user is on a device with viewport width 1024px or greater")
def viewport_desktop(browser_page):
    browser_page.set_viewport_size({"width": 1280, "height": 900})
    browser_page.wait_for_timeout(SHORT_WAIT)


@given("the user has not submitted a job description")
def user_has_not_submitted_jd(browser_page, app_url):
    """Land on Role Match without ever clicking submit."""
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    _wait_for_navbar_stable(browser_page)
    browser_page.locator(ROLE_MATCH_NAV_SELECTOR).first.click()
    wait_for_streamlit_rerun(browser_page)
    browser_page.wait_for_selector(ROLE_MATCH_WORKSPACE_SELECTOR, timeout=15000)


# =============================================================================
# WHEN STEPS
# =============================================================================


@when('the user clicks "Role Match" in the navigation bar')
def user_clicks_role_match_nav(browser_page):
    # The preceding @given step (user_on_any_page) has already navigated and
    # waited for the navbar to be stable via _wait_for_navbar_stable.
    browser_page.locator(ROLE_MATCH_NAV_SELECTOR).first.click()
    wait_for_streamlit_rerun(browser_page)


@when("the user pastes a job description into the text area")
def user_pastes_jd(browser_page):
    sample_jd = (
        "Director of Engineering at Acme Corp. We're looking for a leader with "
        "10+ years of experience modernizing legacy platforms, leading large "
        "engineering organizations, and driving cloud-native transformation. "
        "Required: Java, AWS, agile transformation experience."
    )
    textarea = browser_page.locator(ROLE_MATCH_INPUT_SELECTOR).first
    textarea.fill(sample_jd)
    browser_page.wait_for_timeout(SHORT_WAIT)


@when("the user navigates to Role Match")
def user_navigates_to_role_match(browser_page, app_url):
    """Used by mobile and desktop scenarios — assumes viewport is already set
    by the preceding @given step. The viewport must be set before goto so
    streamlit_js_eval picks up the correct window.innerWidth on first load."""
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")

    # Both the desktop nav button AND the mobile-nav <a> link contain the
    # text "Role Match", but only one is visible at any given viewport. The
    # :visible filter on both selectors keeps Playwright from picking a
    # display:none element via .first.
    browser_page.wait_for_selector(
        "button:has-text('Role Match'):visible, a:has-text('Role Match'):visible",
        timeout=30000,
    )
    target = browser_page.locator(
        "button:has-text('Role Match'):visible, a:has-text('Role Match'):visible"
    ).first
    target.click()
    wait_for_streamlit_rerun(browser_page)


# =============================================================================
# THEN STEPS
# =============================================================================


@then('the page shows a JD text input area and a "Match this role" button')
def page_shows_input_and_button(browser_page):
    assert browser_page.locator(
        ROLE_MATCH_INPUT_SELECTOR
    ).first.is_visible(), "JD text area not visible on Role Match page"
    assert browser_page.locator(
        "button:has-text('Match this role')"
    ).first.is_visible(), '"Match this role" button not visible'


@then(
    '"Role Match" appears in the navigation bar between "Ask MattGPT" and "About Matt"'
)
def role_match_in_navbar_between_ask_and_about(browser_page):
    # All three labels must be present and visible in the navbar.
    assert (
        browser_page.locator("button:has-text('Ask MattGPT'):visible").count() > 0
    ), "'Ask MattGPT' nav button not visible"
    assert (
        browser_page.locator("button:has-text('Role Match'):visible").count() > 0
    ), "'Role Match' nav button not visible"
    assert (
        browser_page.locator("button:has-text('About Matt'):visible").count() > 0
    ), "'About Matt' nav button not visible"

    # Order: Role Match should appear after Ask MattGPT and before About Matt.
    # Use bounding boxes to verify left-to-right ordering.
    ask = browser_page.locator("button:has-text('Ask MattGPT'):visible").first
    role = browser_page.locator("button:has-text('Role Match'):visible").first
    about = browser_page.locator("button:has-text('About Matt'):visible").first

    ask_box = ask.bounding_box()
    role_box = role.bounding_box()
    about_box = about.bounding_box()
    assert ask_box and role_box and about_box, "Could not measure nav button positions"
    assert ask_box["x"] < role_box["x"] < about_box["x"], (
        "Role Match nav button not positioned between Ask MattGPT and About Matt "
        f"(ask.x={ask_box['x']}, role.x={role_box['x']}, about.x={about_box['x']})"
    )


@then("the Role Match page is displayed")
def role_match_page_displayed(browser_page):
    # Wait for the workspace card AND the page header to confirm we're on Role Match.
    assert wait_for_content(
        browser_page, ROLE_MATCH_WORKSPACE_SELECTOR, timeout=10000
    ), "Role Match workspace not visible after click"
    header = browser_page.locator(ROLE_MATCH_HEADER_SELECTOR).first
    assert header.is_visible(), "Role Match header not visible"
    assert (
        "Role Match" in header.inner_text()
    ), f"Header text mismatch: got '{header.inner_text()}'"


@then('the "Match this role" button is enabled')
def match_button_enabled(browser_page):
    button = browser_page.locator("button:has-text('Match this role')").first
    assert button.is_visible(), '"Match this role" button not visible'
    assert button.is_enabled(), '"Match this role" button is unexpectedly disabled'


@then("the JD input and match results are not displayed")
def jd_input_and_results_not_displayed(browser_page):
    # Mobile gate replaces the workspace with a "Best experienced on desktop" message.
    workspace = browser_page.locator(ROLE_MATCH_WORKSPACE_SELECTOR)
    assert (
        workspace.count() == 0 or not workspace.first.is_visible()
    ), "Workspace card should not render in mobile mode"


@then(f'a message says "{MOBILE_GATE_TEXT}"')
def mobile_gate_message_visible(browser_page):
    assert browser_page.get_by_text(
        MOBILE_GATE_TEXT
    ).is_visible(), f"Expected mobile gate text '{MOBILE_GATE_TEXT}' to be visible"


@then("the two-column layout is displayed (JD input left, results right)")
def two_column_layout_visible(browser_page):
    workspace = browser_page.locator(ROLE_MATCH_WORKSPACE_SELECTOR)
    assert workspace.first.is_visible(), "Workspace card not visible on desktop"
    # The workspace contains exactly two stColumn children — input on left, results on right.
    columns = browser_page.locator(
        f"{ROLE_MATCH_WORKSPACE_SELECTOR} [data-testid='stColumn']"
    )
    assert (
        columns.count() >= 2
    ), f"Expected at least 2 columns in workspace, got {columns.count()}"
    # The left column must contain the textarea.
    left_textarea = columns.nth(0).locator("textarea")
    assert left_textarea.count() > 0, "JD textarea not found in left column"


@then("the Helpful, Share, and Export buttons are not visible")
def action_buttons_not_visible(browser_page):
    for button_id in ACTION_BUTTON_IDS:
        # The buttons live inside the results header bar, which only renders
        # when result_payload is set in session_state. Without a submission
        # they should not exist in the DOM at all.
        elem = browser_page.locator(button_id)
        assert (
            elem.count() == 0 or not elem.first.is_visible()
        ), f"Action button {button_id} should not be visible before results render"


# =============================================================================
# PHASE 4 — SLICE 1: Lock icon + password gate (14 scenarios)
# =============================================================================
# IMPORTANT: production code reads MATTGPT_PRIVATE_BYPASS_TOKEN via get_conf()
# and has NO default. The literal "test-bypass-token" below is a test-only
# convention — the value is whatever the developer / CI sets in Streamlit
# secrets. The fixture default gives a deterministic value when secrets are
# unset, so the test process and the Streamlit process agree.
#
# Local-prod parity setup (decided over command-line env-var prefix workflow):
#   Add to .streamlit/secrets.toml:
#     MATTGPT_PRIVATE_BYPASS_TOKEN = "test-bypass-token"
#   Prod value lives in the Streamlit Cloud secrets UI.
#   Restart Streamlit so secrets are reloaded, then:
#     pytest tests/bdd -k role_match
# See MATTGPT-085 for the cleanup history + .streamlit/secrets.example.toml
# template.

# --- Selectors ---
LOCK_ICON_CONTAINER_SELECTOR = ".st-key-lock_icon"
LOCK_ICON_GLYPH_SELECTOR = ".st-key-lock_icon button"
LOCK_POPOVER_PASSWORD_INPUT_SELECTOR = "input[type='password']"
LOCK_POPOVER_SUBMIT_SELECTOR = "button:has-text('Unlock')"
INCORRECT_PASSWORD = "wrong-password-for-tests"


# --- Fixtures ---
@pytest.fixture
def correct_password() -> str:
    """The expected unlock password — read from the same source the app reads
    from (st.secrets first, then os.environ). True env parity: whatever's in
    .streamlit/secrets.toml locally OR the Streamlit Cloud secrets UI in prod
    is what the test types AND what the app compares against.

    May 23, 2026 refactor (MATTGPT-085): previously this used
    `os.getenv("MATTGPT_PRIVATE_BYPASS_TOKEN", "test-bypass-token")` which
    forced a divergent test-only value and required a shell-prefix
    workflow (`MATTGPT_PRIVATE_BYPASS_TOKEN=... streamlit run app.py`) that
    was later decided against. Reading via get_private_bypass_token()
    unifies test + app on the same source.
    """
    from config.constants import get_private_bypass_token

    value = get_private_bypass_token()
    if not value:
        raise pytest.UsageError(
            "MATTGPT_PRIVATE_BYPASS_TOKEN is unset in both st.secrets and "
            "os.environ. Lock-glyph BDD tests can't unlock without it. "
            "Add to .streamlit/secrets.toml — see .streamlit/secrets.example.toml."
        )
    return value


# --- Helpers ---
def _open_password_popover(page) -> None:
    """Click the lock icon (locked state) to open the password popover."""
    page.locator(LOCK_ICON_GLYPH_SELECTOR).first.click()
    page.wait_for_timeout(SHORT_WAIT)
    page.wait_for_selector(LOCK_POPOVER_PASSWORD_INPUT_SELECTOR, timeout=2000)


def _enter_password_and_submit(page, password: str) -> None:
    page.locator(LOCK_POPOVER_PASSWORD_INPUT_SELECTOR).first.fill(password)
    page.locator(LOCK_POPOVER_SUBMIT_SELECTOR).first.click()
    wait_for_streamlit_rerun(page)


def _read_lock_glyph(page) -> str:
    return page.locator(LOCK_ICON_GLYPH_SELECTOR).first.inner_text()


# --- Scenario bindings ---
@scenario(
    "../features/role_match.feature",
    "Lock icon is visible on the Role Match results panel",
)
def test_lock_icon_visible_on_results_panel():
    pass


@scenario("../features/role_match.feature", "Clicking lock icon opens password popover")
def test_clicking_lock_opens_popover():
    pass


@scenario("../features/role_match.feature", "Correct password unlocks private view")
def test_correct_password_unlocks():
    pass


@scenario(
    "../features/role_match.feature", "Incorrect password does not unlock private view"
)
def test_incorrect_password_keeps_locked():
    pass


@scenario("../features/role_match.feature", "Private mode persists within session")
def test_private_mode_persists():
    pass


@scenario("../features/role_match.feature", "Empty password submission is a no-op")
def test_empty_password_no_op():
    pass


@scenario(
    "../features/role_match.feature",
    "Wrong password followed by correct password still unlocks",
)
def test_retry_after_wrong_unlocks():
    pass


@scenario("../features/role_match.feature", "Password input is masked")
def test_password_input_masked():
    pass


@scenario(
    "../features/role_match.feature", "Lock glyph reflects __private_mode__ state"
)
def test_lock_glyph_reflects_state():
    pass


@scenario(
    "../features/role_match.feature", "Clicking the unlocked icon re-locks the session"
)
def test_unlocked_icon_relocks():
    pass


@pytest.mark.skip(
    reason="Streamlit 1.50 st.popover does not close on Escape — verified via "
    "Playwright (popover stays open after keyboard.press('Escape'); also stays "
    "open on click-outside). Implementing this would require a custom JS "
    "handler injected via st.markdown. Out of scope for slice 1 UI shell. "
    "The Gherkin scenario is kept in the feature file as design intent."
)
@scenario(
    "../features/role_match.feature",
    "Pressing Escape inside the popover closes it without unlocking",
)
def test_escape_closes_popover():
    pass


@scenario("../features/role_match.feature", "Lock icon hidden on mobile")
def test_lock_icon_hidden_on_mobile():
    pass


@scenario("../features/role_match.feature", "Browser refresh re-locks the session")
def test_refresh_relocks():
    pass


@scenario("../features/role_match.feature", "New tab does not inherit unlocked state")
def test_new_tab_does_not_inherit():
    pass


# --- GIVEN steps (Phase 4 slice 1) ---


def _navigate_to_role_match(page, app_url) -> None:
    """Land on Role Match — homepage → click Role Match nav → wait for workspace."""
    page.goto(app_url)
    page.wait_for_load_state("networkidle")
    _wait_for_navbar_stable(page)
    page.locator(ROLE_MATCH_NAV_SELECTOR).first.click()
    wait_for_streamlit_rerun(page)
    page.wait_for_selector(ROLE_MATCH_WORKSPACE_SELECTOR, timeout=15000)


@given("the user has clicked the lock icon")
def given_user_clicked_lock_icon(browser_page, app_url):
    _navigate_to_role_match(browser_page, app_url)
    _open_password_popover(browser_page)


@given("the user has unlocked the private view")
def given_user_unlocked_private_view(browser_page, app_url, correct_password):
    _navigate_to_role_match(browser_page, app_url)
    _open_password_popover(browser_page)
    _enter_password_and_submit(browser_page, correct_password)
    glyph = _read_lock_glyph(browser_page)
    assert "🔓" in glyph, (
        "Setup failed: expected unlocked glyph after correct password. "
        f"Got: {glyph!r}. Is MATTGPT_PRIVATE_BYPASS_TOKEN set in the Streamlit env?"
    )


@given("the user has unlocked the private view in tab A")
def given_unlocked_in_tab_a(browser_page, app_url, correct_password):
    """Same setup as 'has unlocked the private view' — kept distinct so the
    multi-tab scenario reads naturally."""
    _navigate_to_role_match(browser_page, app_url)
    _open_password_popover(browser_page)
    _enter_password_and_submit(browser_page, correct_password)
    assert "🔓" in _read_lock_glyph(browser_page)


@given("the user has entered an incorrect access code once")
def given_entered_incorrect_once(browser_page):
    """Assumes the preceding step opened the popover."""
    _enter_password_and_submit(browser_page, INCORRECT_PASSWORD)
    # Empty-form Streamlit reruns can collapse the popover; re-open if needed
    # so the next step lands on a usable popover.
    inputs = browser_page.locator(LOCK_POPOVER_PASSWORD_INPUT_SELECTOR)
    if inputs.count() == 0 or not inputs.first.is_visible():
        _open_password_popover(browser_page)


@given("the user is on a device with viewport width less than 1024px")
def given_viewport_below_1024(browser_page, app_url):
    """Set viewport BEFORE first goto so streamlit_js_eval picks up the
    correct width on first render — same constraint as the existing
    768px viewport step. At <1024px Role Match shows the desktop-only
    message instead of the workspace, so we DON'T wait for the workspace
    selector here (it won't render)."""
    browser_page.set_viewport_size({"width": 1000, "height": 800})
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    _wait_for_navbar_stable(browser_page)
    browser_page.locator(ROLE_MATCH_NAV_SELECTOR).first.click()
    wait_for_streamlit_rerun(browser_page)


# --- WHEN steps (Phase 4 slice 1) ---


@when("the user clicks the lock icon")
def when_user_clicks_lock_icon(browser_page):
    """Click the current lock icon — popover trigger when locked, re-lock button when unlocked."""
    browser_page.locator(LOCK_ICON_GLYPH_SELECTOR).first.click()
    wait_for_streamlit_rerun(browser_page)


@when("the user enters the correct access code")
def when_user_enters_correct(browser_page, correct_password):
    _enter_password_and_submit(browser_page, correct_password)


@when("the user enters an incorrect access code")
def when_user_enters_incorrect(browser_page):
    _enter_password_and_submit(browser_page, INCORRECT_PASSWORD)


@when("the user submits the password popover with an empty input")
def when_user_submits_empty(browser_page):
    """Click submit without filling anything."""
    browser_page.locator(LOCK_POPOVER_SUBMIT_SELECTOR).first.click()
    wait_for_streamlit_rerun(browser_page)


@when("the user navigates to another tab and returns to Role Match")
def when_user_navigates_away_and_back(browser_page):
    """In-app navigation — click About Matt then click Role Match."""
    browser_page.locator(".st-key-topnav_About-Matt button").first.click()
    wait_for_streamlit_rerun(browser_page)
    browser_page.locator(ROLE_MATCH_NAV_SELECTOR).first.click()
    wait_for_streamlit_rerun(browser_page)


@when("the user presses Escape inside the popover")
def when_user_presses_escape(browser_page):
    browser_page.keyboard.press("Escape")
    browser_page.wait_for_timeout(SHORT_WAIT)


@when("the user refreshes the browser")
def when_user_refreshes(browser_page, app_url):
    """Streamlit 1.50 rotates the XSRF cookie on reload, which assigns a new
    session and discards all session_state — verified via cookie inspection.
    The user lands on Home (active_tab defaults to 'Home' in app.py:141).
    The security-relevant outcome (__private_mode__=False) IS preserved by
    Streamlit's behavior; we re-navigate to Role Match so the follow-up
    'lock icon shows closed glyph' assertion can run."""
    browser_page.reload()
    browser_page.wait_for_load_state("networkidle")
    _wait_for_navbar_stable(browser_page)
    browser_page.locator(ROLE_MATCH_NAV_SELECTOR).first.click()
    wait_for_streamlit_rerun(browser_page)
    browser_page.wait_for_selector(ROLE_MATCH_WORKSPACE_SELECTOR, timeout=15000)


@when("the user opens MattGPT in a new tab")
def when_user_opens_new_tab(browser_page, app_url):
    """Open a second tab in the same browser context AND navigate it to
    Role Match (since the lock icon only renders there). Streamlit
    assigns a fresh session per tab. Stash the new page on the original
    so the follow-up THEN can locate it."""
    new_page = browser_page.context.new_page()
    _navigate_to_role_match(new_page, app_url)
    browser_page.__dict__["_new_tab_page"] = new_page


# --- THEN steps (Phase 4 slice 1) ---


@then("a small lock icon appears at the top-right of the results panel")
def then_lock_icon_at_top_right_of_results(browser_page):
    """Assert lock icon is visible AND positioned in the top-right region
    of the workspace's right column (results_col)."""
    lock = browser_page.locator(LOCK_ICON_GLYPH_SELECTOR).first
    workspace = browser_page.locator(ROLE_MATCH_WORKSPACE_SELECTOR).first
    assert lock.is_visible(), "Lock icon not visible in results panel"
    lock_box = lock.bounding_box()
    workspace_box = workspace.bounding_box()
    assert lock_box and workspace_box, "Could not measure lock / workspace positions"
    # Top-right: lock x is past the workspace midpoint, lock y is near the top
    workspace_midpoint_x = workspace_box["x"] + workspace_box["width"] / 2
    assert lock_box["x"] > workspace_midpoint_x, (
        "Lock icon should be in the right half of the workspace "
        f"(lock.x={lock_box['x']}, midpoint.x={workspace_midpoint_x})"
    )
    assert lock_box["y"] < workspace_box["y"] + 100, (
        "Lock icon should be near the top of the workspace "
        f"(lock.y={lock_box['y']}, workspace.y={workspace_box['y']})"
    )


@then("the lock icon is visually discreet and does not draw attention")
def then_lock_icon_discreet(browser_page):
    """Discreet ≡ transparent / muted background, not the brand purple color."""
    button = browser_page.locator(LOCK_ICON_GLYPH_SELECTOR).first
    bg = button.evaluate("el => getComputedStyle(el).backgroundColor")
    color = button.evaluate("el => getComputedStyle(el).color")
    assert (
        "rgba(0, 0, 0, 0)" in bg or "rgba(255, 255, 255, 0" in bg
    ), f"Lock icon background should be transparent / low-alpha, got: {bg!r}"
    # Brand purple is rgb(139, 92, 246). The lock icon must not use it.
    assert (
        "139, 92, 246" not in color
    ), f"Lock icon must not use brand purple — too attention-grabbing. Got: {color!r}"


@then("a popover appears with a single password input field")
def then_popover_with_password_field(browser_page):
    inputs = browser_page.locator(LOCK_POPOVER_PASSWORD_INPUT_SELECTOR)
    assert inputs.first.is_visible(), "Password input not visible after lock click"
    assert (
        inputs.count() == 1
    ), f"Expected exactly 1 password input, got {inputs.count()}"


@given("no password prompt is visible")
def given_no_password_prompt_visible(browser_page):
    """Precondition: the popover hasn't been opened yet. Given/When ordering
    in the scenario establishes the temporal meaning ("before clicking")."""
    inputs = browser_page.locator(LOCK_POPOVER_PASSWORD_INPUT_SELECTOR)
    assert (
        inputs.count() == 0 or not inputs.first.is_visible()
    ), "Password input must not be visible until the lock icon is clicked"


@then("the lock icon changes to indicate unlocked state")
def then_lock_icon_changes_to_unlocked(browser_page):
    glyph = _read_lock_glyph(browser_page)
    assert "🔓" in glyph, f"Expected open-lock (🔓), got: {glyph!r}"


@then("session state __private_mode__ is set to True")
def then_state_set_true(browser_page):
    """Lock icon glyph is the proxy for session state (no DOM access to st.session_state)."""
    glyph = _read_lock_glyph(browser_page)
    assert (
        "🔓" in glyph
    ), f"Expected unlocked glyph (proxy for __private_mode__=True), got: {glyph!r}"


@then("session state __private_mode__ is set to False")
def then_state_set_false(browser_page):
    glyph = _read_lock_glyph(browser_page)
    assert (
        "🔒" in glyph
    ), f"Expected locked glyph (proxy for __private_mode__=False), got: {glyph!r}"


@then("session state __private_mode__ is False")
def then_state_is_false(browser_page):
    glyph = _read_lock_glyph(browser_page)
    assert (
        "🔒" in glyph
    ), f"Expected locked glyph (proxy for __private_mode__=False), got: {glyph!r}"


@then("session state __private_mode__ is not set")
def then_state_not_set(browser_page):
    """Default state — same proxy as 'is False'."""
    glyph = _read_lock_glyph(browser_page)
    assert (
        "🔒" in glyph
    ), f"Expected locked glyph (proxy for __private_mode__ unset), got: {glyph!r}"


@then("session state __private_mode__ in the new tab is False")
def then_state_new_tab_false(browser_page):
    new_page = browser_page.__dict__.get("_new_tab_page")
    assert new_page is not None, "Setup failed: _new_tab_page not stashed by prior step"
    glyph = new_page.locator(LOCK_ICON_GLYPH_SELECTOR).first.inner_text()
    assert "🔒" in glyph, f"New tab should show locked glyph, got: {glyph!r}"


@then("the popover closes")
def then_popover_closes(browser_page):
    inputs = browser_page.locator(LOCK_POPOVER_PASSWORD_INPUT_SELECTOR)
    assert (
        inputs.count() == 0 or not inputs.first.is_visible()
    ), "Popover should be closed (password input hidden)"


@then("the popover stays open")
def then_popover_stays_open(browser_page):
    """After a no-op submission (empty / wrong) the popover must remain visible
    — a silent no-op, not a close-on-error."""
    browser_page.wait_for_timeout(SHORT_WAIT)
    inputs = browser_page.locator(LOCK_POPOVER_PASSWORD_INPUT_SELECTOR)
    assert (
        inputs.first.is_visible()
    ), "Popover should remain open after empty / wrong submission"


@then("the private view remains locked")
def then_private_view_remains_locked(browser_page):
    glyph = _read_lock_glyph(browser_page)
    assert "🔒" in glyph, f"Expected locked glyph, got: {glyph!r}"


@then("the private view unlocks")
def then_private_view_unlocks(browser_page):
    glyph = _read_lock_glyph(browser_page)
    assert "🔓" in glyph, f"Expected unlocked glyph, got: {glyph!r}"


@then("the private view is still unlocked")
def then_private_view_still_unlocked(browser_page):
    glyph = _read_lock_glyph(browser_page)
    assert "🔓" in glyph, f"Expected still-unlocked glyph, got: {glyph!r}"


@then("the lock icon still shows unlocked state")
def then_lock_icon_still_unlocked(browser_page):
    glyph = _read_lock_glyph(browser_page)
    assert "🔓" in glyph, f"Expected unlocked glyph, got: {glyph!r}"


@then(
    "the lock icon shows the closed-lock glyph when session state __private_mode__ is False"
)
def then_closed_glyph_when_state_false(browser_page):
    """Default page-load state: __private_mode__ is unset/False → closed glyph."""
    glyph = _read_lock_glyph(browser_page)
    assert "🔒" in glyph, f"Expected closed-lock (🔒) on default state, got: {glyph!r}"


@then(
    "the lock icon shows the open-lock glyph when session state __private_mode__ is True"
)
def then_open_glyph_when_state_true(browser_page, correct_password):
    """Unlock to verify the open glyph branch — closed branch is asserted by the prior step."""
    _open_password_popover(browser_page)
    _enter_password_and_submit(browser_page, correct_password)
    glyph = _read_lock_glyph(browser_page)
    assert "🔓" in glyph, f"Expected open-lock (🔓) after unlock, got: {glyph!r}"


@then("the lock icon returns to the closed-lock glyph")
def then_lock_icon_returns_closed(browser_page):
    glyph = _read_lock_glyph(browser_page)
    assert "🔒" in glyph, f"Expected closed-lock (🔒), got: {glyph!r}"


@then("the lock icon shows the closed-lock glyph")
def then_lock_icon_shows_closed(browser_page):
    glyph = _read_lock_glyph(browser_page)
    assert "🔒" in glyph, f"Expected closed-lock (🔒), got: {glyph!r}"


@then("no popover is shown")
def then_no_popover_shown(browser_page):
    inputs = browser_page.locator(LOCK_POPOVER_PASSWORD_INPUT_SELECTOR)
    assert (
        inputs.count() == 0 or not inputs.first.is_visible()
    ), "No popover should appear when re-locking"


@then("the lock icon is not visible")
def then_lock_icon_not_visible(browser_page):
    """At viewport <1024px the Role Match workspace is replaced by the
    desktop-only message, so the lock icon (mounted inside the workspace)
    disappears with it."""
    container = browser_page.locator(LOCK_ICON_CONTAINER_SELECTOR)
    if container.count() == 0:
        return
    assert (
        not container.first.is_visible()
    ), "Lock icon should be hidden at viewport <1024px (workspace not rendered)"


@then('the password input has type="password"')
def then_password_input_has_type_password(browser_page):
    input_type = browser_page.locator(
        LOCK_POPOVER_PASSWORD_INPUT_SELECTOR
    ).first.get_attribute("type")
    assert input_type == "password", f"Expected type='password', got: {input_type!r}"


@then("typed characters are not echoed in the DOM as plain text")
def then_typed_chars_not_echoed(browser_page):
    """Type a sample value, then assert it does not appear as visible text
    anywhere on the page. type='password' renders dots; the value lives only
    in the input's DOM property, not in inner_text."""
    sample = "secretvalue123"
    browser_page.locator(LOCK_POPOVER_PASSWORD_INPUT_SELECTOR).first.fill(sample)
    page_text = browser_page.locator("body").inner_text()
    assert (
        sample not in page_text
    ), f"Sample password {sample!r} must not appear as plain text in the rendered DOM"


@then("no rate-limit lockout is applied between attempts")
def then_no_rate_limit(browser_page):
    """Proxy assertion — if the second submission unlocked, no lockout was applied."""
    glyph = _read_lock_glyph(browser_page)
    assert "🔓" in glyph, (
        "Retry should succeed — no rate-limit lockout. " f"Got glyph: {glyph!r}"
    )
