"""
Category Cards Component

Homepage exploration cards for different portfolio categories.
Includes gradient industry cards and white capability cards.
"""

import streamlit as st
from config.theme import COLORS, GRADIENTS

# Card data definition
STARTER_CARDS = [
    {
        "icon": "🏦",
        "title": "Financial Services / Banking",
        "desc": "Banking modernization, payments, compliance, core banking systems",
        "type": "industry",
        "project_count": "55 projects",
        "tags": ["JPMorgan Chase (33)", "American Express (3)", "Capital One (2)", "Fiserv (7)", "HSBC (2)", "RBC (11)"],
        "button_text": "See Banking Projects →",
        "action": "navigate",
        "target": "Banking",
    },
    {
        "icon": "🌐",
        "title": "Cross-Industry Transformation",
        "desc": "Multi-sector consulting, platform engineering, organizational transformation",
        "type": "industry",
        "project_count": "51 projects",
        "tags": ["Accenture (13)", "Multiple Clients (33)", "Healthcare (3)", "Transportation (5)"],
        "button_text": "Browse Transformations →",
        "action": "navigate",
        "target": "Cross-Industry",
    },
    {
        "icon": "🚀",
        "title": "Product Innovation & Strategy",
        "desc": "Cloud-native products from zero. Lean, rapid prototyping, OKRs, MVPs",
        "type": "capability",
        "examples": '"How do you do hypothesis-driven development?" • "How do you shift to product thinking?"',
        "button_text": "Explore Product Work →",
        "action": "ask",
        "question": "Tell me about your product innovation approach",
        "target": "Ask MattGPT",
    },
    {
        "icon": "🔧",
        "title": "App Modernization",
        "desc": "Modernizing legacy apps with event-driven design, microservices, and zero-defect delivery",
        "type": "capability",
        "examples": '"How do you modernize monoliths into microservices?" • "How do you approach application rationalization?"',
        "button_text": "View Case Studies →",
        "action": "ask",
        "question": "How do you modernize legacy applications?",
        "target": "Ask MattGPT",
    },
    {
        "icon": "💡",
        "title": "Consulting & Transformation",
        "desc": "Fortune 500 advisory, operating models, 3-20x acceleration, New Ways of Working",
        "type": "capability",
        "examples": '"How do you achieve 4x faster delivery?" • "How do you align cross-functional teams?"',
        "button_text": "Browse Transformations →",
        "action": "ask",
        "question": "How do you achieve faster delivery for Fortune 500 clients?",
        "target": "Ask MattGPT",
    },
    {
        "icon": "👥",
        "title": "Teams & Talent Development",
        "desc": "300+ professionals trained, innovation centers, servant leadership",
        "type": "capability",
        "examples": '"How did you scale the innovation center to 150+ people?" • "How did you equip teams for New IT ways of working?"',
        "button_text": "Check Team Stories →",
        "action": "ask",
        "question": "How did you scale and develop innovation teams?",
        "target": "Ask MattGPT",
        "highlight": "300+ professionals trained",
    },
    {
        "icon": "💬",
        "title": "Quick Question",
        "desc": "Ask me anything — from building MattGPT to leading global programs.",
        "type": "quick_question",
        "examples": '"How did you build MattGPT?" • "How do you overcome the challenges of scaling to 150+ engineers?"',
        "button_text": "Ask Agy 🐾",
        "action": "navigate",
        "target": "Ask MattGPT",
    },
]


def render_category_cards():
    """
    Render homepage category cards grid.

    Layout:
    - Row 1: 2 industry cards (gradient background)
    - Row 2: 2 capability cards (white background)
    - Row 3: 2 capability cards (white background)
    - Row 4: 1 full-width quick question card (gradient)
    """

    # DEBUG TEST - Add visible marker to confirm code is running
    st.markdown("### 🔴 DEBUG: If you see this red circle, the code is loading!")

    # Card CSS - injected early
    st.markdown(f"""
    <style id="homepage-button-styles">
    /* Industry cards - gradient background, white text */
    .industry-card {{
        background: {GRADIENTS['purple_hero']};
        color: white;
        padding: 32px;
        border-radius: 12px;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        transition: all 0.3s ease;
        margin-bottom: 20px;
        border: none !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
    }}
    .industry-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
    }}
    .industry-card h3 {{
        color: white !important;
        font-size: 24px !important;
        font-weight: 700 !important;
        margin-bottom: 8px !important;
    }}
    .industry-card .project-count {{
        color: rgba(255,255,255,0.9);
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 16px;
    }}
    .industry-card .card-desc {{
        color: rgba(255, 255, 255, 0.95);
        margin-bottom: 16px;
        line-height: 1.5;
        font-size: 15px;
    }}
    .industry-card .tags {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 20px;
        flex-grow: 1;
    }}
    .industry-card .tag {{
        background: rgba(255,255,255,0.25);
        color: white;
        padding: 6px 12px;
        border-radius: 16px;
        font-size: 13px;
        font-weight: 500;
    }}

    /* Capability cards - white background, dark text */
    .capability-card {{
        background: white;
        color: #333;
        padding: 32px;
        border-radius: 12px;
        border: 1px solid {COLORS['border_gray']};
        min-height: 280px;
        display: flex;
        flex-direction: column;
        transition: all 0.3s ease;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
    }}
    .capability-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12) !important;
        border-color: {COLORS['purple_gradient_start']};
    }}
    .capability-card h3 {{
        color: #333 !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        margin-bottom: 12px !important;
    }}
    .capability-card .card-desc {{
        color: #666;
        margin-bottom: 16px;
        line-height: 1.6;
        font-size: 15px;
        flex-grow: 1;
    }}
    .capability-card .card-examples {{
        color: #999;
        font-style: italic;
        font-size: 14px;
        line-height: 1.5;
        margin-bottom: 16px;
    }}

    /* Quick Question card - gradient like industry cards */
    .quick-question-card {{
        background: {GRADIENTS['purple_hero']};
        color: white;
        padding: 32px;
        border-radius: 12px;
        min-height: 200px;
        transition: all 0.3s ease;
        margin-bottom: 20px;
        border: none !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
    }}
    .quick-question-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
    }}

    /* Homepage category buttons - MEGA ULTRA NUCLEAR - Target EXACT classes from HTML */
    button.st-emotion-cache-7lqsib.e8vg11g2[data-testid="stBaseButton-secondary"],
    .stElementContainer[class*="st-key-btn_"] button.st-emotion-cache-7lqsib,
    .st-key-btn_0 button, .st-key-btn_1 button, .st-key-btn_2 button, .st-key-btn_3 button, .st-key-btn_4 button, .st-key-btn_5 button,
    [class*="st-key-btn_"] button[data-testid="stBaseButton-secondary"] {{
        background-color: white !important;
        background-image: none !important;
        background: white !important;
        color: #8B5CF6 !important;
        border: 2px solid #e5e5e5 !important;
        border-radius: 8px !important;
        padding: 11px 20px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        min-height: unset !important;
    }}
    button.st-emotion-cache-7lqsib.e8vg11g2[data-testid="stBaseButton-secondary"]:hover,
    .stElementContainer[class*="st-key-btn_"] button.st-emotion-cache-7lqsib:hover,
    .st-key-btn_0 button:hover, .st-key-btn_1 button:hover, .st-key-btn_2 button:hover, .st-key-btn_3 button:hover, .st-key-btn_4 button:hover, .st-key-btn_5 button:hover,
    [class*="st-key-btn_"] button[data-testid="stBaseButton-secondary"]:hover {{
        background-color: #8B5CF6 !important;
        background-image: none !important;
        background: #8B5CF6 !important;
        color: white !important;
        border-color: #8B5CF6 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3), 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }}

    /* Fix card height inconsistencies */
    .capability-card {{
        min-height: 280px !important;
        height: 100% !important;
    }}

    /* "Ask Agy" bottom CTA button - Premium purple gradient */
    .stElementContainer[class*="st-key-btn_6"] button,
    [class*="st-key-btn_6"] button[class*="st-emotion-cache"] {{
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%) !important;
        background-color: #8B5CF6 !important;
        color: white !important;
        border: none !important;
        padding: 12px 28px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25), 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    .stElementContainer[class*="st-key-btn_6"] button:hover,
    [class*="st-key-btn_6"] button[class*="st-emotion-cache"]:hover {{
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
        background-color: #7C3AED !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4), 0 3px 6px rgba(0, 0, 0, 0.15) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # JavaScript approach - apply styles AFTER page loads to override emotion-cache
    st.markdown("""
    <script>
    setTimeout(function() {{
        // Target homepage category buttons
        const buttons = document.querySelectorAll('[class*="st-key-btn_"] button[data-testid="stBaseButton-secondary"]');
        buttons.forEach(button => {{
            if (!button.classList.contains('st-key-btn_6')) {{ // Not the Ask Agy button
                button.style.backgroundColor = 'white';
                button.style.color = '#8B5CF6';
                button.style.border = '2px solid #e5e5e5';
                button.style.borderRadius = '8px';
                button.style.padding = '11px 20px';
                button.style.fontSize = '14px';
                button.style.fontWeight = '600';
                button.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.08)';
                button.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';

                // Add hover effect
                button.addEventListener('mouseenter', function() {{
                    this.style.backgroundColor = '#8B5CF6';
                    this.style.color = 'white';
                    this.style.borderColor = '#8B5CF6';
                    this.style.transform = 'translateY(-2px)';
                    this.style.boxShadow = '0 4px 12px rgba(139, 92, 246, 0.3), 0 2px 4px rgba(0, 0, 0, 0.1)';
                }});
                button.addEventListener('mouseleave', function() {{
                    this.style.backgroundColor = 'white';
                    this.style.color = '#8B5CF6';
                    this.style.borderColor = '#e5e5e5';
                    this.style.transform = 'translateY(0)';
                    this.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.08)';
                }});
            }}
        }});

        // Target Ask Agy button (btn_6) for purple gradient
        const agyButton = document.querySelector('.st-key-btn_6 button');
        if (agyButton) {{
            agyButton.style.background = 'linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)';
            agyButton.style.backgroundColor = '#8B5CF6';
            agyButton.style.color = 'white';
            agyButton.style.border = 'none';
            agyButton.style.padding = '12px 28px';
            agyButton.style.fontSize = '15px';
            agyButton.style.fontWeight = '600';
            agyButton.style.borderRadius = '8px';
            agyButton.style.boxShadow = '0 2px 8px rgba(139, 92, 246, 0.25), 0 1px 3px rgba(0, 0, 0, 0.1)';

            agyButton.addEventListener('mouseenter', function() {{
                this.style.background = 'linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%)';
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 6px 16px rgba(139, 92, 246, 0.4), 0 3px 6px rgba(0, 0, 0, 0.15)';
            }});
            agyButton.addEventListener('mouseleave', function() {{
                this.style.background = 'linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)';
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '0 2px 8px rgba(139, 92, 246, 0.25), 0 1px 3px rgba(0, 0, 0, 0.1)';
            }});
        }}
    }}, 100);
    </script>
    """, unsafe_allow_html=True)

    st.markdown('<div class="matt-container">', unsafe_allow_html=True)

    # Row 1: Industry cards (2 columns)
    col1, col2 = st.columns(2)

    with col1:
        _render_industry_card(STARTER_CARDS[0], "btn_0")

    with col2:
        _render_industry_card(STARTER_CARDS[1], "btn_1")

    # Row 2: Capability cards
    col3, col4 = st.columns(2)

    with col3:
        _render_capability_card(STARTER_CARDS[2], "btn_2")

    with col4:
        _render_capability_card(STARTER_CARDS[3], "btn_3")

    # Row 3: Capability cards
    col5, col6 = st.columns(2)

    with col5:
        _render_capability_card(STARTER_CARDS[4], "btn_4")

    with col6:
        _render_capability_card(STARTER_CARDS[5], "btn_5")

    # Row 4: Quick Question card (full width)
    _render_quick_question_card(STARTER_CARDS[6], "btn_6")

    st.markdown('</div>', unsafe_allow_html=True)


def _render_industry_card(card, button_key):
    """Render industry card with gradient background."""
    tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in card["tags"]])

    st.markdown(f"""
    <div class="industry-card">
        <div style="font-size: 48px; margin-bottom: 16px;">{card['icon']}</div>
        <h3>{card['title']}</h3>
        <div class="project-count">{card['project_count']}</div>
        <div class="card-desc">{card['desc']}</div>
        <div class="tags">{tags_html}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(card["button_text"], key=button_key, use_container_width=False):
        st.session_state["active_tab"] = card["target"]
        st.rerun()


def _render_capability_card(card, button_key):
    """Render capability card with white background."""
    highlight = card.get("highlight")
    highlight_html = f'<div class="card-desc" style="color: {COLORS["purple_gradient_start"]}; font-weight: 600; margin-bottom: 12px;">{highlight}</div>' if highlight else ""

    st.markdown(f"""
    <div class="capability-card">
        <div style="font-size: 40px; margin-bottom: 16px;">{card['icon']}</div>
        <h3>{card['title']}</h3>
        {highlight_html}
        <div class="card-desc">{card['desc']}</div>
        <div class="card-examples">{card['examples']}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(card["button_text"], key=button_key, use_container_width=False):
        if card["action"] == "ask":
            st.session_state["__inject_user_turn__"] = card["question"]
            st.session_state.pop("__ctx_locked__", None)
            st.session_state.pop("active_context", None)
        st.session_state["active_tab"] = card["target"]
        st.session_state["skip_home_menu"] = True
        st.rerun()


def _render_quick_question_card(card, button_key):
    """Render full-width quick question card."""
    st.markdown(f"""
    <div class="quick-question-card">
        <div style="display: flex; align-items: center; gap: 24px; margin-bottom: 20px;">
            <img src="https://raw.githubusercontent.com/mcpugmire1/mattgpt-design-spec/main/brand-kit/chat_avatars/agy_avatar_128_dark.png"
                 alt="Agy"
                 style="width: 64px; height: 64px; border-radius: 50%; border: 3px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
            <div>
                <h3 style="font-size: 24px; font-weight: 700; margin-bottom: 4px; color: white;">{card['title']}</h3>
                <div style="font-size: 16px; font-weight: 600; color: rgba(255,255,255,0.95);">Ask Agy 🐾 anything</div>
            </div>
        </div>
        <div style="font-size: 16px; margin-bottom: 16px; color: rgba(255,255,255,0.95); line-height: 1.6;">
            From building MattGPT to leading global programs — Agy can help you explore 20+ years of transformation experience.
        </div>
        <div style="font-size: 14px; font-style: italic; color: rgba(255,255,255,0.85); margin-bottom: 20px;">
            {card['examples']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(card["button_text"], key=button_key, use_container_width=False):
        st.session_state["active_tab"] = card["target"]
        st.session_state["skip_home_menu"] = True
        st.rerun()
