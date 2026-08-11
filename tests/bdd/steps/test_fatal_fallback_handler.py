"""
BDD step definitions for fatal_fallback_handler.feature.

Tests that rag_answer's fatal handler (except Exception at line 1751) marks
the response degraded=True and logs the exception unconditionally via the
module logger, regardless of the DEBUG flag.
"""

import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pytest_bdd import given, scenarios, then, when

# Mock streamlit before any backend_service imports at collection time.
if "streamlit" not in sys.modules:
    _st_mock = MagicMock()
    _st_mock.session_state = {}
    _st_mock.secrets = {}
    sys.modules["streamlit"] = _st_mock
    sys.modules["streamlit.components"] = MagicMock()
    sys.modules["streamlit.components.v1"] = MagicMock()

scenarios("../features/fatal_fallback_handler.feature")

FAKE_STORIES = [
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

FAKE_POOL = [{**s, "_search_score": 0.6} for s in FAKE_STORIES]


@pytest.fixture
def ctx():
    return {}


@given("stories are loaded for the fatal fallback handler test")
def given_stories(ctx):
    ctx["stories"] = FAKE_STORIES


@when("rag_answer is called with a semantic_search that raises RuntimeError")
def when_rag_crashes(ctx, caplog):
    from dotenv import load_dotenv

    load_dotenv(Path(".env"))

    _st_mock = sys.modules["streamlit"]
    _st_mock.session_state.clear()
    _st_mock.session_state["__suppress_logging__"] = True

    from ui.pages.ask_mattgpt.backend_service import rag_answer

    with caplog.at_level(logging.ERROR):
        with (
            patch(
                "ui.pages.ask_mattgpt.backend_service.is_portfolio_query_semantic",
                return_value=(True, 1.0, "leadership", "leadership"),
            ),
            patch(
                "ui.pages.ask_mattgpt.backend_service.semantic_search",
                side_effect=RuntimeError("injected crash"),
            ),
            patch("ui.pages.ask_mattgpt.backend_service.log_query"),
        ):
            ctx["result"] = rag_answer(
                "Why should we hire Matt?",
                {"q": "Why should we hire Matt?"},
                ctx["stories"],
            )

    ctx["caplog_records"] = caplog.records


@when("rag_answer is called with a fully mocked happy-path pipeline")
def when_rag_happy(ctx):
    from dotenv import load_dotenv

    load_dotenv(Path(".env"))

    _st_mock = sys.modules["streamlit"]
    _st_mock.session_state.clear()
    _st_mock.session_state["__suppress_logging__"] = True

    from ui.pages.ask_mattgpt.backend_service import rag_answer

    with (
        patch(
            "ui.pages.ask_mattgpt.backend_service.is_portfolio_query_semantic",
            return_value=(True, 1.0, "leadership", "leadership"),
        ),
        patch(
            "ui.pages.ask_mattgpt.backend_service.semantic_search",
            return_value={
                "results": FAKE_POOL,
                "confidence": "high",
                "top_score": 0.6,
            },
        ),
        patch(
            "ui.pages.ask_mattgpt.backend_service._generate_agy_response",
            return_value="Test response.",
        ),
        patch("ui.pages.ask_mattgpt.backend_service.log_query"),
    ):
        ctx["result"] = rag_answer(
            "Tell me about Matt's leadership",
            {"q": "Tell me about Matt's leadership"},
            ctx["stories"],
        )


@then("the returned dict has degraded equal to True")
def then_degraded_true(ctx):
    result = ctx.get("result", {})
    assert result.get("degraded") is True, (
        f"Expected degraded=True but got degraded={result.get('degraded')!r}\n"
        f"Full result keys: {list(result.keys())}"
    )


@then("an exception traceback was logged unconditionally")
def then_traceback_logged(ctx):
    records = ctx.get("caplog_records", [])
    error_records = [
        r
        for r in records
        if r.levelno >= logging.ERROR and r.exc_info and r.exc_info[0] is not None
    ]
    assert error_records, (
        f"Expected an ERROR-level log record with exc_info but found none.\n"
        f"All captured records: {[(r.levelname, r.message) for r in records]}"
    )


@then("the returned dict has degraded equal to False")
def then_degraded_false(ctx):
    result = ctx.get("result", {})
    assert result.get("degraded") is False, (
        f"Expected degraded=False but got degraded={result.get('degraded')!r}\n"
        f"Full result keys: {list(result.keys())}"
    )
