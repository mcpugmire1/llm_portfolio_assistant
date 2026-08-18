"""
BDD step definitions for matt_dna_career_span.feature (MATTGPT-161).

Verifies career-span derivation from corpus dates and enforces that the
resulting values are NOT rendered into MATT_DNA prose. The derived constants
remain available for consumers that need the math (Role Match assessor
reasoning about JD tenure requirements).

Step defs use `getattr(backend_service, "_CAREER_START_YEAR", None)` rather
than a direct import so a Red-state run (constant not yet defined) fails on
the assertion, not on ImportError.
"""

import sys
from unittest.mock import MagicMock

if "streamlit" not in sys.modules:
    _st_mock = MagicMock()
    _st_mock.session_state = {}
    _st_mock.secrets = {}
    sys.modules["streamlit"] = _st_mock
    sys.modules["streamlit.components"] = MagicMock()
    sys.modules["streamlit.components.v1"] = MagicMock()

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/matt_dna_career_span.feature")


def _make_story(**overrides):
    """Minimal story dict with reasonable defaults; override any field."""
    base = {
        "id": "test-story-1",
        "Title": "Test Story",
        "Client": "TestClient",
        "Employer": "Accenture",
        "Division": "Technology",
        "Role": "Test Role",
        "Sub-category": "Test",
        "Theme": "Execution & Delivery",
        "Category": "Execution & Delivery",
        "Industry": "Technology",
        "Start_Date": "2010-01",
        "End_Date": "2010-12",
        "Situation": "s",
        "Task": "t",
        "Action": ["a"],
        "Result": ["r"],
        "Process": [],
        "Performance": [],
        "Competencies": [],
        "public_tags": [],
    }
    base.update(overrides)
    return base


@pytest.fixture
def ctx():
    return {}


@pytest.fixture(autouse=True)
def restore_backend_service_globals():
    """Snapshot and restore backend_service module-level globals that
    sync_portfolio_metadata mutates. Scenario 1 passes a one-story list which
    would leave MATT_DNA, SYNTHESIS_THEMES, and _KNOWN_CLIENTS in a truncated
    state; without this fixture, later tests in the suite that import
    backend_service inherit the pollution.

    Same shape as tests/unit/test_validation.py::TestIsNonsense.restore_nonsense_rules.

    Post-Green: extend to include _CAREER_START_YEAR, _CAREER_END_YEAR,
    _CAREER_SPAN_YEARS once sync_portfolio_metadata sets them. Getattr with
    a sentinel handles the Red-state case where those attributes do not
    exist yet -- restoring None on Red is a no-op relative to their absence.
    """
    from ui.pages.ask_mattgpt import backend_service

    _MISSING = object()
    tracked = (
        "MATT_DNA",
        "SYNTHESIS_THEMES",
        "_KNOWN_CLIENTS",
        "_CAREER_START_YEAR",
        "_CAREER_END_YEAR",
        "_CAREER_SPAN_YEARS",
    )
    snapshot = {name: getattr(backend_service, name, _MISSING) for name in tracked}
    yield
    for name, value in snapshot.items():
        if value is _MISSING:
            # Attribute did not exist at snapshot time; delete if the test
            # created it, so post-test state matches pre-test state exactly.
            if hasattr(backend_service, name):
                delattr(backend_service, name)
        else:
            setattr(backend_service, name, value)


# =============================================================================
# Given
# =============================================================================


@given(
    parsers.parse(
        'a story list containing a synthetic pre-2005 story with Start_Date "{date}"'
    )
)
def given_synthetic_pre_2005(ctx, date):
    """Build an in-memory story list with one pre-2005 record so the derivation
    is verified against the condition it exists to handle -- pre-2005 corpus
    content that MATTGPT-181 will bring. No fixture file needed."""
    ctx["stories"] = [
        _make_story(
            id="synthetic-pre-2005",
            Title="Synthetic Pre-2005 Story",
            Client="Wellfound Technology",
            Employer="Wellfound Technology",
            Start_Date=date,
            End_Date="2001-08",
        )
    ]


@given("the current production story corpus is loaded")
def given_production_corpus(ctx):
    from utils.corpus_loader import load_stories

    ctx["stories"] = load_stories("echo_star_stories_nlp.jsonl")


# =============================================================================
# When
# =============================================================================


@when("sync_portfolio_metadata is called with that story list")
def when_sync_with_synthetic(ctx):
    _run_sync(ctx)


@when("sync_portfolio_metadata is called with the production stories")
def when_sync_with_production(ctx):
    _run_sync(ctx)


def _run_sync(ctx):
    from ui.pages.ask_mattgpt import backend_service

    backend_service.sync_portfolio_metadata(ctx["stories"])
    ctx["backend_service"] = backend_service


# =============================================================================
# Then
# =============================================================================


@then(parsers.parse("_CAREER_START_YEAR is {year:d}"))
def then_career_start_year(ctx, year):
    bs = ctx["backend_service"]
    actual = getattr(bs, "_CAREER_START_YEAR", None)
    assert actual == year, (
        f"Expected _CAREER_START_YEAR == {year}, got {actual!r}."
        " If None, the constant is not yet defined in backend_service --"
        " expected before Green ships the derivation."
    )


@then(parsers.parse('MATT_DNA contains no "{substring}" substring'))
def then_matt_dna_no_substring(ctx, substring):
    bs = ctx["backend_service"]
    assert substring not in bs.MATT_DNA, (
        f"Expected MATT_DNA to NOT contain {substring!r} substring,"
        " but it does. MATT_DNA excerpt (first 400 chars):"
        f" {bs.MATT_DNA[:400]!r}"
    )


@then(parsers.parse('MATT_DNA contains "{substring}"'))
def then_matt_dna_contains(ctx, substring):
    bs = ctx["backend_service"]
    assert substring in bs.MATT_DNA, (
        f"Expected MATT_DNA to contain {substring!r}, but it does not."
        f" MATT_DNA excerpt (first 400 chars): {bs.MATT_DNA[:400]!r}"
    )
