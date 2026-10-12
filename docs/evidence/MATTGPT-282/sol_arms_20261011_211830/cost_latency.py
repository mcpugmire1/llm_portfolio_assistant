import json, sys, statistics as st
from collections import Counter
from pathlib import Path
D = Path(sys.argv[1])
SOL = (2.00, 0.10, 10.0); G4O = (2.50, 1.25, 10.0)
def c(u, p): return ((u["input"] - u["cached"]) * p[0] + u["cached"] * p[1] + u["output"] * p[2]) / 1e6
def pct(xs, q): xs = sorted(xs); return xs[min(len(xs) - 1, int(q * len(xs)))]
grand = 0
for arm in ("poc_4oplan", "poc_sol", "poc_sollow", "lever2_sol"):
    rows = json.loads((D / f"{arm}.json").read_text())
    calls = [x for r in rows for x in r["calls"]]
    cost = sum(c(x["usage"], SOL) for x in calls) + sum(c(r["planner_usage"], G4O) for r in rows if r.get("planner_usage") and (r.get("planner_model_resolved") or "").startswith("gpt-4o"))
    grand += cost
    models = Counter((x["role"], x["model"], x["effort"]) for x in calls)
    pm = Counter(r.get("planner_model_resolved") for r in rows if r.get("plan"))
    fv = [r["first_visible_secs"] for r in rows if r.get("first_visible_secs") is not None]
    vis = [x for r in rows for x in r["calls"] if x["role"] in ("answer", "lever2")]
    fin = [r["calls"][-1] for r in rows if r["calls"]]
    print(f"== {arm}: {len(rows)} turns, errors {sum(1 for r in rows if r.get('error'))}, rejections {sum(1 for r in rows if r.get('rejection'))}, cost ${cost:.2f} (${cost/len(rows):.4f}/turn)")
    print(f"   calls (role, model, effort): {dict(models)}; planner resolved {dict(pm)}; calls/turn {len(calls)/len(rows):.2f}; status {dict(Counter(x['status'] for x in calls))}")
    print(f"   first visible token (turn): median {st.median(fv):.2f}s p90 {pct(fv,.9):.2f}s (n={len(fv)}) | whole turn median {st.median(r['seconds'] for r in rows):.2f}s p90 {pct([r['seconds'] for r in rows],.9):.2f}s")
    print(f"   final call ttft median {st.median(x['ttft'] for x in fin if x['ttft'] is not None):.2f}s | reasoning tokens/call mean {st.mean(x['usage']['reasoning'] for x in calls):.0f} | output/call mean {st.mean(x['usage']['output'] for x in calls):.0f}")
    if arm != "lever2_sol":
        print(f"   actions {dict(Counter(r['plan']['action'] for r in rows if r.get('plan')))}")
print(f"total ${grand:.2f}")
