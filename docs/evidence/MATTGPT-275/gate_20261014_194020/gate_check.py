"""MATTGPT-275 gate check: blind scores + key -> per-arm counts per turn, the
assembled baseline, and every approved threshold. Code checks on the rows:
dashes in visible answers, the paw rate and opener variety, production's
nonsense result on the extras, errors, and cost at run 2's Sol prices."""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
OUT, SD, RS = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
EM, EN, PAW = "—", "–", "\U0001f43e"
SOL = (2.00, 0.10, 10.0)
rows = [r for f in sorted(OUT.glob("rows_lane*.json")) for r in json.loads(f.read_text())]
live = [r for r in rows if not r.get("seeded")]
key = json.loads((OUT / "key" / "key.json").read_text())
scores = [s for f in sorted((SD / "scores").glob("scores_g*.json")) for s in json.loads(f.read_text())]
want = {(r["case"], r["run"], r["turn"], r["arm"]) for r in live}
got = [(s["case"], s["run"], s["turn"], key[f"{s['case']}_r{s['run']:02d}"][s["label"]]) for s in scores]
assert len(got) == len(set(got)) and set(got) == want, (len(got), len(set(got)), len(want), sorted(want - set(got))[:5], sorted(set(got) - want)[:5])
print("scores valid:", len(scores))
S = {g: s for g, s in zip(got, scores)}
run2 = json.loads((RS / "rederived_baseline_locked.json").read_text())
RUN2_FIVE = {"c01", "c03", "c04", "c11", "c12", "x1", "x2", "x3", "x4", "x5"}
turns = sorted({(c, t) for c, _r, t, _a in want})
GENERAL = {"c01 t1", "c03 t1", "c04 t1", "c04 t3", "c09 t1", "c11 t1", "c12 t1", "c02 t1", "c05 t1", "c06 t1", "c07 t1", "c08 t1", "c13 t1", "c10 t1", "c18 t1", "c14 t1", "c15 t1", "c16 t1", "x7 t1"}
FOLLOW = {"c01 t2", "c01 t3", "c09 t3", "c09 t4", "c10 t2", "c10 t3", "c11 t3", "c12 t2", "c18 t3", "c02 t2", "c03 t2", "c05 t2", "c06 t2", "c07 t2", "c08 t2", "c13 t2", "c17 t2"}
SWITCH = {"c09 t2", "c11 t2", "c18 t2"}
ABSENCE = {"x2 t1", "x3 t1", "x4 t1", "x5 t1", "x1 t1"}
PMP = {"c04 t2"}
classes = GENERAL | FOLLOW | SWITCH | ABSENCE | PMP
names = {f"{c} t{t}" for c, t in turns}
assert names == classes and len(classes) == 45 == len(GENERAL) + len(FOLLOW) + len(SWITCH) + len(ABSENCE) + len(PMP), (names ^ classes)

def arm_stats(arm, c, t):
    ss = [S[(c, r, t, arm)] for r in range(1, 11) if (c, r, t, arm) in S]
    return {"n": len(ss), "pass": sum(bool(s["pass"]) for s in ss),
            "contra": sum(s["contradicted"] > 0 for s in ss), "unsup": sum(s["unsupported"] > 0 for s in ss),
            "invented": [(s["run"], i) for s in ss for i in s["invented"]], "carry": sum(bool(s["carry_over"]) for s in ss),
            "fails": [f"r{s['run']}: {s['reason'][:170]}" for s in ss if not s["pass"]]}

table, fails_gate, notes = [], [], []
tot = Counter()
for c, t in turns:
    nm = f"{c} t{t}"
    new, op, bl = arm_stats("new", c, t), arm_stats("opener", c, t), arm_stats("baseline", c, t)
    if c == "c09":
        base, bsrc = run2[nm]["pass"], "run 2 (10)"
    elif c in RUN2_FIVE:
        assert bl["n"] == 5, (nm, bl["n"])
        base, bsrc = run2[nm]["pass"] + bl["pass"], f"run 2 {run2[nm]['pass']}/5 + gate {bl['pass']}/5"
    else:
        assert bl["n"] == 10, (nm, bl["n"])
        base, bsrc = bl["pass"], f"gate {bl['pass']}/10"
    assert new["n"] == op["n"] == 10, nm
    if nm in GENERAL: kind, bar, ok = "general", f">= {base - 1}", new["pass"] >= base - 1
    elif nm in FOLLOW: kind, bar, ok = "follow-up", f">= {base}", new["pass"] >= base
    elif nm in SWITCH: kind, bar, ok = "switch", "10, no carry-over", new["pass"] == 10 and new["carry"] == 0
    elif nm in PMP: kind, bar, ok = "PMP", "10", new["pass"] == 10
    elif nm == "x1 t1": kind, bar, ok = "absence strict", f">= {base}, 0 contradicted", new["pass"] >= base and new["contra"] == 0
    else: kind, bar, ok = "absence", f">= {base}", new["pass"] >= base
    if nm == "c12 t2":
        kind += " (strict ranking)"
    if not ok: fails_gate.append(nm)
    tot["new"] += new["pass"]; tot["opener"] += op["pass"]; tot["base"] += base
    table.append({"turn": nm, "kind": kind, "baseline": base, "baseline_src": bsrc, "bar": bar,
                  "new": new["pass"], "opener": op["pass"], "ok": ok,
                  "new_contra": new["contra"], "new_unsup": new["unsup"], "new_invented": new["invented"], "new_carry": new["carry"],
                  "opener_contra": op["contra"], "opener_unsup": op["unsup"], "opener_invented": op["invented"], "opener_carry": op["carry"],
                  "new_fails": new["fails"], "opener_fails": op["fails"], "baseline_fails": bl["fails"]})
print(f"\n{'turn':8} {'kind':26} {'baseline':>8}  {'bar':>18} {'new':>4} {'opener':>6}  ok   new: contra/unsup/carry")
for x in table:
    print(f"{x['turn']:8} {x['kind']:26} {x['baseline']:>5}/10  {x['bar']:>18} {x['new']:>4} {x['opener']:>6}  {'yes' if x['ok'] else 'NO ':3}  {x['new_contra']}/{x['new_unsup']}/{x['new_carry']}")
print(f"\nTOTAL baseline {tot['base']}/450 | new {tot['new']}/450 | opener {tot['opener']}/450 | total bar {'met' if tot['new'] >= tot['base'] else 'NOT MET'}")
contra_runs = sorted({(c, r) for (c, r, t, a), s in S.items() if a == "new" and s["contradicted"] > 0})
invented = [(c, r, t, s["invented"]) for (c, r, t, a), s in S.items() if a == "new" and s["invented"]]
print("new arm: runs with a contradicted claim:", contra_runs)
print("new arm: invented figures, clients or dates:", invented)
print("turns below their bar:", fails_gate)
# code checks
def first_line(a): return (a or "").strip().split("\n", 1)[0].strip()
code = {}
for arm in ("new", "opener", "baseline"):
    rs = [r for r in live if r["arm"] == arm]
    answered = [r for r in rs if not r.get("rejection") and not r.get("error")]
    vis = sum(1 for r in rs if EM in (r["answer_md"] or "") or EN in (r["answer_md"] or ""))
    raw = sum(1 for r in rs if any(EM in (c.get("raw_text") or "") or EN in (c.get("raw_text") or "") for c in r.get("calls") or []))
    paw_open = sum(1 for r in answered if (r["answer_md"] or "").lstrip().startswith(PAW))
    paw_one = sum(1 for r in answered if (r["answer_md"] or "").count(PAW) == 1)
    fl = Counter(first_line(r["answer_md"]) for r in answered)
    usage = [c["usage"] for r in rs for c in r.get("calls") or [] if c.get("usage")]
    cost = sum(((u["input"] - u["cached"]) * SOL[0] + u["cached"] * SOL[1] + u["output"] * SOL[2]) / 1e6 for u in usage)
    code[arm] = {"turns": len(rs), "errors": sum(1 for r in rs if r.get("error")), "rejections": Counter(r.get("rejection") for r in rs if r.get("rejection")),
                 "visible_dash_answers": vis, "raw_dash_answers": raw if arm != "baseline" else None,
                 "paw_opens": f"{paw_open}/{len(answered)}", "paw_exactly_one": f"{paw_one}/{len(answered)}",
                 "distinct_first_lines": len(fl), "top_first_line": fl.most_common(1)[0] if fl else None, "cost": round(cost, 2)}
    print(f"\n{arm}: {json.dumps(code[arm], ensure_ascii=False, default=str)}")
prod = Counter((r["case"], r.get("production_nonsense")) for r in live if r["arm"] == "new" and r["case"].startswith("x"))
print("\nproduction nonsense result on the extras (new arm rows):", dict(prod))
json.dump({"table": table, "total": dict(tot), "contra_runs": contra_runs, "invented": invented, "below": fails_gate, "code": code},
          open(OUT / "gate_result.json", "w"), indent=1, default=str, ensure_ascii=False)
