"""Gate rerun (Oct 15): blind packets, one per (case, run), arms shuffled into
labels A, B (and C where the baseline ran), seed 2754. As gate_packets.py,
with two changes:
  - the baseline's answers go through production's normalize_dashes()
    before packing, so dashes no longer tell the baseline apart (the Oct 14
    gate's blinding leak); every live answer in every packet is then
    asserted dash-free;
  - the scorers get brief_v2.md as is (already worded for two or three
    labels, x7 included, rule 10 with the reach sentence) and
    matt_dna_ground_truth.txt (Section 7 exception).
Run from the repo root with the repo venv. Key goes to <out>/key/."""
import json, random, shutil, string, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, ".")
from ui.pages.ask_mattgpt.backend_service import normalize_dashes  # noqa: E402
OUT, SD, RS = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
EM, EN = "—", "–"
rows = [r for f in sorted(OUT.glob("rows_lane*.json")) for r in json.loads(f.read_text())]
TITLES = {"x1": "real estate", "x2": "SAP", "x3": "trading platforms", "x4": "ROI", "x5": "gaming", "x7": "JP Morgan dates"}
normalized = unbolded = 0
# Ruling, Oct 15: every answer in every packet (all labels, seeds too) has its
# bold markers removed, then its dashes normalized, so neither the old
# pipeline's split bold nor its dashes tell the baseline apart.
for r in rows:
    if r.get("answer_md"):
        plain = r["answer_md"].replace("**", "")
        unbolded += plain != r["answer_md"]
        new = normalize_dashes(plain)
        normalized += new != plain
        r["answer_md"] = new
by = defaultdict(lambda: defaultdict(list))
for r in rows:
    by[(r["case"], r["run"])][r["arm"]].append(r)
rng = random.Random(2754)
for d in ("packets", "scores", "helpers"):
    (SD / d).mkdir(parents=True, exist_ok=True)
key, sizes = {}, {}
for (case, run), arms in sorted(by.items()):
    order = sorted(arms); rng.shuffle(order)
    letters = string.ascii_uppercase[:len(order)]
    name = f"{case}_r{run:02d}"
    key[name] = dict(zip(letters, order))
    per = {lab: sorted(arms[a], key=lambda x: x["turn"]) for lab, a in zip(letters, order)}
    assert len({len(v) for v in per.values()}) == 1, name
    title = f"Conversation {int(case[1:])}" if case.startswith("c") else f"Extra {case} ({TITLES[case]})"
    lines = [f"# {title}, run {run}", "", f"Labels in this packet: {', '.join(letters)}.", ""]
    live = 0
    for i, tx in enumerate(per[letters[0]]):
        if tx.get("seeded"):
            assert len({per[l][i]["answer_md"] for l in letters}) == 1, name
            lines += [f"## Turn {tx['turn']}. Seeded answer (given to every label; not scored)", "", tx["answer_md"], ""]
            continue
        live += 1
        lines += [f"## Turn {tx['turn']}. Visitor: {tx['question']}", ""]
        for lab in letters:
            ans = per[lab][i].get("answer_md") or "(no answer)"
            assert EM not in ans and EN not in ans, (name, lab, tx["turn"])
            lines += [f"### {lab}", "", ans, ""]
    text = "\n".join(lines)
    assert EM not in text and EN not in text and "**" not in text, name
    (SD / "packets" / f"{name}.md").write_text(text, encoding="utf-8")
    sizes[name] = live * len(letters)
(OUT / "key").mkdir(exist_ok=True)
(OUT / "key" / "key.json").write_text(json.dumps(key, indent=1))
for f in ("corpus_6ec9aec.jsonl", "matt_profile.json", "profile_rendered.txt", "matt_dna_ground_truth.txt"):
    shutil.copy(RS / "arms_score" / f, SD / f)
shutil.copy(RS / "brief_v2.md", SD / "brief.md")
task = (RS / "arms_score" / "TASK.md").read_text(encoding="utf-8")
for old, new in [
    ("answered by five systems, labelled A to E.", "answered by two or three systems, labelled A, B and sometimes C."),
    ('"label" ("A" to "E")', '"label" ("A", "B" or "C")'),
]:
    assert task.count(old) == 1, old
    task = task.replace(old, new)
(SD / "TASK.md").write_text(task, encoding="utf-8")
for f in ("brief.md", "TASK.md"):
    bb = (SD / f).read_bytes()
    assert bb.count(EM.encode()) == bb.count(EN.encode()) == 0, f
# groups: whole packets, kept together by case, at most ~44 answers each (as the Oct 14 gate)
groups, cur, cur_n, cur_case = [], [], 0, None
for name in sorted(sizes):
    case = name.split("_")[0]
    if cur and (cur_n + sizes[name] > 44 or (case != cur_case and cur_n >= 30)):
        groups.append(cur); cur, cur_n = [], 0
    cur.append(name); cur_n += sizes[name]; cur_case = case
if cur: groups.append(cur)
(SD / "groups.json").write_text(json.dumps([{"g": i + 1, "packets": g, "answers": sum(sizes[n] for n in g)} for i, g in enumerate(groups)], indent=1))
print("answers unbolded:", unbolded, "| answers with dashes normalized:", normalized)
for p in sorted((SD / "packets").glob("*.md")):
    t = p.read_text(encoding="utf-8")
    assert EM not in t and EN not in t and "**" not in t, p.name
print("all packets: 0 dashes, 0 bold markers")
print("packets", len(key), "answers", sum(sizes.values()), "groups", len(groups), "sizes", [sum(sizes[n] for n in g) for g in groups])
