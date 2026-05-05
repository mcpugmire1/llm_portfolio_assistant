"""
Private View Lock Icon (Phase 4 — slice 1)

Renders a discreet lock icon mounted on the Role Match page (top-right
of the results column) that toggles st.session_state[PRIVATE_MODE_KEY].
Locked state opens an st.popover with a masked password input; unlocked
state shows a plain button that re-locks on click.

Submission compares the typed password to MATTGPT_PRIVATE_BYPASS_TOKEN
via get_private_bypass_token(). Env unset, empty input, or mismatch all
fail closed silently — no error surfaced. Deployment state must not leak
to the user.

Mount point: ui/pages/role_match.py inside the right column (results_col).
Visibility on mobile is handled by Role Match's own desktop-only gate
(<1024px shows the "Best experienced on desktop" message instead of the
workspace, so the lock disappears with it).
"""

import streamlit as st

from config.constants import PRIVATE_MODE_KEY, get_private_bypass_token


def render_lock_icon() -> None:
    """Render the lock icon: re-lock button when unlocked, password popover when locked."""
    is_unlocked = bool(st.session_state.get(PRIVATE_MODE_KEY, False))

    if is_unlocked:
        if st.button("🔓", key="lock_icon_relock", help="Lock private fit assessment"):
            st.session_state[PRIVATE_MODE_KEY] = False
            st.rerun()
        return

    with st.popover(
        "🔒", help="Unlock private fit assessment", use_container_width=False
    ):
        # st.container(key=...) gives us a reachable st-key-* class inside the
        # portal-rendered popover body for scoped CSS. Without it, the popover
        # body has only Streamlit's emotion-cache hash classes, which aren't
        # stable across Streamlit versions.
        with st.container(key="lock_popover"):
            st.markdown("**Private view**")
            with st.form("lock_password_form", clear_on_submit=True):
                password = st.text_input(
                    "Access code",
                    type="password",
                    label_visibility="collapsed",
                    placeholder="Access code",
                    key="lock_password_input",
                )
                submitted = st.form_submit_button("Unlock", use_container_width=True)
                if submitted:
                    expected = get_private_bypass_token()
                    # Fail closed: env unset, empty password, or mismatch are all
                    # silent no-ops. Deployment state must not leak to the user.
                    if expected and password and password == expected:
                        st.session_state[PRIVATE_MODE_KEY] = True
                        st.rerun()
