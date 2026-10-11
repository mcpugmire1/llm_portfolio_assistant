# Scoring brief (blind)

You score transcripts of an assistant ("Agy") that answers visitors' questions about Matt Pugmire's career, from a corpus of his work stories and his profile. Each packet holds one conversation run by two systems, labelled A and B. You don't know which system is which, and you must not try to find out: read only the files named in your task.

Score every assistant turn of A and of B, separately, pass or fail, against the expected outcome and rules below. Judge each answer against the expected outcome, not against the other system's answer. Read every answer in full. Check every figure, date and named fact an answer states against the corpus (corpus_6ec9aec.jsonl, one story per line) and the profile (matt_profile.json); a fact neither holds fails Honest. A seeded turn is given, not scored.

Lines marked **Protocol** are scoring rules too. Ignore any mention of "PoC" or "lever 2" in these rules except as a scoring rule: you do not know which label is which.

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



## Extras (x1 to x5): single-turn absence and adjacency questions

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
