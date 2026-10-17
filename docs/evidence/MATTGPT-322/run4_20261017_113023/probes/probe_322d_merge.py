"""MATTGPT-322 run 4 merge (Oct 17, 2026; untracked probe): joins the blind
scores to the key and reports, for DB (run 4: decline line picked in code
per turn, router off) against TB (run 3: four lines to vary in rule 0b,
router off):
  - pass by set (declines, facts, controls);
  - each Brand Voice Checklist item and the decline standard, on declines;
  - the bar per decline question: runs meeting every item;
and, from the answer text alone, per decline question and overall:
distinct first lines, declines using "trail", declines reusing one of the
four example lines word for word around the [topic] slot, and declines
still using the old template phrase "on record about"; for DB, whether each
decline follows its assigned line (whole line around [topic], or its
opening clause), and every decline scored opening_fits false.
Usage: python probes/probe_322d_merge.py <run4_out> <run3_out> <scoring_dir>
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

OUT, PREV, SD = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
ARMS = ["DB", "TB"]
VOICE = ["voice_first_person", "voice_paw_ok", "voice_smart_helpful", "voice_professional",
         "voice_no_dog_puns", "voice_warm_credible", "voice_ends_on_content",
         "voice_substance_first", "voice_trust"]
STANDARD = ("names_missing", "too_dismissive", "too_apologetic", "padded", "speculation")
EXAMPLES = [
    "I followed that trail and came up empty: Matt's stories don't cover [topic].",
    "That trail goes cold here. There's nothing on record about [topic].",
    "I searched Matt's whole record, and it doesn't mention [topic].",
    "I've been through Matt's stories, and nothing speaks to [topic].",
]
EXAMPLE_RE = [re.compile(re.escape(e).replace(re.escape("[topic]"), ".+?"), re.I) for e in EXAMPLES]
key = json.loads((OUT / "key" / "key.json").read_text())
groups = json.loads((SD / "groups.json").read_text())
scores, missing = [], []
for g in groups:
    f = SD / "scores" / f"scores_g{g['g']:02d}.json"
    if not f.exists():
        missing.append(g["g"])
        continue
    rows = json.loads(f.read_text())
    assert len(rows) == g["answers"], (g["g"], len(rows))
    scores += rows


def kind(case):
    n = int(case[1:])
    return "decline" if n <= 8 else "fact" if n <= 12 else "control"


def good_decline(s):
    return (s["pass"] and all(s.get(v) for v in VOICE) and s.get("names_missing")
            and 1 <= (s.get("sentence_count") or 0) <= 2
            and not any(s.get(f) for f in STANDARD[1:]))


seen = set()
misfit = []
t = defaultdict(lambda: [0, 0])
bar = defaultdict(lambda: defaultdict(lambda: [0, 0]))
for s in scores:
    name = f"{s['case']}_r{int(s['run']):02d}"
    arm = key[name][s["label"]]
    assert (name, s["label"]) not in seen
    seen.add((name, s["label"]))
    kd = kind(s["case"])
    t[(kd, "pass", arm)][0] += bool(s["pass"])
    t[(kd, "pass", arm)][1] += 1
    for v in VOICE:
        t[(kd, v, arm)][0] += bool(s.get(v))
        t[(kd, v, arm)][1] += 1
    if kd == "decline":
        for f in STANDARD:
            t[("decline", f, arm)][0] += bool(s.get(f))
            t[("decline", f, arm)][1] += 1
        t[("decline", "one_or_two_sentences", arm)][0] += 1 <= (s.get("sentence_count") or 0) <= 2
        t[("decline", "one_or_two_sentences", arm)][1] += 1
        ok = good_decline(s)
        t[("decline", "meets_every_item", arm)][0] += bool(ok)
        t[("decline", "meets_every_item", arm)][1] += 1
        bar[s["case"]][arm][0] += bool(ok)
        bar[s["case"]][arm][1] += 1
        t[("decline", "opening_fits", arm)][0] += bool(s.get("opening_fits"))
        t[("decline", "opening_fits", arm)][1] += 1
        if not s.get("opening_fits"):
            misfit.append((arm, name, s["label"]))


def norm(x):
    return (x or "").replace("’", "'").replace("\U0001f43e", "").strip()


rows = [r for f in sorted(OUT.glob("rows_lane*.json")) for r in json.loads(f.read_text())]
rows += [r for f in sorted(PREV.glob("rows_lane*.json")) for r in json.loads(f.read_text()) if r["arm"] == "TB"]
firsts = defaultdict(lambda: defaultdict(list))
trail = defaultdict(lambda: defaultdict(int))
reuse = defaultdict(lambda: defaultdict(lambda: [0] * len(EXAMPLES)))
old = defaultdict(lambda: defaultdict(int))
n = defaultdict(lambda: defaultdict(int))
for r in rows:
    if r["kind"] != "decline":
        continue
    assert not r.get("ui_reason"), "router-off arm returned a banner"
    a, c, text = r["arm"], r["case"], norm(r["answer_md"])
    n[a][c] += 1
    firsts[a][c].append(text.splitlines()[0].strip() if text else "")
    trail[a][c] += "trail" in text.lower()
    old[a][c] += "on record about" in text.lower()
    for i, rx in enumerate(EXAMPLE_RE):
        reuse[a][c][i] += bool(rx.search(text))

print(f"scored answers: {len(scores)}, no duplicates; groups with no scores: {missing or 'none'}\n")
for label, scope in [("declines pass", "decline"), ("0a facts pass", "fact"), ("story controls pass", "control")]:
    print(f"  {label:30}", "  ".join(f"{a}: {t[(scope, 'pass', a)][0]}/{t[(scope, 'pass', a)][1]}" for a in ARMS))
print("\ndeclines, Brand Voice Checklist (true):")
for v in VOICE:
    print(f"  {v:30}", "  ".join(f"{a}: {t[('decline', v, a)][0]}/{t[('decline', v, a)][1]}" for a in ARMS))
print("\ndeclines, the decline standard:")
for f in (*STANDARD[:1], "one_or_two_sentences", *STANDARD[1:], "meets_every_item", "opening_fits"):
    print(f"  {f:30}", "  ".join(f"{a}: {t[('decline', f, a)][0]}/{t[('decline', f, a)][1]}" for a in ARMS))
print("\nfacts and controls, Brand Voice Checklist items not met:")
print("  ", "  ".join(f"{a}: {sum(t[(k, v, a)][1] - t[(k, v, a)][0] for k in ('fact', 'control') for v in VOICE)}" for a in ARMS))
print("\nthe bar, per decline question (runs meeting every item, of 10):")
for case in sorted(bar):
    print(f"  {case}", "  ".join(f"{a} {bar[case][a][0]:2}/{bar[case][a][1]}" for a in ARMS))
print("\ndeclines from the answer text, per question: distinct first lines | 'trail' | example reuse (lines 1-4) | 'on record about'")
for a in ARMS:
    print(f"  {a}")
    for c in sorted(n[a]):
        print(f"    {c}: {len(set(firsts[a][c])):2}/{n[a][c]} distinct | trail {trail[a][c]:2} | reuse {reuse[a][c]} | old phrase {old[a][c]:2}")
    allf = [x for c in firsts[a] for x in firsts[a][c]]
    tot = sum(n[a].values())
    ru = [sum(reuse[a][c][i] for c in reuse[a]) for i in range(len(EXAMPLES))]
    print(f"    overall: {len(set(allf))}/{tot} distinct first lines | trail {sum(trail[a].values())}/{tot}"
          f" | reuse {ru} | old phrase {sum(old[a].values())}/{tot}")
print("\nDB first lines by frequency:")
cnt = defaultdict(int)
for c in firsts["DB"]:
    for x in firsts["DB"][c]:
        cnt[(c, x)] += 1
for (c, x), k in sorted(cnt.items()):
    print(f"  {c} x{k}: {x}")


def clause(line):
    """The assigned line's opening clause, before [topic]'s sentence."""
    body = norm(line)
    for sep in (":", ". ", ", and "):
        if sep in body:
            return body.split(sep)[0]
    return body.split("[topic]")[0]


print("\nDB: follows its assigned line, per question (whole line around [topic] | opening clause), of 10:")
byrow = {}
whole_t = clause_t = tot = 0
per = defaultdict(lambda: [0, 0, 0])
lines_used = defaultdict(lambda: [0, 0, 0])
for r in rows:
    if r["arm"] != "DB" or r["kind"] != "decline":
        continue
    a = r["decline_line"]
    assert isinstance(a, str), (r["case"], r["run"], a)
    text = norm(r["answer_md"])
    rx = re.compile(re.escape(norm(a)).replace(re.escape("[topic]"), ".+?"), re.I)
    w = bool(rx.search(text))
    c = clause(a).lower() in text.lower()
    per[r["case"]][0] += w
    per[r["case"]][1] += c
    per[r["case"]][2] += 1
    i = EXAMPLES.index(norm(a))
    lines_used[i][0] += 1
    lines_used[i][1] += w
    lines_used[i][2] += c
    byrow[f"{r['case']}_r{int(r['run']):02d}"] = (a, r["answer_md"])
    whole_t += w
    clause_t += c
    tot += 1
for case in sorted(per):
    print(f"  {case}: {per[case][0]:2} | {per[case][1]:2} (of {per[case][2]})")
print(f"  overall: whole {whole_t}/{tot} | clause {clause_t}/{tot}")
print("\nDB per assigned line: assigned | whole | clause")
for i, e in enumerate(EXAMPLES):
    print(f"  line {i + 1} ({e[:40]}...): {lines_used[i][0]} | {lines_used[i][1]} | {lines_used[i][2]}")
print("\ndeclines scored opening_fits false:")
for arm, name, lab in misfit:
    a, ans = byrow.get(name, ("(run 3: no assigned line)", ""))
    if arm == "DB":
        print(f"  DB {name}: assigned {a!r}\n     answer {ans!r}")
    else:
        print(f"  TB {name} (label {lab})")
if not misfit:
    print("  none")
