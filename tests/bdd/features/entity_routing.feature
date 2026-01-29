Feature: Entity Detection and Routing
  As the RAG pipeline
  I need to correctly identify when queries reference specific entities
  So that I can scope results appropriately without false positives

  Background:
    Given the story index contains Matt's transformation project stories
    And entity detection is configured with excluded values

  # =============================================================================
  # COMMON WORDS SHOULD NOT SCOPE (False Positive Prevention)
  # =============================================================================

  Scenario: "Technology" should not scope to Division
    Given "Technology" is a Division value in 9 stories
    When the user asks "What's Matt's technology experience?"
    Then entity detection should return None
    And the query should use broad semantic search
    And results should include stories from multiple divisions

  Scenario: "Innovation" should not scope to Project
    Given "Innovation" was a Project value
    When the user asks "Tell me about innovation at Accenture"
    Then entity detection should return None
    And results should include innovation-related stories across projects

  Scenario: "Transformation" should not scope
    When the user asks "How does Matt handle transformation?"
    Then entity detection should return None
    And the query should retrieve transformation stories broadly

  Scenario: Technology in leadership context
    When the user asks "What's Matt's technology leadership style?"
    Then entity detection should return None
    And results should cover technology leadership across all clients

  Scenario: Innovation as concept
    When the user asks "Where has Matt scaled innovation?"
    Then entity detection should return None
    And results should include innovation stories from CIC and other contexts

  # =============================================================================
  # PROPER NOUNS SHOULD SCOPE (Correct Entity Detection)
  # =============================================================================

  Scenario: CIC abbreviation scopes to Cloud Innovation Center
    When the user asks "Tell me about the CIC"
    Then entity detection should return Division = "Cloud Innovation Center"
    And results should be filtered to CIC stories
    And the response should focus on Cloud Innovation Center work

  Scenario: JP Morgan scopes to client
    When the user asks "What did Matt do at JP Morgan?"
    Then entity detection should return Client = "JP Morgan Chase"
    And results should be filtered to JP Morgan stories

  Scenario: RBC scopes to client
    When the user asks "Tell me about Matt's work at RBC"
    Then entity detection should return Client = "RBC"
    And results should be filtered to RBC stories

  Scenario: Full division name scopes correctly
    When the user asks "How did Matt scale the Cloud Innovation Center?"
    Then entity detection should return Division = "Cloud Innovation Center"
    And results should focus on CIC scaling stories

  Scenario: Accenture scopes to employer
    When the user asks "What did Matt build at Accenture?"
    Then entity detection should return Employer = "Accenture"
    And results should include Accenture stories across all clients

  # =============================================================================
  # EXCLUSION CONTEXT (Transition Queries)
  # =============================================================================

  Scenario: "After Accenture" should not scope to Accenture
    When the user asks "What is Matt doing after Accenture?"
    Then entity detection should return None
    Because "after" is an exclusion context prefix
    And results should include transition/sabbatical stories

  Scenario: "Leaving" prefix prevents scoping
    When the user asks "Why is Matt leaving Accenture?"
    Then entity detection should return None
    And results should focus on career transition narratives

  Scenario: "Before" prefix prevents scoping
    When the user asks "What did Matt do before Accenture?"
    Then entity detection should return None
    And results should be broad career history

  # =============================================================================
  # ENTITY FIELD PRIORITY
  # =============================================================================

  Scenario: Client takes priority over Division
    Given a query mentions both a client and division
    When the user asks "JP Morgan work in the technology division"
    Then entity detection should prioritize Client = "JP Morgan Chase"
    And Division should not override the client match

  Scenario: Longer entity names match first
    When the user asks "Cloud Innovation Center in Atlanta"
    Then the full "Cloud Innovation Center" should match
    And partial matches should not take precedence

  # =============================================================================
  # EDGE CASES
  # =============================================================================

  Scenario: Case insensitive matching
    When the user asks "tell me about RBC"
    Then entity detection should match Client = "RBC"
    And case differences should not prevent matching

  Scenario: Partial client name in sentence
    When the user asks "How did Matt modernize payments at JPMorgan Chase?"
    Then entity detection should return Client = "JP Morgan Chase"
    And the full client name variant should be recognized

  Scenario: Generic "client" word is not an entity
    When the user asks "How does Matt work with clients?"
    Then entity detection should return None
    And "client" as a common noun should not match
