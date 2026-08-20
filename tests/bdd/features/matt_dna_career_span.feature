Feature: MATT_DNA career-span derivation and prose (MATTGPT-161)

  Career start and span are derived from the corpus (min Start_Date, max
  End_Date, span difference) so they cannot drift from story data. The
  derived values exist as constants for consumers that need the math
  (Role Match assessor reasoning about JD tenure requirements). The
  values are NOT rendered into MATT_DNA prose -- the ageism-signal rule
  Matt has applied elsewhere (resume, About page, matt_profile.json
  career_summary) extends to the LLM grounding surface.

  Scenario: derivation returns 2000 when the story list contains a pre-2005 record
    Given a story list containing a synthetic pre-2005 story with Start_Date "2000-06"
    When sync_portfolio_metadata is called with that story list
    Then _CAREER_START_YEAR is 2000

  Scenario: derivation returns 2000, the current corpus earliest start year
    Given the current production story corpus is loaded
    When sync_portfolio_metadata is called with the production stories
    Then _CAREER_START_YEAR is 2000

  Scenario: MATT_DNA output contains no "+ years" assertion
    Given the current production story corpus is loaded
    When sync_portfolio_metadata is called with the production stories
    Then MATT_DNA contains no "+ years" substring

  Scenario: Accenture date range survives in MATT_DNA
    Given the current production story corpus is loaded
    When sync_portfolio_metadata is called with the production stories
    Then MATT_DNA contains "Accenture: March 2005 - September 2023"
