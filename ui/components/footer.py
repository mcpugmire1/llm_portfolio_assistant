"""
Footer Component

Reusable footer with contact information and availability.
"""

import streamlit as st
import streamlit.components.v1 as components


def render_footer():
    """Render footer with contact information and CTAs."""

    # =========================================================================
    # LET'S CONNECT FOOTER - WIREFRAME EXACT
    # =========================================================================
    st.markdown(
        """
    <style>
    /* Hide the footer trigger button */
    [class*="st-key-footer_ask"] {
        display: none !important;
    }
    </style>
    <div style="background: #2c3e50; color: white; padding: 48px 40px; text-align: center; margin-top: 40px; border-radius: 8px;">
        <h3 style="font-size: 28px; margin-bottom: 12px; color: white;">Let's Connect</h3>
        <p style="font-size: 16px; margin-bottom: 8px; opacity: 0.9;">
            Seeking Director/VP opportunities in <strong>Product Leadership</strong>, <strong>Platform Engineering</strong>, and <strong>Organizational Transformation</strong>
        </p>
        <p style="font-size: 14px; margin-bottom: 32px; opacity: 0.75;">
            Available immediately • Atlanta-based preferred • Open to relocation and consulting engagements
        </p>
        <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;">
            <a href="mailto:mcpugmire@gmail.com" style="padding: 12px 28px; background: #8B5CF6; color: white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
                📧 mcpugmire@gmail.com
            </a>
            <a href="https://www.linkedin.com/in/matt-pugmire/" target="_blank" style="padding: 12px 28px; background: rgba(255,255,255,0.1); color: white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
                💼 LinkedIn
            </a>
            <a id="btn-footer-ask" style="padding: 12px 28px; background: rgba(255,255,255,0.1); color: white; border-radius: 8px; font-weight: 600; text-decoration: none; transition: all 0.2s ease; cursor: pointer;">
                🐾 Ask Agy
            </a>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # JavaScript to wire up the Ask Agy button
    components.html(
        """
    <script>
    (function() {
        setTimeout(function() {
            const parentDoc = window.parent.document;
            const btnAsk = parentDoc.getElementById('btn-footer-ask');

            if (btnAsk) {
                btnAsk.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-footer_ask"] button');
                    if (stBtn) stBtn.click();
                };
            }
        }, 200);
    })();
    </script>
    """,
        height=0,
    )

    # Hidden Streamlit button
    if st.button("", key="footer_ask"):
        st.session_state["active_tab"] = "Ask MattGPT"
        st.rerun()
