Feature: Agy Voice Consistency
  As a recruiter reading Agy's responses
  I want consistent third-person narration about Matt
  So the experience feels authentic and professional, not AI-generated

  # The answers come from the latest live acceptance run
  # (tests/fixtures/agy_voice_answers.json): router redirects and seeded
  # turns are left out. A prompt ticket's acceptance run refreshes it with
  # scripts/build_agy_voice_fixture.py.

  Background:
    Given the answers recorded by the latest live acceptance run

  # =============================================================================
  # THIRD PERSON NARRATION
  # =============================================================================

  Scenario: Agy speaks in third person about Matt
    When I read every recorded first-turn answer
    Then every answer should refer to "Matt" or "he/his"
    And no answer should contain:
      | pattern                |
      | I led                  |
      | I built                |
      | I managed              |
      | I created              |
      | I developed            |
      | I drove                |
      | I established          |
      | I scaled               |
      | I transformed          |
      | I worked               |
      | I implemented          |
      | I designed             |
      | I was responsible      |
      | my team                |
      | my approach            |
      | my experience          |

  Scenario: Synthesis mode maintains third person
    When I read every recorded synthesis answer
    Then no answer should contain:
      | pattern                |
      | I led                  |
      | I built                |
      | I managed              |
      | I created              |
      | I developed            |
      | I drove                |
      | I established          |
      | I scaled               |
      | I transformed          |
      | I worked               |
      | I implemented          |
      | I designed             |
      | I was responsible      |
      | my team                |
      | my approach            |
      | my experience          |

  Scenario: Client-scoped query maintains third person
    When I read every recorded answer that names a client
    Then every answer should refer to "Matt" or "he/his"
    And no answer should contain:
      | pattern                |
      | I led                  |
      | my team                |

  # =============================================================================
  # PAW EMOJI CONSISTENCY
  # =============================================================================

  Scenario: Exactly one paw emoji per response
    When I read every recorded answer
    Then every answer should contain exactly one paw emoji
    And the paw emoji should be in the opening line

  Scenario: Paw emoji present in all response types
    When I read every recorded answer
    Then every answer should start with a line containing the paw emoji
    And no answer should have an additional paw emoji

  # =============================================================================
  # NO META-COMMENTARY
  # =============================================================================

  Scenario: No "This demonstrates" patterns
    When I read every recorded answer
    Then no answer should contain:
      | pattern                    |
      | This demonstrates          |
      | This reflects              |
      | This illustrates           |
      | This showcases             |
      | This highlights            |
      | This story demonstrates    |
      | This example shows         |
      | This reveals Matt's        |

  Scenario: No "Matt's ability to" patterns
    When I read every recorded answer
    Then no answer should contain:
      | pattern                |
      | Matt's ability to      |
      | his ability to         |
      | demonstrates his       |
      | reflects his           |
      | showcases his          |

  Scenario: No academic summarization tone
    When I read every recorded answer
    Then no sentence should start with:
      | pattern        |
      | In essence     |
      | In summary     |
      | Essentially    |
      | Overall        |

  # =============================================================================
  # NO CORPORATE FILLER
  # =============================================================================

  Scenario: No banned corporate phrases
    When I read every recorded answer
    Then no answer should contain:
      | pattern                                     |
      | meaningful outcomes                         |
      | foster collaboration                        |
      | strategic mindset                           |
      | stakeholder alignment                       |
      | bridge the gap                              |
      | stagnant growth                             |
      | emerging market demands                     |
      | limited potential                           |
      | prioritize maintenance over innovation      |

  # =============================================================================
  # NO SELF-REFERENCE
  # =============================================================================

  Scenario: Agy does not refer to herself in third person
    When I read every recorded answer
    Then no answer should contain:
      | pattern              |
      | Agy thinks           |
      | Agy believes         |
      | Agy knows            |
      | Agy found            |
      | As Agy               |
      | Agy can              |
      | Agy's perspective    |

  Scenario: Agy does not use "we" pronouns
    When I read every recorded answer
    Then no answer should use "we" as a subject pronoun
    And no answer should contain:
      | pattern        |
      | our team       |
      | our analysis   |
