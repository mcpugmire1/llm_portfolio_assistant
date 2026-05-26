Feature: About Matt — Content polish bundle (MATTGPT-068)
  As a recruiter or hiring manager landing on About Matt
  I want the page to be scannable, interactive, and free of redundant content
  So that I can navigate to the section I need and try the AI assistant directly
  from the page that pitches it.

  # Background:
  # MATTGPT-068 bundles six locked content-polish decisions from the May 15, 2026
  # UX assessment. The page (ui/pages/about_matt.py, ~1500 lines) is the deep
  # technical narrative — it must be skimmable for non-technical recruiters AND
  # detailed enough for engineering hiring managers.
  #
  # The six decisions:
  #   1. Stats bar parity — drop "4x Delivery Acceleration" from the 5-stat
  #      About Matt bar (line 884). The Home hero bar (hero.py:298-311) shows 4
  #      stats; the About bar should match. The 4x metric already exists in the
  #      Career Evolution CIC timeline entry (line 916), so this is removal-only.
  #
  #   2. Sample questions clickable — the four "Try asking" prompts at lines
  #      1199-1204 are currently <li> plain text inside a single st.markdown
  #      block. Convert to four st.button calls using the chip→Ask pattern from
  #      category_cards.py:55-57 / story_detail.py:203-218 (set seed_prompt +
  #      __ask_from_suggestion__ + active_tab="Ask MattGPT", then st.rerun()).
  #      Define the four prompt strings as ABOUT_MATT_SEED_QUESTIONS at module
  #      scope so BDD + eval can import them.
  #
  #   3. Click routing — when a sample question button is clicked, the user
  #      should land on Ask MattGPT with the prompt pre-loaded and auto-fired.
  #      Assertion strategy is DOM-observable end-to-end UX (navigation visible,
  #      user message in chat, assistant response streaming) — Playwright cannot
  #      read st.session_state, so session-state assertions are deliberately
  #      avoided here. Behavioral equivalence to the chip plumbing is implicit:
  #      a user message that matches the button label AND a streaming assistant
  #      response can only happen if seed_prompt + __ask_from_suggestion__ +
  #      active_tab were set correctly.
  #
  #   4. Footer copy removal — once questions are clickable, the "Head to Ask
  #      MattGPT in the navigation above" sentence and the "Real AI assistant •
  #      130+ projects • Instant answers • Available 24/7" bullets (lines
  #      1205-1208) are redundant. Remove entirely.
  #
  #   5. Anchor nav — page is 3,000+ words. Add id="career", id="mattgpt",
  #      id="competencies", id="philosophy" to the four section headers
  #      (lines 896, 957, 1218, 1303) and render a nav block right after the
  #      hero linking to all four. Placement locked per ticket (after hero,
  #      not navbar).
  #
  #   6. DevOps & Quality card merge — .details-grid is 2-column; with 7 cards
  #      the bottom row has 1 orphan (DevOps & Quality, lines 1157-1164). Merge
  #      its content into the CI/CD Pipeline card (lines 1129-1137) — both
  #      already reference CI/CD, so the merge removes the orphan AND the
  #      redundancy in one move.
  #
  #   7. Code block in <details> — the 5-Stage RAG Pipeline code block (lines
  #      1062-1091) is a wall of Python mid-page. Wrap in native HTML
  #      <details><summary>Show code</summary>...</details> inside the existing
  #      markdown (no st.expander → no markdown-block split needed). Collapsed
  #      by default — non-technical readers skip past, technical readers expand.
  #
  # CLAUDE.md "Streamlit markdown call count" rule applies to this page if any
  # change touches CSS injection order. About Matt does NOT use the
  # .conversation-header negative margin (that's role_match.py / Ask MattGPT),
  # but the principle of consolidating st.markdown calls still applies.

  Background:
    Given the user navigates to the About Matt page

  # ---------------------------------------------------------------------------
  # STATS BAR PARITY — drop 4x Delivery Acceleration (decision 1)
  # ---------------------------------------------------------------------------

  Scenario: Stats bar renders exactly four stats with no Delivery Acceleration card
    Then the About Matt stats bar should contain exactly 4 stat cards
    And no stat card labeled "Delivery Acceleration" should be visible in the stats bar

  # ---------------------------------------------------------------------------
  # SAMPLE QUESTIONS CLICKABLE — buttons replace <li> text (decisions 2, 3)
  # ---------------------------------------------------------------------------

  Scenario: Four sample question buttons render with labels from ABOUT_MATT_SEED_QUESTIONS
    Then four sample question buttons should be visible in the See It In Action card
    And each button label should match a string in ABOUT_MATT_SEED_QUESTIONS
    And the four legacy <li> sample-question lines should not be present as plain text

  Scenario: Clicking a sample question routes to Ask MattGPT and auto-fires the question
    When the user clicks the first sample question button
    Then the Ask MattGPT conversation view should be visible
    And a user message matching that button's label should be visible in the chat
    And an assistant response should begin streaming in the chat

  # ---------------------------------------------------------------------------
  # FOOTER COPY REMOVAL (decision 4)
  # ---------------------------------------------------------------------------

  Scenario: Redundant CTA footer copy is absent from the See It In Action card
    Then the text "Head to Ask MattGPT in the navigation above to try it yourself" should not appear on the page
    And the text "Real AI assistant • 130+ projects • Instant answers • Available 24/7" should not appear on the page

  # ---------------------------------------------------------------------------
  # ANCHOR NAVIGATION (decision 5)
  # ---------------------------------------------------------------------------

  Scenario: Anchor nav block renders post-hero with four links to section ids
    Then an anchor nav block should be visible immediately after the hero
    And the anchor nav should contain a link to "#career"
    And the anchor nav should contain a link to "#mattgpt"
    And the anchor nav should contain a link to "#competencies"
    And the anchor nav should contain a link to "#philosophy"
    And the Career Evolution section header should have id "career"
    And the How I Built MattGPT section header should have id "mattgpt"
    And the Core Competencies section header should have id "competencies"
    And the Leadership Philosophy section header should have id "philosophy"

  # ---------------------------------------------------------------------------
  # DEVOPS & QUALITY MERGE (decision 6)
  # ---------------------------------------------------------------------------

  Scenario: DevOps & Quality card is absent and CI/CD Pipeline card carries the merged bullets
    Then no detail card with the heading "DevOps & Quality" should be visible
    And the "CI/CD Pipeline" detail card should be visible
    And the "CI/CD Pipeline" detail card should mention testing
    And the "CI/CD Pipeline" detail card should mention monitoring
    And the "CI/CD Pipeline" detail card should mention security

  # ---------------------------------------------------------------------------
  # CODE BLOCK COLLAPSED BY DEFAULT (decision 7)
  # ---------------------------------------------------------------------------

  Scenario: RAG pipeline code block is wrapped in a collapsed details element
    Then the 5-Stage RAG Pipeline code block should be wrapped in a <details> element
    And that <details> element should not have the "open" attribute
    And a <summary> element should be visible as the affordance to expand the code
