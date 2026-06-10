"""
BDD step bindings for the navbar desktop brand-left + space-between layout
(MATTGPT-106).

Red (step defs) gate state: step definitions are implemented and bound via
the scenarios() loader. Against current production (desktop navbar has no
brand element and uses space-evenly across 5 columns):
  - Scenario 1 fails — .navbar-brand element does not exist on desktop.
  - Scenario 2 passes content-wise (5 labels render post-MATTGPT-100) but
    is included as a regression guard against the Green layout change.
  - Scenario 3 passes content-wise (routing intact post-MATTGPT-100) but
    guards against the layout change breaking the Streamlit click bridge.

The coordinated layout change (brand-left HTML + space-between CSS) lands
in the Green commit per the CLAUDE.md testing protocol.

Selectors:
  - .navbar-brand           — new brand element rendered by Green (desktop
                              only; mobile keeps .mobile-brand untouched).
  - [class*="st-key-topnav_"]
                            — nav button container class; substring match
                              survives the MATTGPT-100 label rename and
                              any future Streamlit class normalization.
  - .es-results-count          — Explore Stories filter UI proxy (same DOM
                              marker used by test_nav_labels.py).
"""

from pytest_bdd import given, scenarios, then, when

scenarios("../features/navbar_brand_layout.feature")


SHORT_WAIT = 200  # ms
LONG_WAIT = 15000  # ms


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
    # Wait for any top-nav button to render — Home is stable across renames.
    browser_page.wait_for_selector('[class*="st-key-topnav_"]', timeout=30000)


@then('the navbar should display "MattGPT" to the left of the "Home" nav button')
def assert_brand_left_of_home(browser_page):
    brand = browser_page.locator(".navbar-brand").first
    brand.wait_for(state="visible", timeout=LONG_WAIT)
    assert "MattGPT" in brand.inner_text(), (
        f"Expected '.navbar-brand' element to contain 'MattGPT'; got "
        f"{brand.inner_text()!r}. MATTGPT-106: text-only brand on the left."
    )

    home_btn = browser_page.locator('[class*="st-key-topnav_Home"] button').first
    home_btn.wait_for(state="visible", timeout=LONG_WAIT)

    brand_box = brand.bounding_box()
    home_box = home_btn.bounding_box()
    assert brand_box is not None, "could not measure '.navbar-brand' bounding box"
    assert home_box is not None, "could not measure Home nav button bounding box"
    assert brand_box["x"] < home_box["x"], (
        f"'MattGPT' brand should be positioned left of the 'Home' nav button. "
        f"brand.x={brand_box['x']}, home.x={home_box['x']}. MATTGPT-106 "
        f"wireframe locks brand-left + space-between layout."
    )


@then(
    'the navigation should display "Home", "My Work", "Ask Agy", "Role Match", and "My Profile"'
)
def assert_nav_displays_labels(browser_page):
    expected = ["Home", "My Work", "Ask Agy", "Role Match", "My Profile"]
    nav = _nav_text(browser_page)
    missing = [label for label in expected if label not in nav]
    assert not missing, (
        f"Nav labels missing from top navigation after MATTGPT-106 layout "
        f"change: {missing}. The five MATTGPT-100 labels must survive the "
        f"layout shift. Got nav text: {nav!r}"
    )


@when('the user clicks the "My Work" navigation label')
def click_my_work(browser_page):
    btn = browser_page.locator('[class*="st-key-topnav_"] button').filter(
        has_text="My Work"
    )
    assert btn.count() > 0, (
        "Nav button labeled 'My Work' not found — MATTGPT-100 should have "
        "renamed Explore Stories, and MATTGPT-106 must preserve the label."
    )
    btn.first.click()
    wait_for_streamlit_rerun(browser_page)


@then("the project-stories filter UI should be shown")
def assert_filter_ui_shown(browser_page):
    # .es-results-count is the DOM-observable proxy for the Explore Stories
    # surface (same marker used by test_nav_labels.py). If the layout
    # change breaks the Streamlit click bridge or the routing wire-up,
    # this assertion will fail because no filter UI renders.
    count_el = browser_page.locator(".es-results-count").first
    count_el.wait_for(state="visible", timeout=LONG_WAIT)
    assert count_el.count() > 0, (
        "Explore Stories filter UI did not render after clicking the "
        "'My Work' nav label — MATTGPT-106 layout change broke routing."
    )
