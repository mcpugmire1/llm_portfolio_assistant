Feature: Home Seniority Anchor — scope/outcome positioning (MATTGPT-092)
  As Matt's positioning signal to triaging recruiters and decision-makers
  I want the Home page to anchor a scope/outcome positioning claim without naming a title
  So that the page narrows the role range through scope (builder-operator)
  rather than declaring Director-vs-VP, which forecloses the broader target taxonomy

  # MATTGPT-092. Locked principle (from commit f0ad706, May 29, 2026): the
  # Home seniority signal is a scope/outcome anchor, NOT a title chip.
  #
  # Locked positioning clause (verbatim, hero band):
  #   "In active search for a role where building the engineering
  #    organization, establishing the culture, and delivering results are
  #    part of the same job."
  # The load-bearing sub-clause "are part of the same job" is the
  # builder-operator positioning signal; Scenario 1 below asserts it on-page.
  #
  # The Stats "Level" tile must not carry a concrete title chip either —
  # e.g. "Director · VP target" is exactly the failure mode this ticket
  # guards against. Scenario 2 is the regression guard against that shape;
  # it spans the hero region AND the stats bar because the title trap could
  # leak into either.
  #
  # Placement: the seniority band is a SEPARATE COMPONENT — it does NOT live
  # inside render_hero(). The gray strip in the wireframe sits outside the
  # hero card.

  Background:
    Given the user navigates to the home page

  Scenario: Home page carries the locked positioning clause
    Then the hero region should contain the locked positioning clause "are part of the same job"

  Scenario: Home page does not declare a level title in the positioning region
    Then no level-title token (Director, VP, Vice President, SVP) should appear in the hero region or the stats bar
