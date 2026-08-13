Feature: Shared corpus loader normalization and id enforcement

  Background:
    Given the corpus loader module is importable without Streamlit side effects

  Scenario: normalize_story coerces comma-separated public_tags string to a list
    Given a story dict with public_tags set to the string "cloud,aws"
    When normalize_story processes the story
    Then the story's public_tags is the list ["cloud", "aws"]

  Scenario: normalize_story leaves public_tags list unchanged
    Given a story dict with public_tags set to the list ["cloud", "aws"]
    When normalize_story processes the story
    Then the story's public_tags is the list ["cloud", "aws"]

  Scenario: normalize_story coerces a present PascalCase list field from string to list
    Given a story dict with Performance set to the string "Reduced latency by 60%"
    When normalize_story processes the story
    Then the story's Performance is the list ["Reduced latency by 60%"]

  Scenario: normalize_story does not add absent list fields
    Given a story dict with no Competencies key
    When normalize_story processes the story
    Then the story has no Competencies key

  Scenario: load_stories skips a story with no id field
    Given a JSONL file containing one story with no id field
    When load_stories processes the file
    Then the result is an empty list

  Scenario: load_stories skips a story with an empty-string id
    Given a JSONL file containing one story with id set to ""
    When load_stories processes the file
    Then the result is an empty list

  Scenario: load_stories skips a story with id set to 0
    Given a JSONL file containing one story with id set to 0
    When load_stories processes the file
    Then the result is an empty list

  Scenario: load_stories returns a story with id stripped of surrounding whitespace
    Given a JSONL file containing one story with id set to "  story-1  "
    When load_stories processes the file
    Then the story's id equals "story-1"

  Scenario: load_stories includes a story with a valid id
    Given a JSONL file containing one story with id set to "story-1"
    When load_stories processes the file
    Then the result contains exactly 1 story

  Scenario: load_stories raises on malformed JSON
    Given a JSONL file containing a line that is not valid JSON
    When load_stories attempts to process the file
    Then a json.JSONDecodeError is raised

  Scenario: load_stories skips empty lines silently
    Given a JSONL file containing one empty line followed by one story with id "story-1"
    When load_stories processes the file
    Then the result contains exactly 1 story

  Scenario: normalization enables public_tags tokens to reach the keyword scorer
    Given a story where public_tags is the raw string "cloud" and no other field contains "cloud"
    When _keyword_score_for_story runs with query "cloud" on the unnormalized story
    Then the keyword score equals 0.0
    When load_stories normalizes the story and _keyword_score_for_story runs with query "cloud"
    Then the keyword score equals 0.5
