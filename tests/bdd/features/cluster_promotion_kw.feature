Feature: Entity cluster promotion content-kw gate (MATTGPT-074)

  Scenario: entity name in one story title no longer disperses kw
    Given a pool of 3 Liquid Studio stories where one title contains the entity name
    When rag_answer is called with a broad Liquid Studio query
    Then synthesis mode is triggered

  Scenario: content tokens beyond the entity name still disperse kw
    Given a pool of 3 AT&T stories where one title contains production incident vocabulary
    When rag_answer is called with a production incident AT&T query
    Then synthesis mode is suppressed

  Scenario: query that resolves via alias strips the alias key as well as the canonical tokens
    Given a pool of 3 CIC stories where one title contains the alias cic and the query resolves via alias to Division Cloud Innovation Center
    When rag_answer is called with a broad CIC query using the alias
    Then synthesis mode is triggered

  Scenario: alias-matched query with specific content tokens still disperses kw
    Given a pool of 3 American Express stories where one title contains production incident vocabulary
    When rag_answer is called with an amex production incident query
    Then synthesis mode is suppressed

  Scenario: stripped query with no content tokens left promotes to synthesis
    Given a pool of 3 RBC stories with no content tokens in the query
    When rag_answer is called with a bare entity-only RBC query
    Then synthesis mode is triggered

  # Corpus-dependent: promotes because "work" is absent from all Fiserv haystack fields. See MATTGPT-074.
  Scenario: possessive entity query promotes when ambient words do not appear in story fields
    Given a pool of 3 Fiserv stories where no story field contains the word work
    When rag_answer is called with a possessive Fiserv query
    Then synthesis mode is triggered

  Scenario: gate strips entity tokens from the retrieval query not the original question
    Given a pool of 3 CIC stories where one story summary mentions Matt by name
    When rag_answer is called with a broad CIC query in the technical intent family
    Then synthesis mode is triggered

  Scenario: fewer than 3 entity stories does not promote even with uniform kw
    Given a pool of 2 Liquid Studio stories where no title contains the entity name
    When rag_answer is called with a broad Liquid Studio query
    Then synthesis mode is suppressed
