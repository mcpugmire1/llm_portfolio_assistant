"""BDD steps for MATTGPT-212: story detail sidebar pill rendering.

Both scenarios open the Cendian story via deeplink and count pills against the
story's own field length. Counting against the fixture (not a hardcoded 15/28)
means a corpus edit to Cendian's Competencies or public_tags will re-baseline
the assertion instead of breaking it.

Pill containers are located by anchoring on the section header text and
walking to the next stMarkdown sibling via XPath. No data-* attribute is
added to production code just for test selectors.

The deeplink @when step and its two helper functions are duplicated from
test_explore_stories.py rather than imported. pytest-bdd's step registration
scans only the collecting module for decorated defs; imports do not surface
them. Confirmed empirically on 2026-08-26: an imported @when failed to
resolve. Duplication is the standing convention in this suite (test_home.py,
test_role_match.py, and now this one — the third copy). The proper fix is to
move shared step defs to conftest.py; that refactor is tracked as
MATTGPT-213. Before adding a fourth copy, do MATTGPT-213 first.
"""

import json
from pathlib import Path

from pytest_bdd import parsers, scenarios, then, when

scenarios("../features/story_detail_sidebar.feature")

CENDIAN_STORY_ID = (
    "integrating-a-chemical-logistics-network-across-every-partner-capability"
    "|cendian-chemical-logistics"
)

SHORT_WAIT = 200


# --- Duplicated from test_explore_stories.py; see MATTGPT-213 before copying again ---


def wait_for_content(page, selector, timeout=10000):
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return True
    except Exception:
        return False


def wait_for_streamlit_rerun(page, timeout=15000):
    from playwright.sync_api import expect as pw_expect

    stapp = page.locator('[data-testid="stApp"]')
    try:
        pw_expect(stapp).to_have_attribute(
            "data-test-script-state", "running", timeout=2000
        )
    except Exception:
        pass
    pw_expect(stapp).to_have_attribute(
        "data-test-script-state", "notRunning", timeout=timeout
    )
    page.wait_for_timeout(SHORT_WAIT)


@when(parsers.parse('the user navigates to "{url_params}"'))
def navigate_with_params(browser_page, app_url, url_params):
    browser_page.goto(f"{app_url}{url_params}")
    wait_for_streamlit_rerun(browser_page)
    if "?story=" in url_params:
        wait_for_content(browser_page, ".es-results-count", timeout=15000)
        wait_for_content(
            browser_page,
            ".es-detail-header, .star-label, #btn-share-story",
            timeout=10000,
        )


# --- MATTGPT-212 specifics ---


def _load_story_by_id(story_id: str) -> dict:
    corpus = Path(__file__).parents[3] / "echo_star_stories_nlp.jsonl"
    with corpus.open(encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("id") == story_id:
                return rec
    raise AssertionError(f"Story not found in corpus: {story_id}")


def _parse_public_tags(raw) -> list[str]:
    """public_tags is stored as a comma-joined string post-MATTGPT-072."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return [t for t in raw if t and str(t).strip()]
    return [t.strip() for t in str(raw).split(",") if t.strip()]


def _pills_following_header(browser_page, header_text: str):
    """Locate spans in the pill container that follows a section header.

    Each Streamlit element is wrapped as
      div[data-testid="stElementContainer"] > div[data-testid="stMarkdown"] > ...
    so sibling relationships live at stElementContainer level, not stMarkdown.
    Anchors on the stMarkdown whose text contains the header copy, walks up
    to its stElementContainer parent, walks to the next stElementContainer
    sibling, then locates spans inside.

    Waits for the header stMarkdown to be visible first: the deeplink @when
    step waits for .es-detail-header to appear, but the sidebar renders after
    the STAR sections, so the header text may not exist yet when the Then
    step first runs.
    """
    header_selector = f'div[data-testid="stMarkdown"]:has-text("{header_text}")'
    browser_page.wait_for_selector(header_selector, timeout=15000)
    header_container = browser_page.locator(
        f'div[data-testid="stElementContainer"]:has({header_selector})'
    ).first
    return header_container.locator(
        'xpath=following-sibling::div[@data-testid="stElementContainer"][1]//span'
    )


@then(
    "the Core Competencies pill count matches " "the story's Competencies field length"
)
def verify_competencies_pill_count(browser_page):
    story = _load_story_by_id(CENDIAN_STORY_ID)
    expected = len([c for c in (story.get("Competencies") or []) if c])
    pills = _pills_following_header(browser_page, "CORE COMPETENCIES")
    actual = pills.count()
    assert actual == expected, (
        f"Core Competencies pill count {actual} does not match story's "
        f"Competencies field length {expected} for {CENDIAN_STORY_ID}"
    )


@then(
    "the Technologies and Practices pill count matches "
    "the story's public_tags field length"
)
def verify_tags_pill_count(browser_page):
    story = _load_story_by_id(CENDIAN_STORY_ID)
    expected = len(_parse_public_tags(story.get("public_tags")))
    pills = _pills_following_header(browser_page, "TECHNOLOGIES & PRACTICES")
    actual = pills.count()
    assert actual == expected, (
        f"Technologies and Practices pill count {actual} does not match "
        f"story's public_tags field length {expected} for {CENDIAN_STORY_ID}"
    )
