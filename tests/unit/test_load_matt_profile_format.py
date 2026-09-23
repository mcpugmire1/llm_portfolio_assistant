"""MATTGPT-250 Red: load_matt_profile() and build_assessment_prompt() format.

Class D (line-based, one per education entry): each entry renders on
  its own newline-separated line carrying its institution and its own
  note marker, and containing no other entry's institution or marker.
  Anchors on institution names, not degree text -- the master's
  equivalence note text contains "Master's degree", so degree-text
  anchoring would false-pass at Red.
  D1: master's entry line (American InterContinental University)
  D2: UGA graduate coursework entry line (University of Georgia)
  D3: Queens BA entry line (Queens University of Charlotte)
  D4: languages field renders, both entries verbatim.

Class H (Role Match transport): build_assessment_prompt() output
  contains "English (native)" and "French (B2, self-assessed)". The
  Coca-Cola miss that put languages in scope was a Role Match failure,
  so the Role Match transport is what the test must cover -- not the
  loader in isolation.

Both classes use their own controlled fixtures with `languages` and
`note` keys present -- open() is patched via unittest.mock.mock_open so
the loader reads a fixture dict rather than data/matt_profile.json.
The profile_grounding BDD suite (whose fixture has neither key)
verifies loader tolerance separately at Green.
"""

import json
from unittest.mock import mock_open, patch

import pytest

from services.jd_assessor import build_assessment_prompt, load_matt_profile

# ---------------------------------------------------------------------------
# Fixture: profile dict with languages and per-entry notes present
# ---------------------------------------------------------------------------


_INSTITUTIONS = {
    "masters": "American InterContinental University",
    "uga": "University of Georgia",
    "queens": "Queens University of Charlotte",
}

_MARKERS = {
    "masters": "MARKER_MASTERS_NOTE",
    "uga": "MARKER_UGA_NOTE",
    "queens": "MARKER_QUEENS_NOTE",
}


def _fixture_profile() -> dict:
    """Fixture profile with languages field and distinctive markers
    on every note. Note strings intentionally do NOT contain any
    institution name from another entry, so a test that asserts
    "no other institution in this line" only fires on genuine
    cross-attachment, not on marker text leaking a foreign institution."""
    return {
        "name": "Matt Pugmire",
        "career_summary": "irrelevant to loader format",
        "education": [
            {
                "degree": "Master's degree, Information Technology",
                "institution": _INSTITUTIONS["masters"],
                "note": (
                    f"{_MARKERS['masters']} Master's degree in Information "
                    f"Technology satisfies requirements for 'Bachelor's "
                    f"degree in Computer Science or related field'."
                ),
            },
            {
                "degree": "Graduate coursework, Romance Languages (Linguistics)",
                "institution": _INSTITUTIONS["uga"],
                "note": (
                    f"{_MARKERS['uga']} Teaching assistant; taught French "
                    f"101, 102, and 103."
                ),
            },
            {
                "degree": "BA, French Language and Literature",
                "institution": _INSTITUTIONS["queens"],
                "note": (
                    f"{_MARKERS['queens']} Included a year abroad at "
                    f"Universite Paul Valery, Montpellier, France."
                ),
            },
        ],
        "certifications": [
            "SAFe 4 Certified Agilist",
            "Microsoft Certified Professional (MCP) - Oracle",
            "AWS Launchpad Champion",
            "AWS Certified Solutions Architect - Associate",
        ],
        "languages": [
            "English (native)",
            "French (B2, self-assessed)",
        ],
        "logistics": {
            "location": {"value": "Atlanta, GA", "subline": ""},
        },
    }


def _patched_open():
    """Returns a context manager patching builtins.open with the fixture
    profile serialized to JSON. json.load(f) calls f.read(); mock_open's
    read() returns the read_data string, so no separate json.load patch
    is needed."""
    fixture_json = json.dumps(_fixture_profile())
    return patch("builtins.open", mock_open(read_data=fixture_json))


@pytest.fixture
def loader_output():
    with _patched_open():
        return load_matt_profile()


@pytest.fixture
def assessment_prompt_output():
    with _patched_open():
        return build_assessment_prompt()


def _line_containing(text: str, institution: str) -> str | None:
    """Return the first newline-separated line that contains the given
    institution string. Splitting only on newlines: Green must render
    each entry on its own line."""
    for line in text.splitlines():
        if institution in line:
            return line
    return None


def _entry_line_test(loader_output: str, key: str) -> None:
    """Shared assertion body for D1-D3. Fails at Red because today's
    loader produces one flat string with no newlines -- splitlines()
    returns exactly one unit containing every institution and every
    marker, which fails the "no other institution/marker" checks."""
    institution = _INSTITUTIONS[key]
    marker = _MARKERS[key]
    line = _line_containing(loader_output, institution)
    assert line is not None, (
        f"no newline-separated line contains institution {institution!r}. "
        f"Loader output: {loader_output!r}"
    )
    assert marker in line, (
        f"line for {institution!r} does not contain its own marker "
        f"{marker!r}. Line: {line!r}. Loader output: {loader_output!r}"
    )
    for other_key in _INSTITUTIONS:
        if other_key == key:
            continue
        other_institution = _INSTITUTIONS[other_key]
        assert other_institution not in line, (
            f"line for {institution!r} also contains foreign institution "
            f"{other_institution!r}. Line: {line!r}. Loader output: "
            f"{loader_output!r}"
        )
        other_marker = _MARKERS[other_key]
        assert other_marker not in line, (
            f"line for {institution!r} also contains foreign marker "
            f"{other_marker!r}. Line: {line!r}. Loader output: "
            f"{loader_output!r}"
        )


# ---------------------------------------------------------------------------
# Class D: per-entry line contents
# ---------------------------------------------------------------------------


class TestLoaderPerEntryLines:
    def test_masters_entry_renders_on_own_line_with_own_note(self, loader_output):
        _entry_line_test(loader_output, "masters")

    def test_uga_entry_renders_on_own_line_with_own_note(self, loader_output):
        _entry_line_test(loader_output, "uga")

    def test_queens_entry_renders_on_own_line_with_own_note(self, loader_output):
        _entry_line_test(loader_output, "queens")

    def test_languages_field_renders_both_entries_verbatim(self, loader_output):
        assert "English (native)" in loader_output, (
            f"'English (native)' missing from loader output. "
            f"Full output: {loader_output!r}"
        )
        assert "French (B2, self-assessed)" in loader_output, (
            f"'French (B2, self-assessed)' missing from loader output. "
            f"Full output: {loader_output!r}"
        )


# ---------------------------------------------------------------------------
# Class H: languages reach Role Match's build_assessment_prompt() output
# ---------------------------------------------------------------------------


class TestAssessmentPromptContainsLanguages:
    """The Coca-Cola miss that put languages in scope was a Role Match
    failure: the assessor had nothing to ground English fluency against
    because the field was absent. This test asserts languages travel
    into build_assessment_prompt()'s output, which is what the assessor
    reads. A Green that adds languages only to the loader but breaks
    the template composition would fail here."""

    def test_assessment_prompt_contains_both_language_entries_verbatim(
        self, assessment_prompt_output
    ):
        assert "English (native)" in assessment_prompt_output, (
            f"'English (native)' missing from build_assessment_prompt() "
            f"output. This is the Role Match transport path -- a Green "
            f"that adds languages to the loader but drops them from the "
            f"template composition fails here. "
            f"Head of prompt: {assessment_prompt_output[:800]!r}"
        )
        assert "French (B2, self-assessed)" in assessment_prompt_output, (
            f"'French (B2, self-assessed)' missing from "
            f"build_assessment_prompt() output. "
            f"Head of prompt: {assessment_prompt_output[:800]!r}"
        )
