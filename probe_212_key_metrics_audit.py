"""MATTGPT-212 discovery: audit Key Metrics parse heuristic against the corpus.

Mirrors ui/components/story_detail.py:641-654 exactly so the output shows
what actually reaches the sidebar today. For each story with Performance
data, prints every entry that trips the trigger, the extracted value, and
the label the sidebar would render.

The audit produces two lists: entries that read as plausible metrics
(number + unit at the head of the string), and entries that read as
false positives (trigger fired on a bare "x" or "month" letter/word inside
an unrelated phrase). The plausibility check here is a rough heuristic to
group the output; the final call on which are bogus is manual.

Read from data/echo_star_stories_nlp.jsonl so post-enrichment content is
scanned (Performance is preserved from the Excel master through ingest).
"""

import json
import re
from pathlib import Path

CORPUS = Path("data/echo_star_stories_nlp.jsonl")
FALLBACK_CORPUS = Path("echo_star_stories_nlp.jsonl")

VALUE_REGEX = re.compile(r"(\d+[%xX]?|\d+\+?)")
LABEL_CAP = 50


def trigger_fires(perf: str) -> bool:
    """Exact copy of the sidebar's trigger clause."""
    return bool(
        perf
        and (
            "%" in perf
            or "x" in perf.lower()
            or "month" in perf.lower()
            or "week" in perf.lower()
        )
    )


PLAUSIBLE_UNIT_HEAD = re.compile(
    r"^\s*\d+\s*(%|x\b|X\b|[+]?\s*(month|week|day|year)s?\b)", re.IGNORECASE
)


def plausible_metric(perf: str) -> bool:
    """Rough grouping: does the string look like a real metric (number + unit)?

    True: "70% reduction", "4x throughput", "6 months to production"
    False: "3 canonical business objects normalizing multiple trading
           exchange formats" (triggers on the 'x' in 'exchange')
    """
    return bool(PLAUSIBLE_UNIT_HEAD.match(perf.strip()))


def main():
    corpus_path = CORPUS if CORPUS.exists() else FALLBACK_CORPUS
    if not corpus_path.exists():
        raise SystemExit(f"Corpus not found at {CORPUS} or {FALLBACK_CORPUS}")

    plausible = []
    suspect = []

    with corpus_path.open(encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            story_id = rec.get("id", "?")
            title = rec.get("Title", "?")
            performance = rec.get("Performance") or []
            for perf in performance:
                if not trigger_fires(perf):
                    continue
                match = VALUE_REGEX.search(perf)
                if not match:
                    continue
                value = match.group(1)
                label = perf[:LABEL_CAP]
                entry = (story_id, title, perf, value, label)
                (plausible if plausible_metric(perf) else suspect).append(entry)

    print("=" * 78)
    print(f"SUSPECT ({len(suspect)}) — trigger fires but no leading number+unit")
    print("=" * 78)
    for sid, title, perf, value, label in suspect:
        print(f"\n[{sid}]")
        print(f"  Title:  {title[:70]}")
        print(f"  Source: {perf}")
        print(f"  Renders: value='{value}'  label='{label}'  (uppercased at render)")

    print("\n" + "=" * 78)
    print(f"PLAUSIBLE ({len(plausible)}) — number + unit at head of string")
    print("=" * 78)
    for sid, _title, perf, value, label in plausible[:20]:
        print(f"\n[{sid}]")
        print(f"  Source: {perf}")
        print(f"  Renders: value='{value}'  label='{label}'")
    if len(plausible) > 20:
        print(f"\n... {len(plausible) - 20} more plausible entries not shown")

    print("\n" + "=" * 78)
    print(
        f"SUMMARY: {len(suspect)} suspect / {len(plausible)} plausible "
        f"across the corpus"
    )
    print("=" * 78)


if __name__ == "__main__":
    main()
