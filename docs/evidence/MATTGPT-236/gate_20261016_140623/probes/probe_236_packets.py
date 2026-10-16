"""MATTGPT-236 blind packets (Oct 16, 2026; untracked probe). One packet per
(case, run), the three arms shuffled into labels A, B, C (seed 2360); the key
goes to <out>/key/, never into the scoring folder.

As MATTGPT-275's gate2_packets.py: every answer has its bold markers removed,
then its dashes normalized (production's normalize_dashes()), and every
packet is asserted free of both. A redirected turn (the router's or a
nonsense rule's) is packed as what the visitor sees: the banner text from
BANNER_COPY and the chip labels the banner shows, not _router_rejection()'s
prose, which the UI never renders.

Usage, from the frozen checkout with the repo venv:
  python probes/probe_236_packets.py <gate_out> <scoring_dir>
"""

import json
import random
import shutil
import string
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, ".")
from probe_236_step0 import ROUTER_SET  # noqa: E402
from ui.pages.ask_mattgpt.backend_service import normalize_dashes  # noqa: E402
from utils import ui_helpers as uh  # noqa: E402

OUT, SD = Path(sys.argv[1]), Path(sys.argv[2])
EM, EN = "—", "–"
HERE = Path(__file__).resolve().parent
SCRATCH = Path(__file__).resolve().parents[2]
EXTRA_TITLES = {"x1": "real estate", "x2": "SAP", "x3": "trading platforms", "x4": "ROI", "x5": "gaming", "x7": "JP Morgan dates"}
BANNERS = {
    "semantic_router:personal": ("personal", uh.PERSONAL_CHIPS),
    "semantic_router:out_of_scope": ("out_of_scope", uh.OUT_OF_SCOPE_CHIPS),
}


def rendered(row):
    reason = row.get("ui_reason")
    if not reason:
        return row.get("answer_md") or "(no answer)"
    if reason.startswith("rule:"):
        key, chips = "rule", uh.RULE_CHIPS
    else:
        key, chips = BANNERS[reason]
    labels = "; ".join(c[0] for c in chips)
    return f"{uh.BANNER_COPY[key]}\n\n(Shown under the banner as buttons: {labels})"


def title(case):
    if case.startswith("c"):
        return f"Conversation {int(case[1:])}"
    if case.startswith("x"):
        return f"Extra {case} ({EXTRA_TITLES[case]})"
    return f"Router question {case}"


rows = [r for f in sorted(OUT.glob("rows_lane*.json")) for r in json.loads(f.read_text())]
unbolded = normalized = redirects = 0
for r in rows:
    if r.get("seeded"):
        continue
    text = rendered(r)
    redirects += bool(r.get("ui_reason"))
    plain = text.replace("**", "")
    unbolded += plain != text
    new = normalize_dashes(plain)
    normalized += new != plain
    r["packed"] = new
by = defaultdict(lambda: defaultdict(list))
for r in rows:
    by[(r["case"], r["run"])][r["arm"]].append(r)
assert all(sorted(a) == ["A", "B", "C"] for a in by.values()), "an arm is missing from a (case, run)"
rng = random.Random(2360)
for d in ("packets", "scores", "helpers"):
    (SD / d).mkdir(parents=True, exist_ok=True)
key, sizes = {}, {}
for (case, run), arms in sorted(by.items()):
    order = sorted(arms)
    rng.shuffle(order)
    letters = string.ascii_uppercase[: len(order)]
    name = f"{case}_r{run:02d}"
    key[name] = dict(zip(letters, order))
    per = {lab: sorted(arms[a], key=lambda x: x["turn"]) for lab, a in zip(letters, order)}
    assert len({len(v) for v in per.values()}) == 1, name
    lines = [f"# {title(case)}, run {run}", "", f"Labels in this packet: {', '.join(letters)}.", ""]
    live = 0
    for i, tx in enumerate(per[letters[0]]):
        if tx.get("seeded"):
            assert len({per[lab][i]["answer_md"] for lab in letters}) == 1, name
            lines += [f"## Turn {tx['turn']}. Seeded answer (given to every label; not scored)", "", normalize_dashes(tx["answer_md"].replace("**", "")), ""]
            continue
        live += 1
        lines += [f"## Turn {tx['turn']}. Visitor: {tx['question']}", ""]
        for lab in letters:
            lines += [f"### {lab}", "", per[lab][i]["packed"], ""]
    text = "\n".join(lines)
    assert EM not in text and EN not in text and "**" not in text, name
    (SD / "packets" / f"{name}.md").write_text(text, encoding="utf-8")
    sizes[name] = live * len(letters)
(OUT / "key").mkdir(exist_ok=True)
(OUT / "key" / "key.json").write_text(json.dumps(key, indent=1))

# Scoring folder: the frozen checkout's corpus and profile, brief_v2 as
# scored in MATTGPT-320 (no Section 7 exception), and the rubric and task.
shutil.copy("echo_star_stories_nlp.jsonl", SD / "corpus_725d564.jsonl")
shutil.copy("data/matt_profile.json", SD / "matt_profile.json")
shutil.copy(SCRATCH / "profile_rendered_725d564.txt", SD / "profile_rendered.txt")
shutil.copy(SCRATCH / "score_320" / "brief.md", SD / "brief.md")
shutil.copy(HERE / "236_RUBRIC.md", SD / "RUBRIC.md")
shutil.copy(HERE / "236_TASK.md", SD / "TASK.md")
for f in ("brief.md", "TASK.md", "RUBRIC.md"):
    bb = (SD / f).read_bytes()
    assert bb.count(EM.encode()) == bb.count(EN.encode()) == 0, f
rubric = " ".join((SD / "RUBRIC.md").read_text(encoding="utf-8").split())
assert all(f'"{q}"' in rubric for _k, q in ROUTER_SET), "a router-set question is missing from RUBRIC.md"

# Groups: whole packets kept together by case, at most ~44 answers each.
groups, cur, cur_n, cur_case = [], [], 0, None
for name in sorted(sizes):
    case = name.split("_")[0]
    if cur and (cur_n + sizes[name] > 44 or (case != cur_case and cur_n >= 30)):
        groups.append(cur)
        cur, cur_n = [], 0
    cur.append(name)
    cur_n += sizes[name]
    cur_case = case
if cur:
    groups.append(cur)
(SD / "groups.json").write_text(json.dumps([{"g": i + 1, "packets": g, "answers": sum(sizes[n] for n in g)} for i, g in enumerate(groups)], indent=1))
print("answers unbolded:", unbolded, "| dashes normalized:", normalized, "| redirects packed as banners:", redirects)
print("packets", len(key), "answers", sum(sizes.values()), "groups", len(groups), "sizes", [sum(sizes[n] for n in g) for g in groups])
