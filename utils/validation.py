"""Query validation and text overlap utilities.

This module provides functionality for detecting off-domain queries, tokenizing
text, and calculating vocabulary overlap ratios. Used primarily for filtering
nonsense/off-topic queries in the RAG pipeline.
"""

import json
import os
import re
from typing import Any

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
_NONSENSE_RULES: list[dict] = []


def _tokenize(text: str) -> list[str]:
    """Tokenize text into normalized words (3+ chars).

    Extracts alphanumeric tokens (including +, #, -, _, .) from text,
    lowercases them, and filters to tokens with length >= 3 characters.
    Used for keyword matching and vocabulary overlap calculations.

    Args:
        text: Input text to tokenize. None or empty strings handled gracefully.

    Returns:
        List of lowercase tokens with length >= 3. Empty list if no valid tokens.

    Example:
        >>> _tokenize("Platform Engineering with AWS")
        ['platform', 'engineering', 'with', 'aws']
        >>> _tokenize("C# and .NET")
        []  # Tokens too short after filtering
        >>> _tokenize("")
        []
    """
    return [t.lower() for t in _WORD_RX.findall(text or "") if len(t) >= 3]


def _load_nonsense_rules(path: str = "nonsense_filters.jsonl") -> list[dict[str, Any]]:
    """Load off-domain query rules from JSONL file.

    Reads a JSONL file containing regex patterns and categories for detecting
    nonsense/off-domain queries. Each line should be a JSON object with fields:
    - pattern (str): Regex pattern to match against queries
    - category (str): Category label (e.g., "profanity", "meta", "gibberish")

    Args:
        path: Path to JSONL rules file. Defaults to "nonsense_filters.jsonl"
            in current directory.

    Returns:
        List of rule dictionaries loaded from file. Empty list if file not found
        or parsing fails. Malformed JSON lines are skipped with debug logging.

    Side Effects:
        Logs debug messages via dbg() for file not found, JSON errors, and
        successful load count.

    Example:
        >>> rules = _load_nonsense_rules("nonsense_filters.jsonl")
        >>> len(rules) > 0
        True
        >>> rules[0].keys()
        dict_keys(['pattern', 'category'])
    """
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
    """Check if query matches off-domain/nonsense patterns.

    Tests query against loaded regex rules to detect off-domain queries like
    profanity, meta questions about the system, gibberish, etc. Loads rules
    from nonsense_filters.jsonl on first call (lazy loading with caching).

    Args:
        query: User query string to validate.

    Returns:
        Category string (e.g., "profanity", "meta", "gibberish") if query
        matches a nonsense pattern, otherwise None. Empty/whitespace-only
        queries return None.

    Side Effects:
        Lazy-loads _NONSENSE_RULES global cache from nonsense_filters.jsonl
        on first call.

    Example:
        >>> is_nonsense("What can you do?")  # Meta question
        'meta'
        >>> is_nonsense("Tell me about platform modernization")
        None
        >>> is_nonsense("")
        None
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
    """Calculate token overlap ratio between query and known vocabulary.

    Measures how many unique query tokens (3+ chars, excluding stopwords)
    appear in the known vocabulary set. Used to detect off-domain queries
    that have low overlap with portfolio content.

    Args:
        query: User query string to analyze.
        vocab: Set of known vocabulary terms from story corpus (lowercase).
            Typically built via build_known_vocab() in backend_service.

    Returns:
        Float ratio between 0.0 and 1.0 representing the proportion of unique
        query tokens found in vocab. Returns 0.0 for empty queries or when
        no valid tokens remain after stopword filtering.

    Example:
        >>> vocab = {"platform", "engineering", "modernization", "aws"}
        >>> token_overlap_ratio("platform modernization", vocab)
        1.0  # Both tokens found
        >>> token_overlap_ratio("unrelated topic here", vocab)
        0.0  # No tokens found
        >>> token_overlap_ratio("platform and some unrelated words", vocab)
        0.5  # 1 out of 2 unique non-stopword tokens found
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
