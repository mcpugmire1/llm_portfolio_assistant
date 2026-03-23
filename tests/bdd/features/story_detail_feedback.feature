Feature: Helpful button on story detail
  As a visitor viewing a story detail
  I want to mark a story as helpful
  So that the portfolio owner receives feedback on which stories resonate

  Background:
    Given the user navigates to the Explore Stories page
    And the page has finished loading
    And the user has opened a story detail

  # =============================================================================
  # RENDER
  # =============================================================================

  Scenario: Helpful button renders in story detail action row
    Then a "👍 Helpful" button appears in the detail-actions row
    And the button appears to the left of "🔗 Share" and "📄 Export"
    And the button is enabled and unrated

  # =============================================================================
  # CONFIRMED STATE
  # =============================================================================

  Scenario: Helpful click confirmed state
    When the user clicks the "👍 Helpful" button
    Then the button label changes to "👍 Helpful ✓"
    And the button fills with var(--success-color)
    And the button is disabled
    And log_feedback is called with rating="up" and the story title

  Scenario: Confirmed state persists within session
    Given the user has clicked the "👍 Helpful" button
    When Streamlit reruns
    Then the Helpful button still shows "👍 Helpful ✓" with green fill
    And the button remains disabled

  # =============================================================================
  # MOBILE
  # =============================================================================

  Scenario: Helpful button follows existing mobile behavior
    Given a story detail is rendered at 375px viewport
    Then the Helpful button is not visible
    And the button is hidden along with Share and Export via existing .detail-actions CSS
    And no existing mobile CSS rules are modified
