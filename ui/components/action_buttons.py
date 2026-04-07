"""
Action Buttons Component — Shared Share / Export / Helpful row

Extracted from ui/components/story_detail.py so the same row of action
buttons can be reused on the Role Match results panel and any future
detail-style surface that needs them. Single source of truth for the
visual treatment, click wiring, feedback logging, and print export.

Design:

The component is split into THREE small functions so the caller can
embed the buttons inside their own header HTML (where they need to live
as a flex sibling of a title section), then trigger the click handlers
and JS wiring afterward as separate Streamlit calls:

    get_action_buttons_css()         -> str  (paste into a <style> block)
    get_action_buttons_html(...)     -> str  (embed in your header HTML)
    render_action_button_handlers(...)       (renders hidden buttons + JS)

The HTML and CSS class names match story_detail.py exactly
(`.detail-actions`, `.detail-action-btn`, `.helpful-confirmed`) so the
visual treatment stays in lockstep across surfaces.

Caller pattern (see story_detail.py and role_match.py for live examples):

    buttons_html = get_action_buttons_html(
        button_id_prefix="btn-role-match",
        is_helpful_confirmed=False,
    )

    st.markdown(
        f'''<style>{get_action_buttons_css()}</style>
        <div class="my-header">
            <div class="my-title">...</div>
            {buttons_html}
        </div>''',
        unsafe_allow_html=True,
    )

    render_action_button_handlers(
        button_id_prefix="btn-role-match",
        key_suffix="role_match",
        share_text="Role Match: ...",
        export_html_doc=printable_html,
        feedback_query=role_title,
        feedback_sources=f"role_match:{role_title}",
        confirmed_key="role_match_helpful_voted",
    )
"""

import streamlit as st
import streamlit.components.v1 as components

from services.query_logger import log_feedback


def get_action_buttons_css() -> str:
    """Return the CSS rules that style the action buttons row.

    Caller pastes the returned string inside their own <style> block.
    Class names (`.detail-actions`, `.detail-action-btn`, etc.) are kept
    identical to story_detail.py for visual consistency across surfaces.
    """
    return """
    .detail-actions {
        display: flex;
        gap: 8px;
        flex-shrink: 0;
    }

    .detail-action-btn {
        padding: 8px 16px;
        border: 2px solid var(--border-color, #e0e0e0);
        background: var(--bg-card, white);
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        color: var(--text-secondary, #555);
        cursor: pointer;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .detail-action-btn:hover {
        border-color: var(--accent-purple, #8B5CF6);
        color: var(--accent-purple, #8B5CF6);
    }

    /* Hide the Streamlit trigger buttons that the HTML buttons wire to */
    [class*="st-key-share_"],
    [class*="st-key-export_"],
    [class*="st-key-helpful_"] {
        position: absolute !important;
        left: -9999px !important;
        height: 0 !important;
        overflow: hidden !important;
    }

    /* Helpful button confirmed state */
    .detail-action-btn.helpful-confirmed {
        background: var(--success-color) !important;
        border-color: var(--success-color) !important;
        color: white !important;
        cursor: default;
        opacity: 1;
    }
    .detail-action-btn.helpful-confirmed:hover {
        border-color: var(--success-color) !important;
        color: white !important;
    }

    /* Mobile: hide the action row entirely — these are desktop actions */
    @media (max-width: 768px) {
        .detail-actions {
            display: none !important;
        }
    }
    """


def get_action_buttons_html(
    *, button_id_prefix: str, is_helpful_confirmed: bool
) -> str:
    """Return the HTML for the three-button action row.

    Args:
        button_id_prefix: Unique HTML id prefix for this instance — buttons
            become `{prefix}-helpful`, `{prefix}-share`, `{prefix}-export`.
            Pick something stable per surface (e.g., "btn-story-detail",
            "btn-role-match"). Used by render_action_button_handlers to
            wire the click events.
        is_helpful_confirmed: When True, the Helpful button renders in the
            confirmed (green ✓) state and is disabled.

    Returns:
        HTML string for `<div class="detail-actions">...</div>`. The caller
        embeds this string inside their own header markup so it lands as a
        flex sibling of their title section.
    """
    helpful_class = " helpful-confirmed" if is_helpful_confirmed else ""
    helpful_disabled = " disabled" if is_helpful_confirmed else ""
    helpful_label = "👍 Helpful ✓" if is_helpful_confirmed else "Helpful"

    return (
        '<div class="detail-actions">'
        f'<button class="detail-action-btn{helpful_class}" '
        f'id="{button_id_prefix}-helpful"{helpful_disabled}>'
        f'<span class="btn-label">{helpful_label}</span></button>'
        f'<button class="detail-action-btn" id="{button_id_prefix}-share">'
        '<span>🔗</span><span class="btn-label">Share</span></button>'
        f'<button class="detail-action-btn" id="{button_id_prefix}-export">'
        '<span>📄</span><span class="btn-label">Export</span></button>'
        "</div>"
    )


def render_action_button_handlers(
    *,
    button_id_prefix: str,
    key_suffix: str,
    export_html_doc: str,
    feedback_query: str,
    feedback_sources: str,
    confirmed_key: str,
    feedback_msg_hash: int = 0,
    share_text: str | None = None,
    share_url_path: str | None = None,
) -> None:
    """Render the hidden Streamlit trigger buttons and JS wiring for the action row.

    Must be called AFTER the parent HTML containing get_action_buttons_html()
    has been rendered, so the JS can find the buttons in the DOM.

    Helpful click → log_feedback() + sets `confirmed_key` in session state +
        triggers a rerun so the button re-renders in confirmed state.
    Share click → pure client-side clipboard copy of either `share_text`
        (literal) or a URL built from window.parent.location + share_url_path.
    Export click → opens a new browser window and prints `export_html_doc`.

    Exactly one of `share_text` or `share_url_path` must be provided.

    Args:
        button_id_prefix: Same prefix passed to get_action_buttons_html().
        key_suffix: Unique suffix for the hidden Streamlit button keys
            (`share_{suffix}`, `export_{suffix}`, `helpful_{suffix}`).
        export_html_doc: Full HTML document body that will be written to
            the new window for printing. Caller is responsible for the
            full <html>...</html> structure including any inline styles.
        feedback_query: `query` field passed to log_feedback().
        feedback_sources: `sources` field passed to log_feedback().
        confirmed_key: Session state key tracking the helpful-confirmed flag.
        feedback_msg_hash: Optional msg_hash for log_feedback(). Defaults to 0.
        share_text: Plain text or URL to copy verbatim to the clipboard.
        share_url_path: URL path or query string (e.g., "?story=123") that
            gets appended to window.parent.location.origin + .pathname at
            click time. Use this when the link must be the user's current URL.
    """
    if (share_text is None) == (share_url_path is None):
        raise ValueError("Provide exactly one of share_text or share_url_path")

    helpful_btn_key = f"helpful_{key_suffix}"
    export_btn_key = f"export_{key_suffix}"

    is_helpful_confirmed = st.session_state.get(confirmed_key) == "up"

    # Hidden Streamlit button: Helpful → log_feedback + set confirmed
    helpful_clicked = st.button("", key=helpful_btn_key)
    if helpful_clicked and not is_helpful_confirmed:
        st.session_state[confirmed_key] = "up"
        log_feedback(
            rating="up",
            query=feedback_query,
            sources=feedback_sources,
            turn_index=0,
            msg_hash=feedback_msg_hash,
        )
        st.rerun()

    # Hidden Streamlit button: Export → opens print window
    export_clicked = st.button("", key=export_btn_key)
    if export_clicked:
        # Escape backticks in the doc since we're embedding it in a JS template literal
        escaped_doc = export_html_doc.replace("\\", "\\\\").replace("`", "\\`")
        components.html(
            f"""
            <script>
                var printWindow = window.open('', '_blank');
                printWindow.document.write(`{escaped_doc}`);
                printWindow.document.close();
                printWindow.print();
            </script>
            """,
            height=0,
        )

    # JS wiring: bridge HTML buttons → hidden Streamlit buttons + clipboard copy.
    # Share is purely client-side (no Streamlit roundtrip needed).
    if share_url_path is not None:
        # Build the URL at click time using the user's current location
        share_url_js_literal = repr(share_url_path)  # Python repr → safe JS string
        share_target_js = (
            "var url = window.parent.location.origin + "
            "window.parent.location.pathname + " + share_url_js_literal + ";"
        )
        clipboard_value_js = "url"
    else:
        # Copy the provided text verbatim. Use repr() so newlines/quotes are escaped safely.
        share_text_js_literal = repr(share_text)
        share_target_js = f"var url = {share_text_js_literal};"
        clipboard_value_js = "url"

    components.html(
        f"""
        <script>
        (function() {{
            var parentDoc = window.parent.document;

            setTimeout(function() {{
                var shareBtn = parentDoc.getElementById('{button_id_prefix}-share');
                if (shareBtn) {{
                    shareBtn.onclick = function(e) {{
                        e.preventDefault();
                        {share_target_js}

                        var tempInput = parentDoc.createElement('textarea');
                        tempInput.style.position = 'absolute';
                        tempInput.style.left = '-9999px';
                        tempInput.style.opacity = '0';
                        tempInput.value = {clipboard_value_js};
                        parentDoc.body.appendChild(tempInput);
                        tempInput.select();
                        parentDoc.execCommand('copy');
                        parentDoc.body.removeChild(tempInput);

                        var originalHTML = shareBtn.innerHTML;
                        shareBtn.innerHTML = '<span>✓</span><span class="btn-label">Copied!</span>';
                        shareBtn.style.borderColor = '#10B981';
                        shareBtn.style.color = '#10B981';
                        setTimeout(function() {{
                            shareBtn.innerHTML = originalHTML;
                            shareBtn.style.borderColor = '';
                            shareBtn.style.color = '';
                        }}, 2000);
                    }};
                }}

                var exportBtn = parentDoc.getElementById('{button_id_prefix}-export');
                if (exportBtn) {{
                    exportBtn.onclick = function() {{
                        var stBtn = parentDoc.querySelector('[class*="st-key-{export_btn_key}"] button');
                        if (stBtn) stBtn.click();
                    }};
                }}

                var helpfulBtn = parentDoc.getElementById('{button_id_prefix}-helpful');
                if (helpfulBtn && !helpfulBtn.disabled) {{
                    helpfulBtn.onclick = function() {{
                        var stBtn = parentDoc.querySelector('[class*="st-key-{helpful_btn_key}"] button');
                        if (stBtn) stBtn.click();
                    }};
                }}
            }}, 200);
        }})();
        </script>
        """,
        height=0,
    )
