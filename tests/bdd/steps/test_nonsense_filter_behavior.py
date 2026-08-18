"""
BDD step definitions for nonsense_filter_behavior.feature (MATTGPT-165 Cycle C).

Verifies is_nonsense returns None on the two target queries that Cycle C's
nonsense_filters.jsonl edits are designed to unblock (credit card portal work,
SWIFT payment rails), and returns the expected blocking category on the two
regression queries the narrower patterns must continue to catch (Taylor Swift
by full name, credit card number as PII).

Each scenario loads the production nonsense_filters.jsonl via _load_nonsense_rules
into the module-level cache, then exercises is_nonsense() directly. No mocking:
the whole point is to assert that the real file's rules do what Cycle C intends.
"""

import sys
from unittest.mock import MagicMock

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

if "streamlit" not in sys.modules:
    _st_mock = MagicMock()
    _st_mock.session_state = {}
    _st_mock.secrets = {}
    sys.modules["streamlit"] = _st_mock
    sys.modules["streamlit.components"] = MagicMock()
    sys.modules["streamlit.components.v1"] = MagicMock()

scenarios("../features/nonsense_filter_behavior.feature")


@pytest.fixture
def ctx():
    return {}


@given("the production nonsense_filters.jsonl is loaded")
def given_production_rules_loaded(ctx):
    """Load real nonsense_filters.jsonl into the module cache.

    Snapshots the current cache and restores it after the test to avoid
    leaking state into other tests in the suite.
    """
    from utils import validation

    ctx["_orig_rules"] = validation._NONSENSE_RULES
    validation._NONSENSE_RULES = validation._load_nonsense_rules()


@when(parsers.parse('is_nonsense is called with "{query}"'))
def when_is_nonsense_called(ctx, query):
    from utils.validation import is_nonsense

    ctx["result"] = is_nonsense(query)


@then("it returns None")
def then_returns_none(ctx):
    _restore_cache(ctx)
    assert ctx["result"] is None, (
        f"Expected is_nonsense to return None (query reaches retrieval),"
        f" got category={ctx['result']!r}. Cycle C intent: this query is"
        f" no longer blocked by the nonsense filter."
    )


@then("it returns the celebrity category")
def then_returns_celebrity(ctx):
    _restore_cache(ctx)
    assert ctx["result"] == "celebrity", (
        f"Expected is_nonsense to return 'celebrity' (query still blocked),"
        f" got {ctx['result']!r}. Regression guard: Cycle C's edit to line 2"
        f" must not unblock full-name celebrity queries -- line 30 (full-names"
        f" celebrity pattern) is the surviving block."
    )


@then("it returns the personal_sensitive category")
def then_returns_personal_sensitive(ctx):
    _restore_cache(ctx)
    assert ctx["result"] == "personal_sensitive", (
        f"Expected is_nonsense to return 'personal_sensitive' (query still"
        f" blocked), got {ctx['result']!r}. Regression guard: Cycle C's deletion"
        f" of line 1 must not unblock credit card number PII queries -- line 6"
        f" (narrower personal_sensitive pattern with 'credit card number') is"
        f" the surviving block."
    )


def _restore_cache(ctx):
    """Restore _NONSENSE_RULES to its pre-test value so state does not leak."""
    from utils import validation

    validation._NONSENSE_RULES = ctx.get("_orig_rules", [])
