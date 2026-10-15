"""Tally the control isolation run: passes per (case, turn, arm) out of 10,
contradicted and unsupported counts, and every fail's reason."""
import json, sys
from collections import defaultdict
from pathlib import Path
OUT, SD = Path(sys.argv[1]), Path(sys.argv[2])
key = json.loads((OUT / "key" / "key.json").read_text())
scores = [s for f in sorted((SD / "scores").glob("scores_g*.json")) for s in json.loads(f.read_text())]
seen = set()
t = defaultdict(lambda: [0, 0, 0, 0])  # pass, n, contradicted>0, unsupported>0
fails = []
for s in scores:
    name = f"{s['case']}_r{int(s['run']):02d}"
    arm = key[name][s["label"]]
    k = (s["case"], int(s["run"]), int(s["turn"]), arm)
    assert k not in seen, k
    seen.add(k)
    c = t[(s["case"], int(s["turn"]), arm)]
    c[0] += bool(s["pass"]); c[1] += 1; c[2] += s["contradicted"] > 0; c[3] += s["unsupported"] > 0
    if not s["pass"]:
        fails.append((s["case"], int(s["turn"]), arm, int(s["run"]), s["reason"]))
print("scores", len(scores), "unique", len(seen))
arms = ["cur", "A", "B", "C"]
turns = sorted({(c, tn) for c, tn, _ in t})
print("turn      " + "  ".join(f"{a:>10}" for a in arms))
for c, tn in turns:
    print(f"{c} t{tn}    " + "  ".join(f"{t[(c, tn, a)][0]:>2}/{t[(c, tn, a)][1]} ({t[(c, tn, a)][2]},{t[(c, tn, a)][3]})" for a in arms))
for a in arms:
    p = sum(v[0] for (c, tn, aa), v in t.items() if aa == a); n = sum(v[1] for (c, tn, aa), v in t.items() if aa == a)
    print(f"total {a}: {p}/{n}")
print("\nfails:")
for f in sorted(fails):
    print(f"{f[0]} t{f[1]} {f[2]:>3} r{f[3]:02d}: {f[4][:260]}")
