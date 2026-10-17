"""MATTGPT-322 run 2 merge (Oct 16, 2026; untracked probe): joins the blind
scores to the key and reports, per arm (VA, VB: rule 0b in Agy's voice; NB,
OB: run 1's first rewording and old 0b, router off):
  - pass by set (declines, facts, controls);
  - each Brand Voice Checklist item, on declines and on all answers;
  - the decline standard: names_missing, one or two sentences,
    too_dismissive, too_apologetic, padded, speculation;
  - the bar per decline question: runs meeting every item;
and, from the answer text alone: distinct first lines across the model's
declines, and declines that reuse one of rule 0b's two examples verbatim.
Usage: python probes/probe_322b_merge.py <run2_out> <run1_out> <scoring_dir>
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

OUT, RUN1, SD = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
ARMS = ["VA", "VB", "NB", "OB"]
VOICE = ["voice_first_person", "voice_paw_ok", "voice_smart_helpful", "voice_professional",
         "voice_no_dog_puns", "voice_warm_credible", "voice_ends_on_content",
         "voice_substance_first", "voice_trust"]
EXAMPLES = ["I came up empty on that one: Matt's stories don't mention his hobbies.",
            "That's not something Matt's record covers: there's nothing on patents."]
key = json.loads((OUT / "key" / "key.json").read_text())
groups = json.loads((SD / "groups.json").read_text())
scores = []
missing = []
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
            and not any(s.get(f) for f in ("too_dismissive", "too_apologetic", "padded", "speculation")))


seen = set()
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
        for scope in (kd == "decline" and "decline", "all"):
            if scope:
                t[(scope, v, arm)][0] += bool(s.get(v))
                t[(scope, v, arm)][1] += 1
    if kd == "decline":
        for f in ("names_missing", "too_dismissive", "too_apologetic", "padded", "speculation"):
            t[("decline", f, arm)][0] += bool(s.get(f))
            t[("decline", f, arm)][1] += 1
        t[("decline", "one_or_two_sentences", arm)][0] += 1 <= (s.get("sentence_count") or 0) <= 2
        t[("decline", "one_or_two_sentences", arm)][1] += 1
        ok = good_decline(s)
        t[("decline", "meets_every_item", arm)][0] += bool(ok)
        t[("decline", "meets_every_item", arm)][1] += 1
        bar[s["case"]][arm][0] += bool(ok)
        bar[s["case"]][arm][1] += 1


def norm(x):
    return (x or "").replace("’", "'").strip()


rows = [r for f in sorted(OUT.glob("rows_lane*.json")) for r in json.loads(f.read_text())]
rows += [r for f in sorted(RUN1.glob("rows_lane*.json")) for r in json.loads(f.read_text()) if r["arm"] in ("NB", "OB")]
firsts, reuse = defaultdict(list), defaultdict(int)
for r in rows:
    if r["kind"] == "decline" and not r.get("ui_reason"):
        firsts[r["arm"]].append(norm(r["answer_md"]).splitlines()[0] if r["answer_md"] else "")
        reuse[r["arm"]] += any(e in norm(r["answer_md"]) for e in EXAMPLES)

print(f"scored answers: {len(scores)}, no duplicates; groups with no scores: {missing or 'none'}\n")
for label, scope, f in [("declines pass", "decline", "pass"), ("0a facts pass", "fact", "pass"),
                        ("story controls pass", "control", "pass")]:
    print(f"  {label:30}", "  ".join(f"{a}: {t[(scope, f, a)][0]}/{t[(scope, f, a)][1]}" for a in ARMS))
print("\ndeclines, Brand Voice Checklist (true):")
for v in VOICE:
    print(f"  {v:30}", "  ".join(f"{a}: {t[('decline', v, a)][0]}/{t[('decline', v, a)][1]}" for a in ARMS))
print("\ndeclines, the decline standard:")
for f in ("names_missing", "one_or_two_sentences", "too_dismissive", "too_apologetic", "padded", "speculation", "meets_every_item"):
    print(f"  {f:30}", "  ".join(f"{a}: {t[('decline', f, a)][0]}/{t[('decline', f, a)][1]}" for a in ARMS))
print("\nall answers, Brand Voice Checklist items not met:")
print("  ", "  ".join(f"{a}: {sum(t[('all', v, a)][1] - t[('all', v, a)][0] for v in VOICE)}" for a in ARMS))
print("\nmodel-written declines (banners excluded), from the answer text:")
for a in ARMS:
    print(f"  {a}: {len(firsts[a])} declines, {len(set(firsts[a]))} distinct first lines, {reuse[a]} reuse an example verbatim")
print("\nthe bar, per decline question (runs meeting every item, of 10):")
for case in sorted(bar):
    print(f"  {case}", "  ".join(f"{a} {bar[case][a][0]:2}/{bar[case][a][1]}" for a in ARMS))
