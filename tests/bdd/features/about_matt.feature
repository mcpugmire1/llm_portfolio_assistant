Feature: My Profile — Content polish bundle (MATTGPT-068)
  As a recruiter or hiring manager landing on My Profile
  I want the page to be scannable, interactive, and free of redundant content
  So that I can navigate to the section I need and try the AI assistant directly
  from the page that pitches it.

  # Background:
  # MATTGPT-068 was scoped from seven locked scenarios (six decisions) on
  # May 15, 2026 down to five scenarios on May 27, 2026 after live design
  # review against the about_matt_wireframe.html spec. Two locked decisions
  # were reversed:
  #   - Anchor nav (originally decision 5) — removed entirely. Doesn't work
  #     reliably in Streamlit without JS hackery; no validated user need.
  #     Section header ids and the post-hero nav are no longer required.
  #   - Stats bar parity (originally decision 1) — reverted. The 5-card
  #     stats bar with "4x Delivery Acceleration" is restored on My Profile;
  #     the inconsistency with the Home hero's 4-card bar is accepted.
  # The chip-containment fix was also tightened to require true DOM nesting
  # inside the CTA card rather than the visual-only treatment of the
  # first Green pass.
  #
  # The four remaining decisions:
  #   1. Sample questions clickable — the four "Try asking" prompts at lines
  #      1199-1204 are currently <li> plain text inside a single st.markdown
  #      block. Convert to four st.button calls using the chip→Ask pattern from
  #      category_cards.py:55-57 / story_detail.py:203-218 (set seed_prompt +
  #      __ask_from_suggestion__ + active_tab="Ask Agy", then st.rerun()).
  #      Define the four prompt strings as ABOUT_MATT_SEED_QUESTIONS at module
  #      scope so BDD + eval can import them. Per the May 27 wireframe, the
  #      buttons must render INSIDE the CTA card container (DOM-nested), not
  #      as visual-only siblings below it.
  #
  #   2. Click routing — when a sample question button is clicked, the user
  #      should land on Ask Agy with the prompt pre-loaded and auto-fired.
  #      Assertion strategy is DOM-observable end-to-end UX (navigation visible,
  #      user message in chat, assistant response streaming) — Playwright cannot
  #      read st.session_state, so session-state assertions are deliberately
  #      avoided here. Behavioral equivalence to the chip plumbing is implicit:
  #      a user message that matches the button label AND a streaming assistant
  #      response can only happen if seed_prompt + __ask_from_suggestion__ +
  #      active_tab were set correctly.
  #
  #   3. Footer copy removal — once questions are clickable, the "Head to Ask
  #      Agy in the navigation above" sentence and the "Real AI assistant •
  #      130+ projects • Instant answers • Available 24/7" bullets (lines
  #      1205-1208) are redundant. Remove entirely. The May 27 wireframe also
  #      drops the "Try asking questions like:" label — chips speak for
  #      themselves.
  #
  #   4. DevOps & Quality card merge — .details-grid is 2-column; with 7 cards
  #      the bottom row had 1 orphan (DevOps & Quality, lines 1157-1164). Merge
  #      its content into the CI/CD Pipeline card (lines 1129-1137) — both
  #      already reference CI/CD, so the merge removes the orphan AND the
  #      redundancy in one move. Shipped in the original Green pass; unaffected
  #      by the May 27 amendments.
  #
  #   5. Code block in <details> — the 5-Stage RAG Pipeline code block (lines
  #      1062-1091) is a wall of Python mid-page. Wrap in native HTML
  #      <details><summary>Show code</summary>...</details> inside the existing
  #      markdown (no st.expander → no markdown-block split needed). Collapsed
  #      by default — non-technical readers skip past, technical readers expand.
  #
  # CLAUDE.md "Streamlit markdown call count" rule applies to this page if any
  # change touches CSS injection order. My Profile does NOT use the
  # .conversation-header negative margin (that's role_match.py / Ask Agy),
  # but the principle of consolidating st.markdown calls still applies.

  Background:
    Given the user navigates to the My Profile page

  # ---------------------------------------------------------------------------
  # FOOTER COPY REMOVAL (decision 3)
  # ---------------------------------------------------------------------------

  Scenario: Redundant CTA footer copy is absent from the See It In Action card
    Then the text "Head to Ask Agy in the navigation above to try it yourself" should not appear on the page
    And the text "Real AI assistant • 130+ projects • Instant answers • Available 24/7" should not appear on the page

  # ---------------------------------------------------------------------------
  # SEE IT IN ACTION REMOVAL (MATTGPT-093)
  # CTA card relocated to How I Built MattGPT dialog (how_i_built_dialog.py §9).
  # ---------------------------------------------------------------------------

  Scenario: See It In Action heading is not present on the page
    Then the text "See It In Action" should not appear on the page

  # ---------------------------------------------------------------------------
  # CAREER EVOLUTION TIMELINE — row 7 update (MATTGPT-093, Item 1)
  # Liquid Studio stays. Count stays at 7. Sabbatical closes to 2023-2026.
  # Rows 2 (2019-2023) and 3 (2016-2023) are concurrent — intentional.
  # ---------------------------------------------------------------------------

  Scenario: Career Evolution timeline has exactly seven entries
    Then the career evolution timeline should have 7 entries

  Scenario: Concurrent Accenture roles 2019-2023 and 2016-2023 are both present
    Then the career timeline should contain period "2019-2023"
    And the career timeline should contain period "2016-2023"

  Scenario: Liquid Studio row is present in the timeline
    Then the career timeline should contain "Liquid Studio"

  Scenario: Pre-Accenture row names both Cendian Corporation and Wellfound Technology
    Then the career timeline should contain "Cendian Corporation"
    And the career timeline should contain "Wellfound Technology"

  Scenario: Sabbatical row shows 2023-2026 not 2023-Present
    Then the career timeline should contain period "2023-2026"
    And the career timeline should not contain "2023–Present"

  # ---------------------------------------------------------------------------
  # COMPETENCY RENAME (MATTGPT-093, Item 2)
  # ---------------------------------------------------------------------------

  Scenario: Agile at Scale competency is renamed to Product delivery at scale
    Then the competencies grid should contain a card with heading "Product delivery at scale"
    And the competencies grid should not contain a card with heading "Agile at Scale"

  # ---------------------------------------------------------------------------
  # HOW I LEAD (MATTGPT-093, Item 3)
  # ---------------------------------------------------------------------------

  Scenario: Leadership section is titled How I Lead
    Then the section heading "How I Lead" should be visible
    And the section heading "Leadership Philosophy" should not be visible

  Scenario: How I Lead section contains the four locked values
    Then the How I Lead section should contain "Outcomes over output"
    And the How I Lead section should contain "Experimentation over certainty"
    And the How I Lead section should contain "High-trust, sustainable teams"
    And the How I Lead section should contain "Grow the people"

  Scenario: Replaced leadership values are absent from How I Lead
    Then the How I Lead section should not contain "Servant Leadership"
    And the How I Lead section should not contain "Continuous Learning"
    And the How I Lead section should not contain "Experimentation Culture"

  # ---------------------------------------------------------------------------
  # SIGNALS PANEL — replaces stats bar (MATTGPT-093, expanded scope)
  # ---------------------------------------------------------------------------

  Scenario: Stats bar is not present in the DOM on My Profile
    Then the profile stats bar should not be present in the DOM

  Scenario: Signals panel is present with six tiles
    Then the signals panel should be visible
    And the signals panel should have 6 tiles

  Scenario: Signals panel tile values match the wireframe spec
    Then the signals panel should contain "Senior leader"
    And the signals panel should contain "Director, Cloud Innovation Center"
    And the signals panel should contain "150+ practitioners"
    And the signals panel should contain "Atlanta"
    And the signals panel should contain "Active search"
    And the signals panel should contain "Hybrid or in-person"

  # ---------------------------------------------------------------------------
  # IN MY OWN WORDS — voice block (MATTGPT-093, expanded scope)
  # Step defs scope assertions to the "In my own words" container.
  # ---------------------------------------------------------------------------

  Scenario: In my own words section is present with correct heading
    Then the section heading "In my own words" should be visible

  Scenario: In my own words voice block contains the brand line and referral close
    Then the "In my own words" section should contain "I build what's next, modernize what's not"
    And the "In my own words" section should contain "Career built through networking and referrals"

  # ---------------------------------------------------------------------------
  # FOR A REFERRER — snippet and action buttons (MATTGPT-093, expanded scope)
  # Step defs scope button assertions to the "For a referrer" container.
  # ---------------------------------------------------------------------------

  Scenario: For a referrer section is present with correct heading
    Then the section heading "For a referrer" should be visible

  Scenario: For a referrer section contains snippet text and action buttons
    Then the "For a referrer" section should contain a copy snippet block
    And the "For a referrer" section should contain action button text "Copy snippet"
    And the "For a referrer" section should contain action button text "Download PDF"

  # ---------------------------------------------------------------------------
  # PROFILE HEADER SUBTITLE — locked target text for feature/ui-redesign branch (MATTGPT-093)
  # ---------------------------------------------------------------------------

  Scenario: Profile header subtitle matches the locked production text
    Then the profile header should contain "Engineering leader · builds organizations from zero · platform modernization · AI · Atlanta · open to relocate"
