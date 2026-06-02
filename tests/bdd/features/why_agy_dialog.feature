Feature: Why Agy? — "i" badge triggers origin story dialog

  Background:
    Given the MattGPT app is running at "http://localhost:8501"

  # ── Home hero (all viewports) ────────────────────────────

  Scenario: Badge renders on Home hero illustration on desktop
    Given I navigate to the Home page at viewport width 1280
    Then the Home hero illustration wrapper has a visible "i" badge

  Scenario: Badge renders on Home hero illustration on mobile
    Given I navigate to the Home page at viewport width 390
    Then the Home hero illustration wrapper has a visible "i" badge

  # ── Ask Agy landing body (all viewports) ─────────────────

  Scenario: Badge renders on Ask Agy landing body avatar on desktop
    Given I navigate to the "Ask Agy" page at viewport width 1280
    Then the Agy intro avatar has a visible "i" badge

  Scenario: Badge renders on Ask Agy landing body avatar on mobile
    Given I navigate to the "Ask Agy" page at viewport width 390
    Then the Agy intro avatar has a visible "i" badge

  # ── Ask Agy header (desktop only) ────────────────────────

  Scenario: Badge renders on Ask Agy header avatar on desktop
    Given I navigate to the "Ask Agy" page at viewport width 1280
    Then the Ask Agy header avatar has a visible "i" badge

  Scenario: No badge on Ask Agy header avatar on mobile
    Given I navigate to the "Ask Agy" page at viewport width 390
    Then the Ask Agy header avatar does not have a visible "i" badge

  # ── Banking Landing header (desktop only) ─────────────────

  Scenario: Badge renders on Banking Landing header avatar on desktop
    Given I navigate to the Banking landing page at viewport width 1280
    Then the header avatar has a visible "i" badge

  # ── Cross-Industry Landing header (desktop only) ──────────

  Scenario: Badge renders on Cross-Industry Landing header avatar on desktop
    Given I navigate to the Cross-Industry landing page at viewport width 1280
    Then the header avatar has a visible "i" badge

  # ── Dialog content (triggered via Ask Agy landing body) ───

  Scenario: Clicking badge opens Why Agy dialog
    Given I navigate to the "Ask Agy" page at viewport width 1280
    When I click the "i" badge on the Agy intro avatar
    Then a dialog with title "Why Agy?" is visible

  Scenario: Why Agy dialog body contains Plott Hound copy and story count
    Given I navigate to the "Ask Agy" page at viewport width 1280
    And I click the "i" badge on the Agy intro avatar
    Then the dialog body contains "Plott Hound"
    And the dialog body contains "100+"
    And the dialog body contains "tracking"

  Scenario: Why Agy dialog has italicized closing line
    Given I navigate to the "Ask Agy" page at viewport width 1280
    And I click the "i" badge on the Agy intro avatar
    Then the dialog contains an italic element with text beginning "It felt right"

  Scenario: Why Agy dialog footer button text matches spec
    Given I navigate to the "Ask Agy" page at viewport width 1280
    And I click the "i" badge on the Agy intro avatar
    Then the dialog contains a button with text "Curious how I was built? Read the technical deep-dive →"

  # ── Sequential dialog ─────────────────────────────────────

  Scenario: Clicking footer button closes the Why Agy dialog
    Given I navigate to the "Ask Agy" page at viewport width 1280
    And I click the "i" badge on the Agy intro avatar
    And a dialog with title "Why Agy?" is visible
    When I click the button "Curious how I was built? Read the technical deep-dive →"
    Then no dialog with title "Why Agy?" is visible
