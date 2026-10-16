Feature: Landing page + Home card project counts align with post-Era convention (MATTGPT-104)
  As a recruiter or hiring manager navigating between Home and a landing page
  I want the project count for an industry to be the same number everywhere it appears
  So that I don't see "33 projects" on Home and "32 projects" on the Banking landing for
  the same filter — a data-quality smell that undermines the polish of the rest of the site

  # MATTGPT-104. Phase 1 audit (in ticket body): the 4 displayed numbers
  # (Banking 33 vs 32 vs Cross-Industry 57 vs 48) all traced to two filter
  # regimes — raw Industry filter vs. raw + Era != "Leadership & Professional
  # Narrative". Phase 2 fix: align landing page hero/stats + Home card meta
  # to the POST-ERA convention, which Timeline + landing card grids + (post
  # MATTGPT-098) Explore Stories already use.
  #
  # Sequencing: MATTGPT-098 ships first (Explore Stories post-Era default).
  # Without -098, -104 would create a worse interim state (Home shows 32,
  # Explore Stories still shows 33 for the same filter).
  #
  # DOM-observable note: Banking + Cross-Industry landings render the count
  # in the hero subtitle <p>. The landing stats bar was removed on purpose,
  # so MATTGPT-254 dropped its assertions. Home cards render descriptive copy
  # in .home-cat-meta. Step defs compute the expected post-Era counts
  # dynamically from the corpus to survive corpus growth, with no hardcoded
  # "32" or "48".

  Scenario: Banking landing displays post-Era project count in hero
    Given the user navigates to the Banking landing page
    Then the Banking hero subtitle should contain the post-Era Banking count

  Scenario: Cross-Industry landing displays post-Era project count in hero
    Given the user navigates to the Cross-Industry landing page
    Then the Cross-Industry hero subtitle should contain the post-Era Cross-Industry count

  Scenario: Home category cards display descriptive copy
    Given the user navigates to the home page
    Then the Banking category card meta should contain "Payments infrastructure"
    And the Cross-Industry category card meta should contain "Cloud-native products"
