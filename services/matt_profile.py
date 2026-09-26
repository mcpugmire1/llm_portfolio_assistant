"""Shared reader for data/matt_profile.json (MATTGPT-250 fact card)."""


def load_profile_dict() -> dict:
    raise NotImplementedError


def iter_location_cells(profile: dict) -> list[tuple[str, str, str]]:
    raise NotImplementedError


def certification_sentence(entry: dict) -> str:
    raise NotImplementedError


def cert_date_label(entry: dict) -> str:
    raise NotImplementedError
