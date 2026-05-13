Feature: Banking Landing Page Capability Cards
  As a recruiter or hiring manager interested in Matt's banking work
  I want the Banking landing page to surface real, browsable capability slices
  So that every card I click delivers a focused view of actual banking projects

  # Background:
  # Banking landing page lives in ui/pages/banking_landing.py. As of the Phase 2
  # refactor (May 12, 2026), cards are data-derived via build_landing_cards()
  # from utils/landing_cards.py — not a hardcoded list.
  #
  # The data-derivation rule eliminates by construction the May 12 Card 3
  # regression shape: no card can reference a Solution/Offering value that
  # doesn't exist in the data, because cards ARE the data.
  #
  # Era exclusion: stories with Era=="Leadership & Professional Narrative"
  # don't contribute to capability cards (mirrors timeline_view.py rule).
  #
  # Cards are tiered: Core Capabilities (>=3 banking stories) and
  # Specialized Capabilities (<3 banking stories).

  Background:
    Given the user navigates to the Banking landing page

  # ---------------------------------------------------------------------------
  # REGRESSION TEST — fully wired
  # The contract pinned here is what the data-derivation refactor guarantees:
  # any card visible on the page leads to a non-empty Explore Stories result.
  # If this fails, the page is showing a card that doesn't exist in the data.
  # ---------------------------------------------------------------------------

  Scenario: Clicking the top Core capability card lands on a filtered Explore Stories with results
    When the user clicks the top capability card
    Then the active tab should be "Explore Stories"
    And the result count should be greater than 0

  # ---------------------------------------------------------------------------
  # DOCUMENTED CONTRACTS — step defs pending (MATTGPT-060)
  # These scenarios describe the broader page behavior post-refactor. They are
  # acceptance criteria for code reviewers and future test authoring sessions,
  # not yet runnable.
  # ---------------------------------------------------------------------------

  Scenario: Banking landing shows Core and Specialized tier sections
    Then the page should display a "Core Capabilities" section header
    And the page should display a "Specialized Capabilities" section header

  Scenario: No capability card on the page shows zero projects
    Then every visible capability card should report at least 1 banking project

  Scenario: Capability cards do not include narrative-era stories
    Then no card should be derived from stories with Era "Leadership & Professional Narrative"

  Scenario: Capability subtitles render when curated
    Then capability cards with a CAPABILITY_SUBTITLES entry should display the subtitle text
    And capability cards without an entry should render without a subtitle
