Feature: JD requirement assessment
  As the Role Match feature
  I want to assess how well Matt's experience matches each extracted requirement
  So that I can produce a structured match report with evidence and gap analysis

  Background:
    Given the JD assessment prompt is loaded
    And the OpenAI API is available
    And Pinecone has returned candidate stories for a requirement

  # =============================================================================
  # MATCH STATUS
  # =============================================================================

  Scenario: Strong match when stories directly address the requirement
    Given a requirement "10+ years of professional software development experience"
    And retrieved stories include CIC build-out and JPM delivery with high relevance
    When the assessment prompt is run
    Then match_status is "strong"
    And evidence contains up to 2 stories with title, client, and relevance
    And gap_explanation is empty
    And confidence is "high"

  Scenario: Partial match when stories are related but don't fully cover the requirement
    Given a requirement "Insurance or risk management domain knowledge"
    And retrieved stories show financial services experience but not insurance specifically
    When the assessment prompt is run
    Then match_status is "partial"
    And gap_explanation explains specifically what is missing
    And gap_explanation is not empty
    And gap_explanation is not apologetic

  Scenario: Gap when no retrieved stories address the requirement
    Given a requirement "Experience with customer loyalty programs"
    And retrieved stories have low relevance to loyalty programs
    When the assessment prompt is run
    Then match_status is "gap"
    And evidence is empty or contains no meaningful match
    And gap_explanation explains specifically what is missing

  # =============================================================================
  # EVIDENCE QUALITY
  # =============================================================================

  Scenario: Evidence is grounded in provided stories only
    Given a requirement and a set of retrieved stories
    When the assessment prompt is run
    Then evidence story titles match titles from the provided stories
    And evidence does not reference stories not in the provided set
    And evidence does not fabricate experience not present in the stories

  Scenario: Evidence contains at most 2 stories
    Given a requirement with multiple relevant stories retrieved
    When the assessment prompt is run
    Then evidence contains no more than 2 stories

  # =============================================================================
  # CONFIDENCE
  # =============================================================================

  Scenario: High confidence when evidence is direct and specific
    Given a requirement with directly matching stories
    When the assessment prompt is run
    And match_status is "strong"
    Then confidence is "high"

  Scenario: Medium confidence when match requires inference
    Given a requirement where stories are related but require interpretation
    When the assessment prompt is run
    And match_status is "partial"
    Then confidence is "medium"

  Scenario: Low confidence when match is tenuous
    Given a requirement with weakly related stories
    When the assessment prompt is run
    Then confidence is "low"

  # =============================================================================
  # OUTPUT QUALITY
  # =============================================================================

  Scenario: Output is valid JSON with no preamble
    Given any requirement and retrieved stories
    When the assessment prompt is run
    Then the output contains no preamble or explanation
    And the output parses as valid JSON
    And all required fields are present: requirement, match_status, evidence, gap_explanation, confidence

  Scenario: Gap explanation is specific not apologetic
    Given a requirement with no matching stories
    When the assessment prompt is run
    Then gap_explanation does not contain phrases like "unfortunately" or "I'm sorry"
    And gap_explanation states specifically what experience is missing

  # =============================================================================
  # PRIVATE VIEW — RECOMMENDATION
  # =============================================================================

  Scenario: Apply recommendation when strong matches dominate
    Given a full set of match results with 70% or more strong matches and no gaps
    When compute_recommendation is called
    Then recommendation is "Apply"

  Scenario: Consider recommendation when partial matches are present
    Given a full set of match results with at most 1 gap and strong plus partial covering 70% or more
    When compute_recommendation is called
    Then recommendation is "Consider"

  Scenario: Pass recommendation when gaps are significant
    Given a full set of match results with multiple gaps
    When compute_recommendation is called
    Then recommendation is "Pass"
