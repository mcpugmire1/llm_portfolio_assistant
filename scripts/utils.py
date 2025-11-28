# utils.py

import re


def normalize(s: str) -> str:
    return (s or "").strip()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)  # remove punctuation
    text = re.sub(r"\s+", "-", text)  # replace spaces with hyphens
    return text


def norm_key(title: str, client: str) -> str:
    return f"{normalize(title).lower()}|{normalize(client).lower()}"


def split_bullets(value: str):
    if not value:
        return []
    raw = str(value)
    parts = []
    for line in raw.replace("•", "\n").replace("–", "\n").split("\n"):
        line = line.strip()
        if line.startswith("- ") or line.startswith("• ") or line.startswith("– "):
            line = line[2:].strip()
        if line:
            parts.append(line)
    if len(parts) == 1 and " - " in raw:
        parts = [p.strip() for p in raw.split(" - ") if p.strip()]
    return parts
