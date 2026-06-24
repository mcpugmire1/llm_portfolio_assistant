Feature: Ask Agy Landing Page
  As a visitor to Ask Agy
  I want a clear and inviting landing page
  So that I understand how to interact with Agy and explore Matt's experience

  # No Background block -- every scenario owns its full setup sequence.
  # Viewport must be set before navigation so _browser_screen_size captures correctly.

  # =============================================================================
  # VISUAL ELEMENTS
  # =============================================================================

  Scenario: Landing page displays Agy introduction
    Given the viewport is 1024px wide
    And the user navigates to the Ask Agy page
    Then the page should display Agy's avatar
    And the page should display "Hi, I'm Agy" heading
    And the page should explain Agy is a Plott Hound

  Scenario: Status bar shows system readiness
    Given the viewport is 1024px wide
    And the user navigates to the Ask Agy page
    Then the status bar should show "Semantic search active"
    And the status bar should show "Pinecone index ready"
    And the status bar should show story count

  # =============================================================================
  # SUGGESTION CHIPS -- DESKTOP (static HTML + JS bridge, MATTGPT-139)
  # =============================================================================

  Scenario: Six suggestion chips are displayed on desktop
    Given the viewport is 1024px wide
    And the user navigates to the Ask Agy page
    Then there should be exactly 6 suggestion chips in the chip grid
    And each chip should have an emoji icon
    And the chip grid should use a 2-column CSS grid layout

  Scenario: Suggestion chips are static HTML on desktop
    Given the viewport is 1024px wide
    And the user navigates to the Ask Agy page
    Then the suggestion chips should be HTML button elements with class "suggested-chip"
    And no visible Streamlit button widget should exist in the chip grid

  Scenario: Clicking a suggestion chip routes to conversation
    Given the viewport is 1024px wide
    And the user navigates to the Ask Agy page
    When the user clicks the first suggestion chip
    Then the thinking indicator should appear
    And the conversation view should load

  Scenario: Chip grid is not interactive during processing
    Given the viewport is 1024px wide
    And the user navigates to the Ask Agy page
    When the user clicks the first suggestion chip
    Then the hidden receiver buttons should have the disabled attribute

  # =============================================================================
  # SUGGESTION CHIPS -- MOBILE (st.button, unchanged path)
  # =============================================================================

  Scenario: Mobile path uses HTML chips with short labels
    Given the viewport is 375px wide
    And the user navigates to the Ask Agy page
    Then there should be exactly 6 suggestion chips in the chip grid
    And each chip should have an emoji icon
    And the suggestion chips should be HTML button elements with class "suggested-chip"
    And the chips should display short labels not full query text
    And the first chip should contain "Payments at JP Morgan"

  # =============================================================================
  # INPUT AREA
  # =============================================================================

  Scenario: Input field is ready for questions
    Given the viewport is 1024px wide
    And the user navigates to the Ask Agy page
    Then the input field should have placeholder text
    And the input should not have a red border

  Scenario: Input and button stay on same line
    Given the viewport is 1024px wide
    And the user navigates to the Ask Agy page
    When the viewport is 800px wide
    Then the input field and button should remain on the same row

  Scenario: Submit question via Enter key
    Given the viewport is 1024px wide
    And the user navigates to the Ask Agy page
    And the user types "Tell me about leadership" in the input
    When the user presses Enter
    Then the thinking indicator should appear
    And the query should be processed

  Scenario: Submit button is disabled on fresh load
    Given the viewport is 1024px wide
    And the user navigates to the Ask Agy page
    Then the submit button should be visible
    And the submit button should be disabled

  Scenario: Submit button has correct label and is a primary button
    Given the viewport is 1024px wide
    And the user navigates to the Ask Agy page
    Then the submit button should contain "Ask Agy"
    And the submit button should be a primary button

  # =============================================================================
  # RESPONSIVE DESIGN (CSS-only -- navigate at 1024px, resize to test CSS)
  # =============================================================================

  Scenario: Layout adapts to narrow screens
    Given the viewport is 1024px wide
    And the user navigates to the Ask Agy page
    When the viewport is 600px wide
    Then content should not overflow horizontally

  Scenario: Layout adapts to wide screens
    Given the viewport is 1024px wide
    And the user navigates to the Ask Agy page
    When the viewport is 1400px wide
    Then the intro section should be centered
    And there should be margin on both sides
