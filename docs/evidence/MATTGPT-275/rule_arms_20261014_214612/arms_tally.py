"""Five-arm tally: blind scores + key -> passes per arm per turn; targets and
controls; reasons for each target fail; cost per arm at run 2's Sol prices."""
import json, sys
from collections import defaultdict
from pathlib import Path
OUT, SD = Path(sys.argv[1]), Path(sys.argv[2])
ARMS = ["cur", "S", "A", "B", "C"]
SOL = (2.00, 0.10, 10.0)
rows = [r for f in sorted(OUT.glob("rows_lane*.json")) for r in json.loads(f.read_text()) if not r.get("seeded")]
key = json.loads((OUT / "key" / "key.json").read_text())
scores = [s for f in sorted((SD / "scores").glob("scores_g*.json")) for s in json.loads(f.read_text())]
want = {(r["case"], r["run"], r["turn"], r["arm"]) for r in rows}
got = [(s["case"], s["run"], s["turn"], key[f"{s['case']}_r{s['run']:02d}"][s["label"]]) for s in scores]
assert len(got) == len(set(got)) and set(got) == want, (len(got), len(set(got)), len(want))
print("scores valid:", len(scores))
S = dict(zip(got, scores))
TARGETS = {"c12 t2": "A", "x1 t1": "B", "x3 t1": "C"}
turns = sorted({(c, t) for c, _r, t, _a in want})
tab = defaultdict(dict)
for c, t in turns:
    for a in ARMS:
        ss = [S[(c, r, t, a)] for r in range(1, 4)]
        tab[f"{c} t{t}"][a] = (sum(bool(x["pass"]) for x in ss), sum(x["contradicted"] > 0 for x in ss), sum(x["unsupported"] > 0 for x in ss))
print(f"\n{'turn':8} {'role':10}" + "".join(f"{a:>12}" for a in ARMS) + "    (pass/3, contra, unsup)")
for nm, v in tab.items():
    role = "target " + TARGETS[nm] if nm in TARGETS else ("absence ctl" if nm[0] == "x" else "story ctl")
    print(f"{nm:8} {role:10}" + "".join(f"{f'{v[a][0]}/3 {v[a][1]} {v[a][2]}':>12}" for a in ARMS))
print("\ncontrol turns where an arm passes fewer than cur:")
for nm, v in tab.items():
    if nm in TARGETS: continue
    worse = [a for a in ARMS[1:] if v[a][0] < v["cur"][0]]
    if worse:
        base = v["cur"][0]
        print("  " + nm + ": " + ", ".join(f"{a} {v[a][0]}/3 vs cur {base}/3" for a in worse))
for a in ARMS:
    tot = sum(v[a][0] for v in tab.values()); ctl = sum(v[a][0] for n, v in tab.items() if n not in TARGETS)
    rs = [r for r in rows if r["arm"] == a]
    cost = sum(((u["input"] - u["cached"]) * SOL[0] + u["cached"] * SOL[1] + u["output"] * SOL[2]) / 1e6 for r in rs for c in r.get("calls") or [] for u in [c.get("usage")] if u)
    words = sum(len((r["answer_md"] or "").split()) for r in rs) / len(rs)
    n_all = 3 * len(tab); n_ctl = 3 * (len(tab) - len(TARGETS))
    print(f"arm {a:3}: total {tot}/{n_all}, controls {ctl}/{n_ctl}, mean words {words:.0f}, cost ${cost:.2f}")
print("\nTARGET FAILS by arm")
for nm in TARGETS:
    c, t = nm.split(" t"); t = int(t)
    for a in ARMS:
        for r in range(1, 4):
            s = S[(c, r, t, a)]
            if not s["pass"]: print(f"  {nm} {a} r{r}: {s['reason'][:200]}")
json.dump({k: {a: list(x) for a, x in v.items()} for k, v in tab.items()}, open(OUT / "arms_result.json", "w"), indent=1)
