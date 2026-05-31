Feature: Home Hero — Recruiter Routing CTA
  As a cold recruiter triaging Matt's portfolio in 90 seconds
  I want the hero to surface a CTA that names my job and routes to Role Match
  So that I reach the surface built for the placement decision instead of bouncing

  # MATTGPT-087. CTA structure locked from the May 29, 2026 wireframe: the hero
  # carries two CTAs — Role Match (primary, "Recruiting for a role? Match it",
  # routes to Role Match) and Ask Agy (secondary, "Want to dig deeper? Ask Agy").
  # No My Work CTA in the hero; Explore is reached via the top nav.
  # Supersedes the May 28 "tertiary CTA below Ask Agy" framing.
  #
  # Assertions are DOM-observable only (button labels visible, target surface
  # rendered after click). Visual primary/secondary weight is CSS and is not
  # asserted here. The -092 hero seniority anchor ships in a separate change.

  Background:
    Given the user navigates to the home page

  Scenario: Hero surfaces a recruiter-routing CTA and an Ask Agy CTA
    Then the hero should show a CTA whose label names the recruiter's job
    And the hero should show an Ask Agy CTA

  Scenario: Recruiter CTA navigates to Role Match
    When the user clicks the recruiter-routing CTA in the hero
    Then the Role Match surface should be shown
