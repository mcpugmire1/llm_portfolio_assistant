"""Control isolation run (Oct 15): blind packets, one per (case, run), arms
cur, A, B, C shuffled into labels A to D (seed 2753). Scorer files are
last night's arms_score set (brief_v2, corpus, profile, Ground Truth lines)
with the label count changed from five to four. Key goes to <out>/key/."""
import json, random, shutil, string, sys
from collections import defaultdict
from pathlib import Path
OUT, SD, SRC = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
rows = [r for f in sorted(OUT.glob("rows_lane*.json")) for r in json.loads(f.read_text())]
by = defaultdict(lambda: defaultdict(list))
for r in rows:
    by[(r["case"], r["run"])][r["arm"]].append(r)
rng = random.Random(2753)
(SD / "packets").mkdir(parents=True, exist_ok=True)
(SD / "scores").mkdir(exist_ok=True)
(SD / "helpers").mkdir(exist_ok=True)
key, sizes = {}, {}
for (case, run), arms in sorted(by.items()):
    assert sorted(arms) == ["A", "B", "C", "cur"], (case, run, sorted(arms))
    order = sorted(arms); rng.shuffle(order)
    letters = string.ascii_uppercase[:len(order)]
    name = f"{case}_r{run:02d}"
    key[name] = dict(zip(letters, order))
    per = {lab: sorted(arms[a], key=lambda x: x["turn"]) for lab, a in zip(letters, order)}
    assert len({len(v) for v in per.values()}) == 1, name
    lines = [f"# Conversation {int(case[1:])}, run {run}", "", f"Labels in this packet: {', '.join(letters)}.", ""]
    live = 0
    for i, tx in enumerate(per[letters[0]]):
        if tx.get("seeded"):
            assert len({per[l][i]["answer_md"] for l in letters}) == 1, name
            lines += [f"## Turn {tx['turn']}. Seeded answer (given to every label; not scored)", "", tx["answer_md"], ""]
            continue
        live += 1
        lines += [f"## Turn {tx['turn']}. Visitor: {tx['question']}", ""]
        for lab in letters:
            lines += [f"### {lab}", "", per[lab][i].get("answer_md") or "(no answer)", ""]
    (SD / "packets" / f"{name}.md").write_text("\n".join(lines), encoding="utf-8")
    sizes[name] = live * len(letters)
(OUT / "key").mkdir(exist_ok=True)
(OUT / "key" / "key.json").write_text(json.dumps(key, indent=1))
for f in ("corpus_6ec9aec.jsonl", "matt_profile.json", "profile_rendered.txt", "matt_dna_ground_truth.txt"):
    shutil.copy(SRC / f, SD / f)
for f, old, new in [
    ("brief.md", "answered by five systems, labelled A to E;", "answered by four systems, labelled A to D;"),
    ("TASK.md", "answered by five systems, labelled A to E.", "answered by four systems, labelled A to D."),
    ("TASK.md", '"label" ("A" to "E")', '"label" ("A" to "D")'),
]:
    src = (SD / f) if (SD / f).exists() else (SRC / f)
    t = src.read_text(encoding="utf-8")
    assert t.count(old) == 1, (f, old)
    (SD / f).write_text(t.replace(old, new), encoding="utf-8")
for f in ("brief.md", "TASK.md"):
    bb = (SD / f).read_bytes()
    assert bb.count("—".encode()) == bb.count("–".encode()) == 0, f
# groups: whole packets, at most ~40 answers each
groups, cur, n = [], [], 0
for name in sorted(sizes):
    if cur and n + sizes[name] > 40:
        groups.append(cur); cur, n = [], 0
    cur.append(name); n += sizes[name]
if cur: groups.append(cur)
(SD / "groups.json").write_text(json.dumps([{"g": i + 1, "packets": g, "answers": sum(sizes[x] for x in g)} for i, g in enumerate(groups)], indent=1))
print("packets", len(key), "answers", sum(sizes.values()), "groups", len(groups), "sizes", [sum(sizes[x] for x in g) for g in groups])
