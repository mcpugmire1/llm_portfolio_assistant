Feature: Home Page Category Cards
  As a recruiter or hiring manager visiting Matt's portfolio
  I want each category card on the home page to deliver a curated slice
  So that I land on a focused set of stories that match what the card promised

  # Background:
  # Home is the default tab when the app loads. The 6 category cards live in
  # ui/components/category_cards.py. Cards 1+2 navigate to dedicated subpages
  # (Banking, Cross-Industry). Cards 3-6 set session prefilter keys and
  # navigate to Explore Stories, which reads those keys and applies the filter.
  #
  # The May 12, 2026 regression: Card 3 set prefilter_capability="Product
  # Leadership" — a value not present in any story's "Solution / Offering"
  # field. The Capability dropdown widget silently sanitized to "All", showing
  # 113 unfiltered stories. The card promise was broken: a recruiter expecting
  # "Product Innovation & Strategy" saw the entire corpus instead.
  #
  # The scenarios below assert post-navigation page STATE, not just that
  # navigation happened. See MATTGPT-060 in BACKLOG.md for the broader rollout.

  Background:
    Given the user navigates to the home page

  # ---------------------------------------------------------------------------
  # CARDS WITH SUBPAGE DESTINATIONS (full custom pages)
  # Documented as acceptance criteria. Step definitions pending — MATTGPT-060.
  # ---------------------------------------------------------------------------

  Scenario: Card 1 — Banking opens the Banking subpage
    When the user clicks "Explore Banking Work" on the Banking card
    Then the active tab should be "Banking"
    And the Banking subpage content should be visible

  Scenario: Card 2 — Cross-Industry opens the Cross-Industry subpage
    When the user clicks "Explore Stories" on the Cross-Industry Transformation card
    Then the active tab should be "Cross-Industry"
    And the Cross-Industry subpage content should be visible

  # ---------------------------------------------------------------------------
  # CARDS WITH PREFILTER INTO EXPLORE STORIES
  # Card 3 is the regression test — its step definitions are implemented in
  # test_home.py. Cards 4, 5, 6 are documented but pending step definitions.
  # ---------------------------------------------------------------------------

  Scenario: Card 3 — Product Innovation prefilters to product Sub-categories
    When the user clicks "View Product Work" on the Product Innovation card
    Then the active tab should be "Explore Stories"
    And the result count should be less than 113
    And a filter chip "User-Centered Product Strategy & Innovation" should be visible

  Scenario: Card 4 — Application Modernization prefilters by capability
    When the user clicks "View Case Studies" on the Application Modernization card
    Then the active tab should be "Explore Stories"
    And the result count should be less than 113
    And a filter chip "Application Modernization" should be visible

  Scenario: Card 5 — Consulting & Transformation prefilters to consulting Sub-categories
    When the user clicks "Browse Transformations" on the Consulting & Transformation card
    Then the active tab should be "Explore Stories"
    And the result count should be less than 113
    And a filter chip "Agile Planning & Value-Driven Delivery" should be visible

  Scenario: Card 6 — Teams & Talent Development prefilters to talent Sub-categories
    When the user clicks "Check Team Stories" on the Teams & Talent Development card
    Then the active tab should be "Explore Stories"
    And the result count should be less than 113
    And a filter chip "Talent Enablement & Growth" should be visible

  # ---------------------------------------------------------------------------
  # ASK AGY ANYTHING — suggested-question chips
  # New CX, May 13 2026. The bottom Quick Question card on Home grows from
  # one "Ask Agy" button + two static pills into a two-column card:
  #   left  — Ask Agy avatar + body copy + "Ask Agy 🐾" primary button
  #   right — "Try asking" label + 3 clickable suggested-question chips
  #
  # Plumbing pattern: mirrors ui/components/story_detail.py::on_ask_this_story
  # exactly. A chip click sets seed_prompt (the literal question string),
  # __ask_from_suggestion__ (True, to bypass nonsense-filter misfires), and
  # active_tab ("Ask MattGPT"), then calls st.rerun(). The Ask MattGPT page
  # (conversation_view.py:165) pops seed_prompt and fires the query
  # automatically. No new plumbing — just a new entry point onto a paved road.
  #
  # The "Ask Agy 🐾" button (left column) is the no-pre-population path —
  # navigates to Ask MattGPT and lands on the landing view, not a fired query.
  #
  # Eval entries 62-64 in tests/eval_rag_quality.py pin the response quality
  # for the three chip questions (CIC scale, startup-pace teams, resistance
  # handling).
  # ---------------------------------------------------------------------------

  Scenario: Ask Agy button navigates without pre-loading a question
    When the user clicks "Ask Agy 🐾" on the Ask Agy Anything card
    Then the active tab should be "Ask MattGPT"
    And no seed prompt should be present in session state

  Scenario: Clicking a suggested chip auto-fires the question on Ask MattGPT
    When the user clicks the suggested chip "How did Matt scale a Cloud Innovation Center from 0 to 150+ engineers?"
    Then the active tab should be "Ask MattGPT"
    And the seed prompt in session state should be "How did Matt scale a Cloud Innovation Center from 0 to 150+ engineers?"
    And the suggestion flag should be set in session state

  Scenario: Session state cleared after auto-fire
    Given the user arrived at Ask MattGPT via a chip click
    When the seed prompt has been consumed by the conversation view
    Then the seed prompt key should be absent from session state
    And refreshing the Ask MattGPT page should not re-fire the query

  Scenario: Ask MattGPT renders default landing when no chip was clicked
    Given the user navigates to Ask MattGPT directly
    When the page loads with no seed prompt in session state
    Then the Ask MattGPT landing view should render
    And no query should be auto-fired

  Scenario: Suggested chips render with directional affordance
    Then three suggested-question chips should be visible on the Ask Agy Anything card
    And each chip should display the ↗ directional affordance
    And each chip should be visually distinct from the "Ask Agy 🐾" primary button
