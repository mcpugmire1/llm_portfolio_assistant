Feature: Mode Routing (Synthesis vs Standard vs Narrative)
  As the RAG pipeline
  I need to route queries to the correct response mode
  So that users get appropriately scoped answers

  Background:
    Given the story index contains Matt's transformation project stories
    And the semantic router is configured with intent families

  # =============================================================================
  # SYNTHESIS MODE (Forest View - Multiple Stories)
  # =============================================================================

  Scenario: Theme questions trigger synthesis mode
    When the user asks "What are Matt's core themes?"
    Then the query should be routed to synthesis mode
    And the response should cite 3+ different clients
    And the response should draw from multiple stories

  Scenario: Capability verbs trigger synthesis
    When the user asks "How did Matt scale teams?"
    Then the query should be routed to synthesis mode
    And results should span multiple engagements

  Scenario: Pattern questions trigger synthesis
    When the user asks "What patterns do you see in Matt's approach?"
    Then the query should be routed to synthesis mode
    And the response should identify cross-cutting themes

  Scenario: Transformation questions trigger synthesis
    When the user asks "How did Matt transform delivery at scale?"
    Then the query should be routed to synthesis mode
    And results should include delivery transformation stories

  Scenario: Verb overrides client mention
    When the user asks "How did Matt scale talent at Accenture?"
    Then the query should be routed to synthesis mode
    Because "scale" is a capability verb
    And results may include Accenture stories but not be limited to them

  Scenario: Methodology nouns trigger synthesis
    When the user asks "Tell me about Matt's rapid prototyping work"
    Then the query should be routed to synthesis mode
    And results should include prototyping stories across clients

  # =============================================================================
  # CLIENT-SCOPED MODE (Tree View - Specific Entity)
  # =============================================================================

  Scenario: Client name triggers client mode
    When the user asks "What did Matt do at JP Morgan?"
    Then the query should be routed to client-scoped mode
    And results should be filtered to JP Morgan stories
    And the response should focus on JP Morgan work

  Scenario: Division name triggers scoped mode
    When the user asks "Tell me about the Cloud Innovation Center"
    Then the query should be routed to entity-scoped mode
    And results should be filtered to CIC stories

  Scenario: Specific project question
    When the user asks "Tell me about Matt's payments work at JPMorgan"
    Then the query should be routed to client-scoped mode
    And results should prioritize JPMorgan payments stories

  # =============================================================================
  # BEHAVIORAL MODE (STAR Format)
  # =============================================================================

  Scenario: "Tell me about a time" triggers behavioral
    When the user asks "Tell me about a time Matt failed"
    Then the query should be routed to behavioral mode
    And the response should follow STAR format
    And results should include failure/learning stories

  Scenario: Conflict questions trigger behavioral
    When the user asks "How does Matt handle conflict?"
    Then the query should be routed to behavioral mode
    And results should include stakeholder/conflict stories

  Scenario: Pressure questions trigger behavioral
    When the user asks "How do you handle pressure?"
    Then the query should be routed to behavioral mode
    And results should include high-stakes delivery stories

  Scenario: Example requests trigger behavioral
    When the user asks "Give me an example of Matt showing leadership"
    Then the query should be routed to behavioral mode
    And the response should provide a specific STAR example

  # =============================================================================
  # NARRATIVE MODE (Professional Identity)
  # =============================================================================

  Scenario: Career intent questions trigger narrative
    When the user asks "What is Matt looking for next?"
    Then the query should be routed to narrative mode
    And results should include Career Intent story
    And the response should use Matt's verbatim phrases

  Scenario: Leadership philosophy triggers narrative
    When the user asks "What's Matt's leadership philosophy?"
    Then the query should be routed to narrative mode
    And results should include Leadership Philosophy story

  Scenario: Identity questions trigger narrative
    When the user asks "Who is Matt Pugmire?"
    Then the query should be routed to background/narrative mode
    And the response should cover Matt's professional identity

  Scenario: Transition questions trigger narrative
    When the user asks "Why is Matt exploring opportunities?"
    Then the query should be routed to narrative mode
    And results should include Transition Story

  # =============================================================================
  # REDIRECT MODE (Out of Scope)
  # =============================================================================

  Scenario: Retail experience triggers redirect
    When the user asks "Tell me about Matt's retail experience"
    Then the query should be routed to redirect mode
    And the response should gracefully acknowledge limited experience
    And the response should suggest related areas Matt does cover

  Scenario: Off-topic questions are handled gracefully
    When the user asks "What's the weather today?"
    Then the semantic router should reject the query
    And a polite off-topic message should be returned

  # =============================================================================
  # EDGE CASES
  # =============================================================================

  Scenario: Synthesis + client combo
    When the user asks "How did Matt transform delivery at JP Morgan?"
    Then the query should combine synthesis approach with client focus
    And results should be scoped to JP Morgan
    And the response should cover transformation themes

  Scenario: Generic "client" word is not a client entity
    When the user asks "How does Matt work with clients?"
    Then "client" should not be treated as an entity
    And the query should use synthesis mode
    And results should span multiple client engagements

  Scenario: Multi-turn context maintained
    Given the user previously asked about "JPMorgan payments"
    When the user asks "Tell me more about that project"
    Then context from the previous turn should inform the response
    And results should continue focusing on JPMorgan payments
