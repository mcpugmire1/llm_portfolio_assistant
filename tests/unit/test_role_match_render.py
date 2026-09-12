"""MATTGPT-248 Cycle 1: Role Match render-side unit tests.

Covers the consumer surface for the partial-failure feature. Producer
(jd_assessor._assess_one_with_index catching Exception into an unassessed
row) is Cycle 2; this file exercises the consumer against synthetic
result payloads whose rows already carry the target statuses.

Imports role_match functions inside test methods (not at module top) to
avoid pulling Streamlit runtime state into pytest collection, matching
test_role_match_gate.py's pattern.

Parity rule (per MATTGPT-246 folded-in scope): facts identical across
screen, export, and report; affordances only where they exist; actions
only where the reader can take them. Count line is verbose and
word-identical across all three surfaces:

    Required: 10 ✓ strong, 1 ~ partial, 2 ✗ gap, 2 ⋯ unassessed

Legend is static per surface -- every entry renders regardless of what
statuses or evidence types the assessment contains. Signature enforces
staticness: `_legend_entries(*, surface)` takes no `results` argument.
The only per-surface filter is the 🔗 icon, which appears on screen
only (clickable affordance). Export and report use plain-text prefixes
("Project evidence:" / "Profile:") for the evidence-type entries.

Malformed rows (missing match_status or an unrecognized value) coerce
to unassessed at both the count layer and the render layer. The `?`
sentinel is deleted from the design because a `?` glyph on a forwarded
PDF has no legend entry and no explanation. The developer-facing
distinction moves to the log: "malformed row" phrase for producer-side
bugs, distinct from Cycle 2's caught-exception log wording.

Helper stubs land in role_match.py in this Red commit:
  _incomplete_notice_text(counts, total, *, surface)
  _dp_lines(points, *, surface)
  _legend_entries(*, surface)

Each raises NotImplementedError per CLAUDE.md line 195. Cycle 1 Green
implements them and threads the three surface builders through them.
"""

import logging

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _row(
    category: str,
    match_status: str,
    text: str = "Some requirement",
    evidence=None,
    gap_explanation: str = "",
) -> dict:
    return {
        "category": category,
        "requirement": text,
        "match_status": match_status,
        "evidence": evidence or [],
        "gap_explanation": gap_explanation,
        "confidence": "medium",
    }


def _payload(
    *rows: dict,
    role: str = "Senior Engineering Leader",
    company: str = "Acme Corp",
) -> dict:
    return {
        "extraction": {"role_title": role, "company": company},
        "results": list(rows),
    }


def _legend_section(output: str) -> str:
    """Slice the legend section from a rendered output, starting at the
    'Key:' marker and lowercasing so status-word assertions don't have to
    guess the surface's capitalization. Test-level helper used by both the
    share-text and export-html legend tests."""
    key_pos = output.find("Key:")
    assert (
        key_pos >= 0
    ), f"output missing 'Key:' anchor; first 300 chars: {output[:300]!r}"
    return output[key_pos:].lower()


# ---------------------------------------------------------------------------
# _STATUS_ICON badge dispatch for unassessed
# ---------------------------------------------------------------------------


class TestStatusIconUnassessed:
    def test_status_icon_has_unassessed_entry_with_ellipsis(self):
        """MATTGPT-248 badge treatment: grey pill, `⋯` glyph. CSS-token
        pinning (--pill-bg fill, --text-secondary glyph) is a manual
        visual check; this test locks the glyph only."""
        from ui.pages.role_match import _STATUS_ICON

        assert _STATUS_ICON.get("unassessed") == "⋯", (
            f"_STATUS_ICON['unassessed'] expected '⋯', got "
            f"{_STATUS_ICON.get('unassessed')!r}"
        )


# ---------------------------------------------------------------------------
# Em-dash absence in generated share/export strings (MATTGPT-246 items 1, 5)
# ---------------------------------------------------------------------------


class TestBuildShareTextEmDashAbsence:
    def test_share_text_generated_string_contains_no_em_dash(self):
        from ui.pages.role_match import _build_share_text

        payload = _payload(_row("required", "strong", "Engineering leadership"))
        output = _build_share_text(payload)
        assert "—" not in output, (
            f"em-dash character in share text output near: "
            f"{output[max(0, output.find(chr(0x2014)) - 25) : output.find(chr(0x2014)) + 25]!r}"
        )


class TestBuildExportHtmlEmDashAbsence:
    def test_export_html_generated_string_contains_no_em_dash(self):
        from ui.pages.role_match import _build_export_html

        payload = _payload(_row("required", "strong", "Engineering leadership"))
        output = _build_export_html(payload)
        assert "—" not in output, "em-dash character in export html output"


# ---------------------------------------------------------------------------
# Share text gains summary block, legend footer, supporting evidence
# ---------------------------------------------------------------------------


class TestBuildShareTextSummaryBlock:
    def test_share_text_includes_summary_block(self):
        """Report today has no summary. -248 item 4 adds a summary block
        mirroring the on-screen version."""
        from ui.pages.role_match import _build_share_text

        payload = _payload(
            _row("required", "strong"),
            _row("required", "gap"),
        )
        output = _build_share_text(payload)
        assert "SUMMARY" in output.upper(), "share text missing SUMMARY header"


class TestBuildShareTextLegendFooter:
    """Report gains a plain-text legend footer. Entries are static -- all
    four statuses + both evidence type prefixes appear regardless of what
    the assessment contains. Assertions slice from 'Key:' and lowercase
    so requirement text, gap explanations, and count-line words can't
    accidentally satisfy them."""

    def test_share_text_includes_key_marker(self):
        from ui.pages.role_match import _build_share_text

        payload = _payload(_row("required", "strong"))
        output = _build_share_text(payload)
        assert "Key:" in output, "share text missing 'Key:' legend footer"

    def test_share_text_legend_footer_lists_all_four_statuses(self):
        from ui.pages.role_match import _build_share_text

        payload = _payload(_row("required", "strong"))
        output = _build_share_text(payload)
        legend = _legend_section(output)
        for word in ("strong", "partial", "gap", "unassessed"):
            assert word in legend, (
                f"share text legend missing {word!r} entry; legend "
                f"section is: {legend!r}"
            )

    def test_share_text_legend_footer_lists_evidence_type_prefixes(self):
        """Off-screen surfaces render the evidence-type distinction with
        plain-text prefixes: 'Project evidence:' and 'Profile:'. Prefix
        form (no glyph) since 🔗 marks clickability, which doesn't exist
        off-screen."""
        from ui.pages.role_match import _build_share_text

        payload = _payload(_row("required", "strong"))
        output = _build_share_text(payload)
        legend = _legend_section(output)
        assert (
            "project evidence:" in legend
        ), "share text legend missing 'Project evidence:' prefix"
        assert "profile:" in legend, "share text legend missing 'Profile:' prefix"

    def test_share_text_legend_does_not_render_link_glyph(self):
        """🔗 is a screen-only affordance (clickable). Report renders
        type prefixes without the glyph."""
        from ui.pages.role_match import _build_share_text

        payload = _payload(_row("required", "strong"))
        output = _build_share_text(payload)
        assert (
            "🔗" not in output
        ), "share text legend contains 🔗 (screen-only affordance)"


class TestBuildShareTextSupportingEvidence:
    """Acceptance line 1638: report lists the supporting story/evidence
    for each non-gap requirement. Both evidence types qualify -- top pick
    per row -- with the type prefix in front."""

    def test_share_text_lists_project_evidence_for_strong_requirement(self):
        from ui.pages.role_match import _build_share_text

        story_title = "Modernizing Legacy Systems"
        payload = _payload(
            _row(
                "required",
                "strong",
                "Modernization leadership",
                evidence=[
                    {
                        "evidence_type": "story",
                        "story_title": story_title,
                        "client": "Norfolk Southern",
                    }
                ],
            ),
        )
        output = _build_share_text(payload)
        assert story_title in output, (
            f"share text missing supporting story {story_title!r} for " f"strong row"
        )
        assert (
            "Project evidence:" in output
        ), "share text missing 'Project evidence:' prefix on story row"

    def test_share_text_lists_profile_evidence_for_strong_requirement(self):
        """Row with only profile-type evidence still gets a supporting
        evidence line. Without this, a strong verdict backed by profile
        alone renders bare in the forwarded artifact."""
        from ui.pages.role_match import _build_share_text

        relevance = "Twenty-plus years leading engineering organizations"
        payload = _payload(
            _row(
                "required",
                "strong",
                "Leadership experience",
                evidence=[
                    {"evidence_type": "profile", "relevance": relevance},
                ],
            ),
        )
        output = _build_share_text(payload)
        assert (
            "Profile:" in output
        ), "share text missing 'Profile:' prefix on profile-only row"

    def test_share_text_does_not_list_evidence_for_gap_requirement(self):
        """Gap rows have nothing supporting them. Naming an adjacent
        story would misrepresent the assessment."""
        from ui.pages.role_match import _build_share_text

        adjacent_title = "Unrelated Adjacent Story"
        payload = _payload(
            _row(
                "required",
                "gap",
                "Something we cannot do",
                evidence=[
                    {
                        "evidence_type": "story",
                        "story_title": adjacent_title,
                        "client": "X",
                    }
                ],
                gap_explanation="Note: no direct experience",
            ),
        )
        output = _build_share_text(payload)
        assert (
            adjacent_title not in output
        ), f"share text listed evidence for a gap row: {adjacent_title!r}"


# ---------------------------------------------------------------------------
# Export HTML: gap icon alignment, legend added, unassessed entry present
# ---------------------------------------------------------------------------


class TestBuildExportHtmlGapIcon:
    def test_export_gap_icon_matches_ui_status_icon(self):
        """MATTGPT-246 item 3: export gap icon is the UI's circled-X,
        not a red dot. Anchor on _STATUS_ICON['gap']."""
        from ui.pages.role_match import _STATUS_ICON, _build_export_html

        ui_gap_icon = _STATUS_ICON.get("gap")
        assert ui_gap_icon is not None, "_STATUS_ICON missing 'gap' key"

        payload = _payload(_row("required", "gap", "Something"))
        output = _build_export_html(payload)
        assert (
            ui_gap_icon in output
        ), f"export gap rendering does not use UI icon {ui_gap_icon!r}"


class TestBuildExportHtmlLegend:
    """MATTGPT-246 item 2: export gains a legend block. Under -248 the
    legend includes an unassessed entry positioned after gap and before
    the evidence divider. Same 'Key:' anchor + lowercase slice as the
    share-text legend tests."""

    def test_export_html_includes_key_marker(self):
        from ui.pages.role_match import _build_export_html

        payload = _payload(_row("required", "strong"))
        output = _build_export_html(payload)
        assert "Key:" in output, "export html missing 'Key:' legend marker"

    def test_export_legend_contains_all_four_statuses(self):
        from ui.pages.role_match import _build_export_html

        payload = _payload(_row("required", "strong"))
        output = _build_export_html(payload)
        legend = _legend_section(output)
        for word in ("strong", "partial", "gap", "unassessed"):
            assert word in legend, (
                f"export legend missing {word!r} entry; legend section "
                f"is: {legend!r}"
            )

    def test_export_legend_contains_evidence_type_prefixes(self):
        from ui.pages.role_match import _build_export_html

        payload = _payload(_row("required", "strong"))
        output = _build_export_html(payload)
        legend = _legend_section(output)
        assert "project evidence:" in legend
        assert "profile:" in legend

    def test_export_legend_omits_link_glyph(self):
        """🔗 is screen-only affordance; export legend uses plain-text
        prefixes."""
        from ui.pages.role_match import _build_export_html

        payload = _payload(_row("required", "strong"))
        output = _build_export_html(payload)
        assert "🔗" not in output, "export legend contains 🔗 (screen-only)"


# ---------------------------------------------------------------------------
# Count builder parity: verbose, word-identical fragments
# ---------------------------------------------------------------------------


class TestCountBuilderParity:
    """Parity across all three surfaces. Assertions cover:
      - screen  via `_count_spans` (module-scope after Cycle 1 Green
                 extracts it from its nested location in
                 `_render_results_panel`; Red has a NIE stub)
      - export  via `_build_export_html` output (which internally calls
                 the nested `_ex_count_line`)
      - share   via `_build_share_text` output (Green adds the count line)

    Testing all three at once is the point of the class -- the drift
    that this ticket exists to close came from testing two while
    inspecting the third by eye."""

    _COUNTS = {"strong": 10, "partial": 1, "gap": 2, "unassessed": 2}

    def _payload_with_full_counts(self) -> dict:
        """Ten strong + one partial + two gap + two unassessed under
        required = 15 rows total; enough for every verbose fragment to
        appear in the count line without any zero-count omissions."""
        rows = []
        rows.extend([_row("required", "strong", f"Strong req {i}") for i in range(10)])
        rows.append(_row("required", "partial", "Partial req"))
        rows.extend([_row("required", "gap", f"Gap req {i}") for i in range(2)])
        rows.extend(
            [_row("required", "unassessed", f"Unassessed req {i}") for i in range(2)]
        )
        return _payload(*rows)

    def test_all_three_surfaces_carry_strong_fragment(self):
        from ui.pages.role_match import (
            _build_export_html,
            _build_share_text,
            _count_spans,
        )

        payload = self._payload_with_full_counts()
        screen = _count_spans(self._COUNTS)
        share = _build_share_text(payload)
        export = _build_export_html(payload)
        assert "10 ✓ strong" in screen, "screen missing '10 ✓ strong'"
        assert "10 ✓ strong" in share, "share text missing '10 ✓ strong'"
        assert "10 ✓ strong" in export, "export html missing '10 ✓ strong'"

    def test_all_three_surfaces_carry_partial_fragment(self):
        from ui.pages.role_match import (
            _build_export_html,
            _build_share_text,
            _count_spans,
        )

        payload = self._payload_with_full_counts()
        screen = _count_spans(self._COUNTS)
        share = _build_share_text(payload)
        export = _build_export_html(payload)
        assert "1 ~ partial" in screen
        assert "1 ~ partial" in share
        assert "1 ~ partial" in export

    def test_all_three_surfaces_carry_gap_fragment(self):
        from ui.pages.role_match import (
            _build_export_html,
            _build_share_text,
            _count_spans,
        )

        payload = self._payload_with_full_counts()
        screen = _count_spans(self._COUNTS)
        share = _build_share_text(payload)
        export = _build_export_html(payload)
        assert "2 ✗ gap" in screen
        assert "2 ✗ gap" in share
        assert "2 ✗ gap" in export

    def test_all_three_surfaces_carry_unassessed_fragment(self):
        from ui.pages.role_match import (
            _build_export_html,
            _build_share_text,
            _count_spans,
        )

        payload = self._payload_with_full_counts()
        screen = _count_spans(self._COUNTS)
        share = _build_share_text(payload)
        export = _build_export_html(payload)
        assert "2 ⋯ unassessed" in screen, "screen missing '2 ⋯ unassessed'"
        assert "2 ⋯ unassessed" in share, "share text missing '2 ⋯ unassessed'"
        assert "2 ⋯ unassessed" in export, "export html missing '2 ⋯ unassessed'"

    def test_zero_count_status_omitted_from_summary_count_line(self):
        """When a status count is zero, its fragment does not appear in
        the summary count line. Assertion is scoped by extracting the
        count-line substring (bounded by 'Required:' and the newline
        after the last count fragment) so the static legend elsewhere
        on the surface cannot accidentally satisfy the check."""
        from ui.pages.role_match import _build_export_html, _build_share_text

        payload = _payload(_row("required", "strong", "Only a strong row"))
        share = _build_share_text(payload)
        export = _build_export_html(payload)

        # Extract the count line from each surface. In share text it's on
        # its own line beginning with "Required:". In export HTML it's
        # inside <p class="summary-counts">Required: ...</p>.
        share_line = next(
            (ln for ln in share.splitlines() if ln.strip().startswith("Required:")),
            "",
        )
        export_match_pos = export.find("Required:")
        export_line = (
            export[export_match_pos : export.find("</p>", export_match_pos)]
            if export_match_pos >= 0
            else ""
        )
        assert share_line, f"share text missing count line: {share!r}"
        assert export_line, "export html missing count line"

        for absent in ("partial", "gap", "unassessed"):
            assert absent not in share_line.lower(), (
                f"share count line renders zero-{absent} fragment: " f"{share_line!r}"
            )
            assert absent not in export_line.lower(), (
                f"export count line renders zero-{absent} fragment: " f"{export_line!r}"
            )


# ---------------------------------------------------------------------------
# Malformed rows coerce to unassessed (missing key OR unrecognized value)
# ---------------------------------------------------------------------------


class TestMalformedMatchStatusCoercion:
    """MATTGPT-248: render sites coerce any unrecognized match_status
    (missing key or unknown value) to unassessed. The `?` sentinel is
    deleted from the design -- a `?` glyph on a forwarded PDF has no
    legend entry and no explanation. `_STATUS_ICON` never sees an
    unknown status because coercion happens upstream at the render site.

    Cycle 2's producer path converges on the same "unassessed" status
    rather than introducing a second vocabulary. The developer-facing
    distinction moves to the log: 'malformed row' phrase for producer-
    side bugs, distinct from Cycle 2's caught-exception log wording."""

    def test_missing_match_status_row_renders_with_ellipsis_glyph(self):
        from ui.pages.role_match import _STATUS_ICON, _build_share_text

        bad_row = {
            "category": "required",
            "requirement": "Marker-missing-key",
            "evidence": [],
            "gap_explanation": "",
            "confidence": "",
        }
        payload = _payload(bad_row)
        output = _build_share_text(payload)
        req_line = next(
            (ln for ln in output.splitlines() if "Marker-missing-key" in ln),
            None,
        )
        assert req_line is not None, f"row line not found: {output!r}"
        ellipsis = _STATUS_ICON.get("unassessed", "⋯")
        assert ellipsis in req_line, (
            f"missing-status row expected to render as unassessed ({ellipsis!r}); "
            f"got line: {req_line!r}"
        )
        assert "?" not in req_line, (
            f"missing-status row rendered with `?` sentinel; coercion to "
            f"unassessed missing: {req_line!r}"
        )

    def test_unknown_match_status_row_renders_with_ellipsis_glyph(self):
        from ui.pages.role_match import _STATUS_ICON, _build_share_text

        payload = _payload(
            _row("required", "not-a-real-status", "Marker-unknown-value")
        )
        output = _build_share_text(payload)
        req_line = next(
            (ln for ln in output.splitlines() if "Marker-unknown-value" in ln),
            None,
        )
        assert req_line is not None
        ellipsis = _STATUS_ICON.get("unassessed", "⋯")
        assert ellipsis in req_line, (
            f"unknown-status row expected to render as unassessed; got "
            f"line: {req_line!r}"
        )

    def test_malformed_row_logs_warning_with_malformed_row_phrase(self, caplog):
        """The log message distinguishes malformed rows (producer bug)
        from caught exceptions (Cycle 2 outage). Phrase 'malformed row'
        pins the vocabulary."""
        from ui.pages.role_match import _build_share_text

        bad_row = {
            "category": "required",
            "requirement": "Some req",
            "evidence": [],
            "gap_explanation": "",
            "confidence": "",
        }
        payload = _payload(bad_row)
        with caplog.at_level(logging.WARNING, logger="ui.pages.role_match"):
            _build_share_text(payload)
        matching = [r for r in caplog.records if "malformed row" in r.message.lower()]
        assert matching, (
            f"expected warning containing 'malformed row'; got "
            f"{[r.message for r in caplog.records]!r}"
        )

    def test_malformed_row_counted_in_notice_and_summary(self):
        """Two-row payload: one strong, one malformed. The incomplete
        notice reads '1 of these 2' -- if the malformed row weren't
        coerced to unassessed at the count layer, the notice would say
        '0 of these 2' or omit entirely and the badges would disagree
        with the count line."""
        from ui.pages.role_match import _build_share_text

        payload = _payload(
            _row("required", "strong", "Assessed strong requirement"),
            _row("required", "not-a-real-status", "Malformed row"),
        )
        output = _build_share_text(payload)
        assert "1 of these 2" in output, (
            f"incomplete notice does not reflect malformed row as "
            f"unassessed; output: {output!r}"
        )


# ---------------------------------------------------------------------------
# _incomplete_notice_text helper: per-surface copy, None when no unassessed
# ---------------------------------------------------------------------------


class TestIncompleteNoticeText:
    """New helper stubs `_incomplete_notice_text(counts, total, *, surface)`.
    Returns None when unassessed counts are zero; returns surface-appropriate
    copy otherwise. Callers pass 'print' for both export and share since
    the copy is identical for the two off-screen surfaces."""

    def _counts_with_unassessed(
        self, required_unassessed: int, preferred_unassessed: int = 0
    ) -> dict:
        return {
            "required": {
                "strong": 0,
                "partial": 0,
                "gap": 0,
                "unassessed": required_unassessed,
            },
            "preferred": {
                "strong": 0,
                "partial": 0,
                "gap": 0,
                "unassessed": preferred_unassessed,
            },
        }

    def _counts_no_unassessed(self) -> dict:
        return {
            "required": {"strong": 5, "partial": 0, "gap": 0, "unassessed": 0},
            "preferred": {"strong": 0, "partial": 0, "gap": 0, "unassessed": 0},
        }

    def test_returns_none_when_no_unassessed_screen(self):
        from ui.pages.role_match import _incomplete_notice_text

        result = _incomplete_notice_text(
            self._counts_no_unassessed(), total=5, surface="screen"
        )
        assert result is None

    def test_returns_none_when_no_unassessed_print(self):
        from ui.pages.role_match import _incomplete_notice_text

        result = _incomplete_notice_text(
            self._counts_no_unassessed(), total=5, surface="print"
        )
        assert result is None

    def test_screen_copy_names_counts_and_includes_action_clause(self):
        from ui.pages.role_match import _incomplete_notice_text

        result = _incomplete_notice_text(
            self._counts_with_unassessed(2), total=22, surface="screen"
        )
        assert result is not None
        assert "2 of these 22" in result, f"got {result!r}"
        assert "Try again" in result, f"screen copy missing action clause: {result!r}"

    def test_print_copy_names_counts_and_omits_action_clause(self):
        from ui.pages.role_match import _incomplete_notice_text

        result = _incomplete_notice_text(
            self._counts_with_unassessed(2), total=22, surface="print"
        )
        assert result is not None
        assert "2 of these 22" in result, f"got {result!r}"
        assert (
            "Try again" not in result
        ), f"print copy has an action clause it shouldn't: {result!r}"

    def test_screen_and_print_both_open_with_paw_emoji(self):
        from ui.pages.role_match import _incomplete_notice_text

        screen = _incomplete_notice_text(
            self._counts_with_unassessed(2), total=22, surface="screen"
        )
        printed = _incomplete_notice_text(
            self._counts_with_unassessed(2), total=22, surface="print"
        )
        assert screen is not None and printed is not None
        assert "🐾" in screen
        assert "🐾" in printed

    def test_counts_sum_across_required_and_preferred(self):
        """When unassessed rows exist under both categories, the notice
        N is the combined count."""
        from ui.pages.role_match import _incomplete_notice_text

        counts = self._counts_with_unassessed(
            required_unassessed=2, preferred_unassessed=1
        )
        result = _incomplete_notice_text(counts, total=22, surface="screen")
        assert result is not None
        assert "3 of these 22" in result, (
            f"expected combined count 3 (2 required + 1 preferred); " f"got {result!r}"
        )


# ---------------------------------------------------------------------------
# _dp_lines helper: returns [] on empty input, populated fragments otherwise
# ---------------------------------------------------------------------------


class TestDpLinesHelper:
    """New helper stubs `_dp_lines(points, *, surface)` centralizes the
    discussion-points section rendering across screen, export, and share.
    Empty input returns []; callers skip emitting a section header when
    the return is empty. This is what makes branch 4 renderer-safe on
    all three surfaces without three separate empty-guard checks."""

    def test_empty_points_returns_empty_list_screen(self):
        from ui.pages.role_match import _dp_lines

        assert _dp_lines([], surface="screen") == []

    def test_empty_points_returns_empty_list_export(self):
        from ui.pages.role_match import _dp_lines

        assert _dp_lines([], surface="export") == []

    def test_empty_points_returns_empty_list_share(self):
        from ui.pages.role_match import _dp_lines

        assert _dp_lines([], surface="share") == []

    def test_populated_points_returns_non_empty_on_all_surfaces(self):
        from ui.pages.role_match import _dp_lines

        points = [
            {
                "text": "Kubernetes at scale",
                "label_type": "Required, Gap",
                "is_overflow_indicator": False,
                "is_zero_case": False,
            }
        ]
        for surface in ("screen", "export", "share"):
            result = _dp_lines(points, surface=surface)
            assert (
                len(result) >= 1
            ), f"expected non-empty on surface {surface!r}; got {result!r}"


# ---------------------------------------------------------------------------
# _legend_entries helper: static per-surface list; 🔗 only on screen
# ---------------------------------------------------------------------------


class TestLegendEntriesHelper:
    """New helper stubs `_legend_entries(*, surface)`. Returns a fixed
    list of legend entries for the given surface. No results argument --
    legend is static by construction; the invariant is enforced by the
    signature.

    Order (fixed across surfaces): strong -> partial -> gap -> unassessed
    -> evidence entries.

    Per-surface filter: 🔗 icon appears on screen only (clickable
    affordance). Export and report show evidence types with plain-text
    prefixes without the glyph.

    Ordering assertion anchors on lowercase 'project evidence', which
    appears on all three surfaces after the unassessed entry (screen as
    part of '🔗 = project evidence', export/share as 'Project
    evidence:')."""

    def _serialize(self, entries):
        """Flatten entries to one lowercased string for substring
        assertions, independent of whether entries are dicts, strs, or
        HTML fragments."""
        return "\n".join(str(e) for e in entries).lower()

    def test_screen_legend_contains_all_four_status_words(self):
        from ui.pages.role_match import _legend_entries

        text = self._serialize(_legend_entries(surface="screen"))
        for word in ("strong", "partial", "gap", "unassessed"):
            assert word in text, f"screen legend missing {word!r} entry"

    def test_export_legend_contains_all_four_status_words(self):
        from ui.pages.role_match import _legend_entries

        text = self._serialize(_legend_entries(surface="export"))
        for word in ("strong", "partial", "gap", "unassessed"):
            assert word in text, f"export legend missing {word!r} entry"

    def test_share_legend_contains_all_four_status_words(self):
        from ui.pages.role_match import _legend_entries

        text = self._serialize(_legend_entries(surface="share"))
        for word in ("strong", "partial", "gap", "unassessed"):
            assert word in text, f"share legend missing {word!r} entry"

    def test_screen_legend_contains_link_glyph(self):
        from ui.pages.role_match import _legend_entries

        text = "\n".join(str(e) for e in _legend_entries(surface="screen"))
        assert (
            "🔗" in text
        ), "screen legend missing 🔗 (project-evidence clickability icon)"

    def test_export_legend_omits_link_glyph(self):
        from ui.pages.role_match import _legend_entries

        text = "\n".join(str(e) for e in _legend_entries(surface="export"))
        assert "🔗" not in text, "export legend contains 🔗 (screen-only affordance)"

    def test_share_legend_omits_link_glyph(self):
        from ui.pages.role_match import _legend_entries

        text = "\n".join(str(e) for e in _legend_entries(surface="share"))
        assert "🔗" not in text

    def test_export_and_share_legend_contain_evidence_type_prefixes(self):
        """Off-screen surfaces render the evidence-type distinction with
        plain-text prefixes: 'Project evidence:' and 'Profile:'."""
        from ui.pages.role_match import _legend_entries

        for surface in ("export", "share"):
            text = "\n".join(str(e) for e in _legend_entries(surface=surface))
            assert (
                "Project evidence:" in text
            ), f"{surface!r} legend missing 'Project evidence:' prefix"
            assert "Profile:" in text, f"{surface!r} legend missing 'Profile:' prefix"

    def test_unassessed_appears_before_project_evidence_marker(self):
        """Legend order pins unassessed BEFORE the surface's first
        evidence marker. Anchor 'project evidence' (lowercase) works on
        all three surfaces: screen has '🔗 = project evidence' as the
        divider label; export and share have 'Project evidence:' as the
        entry prefix."""
        from ui.pages.role_match import _legend_entries

        for surface in ("screen", "export", "share"):
            text = self._serialize(_legend_entries(surface=surface))
            pos_unassessed = text.find("unassessed")
            pos_project_evidence = text.find("project evidence")
            assert (
                pos_unassessed >= 0
            ), f"{surface!r} legend missing 'unassessed' marker"
            assert (
                pos_project_evidence >= 0
            ), f"{surface!r} legend missing 'project evidence' marker"
            assert pos_unassessed < pos_project_evidence, (
                f"{surface!r} legend: unassessed at {pos_unassessed} must "
                f"appear before project evidence at {pos_project_evidence}"
            )


# ---------------------------------------------------------------------------
# Notice-above-summary ordering on off-screen surfaces
# ---------------------------------------------------------------------------


class TestIncompleteNoticeOrdering:
    """Under branch 4 (all-unassessed), the incomplete notice is the only
    visible signal above the count line. Ordering: notice above BOTH the
    summary block AND the first requirement, on every surface where the
    notice renders.

    Two assertions per surface, not one: the summary check pins the
    notice above the SUMMARY section header; the first-requirement check
    pins it above the requirement list. Nothing else stops a future edit
    from placing the notice between summary and requirements, which
    would still read as a footnote to the summary rather than a headline
    signal.

    SUMMARY anchor is case-sensitive (`output.find("SUMMARY")`, not
    `.upper().find(...)`) so lowercase CSS class names like
    `.summary-section` and `.summary-counts` in the export HTML style
    block are not matched -- only the uppercase `<h2>SUMMARY</h2>`
    section header in the body counts.

    Fixture fragility: the first-requirement anchor 'First unassessed req'
    passes through html.escape() in _build_export_html. Plain ASCII with
    no special characters survives unchanged (verified), so the same
    substring anchors both the share (unescaped) and export (escaped)
    outputs. If the fixture string ever gains an apostrophe, ampersand,
    angle bracket, or quote, html.escape will transform the export
    version and output.find('First unassessed req') will return -1 on
    export while share still matches. The failure would look like a
    wiring bug but would be a fixture bug. Keep fixture strings plain
    ASCII or update both surface anchors together."""

    def _payload_with_unassessed(self):
        return _payload(
            _row("required", "unassessed", "First unassessed req"),
            _row("required", "unassessed", "Second unassessed req"),
        )

    def test_share_text_notice_appears_before_summary_block(self):
        from ui.pages.role_match import _build_share_text

        output = _build_share_text(self._payload_with_unassessed())
        notice_pos = output.find("2 of these")
        summary_pos = output.find("SUMMARY")
        first_req_pos = output.find("First unassessed req")
        assert (
            notice_pos >= 0
        ), f"share text missing notice text '2 of these ...': {output!r}"
        assert summary_pos >= 0, "share text missing SUMMARY section header"
        assert first_req_pos >= 0, "share text missing first requirement anchor"
        assert notice_pos < summary_pos, (
            f"notice at pos {notice_pos} must appear before SUMMARY header "
            f"at pos {summary_pos} in share text"
        )
        assert notice_pos < first_req_pos, (
            f"notice at pos {notice_pos} must also appear before the first "
            f"requirement at pos {first_req_pos} in share text -- placing "
            f"the notice between summary and requirements reads as a "
            f"footnote, not a headline signal"
        )

    def test_export_html_notice_appears_before_summary_block(self):
        from ui.pages.role_match import _build_export_html

        output = _build_export_html(self._payload_with_unassessed())
        notice_pos = output.find("2 of these")
        summary_pos = output.find("SUMMARY")
        first_req_pos = output.find("First unassessed req")
        assert notice_pos >= 0, "export html missing notice text '2 of these ...'"
        assert summary_pos >= 0, "export html missing SUMMARY section header"
        assert first_req_pos >= 0, "export html missing first requirement anchor"
        assert notice_pos < summary_pos, (
            f"notice at pos {notice_pos} must appear before SUMMARY header "
            f"at pos {summary_pos} in export html"
        )
        assert notice_pos < first_req_pos, (
            f"notice at pos {notice_pos} must also appear before the first "
            f"requirement at pos {first_req_pos} in export html -- placing "
            f"the notice between summary and requirements reads as a "
            f"footnote, not a headline signal"
        )
