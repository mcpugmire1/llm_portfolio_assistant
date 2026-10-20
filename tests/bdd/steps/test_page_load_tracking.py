"""
Step definitions for tests/bdd/features/page_load_tracking.feature (MATTGPT-345).

Each scenario runs app.py's first mount under streamlit.testing AppTest, in
this process: no server, no browser. The request's headers come from a patched
streamlit.runtime.context._get_request, which st.context.headers reads, and
the UTM params go in as URL query params. get_sheet returns a mock sheet, so
the real log_page_load and _append_row write rows to mock_sheet.append_row and
never reach Google (the test_role_match_logging.py pattern).
"""

import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qsl

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from tornado.httputil import HTTPHeaders

from config.constants import MONITORING_BOT_SIGNATURES
from services import query_logger

scenarios("../features/page_load_tracking.feature")

# app.py, at the repo root (services/ sits directly under it).
APP = str(Path(query_logger.__file__).resolve().parents[1] / "app.py")
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
UTM_COLUMNS = ["UTM Source", "UTM Medium", "UTM Campaign", "UTM Content", "UTM Term"]


@pytest.fixture
def visit():
    """One or more requests: each is (headers dict, query params dict)."""
    return {"requests": [], "rows": []}


def _first_mount(headers, params):
    """Run app.py's first mount for one request; return its page_load rows."""
    from streamlit.testing.v1 import AppTest

    sheet = MagicMock()
    sheet.row_values.return_value = []
    request = SimpleNamespace(headers=HTTPHeaders(headers))
    with (
        patch("streamlit.runtime.context._get_request", return_value=request),
        patch("services.query_logger.get_sheet", return_value=sheet),
        patch("services.query_logger._headers_checked", False),
    ):
        at = AppTest.from_file(APP, default_timeout=60)
        for key, value in params.items():
            at.query_params[key] = value
        at.run()
        assert not at.exception, [e.value for e in at.exception]
        time.sleep(0.3)  # let the logging daemon thread finish
    return [
        dict(zip(query_logger.HEADERS, call.args[0], strict=False))
        for call in sheet.append_row.call_args_list
        if call.args[0][0] == "page_load"
    ]


# ── Given ──────────────────────────────────────────────────────────────────


@given(parsers.parse("a visitor arrives via URL with {query}"))
def utm_url(visit, query):
    visit["requests"].append(({"User-Agent": BROWSER_UA}, dict(parse_qsl(query))))


@given("a visitor arrives via direct URL with no UTM params")
def direct_url(visit):
    visit["requests"].append(({"User-Agent": BROWSER_UA}, {}))


@given("a request arrives from UptimeRobot with an empty User-Agent")
def empty_user_agent(visit):
    visit["requests"].append(({"User-Agent": ""}, {}))


@given("a request arrives with a standard browser User-Agent")
def browser_user_agent(visit):
    visit["requests"].append(({"User-Agent": BROWSER_UA}, {}))


@given("MONITORING_BOT_SIGNATURES contains multiple entries")
def several_signatures():
    assert len(MONITORING_BOT_SIGNATURES) > 1, MONITORING_BOT_SIGNATURES


@given("a request arrives with no User-Agent header")
def no_user_agent(visit):
    visit["requests"].append(({}, {}))


# ── When ───────────────────────────────────────────────────────────────────


@when("the first-mount guard fires")
def guard_fires(visit):
    for headers, params in visit["requests"]:
        visit["rows"] += _first_mount(headers, params)


@when("a request arrives with a User-Agent matching any entry")
def signature_requests(visit):
    for signature in MONITORING_BOT_SIGNATURES:
        visit["rows"] += _first_mount({"User-Agent": f"Mozilla/5.0 {signature}"}, {})


# ── Then ───────────────────────────────────────────────────────────────────


def _one_row(visit):
    assert len(visit["rows"]) == 1, visit["rows"]
    return visit["rows"][0]


@then(parsers.parse("the page_load row contains {pairs}"))
def row_contains(visit, pairs):
    row = _one_row(visit)
    expected = dict(pair.split("=") for pair in pairs.split(", "))
    assert {k: row[k] for k in expected} == expected


@then(
    "UTM Source, UTM Medium, UTM Campaign, UTM Content, UTM Term are all empty strings"
)
def utm_empty(visit):
    row = _one_row(visit)
    assert {k: row[k] for k in UTM_COLUMNS} == dict.fromkeys(UTM_COLUMNS, "")


@then("log_page_load is called")
def logged(visit):
    _one_row(visit)


@then("log_page_load is not called")
def not_logged(visit):
    assert visit["rows"] == []
