"""
BDD step bindings for the home category cards redesign (MATTGPT-107).

Red (step defs) gate state: step definitions are implemented and bound
via the scenarios() loader. Against current production (2-col grid with
gradient Banking + Cross-Industry cards, inline anchor "buttons" and
italic .hints lines):
  - Scenario 1 fails — .home-cat-card class does not exist yet; current
    production uses .capability-card. Locator wait times out.
  - Scenario 2 fails — same TimeoutError (no .home-cat-card to inspect).
  - Scenario 3 fails — same TimeoutError.
  - Scenario 4 fails — same TimeoutError; cannot click a non-existent
    .home-cat-card containing "Banking".

The coordinated redesign (rename .capability-card -> .home-cat-card,
drop gradient on Banking + Cross-Industry, 3-col grid, drop inline
buttons + .hints lines, extend JS bridge to the whole card body) lands
in the Green commit per the CLAUDE.md testing protocol.

Selectors:
  - .home-cat-card  — new card class rendered by Green (per ticket spec
    lines 2429-2459). Substring-stable across Streamlit class
    normalization (no st-key dependency).
  - .home-cat-title — inner card title element used to disambiguate
    cards by name when filtering.
  - .conversation-header h1 containing "Financial Services" — Banking
    landing distinctive marker (banking_landing.py:73).
  - [class*="st-key-topnav_"] — stable nav marker for the Background's
    page-ready wait (same as test_nav_labels.py / test_navbar_brand_layout.py).
"""

from pytest_bdd import given, scenarios, then, when

scenarios("../features/home_category_cards.feature")

SHORT_WAIT = 200  # ms
LONG_WAIT = 15000  # ms
ROW_Y_TOL = 5  # px tolerance for grouping cards into rows by y-coordinate


def wait_for_streamlit_rerun(page):
    """Wait for Streamlit to finish a rerun after an action."""
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


def _group_cards_by_row(page):
    """Group .home-cat-card elements by y-coordinate.

    Returns a list of (row_y, [bounding_boxes]) tuples sorted top-to-bottom.
    Two boxes are in the same row if their y-coordinates are within
    ROW_Y_TOL pixels of each other.
    """
    cards = page.locator(".home-cat-card").all()
    boxes = [c.bounding_box() for c in cards]
    boxes = [b for b in boxes if b is not None]
    if not boxes:
        return []
    boxes.sort(key=lambda b: b["y"])
    rows = []
    current_y = boxes[0]["y"]
    current_group = []
    for b in boxes:
        if abs(b["y"] - current_y) <= ROW_Y_TOL:
            current_group.append(b)
        else:
            rows.append((current_y, current_group))
            current_y = b["y"]
            current_group = [b]
    rows.append((current_y, current_group))
    return rows


@given("the user navigates to the home page")
def navigate_to_home(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    # Wait for the top navbar to render — stable marker that survives
    # pre/post Green on the Home page (the cards class changes but the
    # navbar is always present).
    browser_page.wait_for_selector('[class*="st-key-topnav_"]', timeout=30000)


# ---------------------------------------------------------------------------
# Scenario 1 — 3-column grid (6 cards in 2 rows of 3)
# ---------------------------------------------------------------------------


@then("the home page should display 6 category cards")
def assert_six_cards(browser_page):
    browser_page.wait_for_selector(".home-cat-card", timeout=LONG_WAIT)
    count = browser_page.locator(".home-cat-card").count()
    assert count == 6, (
        f"Expected 6 category cards on the home page; found {count}. "
        f"MATTGPT-107 wireframe locks the 6-card layout (Banking, "
        f"Cross-Industry, Product Innovation, App Modernization, "
        f"Consulting Leadership, AI / Cloud Acceleration)."
    )


@then("the first row of category cards should contain exactly 3 cards")
def assert_first_row_three(browser_page):
    rows = _group_cards_by_row(browser_page)
    assert rows, (
        "No category cards found on the home page — cannot evaluate "
        "row grouping for the 3-column grid assertion."
    )
    assert len(rows[0][1]) == 3, (
        f"First row should contain 3 cards; got {len(rows[0][1])}. "
        f"MATTGPT-107 wireframe locks a 3-column grid at desktop. "
        f"Row y-coords + sizes: "
        f"{[(round(r[0]), len(r[1])) for r in rows]}"
    )


@then("the second row of category cards should contain exactly 3 cards")
def assert_second_row_three(browser_page):
    rows = _group_cards_by_row(browser_page)
    assert len(rows) >= 2, (
        f"Expected at least 2 rows of category cards; got {len(rows)}. "
        f"MATTGPT-107: 6 cards in a 3-col grid = 2 rows of 3."
    )
    assert len(rows[1][1]) == 3, (
        f"Second row should contain 3 cards; got {len(rows[1][1])}. "
        f"Row y-coords + sizes: "
        f"{[(round(r[0]), len(r[1])) for r in rows]}"
    )


# ---------------------------------------------------------------------------
# Scenario 2 — unified light-bg treatment (no purple gradient)
# ---------------------------------------------------------------------------


@then("no category card should use a purple gradient background")
def assert_no_gradient(browser_page):
    browser_page.wait_for_selector(".home-cat-card", timeout=LONG_WAIT)
    cards = browser_page.locator(".home-cat-card").all()
    offenders = []
    for i, card in enumerate(cards):
        bg_image = card.evaluate("el => getComputedStyle(el).backgroundImage")
        if "gradient" in (bg_image or "").lower():
            title_loc = card.locator(".home-cat-title")
            label = title_loc.inner_text() if title_loc.count() else f"card #{i}"
            offenders.append(f"{label!r}: background-image={bg_image}")
    assert not offenders, (
        f"{len(offenders)} category card(s) still use a gradient "
        f"background: {offenders}. MATTGPT-107: unified light-bg "
        f"treatment across all 6 cards; drop the purple gradient on "
        f"Banking + Cross-Industry."
    )


# ---------------------------------------------------------------------------
# Scenario 3 — compact content (no inline button, no italic example-question)
# ---------------------------------------------------------------------------


@then("no category card should contain an inline button element")
def assert_no_inline_button(browser_page):
    browser_page.wait_for_selector(".home-cat-card", timeout=LONG_WAIT)
    button_count = browser_page.locator(".home-cat-card button").count()
    anchor_btn_count = browser_page.locator(
        ".home-cat-card a[class*='card-btn']"
    ).count()
    total = button_count + anchor_btn_count
    assert total == 0, (
        f"Found {button_count} <button> and {anchor_btn_count} "
        f"<a class*='card-btn'> element(s) inside category cards. "
        f"MATTGPT-107: drop the visible inline button — the whole card "
        f"is the click target via the existing JS bridge."
    )


@then("no category card should contain an italic example-question line")
def assert_no_italic_hint(browser_page):
    browser_page.wait_for_selector(".home-cat-card", timeout=LONG_WAIT)
    # Production uses .hints (CSS sets font-style: italic). Post-Green
    # the .hints div is removed from card content. Also guard against
    # <em>/<i> tags appearing as a different encoding of the same idea.
    hint_count = browser_page.locator(".home-cat-card .hints").count()
    italic_count = browser_page.locator(".home-cat-card em, .home-cat-card i").count()
    total = hint_count + italic_count
    assert total == 0, (
        f"Found {hint_count} .hints and {italic_count} <em>/<i> "
        f"element(s) inside category cards. MATTGPT-107: drop the "
        f"italic example-question lines; card content is "
        f"icon + title + one meta line."
    )


# ---------------------------------------------------------------------------
# Scenario 4 — whole-card click routes to Banking landing
# ---------------------------------------------------------------------------


@when('the user clicks anywhere inside the "Banking" category card')
def click_banking_card(browser_page):
    browser_page.wait_for_selector(".home-cat-card", timeout=LONG_WAIT)
    # Disambiguate "Banking" from any other card by requiring its
    # .home-cat-title to contain "Banking" (avoids matching cards that
    # mention banking in their meta line).
    card = (
        browser_page.locator(".home-cat-card")
        .filter(has=browser_page.locator(".home-cat-title", has_text="Banking"))
        .first
    )
    assert card.count() > 0, (
        "No .home-cat-card with title text 'Banking' found on the home "
        "page. MATTGPT-107: Banking card must remain titled 'Banking' "
        "after the redesign."
    )
    card.click()
    wait_for_streamlit_rerun(browser_page)


@then("the Banking landing surface should be shown")
def assert_banking_landing(browser_page):
    # banking_landing.py:73 renders
    #   <h1>Matt's Financial Services Expertise</h1>
    # inside .conversation-header. That heading text is unique to the
    # Banking landing surface and unaffected by MATTGPT-107.
    heading = browser_page.locator(
        ".conversation-header h1", has_text="Financial Services"
    ).first
    heading.wait_for(state="visible", timeout=LONG_WAIT)
    assert heading.count() > 0, (
        "Banking landing distinctive heading ('Matt's Financial "
        "Services Expertise') did not appear after clicking the "
        "Banking category card. MATTGPT-107: whole-card click must "
        "route via the existing JS bridge + active_tab/prefilter_* "
        "pattern."
    )
