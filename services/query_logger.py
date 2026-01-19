from datetime import datetime

import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

SHEET_ID = "1Xxsh7hBx6yh8K2Vn1r6ST6JTACIblUBOGbQ2QBvrAk4"


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


def log_query(query: str, page: str = "Ask Agy"):
    try:
        sheet = get_sheet()
        if sheet:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([timestamp, query, page])
    except Exception:
        pass
