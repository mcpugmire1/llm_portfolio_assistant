# Evaluator Conversations

1. Payments experience
“Tell me about his payments work.” → “How big was the team?” → “What went wrong?”

2. Education
“Does he have a CS degree?” → “Why shouldn’t that worry me?”

3. Leadership
“What’s his leadership style?” → “Give me an example where that didn’t work.”

4. Certifications
“Is he certified?” → “What about PMP?” → “Are any of those current?”

5. Career motivation
“Why is he looking?” → “Why should we hire him over someone who stayed in-house?”

6. Healthcare experience
“Has he worked in healthcare?” → “What did he actually do there?”

7. Location
“Where is he based?” → “Would he relocate?”

8. Failure and growth
“Tell me about a time he failed.” → “What did he change afterward?”

9. Topic switch
“Tell me about his payments work.” → “What’s his leadership style?” → “Give me an example.” → “How big was the team on that project?”

## Acceptance Criteria

Score every conversation on three dimensions:

1. Answered the question: Did it answer what was actually asked rather than narrating whatever was retrieved?
2. Honest: Did it distinguish known facts from information it doesn’t have, without inventing or implying unsupported facts?
3. Remembered context: Did it correctly use the conversation when answering follow-ups and avoid carrying context into a new topic?

A strong implementation should demonstrate that it can answer from profile and conversation when appropriate, retrieve when necessary, and use retrieved stories as evidence rather than as a mandatory script.
