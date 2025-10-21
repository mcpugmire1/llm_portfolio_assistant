"""UI helper utilities - containers, debug output."""

import streamlit as st
from config.debug import DEBUG

def dbg(*args):
    """Debug output to sidebar (only when DEBUG=True)."""
    if DEBUG:
        try:
            st.sidebar.write("🧪", *args)
        except Exception:
            pass

def safe_container(*, border: bool = False):
    """
    Streamlit compatibility helper for bordered containers.
    
    Older Streamlit versions don't support border kwarg.
    """
    try:
        return st.container(border=border)
    except TypeError:
        return st.container()