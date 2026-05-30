"""
BDD step bindings for the wireframe-locked navigation label rename (MATTGPT-100).

Red (step defs) commit: step definitions are implemented and bound via the
scenarios() loader. Against current production (nav still reads Home / Explore
Stories / Ask MattGPT / Role Match / About Matt):
  - Scenario 1 fails — "My Work", "Ask Agy", "My Profile" are not in the nav.
  - Scenario 2 fails — "Explore Stories", "Ask MattGPT", "About Matt" still
    appear in the nav.
  - Scenario 3 fails — no nav button labeled "My Work" to click.

The coordinated rename (display labels + session_state["active_tab"] values)
lands in the Green commit per the CLAUDE.md testing protocol.

Nav buttons are scoped via [class*="st-key-topnav_"] — Streamlit wraps each
nav button in a key-derived class (key=f"topnav_{name}" in
ui/components/navbar.py). Substring match survives the Green rename of names.
"""

from pytest_bdd import given, scenarios, then, when

scenarios("../features/nav_labels.feature")


SHORT_WAIT = 200  # ms


def wait_for_streamlit_rerun(page):
    """Wait for Streamlit to finish a rerun after an action."""
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


def _nav_text(page) -> str:
    """Concatenated inner text of all top-nav buttons. Substring-scan target."""
    return " ".join(page.locator('[class*="st-key-topnav_"]').all_inner_texts())


@given("the user navigates to the home page")
def navigate_to_home(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    # Wait for any top-nav button to render — Home is stable across the rename.
    browser_page.wait_for_selector('[class*="st-key-topnav_"]', timeout=30000)


@then(
    'the navigation should display "Home", "My Work", "Ask Agy", "Role Match", and "My Profile"'
)
def assert_nav_displays_new_labels(browser_page):
    expected = ["Home", "My Work", "Ask Agy", "Role Match", "My Profile"]
    nav = _nav_text(browser_page)
    missing = [label for label in expected if label not in nav]
    assert not missing, (
        f"Nav labels missing from top navigation: {missing}. MATTGPT-100: nav "
        f"should render the wireframe-locked taxonomy. Got nav text: {nav!r}"
    )


@then(
    'the navigation should not display "Explore Stories", "Ask MattGPT", or "About Matt"'
)
def assert_nav_excludes_old_labels(browser_page):
    forbidden = ["Explore Stories", "Ask MattGPT", "About Matt"]
    nav = _nav_text(browser_page)
    present = [label for label in forbidden if label in nav]
    assert not present, (
        f"Pre-rename nav labels still present: {present}. MATTGPT-100: these "
        f"labels should be renamed (Strategy B coordinated rename). Got nav "
        f"text: {nav!r}"
    )


@when('the user clicks the "My Work" navigation label')
def click_my_work(browser_page):
    btn = browser_page.locator('[class*="st-key-topnav_"] button').filter(
        has_text="My Work"
    )
    assert btn.count() > 0, (
        "Nav button labeled 'My Work' not found — MATTGPT-100 rename not "
        "applied yet (production currently labels this 'Explore Stories')."
    )
    btn.first.click()
    wait_for_streamlit_rerun(browser_page)


@then("the project-stories filter UI should be shown")
def assert_filter_ui_shown(browser_page):
    # .results-count is unique to Explore Stories — same DOM-observable proxy
    # used in test_home.py for navigation to that surface (file name stays
    # explore_stories.py per the Strategy B scope; only the display label and
    # session_state["active_tab"] string change in Green).
    count_el = browser_page.locator(".results-count").first
    count_el.wait_for(state="visible", timeout=15000)
    assert count_el.count() > 0, (
        "Explore Stories filter UI did not render after clicking the renamed "
        "nav label — routing did not survive the coordinated rename."
    )
