from datetime import datetime
from threading import Thread

import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

SHEET_ID = "1Xxsh7hBx6yh8K2Vn1r6ST6JTACIblUBOGbQ2QBvrAk4"
HEADERS = [
    "Event Type",
    "Timestamp",
    "Query",
    "Page",
    "Intent Family",
    "Confidence",
    "Result Count",
    "Redirect Reason",
    "User-Agent",
    "Screen Width",
    "Timezone",
    "Referrer",
    "Sources",
    "Rating",
    "Turn Index",
    "Msg Hash",
    "UTM Source",
    "UTM Medium",
    "UTM Campaign",
    "UTM Content",
    "UTM Term",
    # Role Match columns (added Apr 2026)
    "Role Title",
    "Company",
    "JD Format",
    "Required Count",
    "Preferred Count",
    "Strong Count",
    "Partial Count",
    "Gap Count",
    "Session ID",
    "Story Title",
    "Client",
]

_headers_checked = False


def is_bot() -> bool:
    """Check if the current request comes from a known monitoring bot.

    Reads the User-Agent from st.context and checks against the
    MONITORING_BOT_SIGNATURES list in config/constants.py. Call from the
    main Streamlit thread (before spawning daemon threads) since
    st.context is thread-local.

    Used by Role Match logging call sites to skip logging for bot
    traffic. The existing page_load bot filter in app.py predates this
    utility — both use the same signature list.
    """
    try:
        from config.constants import MONITORING_BOT_SIGNATURES

        user_agent = st.context.headers.get("User-Agent", "")
        if not user_agent:
            return True  # Empty UA is likely a bot (UptimeRobot free tier)
        return any(sig in user_agent for sig in MONITORING_BOT_SIGNATURES)
    except Exception:
        return False  # Fail open — don't suppress logging on errors


def get_sheet():
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        client = gspread.authorize(creds)
        return client.open_by_key(SHEET_ID).sheet1
    except Exception:
        return None


def _ensure_headers(sheet):
    global _headers_checked
    if _headers_checked:
        return
    try:
        row1 = sheet.row_values(1)
        if not row1 or len(row1) != len(HEADERS):
            sheet.update(values=[HEADERS], range_name="A1")
        _headers_checked = True
    except Exception:
        pass


def _capture_context():
    """Capture browser context from st.context before spawning thread.
    Must be called from the main Streamlit thread."""
    user_agent = ""
    timezone = ""
    screen_size = ""
    referrer = ""
    try:
        user_agent = st.context.headers.get("User-Agent", "")
    except Exception:
        pass
    try:
        timezone = st.context.timezone or ""
    except Exception:
        pass
    try:
        screen_size = st.session_state.get("_browser_screen_size", "")
    except Exception:
        pass
    try:
        referrer = st.session_state.get("_browser_referrer", "")
    except Exception:
        pass
    return user_agent, screen_size, timezone, referrer


def _append_row(row):
    """Append a single row to the sheet. Called from daemon threads.
    To suppress logging during evals, set st.session_state['__suppress_logging__'] = True
    in the eval runner before calling any log_* functions."""
    try:
        sheet = get_sheet()
        if sheet:
            _ensure_headers(sheet)
            sheet.append_row(row)
        else:
            pass
    except Exception:
        pass


def _build_row(event_type, **fields):
    """Build a row list matching HEADERS order. Missing fields default to empty."""
    row = []
    for header in HEADERS:
        if header == "Event Type":
            row.append(event_type)
        elif header == "Timestamp":
            row.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            row.append(fields.get(header, ""))
    return row


def log_query(
    query: str,
    page: str = "Ask Agy",
    intent_family: str = "",
    confidence: str = "",
    result_count: int = 0,
    redirect_reason: str = "",
):
    # Capture context in main thread before spawning daemon
    user_agent, screen_size, timezone, referrer = _capture_context()
    row = _build_row(
        "query",
        Query=query,
        Page=page,
        Confidence=confidence,
        Referrer=referrer,
        Timezone=timezone,
        **{
            "Intent Family": intent_family,
            "Result Count": result_count,
            "Redirect Reason": redirect_reason,
            "User-Agent": user_agent,
            "Screen Width": screen_size,
        },
    )
    Thread(target=_append_row, args=(row,), daemon=True).start()


def log_page_load(
    user_agent: str,
    screen_size: str,
    timezone: str,
    referrer: str,
    utm_source: str = "",
    utm_medium: str = "",
    utm_campaign: str = "",
    utm_content: str = "",
    utm_term: str = "",
):
    """Log a page_load event. Called once per session from the first-mount guard."""
    row = _build_row(
        "page_load",
        Referrer=referrer,
        Timezone=timezone,
        **{
            "User-Agent": user_agent,
            "Screen Width": screen_size,
            "UTM Source": utm_source,
            "UTM Medium": utm_medium,
            "UTM Campaign": utm_campaign,
            "UTM Content": utm_content,
            "UTM Term": utm_term,
        },
    )
    Thread(target=_append_row, args=(row,), daemon=True).start()


def log_feedback(
    rating: str,
    query: str,
    sources: str,
    turn_index: int,
    msg_hash: int,
):
    """Log a feedback (up/down vote) event. Called from the conversation UI."""
    row = _build_row(
        "feedback",
        Query=query[:200],
        Sources=sources,
        Rating=rating,
        **{
            "Turn Index": str(turn_index),
            "Msg Hash": str(msg_hash),
        },
    )
    Thread(target=_append_row, args=(row,), daemon=True).start()


# =============================================================================
# ROLE MATCH LOGGING
# =============================================================================
# Three event types, correlated by session_id:
#   role_match_assessment  — one row per successful assessment submission
#   role_match_chip_click  — one row per story chip expansion (not close)
#   role_match_action      — one row per action button click (helpful/copy_report/export)


def log_role_match_assessment(
    role_title: str,
    company: str,
    jd_format: str,
    required_count: int,
    preferred_count: int,
    strong_count: int,
    partial_count: int,
    gap_count: int,
) -> None:
    """Log a successful Role Match assessment. Called after run_assessment()."""
    user_agent, screen_size, timezone, referrer = _capture_context()
    session_id = ""
    utm_source = ""
    utm_medium = ""
    utm_campaign = ""
    utm_content = ""
    try:
        session_id = st.session_state.get("_session_id", "")
        utm_source = st.session_state.get("_utm_source", "")
        utm_medium = st.session_state.get("_utm_medium", "")
        utm_campaign = st.session_state.get("_utm_campaign", "")
        utm_content = st.session_state.get("_utm_content", "")
    except Exception:
        pass
    row = _build_row(
        "role_match_assessment",
        Timezone=timezone,
        Referrer=referrer,
        **{
            "User-Agent": user_agent,
            "Screen Width": screen_size,
            "Role Title": role_title,
            "Company": company,
            "JD Format": jd_format,
            "Required Count": str(required_count),
            "Preferred Count": str(preferred_count),
            "Strong Count": str(strong_count),
            "Partial Count": str(partial_count),
            "Gap Count": str(gap_count),
            "Session ID": session_id,
            "UTM Source": utm_source,
            "UTM Medium": utm_medium,
            "UTM Campaign": utm_campaign,
            "UTM Content": utm_content,
        },
    )
    Thread(target=_append_row, args=(row,), daemon=True).start()


def log_role_match_chip_click(
    story_title: str,
    client: str,
) -> None:
    """Log a story chip expansion. Called only on the OPEN path, not close."""
    session_id = ""
    try:
        session_id = st.session_state.get("_session_id", "")
    except Exception:
        pass
    row = _build_row(
        "role_match_chip_click",
        **{
            "Story Title": story_title[:200],
            "Client": client,
            "Session ID": session_id,
        },
    )
    Thread(target=_append_row, args=(row,), daemon=True).start()


def log_role_match_action(
    action: str,
    role_title: str = "",
) -> None:
    """Log a Role Match action button click (helpful/copy_report/export)."""
    session_id = ""
    try:
        session_id = st.session_state.get("_session_id", "")
    except Exception:
        pass
    row = _build_row(
        "role_match_action",
        Rating=action,
        **{
            "Role Title": role_title,
            "Session ID": session_id,
        },
    )
    Thread(target=_append_row, args=(row,), daemon=True).start()
