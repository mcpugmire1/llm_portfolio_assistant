"""MATTGPT-302: the required extraction's Populate rule drops its parenthetical.

On gpt-5.6-terra at low effort, the rule "Populate `key_responsibilities`
with the JD's stated responsibilities (what the role does, not what the
candidate must have)" left a responsibilities-only JD with no required
rows: hybrid_jd (tests/bdd/fixtures/jd_extraction/), which has no
qualifications section, got 0 required in 4 of 6 runs and once 0 rows in
all (green_20261025_073015, green_isolate_20261025_073855). gpt-4o got 15
required in each of its runs.

With the parenthetical removed and the field kept, hybrid_jd got 10 to 14
required plus implicit over 9 runs, never 0, with the other nine test JDs
inside 25% of gpt-4o's count wherever gpt-4o extracts 5 or more
(paren_20261025_091309, gpt-4o counts from nokr_20261025_081301). Required
was 0 in one of the 9, with all 10 rows in implicit.

key_responsibilities stays: it is ADR 016's planned responsibilities output.
Removing the field also gave a steady count (12 required in each of 9
runs, nokr_20261025_081301 and paren_20261025_091309).
"""

from services import jd_assessor

PARENTHETICAL = "(what the role does, not what the candidate must have)"
POPULATE_RULE = (
    "- Populate `key_responsibilities` with the JD's stated responsibilities. "
    "One item per distinct responsibility. Empty list if none are stated."
)


def test_the_populate_rule_has_no_parenthetical():
    assert PARENTHETICAL not in jd_assessor._REQUIRED_EXTRACTION_PROMPT


def test_the_populate_rule_is_otherwise_unchanged():
    assert jd_assessor._REQUIRED_EXTRACTION_PROMPT.count(POPULATE_RULE) == 1


def test_the_required_schema_keeps_key_responsibilities():
    assert (
        '"key_responsibilities": ["string"]' in jd_assessor._REQUIRED_EXTRACTION_PROMPT
    )
