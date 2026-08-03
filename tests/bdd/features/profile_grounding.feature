Feature: Profile grounding string emits discrete facts only
  As the JD assessor
  I want load_matt_profile to produce a grounding string from education and
  certifications only
  So that verdicts rest on story evidence and discrete verifiable facts, not
  prose characterizations the assessor can paraphrase as profile evidence

  # MATTGPT-158: career_summary excluded from assessment grounding.
  # Prose in the grounding is a citable surface; the assessor paraphrases it
  # and presents the paraphrase as profile evidence. Only discrete facts
  # (degree, certifications) belong here.
  #
  # MATTGPT-080: skills array excluded from assessment grounding.
  # Sentinel ZZZ_SENTINEL_SKILL_DO_NOT_USE is invented -- not drawn from the
  # skills array or the corpus. It cannot collide or go stale.

  Scenario: load_matt_profile omits skills array content from grounding string
    Given a profile whose skills array contains "ZZZ_SENTINEL_SKILL_DO_NOT_USE"
    When load_matt_profile is called
    Then the output does not contain "ZZZ_SENTINEL_SKILL_DO_NOT_USE"

  Scenario: load_matt_profile excludes career summary from grounding string
    Given a profile whose skills array contains "ZZZ_SENTINEL_SKILL_DO_NOT_USE"
    When load_matt_profile is called
    Then the output does not contain the career summary text

  Scenario: load_matt_profile retains both degree and institution in grounding string
    Given a profile whose skills array contains "ZZZ_SENTINEL_SKILL_DO_NOT_USE"
    When load_matt_profile is called
    Then the output contains both the degree and the institution text

  Scenario: load_matt_profile retains certifications in grounding string
    Given a profile whose skills array contains "ZZZ_SENTINEL_SKILL_DO_NOT_USE"
    When load_matt_profile is called
    Then the output contains the certifications text

  Scenario: build_assessment_prompt contains template keys and omits skills array content
    Given a profile whose skills array contains "ZZZ_SENTINEL_SKILL_DO_NOT_USE"
    When build_assessment_prompt is called
    Then the output contains "match_status" and "gap_explanation"
    And the output does not contain "ZZZ_SENTINEL_SKILL_DO_NOT_USE"

  Scenario: build_assessment_prompt contains the discrete-facts-only profile evidence rule
    Given a profile whose skills array contains "ZZZ_SENTINEL_SKILL_DO_NOT_USE"
    When build_assessment_prompt is called
    Then the output contains the discrete facts profile rule

  Scenario: build_assessment_prompt does not contain the counterfactual verdict clause
    Given a profile whose skills array contains "ZZZ_SENTINEL_SKILL_DO_NOT_USE"
    When build_assessment_prompt is called
    Then the output does not contain the counterfactual verdict clause
