import json, sys
from collections import defaultdict
from pathlib import Path
D = Path(sys.argv[1])
scores = [s for f in sorted((D / "scores").glob("scores_g*.json")) for s in json.loads(f.read_text())]
rows = {a: json.loads((D / f"{a}.json").read_text()) for a in ("poc4o", "pocsol")}
expect = {(r["case"], r["run"], r["turn"]) for r in rows["poc4o"]}
keys = [(s["case"], s["run"], s["turn"], s["label"]) for s in scores]
assert len(keys) == len(set(keys)) == 2 * len(expect), (len(keys), len(set(keys)), len(expect))
assert {k[:3] for k in keys} == expect and {k[3] for k in keys} == {"A", "B"}
print("scores valid:", len(scores))
key = json.loads((D / "key" / "key.json").read_text())
tally = defaultdict(lambda: {"poc4o": 0, "pocsol": 0, "n": 0})
for s in scores:
    arm = key[f"{s['case']}_r{s['run']:02d}"][s["label"]]
    t = tally[(s["case"], s["turn"])]
    t[arm] += bool(s["pass"])
    t["n"] += 0.5
tot = {"poc4o": 0, "pocsol": 0}; n = 0
print("turn       gpt-4o  sol")
for (c, t), v in sorted(tally.items()):
    print(f"{c} t{t}    {v['poc4o']:>2}/{int(v['n'])}   {v['pocsol']:>2}/{int(v['n'])}" + ("   <-- sol below" if v["pocsol"] < v["poc4o"] else "   sol ahead" if v["pocsol"] > v["poc4o"] else ""))
    tot["poc4o"] += v["poc4o"]; tot["pocsol"] += v["pocsol"]; n += int(v["n"])
print("total", tot, "of", n)
json.dump({f"{c} t{t}": v for (c, t), v in sorted(tally.items())}, open(D / "gate.json", "w"), indent=1)
