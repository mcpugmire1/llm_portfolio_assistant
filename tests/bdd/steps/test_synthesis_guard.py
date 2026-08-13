"""
BDD step definitions for synthesis_guard.feature.

Tests that rag_answer degrades gracefully when portfolio theme metadata is
unsynced (SYNTHESIS_THEMES=[]), reproducing the genuine crash condition
observed in the inline diagnostic harness.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

# Mock streamlit before any backend_service imports at collection time.
if "streamlit" not in sys.modules:
    _st_mock = MagicMock()
    _st_mock.session_state = {}
    _st_mock.secrets = {}
    sys.modules["streamlit"] = _st_mock
    sys.modules["streamlit.components"] = MagicMock()
    sys.modules["streamlit.components.v1"] = MagicMock()

from utils.corpus_loader import load_stories  # noqa: E402

scenarios("../features/synthesis_guard.feature")

FAKE_POOL = [
    {
        "id": f"test-story-{i}",
        "Title": f"Test Story {i}",
        "Client": "RBC",
        "Employer": "Accenture",
        "Role": "Manager",
        "Sub-category": "Leadership",
        "Domain": "Banking",
        "Industry": "Financial Services / Banking",
        "Theme": "Leadership",
        "pc": 0.5,
        "kw": 0.1,
        "blend": 0.5,
        "_search_score": 0.5,
        "Situation": "A situation.",
        "Task": "A task.",
        "Action": ["An action."],
        "Result": ["A result."],
        "Process": [],
        "Performance": [],
        "Competencies": [],
        "public_tags": [],
    }
    for i in range(5)
]


@pytest.fixture
def ctx():
    return {}


@given("stories are loaded for the synthesis guard test")
def given_stories(ctx):
    ctx["stories"] = load_stories("echo_star_stories_nlp.jsonl")


@given("portfolio theme metadata is empty")
def given_empty_themes(ctx, request):
    import ui.pages.ask_mattgpt.backend_service as bs

    original = list(bs.SYNTHESIS_THEMES)
    bs.SYNTHESIS_THEMES.clear()

    def restore():
        bs.SYNTHESIS_THEMES.clear()
        bs.SYNTHESIS_THEMES.extend(original)

    request.addfinalizer(restore)


@when(parsers.parse('rag_answer is called with the synthesis query "{query}"'))
def when_rag_answer(ctx, query):
    from dotenv import load_dotenv

    load_dotenv(Path(".env"))

    _st_mock = sys.modules["streamlit"]
    _st_mock.session_state.clear()
    _st_mock.session_state["__suppress_logging__"] = True

    from ui.pages.ask_mattgpt.backend_service import rag_answer

    stories = ctx["stories"]

    with (
        patch(
            "ui.pages.ask_mattgpt.backend_service.semantic_search",
            return_value={"results": FAKE_POOL, "confidence": "high", "top_score": 0.5},
        ),
        patch(
            "ui.pages.ask_mattgpt.backend_service.is_portfolio_query_semantic",
            return_value=(True, 1.0, "synthesis", "synthesis"),
        ),
        patch(
            "ui.pages.ask_mattgpt.backend_service._generate_agy_response",
            return_value="Test synthesis response",
        ),
        patch("ui.pages.ask_mattgpt.backend_service.log_query"),
    ):
        try:
            ctx["result"] = rag_answer(query, {"q": query}, stories)
        except Exception as e:
            ctx["exception"] = e


@then("no exception is raised")
def then_no_exception(ctx):
    exc = ctx.get("exception")
    assert exc is None, f"Expected no exception but got: {exc!r}"


@then("the response has at least one source")
def then_has_sources(ctx):
    sources = ctx.get("result", {}).get("sources", [])
    assert len(sources) >= 1, f"Expected at least one source but got: {sources!r}"
