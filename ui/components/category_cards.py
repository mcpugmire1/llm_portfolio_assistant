"""
Category Cards Component

Homepage exploration cards for different portfolio categories.
Includes gradient industry cards and white capability cards.
Uses HTML buttons with JS triggers for consistent styling across themes.
Counts are derived dynamically from JSONL data.

MOBILE CSS: Card heights are handled here. Layout/spacing handled by mobile_overrides.py
"""

from collections import Counter

import streamlit as st

from utils.client_utils import is_generic_client

# Ask Agy Anything suggested-question chip strings. Order is load-bearing —
# index N maps to the hidden Streamlit button card_btn_ask_chip_N and to the
# visible HTML button.chip in DOM order. The chip-click handler reads from
# this list by index.
#
# SINGLE-CONTRACT TRIPLE: these strings appear in three test files. If they
# change here, update ALL THREE in lockstep:
#   - tests/bdd/features/home.feature (scenario text)
#   - tests/bdd/steps/test_home.py CHIP_QUESTIONS
#   - tests/eval_rag_quality.py GOLDEN_QUERIES["narrative"] entries 62-64
# Out-of-sync edits break either the BDD wiring or the eval quality pinning.
_CHIP_QUESTIONS = [
    "How did Matt scale a Cloud Innovation Center from 0 to 150+ engineers?",
    "How does Matt build teams that ship like startups in enterprise?",
    "How does Matt manage resistance when leading enterprise transformation programs?",
]


def on_chip_click(question: str) -> None:
    """Handle a suggested-question chip click on the Ask Agy Anything card.

    Mirrors ui/components/story_detail.py::on_ask_this_story exactly, minus
    the story-specific keys (active_story / active_story_obj) — those would
    wrongly anchor the response to a single story when the chip questions
    are intentionally broad.

    Sets the three session-state keys that conversation_view.py:165 reads
    and pops to auto-fire the query:
      - seed_prompt: the literal question string (rendered as the user's
        first turn in the chat transcript)
      - __ask_from_suggestion__: True — tells backend_service.py:1413 to
        bypass the nonsense filter (otherwise "How does Matt..." style
        queries can get redirected)
      - active_tab: "Ask Agy" — routes the rerun to the chat page

    Contract pinned by tests/unit/test_category_cards.py::TestOnChipClick.
    """
    st.session_state["seed_prompt"] = question
    st.session_state["__ask_from_suggestion__"] = True
    st.session_state["active_tab"] = "Ask Agy"
    st.rerun()


def render_category_cards(stories: list[dict]):
    """Render homepage category cards grid - responsive with CSS Grid.

    Args:
        stories: Full story corpus from JSONL.
    """
    # === DYNAMIC COUNTS (derived from JSONL) ===
    banking_stories = [
        s for s in stories if s.get("Industry") == "Financial Services / Banking"
    ]
    cross_industry_stories = [
        s for s in stories if s.get("Industry") == "Cross Industry"
    ]

    # Banking client counts (top 3, excluding generic)
    banking_clients = Counter(
        s.get("Client", "Unknown")
        for s in banking_stories
        if not is_generic_client(s.get("Client"))
    )
    top_banking_clients = banking_clients.most_common(3)

    # Cross-industry: show Accenture and telecom clients
    telecom_stories = [s for s in stories if s.get("Industry") == "Telecommunications"]
    accenture_stories = [s for s in stories if s.get("Client") == "Accenture"]

    # === END DYNAMIC COUNTS ===

    # Inject card and button styles
    st.markdown(
        """
    <style>
    /* === CARD BUTTON STYLES === */

    /* Buttons inside purple gradient cards */
    .card-btn-gradient {
        display: inline-block;
        padding: 12px 24px;
        background: rgba(255, 255, 255, 0.2);
        border: 2px solid rgba(255, 255, 255, 0.4);
        border-radius: 8px;
        color: white !important;
        font-weight: 600;
        font-size: 14px;
        text-decoration: none !important;
        cursor: pointer;
        transition: all 0.2s ease;
        backdrop-filter: blur(4px);
    }

    .card-btn-gradient:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.6);
        transform: translateY(-2px);
        text-decoration: none !important;
    }

    /* Buttons inside capability cards (theme-aware) */
    .card-btn-outline {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background: var(--bg-surface);
        border: 2px solid var(--border-color);
        border-radius: 6px;
        color: var(--accent-purple) !important;
        font-weight: 600;
        font-size: 13px;
        text-decoration: none !important;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .card-btn-outline:hover {
        background: var(--accent-purple);
        border-color: var(--accent-purple);
        color: white !important;
        text-decoration: none !important;
    }

    /* Ask Agy button - always purple filled */
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

    /* MATTGPT-107: Collapse stElementContainer wrappers whose markdown
       holds only a <style> tag. Streamlit wraps every st.markdown call in
       an stElementContainer regardless of whether the content is visible,
       and the wrapper takes part in stVerticalBlock spacing. Between
       render_section_title's <h2> and this component's cards grid, the
       CSS-injection stElementContainer below contributed ~55px of phantom
       vertical gap. The rule below applies globally to the document so it
       benefits any style-only injection on Home — including the one this
       rule itself lives in (CSS rules in a <style> tag still take effect
       even when an ancestor is display:none, so the self-hide is fine). */
    div[data-testid="stElementContainer"]:has(> div[data-testid="stMarkdown"] > div[data-testid="stMarkdownContainer"] > style:only-child) {
        display: none !important;
    }
    /* Empty stMarkdownContainer (e.g., a markdown call that produced no
       output after parsing). Saves ~56px in the panel-to-footer region
       on the home page where intermediate empty containers stacked. */
    div[data-testid="stElementContainer"]:has(> div[data-testid="stMarkdown"] > div[data-testid="stMarkdownContainer"]:empty) {
        display: none !important;
    }
    /* Truly-empty stElementContainer (no markdown child at all). Covers
       the edge case where Streamlit emitted a wrapper with no body. */
    div[data-testid="stElementContainer"]:empty {
        display: none !important;
    }

    /* === MATTGPT-107: Home category cards (3-col grid, unified treatment) ===
       Wireframe-locked values from MATTGPT_WIREFRAMES.html lines 77-82.
       Replaces the legacy 2-col Streamlit-columns layout (matt-container +
       .capability-card / inline anchor buttons + .hints). Whole-card click
       handled by the components.html JS bridge below (listens on the card
       id="card-X" divs and dispatches to hidden Streamlit buttons whose
       active_tab / prefilter_* routing logic is unchanged from production). */
    .home-cat-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        padding: 0 24px 18px;
    }
    .home-cat-card {
        background: var(--bg-surface);
        border: 0.5px solid var(--border-color);
        border-radius: 6px;
        padding: 14px;
        cursor: pointer;
        transition: border-color 0.15s ease, transform 0.15s ease;
        display: flex;
        flex-direction: column;
        color: var(--text-primary);
    }
    .home-cat-card:hover {
        border-color: var(--text-secondary);
        transform: translateY(-1px);
    }
    .home-cat-icon {
        font-size: 18px;
        line-height: 1;
        margin-bottom: 6px;
    }
    .home-cat-title {
        font-size: 12px;
        font-weight: 500;
        margin: 0 0 3px 0;
        color: var(--text-primary);
    }
    .home-cat-meta {
        font-size: 11px;
        color: var(--text-secondary);
        margin: 0;
        line-height: 1.5;
    }
    @media (max-width: 1024px) {
        .home-cat-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 640px) {
        .home-cat-grid { grid-template-columns: 1fr; padding: 0 16px 24px; }
        .home-cat-card { padding: 12px; }
    }

    /* Capability card container (theme-aware) */
    .capability-card {
        background: var(--bg-card);
        color: var(--text-primary);
        padding: 32px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        height: 320px;
        display: flex;
        flex-direction: column;
    }

    .capability-card h3 {
        color: var(--text-heading);
        font-size: 20px;
        font-weight: 700;
        margin: 0 0 12px 0;
    }

    .capability-card .description {
        color: var(--text-secondary);
        margin-bottom: 16px;
        line-height: 1.6;
        font-size: 15px;
        flex-grow: 1;
    }

    .capability-card .hints {
        color: var(--text-muted);
        font-style: italic;
        font-size: 14px;
        line-height: 1.5;
        margin-bottom: 16px;
    }

    .capability-card .highlight {
        color: var(--accent-purple);
        font-weight: 600;
        margin-bottom: 12px;
        font-size: 15px;
    }

    /* Hide the trigger buttons */
    [class*="st-key-card_btn_"] {
        display: none !important;
    }

    /* ========================================
       MOBILE: COMPACT CARDS
       ======================================== */
    @media (max-width: 767px) {
        /* Purple gradient cards - compact */
        div[style*="background: var(--gradient-purple-hero)"] {
            height: auto !important;
            min-height: 0 !important;
            padding: 20px !important;
        }
        div[style*="background: var(--gradient-purple-hero)"] > div:first-child {
            font-size: 32px !important;
            margin-bottom: 10px !important;
        }
        div[style*="background: var(--gradient-purple-hero)"] h3 {
            font-size: 18px !important;
            margin-bottom: 6px !important;
        }
        div[style*="background: var(--gradient-purple-hero)"] > div[style*="font-size: 16px"] {
            font-size: 14px !important;
            margin-bottom: 10px !important;
        }
        div[style*="background: var(--gradient-purple-hero)"] > div[style*="line-height: 1.5"] {
            font-size: 13px !important;
            margin-bottom: 10px !important;
        }
        div[style*="background: var(--gradient-purple-hero)"] > div[style*="flex-wrap: wrap"] {
            margin-bottom: 12px !important;
        }
        div[style*="background: var(--gradient-purple-hero)"] span[style*="border-radius: 12px"] {
            font-size: 10px !important;
            padding: 3px 8px !important;
        }
        .card-btn-gradient {
            padding: 10px 18px !important;
            font-size: 13px !important;
        }

        /* Capability cards - compact */
        .capability-card {
            height: auto !important;
            min-height: 0 !important;
            padding: 16px !important;
        }
        .capability-card h3 {
            font-size: 16px !important;
            margin-bottom: 8px !important;
        }
        .capability-card .description {
            font-size: 13px !important;
            margin-bottom: 10px !important;
        }
        .capability-card .hints {
            font-size: 12px !important;
            margin-bottom: 10px !important;
        }
        .capability-card .highlight {
            font-size: 13px !important;
            margin-bottom: 8px !important;
        }
        .card-btn-outline {
            padding: 6px 12px !important;
            font-size: 12px !important;
        }

        /* Fix Streamlit column heights */
        .stColumn {
            width: 100% !important;
        }
        .stColumn .stVerticalBlock {
            height: auto !important;
        }
        .stHorizontalBlock {
            flex-wrap: wrap !important;
            gap: 0 !important;
        }
        .card-mobile-spacing {
            margin-bottom: 12px !important;
        }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # === MATTGPT-107: Six category cards in a single 3-col CSS grid ===
    # Whole-card click target: each card div has id="card-X". The JS bridge
    # in the components.html block below listens for clicks on these IDs
    # and dispatches to the hidden Streamlit buttons further down, whose
    # active_tab / prefilter_* routing logic is unchanged from production.
    # -107 is visual-only redesign; routing model is out of scope.
    #
    # Card-meta lines:
    #   1, 2 — dynamic project counts + top-client names from JSONL
    #   3-6  — wireframe-locked descriptive copy (no inline button, no
    #          italic example-question line; the whole card is the click).
    banking_clients_inline = (
        ", ".join(name for name, _ in top_banking_clients) or "JP Morgan, RBC, Fiserv"
    )
    cross_industry_segments = []
    if telecom_stories:
        cross_industry_segments.append("Telecom")
    if accenture_stories:
        cross_industry_segments.append("Accenture")
    cross_industry_inline = ", ".join(cross_industry_segments) or "Telecom, Accenture"

    cards_html = f"""
<div class="matt-container">
<div class="home-cat-grid">
<div class="home-cat-card" id="card-banking">
<div class="home-cat-icon">🏦</div>
<p class="home-cat-title">Financial Services / Banking</p>
<p class="home-cat-meta">{len(banking_stories)} projects · {banking_clients_inline}</p>
</div>
<div class="home-cat-card" id="card-cross-industry">
<div class="home-cat-icon">🌐</div>
<p class="home-cat-title">Cross-Industry Transformation</p>
<p class="home-cat-meta">{len(cross_industry_stories)} projects · {cross_industry_inline}</p>
</div>
<div class="home-cat-card" id="card-product">
<div class="home-cat-icon">🚀</div>
<p class="home-cat-title">Product Innovation &amp; Strategy</p>
<p class="home-cat-meta">Cloud-native prototypes to enterprise platforms that transform businesses</p>
</div>
<div class="home-cat-card" id="card-modernization">
<div class="home-cat-icon">⚙️</div>
<p class="home-cat-title">Application Modernization</p>
<p class="home-cat-meta">Event-driven design, microservices, zero-defect delivery</p>
</div>
<div class="home-cat-card" id="card-consulting">
<div class="home-cat-icon">💡</div>
<p class="home-cat-title">Consulting &amp; Transformation</p>
<p class="home-cat-meta">Fortune 500 advisory, operating models, 3-20x acceleration</p>
</div>
<div class="home-cat-card" id="card-teams">
<div class="home-cat-icon">👥</div>
<p class="home-cat-title">Teams &amp; Talent Development</p>
<p class="home-cat-meta">Innovation centers, servant leadership, upskilling programs</p>
</div>
</div>
</div>
"""
    st.markdown(cards_html, unsafe_allow_html=True)

    # Hidden Streamlit buttons — same keys + routing logic as pre-MATTGPT-107.
    # The JS bridge below maps clicks on .home-cat-card[id="card-X"] divs to
    # these via querySelector on [class*="st-key-card_btn_X"] button.
    if st.button("", key="card_btn_banking"):
        st.session_state["active_tab"] = "Banking"
        st.rerun()

    if st.button("", key="card_btn_cross_industry"):
        st.session_state["active_tab"] = "Cross-Industry"
        st.rerun()

    if st.button("", key="card_btn_product"):
        if st.session_state.get("active_tab") == "Home":
            # Switched from prefilter_capability="Product Leadership" (not a valid
            # Solution/Offering value, silently sanitized to "All" → 113 unfiltered).
            # See BACKLOG MATTGPT-060 for the BDD gap that let this ship.
            st.session_state["prefilter_domains"] = [
                "User-Centered Product Strategy & Innovation",
                "Product Strategy & Innovation",
                "Product Management",
                "Digital Product Development & Delivery",
                "Client Product Innovation & Co-Creation",
            ]
            st.session_state["active_tab"] = "My Work"
            st.rerun()

    if st.button("", key="card_btn_modernization"):
        if st.session_state.get("active_tab") == "Home":
            st.session_state["prefilter_capability"] = "Application Modernization"
            st.session_state["active_tab"] = "My Work"
            st.rerun()

    if st.button("", key="card_btn_consulting"):
        if st.session_state.get("active_tab") == "Home":
            # Trimmed from 18 → 8 domains. Product-related domains moved to
            # Card 3 (Product Innovation); 1-story long-tail dropped to reduce
            # filter-chip noise. ~29 stories covered (vs 43 prior).
            st.session_state["prefilter_domains"] = [
                "Agile Planning & Value-Driven Delivery",
                "Leadership & Continuous Improvement",
                "Agile Transformation & Leadership Enablement",
                "Technology Strategy & Advisory Services",
                "Strategic Client Partnerships",
                "Cross-Functional Collaboration & Alignment",
                "Process Optimization & Automation",
                "Security & Compliance Solutions",
            ]
            st.session_state["active_tab"] = "My Work"
            st.rerun()

    if st.button("", key="card_btn_teams"):
        if st.session_state.get("active_tab") == "Home":
            st.session_state["prefilter_domains"] = [
                "Client Upskilling & Enablement",
                "Cross-Functional Team Enablement",
                "Psychological Safety & Innovation Culture",
                "Talent Enablement & Growth",
            ]
            st.session_state["active_tab"] = "My Work"
            st.rerun()

    # Row spacing (hidden on mobile via CSS)
    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)

    # === ROW 4: Ask Agy Anything card (two-column with suggested chips) ===
    # Layout: left column has the Agy avatar/header/body/primary CTA; right
    # column has the "Try asking" label and three clickable chip buttons.
    # Chip CSS includes a ::before { content: '↗' } affordance pinned by the
    # test_chips_render_with_arrow BDD scenario.
    st.markdown(
        """
    <style>
    .ask-agy-card {
        background: var(--gradient-purple-hero);
        color: white;
        padding: 28px 56px 32px 56px;
        border-radius: 12px;
        margin-top: 8px;
    }
    /* MATTGPT-107: kill the phantom Streamlit anchor padding inside the
       ask-agy-card heading. Same pattern as the section-header tighten
       in hero.py — the <h3> Streamlit wraps with stHeadingWithActionElements
       picks up 12px top + 16px bottom anchor padding by default, plus a
       hover anchor-icon that's irrelevant inside a styled panel. */
    .ask-agy-card .ask-agy-title {
        padding: 0 !important;
    }
    .ask-agy-card [data-testid="stHeadingWithActionElements"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    .ask-agy-card [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    .ask-agy-grid {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        align-items: stretch;
        gap: 0;
    }
    .ask-agy-left {
        padding-right: 44px;
        display: flex;
        flex-direction: column;
    }
    .ask-agy-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 14px;
    }
    .ask-agy-avatar {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        border: 3px solid white;
        flex-shrink: 0;
        overflow: hidden;
    }
    .ask-agy-avatar img { width: 100%; height: 100%; object-fit: cover; }
    .ask-agy-title {
        font-size: 28px;
        font-weight: 700;
        color: white;
        line-height: 1.2;
        margin: 0;
    }
    .ask-agy-body {
        font-size: 15px;
        line-height: 1.65;
        color: rgba(255,255,255,0.88);
        margin-bottom: 24px;
        flex: 1;
    }
    .ask-agy-divider {
        width: 1px;
        background: rgba(255,255,255,0.2);
        margin: 0 8px;
        align-self: stretch;
    }
    .ask-agy-right {
        padding-left: 44px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 10px;
    }
    .ask-agy-try-label {
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: rgba(255,255,255,1.0);
        margin-bottom: 4px;
    }
    /* MATTGPT-107: chip styling matched to the hero secondary CTA
       (.cta-secondary in hero.py) — solid 2px white border + 0.2 bg +
       weight 600 — so the "Try asking" chips read as clickable objects
       and the design language stays consistent across the
       "interact with Agy" surfaces (hero CTA + Ask Agy panel chips). */
    .chip {
        background: rgba(255,255,255,0.2);
        border: 2px solid rgb(255,255,255);
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 14px;
        font-weight: 600;
        color: white;
        text-align: left;
        cursor: pointer;
        transition: background 0.15s;
        line-height: 1.4;
        font-family: inherit;
        width: 100%;
    }
    .chip:hover {
        background: rgba(255,255,255,0.3);
    }
    .chip::before {
        content: '↗';
        float: right;
        opacity: 1.0;
        margin-left: 8px;
        font-size: 12px;
    }
    /* Mobile: stack columns, drop divider. */
    @media (max-width: 768px) {
        .ask-agy-grid { grid-template-columns: 1fr; }
        .ask-agy-left { padding-right: 0; }
        .ask-agy-right { padding-left: 0; padding-top: 24px; }
        .ask-agy-divider { display: none; }
    }
    /* Hide the placeholder Streamlit buttons (the visible chips/anchor
       handle the user-facing click; these hidden buttons are the actual
       click receivers bridged via JS). */
    [class*="st-key-card_btn_ask_agy"] button,
    [class*="st-key-card_btn_ask_chip_"] button {
        position: absolute !important;
        left: -9999px !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
    }
    </style>
    <div class="ask-agy-card">
      <div class="ask-agy-grid">
        <div class="ask-agy-left">
          <div class="ask-agy-header">
            <div class="ask-agy-avatar">
              <img src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_ask_mattgpt.png" alt="Agy">
            </div>
            <h3 class="ask-agy-title">Ask Agy 🐾 Anything</h3>
          </div>
          <div class="ask-agy-body">
            From building MattGPT to leading global programs, Agy is trained on every project Matt has delivered. Ask him anything, he'll track it down.
          </div>
          <a id="btn-ask-agy" class="hero-btn hero-btn-primary" style="align-self: flex-start;">Ask Agy 🐾</a>
        </div>
        <div class="ask-agy-divider"></div>
        <div class="ask-agy-right">
          <div class="ask-agy-try-label">Try asking</div>
          <button class="chip" id="chip-ask-0">"""
        + _CHIP_QUESTIONS[0]
        + """</button>
          <button class="chip" id="chip-ask-1">"""
        + _CHIP_QUESTIONS[1]
        + """</button>
          <button class="chip" id="chip-ask-2">"""
        + _CHIP_QUESTIONS[2]
        + """</button>
        </div>
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    # Hidden Streamlit buttons — the JS bridge in the components.html block
    # below routes visible-chip and Ask Agy anchor clicks here.
    if st.button("", key="card_btn_ask_agy"):
        st.session_state["active_tab"] = "Ask Agy"
        st.session_state["skip_home_menu"] = True
        st.rerun()
    for _idx, _question in enumerate(_CHIP_QUESTIONS):
        if st.button("", key=f"card_btn_ask_chip_{_idx}"):
            on_chip_click(_question)

    st.markdown("</div>", unsafe_allow_html=True)

    # JavaScript to wire up the HTML buttons - same pattern as hero.py
    import streamlit.components.v1 as components

    components.html(
        """
    <script>
    (function() {
    // Theme detection
    function detectTheme() {
        var body = window.parent.document.body;
        var bg = window.parent.getComputedStyle(body).backgroundColor;

        if (bg === 'rgb(14, 17, 23)' || bg === 'rgb(17, 20, 24)') {
            body.classList.add('dark-theme');
        } else {
            body.classList.remove('dark-theme');
        }
    }
    // Intentional polling — DO NOT replace with MutationObserver or remove.
    // Streamlit destroys and recreates this components.html iframe on every
    // rerun, killing the JS context that owns any single-fire listener. A
    // MutationObserver attached from inside this iframe loses its callback
    // closure the moment the iframe is recreated; the theme class then drifts
    // out of sync. Re-firing every 500ms re-asserts the class from a live
    // closure regardless of how many iframe-destroy cycles have happened.
    // Same defense rationale as the multi-setTimeout pattern in
    // utils/landing_cards.py build_card_wiring_js (see header there).
    // History: MATTGPT-058 originally proposed replacing this with
    // MutationObserver — closed May 13 2026 after recognizing the polling
    // is the iframe-rewire defense, not an anti-pattern.
    setInterval(detectTheme, 500);
    detectTheme();
        setTimeout(function() {
            const parentDoc = window.parent.document;

            // MATTGPT-107: card divs (id="card-X") replaced the inline
            // anchor buttons (id="btn-X"). Whole-card click dispatches to
            // the same hidden Streamlit buttons (key="card_btn_X") whose
            // routing logic is unchanged from pre-MATTGPT-107.
            const cardBanking = parentDoc.getElementById('card-banking');
            const cardCrossIndustry = parentDoc.getElementById('card-cross-industry');
            const cardProduct = parentDoc.getElementById('card-product');
            const cardModernization = parentDoc.getElementById('card-modernization');
            const cardConsulting = parentDoc.getElementById('card-consulting');
            const cardTeams = parentDoc.getElementById('card-teams');
            const btnAskAgy = parentDoc.getElementById('btn-ask-agy');

            if (cardBanking) {
                cardBanking.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-card_btn_banking"] button');
                    if (stBtn) stBtn.click();
                };
            }

            if (cardCrossIndustry) {
                cardCrossIndustry.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-card_btn_cross_industry"] button');
                    if (stBtn) stBtn.click();
                };
            }

            if (cardProduct) {
                cardProduct.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-card_btn_product"] button');
                    if (stBtn) stBtn.click();
                };
            }

            if (cardModernization) {
                cardModernization.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-card_btn_modernization"] button');
                    if (stBtn) stBtn.click();
                };
            }

            if (cardConsulting) {
                cardConsulting.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-card_btn_consulting"] button');
                    if (stBtn) stBtn.click();
                };
            }

            if (cardTeams) {
                cardTeams.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-card_btn_teams"] button');
                    if (stBtn) stBtn.click();
                };
            }

            if (btnAskAgy) {
                btnAskAgy.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-card_btn_ask_agy"] button');
                    if (stBtn) stBtn.click();
                };
            }
        }, 200);

    // Ask Agy Anything CHIP wiring — separate multi-firing block.
    // Re-attaches onclick on every firing without a dataset.wired gate.
    // Streamlit destroys and recreates this components.html iframe on every
    // rerun (e.g., when the user returns from Ask Agy back to Home),
    // killing the JS context that owns the chip onclick closures. The
    // single setTimeout(200ms) pattern above works for the cards because
    // those typically receive only the entry-point click and the user moves
    // on — but the chips live on Home, are clicked, route to Ask Agy,
    // then the user often comes back and clicks another chip. That's the
    // back-and-forth navigation pattern that surfaced the May 12 2026 dead-
    // closure bug on Cross-Industry landing. Multi-firing setTimeout
    // (100/300/600/1000ms) re-asserts the wiring from a live closure
    // regardless of how many iframe destroy/create cycles have happened.
    // See utils/landing_cards.py build_card_wiring_js for the original
    // pattern and CLAUDE.md "Click Handling Pattern" for the documented
    // anti-pattern (dataset.wired gating).
    function wireAskAgyChips() {
        const parentDoc = window.parent.document;
        for (let idx = 0; idx < 3; idx++) {
            const chip = parentDoc.getElementById('chip-ask-' + idx);
            if (chip) {
                chip.onclick = (function(i) {
                    return function() {
                        const stBtn = parentDoc.querySelector(
                            '[class*="st-key-card_btn_ask_chip_' + i + '"] button'
                        );
                        if (stBtn) stBtn.click();
                    };
                })(idx);
            }
        }
    }
    setTimeout(wireAskAgyChips, 100);
    setTimeout(wireAskAgyChips, 300);
    setTimeout(wireAskAgyChips, 600);
    setTimeout(wireAskAgyChips, 1000);
    })();
    </script>
    """,
        height=0,
    )
