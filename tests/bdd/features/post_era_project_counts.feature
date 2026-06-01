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
  # in BOTH the hero subtitle <p> AND the stats bar .stat-number. Home cards
  # render in .home-cat-meta (category_cards.py:402, 407). Step defs compute
  # the expected post-Era counts dynamically from the corpus to survive
  # corpus growth — no hardcoded "32" / "48".

  Scenario: Banking landing displays post-Era project count in hero and stats bar
    Given the user navigates to the Banking landing page
    Then the Banking hero subtitle should contain the post-Era Banking count
    And the Banking stats bar should display the post-Era Banking count

  Scenario: Cross-Industry landing displays post-Era project count in hero and stats bar
    Given the user navigates to the Cross-Industry landing page
    Then the Cross-Industry hero subtitle should contain the post-Era Cross-Industry count
    And the Cross-Industry stats bar should display the post-Era Cross-Industry count

  Scenario: Home category cards display post-Era project counts
    Given the user navigates to the home page
    Then the Banking category card should display the post-Era Banking count
    And the Cross-Industry category card should display the post-Era Cross-Industry count
