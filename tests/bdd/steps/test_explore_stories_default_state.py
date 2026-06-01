"""
BDD step bindings for the Explore Stories default-state change (MATTGPT-098).

Red (step defs) commit: step definitions are bound; assertions target the
DOM elements that are actually rendered (AgGrid rows on the page, plus the
results-count text). Against current production:
  - Scenario 1 (default excludes Professional Narrative): FAILS with
    AssertionError — current default shows all 113 stories, expected 103
    after the -098 exclusion lands.
  - Scenario 2 (default sort Start_Date desc): FAILS with AssertionError —
    current default sort is alphabetical by Title, so the first row's
    Start_Date won't reliably be >= the second row's.

The Green commit lands the default-state change to explore_stories.py.

Implementation notes per existing patterns in test_explore_stories.py:
  - .results-count text format: "Showing X–Y of N projects"
    (explore_stories.py:2236). Parse N via regex "of\\s+(\\d+)".
  - AgGrid .ag-row elements are accessible directly on browser_page —
    NOT inside a frame_locator. Existing test_explore_stories.py:80-83
    waits for .ag-root-wrapper + .ag-row on the parent page.
  - AgGrid cells carry a col-id attribute matching the column field name
    (e.g., col-id="Start_Date" for the Start_Date column).
"""

import json
import re
from pathlib import Path

from pytest_bdd import given, scenarios, then

scenarios("../features/explore_stories_default_state.feature")

# =============================================================================
# CONSTANTS
# =============================================================================

NARRATIVE_CATEGORY = "Professional Narrative"

# Path to the active story corpus JSONL.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CORPUS_PATH = _REPO_ROOT / "echo_star_stories_nlp.jsonl"

SHORT_WAIT = 200  # ms — quick UI updates after a Streamlit rerun
LONG_TIMEOUT = 30000  # ms — Streamlit rerun + AgGrid initial render
RESULTS_COUNT_TIMEOUT = 15000  # ms — results-count element render


# =============================================================================
# HELPERS
# =============================================================================


def _load_corpus():
    """Load story corpus from JSONL."""
    if not CORPUS_PATH.exists():
        raise AssertionError(
            f"Story corpus not found at {CORPUS_PATH}. MATTGPT-098 BDD "
            f"requires the active corpus to compute expected counts."
        )
    stories = []
    with open(CORPUS_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                stories.append(json.loads(line))
    return stories


def _count_post_era(stories):
    """Count stories that are NOT Professional Narrative."""
    return sum(1 for s in stories if s.get("Category") != NARRATIVE_CATEGORY)


def _count_narrative(stories):
    """Count Professional Narrative stories."""
    return sum(1 for s in stories if s.get("Category") == NARRATIVE_CATEGORY)


def _wait_for_streamlit_rerun(page):
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


def _read_results_count(page):
    """Parse the .results-count element's displayed TOTAL count.

    The element text is rendered as "Showing X–Y of N projects" by
    explore_stories.py:2236. We want N (the total), not X (the page start).
    Regex: "of\\s+(\\d+)" captures the digits immediately after "of".
    """
    elem = page.locator(".results-count").first
    elem.wait_for(state="visible", timeout=RESULTS_COUNT_TIMEOUT)
    text = elem.inner_text()
    match = re.search(r"of\s+(\d+)", text)
    if not match:
        raise AssertionError(
            f".results-count text does not match the expected 'Showing X-Y "
            f"of N projects' format: {text!r}. Has the rendering changed?"
        )
    return int(match.group(1))


# =============================================================================
# GIVEN — Navigation
# =============================================================================


@given("the user navigates to the My Work page")
def navigate_to_my_work(browser_page, app_url):
    """Open the app and click the My Work tab, then wait for the results
    count + AgGrid to render — confirming the page rendered + Table view loaded.
    """
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    browser_page.wait_for_selector("button:has-text('My Work')", timeout=LONG_TIMEOUT)
    nav_button = browser_page.locator("button:has-text('My Work'):visible").first
    nav_button.click()
    _wait_for_streamlit_rerun(browser_page)
    browser_page.wait_for_selector(".results-count", timeout=LONG_TIMEOUT)
    # Wait for AgGrid Table view to render (default view).
    try:
        browser_page.wait_for_selector(".ag-root-wrapper", timeout=LONG_TIMEOUT)
        browser_page.wait_for_selector(".ag-row", timeout=15000)
    except Exception:
        # Not in Table view — scenarios may still pass on results-count alone,
        # but sort-order scenario will surface the issue with a clear error.
        pass


# =============================================================================
# THEN — Default-state assertions
# =============================================================================


@then(
    "the visible Table results count should equal the corpus total minus the 10 "
    "Professional Narrative stories"
)
def assert_default_excludes_narrative(browser_page):
    stories = _load_corpus()
    total = len(stories)
    narrative = _count_narrative(stories)
    expected = _count_post_era(stories)
    actual = _read_results_count(browser_page)
    assert actual == expected, (
        f"Default My Work view should display {expected} stories "
        f"(corpus total {total} minus {narrative} Professional Narrative), "
        f"found {actual}. MATTGPT-098: default Professional Narrative "
        f"exclusion not applied."
    )


@then(
    "the first visible Table row's Start_Date should be greater than or equal "
    "to the second visible Table row's Start_Date"
)
def assert_sort_descending(browser_page):
    # AgGrid renders inside a Streamlit custom component iframe — access via
    # frame_locator per the existing test_explore_stories.py:111-120 pattern.
    aggrid_frame = browser_page.frame_locator(
        "[data-testid='stCustomComponentV1']"
    ).first
    rows = aggrid_frame.locator(".ag-row")
    # Wait for at least 2 rows to render. AgGrid can take time to mount.
    rows.nth(1).wait_for(state="visible", timeout=LONG_TIMEOUT)
    row_count = rows.count()
    assert row_count >= 2, (
        f"Need at least 2 visible Table rows to assert sort order; found "
        f"{row_count}. MATTGPT-098 sort assertion cannot run."
    )
    # Parse Start_Date from full row text (avoids AgGrid cell-attribute
    # variability). The Start_Date column renders YYYY-MM strings — find
    # the first 4-digit-year-dash-2-digit-month token in each row.
    date_pattern = re.compile(r"\b(\d{4}-\d{2})\b")
    first_text = rows.nth(0).inner_text()
    second_text = rows.nth(1).inner_text()
    first_match = date_pattern.search(first_text)
    second_match = date_pattern.search(second_text)
    assert (
        first_match is not None
    ), f"Could not find YYYY-MM Start_Date in first row text: {first_text!r}"
    assert (
        second_match is not None
    ), f"Could not find YYYY-MM Start_Date in second row text: {second_text!r}"
    first_date = first_match.group(1)
    second_date = second_match.group(1)
    assert first_date >= second_date, (
        f"Default sort should be Start_Date descending. First row "
        f"Start_Date={first_date!r}, second row Start_Date={second_date!r}. "
        f"MATTGPT-098: default sort not applied (still alphabetical?)."
    )
