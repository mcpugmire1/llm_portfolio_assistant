"""
BDD step definitions for cluster_promotion_kw.feature (MATTGPT-074).

Tests that entity cluster promotion is suppressed when kw scores are
dispersed across the entity pool (signaling a specific query), and
fires when kw is uniform (signaling a broad entity query).
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pytest_bdd import given, scenarios, then, when

if "streamlit" not in sys.modules:
    _st_mock = MagicMock()
    _st_mock.session_state = {}
    _st_mock.secrets = {}
    sys.modules["streamlit"] = _st_mock
    sys.modules["streamlit.components"] = MagicMock()
    sys.modules["streamlit.components.v1"] = MagicMock()

scenarios("../features/cluster_promotion_kw.feature")

_ENTITY_FIELD = "Client"
_ENTITY_VALUE = "AT&T"


def _entity_story(i, kw):
    return {
        "id": f"att-story-{i}|att",
        "Title": f"AT&T Story {i}",
        "Client": "AT&T",
        "Employer": "AT&T",
        "Theme": "Execution & Delivery",
        "Category": "Execution & Delivery",
        "pc": 0.5,
        "kw": kw,
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


_NON_ENTITY_STORY = {
    "id": "other-story-0|accenture",
    "Title": "Other Story",
    "Client": "Accenture",
    "Employer": "Accenture",
    "Theme": "Execution & Delivery",
    "Category": "Execution & Delivery",
    "pc": 0.4,
    "kw": 0.0,
    "blend": 0.4,
    "_search_score": 0.4,
    "Situation": "A situation.",
    "Task": "A task.",
    "Action": ["An action."],
    "Result": ["A result."],
    "Process": [],
    "Performance": [],
    "Competencies": [],
    "public_tags": [],
}


@pytest.fixture
def ctx():
    return {}


@given("a pool of 3 entity-matched stories with uniform kw scores")
def given_3_uniform(ctx):
    ctx["pool"] = [_entity_story(i, 0.333) for i in range(3)] + [_NON_ENTITY_STORY]


@given("a pool of 3 entity-matched stories with dispersed kw scores")
def given_3_dispersed(ctx):
    ctx["pool"] = [
        _entity_story(0, 0.667),
        _entity_story(1, 0.0),
        _entity_story(2, 0.0),
        _NON_ENTITY_STORY,
    ]


@given("a pool of 3 entity-matched stories with all-zero kw scores")
def given_3_zero(ctx):
    ctx["pool"] = [_entity_story(i, 0.0) for i in range(3)] + [_NON_ENTITY_STORY]


@given("a pool of 2 entity-matched stories with uniform kw scores")
def given_2_uniform(ctx):
    ctx["pool"] = [_entity_story(i, 0.333) for i in range(2)] + [_NON_ENTITY_STORY]


@when("rag_answer is called with an entity query")
def when_rag_answer(ctx):
    from dotenv import load_dotenv

    load_dotenv(Path(".env"))

    _st_mock = sys.modules["streamlit"]
    _st_mock.session_state.clear()
    _st_mock.session_state["__suppress_logging__"] = True

    from ui.pages.ask_mattgpt.backend_service import rag_answer

    pool = ctx["pool"]
    entity_stories = [s for s in pool if s.get(_ENTITY_FIELD) == _ENTITY_VALUE]
    synthesis_spy = MagicMock(return_value=entity_stories)

    with (
        patch(
            "ui.pages.ask_mattgpt.backend_service.semantic_search",
            return_value={"results": pool, "confidence": "high", "top_score": 0.5},
        ),
        patch(
            "ui.pages.ask_mattgpt.backend_service.detect_entity",
            return_value=(_ENTITY_FIELD, _ENTITY_VALUE),
        ),
        patch(
            "ui.pages.ask_mattgpt.backend_service.is_portfolio_query_semantic",
            return_value=(True, 0.7, "background", "background"),
        ),
        patch(
            "ui.pages.ask_mattgpt.backend_service.get_synthesis_stories",
            synthesis_spy,
        ),
        patch(
            "ui.pages.ask_mattgpt.backend_service._generate_agy_response",
            return_value="Test response",
        ),
        patch("ui.pages.ask_mattgpt.backend_service.log_query"),
    ):
        ctx["result"] = rag_answer(
            "What did Matt do at AT&T?",
            {"q": "What did Matt do at AT&T?"},
            [],
        )

    ctx["synthesis_called"] = synthesis_spy.called


@then("synthesis mode is triggered")
def then_synthesis_triggered(ctx):
    assert ctx.get(
        "synthesis_called"
    ), "Expected get_synthesis_stories to be called (synthesis mode) but it was not."


@then("synthesis mode is suppressed")
def then_synthesis_suppressed(ctx):
    assert not ctx.get(
        "synthesis_called"
    ), "Expected get_synthesis_stories NOT to be called (standard mode) but it was."
