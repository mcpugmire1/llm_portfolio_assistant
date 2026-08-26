Feature: Story detail sidebar renders Core Competencies as wrapping pills and Technologies & Practices uncapped

  MATTGPT-212. Both sidebar sections render as wrapping pills using the same
  flex container. Pill counts are asserted against the fixture story's own
  field length so a corpus edit to Cendian re-baselines the assertion rather
  than breaking the test for the wrong reason.

  Scenario: Core Competencies pills match the story's Competencies field length
    When the user navigates to "?story=integrating-a-chemical-logistics-network-across-every-partner-capability%7Ccendian-chemical-logistics"
    Then the Core Competencies pill count matches the story's Competencies field length

  Scenario: Technologies and Practices pills match the story's public_tags field length
    When the user navigates to "?story=integrating-a-chemical-logistics-network-across-every-partner-capability%7Ccendian-chemical-logistics"
    Then the Technologies and Practices pill count matches the story's public_tags field length
