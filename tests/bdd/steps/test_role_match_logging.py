"""
Step definitions for tests/bdd/features/role_match_logging.feature

Assessment, UTM and bot scenarios unit-test the logging functions in
services/query_logger.py against a mocked Google Sheet (mock_env).

Chip, action-button and session scenarios (MATTGPT-017) render the Role Match
page in this process with streamlit.testing AppTest (app_env) and click its
hidden buttons by key: no server, no model call, no Sheet write. Rows reach a
mock sheet's append_row through the real _append_row, the same place mock_env
collects them.
"""

import time
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pytest_bdd import given, parsers, scenario, then, when

from utils import corpus_loader

FEATURE = "../features/role_match_logging.feature"
# The app's corpus, at the repo root (utils/ sits directly under it).
CORPUS = str(
    Path(corpus_loader.__file__).resolve().parents[1] / "echo_star_stories_nlp.jsonl"
)

# The AppTest script: renders Role Match, optionally logging the assessment row
# first through the page's own success-path helper.
ROLE_MATCH_SCRIPT = """\
import streamlit as st
from ui.pages.role_match import _log_role_match_success, render_role_match
from utils.corpus_loader import load_stories

if st.session_state.pop("__log_assessment__", False):
    _log_role_match_success(st.session_state["role_match_result"])
render_role_match(load_stories({corpus!r}))
"""

# ── Assessment submission ──────────────────────────────────────────────────


@scenario(
    FEATURE, "Successful assessment logs role_match_assessment with full metadata"
)
def test_successful_assessment_logs():
    pass


@scenario(FEATURE, "Narrative JD logs jd_format as narrative")
def test_narrative_jd_format():
    pass


@scenario(FEATURE, "Bulleted JD logs jd_format as bulleted")
def test_bulleted_jd_format():
    pass


@scenario(FEATURE, "Failed assessment does not log a row")
def test_failed_assessment_no_log():
    pass


# ── Chip interaction (AppTest) ─────────────────────────────────────────────


@scenario(
    FEATURE, "Chip expansion logs role_match_chip_click with story title and client"
)
def test_chip_click_logs():
    pass


@scenario(FEATURE, "Closing a chip does not log an additional row")
def test_chip_close_no_log():
    pass


# ── Action buttons (AppTest) ──────────────────────────────────────────────


@scenario(FEATURE, "Helpful click logs role_match_action with action helpful")
def test_helpful_logs():
    pass


@scenario(
    FEATURE, "Copy Report click does not log a row (known gap, see action_buttons.py)"
)
def test_copy_report_no_log():
    pass


@scenario(FEATURE, "Export click logs role_match_action with action export")
def test_export_logs():
    pass


# ── UTM attribution ───────────────────────────────────────────────────────


@scenario(FEATURE, "UTM parameters present are captured on assessment row")
def test_utm_present():
    pass


@scenario(FEATURE, "UTM parameters missing logs with empty UTM fields")
def test_utm_missing():
    pass


# ── Bot filtering ─────────────────────────────────────────────────────────


@scenario(FEATURE, "Known bot user agent does not produce a logged row")
def test_bot_no_log():
    pass


@scenario(FEATURE, "Real browser user agent produces a logged row")
def test_real_browser_logs():
    pass


# ── Session correlation (AppTest) ─────────────────────────────────────────


@scenario(FEATURE, "All event types from the same session share the same session_id")
def test_session_correlation():
    pass


# ═════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def log_context():
    """Shared mutable dict for passing data between Given/When/Then steps."""
    return {
        "jd_format": "bulleted",
        "session_id": str(uuid.uuid4()),
        "utm": {
            "_utm_source": "",
            "_utm_medium": "",
            "_utm_campaign": "",
            "_utm_content": "",
        },
    }


@pytest.fixture
def mock_env(log_context):
    """Mock Streamlit + Google Sheet for the logging functions."""
    mock_sheet = MagicMock()
    mock_sheet.row_values.return_value = []

    session_state = {
        "_session_id": log_context["session_id"],
        "_browser_screen_size": "1710",
        "_browser_referrer": "",
        **log_context["utm"],
    }

    with (
        patch("services.query_logger.get_sheet", return_value=mock_sheet),
        patch("services.query_logger.st") as mock_st,
        patch("services.query_logger._headers_checked", False),
    ):
        mock_st.session_state = MagicMock()
        mock_st.session_state.get = lambda k, d="": session_state.get(k, d)
        mock_st.context = MagicMock()
        mock_st.context.headers = {"User-Agent": "Mozilla/5.0 Chrome/146.0.0.0"}
        mock_st.context.timezone = "America/New_York"
        yield mock_sheet


@pytest.fixture
def app_env(log_context):
    """Role Match under streamlit.testing AppTest, in this process.

    role_match_result is preset, so no assessment (and no model call) runs. The
    desktop-only gate gets a width (AppTest has no browser). is_bot is False in
    both modules that check it (AppTest sends no User-Agent). get_sheet returns
    a mock sheet, so the real _append_row writes rows to mock_sheet.append_row
    and never reaches Google. The evidence chip's story is the corpus's first
    story, picked by index rather than by title.
    """
    from streamlit.testing.v1 import AppTest

    story = corpus_loader.load_stories(CORPUS)[0]
    payload = {
        "extraction": {"role_title": "Director of Engineering", "company": "Acme"},
        "results": [
            {
                "category": "required",
                "requirement": "Lead engineering teams",
                "match_status": "strong",
                "evidence": [
                    {
                        "evidence_type": "story",
                        "story_title": story["Title"],
                        "client": story["Client"],
                    }
                ],
                "gap_explanation": "",
                "confidence": "high",
            }
        ],
    }
    mock_sheet = MagicMock()
    mock_sheet.row_values.return_value = []
    with (
        patch("services.query_logger.get_sheet", return_value=mock_sheet),
        patch("services.query_logger._headers_checked", False),
        patch("services.query_logger.is_bot", return_value=False),
        patch("ui.pages.role_match.is_bot", return_value=False),
    ):
        at = AppTest.from_string(
            ROLE_MATCH_SCRIPT.format(corpus=CORPUS), default_timeout=60
        )
        at.session_state["role_match_result"] = payload
        at.session_state["_session_id"] = log_context["session_id"]
        at.session_state["_browser_screen_size"] = "1280"
        yield {"at": at, "sheet": mock_sheet, "story": story}


def _run(app_env):
    """Run the page once more and let the logging daemon threads finish."""
    at = app_env["at"]
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    time.sleep(0.3)


def _click(app_env, key_prefix):
    """Click the hidden button whose key starts with key_prefix. Action-button
    keys end in id(result_payload), so they are matched by prefix."""
    at = app_env["at"]
    keys = [b.key for b in at.button if b.key and b.key.startswith(key_prefix)]
    assert (
        keys
    ), f"No button with key prefix {key_prefix!r}: {[b.key for b in at.button]}"
    at.button(key=keys[0]).click()
    _run(app_env)


def _rows(sheet, event_type):
    from services.query_logger import HEADERS

    return [
        dict(zip(HEADERS, call.args[0], strict=False))
        for call in sheet.append_row.call_args_list
        if call.args[0][0] == event_type
    ]


# ═════════════════════════════════════════════════════════════════════════════
# GIVEN STEPS
# ═════════════════════════════════════════════════════════════════════════════


@given("the user has submitted a job description")
def given_jd_submitted():
    pass


@given("the assessment completes successfully", target_fixture="assessment_logged")
def given_assessment_success(mock_env, log_context):
    from services.query_logger import log_role_match_assessment

    log_role_match_assessment(
        role_title="Director of Engineering",
        company="RiskTech Solutions",
        jd_format=log_context["jd_format"],
        required_count=11,
        preferred_count=4,
        strong_count=8,
        partial_count=2,
        gap_count=1,
        unassessed_count=4,
        failure_type="ok",
        required_strong_count=6,
        required_partial_count=2,
        required_gap_count=1,
        required_unassessed_count=2,
        preferred_strong_count=2,
        preferred_partial_count=0,
        preferred_gap_count=0,
        preferred_unassessed_count=2,
    )
    time.sleep(0.3)  # Wait for daemon thread
    return mock_env


@given(
    "the user has submitted a narrative-style job description"
    " with no Required/Preferred sections"
)
def given_narrative_jd(log_context):
    log_context["jd_format"] = "narrative"


@given(
    "the user has submitted a job description"
    " with explicit Required and Preferred sections"
)
def given_bulleted_jd(log_context):
    log_context["jd_format"] = "bulleted"


@given("the assessment fails with an error", target_fixture="assessment_logged")
def given_assessment_fails(mock_env):
    # Deliberately do NOT call log_role_match_assessment
    return mock_env


@given("the user arrived via a UTM-tagged URL")
def given_utm_present(log_context):
    log_context["utm"] = {
        "_utm_source": "role_match",
        "_utm_medium": "clipboard",
        "_utm_campaign": "fit_assessment",
        "_utm_content": "director-of-engineering-risktech",
    }


@given("the user submits a job description")
def given_submits_jd():
    pass


@given("the user arrived via a direct URL with no UTM parameters")
def given_no_utm(log_context):
    log_context["utm"] = {
        "_utm_source": "",
        "_utm_medium": "",
        "_utm_campaign": "",
        "_utm_content": "",
    }


@given("the request has a user agent matching a MONITORING_BOT_SIGNATURES entry")
def given_bot_ua():
    pass


@given("the request has a standard browser user agent")
def given_real_browser():
    pass


# AppTest steps (MATTGPT-017). Each Given that renders the page returns the mock
# sheet as assessment_logged, so the shared Then steps read the same rows.
@given(
    "the user has submitted a job description and results are displayed",
    target_fixture="assessment_logged",
)
def given_results_displayed(app_env):
    _run(app_env)
    return app_env["sheet"]


@given(
    "the user has expanded a story evidence chip", target_fixture="assessment_logged"
)
def given_chip_expanded(app_env):
    _run(app_env)
    _click(app_env, "evidence_btn_0_0")
    return app_env["sheet"]


@given("results are displayed", target_fixture="assessment_logged")
def given_results(app_env):
    _run(app_env)
    return app_env["sheet"]


@given(
    "the user submits a job description and the assessment completes",
    target_fixture="assessment_logged",
)
def given_full_assessment(app_env):
    """The assessment row comes from calling _log_role_match_success() directly
    inside the AppTest session (the page's success-path helper, with the preset
    role_match_result), not from a real assessment run, so no model call is made.
    It reads the same _session_id the chip and Helpful clicks log."""
    app_env["at"].session_state["__log_assessment__"] = True
    _run(app_env)
    return app_env["sheet"]


@given("the user clicks a story evidence chip")
def given_chip_click(app_env):
    _click(app_env, "evidence_btn_0_0")


@given("the user clicks Helpful")
def given_helpful_click(app_env):
    _click(app_env, "helpful_role_match_")


# ═════════════════════════════════════════════════════════════════════════════
# WHEN STEPS
# ═════════════════════════════════════════════════════════════════════════════


@when("the assessment completes successfully", target_fixture="assessment_logged")
def when_assessment_completes(mock_env, log_context):
    from services.query_logger import log_role_match_assessment

    log_role_match_assessment(
        role_title="Director of Engineering",
        company="RiskTech Solutions",
        jd_format=log_context["jd_format"],
        required_count=11,
        preferred_count=4,
        strong_count=8,
        partial_count=2,
        gap_count=1,
        unassessed_count=4,
        failure_type="ok",
        required_strong_count=6,
        required_partial_count=2,
        required_gap_count=1,
        required_unassessed_count=2,
        preferred_strong_count=2,
        preferred_partial_count=0,
        preferred_gap_count=0,
        preferred_unassessed_count=2,
    )
    time.sleep(0.3)
    return mock_env


@when("an assessment completes")
def when_assessment_completes_bot():
    pass


@when("the user clicks a story evidence chip")
def when_chip_clicked(app_env):
    _click(app_env, "evidence_btn_0_0")


@when("the user clicks the same chip again to close it")
def when_chip_closed(app_env):
    _click(app_env, "evidence_btn_0_0")


@when("the user clicks Helpful")
def when_helpful(app_env):
    _click(app_env, "helpful_role_match_")


@when("the user clicks Report")
def when_report(app_env):
    """Report copies in the browser with no Streamlit rerun, so the page has no
    server-side button to click. Assert that is still so (the known gap): the
    action buttons the page exposes are Helpful and Export only."""
    keys = [b.key or "" for b in app_env["at"].button]
    # Action-button keys are "<action>_role_match_<id(result_payload)>".
    actions = sorted(
        k.split("_role_match_")[0]
        for k in keys
        if "_role_match_" in k and k.split("_role_match_")[1].isdigit()
    )
    assert actions == ["export", "helpful"], keys


@when("the user clicks Export")
def when_export(app_env):
    _click(app_env, "export_role_match_")


# ═════════════════════════════════════════════════════════════════════════════
# THEN STEPS
# ═════════════════════════════════════════════════════════════════════════════


@then(parsers.parse('a row with event type "{event_type}" is logged'))
def then_row_logged(assessment_logged, log_context, event_type):
    sheet = assessment_logged
    rows = sheet.append_row.call_args_list
    assert any(
        call.args[0][0] == event_type for call in rows
    ), f"No row with event type '{event_type}' was logged. Rows: {[c.args[0][0] for c in rows]}"
    log_context["event_type"] = event_type  # "the row" in the steps that follow


@then(parsers.parse('no "{event_type}" row is logged'))
def then_no_row_logged(assessment_logged, event_type):
    rows = assessment_logged.append_row.call_args_list
    assert not any(
        call.args[0][0] == event_type for call in rows
    ), f"Unexpected row with event type '{event_type}'"


def _last_row(sheet):
    from services.query_logger import HEADERS

    row = sheet.append_row.call_args_list[-1].args[0]
    return dict(zip(HEADERS, row, strict=False))


@then("the row contains the extracted role title")
def then_has_role_title(assessment_logged):
    assert _last_row(assessment_logged)["Role Title"] == "Director of Engineering"


@then("the row contains the extracted company")
def then_has_company(assessment_logged):
    assert _last_row(assessment_logged)["Company"] == "RiskTech Solutions"


@then("the row contains the required qualification count")
def then_has_required(assessment_logged):
    assert _last_row(assessment_logged)["Required Count"] == "11"


@then("the row contains the preferred qualification count")
def then_has_preferred(assessment_logged):
    assert _last_row(assessment_logged)["Preferred Count"] == "4"


@then("the row contains the strong match count")
def then_has_strong(assessment_logged):
    assert _last_row(assessment_logged)["Strong Count"] == "8"


@then("the row contains the partial match count")
def then_has_partial(assessment_logged):
    assert _last_row(assessment_logged)["Partial Count"] == "2"


@then("the row contains the gap count")
def then_has_gap(assessment_logged):
    assert _last_row(assessment_logged)["Gap Count"] == "1"


@then("the row contains a session ID")
def then_has_session_id(assessment_logged):
    sid = _last_row(assessment_logged)["Session ID"]
    assert sid, "Session ID is empty"
    uuid.UUID(sid)  # Validates UUID format


@then(parsers.parse('the logged row contains jd_format "{jd_format}"'))
def then_has_jd_format(assessment_logged, jd_format):
    assert _last_row(assessment_logged)["JD Format"] == jd_format


@then(
    "the logged row contains the utm_source, utm_medium,"
    " utm_campaign, and utm_content values from the URL"
)
def then_has_utm(assessment_logged):
    row = _last_row(assessment_logged)
    assert row["UTM Source"] == "role_match"
    assert row["UTM Medium"] == "clipboard"
    assert row["UTM Campaign"] == "fit_assessment"
    assert row["UTM Content"] == "director-of-engineering-risktech"


@then("the logged row has empty UTM fields")
def then_empty_utm(assessment_logged):
    row = _last_row(assessment_logged)
    assert row["UTM Source"] == ""
    assert row["UTM Medium"] == ""
    assert row["UTM Campaign"] == ""
    assert row["UTM Content"] == ""


@then("no error occurs")
def then_no_error():
    pass


@then("no row is logged")
def then_bot_no_row():
    from services.query_logger import is_bot

    with patch("services.query_logger.st") as mock_st:
        mock_st.context = MagicMock()
        mock_st.context.headers = {
            "User-Agent": "Mozilla/5.0 Chrome/103.0.0.0 Safari/537.36"
        }
        assert is_bot(), "Expected is_bot() to return True for Chrome/103 UA"


@then(parsers.parse('a "{event_type}" row is logged'))
def then_real_browser_logs(event_type):
    from services.query_logger import is_bot

    with patch("services.query_logger.st") as mock_st:
        mock_st.context = MagicMock()
        mock_st.context.headers = {
            "User-Agent": "Mozilla/5.0 Chrome/146.0.0.0 Safari/537.36"
        }
        assert not is_bot(), "Expected is_bot() to return False for real browser"


# AppTest Then steps (MATTGPT-017)
@then("the row contains the story title")
def then_has_story_title(assessment_logged, app_env):
    [row] = _rows(assessment_logged, "role_match_chip_click")
    assert row["Story Title"] == app_env["story"]["Title"][:200]


@then("the row contains the client name")
def then_has_client(assessment_logged, app_env):
    [row] = _rows(assessment_logged, "role_match_chip_click")
    assert row["Client"] == app_env["story"]["Client"]


@then("the row contains the same session ID as the assessment row")
def then_same_session(assessment_logged, log_context):
    """The page's _session_id, which the assessment row is written with."""
    rows = _rows(assessment_logged, log_context["event_type"])
    assert rows and all(r["Session ID"] == log_context["session_id"] for r in rows)


@then(parsers.parse('no additional "{event_type}" row is logged'))
def then_no_additional(assessment_logged, event_type):
    rows = _rows(assessment_logged, event_type)
    assert len(rows) == 1, f"Expected only the opening row, got {len(rows)}"


@then(parsers.parse('the row contains action "{action}"'))
def then_has_action(assessment_logged, action):
    rows = _rows(assessment_logged, "role_match_action")
    assert [r["Rating"] for r in rows] == [action]


@then(parsers.parse('a "{event_type}" row with rating "{rating}" is also logged'))
def then_also_logged_with_rating(assessment_logged, event_type, rating):
    rows = _rows(assessment_logged, event_type)
    assert [r["Rating"] for r in rows] == [rating]


@then(
    "the role_match_assessment row, the role_match_chip_click row,"
    " and the role_match_action row all contain the same session_id value"
)
def then_all_same_session(assessment_logged, log_context):
    ids = {
        event_type: [r["Session ID"] for r in _rows(assessment_logged, event_type)]
        for event_type in (
            "role_match_assessment",
            "role_match_chip_click",
            "role_match_action",
        )
    }
    assert all(len(v) == 1 for v in ids.values()), ids
    assert len({v[0] for v in ids.values()}) == 1, ids
    log_context["shared_session_id"] = ids["role_match_action"][0]


@then("the session_id is a valid UUID")
def then_valid_uuid(log_context):
    uuid.UUID(log_context["shared_session_id"])
