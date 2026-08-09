Feature: MATTGPT-077 retrieval query strip for Matt-subject queries
  As the RAG pipeline
  I want to strip "Matt" and "Matt's" from the retrieval query on
  technical, team_scaling, and agile_transformation intent families
  So that self-referential tokens don't bias embeddings toward
  Independent Project stories over topically-relevant named-client stories

  # Pure unit tests -- no Playwright, no API calls, no Pinecone.
  # Tests _strip_matt_subject() and _build_retrieval_query() in utils/scoring.py.
  # Strip families (technical/team_scaling/agile_transformation) were derived from
  # the Step 0 re-baseline router-family column (Aug 2026).

  Scenario: strip removes possessive "Matt's" from query
    Given the query "What is Matt's approach to event storming?"
    When _strip_matt_subject is applied
    Then the retrieval query does not contain "Matt"
    And the retrieval query contains "event storming"

  Scenario: strip removes subject "Matt" from query
    Given the query "How does Matt build MVPs?"
    When _strip_matt_subject is applied
    Then the retrieval query does not contain "Matt"
    And the retrieval query contains "MVPs"

  Scenario: strip is a no-op when query contains no Matt token
    Given the query "How do you build MVPs?"
    When _strip_matt_subject is applied
    Then the retrieval query equals "How do you build MVPs?"

  Scenario: gate fires for technical intent family
    Given the query "How does Matt do platform refactoring?" and intent family "technical"
    When _build_retrieval_query is called
    Then the retrieval query does not contain "Matt"

  Scenario: gate fires for team_scaling intent family
    Given the query "How does Matt build MVPs?" and intent family "team_scaling"
    When _build_retrieval_query is called
    Then the retrieval query does not contain "Matt"

  Scenario: gate fires for agile_transformation intent family
    Given the query "How does Matt use event storming?" and intent family "agile_transformation"
    When _build_retrieval_query is called
    Then the retrieval query does not contain "Matt"

  Scenario: gate does not fire for narrative intent family (regression anchor)
    Given the query "Why should we hire Matt?" and intent family "narrative"
    When _build_retrieval_query is called
    Then the retrieval query equals "Why should we hire Matt?"

  Scenario: gate does not fire for background intent family
    Given the query "Tell me about Matt's background" and intent family "background"
    When _build_retrieval_query is called
    Then the retrieval query equals "Tell me about Matt's background"

  Scenario: gate does not fire for synthesis intent family
    Given the query "What are Matt's core themes?" and intent family "synthesis"
    When _build_retrieval_query is called
    Then the retrieval query equals "What are Matt's core themes?"

  Scenario: you-phrasing with no Matt token is unchanged under technical family
    Given the query "How do you modernize monoliths into microservices?" and intent family "technical"
    When _build_retrieval_query is called
    Then the retrieval query equals "How do you modernize monoliths into microservices?"
