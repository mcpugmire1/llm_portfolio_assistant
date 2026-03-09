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
            sheet.update("A1", [HEADERS])
        _headers_checked = True
    except Exception:
        pass


def log_query(
    query: str,
    page: str = "Ask Agy",
    intent_family: str = "",
    confidence: str = "",
    result_count: int = 0,
    redirect_reason: str = "",
):
    Thread(
        target=_write_to_sheet,
        args=(query, page, intent_family, confidence, result_count, redirect_reason),
        daemon=True,
    ).start()


def _write_to_sheet(
    query, page, intent_family, confidence, result_count, redirect_reason
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
                ]
            )
    except Exception:
        pass
