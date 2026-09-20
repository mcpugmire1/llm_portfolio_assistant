"""Probe -160: extraction variance across JD length and style.

Does extraction requirement-count variance scale with JD length or
authoring style? The -244 probe showed extraction produces 20 or 23
requirements on the demo JD (small spread). Earlier hand observations
on the AT&T JD showed 32/35/39 across three runs (wider spread). This
probe measures spread across six JDs of varying length and style,
five runs each.

No concurrency arms. Concurrency's inability to affect extraction is
STRUCTURAL, not a small-sample open question:
services.jd_assessor.extract_requirements is a single serial OpenAI
call, invoked BEFORE any fan-out concurrency patch takes effect
(_CONCURRENCY is used only inside _fan_out_assessments). Do not
re-run at concurrency=1 for an answer the design already gives.

Also carrying from -244 so both findings live in one place:
  - Verdicts are deterministic at ASSESSMENT_TEMPERATURE = 0.0 on
    the demo JD. Zero flips and zero evidence swaps across 5 runs
    per arm.
  - Evidence-swap zero under both concurrency arms means Pinecone
    returns identical candidates under load. The "upstream (Pinecone
    under load)" hypothesis the -244 arms were structured around is
    ruled out.

Two variance metrics reported per JD, because a single count would
conflate two different failure modes:

  intermittent_count: buckets present in fewer than N runs. Catches
    requirements the extractor dropped or added across runs. This is
    the count-instability signal.

  paraphrase_only_count: buckets present in every run but carrying
    more than one distinct full text. Catches the case where the
    extractor produces the same conceptual requirement N times with
    different qualifiers each time -- appearing stable in count while
    being exactly the text instability -160 is about.

Bucketing has two passes so the paraphrase-only signal isn't masked
by prefix/suffix drift landing in different first-6-words buckets:

  Pass 1 (primary key): first six words, lowercased.
  Pass 2 (fuzzy merge): pairwise difflib.SequenceMatcher.ratio() >=
    FUZZY_MERGE_THRESHOLD on any-variant comparison, union-find to
    coalesce. Catches leading-word variants ("Experience..." vs
    "Deep experience..."), connective swaps, punctuation-only diffs.

Variant sets store canonical form (lowercased, whitespace-collapsed,
trailing punctuation stripped) for uniqueness comparison, raw form
for display. This kills the case-only split observed in the AT&T
run (Engineering vs engineering counted as two variants).

Watch: canonicalization + fuzzy merge could collapse variants that
matter. Every bucket's report prints all raw variants that landed
in it AND the original first-6-words keys that fed into it, so a
suspicious merge is spot-checkable by hand. If a paraphrase count
looks surprising, inspect the bucket's variants and origin keys
before concluding the underlying variance shape has changed.

This probe skips the fan-out entirely -- the question is about
extraction, so running assess_requirement N times per run would just
add wall clock for no signal.

AT&T fixture caveat: probe_jd_att_principal.txt in the repo was
written during -159. Whether the 32/35/39 hand observations came
from THIS fixture or from a paste is not established.

Usage:

    python probe_160_extraction_variance.py

    or, with explicit JDs:

    python probe_160_extraction_variance.py path/to/jd.txt [path...]

Roughly 10s per extraction * 5 runs * N JDs. For the six defaults:
~5 minutes.
"""

import json
import string
import sys
import time
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services import jd_assessor

RUNS_PER_JD = 5
NORMALIZED_KEY_WORDS = 6
FUZZY_MERGE_THRESHOLD = 0.75

_BASE = Path(__file__).parent
_FIXTURES = _BASE / "tests" / "bdd" / "fixtures" / "jd_extraction"

DEFAULT_JD_PATHS = [
    _FIXTURES / "narrative_jd.txt",
    _FIXTURES / "hybrid_jd.txt",
    _FIXTURES / "structured_jd.txt",
    _FIXTURES / "mixed_jd.txt",
    _BASE / "data" / "demo_jd.txt",
    _BASE / "data" / "probe_jd_att_principal.txt",
]

# Per-run timestamped output directory. Every invocation writes to a
# fresh subdirectory so re-running the probe against a JD does not
# destroy the previous measurement. Per-JD files inside each run
# preserve each fixture's runs separately. September 2026: the previous
# single-file `probe_160_raw_results.json` overwrote the pre-split
# six-JD baseline the first time it was re-run against a single JD;
# the recovery for that baseline came from `probe_159_att_output/` and
# `probe_159a_output/`, not from this probe's own record.
OUTPUT_DIR = _BASE / "probe_160_output"


def _flatten_requirements(extraction: dict) -> list[dict]:
    """Same three-block flatten as run_assessment / the -245 submit
    path. Kept inline so the probe stays self-contained."""
    out: list[dict] = []
    for r in extraction.get("required_qualifications", []) or []:
        out.append({"text": r["requirement"], "category": "required"})
    for r in extraction.get("preferred_qualifications", []) or []:
        out.append({"text": r["requirement"], "category": "preferred"})
    for r in extraction.get("implicit_requirements", []) or []:
        out.append({"text": r["requirement"], "category": "required"})
    return out


def _normalized_req_key(requirement_text: str) -> str:
    """First N words, lowercased. Primary bucket key (pass 1 of
    bucketing). See _fuzzy_merge_buckets for pass 2."""
    tokens = requirement_text.lower().split()[:NORMALIZED_KEY_WORDS]
    return " ".join(tokens)


def _canonicalize(text: str) -> str:
    """Canonical form for uniqueness comparison inside a bucket's
    variant set. Lowercases, collapses whitespace, strips trailing
    punctuation. Kills case-only splits (Engineering vs engineering)
    and punctuation-only splits (trailing comma or period) that
    inflated variant counts in the pre-fix run."""
    return " ".join(text.lower().split()).rstrip(string.punctuation + " ")


def extract_once(jd_text: str) -> tuple[list[dict], float]:
    """Single extract call. Returns (all_requirements, elapsed_ms).
    No fan-out (assessment is not the subject of this probe)."""
    client = jd_assessor._get_openai_client()
    t = time.perf_counter()
    extraction = jd_assessor.extract_requirements(client, jd_text)
    elapsed_ms = (time.perf_counter() - t) * 1000.0
    return _flatten_requirements(extraction), elapsed_ms


def _fuzzy_merge_buckets(buckets: dict) -> dict:
    """Pass 2 bucketing. Merges buckets whose canonical variants
    are close under difflib.SequenceMatcher.ratio() at or above
    FUZZY_MERGE_THRESHOLD. Union-find over primary keys; the max
    ratio across every canonical-variant pair between two buckets
    is the decision signal, so a pair merges if ANY of their
    variants are close enough.

    Preserves merge provenance: every merged bucket carries the
    set of primary keys that fed into it, so a suspicious merge is
    inspectable in the report."""
    keys = list(buckets.keys())
    parent = {k: k for k in keys}

    def find(k: str) -> str:
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i, ka in enumerate(keys):
        variants_a = list(buckets[ka]["variants"].keys())
        for kb in keys[i + 1 :]:
            if find(ka) == find(kb):
                continue
            variants_b = list(buckets[kb]["variants"].keys())
            max_ratio = 0.0
            for va in variants_a:
                for vb in variants_b:
                    r = SequenceMatcher(None, va, vb).ratio()
                    if r > max_ratio:
                        max_ratio = r
                    if max_ratio >= FUZZY_MERGE_THRESHOLD:
                        break
                if max_ratio >= FUZZY_MERGE_THRESHOLD:
                    break
            if max_ratio >= FUZZY_MERGE_THRESHOLD:
                union(ka, kb)

    merged: dict = {}
    for k in keys:
        root = find(k)
        if root not in merged:
            merged[root] = {
                "variants": {},
                "present_in_runs": set(),
                "origin_primary_keys": set(),
            }
        merged[root]["variants"].update(buckets[k]["variants"])
        merged[root]["present_in_runs"].update(buckets[k]["present_in_runs"])
        merged[root]["origin_primary_keys"].add(k)
    return merged


def summarize_jd(jd_path: Path, runs: list[dict]) -> dict:
    """Print per-JD section: word count, req counts per run, spread,
    intermittent-bucket count, paraphrase-only bucket count with
    variants and merge provenance listed."""
    jd_text = jd_path.read_text(encoding="utf-8").strip()
    word_count = len(jd_text.split())
    counts = [r["req_count"] for r in runs]
    spread = max(counts) - min(counts)
    elapsed = [r["elapsed_ms"] for r in runs]

    print(f"\n=== {jd_path.name} ===")
    print(f"Word count: {word_count}")
    print(f"Requirement counts across {len(runs)} runs: {counts}")
    print(f"Spread (max - min): {spread}")
    print(
        f"Extract ms:  min={min(elapsed):>7.0f}  max={max(elapsed):>7.0f}  "
        f"(cache-affected; context only)"
    )

    # Pass 1: primary bucket by first-N-words. Variants stored as
    # {canonical: raw} dict so a case-only or trailing-punctuation
    # difference doesn't count as a new variant.
    primary_buckets: dict[str, dict] = defaultdict(
        lambda: {"variants": {}, "present_in_runs": set()}
    )
    for run_idx, run in enumerate(runs):
        run_primary_keys: set = set()
        for req in run["reqs"]:
            raw = req["text"]
            canonical = _canonicalize(raw)
            primary_key = _normalized_req_key(raw)
            b = primary_buckets[primary_key]
            if canonical not in b["variants"]:
                b["variants"][canonical] = raw
            b["present_in_runs"].add(run_idx)
            run_primary_keys.add(primary_key)

    # Pass 2: fuzzy merge across primary buckets.
    merged_buckets = _fuzzy_merge_buckets(primary_buckets)

    intermittent = []
    paraphrase_only = []
    for k, bucket in merged_buckets.items():
        in_runs = len(bucket["present_in_runs"])
        variants = list(bucket["variants"].values())
        origins = sorted(bucket["origin_primary_keys"])
        if in_runs < len(runs):
            intermittent.append((k, in_runs, variants, origins))
        elif len(variants) > 1:
            paraphrase_only.append((k, variants, origins))

    print(
        f"Intermittent buckets (present in fewer than {len(runs)} runs): "
        f"{len(intermittent)}"
    )
    if intermittent:
        for k, in_runs, variants, origins in sorted(intermittent, key=lambda t: -t[1]):
            merge_note = ""
            if len(origins) > 1:
                chain_tag = " [CHAIN?]" if len(origins) >= 4 else ""
                merge_note = f"  <- MERGED from {len(origins)} origins{chain_tag}"
            print(f"  {in_runs}/{len(runs)}  bucket: {k!r}{merge_note}")
            if len(origins) > 1:
                for o in origins:
                    print(f"      origin: {o!r}")
            if len(variants) > 1:
                for v in variants:
                    print(f"      variant: {v[:100]}")

    print(
        f"Paraphrase-only buckets (present in every run, >1 distinct "
        f"variant): {len(paraphrase_only)}"
    )
    if paraphrase_only:
        for k, variants, origins in paraphrase_only:
            merge_note = ""
            if len(origins) > 1:
                chain_tag = " [CHAIN?]" if len(origins) >= 4 else ""
                merge_note = f"  <- MERGED from {len(origins)} origins{chain_tag}"
            print(f"  {len(variants)} variants  bucket: {k!r}{merge_note}")
            if len(origins) > 1:
                for o in origins:
                    print(f"      origin: {o!r}")
            for v in variants:
                print(f"      variant: {v[:100]}")

    return {
        "jd_name": jd_path.name,
        "word_count": word_count,
        "counts": counts,
        "spread": spread,
        "intermittent_count": len(intermittent),
        "paraphrase_only_count": len(paraphrase_only),
    }


def main() -> None:
    if len(sys.argv) > 1:
        jd_paths = [Path(p) for p in sys.argv[1:]]
    else:
        jd_paths = DEFAULT_JD_PATHS

    for p in jd_paths:
        if not p.exists():
            print(f"WARN: {p} not found, skipping")
    jd_paths = [p for p in jd_paths if p.exists()]

    print(f"Running {RUNS_PER_JD} extractions per JD across " f"{len(jd_paths)} JDs")
    print(
        f"Bucketing: pass 1 = first {NORMALIZED_KEY_WORDS} words lowercased; "
        f"pass 2 = fuzzy merge at ratio >= {FUZZY_MERGE_THRESHOLD}"
    )

    all_results: dict[str, dict] = {}
    for jd_path in jd_paths:
        print("\n" + "=" * 60)
        print(f"JD: {jd_path.name}")
        print("=" * 60)
        jd_text = jd_path.read_text(encoding="utf-8").strip()
        runs = []
        for i in range(RUNS_PER_JD):
            print(f"  run {i + 1}/{RUNS_PER_JD}...", end=" ", flush=True)
            reqs, elapsed_ms = extract_once(jd_text)
            runs.append(
                {
                    "iteration": i + 1,
                    "req_count": len(reqs),
                    "elapsed_ms": elapsed_ms,
                    "reqs": reqs,
                }
            )
            print(f"{len(reqs)} reqs, {elapsed_ms:.0f}ms")
        all_results[jd_path.name] = {"path": str(jd_path), "runs": runs}

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    stats = []
    for jd_path in jd_paths:
        runs = all_results[jd_path.name]["runs"]
        stats.append(summarize_jd(jd_path, runs))

    print("\n" + "=" * 60)
    print("CROSS-JD COMPARISON (sorted by word count)")
    print("=" * 60)
    stats_sorted = sorted(stats, key=lambda s: s["word_count"])
    print(
        f"{'JD':<38}  {'words':>6}  {'counts':<25}  "
        f"{'spread':>7}  {'intermit':>9}  {'paraph':>7}"
    )
    print("-" * 100)
    for s in stats_sorted:
        counts_str = str(s["counts"])
        print(
            f"{s['jd_name']:<38}  {s['word_count']:>6}  "
            f"{counts_str:<25}  {s['spread']:>7}  "
            f"{s['intermittent_count']:>9}  {s['paraphrase_only_count']:>7}"
        )

    print()
    print("Watch: canonicalization (lowercase + strip trailing punctuation)")
    print("plus fuzzy merge at 0.75 can collapse variants that matter. Every")
    print("bucket that came from a merge is tagged '<- MERGED from N' with")
    print("its origin primary keys listed, so a suspicious merge is spot-")
    print("checkable. If paraphrase counts changed unexpectedly from the")
    print("previous run, inspect those buckets before drawing conclusions.")

    run_timestamp = time.strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_DIR / run_timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    for jd_name, jd_data in all_results.items():
        out_path = run_dir / f"{Path(jd_name).stem}.json"
        out_path.write_text(json.dumps(jd_data, indent=2, default=str))
    print(f"\nRaw results written to: {run_dir}/")


if __name__ == "__main__":
    main()
