"""
Step definitions for tests/bdd/features/page_load_tracking.feature (MATTGPT-345).

Each scenario runs app.py's first mount under streamlit.testing AppTest, in
this process: no server, no browser. The request's headers come from a patched
streamlit.runtime.context._get_request, which st.context.headers reads, and
the UTM params go in as URL query params. get_sheet returns a mock sheet, so
the real log_page_load and _append_row write rows to mock_sheet.append_row and
never reach Google (the test_role_match_logging.py pattern).
"""

import json
import time
from contextlib import ExitStack
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


# ── page_context: what the browser reports (MATTGPT-347) ───────────────────
#
# streamlit_js_eval never runs under AppTest (no browser), so these steps
# patch it to return what the browser would: a JSON object with the viewport
# width and window.top.document.referrer. That object is the contract the
# screen-size capture in app.py reads. None stands for a browser that has not
# answered yet.


def _browser_report(width, referrer):
    return json.dumps({"innerWidth": width, "referrer": referrer})


@pytest.fixture
def browser():
    """The browser's report for the next load, and the patches that stay
    active until the scenario ends (the visitor may keep using the app)."""
    with ExitStack() as stack:
        yield {"report": _browser_report(1440, ""), "stack": stack, "loads": []}


def _rows_of(sheet, event_type):
    return [
        dict(zip(query_logger.HEADERS, call.args[0], strict=False))
        for call in sheet.append_row.call_args_list
        if call.args[0][0] == event_type
    ]


def _load(browser, headers, params):
    """Run app.py for one request with the browser's report patched in. The
    patches stay active so a later step can rerun the same session."""
    from streamlit.testing.v1 import AppTest

    stack = browser["stack"]
    sheet = MagicMock()
    sheet.row_values.return_value = []
    request = SimpleNamespace(headers=HTTPHeaders(headers))
    stack.enter_context(
        patch("streamlit.runtime.context._get_request", return_value=request)
    )
    stack.enter_context(patch("services.query_logger.get_sheet", return_value=sheet))
    stack.enter_context(patch("services.query_logger._headers_checked", False))
    stack.enter_context(
        patch("streamlit_js_eval.streamlit_js_eval", return_value=browser["report"])
    )
    at = AppTest.from_file(APP, default_timeout=60)
    for key, value in params.items():
        at.query_params[key] = value
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    time.sleep(0.3)  # let the logging daemon threads finish
    browser["loads"].append({"at": at, "sheet": sheet})


def _context_rows(browser):
    return [
        r for load in browser["loads"] for r in _rows_of(load["sheet"], "page_context")
    ]


def _only_load(browser):
    assert len(browser["loads"]) == 1, browser["loads"]
    return browser["loads"][0]


@given(
    parsers.parse(
        "the browser reports referrer {referrer} and viewport width {width:d}"
    )
)
def browser_reports(browser, referrer, width):
    browser["report"] = _browser_report(width, referrer)


@given("the browser has not reported its context yet")
def browser_silent(browser):
    browser["report"] = None


@given("a request arrives with a User-Agent matching each entry")
def signature_visits(visit):
    for signature in MONITORING_BOT_SIGNATURES:
        visit["requests"].append(({"User-Agent": f"Mozilla/5.0 {signature}"}, {}))


@when("the page loads and the browser reports its context")
def page_loads(visit, browser):
    for headers, params in visit["requests"]:
        _load(browser, headers, params)
    visit["rows"] += [
        r for load in browser["loads"] for r in _rows_of(load["sheet"], "page_load")
    ]


@when("the visitor keeps using the app")
def keeps_using(browser):
    load = _only_load(browser)
    for _ in range(2):
        load["at"].run()
        assert not load["at"].exception, [e.value for e in load["at"].exception]
    time.sleep(0.3)


@then(parsers.parse("the page_context row contains {pairs}"))
def context_row_contains(browser, pairs):
    rows = _context_rows(browser)
    assert len(rows) == 1, rows
    expected = dict(pair.split("=", 1) for pair in pairs.split(", "))
    assert {k: rows[0][k] for k in expected} == expected


@then("the page_context row has the page_load row's Session ID")
def same_session(visit, browser):
    rows = _context_rows(browser)
    assert len(rows) == 1, rows
    page_load = _one_row(visit)
    assert page_load["Session ID"], page_load
    assert rows[0]["Session ID"] == page_load["Session ID"]


@then(parsers.parse("the mobile gate reads a screen width of {width}"))
def mobile_gate_width(browser, width):
    # role_match.py and landing_view.py read this key with int(); its value
    # stays the bare width string it was before page_context.
    at = _only_load(browser)["at"]
    assert at.session_state["_browser_screen_size"] == width


@then(parsers.parse("later rows in the session carry Referrer {referrer}"))
def later_rows_referrer(browser, referrer):
    # _capture_context() reads this key into query and Role Match rows.
    at = _only_load(browser)["at"]
    assert at.session_state["_browser_referrer"] == referrer


@then("exactly one page_context row is written")
def one_context_row(browser):
    rows = _context_rows(browser)
    assert len(rows) == 1, rows


@then("no page_context row is written")
def no_context_row(browser):
    assert _context_rows(browser) == []
