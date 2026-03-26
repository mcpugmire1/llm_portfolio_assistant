Feature: JD requirement extraction
  As the Role Match feature
  I want to extract structured requirements from a job description
  So that they can be matched against Matt's STAR stories in Pinecone

  Background:
    Given the JD extraction prompt is loaded
    And the OpenAI API is available

  Scenario: Extract requirements from a structured JD with explicit Required/Preferred split
    Given a sanitized structured JD with clearly labeled Required and Preferred sections
    When the extraction prompt is run against the JD
    Then required_qualifications contains all explicitly required items
    And preferred_qualifications contains all explicitly preferred items
    And each qualification has a requirement, source_text, and type field
    And the JSON is valid and parseable

  Scenario: Extract requirements from a narrative JD with no explicit sections
    Given a sanitized narrative JD written entirely in prose with no bullet points or section headers
    When the extraction prompt is run against the JD
    Then required_qualifications contains requirements inferred from strong language signals
    And implicit_requirements contains requirements inferred from responsibilities
    And implicit_requirements each have a confidence field of high, medium, or low
    And no requirements are invented beyond what the text states or clearly implies

  Scenario: Extract requirements from a hybrid narrative and structured JD
    Given a sanitized hybrid JD with narrative responsibility sections and structured qualifications
    When the extraction prompt is run against the JD
    Then requirements are extracted from both narrative and structured sections
    And influence and strategy requirements are captured even without technical specifics
    And preferred_qualifications is not empty even when no explicit preferred section exists

  Scenario: Extract company name from any section of the JD
    Given a sanitized structured JD where the company name appears in the company description or closing sections
    When the extraction prompt is run against the JD
    Then the company field contains the correct company name
    And the company field is not "Not specified"

  Scenario: Handle undisclosed company name
    Given a sanitized narrative JD where no company name appears anywhere in the text
    When the extraction prompt is run against the JD
    Then the company field contains "Undisclosed"

  Scenario: Requirements are normalized into testable statements
    Given a sanitized JD with vague qualification language
    When the extraction prompt is run against the JD
    Then the normalized requirement is specific and testable
    And source_text preserves the original wording for verification

  Scenario: Output is valid JSON with no preamble
    Given any sanitized JD format
    When the extraction prompt is run against the JD
    Then the output contains no preamble or explanation
    And the output parses as valid JSON
    And all required top-level fields are present: role_title, company, required_qualifications, preferred_qualifications, implicit_requirements, key_responsibilities, seniority_signals

  Scenario: Mixed format JD with narrative intro and structured qualifications
    Given a sanitized mixed JD with prose responsibilities and bulleted qualifications
    When the extraction prompt is run against the JD
    Then requirements are extracted from the structured qualifications section
    And seniority_signals captures reporting line and scope signals from the narrative
