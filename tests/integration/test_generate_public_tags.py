"""End-to-end tests for generate_public_tags.py.

MATTGPT-216 (Aug 28, 2026): moved from tests/unit/ to tests/integration/
because these tests import generate_public_tags at the top of their
fixtures, which triggers the script's eager OpenAI(api_key=...) client
construction at module load. That construction is correct for the
script's real invocation (`python generate_public_tags.py` fails loud
when the key is missing) but incompatible with a hermetic CI unit gate.

These tests mock the OpenAI client method before any real call fires, so
they do not hit the network -- but they DO require the module to import,
which requires OPENAI_API_KEY to be present in the environment
(any value; the SDK validates presence at construction, not validity).
Locally, .env supplies this; the pre-push hook picks them up. GH Actions
CI runs only tests/unit/ and does not carry the key.

No `pytestmark` here -- the directory placement is the signal ("this
lives in integration"). The `network` marker is reserved for tests that
hit real external services; these mock everything.

Test coverage preserved:
- MATTGPT-211 backup contract (was TestGeneratePublicTagsBackup)
- MATTGPT-072 skip-unchanged logic (was TestSkipUnchangedStories)
"""

import json
from types import SimpleNamespace
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
            MagicMock(message=MagicMock(content='{"tags": ["freshly-generated-tag"]}'))
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


class TestSkipUnchangedStories:
    """MATTGPT-072 Change 2: skip stories whose _prompt_view is unchanged
    against the prior OUTPUT_FILE. Copy prior public_tags forward, no API
    call. First-run empty-dict fallback. public_tags excluded from the
    comparison (matches generate_jsonl_from_excel.py's diff-loop convention).
    """

    @pytest.fixture
    def env(self, monkeypatch, tmp_path):
        """Like TestGeneratePublicTagsBackup.stubbed_env but exposes
        mock_create so tests can assert on API call counts.
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
        monkeypatch.setattr(g, "ARCHIVE_BACKUPS_DIR", g.Path("backups"))
        monkeypatch.setattr("builtins.input", lambda _prompt="": "y")

        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content='{"tags": ["freshly-generated-tag"]}'))
        ]
        mock_create = MagicMock(return_value=mock_completion)
        monkeypatch.setattr(g.client.chat.completions, "create", mock_create)

        return SimpleNamespace(
            g=g,
            input_path=input_path,
            output_path=output_path,
            backups_dir=backups_dir,
            mock_create=mock_create,
        )

    @staticmethod
    def _write_jsonl(path, records):
        with open(path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

    @staticmethod
    def _read_jsonl(path):
        with open(path, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def test_no_api_calls_when_every_story_matches_prior(self, env):
        """3 stories, prior output has 3 identical prompt-views, input has
        non-empty public_tags. Zero API calls; input.public_tags carried
        forward on skip (Excel is authoritative, MATTGPT-072)."""
        input_records = [
            {"id": "s1", "Title": "A", "Situation": ["ax"], "public_tags": "input-s1"},
            {"id": "s2", "Title": "B", "Situation": ["bx"], "public_tags": "input-s2"},
            {"id": "s3", "Title": "C", "Situation": ["cx"], "public_tags": "input-s3"},
        ]
        prior_records = [
            {
                **{k: v for k, v in r.items() if k != "public_tags"},
                "public_tags": f"prior-{r['id']}",
            }
            for r in input_records
        ]
        self._write_jsonl(env.input_path, input_records)
        self._write_jsonl(env.output_path, prior_records)

        env.g.enrich_stories_with_nlp_tags()

        assert env.mock_create.call_count == 0, (
            f"No LLM calls expected when all prompt-views match prior; "
            f"got {env.mock_create.call_count}"
        )
        # Post-processing title-cases every tag; check content survives
        # case-insensitively so this test doesn't fight the normalizer.
        out = {r["id"]: r for r in self._read_jsonl(env.output_path)}
        for sid in ("s1", "s2", "s3"):
            assert out[sid]["public_tags"].lower() == f"input-{sid}", (
                f"Input.public_tags must carry forward on skip (Excel authoritative); "
                f"{sid} got {out[sid]['public_tags']!r}"
            )

    def test_api_called_only_for_changed_stories(self, env):
        """3 stories, prior has s1 and s3 matching but s2's Title changed.
        Expect exactly 1 API call. s1 and s3 keep input.public_tags (Excel
        authoritative on skip); s2 gets the freshly-generated tag merged
        with its input tag."""
        input_records = [
            {
                "id": "s1",
                "Title": "A",
                "Situation": ["ax"],
                "public_tags": "input-s1",
            },
            {
                "id": "s2",
                "Title": "B-CHANGED",
                "Situation": ["bx"],
                "public_tags": "input-s2",
            },
            {
                "id": "s3",
                "Title": "C",
                "Situation": ["cx"],
                "public_tags": "input-s3",
            },
        ]
        prior_records = [
            {
                "id": "s1",
                "Title": "A",
                "Situation": ["ax"],
                "public_tags": "prior-s1",
            },
            {
                "id": "s2",
                "Title": "B",
                "Situation": ["bx"],
                "public_tags": "prior-s2",
            },
            {
                "id": "s3",
                "Title": "C",
                "Situation": ["cx"],
                "public_tags": "prior-s3",
            },
        ]
        self._write_jsonl(env.input_path, input_records)
        self._write_jsonl(env.output_path, prior_records)

        env.g.enrich_stories_with_nlp_tags()

        assert env.mock_create.call_count == 1, (
            f"Expected 1 LLM call (only s2 changed); "
            f"got {env.mock_create.call_count}"
        )
        out = {r["id"]: r for r in self._read_jsonl(env.output_path)}
        # Post-processing normalizes all tags regardless of source; check
        # content survives case-insensitively.
        assert out["s1"]["public_tags"].lower() == "input-s1"
        assert out["s3"]["public_tags"].lower() == "input-s3"
        s2_tags_lower = out["s2"]["public_tags"].lower()
        assert "freshly-generated-tag" in s2_tags_lower, (
            f"s2 should have the fresh LLM-generated tag; "
            f"got {out['s2']['public_tags']!r}"
        )
        assert "input-s2" in s2_tags_lower, (
            f"s2's input.public_tags must survive the re-tag merge (union); "
            f"got {out['s2']['public_tags']!r}"
        )

    def test_first_run_no_prior_calls_llm_for_all_stories(self, env):
        """No prior OUTPUT_FILE. Every input story goes through the LLM
        (empty-dict fallback for the prior lookup)."""
        input_records = [
            {"id": "s1", "Title": "A", "Situation": ["ax"]},
            {"id": "s2", "Title": "B", "Situation": ["bx"]},
        ]
        self._write_jsonl(env.input_path, input_records)
        assert not env.output_path.exists()

        env.g.enrich_stories_with_nlp_tags()

        assert env.mock_create.call_count == 2, (
            f"First run should tag all {len(input_records)} stories; "
            f"got {env.mock_create.call_count} LLM calls"
        )

    def test_public_tags_change_alone_does_not_trigger_retag(self, env):
        """Only public_tags differs between input and prior; all prompt-view
        fields identical. Skip fires (no LLM call); input.public_tags carries
        forward (Excel authoritative on skip, MATTGPT-072)."""
        input_record = {
            "id": "s1",
            "Title": "T",
            "Situation": ["s"],
            "public_tags": "excel-tag-updated",
        }
        prior_record = {
            "id": "s1",
            "Title": "T",
            "Situation": ["s"],
            "public_tags": "prior-generated-tag",
        }
        self._write_jsonl(env.input_path, [input_record])
        self._write_jsonl(env.output_path, [prior_record])

        env.g.enrich_stories_with_nlp_tags()

        assert env.mock_create.call_count == 0, (
            "public_tags must be excluded from the change-detection comparison; "
            "skip should fire when prompt-view fields are identical"
        )
        out = self._read_jsonl(env.output_path)
        assert out[0]["public_tags"].lower() == "excel-tag-updated", (
            f"Input.public_tags must carry forward on skip (Excel authoritative); "
            f"got {out[0]['public_tags']!r}"
        )

    def test_situation_second_item_change_triggers_retag(self, env):
        """Change 1 + Change 2 interaction: a change ONLY in Situation[1]
        must trigger a retag once _prompt_view reads the full Situation.
        Under the pre-Change-1 behavior (Situation[0] only), this edit
        would be invisible to the change-detector -- silent-skip failure."""
        input_record = {
            "id": "s1",
            "Title": "T",
            "Situation": ["first paragraph", "second paragraph EDITED"],
        }
        prior_record = {
            "id": "s1",
            "Title": "T",
            "Situation": ["first paragraph", "second paragraph"],
            "public_tags": "prior-generated-tag",
        }
        self._write_jsonl(env.input_path, [input_record])
        self._write_jsonl(env.output_path, [prior_record])

        env.g.enrich_stories_with_nlp_tags()

        assert env.mock_create.call_count == 1, (
            f"Change in Situation[1] must trigger a retag once _prompt_view "
            f"reads the full Situation. Got {env.mock_create.call_count}."
        )
