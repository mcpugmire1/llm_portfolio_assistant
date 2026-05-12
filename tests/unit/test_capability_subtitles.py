"""
Unit tests for CAPABILITY_SUBTITLES dict in config/constants.py.

CAPABILITY_SUBTITLES is the editorial-description layer for Solution/Offering
values surfaced on landing pages (Banking, Cross-Industry). It mirrors the
ERA_SUBTITLES pattern in ui/components/timeline_view.py — short descriptive
phrase per category, falls through to empty string on miss.

The dict has one hard invariant enforced by these tests: every key MUST
reference a Solution/Offering value that exists in the current story data.
If a key drifts (renamed upstream in the master data, or category removed),
this test fails CI and signals the maintainer to either rename the key or
remove it.

Why this matters: today's MATTGPT-060 / Card 3 regression was caused by
exactly this kind of drift — a hardcoded string didn't match a real data
value. The hardcoded string silently sanitized to "All" instead of failing
loudly. This test prevents the same shape of bug for CAPABILITY_SUBTITLES.
"""

import json
from pathlib import Path


def _load_solution_offerings() -> set[str]:
    """Read all Solution/Offering values from the current story corpus."""
    stories_path = Path(__file__).parent.parent.parent / "echo_star_stories_nlp.jsonl"
    offerings: set[str] = set()
    with stories_path.open() as f:
        for line in f:
            try:
                story = json.loads(line)
                value = story.get("Solution / Offering")
                if value:
                    offerings.add(value)
            except json.JSONDecodeError:
                continue
    return offerings


class TestCapabilitySubtitles:
    """CAPABILITY_SUBTITLES integrity contract."""

    def test_every_key_references_real_solution_offering(self):
        """Every dict key must exist in the data's Solution/Offering values.

        If this fails: a key in CAPABILITY_SUBTITLES doesn't match anything
        in the current story corpus. Either:
        - The category was renamed upstream → rename the dict key to match
        - The category was removed entirely → delete the dict entry
        """
        from config.constants import CAPABILITY_SUBTITLES

        offerings = _load_solution_offerings()
        stale_keys = sorted(set(CAPABILITY_SUBTITLES) - offerings)

        assert not stale_keys, (
            f"CAPABILITY_SUBTITLES contains {len(stale_keys)} key(s) that no "
            f"longer reference any Solution/Offering value in the data: "
            f"{stale_keys}. Either rename to match the current data value or "
            f"remove the entry. See test docstring for details."
        )

    def test_all_values_are_non_empty_strings(self):
        """Subtitle values must be non-empty strings to be useful."""
        from config.constants import CAPABILITY_SUBTITLES

        empty_or_invalid = [
            k
            for k, v in CAPABILITY_SUBTITLES.items()
            if not isinstance(v, str) or not v.strip()
        ]
        assert not empty_or_invalid, (
            f"CAPABILITY_SUBTITLES has entries with empty/invalid subtitle "
            f"values: {empty_or_invalid}. Either supply a real description or "
            f"remove the entry (fallback to empty string is automatic for "
            f"missing keys, no need to explicitly map to empty string)."
        )
