Feature: Home Page Category Cards
  As a recruiter or hiring manager visiting Matt's portfolio
  I want each category card on the home page to deliver a curated slice
  So that I land on a focused set of stories that match what the card promised

  # Background:
  # Home is the default tab when the app loads. The 6 category cards live in
  # ui/components/category_cards.py. Cards 1+2 navigate to dedicated subpages
  # (Banking, Cross-Industry). Cards 3-6 set session prefilter keys and
  # navigate to My Work, which reads those keys and applies the filter.
  #
  # The May 12, 2026 regression: Card 3 set prefilter_capability="Product
  # Leadership" — a value not present in any story's "Solution / Offering"
  # field. The Capability dropdown widget silently sanitized to "All", showing
  # 100+ unfiltered stories. The card promise was broken: a recruiter expecting
  # "Product Innovation & Strategy" saw the entire corpus instead.
  #
  # The scenarios below assert post-navigation page STATE, not just that
  # navigation happened. See MATTGPT-060 in BACKLOG.md for the broader rollout.

  Background:
    Given the user navigates to the home page

  # ---------------------------------------------------------------------------
  # CARDS WITH SUBPAGE DESTINATIONS (full custom pages)
  # The When step clicks each card's hidden card_btn_* button, isolating the
  # routing logic; the visible-card JS bridge has its own coverage in
  # home_category_cards.feature.
  # ---------------------------------------------------------------------------

  Scenario: Card 1: Banking opens the Banking subpage
    When the user clicks the "Banking" category card
    Then the active tab should be "Banking"
    And the landing card grid should be visible

  Scenario: Card 2: Cross-Industry opens the Cross-Industry subpage
    When the user clicks the "Cross-Industry" category card
    Then the active tab should be "Cross-Industry"
    And the landing card grid should be visible

  # ---------------------------------------------------------------------------
  # CARDS WITH PREFILTER INTO MY WORK
  # Card 3 is the May 12 regression test. The count bound is derived from the
  # corpus (stories outside Professional Narrative), not hardcoded.
  # Cards 3, 5 and 6 list every Sub-category their card sets (category_cards.py);
  # all must show as chips. They are xfail under MATTGPT-331 (My Work keeps
  # only the first) until that is fixed.
  # ---------------------------------------------------------------------------

  Scenario: Card 3: Product Innovation prefilters to product Sub-categories
    When the user clicks the "Product Innovation" category card
    Then the active tab should be "My Work"
    And the result count should be less than the unfiltered My Work total
    And these filter chips should be visible:
      | User-Centered Product Strategy & Innovation |
      | Product Strategy & Innovation |
      | Product Management |
      | Digital Product Development & Delivery |
      | Client Product Innovation & Co-Creation |

  Scenario: Card 4: Application Modernization prefilters by capability
    When the user clicks the "Application Modernization" category card
    Then the active tab should be "My Work"
    And the result count should be less than the unfiltered My Work total
    And a filter chip "Application Modernization" should be visible

  Scenario: Card 5: Consulting & Transformation prefilters to consulting Sub-categories
    When the user clicks the "Consulting & Transformation" category card
    Then the active tab should be "My Work"
    And the result count should be less than the unfiltered My Work total
    And these filter chips should be visible:
      | Agile Planning & Value-Driven Delivery |
      | Leadership & Continuous Improvement |
      | Agile Transformation & Leadership Enablement |
      | Technology Strategy & Advisory Services |
      | Strategic Client Partnerships |
      | Cross-Functional Collaboration & Alignment |
      | Process Optimization & Automation |
      | Security & Compliance Solutions |

  Scenario: Card 6: Teams & Talent Development prefilters to talent Sub-categories
    When the user clicks the "Teams & Talent Development" category card
    Then the active tab should be "My Work"
    And the result count should be less than the unfiltered My Work total
    And these filter chips should be visible:
      | Client Upskilling & Enablement |
      | Cross-Functional Team Enablement |
      | Psychological Safety & Innovation Culture |
      | Talent Enablement & Growth |

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
  # active_tab ("Ask Agy"), then calls st.rerun(). The Ask Agy page
  # (conversation_view.py:165) pops seed_prompt and fires the query
  # automatically. No new plumbing — just a new entry point onto a paved road.
  #
  # The "Ask Agy 🐾" button (left column) is the no-pre-population path —
  # navigates to Ask Agy and lands on the landing view, not a fired query.
  #
  # Eval entries 62-64 in tests/eval_rag_quality.py pin the response quality
  # for the three chip questions (CIC scale, startup-pace teams, resistance
  # handling).
  # ---------------------------------------------------------------------------

  Scenario: Ask Agy button navigates without pre-loading a question
    When the user clicks "Ask Agy 🐾" on the Ask Agy Anything card
    Then the active tab should be "Ask Agy"
    And the Ask Agy landing should render with no conversation

  Scenario: Clicking a suggested chip auto-fires the question on Ask Agy
    When the user clicks the suggested chip "How did Matt scale a Cloud Innovation Center from 0 to 150+ engineers?"
    Then the active tab should be "Ask Agy"
    And the seed prompt in session state should be "How did Matt scale a Cloud Innovation Center from 0 to 150+ engineers?"
    And the suggestion flag should be set in session state

  # Live: one real answer to chip 0. Playwright can't read session state, so
  # "the seed prompt was consumed" is asserted through the DOM: going Home and
  # back to Ask Agy shows the same transcript, with the question once.
  Scenario: Returning to Ask Agy after a chip auto-fire does not fire it again
    Given the user clicked the suggested chip "How did Matt scale a Cloud Innovation Center from 0 to 150+ engineers?" and its answer finished
    When the user goes Home and returns to Ask Agy
    Then the chip question should appear exactly once in the conversation
    And the conversation should have the same number of messages as before

  Scenario: Ask Agy renders default landing when no chip was clicked
    When the user clicks the "Ask Agy" navigation label
    Then the active tab should be "Ask Agy"
    And the Ask Agy landing should render with no conversation

  Scenario: Suggested chips render with directional affordance
    Then three suggested-question chips should be visible on the Ask Agy Anything card
    And each chip should display the ↗ directional affordance
    And each chip should be visually distinct from the "Ask Agy 🐾" primary button
