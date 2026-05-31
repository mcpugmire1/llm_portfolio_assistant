Feature: Home category cards — unified 3-col grid + whole-card click (MATTGPT-107)
  As a recruiter or warm CTO landing on the home page
  I want the category cards to render as a uniform 3-column grid where
  each card body is itself the click target (no inline button)
  So that the home page reads as a clean, scannable entry point that
  matches the May 29, 2026 wireframe (lines 76-85 of
  MATTGPT_WIREFRAMES.html)

  # MATTGPT-107. Visual-only redesign locked to wireframe + May 31, 2026
  # handoff. Three real changes from current production:
  #   1. Unified card treatment — drop the purple gradient on Banking
  #      and Cross-Industry cards. All 6 share the same light-bg
  #      secondary treatment.
  #   2. 3-column grid (was 2). Responsive: 2 cols at <=1024px, 1 col
  #      at <=640px.
  #   3. Compact card content — drop the inline buttons and italic
  #      example-question lines. Card body is icon + title + one meta
  #      line. The entire card is the click target.
  #
  # OUT OF SCOPE per the ticket:
  #   - Routing model migration. The existing
  #     JS-bridge + hidden Streamlit button + active_tab / prefilter_*
  #     routing pattern in category_cards.py stays. Anchor + query-param
  #     routing is a separate ticket if wanted later.
  #   - Emojis for icons stay (move to SVG/Tabler later as a separate
  #     ticket).
  #   - Quick question strip below the cards is a separate concern.
  #
  # Scenarios assert DOM-observable state — visible card count, row
  # grouping via bounding-box y-coordinates, computed background style,
  # absence of inline button / italic content, and post-click destination
  # surface. No st.session_state reads — see
  # feedback_bdd_dom_observable.

  Background:
    Given the user navigates to the home page

  Scenario: All six category cards render in a 3-column grid on desktop
    Then the home page should display 6 category cards
    And the first row of category cards should contain exactly 3 cards
    And the second row of category cards should contain exactly 3 cards

  Scenario: All six category cards share the unified light-background treatment
    Then no category card should use a purple gradient background

  Scenario: Each category card uses compact content (icon + title + meta only)
    Then no category card should contain an inline button element
    And no category card should contain an italic example-question line

  Scenario: Clicking anywhere on the Banking card routes to the Banking landing surface
    When the user clicks anywhere inside the "Banking" category card
    Then the Banking landing surface should be shown
