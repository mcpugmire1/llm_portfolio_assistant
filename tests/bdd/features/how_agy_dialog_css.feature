Feature: How Agy Searches dialog — CSS correctness regression guards (MATTGPT-110)
  As a developer maintaining the How Agy Searches @st.dialog
  I want CSS regressions to be caught immediately
  So that footer button styling, design system variables, and mobile layout don't silently break

  # Regression guards for issues found and fixed during MATTGPT-110:
  # 1. Footer button was rendering as a bare text link (border: none, padding: 0)
  # 2. Dialog CSS used hardcoded hex instead of app design system variables
  # 3. Cards-row forced 2-col on mobile, causing heavy text wrapping at 375/430px

  Background:
    Given the user navigates to the Ask Agy landing page
    And the user clicks the "How Agy searches" button

  Scenario: Footer button renders as a styled button not a bare text link
    Then the footer element inside the dialog should be a button
    And the footer button should have a visible border
    And the footer button should have non-zero padding
    And the footer button width should fill the dialog content width

  Scenario: Dialog elements use app design system CSS variables
    Then the query card background should match the resolved value of --bg-card
    And the step title color should match the resolved value of --text-primary
    And the card description color should match the resolved value of --text-secondary
    And the query card font-size should be 13px

  Scenario Outline: Modal renders single-column cards on mobile
    Given the viewport is resized to <width>px wide
    Then the search cards should render in a single column
    And the desktop pipeline flow should not be visible
    And the mobile pipeline summary should be visible
    And the pipeline summary font-size should be 12px
    And the footer button should be full width

    Examples:
      | width |
      | 375   |
      | 430   |
