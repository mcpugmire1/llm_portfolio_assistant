"""MATTGPT-322 blind packets for run 6 (Oct 17, 2026; untracked probe). One
packet per (question, run), two arms shuffled into labels A and B (seed
3224): run 6's FB ("Begin with this line", two lines, router off) and run
4's DB ("Use this shape", four lines, router off). The key goes to
<run6_out>/key/. As probe_236_packets.py: bold removed, dashes
normalized, every packet asserted free of both; a redirected turn is packed
as the banner and chip labels the visitor sees. One scorer group per
question (10 packets, 20 answers).

Usage, from the frozen checkout with the repo venv:
  python probes/probe_322f_packets.py <run6_out> <run4_out> <scoring_dir>
"""

import json
import random
import shutil
import string
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, ".")
from probe_322f_run import CASES  # noqa: E402

from ui.pages.ask_mattgpt.backend_service import normalize_dashes  # noqa: E402
from utils import ui_helpers as uh  # noqa: E402

OUT, PREV, SD = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
EM, EN = "—", "–"
HERE = Path(__file__).resolve().parent
SCRATCH = Path(__file__).resolve().parents[2]
BANNERS = {
    "semantic_router:personal": ("personal", uh.PERSONAL_CHIPS),
    "semantic_router:out_of_scope": ("out_of_scope", uh.OUT_OF_SCOPE_CHIPS),
}


def rendered(row):
    reason = row.get("ui_reason")
    if not reason:
        return row.get("answer_md") or "(no answer)"
    key, chips = ("rule", uh.RULE_CHIPS) if reason.startswith("rule:") else BANNERS[reason]
    labels = "; ".join(c[0] for c in chips)
    return f"{uh.BANNER_COPY[key]}\n\n(Shown under the banner as buttons: {labels})"


rows = [r for f in sorted(OUT.glob("rows_lane*.json")) for r in json.loads(f.read_text())]
rows += [r for f in sorted(PREV.glob("rows_lane*.json")) for r in json.loads(f.read_text()) if r["arm"] == "DB"]
by = defaultdict(dict)
for r in rows:
    by[(r["case"], r["run"])][r["arm"]] = normalize_dashes(rendered(r).replace("**", ""))
assert all(sorted(a) == ["DB", "FB"] for a in by.values()), "an arm is missing"
assert len(by) == len(CASES) * 10, len(by)
rng = random.Random(3224)
for d in ("packets", "scores", "helpers"):
    (SD / d).mkdir(parents=True, exist_ok=True)
key = {}
for (case, run), arms in sorted(by.items()):
    order = sorted(arms)
    rng.shuffle(order)
    letters = string.ascii_uppercase[: len(order)]
    name = f"{case}_r{run:02d}"
    key[name] = dict(zip(letters, order, strict=False))
    lines = [f"# Question {case}, run {run}", "", f"Labels in this packet: {', '.join(letters)}.", "",
             f"## Visitor: {CASES[case]}", ""]
    for lab, arm in zip(letters, order, strict=False):
        lines += [f"### {lab}", "", arms[arm], ""]
    text = "\n".join(lines)
    assert EM not in text and EN not in text and "**" not in text, name
    (SD / "packets" / f"{name}.md").write_text(text, encoding="utf-8")
(OUT / "key").mkdir(exist_ok=True)
(OUT / "key" / "key.json").write_text(json.dumps(key, indent=1))
shutil.copy("echo_star_stories_nlp.jsonl", SD / "corpus.jsonl")
shutil.copy("data/matt_profile.json", SD / "matt_profile.json")
shutil.copy(SCRATCH / "profile_rendered_725d564.txt", SD / "profile_rendered.txt")
shutil.copy(SCRATCH / "score_320" / "brief.md", SD / "brief.md")
shutil.copy(HERE / "322f_RUBRIC.md", SD / "RUBRIC.md")
shutil.copy(HERE / "322f_TASK.md", SD / "TASK.md")
for f in ("RUBRIC.md", "TASK.md"):
    t = (SD / f).read_text(encoding="utf-8")
    assert EM not in t and EN not in t, f
rubric = " ".join((SD / "RUBRIC.md").read_text(encoding="utf-8").split())
assert all(f'"{q}"' in rubric or case in ("q13", "q14", "q15", "q16", "q17") for case, q in CASES.items()), "a question is missing from RUBRIC.md"
groups = [{"g": i, "packets": [f"{c}_r{r:02d}" for r in range(1, 11)], "answers": 20} for i, c in enumerate(CASES, 1)]
(SD / "groups.json").write_text(json.dumps(groups, indent=1))
print("packets", len(key), "answers", 20 * len(groups), "groups", len(groups))
