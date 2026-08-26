"""Unit test for generate_jsonl_from_excel.py merge behavior (MATTGPT-072).

Excel is authoritative for public_tags: a blank column value means the
JSONL's public_tags is blank, even if the prior JSONL had tags. Prior to
Aug 2026 the ingest silently preserved the prior tags when Excel was blank,
which meant the master could not express "no tags."
"""


class TestMergeWithExisting:
    def test_blank_excel_public_tags_produces_blank_jsonl(self):
        """The preserve-on-blank rule (Aug 2025) meant a cleared Excel
        column was silently overridden by the prior JSONL's tags. Excel
        is now authoritative -- blank means blank."""
        from generate_jsonl_from_excel import _merge_with_existing

        record = {"id": "s1", "Title": "T", "public_tags": ""}
        existing = {"id": "s1", "Title": "T", "public_tags": "prior-generated-tag"}
        merged = _merge_with_existing(record, existing)
        assert merged["public_tags"] == "", (
            f"Blank Excel public_tags must survive as blank in the JSONL. "
            f"Got {merged['public_tags']!r}"
        )
