Feature: Fatal fallback handler degradation marking

  Scenario: Pipeline crash inside the outer try produces a marked logged degraded response
    Given stories are loaded for the fatal fallback handler test
    When rag_answer is called with a semantic_search that raises RuntimeError
    Then the returned dict has degraded equal to True
    And an exception traceback was logged unconditionally

  Scenario: Successful responses are not marked degraded
    Given stories are loaded for the fatal fallback handler test
    When rag_answer is called with a fully mocked happy-path pipeline
    Then the returned dict has degraded equal to False
