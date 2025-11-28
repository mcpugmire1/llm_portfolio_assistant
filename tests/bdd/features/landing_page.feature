Feature: Landing Page
  As a visitor to Ask MattGPT
  I want a clear and inviting landing page
  So that I understand how to interact with Agy and explore Matt's experience

  Background:
    Given the user navigates to the Ask MattGPT page

  # =============================================================================
  # VISUAL ELEMENTS
  # =============================================================================

  Scenario: Landing page displays Agy introduction
    Then the page should display Agy's avatar
    And the page should display "Hi, I'm Agy" heading
    And the page should explain Agy is a Plott Hound
    And the introduction text should be centered

  Scenario: Status bar shows system readiness
    Then the status bar should show "Semantic search active"
    And the status bar should show "Pinecone index ready"
    And the status bar should show story count

  Scenario: White card contains all intro content
    Then the intro section should be in a white card
    And the suggested questions should be in the same white card
    And the card should have rounded corners
    And the card should have a subtle shadow

  # =============================================================================
  # SUGGESTED QUESTIONS
  # =============================================================================

  Scenario: Six suggested questions are displayed
    Then there should be exactly 6 suggested question buttons
    And questions should be arranged in a 2x3 grid
    And each question should have an emoji icon

  Scenario: Suggested questions have correct styling
    Then suggested question buttons should have gray background
    And button text should be italicized
    And buttons should have subtle borders

  Scenario: Clicking suggested question navigates to conversation
    When the user clicks "How did Matt transform global payments at scale?"
    Then the thinking indicator should appear
    And the conversation view should load
    And results should appear within 10 seconds

  # =============================================================================
  # INPUT AREA
  # =============================================================================

  Scenario: Input field is ready for questions
    Then the input field should have placeholder text
    And the placeholder should mention "Ask me anything"
    And the input should not have a red border

  Scenario: Ask Agy button styling
    Then the "Ask Agy" button should be purple (#8B5CF6)
    And the button should include the paw emoji
    And the button text should not wrap to multiple lines

  Scenario: Input and button stay on same line
    When the browser window is resized to 800px width
    Then the input field and button should remain on the same row
    And the button should not wrap below the input

  Scenario: Submit question via Enter key
    Given the user types "Tell me about leadership" in the input
    When the user presses Enter
    Then the thinking indicator should appear
    And the query should be processed

  Scenario: Submit question via button click
    Given the user types "Tell me about leadership" in the input
    When the user clicks the "Ask Agy" button
    Then the thinking indicator should appear
    And the query should be processed

  # =============================================================================
  # LOADING STATES
  # =============================================================================

  Scenario: Thinking indicator during processing
    When the user submits a question
    Then the animated thinking indicator should display
    And the text "Tracking down insights..." should appear
    And all suggested question buttons should be disabled

  Scenario: Buttons disabled during processing
    Given a question is being processed
    Then all suggested question buttons should be disabled
    And the Ask Agy button should be disabled
    And the input field should remain enabled

  # =============================================================================
  # RESPONSIVE DESIGN
  # =============================================================================

  Scenario: Layout adapts to narrow screens
    When the browser window is 600px wide
    Then the white card should remain centered
    And content should not overflow horizontally
    And suggested questions should remain readable

  Scenario: Layout adapts to wide screens
    When the browser window is 1400px wide
    Then the white card should be constrained to max-width
    And the card should remain centered
    And there should be margin on both sides
