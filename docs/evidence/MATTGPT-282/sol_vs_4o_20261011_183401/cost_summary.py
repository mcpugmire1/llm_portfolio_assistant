import json, sys, statistics as st
from collections import Counter
from pathlib import Path
D = Path(sys.argv[1])
PRICE = {"gpt-4o": (2.50, 1.25, 10.0), "gpt-6.1-sol": (2.00, 0.10, 10.0)}  # $/M input, cached input, output
P4O = PRICE["gpt-4o"]
def cost(u, p):
    if not u: return 0.0
    return ((u["input"] - u["cached"]) * p[0] + u["cached"] * p[1] + u["output"] * p[2]) / 1e6
out = {}
for arm in ("poc4o", "pocsol"):
    rows = json.loads((D / f"{arm}.json").read_text())
    ans = [r for r in rows if r.get("answer_usage")]
    req = Counter(r.get("answer_model_requested") for r in ans); res = Counter(r.get("answer_model_resolved") for r in ans)
    api = Counter(r.get("answer_api") for r in ans); pres = Counter(r.get("planner_model_resolved") for r in rows if r.get("planner_model_resolved"))
    fin = Counter(r.get("finish_reason") for r in ans)
    errs = [(r["case"], r["run"], r["turn"], r["error"]) for r in rows if r.get("error")]
    rej = Counter(r.get("rejection") for r in rows if r.get("rejection"))
    acts = Counter(r["plan"]["action"] for r in rows if r.get("plan"))
    p = PRICE[ans[0]["answer_model_requested"]]
    ac = [cost(r["answer_usage"], p) for r in ans]; pcst = [cost(r.get("planner_usage"), P4O) for r in rows if r.get("planner_usage")]
    clar = sum(1 for r in rows if r.get("plan", {}).get("action") == "clarify")
    no_answer_call = sum(1 for r in rows if r.get("plan") and not r.get("answer_usage"))
    print(f"== {arm}: {len(rows)} rows, {len(ans)} answering calls, {no_answer_call} turns without one (clarify rendered), errors {len(errs)}, rejections {dict(rej)}")
    print("   requested", dict(req), "| resolved", dict(res), "| api", dict(api), "| planner resolved", dict(pres))
    print("   finish", dict(fin), "| actions", dict(acts))
    tok = lambda k: st.mean(r["answer_usage"][k] for r in ans)
    print(f"   answering tokens/call mean: input {tok('input'):.0f}, cached {tok('cached'):.0f}, output {tok('output'):.0f}, reasoning {tok('reasoning'):.0f} (max {max(r['answer_usage']['reasoning'] for r in ans)})")
    secs = [r["answer_secs"] for r in ans]; tsecs = [r["seconds"] for r in rows]
    print(f"   answer_secs mean {st.mean(secs):.2f} median {st.median(secs):.2f} p90 {sorted(secs)[int(.9*len(secs))]:.2f} | whole turn mean {st.mean(tsecs):.2f}")
    print(f"   cost/answering call ${st.mean(ac):.4f} | planner/turn ${st.mean(pcst):.4f} | per turn total ${(sum(ac)+sum(pcst))/len(rows):.4f} | arm total ${sum(ac)+sum(pcst):.2f}")
    if errs: print("   errors:", errs[:5])
