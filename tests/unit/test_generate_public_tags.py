"""Unit tests for generate_public_tags.py (MATTGPT-211).

Scope: the backup step at line 184. The bug: shutil.copy(INPUT_FILE, backup_file)
copies the raw echo_star_stories.jsonl (never overwritten) instead of the
echo_star_stories_nlp.jsonl (destroyed on line 188). Fix backs up OUTPUT_FILE
with an existence guard for first runs.

These tests mock the OpenAI client and the input() prompt to exercise the real
enrich_stories_with_nlp_tags() flow end-to-end against tmp files. No paid API
calls; no repo-file writes.
"""

from unittest.mock import MagicMock

import pytest


class TestGeneratePublicTagsBackup:
    """MATTGPT-211: backup at line 184 must copy OUTPUT_FILE, not INPUT_FILE."""

    @pytest.fixture
    def stubbed_env(self, monkeypatch, tmp_path):
        """Point module constants at tmp files; mock input() and OpenAI client.

        Uses bare filenames + chdir to mirror production (script runs from repo
        root with bare filenames; ARCHIVE_BACKUPS_DIR resolves as a relative
        Path). Passing absolute paths breaks the backup-filename construction
        because Path / absolute_path ignores the left side.

        Returns (module, input_path, output_path, backups_dir). Caller populates
        input_path and optionally output_path.
        """
        import generate_public_tags as g

        input_name = "echo_star_stories.jsonl"
        output_name = "echo_star_stories_nlp.jsonl"
        input_path = tmp_path / input_name
        output_path = tmp_path / output_name
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(g, "INPUT_FILE", input_name)
        monkeypatch.setattr(g, "OUTPUT_FILE", output_name)
        # ARCHIVE_BACKUPS_DIR is a Path -- keep it relative so bare-filename
        # concatenation resolves under our tmp cwd
        monkeypatch.setattr(g, "ARCHIVE_BACKUPS_DIR", g.Path("backups"))

        # Auto-confirm the cost/count prompt
        monkeypatch.setattr("builtins.input", lambda _prompt="": "y")

        # Mock OpenAI so no API call fires
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content="freshly-generated-tag"))
        ]
        monkeypatch.setattr(
            g.client.chat.completions,
            "create",
            lambda **_kw: mock_completion,
        )

        return g, input_path, output_path, backups_dir

    def test_backup_contains_output_file_content_not_input(self, stubbed_env):
        """Backup file must be a byte-for-byte copy of OUTPUT_FILE (the file
        about to be overwritten), not INPUT_FILE (which is only read)."""
        g, input_path, output_path, backups_dir = stubbed_env

        # Distinct content in each file so a wrong-source copy is provable
        input_content = '{"id": "s1", "Title": "Raw from Excel"}\n'
        prior_output_content = (
            '{"id": "s1", "Title": "Prior enriched",'
            ' "public_tags": "prior-tag-one, prior-tag-two"}\n'
        )
        input_path.write_text(input_content, encoding="utf-8")
        output_path.write_text(prior_output_content, encoding="utf-8")

        g.enrich_stories_with_nlp_tags()

        backup_files = list(backups_dir.glob("*_backup_*.jsonl"))
        assert len(backup_files) == 1, (
            f"Expected exactly 1 backup file, got {len(backup_files)}: "
            f"{[p.name for p in backup_files]}"
        )
        backup_bytes = backup_files[0].read_bytes()
        assert backup_bytes == prior_output_content.encode("utf-8"), (
            "Backup must preserve OUTPUT_FILE (the file being overwritten). "
            f"Got backup matching {'INPUT_FILE' if backup_bytes == input_content.encode('utf-8') else 'neither'}."
        )

    def test_first_run_with_no_prior_output_does_not_fail(self, stubbed_env):
        """First run has no OUTPUT_FILE to back up. Script must not raise; no
        backup file should be created; the OUTPUT_FILE gets written fresh."""
        g, input_path, output_path, backups_dir = stubbed_env

        input_path.write_text(
            '{"id": "s1", "Title": "Raw from Excel"}\n', encoding="utf-8"
        )
        # Do NOT create output_path -- simulate first-ever run
        assert not output_path.exists()

        # Should not raise
        g.enrich_stories_with_nlp_tags()

        backup_files = list(backups_dir.glob("*_backup_*.jsonl"))
        assert len(backup_files) == 0, (
            f"No backup should be created on first run (no OUTPUT_FILE to back up); "
            f"got {[p.name for p in backup_files]}"
        )
        assert output_path.exists(), "OUTPUT_FILE should be written on first run"
