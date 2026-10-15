"""MATTGPT-275 (Oct 14, 2026; untracked probe): dashes in Role Match's
model-written text, before and after the no-dash rule, and source_text
verbatim fidelity under the scoped extraction rule.

  before  production prompts as they are
  after   the planned Green prompts, applied in memory: NO_DASH_RULE on the
          assessment prompt, the scoped rule on the three extraction
          prompts (requirement text only; text copied from the JD keeps its
          dashes), and the assessment prompt's two em dashes rewritten.
          Every replacement is asserted before any model call.

JDs: data/probe_jd_att_principal.txt (0 dashes) and data/demo_jd.txt (4 em
dashes, 2 of them in requirement bullets). 3 runs per JD per arm,
interleaved. Runs run_assessment() on the working tree, gpt-4o, with every
chat.completions call's usage recorded. The Role Match pipeline calls no
query logger (services/jd_assessor.py, services/pinecone_service.py).

Usage: python probes/probe_275_role_match_dashes.py <out_dir>
"""

import json
import logging
import sys
import time
import traceback
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from services import jd_assessor as ja  # noqa: E402

EM, EN = "\u2014", "\u2013"
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=OUT / "stderr.txt", level=logging.WARNING)

LINE = (
    "Don't use em dashes or en dashes; use a comma, a colon, parentheses or a "
    "separate sentence, whichever fits."
)
EXTRACTION_RULE = (
    "- In the requirement statements you write yourself: " + LINE + " Text you "
    "copy from the JD keeps its exact wording and punctuation, dashes included."
)
VERBATIM = (
    "- Copy source_text as the entire JD bullet or sentence, verbatim and "
    "complete. Do not shorten, summarize, or truncate."
)
INVENT = "- Do not invent requirements -- only extract what is stated or clearly implied."


def _after_prompts():
    req = ja._REQUIRED_EXTRACTION_PROMPT
    pref = ja._PREFERRED_EXTRACTION_PROMPT
    imp = ja._IMPLICIT_EXTRACTION_PROMPT
    tmpl = ja.JD_ASSESSMENT_PROMPT_TEMPLATE
    for p in (req, pref):
        assert p.count(VERBATIM) == 1
    assert imp.count(INVENT) == 1
    req = req.replace(VERBATIM, VERBATIM + "\n" + EXTRACTION_RULE)
    pref = pref.replace(VERBATIM, VERBATIM + "\n" + EXTRACTION_RULE)
    imp = imp.replace(INVENT, INVENT + "\n" + EXTRACTION_RULE)
    edits = [
        (
            f"demonstrate the requirement {EM} high when",
            "demonstrate the requirement: high when",
        ),
        (
            f"describe ONLY what's missing {EM} do NOT restate what's present",
            "describe ONLY what's missing. Do NOT restate what's present",
        ),
        (
            "- Output valid JSON only, no preamble",
            "- " + LINE + "\n- Output valid JSON only, no preamble",
        ),
    ]
    for old, new in edits:
        assert tmpl.count(old) == 1, old
        tmpl = tmpl.replace(old, new)
    for p in (req, pref, imp, tmpl):
        assert EM not in p and EN not in p
    return {"req": req, "pref": pref, "imp": imp, "tmpl": tmpl}


AFTER = _after_prompts()
USAGE = []
_ORIG_CLIENT = ja._get_openai_client


def _recording_client():
    client = _ORIG_CLIENT()
    create = client.chat.completions.create

    def recording_create(*args, **kwargs):
        resp = create(*args, **kwargs)
        u = resp.usage
        cached = getattr(getattr(u, "prompt_tokens_details", None), "cached_tokens", 0) or 0
        USAGE.append({"in": u.prompt_tokens, "cached": cached, "out": u.completion_tokens})
        return resp

    client.chat.completions.create = recording_create
    return client


def main():
    stories = [
        json.loads(line)
        for line in (REPO / "echo_star_stories_nlp.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    (OUT / "after_prompts.json").write_text(json.dumps(AFTER, indent=1, ensure_ascii=False))
    jds = {
        "att": (REPO / "data/probe_jd_att_principal.txt").read_text(encoding="utf-8"),
        "demo": (REPO / "data/demo_jd.txt").read_text(encoding="utf-8"),
    }
    arms = ["before", "after"]
    rows = []
    for run in range(1, 4):
        order = arms if run % 2 else arms[::-1]
        for jd_name, jd_text in jds.items():
            for arm in order:
                USAGE.clear()
                ps = [patch.object(ja, "_get_openai_client", _recording_client)]
                if arm == "after":
                    ps += [
                        patch.object(ja, "_REQUIRED_EXTRACTION_PROMPT", AFTER["req"]),
                        patch.object(ja, "_PREFERRED_EXTRACTION_PROMPT", AFTER["pref"]),
                        patch.object(ja, "_IMPLICIT_EXTRACTION_PROMPT", AFTER["imp"]),
                        patch.object(ja, "JD_ASSESSMENT_PROMPT_TEMPLATE", AFTER["tmpl"]),
                    ]
                for p in ps:
                    p.start()
                t0 = time.perf_counter()
                try:
                    res, err = ja.run_assessment(jd_text, stories), None
                except Exception as e:  # recorded; the run goes on
                    res, err = {}, f"{type(e).__name__}: {e}"
                    logging.error("run failed %s %s r%s\n%s", arm, jd_name, run, traceback.format_exc())
                finally:
                    for p in reversed(ps):
                        p.stop()
                rows.append({
                    "arm": arm, "jd": jd_name, "run": run, "error": err,
                    "seconds": round(time.perf_counter() - t0, 1),
                    "usage": list(USAGE), "extraction": res.get("extraction"),
                    "results": res.get("results"),
                })
                (OUT / "rows.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
                n = len(res.get("results") or [])
                print(f"r{run} {jd_name} {arm} rows={n} calls={len(USAGE)}"
                      f"{' ERROR ' + err if err else ''}", flush=True)
                if sum(1 for r in rows if r["error"]) >= 2:
                    print("ABORT: 2 errors", flush=True)
                    return
    print("done", len(rows), "runs", flush=True)


if __name__ == "__main__":
    main()
