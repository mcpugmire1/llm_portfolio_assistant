from datetime import datetime
from threading import Thread

import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

SHEET_ID = "1Xxsh7hBx6yh8K2Vn1r6ST6JTACIblUBOGbQ2QBvrAk4"
HEADERS = [
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
    except Exception as e:
        print(f"[QUERY_LOGGER] get_sheet error: {e}")
        return None


def _ensure_headers(sheet):
    global _headers_checked
    if _headers_checked:
        return
    try:
        row1 = sheet.row_values(1)
        if not row1 or len(row1) != len(HEADERS):
            sheet.update("A1", [HEADERS])
        _headers_checked = True
    except Exception as e:
        print(f"[QUERY_LOGGER] _ensure_headers error: {e}")


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
    Thread(
        target=_write_to_sheet,
        args=(
            query,
            page,
            intent_family,
            confidence,
            result_count,
            redirect_reason,
            user_agent,
            screen_size,
            timezone,
            referrer,
        ),
        daemon=True,
    ).start()


def _write_to_sheet(
    query,
    page,
    intent_family,
    confidence,
    result_count,
    redirect_reason,
    user_agent,
    screen_size,
    timezone,
    referrer,
):
    try:
        sheet = get_sheet()
        if sheet:
            _ensure_headers(sheet)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row(
                [
                    timestamp,
                    query,
                    page,
                    intent_family,
                    confidence,
                    result_count,
                    redirect_reason,
                    user_agent,
                    screen_size,
                    timezone,
                    referrer,
                ]
            )
    except Exception as e:
        print(f"[QUERY_LOGGER] _write_to_sheet error: {e}")
