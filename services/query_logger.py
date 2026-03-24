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
]

_headers_checked = False


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
    """Append a single row to the sheet. Called from daemon threads."""
    try:
        sheet = get_sheet()
        if sheet:
            _ensure_headers(sheet)
            sheet.append_row(row)
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


def log_page_load(user_agent: str, screen_size: str, timezone: str, referrer: str):
    """Log a page_load event. Called once per session from the first-mount guard."""
    row = _build_row(
        "page_load",
        Referrer=referrer,
        Timezone=timezone,
        **{
            "User-Agent": user_agent,
            "Screen Width": screen_size,
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
