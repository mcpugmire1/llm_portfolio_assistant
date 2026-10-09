# Scoring correction: turn 1.3

Correction to `blind_scores.json` in this folder (committed in 4b46c38). The scores file is left as recorded; this note supersedes its 1.3 entries.

## What changes

1.3 r2-B, r3-B and r5-B were scored F for narrating "a different engagement", the Global Payments Gateway, after a first answer about ACCESS. They pass. The corpus files both stories under the same engagement:

| Story id | Client | Project |
|---|---|---|
| `building-jp-morgans-global-payments-gateway-across-12-countries\|jp-morgan-chase` | JP Morgan Chase | ACCESS Next Generation |
| `building-the-payment-engine-behind-jp-morgan-access\|jp-morgan-chase` | JP Morgan Chase | ACCESS Next Generation |

The fixture's 1.3 criterion fails "a different engagement, such as the anonymized Fortune 500 data-exposure story"; the gateway is the same engagement at the corpus's `(Client, Project)` grain.

## Corrected 1.3

| Path | Recorded | Corrected |
|---|---|---|
| lever 2 (r3-B) | 4/5 | 5/5 |
| arm (r2-B, r5-B) | 3/5 | 5/5 |
| Both | 7/10 | 10/10 |

## Verdict

Unchanged: the arm fails. Conversation 11 is 0/5 on both paths (bar 4/5). With 1.3 now equal, the arm is still below lever 2 in the same run on 4.2 (4 vs 5), 10.2 (1 vs 2) and 10.3 (3 vs 5).
