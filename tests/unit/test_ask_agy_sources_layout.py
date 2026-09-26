"""MATTGPT-250 Ask Agy Sources layout and profile fact cards.

_sources_layout(categories, sources, is_synthesis) decides what the
Sources block renders:
  - show_label: the SOURCES label (always renders)
  - fact_cards: one category key per cited category, in cited order
  - story_count: story cards shown, min(len(sources), cap), where cap is
    SOURCES_MAX_SYNTHESIS or SOURCES_MAX_SURGICAL. Fact cards do not
    count toward the cap.

_fact_card_html(category) renders one full-width fact card (mock #4a):
the label "From Matt's profile · <display name>", then that category's
entries read from the profile via services.matt_profile, never from the
answer text. Not a link. One card per cited category, stacked above the
story grid.

Every K assertion compares against html.escape(value, quote=False), the
same escaping the card uses: &, < and > are escaped, apostrophes are not.

R1: category markers present -> fact cards plus story grid.
R2: no markers -> story grid only.
K1-K7: fact card content.
"""

import html
from unittest.mock import patch

import pytest

from services import matt_profile
from ui.pages.ask_mattgpt import conversation_helpers as ch

_ALL_CATEGORIES = ["certifications", "education", "languages"]
_LABEL_PREFIX = "From Matt's profile · "
_CERT_DATE_LABELS = ["2020–2023", "2019–2023", "2017", "2002"]


def _esc(value: str) -> str:
    return html.escape(value, quote=False)


def _sources(n: int) -> list[dict]:
    return [
        {"id": f"story-{i}", "title": f"Story {i}", "client": "Client"}
        for i in range(n)
    ]


def _cap(is_synthesis: bool) -> int:
    return ch.SOURCES_MAX_SYNTHESIS if is_synthesis else ch.SOURCES_MAX_SURGICAL


def _assert_not_a_link(html_out: str) -> None:
    for forbidden in ("<a", "href", "related_proj"):
        assert (
            forbidden not in html_out
        ), f"fact card must not be a link; found {forbidden!r}: {html_out!r}"


_GRID_CASES = [
    (8, False),  # more sources than the surgical cap
    (8, True),  # more sources than the synthesis cap
    (2, False),  # fewer sources than the cap
    (0, False),  # no sources came back
]


class TestSourcesLayout:
    @pytest.mark.parametrize("n_sources, is_synthesis", _GRID_CASES)
    def test_r1_categories_present_fact_cards_plus_story_grid(
        self, n_sources, is_synthesis
    ):
        layout = ch._sources_layout(_ALL_CATEGORIES, _sources(n_sources), is_synthesis)
        assert layout["show_label"] is True
        assert (
            layout["fact_cards"] == _ALL_CATEGORIES
        ), f"fact cards must be one category key each, got {layout['fact_cards']!r}"
        assert layout["story_count"] == min(n_sources, _cap(is_synthesis))

    @pytest.mark.parametrize(
        "categories",
        [["languages", "certifications"], ["education"], ["location_availability"]],
    )
    def test_k6_one_card_per_category_in_cited_order(self, categories):
        layout = ch._sources_layout(categories, _sources(3), False)
        assert layout["fact_cards"] == categories

    @pytest.mark.parametrize("n_sources, is_synthesis", _GRID_CASES)
    def test_r2_no_markers_story_grid_only(self, n_sources, is_synthesis):
        layout = ch._sources_layout([], _sources(n_sources), is_synthesis)
        assert layout["show_label"] is True
        assert (
            layout["fact_cards"] == []
        ), f"no markers must render no fact cards, got {layout['fact_cards']!r}"
        assert layout["story_count"] == min(n_sources, _cap(is_synthesis))


class TestFactCardContent:
    def test_k1_certifications_card_lists_every_cert_with_dates(self):
        profile = matt_profile.load_profile_dict()
        names = [c["name"] for c in profile["certifications"]]
        assert len(names) == 4, names
        html_out = ch._fact_card_html("certifications")
        assert _esc(f"{_LABEL_PREFIX}Certifications") in html_out, html_out
        missing = [n for n in names if _esc(n) not in html_out]
        assert not missing, f"cert names not verbatim in card: {missing!r}"
        missing_dates = [d for d in _CERT_DATE_LABELS if _esc(d) not in html_out]
        assert not missing_dates, f"date labels missing: {missing_dates!r}"
        _assert_not_a_link(html_out)

    def test_k2_education_card_degree_over_institution(self):
        profile = matt_profile.load_profile_dict()
        html_out = ch._fact_card_html("education")
        assert _esc(f"{_LABEL_PREFIX}Education") in html_out, html_out
        for e in profile["education"]:
            degree_pos = html_out.find(_esc(e["degree"]))
            inst_pos = html_out.find(_esc(e["institution"]))
            assert degree_pos >= 0, f"degree {e['degree']!r} missing"
            assert (
                inst_pos > degree_pos
            ), f"institution {e['institution']!r} not after degree"
        _assert_not_a_link(html_out)

    def test_k3_languages_card_language_over_level(self):
        profile = matt_profile.load_profile_dict()
        html_out = ch._fact_card_html("languages")
        assert _esc(f"{_LABEL_PREFIX}Languages") in html_out, html_out
        for lang in profile["languages"]:
            lang_pos = html_out.find(_esc(lang["language"]))
            level_pos = html_out.find(_esc(lang["level"]))
            assert lang_pos >= 0, f"language {lang['language']!r} missing"
            assert level_pos > lang_pos, f"level {lang['level']!r} not after language"
        _assert_not_a_link(html_out)

    def test_k4_location_availability_card_matches_role_match_cells(self):
        cells = matt_profile.iter_location_cells(matt_profile.load_profile_dict())
        assert len(cells) == 4, cells
        html_out = ch._fact_card_html("location_availability")
        assert _esc(f"{_LABEL_PREFIX}Location & Availability") in html_out, html_out
        last = -1
        for label, value, subline in cells:
            pos = html_out.find(_esc(label))
            assert pos > last, f"cell {label!r} missing or out of Role Match order"
            assert _esc(value) in html_out, f"value {value!r} missing"
            if subline:
                assert _esc(subline) in html_out, f"subline {subline!r} missing"
            last = pos
        _assert_not_a_link(html_out)

    def test_k7_entries_come_from_the_profile(self):
        fixture = {
            "certifications": [
                {
                    "name": "ZZZ_SENTINEL Certified Tester",
                    "issued": 2021,
                    "expired": 2024,
                }
            ]
        }
        with patch.object(matt_profile, "load_profile_dict", return_value=fixture):
            html_out = ch._fact_card_html("certifications")
        assert _esc("ZZZ_SENTINEL Certified Tester") in html_out, html_out
        assert _esc("2021–2024") in html_out, html_out
        assert (
            "AWS Certified" not in html_out
        ), "card did not read entries from the profile loader"


class TestLocationAvailabilityFactCard:
    """location_availability is a profile fact category. Its display name
    comes from the display-name map in config/constants.py."""

    def test_display_name_map_defines_location_availability(self):
        from config import constants

        names = getattr(constants, "PROFILE_FACT_DISPLAY_NAMES", None)
        assert (
            names is not None
        ), "config.constants.PROFILE_FACT_DISPLAY_NAMES not defined"
        assert names.get("location_availability") == "Location & Availability"

    def test_every_fact_category_has_a_display_name(self):
        """_fact_card_html() labels each card from the map; a category added
        to PROFILE_FACT_CATEGORIES without a display name must fail here, not
        raise KeyError at render time."""
        from config.constants import PROFILE_FACT_CATEGORIES, PROFILE_FACT_DISPLAY_NAMES

        missing = set(PROFILE_FACT_CATEGORIES) - set(PROFILE_FACT_DISPLAY_NAMES)
        assert set(PROFILE_FACT_CATEGORIES) <= set(
            PROFILE_FACT_DISPLAY_NAMES
        ), f"categories without a display name: {sorted(missing)}"
