"""Unit tests for services.query_logger bot-filter behavior.

Why this exists: until May 13, 2026, log_query() had no bot filter. The
page_load path was guarded in app.py (MONITORING_BOT_SIGNATURES check) and
the role_match path was guarded at call sites (is_bot() in role_match.py
and action_buttons.py), but log_query() — used by Ask Agy and Explore
Stories — logged unconditionally. Result: HeadlessChrome and UptimeRobot
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
        send real queries (e.g., "banking" on Explore Stories). Pre-fix, those
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
            query_logger.log_query("banking", page="Explore Stories")
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
