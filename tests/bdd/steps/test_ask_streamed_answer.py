"""
BDD Step Definitions for Ask Agy's streamed answer (MATTGPT-275 step 1).

Implements the 3 scenarios in tests/bdd/features/ask_streamed_answer.feature.
Step definitions use Playwright (via the shared browser_page fixture in
conftest.py) to drive the running Streamlit app at localhost:8501, with
live answers.

How streaming is observed: before the question is submitted, a recorder is
installed in the page. On every DOM change (and every 50 ms as a backstop)
it samples the newest chat message: its avatar, the length of its first
markdown block (the answer text), and whether the thinking indicator is
on the page. Streamlit is a single-page app, so the recorder survives the
reruns of the turn. When the turn has finished, the samples belonging to
Agy's message (the finished answer's avatar, newer than the messages
before the question) are read back. An answer rendered in one piece shows
one text length; a streamed answer shows several, growing.

Navigation, wait and submit helpers mirror tests/bdd/steps/test_ask_mattgpt.py
and tests/bdd/steps/test_home.py.

Run with: pytest tests/bdd/steps/test_ask_streamed_answer.py -v
(requires `streamlit run app.py` running on localhost:8501)
"""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/ask_streamed_answer.feature")

# =============================================================================
# WAIT CONSTANTS
# =============================================================================

SHORT_WAIT = 200  # ms: quick UI updates
TURN_TIMEOUT = 90000  # ms: one live turn on gpt-6.1-sol (run 2 p90 12.35 s)
SETTLE_MS = 1000  # ms the answer text must hold still to count as finished

# "Grows": at least this many distinct non-empty text lengths before the
# turn finishes, the first under this fraction of the finished length.
MIN_DISTINCT_LENGTHS = 3
FIRST_LENGTH_MAX_FRACTION = 0.5

CHAT_MESSAGE = "[data-testid='stChatMessage']"
ASK_AGY_NAV_SELECTOR = ".st-key-topnav_Ask-Agy button"
HOME_CHIP_INDEX = 0  # card_btn_ask_chip_0 and its visible #chip-ask-0

# =============================================================================
# HELPERS
# =============================================================================


def wait_for_streamlit_rerun(page):
    """Wait for Streamlit to complete a rerun after an action."""
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


def _wait_for_navbar_stable(page, timeout: int = 30000) -> None:
    """Wait until the desktop navbar is rendered (mirrors test_ask_mattgpt.py)."""
    page.wait_for_function(
        """
        () => {
            const classes = [
                'st-key-topnav_Home',
                'st-key-topnav_My-Work',
                'st-key-topnav_Ask-Agy',
                'st-key-topnav_Role-Match',
                'st-key-topnav_My-Profile'
            ];
            return classes.every(c => document.querySelector('.' + c) !== null);
        }
        """,
        timeout=timeout,
    )


def submit_query(page, query: str):
    """Type a question and submit it, on whichever input is showing.

    Landing view: press_sequentially + Tab (the path test_ask_mattgpt.py
    documents; fill() does not reach Streamlit's onChange). Conversation
    view: st.chat_input, fill + Enter.
    """
    chat_input = page.locator("[data-testid='stChatInput'] textarea")
    landing_input = page.locator("[class*='st-key-landing_input'] input[type='text']")
    if chat_input.count() > 0 and chat_input.first.is_visible():
        chat_input.first.fill(query)
        chat_input.first.press("Enter")
    else:
        landing_input.first.click()
        landing_input.first.press_sequentially(query, delay=20)
        landing_input.first.press("Tab")


_RECORDER_JS = """
(before) => {
    const sample = () => {
        const msgs = document.querySelectorAll("[data-testid='stChatMessage']");
        const n = msgs.length;
        const last = n ? msgs[n - 1] : null;
        const img = last ? last.querySelector('img') : null;
        const src = img ? (img.getAttribute('src') || '') : '';
        const md = last ? last.querySelector("[data-testid='stMarkdownContainer']") : null;
        window.__agyStream.samples.push({
            n: n,
            avatar: src.length + ':' + src.slice(-48),
            len: md ? md.innerText.trim().length : 0,
            thinking: document.querySelector('.thinking-modal') !== null,
        });
    };
    window.__agyStream = {before: before, samples: []};
    const observer = new MutationObserver(sample);
    observer.observe(document.body, {childList: true, subtree: true, characterData: true});
    const timer = setInterval(sample, 50);
    window.__agyStream.stop = () => { observer.disconnect(); clearInterval(timer); };
    sample();
}
"""


def _start_recorder(page, turn):
    turn["before"] = page.locator(CHAT_MESSAGE).count()
    page.evaluate(_RECORDER_JS, turn["before"])


def _wait_for_finished_turn(page, before):
    """The turn is finished when the visitor's message and Agy's are both
    newer than `before`, the newest carries its related projects, the
    thinking indicator is gone, and the answer text has held still."""
    page.wait_for_function(
        f"""() => {{
            const m = document.querySelectorAll("{CHAT_MESSAGE}");
            if (m.length < {before} + 2) return false;
            if (document.querySelector('.thinking-modal')) return false;
            return m[m.length - 1].querySelector('.source-links-title') !== null;
        }}""",
        timeout=TURN_TIMEOUT,
    )
    page.wait_for_function(
        f"""() => {{
            const m = document.querySelectorAll("{CHAT_MESSAGE}");
            const md = m[m.length - 1].querySelector("[data-testid='stMarkdownContainer']");
            const len = md ? md.innerText.trim().length : 0;
            const now = Date.now();
            if (window.__agySettle === undefined || window.__agySettle.len !== len) {{
                window.__agySettle = {{len: len, since: now}};
                return false;
            }}
            return now - window.__agySettle.since >= {SETTLE_MS};
        }}""",
        timeout=TURN_TIMEOUT,
        polling=100,
    )
    page.evaluate("() => { delete window.__agySettle; }")


def _finish_and_read(page, turn):
    _wait_for_finished_turn(page, turn["before"])
    samples = page.evaluate(
        "() => { window.__agyStream.stop(); return window.__agyStream.samples; }"
    )
    messages = page.locator(CHAT_MESSAGE)
    newest = messages.nth(messages.count() - 1)
    src = newest.locator("img").first.get_attribute("src") or ""
    turn["agy_avatar"] = f"{len(src)}:{src[-48:]}"
    # Measured the way the recorder measures (innerText, trimmed), so the
    # finished length and the samples compare on one ruler.
    turn["final_len"] = page.evaluate(
        f"""() => {{
            const m = document.querySelectorAll("{CHAT_MESSAGE}");
            const md = m[m.length - 1].querySelector("[data-testid='stMarkdownContainer']");
            return md ? md.innerText.trim().length : 0;
        }}"""
    )
    turn["samples"] = samples
    # Samples of Agy's message for this turn: newer than the messages before
    # the question, under Agy's avatar, with text.
    turn["agy_samples"] = [
        s
        for s in samples
        if s["n"] > turn["before"] and s["avatar"] == turn["agy_avatar"] and s["len"]
    ]


@pytest.fixture
def stream_turn():
    """State shared between the steps of one streamed turn."""
    return {}


# =============================================================================
# GIVEN
# =============================================================================


@given("the user navigates to Ask Agy")
def navigate_to_ask_agy(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    _wait_for_navbar_stable(browser_page)
    browser_page.locator(ASK_AGY_NAV_SELECTOR).first.click()
    wait_for_streamlit_rerun(browser_page)
    browser_page.wait_for_selector("[class*='st-key-landing_input']", timeout=15000)


@given("the user navigates to the home page")
def navigate_to_home(browser_page, app_url):
    """Home is the default tab; #card-product signals the cards rendered
    (mirrors test_home.py)."""
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    browser_page.wait_for_selector("#card-product", timeout=30000)


@given(parsers.parse('the user has asked "{query}"'))
def user_has_asked(browser_page, query):
    before = browser_page.locator(CHAT_MESSAGE).count()
    submit_query(browser_page, query)
    _wait_for_finished_turn(browser_page, before)


# =============================================================================
# WHEN
# =============================================================================


@when(parsers.parse('the user types "{query}" and watches the answer arrive'))
def type_and_watch(browser_page, stream_turn, query):
    stream_turn["question"] = query
    _start_recorder(browser_page, stream_turn)
    submit_query(browser_page, query)
    _finish_and_read(browser_page, stream_turn)


@when("the user clicks the first Home suggested chip and watches the answer arrive")
def click_chip_and_watch(browser_page, stream_turn):
    """Clicks the hidden Streamlit button behind the first chip, as
    test_home.py does (the JS bridge is covered there). The question is the
    chip's visible text, read from the page."""
    stream_turn["question"] = (
        browser_page.locator(f"#chip-ask-{HOME_CHIP_INDEX}").first.inner_text().strip()
    )
    assert stream_turn["question"], "The first Home suggested chip has no text."
    _start_recorder(browser_page, stream_turn)
    browser_page.locator(
        f"[class*='st-key-card_btn_ask_chip_{HOME_CHIP_INDEX}'] button"
    ).first.dispatch_event("click")
    _finish_and_read(browser_page, stream_turn)


# =============================================================================
# THEN
# =============================================================================


@then("the question is shown as the visitor's message")
def question_echoed(browser_page, stream_turn):
    messages = browser_page.locator(CHAT_MESSAGE)
    visitor = messages.nth(stream_turn["before"])
    text = visitor.inner_text()
    assert stream_turn["question"] in text, (
        f"Expected the visitor's message to show {stream_turn['question']!r};"
        f" it shows {text[:200]!r}."
    )
    src = visitor.locator("img").first.get_attribute("src") or ""
    assert (
        f"{len(src)}:{src[-48:]}" != stream_turn["agy_avatar"]
    ), "The question's message carries Agy's avatar, not the visitor's."


@then("Agy's answer text grows on screen before the turn finishes")
def answer_grows(stream_turn):
    lengths = []
    for s in stream_turn["agy_samples"]:
        if not lengths or s["len"] != lengths[-1]:
            lengths.append(s["len"])
    distinct = sorted(set(lengths))
    final = stream_turn["final_len"]
    assert len(distinct) >= MIN_DISTINCT_LENGTHS, (
        f"Expected Agy's answer to grow: at least {MIN_DISTINCT_LENGTHS} distinct"
        f" text lengths before the turn finished; saw {distinct} (finished length"
        f" {final}, {len(stream_turn['samples'])} samples)."
    )
    assert lengths[0] < final * FIRST_LENGTH_MAX_FRACTION, (
        f"Expected the first answer text seen to be under"
        f" {FIRST_LENGTH_MAX_FRACTION:.0%} of the finished length {final};"
        f" it was {lengths[0]}."
    )


@then("the thinking indicator is gone while the answer text grows")
def indicator_gone_while_growing(stream_turn):
    final = stream_turn["final_len"]
    partial = [s for s in stream_turn["agy_samples"] if s["len"] < final]
    assert partial, (
        "Expected samples of Agy's answer while it was still arriving (shorter"
        f" than the finished {final} characters); saw none."
    )
    with_indicator = [s for s in partial if s["thinking"]]
    assert not with_indicator, (
        f"The thinking indicator was on the page in {len(with_indicator)} of"
        f" {len(partial)} samples while Agy's answer text was arriving."
    )


@then("the finished turn shows one Agy answer with its related projects")
def one_finished_answer(browser_page, stream_turn):
    messages = browser_page.locator(CHAT_MESSAGE)
    count = messages.count()
    assert count == stream_turn["before"] + 2, (
        f"Expected the visitor's message and one Agy answer"
        f" ({stream_turn['before']} + 2 chat messages); found {count}."
    )
    newest = messages.nth(count - 1)
    assert (
        newest.locator(".source-links-title").count() == 1
    ), "Expected the finished Agy answer to carry its related projects."
    assert stream_turn["final_len"] > 0, "The finished Agy answer has no text."
