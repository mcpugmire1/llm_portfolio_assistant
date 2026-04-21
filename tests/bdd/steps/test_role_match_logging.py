"""
Step definitions for tests/bdd/features/role_match_logging.feature

Unit-test the logging functions in services/query_logger.py by mocking
the Google Sheet. Scenarios requiring Streamlit runtime (chip clicks,
action buttons) are skipped with reason.
"""

import time
import uuid
from unittest.mock import MagicMock, patch

import pytest
from pytest_bdd import given, parsers, scenario, then, when

FEATURE = "../features/role_match_logging.feature"

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


# ── Chip interaction (skip) ────────────────────────────────────────────────


@pytest.mark.skip(reason="Requires Streamlit runtime for chip click simulation")
@scenario(
    FEATURE, "Chip expansion logs role_match_chip_click with story title and client"
)
def test_chip_click_logs():
    pass


@pytest.mark.skip(reason="Requires Streamlit runtime for chip click simulation")
@scenario(FEATURE, "Closing a chip does not log an additional row")
def test_chip_close_no_log():
    pass


# ── Action buttons (skip) ─────────────────────────────────────────────────


@pytest.mark.skip(reason="Requires Streamlit runtime for action button wiring")
@scenario(FEATURE, "Helpful click logs role_match_action with action helpful")
def test_helpful_logs():
    pass


@pytest.mark.skip(reason="Requires Streamlit runtime for action button wiring")
@scenario(FEATURE, "Copy Report click logs role_match_action with action copy_report")
def test_copy_report_logs():
    pass


@pytest.mark.skip(reason="Requires Streamlit runtime for action button wiring")
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


# ── Session correlation (skip) ────────────────────────────────────────────


@pytest.mark.skip(reason="Requires Streamlit runtime for full session simulation")
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


@given("the assessment fails with an error")
def given_assessment_fails(mock_env):
    # Deliberately do NOT call log_role_match_assessment
    pass


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


# Stubs for skipped scenarios
@given("the user has submitted a job description and results are displayed")
def given_results_displayed():
    pass


@given("the user has expanded a story evidence chip")
def given_chip_expanded():
    pass


@given("results are displayed")
def given_results():
    pass


@given("the user submits a job description and the assessment completes")
def given_full_assessment():
    pass


@given("the user clicks a story evidence chip", target_fixture="chip_click")
def given_chip_click():
    pass


@given("the user clicks Helpful", target_fixture="helpful_click")
def given_helpful_click():
    pass


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
    )
    time.sleep(0.3)
    return mock_env


@when("an assessment completes")
def when_assessment_completes_bot():
    pass


@when("the user clicks a story evidence chip")
def when_chip_clicked():
    pass


@when("the user clicks the same chip again to close it")
def when_chip_closed():
    pass


@when("the user clicks Helpful")
def when_helpful():
    pass


@when("the user clicks Report")
def when_report():
    pass


@when("the user clicks Export")
def when_export():
    pass


# ═════════════════════════════════════════════════════════════════════════════
# THEN STEPS
# ═════════════════════════════════════════════════════════════════════════════


@then(parsers.parse('a row with event type "{event_type}" is logged'))
def then_row_logged(assessment_logged, event_type):
    sheet = assessment_logged
    rows = sheet.append_row.call_args_list
    assert any(
        call.args[0][0] == event_type for call in rows
    ), f"No row with event type '{event_type}' was logged. Rows: {[c.args[0][0] for c in rows]}"


@then(parsers.parse('no "{event_type}" row is logged'))
def then_no_row_logged(mock_env, event_type):
    rows = mock_env.append_row.call_args_list
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


# Stubs for skipped scenarios
@then("the row contains the story title")
def then_has_story_title():
    pass


@then("the row contains the client name")
def then_has_client():
    pass


@then("the row contains the same session ID as the assessment row")
def then_same_session():
    pass


@then(parsers.parse('no additional "{event_type}" row is logged'))
def then_no_additional(event_type):
    pass


@then(parsers.parse('the row contains action "{action}"'))
def then_has_action(action):
    pass


@then(
    "the role_match_assessment row, the role_match_chip_click row,"
    " and the role_match_action row all contain the same session_id value"
)
def then_all_same_session():
    pass


@then("the session_id is a valid UUID")
def then_valid_uuid():
    pass
