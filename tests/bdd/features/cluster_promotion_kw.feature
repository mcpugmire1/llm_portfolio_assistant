Feature: Entity cluster promotion kw-uniformity gate (MATTGPT-074)

  Scenario: cluster promotion fires in the baseline case
    Given a pool of 3 entity-matched stories with uniform kw scores
    When rag_answer is called with an entity query
    Then synthesis mode is triggered

  Scenario: dispersed kw across entity pool suppresses promotion
    Given a pool of 3 entity-matched stories with dispersed kw scores
    When rag_answer is called with an entity query
    Then synthesis mode is suppressed

  Scenario: all-zero kw across entity pool allows promotion
    Given a pool of 3 entity-matched stories with all-zero kw scores
    When rag_answer is called with an entity query
    Then synthesis mode is triggered

  Scenario: fewer than 3 entity stories with uniform kw does not promote
    Given a pool of 2 entity-matched stories with uniform kw scores
    When rag_answer is called with an entity query
    Then synthesis mode is suppressed
