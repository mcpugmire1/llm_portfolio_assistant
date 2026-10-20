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
    # Note: UptimeRobot free tier sends empty User-Agent, not a signature.
    # Caught by the empty User-Agent guard, not the signature check.
    Given a request arrives from UptimeRobot with an empty User-Agent
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

  # =============================================================================
  # BROWSER-SIDE CONTEXT (page_context)
  # =============================================================================
  # On Streamlit Cloud the server only ever sees Cloud's own page as the
  # referrer, so a second row, page_context, records what the browser
  # reports (window.top.document.referrer and window.innerWidth) once the
  # screen-size capture returns. page_load is unchanged; the two rows share
  # a Session ID.

  Scenario: A UTM link logs its UTM values alongside the browser-side referrer
    Given a visitor arrives via URL with utm_source=linkedin&utm_medium=profile&utm_campaign=portfolio
    And the browser reports referrer https://www.linkedin.com/ and viewport width 1440
    When the page loads and the browser reports its context
    Then the page_load row contains UTM Source=linkedin, UTM Medium=profile, UTM Campaign=portfolio
    And the page_context row contains Referrer=https://www.linkedin.com/, Screen Width=1440, UTM Source=linkedin, UTM Medium=profile, UTM Campaign=portfolio
    And the page_context row has the page_load row's Session ID

  Scenario: The mobile gate reads the same screen width as before
    Given a request arrives with a standard browser User-Agent
    And the browser reports referrer https://www.linkedin.com/ and viewport width 1440
    When the page loads and the browser reports its context
    Then the mobile gate reads a screen width of 1440

  Scenario: Later rows in the session carry the browser-side referrer
    Given a request arrives with a standard browser User-Agent
    And the browser reports referrer https://www.linkedin.com/ and viewport width 1440
    When the page loads and the browser reports its context
    Then later rows in the session carry Referrer https://www.linkedin.com/

  Scenario: One page_context row per session
    Given a request arrives with a standard browser User-Agent
    And the browser reports referrer https://www.linkedin.com/ and viewport width 1440
    When the page loads and the browser reports its context
    And the visitor keeps using the app
    Then exactly one page_context row is written

  Scenario: No page_context row until the browser reports
    Given a request arrives with a standard browser User-Agent
    And the browser has not reported its context yet
    When the page loads and the browser reports its context
    Then log_page_load is called
    And no page_context row is written

  Scenario: Monitoring bots get no page_context row
    Given MONITORING_BOT_SIGNATURES contains multiple entries
    And a request arrives with a User-Agent matching each entry
    And the browser reports referrer https://www.linkedin.com/ and viewport width 1440
    When the page loads and the browser reports its context
    Then no page_context row is written
