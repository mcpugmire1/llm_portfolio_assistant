"""
BDD step bindings for landing page + Home card project-count alignment
to the post-Era convention (MATTGPT-104).

Red (step defs) commit: step definitions are bound; assertions target the
DOM elements actually rendered on each surface. Against current production
(landing hero/stats + Home cards still use RAW Industry counts):
  - Banking scenario: FAILS — landing shows 33 / Home card shows 33;
    expected 32 (post-Era).
  - Cross-Industry scenario: FAILS — landing shows 57 / Home card shows 57;
    expected 48 (post-Era).

The Green commit updates banking_landing.py, cross_industry_landing.py,
and category_cards.py to use post-Era counts.

DOM landmarks (from explore-stories.py / category_cards.py inspection):
  - Banking + Cross-Industry hero subtitle: .conversation-header-text p
  - Stats bar Projects Delivered count: .stats-bar .stat with the
    "Projects Delivered" label — first stat in the bar per the existing render.
  - Home Banking card meta: #card-banking .home-cat-meta
  - Home Cross-Industry card meta: #card-cross-industry .home-cat-meta
"""

import json
import re
from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then

scenarios("../features/post_era_project_counts.feature")

# =============================================================================
# CONSTANTS
# =============================================================================

NARRATIVE_CATEGORY = "Professional Narrative"
BANKING_INDUSTRY = "Financial Services / Banking"
CROSS_INDUSTRY = "Cross Industry"

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CORPUS_PATH = _REPO_ROOT / "echo_star_stories_nlp.jsonl"

SHORT_WAIT = 200
LONG_TIMEOUT = 30000


# =============================================================================
# HELPERS
# =============================================================================


def _load_corpus():
    if not CORPUS_PATH.exists():
        raise AssertionError(
            f"Story corpus not found at {CORPUS_PATH}. MATTGPT-104 BDD "
            f"requires the active corpus to compute expected counts."
        )
    stories = []
    with open(CORPUS_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                stories.append(json.loads(line))
    return stories


def _post_era_count(stories, industry):
    """Count stories with Industry == industry AND Category != Professional Narrative."""
    return sum(
        1
        for s in stories
        if s.get("Industry") == industry and s.get("Category") != NARRATIVE_CATEGORY
    )


def _wait_for_streamlit_rerun(page):
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


def _click_category_card(page, card_id, landing_marker_selector):
    """Click a Home category card's hidden Streamlit button (the JS-bridge
    pattern) and wait for the destination landing page to render.

    Pattern: HTML card with id="card-X" triggers a JS-bridged hidden
    Streamlit button keyed "card_btn_X". The hidden button sets
    active_tab and triggers a rerun. Clicking the hidden button directly
    is more reliable than synthesizing clicks on the visible HTML card.
    """
    btn_key = card_id.replace("card-", "card_btn_").replace("-", "_")
    hidden_btn = page.locator(f"[class*='st-key-{btn_key}'] button").first
    hidden_btn.wait_for(state="attached", timeout=LONG_TIMEOUT)
    hidden_btn.dispatch_event("click")
    _wait_for_streamlit_rerun(page)
    page.wait_for_selector(landing_marker_selector, timeout=LONG_TIMEOUT)


def _read_count_from_text(text):
    """Extract the first integer from a text blob."""
    match = re.search(r"\d+", text)
    if not match:
        raise AssertionError(f"Could not find an integer in element text: {text!r}")
    return int(match.group(0))


def _read_stats_projects_delivered(page):
    """Read the Projects Delivered count from the .stats-bar.

    Pattern from banking_landing.py / cross_industry_landing.py:
        <div class="stats-bar">
          <div class="stat">
            <div class="stat-number">{total_projects}</div>
            <div class="stat-label">Projects Delivered</div>
          </div>
          ...
        </div>
    Locate the .stat whose label is "Projects Delivered", then read its
    .stat-number text.
    """
    stat = page.locator(
        ".stats-bar .stat:has(.stat-label:has-text('Projects Delivered'))"
    ).first
    stat.wait_for(state="visible", timeout=LONG_TIMEOUT)
    number_text = stat.locator(".stat-number").first.inner_text().strip()
    return _read_count_from_text(number_text)


# =============================================================================
# GIVEN — Navigation
# =============================================================================


@given("the user navigates to the Banking landing page")
def navigate_to_banking_landing(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    _click_category_card(
        browser_page,
        card_id="card-banking",
        landing_marker_selector="h1:has-text('Financial Services Expertise')",
    )


@given("the user navigates to the Cross-Industry landing page")
def navigate_to_cross_industry_landing(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    _click_category_card(
        browser_page,
        card_id="card-cross-industry",
        landing_marker_selector="h1:has-text('Cross-Industry')",
    )


@given("the user navigates to the home page")
def navigate_to_home(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    browser_page.wait_for_selector("#card-banking", timeout=LONG_TIMEOUT)


# =============================================================================
# THEN — Count assertions (dynamically computed from corpus)
# =============================================================================


@then("the Banking hero subtitle should contain the post-Era Banking count")
def assert_banking_hero_post_era(browser_page):
    stories = _load_corpus()
    expected = _post_era_count(stories, BANKING_INDUSTRY)
    subtitle = browser_page.locator(".conversation-header-text p").first
    subtitle.wait_for(state="visible", timeout=LONG_TIMEOUT)
    text = subtitle.inner_text()
    actual = _read_count_from_text(text)
    assert actual == expected, (
        f"Banking landing hero subtitle should show {expected} (post-Era), "
        f"found {actual} in text: {text!r}. MATTGPT-104: hero source still "
        f"uses raw Industry count."
    )


@then("the Banking stats bar should display the post-Era Banking count")
def assert_banking_stats_post_era(browser_page):
    stories = _load_corpus()
    expected = _post_era_count(stories, BANKING_INDUSTRY)
    actual = _read_stats_projects_delivered(browser_page)
    assert actual == expected, (
        f"Banking landing stats bar should show {expected} (post-Era), "
        f"found {actual}. MATTGPT-104: stats source still uses raw count."
    )


@then(
    "the Cross-Industry hero subtitle should contain the post-Era Cross-Industry count"
)
def assert_cross_industry_hero_post_era(browser_page):
    stories = _load_corpus()
    expected = _post_era_count(stories, CROSS_INDUSTRY)
    subtitle = browser_page.locator(".conversation-header-text p").first
    subtitle.wait_for(state="visible", timeout=LONG_TIMEOUT)
    text = subtitle.inner_text()
    actual = _read_count_from_text(text)
    assert actual == expected, (
        f"Cross-Industry landing hero subtitle should show {expected} "
        f"(post-Era), found {actual} in text: {text!r}. MATTGPT-104: hero "
        f"source still uses raw Industry count."
    )


@then("the Cross-Industry stats bar should display the post-Era Cross-Industry count")
def assert_cross_industry_stats_post_era(browser_page):
    stories = _load_corpus()
    expected = _post_era_count(stories, CROSS_INDUSTRY)
    actual = _read_stats_projects_delivered(browser_page)
    assert actual == expected, (
        f"Cross-Industry landing stats bar should show {expected} (post-Era), "
        f"found {actual}. MATTGPT-104: stats source still uses raw count."
    )


@then(parsers.parse('the Banking category card meta should contain "{text}"'))
def assert_home_banking_card_meta_contains(browser_page, text):
    meta = browser_page.locator("#card-banking .home-cat-meta").first
    meta.wait_for(state="visible", timeout=LONG_TIMEOUT)
    actual = meta.inner_text()
    assert text in actual, (
        f"Banking card meta should contain {text!r}, got: {actual!r}. "
        f"MATTGPT-108: Home cards now use descriptive copy, not counts."
    )


@then(parsers.parse('the Cross-Industry category card meta should contain "{text}"'))
def assert_home_cross_industry_card_meta_contains(browser_page, text):
    meta = browser_page.locator("#card-cross-industry .home-cat-meta").first
    meta.wait_for(state="visible", timeout=LONG_TIMEOUT)
    actual = meta.inner_text()
    assert text in actual, (
        f"Cross-Industry card meta should contain {text!r}, got: {actual!r}. "
        f"MATTGPT-108: Home cards now use descriptive copy, not counts."
    )
