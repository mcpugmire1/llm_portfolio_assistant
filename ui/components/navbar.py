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
/* Strip Streamlit's inner block margins inside the navbar brand column only.
   Guard matches rules 2-5 below — prevents hitting other stHorizontalBlock
   layouts on the page (e.g. Ask Agy suggestion chip grid left column). */
div[data-testid="stHorizontalBlock"]:has([class*="st-key-topnav_"]) > div[data-testid="stColumn"]:first-child div[data-testid="stVerticalBlock"] {
    margin: 0 !important;
    padding: 0 !important;
    gap: 0 !important;
}
        /* Strip Streamlit's default element margin/padding from the brand container */
div[data-testid="stColumn"]:has(.navbar-brand) div[data-testid="stBlock"] {
    margin: 0 !important;
    padding: 0 !important;
}

/* Outer block: the navbar itself */
div[data-testid="stHorizontalBlock"]:has([class*="st-key-topnav_"]):has(div[data-testid="stHorizontalBlock"]) {
    background: var(--dark-navy) !important;
    padding: 0 40px !important;
    margin: 40px 0 0 0 !important;
    min-height: 72px !important;
    border-radius: 0 !important;
    align-items: center !important;
    position: relative !important;
    z-index: 999998 !important;
}

/* Outer columns (brand_col, nav_container): center their content */
div[data-testid="stHorizontalBlock"]:has([class*="st-key-topnav_"]):has(div[data-testid="stHorizontalBlock"]) > div[data-testid="stColumn"] {
    display: flex !important;
    align-items: center !important;
    min-height: 72px !important;
}

/* Inner block: transparent container, right-justify buttons */
div[data-testid="stHorizontalBlock"]:has([class*="st-key-topnav_"]):not(:has(div[data-testid="stHorizontalBlock"])) {
    justify-content: flex-end !important;
    align-items: center !important;
    min-height: 72px !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
}

/* Nav columns: natural width */
div[data-testid="stHorizontalBlock"]:has([class*="st-key-topnav_"]):not(:has(div[data-testid="stHorizontalBlock"])) > div[data-testid="stColumn"] {
flex: 0 1 auto !important;
    width: auto !important;
    min-width: auto !important;
    max-width: none !important;
    background: transparent !important;
    display: flex !important;
    align-items: center !important;
}

/* Brand: just text, no positioning */
/* Brand column needs position: relative to anchor the absolutely-positioned
   .navbar-brand inside it. Streamlit's stMarkdown wrapper layers were
   ignoring flex centering, so we use absolute positioning instead. */
div[data-testid="stColumn"]:has(.navbar-brand) {
    position: relative !important;
    min-height: 72px !important;
}
.navbar-brand {
    position: absolute !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    left: 0 !important;
    color: white;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 0.5px;
    white-space: nowrap;
    line-height: 1;
}
/* Strip default paragraph margin inside the brand column */
div[data-testid="stColumn"]:first-child p {
    margin-bottom: 0 !important;
}
[class*="st-key-topnav_"] button {
    background: transparent !important;
    color: white !important;
    border: none !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    padding: 8px 12px !important;
    margin-top: 0 !important;
    white-space: nowrap !important;
    font-size: 14px !important;
    width: auto !important;
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
    cursor: default !important;
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
    /* Also collapse the desktop navbar's outer stLayoutWrapper on mobile.
       The offscreen-positioning rule above hides the inner block visually
       but the wrapper still reserves ~184px of vertical flow below the
       fixed mobile header. Hiding the wrapper removes that gap entirely.
       The mobile dropdown is unaffected — it's a separate fixed-position
       element built from .mobile-nav-dropdown by the components.html JS. */
    div[data-testid="stLayoutWrapper"]:has([class*="st-key-topnav_"]) {
        display: none !important;
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

    # Desktop navigation: brand-left (MATTGPT-106) + 5 nav buttons grouped right.
    # Outer columns split [1, 4] = brand (~20%) + nav container (~80%). The 5
    # nav buttons live inside the nav_container's nested 5-column block so the
    # existing stHorizontalBlock:has([class*="st-key-topnav_"]) CSS scopes to
    # the nested row only — the outer brand+container block doesn't get the
    # navbar styling. Brand cell uses its own .navbar-brand styling (dark-navy
    # bg, 72px height, 40px top margin) to align visually with the nav row.
    labels = [
        ("Home", "Home"),
        ("My Work", "My Work"),
        ("Ask Agy", "Ask Agy"),
        ("Role Match", "Role Match"),
        ("My Profile", "My Profile"),
    ]

    brand_col, nav_container = st.columns([1, 4])

    with brand_col:
        st.markdown(
            '<div class="navbar-brand">MattGPT</div>',
            unsafe_allow_html=True,
        )

    with nav_container:
        nav_cols = st.columns(len(labels), gap="small")
        for i, (label, name) in enumerate(labels):
            with nav_cols[i]:
                if st.button(
                    label,
                    use_container_width=True,
                    key=f"topnav_{name}",
                    type="secondary",
                    disabled=(name == current_tab),
                ):
                    st.session_state["active_tab"] = name
                    if name == "My Work":
                        st.session_state["_just_switched_to_explore"] = True
                    st.rerun()

    # Mobile menu JS
    active_home = "active" if current_tab == "Home" else ""
    active_explore = "active" if current_tab == "My Work" else ""
    active_ask = "active" if current_tab == "Ask Agy" else ""
    active_role = "active" if current_tab == "Role Match" else ""
    active_about = "active" if current_tab == "My Profile" else ""

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
        header.innerHTML = '<button class="mobile-hamburger" id="mobile-hamburger" aria-label="Menu"><span></span><span></span><span></span></button><div class="mobile-brand"><img src="/app/static/agy_avatar.png" width="44" height="44" alt="Agy"><span>MattGPT</span></div><div class="mobile-spacer"></div>';
        doc.body.insertBefore(header, doc.body.firstChild);

        // Create overlay
        var overlay = document.createElement('div');
        overlay.className = 'mobile-nav-overlay';
        overlay.id = 'mobile-nav-overlay';
        doc.body.insertBefore(overlay, doc.body.firstChild);

        // Page transition overlay — injected into the parent window via <script> tag (MATTGPT-018).
        // Overlay, maskNav(), setTimeout, and click listener all live in parent window scope so
        // they survive Streamlit destroying the components.html iframe on every rerun. Anything
        // defined in the iframe (closures, timers, listeners) dies with the iframe.
        if (!window.parent.__maskNav) {
            var ptScript = doc.createElement('script');
            ptScript.text = `(function(){
                var ov = document.createElement('div');
                ov.id = 'page-transition-overlay';
                ov.style.cssText = 'position:fixed;inset:0;z-index:9997;opacity:0;pointer-events:none;';
                document.body.appendChild(ov);
                window.__maskNav = function() {
                    ov.style.background = getComputedStyle(document.body).backgroundColor;
                    ov.style.transition = 'none';
                    ov.style.opacity = '1';
                    setTimeout(function() {
                        ov.style.transition = 'opacity 0.08s ease-in';
                        ov.style.opacity = '0';
                    }, 150);
                };
                document.addEventListener('click', function(e) {
                    if (e.target.closest('[class*="st-key-topnav_"] button')) window.__maskNav();
                });
            })();`;
            doc.head.appendChild(ptScript);
        }

        // Preload all static images on first page load so they're cache-warm before navigation
        if (!doc.body.__imgPreloaded) {
            doc.body.__imgPreloaded = true;
            ['/app/static/agy_avatar.png', '/app/static/agy_explore_stories.png',
             '/app/static/agy_ask_mattgpt.png', '/app/static/matt_agy_hero.png',
             '/app/static/agy_banking.png', '/app/static/agy_cross_industry.png',
             '/app/static/MattCartoon-Transparent.png', '/app/static/AgyMattCartoon-Transparent.png',
             '/app/static/chase_48px_1.png', '/app/static/chase_48px_2.png', '/app/static/chase_48px_3.png'
            ].forEach(function(src) { new Image().src = src; });
        }

        // Create dropdown with active states
        var dropdown = document.createElement('nav');
        dropdown.className = 'mobile-nav-dropdown';
        dropdown.id = 'mobile-nav-dropdown';
        dropdown.innerHTML = '<a href="#" id="mobile-nav-home" class="ACTIVE_HOME">Home</a><a href="#" id="mobile-nav-explore" class="ACTIVE_EXPLORE">My Work</a><a href="#" id="mobile-nav-ask" class="ACTIVE_ASK">Ask Agy</a><a href="#" id="mobile-nav-role" class="ACTIVE_ROLE">Role Match</a><a href="#" id="mobile-nav-about" class="ACTIVE_ABOUT">My Profile</a><a href="#" id="mobile-nav-settings" style="border-top:1px solid rgba(255,255,255,0.2);margin-top:8px;padding-top:16px;">⚙️ Settings</a>';
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
            'mobile-nav-explore': 'topnav_My-Work',
            'mobile-nav-ask': 'topnav_Ask-Agy',
            'mobile-nav-role': 'topnav_Role-Match',
            'mobile-nav-about': 'topnav_My-Profile'
        };

        Object.keys(links).forEach(function(id) {
            var link = doc.getElementById(id);
            if (link) {
                link.onclick = function(e) {
                    e.preventDefault();
                    if (window.parent.__maskNav) window.parent.__maskNav();
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
    js_code = js_code.replace('ACTIVE_ROLE', active_role)
    js_code = js_code.replace('ACTIVE_ABOUT', active_about)

    components.html(js_code, height=0)
