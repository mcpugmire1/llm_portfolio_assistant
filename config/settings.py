"""
Configuration management utilities.

Handles reading from st.secrets (Streamlit Cloud) with .env fallback.
"""

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def _in_streamlit_context() -> bool:
    """True if Streamlit's runtime is initialized (i.e., we're inside a
    live `streamlit run` invocation).

    Used to gate st.secrets access. Outside a script run, Streamlit's
    runtime is not initialized and st.secrets access raises + prints
    "missing ScriptRunContext" to stderr.

    Uses streamlit.runtime.exists() rather than get_script_run_ctx()
    because the latter itself logs the missing-context warning when
    called in bare mode -- exactly the noise we're trying to avoid.
    exists() is silent and returns False cleanly.
    """
    try:
        from streamlit.runtime import exists

        return exists()
    except Exception:
        return False


def get_conf(key: str, default: str | None = None):
    """Get config value from st.secrets or environment variable.

    Resolution order depends on execution context:
      - Streamlit run: st.secrets -> os.getenv -> default
      - Bare mode (CLI, subprocess, pytest without streamlit):
            os.getenv -> default  (st.secrets skipped entirely)

    Behavior change vs prior implementation (MATTGPT-216, Aug 28 2026):
    prior code always attempted st.secrets and caught the exception in
    bare mode. That was a guaranteed failure path -- st.secrets is
    script-scoped and never populated outside a script run -- but it
    triggered a Streamlit warning to stderr on every call, polluting
    CLI output and breaking tests that parsed stderr as JSON. New code
    skips the guaranteed-failure path. If any code path outside a
    Streamlit run somehow had a populated st.secrets (unusual: would
    require programmatic assignment before the get_conf call), it would
    no longer be consulted. No such path exists in this repo today.
    """
    if _in_streamlit_context():
        try:
            v = st.secrets.get(key)
            if v is not None:
                return v
        except Exception:
            pass
    return os.getenv(key, default)
