"""MATTGPT-238: verify below-SOFT router queries land on disk.

Acceptance evidence for -238. The ticket's acceptance criterion is
that a real query known to score below SOFT_ACCEPT appears in
data/router_low_confidence.csv with the correct row values.

Pre-implementation run (Red): file missing or no matching row.
Post-implementation run (Green): row present with expected columns.

Uses "how much are bananas?" as the trigger. Probe evidence from
MATTGPT-234 recorded this at 0.186 -- well below SOFT_ACCEPT (0.40).
"""

import csv
import sys
from pathlib import Path
from unittest.mock import MagicMock

_st = MagicMock()
_st.session_state = {}
sys.modules["streamlit"] = _st

from config.constants import SOFT_ACCEPT  # noqa: E402
from services.semantic_router import is_portfolio_query_semantic  # noqa: E402

TRIGGER_QUERY = "how much are bananas?"
LOG_PATH = Path("data/router_low_confidence.csv")


def main() -> None:
    print(f"SOFT_ACCEPT = {SOFT_ACCEPT}")
    print(f"Trigger query: {TRIGGER_QUERY!r}")

    _, score, _, family = is_portfolio_query_semantic(TRIGGER_QUERY)
    print(f"Router: score={score:.3f}  family={family}")
    if score >= SOFT_ACCEPT:
        print(
            f"  ERROR: trigger query no longer scores below SOFT_ACCEPT "
            f"({score:.3f} >= {SOFT_ACCEPT}). Choose a different trigger."
        )
        return

    print(f"\nChecking {LOG_PATH}...")
    if not LOG_PATH.exists():
        print("  FAIL: file does not exist. Below-SOFT logging not implemented.")
        return

    with LOG_PATH.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    matching = [r for r in rows if r.get("query") == TRIGGER_QUERY]
    print(f"  File exists. Total rows: {len(rows)}. Matching rows: {len(matching)}")
    if not matching:
        print("  FAIL: no row found for trigger query. Writer did not fire.")
        return

    latest = matching[-1]
    print("  PASS: latest matching row:")
    for k, v in latest.items():
        print(f"    {k}: {v}")


if __name__ == "__main__":
    main()
