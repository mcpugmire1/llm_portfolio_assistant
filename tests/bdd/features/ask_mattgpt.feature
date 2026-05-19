Feature: Ask MattGPT — Nonsense rejection banner + contextual chip sets
  As a recruiter who submits a query that can't be answered
  I want the rejection banner to explain the reason and offer relevant follow-ups
  So that a dead-end query becomes a productive redirect into Matt's portfolio

  # See MATTGPT-071 in BACKLOG.md for the full design rationale. Four rejection
  # branches, each with a distinct banner and chip set:
  #   rule:*         → banner + RULE_CHIPS (capability verbs)
  #   personal       → banner + PERSONAL_CHIPS (character questions)
  #   out_of_scope   → banner + OUT_OF_SCOPE_CHIPS (named anchors)
  #   low_confidence → banner + rephrase prompt, NO chips
  #
  # Chip prompts were empirically validated against production on May 19, 2026.
  # See MATTGPT-077 for the phrasing-sensitivity findings that informed the
  # locked RULE_CHIPS prompts ("Modernize legacy systems" replaced
  # "Modernize monoliths into microservices" because the latter triggered
  # MattGPT/Strangler Fig self-referential responses).
  #
  # Chip label literals live as module-level constants in utils/ui_helpers.py
  # (RULE_CHIPS, PERSONAL_CHIPS, OUT_OF_SCOPE_CHIPS). BDD step definitions
  # read those constants — DO NOT inline chip text in this file. This keeps
  # chip-copy edits from breaking the spec.
  #
  # Step definitions pending — committed here as design contract first per
  # CLAUDE.md Testing Protocol (BDD scenarios committed before implementation).

  Background:
    Given the user navigates to Ask MattGPT

  # ---------------------------------------------------------------------------
  # BRANCH 1: rule:* (nonsense filter pattern matched)
  # ---------------------------------------------------------------------------

  Scenario: rule:* rejection shows banner and the capability chip set
    When the user submits "Tell me a joke about Matt's career"
    Then the rule:* rejection banner should be displayed
    And all RULE_CHIPS should be visible

  Scenario: Clicking a rule:* chip injects its prompt
    Given the rule:* rejection banner is showing
    When the user clicks the first rule:* chip
    Then that chip's prompt should appear as the next user message
    And a response should be generated

  # ---------------------------------------------------------------------------
  # BRANCH 2: personal (semantic router personal intent)
  # ---------------------------------------------------------------------------

  Scenario: personal rejection shows banner and the character chip set
    When the user submits "Is Matt married?"
    Then the personal rejection banner should be displayed
    And all PERSONAL_CHIPS should be visible

  Scenario: Clicking a personal chip injects its prompt
    Given the personal rejection banner is showing
    When the user clicks the first personal chip
    Then that chip's prompt should appear as the next user message

  # ---------------------------------------------------------------------------
  # BRANCH 3: out_of_scope (semantic router out_of_scope intent)
  # ---------------------------------------------------------------------------

  Scenario: out_of_scope rejection shows banner and the named-anchor chip set
    When the user submits "Tell me about Matt's retail experience"
    Then the out_of_scope rejection banner should be displayed
    And all OUT_OF_SCOPE_CHIPS should be visible

  Scenario: Clicking an out_of_scope chip injects its prompt
    Given the out_of_scope rejection banner is showing
    When the user clicks the first out_of_scope chip
    Then that chip's prompt should appear as the next user message

  # ---------------------------------------------------------------------------
  # BRANCH 4: low_confidence (Pinecone confidence below threshold)
  # ---------------------------------------------------------------------------
  # Step definition for the trigger phrase mocks the Pinecone score below
  # CONFIDENCE_LOW. Mock approach chosen over a known-low-confidence query
  # because (a) corpus changes would break a stable trigger query and
  # (b) production-side debug flags would leak test infra into prod code.

  Scenario: low_confidence rejection shows rephrase prompt and NO chips
    When the user submits a query that scores below the confidence threshold
    Then the low_confidence rejection banner should be displayed
    And zero chips should be visible
    And a rephrase prompt should be displayed

  # ---------------------------------------------------------------------------
  # STATE LIFECYCLE
  # ---------------------------------------------------------------------------

  Scenario: Chip click clears the rejection banner
    Given the rule:* rejection banner is showing
    When the user clicks the first rule:* chip
    And the response has been generated
    Then the rule:* rejection banner should NOT be visible
    And no chips should be visible

  Scenario: Sequential rejections swap chip sets per branch
    When the user submits "Tell me a joke about Matt's career"
    Then the rule:* rejection banner should be displayed
    And all RULE_CHIPS should be visible
    When the user submits "Is Matt married?"
    Then the personal rejection banner should be displayed
    And all PERSONAL_CHIPS should be visible
    And no RULE_CHIPS should be visible

  # ---------------------------------------------------------------------------
  # CONTEXT GUARD
  # ---------------------------------------------------------------------------
  # Chips render only when context == "ask". Regression guard against the
  # chip-rendering logic leaking into Explore Stories or other surfaces.

  Scenario: Explore Stories suppresses rejection chips entirely
    Given the user navigates to Explore Stories
    When the user types "Tell me a joke about Matt's career" in the search box
    And the user presses Enter
    Then the rejection banner should be displayed
    And zero chips should be visible
