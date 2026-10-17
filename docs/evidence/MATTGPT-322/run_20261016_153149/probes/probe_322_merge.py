"""MATTGPT-322 merge (Oct 16, 2026; untracked probe): joins the blind scores
to the key and reports, per arm (NA, OA, NB, OB): pass by question set
(declines, facts, controls), opener_present and padded on the declines, and
per-question passes. The bare-decline count is also derived from the answer
text, independently of the scorers.
Usage: python probes/probe_322_merge.py <run_out> <scoring_dir>
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

OUT, SD = Path(sys.argv[1]), Path(sys.argv[2])
ARMS = ["NA", "OA", "NB", "OB"]
key = json.loads((OUT / "key" / "key.json").read_text())
groups = json.loads((SD / "groups.json").read_text())
scores = []
for g in groups:
    rows = json.loads((SD / "scores" / f"scores_g{g['g']:02d}.json").read_text())
    assert len(rows) == g["answers"], (g["g"], len(rows))
    scores += rows
assert len(scores) == sum(g["answers"] for g in groups)
corr_path = SD / "corrections.json"
corrections = json.loads(corr_path.read_text()) if corr_path.exists() else []
for c in corrections:
    hit = [s for s in scores if (s["case"], int(s["run"]), s["label"]) == (c["case"], c["run"], c["label"])]
    assert len(hit) == 1, c
    hit[0].update({k: v for k, v in c.items() if k in ("pass", "opener_present", "padded")})


def kind(case):
    n = int(case[1:])
    return "decline" if n <= 8 else "fact" if n <= 12 else "control"


seen = set()
tally = defaultdict(lambda: [0, 0])
per_q = defaultdict(lambda: defaultdict(lambda: [0, 0]))
for s in scores:
    name = f"{s['case']}_r{int(s['run']):02d}"
    arm = key[name][s["label"]]
    k = (name, s["label"])
    assert k not in seen, k
    seen.add(k)
    kd = kind(s["case"])
    for t in (tally[(kd, "pass", arm)], per_q[s["case"]][arm]):
        t[0] += bool(s["pass"])
        t[1] += 1
    if kd == "decline":
        for f in ("opener_present", "padded"):
            tally[(kd, f, arm)][0] += bool(s.get(f))
            tally[(kd, f, arm)][1] += 1

BARE = re.compile(r"\s*Nothing I know about Matt covers that\.?\s*")
bare = defaultdict(lambda: [0, 0])
for f in sorted(OUT.glob("rows_lane*.json")):
    for r in json.loads(f.read_text()):
        if r["kind"] == "decline":
            bare[r["arm"]][0] += bool(BARE.fullmatch(r["answer_md"] or "")) and not r.get("ui_reason")
            bare[r["arm"]][1] += 1

print(f"scored answers: {len(scores)}, no duplicates; corrections applied: {len(corrections)}\n")
for label, kd, f in [("declines pass", "decline", "pass"), ("declines opener_present", "decline", "opener_present"),
                     ("declines padded", "decline", "padded"), ("0a facts pass", "fact", "pass"),
                     ("story controls pass", "control", "pass")]:
    print(f"  {label:24}", "  ".join(f"{a}: {tally[(kd, f, a)][0]}/{tally[(kd, f, a)][1]}" for a in ARMS))
print("  bare decline (text)     ", "  ".join(f"{a}: {bare[a][0]}/{bare[a][1]}" for a in ARMS))
print("\nper question (pass of 10):")
for case in sorted(per_q):
    print(f"  {case} {kind(case):8}", "  ".join(f"{a} {per_q[case][a][0]:2}/{per_q[case][a][1]}" for a in ARMS))
