"""Shared corpus loader: normalization and id enforcement extracted from app.py.

load_stories() replicates the normalization and id-filtering logic that
load_star_stories() applies in app.py, without the Streamlit dependency.
Use this in eval harnesses and probe scripts instead of raw json.loads loops.
"""

import json
from pathlib import Path

_LIST_FIELDS = (
    "Situation",
    "Task",
    "Action",
    "Result",
    "Process",
    "Performance",
    "Competencies",
    "Use Case(s)",
)


def _ensure_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return [x for x in v if str(x).strip()]
    return [str(v)] if str(v).strip() else []


def _split_tags(s):
    if not s:
        return []
    if isinstance(s, list):
        return [str(x).strip() for x in s if str(x).strip()]
    return [t.strip() for t in str(s).split(",") if t.strip()]


def normalize_story(story: dict) -> dict:
    """Coerce list fields and public_tags in-place; return the same dict.

    Mirrors app.py load_star_stories() normalization exactly:
    - Only touches fields already present in the dict (does not add absent fields)
    - Coerces present list fields from string or None to list via _ensure_list
    - Parses public_tags from comma-separated string to list via _split_tags
    """
    for field in _LIST_FIELDS:
        if field in story:
            story[field] = _ensure_list(story[field])
    if "public_tags" in story and isinstance(story["public_tags"], str):
        story["public_tags"] = _split_tags(story["public_tags"])
    return story


def load_stories(path: str) -> list[dict]:
    """Load, filter, and normalize a JSONL corpus file.

    Replicates app.py id enforcement:
    - Skips empty lines silently
    - Raises json.JSONDecodeError on malformed lines (does not swallow)
    - Skips records where id is None, empty string, or 0
    - Strips whitespace from id
    - Applies normalize_story to each kept record
    """
    stories = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            story = json.loads(line)
            story_id = story.get("id")
            if story_id in (None, "", 0):
                continue
            story["id"] = str(story_id).strip()
            normalize_story(story)
            stories.append(story)
    return stories
