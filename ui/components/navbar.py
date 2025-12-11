"""
Navigation Bar Component

Desktop: Dark navy horizontal bar (unchanged from production)
Mobile (<768px): Hamburger menu with dropdown
"""

import streamlit as st
import streamlit.components.v1 as components


def render_navbar(current_tab: str = "Home"):
    """
    Render top navigation bar with tab selection.

    Args:
        current_tab: Currently active tab name

    Returns:
        None (updates session state and triggers rerun on navigation)
    """

    # CSS only - mobile HTML injected via components.html
    st.markdown(
        """<style>
div[data-testid="stHorizontalBlock"]:has([class*="st-key-topnav_"]) {
    background: var(--dark-navy) !important;
    padding: 16px 40px !important;
    margin: 40px 0 0 0 !important;
    height: 72px !important;
    border-radius: 0 !important;
    position: relative !important;
    z-index: 999998 !important;
}
div[data-testid="stHorizontalBlock"]:has([class*="st-key-topnav_"]) > div[data-testid="column"] {
    background: var(--dark-navy) !important;
}
[class*="st-key-topnav_"] button {
    background: transparent !important;
    color: white !important;
    border: none !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    padding: 8px 16px !important;
    margin-top: 0 !important;
}
[class*="st-key-topnav_"] button:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    color: white !important;
}
[class*="st-key-topnav_"] button:disabled {
    background: var(--dark-navy-hover) !important;
    color: white !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}
.mobile-header, .mobile-nav-dropdown, .mobile-nav-overlay {
    display: none;
}
@media (max-width: 767px) {
    div[data-testid="stHorizontalBlock"]:has([class*="st-key-topnav_"]) {
        position: absolute !important;
        left: -9999px !important;
        height: 0 !important;
        overflow: hidden !important;
    }
    .mobile-header {
        display: flex !important;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 56px;
        background: var(--dark-navy, #2c3e50);
        align-items: center;
        justify-content: space-between;
        padding: 0 16px;
        z-index: 999999;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .mobile-hamburger {
        background: transparent;
        border: none;
        padding: 8px;
        cursor: pointer;
        width: 44px;
        height: 44px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .mobile-hamburger span {
        display: block;
        width: 24px;
        height: 2px;
        background: white;
        margin: 3px 0;
        border-radius: 2px;
        transition: all 0.3s ease;
    }
    .mobile-hamburger.open span:nth-child(1) {
        transform: rotate(45deg) translate(4px, 6px);
    }
    .mobile-hamburger.open span:nth-child(2) {
        opacity: 0;
    }
    .mobile-hamburger.open span:nth-child(3) {
        transform: rotate(-45deg) translate(4px, -6px);
    }
    .mobile-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .mobile-brand img {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .mobile-brand span {
        color: white;
        font-size: 20px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .mobile-spacer {
        width: 44px;
        visibility: hidden;
    }
    .mobile-nav-dropdown {
        display: none;
        position: fixed;
        top: 56px;
        left: 0;
        right: 0;
        background: var(--dark-navy, #2c3e50);
        padding: 8px 0 16px 0;
        z-index: 999998;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .mobile-nav-dropdown.open {
        display: block !important;
    }
    .mobile-nav-dropdown a {
        display: block;
        padding: 16px 24px;
        color: white;
        text-decoration: none;
        font-size: 17px;
        font-weight: 500;
    }
    .mobile-nav-dropdown a:hover {
        background: rgba(255,255,255,0.1);
    }
    .mobile-nav-dropdown a.active {
        background: rgba(255,255,255,0.15);
        font-weight: 600;
        border-left: 3px solid #d4a039;
        padding-left: 21px;
    }
    .mobile-nav-overlay {
        display: none;
        position: fixed;
        top: 56px;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 999997;
    }
    .mobile-nav-overlay.open {
        display: block !important;
    }
}
</style>""",
        unsafe_allow_html=True,
    )

    # Desktop navigation buttons
    with st.container():
        labels = [
            ("Home", "Home"),
            ("Explore Stories", "Explore Stories"),
            ("Ask MattGPT", "Ask MattGPT"),
            ("About Matt", "About Matt"),
        ]

        cols = st.columns(len(labels), gap="small")

        for i, (label, name) in enumerate(labels):
            with cols[i]:
                if st.button(
                    label,
                    use_container_width=True,
                    key=f"topnav_{name}",
                    type="secondary",
                    disabled=(name == current_tab),
                ):
                    st.session_state["active_tab"] = name
                    if name == "Explore Stories":
                        st.session_state["_just_switched_to_explore"] = True
                    st.rerun()

    # Mobile menu JS
    active_home = "active" if current_tab == "Home" else ""
    active_explore = "active" if current_tab == "Explore Stories" else ""
    active_ask = "active" if current_tab == "Ask MattGPT" else ""
    active_about = "active" if current_tab == "About Matt" else ""

    js_code = """
    <script>
    (function() {
        var doc = window.parent.document;

        // Theme detection
        function detectTheme() {
            var body = doc.body;
            var bg = window.parent.getComputedStyle(body).backgroundColor;
            if (bg === 'rgb(14, 17, 23)' || bg === 'rgb(17, 20, 24)') {
                body.classList.add('dark-theme');
            } else {
                body.classList.remove('dark-theme');
            }
        }
        setInterval(detectTheme, 500);
        detectTheme();

        // Remove existing mobile nav if present
        ['mobile-header', 'mobile-nav-overlay', 'mobile-nav-dropdown'].forEach(function(id) {
            var el = doc.getElementById(id);
            if (el) el.remove();
        });

        // Create header
        var header = document.createElement('div');
        header.className = 'mobile-header';
        header.id = 'mobile-header';
        header.innerHTML = '<button class="mobile-hamburger" id="mobile-hamburger" aria-label="Menu"><span></span><span></span><span></span></button><div class="mobile-brand"><img src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_avatar.png" alt="Agy"><span>MattGPT</span></div><div class="mobile-spacer"></div>';
        doc.body.insertBefore(header, doc.body.firstChild);

        // Create overlay
        var overlay = document.createElement('div');
        overlay.className = 'mobile-nav-overlay';
        overlay.id = 'mobile-nav-overlay';
        doc.body.insertBefore(overlay, doc.body.firstChild);

        // Create dropdown with active states
        var dropdown = document.createElement('nav');
        dropdown.className = 'mobile-nav-dropdown';
        dropdown.id = 'mobile-nav-dropdown';
        dropdown.innerHTML = '<a href="#" id="mobile-nav-home" class="ACTIVE_HOME">Home</a><a href="#" id="mobile-nav-explore" class="ACTIVE_EXPLORE">Explore Stories</a><a href="#" id="mobile-nav-ask" class="ACTIVE_ASK">Ask MattGPT</a><a href="#" id="mobile-nav-about" class="ACTIVE_ABOUT">About Matt</a><a href="#" id="mobile-nav-settings" style="border-top:1px solid rgba(255,255,255,0.2);margin-top:8px;padding-top:16px;">⚙️ Settings</a>';
        doc.body.insertBefore(dropdown, doc.body.firstChild);

        // Event handlers
        var hamburger = doc.getElementById('mobile-hamburger');

        hamburger.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            var isOpen = dropdown.style.display === 'block';
            dropdown.style.display = isOpen ? 'none' : 'block';
            overlay.style.display = isOpen ? 'none' : 'block';
            hamburger.classList.toggle('open', !isOpen);
        };

        overlay.onclick = function() {
            dropdown.style.display = 'none';
            overlay.style.display = 'none';
            hamburger.classList.remove('open');
        };

        // Nav link handlers
        var links = {
            'mobile-nav-home': 'topnav_Home',
            'mobile-nav-explore': 'topnav_Explore',
            'mobile-nav-ask': 'topnav_Ask',
            'mobile-nav-about': 'topnav_About'
        };

        Object.keys(links).forEach(function(id) {
            var link = doc.getElementById(id);
            if (link) {
                link.onclick = function(e) {
                    e.preventDefault();
                    var btn = doc.querySelector('[class*="st-key-' + links[id] + '"] button');
                    if (btn) btn.click();
                    dropdown.style.display = 'none';
                    overlay.style.display = 'none';
                    hamburger.classList.remove('open');
                };
            }
        });

        // Settings link
        var settings = doc.getElementById('mobile-nav-settings');
        if (settings) {
            settings.onclick = function(e) {
                e.preventDefault();
                var menu = doc.querySelector('[data-testid="stMainMenu"] button');
                if (menu) menu.click();
                dropdown.style.display = 'none';
                overlay.style.display = 'none';
                hamburger.classList.remove('open');
            };
        }
    })();
    </script>
    """

    js_code = js_code.replace('ACTIVE_HOME', active_home)
    js_code = js_code.replace('ACTIVE_EXPLORE', active_explore)
    js_code = js_code.replace('ACTIVE_ASK', active_ask)
    js_code = js_code.replace('ACTIVE_ABOUT', active_about)

    components.html(js_code, height=0)
