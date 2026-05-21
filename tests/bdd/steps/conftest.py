"""
Shared Playwright fixtures for BDD step definitions.

A single session-scoped browser instance is shared across ALL BDD test
files (test_explore_stories.py, test_role_match.py, etc.) to avoid the
Playwright sync/async clash that occurs when multiple files each call
sync_playwright().start() in the same pytest session.

Each test gets its own browser_page (fresh context + page) for isolation.

Also registers a pytest-bdd hook to auto-skip scenarios tagged @deferred.
Deferred scenarios are kept in the .feature files as design intent for
future tickets but intentionally not implemented — typically because the
production code has dead-flag stubs or because the locked spec turned out
to describe behavior that would add complexity for zero user-visible
benefit. The scenario comment + BACKLOG entry document the rationale.
"""

import pytest


def pytest_bdd_apply_tag(tag, function):
    """Convert @deferred scenario tags into pytest.mark.skip.

    Tagged scenarios are still collected (so they appear in test discovery
    and Red-A counts), but skipped at runtime with a generic reason that
    points the reader to the scenario comment and BACKLOG ticket for the
    full rationale.
    """
    if tag == "deferred":
        marker = pytest.mark.skip(
            reason="Deferred — scenario kept as design intent. See scenario "
            "comment + BACKLOG ticket for rationale."
        )
        marker(function)
        return True
    return None


_browser_instance = None
_playwright_instance = None


@pytest.fixture(scope="session")
def shared_browser():
    """Create a shared browser instance for all BDD tests in the session."""
    global _browser_instance, _playwright_instance
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip(
            "Playwright not installed. Run: pip install playwright && playwright install chromium"
        )

    _playwright_instance = sync_playwright().start()
    _browser_instance = _playwright_instance.chromium.launch(headless=True)
    yield _browser_instance
    _browser_instance.close()
    _playwright_instance.stop()


@pytest.fixture
def browser_page(shared_browser):
    """Create a fresh page for each test, reusing the shared browser."""
    context = shared_browser.new_context(
        viewport={"width": 1280, "height": 900},
        permissions=["clipboard-read", "clipboard-write"],
    )
    page = context.new_page()
    yield page
    page.close()
    context.close()


@pytest.fixture
def app_url():
    """URL of the running Streamlit app."""
    return "http://localhost:8501"
