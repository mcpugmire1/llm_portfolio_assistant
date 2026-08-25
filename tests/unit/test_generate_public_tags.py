"""Unit tests for generate_public_tags.py (MATTGPT-211, MATTGPT-072).

MATTGPT-211: the backup step at line 184 must copy OUTPUT_FILE (the file
overwritten) not INPUT_FILE (only read). Guarded for first runs.

MATTGPT-072 first pass:
- Change 1 (_prompt_view helper): the LLM prompt reads Situation and Task
  as [0] only while joining the other list fields. Fix reads them in full
  so tags derive from the same slice as the embedding.
- Change 2 (skip unchanged): re-tagging all 123 stories on every run is
  the cost driver. Compare _prompt_view(input) against _prompt_view(prior)
  and only call the LLM for changed or new stories. public_tags is
  excluded from the comparison (matches generate_jsonl_from_excel.py's
  diff-loop convention).

All tests mock the OpenAI client and the input() prompt to exercise the
real enrich_stories_with_nlp_tags() flow end-to-end against tmp files.
No paid API calls; no repo-file writes.
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
        from generate_public_tags import _prompt_view

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
        from generate_public_tags import _prompt_view

        story = {"Task": ["First task item.", "Second task item."]}
        rendered = _prompt_view(story)["Task"]
        assert (
            "Second task item" in rendered
        ), f"Task must include all items, got: {rendered!r}"

    def test_covers_all_sixteen_prompt_fields(self):
        """Every field the prompt reads must appear in _prompt_view. Missing
        a field means the change-detector would silently skip stories whose
        LLM-relevant content did change -- the worst failure mode."""
        from generate_public_tags import _prompt_view

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
            MagicMock(message=MagicMock(content="freshly-generated-tag"))
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
        """3 stories, prior output has 3 identical prompt-views. Zero API
        calls; prior public_tags carried forward verbatim."""
        input_records = [
            {"id": "s1", "Title": "A", "Situation": ["ax"]},
            {"id": "s2", "Title": "B", "Situation": ["bx"]},
            {"id": "s3", "Title": "C", "Situation": ["cx"]},
        ]
        prior_records = [
            {**r, "public_tags": f"prior-{r['id']}"} for r in input_records
        ]
        self._write_jsonl(env.input_path, input_records)
        self._write_jsonl(env.output_path, prior_records)

        env.g.enrich_stories_with_nlp_tags()

        assert env.mock_create.call_count == 0, (
            f"No LLM calls expected when all prompt-views match prior; "
            f"got {env.mock_create.call_count}"
        )
        out = {r["id"]: r for r in self._read_jsonl(env.output_path)}
        for sid in ("s1", "s2", "s3"):
            assert out[sid]["public_tags"] == f"prior-{sid}", (
                f"Prior tags must carry forward on skip; "
                f"{sid} got {out[sid]['public_tags']!r}"
            )

    def test_api_called_only_for_changed_stories(self, env):
        """3 stories, prior has s1 and s3 matching but s2's Title changed.
        Expect exactly 1 API call. s1 and s3 keep prior tags; s2 gets the
        freshly-generated tag."""
        input_records = [
            {"id": "s1", "Title": "A", "Situation": ["ax"]},
            {"id": "s2", "Title": "B-CHANGED", "Situation": ["bx"]},
            {"id": "s3", "Title": "C", "Situation": ["cx"]},
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
        assert out["s1"]["public_tags"] == "prior-s1"
        assert out["s3"]["public_tags"] == "prior-s3"
        assert "freshly-generated-tag" in out["s2"]["public_tags"], (
            f"s2 should have the fresh LLM-generated tag; "
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
        fields identical. Skip should fire; prior public_tags carries forward.
        (Matches generate_jsonl_from_excel.py's exclusion of public_tags
        from its diff for the same reason.)"""
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
        assert out[0]["public_tags"] == "prior-generated-tag", (
            f"Prior tags must carry forward on skip; " f"got {out[0]['public_tags']!r}"
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
