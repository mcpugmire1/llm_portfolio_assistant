"""Unit test: the JSONL is rebuilt from the Excel master (MATTGPT-072, MATTGPT-323).

Excel is authoritative: a blank Public Tags cell means blank public_tags in
the JSONL even if the prior JSONL had tags, and a field that lives only in
the prior JSONL does not survive the export.
"""

import json

import pandas as pd

import generate_jsonl_from_excel as gen

MASTER = "MPugmire - STAR Stories - 01JAN26.xlsx"


def test_export_rebuilds_records_from_excel_only(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "archive" / "jsonl-backups").mkdir(parents=True)
    prior = {
        "id": "t|c",
        "Title": "T",
        "Client": "C",
        "public_tags": "prior-generated-tag",
        "jsonl_only": "x",
    }
    (tmp_path / gen.OUTPUT_JSONL_FILE).write_text(
        json.dumps(prior) + "\n", encoding="utf-8"
    )
    pd.DataFrame([{"Title": "T", "Client": "C", "Public Tags": ""}]).to_excel(
        tmp_path / MASTER, sheet_name=gen.SHEET_NAME, index=False
    )
    monkeypatch.setattr(gen, "DRY_RUN", False)

    gen.excel_to_jsonl()

    lines = (tmp_path / gen.OUTPUT_JSONL_FILE).read_text(encoding="utf-8").splitlines()
    [record] = [json.loads(line) for line in lines if line.strip()]
    assert record["public_tags"] == "", "Blank Excel public_tags must stay blank."
    assert "jsonl_only" not in record, "A JSONL-only field must not survive the export."
