Feature: Ask Agy streams its answer
  As a recruiter asking Agy about Matt
  I want the answer to appear as it is written
  So that I am reading within seconds instead of waiting on the whole answer

  # MATTGPT-275 step 1. Answers come from gpt-6.1-sol on the Responses API,
  # streamed (MATTGPT-282 run 2: first visible text at a 4.13 s median, the
  # whole turn at 9.35 s). Agy's answer text reaches the page as it arrives,
  # then the finished, post-processed answer takes its place (stream, then
  # swap): one Agy message per turn, with its related projects.
  #
  # One scenario per way a question reaches the answer:
  #   - typed on the Ask Agy landing page (landing_view.py)
  #   - typed as a follow-up in the conversation (conversation_view.py)
  #   - started from a Home suggested chip, which seeds the question into the
  #     conversation (conversation_view.py, the chip-injection path that
  #     category cards and "Ask Agy about this" also use)
  #
  # "Grows on screen" is read from the DOM while the turn runs: a recorder
  # samples the newest Agy message (avatar differs from the visitor's) on
  # every DOM change. It grows when at least 3 distinct non-empty text
  # lengths are seen before the turn finishes and the first is under half
  # the finished length. An answer rendered in one piece shows one length.
  # Answers are live (real model), so the steps assert shape, never wording.

  Scenario: The first question typed on Ask Agy streams in
    Given the user navigates to Ask Agy
    When the user types "Tell me about his payments work." and watches the answer arrive
    Then the question is shown as the visitor's message
    And Agy's answer text grows on screen before the turn finishes
    And the thinking indicator is gone while the answer text grows
    And the finished turn shows one Agy answer with its related projects

  Scenario: A follow-up typed in the conversation streams in
    Given the user navigates to Ask Agy
    And the user has asked "Tell me about his payments work."
    When the user types "How big was the team?" and watches the answer arrive
    Then the question is shown as the visitor's message
    And Agy's answer text grows on screen before the turn finishes
    And the thinking indicator is gone while the answer text grows
    And the finished turn shows one Agy answer with its related projects

  Scenario: A question started from a Home suggested chip streams in
    Given the user navigates to the home page
    When the user clicks the first Home suggested chip and watches the answer arrive
    Then the question is shown as the visitor's message
    And Agy's answer text grows on screen before the turn finishes
    And the thinking indicator is gone while the answer text grows
    And the finished turn shows one Agy answer with its related projects
