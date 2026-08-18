"""
BDD step definitions for query_logger_top_score.feature.

Post-hoc regression guard for behavior shipped at bc72fba ("Add top_score to
query logger -- HEADERS, log_query param, three call sites"). Not a Red-Green
cycle: the implementation predates these scenarios. Written to pin the
HEADERS ordering and the log_query row-assembly so a future refactor cannot
silently drop the Top Score column or reorder it.
"""

import sys
from unittest.mock import MagicMock, patch

if "streamlit" not in sys.modules:
    _st_mock = MagicMock()
    _st_mock.session_state = {}
    _st_mock.secrets = {}
    sys.modules["streamlit"] = _st_mock
    sys.modules["streamlit.components"] = MagicMock()
    sys.modules["streamlit.components.v1"] = MagicMock()

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/query_logger_top_score.feature")


class _SyncThread:
    """Thread stand-in that runs target synchronously in the calling thread.

    log_query spawns a daemon thread to call _append_row; we can't inspect
    the row until that thread runs. Patching services.query_logger.Thread
    with this class makes start() call target immediately so assertions can
    read the resulting call args without a join or sleep.
    """

    def __init__(self, target=None, args=(), daemon=False, **kwargs):
        self._target = target
        self._args = args

    def start(self):
        self._target(*self._args)


@pytest.fixture
def ctx():
    return {}


# =============================================================================
# Scenario 1: HEADERS ordering
# =============================================================================


@given("the query_logger module is imported")
def given_module_imported(ctx):
    import services.query_logger as ql

    ctx["ql"] = ql


@then(parsers.parse('"{header}" is the last entry in HEADERS'))
def then_last_header(ctx, header):
    from services.query_logger import HEADERS

    assert HEADERS[-1] == header, (
        f"Expected {header!r} to be the last HEADERS entry; got {HEADERS[-1]!r}."
        f" Full HEADERS length={len(HEADERS)}: {HEADERS}"
    )


# =============================================================================
# Scenarios 2 & 3: log_query row-assembly
# =============================================================================


@given("a non-bot user agent is active")
def given_non_bot_ua(ctx):
    """Set up patches so log_query proceeds past the bot filter and its
    daemon thread runs synchronously against a captured _append_row mock.
    Patches are stopped by _teardown() in the Then step so state does not
    leak into other scenarios.
    """
    ctx["_patches"] = [
        patch("services.query_logger.is_bot", return_value=False),
        patch("services.query_logger._append_row"),
        patch("services.query_logger.Thread", _SyncThread),
        patch(
            "services.query_logger._capture_context",
            return_value=("test-agent", "", "", ""),
        ),
    ]
    started = [p.start() for p in ctx["_patches"]]
    # _append_row mock is the second patch; capture its handle for assertions.
    ctx["_append_row_mock"] = started[1]


@when(parsers.parse("log_query is called with top_score {score:g}"))
def when_log_query_with_score(ctx, score):
    from services.query_logger import log_query

    log_query("test query", top_score=score)


@when("log_query is called without top_score")
def when_log_query_without_score(ctx):
    from services.query_logger import log_query

    log_query("test query")


def _teardown(ctx):
    for p in ctx.get("_patches", []):
        try:
            p.stop()
        except RuntimeError:
            pass  # Already stopped


def _get_row(ctx):
    call_args = ctx["_append_row_mock"].call_args
    assert call_args is not None, "_append_row was not called by log_query"
    return call_args.args[0]


@then(parsers.parse('the logged row contains {value:g} at the "{column}" column'))
def then_row_contains_number(ctx, value, column):
    try:
        from services.query_logger import HEADERS

        row = _get_row(ctx)
        idx = HEADERS.index(column)
        assert row[idx] == value, (
            f"Expected {value!r} at HEADERS[{idx}] ({column!r}), got {row[idx]!r}."
            f" Full row: {row}"
        )
    finally:
        _teardown(ctx)


@then(parsers.parse('the logged row contains "" at the "{column}" column'))
def then_row_contains_empty_string(ctx, column):
    try:
        from services.query_logger import HEADERS

        row = _get_row(ctx)
        idx = HEADERS.index(column)
        assert row[idx] == "", (
            f"Expected empty string at HEADERS[{idx}] ({column!r}), got {row[idx]!r}."
            f" Full row: {row}"
        )
    finally:
        _teardown(ctx)
