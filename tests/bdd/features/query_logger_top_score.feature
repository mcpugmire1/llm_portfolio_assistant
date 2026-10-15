Feature: Query logger records top_score

  Scenario: Top Score keeps its column position in HEADERS
    Given the query_logger module is imported
    Then "Top Score" is entry 33 in HEADERS, right after "Client"

  Scenario: top_score is written to the row when supplied
    Given a non-bot user agent is active
    When log_query is called with top_score 0.847
    Then the logged row contains 0.847 at the "Top Score" column

  Scenario: top_score defaults to empty string when not supplied
    Given a non-bot user agent is active
    When log_query is called without top_score
    Then the logged row contains "" at the "Top Score" column
