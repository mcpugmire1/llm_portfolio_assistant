Feature: Agy Voice Consistency
  As a recruiter reading Agy's responses
  I want consistent third-person narration about Matt
  So the experience feels authentic and professional, not AI-generated

  Background:
    Given the story index contains Matt's transformation project stories
    And Agy is configured to respond in third person

  # =============================================================================
  # THIRD PERSON NARRATION
  # =============================================================================

  Scenario: Agy speaks in third person about Matt
    When the user asks "Tell me about Matt's leadership experience"
    Then the response should refer to "Matt" or "he/his"
    And the response should not contain first-person patterns:
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
    When the user asks "What are Matt's core leadership themes?"
    Then the response should use third person throughout
    And no first-person voice from stories should leak through

  Scenario: Client-scoped query maintains third person
    When the user asks "Tell me about Matt's work at JP Morgan"
    Then the response should refer to Matt in third person
    And the response should not contain "I led" or "my team"

  # =============================================================================
  # PAW EMOJI CONSISTENCY
  # =============================================================================

  Scenario: Exactly one paw emoji per response
    When the user asks any valid question
    Then the response should contain exactly one paw emoji
    And the paw emoji should be in the opening line

  Scenario: Paw emoji present in all response types
    When the user asks "Tell me about Matt's background"
    Then the response should start with a line containing the paw emoji
    And there should be no additional paw emojis in the response

  # =============================================================================
  # NO META-COMMENTARY
  # =============================================================================

  Scenario: No "This demonstrates" patterns
    When the user asks about Matt's experience
    Then the response should not contain meta-commentary patterns:
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
    When the user asks "How does Matt lead teams?"
    Then the response should not contain:
      | pattern                |
      | Matt's ability to      |
      | his ability to         |
      | demonstrates his       |
      | reflects his           |
      | showcases his          |

  Scenario: No academic summarization tone
    When the user asks about Matt's work
    Then the response should not contain:
      | pattern        |
      | In essence     |
      | In summary     |
      | Essentially    |
      | Overall        |

  # =============================================================================
  # NO CORPORATE FILLER
  # =============================================================================

  Scenario: No banned corporate phrases
    When the user asks any question about Matt
    Then the response should not contain banned phrases:
      | phrase                                      |
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
    When the user asks any question
    Then the response should not contain:
      | pattern              |
      | Agy thinks           |
      | Agy believes         |
      | Agy knows            |
      | Agy found            |
      | As Agy               |
      | Agy can              |
      | Agy's perspective    |

  Scenario: Agy does not use "we" pronouns
    When the user asks about Matt's experience
    Then the response should not use "we" as a subject pronoun
    And the response should not contain "our team" or "our analysis"
