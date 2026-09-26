"""Shared reader for data/matt_profile.json (MATTGPT-250 fact card).

load_profile_dict() is the only function that opens the profile file.
Role Match (Location & Availability block), the assessor grounding
(jd_assessor.load_matt_profile) and the Ask Agy fact cards all read
through it, so the three surfaces see the same data.
"""

import json
from pathlib import Path

from config.constants import PROFILE_LOCATION_AVAILABILITY_FIELDS

_PROFILE_PATH = Path(__file__).parent.parent / "data" / "matt_profile.json"


def load_profile_dict() -> dict:
    """Load matt_profile.json as a dict. Errors raise; callers that must
    degrade gracefully catch at their own call site."""
    with open(_PROFILE_PATH) as f:
        return json.load(f)


def iter_location_cells(profile: dict) -> list[tuple[str, str, str]]:
    """Return [(label, value, subline), ...] for populated Location &
    Availability cells only (profile JSON key "logistics"), in
    PROFILE_LOCATION_AVAILABILITY_FIELDS order. Cells whose field is
    absent, or whose value is empty, are omitted entirely (MATTGPT-089
    omit-cleanly contract): a label-only cell would be the 'blank box'
    failure mode."""
    location_availability = (profile or {}).get("logistics") or {}
    cells: list[tuple[str, str, str]] = []
    for field_key, label in PROFILE_LOCATION_AVAILABILITY_FIELDS:
        cell_data = location_availability.get(field_key)
        if not cell_data:
            continue
        value = str(cell_data.get("value", "")).strip()
        subline = str(cell_data.get("subline", "")).strip()
        if not value:
            continue
        cells.append((label, value, subline))
    return cells


def certification_sentence(entry: dict) -> str:
    """Grounding sentence for one {name, issued, expired} certification.

    expired is a year, True (expired, year unknown), or absent (no
    expiry, e.g. passed exams): "Name (issued 2020, expired 2023)",
    "Name (issued 2017, expired)", "Name (2002)".
    """
    name = entry["name"]
    issued = entry.get("issued")
    expired = entry.get("expired")
    if expired is True:
        return f"{name} (issued {issued}, expired)"
    if expired:
        return f"{name} (issued {issued}, expired {expired})"
    if issued:
        return f"{name} ({issued})"
    return name


def cert_date_label(entry: dict) -> str:
    """Fact-card date label: "2020–2023" when both years are known,
    otherwise the issued year alone ("2017", "2002")."""
    issued = entry.get("issued")
    expired = entry.get("expired")
    if expired and expired is not True:
        return f"{issued}–{expired}"
    return str(issued) if issued else ""
