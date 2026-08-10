Feature: MATTGPT-077 retrieval query pronoun substitution for Matt-subject queries
  As the RAG pipeline
  I want to substitute "Matt"→"he" and "Matt's"→"his" in the retrieval query on
  technical, team_scaling, and agile_transformation intent families
  So that self-referential name tokens don't bias embeddings toward
  Independent Project stories over topically-relevant named-client stories
  while preserving grammatical sentences for the embedding model.

  # Pure unit tests -- no Playwright, no API calls, no Pinecone.
  # Tests _substitute_matt_subject() and _build_retrieval_query() in utils/scoring.py.
  # The LLM receives the original query verbatim; only the retrieval query is transformed.
  # Gate families derived from Step 0 re-baseline router-family column (Aug 2026).
  # Arm C (pronoun substitution) chosen over deletion based on A/B/C probe (Aug 2026):
  # Q1 Revenue held at LLM[1] under substitution but was displaced under deletion.

  Scenario: substitution replaces possessive "Matt's" with "his"
    Given the query "What is Matt's approach to event storming?"
    When _substitute_matt_subject is applied
    Then the retrieval query contains "his"
    And the retrieval query does not contain "Matt"

  Scenario: substitution replaces subject "Matt" with "he"
    Given the query "How does Matt build MVPs?"
    When _substitute_matt_subject is applied
    Then the retrieval query contains "he"
    And the retrieval query does not contain "Matt"

  Scenario: substitution is a no-op when query contains no Matt token
    Given the query "How do you build MVPs?"
    When _substitute_matt_subject is applied
    Then the retrieval query equals "How do you build MVPs?"

  Scenario: query starting with "Matt" capitalizes the substitution
    Given the query "Matt built the platform from scratch."
    When _substitute_matt_subject is applied
    Then the retrieval query equals "He built the platform from scratch."

  Scenario: mid-sentence substitution does not capitalize
    Given the query "The platform that Matt built."
    When _substitute_matt_subject is applied
    Then the retrieval query equals "The platform that he built."

  Scenario: query consisting only of "Matt" substitutes without error
    Given the query "Matt"
    When _substitute_matt_subject is applied
    Then the retrieval query equals "He"

  # "contains he" is substring-weak ("The" satisfies it before any substitution).
  # The load-bearing assertion is "does not contain Matt" -- that's what fails
  # when the gate is broken. The pairing is deliberate; do not remove the
  # "does not contain" step to simplify.
  Scenario: gate fires for technical intent family
    Given the query "How does Matt do platform refactoring?" and intent family "technical"
    When _build_retrieval_query is called
    Then the retrieval query contains "he"
    And the retrieval query does not contain "Matt"

  Scenario: gate fires for team_scaling intent family
    Given the query "How does Matt build MVPs?" and intent family "team_scaling"
    When _build_retrieval_query is called
    Then the retrieval query contains "he"
    And the retrieval query does not contain "Matt"

  Scenario: gate fires for agile_transformation intent family
    Given the query "How does Matt use event storming?" and intent family "agile_transformation"
    When _build_retrieval_query is called
    Then the retrieval query contains "he"
    And the retrieval query does not contain "Matt"

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
