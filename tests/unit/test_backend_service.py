"""
Unit tests for backend_service.py

Tests for log_offdomain() and send_to_backend().
"""

from unittest.mock import patch

import pytest


class TestLogOffdomain:
    """Tests for log_offdomain() function."""

    def test_logs_to_csv(self, tmp_path):
        """Should append query to CSV file."""
        try:
            from ui.pages.ask_mattgpt.backend_service import log_offdomain
        except ImportError:
            pytest.skip("log_offdomain not available")

        csv_path = tmp_path / "offdomain.csv"
        log_offdomain("test query", "nonsense", path=str(csv_path))

        assert csv_path.exists()
        content = csv_path.read_text()
        assert "test query" in content
        assert "nonsense" in content

    def test_creates_file_with_headers(self, tmp_path):
        """Should create file with headers if it doesn't exist."""
        try:
            from ui.pages.ask_mattgpt.backend_service import log_offdomain
        except ImportError:
            pytest.skip("log_offdomain not available")

        csv_path = tmp_path / "new_offdomain.csv"
        log_offdomain("first query", "rule:profanity", path=str(csv_path))

        content = csv_path.read_text()
        lines = content.strip().split("\n")

        # Should have header + 1 data row
        assert len(lines) == 2
        assert "ts_utc" in lines[0]
        assert "query" in lines[0]
        assert "reason" in lines[0]

    def test_appends_to_existing_file(self, tmp_path):
        """Should append to existing file without adding new headers."""
        try:
            from ui.pages.ask_mattgpt.backend_service import log_offdomain
        except ImportError:
            pytest.skip("log_offdomain not available")

        csv_path = tmp_path / "append_test.csv"

        # Log first query
        log_offdomain("query 1", "reason 1", path=str(csv_path))

        # Log second query
        log_offdomain("query 2", "reason 2", path=str(csv_path))

        content = csv_path.read_text()
        lines = content.strip().split("\n")

        # Should have 1 header + 2 data rows
        assert len(lines) == 3
        assert "query 1" in content
        assert "query 2" in content


class TestSendToBackend:
    """Tests for send_to_backend() legacy wrapper."""

    def test_delegates_to_agy_answer(self, sample_stories, mock_streamlit):
        """Should delegate to agy_answer() (MATTGPT-275)."""
        with patch("ui.pages.ask_mattgpt.backend_service.agy_answer") as mock_agy:
            mock_agy.return_value = {
                "answer_md": "test",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }

            from ui.pages.ask_mattgpt.backend_service import send_to_backend

            result = send_to_backend(
                prompt="test", filters={}, ctx=None, stories=sample_stories
            )

            # filters and ctx are dropped; history comes from ask_transcript
            # (MATTGPT-273), none here.
            mock_agy.assert_called_once_with(
                "test", sample_stories, history=[], on_delta=None
            )
            assert result["answer_md"] == "test"
