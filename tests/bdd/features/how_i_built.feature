Feature: How I Built MattGPT deep-link surface (MATTGPT-102)
  As a recruiter or warm-intro CTO arriving via a Why Agy modal / Ask Agy
  Landing Why Agy section / Profile signals panel link
  I want a standalone page that holds the technical deep-dive previously
  buried at the bottom of My Profile, with a back link that returns me to
  wherever I came from
  So that the content gets its own surface (not crowding My Profile) and
  I can return to my browsing context with one click

  # MATTGPT-102. Per the May 29, 2026 wireframe (line 929 section sub):
  # "Secondary surface (no top nav). Standalone deep-link only, accessed
  #  from Why Agy modal, Ask Agy Landing Why Agy section, Profile signals
  #  panel. Content relocated from About Matt's How I Built section."
  #
  # URL pattern: ?route=how-i-built[&from=<surface-slug>]
  #   - route=how-i-built activates the surface (mirrors existing
  #     ?story=story-id deep-link pattern at app.py:309-312).
  #   - from=<surface-slug> drives the back-link target. Missing → defaults
  #     to "My Profile" (where the content originally lived).
  #
  # IN SCOPE:
  #   - New page ui/pages/how_i_built.py with content relocated from
  #     about_matt.py:155-416 (the "MATTGPT DEEP-DIVE" / "How I Built
  #     MattGPT" section).
  #   - URL query param entry: ?route=how-i-built.
  #   - Optional from param for context-aware back link.
  #   - Removal of the block from about_matt.py to avoid duplicate content.
  #   - Top-left back link, label varies by from slug, click returns to
  #     that surface via session_state.active_tab change + rerun.
  #
  # OUT OF SCOPE:
  #   - The Why Agy modal itself (MATTGPT-101) — the modal's footer link
  #     that sets ?route=how-i-built&from=<surface> ships there.
  #   - Ask Agy Landing Why Agy section's link to this surface — ships
  #     with the Ask Agy Landing refresh, not here.
  #   - Profile signals panel link — ships when the Profile signals panel
  #     is implemented.
  #   - Navbar treatment: navbar still renders on this page (for orientation
  #     and as the navigation-away fallback). No tab is highlighted as
  #     active because the surface isn't in the main nav.
  #
  # Scenarios assert DOM-observable state: page heading + key landmark cards
  # for the deep-link render, back-link text for the from-driven label,
  # and post-click navigation for the return path. No st.session_state reads
  # per the BDD DOM-observable rule.

  Scenario: URL deep-link renders the How I Built page
    Given the user navigates to "/?route=how-i-built"
    Then the "How I Built MattGPT" heading should be visible
    And the "The Problem" deep-dive card should be visible

  Scenario: Back link displays the origin surface when from param is provided
    Given the user navigates to "/?route=how-i-built&from=ask-agy"
    Then the back link should be visible
    And the back link text should contain "Ask Agy"

  Scenario: Back link defaults to My Profile when from param is missing
    Given the user navigates to "/?route=how-i-built"
    Then the back link should be visible
    And the back link text should contain "My Profile"

  Scenario: My Profile page no longer contains the How I Built section
    Given the user navigates to the My Profile page
    Then the "How I Built MattGPT" heading should NOT be visible on the My Profile page

  # Dialog entry paths — How I Built as @st.dialog triggered sequentially
  # from Why Agy and How Agy Searches footer buttons.

  Scenario: Why Agy footer button opens How I Built dialog
    Given I navigate to the "Ask Agy" page at viewport width 1280
    And I click the "i" badge on the Agy intro avatar
    And a dialog with title "Why Agy?" is visible
    When I click the button "Curious how I was built? Read the technical deep-dive →"
    Then a dialog with title "How I Built MattGPT" is visible

  Scenario: How Agy Searches footer button opens How I Built dialog
    Given the user is on the Ask Agy landing page
    And the user clicks the "How Agy searches" button
    And the How Agy Searches dialog is visible
    When I click the button "See how I built it →"
    Then a dialog with title "How I Built MattGPT" is visible
