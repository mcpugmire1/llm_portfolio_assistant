"""
Category Cards Component

Homepage exploration cards for different portfolio categories.
Includes gradient industry cards and white capability cards.
"""

import streamlit as st
from config.theme import COLORS, GRADIENTS


def render_category_cards():
    """Render homepage category cards grid - responsive with CSS Grid."""
    
    st.markdown('<div class="matt-container">', unsafe_allow_html=True)

    # Row 1: Industry cards with buttons
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div style="background: {GRADIENTS['purple_hero']}; color: white; padding: 32px; border-radius: 12px; height: 340px; display: flex; flex-direction: column;">
            <div style="font-size: 48px; margin-bottom: 16px;">🏦</div>
            <h3 style="color: white; font-size: 24px; font-weight: 700; margin: 0 0 8px 0;">Financial Services / Banking</h3>
            <div style="color: rgba(255,255,255,0.9); font-size: 16px; font-weight: 600; margin-bottom: 16px;">55 projects</div>
            <div style="color: rgba(255,255,255,0.95); margin-bottom: 16px; line-height: 1.5; font-size: 15px;">Banking modernization, payments, compliance, core banking systems</div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px; flex-grow: 1; align-items: flex-start;">
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; display: inline-block; white-space: nowrap;">JPMorgan Chase (33)</span>
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; display: inline-block; white-space: nowrap;">American Express (3)</span>
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; display: inline-block; white-space: nowrap;">Capital One (2)</span>
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; display: inline-block; white-space: nowrap;">Fiserv (7)</span>
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; display: inline-block; white-space: nowrap;">HSBC (2)</span>
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; display: inline-block; white-space: nowrap;">RBC (11)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("See Banking Projects →", key="btn_0", use_container_width=False):
            st.session_state["active_tab"] = "Banking"
            st.rerun()

    with col2:
        st.markdown(f"""
        <div style="background: {GRADIENTS['purple_hero']}; color: white; padding: 32px; border-radius: 12px; height: 340px; display: flex; flex-direction: column;">
            <div style="font-size: 48px; margin-bottom: 16px;">🌐</div>
            <h3 style="color: white; font-size: 24px; font-weight: 700; margin: 0 0 8px 0;">Cross-Industry Transformation</h3>
            <div style="color: rgba(255,255,255,0.9); font-size: 16px; font-weight: 600; margin-bottom: 16px;">51 projects</div>
            <div style="color: rgba(255,255,255,0.95); margin-bottom: 16px; line-height: 1.5; font-size: 15px;">Multi-sector consulting, platform engineering, organizational transformation</div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px; flex-grow: 1; align-items: flex-start;">
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; display: inline-block; white-space: nowrap;">Accenture (13)</span>
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; display: inline-block; white-space: nowrap;">Multiple Clients (33)</span>
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; display: inline-block; white-space: nowrap;">Healthcare (3)</span>
                <span style="background: rgba(255,255,255,0.25); color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; display: inline-block; white-space: nowrap;">Transportation (5)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Browse Transformations →", key="btn_1", use_container_width=False):
            st.session_state["active_tab"] = "Cross-Industry"
            st.rerun()

    # Row 2: Capability cards with buttons
    col3, col4 = st.columns(2)

    with col3:
        st.markdown(f"""
        <div style="background: white; color: #333; padding: 32px; border-radius: 12px; border: 1px solid {COLORS['border_gray']}; height: 320px; display: flex; flex-direction: column;">
            <div style="font-size: 40px; margin-bottom: 16px;">🚀</div>
            <h3 style="color: #333; font-size: 20px; font-weight: 700; margin: 0 0 12px 0;">Product Innovation &amp; Strategy</h3>
            <div style="color: #666; margin-bottom: 16px; line-height: 1.6; font-size: 15px; flex-grow: 1;">Cloud-native products from zero. Lean, rapid prototyping, OKRs, MVPs</div>
            <div style="color: #999; font-style: italic; font-size: 14px; line-height: 1.5;">&quot;How do you do hypothesis-driven development?&quot; • &quot;How do you shift to product thinking?&quot;</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Case Studies →", key="btn_product_mgmt", use_container_width=False):
            # Guard: Only trigger if we're actually on the Home page
            if st.session_state.get("active_tab") == "Home":
                st.session_state["prefilter_domains"] = [
                    "Product Management",
                    "Product Strategy & Innovation",
                    "Client Product Innovation & Co-Creation",
                    "User-Centered Product Strategy & Innovation",
                    "Digital Product Development & Delivery"
                ]
                st.session_state["active_tab"] = "Explore Stories"
                st.rerun()

    with col4:
        st.markdown(f"""
        <div style="background: white; color: #333; padding: 32px; border-radius: 12px; border: 1px solid {COLORS['border_gray']}; height: 320px; display: flex; flex-direction: column;">
            <div style="font-size: 40px; margin-bottom: 16px;">🔧</div>
            <h3 style="color: #333; font-size: 20px; font-weight: 700; margin: 0 0 12px 0;">App Modernization</h3>
            <div style="color: #666; margin-bottom: 16px; line-height: 1.6; font-size: 15px; flex-grow: 1;">Modernizing legacy apps with event-driven design, microservices, and zero-defect delivery</div>
            <div style="color: #999; font-style: italic; font-size: 14px; line-height: 1.5;">&quot;How do you modernize monoliths into microservices?&quot; • &quot;How do you approach application rationalization?&quot;</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Case Studies →", key="btn_3", use_container_width=False):
            # Add the same guard here!
            if st.session_state.get("active_tab") == "Home":
                st.session_state["prefilter_capability"] = "Application Modernization"
                st.session_state["active_tab"] = "Explore Stories"
                st.rerun()


    # Row 3: Capability cards with buttons
    col5, col6 = st.columns(2)

    with col5:
        st.markdown(f"""
        <div style="background: white; color: #333; padding: 32px; border-radius: 12px; border: 1px solid {COLORS['border_gray']}; height: 320px; display: flex; flex-direction: column;">
            <div style="font-size: 40px; margin-bottom: 16px;">💡</div>
            <h3 style="color: #333; font-size: 20px; font-weight: 700; margin: 0 0 12px 0;">Consulting &amp; Transformation</h3>
            <div style="color: #666; margin-bottom: 16px; line-height: 1.6; font-size: 15px; flex-grow: 1;">Fortune 500 advisory, operating models, 3-20x acceleration, New Ways of Working</div>
            <div style="color: #999; font-style: italic; font-size: 14px; line-height: 1.5;">&quot;How do you achieve 4x faster delivery?&quot; • &quot;How do you align cross-functional teams?&quot;</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Browse Transformations →", key="btn_4", use_container_width=False):
            # Guard: Only trigger if we're actually on the Home page
            if st.session_state.get("active_tab") == "Home":
                st.session_state["prefilter_domains"] = [
                "Agile Planning & Value-Driven Delivery",
                "Agile Transformation & Leadership Enablement",
                "AI Governance & Data Privacy",
                "Client Product Innovation & Co-Creation",
                "Cross-Functional Collaboration & Alignment",
                "Leadership & Continuous Improvement",
                "Platform Adoption & Client Integration",
                "Process Optimization & Automation",
                "Product Management",
                "Product Strategy & Innovation",
                "Program Management & Governance",
                "Psychological Safety & Innovation Culture",
                "Security & Compliance Solutions",
                "Strategic Client Partnerships",
                "Strategic Enterprise & Methodology Innovation",
                "Technical Leadership",
                "Technology Strategy & Advisory Services",
                "User-Centered Product Strategy & Innovation"
                ]
                st.session_state["active_tab"] = "Explore Stories"
                st.rerun()



    with col6:
        st.markdown(f"""
        <div style="background: white; color: #333; padding: 32px; border-radius: 12px; border: 1px solid {COLORS['border_gray']}; height: 320px; display: flex; flex-direction: column;">
            <div style="font-size: 40px; margin-bottom: 16px;">👥</div>
            <h3 style="color: #333; font-size: 20px; font-weight: 700; margin: 0 0 12px 0;">Teams &amp; Talent Development</h3>
            <div style="color: {COLORS['purple_gradient_start']}; font-weight: 600; margin-bottom: 12px; font-size: 15px;">300+ professionals trained</div>
            <div style="color: #666; margin-bottom: 16px; line-height: 1.6; font-size: 15px; flex-grow: 1;">Innovation centers, servant leadership, upskilling programs</div>
            <div style="color: #999; font-style: italic; font-size: 14px; line-height: 1.5;">&quot;How did you scale the innovation center to 150+ people?&quot; • &quot;How did you equip teams for New IT ways of working?&quot;</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Check Team Stories →", key="btn_5", use_container_width=False):
            # Guard: Only trigger if we're actually on the Home page
            if st.session_state.get("active_tab") == "Home":
                st.session_state["prefilter_domains"] = [
                "Client Upskilling & Enablement",
                "Cross-Functional Team Enablement",
                "Psychological Safety & Innovation Culture",
                "Talent Enablement & Growth",
                ]
                st.session_state["active_tab"] = "Explore Stories"
                st.rerun()


    # Row 4: Quick Question card
    st.markdown(f"""
    <div style="background: {GRADIENTS['purple_hero']}; color: white; padding: 32px; border-radius: 12px; min-height: 200px; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 24px; margin-bottom: 20px;">
            <img src="https://raw.githubusercontent.com/mcpugmire1/mattgpt-design-spec/main/brand-kit/chat_avatars/agy_avatar_128_dark.png"
                 alt="Agy" style="width: 64px; height: 64px; border-radius: 50%; border: 3px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
            <div>
                <h3 style="font-size: 24px; font-weight: 700; margin: 0 0 4px 0; color: white;">Quick Question</h3>
                <div style="font-size: 16px; font-weight: 600; color: rgba(255,255,255,0.95);">Ask Agy 🐾 anything</div>
            </div>
        </div>
        <div style="font-size: 16px; margin-bottom: 16px; color: rgba(255,255,255,0.95); line-height: 1.6;">
            From building MattGPT to leading global programs — Agy can help you explore 20+ years of transformation experience.
        </div>
        <div style="font-size: 14px; font-style: italic; color: rgba(255,255,255,0.85); margin-bottom: 20px;">
            &quot;How did you build MattGPT?&quot; • &quot;How do you overcome the challenges of scaling to 150+ engineers?&quot;
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Ask Agy 🐾", key="btn_6", use_container_width=False):
        st.session_state["active_tab"] = "Ask MattGPT"
        st.session_state["skip_home_menu"] = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # JavaScript for button styling
    import streamlit.components.v1 as components
    components.html("""
    <script>
    (function() {
        function applyPurpleButtons() {
            const iframeDoc = window.parent.document;
            for (let i = 0; i <= 5; i++) {
                const container = iframeDoc.querySelector('.st-key-btn_' + i);
                if (container) {
                    const button = container.querySelector('button');
                    if (button && !button.dataset.purpled) {
                        button.dataset.purpled = 'true';
                        button.style.cssText = 'background: white !important; background-color: white !important; background-image: none !important; border: 2px solid #e5e5e5 !important; color: #8B5CF6 !important;';
                        button.onmouseenter = function() {
                            this.style.cssText = 'background: #8B5CF6 !important; background-color: #8B5CF6 !important; background-image: none !important; border: 2px solid #8B5CF6 !important; color: white !important;';
                        };
                        button.onmouseleave = function() {
                            this.style.cssText = 'background: white !important; background-color: white !important; background-image: none !important; border: 2px solid #e5e5e5 !important; color: #8B5CF6 !important;';
                        };
                    }
                }
            }
            const agyContainer = iframeDoc.querySelector('.st-key-btn_6');
            if (agyContainer) {
                const agyButton = agyContainer.querySelector('button');
                if (agyButton && !agyButton.dataset.purpled) {
                    agyButton.dataset.purpled = 'true';
                    agyButton.style.cssText = 'background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%) !important; background-color: #8B5CF6 !important; border: none !important; color: white !important; padding: 14px 28px !important; font-size: 15px !important; font-weight: 600 !important; border-radius: 8px !important; box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25) !important;';
                    agyButton.onmouseenter = function() {
                        this.style.cssText = 'background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important; background-color: #7C3AED !important; border: none !important; color: white !important; padding: 14px 28px !important; font-size: 15px !important; font-weight: 600 !important; border-radius: 8px !important; box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4) !important; transform: translateY(-2px) !important;';
                    };
                    agyButton.onmouseleave = function() {
                        this.style.cssText = 'background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%) !important; background-color: #8B5CF6 !important; border: none !important; color: white !important; padding: 14px 28px !important; font-size: 15px !important; font-weight: 600 !important; border-radius: 8px !important; box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25) !important;';
                    };
                }
            }
        }
        setTimeout(applyPurpleButtons, 100);
        setTimeout(applyPurpleButtons, 500);
        setTimeout(applyPurpleButtons, 1000);
        setTimeout(applyPurpleButtons, 2000);
    })();
    </script>
    """, height=0)
