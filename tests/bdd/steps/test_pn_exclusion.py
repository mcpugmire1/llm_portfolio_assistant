"""
BDD step definitions for pn_exclusion.feature (MATTGPT-169).

Tests that Professional Narrative stories are excluded from retrieval
only when intent_family is in the technical allowlist, and that the
guard fires correctly when the allowlist filter would empty the pool.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

if "streamlit" not in sys.modules:
    _st_mock = MagicMock()
    _st_mock.session_state = {}
    _st_mock.secrets = {}
    sys.modules["streamlit"] = _st_mock
    sys.modules["streamlit.components"] = MagicMock()
    sys.modules["streamlit.components.v1"] = MagicMock()

scenarios("../features/pn_exclusion.feature")

_NON_PN_STORIES = [
    {
        "id": f"delivery-story-{i}|accenture",
        "Title": f"Delivery Story {i}",
        "Client": "Accenture",
        "Employer": "Accenture",
        "Theme": "Execution & Delivery",
        "Category": "Execution & Delivery",
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
    for i in range(3)
]

_PN_STORIES = [
    {
        "id": f"pn-story-{i}|career-narrative",
        "Title": f"Why Hire Matt {i}",
        "Client": "Career Narrative",
        "Employer": "Accenture",
        "Theme": "Professional Narrative",
        "Category": "Professional Narrative",
        "pc": 0.48,
        "kw": 0.2,
        "blend": 0.48,
        "_search_score": 0.48,
        "Situation": "A situation.",
        "Task": "A task.",
        "Action": ["An action."],
        "Result": ["A result."],
        "Process": [],
        "Performance": [],
        "Competencies": [],
        "public_tags": [],
    }
    for i in range(2)
]


@pytest.fixture
def ctx():
    return {}


@given("a mixed pool containing non-narrative and Professional Narrative stories")
def given_mixed_pool(ctx):
    ctx["pool"] = _NON_PN_STORIES + _PN_STORIES


@given("a pool containing only Professional Narrative stories")
def given_pn_only_pool(ctx):
    ctx["pool"] = list(_PN_STORIES)


@when(parsers.parse('rag_answer is called with intent family "{family}"'))
def when_rag_answer(ctx, family):
    from dotenv import load_dotenv

    load_dotenv(Path(".env"))

    _st_mock = sys.modules["streamlit"]
    _st_mock.session_state.clear()
    _st_mock.session_state["__suppress_logging__"] = True

    from ui.pages.ask_mattgpt.backend_service import rag_answer

    pool = ctx["pool"]

    with (
        patch(
            "ui.pages.ask_mattgpt.backend_service.semantic_search",
            return_value={"results": pool, "confidence": "high", "top_score": 0.5},
        ),
        patch(
            "ui.pages.ask_mattgpt.backend_service.is_portfolio_query_semantic",
            return_value=(True, 0.7, family, family),
        ),
        patch(
            "ui.pages.ask_mattgpt.backend_service._generate_agy_response",
            return_value="Test response",
        ),
        patch("ui.pages.ask_mattgpt.backend_service.log_query"),
    ):
        ctx["result"] = rag_answer(
            "How does Matt handle delivery?",
            {"q": "How does Matt handle delivery?"},
            [],
        )


@then("no Professional Narrative story appears in sources")
def then_no_pn_in_sources(ctx):
    sources = ctx.get("result", {}).get("sources", [])
    pn_ids = {s["id"] for s in _PN_STORIES}
    pn_found = [s for s in sources if s["id"] in pn_ids]
    assert not pn_found, (
        f"Professional Narrative stories found in sources but should be excluded: "
        f"{[s['title'] for s in pn_found]}"
    )


@then("a Professional Narrative story appears in sources")
def then_pn_in_sources(ctx):
    sources = ctx.get("result", {}).get("sources", [])
    pn_ids = {s["id"] for s in _PN_STORIES}
    pn_found = [s for s in sources if s["id"] in pn_ids]
    assert pn_found, (
        f"Expected a Professional Narrative story in sources but found none. "
        f"Sources: {[s['title'] for s in sources]}"
    )


@then("sources are not empty")
def then_sources_not_empty(ctx):
    sources = ctx.get("result", {}).get("sources", [])
    assert sources, f"Expected non-empty sources but got: {sources!r}"
