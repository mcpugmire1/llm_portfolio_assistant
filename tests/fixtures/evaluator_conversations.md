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

## Expected Answers

"Answered" means the correct referent and materially correct facts, not matching the expected wording. Score on correct referent, materially correct facts, honest uncertainty, and contextual continuity; allow natural variation in wording. First turns are scored on Answered and Honest; Remembered context passes unless the answer imports unrelated context. A fact must be backed by a story or the profile: a figure that only the assistant's context asserts fails Honest.

1. Payments experience
- "How big was the team?": the team on the engagement just described. For JP Morgan ACCESS, a blended onshore/offshore team of 40+ across Accenture and JP Morgan. Fails if it gives a different engagement's team.
- "What went wrong?": what went wrong on that same engagement, from its story (for ACCESS, the WebSeries platform could not meet JP Morgan's needs out of the box; he owned Sev-1 production incident response). If the story records no failure, it says so. Fails if it narrates a different engagement, such as the anonymized Fortune 500 data-exposure story.

2. Education
- "Why shouldn't that worry me?": explains the missing CS degree from the profile (Master's in Information Technology, American InterContinental University, a recognized Computer Science-related discipline that exceeds a Bachelor's) plus his technical track record, stated as facts. Fails if it inflates, evaluates, or ignores the degree.

3. Leadership
- "Give me an example where that didn't work.": one story the corpus presents as a shortfall or failure under his leadership, described honestly. Fails if it reframes a success as a failure or gives no example.

4. Certifications
- "What about PMP?": no PMP, then the certifications from the profile. Fails if it pivots to PMO stories in place of the answer.
- "Are any of those current?": no, all are expired (AWS Solutions Architect Associate expired 2023, AWS Cloud Practitioner expired 2023, SAFe 4 Agilist expired, Oracle 8i exams 2002). Fails if it implies any are current.

5. Career motivation
- "Why should we hire him over someone who stayed in-house?": answers the in-house comparison directly from the corpus (what consulting breadth across clients brings), stated as facts. Fails if it disparages in-house candidates, invents claims, or gives a generic pitch that ignores the comparison.

6. Healthcare experience
- "What did he actually do there?": his role and actions in the healthcare work (AI-powered chronic disease management and responsible AI governance for patient data privacy, for a major U.S. health system). Fails if generic or about non-healthcare work.

7. Location
- "Would he relocate?": yes, open to relocation and travel (based in Atlanta, GA). Fails if it hedges, deflects, or invents conditions.

8. Failure and growth
- "What did he change afterward?": the changes from that incident's own story (IAM validation, environment verification, PII scrubbing, and risk ownership as day-one responsibilities). Fails if it presents a different engagement as a consequence of the incident; mentioning one plainly as separate is not a fail on its own.

9. Topic switch
- "What's his leadership style?": leadership style with no payments carry-over.
- "Give me an example.": an example of the leadership style just described, not payments.
- "How big was the team on that project?": the team size of the project used as the example in the previous turn (for the Cloud Innovation Center, 150+, grown from a 10-person pilot). If that story gives no size, it says so. Fails if it reports the payments team or an unrelated project.
