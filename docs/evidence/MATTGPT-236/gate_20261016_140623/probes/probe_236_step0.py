"""MATTGPT-236 step 0 (Oct 16, 2026; untracked probe): what the router decides
for every question the router-off vs router-on gate will ask. Embeddings
only, no answering call. For each question: is_nonsense() (which runs before
the router in agy_answer()), is_portfolio_query_semantic(), and
router_rejection_reason(). The router's two CSV writers are patched out.

Questions: the 275 gate's 45 live turns (probe_275_gate.CASES) plus the
router set (personal and hobby questions, out_of_scope candidates, synthesis
questions, and the fact questions the query log shows it mislabeling).
Usage: python probes/probe_236_step0.py <out_dir>
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe_275_gate as g  # noqa: E402  (reads sys.argv[1] as the out dir)

from services import semantic_router  # noqa: E402
from utils.validation import is_nonsense  # noqa: E402

ROUTER_SET = [
    ("personal", "Is Matt married?"),
    ("personal", "How old is Matt?"),
    ("personal", "Does Matt have kids?"),
    ("hobby", "What does Matt like to do for fun?"),
    ("hobby", "What does Matt do outside of work?"),
    ("hobby", "What are Matt's hobbies?"),
    ("oos-candidate", "Has Matt worked in agriculture?"),
    ("oos-candidate", "Has Matt worked in oil and gas?"),
    ("oos-candidate", "Has Matt worked in retail?"),
    ("oos-candidate", "Has Matt worked in insurance?"),
    ("synthesis", "Why hire Matt?"),
    ("synthesis", "What are Matt's core themes?"),
    ("synthesis", "What patterns show up across Matt's work?"),
    ("fact", "What languages does Matt speak?"),
    ("fact", "Does Matt have a master's degree?"),
    ("fact", "Does Matt speak French?"),
]


def decide(q):
    nonsense = is_nonsense(q)
    valid, score, matched, family = semantic_router.is_portfolio_query_semantic(q)
    return {
        "nonsense": nonsense,
        "family": family,
        "score": round(score, 3),
        "matched": matched,
        "redirect": semantic_router.router_rejection_reason(family, score),
        "synthesis": family == "synthesis",
    }


def main():
    rows = []
    with (
        patch.object(semantic_router, "_log_borderline", lambda *a, **k: None),
        patch.object(semantic_router, "_log_router_low_confidence", lambda *a, **k: None),
    ):
        for case, turns in g.CASES.items():
            for t, q in enumerate(turns, 1):
                if q is not None:
                    rows.append({"set": "gate", "case": case, "turn": t, "question": q, **decide(q)})
        for kind, q in ROUTER_SET:
            rows.append({"set": "router", "case": kind, "turn": 1, "question": q, **decide(q)})
    (g.OUT / "rows.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    for r in rows:
        flag = "REDIRECT " + r["redirect"] if r["redirect"] else ("SYNTHESIS" if r["synthesis"] else "")
        if r["nonsense"]:
            flag = f"NONSENSE {r['nonsense']}"
        print(f"{r['set']:6} {r['case']:13} t{r['turn']} {r['score']:.3f} {r['family']!s:20} {flag:28} {r['question'][:70]}")


if __name__ == "__main__":
    main()
