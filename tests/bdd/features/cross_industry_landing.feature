Feature: Cross-Industry Landing Page Capability Cards
  As a recruiter or hiring manager interested in Matt's cross-industry work
  I want the Cross-Industry landing page to surface real, browsable capability slices
  So that every card I click delivers a focused view of actual cross-industry projects

  # Background:
  # Cross-Industry landing page lives in ui/pages/cross_industry_landing.py.
  # As of the Phase 2 part B refactor (May 12, 2026), cards are data-derived
  # via build_landing_cards() from utils/landing_cards.py — not a hardcoded list.
  #
  # Symmetry with Banking landing: same data-derivation rule, same tiered
  # hierarchy (Core / Specialized Capabilities), same CAPABILITY_SUBTITLES
  # consumption, same EXCLUDED_ERA filter applied.
  #
  # Cross-Industry's pre-refactor hardcoded list of 11 categories all happened
  # to be valid Solution/Offering values (no broken cards), so this refactor
  # is structural alignment, not a bug fix. The drift surface is eliminated.

  Background:
    Given the user navigates to the Cross-Industry landing page

  # ---------------------------------------------------------------------------
  # REGRESSION TEST — fully wired
  # Pins the post-refactor structure: Core Capabilities section header must
  # be present. This intentionally fails against the pre-refactor page (which
  # has no tier sections — just a flat 11-card grid), giving a meaningful
  # RED state before implementation.
  # ---------------------------------------------------------------------------

  Scenario: Cross-Industry landing displays the Core Capabilities tier header
    Then the page should display a "Core Capabilities" section header

  Scenario: Clicking the top Core capability card lands on a filtered Explore Stories with results
    When the user clicks the top capability card
    Then the active tab should be "Explore Stories"
    And the result count should be greater than 0

  # ---------------------------------------------------------------------------
  # DOCUMENTED CONTRACTS — step defs pending (MATTGPT-060)
  # ---------------------------------------------------------------------------

  Scenario: Cross-Industry landing shows Specialized tier section
    Then the page should display a "Specialized Capabilities" section header

  Scenario: No capability card on the page shows zero projects
    Then every visible capability card should report at least 1 cross-industry project

  Scenario: Capability cards do not include narrative-era stories
    Then no card should be derived from stories with Era "Leadership & Professional Narrative"
