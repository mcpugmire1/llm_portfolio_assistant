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

10. Accepting an offer
“Tell me about his Norfolk Southern work.” → “Sure, the deep dive on that one.” → “How long did that take?”

11. Ambiguous follow-up after a topic change
“How did Matt scale engineering teams from 4 to 150+ people?” → “Tell me about his payments work” → “how big was his teams”

12. Comparing two engagements
“Compare his Fiserv and JP Morgan ACCESS work.” → “Which was bigger?”

13. Unambiguous follow-up
“Tell me about his Fiserv work.” → “How big was the team?”

14. Evaluating for a role
“I’m hiring a VP of Platform Engineering. Would Matt be a fit?”

15. Getting in touch
“How do I get in touch with Matt?”

16. Résumé
“Can I see his résumé?”

17. Accepting a seeded offer
(seeded answer) → “Sure.”

The first assistant turn is seeded with this answer, verbatim, so every run starts from the same offer:

> 🐾 Found it! Matt was brought in roughly seven months into **Fiserv**'s 14-month, **$8.5M** white-label card portal program, the shared platform behind branded credit card sites for **2M+** cardholders across **15** financial institutions. The **45-person** globally dispersed team had missed multiple consecutive deadlines, and client stakeholders were threatening contract cancellation. He recovered a Q4 release that was **3 weeks** behind, avoiding **$500K** in penalties, and the program was delivered **3%** under budget with zero critical defects at launch.
>
> Want to hear how he moved that team from 6-month waterfall releases to 2-week sprints?

18. Earlier topic competing with the latest
“Tell me about his Norfolk Southern work.” → “Tell me about his RBC work.” → “How long did that take?”

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

10. Accepting an offer
- "Sure, the deep dive on that one.": more depth on the same Norfolk Southern engagement from its story (his role, the approach, the outcomes), not a repeat of the first answer and not a different engagement. If the first answer ended with an offer, this delivers what was offered, for that story.
- "How long did that take?": the duration of the work the second turn described, from that story's dates, stated approximately, or a clarifying question if the second turn covered stories with different ranges. Norfolk Southern's engagement runs 2019-11 to 2023-09; the quality-crisis story runs 2020-01 to 2020-12. Fails if it conflates the two timelines, says the duration is not on record, gives the CIC Academy's six months as the whole, gives another project's timeline, or invents precision.

11. Ambiguous follow-up after a topic change
- "how big was his teams": the teams from the previous answer: JP Morgan ACCESS (40+) and RBC (its size if the story records one; if not, it says so), or a clarifying question asking which. Fails if it answers about the Cloud Innovation Center or another engagement not in the previous answer.

12. Comparing two engagements
- "Compare his Fiserv and JP Morgan ACCESS work.": both engagements from their stories. Fails if it leaves out either engagement.
- "Which was bigger?": asks bigger by what (team, budget, reach), or names the dimension and compares both engagements accurately on it. The stories hold: Fiserv, a 45-person team and an $8.5M program; ACCESS, a blended team of 40+ and 135,000+ clients. Fails if it picks one without naming the dimension, compares on a dimension inaccurately, or leaves out one engagement.

13. Unambiguous follow-up
- "How big was the team?": the Fiserv team size from its story (45). Fails if it asks a clarifying question or gives another figure.

14. Evaluating for a role
- "I'm hiring a VP of Platform Engineering. Would Matt be a fit?": the facts relevant to the role's scope from the stories (organization size, platforms, delivery), with no level label ("VP-level", "Director-level", "Senior Director"), no vouching ("a strong fit"), and no refusal because of the VP title. It closes with an offer to run Role Match against the job description. Fails if it asserts or denies a level, evaluates fit itself, or has no Role Match close.

15. Getting in touch
- "How do I get in touch with Matt?": a close carrying Contact and LinkedIn links that work in the conversation view. Fails if either link is missing or invented.

16. Résumé
- "Can I see his résumé?": points to About Matt (his profile) and LinkedIn. Fails if it invents a file or a link.

17. Accepting a seeded offer
- "Sure.": delivers the offered thread, how he moved the Fiserv team from 6-month waterfall releases to 2-week sprints, from its story. Fails if it gives a different thread, a different engagement, or a repeat of the seeded answer.

18. Earlier topic competing with the latest
- "Tell me about his RBC work.": a new topic, answered from the RBC stories with no Norfolk Southern carry-over.
- "How long did that take?": RBC's duration from its dates (June 2012 to June 2013, about a year), or a clarifying question between Norfolk Southern and RBC. Fails if it says the duration is not on record, gives Norfolk Southern's six months (the CIC Academy course) or any other Norfolk Southern figure (2019-11 to 2023-09; 2020-01 to 2020-12), or invents precision (days, weeks, an exact month count, or dates the corpus doesn't hold).
