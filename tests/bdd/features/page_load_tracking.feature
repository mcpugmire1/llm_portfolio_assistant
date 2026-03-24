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
