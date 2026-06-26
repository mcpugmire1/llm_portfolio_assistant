Feature: Ask Agy stale hero suppression on navigation
  As a visitor navigating away from Ask Agy
  I want the Ask Agy landing hero to be hidden during the rerun window
  So that it does not ghost over the incoming page

  # Implementation note: the blep is a sub-50ms transient visual overlap —
  # not assertable by screenshot polling. These scenarios test the three
  # preconditions the fix depends on via MutationObserver, which fires
  # synchronously when Streamlit sets data-stale="true", allowing a
  # deterministic getComputedStyle read at the exact instant of staling.
  # Manual visual check (Ask Agy -> My Work, Ask Agy -> Role Match)
  # remains the coverage for the visual symptom itself.

  Background:
    Given the user navigates to the Ask Agy landing page

  Scenario: Navigating away from Ask Agy hides the stale landing hero
    Given a mutation observer is recording computed visibility when containers gain data-stale
    When the user navigates to Role Match
    Then the Role Match header should be visible
    And the landing hero container was computed visibility hidden at the instant it became stale

  Scenario: Streamlit still marks prior-page elements stale during navigation
    Given a mutation observer is watching for data-stale across the element tree
    When the user navigates to Role Match
    Then the Role Match header should be visible
    And at least one element container was marked data-stale during the transition

  Scenario: The Ask Agy landing exposes the stale-guard hooks
    Then a stElementContainer wraps a node with class "main-intro-section"
    And a stElementContainer wraps a node with class "ask-header-landing"
