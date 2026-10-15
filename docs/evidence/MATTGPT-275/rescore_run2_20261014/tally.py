"""Validate the 130 re-scores and re-derive run 2's lever2_sol baseline per turn."""
import json, sys
from collections import defaultdict
from pathlib import Path
R = Path(sys.argv[1]); E = Path(sys.argv[2])
KEYS = {"case","run","turn","label","pass","reason","claims","contradicted","unsupported","invented","carry_over","clarifying","acknowledges_missing","useful_direct"}
scores = [s for f in sorted((R/"scores").glob("scores_g*.json")) for s in json.loads(f.read_text())]
rows = json.loads((E/"lever2_sol.json").read_text())
expect = {(r["case"], r["run"], r["turn"]) for r in rows}
got = [(s["case"], s["run"], s["turn"]) for s in scores]
bad = [s for s in scores if set(s) != KEYS]
assert not bad, f"{len(bad)} scores with wrong keys, e.g. {sorted(set(bad[0]) ^ KEYS)}"
assert len(got) == len(set(got)) == len(expect) and set(got) == expect, (len(got), len(set(got)), len(expect), sorted(expect - set(got))[:5], sorted(set(got) - expect)[:5])
print("scores valid:", len(scores))
old = json.loads((E/"gate.json").read_text())
t = defaultdict(lambda: {"n":0,"pass":0,"contra":0,"unsup":0,"invented":0,"carry":0,"fails":[]})
for s in scores:
    k = (s["case"], s["turn"]); v = t[k]
    v["n"] += 1; v["pass"] += bool(s["pass"])
    v["contra"] += s["contradicted"] > 0; v["unsup"] += s["unsupported"] > 0; v["invented"] += bool(s["invented"])
    v["carry"] += bool(s["carry_over"])
    if not s["pass"]: v["fails"].append(f"r{s['run']}: {s['reason'][:150]}")
print(f"\n{'turn':8} {'old':>6} {'new':>6} {'diff':>5}  answers with: contradicted / unsupported / invented / carry-over")
to = tn = 0
for (c, tu), v in sorted(t.items()):
    o = old[f"{c} t{tu}"]["lever2_sol"]; to += o; tn += v["pass"]
    print(f"{c} t{tu:<4} {o:>3}/{v['n']:<2} {v['pass']:>3}/{v['n']:<2} {v['pass']-o:>+5}  {v['contra']} / {v['unsup']} / {v['invented']} / {v['carry']}")
print(f"total    {to:>3}/130 {tn:>3}/130 {tn-to:>+5}")
json.dump({f"{c} t{tu}": {"old": old[f"{c} t{tu}"]["lever2_sol"], **{k: v[k] for k in ("n","pass","contra","unsup","invented","carry")}} for (c, tu), v in sorted(t.items())},
          open(R/"rederived_baseline.json", "w"), indent=1)
print("\nFAILS")
for (c, tu), v in sorted(t.items()):
    for f in v["fails"]: print(f"  {c} t{tu} {f}")
