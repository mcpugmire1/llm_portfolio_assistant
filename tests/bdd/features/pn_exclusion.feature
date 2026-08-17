Feature: Professional Narrative exclusion from technical-family retrieval (MATTGPT-169)

  Scenario: technical family excludes Professional Narrative stories from sources
    Given a mixed pool containing non-narrative and Professional Narrative stories
    When rag_answer is called with intent family "technical"
    Then no Professional Narrative story appears in sources

  Scenario: non-technical family preserves Professional Narrative stories in sources
    Given a mixed pool containing non-narrative and Professional Narrative stories
    When rag_answer is called with intent family "background"
    Then a Professional Narrative story appears in sources

  Scenario: guard prevents empty pool when all candidates are Professional Narrative
    Given a pool containing only Professional Narrative stories
    When rag_answer is called with intent family "technical"
    Then sources are not empty
