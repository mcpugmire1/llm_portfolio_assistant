"""
BDD Step Definitions for Ask Agy's hand-off to the conversation (MATTGPT-275).

Implements the scenarios in tests/bdd/features/ask_handoff.feature against the
running Streamlit app at localhost:8501, with live answers.

How the hand-off is observed: before the tap, a recorder is installed in the
page. On every animation frame and every DOM change it samples whether
landing's hero containers (.ask-header-landing, .main-intro-section) are on
the page and hidden, whether the conversation header is visible, which of the
previous page's elements are visible with height, and how many chat bubbles
are visible with no text. The window ends 300 ms after the visitor's question
bubble first shows its text. The step then waits for the answer to finish, so
no scenario closes the browser mid-stream.

Navigation and chip helpers mirror tests/bdd/steps/test_landing_page.py and
tests/bdd/steps/test_home.py.

Run with: pytest tests/bdd/steps/test_ask_handoff.py -v
(requires `streamlit run app.py` running on localhost:8501)
"""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

FEATURE = "../features/ask_handoff.feature"

scenarios(FEATURE)

# =============================================================================
# CONSTANTS
# =============================================================================

SHORT_WAIT = 200  # ms: quick UI updates
JS_BRIDGE_SETTLE_MS = 1200  # landing chips wire up at 100/300/600/1000 ms
TURN_TIMEOUT = 90000  # ms: one live turn on gpt-6.1-sol
AFTER_QUESTION_MS = 300  # window kept after the question bubble shows text
MOBILE_BREAKPOINT = 768  # below this, navigation is the hamburger menu

MAX_HERO_BLANKS = 1
MAX_HERO_BLANK_MS = 290  # production's single blank, Oct 12, 2026 trace

ASK_AGY_DESKTOP_NAV = ".st-key-topnav_Ask-Agy button"
ASK_AGY_MOBILE_NAV = "#mobile-nav-ask"
CHAT_MESSAGE = "[data-testid='stChatMessage']"
HOME_CHIP_BUTTON = "[class*='st-key-card_btn_ask_chip_0'] button"
TYPED_QUESTION = "Tell me about his payments work."

# Elements of the page a question can come from: landing (input, caption,
# chips, intro), Home (category cards, Ask Agy card) and the shared footer.
# The landing input row is matched by its input and button: the keyed row
# container itself is transparent with no border, so its box still counts as
# visible after everything inside it is hidden.
PREVIOUS_PAGE_SELECTORS = [
    "[class*='st-key-landing_input'] input",
    "[class*='st-key-landing_input'] button",
    ".powered-by-text",
    ".suggested-chip",
    ".main-intro-section",
    ".home-cat-card",
    ".ask-agy-card",
    ".footer-connect",
]

_RECORDER_JS = """
(previous) => {
    const S = window.__handoff = {t0: performance.now(), samples: [], done: false};
    const style = (el) => getComputedStyle(el);
    const visible = (el) => {
        const r = el.getBoundingClientRect();
        const s = style(el);
        return r.height > 0 && r.width > 0 && s.visibility !== 'hidden' && s.display !== 'none';
    };
    const sample = () => {
        const heroes = [...document.querySelectorAll("[data-testid='stElementContainer']")]
            .filter(c => c.querySelector('.ask-header-landing, .main-intro-section'));
        const msgs = [...document.querySelectorAll("[data-testid='stChatMessage']")];
        S.samples.push({
            t: performance.now() - S.t0,
            heroPresent: heroes.length > 0,
            heroHidden: heroes.some(c => style(c).visibility === 'hidden'),
            conv: [...document.querySelectorAll('.ask-header-conversation')].some(visible),
            previous: previous.filter(sel => [...document.querySelectorAll(sel)].some(visible)),
            emptyBubbles: msgs.filter(m => visible(m) && m.innerText.trim() === '').length,
            bubblesWithText: msgs.filter(m => m.innerText.trim().length > 0).length,
            chipsUnstyled: [...document.querySelectorAll('.suggested-chip')].filter(c => {
                const box = c.closest('.suggested-chips-grid, .suggested-chips-mobile');
                return visible(c) && (!box || style(box).display !== 'grid');
            }).length,
            receiversVisible: [...document.querySelectorAll("[class*='st-key-suggested_'] button")]
                .filter(visible).length,
        });
    };
    const loop = () => { if (S.done) return; sample(); requestAnimationFrame(loop); };
    new MutationObserver(() => { if (!S.done) sample(); }).observe(document.body, {
        childList: true, subtree: true, attributes: true,
        attributeFilter: ['data-stale', 'class', 'style'],
    });
    requestAnimationFrame(loop);
}
"""

_QUESTION_SHOWN_JS = """
() => document.querySelector('.ask-header-conversation') !== null
    && [...document.querySelectorAll("[data-testid='stChatMessage']")]
        .some(m => m.innerText.trim().length > 0)
"""

_TURN_DONE_JS = """
() => { const m = document.querySelectorAll("[data-testid='stChatMessage']");
  return m.length >= 2 && !document.querySelector('.thinking-modal')
    && m[m.length - 1].querySelector('.source-links-title') !== null; }
"""

# =============================================================================
# HELPERS
# =============================================================================


def wait_for_streamlit_rerun(page):
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


def _wait_for_navbar_stable(page, timeout: int = 30000) -> None:
    """Desktop navbar rendered (mirrors test_landing_page.py)."""
    page.wait_for_function(
        """
        () => ['st-key-topnav_Home', 'st-key-topnav_Ask-Agy']
            .every(c => document.querySelector('.' + c) !== null)
        """,
        timeout=timeout,
    )


def _watch_handoff(page, handoff, action):
    """Install the recorder, act, wait for the question bubble's text, keep
    AFTER_QUESTION_MS more, stop, then let the answer finish."""
    page.evaluate(_RECORDER_JS, PREVIOUS_PAGE_SELECTORS)
    action()
    page.wait_for_function(_QUESTION_SHOWN_JS, timeout=TURN_TIMEOUT, polling=50)
    page.wait_for_timeout(AFTER_QUESTION_MS)
    samples = page.evaluate(
        "() => { window.__handoff.done = true; return window.__handoff.samples; }"
    )
    shown = next(
        (s["t"] for s in samples if s["conv"] and s["bubblesWithText"] > 0), None
    )
    assert shown is not None, "The recorder never saw the question bubble with text."
    handoff["samples"] = [s for s in samples if s["t"] <= shown + AFTER_QUESTION_MS]
    page.wait_for_function(_TURN_DONE_JS, timeout=TURN_TIMEOUT, polling=200)


@pytest.fixture
def handoff():
    """Samples of one hand-off, shared between steps."""
    return {}


# =============================================================================
# GIVEN
# =============================================================================


@given(parsers.parse("the viewport for the hand-off is {width:d} px wide"))
def set_viewport(browser_page, width):
    # Before navigation: the app reads the screen width once per session.
    browser_page.set_viewport_size({"width": width, "height": 900})


def on_landing(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    if browser_page.viewport_size["width"] < MOBILE_BREAKPOINT:
        browser_page.locator("#mobile-hamburger").click()
        browser_page.locator("#mobile-nav-dropdown").wait_for(
            state="visible", timeout=5000
        )
        browser_page.locator(ASK_AGY_MOBILE_NAV).click()
    else:
        _wait_for_navbar_stable(browser_page)
        browser_page.locator(ASK_AGY_DESKTOP_NAV).first.click()
        wait_for_streamlit_rerun(browser_page)
    browser_page.wait_for_selector("[class*='st-key-landing_input']", timeout=15000)
    browser_page.wait_for_timeout(JS_BRIDGE_SETTLE_MS)


def on_home(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    browser_page.wait_for_selector("#card-product", state="attached", timeout=30000)
    browser_page.wait_for_timeout(JS_BRIDGE_SETTLE_MS)


@given(parsers.parse("the user is on the page the {path} starts from"))
def on_start_page(browser_page, app_url, path):
    if path.startswith("Home"):
        on_home(browser_page, app_url)
    else:
        on_landing(browser_page, app_url)


# =============================================================================
# WHEN
# =============================================================================


def tap_landing_chip(page, handoff):
    _watch_handoff(page, handoff, lambda: page.locator(".suggested-chip").first.click())


def type_on_landing(page, handoff):
    box = page.locator("[class*='st-key-landing_input'] input[type='text']")
    box.first.click()
    box.first.press_sequentially(TYPED_QUESTION, delay=20)
    _watch_handoff(page, handoff, lambda: box.first.press("Tab"))


def tap_home_chip(page, handoff):
    _watch_handoff(
        page,
        handoff,
        lambda: page.locator(HOME_CHIP_BUTTON).first.dispatch_event("click"),
    )


HANDOFF_PATHS = {
    "landing suggestion chip": tap_landing_chip,
    "typed landing question": type_on_landing,
    "Home suggested question": tap_home_chip,
}


@when(parsers.parse("the user asks from the {path} and watches the hand-off"))
def ask_from_path(browser_page, handoff, path):
    HANDOFF_PATHS[path](browser_page, handoff)


# =============================================================================
# THEN
# =============================================================================


@then("landing's hero blanks at most once, for no longer than 290 ms")
def hero_blanks_at_most_once(handoff):
    samples = handoff["samples"]
    episodes, start = [], None
    for s in samples:
        blank = s["heroPresent"] and s["heroHidden"]
        if blank and start is None:
            start = s["t"]
        elif not blank and start is not None:
            episodes.append(s["t"] - start)
            start = None
    if start is not None:
        episodes.append(samples[-1]["t"] - start)
    lengths = [round(e) for e in episodes]
    assert len(episodes) <= MAX_HERO_BLANKS, (
        f"Landing's hero blanked {len(episodes)} times during the hand-off"
        f" ({lengths} ms); at most {MAX_HERO_BLANKS} allowed."
    )
    assert all(e <= MAX_HERO_BLANK_MS for e in episodes), (
        f"Landing's hero blanked for {lengths} ms; no blank may exceed"
        f" {MAX_HERO_BLANK_MS} ms."
    )


@then("the conversation header never shows over the previous page's elements")
def no_conversation_over_previous_page(handoff):
    overlaps = [s for s in handoff["samples"] if s["conv"] and s["previous"]]
    seen = sorted({p for s in overlaps for p in s["previous"]})
    span = round(overlaps[-1]["t"] - overlaps[0]["t"]) if overlaps else 0
    assert not overlaps, (
        f"In {len(overlaps)} samples (over {span} ms) the conversation header was"
        f" on screen with the previous page's elements: {seen}."
    )


@then("the question bubble is never shown empty")
def no_empty_question_bubble(handoff):
    empty = [s for s in handoff["samples"] if s["emptyBubbles"]]
    span = round(empty[-1]["t"] - empty[0]["t"]) if empty else 0
    assert not empty, (
        f"A chat bubble with no text was on screen in {len(empty)} samples"
        f" (over {span} ms) before the question showed its text."
    )


@then("landing's suggestion chips never show unstyled")
def chips_never_unstyled(handoff):
    bad = [s for s in handoff["samples"] if s["chipsUnstyled"] or s["receiversVisible"]]
    span = round(bad[-1]["t"] - bad[0]["t"]) if bad else 0
    worst = (
        max(bad, key=lambda s: s["chipsUnstyled"] + s["receiversVisible"])
        if bad
        else None
    )
    assert not bad, (
        f"Landing's chips showed unstyled in {len(bad)} samples (over {span} ms):"
        f" up to {worst['chipsUnstyled']} chips outside their grid and"
        f" {worst['receiversVisible']} hidden-receiver buttons visible."
    )
