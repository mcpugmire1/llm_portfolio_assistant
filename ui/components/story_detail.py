"""
Story Detail Component - Shared Renderer

Displays full STAR narrative with sidebar metadata.
Used by both Explore Stories and Ask MattGPT pages.
"""

import streamlit as st
import streamlit.components.v1 as components


# Handle deep-link to specific story via ?story= query param
def handle_story_deeplink():
    query_params = st.query_params
    if 'story' in query_params:
        story_id = query_params['story']
        # Convert sanitized ID back if needed (hyphens to pipes)
        # Only set if not already set (avoid overwriting user selection)
        if not st.session_state.get('_deeplink_handled'):
            st.session_state['active_story'] = story_id
            st.session_state['_deeplink_handled'] = True


# Call it early
handle_story_deeplink()


def _format_nested_bullet(text: str) -> str:
    """
    Format text with delimiters (◘, •, -) into nested HTML bullets.

    Handles patterns like:
    - Main point - with sub-items: ◘ Sub 1 ◘ Sub 2
    - Main point - Sub 1 - Sub 2 - Sub 3
    - Converts delimiters into proper nested <ul> structure
    """
    if not text:
        return ""

    # Strip leading " - " or "- " from the entire text (common Excel artifact)
    text = text.lstrip("- ").strip()
    # Also strip leading bullet characters
    while text and text[0] in "-*•":
        text = text[1:].lstrip()

    # Check for ◘ delimiter (highest priority)
    if "◘" in text:
        segments = text.split("◘")
        main_text = segments[0].strip()
        # Remove trailing " -" or ":" from main text if present
        if main_text.endswith(" -") or main_text.endswith(":"):
            main_text = main_text[:-1].strip()
            if main_text.endswith(":"):
                main_text = main_text[:-1].strip()

        sub_items = [s.strip() for s in segments[1:] if s.strip()]

        if sub_items:
            # Build nested structure using divs
            html = f'<div style="margin-bottom: 12px;">{main_text}'
            html += '<div style="margin-left: 20px; margin-top: 8px;">'
            for item in sub_items:
                html += f'<div style="font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 6px;">◦ {item}</div>'
            html += '</div></div>'
            return html

    # Check for bullet points
    elif " • " in text:
        segments = text.split(" • ")
        main_text = segments[0].strip()
        sub_items = [s.strip() for s in segments[1:] if s.strip()]

        if sub_items:
            html = f'<div style="margin-bottom: 12px;">{main_text}'
            html += '<div style="margin-left: 20px; margin-top: 8px;">'
            for item in sub_items:
                html += f'<div style="font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 6px;">◦ {item}</div>'
            html += '</div></div>'
            return html

    # Check for newline-separated list items (common in ACTION fields)
    # Pattern: "- Item 1\n\n- Item 2\n\n- Item 3"
    elif "\n\n-" in text or (text.count("\n") >= 2 and "-" in text):
        import re

        # Split on double newline followed by dash
        segments = re.split(r'\n\n-\s*', text)

        if len(segments) > 1:
            # First segment might not start with dash (already stripped by lstrip)
            items = []
            for seg in segments:
                seg = seg.strip()
                if seg:
                    # Remove leading dash if present
                    if seg.startswith("-"):
                        seg = seg[1:].strip()
                    items.append(seg)

            if len(items) > 1:
                # Multiple list items - render using divs
                html = ''
                for item in items:
                    html += f'<div style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin-bottom: 12px;">• {item}</div>'
                return html

    # Check for dash patterns: " -" at start of segments (common list pattern)
    # Look for pattern where text has " -" followed by capital letter or common list indicators
    elif " -" in text and text.count(" -") >= 3:
        # Try splitting on " -" (space-dash, may or may not have trailing space)
        import re

        # Split on " -" but keep the dash pattern visible for analysis
        segments = re.split(r'\s+-\s*', text)

        if len(segments) > 1:
            main_text = segments[0].strip()
            # Remove trailing colon if present
            main_text = main_text.rstrip(":").strip()
            sub_items = [s.strip() for s in segments[1:] if s.strip()]

            if sub_items and len(sub_items) >= 1:
                html = f'<div style="margin-bottom: 12px;">{main_text}'
                html += '<div style="margin-left: 20px; margin-top: 8px;">'
                for item in sub_items:
                    html += f'<div style="font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 6px;">◦ {item}</div>'
                html += '</div></div>'
                return html

    # No delimiters found, return as plain text
    return text


def _render_bullet_list(items: list) -> str:
    """
    Render a list of items as HTML divs with bullet characters (no ul/li to avoid browser defaults).
    """

    if not items:
        return ""

    html = ''
    i = 0
    while i < len(items):
        item = items[i]
        if not item:
            i += 1
            continue

        # Check if this item is indented (it's a sub-item that wasn't caught)
        is_indented = item.startswith("  ")

        # Strip leading whitespace, hyphens, asterisks, and bullets more aggressively
        clean_item = item.lstrip()
        while clean_item and clean_item[0] in "-*•":
            clean_item = clean_item[1:].lstrip()

        # Format the item text
        formatted = _format_nested_bullet(clean_item)

        # Look ahead: collect any indented sub-items
        sub_items = []
        j = i + 1
        while j < len(items) and items[j] and items[j].startswith("  "):
            sub_items.append(items[j])
            j += 1

        if sub_items:
            # Parent with nested children
            html += f'<div style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin-bottom: 8px;">• {formatted}'
            html += '<div style="margin-left: 20px; margin-top: 8px;">'
            for sub in sub_items:
                sub_formatted = _format_nested_bullet(sub.lstrip(" -"))
                html += f'<div style="font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 6px;">◦ {sub_formatted}</div>'
            html += '</div></div>'
            i = j  # Skip past the sub-items we just processed
        elif is_indented:
            # Orphaned indented item (shouldn't happen, but handle gracefully)
            html += f'<div style="font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 6px; margin-left: 20px;">◦ {formatted}</div>'
            i += 1
        else:
            # Regular item, no children
            html += f'<div style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin-bottom: 8px;">• {formatted}</div>'
            i += 1

    return html


def on_ask_this_story(detail: dict):
    """
    Handle 'Ask Agy About This' button.
    Sets up seed prompt for chip injection flow.
    """
    current_tab = st.session_state.get("active_tab", "")
    is_in_ask_mattgpt = current_tab == "Ask MattGPT"

    # Set story context
    st.session_state["active_story"] = detail.get("id")
    st.session_state["active_story_obj"] = detail
    prompt = f"Tell me more about: {detail.get('Title', 'this project')}"
    st.session_state["seed_prompt"] = prompt
    st.session_state["__ctx_locked__"] = True
    st.session_state["__ask_from_suggestion__"] = (
        True  # <-- ADD to prevent nonsense logic from misfiring
    )

    if is_in_ask_mattgpt:
        # Close any open expanders
        st.session_state["live_source_expanded"] = None
        st.session_state["live_source_expanded_id"] = None
        st.session_state["transcript_source_expanded"] = None
        st.session_state["transcript_source_expanded_id"] = None
        st.session_state["transcript_source_expanded_msg"] = None
    else:
        # Navigate to Ask MattGPT
        st.session_state["active_tab"] = "Ask MattGPT"

    st.rerun()


def render_story_detail(detail: dict | None, key_suffix: str, stories: list[dict]):
    """Render the story detail panel with full STAR narrative and sidebar (matches wireframe).

    Args:
        detail: Story dictionary to display
        key_suffix: Suffix for widget keys (automatically sanitized for Streamlit compatibility)
        stories: Full list of stories for Related Projects

    Note:
        key_suffix is sanitized to replace pipes (|) and spaces with hyphens (-).
        Story IDs use pipe delimiters (e.g., "title|client") which aren't allowed in Streamlit widget keys.
    """

    # Sanitize key_suffix for Streamlit widget keys (pipes not allowed)
    # Story IDs use | delimiter (e.g., "title|client") but Streamlit keys don't support it
    key_suffix = key_suffix.replace('|', '-').replace(' ', '-')

    hr_style = "margin: 16px 0 12px 0; border: none; border-top: 4px solid #8B5CF6; box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);"
    st.markdown(f"<hr style='{hr_style}'>", unsafe_allow_html=True)

    if not detail:
        st.markdown(
            """
            <div style="background: var(--banner-info-bg); border-left: 4px solid var(--accent-purple); padding: 12px 16px; margin: 16px 0;">
                <span style="color: var(--accent-purple); font-size: 14px;">🐾 Click a row/card above to view details.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Extract data
    title = detail.get("Title", "Untitled")
    client = detail.get("Client", "Unknown")
    role = detail.get("Role", "Unknown")
    domain = detail.get("Sub-category", "Unknown")
    start_date = detail.get("Start_Date", "")
    end_date = detail.get("End_Date", "")

    # STAR sections
    situation = detail.get("Situation", [])
    task = detail.get("Task", [])
    action = detail.get("Action", [])
    result = detail.get("Result", [])

    # Sidebar data
    public_tags = detail.get("public_tags", []) or []
    competencies = detail.get("Competencies", []) or []
    performance = detail.get("Performance", []) or []

    # 5P summary
    summary_5p = detail.get("5PSummary", "")

    # Format dates
    date_range = ""
    if start_date or end_date:
        date_range = f"{start_date or '?'} - {end_date or '?'}"

    # HEADER: Title + Metadata + Action Buttons
    # Using HTML buttons for pixel-perfect control (same pattern as Ask Agy button)
    story_id_original = detail.get("id", "")
    story_id_safe = str(detail.get('id', 'x')).replace('|', '-').replace(' ', '-')
    export_btn_key = f"export_{key_suffix}_{story_id_safe}"

    header_html = f"""
    <style>
    /* Action buttons - matches wireframe exactly */
    .detail-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 2px solid var(--border-color, #e0e0e0);
        background: linear-gradient(180deg, var(--accent-purple-bg) 0%, transparent 100%);
        padding-top: 16px;
        scroll-margin-top: 80px;
    }}

    .detail-title-section {{
        flex: 1;
    }}

    .detail-title {{
        font-size: 24px !important;
        font-weight: 700 !important;
        color: var(--accent-purple-text) !important;
        margin-bottom: 12px !important;
        line-height: 1.3 !important;
    }}

    .detail-meta {{
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        align-items: center;
    }}

    .detail-meta-item {{
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
        color: var(--text-muted, #7f8c8d);
    }}

    .detail-meta-item strong {{
        color: var(--text-primary, #2c3e50);
    }}

    .detail-actions {{
        display: flex;
        gap: 8px;
        flex-shrink: 0;
    }}

    .detail-action-btn {{
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
    }}

    .detail-action-btn:hover {{
        border-color: var(--accent-purple, #8B5CF6);
        color: var(--accent-purple, #8B5CF6);
    }}

    /* Hide Streamlit trigger buttons */
    [class*="st-key-share_"],
    [class*="st-key-export_"] {{
        position: absolute !important;
        left: -9999px !important;
        height: 0 !important;
        overflow: hidden !important;
    }}

    /* Mobile: optimized for scanning, not reading */
    @media (max-width: 768px) {{
        .detail-header {{
            flex-direction: column;
            gap: 12px;
        }}

        .detail-title {{
            font-size: 18px !important;
        }}

        .detail-meta {{
            gap: 6px 12px;
            font-size: 12px;
        }}

        .detail-meta-item {{
            font-size: 12px;
        }}

        .detail-meta-item .meta-icon {{
            display: none;
        }}

        .detail-meta-item:not(:first-child)::before {{
            content: "•";
            margin-right: 6px;
            color: var(--text-muted);
        }}

        /* Hide Share/Export on mobile - these are desktop actions */
        .detail-actions {{
            display: none !important;
        }}

        /* STAR sections: truncate to 3 lines on mobile */
        .star-content {{
            display: -webkit-box !important;
            -webkit-line-clamp: 3 !important;
            -webkit-box-orient: vertical !important;
            overflow: hidden !important;
        }}

        /* Tighter spacing between STAR sections on mobile */
        .star-section {{
            margin-bottom: 16px !important;
        }}
    }}

    /* Ensure star-content has no extra margin */
    .star-content {{
        margin: 0 !important;
        padding: 0 !important;
    }}
    </style>

    <div class="detail-header">
        <div class="detail-title-section">
            <div class="detail-title">{title}</div>
            <div class="detail-meta">
                <div class="detail-meta-item">
                    <span class="meta-icon">💼</span>
                    <strong>{client}</strong>
                </div>
                <div class="detail-meta-item">
                    <span class="meta-icon">👤</span>
                    <span>{role}</span>
                </div>
                {'<div class="detail-meta-item"><span class="meta-icon">📅</span><span>' + date_range + '</span></div>' if date_range else ''}
                <div class="detail-meta-item">
                    <span class="meta-icon">📁</span>
                    <span>{domain}</span>
                </div>
            </div>
        </div>
        <div class="detail-actions">
            <button class="detail-action-btn" id="btn-share-story">
                <span>🔗</span>
                <span class="btn-label">Share</span>
            </button>
            <button class="detail-action-btn" id="btn-export-story">
                <span>📄</span>
                <span class="btn-label">Export</span>
            </button>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    export_clicked = st.button("", key=export_btn_key)

    if export_clicked:
        # Format tags
        tags_html = ', '.join(public_tags[:10]) if public_tags else 'N/A'

        # Format competencies
        comp_html = ', '.join(competencies) if competencies else 'N/A'

        # Format metrics
        metrics_list = []
        for perf in performance:
            if perf and ("%" in perf or "x" in perf.lower()):
                metrics_list.append(perf)
        metrics_html = '<br>'.join(metrics_list) if metrics_list else 'N/A'

        # Build printable HTML
        print_html = f"""
        <script>
            var printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>{title}</title>
                    <style>
                        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 40px; max-width: 900px; margin: 0 auto; }}
                        h1 {{ color: #2c3e50; font-size: 24px; margin-bottom: 8px; }}
                        .meta {{ color: #7f8c8d; font-size: 14px; margin-bottom: 20px; }}
                        .summary {{ background: #faf5ff; border-left: 3px solid #8B5CF6; padding: 16px; margin-bottom: 20px; }}
                        .summary-title {{ color: #8B5CF6; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; }}
                        .section-title {{ color: #8B5CF6; font-size: 12px; font-weight: 700; text-transform: uppercase; margin: 20px 0 8px 0; }}
                        .content {{ color: #2c3e50; font-size: 14px; line-height: 1.7; }}
                        ul {{ padding-left: 20px; }}
                        li {{ margin-bottom: 8px; }}
                        .sidebar {{ background: #f8f9fa; padding: 20px; margin-top: 30px; border-radius: 8px; }}
                        .sidebar-title {{ color: #7f8c8d; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; }}
                        .sidebar-content {{ color: #555; font-size: 13px; margin-bottom: 16px; }}
                        .metric {{ background: #fff; border-left: 3px solid #27ae60; padding: 8px 12px; margin-bottom: 8px; }}
                        .metric-value {{ color: #27ae60; font-size: 18px; font-weight: 700; }}
                    </style>
                </head>
                <body>
                    <h1>{title}</h1>
                    <div class="meta">💼 {client} • 🤝 {role} • 📅 {date_range} • 📁 {domain}</div>

                    <div class="summary">
                        <div class="summary-title">💡 WHY THIS MATTERS</div>
                        <div class="content">{summary_5p or 'N/A'}</div>
                    </div>

                    <div class="section-title">📍 SITUATION</div>
                    <div class="content">{'<br>'.join(situation) if situation else 'N/A'}</div>

                    <div class="section-title">🎯 TASK</div>
                    <div class="content">{'<br>'.join(task) if task else 'N/A'}</div>

                    <div class="section-title">⚡ ACTION</div>
                    <div class="content"><ul>{''.join(f'<li>{a.lstrip("-*• ").strip()}</li>' for a in action if a)}</ul></div>

                    <div class="section-title">🎯 RESULT</div>
                    <div class="content"><ul>{''.join(f'<li>{r.lstrip("-*• ").strip()}</li>' for r in result if r)}</ul></div>

                    <div class="sidebar">
                        <div class="sidebar-title">Technologies & Practices</div>
                        <div class="sidebar-content">{tags_html}</div>

                        <div class="sidebar-title">Core Competencies</div>
                        <div class="sidebar-content">{comp_html}</div>

                        <div class="sidebar-title">Key Metrics</div>
                        <div class="sidebar-content">{metrics_html}</div>
                    </div>
                </body>
                </html>
            `);
            printWindow.document.close();
            printWindow.print();
        </script>
        """
        st.components.v1.html(print_html, height=0)

    # JS wiring for HTML buttons
    components.html(
        f"""
        <script>
        (function() {{
            var parentDoc = window.parent.document;

            // Micro-scroll with offset for navbar
            setTimeout(function() {{
                var detail = parentDoc.querySelector('.detail-header');
                if (detail) {{
                    var rect = detail.getBoundingClientRect();
                    var scrollTop = window.parent.scrollY + rect.top - 100;
                    detail.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}

                // Wire buttons after scroll
                setTimeout(function() {{
                    var shareBtn = parentDoc.getElementById('btn-share-story');
                    if (shareBtn) {{
                        shareBtn.onclick = function(e) {{
                            e.preventDefault();
                            var storyId = '{story_id_original}';
                            var url = window.parent.location.origin + window.parent.location.pathname + '?story=' + encodeURIComponent(storyId);

                            var tempInput = parentDoc.createElement('input');
                            tempInput.style.position = 'absolute';
                            tempInput.style.left = '-9999px';
                            tempInput.style.opacity = '0';
                            tempInput.value = url;
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

                    var exportBtn = parentDoc.getElementById('btn-export-story');
                    if (exportBtn) {{
                        exportBtn.onclick = function() {{
                            var stBtn = parentDoc.querySelector('[class*="st-key-{export_btn_key}"] button');
                            if (stBtn) stBtn.click();
                        }};
                    }}
                }}, 500);
            }}, 200);
        }})();
        </script>
        """,
        height=0,
    )

    # TWO-COLUMN LAYOUT
    main_col, sidebar_col = st.columns([2, 1])

    with main_col:
        # 5P SUMMARY (if available)
        if summary_5p:
            st.markdown(
                f'''
            <div style="background: var(--banner-info-bg); border-left: 3px solid var(--accent-purple); padding: 16px 20px; border-radius: 8px; margin-bottom: 24px;">
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--accent-purple); margin-bottom: 12px; letter-spacing: 0.5px;">
                    💡 WHY THIS MATTERS
                </div>
                <p style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin: 0;">{summary_5p}</p>
            </div>
            ''',
                unsafe_allow_html=True,
            )

        # SITUATION
        if situation:
            if len(situation) > 1:
                items_html = ''.join(
                    f'<div style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin-bottom: 8px;">• {_format_nested_bullet(s)}</div>'
                    for s in situation
                    if s
                )
                html = f'<div class="star-section"><div class="star-label" style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span>📍</span><span>SITUATION</span></div><div class="star-content">{items_html}</div></div>'
            else:
                html = f'<div class="star-section"><div class="star-label" style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span>📍</span><span>SITUATION</span></div><div class="star-content"><p style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin: 0;">{situation[0]}</p></div></div>'
            st.markdown(html, unsafe_allow_html=True)
            st.markdown(
                "<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True
            )

        # TASK
        if task:
            if len(task) > 1:
                items_html = ''.join(
                    f'<div style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin-bottom: 8px;">• {_format_nested_bullet(t)}</div>'
                    for t in task
                    if t
                )
                html = f'<div class="star-section"><div class="star-label" style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span>🎯</span><span>TASK</span></div><div class="star-content">{items_html}</div></div>'
            else:
                formatted = _format_nested_bullet(task[0]) if task[0] else ''
                html = f'<div class="star-section"><div class="star-label" style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span>🎯</span><span>TASK</span></div><div class="star-content"><div style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin: 0;">{formatted}</div></div></div>'
            st.markdown(html, unsafe_allow_html=True)
            st.markdown(
                "<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True
            )

        # ACTION
        if action:
            if len(action) > 1:
                content_html = _render_bullet_list(action)
                html = f'<div class="star-section"><div class="star-label" style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span>⚡</span><span>ACTION</span></div><div class="star-content">{content_html}</div></div>'
            else:
                formatted = _format_nested_bullet(action[0]) if action[0] else ''
                html = f'<div class="star-section"><div class="star-label" style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span>⚡</span><span>ACTION</span></div><div class="star-content"><div style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin: 0;">{formatted}</div></div></div>'
            st.markdown(html, unsafe_allow_html=True)
            st.markdown(
                "<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True
            )

        # RESULT
        if result:
            if len(result) > 1:
                items_html = ''.join(
                    f'<div style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin-bottom: 8px;">• {_format_nested_bullet(r)}</div>'
                    for r in result
                    if r
                )
                html = f'<div class="star-section"><div class="star-label" style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span>🏆</span><span>RESULT</span></div><div class="star-content">{items_html}</div></div>'
            else:
                formatted = _format_nested_bullet(result[0]) if result[0] else ''
                html = f'<div class="star-section"><div class="star-label" style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span>🏆</span><span>RESULT</span></div><div class="star-content"><div style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin: 0;">{formatted}</div></div></div>'
            st.markdown(html, unsafe_allow_html=True)
    with sidebar_col:
        # TECHNOLOGIES & PRACTICES
        if public_tags:
            st.markdown(
                '<div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 12px;">TECHNOLOGIES & PRACTICES</div>',
                unsafe_allow_html=True,
            )
            tags_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px;">'
            for tag in public_tags[:10]:
                if tag:
                    tags_html += f'<span style="background: var(--pill-bg); padding: 6px 12px; border-radius: 12px; font-size: 12px; color: var(--pill-text); font-weight: 500;">{tag}</span>'
            tags_html += '</div>'
            st.markdown(tags_html, unsafe_allow_html=True)
            st.markdown(
                '<div style="border-bottom: 1px solid var(--border-color); margin-bottom: 24px;"></div>',
                unsafe_allow_html=True,
            )

        # CORE COMPETENCIES
        if competencies:
            st.markdown(
                '<div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 12px;">CORE COMPETENCIES</div>',
                unsafe_allow_html=True,
            )
            for comp in competencies:
                if comp:
                    st.markdown(
                        f'<div style="padding: 8px 0; font-size: 13px; color: var(--text-secondary);">{comp}</div>',
                        unsafe_allow_html=True,
                    )

            st.markdown(
                '<div style="border-bottom: 1px solid var(--border-color); margin: 24px 0;"></div>',
                unsafe_allow_html=True,
            )

        # KEY METRICS
        metrics = []
        for perf in performance:
            if perf and (
                "%" in perf
                or "x" in perf.lower()
                or "month" in perf.lower()
                or "week" in perf.lower()
            ):
                import re

                match = re.search(r'(\d+[%xX]?|\d+\+?)', perf)
                if match:
                    metrics.append((match.group(1), perf[:50]))

        if metrics:
            st.markdown(
                '<div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 12px;">KEY METRICS</div>',
                unsafe_allow_html=True,
            )
            for value, label in metrics[:4]:
                metric_html = f'''
                <div style="background: var(--bg-surface); padding: 12px; border-radius: 6px; border-left: 3px solid var(--success-color); margin-bottom: 12px;">
                    <div style="font-size: 18px; font-weight: 700; color: var(--success-color); margin-bottom: 4px;">{value}</div>
                    <div style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">{label}</div>
                </div>
                '''
                st.markdown(metric_html, unsafe_allow_html=True)

    # ASK AGY ABOUT THIS
    btn_key = f"ask_story_{key_suffix}_{story_id_safe}"
    st.markdown(
        """
        <style>
        .card-btn-primary {
            display: inline-block;
            padding: 14px 28px;
            background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
            border: none;
            border-radius: 8px;
            color: white !important;
            font-weight: 600;
            font-size: 15px;
            text-decoration: none !important;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .card-btn-primary:hover {
            background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);
            text-decoration: none !important;
        }
        [class*="st-key-ask_story_"] {
            display: none !important;
        }
        [class*="st-key-btn_page_"] .stButton > button,
        [class*="st-key-btn_first_"] .stButton > button,
        [class*="st-key-btn_prev_"] .stButton > button,
        [class*="st-key-btn_next_"] .stButton > button,
        [class*="st-key-btn_last_"] .stButton > button {
            padding: 8px 16px !important;
            font-size: 13px !important;
            border-radius: 6px !important;
            border: 1px solid var(--border-color) !important;
            background: var(--bg-card) !important;
            color: var(--text-secondary) !important;
            margin-top: 0 !important;
            box-shadow: none !important;
            width: auto !important;
        }
        </style>
        <br>
        <p style='text-align: center; margin-bottom: 20px; color: var(--text-secondary); font-size: 14px;'>💬 Want to know more about this project?</p>
        <div style="text-align: center;">
            <a id="btn-ask-story" class="card-btn-primary">Ask Agy 🐾 About This</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Hidden trigger button
    btn_key = f"ask_story_{key_suffix}_{detail.get('id', 'x')}"
    if st.button("", key=btn_key):
        on_ask_this_story(detail)

    # JS wiring

    components.html(
        """
    <script>
    (function() {
        setTimeout(function() {
            var parentDoc = window.parent.document;
            var btn = parentDoc.getElementById('btn-ask-story');
            if (btn) {
                btn.onclick = function() {
                    var stBtn = parentDoc.querySelector('[class*="st-key-ask_story_"] button');
                    if (stBtn) stBtn.click();
                };
            }
        }, 200);
    })();
    </script>
    """,
        height=0,
    )
