Feature: Nonsense filter loader guards (MATTGPT-165 loader hardening)

  Scenario: loader raises on duplicate (category, pattern) pair
    Given a nonsense filters file containing two rules with the same category and pattern
    When _load_nonsense_rules is called
    Then it raises ValueError naming the offending line number

  Scenario: loader raises on a non-dict rule
    Given a nonsense filters file containing a bare JSON string as a rule line
    When _load_nonsense_rules is called
    Then it raises ValueError identifying the line as not a rule dict

  Scenario: loader raises on a dict missing required fields
    Given a nonsense filters file containing a dict with only a category field
    When _load_nonsense_rules is called
    Then it raises ValueError identifying the missing pattern field

  Scenario: loader raises on a dict with an uncompilable regex
    Given a nonsense filters file containing a rule with an invalid regex pattern
    When _load_nonsense_rules is called
    Then it raises ValueError identifying the pattern as invalid

  Scenario: preload_nonsense_rules is invoked unconditionally at app.py module top level
    Given the app.py source file at project root
    When its AST is inspected for preload_nonsense_rules call sites
    Then at least one call appears as a module top-level statement not nested in any function, class, if, or try block
