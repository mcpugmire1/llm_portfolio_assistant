Feature: How Agy Searches — migrate inline expander to @st.dialog (MATTGPT-110)
  As a recruiter or hiring manager on the Ask Agy surface
  I want "How Agy searches" to open as a focused dialog overlay
  So that the conversation or landing page stays intact behind the modal
  And I can dismiss it cleanly without losing my place

  # MATTGPT-110. Migrates the "How Agy searches" inline expander to @st.dialog.
  # Technical Details block removed (content moves to How I Built modal).
  # Footer st.button opens How I Built sequentially (active_dialog pattern).
  # Applies to both Ask Agy Landing and Ask Agy Conversation views.
  #
  # DOM-observable: dialog title visible, content text visible, inline
  # wrapper absent (old pattern regression guard), footer button present.

  Background:
    Given the user navigates to the Ask Agy landing page

  Scenario: "How Agy searches" button opens a dialog overlay
    When the user clicks the "How Agy searches" button
    Then a dialog titled "How Agy searches" should be visible
    And the dialog should contain the text "You Ask"
    And the dialog should contain the text "Agy Searches"
    And the dialog should contain the text "You Get Results"

  Scenario: Dialog closes when dismissed
    When the user clicks the "How Agy searches" button
    Then a dialog titled "How Agy searches" should be visible
    When the user dismisses the dialog
    Then the dialog should not be visible

  Scenario: Inline modal wrapper is no longer present in the page body
    When the user clicks the "How Agy searches" button
    Then no inline how-agy-modal-wrapper should be present in the page body

  Scenario: Dialog contains a footer button linking to How I Built
    When the user clicks the "How Agy searches" button
    Then the dialog should contain a button with text "See how I built it"

  Scenario: "How Agy searches" dialog works on the Conversation view
    Given the user navigates to the Ask Agy conversation view
    When the user clicks the "How Agy searches" button
    Then a dialog titled "How Agy searches" should be visible
    And the dialog should contain the text "You Ask"

  Scenario: Dialog opens scrolled to top when page has been scrolled down
    Given the page has been scrolled down
    When the user clicks the "How Agy searches" button
    Then a dialog titled "How Agy searches" should be visible
    And the dialog content should be scrolled to the top
