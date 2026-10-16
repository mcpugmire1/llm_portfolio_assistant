"""MATTGPT-236 merge (Oct 16, 2026; untracked probe): joins the blind scores
to the key and reports pass rates per arm.

Splits:
  - unchanged turns (the A/A noise floor): every live turn step 0 shows the
    router does not redirect and does not pick synthesis for;
  - changed turns: the 4 gate turns the router picks synthesis for, and the
    router-set questions it redirects or picks synthesis for;
  - the bare-sentence rate per arm on r01 to r06, from the scorers' field
    and, independently, from the answer text in the gate rows.
Usage: python probes/probe_236_merge.py <gate_out> <scoring_dir> <step0_rows.json>
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

OUT, SD, STEP0 = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
key = json.loads((OUT / "key" / "key.json").read_text())
groups = json.loads((SD / "groups.json").read_text())
want = sum(g["answers"] for g in groups)
scores = []
for g in groups:
    f = SD / "scores" / f"scores_g{g['g']:02d}.json"
    rows = json.loads(f.read_text())
    assert len(rows) == g["answers"], (f.name, len(rows), g["answers"])
    scores += rows
assert len(scores) == want, (len(scores), want)
corr_path = SD / "corrections.json"
corrections = json.loads(corr_path.read_text()) if corr_path.exists() else []
for c in corrections:
    hit = [s for s in scores if (s["case"], int(s["run"]), int(s["turn"]), s["label"]) == (c["case"], c["run"], c["turn"], c["label"])]
    assert len(hit) == 1, c
    hit[0]["pass"] = c["pass"]

case_of = {}
for name, labels in key.items():
    case, run = name.split("_r")
    case_of[name] = (case, int(run), labels)

step0 = json.loads(STEP0.read_text())
q_case = {"r": {}, "gate": {}}
i = 0
for r in step0:
    if r["set"] == "router":
        i += 1
        q_case["r"][f"r{i:02d}"] = r
    else:
        q_case["gate"][(r["case"], r["turn"])] = r


def changed(case, turn):
    r = q_case["r"].get(case) if case.startswith("r") else q_case["gate"].get((case, turn))
    return bool(r and (r["redirect"] or r["synthesis"]) and not r["nonsense"])


by = defaultdict(lambda: [0, 0])
per_turn = defaultdict(lambda: defaultdict(lambda: [0, 0]))
bare_scorer = defaultdict(lambda: [0, 0])
seen = set()
for s in scores:
    name = f"{s['case']}_r{int(s['run']):02d}"
    case, run, labels = case_of[name]
    arm = labels[s["label"]]
    k = (name, int(s["turn"]), s["label"])
    assert k not in seen, k
    seen.add(k)
    split = "changed" if changed(case, int(s["turn"])) else "unchanged"
    for b in (by[(split, arm)], by[("all", arm)], per_turn[(case, int(s["turn"]))][arm]):
        b[0] += bool(s["pass"])
        b[1] += 1
    if re.fullmatch(r"r0[1-6]", case):
        bare_scorer[arm][0] += bool(s.get("bare_sentence"))
        bare_scorer[arm][1] += 1

BARE = re.compile(r"\s*Nothing I know about Matt covers that\.?\s*")
bare_text = defaultdict(lambda: [0, 0])
for f in sorted(OUT.glob("rows_lane*.json")):
    for r in json.loads(f.read_text()):
        if re.fullmatch(r"r0[1-6]", r["case"]) and not r.get("seeded"):
            bare_text[r["arm"]][0] += bool(BARE.fullmatch(r.get("answer_md") or "")) and not r.get("ui_reason")
            bare_text[r["arm"]][1] += 1

print(f"scored answers: {len(scores)} (all {want} present, no duplicates); corrections applied: {len(corrections)}\n")
print("pass rate by split and arm:")
for split in ("all", "unchanged", "changed"):
    print(f"  {split:10}", "  ".join(f"{a}: {by[(split, a)][0]}/{by[(split, a)][1]}" for a in "ABC"))
print("\nbare sentence on r01 to r06 (scorer field | from the answer text):")
for a in "ABC":
    print(f"  {a}: {bare_scorer[a][0]}/{bare_scorer[a][1]} | {bare_text[a][0]}/{bare_text[a][1]}")
print("\nper turn (A, B, C pass out of 10), * = router-changed:")
for (case, turn), arms in sorted(per_turn.items()):
    mark = "*" if changed(case, turn) else " "
    cells = "  ".join(f"{a} {arms[a][0]:2}/{arms[a][1]}" for a in "ABC")
    flag = "" if len({arms[a][0] for a in "ABC"}) == 1 else "   differs"
    print(f" {mark} {case} t{turn}: {cells}{flag}")
