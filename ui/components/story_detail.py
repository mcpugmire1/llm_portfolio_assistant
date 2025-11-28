"""
Story Detail Component - Shared Renderer

Displays full STAR narrative with sidebar metadata.
Used by both Explore Stories and Ask MattGPT pages.
"""

from typing import List, Optional

import streamlit as st
from streamlit_js_eval import streamlit_js_eval


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
                html += f'<li style="font-size: 13px; color: #555; line-height: 1.6; margin-bottom: 6px;">{item}</li>'
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
                html += f'<li style="font-size: 13px; color: #555; line-height: 1.6; margin-bottom: 6px;">{item}</li>'
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
                html = '<ul style="margin: 0; padding-left: 20px; list-style-type: disc;">'
                for item in items:
                    html += f'<li style="font-size: 14px; color: #2c3e50; line-height: 1.7; margin-bottom: 12px;">{item}</li>'
                html += '</ul>'
                return html

    # Check for dash patterns: " -" at start of segments (common list pattern)
    # Look for pattern where text has " -" followed by capital letter or common list indicators
    elif " -" in text and text.count(" -") >= 2:
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
                    html += f'<li style="font-size: 13px; color: #555; line-height: 1.6; margin-bottom: 6px;">{item}</li>'
                html += '</ul></div>'
                return html

    # No delimiters found, return as plain text
    return text


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


def render_story_detail(detail: Optional[dict], key_suffix: str, stories: List[dict]):
    """Render the story detail panel with full STAR narrative and sidebar (matches wireframe)"""
    hr_style = "margin: 16px 0 12px 0; border: none; border-top: 3px solid #8B5CF6;"
    st.markdown(f"<hr style='{hr_style}'>", unsafe_allow_html=True)

    if not detail:
        st.info("Click a row/card above to view details.")
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
        st.markdown(f"<h2 style='font-size: 24px; font-weight: 700; color: #2c3e50; margin-bottom: 12px; line-height: 1.3;'>{title}</h2>", unsafe_allow_html=True)

        # Metadata with icons
        meta_html = f"""
        <div style="display: flex; gap: 20px; flex-wrap: wrap; align-items: center; font-size: 14px; color: #7f8c8d; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span>🏢</span>
                <strong style="color: #2c3e50;">{client}</strong>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span>🤝</span>
                <strong style="color: #2c3e50;">{role}</strong>
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
            if st.button("🔗", key=f"share_{key_suffix}_{detail.get('id', 'x')}", help="Share (Copy link)", use_container_width=True):
                st.toast("💡 To share: Copy the URL from your browser address bar", icon="ℹ️")
        with btn_col2:
            if st.button("📄", key=f"export_{key_suffix}_{detail.get('id', 'x')}", help="Export (Print)", use_container_width=True):
                st.toast("Print dialog opened. Save as PDF.", icon="ℹ️")
                streamlit_js_eval(js_expressions="window.print()", key=f"print_{key_suffix}")

    st.markdown("<hr style='border: none; border-top: 2px solid #e0e0e0; margin: 12px 0 20px 0;'>", unsafe_allow_html=True)

    # TWO-COLUMN LAYOUT
    main_col, sidebar_col = st.columns([2, 1])

    with main_col:
        # 5P SUMMARY (if available)
        if summary_5p:
            st.markdown(f'''
            <div style="background: #faf5ff; border-left: 3px solid #8B5CF6; padding: 16px 20px; border-radius: 8px; margin-bottom: 24px;">
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 12px; letter-spacing: 0.5px;">
                    💡 WHY THIS MATTERS
                </div>
                <p style="font-size: 14px; color: #2c3e50; line-height: 1.7; margin: 0;">{summary_5p}</p>
            </div>
            ''', unsafe_allow_html=True)

        # SITUATION
        if situation:
            st.markdown('<div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span>📍</span><span>SITUATION</span></div>', unsafe_allow_html=True)
            for s in situation:
                if s:
                    st.markdown(f'<p style="font-size: 14px; color: #2c3e50; line-height: 1.7; margin-bottom: 12px;">{s}</p>', unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

        # TASK
        if task:
            st.markdown('<div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span>🎯</span><span>TASK</span></div>', unsafe_allow_html=True)
            for t in task:
                if t:
                    formatted = _format_nested_bullet(t)
                    st.markdown(f'<div style="font-size: 14px; color: #2c3e50; line-height: 1.7; margin-bottom: 12px;">{formatted}</div>', unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

        # ACTION
        if action:
            st.markdown('<div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span>⚡</span><span>ACTION</span></div>', unsafe_allow_html=True)
            for a in action:
                if a:
                    formatted = _format_nested_bullet(a)
                    # Use div instead of p to avoid nesting issues with nested HTML
                    st.markdown(f'<div style="font-size: 14px; color: #2c3e50; line-height: 1.7; margin-bottom: 12px;">{formatted}</div>', unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

        # RESULT
        if result:
            st.markdown('<div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #8B5CF6; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><span>🎯</span><span>RESULT</span></div>', unsafe_allow_html=True)
            for r in result:
                if r:
                    formatted = _format_nested_bullet(r)
                    # Use div instead of p to avoid nesting issues with nested HTML
                    st.markdown(f'<div style="font-size: 14px; color: #2c3e50; line-height: 1.7; margin-bottom: 12px;">{formatted}</div>', unsafe_allow_html=True)

    with sidebar_col:
        # TECHNOLOGIES & PRACTICES
        if public_tags:
            st.markdown('<div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #7f8c8d; margin-bottom: 12px;">TECHNOLOGIES & PRACTICES</div>', unsafe_allow_html=True)
            tags_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px;">'
            for tag in public_tags[:10]:
                if tag:
                    tags_html += f'<span style="background: #ecf0f1; padding: 6px 12px; border-radius: 12px; font-size: 12px; color: #555; font-weight: 500;">{tag}</span>'
            tags_html += '</div>'
            st.markdown(tags_html, unsafe_allow_html=True)
            st.markdown('<div style="border-bottom: 1px solid #e0e0e0; margin-bottom: 24px;"></div>', unsafe_allow_html=True)

        # CORE COMPETENCIES
        if competencies:
            st.markdown('<div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #7f8c8d; margin-bottom: 12px;">CORE COMPETENCIES</div>', unsafe_allow_html=True)
            for comp in competencies:
                if comp:
                    st.markdown(f'<div style="padding: 8px 0; font-size: 13px; color: #555; border-bottom: 1px solid #ecf0f1;">{comp}</div>', unsafe_allow_html=True)
            st.markdown('<div style="border-bottom: 1px solid #e0e0e0; margin: 24px 0;"></div>', unsafe_allow_html=True)

        # KEY METRICS
        metrics = []
        for perf in performance:
            if perf and ("%" in perf or "x" in perf.lower() or "month" in perf.lower() or "week" in perf.lower()):
                import re
                match = re.search(r'(\d+[%xX]?|\d+\+?)', perf)
                if match:
                    metrics.append((match.group(1), perf[:50]))

        if metrics:
            st.markdown('<div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #7f8c8d; margin-bottom: 12px;">KEY METRICS</div>', unsafe_allow_html=True)
            for value, label in metrics[:4]:
                metric_html = f'''
                <div style="background: #f8f9fa; padding: 12px; border-radius: 6px; border-left: 3px solid #27ae60; margin-bottom: 12px;">
                    <div style="font-size: 18px; font-weight: 700; color: #27ae60; margin-bottom: 4px;">{value}</div>
                    <div style="font-size: 11px; color: #7f8c8d; text-transform: uppercase;">{label}</div>
                </div>
                '''
                st.markdown(metric_html, unsafe_allow_html=True)

    # ASK AGY ABOUT THIS
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 20px; color: #555; font-size: 14px;'>💬 Want to know more about this project?</p>", unsafe_allow_html=True)

    _, col_center, _ = st.columns([1.5, 1, 1.5])
    with col_center:
        btn_key = f"ask_from_detail_{key_suffix}_{detail.get('id', 'x')}"
        if st.button("Ask Agy 🐾 About This", key=btn_key, type="primary", use_container_width=True):
            on_ask_this_story(detail)
