Feature: Nonsense filter behavior on target queries (MATTGPT-165 Cycle C)

  Verifies is_nonsense returns None (query reaches retrieval) for the two
  narrowings resolved in Cycle C, and preserves regression protection for
  the previously-blocked queries the narrowings were designed to keep out.

  Scenario: credit card portal query reaches retrieval after line 1 deletion
    Given the production nonsense_filters.jsonl is loaded
    When is_nonsense is called with "Tell me about the credit card portal work"
    Then it returns None

  Scenario: SWIFT payment rails query reaches retrieval after line 2 edit
    Given the production nonsense_filters.jsonl is loaded
    When is_nonsense is called with "What did Matt do with SWIFT payment rails"
    Then it returns None

  Scenario: Taylor Swift celebrity query is still blocked by the full-names celebrity pattern
    Given the production nonsense_filters.jsonl is loaded
    When is_nonsense is called with "Does Matt know Taylor Swift"
    Then it returns the celebrity category

  Scenario: credit card number query is still blocked by the personal_sensitive pattern
    Given the production nonsense_filters.jsonl is loaded
    When is_nonsense is called with "What is Matt's credit card number"
    Then it returns the personal_sensitive category
