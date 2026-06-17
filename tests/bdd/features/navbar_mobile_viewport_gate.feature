Feature: Mobile navbar IIFE viewport gate (MATTGPT-135)
  The mobile navbar IIFE must exit immediately on desktop viewports
  so that mobile-header, mobile-nav-overlay, and mobile-nav-dropdown
  are never injected into window.parent.document on wide screens.

  Scenario: On desktop viewport, no mobile elements injected into parent document
    Given the viewport is 1280px wide
    And the user navigates to the home page
    Then "#mobile-header" should not exist in the parent document
    And "#mobile-nav-dropdown" should not exist in the parent document
    And "#mobile-nav-overlay" should not exist in the parent document

  Scenario: On mobile viewport, mobile header renders correctly
    Given the viewport is 375px wide
    And the user navigates to the home page
    Then "#mobile-header" should exist in the parent document
    And "#mobile-nav-dropdown" should exist in the parent document
