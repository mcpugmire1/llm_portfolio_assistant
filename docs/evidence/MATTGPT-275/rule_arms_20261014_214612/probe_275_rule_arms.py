"""MATTGPT-275 five-arm live acceptance run (Oct 14, 2026; untracked probe),
interleaved run by run within each (case, run):

  cur  the working tree as is (dates line and split-bold fix in)
  S    "- Draw on all the stories provided." removed from STANDARD_DELTA's RULES
  A    COMPARISON_RULE added after NO_DASH_RULE
  B    INDUSTRY_CLAIM_RULE added after NO_DASH_RULE
  C    TERM_SENSE_RULE added after NO_DASH_RULE

Arms are applied in memory to build_tool_system_prompt()'s output; every
replacement is asserted in both modes before any model call (S has nothing to
remove in synthesis mode, so it equals cur there). Each arm alone; no
combinations. Turns run through probe_275_gate.new_turn(): send_to_backend()
-> agy_answer(), loggers patched (log_query, log_offdomain, _log_borderline,
_log_router_low_confidence, the query logger's sheet), the extras bypass the
nonsense rules as in the gate, raw model text and usage recorded.

Cases: c12, c01, c04, c09, c13 (fixture 609f903) and x1, x2, x3, x5; 18 live
turns per run, 3 runs, 270 turns. Lanes: LANE=i/N.
Usage: LANE=0/3 python probes/probe_275_rule_arms.py <out_dir>
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe_275_gate as g  # noqa: E402  (reads sys.argv[1] as the out dir)

bs, OUT = g.bs, g.OUT
LANE, LANES = (int(x) for x in os.environ.get("LANE", "0/1").split("/"))
RUNS = 3
CASES = ["c12", "c01", "c04", "c09", "c13", "x1", "x2", "x3", "x5"]
ARMS = ["cur", "S", "A", "B", "C"]

NO_DASH = (
    "Don't use em dashes or en dashes; use a comma, a colon, parentheses or a "
    "separate sentence, whichever fits."
)
DRAW_ON_ALL = "- Draw on all the stories provided.\n"
RULES = {
    "A": (
        "When asked which of two things was bigger or better, compare only on a "
        "measure the stories give for both, in the same units. If their figures "
        "can't settle it (an open-ended figure against an exact one, or two "
        "different measures), say the stories don't establish which is larger."
    ),
    "B": (
        "Say Matt has worked in an industry or domain only when a story's "
        "[INDUSTRY] or [DOMAIN] line, or a fact about Matt above, names it. "
        "Otherwise say it is not on record in Matt's stories, then name the "
        "closest related work with its own industry. Never say Matt has not "
        "worked in it."
    ),
    "C": (
        "If a story uses the visitor's term for something else (a system named "
        "with it, or the same word in another sense), name that work and say "
        "what it is, so it isn't taken for the thing asked about."
    ),
}
ARM = {"name": "cur"}
_build = g._orig_build


def build_for_arm(*args, **kwargs):
    prompt = _build(*args, **kwargs)
    name, synthesis = ARM["name"], kwargs.get("is_synthesis")
    if name == "S":
        if synthesis:
            assert DRAW_ON_ALL not in prompt
        else:
            assert prompt.count(DRAW_ON_ALL) == 1, "S: line not found once"
            prompt = prompt.replace(DRAW_ON_ALL, "")
    elif name in RULES:
        assert prompt.count(NO_DASH) == 1, f"{name}: anchor not found once"
        prompt = prompt.replace(NO_DASH, NO_DASH + "\n" + RULES[name])
    return prompt


def main():
    for arm in ARMS:
        for syn in (False, True):
            ARM["name"] = arm
            build_for_arm(
                is_synthesis=syn, matt_dna=bs.MATT_DNA, profile_facts="",
                opener_examples=bs.SYNTHESIS_OPENERS + bs.STANDARD_OPENERS, focus_angle="",
            )
    print("all arms built in both modes", flush=True)
    jobs = [(c, r) for c in CASES for r in range(1, RUNS + 1)][LANE::LANES]
    rows, errors = [], []
    g.canary("start")
    with patch.object(bs, "build_tool_system_prompt", build_for_arm):
        for case, r in jobs:
            k = r % len(ARMS)
            for arm in ARMS[k:] + ARMS[:k]:
                ARM["name"] = arm
                got = g.new_run("new", case, r)
                for x in got:
                    x["arm"] = arm
                rows += got
                errors += [(arm, case, r, x["turn"]) for x in got if x.get("error")]
                if len(errors) > g.MAX_ERRORS:
                    raise g.Abort(f"more than {g.MAX_ERRORS} errors: {errors[-3:]}")
                (OUT / f"rows_lane{LANE}.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    g.canary("end")
    print(f"done | rows {len(rows)} | errors {errors}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except g.Abort as e:
        print(f"ABORT: {e}", flush=True)
        sys.exit(2)
