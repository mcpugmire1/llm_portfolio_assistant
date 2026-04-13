Feature: Role Match logging
  As a portfolio owner
  I want every Role Match interaction logged to the analytics sheet
  So that I can track recruiter engagement, identify which roles generate interest, and correlate assessments with chip clicks and actions

  # =============================================================================
  # ASSESSMENT SUBMISSION
  # =============================================================================

  Scenario: Successful assessment logs role_match_assessment with full metadata
    Given the user has submitted a job description
    And the assessment completes successfully
    Then a row with event type "role_match_assessment" is logged
    And the row contains the extracted role title
    And the row contains the extracted company
    And the row contains the required qualification count
    And the row contains the preferred qualification count
    And the row contains the strong match count
    And the row contains the partial match count
    And the row contains the gap count
    And the row contains a session ID

  Scenario: Narrative JD logs jd_format as narrative
    Given the user has submitted a narrative-style job description with no Required/Preferred sections
    And the assessment completes successfully
    Then the logged row contains jd_format "narrative"

  Scenario: Bulleted JD logs jd_format as bulleted
    Given the user has submitted a job description with explicit Required and Preferred sections
    And the assessment completes successfully
    Then the logged row contains jd_format "bulleted"

  Scenario: Failed assessment does not log a row
    Given the user has submitted a job description
    And the assessment fails with an error
    Then no "role_match_assessment" row is logged

  # =============================================================================
  # CHIP INTERACTION
  # =============================================================================

  Scenario: Chip expansion logs role_match_chip_click with story title and client
    Given the user has submitted a job description and results are displayed
    When the user clicks a story evidence chip
    Then a row with event type "role_match_chip_click" is logged
    And the row contains the story title
    And the row contains the client name
    And the row contains the same session ID as the assessment row

  Scenario: Closing a chip does not log an additional row
    Given the user has expanded a story evidence chip
    When the user clicks the same chip again to close it
    Then no additional "role_match_chip_click" row is logged

  # =============================================================================
  # ACTION BUTTONS
  # =============================================================================

  Scenario: Helpful click logs role_match_action with action helpful
    Given results are displayed
    When the user clicks Helpful
    Then a row with event type "role_match_action" is logged
    And the row contains action "helpful"
    And the row contains the same session ID as the assessment row

  Scenario: Copy Report click logs role_match_action with action copy_report
    Given results are displayed
    When the user clicks Report
    Then a row with event type "role_match_action" is logged
    And the row contains action "copy_report"
    And the row contains the same session ID as the assessment row

  Scenario: Export click logs role_match_action with action export
    Given results are displayed
    When the user clicks Export
    Then a row with event type "role_match_action" is logged
    And the row contains action "export"
    And the row contains the same session ID as the assessment row

  # =============================================================================
  # UTM ATTRIBUTION
  # =============================================================================

  Scenario: UTM parameters present are captured on assessment row
    Given the user arrived via a UTM-tagged URL
    And the user submits a job description
    When the assessment completes successfully
    Then the logged row contains the utm_source, utm_medium, utm_campaign, and utm_content values from the URL

  Scenario: UTM parameters missing logs with empty UTM fields
    Given the user arrived via a direct URL with no UTM parameters
    And the user submits a job description
    When the assessment completes successfully
    Then the logged row has empty UTM fields
    And no error occurs

  # =============================================================================
  # BOT FILTERING
  # =============================================================================

  Scenario: Known bot user agent does not produce a logged row
    Given the request has a user agent matching a MONITORING_BOT_SIGNATURES entry
    When an assessment completes
    Then no row is logged

  Scenario: Real browser user agent produces a logged row
    Given the request has a standard browser user agent
    When an assessment completes
    Then a "role_match_assessment" row is logged

  # =============================================================================
  # SESSION CORRELATION
  # =============================================================================

  Scenario: All event types from the same session share the same session_id
    Given the user submits a job description and the assessment completes
    And the user clicks a story evidence chip
    And the user clicks Helpful
    Then the role_match_assessment row, the role_match_chip_click row, and the role_match_action row all contain the same session_id value
    And the session_id is a valid UUID
