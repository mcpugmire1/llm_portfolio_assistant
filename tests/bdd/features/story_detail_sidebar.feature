Feature: Story detail sidebar renders Core Competencies as wrapping pills and Technologies & Practices uncapped

  MATTGPT-212. Sidebar renders both sections as wrapping pills using the same
  flex container. Competency count is not capped; tag count is not capped. Both
  counts are asserted against the fixture story's own field length so a corpus
  edit to Cendian does not break the test for the wrong reason.

  Scenario: Core Competencies pills match the story's Competencies field length
    Given the user opens the Cendian story detail via deeplink
    Then the Core Competencies pill count matches the story's Competencies field length

  Scenario: Technologies and Practices pills match the story's public_tags field length
    Given the user opens the Cendian story detail via deeplink
    Then the Technologies and Practices pill count matches the story's public_tags field length
