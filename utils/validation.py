"""Query validation and text overlap utilities."""

import json
import os
import re

from utils.ui_helpers import dbg

# Small stopword set to avoid false overlap on generic words
_STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "if",
    "then",
    "else",
    "of",
    "in",
    "on",
    "for",
    "to",
    "from",
    "by",
    "with",
    "about",
    "how",
    "what",
    "why",
    "when",
    "where",
    "who",
    "whom",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "do",
    "does",
    "did",
    "done",
    "much",
    "at",
    "as",
    "into",
    "over",
    "under",
}

# Word regex for tokenization
_WORD_RX = re.compile(r"[A-Za-z0-9+#\-_.]+")

# Global rules cache
_NONSENSE_RULES = []


def _tokenize(text: str) -> list[str]:
    """Tokenize text into normalized words (3+ chars)."""
    return [t.lower() for t in _WORD_RX.findall(text or "") if len(t) >= 3]


def _load_nonsense_rules(path: str = "nonsense_filters.jsonl"):
    """Load off-domain query rules from JSONL file."""
    rules = []
    try:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rules.append(json.loads(line))
                    except Exception as e:
                        dbg(f"[rules] JSON error on line {i}: {e}")
        else:
            dbg(f"[rules] file not found: {path}")
    except Exception as e:
        dbg(f"[rules] load exception: {e}")
    dbg(f"[rules] loaded: {len(rules)}")
    if rules[:2]:
        dbg("[rules] first items →", rules[:2])
    return rules


def is_nonsense(query: str) -> str | None:
    """
    Check if query matches off-domain patterns.

    Returns category string if nonsense, else None.
    """
    global _NONSENSE_RULES
    if not _NONSENSE_RULES:
        _NONSENSE_RULES = _load_nonsense_rules()

    q = (query or "").strip()
    if not q:
        return None

    for r in _NONSENSE_RULES:
        pat = r.get("pattern")
        if not pat:
            continue
        try:
            if re.search(pat, q, re.IGNORECASE):
                return r.get("category") or "other"
        except re.error:
            continue
    return None


def token_overlap_ratio(query: str, vocab: set[str]) -> float:
    """
    Calculate token overlap ratio between query and known vocabulary.

    Args:
        query: User query string
        vocab: Set of known vocabulary terms

    Returns:
        Ratio of query tokens found in vocab (0.0 to 1.0)
    """
    toks = [
        t
        for t in re.split(r"[^\w]+", (query or "").lower())
        if len(t) >= 3 and t not in _STOPWORDS
    ]
    if not toks:
        return 0.0
    hits = sum(1 for t in toks if t in vocab)
    return hits / max(1, len(set(toks)))
