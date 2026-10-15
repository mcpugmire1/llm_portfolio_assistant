# Your scoring task

You are a blind scorer. Work only inside this folder (the folder holding this file). Read nothing outside it.

Read:
- brief.md: the scoring rules. Follow them exactly, including Section 4's protocol rules, the extras rules, Section 5's per-answer fields and pass rule with its strict readings, and Section 6's locked rulings (rule 8: quoted text must be verbatim in a story or the profile).
- corpus_6ec9aec.jsonl (Matt's work stories, one JSON object per line), matt_profile.json and profile_rendered.txt (his profile), and matt_dna_ground_truth.txt (under the brief's Section 7 exception): check every figure, date, client, named fact and quotation against these.
- your packets in packets/ (listed in your prompt).

Each packet is one extra question answered by one system, labelled A. Score its one turn. Read each answer in full. For each, list every claim about Matt with its label and source, set every Section 5 field, and apply the pass rule. Score each answer on its own merits.

You may write small helper scripts, but only in helpers/ inside this folder, with names starting with your group id (e.g. g07_search.py). Do not edit brief.md, the corpus, the profile, the packets, or any other group's files.

Write your scores to scores/scores_gNN.json (your group id): one JSON array, one object per answer, each with exactly these keys: "case" (e.g. "c01" or "x3"), "run" (integer), "turn" (integer), "label" ("A"), "pass" (boolean), "reason" (string; name the claim labels that decided it), "claims" (list of {"text","label","source"}), "contradicted" (int), "unsupported" (int), "invented" (list of {"kind","text"}), "carry_over" (bool or null), "clarifying" (bool), "acknowledges_missing" (bool or null), "useful_direct" (bool or null). Make sure the file parses as JSON and holds exactly the number of answers named in your prompt.

Then reply with: pass counts per case, turn and label; what drove each fail; and any calls you found ambiguous.
