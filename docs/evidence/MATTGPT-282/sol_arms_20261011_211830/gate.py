import json, sys
from collections import defaultdict
from pathlib import Path
D = Path(sys.argv[1])
ARMS = ["poc_4oplan", "poc_sol", "poc_sollow", "lever2_sol"]
scores = [s for f in sorted((D / "scores").glob("scores_g*.json")) for s in json.loads(f.read_text())]
rows = json.loads((D / "lever2_sol.json").read_text())
expect = {(r["case"], r["run"], r["turn"]) for r in rows}
keys = [(s["case"], s["run"], s["turn"], s["label"]) for s in scores]
assert len(keys) == len(set(keys)) == 4 * len(expect), (len(keys), len(set(keys)), len(expect))
assert {k[:3] for k in keys} == expect and {k[3] for k in keys} == set("ABCD")
print("scores valid:", len(scores))
key = json.loads((D / "key" / "key.json").read_text())
tally = defaultdict(lambda: defaultdict(int)); n = defaultdict(set)
for s in scores:
    arm = key[f"{s['case']}_r{s['run']:02d}"][s["label"]]
    tally[(s["case"], s["turn"])][arm] += bool(s["pass"]); n[(s["case"], s["turn"])].add(s["run"])
print(f"{'turn':9}" + "".join(f"{a:>12}" for a in ARMS) + "   vs lever2_sol (B/C/A)")
tot = defaultdict(int); N = 0; below = defaultdict(list); noise = defaultdict(list)
for (c, t), v in sorted(tally.items()):
    runs = len(n[(c, t)]); N += runs
    flags = []
    for a in ("poc_sol", "poc_sollow", "poc_4oplan"):
        gap = v["lever2_sol"] - v[a]
        if gap > 0 and (runs >= 10 or gap >= 2):
            below[a].append(f"{c} t{t} {v[a]} vs {v['lever2_sol']}"); flags.append(f"{a} BELOW")
        elif gap == 1:
            noise[a].append(f"{c} t{t}"); flags.append(f"{a} -1 noise")
    for a in ARMS: tot[a] += v[a]
    print(f"{c} t{t:<5}" + "".join(f"{str(v[a]) + '/' + str(runs):>12}" for a in ARMS) + "   " + "; ".join(flags))
print("total", {a: f"{tot[a]}/{N}" for a in ARMS})
print("below lever2_sol:", dict(below)); print("1-run noise:", dict(noise))
json.dump({f"{c} t{t}": dict(v) for (c, t), v in sorted(tally.items())}, open(D / "gate.json", "w"), indent=1)
