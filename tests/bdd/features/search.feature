Feature: Story Search
  As a recruiter or hiring manager
  I want to search Matt's project stories
  So that I can find relevant examples of his experience

  Background:
    Given the story index contains 120+ transformation project stories
    And the Pinecone index is ready

  # =============================================================================
  # BEHAVIORAL QUERY MATCHING
  # =============================================================================

  Scenario: Behavioral interview question returns leadership stories
    When the user searches "tell me about a time you led a team through conflict"
    Then the top 3 results should include at least 1 Talent & Enablement story
    And results should include stories with leadership or conflict themes

  Scenario: Technical question returns execution stories
    When the user searches "how did Matt build the payments platform"
    Then the top 3 results should include Execution & Delivery stories
    And results should include stories about platform engineering

  Scenario: Stakeholder question returns interpersonal stories
    When the user searches "show me how Matt handles difficult stakeholders"
    Then results should prioritize Talent & Enablement stories
    And results should include stories with stakeholder management themes

  # =============================================================================
  # CLIENT DIVERSITY
  # =============================================================================

  Scenario: Results show client diversity
    When the user searches "transformation projects"
    Then no single client should have more than 2 stories in top 5 results
    And results should represent at least 3 different clients

  Scenario: JPMC stories don't dominate results
    Given JPMC represents 16% of all stories
    When the user searches for a common topic
    Then JPMC stories should not exceed 30% of results

  # =============================================================================
  # NONSENSE FILTERING
  # =============================================================================

  Scenario: Nonsense query is rejected
    When the user searches "asdfghjkl"
    Then the system should return a polite rejection message
    And no API call should be made to OpenAI

  Scenario: Empty query is handled gracefully
    When the user searches ""
    Then the system should prompt for a valid question
    And no error should be displayed

  Scenario: Single character query is rejected
    When the user searches "a"
    Then the system should return a polite rejection message

  # =============================================================================
  # SEMANTIC UNDERSTANDING
  # =============================================================================

  Scenario: Synonyms are understood
    When the user searches "agile transformation"
    And another user searches "scrum adoption"
    Then both searches should return overlapping results

  Scenario: Context is understood beyond keywords
    When the user searches "how did Matt help teams work better together"
    Then results should include collaboration and team dynamics stories
    And results should not require exact keyword matches
