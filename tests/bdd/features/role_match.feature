Feature: Role Match page
  As a visitor to MattGPT
  I want to paste a job description and see how Matt's experience maps to the requirements
  So that I can quickly assess fit without reading an entire resume

  # =============================================================================
  # NAVIGATION
  # =============================================================================

  Scenario: Role Match tab appears in navigation
    Given the user is on any page
    Then "Role Match" appears in the navigation bar between "Ask Agy" and "My Profile"

  Scenario: Clicking Role Match tab navigates to the page
    Given the user is on any page
    When the user clicks "Role Match" in the navigation bar
    Then the Role Match page is displayed
    And the page shows a JD text input area and a "Match this role" button

  # =============================================================================
  # RECRUITER VIEW — JD INPUT
  # =============================================================================

  Scenario: Hint text renders in the left column above the textarea
    Given the user is on the Role Match page
    Then a hint text instructing the user to paste a job description is visible in the left column above the JD textarea
    And no hint text is rendered in the right column above the results panel
    And the hint text is styled as plain secondary-color text

  Scenario: JD text area accepts pasted job description
    Given the user is on the Role Match page
    When the user pastes a job description into the text area
    Then the "Match this role" button is enabled

  Scenario: Empty text area disables the match button
    Given the user is on the Role Match page
    And the text area is empty
    Then the "Match this role" button is disabled

  # =============================================================================
  # RECRUITER VIEW — MATCH RESULTS
  # =============================================================================

  Scenario: Legend bar appears at the top of the results panel
    Given the user has submitted a job description
    When the match results are displayed
    Then a legend bar appears at the top of the results panel above the first section header
    And the legend includes a green ✓ swatch labeled "Strong match"
    And the legend includes an amber ~ swatch labeled "Partial"
    And the legend includes a red ✗ swatch labeled "Gap"
    And the legend includes a 🔗 swatch labeled "= clickable story"
    And the legend includes a green dot swatch labeled "= profile evidence"

  Scenario: Match results show required qualifications with status badges
    Given the user has submitted a job description
    When the match results are displayed
    Then each required qualification shows a 22px circular status badge: green ✓ for strong, amber ~ for partial, red ✗ for gap
    And the status badge sits in a fixed-width left gutter to the left of the requirement title
    And each qualification with a strong or partial match shows up to 2 pieces of evidence
    And clickable story chips are rendered as pills with brand purple text and a 🔗 link icon prefix
    And profile evidence is rendered as an indented text block (NOT a pill) with a small green dot prefix and muted secondary-color text
    And the pill container is reserved for short references (story chips, unresolved-story fallback) — NOT for argumentative profile evidence
    And the link icon (🔗) is used exclusively to signal a clickable story chip

  Scenario: Match results show preferred qualifications separately
    Given the user has submitted a job description with preferred qualifications
    When the match results are displayed
    Then preferred qualifications appear in a separate section below required qualifications
    And preferred qualifications use the same circular status badges as required qualifications

  Scenario: Results show all qualifications without a summary count or score
    Given the user has submitted a job description
    When the match results are displayed
    Then all qualifications are listed with individual match statuses
    And no summary count, fit score, or recommendation is visible

  Scenario: Partial match shows gap explanation
    Given a requirement is assessed as partial match
    When the match results are displayed
    Then the partial match shows a specific explanation of what is missing
    And the explanation is rendered as italic muted-color text indented to align with the chip row

  Scenario: Gap shows explanation with no story chips
    Given a requirement is assessed as a gap
    When the match results are displayed
    Then the gap shows a specific explanation of what is missing
    And no evidence chips are displayed for that requirement
    And the explanation is rendered as italic muted-color text indented to align with the chip row

  Scenario: No fit score or recommendation in recruiter view
    Given the user has not unlocked the private view
    When the match results are displayed
    Then no "High/Medium/Low" fit score is visible
    And no "Apply/Consider/Pass" recommendation is visible
    And no "Matt's Private Assessment" section is visible

  # =============================================================================
  # RECRUITER VIEW — STORY EVIDENCE
  # =============================================================================

  Scenario: Story evidence chips are clickable and expand inline
    Given the match results show a story evidence chip
    When the user clicks a story evidence chip
    Then the story detail expands inline using render_story_detail()
    And the expanded detail shows the full STAR narrative

  Scenario: Clickable story chips show pointer cursor and selected state
    Given the match results show a clickable story evidence chip
    Then the chip has a pointer cursor on hover
    When the user clicks the chip
    Then the chip is rendered in a visually selected state
    And only one chip can be in the selected state at a time

  Scenario: Profile evidence renders as an indented text block, not a pill
    Given a requirement is matched using grounding context only (evidence_type "profile")
    When the match results are displayed
    Then the profile evidence renders as a block-level text node indented to 32px
    And the block begins with a small green dot followed by "Verified profile · <description>"
    And the block has NO pill border, NO rounded background — it is plain prose, not a chip
    And the block uses muted secondary-color text
    And the block does NOT show a 🔗 link icon
    And the block does not show a pointer cursor on hover
    And clicking the profile evidence has no effect
    And the link icon (🔗) is reserved exclusively for clickable story chips
    And no "VERIFIED SKILL" pill element is rendered anywhere on the page

  Scenario: Story chip with unresolved title falls back to non-clickable pill
    Given a story evidence chip has a title that does not match any story in the corpus
    When the match results are displayed
    Then the chip renders as a pill in the "Title · Client" format with NO 🔗 link icon
    And the chip uses muted secondary-color text and a muted background to signal it is non-clickable
    And the unresolved chip remains a PILL (not a text block) because "Title · Client" is a short reference, not an argument
    And the chip does NOT show a green dot prefix (the green dot is reserved for profile evidence blocks)
    And clicking the chip has no effect
    And no selected state is applied

  Scenario: Clicking the same chip twice closes the inline detail
    Given the match results show an expanded story detail beneath a chip
    When the user clicks the same chip again
    Then the inline detail is closed
    And no story detail is rendered for that requirement

  Scenario: Clicking a different chip switches the inline detail
    Given the match results show an expanded story detail beneath a chip
    When the user clicks a different story evidence chip
    Then the previously expanded detail is closed
    And the inline detail for the newly clicked chip is rendered

  Scenario: Inline detail appears below the requirement that owns the clicked chip
    Given the user has submitted a job description
    And the match results show multiple requirements with story evidence chips
    When the user clicks a story evidence chip on a specific requirement
    Then the inline detail renders immediately below that requirement card
    And the inline detail does not render below any other requirement card

  Scenario: Profile-level evidence appears in a block above the story chip row
    Given a requirement is matched using grounding context only (evidence_type "profile")
    When the match results are displayed
    Then the profile evidence renders as a block-level text node BEFORE any story chips
    And the block is formatted as "● Verified profile · <description>" with a small green dot prefix
    And the block uses muted secondary-color text indented 32px from the card edge
    And there is no pill border or rounded background around the block
    And there is no "VERIFIED SKILL" pill element anywhere on the page

  # =============================================================================
  # PRIVATE VIEW — LOCK ICON AND PASSWORD GATE
  # =============================================================================

  Scenario: Lock icon is visible on the Role Match results panel
    Given the user is on the Role Match page
    Then a small lock icon appears at the top-right of the results panel
    And the lock icon is visually discreet and does not draw attention

  Scenario: Clicking lock icon opens password popover
    Given the user is on the Role Match page
    And no password prompt is visible
    When the user clicks the lock icon
    Then a popover appears with a single password input field

  Scenario: Correct password unlocks private view
    Given the user has clicked the lock icon
    When the user enters the correct access code
    Then the lock icon changes to indicate unlocked state
    And session state __private_mode__ is set to True
    And the popover closes

  Scenario: Incorrect password does not unlock private view
    Given the user has clicked the lock icon
    When the user enters an incorrect access code
    Then the private view remains locked
    And session state __private_mode__ is not set

  Scenario: Private mode persists within session
    Given the user has unlocked the private view
    When the user navigates to another tab and returns to Role Match
    Then the private view is still unlocked
    And the lock icon still shows unlocked state

  Scenario: Empty password submission is a no-op
    Given the user has clicked the lock icon
    When the user submits the password popover with an empty input
    Then the private view remains locked
    And session state __private_mode__ is not set
    And the popover stays open

  Scenario: Wrong password followed by correct password still unlocks
    Given the user has clicked the lock icon
    And the user has entered an incorrect access code once
    When the user enters the correct access code
    Then the private view unlocks
    And no rate-limit lockout is applied between attempts

  Scenario: Password input is masked
    Given the user has clicked the lock icon
    Then the password input has type="password"
    And typed characters are not echoed in the DOM as plain text

  Scenario: MATTGPT_PRIVATE_BYPASS_TOKEN env var unset — password submission is a silent no-op
    Given the MATTGPT_PRIVATE_BYPASS_TOKEN env var is unset
    And the user has clicked the lock icon
    When the user enters any password and submits
    Then the private view remains locked
    And no error is surfaced to the user
    And session state __private_mode__ is not set

  Scenario: Lock glyph reflects __private_mode__ state
    Given the user is on the Role Match page
    Then the lock icon shows the closed-lock glyph when session state __private_mode__ is False
    And the lock icon shows the open-lock glyph when session state __private_mode__ is True

  Scenario: Clicking the unlocked icon re-locks the session
    Given the user has unlocked the private view
    When the user clicks the lock icon
    Then session state __private_mode__ is set to False
    And the lock icon returns to the closed-lock glyph
    And no popover is shown

  Scenario: Pressing Escape inside the popover closes it without unlocking
    Given the user has clicked the lock icon
    When the user presses Escape inside the popover
    Then the popover closes
    And session state __private_mode__ is not set

  Scenario: Lock icon hidden on mobile
    Given the user is on a device with viewport width less than 1024px
    Then the lock icon is not visible

  Scenario: Browser refresh re-locks the session
    Given the user has unlocked the private view
    When the user refreshes the browser
    Then session state __private_mode__ is False
    And the lock icon shows the closed-lock glyph

  Scenario: New tab does not inherit unlocked state
    Given the user has unlocked the private view in tab A
    When the user opens MattGPT in a new tab
    Then session state __private_mode__ in the new tab is False

  Scenario: Toggling lock back hides the private assessment on next rerun
    Given the user has unlocked the private view
    And the private assessment is visible
    When the user clicks the lock icon to re-lock
    Then on the next rerun the private assessment section is not visible
    And the recruiter view content remains intact

  # =============================================================================
  # PRIVATE VIEW — AGENTIC BYPASS
  # =============================================================================
  # Headless / programmatic access bypasses the UI password gate by sending the
  # X-Mattgpt-Bypass-Token header. The header value is compared to the
  # MATTGPT_PRIVATE_BYPASS_TOKEN env var. Both names are referenced as named
  # constants in code per CLAUDE.md (no magic strings in guards).

  Scenario: Valid bypass header auto-unlocks private view on first paint
    Given the MATTGPT_PRIVATE_BYPASS_TOKEN env var is set
    And the request carries an X-Mattgpt-Bypass-Token header matching the env var
    When the Role Match page renders
    Then session state __private_mode__ is True before any user interaction
    And the private assessment is visible without the user clicking the lock icon

  Scenario: Invalid bypass header is treated as locked
    Given the MATTGPT_PRIVATE_BYPASS_TOKEN env var is set
    And the request carries an X-Mattgpt-Bypass-Token header that does NOT match the env var
    When the Role Match page renders
    Then session state __private_mode__ is False
    And no error is surfaced to the caller

  Scenario: Bypass header silently ignored when env var is unset
    Given the MATTGPT_PRIVATE_BYPASS_TOKEN env var is unset
    And the request carries any X-Mattgpt-Bypass-Token header value
    When the Role Match page renders
    Then session state __private_mode__ is False
    And the system fails closed with no error surfaced to the caller

  # =============================================================================
  # PRIVATE VIEW — FIT ASSESSMENT
  # =============================================================================

  Scenario: Private assessment section visible when unlocked
    Given the user has unlocked the private view
    And the user has submitted a job description
    When the match results are displayed
    Then "Matt's Private Assessment" section is visible below the match results
    And the section shows fit score (High/Medium/Low)
    And the section shows recommendation (Apply/Consider/Pass)
    And the section shows gap count

  Scenario: Gap analysis shows actionable detail
    Given the private view is unlocked
    And the match results contain gaps
    When the private assessment section is displayed
    Then each gap shows the requirement text and what is missing
    And the gap explanation suggests how to address it (e.g. "prepare a narrative")

  Scenario: Recommendation is computed from required gaps only
    Given the private view is unlocked
    And the match results have 0 required gaps and 1 preferred gap
    And 70% or more strong matches
    When the private assessment section is displayed
    Then recommendation is "Apply"
    And fit score is "High"

  # Thresholds below match compute_recommendation() in services/jd_assessor.py:
  #   Apply / High:    required_gap_count == 0 AND strong_ratio >= 0.7
  #   Consider / Med:  required_gap_count <= 1 AND coverage_ratio >= 0.7
  #                    (coverage_ratio = (strong + partial) / total)
  #   Pass / Low:      otherwise (including 0-requirements edge case)

  Scenario: Two or more required gaps yields Pass / Low
    Given the private view is unlocked
    And the match results have 2 or more required gaps
    When the private assessment section is displayed
    Then recommendation is "Pass"
    And fit score is "Low"

  Scenario: One required gap with at least 70 percent coverage yields Consider / Medium
    Given the private view is unlocked
    And the match results have exactly 1 required gap
    And the strong+partial coverage ratio is 0.7 or higher
    When the private assessment section is displayed
    Then recommendation is "Consider"
    And fit score is "Medium"

  Scenario: Zero required gaps with low strong ratio but high coverage yields Consider / Medium
    Given the private view is unlocked
    And the match results have 0 required gaps
    And the strong ratio is below 0.7
    And the strong+partial coverage ratio is 0.7 or higher
    When the private assessment section is displayed
    Then recommendation is "Consider"
    And fit score is "Medium"

  Scenario: Empty extraction yields Pass / Low
    Given the private view is unlocked
    And the JD extraction returned 0 requirements
    When the private assessment section is displayed
    Then recommendation is "Pass"
    And fit score is "Low"

  Scenario: Unlocking after submission reveals the assessment without re-submit
    Given the user has submitted a job description while locked
    And the recruiter view results are visible
    When the user unlocks the private view
    Then the private assessment section appears below the recruiter view
    And no re-submission of the JD is required

  Scenario: Locking back while assessment is visible hides only the private section
    Given the user has unlocked the private view
    And the private assessment is visible alongside the recruiter view
    When the user clicks the lock icon to re-lock
    Then the private assessment section is hidden on the next rerun
    And the recruiter view (Phases 1-3) remains intact and unchanged

  # =============================================================================
  # DESKTOP ONLY
  # =============================================================================

  Scenario: Mobile shows desktop-only message
    Given the user is on a device with viewport width less than 1024px
    When the user navigates to Role Match
    Then the JD input and match results are not displayed
    And a message says "Best experienced on desktop"

  Scenario: Desktop shows full Role Match interface
    Given the user is on a device with viewport width 1024px or greater
    When the user navigates to Role Match
    Then the two-column layout is displayed (JD input left, results right)

  # =============================================================================
  # PIPELINE INTEGRATION
  # =============================================================================

  Scenario: Results come from the three-step pipeline
    Given the user has submitted a job description
    When the match results are displayed
    Then requirements were extracted using JD_EXTRACTION_PROMPT via OpenAI
    And each requirement was queried against Pinecone via pinecone_service.py
    And each requirement was assessed using build_assessment_prompt() via OpenAI
    And the recommendation was computed by compute_recommendation()

  Scenario: Pipeline handles JD with no preferred qualifications
    Given a job description with only required qualifications and no preferred section
    When the user submits the JD
    Then only required qualifications are shown in the results
    And the preferred qualifications section is not displayed

  Scenario: Pipeline handles empty Pinecone results gracefully
    Given a requirement that returns no stories from Pinecone
    When the assessment prompt is run for that requirement
    Then the requirement is assessed using grounding context only
    And the result is not an error

  # =============================================================================
  # ACTION BUTTONS — Helpful / Share / Export
  # =============================================================================
  # Visual treatment and click wiring shared with story_detail via the
  # ui/components/action_buttons.py module. The buttons live in the results
  # header bar at the top of the right column when results are present.

  Scenario: Action buttons appear only when results are present
    Given the user has not submitted a job description
    Then the Helpful, Share, and Export buttons are not visible

  Scenario: Action buttons appear after results render
    Given the user has submitted a job description and results are displayed
    Then the Helpful, Share, and Export buttons appear in the results header

  Scenario: Share copies plain-text summary to clipboard
    Given results are displayed
    When the user clicks Share
    Then a plain-text summary is copied to clipboard
    And the summary includes the role title and company
    And the summary includes required qualifications with status icons
    And the summary includes preferred qualifications with status icons
    And gap explanations appear under partial and gap items

  Scenario: Export opens a printable document
    Given results are displayed
    When the user clicks Export
    Then a print-ready window opens
    And the window contains the role title and all requirements

  Scenario: Helpful button logs feedback
    Given results are displayed
    When the user clicks Helpful
    Then log_feedback is called with rating up
    And the button shows a confirmed state
    And the button cannot be clicked again in the same session

  Scenario: Action buttons hidden on mobile
    Given the user is on a device with viewport width less than 768px
    And results are displayed
    Then the action buttons are not visible

  # Regression guard — Role Match mobile gate (broken 3x via CSS/JS changes to
  # global_styles.py + app.py). Fixed by: key="screen_size_capture" + window.innerWidth.
  # Uses the existing <1024px navigation step (375px catches real mobile, not just 1000px).
  Scenario: Role Match shows mobile gate at 375px
    Given the user is on a device with viewport width less than 1024px
    Then the page contains "Best experienced on desktop"
    And the page contains "Role Match requires a wider screen to display the two-column layout."
    And the textarea is not visible
