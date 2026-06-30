Feature: Ask Agy button alignment and focus ring

  # Focus ring :focus-visible coverage is in test_ask_agy_button_css.py (unit test)
  # for both buttons:
  # - Landing button: on_change navigates away on any text commit; Tab triggers
  #   navigation before focus-visible state can be read.
  # - Conversation submit button: Streamlit intercepts Tab in the chat textarea;
  #   document.activeElement drops to BODY instead of moving to the button.
  # CSS unit assertions are deterministic and cover what E2E cannot.

  Scenario: Landing Ask button has zero top margin on desktop
    Given the user navigates to the Ask Agy landing page
    Then the landing Ask button computed margin-top is 0px

  Scenario: Landing Ask button min-height matches the input height
    Given the user navigates to the Ask Agy landing page
    Then the landing Ask button computed min-height is 44px

  Scenario: Conversation submit button min-height does not override the container
    Given the user navigates to the Ask Agy conversation page
    Then the conversation submit button computed min-height is auto

  Scenario: Conversation submit button has no vertical translation
    Given the user navigates to the Ask Agy conversation page
    Then the conversation submit button transform Y translation is zero
