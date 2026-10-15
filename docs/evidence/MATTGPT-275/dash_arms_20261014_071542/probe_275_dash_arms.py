"""MATTGPT-275 step 3 measurement (Oct 14, 2026; untracked probe): dashes in
Sol's raw answers under four prompt arms, interleaved.

  A  current prompt
  B  current prompt plus the no-dash line
  C  the prompt's own 19 em-dash lines rewritten by hand (approved), no line
  D  C plus the no-dash line

Set: c01, c03, c09 (fixture 609f903, with history) and x1, x3, 5 runs each:
11 turns per arm per run, 55 per arm, 220 in all. Runs agy_answer() on the
working tree with the step 3 code backstop on; the raw model text is
captured from _stream_response() before any dash rule. The prompt arms are
applied in memory to build_tool_system_prompt()'s output; every replacement
is asserted before any model call. Loggers patched: log_query,
log_offdomain, _log_borderline, _log_router_low_confidence. The nonsense
check is bypassed for x1 and x3 (as run 2 did).

Usage: python probes/probe_275_dash_arms.py <out_dir>
"""

import json
import logging
import re
import sys
import time
import traceback
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from services import semantic_router  # noqa: E402
from ui.pages.ask_mattgpt import backend_service as bs  # noqa: E402

EM, EN = "—", "–"
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=OUT / "stderr.txt", level=logging.WARNING)

LINE = (
    "Don't use em dashes or en dashes; use a comma, a colon, parentheses or a "
    "separate sentence, whichever fits."
)
LINE_AFTER = "Write natural prose paragraphs after the opening. No section headers or labels."

# (old, new, modes) for the 19 approved rewrites; modes the line appears in.
REWRITES = [
    (f"You are Agy 🐾 {EM} Matt Pugmire's", "You are Agy 🐾, Matt Pugmire's", "both"),
    (f'"This demonstrates..." {EM} STOP.', '"This demonstrates...", STOP.', "both"),
    (f"## Matt Pugmire {EM} Ground Truth", "## Matt Pugmire: Ground Truth", "both"),
    (f"capabilities that win work {EM} differentiation", "capabilities that win work: differentiation", "both"),
    (f"emphasize delivery excellence {EM} never position", "emphasize delivery excellence, and never position", "both"),
    (f"WHY (30-40%): The tension {EM} what was broken, who was pushing back, what wasn't working.",
     "WHY (30-40%): The tension (what was broken, who was pushing back, what wasn't working).", "standard"),
    (f"HOW (40-50%): What Matt did differently {EM} specific practices, anecdotes, what he did instead of the standard approach.",
     "HOW (40-50%): What Matt did differently (specific practices, anecdotes, what he did instead of the standard approach).", "standard"),
    (f"WHAT (10-20%): The proof {EM} measurable results with bolded numbers, client context, scale.",
     "WHAT (10-20%): The proof (measurable results with bolded numbers, client context, scale).", "standard"),
    (f"Matt redesigned the pipeline {EM} CI/CD automation and pair programming\ninstead of the manual review cycle",
     "Matt redesigned the pipeline, adding CI/CD automation and pair programming\nin place of the manual review cycle", "standard"),
    (f"differentiation, or adoption** {EM} what was broken", "differentiation, or adoption**: what was broken", "standard"),
    (f"made Matt's approach different {EM} not just what he did", "made Matt's approach different: not just what he did", "standard"),
    (f"(pair programming, TDD {EM} not \"agile methodologies\")", "(pair programming or TDD, not \"agile methodologies\")", "standard"),
    (f"Preserve the story's texture {EM} specific details", "Preserve the story's texture: specific details", "standard"),
    (f"tension or pattern of difficulty {EM} what keeps failing across organizations, what resistance Matt encountered repeatedly.",
     "tension or pattern of difficulty (what keeps failing across organizations, what resistance Matt encountered repeatedly).", "synthesis"),
    (f"HOW (40-50%): What Matt did differently {EM} the repeatable approach across these stories, how it contrasts with standard practice.",
     "HOW (40-50%): What Matt did differently (the repeatable approach across these stories, and how it contrasts with standard practice).", "synthesis"),
    (f"WHAT (10-20%): Proof {EM} measurable outcomes across clients, scale, pattern confirmation.",
     "WHAT (10-20%): Proof (measurable outcomes across clients, scale, pattern confirmation).", "synthesis"),
    (f"Remaining stories are optional {EM} use them only", "Remaining stories are optional. Use them only", "synthesis"),
    (f'state the shared difficulty: "In both cases, teams were stuck on..." {EM} not "This demonstrates Matt\'s pattern of..."',
     'state the shared difficulty, for example "In both cases, teams were stuck on...". Don\'t write "This demonstrates Matt\'s pattern of..."',
     "synthesis"),
    (f"Do NOT evaluate Matt {EM} state what happened", "Do NOT evaluate Matt. State what happened.", "synthesis"),
]

_orig_build = bs.build_tool_system_prompt
ARM = {"name": "A"}


def build_for_arm(*args, **kwargs):
    prompt = _orig_build(*args, **kwargs)
    mode = "synthesis" if kwargs.get("is_synthesis") else "standard"
    if ARM["name"] in ("C", "D"):
        for old, new, modes in REWRITES:
            if modes in ("both", mode):
                assert prompt.count(old) == 1, (mode, old)
                prompt = prompt.replace(old, new)
        assert EM not in prompt and EN not in prompt, (mode, "dash left after rewrites")
    if ARM["name"] in ("B", "D"):
        assert prompt.count(LINE_AFTER) == 1, (mode, "insertion point")
        prompt = prompt.replace(LINE_AFTER, LINE_AFTER + "\n" + LINE)
    return prompt


RAW = []
_orig_stream = bs._stream_response


def recording_stream(*args, **kwargs):
    resp = _orig_stream(*args, **kwargs)
    RAW.append(getattr(resp, "output_text", "") or "")
    return resp


def fixture_turns(text, num):
    m = re.search(rf"^{num}\. .+\n(.+)$", text, re.M)
    return [t.strip()[1:-1] for t in m.group(1).split(" → ")]


FIXTURE = (REPO / "tests/fixtures/evaluator_conversations.md").read_text(encoding="utf-8")
CONVS = {f"c{n:02d}": fixture_turns(FIXTURE, n) for n in (1, 3, 9)}
CONVS["x1"] = ["Has Matt worked in real estate?"]
CONVS["x3"] = ["Has Matt worked on trading platforms?"]
ARMS = ["A", "B", "C", "D"]
RUNS = 5
MAX_ERRORS = 5


def main():
    stories = [
        json.loads(line)
        for line in (REPO / "echo_star_stories_nlp.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for s in stories:
        s["id"] = str(s.get("id", "")).strip()
    bs.sync_portfolio_metadata(stories)

    # Pre-flight: every arm's prompt builds in both modes before any model call.
    for arm in ARMS:
        ARM["name"] = arm
        for syn in (False, True):
            build_for_arm(
                is_synthesis=syn, matt_dna=bs.MATT_DNA, profile_facts="",
                opener_examples=bs.SYNTHESIS_OPENERS + bs.STANDARD_OPENERS, focus_angle="",
            )
    print("prompt arms built in both modes", flush=True)

    rows, errors = [], 0
    mock_st = MagicMock()
    for run in range(1, RUNS + 1):
        order = ARMS[run - 1 :] + ARMS[: run - 1]
        for arm in order:
            ARM["name"] = arm
            for case, turns in CONVS.items():
                transcript = []
                for t, q in enumerate(turns, 1):
                    mock_st.session_state = {}
                    transcript.append({"role": "user", "text": q})
                    history = bs._build_history_messages(transcript)
                    RAW.clear()
                    t0 = time.perf_counter()
                    ps = [
                        patch.object(bs, "st", mock_st),
                        patch.object(bs, "build_tool_system_prompt", build_for_arm),
                        patch.object(bs, "_stream_response", recording_stream),
                        patch.object(bs, "log_query", MagicMock()),
                        patch.object(bs, "log_offdomain", MagicMock()),
                        patch.object(semantic_router, "_log_borderline", MagicMock()),
                        patch.object(semantic_router, "_log_router_low_confidence", MagicMock()),
                    ]
                    if case.startswith("x"):
                        ps.append(patch.object(bs, "_nonsense_rejection", lambda *a, **k: None))
                    for p in ps:
                        p.start()
                    try:
                        res = bs.agy_answer(q, stories, history=history)
                        err = None
                    except Exception as e:  # recorded; the run goes on
                        res, err = {"answer_md": ""}, f"{type(e).__name__}: {e}"
                        logging.error("turn failed %s %s t%s r%s\n%s", arm, case, t, run, traceback.format_exc())
                    finally:
                        for p in reversed(ps):
                            p.stop()
                    if err or res.get("degraded"):
                        errors += 1
                    raw = RAW[-1] if RAW else ""
                    rows.append({
                        "arm": arm, "case": case, "turn": t, "run": run, "question": q,
                        "raw_text": raw, "answer_md": res.get("answer_md", ""),
                        "rejection": res.get("rejection_reason"), "degraded": res.get("degraded"),
                        "error": err, "calls": len(RAW), "seconds": round(time.perf_counter() - t0, 2),
                    })
                    transcript.append({"Role": "assistant", "text": res.get("answer_md", "")})
                    print(f"r{run} {arm} {case} t{t} em={raw.count(EM)} en={raw.count(EN)}"
                          f"{' ERROR ' + err if err else ''}", flush=True)
                    (OUT / "rows.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
                    if errors > MAX_ERRORS:
                        print("ABORT: too many errors", flush=True)
                        return
    print("done", len(rows), "turns", flush=True)


if __name__ == "__main__":
    main()
