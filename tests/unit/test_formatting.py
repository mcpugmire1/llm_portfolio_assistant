"""
Unit tests for utils/formatting.py

Tests for story formatting utilities: curated 5P summaries, metric
extraction, and tag normalization.

Story fixtures come from the corpus via load_stories(), picked by field
value, so the tests read the fields production reads.
"""

import pytest

from utils.corpus_loader import load_stories


@pytest.fixture(scope="module")
def stories():
    return load_stories("echo_star_stories_nlp.jsonl")


class TestBuild5PSummary:
    """Tests for build_5p_summary() function."""

    def test_uses_curated_5p_summary_if_present(self, stories):
        """Should prefer curated 5PSummary field."""
        from utils.formatting import build_5p_summary

        story = stories[0]
        curated = story["5PSummary"].strip()
        result = build_5p_summary(story, max_chars=len(curated))
        assert result == curated

    def test_truncates_to_max_chars(self, stories):
        """Should truncate output to max_chars with ellipsis."""
        from utils.formatting import build_5p_summary

        story = next(s for s in stories if len(s["5PSummary"].strip()) > 50)
        result = build_5p_summary(story, max_chars=50)
        assert len(result) <= 50
        assert result.endswith("…")

    def test_falls_back_to_generic_text(self):
        """Should provide generic fallback when fields missing."""
        from utils.formatting import build_5p_summary

        story = {}
        result = build_5p_summary(story)
        assert len(result) > 0  # Should return something


class TestExtractMetricValue:
    """Tests for _extract_metric_value() helper function."""

    def test_extracts_percentage(self):
        """Should extract percentage metrics."""
        from utils.formatting import _extract_metric_value

        result = _extract_metric_value("Reduced cost by 50%")
        assert result is not None
        score, text = result
        assert score > 1000  # Percentages get +1000 bonus
        assert text == "Reduced cost by 50%"

    def test_extracts_multiplier(self):
        """Should extract multiplier metrics."""
        from utils.formatting import _extract_metric_value

        result = _extract_metric_value("Deployed 3x faster")
        assert result is not None
        score, text = result
        assert score == 3.0
        assert text == "Deployed 3x faster"

    def test_extracts_dollar_amount(self):
        """Should extract dollar amounts."""
        from utils.formatting import _extract_metric_value

        result = _extract_metric_value("Saved $2.5M")
        assert result is not None

    def test_returns_none_for_no_metrics(self):
        """Should return None when no metrics found."""
        from utils.formatting import _extract_metric_value

        assert _extract_metric_value("No metrics here") is None

    def test_handles_empty_string(self):
        """Should handle empty string."""
        from utils.formatting import _extract_metric_value

        assert _extract_metric_value("") is None

    def test_returns_highest_metric_when_multiple(self):
        """Should return highest-scored metric from text."""
        from utils.formatting import _extract_metric_value

        # Percentage should win over multiplier
        result = _extract_metric_value("Deployed 3x faster with 50% cost reduction")
        assert result is not None
        score, _ = result
        assert score > 1000  # Percentage score


class TestExtractMetricDisplay:
    """Tests for _extract_metric_display() -- MATTGPT-215.

    Replaces the story_detail.py sidebar Key Metrics inline heuristic. Returns
    (value, label) pairs for rendering, or None when the text has no metric
    marker. Uses METRIC_RX so decimals, currency with unit suffix (K/M/B), +
    suffix, and multipliers are all captured; bare digits, years, and counted
    nouns produce None.
    """

    def test_returns_none_for_cendian_false_positive(self):
        """MATTGPT-215: '3 canonical business objects normalizing multiple
        trading exchange formats' must NOT match. The old heuristic triggered
        on the 'x' in 'exchange'; METRIC_RX requires a digit-adjacent marker."""
        from utils.formatting import _extract_metric_display

        result = _extract_metric_display(
            "- 3 canonical business objects normalizing multiple trading exchange formats"
        )
        assert result is None, f"Cendian false positive still fires: {result!r}"

    def test_returns_none_for_year_reference(self):
        """MATTGPT-215: 'Launched April 2011 as part of ACCESS Next Generation'
        must NOT render 2011 as a metric value."""
        from utils.formatting import _extract_metric_display

        result = _extract_metric_display(
            "- Launched April 2011 as part of ACCESS Next Generation"
        )
        assert result is None, f"Year rendered as metric: {result!r}"

    def test_returns_none_for_counted_noun(self):
        """MATTGPT-215: '15+ Fortune 500 engagements' is a count of things,
        not a delivery metric. No metric marker in the text -> None."""
        from utils.formatting import _extract_metric_display

        result = _extract_metric_display(
            "- 15+ Fortune 500 engagements, reducing lead time from weeks to days"
        )
        assert result is None, f"Counted noun rendered as metric: {result!r}"

    def test_extracts_decimal_percentage_precisely(self):
        """MATTGPT-215: '99.9% uptime' must extract '99.9%' as value, not '9%'
        or '99'. The old METRIC_RX matched only trailing '9%' because '.'
        broke the word boundary."""
        from utils.formatting import _extract_metric_display

        result = _extract_metric_display(
            "- Achieved 99.9% system uptime through automated recovery"
        )
        assert result is not None
        value, _ = result
        assert value == "99.9%", f"Decimal precision lost: {value!r}"

    def test_extracts_currency_with_unit_suffix(self):
        """MATTGPT-215: '$100M+ repeat business' must extract '$100M+' as
        value. The old METRIC_RX dropped the M+ because \\b after [\\d,\\.]*
        failed on the letter transition."""
        from utils.formatting import _extract_metric_display

        result = _extract_metric_display("- $100M+ in repeat business")
        assert result is not None
        value, _ = result
        assert value == "$100M+", f"Currency unit/suffix lost: {value!r}"

    def test_extracts_currency_with_decimal_and_unit(self):
        """MATTGPT-215: '$5.2M platform savings' must extract '$5.2M', not
        '$5.'."""
        from utils.formatting import _extract_metric_display

        result = _extract_metric_display("- $5.2M platform savings realized")
        assert result is not None
        value, _ = result
        assert value == "$5.2M", f"Decimal currency mishandled: {value!r}"

    def test_extracts_upper_bound_of_range(self):
        """MATTGPT-215: '3-4x faster' extracts '4x' (upper bound per ticket
        decision -- the claim the reader would make anyway)."""
        from utils.formatting import _extract_metric_display

        result = _extract_metric_display("- Delivered features 3-4x faster")
        assert result is not None
        value, _ = result
        assert value == "4x", f"Range extraction wrong: {value!r}"

    def test_picks_correct_metric_from_sev_pattern(self):
        """MATTGPT-215: 'Sev-1 outages dropped 50%+' must extract '50%', not
        '1' from 'Sev-1'. Old heuristic grabbed the first digit; METRIC_RX
        requires a marker so only 50% qualifies."""
        from utils.formatting import _extract_metric_display

        result = _extract_metric_display(
            "- Sev-1 outages dropped 50%+, stabilizing production"
        )
        assert result is not None
        value, _ = result
        assert value == "50%", f"Sev-1 pattern extracted wrong value: {value!r}"

    def test_strips_leading_bullet_dash_from_label(self):
        """MATTGPT-215: Performance bullets start with '- ' in the Excel
        source. That prefix wastes 2 chars of the label truncation window
        and reads oddly in the uppercase-transformed label. Strip it."""
        from utils.formatting import _extract_metric_display

        result = _extract_metric_display("- 4x delivery velocity")
        assert result is not None
        _, label = result
        assert not label.startswith(
            "- "
        ), f"Leading '- ' bullet prefix not stripped: {label!r}"
        assert label == "4x delivery velocity"

    def test_truncates_label_at_word_boundary(self):
        """MATTGPT-215: label_max defaults to 50 chars; truncation must land
        on a word boundary, not mid-word. Old code cut '4X velocity compared
        to client internal teams' at 'clien[t]' -- ugly."""
        from utils.formatting import _extract_metric_display

        result = _extract_metric_display(
            "- 4X velocity compared to client internal teams through reduced rework",
            label_max=50,
        )
        assert result is not None
        _, label = result
        # Label should end at a word boundary within 50 chars (after '- ' strip).
        assert len(label) <= 50, f"Label exceeds max: {len(label)} chars"
        assert not label.rstrip().endswith(
            ("clien", "compare", "compa")
        ), f"Mid-word truncation: {label!r}"

    def test_label_shorter_than_max_returns_full_text(self):
        """MATTGPT-215: strings shorter than label_max should return the full
        text (post dash-strip), not get artificially truncated."""
        from utils.formatting import _extract_metric_display

        result = _extract_metric_display("- 4x delivery velocity", label_max=50)
        assert result is not None
        _, label = result
        assert label == "4x delivery velocity"

    def test_returns_none_for_empty_string(self):
        from utils.formatting import _extract_metric_display

        assert _extract_metric_display("") is None
        assert _extract_metric_display("   ") is None


# =============================================================================
# Tag-normalization helpers (MATTGPT-072). Moved here from
# tests/unit/test_generate_public_tags.py under MATTGPT-216 -- the functions
# themselves now live in utils/formatting.py (moved from generate_public_tags.py
# so unit tests import them without triggering the script's eager OpenAI()
# construction at module load). End-to-end tests that exercise the full
# enrich_stories_with_nlp_tags() flow live in
# tests/integration/test_generate_public_tags.py.
# =============================================================================


class TestPromptView:
    """MATTGPT-072 Change 1: _prompt_view exposes the exact fields and
    projections the LLM tag prompt reads. Situation and Task must be read
    in full (not [0] only) so tags derive from the same slice the embedding
    is built from.
    """

    def test_reads_full_situation_not_just_first_item(self):
        """Situation is a list; the LLM should see all items joined,
        not just [0]. Sparkfly has a two-paragraph Situation and its
        second paragraph never reaches the tag prompt today."""
        from utils.formatting import _prompt_view

        story = {
            "Situation": [
                "First paragraph of situation.",
                "Second paragraph with distinct content.",
                "Third paragraph too.",
            ]
        }
        rendered = _prompt_view(story)["Situation"]
        assert (
            "Second paragraph" in rendered
        ), f"Situation must include all items, got: {rendered!r}"
        assert "Third paragraph" in rendered

    def test_reads_full_task_not_just_first_item(self):
        from utils.formatting import _prompt_view

        story = {"Task": ["First task item.", "Second task item."]}
        rendered = _prompt_view(story)["Task"]
        assert (
            "Second task item" in rendered
        ), f"Task must include all items, got: {rendered!r}"

    def test_covers_all_sixteen_prompt_fields(self):
        """Every field the prompt reads must appear in _prompt_view. Missing
        a field means the change-detector would silently skip stories whose
        LLM-relevant content did change -- the worst failure mode."""
        from utils.formatting import _prompt_view

        story = {
            "Era": "e",
            "Title": "t",
            "Role": "r",
            "Industry": "i",
            "Theme": "th",
            "Category": "c",
            "Sub-category": "sc",
            "Project Scope / Complexity": "psc",
            "Competencies": "co",
            "Use Case(s)": "uc",
            "Situation": ["s"],
            "Task": ["ta"],
            "Action": ["a1", "a2"],
            "Result": ["r1"],
            "Process": ["p"],
            "Performance": ["pe"],
        }
        view = _prompt_view(story)
        expected = {
            "Era",
            "Title",
            "Role",
            "Industry",
            "Theme",
            "Category",
            "Sub-category",
            "Project Scope / Complexity",
            "Competencies",
            "Use Case(s)",
            "Situation",
            "Task",
            "Action",
            "Result",
            "Process",
            "Performance",
        }
        assert set(view.keys()) == expected, (
            f"_prompt_view field set drift. "
            f"Missing: {expected - set(view.keys())}. "
            f"Extra: {set(view.keys()) - expected}."
        )


class TestTitleCaseDedup:
    """MATTGPT-072: case-insensitive dedup. Title case wins; acronyms preserved."""

    def test_title_case_wins_over_lowercase(self):
        from utils.formatting import _dedupe_title_case_wins

        result = _dedupe_title_case_wins(["Client Engagement", "client engagement"])
        assert result == ["Client Engagement"]

    def test_lowercase_first_seen_replaced_by_title_case(self):
        """First-seen order does not matter; more-uppercase wins."""
        from utils.formatting import _dedupe_title_case_wins

        result = _dedupe_title_case_wins(["client engagement", "Client Engagement"])
        assert result == ["Client Engagement"]

    def test_acronym_preserved_over_lowercase(self):
        from utils.formatting import _dedupe_title_case_wins

        result = _dedupe_title_case_wins(["aws", "AWS"])
        assert result == ["AWS"]

    def test_hyphenated_title_case_wins(self):
        from utils.formatting import _dedupe_title_case_wins

        result = _dedupe_title_case_wins(
            ["cross-functional collaboration", "Cross-Functional Collaboration"]
        )
        assert result == ["Cross-Functional Collaboration"]

    def test_single_variant_passes_through(self):
        from utils.formatting import _dedupe_title_case_wins

        result = _dedupe_title_case_wins(
            ["Client Engagement", "Delivery Excellence", "AWS"]
        )
        assert set(result) == {"Client Engagement", "Delivery Excellence", "AWS"}

    def test_tie_keeps_first_seen(self):
        """When uppercase counts tie, first-seen wins."""
        from utils.formatting import _dedupe_title_case_wins

        result = _dedupe_title_case_wins(["Data Governance", "Data governance"])
        assert result == ["Data Governance"]


class TestStripParenAcronym:
    """MATTGPT-072: collapse 'phrase (ACRONYM)' to just the acronym."""

    def test_parenthetical_acronym_stripped(self):
        from utils.formatting import _strip_paren_acronym

        assert _strip_paren_acronym("large language models (LLM)") == "LLM"
        assert _strip_paren_acronym("enterprise service bus (ESB)") == "ESB"

    def test_non_acronym_parenthetical_unchanged(self):
        """Only trailing all-caps parentheticals are treated as acronym
        expansions. Non-acronym parentheticals (lowercase, mixed, phrases)
        stay intact."""
        from utils.formatting import _strip_paren_acronym

        assert (
            _strip_paren_acronym("prototype (early stage)") == "prototype (early stage)"
        )


class TestNormalizeTagCase:
    """MATTGPT-072: title-case each word, preserve acronyms and mixed-case
    proper nouns."""

    def test_lowercase_to_title_case(self):
        from utils.formatting import _normalize_tag_case

        assert _normalize_tag_case("agile transformation") == "Agile Transformation"

    def test_all_caps_acronym_preserved(self):
        from utils.formatting import _normalize_tag_case

        assert _normalize_tag_case("AWS") == "AWS"
        assert _normalize_tag_case("EDI") == "EDI"

    def test_hyphenated_words(self):
        from utils.formatting import _normalize_tag_case

        assert (
            _normalize_tag_case("cross-functional collaboration")
            == "Cross-Functional Collaboration"
        )

    def test_slashed_acronym(self):
        from utils.formatting import _normalize_tag_case

        assert _normalize_tag_case("CI/CD pipelines") == "CI/CD Pipelines"

    def test_small_word_lowercased_between_words(self):
        from utils.formatting import _normalize_tag_case

        assert _normalize_tag_case("Docker And Kubernetes") == "Docker and Kubernetes"
        assert _normalize_tag_case("Aerospace And Defense") == "Aerospace and Defense"
        assert (
            _normalize_tag_case("Training and Enablement") == "Training and Enablement"
        )

    def test_small_word_capitalized_when_first(self):
        from utils.formatting import _normalize_tag_case

        assert _normalize_tag_case("And Docker") == "And Docker"
        assert _normalize_tag_case("the platform") == "The Platform"

    def test_small_word_lowercased_in_hyphen_segment(self):
        from utils.formatting import _normalize_tag_case

        assert _normalize_tag_case("Cross-And-Effect") == "Cross-and-Effect"

    def test_uppercase_small_word_still_lowercased(self):
        from utils.formatting import _normalize_tag_case

        assert _normalize_tag_case("Docker AND Kubernetes") == "Docker and Kubernetes"

    def test_acronym_preserved_next_to_small_word(self):
        from utils.formatting import _normalize_tag_case

        assert _normalize_tag_case("AWS and GCP") == "AWS and GCP"


class TestDropRestatedFields:
    """MATTGPT-072: tags that exactly restate Industry/Sub-category/Category/
    Project are duplicate routes and get dropped."""

    def test_tag_matching_industry_is_dropped(self):
        from utils.formatting import _drop_restated_fields

        story = {"Industry": "Telecommunications"}
        tags = ["Data Architecture", "Telecommunications", "Order Management"]
        assert _drop_restated_fields(tags, story) == [
            "Data Architecture",
            "Order Management",
        ]


class TestSlugify:
    """slugify() builds Role Match's utm_content from role and company. The
    expected values are what scripts/utils.py's slugify returned before it
    moved here, so the move changes no link."""

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("Senior Director, Acme Corp.", "senior-director-acme-corp"),
            ("VP  of Data - Platform", "vp-of-data---platform"),
            ("Head of AI & ML (Remote)", "head-of-ai-ml-remote"),
            ("", ""),
        ],
    )
    def test_slug_matches_the_scripts_utils_output(self, text, expected):
        from utils.formatting import slugify

        assert slugify(text) == expected
