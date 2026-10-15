Feature: Ask Agy hands a question to the conversation without flicker
  As a recruiter starting a question from the Ask Agy landing page or Home
  I want the page to move straight to my question
  So that I don't watch the old page blink, half-draw and linger

  # MATTGPT-275 step 1. Before this fix, landing's header and "Hi, I'm Agy"
  # intro (hidden while stale by the MATTGPT-018 rule) blanked as follows:
  #   Matt's production trace, Oct 12, 2026 (Chrome performance trace, 767 px,
  #     landing suggestion chip, tap to a settled page): 1 blank of about
  #     290 ms, then landing stays under the thinking indicator's scrim
  #   headless HEAD (d04396b, this feature run against it on Oct 13, 2026,
  #     both landing paths at 1280 and 767 px): 3 blanks of about 100, 20 and
  #     120 ms
  #   local Green before this fix (Chrome performance trace, Oct 12, 2026,
  #     767 px, landing suggestion chip): the same hero blanks twice (about 330 ms
  #     in all, with landing reappearing between), then for about 85 ms the
  #     conversation header and an empty question bubble sit over landing's
  #     input, its in-flow caption and the Let's Connect footer
  #
  # A recorder samples every animation frame and every DOM change from the
  # tap until the visitor's question bubble shows its text. The bar is
  # production's: at most one hero blank, no longer than 290 ms; no frame with
  # the conversation header and any element of the page the question came
  # from; no empty question bubble. "Hero blank" means landing's header or
  # intro container is on the page but hidden. Elements of the previous page
  # are landing's input, caption, chips and intro, Home's cards and Ask Agy
  # card, and the Let's Connect footer, counted when visible with height.
  # "Unstyled chips" (the MATTGPT-289 pattern, also seen in production after a
  # reboot): a visible landing chip whose container is not display: grid (a
  # plain list), or a visible hidden-receiver button (empty grey boxes). With
  # get_landing_css() applied the containers are grid and the receivers are
  # display: none. This check is a regression guard: it has no Red on HEAD
  # (0 of 6 failed against d04396b).
  #
  # One scenario per check, so a known failure in one check does not hide the
  # others. Each example is one live hand-off.

  Scenario Outline: Landing's hero blanks at most once during the hand-off
    Given the viewport for the hand-off is <width> px wide
    And the user is on the page the <path> starts from
    When the user asks from the <path> and watches the hand-off
    Then landing's hero blanks at most once, for no longer than 290 ms

    Examples:
      | path                     | width |
      | landing suggestion chip  | 1280  |
      | landing suggestion chip  | 767   |
      | typed landing question   | 1280  |
      | typed landing question   | 767   |
      | Home suggested question  | 1280  |
      | Home suggested question  | 767   |

  Scenario Outline: The conversation header never shows over the previous page's elements
    Given the viewport for the hand-off is <width> px wide
    And the user is on the page the <path> starts from
    When the user asks from the <path> and watches the hand-off
    Then the conversation header never shows over the previous page's elements

    Examples:
      | path                     | width |
      | landing suggestion chip  | 1280  |
      | landing suggestion chip  | 767   |
      | typed landing question   | 1280  |
      | typed landing question   | 767   |
      | Home suggested question  | 1280  |
      | Home suggested question  | 767   |

  Scenario Outline: The question bubble is never shown empty during the hand-off
    Given the viewport for the hand-off is <width> px wide
    And the user is on the page the <path> starts from
    When the user asks from the <path> and watches the hand-off
    Then the question bubble is never shown empty

    Examples:
      | path                     | width |
      | landing suggestion chip  | 1280  |
      | landing suggestion chip  | 767   |
      | typed landing question   | 1280  |
      | typed landing question   | 767   |
      | Home suggested question  | 1280  |
      | Home suggested question  | 767   |

  Scenario Outline: Landing's suggestion chips never show unstyled during the hand-off
    Given the viewport for the hand-off is <width> px wide
    And the user is on the page the <path> starts from
    When the user asks from the <path> and watches the hand-off
    Then landing's suggestion chips never show unstyled

    Examples:
      | path                     | width |
      | landing suggestion chip  | 1280  |
      | landing suggestion chip  | 767   |
      | typed landing question   | 1280  |
      | typed landing question   | 767   |
      | Home suggested question  | 1280  |
      | Home suggested question  | 767   |
