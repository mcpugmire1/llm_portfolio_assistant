"""
Shared Playwright fixtures for BDD step definitions.

A single session-scoped browser instance is shared across ALL BDD test
files (test_explore_stories.py, test_role_match.py, etc.) to avoid the
Playwright sync/async clash that occurs when multiple files each call
sync_playwright().start() in the same pytest session.

Each test gets its own browser_page (fresh context + page) for isolation.
"""

import pytest

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
