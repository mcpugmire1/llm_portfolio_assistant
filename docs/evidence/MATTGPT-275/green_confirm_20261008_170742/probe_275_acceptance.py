"""MATTGPT-275 acceptance: evaluator conversations through the new tool path. Not tracked.

Arm "new": every conversation in tests/fixtures/evaluator_conversations.md,
turn by turn, through the real send_to_backend() (now agy_answer()), with the
transcript appended as the UI does. N runs per conversation.

Arm "voice": the first question of each conversation through the old path
(rag_answer(), no history) and the new path (agy_answer(), no history),
side by side, for Matt to read for Agy's voice.

All loggers patched out: log_query, log_offdomain, and the router's two CSV
writers. Records per turn: answer, rejection_reason, sources, the search
queries the model made, and wall time.

Usage: python probes/probe_275_acceptance.py <out_dir> <runs> <voice_runs>
"""

import json
import logging
import re
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[1]
load_dotenv(REPO / ".env")
logging.getLogger("streamlit").setLevel(logging.ERROR)
sys.path.insert(0, str(REPO))

from services import semantic_router  # noqa: E402
from ui.pages.ask_mattgpt import backend_service as bs  # noqa: E402
from utils.corpus_loader import load_stories  # noqa: E402

out_dir = Path(sys.argv[1])
runs = int(sys.argv[2])
voice_runs = int(sys.argv[3])
out_dir.mkdir(parents=True, exist_ok=True)

_text = (REPO / "tests" / "fixtures" / "evaluator_conversations.md").read_text()
CONVERSATIONS = [
    (f"{n}. {title}", re.findall(r"“(.+?)”", line))
    for n, title, line in re.findall(r"^(\d+)\. (.+)\n(“.+”)$", _text, re.M)
]

stories = load_stories(str(REPO / "echo_star_stories_nlp.jsonl"))
bs.sync_portfolio_metadata(stories)
_real_search = bs.semantic_search


def patched(session, queries):
    mock_st = MagicMock()
    mock_st.session_state = session

    def search_wrap(q, *a, **k):
        queries.append(q)
        return _real_search(q, *a, **k)

    return [
        patch("streamlit.session_state", session),
        patch.object(bs, "st", mock_st),
        patch.object(bs, "log_query", lambda *a, **k: None),
        patch.object(bs, "log_offdomain", lambda *a, **k: None),
        patch.object(semantic_router, "_log_borderline", lambda *a, **k: None),
        patch.object(semantic_router, "_log_router_low_confidence", lambda *a, **k: None),
        patch.object(bs, "semantic_search", search_wrap),
    ]


def call(fn, session, *args, **kw):
    queries = []
    ps = patched(session, queries)
    for p in ps:
        p.start()
    t0 = time.time()
    try:
        r = fn(*args, **kw)
    finally:
        for p in reversed(ps):
            p.stop()
    return r, queries, round(time.time() - t0, 2)


rows = []
for conv, questions in CONVERSATIONS:
    for run in range(1, runs + 1):
        session = {"ask_transcript": []}
        for turn, q in enumerate(questions, 1):
            session["ask_transcript"].append({"role": "user", "text": q})
            r, queries, secs = call(bs.send_to_backend, session, q, {}, None, stories)
            answer = r.get("answer_md") or ""
            if r.get("rejection_reason"):
                session["ask_transcript"].append({"type": "banner", "Role": "assistant", "reason": r["rejection_reason"]})
            else:
                session["ask_transcript"].append({"type": "conversational", "Role": "assistant", "text": answer})
            rows.append({"arm": "new", "conversation": conv, "run": run, "turn": turn, "question": q,
                         "answer_md": answer, "rejection_reason": r.get("rejection_reason"),
                         "degraded": r.get("degraded"), "search_queries": queries,
                         "sources": [s.get("title") for s in r.get("sources") or []],
                         "profile_categories": r.get("profile_categories") or [], "seconds": secs})
            print(f"[new | {conv[:24]:24} | run {run} | t{turn}] {secs}s searches={len(queries)} "
                  f"reason={r.get('rejection_reason')} | {answer[:70]!r}", flush=True)

for conv, questions in CONVERSATIONS:
    q = questions[0]
    for run in range(1, voice_runs + 1):
        for arm, fn, args, kw in (
            ("voice_old", bs.rag_answer, (q, {}, stories), {"history": []}),
            ("voice_new", bs.agy_answer, (q, stories), {"history": []}),
        ):
            r, queries, secs = call(fn, {"ask_transcript": [{"role": "user", "text": q}]}, *args, **kw)
            rows.append({"arm": arm, "conversation": conv, "run": run, "turn": 1, "question": q,
                         "answer_md": r.get("answer_md") or "", "rejection_reason": r.get("rejection_reason"),
                         "degraded": r.get("degraded"), "search_queries": queries,
                         "sources": [s.get("title") for s in r.get("sources") or []],
                         "profile_categories": r.get("profile_categories") or [], "seconds": secs})
            print(f"[{arm} | {conv[:24]:24} | run {run}] {secs}s | {(r.get('answer_md') or '')[:70]!r}", flush=True)

(out_dir / "acceptance.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
with (out_dir / "answers.txt").open("w") as f:
    for r in rows:
        f.write(f"===== [{r['arm']}] {r['conversation']} | run {r['run']} | turn {r['turn']}\n")
        f.write(f"Q: {r['question']}\n")
        f.write(f"searches: {r['search_queries']} | sources: {r['sources']} | reason: {r['rejection_reason']} | {r['seconds']}s\n\n")
        f.write(r["answer_md"] + "\n\n")
print("done", len(rows))
