"""MATTGPT-250 item 4 Red: Ask Agy Sources layout with the profile fact row.

_sources_layout(categories, sources, is_synthesis) decides what the
Sources block renders:
  - show_label: the SOURCES label (always renders)
  - fact_cards: one display name per cited category, in cited order
  - story_count: story cards shown, min(len(sources), cap), where cap is
    SOURCES_MAX_SYNTHESIS or SOURCES_MAX_SURGICAL. Fact cards do not
    count toward the cap.

_fact_card_html(display_name) renders one fact card: the "FROM MATT'S
PROFILE" label plus the category display name. Not a link.

R1: category markers present -> fact row plus story grid.
R2: no markers -> story grid only.
A profile-only answer is R1 with whatever sources came back.
"""

import pytest

from ui.pages.ask_mattgpt import conversation_helpers as ch

_ALL_CATEGORIES = ["certifications", "education", "languages"]
_DISPLAY_NAMES = ["Certifications", "Education", "Languages"]
_FACT_CARD_LABEL = "FROM MATT'S PROFILE"


def _sources(n: int) -> list[dict]:
    return [
        {"id": f"story-{i}", "title": f"Story {i}", "client": "Client"}
        for i in range(n)
    ]


def _cap(is_synthesis: bool) -> int:
    return ch.SOURCES_MAX_SYNTHESIS if is_synthesis else ch.SOURCES_MAX_SURGICAL


_GRID_CASES = [
    (8, False),  # more sources than the surgical cap
    (8, True),  # more sources than the synthesis cap
    (2, False),  # fewer sources than the cap
    (0, False),  # no sources came back
]


class TestSourcesLayout:
    @pytest.mark.parametrize("n_sources, is_synthesis", _GRID_CASES)
    def test_r1_categories_present_fact_row_plus_story_grid(
        self, n_sources, is_synthesis
    ):
        layout = ch._sources_layout(_ALL_CATEGORIES, _sources(n_sources), is_synthesis)
        assert layout["show_label"] is True
        assert (
            layout["fact_cards"] == _DISPLAY_NAMES
        ), f"fact cards must use display names, got {layout['fact_cards']!r}"
        assert layout["story_count"] == min(n_sources, _cap(is_synthesis))

    @pytest.mark.parametrize(
        "categories, display_names",
        [
            (["languages", "certifications"], ["Languages", "Certifications"]),
            (["education"], ["Education"]),
        ],
    )
    def test_r1_fact_cards_follow_cited_order(self, categories, display_names):
        layout = ch._sources_layout(categories, _sources(3), False)
        assert layout["fact_cards"] == display_names

    @pytest.mark.parametrize("name", _DISPLAY_NAMES)
    def test_r1_fact_card_html_is_label_and_name_not_a_link(self, name):
        html = ch._fact_card_html(name)
        assert _FACT_CARD_LABEL in html, f"card missing label: {html!r}"
        assert name in html, f"card missing {name!r}: {html!r}"
        for forbidden in ("<a", "href", "related_proj"):
            assert (
                forbidden not in html
            ), f"fact card must not be a link; found {forbidden!r}: {html!r}"

    @pytest.mark.parametrize("n_sources, is_synthesis", _GRID_CASES)
    def test_r2_no_markers_story_grid_only(self, n_sources, is_synthesis):
        layout = ch._sources_layout([], _sources(n_sources), is_synthesis)
        assert layout["show_label"] is True
        assert (
            layout["fact_cards"] == []
        ), f"no markers must render no fact cards, got {layout['fact_cards']!r}"
        assert layout["story_count"] == min(n_sources, _cap(is_synthesis))
