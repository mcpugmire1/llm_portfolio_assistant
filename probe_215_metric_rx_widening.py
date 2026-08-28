"""MATTGPT-215 discovery: verify METRIC_RX widening is a strict superset.

Backs the "35 strings improve, zero regressions" claim carried in the
utils/formatting.py METRIC_RX comment. Runs both the pre-215 pattern (kept
inline here as the OLD variant) and the post-215 widened pattern against
every Performance / Result bullet in the corpus that contains a "$" or a
decimal percentage, plus a handful of hand-picked cases the ticket names.

For each string, prints DIFF lines where the two regexes disagree. The
widened form is a strict superset: any OLD match remains under NEW; NEW
adds captures for decimal precision ("99.9%" not "9%") and currency with
K/M/B unit + optional "+" ("$100M+" not empty).

Re-run when METRIC_RX changes again to confirm the direction is still
superset (or to catch a regression). No API calls; pure regex.
"""

import json
import re

METRIC_RX_OLD = re.compile(
    r"(\b\d{1,3}\s?%|\$\s?\d[\d,\.]*\b|\b\d+x\b|\b\d+(?:\.\d+)?\s?(pts|pp|bps)\b)",
    re.I,
)
METRIC_RX_NEW = re.compile(
    r"(\b\d{1,3}(?:\.\d+)?\s?%|\$\s?\d[\d,\.]*[KMB]?[+]?|\b\d+x\b|\b\d+(?:\.\d+)?\s?(pts|pp|bps)\b)",
    re.I,
)


def main() -> None:
    targets: list[str] = []
    with open("echo_star_stories_nlp.jsonl", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            for field in ("Performance", "Result"):
                for item in rec.get(field) or []:
                    if not item:
                        continue
                    if "$" in item or re.search(r"\d+\.\d+\s?%", item):
                        targets.append(item)

    targets.extend(
        [
            "Achieved 99.9% uptime",
            "$100M+ repeat business",
            "$5.2M platform savings",
            "$100 million contract",
            "$3M contract extension",
            "$8.5M Fiserv program",
            "$500K in penalties",
            "generated $1B+ annual revenue",
        ]
    )

    unique = sorted(set(targets))
    print(f"{len(unique)} unique strings scanned\n")

    changed = 0
    regressions = 0
    for s in unique:
        old_matches = list(METRIC_RX_OLD.finditer(s))
        new_matches = list(METRIC_RX_NEW.finditer(s))
        old_tokens = [m.group(0) for m in old_matches]
        new_tokens = [m.group(0) for m in new_matches]
        if old_tokens == new_tokens:
            continue
        changed += 1

        # Superset check on spans, not string equality. Every OLD match's
        # [start, end] span must be fully contained within SOME NEW match's
        # span. Precision improvements (OLD "9%" widened to NEW "99.9%" at
        # an overlapping position) count as containment, not regression.
        new_spans = [(nm.start(), nm.end()) for nm in new_matches]
        regression = any(
            not any(ns <= om.start() and ne >= om.end() for ns, ne in new_spans)
            for om in old_matches
        )

        if regression:
            regressions += 1
            print(f"  REGRESSION: old={old_tokens} -> new={new_tokens}")
        else:
            print(f"  DIFF: old={old_tokens} -> new={new_tokens}")
        print(f"    {s[:100]!r}")

    print(
        f"\n{changed} strings match differently under NEW; "
        f"{regressions} true regressions (OLD span not covered by any NEW match)"
    )


if __name__ == "__main__":
    main()
