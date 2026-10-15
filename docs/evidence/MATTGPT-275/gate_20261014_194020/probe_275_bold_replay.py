"""MATTGPT-275 split-bold fix (Oct 14, 2026; untracked probe): replay the
recorded raw model text of the gate's new and opener answers through the
fixed _postprocess_agy_text(), with the stories each answer's sources named.
Check 1: no split bold remains. Check 2: with every ** removed, the text is
identical to the answer the gate recorded (only bold placement changed).
No model calls. Usage: python probes/probe_275_bold_replay.py <gate_out_dir>
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from ui.pages.ask_mattgpt import backend_service as bs  # noqa: E402
from utils.corpus_loader import load_stories  # noqa: E402

OUT = Path(sys.argv[1])
SPLIT_NUM = re.compile(r"\*\*\d[\d,]*[,.]\*\*\d")      # **135,**000
SPLIT_WORD = re.compile(r"[A-Za-z]{2}\*\*[a-z]\*\*")   # client**s**
stories = load_stories(str(REPO / "echo_star_stories_nlp.jsonl"))
bs.sync_portfolio_metadata(stories)  # as the app and the gate probe do: caches every corpus client
by_label = {f"{s.get('Title')} ({s.get('Client')})": s for s in stories}
rows = [r for f in sorted(OUT.glob("rows_lane*.json")) for r in json.loads(f.read_text())
        if r["arm"] in ("new", "opener") and not r.get("seeded")]
split = lambda t: bool(SPLIT_NUM.search(t) or SPLIT_WORD.search(t))  # noqa: E731
res = {"replayed": 0, "skipped": 0, "split_before": 0, "split_after": 0, "text_changed": [], "bold_changed": 0, "split_after_rows": []}
for r in rows:
    calls = r.get("calls") or []
    if not calls or r.get("error") or r.get("rejection"):
        res["skipped"] += 1
        continue
    used = [by_label[s] for s in r.get("sources") or [] if s in by_label]
    assert len(used) == len(r.get("sources") or []), (r["case"], r["run"], r["turn"])
    after, _ = bs._postprocess_agy_text(calls[-1]["raw_text"], used)
    before = r["answer_md"]
    res["replayed"] += 1
    res["split_before"] += split(before)
    if split(after):
        res["split_after"] += 1
        res["split_after_rows"].append((r["arm"], r["case"], r["run"], r["turn"]))
    if before.replace("**", "") != after.replace("**", ""):
        res["text_changed"].append((r["arm"], r["case"], r["run"], r["turn"]))
    res["bold_changed"] += before != after
(OUT / "bold_replay.json").write_text(json.dumps(res, indent=1))
print({k: (v if not isinstance(v, list) else len(v)) for k, v in res.items()})
