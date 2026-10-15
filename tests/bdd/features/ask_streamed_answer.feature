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
  #
  # "Only the conversation's own input and caption": while Agy's answer text
  # is arriving, no element left over from the previous page (Streamlit marks
  # them data-stale="true" until the run ends) is visible with height, and
  # the conversation's chat input and caption are on the page.
  #
  # "Stays in place": the gap between the bottom of the visitor's question and
  # the top of Agy's bubble while the answer arrives equals the gap in the
  # finished turn (within 1 px), so nothing moves when the finished answer
  # replaces the stream.
  #
  # "Sends nothing to the app": a question that arrives from another page is
  # answered from a fragment whose timer (run_every) sends a rerun request on
  # every tick while it exists. Once the finished answer has replaced the
  # stream, the browser sends no websocket frame to the app for 4 seconds:
  # the timer is gone, so the rest of the session has no background reruns.

  Scenario: The first question typed on Ask Agy streams in
    Given the user navigates to Ask Agy
    When the user types "Tell me about his payments work." and watches the answer arrive
    Then the question is shown as the visitor's message
    And Agy's answer text grows on screen before the turn finishes
    And the thinking indicator is gone while the answer text grows
    And while the answer arrives, only the conversation's own input and caption are on screen
    And Agy's answer stays in place when the finished answer replaces the stream
    And the finished turn shows one Agy answer with its related projects
    And once the turn has finished, the page sends nothing to the app for 4 seconds

  Scenario: A follow-up typed in the conversation streams in
    Given the user navigates to Ask Agy
    And the user has asked "Tell me about his payments work."
    When the user types "How big was the team?" and watches the answer arrive
    Then the question is shown as the visitor's message
    And Agy's answer text grows on screen before the turn finishes
    And the thinking indicator is gone while the answer text grows
    And while the answer arrives, only the conversation's own input and caption are on screen
    And Agy's answer stays in place when the finished answer replaces the stream
    And the finished turn shows one Agy answer with its related projects
    And once the turn has finished, the page sends nothing to the app for 4 seconds

  Scenario: A question started from a Home suggested chip streams in
    Given the user navigates to the home page
    When the user clicks the first Home suggested chip and watches the answer arrive
    Then the question is shown as the visitor's message
    And Agy's answer text grows on screen before the turn finishes
    And the thinking indicator is gone while the answer text grows
    And while the answer arrives, only the conversation's own input and caption are on screen
    And Agy's answer stays in place when the finished answer replaces the stream
    And the finished turn shows one Agy answer with its related projects
    And once the turn has finished, the page sends nothing to the app for 4 seconds
