Feature: MATT_DNA grounding drift guards + What-Matt-is-NOT removal (MATTGPT-207)

  MATT_DNA is anti-hallucination grounding (introduced Jan 19 2026 in commit
  71c3d31 to fix a Kaiser/JPMorgan confabulation). The Sparkfly ingest on
  Aug 20 2026 exposed two drift classes:

  1. Corpus content the grounding does not name (WellFound Technology is a
     new Employer; the block terminates at Accenture). The model reconciled
     an AT&T story against the stale grounding and asserted AT&T-before-
     Accenture. Fix: add WellFound rows to Career Arc and Career Eras.

  2. A hand-maintained "What Matt is NOT" block that has gone stale against
     the corpus and now overrides evidence. Verified in production Aug 20:
     the block claimed "Not early-stage startups" and "Not hardware/embedded
     systems" while the corpus contains Sparkfly (startup) and the Liquid
     Studio IoT/robotic-bartender story. Fix: remove the block. Grounding
     rule 1 ("ONLY cite clients, projects, and metrics that appear in the
     stories below") already covers every case the block was trying to
     enumerate.

  Drift guards below enforce that Employers and specific Clients from the
  corpus are all represented in MATT_DNA going forward, so future story
  additions cannot silently orphan grounding again.

  Scenario: every Employer in the corpus appears as a literal string in MATT_DNA
    Given the current production story corpus is loaded
    When sync_portfolio_metadata is called with the production stories
    Then every distinct Employer value from the corpus appears literally in MATT_DNA

  Scenario: every non-generic Client in the corpus appears in _KNOWN_CLIENTS
    Given the current production story corpus is loaded
    When sync_portfolio_metadata is called with the production stories
    Then every non-generic Client value from the corpus appears in _KNOWN_CLIENTS

  Scenario: MATT_DNA contains no "What Matt is NOT" heading
    Given the current production story corpus is loaded
    When sync_portfolio_metadata is called with the production stories
    Then MATT_DNA contains no "What Matt is NOT" heading

  Scenario: MATT_DNA still contains the NOT-clients list
    Given the current production story corpus is loaded
    When sync_portfolio_metadata is called with the production stories
    Then MATT_DNA contains "NOT Matt's Clients (NEVER mention)"
