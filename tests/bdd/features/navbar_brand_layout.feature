Feature: Navbar desktop layout — brand-left + space-between (MATTGPT-106)
  As a recruiter or warm CTO landing on the desktop site
  I want the navbar to anchor "MattGPT" on the left and group the 5 nav
  items to the right (matching the wireframe and the existing mobile header)
  So that every desktop view carries a persistent brand identity anchor
  in the conventional brand-left + nav-right pattern

  # MATTGPT-106. May 29, 2026 wireframe locks the desktop navbar to a
  # brand-left + space-between layout. Mobile (<768px) already renders
  # "MattGPT" left of the hamburger via the .mobile-brand JS injection
  # in ui/components/navbar.py; this ticket brings desktop into alignment.
  #
  # Strategy per handoff (May 30, 2026):
  #   - Text-only brand "MattGPT" on the left. Agy avatar coordination
  #     defers to MATTGPT-101 (Why Agy modal + badge placement).
  #   - justify-content: space-evenly -> space-between on the desktop
  #     horizontal block.
  #   - 5 nav buttons retain the labels shipped by MATTGPT-100 Green
  #     (Home / My Work / Ask Agy / Role Match / My Profile) and route
  #     to the same surfaces (active_tab values unchanged from -100).
  #
  # Scenarios assert DOM-observable state — visible brand text, brand
  # positioned left of the first nav button via bounding-box comparison,
  # the 5 nav labels still rendering, and post-click routing to the same
  # surface as production today. No session_state reads (Playwright cannot
  # observe st.session_state directly — see feedback_bdd_dom_observable).

  Background:
    Given the user navigates to the home page

  Scenario: Desktop navbar anchors the "MattGPT" brand to the left of the nav buttons
    Then the navbar should display "MattGPT" to the left of the "Home" nav button

  Scenario: All five wireframe-locked nav labels still render after the layout change
    Then the navigation should display "Home", "My Work", "Ask Agy", "Role Match", and "My Profile"

  Scenario: Clicking a nav label still routes to its surface (no regression)
    When the user clicks the "My Work" navigation label
    Then the project-stories filter UI should be shown
