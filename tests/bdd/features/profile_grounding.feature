Feature: Profile grounding string excludes skills array
  As the JD assessor
  I want load_matt_profile to produce a grounding string from career summary and
  education only
  So that verdicts rest on story evidence rather than a self-reported skills list

  # MATTGPT-080: Remove 73-item skills array from assessor grounding.
  # Sentinel ZZZ_SENTINEL_SKILL_DO_NOT_USE is invented -- not drawn from the
  # skills array or the corpus. It cannot collide or go stale.

  Scenario: load_matt_profile omits skills array content from grounding string
    Given a profile whose skills array contains "ZZZ_SENTINEL_SKILL_DO_NOT_USE"
    When load_matt_profile is called
    Then the output does not contain "ZZZ_SENTINEL_SKILL_DO_NOT_USE"

  Scenario: load_matt_profile retains career summary in grounding string
    Given a profile whose skills array contains "ZZZ_SENTINEL_SKILL_DO_NOT_USE"
    When load_matt_profile is called
    Then the output contains the career summary text

  Scenario: load_matt_profile retains both degree and institution in grounding string
    Given a profile whose skills array contains "ZZZ_SENTINEL_SKILL_DO_NOT_USE"
    When load_matt_profile is called
    Then the output contains both the degree and the institution text

  Scenario: build_assessment_prompt contains template keys and omits skills array content
    Given a profile whose skills array contains "ZZZ_SENTINEL_SKILL_DO_NOT_USE"
    When build_assessment_prompt is called
    Then the output contains "match_status" and "gap_explanation"
    And the output does not contain "ZZZ_SENTINEL_SKILL_DO_NOT_USE"

  # Profile evidence traceability: these two scenarios are wiring checks.
  # They verify the rule text is present in the built prompt, not that the LLM
  # honours it. Behavioral validation lives in the JD re-run and the eval suite.

  Scenario: build_assessment_prompt contains the profile evidence traceability rule
    Given a profile whose skills array contains "ZZZ_SENTINEL_SKILL_DO_NOT_USE"
    When build_assessment_prompt is called
    Then the output contains the profile traceability instruction

  Scenario: build_assessment_prompt instructs model to omit profile evidence when grounding has no match
    Given a profile whose skills array contains "ZZZ_SENTINEL_SKILL_DO_NOT_USE"
    When build_assessment_prompt is called
    Then the output contains the profile omission instruction
