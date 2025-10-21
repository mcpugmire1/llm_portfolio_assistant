"""
Configuration management utilities.

Handles reading from st.secrets (Streamlit Cloud) with .env fallback.
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_conf(key: str, default: str | None = None):
    """
    Get config value from st.secrets (priority) or environment variable.
    
    Args:
        key: Configuration key name
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    try:
        v = st.secrets.get(key)
        if v is not None:
            return v
    except Exception:
        pass
    return os.getenv(key, default)