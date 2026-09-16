"""Unit tests for services.query_logger bot-filter behavior.

Why this exists: until May 13, 2026, log_query() had no bot filter. The
page_load path was guarded in app.py (MONITORING_BOT_SIGNATURES check) and
the role_match path was guarded at call sites (is_bot() in role_match.py
and action_buttons.py), but log_query() — used by Ask Agy and My
Work — logged unconditionally. Result: HeadlessChrome and UptimeRobot
queries leaked into the production query log alongside real user queries,
making conversion / bounce analysis unreliable.

These tests pin the contract: log_query() consults is_bot() and short-
circuits before spawning the daemon thread that writes to the sheet.
"""

from unittest.mock import MagicMock, patch


class TestLogQueryBotFilter:
    """log_query() must not spawn a write thread for monitoring-bot traffic."""

    def _mock_context(self, user_agent: str) -> MagicMock:
        """Build a MagicMock that mimics st.context with the given UA header.

        Configures headers.get() to return the UA for any header name asked.
        is_bot() and _capture_context() both read User-Agent via this path.
        """
        ctx = MagicMock()
        ctx.headers.get.return_value = user_agent
        ctx.timezone = "America/New_York"
        return ctx

    def test_log_query_skipped_for_headlesschrome(self):
        """HeadlessChrome UA must not trigger a row append.

        The Chrome agent's regression tests run under a HeadlessChrome UA and
        send real queries (e.g., "banking" on My Work). Pre-fix, those
        landed in the production log — the May 12 query-log dump showed 4
        HeadlessChrome "banking" queries that should never have been written.
        """
        from services import query_logger

        ctx = self._mock_context(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "HeadlessChrome/141.0.7390.37 Safari/537.36"
        )
        with (
            patch.object(query_logger.st, "context", ctx),
            patch.object(query_logger, "Thread") as mock_thread,
        ):
            query_logger.log_query("banking", page="My Work")
            mock_thread.assert_not_called()

    def test_log_query_skipped_for_uptimerobot(self):
        """UptimeRobot UA must not trigger a row append.

        UptimeRobot's paid tier sends a recognizable UA; the free tier sends
        an empty UA (see test_log_query_skipped_for_empty_ua below).
        """
        from services import query_logger

        ctx = self._mock_context("UptimeRobot/2.0; http://uptimerobot.com/")
        with (
            patch.object(query_logger.st, "context", ctx),
            patch.object(query_logger, "Thread") as mock_thread,
        ):
            query_logger.log_query("anything")
            mock_thread.assert_not_called()

    def test_log_query_skipped_for_empty_ua(self):
        """Empty UA must be treated as bot (UptimeRobot free tier sends empty UA).

        is_bot() short-circuits to True when User-Agent is empty — see the
        comment in services/query_logger.py is_bot().
        """
        from services import query_logger

        ctx = self._mock_context("")
        with (
            patch.object(query_logger.st, "context", ctx),
            patch.object(query_logger, "Thread") as mock_thread,
        ):
            query_logger.log_query("anything")
            mock_thread.assert_not_called()

    def test_log_query_skipped_for_chrome_103(self):
        """The legacy Chrome/103.0.0.0 signature must still suppress logging.

        Chrome/103 is in MONITORING_BOT_SIGNATURES (config/constants.py) as a
        legacy monitoring-bot fingerprint. Keeping this test pins the full
        signature list, not just the modern UAs.
        """
        from services import query_logger

        ctx = self._mock_context(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/103.0.0.0 Safari/537.36"
        )
        with (
            patch.object(query_logger.st, "context", ctx),
            patch.object(query_logger, "Thread") as mock_thread,
        ):
            query_logger.log_query("anything")
            mock_thread.assert_not_called()

    def test_log_query_proceeds_for_real_user_ua(self):
        """A real user UA (Chrome on Mac) MUST trigger a row append.

        Negative control: the bot filter must not be overzealous. If this
        starts failing, the filter has drifted to suppress legitimate traffic.
        """
        from services import query_logger

        ctx = self._mock_context(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/147.0.0.0 Safari/537.36"
        )
        with (
            patch.object(query_logger.st, "context", ctx),
            patch.object(query_logger, "Thread") as mock_thread,
        ):
            query_logger.log_query("How did Matt scale teams?", page="Ask Agy")
            mock_thread.assert_called_once()


class TestLogQueryTopScore:
    """log_query() must record top_score in the Top Score column."""

    REAL_UA = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/147.0.0.0 Safari/537.36"
    )

    def _mock_context(self, user_agent: str) -> MagicMock:
        ctx = MagicMock()
        ctx.headers.get.return_value = user_agent
        ctx.timezone = "America/New_York"
        return ctx

    def _captured_row(self, mock_thread) -> list:
        return mock_thread.call_args.kwargs["args"][0]

    # `test_top_score_is_last_header` retired by MATTGPT-247: it pinned
    # `HEADERS[-1] == "Top Score"` on the premise that Top Score was
    # the most recently appended column. -247 appended `Unassessed
    # Count` and `Failure Type` after it, so that assertion is now
    # false-by-design. The stronger form of the same invariant --
    # Top Score at its historical position (index 32) -- is pinned by
    # TestHeadersPrefixInvariant::test_headers_prefix_matches_historical_snapshot
    # below, which asserts the full 33-entry prefix and catches any
    # mid-list insertion regardless of which column moved.

    def test_top_score_written_when_supplied(self):
        from services import query_logger

        ctx = self._mock_context(self.REAL_UA)
        with (
            patch.object(query_logger.st, "context", ctx),
            patch.object(query_logger, "Thread") as mock_thread,
        ):
            query_logger.log_query("test", top_score=0.847)
            row = self._captured_row(mock_thread)
        from services.query_logger import HEADERS

        assert row[HEADERS.index("Top Score")] == 0.847

    def test_top_score_defaults_to_empty_string(self):
        from services import query_logger

        ctx = self._mock_context(self.REAL_UA)
        with (
            patch.object(query_logger.st, "context", ctx),
            patch.object(query_logger, "Thread") as mock_thread,
        ):
            query_logger.log_query("test")
            row = self._captured_row(mock_thread)
        from services.query_logger import HEADERS

        assert row[HEADERS.index("Top Score")] == ""


# ---------------------------------------------------------------------------
# MATTGPT-247: role_match logger extensions for partial-failure paths
# ---------------------------------------------------------------------------
# Ships the Sheet-side of Cycle 2's partial-failure work. Two new columns
# (Unassessed Count, Failure Type), one new event type
# (role_match_gate_rejection), one signature extension on
# log_role_match_assessment. `unassessed_count` is a correctness fix, not
# additive telemetry: since Cycle 2 shipped, `strong + partial + gap` no
# longer sums to `required + preferred` whenever unassessed rows exist,
# so every Sheet row during a partial outage has been understating the
# total. Same defect class as the three render surfaces (fixed at
# 9b0ddc8), still live in the Sheet.
#
# Failure Type values (three, no empty): `ok`, `gate_rejected`,
# `retrieval_failed`. Empty already carries semantic weight for
# pre-column historical rows; new writes cannot add to that ambiguity.


_REAL_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/147.0.0.0 Safari/537.36"
)


def _mock_real_user_context() -> MagicMock:
    """Shared fixture: st.context mock with a real-user UA so is_bot()
    returns False and the log function proceeds to spawn its write
    thread. Kept module-level rather than as a repeated class method
    so the four new test classes can share it without inheritance."""
    ctx = MagicMock()
    ctx.headers.get.return_value = _REAL_UA
    ctx.timezone = "America/New_York"
    return ctx


def _captured_row(mock_thread) -> list:
    """Extract the row list that would have been written to the sheet
    from a patched Thread's call args.

    Assumes `Thread(target=_append_row, args=(row,), daemon=True)` --
    i.e., `args=` passed as a keyword. If a call site is ever
    refactored to pass `args` positionally, the previous shape
    (`mock_thread.call_args.kwargs["args"][0]`) would raise KeyError
    from the missing kwarg rather than reporting a clear assertion.
    The guard below turns that into an explicit AssertionError with
    the offending call shape so the diagnosis lands at the call site
    that changed, not at the row inspection."""
    call = mock_thread.call_args
    if "args" not in call.kwargs:
        raise AssertionError(
            f"_captured_row expected `Thread(...)` called with `args=` "
            f"as a keyword argument; got call_args={call!r}. If a call "
            f"site was changed to pass `args` positionally, update "
            f"this helper or the caller."
        )
    return call.kwargs["args"][0]


class TestLogRoleMatchAssessmentExtensions:
    """MATTGPT-247: `log_role_match_assessment` gains two required kwargs
    (`unassessed_count`, `failure_type`) and writes them to two new
    HEADERS columns (`Unassessed Count`, `Failure Type`). Success path
    passes `failure_type="ok"`; retrieval-failed path passes
    `failure_type="retrieval_failed"`.

    Tests 2 through 4 check preconditions (signature accepts the kwarg,
    HEADERS carries the column) before exercising the write, so a Red
    state failure lands on the precondition rather than a
    TypeError-from-call or a ValueError-from-index."""

    def test_signature_requires_unassessed_count_and_failure_type(self):
        """Test 1. Both new kwargs must be present in the signature and
        have no default -- a default would let callers who forgot to
        set them silently write `ok` (or 0), which is exactly the
        ambiguity the failure_type field exists to remove."""
        import inspect

        from services.query_logger import log_role_match_assessment

        sig = inspect.signature(log_role_match_assessment)
        params = sig.parameters
        assert "unassessed_count" in params, (
            f"missing 'unassessed_count' parameter on "
            f"log_role_match_assessment; got {list(params.keys())!r}"
        )
        assert "failure_type" in params, (
            f"missing 'failure_type' parameter on "
            f"log_role_match_assessment; got {list(params.keys())!r}"
        )
        assert params["unassessed_count"].default is inspect.Parameter.empty, (
            "'unassessed_count' should have no default so a forgot-to-set "
            "caller is visible at call time; got default "
            f"{params['unassessed_count'].default!r}"
        )
        assert params["failure_type"].default is inspect.Parameter.empty, (
            "'failure_type' should have no default so a forgot-to-set "
            "caller can't silently write 'ok' when it meant to write a "
            "failure value; got default "
            f"{params['failure_type'].default!r}"
        )

    def _call_with_all_kwargs(
        self,
        query_logger,
        mock_thread_target,
        *,
        unassessed_count: int,
        failure_type: str,
    ):
        """Shared call shape for tests 2-4. Fills all required kwargs
        with placeholder values so the tests focus on the two new
        columns rather than repeating the eight existing ones."""
        query_logger.log_role_match_assessment(
            role_title="Test Role",
            company="Test Co",
            jd_format="hybrid",
            required_count=5,
            preferred_count=3,
            strong_count=6,
            partial_count=1,
            gap_count=0,
            unassessed_count=unassessed_count,
            failure_type=failure_type,
        )

    def test_unassessed_count_written_to_correct_column(self):
        """Test 2. Passing `unassessed_count=3` writes `"3"` (str) into
        the `Unassessed Count` column of the built row. Precondition
        checks first so a Red failure lands on missing column / kwarg
        rather than the row inspection."""
        import inspect

        from services import query_logger
        from services.query_logger import HEADERS

        assert (
            "unassessed_count"
            in inspect.signature(query_logger.log_role_match_assessment).parameters
        ), "precondition: signature must accept 'unassessed_count'"
        assert (
            "Unassessed Count" in HEADERS
        ), "precondition: HEADERS must include 'Unassessed Count' column"

        with (
            patch.object(query_logger.st, "context", _mock_real_user_context()),
            patch.object(query_logger, "Thread") as mock_thread,
        ):
            self._call_with_all_kwargs(
                query_logger, mock_thread, unassessed_count=3, failure_type="ok"
            )
            row = _captured_row(mock_thread)

        idx = HEADERS.index("Unassessed Count")
        assert row[idx] == "3", (
            f"expected '3' at 'Unassessed Count' column (index {idx}); "
            f"got {row[idx]!r}"
        )

    def test_failure_type_written_to_correct_column(self):
        """Test 3. Passing `failure_type="retrieval_failed"` writes the
        literal string into the `Failure Type` column."""
        import inspect

        from services import query_logger
        from services.query_logger import HEADERS

        assert (
            "failure_type"
            in inspect.signature(query_logger.log_role_match_assessment).parameters
        ), "precondition: signature must accept 'failure_type'"
        assert (
            "Failure Type" in HEADERS
        ), "precondition: HEADERS must include 'Failure Type' column"

        with (
            patch.object(query_logger.st, "context", _mock_real_user_context()),
            patch.object(query_logger, "Thread") as mock_thread,
        ):
            self._call_with_all_kwargs(
                query_logger,
                mock_thread,
                unassessed_count=0,
                failure_type="retrieval_failed",
            )
            row = _captured_row(mock_thread)

        idx = HEADERS.index("Failure Type")
        assert row[idx] == "retrieval_failed", (
            f"expected 'retrieval_failed' at 'Failure Type' column "
            f"(index {idx}); got {row[idx]!r}"
        )

    def test_failure_type_ok_is_explicit_not_empty(self):
        """Test 4. Success path calls with `failure_type="ok"` write the
        literal string `"ok"`, not `""`. Empty already carries the
        semantic of `"row written before this column existed"` for
        every pre-247 row in the Sheet; new writes must not add to
        that ambiguity."""
        import inspect

        from services import query_logger
        from services.query_logger import HEADERS

        assert (
            "failure_type"
            in inspect.signature(query_logger.log_role_match_assessment).parameters
        ), "precondition: signature must accept 'failure_type'"
        assert (
            "Failure Type" in HEADERS
        ), "precondition: HEADERS must include 'Failure Type' column"

        with (
            patch.object(query_logger.st, "context", _mock_real_user_context()),
            patch.object(query_logger, "Thread") as mock_thread,
        ):
            self._call_with_all_kwargs(
                query_logger, mock_thread, unassessed_count=0, failure_type="ok"
            )
            row = _captured_row(mock_thread)

        idx = HEADERS.index("Failure Type")
        assert row[idx] == "ok", (
            f"success path must write 'ok' literal at 'Failure Type' "
            f"column (index {idx}), not empty string -- empty carries "
            f"'column did not exist yet' for pre-247 rows and new "
            f"writes must not add to that ambiguity; got {row[idx]!r}"
        )

    # ----- Per-category count columns (Sheet reads required vs preferred) -----
    #
    # -247 shipped four combined count columns (`Strong Count`,
    # `Partial Count`, `Gap Count`, `Unassessed Count`) that sum
    # required + preferred. The Sheet cannot distinguish
    # required-strong from preferred-strong from those columns alone,
    # which is the distinction fit assessment actually turns on.
    # This ticket adds eight per-category columns alongside the four
    # combined ones. `_build_role_match_log_kwargs` derives all
    # twelve from the same `compute_summary_counts` pass; the
    # signature and column-write tests below pin the wire path.

    _NEW_PER_CATEGORY_KWARGS = (
        "required_strong_count",
        "required_partial_count",
        "required_gap_count",
        "required_unassessed_count",
        "preferred_strong_count",
        "preferred_partial_count",
        "preferred_gap_count",
        "preferred_unassessed_count",
    )

    _NEW_PER_CATEGORY_COLUMNS = (
        "Required Strong Count",
        "Required Partial Count",
        "Required Gap Count",
        "Required Unassessed Count",
        "Preferred Strong Count",
        "Preferred Partial Count",
        "Preferred Gap Count",
        "Preferred Unassessed Count",
    )

    def test_signature_requires_eight_per_category_count_kwargs(self):
        """All eight per-category kwargs must be present in the
        signature and have no defaults. Same forgot-to-set discipline
        as `unassessed_count` and `failure_type`: a default lets a
        caller silently pass 0 for a category count when it meant to
        derive from real data."""
        import inspect

        from services.query_logger import log_role_match_assessment

        sig = inspect.signature(log_role_match_assessment)
        params = sig.parameters
        for kwarg in self._NEW_PER_CATEGORY_KWARGS:
            assert kwarg in params, (
                f"missing {kwarg!r} parameter on "
                f"log_role_match_assessment; got {list(params.keys())!r}"
            )
            assert params[kwarg].default is inspect.Parameter.empty, (
                f"{kwarg!r} should have no default so a forgot-to-set "
                f"caller is visible at call time; got default "
                f"{params[kwarg].default!r}"
            )

    def test_per_category_kwargs_land_in_correct_columns(self):
        """Each of the eight per-category kwargs must land in its
        corresponding HEADERS column. Uses eight unique sentinel
        values across all eight columns so a same-status swap (e.g.,
        Green wires `required_strong_count` into `Preferred Strong
        Count` by copy-paste error) is caught. Reused sentinels per
        status would pass on such a swap and silently ship a
        mis-wired column."""
        import inspect

        from services import query_logger
        from services.query_logger import HEADERS

        # Preconditions: signature and HEADERS must have the new
        # kwargs / columns.
        sig_params = inspect.signature(
            query_logger.log_role_match_assessment
        ).parameters
        for kwarg in self._NEW_PER_CATEGORY_KWARGS:
            assert kwarg in sig_params, f"precondition: signature must accept {kwarg!r}"
        for col in self._NEW_PER_CATEGORY_COLUMNS:
            assert col in HEADERS, f"precondition: HEADERS must include {col!r} column"

        # Eight unique sentinels, one per (category, status) pair.
        # 100-series for required, 200-series for preferred; status
        # varies within each series so no two kwargs share a value.
        sentinels = {
            "required_strong_count": 101,
            "required_partial_count": 102,
            "required_gap_count": 103,
            "required_unassessed_count": 104,
            "preferred_strong_count": 201,
            "preferred_partial_count": 202,
            "preferred_gap_count": 203,
            "preferred_unassessed_count": 204,
        }
        col_for_kwarg = dict(
            zip(
                self._NEW_PER_CATEGORY_KWARGS,
                self._NEW_PER_CATEGORY_COLUMNS,
                strict=False,
            )
        )

        with (
            patch.object(query_logger.st, "context", _mock_real_user_context()),
            patch.object(query_logger, "Thread") as mock_thread,
        ):
            query_logger.log_role_match_assessment(
                role_title="Test Role",
                company="Test Co",
                jd_format="hybrid",
                required_count=410,  # 101 + 102 + 103 + 104
                preferred_count=810,  # 201 + 202 + 203 + 204
                strong_count=302,  # 101 + 201
                partial_count=304,  # 102 + 202
                gap_count=306,  # 103 + 203
                unassessed_count=308,  # 104 + 204
                failure_type="ok",
                **sentinels,
            )
            row = _captured_row(mock_thread)

        for kwarg, sentinel in sentinels.items():
            col = col_for_kwarg[kwarg]
            idx = HEADERS.index(col)
            assert row[idx] == str(sentinel), (
                f"kwarg {kwarg!r}={sentinel} should land at column "
                f"{col!r} (index {idx}). Got {row[idx]!r}. If a value "
                f"from another sentinel appeared here, Green wired "
                f"the wrong kwarg into this column -- classic same-"
                f"status swap (required_strong <-> preferred_strong)."
            )


class TestLogRoleMatchGateRejection:
    """MATTGPT-247: `log_role_match_gate_rejection()` is a new
    zero-argument function for the gate-rejected event. Distinct Event
    Type (`role_match_gate_rejection`), Failure Type `gate_rejected`,
    all six count columns explicit `"0"` (not empty). Gate rejection
    is a different event shape from an assessment -- no requirements
    extracted, no counts, the visitor never got a result -- so it
    lives as its own event type rather than being pretended into the
    assessment shape."""

    def test_gate_rejection_writes_distinct_event_type(self):
        """Test 5. Event Type column carries the distinct literal
        `"role_match_gate_rejection"`, not the assessment event type."""
        from services import query_logger
        from services.query_logger import HEADERS

        with (
            patch.object(query_logger.st, "context", _mock_real_user_context()),
            patch.object(query_logger, "Thread") as mock_thread,
        ):
            query_logger.log_role_match_gate_rejection()
            row = _captured_row(mock_thread)

        idx = HEADERS.index("Event Type")
        assert row[idx] == "role_match_gate_rejection", (
            f"expected Event Type 'role_match_gate_rejection' (distinct "
            f"from 'role_match_assessment'); got {row[idx]!r}"
        )

    def test_gate_rejection_sets_failure_type_and_zero_counts(self):
        """Test 6. Failure Type is `"gate_rejected"` and all six count
        columns (five original + Unassessed Count) are explicit `"0"`,
        not empty. Same ambiguity rule as test 4: empty would collide
        with pre-247 rows."""
        from services import query_logger
        from services.query_logger import HEADERS

        assert (
            "Failure Type" in HEADERS
        ), "precondition: HEADERS must include 'Failure Type' column"
        assert (
            "Unassessed Count" in HEADERS
        ), "precondition: HEADERS must include 'Unassessed Count' column"

        with (
            patch.object(query_logger.st, "context", _mock_real_user_context()),
            patch.object(query_logger, "Thread") as mock_thread,
        ):
            query_logger.log_role_match_gate_rejection()
            row = _captured_row(mock_thread)

        assert row[HEADERS.index("Failure Type")] == "gate_rejected", (
            f"expected Failure Type 'gate_rejected'; got "
            f"{row[HEADERS.index('Failure Type')]!r}"
        )
        # Precondition: HEADERS must include the eight per-category
        # count columns. Without this, the loop below would raise
        # ValueError from HEADERS.index() rather than a clean
        # assertion. Same precondition pattern as -247's Test 2/3.
        for new_col in (
            "Required Strong Count",
            "Required Partial Count",
            "Required Gap Count",
            "Required Unassessed Count",
            "Preferred Strong Count",
            "Preferred Partial Count",
            "Preferred Gap Count",
            "Preferred Unassessed Count",
        ):
            assert (
                new_col in HEADERS
            ), f"precondition: HEADERS must include {new_col!r} column"
        for col in (
            "Required Count",
            "Preferred Count",
            "Strong Count",
            "Partial Count",
            "Gap Count",
            "Unassessed Count",
            # Per-category columns added alongside the four combined
            # counts. Same ambiguity rule as above: empty carries
            # "column did not exist yet" for historical rows, so a
            # gate-rejection row must write explicit "0" on every
            # count column, not skip the eight new ones.
            "Required Strong Count",
            "Required Partial Count",
            "Required Gap Count",
            "Required Unassessed Count",
            "Preferred Strong Count",
            "Preferred Partial Count",
            "Preferred Gap Count",
            "Preferred Unassessed Count",
        ):
            idx = HEADERS.index(col)
            assert row[idx] == "0", (
                f"expected explicit '0' at {col!r} column (index {idx}) "
                f"on gate-rejection row -- empty would collide with "
                f"pre-247 rows where the column did not exist yet; "
                f"got {row[idx]!r}"
            )


class TestHeadersPrefixInvariant:
    """MATTGPT-247 + MATTGPT-086: `HEADERS` grows by appending only,
    never mid-list. This class pins that Green appends rather than
    inserting.

    Two tests together cover the -086 failure mode:

    1. `test_headers_prefix_matches_historical_snapshot` pins the
       historical prefix at 35 entries. Prefix, not suffix -- a
       suffix assertion still passes when someone inserts at index
       10 and shifts everything down, which is exactly the -086
       failure. The prefix comparison catches insertions or renames
       within positions 0-34.

    2. `test_headers_length_matches_current_schema` pins the current
       total length. Catches insertions, removals, or additions at
       any position that the prefix doesn't cover -- including
       positions 35+ where Env and any subsequent columns live
       outside the historical prefix.

    Snapshot is frozen at 35 (state as of -086's landing) and does
    NOT extend for new columns. The pattern of "extend the snapshot
    on the next ticket's Red" was retired -- an ever-growing
    snapshot ends up as a running count, not a historical record.
    New-column additions are covered by the length pin, which
    updates once as part of the ticket that adds them; the prefix
    stays put."""

    # Frozen snapshot of HEADERS as of Sept 16, 2026 (35 entries,
    # pre-086 Green). Produced by piping HEADERS through Python and
    # copying the literal output, not transcribed by hand, to avoid
    # encoding a typo as the historical record:
    #
    #   python3 -c "from services.query_logger import HEADERS; \
    #     [print(repr(h) + ',') for h in HEADERS]"
    #
    # Every write in the production Sheet up to this date has this
    # column order; any mid-list insertion changes the meaning of
    # historical data.
    _HEADERS_HISTORICAL_SNAPSHOT = (
        "Event Type",
        "Timestamp",
        "Query",
        "Page",
        "Intent Family",
        "Confidence",
        "Result Count",
        "Redirect Reason",
        "User-Agent",
        "Screen Width",
        "Timezone",
        "Referrer",
        "Sources",
        "Rating",
        "Turn Index",
        "Msg Hash",
        "UTM Source",
        "UTM Medium",
        "UTM Campaign",
        "UTM Content",
        "UTM Term",
        "Role Title",
        "Company",
        "JD Format",
        "Required Count",
        "Preferred Count",
        "Strong Count",
        "Partial Count",
        "Gap Count",
        "Session ID",
        "Story Title",
        "Client",
        "Top Score",
        "Unassessed Count",
        "Failure Type",
    )

    def test_headers_prefix_matches_historical_snapshot(self):
        """`HEADERS[:35]` must exactly match the frozen snapshot.
        Passes today (HEADERS length 35) and after -086 Green
        (Green appends `Env`, doesn't insert). Fails if someone
        inserts `"Env"` mid-list to group it with related columns,
        which is a defensible instinct but breaks every historical
        row's column semantics."""
        from services.query_logger import HEADERS

        n = len(self._HEADERS_HISTORICAL_SNAPSHOT)
        actual_prefix = tuple(HEADERS[:n])
        assert actual_prefix == self._HEADERS_HISTORICAL_SNAPSHOT, (
            f"HEADERS[:{n}] does not match the historical snapshot. "
            f"New columns must be APPENDED, not inserted -- a mid-list "
            f"insertion changes the column position of every historical "
            f"row in the Sheet. Diff:\n"
            f"  expected: {self._HEADERS_HISTORICAL_SNAPSHOT!r}\n"
            f"  actual:   {actual_prefix!r}"
        )

    # Current-schema length pin. Updated ONCE, as part of the ticket
    # that adds columns. Together with the frozen prefix above:
    #   - Prefix pins positions 0-34 by name and order.
    #   - Length pins the total count.
    # Combined, an insert/remove/rename anywhere in HEADERS is caught:
    # positions 0-34 by prefix; positions 35+ by length change.
    _CURRENT_SCHEMA_LENGTH = 36

    def test_headers_length_matches_current_schema(self):
        """Length pin. Passes when `len(HEADERS)` equals the schema
        length declared here. Fails when a column is added, removed,
        or the schema drifts. Update `_CURRENT_SCHEMA_LENGTH` above
        as part of the ticket that changed HEADERS.

        Rationale: the historical prefix at 35 does not cover
        positions 35+ (Env and beyond). Without this pin, an insert
        after position 34 shifts every subsequent column silently --
        the exact -086 failure mode. This pin catches it because
        insertion changes the total count."""
        from services.query_logger import HEADERS

        assert len(HEADERS) == self._CURRENT_SCHEMA_LENGTH, (
            f"HEADERS length changed unexpectedly: got {len(HEADERS)}, "
            f"pin expects {self._CURRENT_SCHEMA_LENGTH}. If this is "
            f"intentional (a ticket added/removed columns), update "
            f"_CURRENT_SCHEMA_LENGTH above as part of the same commit "
            f"that changed HEADERS. If this fired unexpectedly, "
            f"something inserted or removed a column mid-list and the "
            f"prefix invariant may also be affected."
        )


class TestEnvInjection:
    """MATTGPT-086: `_build_row` injects the `Env` column from
    `get_conf("MATTGPT_ENV", "local")` at row-build time, so every
    caller inherits the environment stamp without call-site changes.

    Two tests pin the injection: one for the set case (MATTGPT_ENV
    provided) and one for the unset case (default fires). The
    default-fires test is the substitute for the startup validation
    scope that was dropped from -086; if MATTGPT_ENV is missing in
    Cloud secrets or the .env file, rows carry `"local"` explicitly
    rather than empty."""

    def test_build_row_injects_env_from_get_conf_when_set(self, monkeypatch):
        """Set MATTGPT_ENV to a distinctive value, call `_build_row`,
        assert the Env column carries that value. `get_conf` in bare
        mode (pytest without Streamlit runtime) skips st.secrets
        entirely and reads os.getenv directly (see MATTGPT-216 fix
        in config/settings.py), so monkeypatch.setenv is
        deterministic."""
        from services.query_logger import HEADERS, _build_row

        assert "Env" in HEADERS, "precondition: HEADERS must include 'Env' column"

        monkeypatch.setenv("MATTGPT_ENV", "test-env-value")
        row = _build_row("test_event")

        assert row[HEADERS.index("Env")] == "test-env-value", (
            f"expected 'test-env-value' at Env column "
            f"(index {HEADERS.index('Env')}); got "
            f"{row[HEADERS.index('Env')]!r}"
        )

    def test_build_row_env_defaults_to_local_when_var_unset(self, monkeypatch):
        """Unset MATTGPT_ENV, call `_build_row`, assert Env carries
        `"local"` (the get_conf default). Substitute for the
        startup-validation scope dropped from -086: if the Cloud
        secret is missing, the default fires rather than the row
        carrying an empty cell."""
        from services.query_logger import HEADERS, _build_row

        assert "Env" in HEADERS, "precondition: HEADERS must include 'Env' column"

        monkeypatch.delenv("MATTGPT_ENV", raising=False)
        row = _build_row("test_event")

        assert row[HEADERS.index("Env")] == "local", (
            f"expected 'local' default at Env column "
            f"(index {HEADERS.index('Env')}) when MATTGPT_ENV is "
            f"unset; got {row[HEADERS.index('Env')]!r}"
        )


class TestBuildRoleMatchLogKwargsArithmeticInvariant:
    """MATTGPT-247 correctness fix. Since Cycle 2's producer added
    unassessed rows as a first-class status, the log call must count
    them into `unassessed_count`. This class pins the invariant
    `strong + partial + gap + unassessed == required + preferred`
    over `_build_role_match_log_kwargs`, which is the helper Green
    extracts from the inline submit-branch counting logic.

    Property-flavored: iterates three representative payloads (mixed,
    all-unassessed, no-unassessed) so the invariant is proven over
    varied count shapes rather than one fixture with specific
    numbers. Deliberately skips the all-zeros gate-rejection case
    where `0 + 0 + 0 + 0 == 0 + 0` is trivially true.

    See the failure-message assertion for what this test does and
    doesn't catch."""

    @staticmethod
    def _row(category: str, match_status: str, text: str = "Some req") -> dict:
        """Build a synthetic results-list row for the helper. Shape
        matches what run_assessment produces per requirement."""
        return {
            "category": category,
            "requirement": text,
            "match_status": match_status,
            "evidence": [],
            "gap_explanation": "",
        }

    def test_arithmetic_invariant_holds_across_payloads(self):
        """Test 8. Over three assessment-shape payloads, the log
        kwargs satisfy `strong + partial + gap + unassessed ==
        required + preferred`. Not universal: gate-rejection rows are
        all-zeros and trivially satisfy the invariant, so they're
        excluded. Extractor-vs-results mismatches (a row lost between
        extraction and results) are NOT covered here -- see
        test_run_assessment_loop.py::TestRunAssessmentLoop::
        test_result_length_equals_requirement_count for that gap."""
        from ui.pages.role_match import _build_role_match_log_kwargs

        payloads = [
            (
                "mixed",
                [
                    self._row("required", "strong"),
                    self._row("required", "strong"),
                    self._row("required", "partial"),
                    self._row("required", "unassessed"),
                    self._row("required", "gap"),
                    self._row("preferred", "partial"),
                    self._row("preferred", "unassessed"),
                    self._row("preferred", "strong"),
                ],
            ),
            (
                "all_unassessed",
                [self._row("required", "unassessed") for _ in range(4)]
                + [self._row("preferred", "unassessed") for _ in range(2)],
            ),
            (
                "no_unassessed",
                [
                    self._row("required", "strong"),
                    self._row("required", "gap"),
                    self._row("preferred", "partial"),
                ],
            ),
        ]

        for payload_name, results in payloads:
            counts = _build_role_match_log_kwargs({}, results)
            lhs = (
                counts["strong_count"]
                + counts["partial_count"]
                + counts["gap_count"]
                + counts["unassessed_count"]
            )
            rhs = counts["required_count"] + counts["preferred_count"]
            assert lhs == rhs, (
                f"[{payload_name}] arithmetic invariant broken: "
                f"strong+partial+gap+unassessed={lhs} != "
                f"required+preferred={rhs}\n"
                f"\n"
                f"This helper derives both sides from "
                f"`compute_summary_counts`, so the invariant holds by "
                f"construction as long as all four statuses are "
                f"forwarded to the log kwargs. If it fires, someone "
                f"added a new status to `compute_summary_counts` "
                f"without forwarding it (unassessed_count was that "
                f"class of miss, before this ticket), or the helper "
                f"stopped deriving both sides from the same pass.\n"
                f"\n"
                f"Deliberately NOT a check for extractor-vs-results "
                f"mismatches: both sides come from the same "
                f"`compute_summary_counts` pass, so a row that went "
                f"missing between extraction and results would leave "
                f"the invariant intact while a row is lost. That case "
                f"is covered by test_run_assessment_loop.py::"
                f"TestRunAssessmentLoop::"
                f"test_result_length_equals_requirement_count.\n"
                f"\n"
                f"Counts: {counts!r}"
            )

            # Per-status split invariant: for each status, the combined
            # count must equal required + preferred for that status.
            # Catches a Green that computes the four combined columns
            # correctly (the invariant above still holds) but swaps or
            # miswires the eight new per-category kwargs. Without
            # this, a swap between required_strong_count and
            # preferred_strong_count leaves combined strong_count
            # correct and the whole-total invariant intact, but the
            # per-category columns on the Sheet mislead the recruiter
            # analyst about where the strong matches actually landed.
            #
            # Precondition: the eight per-category keys must be
            # present in the helper's return dict. Without this
            # check the split loop would raise KeyError rather than
            # a clean assertion.
            for status in ("strong", "partial", "gap", "unassessed"):
                for key_name in (
                    f"required_{status}_count",
                    f"preferred_{status}_count",
                ):
                    assert key_name in counts, (
                        f"[{payload_name}] precondition: helper must "
                        f"return {key_name!r} key. Got keys: "
                        f"{sorted(counts.keys())!r}"
                    )
            for status in ("strong", "partial", "gap", "unassessed"):
                combined = counts[f"{status}_count"]
                required = counts[f"required_{status}_count"]
                preferred = counts[f"preferred_{status}_count"]
                assert combined == required + preferred, (
                    f"[{payload_name}] per-status split invariant "
                    f"broken for {status!r}: combined "
                    f"{status}_count={combined} != "
                    f"required_{status}_count={required} + "
                    f"preferred_{status}_count={preferred}. "
                    f"Either the combined count is wrong, one of the "
                    f"per-category counts is wrong, or they were "
                    f"derived from different passes over the results "
                    f"list. Full counts: {counts!r}"
                )
