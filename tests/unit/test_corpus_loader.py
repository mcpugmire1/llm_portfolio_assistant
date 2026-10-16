"""Unit tests for the story id rule shared by both loaders (MATTGPT-202).

app.py load_star_stories() and utils.corpus_loader.load_stories() keep a row
only when story_id_or_none() returns an id. The rule is the one both loaders
copied before the helper existed: skip None, "" and 0 (and values equal to 0,
like 0.0 and False); otherwise keep str(id).strip().
"""

import pytest

from utils.corpus_loader import story_id_or_none


@pytest.mark.parametrize("raw", [None, "", 0, 0.0, False])
def test_rows_without_a_usable_id_are_skipped(raw):
    assert story_id_or_none(raw) is None


@pytest.mark.parametrize(
    ("raw", "kept"),
    [
        ("abc|client", "abc|client"),
        (" x ", "x"),
        (7, "7"),
        # Whitespace-only ids pass the rule and strip to "" (both loaders do this today).
        ("  ", ""),
    ],
)
def test_kept_ids_are_stripped_strings(raw, kept):
    assert story_id_or_none(raw) == kept
