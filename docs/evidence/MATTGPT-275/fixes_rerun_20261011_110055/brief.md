# Scoring brief (blind)

You score transcripts of an assistant ("Agy") that answers visitors' questions about Matt Pugmire's career, from a corpus of his work stories and his profile. Each packet holds one conversation run by two systems, labelled A and B. You don't know which system is which, and you must not try to find out: read only the files named in your task.

Score every assistant turn of A and of B, separately, pass or fail, against the expected outcome and rules below. Judge each answer against the expected outcome, not against the other system's answer. Read every answer in full. Check every figure, date and named fact an answer states against the corpus (corpus_6ec9aec.jsonl, one story per line) and the profile (matt_profile.json); a fact neither holds fails Honest. A seeded turn is given, not scored.

Lines marked **Protocol** are scoring rules too. Ignore any mention of "PoC" or "lever 2" in these rules except as a scoring rule: you do not know which label is which.

## 3. Cases and expected outcomes

Fixture wording where the fixture has the case; design doc Section 5 wording otherwise. Every turn is also subject to the rules in Section 4, and a turn with no written outcome is scored on those alone.

### Fixture conversations (all 18, D8)

Each conversation's turns and expected answers are quoted verbatim from the fixture at `609f903`. Conversations 12 to 18 are the design doc's cases 3, 4, 7, 8, 9, 10 and 16. Turns the fixture gives no expected answer for are scored on the fixture's first-turn rule (Section 4). Lines marked **Protocol** are rules this protocol adds; they are not in the fixture.

**1. Payments experience.** “Tell me about his payments work.” → “How big was the team?” → “What went wrong?”
- "How big was the team?": the team on the engagement just described. For JP Morgan ACCESS, a blended onshore/offshore team of 40+ across Accenture and JP Morgan. Fails if it gives a different engagement's team.
- "What went wrong?": what went wrong on that same engagement, from its story (for ACCESS, the WebSeries platform could not meet JP Morgan's needs out of the box; he owned Sev-1 production incident response). If the story records no failure, it says so. Fails if it narrates a different engagement, such as the anonymized Fortune 500 data-exposure story.
- **Protocol:** When the first turn discussed several engagements, a clarifying question naming them passes on both follow-up turns (D4).

**2. Education.** “Does he have a CS degree?” → “Why shouldn’t that worry me?”
- "Why shouldn't that worry me?": explains the missing CS degree from the profile (Master's in Information Technology, American InterContinental University, a recognized Computer Science-related discipline that exceeds a Bachelor's) plus his technical track record, stated as facts. Fails if it inflates, evaluates, or ignores the degree.

**3. Leadership.** “What’s his leadership style?” → “Give me an example where that didn’t work.”
- "Give me an example where that didn't work.": one story the corpus presents as a shortfall or failure under his leadership, described honestly. Fails if it reframes a success as a failure or gives no example.

**4. Certifications.** “Is he certified?” → “What about PMP?” → “Are any of those current?”
- "What about PMP?": no PMP, then the certifications from the profile. Fails if it pivots to PMO stories in place of the answer.
- "Are any of those current?": no, all are expired (AWS Solutions Architect Associate expired 2023, AWS Cloud Practitioner expired 2023, SAFe 4 Agilist expired, Oracle 8i exams 2002). Fails if it implies any are current.

**5. Career motivation.** “Why is he looking?” → “Why should we hire him over someone who stayed in-house?”
- "Why should we hire him over someone who stayed in-house?": answers the in-house comparison directly from the corpus (what consulting breadth across clients brings), stated as facts. Fails if it disparages in-house candidates, invents claims, or gives a generic pitch that ignores the comparison.

**6. Healthcare experience.** “Has he worked in healthcare?” → “What did he actually do there?”
- "What did he actually do there?": his role and actions in the healthcare work (AI-powered chronic disease management and responsible AI governance for patient data privacy, for a major U.S. health system). Fails if generic or about non-healthcare work.

**7. Location.** “Where is he based?” → “Would he relocate?”
- "Would he relocate?": yes, open to relocation and travel (based in Atlanta, GA). Fails if it hedges, deflects, or invents conditions.
- **Protocol:** "Would he relocate?" is also an over-asking control (design doc case 6): any clarifying question fails.

**8. Failure and growth.** “Tell me about a time he failed.” → “What did he change afterward?”
- "What did he change afterward?": the changes from that incident's own story (IAM validation, environment verification, PII scrubbing, and risk ownership as day-one responsibilities). Fails if it presents a different engagement as a consequence of the incident; mentioning one plainly as separate is not a fail on its own.

**9. Topic switch.** “Tell me about his payments work.” → “What’s his leadership style?” → “Give me an example.” → “How big was the team on that project?”
- "What's his leadership style?": leadership style with no payments carry-over.
- "Give me an example.": an example of the leadership style just described, not payments.
- "How big was the team on that project?": the team size of the project used as the example in the previous turn (for the Cloud Innovation Center, 150+, grown from a 10-person pilot). If that story gives no size, it says so. Fails if it reports the payments team or an unrelated project.

**10. Accepting an offer.** “Tell me about his Norfolk Southern work.” → “Sure, the deep dive on that one.” → “How long did that take?”
- "Sure, the deep dive on that one.": more depth on the same Norfolk Southern engagement from its story (his role, the approach, the outcomes), not a repeat of the first answer and not a different engagement. If the first answer ended with an offer, this delivers what was offered, for that story.
- "How long did that take?": the duration of the work the second turn described, from that story's dates, stated approximately, or a clarifying question if the second turn covered stories with different ranges. Norfolk Southern's engagement runs 2019-11 to 2023-09; the quality-crisis story runs 2020-01 to 2020-12. Fails if it conflates the two timelines, says the duration is not on record, gives the CIC Academy's six months as the whole, gives another project's timeline, or invents precision.
- **Protocol:** The first turn is also subject to the closing rules (Section 4).

**11. Ambiguous follow-up after a topic change.** “How did Matt scale engineering teams from 4 to 150+ people?” → “Tell me about his payments work” → “how big was his teams”
- "how big was his teams": the teams from the previous answer: JP Morgan ACCESS (40+) and RBC (its size if the story records one; if not, it says so), or a clarifying question asking which. Fails if it answers about the Cloud Innovation Center or another engagement not in the previous answer.
- **Protocol:** "Tell me about his payments work" sets a new topic: it fails Remembered context if it carries the first turn's scaling topic into the payments answer.
- **Protocol:** "how big was his teams" is scored against the engagements that run's second answer actually discussed, not the fixture's fixed JP Morgan ACCESS and RBC, and every fact is checked against the corpus (D5). With that substitution the fixture's pass and fail apply: their team sizes from their stories (or a statement that a story records none), or a clarifying question asking which; fails on the Cloud Innovation Center or any engagement the second answer didn't discuss.

**12. Comparing two engagements.** (design doc case 3) “Compare his Fiserv and JP Morgan ACCESS work.” → “Which was bigger?”
- "Compare his Fiserv and JP Morgan ACCESS work.": both engagements from their stories. Fails if it leaves out either engagement.
- "Which was bigger?": asks bigger by what (team, budget, reach), or names the dimension and compares both engagements accurately on it. The stories hold: Fiserv, a 45-person team and an $8.5M program; ACCESS, a blended team of 40+ and 135,000+ clients. Fails if it picks one without naming the dimension, compares on a dimension inaccurately, or leaves out one engagement.

**13. Unambiguous follow-up.** (design doc case 4) “Tell me about his Fiserv work.” → “How big was the team?”
- "How big was the team?": the Fiserv team size from its story (45). Fails if it asks a clarifying question or gives another figure.
- **Protocol:** An over-asking control: any clarifying question fails.

**14. Evaluating for a role.** (design doc case 7) “I’m hiring a VP of Platform Engineering. Would Matt be a fit?”
- "I'm hiring a VP of Platform Engineering. Would Matt be a fit?": the facts relevant to the role's scope from the stories (organization size, platforms, delivery), with no level label ("VP-level", "Director-level", "Senior Director"), no vouching ("a strong fit"), and no refusal because of the VP title. It closes with an offer to run Role Match against the job description. Fails if it asserts or denies a level, evaluates fit itself, or has no Role Match close.
- **Protocol:** A required closing (D9). In the PoC this is the engage close with Role Match.

**15. Getting in touch.** (design doc case 8) “How do I get in touch with Matt?”
- "How do I get in touch with Matt?": a close carrying Contact and LinkedIn links that work in the conversation view. Fails if either link is missing or invented.
- **Protocol:** A required closing (D9). The links working in the conversation view needs a browser check, which this probe can't do: the links are scored on being present and correct, and the view is reported as not tested.

**16. Résumé.** (design doc case 9) “Can I see his résumé?”
- "Can I see his résumé?": points to About Matt (his profile) and LinkedIn. Fails if it invents a file or a link.
- **Protocol:** A required closing (D9).

**17. Accepting a seeded offer.** (design doc case 10) (seeded answer) → “Sure.”

The first assistant turn is seeded with this answer, verbatim, so every run starts from the same offer:

> 🐾 Found it! Matt was brought in roughly seven months into **Fiserv**'s 14-month, **$8.5M** white-label card portal program, the shared platform behind branded credit card sites for **2M+** cardholders across **15** financial institutions. The **45-person** globally dispersed team had missed multiple consecutive deadlines, and client stakeholders were threatening contract cancellation. He recovered a Q4 release that was **3 weeks** behind, avoiding **$500K** in penalties, and the program was delivered **3%** under budget with zero critical defects at launch.
>
> Want to hear how he moved that team from 6-month waterfall releases to 2-week sprints?

- "Sure.": delivers the offered thread, how he moved the Fiserv team from 6-month waterfall releases to 2-week sprints, from its story. Fails if it gives a different thread, a different engagement, or a repeat of the seeded answer.
- **Protocol:** A required closing (D9). Both arms get the same seeded text; the PoC also gets the seed's record entry and open offer, which lever 2 has no place for.

**18. Earlier topic competing with the latest.** (design doc case 16) “Tell me about his Norfolk Southern work.” → “Tell me about his RBC work.” → “How long did that take?”
- "Tell me about his RBC work.": a new topic, answered from the RBC stories with no Norfolk Southern carry-over.
- "How long did that take?": RBC's duration from its dates (June 2012 to June 2013, about a year), or a clarifying question between Norfolk Southern and RBC. Fails if it says the duration is not on record, gives Norfolk Southern's six months (the CIC Academy course) or any other Norfolk Southern figure (2019-11 to 2023-09; 2020-01 to 2020-12), or invents precision (days, weeks, an exact month count, or dates the corpus doesn't hold).
- **Protocol:** Scored against RBC's dates (D7). Lever 2 has no dates in context, so it can pass only by clarifying.

**Not in this set:** design doc cases 1, 2, 5, 6 and 11 to 15 (5 and 6 are covered as fixture conversations 1 and 7).


## 4. Scoring

**Rubric, both arms, per turn:** pass or fail against Section 3's expected outcome, applying the fixture's scoring rule, quoted verbatim:

> "Answered" means the correct referent and materially correct facts, not matching the expected wording. Score on correct referent, materially correct facts, honest uncertainty, and contextual continuity; allow natural variation in wording. First turns are scored on Answered and Honest; Remembered context passes unless the answer imports unrelated context. A fact must be backed by a story or the profile: a figure that only the assistant's context asserts fails Honest.

**Protocol:** a turn that sets a new topic (conversation 11's second turn, conversation 18's second turn) is scored like a first turn, plus a Remembered context fail if it carries the earlier topic in.

**Protocol: every turn also fails on any of these:**
- **Remembered context:** it carries the previous topic into a new one, or answers a follow-up about the wrong engagement.
- **Closing (D9):** an inappropriate or unsupported closing, whether rendered by the closing step or written into the answer text. The same rule applies to both arms.
  - Inappropriate: an engage close (Role Match, About Matt, contact, LinkedIn) without an evaluating signal or a contact or résumé request in the visitor's own words; or an offer unrelated to what the visitor asked.
  - Unsupported: an offer the stories can't deliver, or one asserting a fact the stories don't hold.
  - A turn with no closing never fails on the closing, except where Section 3 requires one (conversations 14 to 17).

**Required closings (D9):** scored in conversations 14, 15, 16 and 17 as written in Section 3. Lever 2 has no closing step, so it can pass these only if its answer text happens to carry the close. A fail there is reported as by construction, not as a regression.

## Extras (x1, x2, x3, x5): single-turn absence and adjacency questions

Each packet holds one visitor question, answered by A and by B. Score each answer pass or fail, with the same corpus and profile, on these rules instead of Section 3 (Section 4's closing rules still apply):

1. **Per claim:** label every claim the answer makes about Matt supported (a story or the profile holds it, or one of the stated facts below), contradicted (a story field or a stated fact says otherwise, e.g. a story's `Industry`), or unsupported (no source either way). Any contradicted or unsupported claim about Matt fails the answer. Wording that frames an adjacent story as the thing asked about counts as a claim (for example, calling mortgage work "real estate", or a payments portal a "trading platform").
2. **Absence:** when no story or profile entry covers what was asked, the answer says it is not on record ("not on record", "not in Matt's stories", or equivalent). A flat "Matt has not worked with X" fails, even when nothing in the corpus contradicts it.
3. **Trading (x3) passes only if** it makes no trading-platform claim and names Cendian's webMethods B2B Trading Networks work. Naming JP Morgan Asset Management is not required.

**Stated facts (Matt's; treat as supported or contradicting as written):**
- JP Morgan ACCESS is a treasury services and cash management platform: not capital markets, not a trading platform. Calling it either is contradicted.
- RBC (Day2Day) is corporate banking: not capital markets, not trading.
- The closest capital-markets-adjacent work is JP Morgan Asset Management (Global Funds), a Salesforce sales-opportunity CRM.
- Capital-markets and trading-platform questions get "not on record". Cendian's webMethods B2B Trading Networks is B2B document exchange (EDI), not financial trading.
- There is no SAP story; for SAP the correct answer is "not on record".

Save each score with the claim labels in the reason (for example: "contradicted: 'real estate sector'; supported: Cendant underwriting facts").
