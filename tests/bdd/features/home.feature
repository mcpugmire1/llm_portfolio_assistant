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
