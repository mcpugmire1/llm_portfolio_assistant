Feature: Evidence Fidelity (No Hallucination)
  As a recruiter reviewing Agy's responses
  I want responses grounded in actual story content
  So that I can trust the information is accurate

  Background:
    Given the story index contains Matt's verified STAR stories
    And each story has accurate Client, Project, and metric data

  # =============================================================================
  # CLIENT ATTRIBUTION ACCURACY
  # =============================================================================

  Scenario: Client name matches source story
    When the user asks "Tell me about Matt's payments work at JPMorgan"
    Then the response should attribute work to "JP Morgan Chase"
    And the client name should be bolded
    And no other client should be mentioned for JPMorgan-specific stories

  Scenario: No hallucinated client names
    When the user asks about Matt's experience
    Then only clients from the retrieved stories should be mentioned
    And the response should not invent client names not in the data

  Scenario: Career Narrative is not attributed as a client
    When the user asks about Matt's leadership themes
    Then "Career Narrative" should not appear as a client attribution
    And the response should use actual client names from relevant stories

  Scenario: Multiple Clients stories are properly attributed
    Given a story has Client = "Multiple Clients"
    When the user asks about that work
    Then the response should say "Multiple Clients", "various clients", or "across clients"
    Or the response should name 3+ specific companies
    And the response should not claim it was for a single specific client

  # =============================================================================
  # METRIC ACCURACY
  # =============================================================================

  Scenario: Metrics match source stories
    When the user asks "How did Matt improve delivery at JP Morgan?"
    Then any metrics cited should appear in the retrieved JP Morgan stories
    And percentages should match the source exactly
    And timeframes should match the source exactly

  Scenario: No invented percentages
    When the user asks about Matt's achievements
    Then every percentage mentioned should be traceable to a story
    And the response should not round or approximate metrics

  Scenario: Metric context preserved
    Given a story says "40% cycle time reduction"
    When that metric is cited in a response
    Then it should be associated with cycle time, not another metric
    And the metric should not be misattributed to a different outcome

  Scenario: Multiple Clients metrics not attributed to single client
    Given a metric appears in a "Multiple Clients" story
    When that metric is cited
    Then it should not be attributed to a specific named client
    And the multi-client context should be preserved

  # =============================================================================
  # STORY CONTENT FIDELITY
  # =============================================================================

  Scenario: Response uses actual story phrases
    When the user asks about Matt's approach to complex problems
    Then the response should include phrases from the source story
    And the response should not paraphrase into generic language

  Scenario: STAR structure preserved
    When a behavioral question is asked
    Then the response should reflect Situation, Task, Action, Result
    And specific details from each section should appear

  Scenario: Verbatim phrases for Professional Narrative
    When the user asks about Matt's career intent
    Then the response must include verbatim phrases like:
      | phrase                            |
      | builder                           |
      | modernizer                        |
      | complexity to clarity             |
      | build something from nothing      |
      | not looking for a maintenance role|
    And these phrases should not be paraphrased

  # =============================================================================
  # NO CROSS-CONTAMINATION
  # =============================================================================

  Scenario: Metrics stay with their source story
    Given JP Morgan story has "12 countries" metric
    And RBC story has "3 regions" metric
    When the user asks about JP Morgan work
    Then "12 countries" may appear
    And "3 regions" should not be attributed to JP Morgan

  Scenario: Client work not mixed
    When the user asks about RBC modernization
    Then the response should only describe RBC work
    And achievements from other clients should not leak in

  Scenario: Project details stay with correct project
    Given multiple projects exist for the same client
    When the user asks about a specific project
    Then details from other projects should not contaminate the response

  # =============================================================================
  # THEME AND CATEGORY ACCURACY
  # =============================================================================

  Scenario: Theme attribution is accurate
    When the user asks about "Emerging Tech" work
    Then only stories with Theme = "Emerging Tech" should inform the response
    And the response should not include unrelated themes

  Scenario: Industry attribution is accurate
    When the user asks about "Financial Services" experience
    Then only stories from Financial Services should be cited
    And healthcare or telecom stories should not appear

  # =============================================================================
  # SOURCE TRANSPARENCY
  # =============================================================================

  Scenario: Response acknowledges source limitations
    Given a query matches only 1-2 stories
    When the response is generated
    Then the response should focus on available evidence
    And the response should not extrapolate beyond source data

  Scenario: Thin theme handling
    Given "Emerging Tech" has only 3 stories
    When the user asks about GenAI experience
    Then the response should be appropriately scoped
    And the response should not invent additional examples

  Scenario: No invented examples
    When the user asks for examples of Matt's work
    Then every example should trace to an actual story
    And the response should not fabricate scenarios
