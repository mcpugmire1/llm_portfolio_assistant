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
            {"name": "SAFe 4 Certified Agilist", "issued": 2017, "expired": True},
            {"name": "AWS Certified Solutions Architect - Associate", "issued": 2020},
        ],
        "languages": [
            {"language": "English", "level": "native"},
            {"language": "French", "level": "B2, self-assessed"},
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

    def test_real_matt_profile_json_contains_updated_certifications_verbatim(self):
        """Reads the real data/matt_profile.json (no mock_open). All four
        certification strings from BACKLOG.md::MATTGPT-250 (9d5f575) must
        appear verbatim in load_matt_profile() output -- expiry dates
        included, none current. Guards against a data-file edit that
        drops or paraphrases any of the four entries."""
        real_output = load_matt_profile()
        expected = [
            "AWS Certified Solutions Architect - Associate (issued 2020, expired 2023)",
            "AWS Certified Cloud Practitioner (issued 2019, expired 2023)",
            "SAFe 4 Certified Agilist (issued 2017, expired)",
            (
                "Oracle 8i DBA exams passed (OCP track): SQL and PL/SQL, "
                "Architecture and Administration, Backup and Recovery (2002)"
            ),
        ]
        missing = [c for c in expected if c not in real_output]
        assert not missing, (
            f"real matt_profile.json missing verbatim certifications: "
            f"{missing!r}. Full loader output: {real_output!r}"
        )

    def test_real_matt_profile_json_masters_note_is_neutral(self):
        """Reads the real data/matt_profile.json (no mock_open). The AIU
        note is a neutral fact both Role Match and Ask Agy read, replacing
        the JD-requirement wording (Sept 25, 2026)."""
        real_output = load_matt_profile()
        neutral_note = (
            "Information Technology is a recognized Computer Science-related "
            "discipline, and a Master's degree exceeds a Bachelor's."
        )
        assert (
            neutral_note in real_output
        ), f"neutral AIU note missing. Full loader output: {real_output!r}"
        assert (
            "satisfies requirements" not in real_output
        ), f"old requirement wording still present. Full loader output: {real_output!r}"


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


# ---------------------------------------------------------------------------
# Class L: Location & Availability in the shared loader (MATTGPT-250 step 2)
# ---------------------------------------------------------------------------
# The profile's JSON key for this group is "logistics"; the visitor-facing
# name (Role Match header) is "Location & Availability". The loader renders
# one line per populated field, "Label: value. subline.", in the order of
# config.constants.PROFILE_LOCATION_AVAILABILITY_FIELDS, which Role Match's
# _iter_location_cells() also reads.

_LOC_FIXTURE = {
    "location": {"value": "Atlanta, GA", "subline": "Open to relocation and travel"},
    "work_model": {"value": "In-office preferred", "subline": "Hybrid or remote fine"},
    "availability": {"value": "Immediate", "subline": ""},
    "authorization": {"value": "", "subline": "No sponsorship needed"},
}
_LOC_EXPECTED_LINES = [
    "Location: Atlanta, GA. Open to relocation and travel.",
    "Work model: In-office preferred. Hybrid or remote fine.",
    "Availability: Immediate.",
]


def _loc_patched_open():
    profile = _fixture_profile()
    profile["logistics"] = _LOC_FIXTURE
    return patch("builtins.open", mock_open(read_data=json.dumps(profile)))


class TestLoaderLocationAvailability:
    def test_l1_populated_fields_render_one_line_each_in_order(self):
        with _loc_patched_open():
            output = load_matt_profile()
        lines = output.splitlines()
        missing = [e for e in _LOC_EXPECTED_LINES if e not in lines]
        assert not missing, f"missing lines {missing!r}. Output: {output!r}"
        positions = [lines.index(e) for e in _LOC_EXPECTED_LINES]
        assert positions == sorted(positions), f"field order wrong: {output!r}"

    def test_l2_empty_value_field_omitted(self):
        with _loc_patched_open():
            output = load_matt_profile()
        assert "Authorization:" not in output, (
            f"field with empty value must be omitted (omit-cleanly, as in "
            f"_iter_location_cells). Output: {output!r}"
        )

    def test_l3_real_file_contains_location_and_availability(self):
        real_output = load_matt_profile()
        for expected in (
            "Location: Atlanta, GA. Open to relocation and travel.",
            "Availability: Immediate. No notice period.",
        ):
            assert (
                expected in real_output
            ), f"{expected!r} missing from real loader output: {real_output!r}"

    def test_l4_assessment_prompt_contains_location_and_availability(self):
        with _loc_patched_open():
            prompt = build_assessment_prompt()
        for expected in (_LOC_EXPECTED_LINES[0], _LOC_EXPECTED_LINES[2]):
            assert (
                expected in prompt
            ), f"{expected!r} missing from build_assessment_prompt() output"

    def test_l5_role_match_and_loader_share_one_field_list(self):
        from config import constants
        from services import jd_assessor

        shared = getattr(constants, "PROFILE_LOCATION_AVAILABILITY_FIELDS", None)
        assert (
            shared is not None
        ), "config.constants.PROFILE_LOCATION_AVAILABILITY_FIELDS not defined"
        assert (
            getattr(jd_assessor, "PROFILE_LOCATION_AVAILABILITY_FIELDS", None) is shared
        ), "jd_assessor does not read the shared field list"
        # Fact card Red: the cell iterator moved to services.matt_profile,
        # shared by Role Match's block and the Ask Agy fact card.
        from services import matt_profile

        assert (
            getattr(matt_profile, "PROFILE_LOCATION_AVAILABILITY_FIELDS", None)
            is shared
        ), "services.matt_profile does not read the shared field list"

    def test_l6_role_match_defines_no_own_location_helpers(self):
        from ui.pages import role_match

        for own_helper in (
            "_iter_location_cells",
            "_load_matt_profile_dict",
            "_LOCATION_CELL_ORDER",
        ):
            assert not hasattr(
                role_match, own_helper
            ), f"role_match still defines its own {own_helper}"


# ---------------------------------------------------------------------------
# Class C: structured certifications and languages (fact card, mock #4a)
# ---------------------------------------------------------------------------
# data/matt_profile.json stores certifications as {name, issued, expired}
# and languages as {language, level}. load_matt_profile() rebuilds today's
# sentence strings from those fields; the real-file certification test
# above is the round-trip proof that Role Match and Agy see the same text.

_EXPECTED_CERTS = [
    {
        "name": "AWS Certified Solutions Architect - Associate",
        "issued": 2020,
        "expired": 2023,
    },
    {"name": "AWS Certified Cloud Practitioner", "issued": 2019, "expired": 2023},
    {"name": "SAFe 4 Certified Agilist", "issued": 2017, "expired": True},
    {
        "name": (
            "Oracle 8i DBA exams passed (OCP track): SQL and PL/SQL, "
            "Architecture and Administration, Backup and Recovery"
        ),
        "issued": 2002,
    },
]
_EXPECTED_LANGUAGES = [
    {"language": "English", "level": "native"},
    {"language": "French", "level": "B2, self-assessed"},
]
_CERT_SENTENCES = [
    "AWS Certified Solutions Architect - Associate (issued 2020, expired 2023)",
    "AWS Certified Cloud Practitioner (issued 2019, expired 2023)",
    "SAFe 4 Certified Agilist (issued 2017, expired)",
    (
        "Oracle 8i DBA exams passed (OCP track): SQL and PL/SQL, "
        "Architecture and Administration, Backup and Recovery (2002)"
    ),
]
_CERT_DATE_LABELS = ["2020–2023", "2019–2023", "2017", "2002"]


class TestStructuredProfileFacts:
    def test_c1_real_file_stores_structured_certifications_and_languages(self):
        from pathlib import Path

        path = Path(__file__).resolve().parents[2] / "data" / "matt_profile.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["certifications"] == _EXPECTED_CERTS, data["certifications"]
        assert data["languages"] == _EXPECTED_LANGUAGES, data["languages"]

    @pytest.mark.parametrize(
        "entry, sentence", list(zip(_EXPECTED_CERTS, _CERT_SENTENCES, strict=True))
    )
    def test_c2_certification_sentence_round_trip(self, entry, sentence):
        from services import matt_profile

        assert matt_profile.certification_sentence(entry) == sentence

    @pytest.mark.parametrize(
        "entry, label", list(zip(_EXPECTED_CERTS, _CERT_DATE_LABELS, strict=True))
    )
    def test_c3_certification_date_label(self, entry, label):
        from services import matt_profile

        assert matt_profile.cert_date_label(entry) == label

    def test_c4_real_file_languages_round_trip(self):
        real_output = load_matt_profile()
        assert (
            "Languages: English (native), French (B2, self-assessed)." in real_output
        ), real_output
