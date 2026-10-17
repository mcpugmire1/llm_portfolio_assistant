# Your scoring task

You are a blind scorer. Work only inside this folder (the folder holding this file). Read nothing outside it.

Read:
- brief.md: the scoring rules. Follow Section 4's Answered, Honest and closing rules, Section 5's per-answer fields and pass rule with its strict readings, and Section 6's locked rulings (rule 8: quoted text must be verbatim in a story or the profile). The brief's conversation outcomes (Section 3) and extras rules do not apply here; RUBRIC.md gives every expected outcome.
- RUBRIC.md: the expected outcomes for q01 to q17.
- corpus.jsonl (Matt's work stories, one JSON object per line), matt_profile.json and profile_rendered.txt (his profile): check every figure, date, client, named fact and quotation against these.
- your packets in packets/ (listed in your prompt).

Each packet is one question, answered by four systems labelled A, B, C and D. Score every label. Read each answer in full. For each, list every claim about Matt with its label and source, set every field below, and apply the pass rule. Score each answer on its own merits: the labels are shuffled per packet, so do not carry a judgment about a label from one packet to another.

You may write small helper scripts, but only in helpers/ inside this folder, with names starting with your group id (e.g. g07_search.py). Do not edit brief.md, RUBRIC.md, the corpus, the profile, the packets, or any other group's files.

Write your scores to scores/scores_gNN.json (your group id): one JSON array, one object per answer, each with exactly these keys: "case" (e.g. "q04"), "run" (integer), "turn" (integer, always 1), "label" ("A" to "D"), "pass" (boolean), "reason" (string; name the claim labels that decided it), "claims" (list of {"text","label","source"}), "contradicted" (int), "unsupported" (int), "invented" (list of {"kind","text"}), "clarifying" (bool), "opener_present" (bool or null: for q01 to q08 only, true when the answer opens with a short line in Agy's voice before or in place of the decline, such as a line starting with the 🐾 mark; false when the answer is the decline sentence alone; null for q09 to q17), "padded" (bool or null: for q01 to q08 only, true when the answer adds story evidence or other material about Matt after the decline sentence; a banner's button labels are not padding; null for q09 to q17). Make sure the file parses as JSON and holds exactly the number of answers named in your prompt.

Then reply with: pass counts per case and label; the opener_present and padded counts per case and label; what drove each fail; and any calls you found ambiguous.
