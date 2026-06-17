"""
About Matt Page

Professional background, resume, and contact information.
Updated for dark mode compatibility using CSS variables.
"""

import streamlit as st
import streamlit.components.v1 as components

from ui.image_assets import MATT_CARTOON_B64

_ABOUT_HTML = f"""
<div class="about-header">
    <div class="about-header-content">
        <img src="{MATT_CARTOON_B64}"
             class="about-header-avatar"
             alt="Matt Pugmire">
        <div class="about-header-text">
            <h1>Matt Pugmire</h1>
            <p>
                Engineering leader · platform modernization · AI · Atlanta · open to relocate
            </p>
        </div>
    </div>
    <span class="prof-status-badge">● In active conversations</span>
</div>
        """


def render_about_matt():
    """
    Render the About Matt page with professional background and contact info.
    Dark mode compatible using CSS variables.
    """

    # About Matt page CSS lives in ui/styles/global_styles.py (apply_global_styles)
    # so it survives Streamlit position-reconciliation during chip-click transitions
    # (MATTGPT-068). am-* namespace prevents leaking to other pages.
    #
    # Visual language (MATTGPT-093): prof-* classes match wireframe exactly.
    # BDD compat via dual-classing — am-section-title kept on section labels so
    # BDD locators work; prof-section-h !important wins the cascade.

    # =========================================================================
    # 1. HERO SECTION
    # =========================================================================
    st.markdown(_ABOUT_HTML, unsafe_allow_html=True)

    # =========================================================================
    # 2. SIGNALS PANEL (replaces stats bar — MATTGPT-093)
    # BDD: .am-signal-tile count inside [class*='st-key-am_signals_panel'].
    # Dual-class tiles: am-signal-tile (BDD) + prof-signal-tile (visual).
    # Inner labels/values use wireframe class names: prof-signal-lbl/prof-signal-val.
    # =========================================================================

    with st.container(key="am_signals_panel"):
        st.markdown('<p class="prof-section-h">Signals</p>', unsafe_allow_html=True)
        st.markdown(
            '<div class="am-signals-grid prof-signals-grid">'
            '<div class="am-signal-tile prof-signal-tile"><p class="prof-signal-lbl">Level</p><p class="prof-signal-val">Senior leader</p></div>'
            '<div class="am-signal-tile prof-signal-tile"><p class="prof-signal-lbl">Most recent</p><p class="prof-signal-val">Director, Cloud Innovation Center</p></div>'
            '<div class="am-signal-tile prof-signal-tile"><p class="prof-signal-lbl">Peak team</p><p class="prof-signal-val">150+ practitioners</p></div>'
            '<div class="am-signal-tile prof-signal-tile"><p class="prof-signal-lbl">Geo</p><p class="prof-signal-val">Atlanta · open to relocate</p></div>'
            '<div class="am-signal-tile prof-signal-tile"><p class="prof-signal-lbl">Status</p><p class="prof-signal-val">Active conversations</p></div>'
            '<div class="am-signal-tile prof-signal-tile"><p class="prof-signal-lbl">Work mode</p><p class="prof-signal-val">Hybrid or in-person</p></div>'
            "</div>",
            unsafe_allow_html=True,
        )

    # =========================================================================
    # 3. IN MY OWN WORDS — voice block (MATTGPT-093)
    # BDD: .am-section-title (heading text, page-wide), st-key-am_in_my_own_words (content).
    # Section label is <p> not <h2> — matches wireframe; !important in prof-section-h wins.
    # Prose verbatim from wireframe spec — do not paraphrase.
    # =========================================================================
    with st.container(key="am_in_my_own_words"):
        st.markdown(
            '<p class="am-section-title prof-section-h">In my own words</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="prof-voice-p">I build what\'s next, modernize what\'s not, and grow teams along the way.</p>'
            '<p class="prof-voice-p">My foundation is in financial services technology at JPMorgan, Fiserv, RBC, and HSBC. '
            'At JPMorgan I led several programs, the largest a 60+ person global team delivering the ACCESS payments platform '
            'across 12 countries. That\'s where I learned to modernize regulated, high-stakes platforms without breaking them.</p>'
            '<p class="prof-voice-p">Most recently I built Accenture\'s Cloud Innovation Center from zero to a 150+ practitioner '
            'practice of engineers, architects, product managers, and HCD designers, serving 15+ Fortune 500 clients with no '
            'dedicated sales team and generating $100M+ in repeat business. The work itself created the demand.</p>'
            '<p class="prof-voice-p">I used to work in a world where we specified everything upfront and found out at the very end '
            'whether it worked. I work the opposite way now: prototypes in days, a working MVP in weeks, quality built in from '
            'the first commit, with modern engineering and AI tightening the loop. That\'s how a team becomes a system that '
            'delivers, and the people on it do work they\'re proud of.</p>',
            unsafe_allow_html=True,
        )

    # =========================================================================
    # 4. FOR A REFERRER — copy snippet and action buttons (MATTGPT-093)
    # BDD: .am-section-title (heading, page-wide), .am-referrer-snippet (snippet),
    # st-key-am_for_a_referrer (container), buttons by label text inside container.
    # Heading is BEFORE the container so the container IS the info-box (styled via CSS).
    # prof-copy-snippet dual-classes am-referrer-snippet for BDD + white box styling.
    # Snippet verbatim from wireframe spec — do not paraphrase.
    # =========================================================================
    # Inline SVG icons for action buttons (ti-copy / ti-file-download pattern)
    _SVG_COPY = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="8" y="8" width="12" height="12" rx="2"/>'
        '<path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/>'
        '</svg>'
    )
    _SVG_DOWNLOAD = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
        '<polyline points="14,2 14,8 20,8"/>'
        '<line x1="12" y1="18" x2="12" y2="12"/>'
        '<polyline points="9,15 12,18 15,15"/>'
        '</svg>'
    )
    _REFERRER_SNIPPET = (
        "Matt Pugmire is a senior product engineering leader who builds engineering organizations, modernizes platforms, "
        "and grows teams along the way. He has led teams of 60+ across 12 countries, built a practice from zero to "
        "150+ practitioners, and delivered for 15+ Fortune 500 clients across financial services, healthcare, telecom, "
        "and government. In active conversations for senior engineering leadership roles. Atlanta-based, open to relocate."
    )
    with st.container(key="am_for_a_referrer"):
        st.markdown(
            '<p class="am-section-title prof-section-h">For a referrer</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="prof-copy-h">Copy this intro language</p>'
            f'<p class="am-referrer-snippet prof-copy-snippet">{_REFERRER_SNIPPET}</p>'
            f'<div class="prof-copy-actions">'
            f'<span id="am-copy-snippet-btn" class="prof-act-btn">{_SVG_COPY}&nbsp;Copy snippet</span>'
            f'<span id="am-download-pdf-btn" class="prof-act-btn">{_SVG_DOWNLOAD}&nbsp;Download PDF</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # JS wiring: delegated parentDoc listener (MATTGPT-118).
    # Delegated pattern matches how_i_built_dialog.py: listener on parentDoc survives
    # React reconciliation; per-element onclick is lost when React replaces inner DOM.
    # navigator.clipboard.writeText() used over execCommand — works reliably in headless
    # Chromium; both .then() and .catch() show ✓ Copied! so clipboard success is not
    # required for the confirmation feedback.
    _snippet_js_literal = repr(_REFERRER_SNIPPET)
    components.html(
        f"""
<script>
(function() {{
    var parentDoc = window.parent.document;
    var snippetText = {_snippet_js_literal};
    parentDoc.addEventListener('click', function(e) {{
        var copyBtn = e.target.closest ? e.target.closest('#am-copy-snippet-btn') : null;
        if (copyBtn) {{
            e.preventDefault();
            var origHTML = copyBtn.innerHTML;
            var showConfirm = function() {{
                copyBtn.innerHTML = '✓ Copied!';
                copyBtn.style.borderColor = '#10B981';
                copyBtn.style.color = '#10B981';
                setTimeout(function() {{
                    copyBtn.innerHTML = origHTML;
                    copyBtn.style.borderColor = '';
                    copyBtn.style.color = '';
                }}, 2000);
            }};
            window.parent.navigator.clipboard.writeText(snippetText).then(showConfirm).catch(showConfirm);
            return;
        }}
        var dlBtn = e.target.closest ? e.target.closest('#am-download-pdf-btn') : null;
        if (dlBtn) {{
            var stBtn = parentDoc.querySelector('[class*="st-key-am_download_pdf"] button');
            if (stBtn) stBtn.click();
        }}
    }});
}})();
</script>
""",
        height=0,
    )

    if st.button("", key="am_download_pdf"):
        _export_html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<title>Matt Pugmire</title><style>"
            "body{font-family:Arial,sans-serif;max-width:740px;margin:40px auto;color:#1F2937;font-size:14px;line-height:1.6}"
            "h1{font-size:24px;margin:0 0 4px;font-weight:700}"
            ".sub{color:#6B7280;font-size:12px;margin:0 0 28px}"
            "h2{font-size:10px;text-transform:uppercase;letter-spacing:.6px;color:#6B7280;margin:24px 0 10px;font-weight:700;border-bottom:1px solid #E5E7EB;padding-bottom:4px}"
            ".signals{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:0 0 4px}"
            ".tile{background:#F9FAFB;border-radius:6px;padding:8px 12px}"
            ".tile-lbl{font-size:10px;text-transform:uppercase;letter-spacing:.4px;color:#6B7280;margin:0 0 2px}"
            ".tile-val{font-size:13px;font-weight:500;margin:0}"
            "p.voice{font-size:13px;color:#374151;margin:0 0 10px;line-height:1.65}"
            "p.voice:last-child{margin:0}"
            ".comp-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:0 0 4px}"
            ".comp-card{background:#F9FAFB;border-radius:6px;padding:8px 12px}"
            ".comp-name{font-size:12px;font-weight:600;margin:0 0 3px}"
            ".comp-desc{font-size:11px;color:#6B7280;margin:0;line-height:1.4}"
            ".lead-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin:0 0 4px}"
            ".lead-card{background:#F9FAFB;border-radius:6px;padding:8px 12px}"
            ".lead-h{font-size:12px;font-weight:600;margin:0 0 3px;color:#8B5CF6}"
            ".lead-p{font-size:11px;color:#6B7280;margin:0;line-height:1.4}"
            ".tl{border-left:2px solid #E5E7EB;padding-left:16px;margin:0 0 4px}"
            ".tl-item{margin-bottom:12px;position:relative}"
            ".tl-item::before{content:'';position:absolute;left:-21px;top:4px;width:8px;height:8px;border-radius:50%;background:#8B5CF6}"
            ".tl-period{font-size:11px;color:#8B5CF6;font-weight:600;margin:0}"
            ".tl-role{font-size:13px;font-weight:500;margin:2px 0 1px}"
            ".tl-org{font-size:11px;color:#6B7280;margin:0 0 2px}"
            ".tl-desc{font-size:11px;color:#374151;margin:0;line-height:1.45}"
            ".footer{margin-top:32px;padding-top:12px;border-top:1px solid #E5E7EB;font-size:11px;color:#6B7280;text-align:center}"
            "@media print{body{margin:20px}}"
            "</style></head><body>"
            "<h1>Matt Pugmire</h1>"
            "<p class='sub'>Engineering leader &middot; builds organizations from zero &middot; platform modernization &middot; AI &middot; Atlanta &middot; open to relocate</p>"
            "<h2>Signals</h2><div class='signals'>"
            "<div class='tile'><p class='tile-lbl'>Level</p><p class='tile-val'>Senior leader</p></div>"
            "<div class='tile'><p class='tile-lbl'>Most recent</p><p class='tile-val'>Director, Cloud Innovation Center</p></div>"
            "<div class='tile'><p class='tile-lbl'>Peak team</p><p class='tile-val'>150+ practitioners</p></div>"
            "<div class='tile'><p class='tile-lbl'>Geo</p><p class='tile-val'>Atlanta &middot; open to relocate</p></div>"
            "<div class='tile'><p class='tile-lbl'>Status</p><p class='tile-val'>Active conversations</p></div>"
            "<div class='tile'><p class='tile-lbl'>Work mode</p><p class='tile-val'>Hybrid or in-person</p></div>"
            "</div>"
            "<h2>In My Own Words</h2>"
            "<p class='voice'>I build what&#39;s next, modernize what&#39;s not, and grow teams along the way.</p>"
            "<p class='voice'>My foundation is in financial services technology at JPMorgan, Fiserv, RBC, and HSBC. "
            "At JPMorgan I led several programs, the largest a 60+ person global team delivering the ACCESS payments platform "
            "across 12 countries. That&#39;s where I learned to modernize regulated, high-stakes platforms without breaking them.</p>"
            "<p class='voice'>Most recently I built Accenture&#39;s Cloud Innovation Center from zero to a 150+ practitioner "
            "practice of engineers, architects, product managers, and HCD designers, serving 15+ Fortune 500 clients with no "
            "dedicated sales team and generating $100M+ in repeat business. The work itself created the demand.</p>"
            "<p class='voice'>I used to work in a world where we specified everything upfront and found out at the very end "
            "whether it worked. I work the opposite way now: prototypes in days, a working MVP in weeks, quality built in from "
            "the first commit, with modern engineering and AI tightening the loop. That&#39;s how a team becomes a system that "
            "delivers, and the people on it do work they&#39;re proud of.</p>"
            "<h2>Core Competencies</h2><div class='comp-grid'>"
            "<div class='comp-card'><p class='comp-name'>Product &amp; Discovery</p><p class='comp-desc'>Discovery, framing, and prototyping that settle what to build before the build starts.</p></div>"
            "<div class='comp-card'><p class='comp-name'>Modern Engineering</p><p class='comp-desc'>Cloud-native and event-driven, quality engineered in from the first commit. TDD, pair programming, CI/CD.</p></div>"
            "<div class='comp-card'><p class='comp-name'>Organization Building</p><p class='comp-desc'>Engineering organizations and the operating model that scales them. Team Topologies, delivery rhythm, practices that outlast the org chart.</p></div>"
            "<div class='comp-card'><p class='comp-name'>Enterprise Transformation</p><p class='comp-desc'>Regulated enterprises moved from IT delivery to a product operating model, and the change holds.</p></div>"
            "<div class='comp-card'><p class='comp-name'>People &amp; Culture</p><p class='comp-desc'>Cross-functional teams built from zero, plus the reskilling and mentorship that keep them growing.</p></div>"
            "<div class='comp-card'><p class='comp-name'>AI &amp; Emerging Tech</p><p class='comp-desc'>RAG, vector search, and eval-driven development, built hands-on.</p></div>"
            "</div>"
            "<h2>How I Lead</h2><div class='lead-grid'>"
            "<div class='lead-card'><p class='lead-h'>Outcomes over output</p><p class='lead-p'>I measure a team by what it changes, not how much it produces.</p></div>"
            "<div class='lead-card'><p class='lead-h'>Experimentation over certainty</p><p class='lead-p'>I trust what a prototype teaches me over what a plan promises.</p></div>"
            "<div class='lead-card'><p class='lead-h'>High-trust, sustainable teams</p><p class='lead-p'>I build teams where ten people do what twenty usually do, and can still do it next quarter.</p></div>"
            "<div class='lead-card'><p class='lead-h'>Grow the people</p><p class='lead-p'>I develop people with the same discipline I bring to building systems.</p></div>"
            "</div>"
            "<h2>Career Evolution</h2><div class='tl'>"
            "<div class='tl-item'><p class='tl-period'>2023&#8211;2026</p><p class='tl-role'>Sabbatical | Innovation &amp; Upskilling</p><p class='tl-org'>Independent</p><p class='tl-desc'>Sabbatical to recharge, refocus, and reskill. MattGPT is tangible proof of the work.</p></div>"
            "<div class='tl-item'><p class='tl-period'>2019&#8211;2023</p><p class='tl-role'>Director, Cloud Innovation Center</p><p class='tl-org'>Accenture</p><p class='tl-desc'>Launched Innovation Centers (150+ practitioners) &#183; 30+ products &#183; $100M+ in repeat business &#183; 4x faster delivery.</p></div>"
            "<div class='tl-item'><p class='tl-period'>2016&#8211;2023</p><p class='tl-role'>Capability Development Lead, CloudFirst</p><p class='tl-org'>Accenture</p><p class='tl-desc'>Enterprise capability development, engineering enablement, and culture transformation.</p></div>"
            "<div class='tl-item'><p class='tl-period'>2018&#8211;2019</p><p class='tl-role'>Cloud Native Architecture Lead, Liquid Studio</p><p class='tl-org'>Accenture</p><p class='tl-desc'>Cloud-native prototyping and product shaping through rapid experimentation and modern engineering practices.</p></div>"
            "<div class='tl-item'><p class='tl-period'>2009&#8211;2017</p><p class='tl-role'>Sr. Technology Architecture Manager, Financial Services</p><p class='tl-org'>Accenture</p><p class='tl-desc'>Financial services platform modernization and architecture at global scale.</p></div>"
            "<div class='tl-item'><p class='tl-period'>2005&#8211;2009</p><p class='tl-role'>Technology Manager</p><p class='tl-org'>Accenture</p><p class='tl-desc'>Enterprise integration and solution architecture for large-scale telecom and enterprise platforms.</p></div>"
            "<div class='tl-item'><p class='tl-period'>2000&#8211;2005</p><p class='tl-role'>Startups &amp; Consulting</p><p class='tl-org'>Cendian Corporation &#183; Wellfound Technology</p><p class='tl-desc'>Building B2B and supply-chain platforms using enterprise integration technologies.</p></div>"
            "</div>"
            "<div class='footer'>For the full resume, reach out: matthew.c.pugmire+MattGPT@gmail.com | linkedin.com/in/matt-pugmire</div>"
            "</body></html>"
        )
        _escaped_doc = _export_html.replace("\\", "\\\\").replace("`", "\\`")
        components.html(
            f"""
            <script>
                var printWindow = window.open('', '_blank');
                printWindow.document.write(`{_escaped_doc}`);
                printWindow.document.close();
                printWindow.print();
            </script>
            """,
            height=0,
        )

    # =========================================================================
    # 5. CORE COMPETENCIES (MATTGPT-093: "Agile at Scale" -> "Product delivery at scale")
    # BDD: .competencies-grid .competency-card h4 (heading text).
    # Dual-class grid + cards; h4 kept for BDD, prof-comp-name class styles it.
    # prof-comp-desc replaces old bullet lists.
    # No subtitle — wireframe has none.
    # =========================================================================
    with st.container(key="am_competencies"):
        st.markdown(
            '<p class="am-section-title prof-section-h">Core Competencies</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
<div class="competencies-grid prof-comp-grid">
    <div class="competency-card prof-comp-card">
        <h4 class="prof-comp-name">Product &amp; Discovery</h4>
        <p class="prof-comp-desc">Discovery, framing, and prototyping that settle what to build before the build starts.</p>
    </div>
    <div class="competency-card prof-comp-card">
        <h4 class="prof-comp-name">Modern Engineering</h4>
        <p class="prof-comp-desc">Cloud-native and event-driven, quality engineered in from the first commit. TDD, pair programming, CI/CD.</p>
    </div>
    <div class="competency-card prof-comp-card">
        <h4 class="prof-comp-name">Organization Building</h4>
        <p class="prof-comp-desc">Engineering organizations and the operating model that scales them. Team Topologies, delivery rhythm, practices that outlast the org chart.</p>
    </div>
    <div class="competency-card prof-comp-card">
        <h4 class="prof-comp-name">Enterprise Transformation</h4>
        <p class="prof-comp-desc">Regulated enterprises moved from IT delivery to a product operating model, and the change holds.</p>
    </div>
    <div class="competency-card prof-comp-card">
        <h4 class="prof-comp-name">People &amp; Culture</h4>
        <p class="prof-comp-desc">Cross-functional teams built from zero, plus the reskilling and mentorship that keep them growing.</p>
    </div>
    <div class="competency-card prof-comp-card">
        <h4 class="prof-comp-name">AI &amp; Emerging Tech</h4>
        <p class="prof-comp-desc">RAG, vector search, and eval-driven development, built hands-on.</p>
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    # =========================================================================
    # 6. HOW I LEAD (MATTGPT-093: "Leadership Philosophy" -> "How I Lead",
    #    4 locked value/claim pairs; no subtitle — wireframe has none)
    # BDD: .am-section-title (heading), .philosophy-grid inner_text (card content).
    # Grid: philosophy-grid (BDD) + prof-philosophy (visual, wireframe class).
    # Cards: prof-phil-card. Content: prof-phil-h + prof-phil-p (<p> tags per wireframe).
    # =========================================================================
    with st.container(key="am_how_i_lead"):
        st.markdown(
            '<p class="am-section-title prof-section-h">How I Lead</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
<div class="philosophy-grid prof-philosophy">
    <div class="prof-phil-card">
        <p class="prof-phil-h">Outcomes over output</p>
        <p class="prof-phil-p">I measure a team by what it changes, not how much it produces.</p>
    </div>
    <div class="prof-phil-card">
        <p class="prof-phil-h">Experimentation over certainty</p>
        <p class="prof-phil-p">I trust what a prototype teaches me over what a plan promises.</p>
    </div>
    <div class="prof-phil-card">
        <p class="prof-phil-h">High-trust, sustainable teams</p>
        <p class="prof-phil-p">I build teams where ten people do what twenty usually do, and can still do it next quarter.</p>
    </div>
    <div class="prof-phil-card">
        <p class="prof-phil-h">Grow the people</p>
        <p class="prof-phil-p">I develop people with the same discipline I bring to building systems.</p>
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    # =========================================================================
    # 7. CAREER TIMELINE (MATTGPT-093)
    # BDD: .timeline .timeline-item (count=7), .timeline .timeline-year (period text),
    # .timeline inner_text (Cendian/Wellfound/Liquid Studio/2023-2026 checks).
    # Dual-class outer (timeline + prof-timeline) and items (timeline-item + prof-timeline-item).
    # Period uses dual-class (timeline-year + prof-timeline-period); rest wireframe only.
    # No subtitle — wireframe has none.
    # Intentional divergence from wireframe: 7 entries vs 4. See CLAUDE.md.
    # =========================================================================
    with st.container(key="am_career_evolution"):
        st.markdown(
            '<p class="am-section-title prof-section-h">Career Evolution</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
<div class="timeline prof-timeline">
    <div class="timeline-item prof-timeline-item">
        <p class="timeline-year prof-timeline-period">2023–2026</p>
        <p class="prof-timeline-role">Sabbatical | Innovation &amp; Upskilling</p>
        <p class="prof-timeline-org">Independent</p>
        <p class="prof-timeline-desc">Sabbatical to recharge, refocus, and reskill. MattGPT is tangible proof of the work.</p>
    </div>
    <div class="timeline-item prof-timeline-item">
        <p class="timeline-year prof-timeline-period">2019–2023</p>
        <p class="prof-timeline-role">Director, Cloud Innovation Center</p>
        <p class="prof-timeline-org">Accenture</p>
        <p class="prof-timeline-desc">Launched Innovation Centers (150+ practitioners) • 30+ products • $100M+ in repeat business • 4x faster delivery.</p>
    </div>
    <div class="timeline-item prof-timeline-item">
        <p class="timeline-year prof-timeline-period">2016–2023</p>
        <p class="prof-timeline-role">Capability Development Lead, CloudFirst</p>
        <p class="prof-timeline-org">Accenture</p>
        <p class="prof-timeline-desc">Enterprise capability development, engineering enablement, and culture transformation.</p>
    </div>
    <div class="timeline-item prof-timeline-item">
        <p class="timeline-year prof-timeline-period">2018–2019</p>
        <p class="prof-timeline-role">Cloud Native Architecture Lead, Liquid Studio</p>
        <p class="prof-timeline-org">Accenture</p>
        <p class="prof-timeline-desc">Cloud-native prototyping and product shaping through rapid experimentation and modern engineering practices.</p>
    </div>
    <div class="timeline-item prof-timeline-item">
        <p class="timeline-year prof-timeline-period">2009–2017</p>
        <p class="prof-timeline-role">Sr. Technology Architecture Manager, Financial Services</p>
        <p class="prof-timeline-org">Accenture</p>
        <p class="prof-timeline-desc">Financial services platform modernization and architecture at global scale.</p>
    </div>
    <div class="timeline-item prof-timeline-item">
        <p class="timeline-year prof-timeline-period">2005–2009</p>
        <p class="prof-timeline-role">Technology Manager</p>
        <p class="prof-timeline-org">Accenture</p>
        <p class="prof-timeline-desc">Enterprise integration and solution architecture for large-scale telecom and enterprise platforms.</p>
    </div>
    <div class="timeline-item prof-timeline-item">
        <p class="timeline-year prof-timeline-period">2000–2005</p>
        <p class="prof-timeline-role">Startups &amp; Consulting</p>
        <p class="prof-timeline-org">Cendian Corporation · Wellfound Technology</p>
        <p class="prof-timeline-desc">Building B2B and supply-chain platforms using enterprise integration technologies.</p>
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    # =========================================================================
    # FOOTER (imported from shared component)
    # =========================================================================
    from ui.components.footer import render_footer

    render_footer()
