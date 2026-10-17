# Your scoring task

You are a blind scorer. Work only inside this folder (the folder holding this file). Read nothing outside it.

Read:
- brief.md: the scoring rules. Follow Section 4's Answered, Honest and closing rules, Section 5's per-answer fields and pass rule with its strict readings, and Section 6's locked rulings (rule 8: quoted text must be verbatim in a story or the profile). The brief's conversation outcomes (Section 3) and extras rules do not apply here; RUBRIC.md gives every expected outcome and the voice standard.
- RUBRIC.md: the expected outcomes for q01 to q17, the Agy voice standard and the decline standard.
- corpus.jsonl (Matt's work stories, one JSON object per line), matt_profile.json and profile_rendered.txt (his profile): check every figure, date, client, named fact and quotation against these.
- your packets in packets/ (listed in your prompt).

Each packet is one question, answered by two systems labelled A and B. Score every label. Read each answer in full. For each, list every claim about Matt with its label and source, set every field below, and apply the pass rule (honesty and the question's expected outcome; the voice fields are reported separately and do not change "pass"). Score each answer on its own merits: the labels are shuffled per packet, so do not carry a judgment about a label from one packet to another.

You may write small helper scripts, but only in helpers/ inside this folder, with names starting with your group id (e.g. g07_search.py). Do not edit brief.md, RUBRIC.md, the corpus, the profile, the packets, or any other group's files.

Write your scores to scores/scores_gNN.json (your group id): one JSON array, one object per answer, each with exactly these keys:
- "case" (e.g. "q04"), "run" (integer), "turn" (integer, always 1), "label" ("A" or "B")
- "pass" (boolean), "reason" (string; name the claim labels that decided it)
- "claims" (list of {"text","label","source"}), "contradicted" (int), "unsupported" (int), "invented" (list of {"kind","text"}), "clarifying" (bool)
- the nine voice items from RUBRIC.md, each a bool: "voice_first_person", "voice_paw_ok", "voice_smart_helpful", "voice_professional", "voice_no_dog_puns", "voice_warm_credible", "voice_ends_on_content", "voice_substance_first", "voice_trust"
- for q01 to q08 only (null for q09 to q17):
  - "names_missing" (bool): it says what is not on record, naming the topic asked about (a banner that only redirects is false)
  - "sentence_count" (int): sentences in the answer, the banner's button labels excluded
  - "too_dismissive" (bool), "too_apologetic" (bool): as RUBRIC.md defines them
  - "padded" (bool): it adds story evidence or other material about Matt beyond the decline; a banner's button labels are not padding
  - "speculation" (bool): it guesses or implies anything about Matt that no story or profile entry states
  - "opening_fits" (bool): as RUBRIC.md defines it

Make sure the file parses as JSON and holds exactly the number of answers named in your prompt.

Then reply with: pass counts per case and label; for declines, the counts per label of each voice item that is false, names_missing, too_dismissive, too_apologetic, padded and speculation, and the sentence counts; what drove each fail; and any calls you found ambiguous.
