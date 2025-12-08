"""
Story Detail Component - Shared Renderer

Displays full STAR narrative with sidebar metadata.
Used by both Explore Stories and Ask MattGPT pages.
"""

import streamlit as st
import streamlit.components.v1 as components


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
            # Build nested structure
            html = f'<div style="margin-bottom: 12px;">{main_text}'
            html += '<ul style="margin: 8px 0 0 20px; padding-left: 20px; list-style-type: circle;">'
            for item in sub_items:
                html += f'<li style="font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 6px;">{item}</li>'
            html += '</ul></div>'
            return html

    # Check for bullet points
    elif " • " in text:
        segments = text.split(" • ")
        main_text = segments[0].strip()
        sub_items = [s.strip() for s in segments[1:] if s.strip()]

        if sub_items:
            html = f'<div style="margin-bottom: 12px;">{main_text}'
            html += '<ul style="margin: 8px 0 0 20px; padding-left: 20px; list-style-type: circle;">'
            for item in sub_items:
                html += f'<li style="font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 6px;">{item}</li>'
            html += '</ul></div>'
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
                # Multiple list items - render as bullet list
                html = (
                    '<ul style="margin: 0; padding-left: 20px; list-style-type: disc;">'
                )
                for item in items:
                    html += f'<li style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin-bottom: 12px;">{item}</li>'
                html += '</ul>'
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
                html += '<ul style="margin: 8px 0 0 20px; padding-left: 20px; list-style-type: circle;">'
                for item in sub_items:
                    html += f'<li style="font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 6px;">{item}</li>'
                html += '</ul></div>'
                return html

    # No delimiters found, return as plain text
    return text


def _render_bullet_list(items: list) -> str:
    """
    Render a list of items as HTML bullets, detecting indentation for nesting.

    Handles patterns like:
    - Parent item:
      - Child item 1
      - Child item 2
    - Another parent item
    """

    if not items:
        return ""

    html = '<ul style="margin: 0; padding-left: 20px; list-style-type: disc;">'
    i = 0
    while i < len(items):
        item = items[i]
        if not item:
            i += 1
            continue

        # Check if this item is indented (it's a sub-item that wasn't caught)
        is_indented = item.startswith("  ")

        # Format the item text
        formatted = _format_nested_bullet(item.lstrip(" -"))

        # Look ahead: collect any indented sub-items
        sub_items = []
        j = i + 1
        while j < len(items) and items[j] and items[j].startswith("  "):
            sub_items.append(items[j])
            j += 1

        if sub_items:
            # Parent with nested children
            html += f'<li style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin-bottom: 8px;">{formatted}'
            html += '<ul style="margin: 8px 0 0 20px; padding-left: 20px; list-style-type: circle;">'
            for sub in sub_items:
                sub_formatted = _format_nested_bullet(sub.lstrip(" -"))
                html += f'<li style="font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 6px;">{sub_formatted}</li>'
            html += '</ul></li>'
            i = j  # Skip past the sub-items we just processed
        elif is_indented:
            # Orphaned indented item (shouldn't happen, but handle gracefully)
            html += f'<li style="font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 6px; margin-left: 20px;">{formatted}</li>'
            i += 1
        else:
            # Regular item, no children
            html += f'<li style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin-bottom: 8px;">{formatted}</li>'
            i += 1

    html += '</ul>'
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
    """Render the story detail panel with full STAR narrative and sidebar (matches wireframe)"""
    hr_style = "margin: 16px 0 12px 0; border: none; border-top: 3px solid #8B5CF6;"
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
    header_col1, header_col2 = st.columns([4, 1])

    with header_col1:
        st.markdown(
            f"<h2 style='font-size: 24px; font-weight: 700; color: var(--text-heading); margin-bottom: 12px; line-height: 1.3;'>{title}</h2>",
            unsafe_allow_html=True,
        )

        # Metadata with icons
        meta_html = f"""
        <div style="display: flex; gap: 20px; flex-wrap: wrap; align-items: center; font-size: 14px; color: var(--text-muted); margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span>🏢</span>
                <strong style="color: var(--text-primary);">{client}</strong>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span>🤝</span>
                <strong style="color: var(--text-primary);">{role}</strong>
            </div>
            {'<div style="display: flex; align-items: center; gap: 8px;"><span>📅</span><span>' + date_range + '</span></div>' if date_range else ''}
            <div style="display: flex; align-items: center; gap: 8px;">
                <span>🏷️</span>
                <span>{domain}</span>
            </div>
        </div>
        """
        st.markdown(meta_html, unsafe_allow_html=True)

    with header_col2:
        # Share and Export buttons
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button(
                "🔗",
                key=f"share_{key_suffix}_{detail.get('id', 'x')}",
                help="Share (Copy link)",
                use_container_width=True,
            ):
                st.toast(
                    "💡 To share: Copy the URL from your browser address bar", icon="ℹ️"
                )
        with btn_col2:
            if st.button(
                "📄",
                key=f"export_{key_suffix}_{detail.get('id', 'x')}",
                help="Export (Print)",
                use_container_width=True,
            ):
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
                            <div class="meta">🏢 {client} • 🤝 {role} • 📅 {date_range} • 🏷️ {domain}</div>

                            <div class="summary">
                                <div class="summary-title">💡 WHY THIS MATTERS</div>
                                <div class="content">{summary_5p or 'N/A'}</div>
                            </div>

                            <div class="section-title">📍 SITUATION</div>
                            <div class="content">{'<br>'.join(situation) if situation else 'N/A'}</div>

                            <div class="section-title">🎯 TASK</div>
                            <div class="content">{'<br>'.join(task) if task else 'N/A'}</div>

                            <div class="section-title">⚡ ACTION</div>
                            <div class="content"><ul>{''.join(f'<li>{a}</li>' for a in action)}</ul></div>

                            <div class="section-title">🎯 RESULT</div>
                            <div class="content"><ul>{''.join(f'<li>{r}</li>' for r in result)}</ul></div>

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

    st.markdown(
        "<hr style='border: none; border-top: 2px solid #e0e0e0; margin: 12px 0 20px 0;'>",
        unsafe_allow_html=True,
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
            st.markdown(
                '<div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span>📍</span><span>SITUATION</span></div>',
                unsafe_allow_html=True,
            )
            if len(situation) > 1:
                html = (
                    '<ul style="margin: 0; padding-left: 20px; list-style-type: disc;">'
                )
                for s in situation:
                    if s:
                        formatted = _format_nested_bullet(s)
                        html += f'<li style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin-bottom: 8px;">{formatted}</li>'
                html += '</ul>'
                st.markdown(html, unsafe_allow_html=True)
            else:
                if situation[0]:
                    st.markdown(
                        f'<p style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin-bottom: 12px;">{situation[0]}</p>',
                        unsafe_allow_html=True,
                    )
            st.markdown(
                "<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True
            )

        # TASK
        if task:
            st.markdown(
                '<div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span>🎯</span><span>TASK</span></div>',
                unsafe_allow_html=True,
            )
            if len(task) > 1:
                html = (
                    '<ul style="margin: 0; padding-left: 20px; list-style-type: disc;">'
                )
                for t in task:
                    if t:
                        formatted = _format_nested_bullet(t)
                        html += f'<li style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin-bottom: 8px;">{formatted}</li>'
                html += '</ul>'
                st.markdown(html, unsafe_allow_html=True)
            else:
                if task[0]:
                    formatted = _format_nested_bullet(task[0])
                    st.markdown(
                        f'<div style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin-bottom: 12px;">{formatted}</div>',
                        unsafe_allow_html=True,
                    )
            st.markdown(
                "<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True
            )

        # ACTION
        if action:
            st.markdown(
                '<div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span>⚡</span><span>ACTION</span></div>',
                unsafe_allow_html=True,
            )
            if len(action) > 1:
                html = _render_bullet_list(action)
                st.markdown(html, unsafe_allow_html=True)
            else:
                if action[0]:
                    formatted = _format_nested_bullet(action[0])
                    st.markdown(
                        f'<div style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin-bottom: 12px;">{formatted}</div>',
                        unsafe_allow_html=True,
                    )

        # RESULT
        # RESULT
        if result:
            st.markdown(
                '<div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span>🎯</span><span>RESULT</span></div>',
                unsafe_allow_html=True,
            )
            if len(result) > 1:
                # Multiple items - render as bullet list
                html = (
                    '<ul style="margin: 0; padding-left: 20px; list-style-type: disc;">'
                )
                for r in result:
                    if r:
                        formatted = _format_nested_bullet(r)
                        html += f'<li style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin-bottom: 8px;">{formatted}</li>'
                html += '</ul>'
                st.markdown(html, unsafe_allow_html=True)
            else:
                # Single item - render as paragraph
                if result[0]:
                    formatted = _format_nested_bullet(result[0])
                    st.markdown(
                        f'<div style="font-size: 14px; color: var(--text-primary); line-height: 1.7; margin-bottom: 12px;">{formatted}</div>',
                        unsafe_allow_html=True,
                    )
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
                        f'<div style="padding: 8px 0; font-size: 13px; color: var(--text-secondary); border-bottom: 1px solid var(--border-light);">{comp}</div>',
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
                '<div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 12px;">KEY METRICS</div>',
                unsafe_allow_html=True,
            )
            for value, label in metrics[:4]:
                metric_html = f'''
                <div style="background: var(--bg-surface); padding: 12px; border-radius: 6px; border-left: 3px solid var(--success-color); margin-bottom: 12px;">
                    <div style="font-size: 18px; font-weight: 700; color: var(--success-color); margin-bottom: 4px;">{value}</div>
                    <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">{label}</div>
                </div>
                '''
                st.markdown(metric_html, unsafe_allow_html=True)

    # ASK AGY ABOUT THIS
    btn_key = f"ask_story_{key_suffix}_{detail.get('id', 'x')}"
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
            box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25);
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
