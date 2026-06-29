Feature: Ask Agy button alignment and focus ring

  Scenario: Landing Ask button has zero top margin on desktop
    Given the user navigates to the Ask Agy landing page
    Then the landing Ask button computed margin-top is 0px

  Scenario: Landing Ask button min-height matches the input height
    Given the user navigates to the Ask Agy landing page
    Then the landing Ask button computed min-height is 44px

  Scenario: Landing Ask button focus ring is purple not red
    Given the user navigates to the Ask Agy landing page
    When the landing Ask button receives keyboard focus
    Then the landing Ask button box-shadow contains the purple focus color
    And the landing Ask button box-shadow does not contain the red Streamlit color

  Scenario: Conversation submit button min-height matches the textarea height
    Given the user navigates to the Ask Agy conversation page
    Then the conversation submit button computed min-height is 48px

  Scenario: Conversation submit button focus ring is purple not red
    Given the user navigates to the Ask Agy conversation page
    When the conversation submit button receives keyboard focus
    Then the conversation submit button box-shadow contains the purple focus color
    And the conversation submit button box-shadow does not contain the red Streamlit color

  Scenario: Conversation submit button has no vertical translation
    Given the user navigates to the Ask Agy conversation page
    Then the conversation submit button transform Y translation is zero
