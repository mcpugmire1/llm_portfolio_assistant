Feature: Navbar CSS scope guard prevents chip grid regression (MATTGPT-110 fix)
  As a developer shipping new layout features
  I want the navbar's gap-zeroing CSS to be scoped to the navbar only
  So that other stHorizontalBlock layouts (e.g. Ask Agy chip grid) are not affected

  # Regression guard for the MATTGPT-110 fix to navbar.py:
  # The broad CSS rule "stHorizontalBlock > stColumn:first-child stVerticalBlock { gap: 0 }"
  # was zeroing row-gap on the Ask Agy chip grid's left column, causing unequal chip heights.
  # Fix: added :has([class*="st-key-topnav_"]) guard, scoping the rule to navbar only.
  # This scenario catches any reintroduction of a broad gap-zeroing rule.

  Scenario: Navbar CSS does not collapse Ask Agy chip grid spacing
    Given the user navigates to the Ask Agy landing page
    Then the left chip column row-gap should equal the right chip column row-gap
    And the left chip column row-gap should be greater than 0px
    And the navbar brand column row-gap should be 0px
