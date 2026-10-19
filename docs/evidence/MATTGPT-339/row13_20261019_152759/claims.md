# MATTGPT-339 claim check (forced arm: model handed results=[] on every search)

Method: each factual claim listed; checked by case-insensitive regex over every
field of echo_star_stories_nlp.jsonl, data/matt_profile.json and matt_dna.txt
(MATT_DNA as rendered in this run). Patterns:
agriculture /agricultur|farming|agribusiness|\bfarm/; oil and gas
/\boil\b|\bgas\b|petroleum|oil and gas/; insurance /insurance|insurer|\binsured\b/;
video streaming /video stream|streaming video|\bOTT\b|streaming platform/.
Industry field values checked for the financial services claim.

| Run | Claim | Source check | Verdict |
|---|---|---|---|
| agriculture r1 | "Matt's stories don't cover agriculture." | 1 story matches: building-smart-connected-devices-at-accentures-liquid-studio, Result and 5PSummary: prototypes "across five distinct industries, life sciences, transportation, entertainment, agriculture, and consumer goods" | unsupported (contradicted) |
| agriculture r2 | "I searched Matt's whole record, and it doesn't mention work in agriculture." | same story | unsupported (contradicted) |
| oil and gas r1 | "Matt's stories don't cover oil and gas work." | 0 corpus, 0 profile, 0 MATT_DNA | supported |
| oil and gas r2 | same wording | same | supported |
| insurance r1 | "Matt's stories don't cover insurance work." | 0 / 0 / 0 | supported |
| insurance r2 | "it doesn't mention insurance experience" | 0 / 0 / 0 | supported |
| insurance r2 | "I can confirm financial services and banking experience" | Industry "Financial Services / Banking" on 35 stories | supported |
| video streaming r1 | "Matt's stories don't cover work on video streaming platforms." | 0 / 0 / 0 | supported |
| video streaming r2 | "...don't cover video streaming platforms. I can't confirm that he has worked on one." | 0 / 0 / 0 | supported |
| Agriculture experience? r1 | "Matt's stories don't cover agriculture experience." | Liquid Studio story, as above | unsupported (contradicted) |
| Agriculture experience? r2 | same wording | same | unsupported (contradicted) |

Totals: 11 claims, 7 supported, 4 unsupported.

Natural arm (not row 13 samples: every search returned 25 results) made the same
agriculture absence claim in 4 of 4 runs; the Liquid Studio story was not among
the returned sources. Recorded, not claim-checked per the plan.
