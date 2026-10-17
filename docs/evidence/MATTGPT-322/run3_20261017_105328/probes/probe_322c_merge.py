"""MATTGPT-322 run 3 merge (Oct 17, 2026; untracked probe): joins the blind
scores to the key and reports, for TB (run 3: rule 0b with four decline
lines to vary, router off) against VB (run 2: rule 0b in Agy's voice,
router off):
  - pass by set (declines, facts, controls);
  - each Brand Voice Checklist item and the decline standard, on declines;
  - the bar per decline question: runs meeting every item;
and, from the answer text alone, per decline question and overall:
distinct first lines, declines using "trail", declines reusing one of the
four example lines word for word around the [topic] slot, and declines
still using the old template phrase "on record about".
Usage: python probes/probe_322c_merge.py <run3_out> <run2_out> <scoring_dir>
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

OUT, RUN2, SD = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
ARMS = ["TB", "VB"]
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


def norm(x):
    return (x or "").replace("’", "'").replace("\U0001f43e", "").strip()


rows = [r for f in sorted(OUT.glob("rows_lane*.json")) for r in json.loads(f.read_text())]
rows += [r for f in sorted(RUN2.glob("rows_lane*.json")) for r in json.loads(f.read_text()) if r["arm"] == "VB"]
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
for f in (*STANDARD[:1], "one_or_two_sentences", *STANDARD[1:], "meets_every_item"):
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
print("\nTB first lines by frequency:")
cnt = defaultdict(int)
for c in firsts["TB"]:
    for x in firsts["TB"][c]:
        cnt[(c, x)] += 1
for (c, x), k in sorted(cnt.items()):
    print(f"  {c} x{k}: {x}")
