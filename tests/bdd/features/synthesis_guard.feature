Feature: Synthesis path graceful degradation

  Scenario: synthesis path with empty theme pool degrades gracefully instead of raising
    Given stories are loaded for the synthesis guard test
    And portfolio theme metadata is empty
    When rag_answer is called with the synthesis query "Why should we hire Matt?"
    Then no exception is raised
    And the response has at least one source
