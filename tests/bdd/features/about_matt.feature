Feature: About Matt — Content polish bundle (MATTGPT-068)
  As a recruiter or hiring manager landing on About Matt
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
  #     stats bar with "4x Delivery Acceleration" is restored on About Matt;
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
  #      __ask_from_suggestion__ + active_tab="Ask MattGPT", then st.rerun()).
  #      Define the four prompt strings as ABOUT_MATT_SEED_QUESTIONS at module
  #      scope so BDD + eval can import them. Per the May 27 wireframe, the
  #      buttons must render INSIDE the CTA card container (DOM-nested), not
  #      as visual-only siblings below it.
  #
  #   2. Click routing — when a sample question button is clicked, the user
  #      should land on Ask MattGPT with the prompt pre-loaded and auto-fired.
  #      Assertion strategy is DOM-observable end-to-end UX (navigation visible,
  #      user message in chat, assistant response streaming) — Playwright cannot
  #      read st.session_state, so session-state assertions are deliberately
  #      avoided here. Behavioral equivalence to the chip plumbing is implicit:
  #      a user message that matches the button label AND a streaming assistant
  #      response can only happen if seed_prompt + __ask_from_suggestion__ +
  #      active_tab were set correctly.
  #
  #   3. Footer copy removal — once questions are clickable, the "Head to Ask
  #      MattGPT in the navigation above" sentence and the "Real AI assistant •
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
  # change touches CSS injection order. About Matt does NOT use the
  # .conversation-header negative margin (that's role_match.py / Ask MattGPT),
  # but the principle of consolidating st.markdown calls still applies.

  Background:
    Given the user navigates to the About Matt page

  # ---------------------------------------------------------------------------
  # SAMPLE QUESTIONS CLICKABLE — buttons replace <li> text (decisions 1, 2)
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
  # FOOTER COPY REMOVAL (decision 3)
  # ---------------------------------------------------------------------------

  Scenario: Redundant CTA footer copy is absent from the See It In Action card
    Then the text "Head to Ask MattGPT in the navigation above to try it yourself" should not appear on the page
    And the text "Real AI assistant • 130+ projects • Instant answers • Available 24/7" should not appear on the page

  # ---------------------------------------------------------------------------
  # DEVOPS & QUALITY MERGE (decision 4)
  # ---------------------------------------------------------------------------

  Scenario: DevOps & Quality card is absent and CI/CD Pipeline card carries the merged bullets
    Then no detail card with the heading "DevOps & Quality" should be visible
    And the "CI/CD Pipeline" detail card should be visible
    And the "CI/CD Pipeline" detail card should mention testing
    And the "CI/CD Pipeline" detail card should mention monitoring
    And the "CI/CD Pipeline" detail card should mention security

  # ---------------------------------------------------------------------------
  # CODE BLOCK COLLAPSED BY DEFAULT (decision 5)
  # ---------------------------------------------------------------------------

  Scenario: RAG pipeline code block is wrapped in a collapsed details element
    Then the 5-Stage RAG Pipeline code block should be wrapped in a <details> element
    And that <details> element should not have the "open" attribute
    And a <summary> element should be visible as the affordance to expand the code
