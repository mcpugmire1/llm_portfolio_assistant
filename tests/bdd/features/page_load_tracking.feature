Feature: UTM capture on page load
  As the portfolio owner
  I want to know where visitors come from
  So that I can understand which channels drive traffic

  # =============================================================================
  # UTM CAPTURE
  # =============================================================================

  Scenario: UTM params captured on page load
    Given a visitor arrives via URL with utm_source=linkedin&utm_medium=profile&utm_campaign=portfolio
    When the first-mount guard fires
    Then the page_load row contains UTM Source=linkedin, UTM Medium=profile, UTM Campaign=portfolio

  Scenario: UTM columns empty when no UTM params present
    Given a visitor arrives via direct URL with no UTM params
    When the first-mount guard fires
    Then UTM Source, UTM Medium, UTM Campaign, UTM Content, UTM Term are all empty strings

  # =============================================================================
  # MONITORING BOT FILTERING
  # =============================================================================

  Scenario: UptimeRobot requests do not generate page_load events
    Given a request arrives with User-Agent containing "UptimeRobot"
    When the first-mount guard fires
    Then log_page_load is not called

  Scenario: Real visitor requests still generate page_load events
    Given a request arrives with a standard browser User-Agent
    When the first-mount guard fires
    Then log_page_load is called

  Scenario: Multiple monitoring bot signatures are filtered
    Given MONITORING_BOT_SIGNATURES contains multiple entries
    When a request arrives with a User-Agent matching any entry
    Then log_page_load is not called

  Scenario: Requests with empty User-Agent do not generate page_load events
    Given a request arrives with no User-Agent header
    When the first-mount guard fires
    Then log_page_load is not called
