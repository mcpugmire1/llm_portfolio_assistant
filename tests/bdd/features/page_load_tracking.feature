Feature: Production-only logging and UTM capture
  As the portfolio owner
  I want to know where visitors come from and prevent eval noise in the log
  So that I can understand traffic sources and keep the query log clean

  # =============================================================================
  # PRODUCTION GUARD
  # =============================================================================

  Scenario: Logging skipped outside production
    Given MATTGPT_ENV is not set to "production"
    When log_query() or log_page_load() is called
    Then no write is made to Google Sheets

  Scenario: Logging fires in production
    Given MATTGPT_ENV is set to "production"
    When log_page_load() is called
    Then a page_load row is written to Google Sheets

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
