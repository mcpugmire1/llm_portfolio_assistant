"""MATTGPT-354: the work model reads "In-office preferred" / "Hybrid fine"
everywhere, from data/matt_profile.json.

Role Match (panel, Share, Export) and Ask Agy (fact card, profile facts)
already read the profile; About Matt's "Work mode" tile, on the page and in
the print profile, hardcoded "Hybrid or in-person". The tile text is
Design's call: the profile's value, " · ", then the subline, as stored.
"""

from pathlib import Path

from services import matt_profile
from services.jd_assessor import load_matt_profile
from ui.pages import about_matt

ABOUT_MATT_SOURCE = Path(about_matt.__file__).read_text(encoding="utf-8")


def test_profile_work_model_is_in_office_preferred_hybrid_fine():
    profile = matt_profile.load_profile_dict()
    assert profile["logistics"]["work_model"] == {
        "value": "In-office preferred",
        "subline": "Hybrid fine",
    }


def test_profile_facts_carry_the_new_work_model_and_no_remote():
    facts = load_matt_profile()
    assert "Work model: In-office preferred. Hybrid fine." in facts
    assert "remote" not in facts.lower()


def test_work_mode_tile_text_from_the_real_profile():
    profile = matt_profile.load_profile_dict()
    assert about_matt._work_mode_text(profile) == "In-office preferred · Hybrid fine"


def test_work_mode_tile_reads_the_profile_not_a_literal():
    profile = {
        "logistics": {
            "work_model": {"value": "ZZZ_SENTINEL value", "subline": "ZZZ subline"}
        }
    }
    assert about_matt._work_mode_text(profile) == "ZZZ_SENTINEL value · ZZZ subline"


def test_work_mode_without_subline_is_the_value_alone():
    profile = {"logistics": {"work_model": {"value": "ZZZ_SENTINEL value"}}}
    assert about_matt._work_mode_text(profile) == "ZZZ_SENTINEL value"


def test_missing_work_model_value_gives_empty_text():
    # The -089 omit-cleanly contract: no value, no tile.
    assert about_matt._work_mode_text({"logistics": {}}) == ""
    assert about_matt._work_mode_text({}) == ""
    assert (
        about_matt._work_mode_text(
            {"logistics": {"work_model": {"value": " ", "subline": "ZZZ subline"}}}
        )
        == ""
    )


def test_about_matt_has_no_hardcoded_work_mode():
    # The print profile opens in a window.open popup Playwright can't read;
    # this covers its tile along with the page's.
    assert "Hybrid or in-person" not in ABOUT_MATT_SOURCE
