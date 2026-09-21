"""Probe -244: does the source_text instruction cause truncation?

_REQUIRED_EXTRACTION_PROMPT and _PREFERRED_EXTRACTION_PROMPT both
carry the instruction:

    Keep source_text short -- just enough to verify the extraction.

Observed across three runs on the demo JD (September 2026): the
Kubernetes preferred bullet lost its parenthetical every time.
Graduate degree lost it twice of three. Cloud-native, Cross-functional,
and AI/ML lost their bullet tails on one run each. Different form
(parenthetical drop vs tail truncation), same behavior: source_text
comes back shorter than the JD bullet on roughly a quarter of rows,
varying by run.

This probe tests whether the instruction is the cause by comparing
against a treatment prompt that requires the complete bullet
verbatim.

Design:
- 10 runs on the demo JD in one session, interleaved (control,
  treatment, control, treatment, ...). Interleave rather than
  batched arms so cache warmth cannot correlate with arm and
  confound the read. Same rationale as prior -244 probes.
- Metric: exact-match between source_text and a JD line. A
  source_text that is a proper substring of a JD line is a
  truncation. Substring containment is not verbatim -- the earlier
  "234/234 verbatim" measurement missed this class of defect by
  accepting substring containment as sufficient.
- Report per-run truncation counts, list which rows truncated per
  run, and per-row truncation frequency across the ten runs split
  by arm.

Read:
- Zero truncations in the treatment arm: the instruction was the
  cause and a prompt-side fix works.
- Truncations persist at a similar rate: it is summarization, not
  the prompt, and the instruction is not the lever.

Implicit rows are out of scope for this probe: they carry
inferred_from (which is not asserted to be verbatim by design) not
source_text.

Probe only, no production change. Timestamped output under
probe_244_source_text_output/ (output stays untracked). Exempt from
the Red gate under the CLAUDE.md Probes and PoCs rule.
"""

import json
import time
from pathlib import Path
from typing import Any
from unittest.mock import patch

from services import jd_assessor

_BASE = Path(__file__).parent
_JD_PATH = _BASE / "data" / "demo_jd.txt"
OUTPUT_DIR = _BASE / "probe_244_source_text_output"

RUNS_PER_ARM = 5

# The instruction under test. Must match the current prompt text
# character-for-character; _build_treatment_prompt asserts the
# replacement fired so future prompt-copy drift fails loudly rather
# than silently running control text in both arms.
CONTROL_INSTRUCTION = "Keep source_text short -- just enough to verify the extraction."

# Replacement instruction that requires the complete bullet verbatim.
# Names the failure mode ("shorten, summarize, or truncate") so the
# model has no room to reinterpret "just enough."
TREATMENT_INSTRUCTION = (
    "Copy source_text as the entire JD bullet or sentence, verbatim "
    "and complete. Do not shorten, summarize, or truncate."
)


def _build_treatment_prompt(prompt: str) -> str:
    replaced = prompt.replace(CONTROL_INSTRUCTION, TREATMENT_INSTRUCTION)
    if replaced == prompt:
        raise ValueError(
            f"CONTROL_INSTRUCTION not found in prompt; expected: "
            f"{CONTROL_INSTRUCTION!r}. The prompt may have been edited "
            f"since this probe was written; update CONTROL_INSTRUCTION "
            f"in this file to match the current wording."
        )
    return replaced


TREATMENT_REQUIRED_PROMPT = _build_treatment_prompt(
    jd_assessor._REQUIRED_EXTRACTION_PROMPT
)
TREATMENT_PREFERRED_PROMPT = _build_treatment_prompt(
    jd_assessor._PREFERRED_EXTRACTION_PROMPT
)


def extract_control(client, jd_text: str) -> dict:
    """Extract with the current production prompts (control arm).
    DEBUG is patched off for the call so the probe's per-run
    accounting output stays scannable -- if config.debug.DEBUG is
    on, each extract_requirements call emits ~20 extraction_item
    lines that would drown the probe's own reporting."""
    with patch.object(jd_assessor, "DEBUG", False):
        return jd_assessor.extract_requirements(client, jd_text)


def extract_treatment(client, jd_text: str) -> dict:
    """Extract with the treatment prompts (verbatim-required
    instruction). Patches the module-level prompt constants for the
    duration of the call; extract_requirements' internal helpers read
    the constants at call time via module globals, so the patch
    reaches every wave-1 call in the async fan-out. DEBUG is patched
    off for the same reason as extract_control."""
    with (
        patch.object(jd_assessor, "DEBUG", False),
        patch.object(
            jd_assessor,
            "_REQUIRED_EXTRACTION_PROMPT",
            TREATMENT_REQUIRED_PROMPT,
        ),
        patch.object(
            jd_assessor,
            "_PREFERRED_EXTRACTION_PROMPT",
            TREATMENT_PREFERRED_PROMPT,
        ),
    ):
        return jd_assessor.extract_requirements(client, jd_text)


def check_verbatim(source_text: str, jd_lines: list[str]) -> tuple[str, str | None]:
    """Compare source_text against the JD lines.

    Returns (status, matching_line):
      "exact"     : source_text equals a JD line exactly.
      "truncated" : source_text is a proper substring of some JD line.
      "no_match"  : source_text is not contained in any JD line
                    (paraphrase, invention, or empty).

    When multiple JD lines contain source_text, picks the shortest
    (most specific) as the matching_line. Rare on this fixture, but
    the tiebreak is deterministic."""
    source_text = (source_text or "").strip()
    if not source_text:
        return "no_match", None
    matching = [line for line in jd_lines if source_text in line]
    if not matching:
        return "no_match", None
    line = min(matching, key=len)
    if source_text == line:
        return "exact", line
    return "truncated", line


def analyze_extraction(extraction: dict, jd_lines: list[str]) -> list[dict]:
    """Per-item verbatim status for required + preferred sections
    (implicit uses inferred_from and is out of scope)."""
    items = []
    for section in ("required_qualifications", "preferred_qualifications"):
        for i, r in enumerate(extraction.get(section, []) or []):
            source_text = r.get("source_text", "")
            status, line = check_verbatim(source_text, jd_lines)
            items.append(
                {
                    "section": section,
                    "idx": i,
                    "requirement": r.get("requirement", ""),
                    "source_text": source_text,
                    "status": status,
                    "matching_line": line,
                }
            )
    return items


def main() -> None:
    jd_text = _JD_PATH.read_text()
    jd_lines = [line.strip() for line in jd_text.splitlines() if line.strip()]
    client = jd_assessor._get_openai_client()

    run_timestamp = time.strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_DIR / run_timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    # Interleaved order: C, T, C, T, ...
    arm_order = []
    for _ in range(RUNS_PER_ARM):
        arm_order.append("control")
        arm_order.append("treatment")

    print("Probe -244: source_text instruction vs verbatim treatment")
    print(f"JD: {_JD_PATH.name} ({len(jd_text.split())} words)")
    print(f"Runs: {len(arm_order)} interleaved ({RUNS_PER_ARM} per arm)")
    print()

    all_runs: list[dict[str, Any]] = []
    for i, arm in enumerate(arm_order, 1):
        print(f"[{i:2d}/{len(arm_order)}] arm={arm}...", end=" ", flush=True)
        t0 = time.perf_counter()
        if arm == "control":
            extraction = extract_control(client, jd_text)
        else:
            extraction = extract_treatment(client, jd_text)
        elapsed = time.perf_counter() - t0
        items = analyze_extraction(extraction, jd_lines)
        truncated = [it for it in items if it["status"] == "truncated"]
        no_match = [it for it in items if it["status"] == "no_match"]
        print(
            f"{elapsed:5.1f}s  {len(items):>2} items, "
            f"{len(truncated):>2} truncated, {len(no_match):>2} no-match"
        )
        all_runs.append(
            {
                "run": i,
                "arm": arm,
                "elapsed_s": elapsed,
                "items": items,
                "truncated_count": len(truncated),
                "no_match_count": len(no_match),
            }
        )

    # Persist raw for later inspection.
    raw_path = run_dir / "raw.json"
    raw_path.write_text(
        json.dumps(
            {
                "jd_path": str(_JD_PATH),
                "control_instruction": CONTROL_INSTRUCTION,
                "treatment_instruction": TREATMENT_INSTRUCTION,
                "runs": all_runs,
            },
            indent=2,
            default=str,
        )
    )

    # Per-run summary
    print()
    print("=" * 78)
    print("PER-RUN SUMMARY")
    print("=" * 78)
    print(
        f"{'run':>3} {'arm':>10} {'items':>6} {'trunc':>6} {'no_match':>9}  "
        f"truncated rows"
    )
    for r in all_runs:
        trunc_labels = [
            f"[{it['section'].split('_')[0][:4]}/{it['idx']}] "
            f"{it['requirement'][:40]}"
            for it in r["items"]
            if it["status"] == "truncated"
        ]
        rows_str = " ; ".join(trunc_labels) if trunc_labels else "(none)"
        print(
            f"{r['run']:>3} {r['arm']:>10} {len(r['items']):>6} "
            f"{r['truncated_count']:>6} {r['no_match_count']:>9}  {rows_str}"
        )

    # Aggregate by arm
    print()
    print("AGGREGATE BY ARM")
    for arm in ("control", "treatment"):
        arm_runs = [r for r in all_runs if r["arm"] == arm]
        total_trunc = sum(r["truncated_count"] for r in arm_runs)
        total_items = sum(len(r["items"]) for r in arm_runs)
        mean_trunc = total_trunc / len(arm_runs) if arm_runs else 0
        rate = total_trunc / total_items * 100 if total_items else 0
        print(
            f"  {arm:>10}: {len(arm_runs)} runs, {total_items} items total, "
            f"{total_trunc} truncations ({rate:.1f}%), mean {mean_trunc:.1f} per run"
        )

    # Per-row breakdown: which specific JD lines get truncated, in which arm
    print()
    print("PER-ROW TRUNCATION FREQUENCY (only rows truncated at least once)")
    row_map: dict[str, dict[str, dict[str, int]]] = {}
    for r in all_runs:
        for it in r["items"]:
            key = it["matching_line"]
            if key is None:
                continue
            if key not in row_map:
                row_map[key] = {
                    "control": {"trunc": 0, "total": 0},
                    "treatment": {"trunc": 0, "total": 0},
                }
            row_map[key][r["arm"]]["total"] += 1
            if it["status"] == "truncated":
                row_map[key][r["arm"]]["trunc"] += 1

    sorted_rows = sorted(
        row_map.items(),
        key=lambda kv: -(kv[1]["control"]["trunc"] + kv[1]["treatment"]["trunc"]),
    )
    for line, arms in sorted_rows:
        c = arms["control"]
        t = arms["treatment"]
        if c["trunc"] == 0 and t["trunc"] == 0:
            continue
        print(
            f"  ctrl {c['trunc']}/{c['total']}  treat {t['trunc']}/{t['total']}  "
            f"{line[:90]}"
        )

    print()
    print("READ")
    control_total = sum(r["truncated_count"] for r in all_runs if r["arm"] == "control")
    treatment_total = sum(
        r["truncated_count"] for r in all_runs if r["arm"] == "treatment"
    )
    if treatment_total == 0 and control_total > 0:
        print(
            "  Zero truncations under treatment while control truncated -- the "
            "instruction was the cause. Prompt-side fix works."
        )
    elif treatment_total < control_total * 0.5:
        print(
            f"  Treatment reduced truncations significantly ({control_total} -> "
            f"{treatment_total}) but did not eliminate them. Instruction is "
            f"the dominant lever; residual truncation may need additional "
            f"prompt work."
        )
    elif treatment_total >= control_total * 0.5:
        print(
            f"  Truncations persist at similar rate ({control_total} control vs "
            f"{treatment_total} treatment). Summarization behavior, not the "
            f"prompt instruction. The instruction is not the lever."
        )
    else:
        print("  Inconclusive.")

    print()
    print(f"Raw results: {raw_path}")


if __name__ == "__main__":
    main()
