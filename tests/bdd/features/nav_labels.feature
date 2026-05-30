Feature: Navigation labels — wireframe-locked rename (MATTGPT-100)
  As a recruiter or warm CTO scanning the site
  I want the navigation to read in the wireframe-locked taxonomy
  So that My Work / Ask Agy / My Profile match the labels every other
  surface (modals, footer links, badges) references

  # MATTGPT-100. The May 29, 2026 wireframe locks the 5 nav labels at
  # Home / My Work / Ask Agy / Role Match / My Profile. Strategy B
  # coordinated rename: nav label text + session_state["active_tab"]
  # values rename together; file paths stay (about_matt.py,
  # explore_stories.py, ask_mattgpt/ keep their names — first
  # implementation-level rename, not the second).
  #
  # active_tab mapping (Green-phase contract; not asserted in scenarios):
  #   "Home"            -> "Home"            (unchanged)
  #   "Explore Stories" -> "My Work"
  #   "Ask MattGPT"     -> "Ask Agy"
  #   "Role Match"      -> "Role Match"      (unchanged)
  #   "About Matt"      -> "My Profile"
  #
  # Scenarios assert DOM-observable state — visible nav label text and
  # surface render after click — not session_state["active_tab"] reads.

  Background:
    Given the user navigates to the home page

  Scenario: Navigation renders the wireframe-locked labels
    Then the navigation should display "Home", "My Work", "Ask Agy", "Role Match", and "My Profile"

  Scenario: Navigation does not display any pre-rename labels
    Then the navigation should not display "Explore Stories", "Ask MattGPT", or "About Matt"

  Scenario: Clicking a renamed label routes to the same underlying surface
    When the user clicks the "My Work" navigation label
    Then the project-stories filter UI should be shown
