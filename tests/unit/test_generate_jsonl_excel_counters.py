"""Unit test for generate_jsonl_from_excel.py summary counters (MATTGPT-270)."""

import pandas as pd

import generate_jsonl_from_excel as gen

MASTER = "MPugmire - STAR Stories - 01JAN26.xlsx"


def _write_master(folder, rows):
    pd.DataFrame(rows).to_excel(folder / MASTER, sheet_name=gen.SHEET_NAME, index=False)


def test_summary_counts_created_updated_unchanged(tmp_path, monkeypatch, capsys):
    """One story unchanged, one revised, one new: the summary says 1 / 1 / 1."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "archive" / "jsonl-backups").mkdir(parents=True)
    base = [
        {"Title": "Story A", "Client": "Client One", "Situation": "- a"},
        {"Title": "Story B", "Client": "Client Two", "Situation": "- b"},
    ]
    _write_master(tmp_path, base)
    monkeypatch.setattr(gen, "DRY_RUN", False)
    gen.excel_to_jsonl()

    _write_master(
        tmp_path,
        [
            base[0],
            {**base[1], "Situation": "- b revised"},
            {"Title": "Story C", "Client": "Client Three", "Situation": "- c"},
        ],
    )
    monkeypatch.setattr(gen, "DRY_RUN", True)
    capsys.readouterr()
    gen.excel_to_jsonl()

    assert "Created: 1  🔁 Updated: 1  ✅ Unchanged: 1" in capsys.readouterr().out
