"""Build the gate's blind packets: one per (case, run), arms shuffled into
labels A, B (and C where the baseline ran) with a fixed seed. Writes the
packets and the scorers' brief to <score_dir>, and the key to <out>/key/
(outside the scorers' folder). Then splits the packets into scoring groups."""
import json, random, shutil, string, sys
from collections import defaultdict
from pathlib import Path
OUT, SD, RS = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
rows = [r for f in sorted(OUT.glob("rows_lane*.json")) for r in json.loads(f.read_text())]
TITLES = {"x1": "real estate", "x2": "SAP", "x3": "trading platforms", "x4": "ROI", "x5": "gaming", "x7": "JP Morgan dates"}
by = defaultdict(lambda: defaultdict(list))
for r in rows:
    by[(r["case"], r["run"])][r["arm"]].append(r)
rng = random.Random(2752)
(SD / "packets").mkdir(parents=True, exist_ok=True)
key, sizes = {}, {}
for (case, run), arms in sorted(by.items()):
    order = sorted(arms); rng.shuffle(order)
    letters = string.ascii_uppercase[:len(order)]
    name = f"{case}_r{run:02d}"
    key[name] = dict(zip(letters, order))
    per = {lab: sorted(arms[a], key=lambda x: x["turn"]) for lab, a in zip(letters, order)}
    n_turns = {len(v) for v in per.values()}
    assert len(n_turns) == 1, (name, n_turns)
    title = f"Conversation {int(case[1:])}" if case.startswith("c") else f"Extra {case} ({TITLES[case]})"
    lines = [f"# {title}, run {run}", "", f"Labels in this packet: {', '.join(letters)}.", ""]
    live = 0
    for i, tx in enumerate(per[letters[0]]):
        if tx.get("seeded"):
            seeds = {per[l][i]["answer_md"] for l in letters}
            assert len(seeds) == 1, name
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
for f in ("corpus_6ec9aec.jsonl", "matt_profile.json", "profile_rendered.txt"):
    shutil.copy(RS / f, SD / f)
b = (RS / "brief_locked.md").read_text(encoding="utf-8")
edits = [
    ("Each packet holds one conversation, answered by one system, labelled A.",
     "Each packet holds one conversation, answered by two or three systems, labelled A, B and (where present) C; the order is random in each packet."),
    ("Score every assistant turn of A,", "Score every assistant turn of every label,"),
    ("and the profile (matt_profile.json);",
     "and the profile (matt_profile.json, and profile_rendered.txt: the same facts as the sentences the assistant receives);"),
    ("Each packet holds one visitor question, answered by A.", "Each packet holds one visitor question, answered by each label."),
    ('`{"case", "run", "turn", "label": "A", "pass",', '`{"case", "run", "turn", "label" (the label scored), "pass",'),
    ("## Extras (x1 to x5): single-turn absence and adjacency questions",
     "## Extras (x1 to x5): single-turn absence and adjacency questions\n\n**x7** (“When was he at JP Morgan?”) is not an absence question and has no written outcome in Section 3, so it is scored on Sections 4 and 5 alone, as a first turn. The extras rules below apply to x1 to x5 only."),
]
for old, new in edits:
    assert b.count(old) == 1, old
    b = b.replace(old, new)
(SD / "brief.md").write_text(b, encoding="utf-8")
bb = (SD / "brief.md").read_bytes()
assert bb.count("—".encode()) == bb.count("–".encode()) == 0
# groups: whole packets, kept together by case, at most ~44 answers each
groups, cur, cur_n, cur_case = [], [], 0, None
for name in sorted(sizes):
    case = name.split("_")[0]
    if cur and (cur_n + sizes[name] > 44 or (case != cur_case and cur_n >= 30)):
        groups.append(cur); cur, cur_n = [], 0
    cur.append(name); cur_n += sizes[name]; cur_case = case
if cur: groups.append(cur)
(SD / "groups.json").write_text(json.dumps([{"g": i + 1, "packets": g, "answers": sum(sizes[n] for n in g)} for i, g in enumerate(groups)], indent=1))
print("packets", len(key), "answers", sum(sizes.values()), "groups", len(groups), "sizes", [sum(sizes[n] for n in g) for g in groups])
