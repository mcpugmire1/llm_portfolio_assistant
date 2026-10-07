"""MATTGPT-279 Red: MATT_DNA's Industry Experience block is derived from the corpus.

The block was half hand-typed: tier labels (Primary / Secondary / Limited),
"Limited: Healthcare (one engagement)", "NOT Matt's industries: Consumer
products, retail", and fallback client names ("AT&T", "Norfolk Southern")
used when a derived list came back empty. Only three Industry labels were
read, so any other industry (Technology & Software, Aerospace & Defense,
Education, a new one such as hospitality) never reached the model.

Derived instead: every Industry value except "Cross Industry" (not an
industry) is listed as "- {Industry}: {n} stories ({clients})", most stories
first, with the non-generic clients of that industry's stories. No tier
labels, no NOT line, no hardcoded client names.

The Signature Achievements line "{transport clients} legacy-to-cloud
transformation" reused the derived transportation clients; once the Cendian
stories took the same Industry label it read "Cendian Chemical Logistics,
Norfolk Southern legacy-to-cloud transformation", which is false. That line
is removed; the Norfolk Southern stories carry the work themselves.

Invented corpus values use the ZZZ_SENTINEL convention.
"""

import logging
import re
from collections import Counter

import pytest

from ui.pages.ask_mattgpt import backend_service as bs
from utils.client_utils import is_generic_client
from utils.corpus_loader import load_stories

logging.getLogger("streamlit").setLevel(logging.ERROR)

CROSS_INDUSTRY = "Cross Industry"


def _block(dna: str, heading: str) -> str:
    start = dna.find(f"**{heading}")
    assert start != -1, f"MATT_DNA has no {heading!r} block"
    end = dna.find("\n\n**", start + 1)
    return dna[start : end if end != -1 else len(dna)]


def _line_for(block: str, industry: str) -> str:
    for line in block.splitlines():
        if line.startswith(f"- {industry}:"):
            return line
    raise AssertionError(f"No line for industry {industry!r} in:\n{block}")


@pytest.fixture(scope="module")
def stories():
    return load_stories("echo_star_stories_nlp.jsonl")


@pytest.fixture(scope="module")
def matt_dna(stories):
    bs.sync_portfolio_metadata(stories)
    return bs.MATT_DNA


@pytest.fixture(scope="module")
def industry_counts(stories):
    return Counter(
        s["Industry"]
        for s in stories
        if s.get("Industry") and s["Industry"] != CROSS_INDUSTRY
    )


# ---------------------------------------------------------------------------
# Hand-typed text is gone
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("label", ["Primary:", "Secondary:", "Limited:"])
def test_no_hand_typed_tier_labels(matt_dna, label):
    assert label not in _block(matt_dna, "Industry Experience")


def test_no_not_industries_line(matt_dna):
    assert "NOT Matt's industries" not in matt_dna


def test_signature_achievements_name_no_client(matt_dna, stories):
    achievements = _block(matt_dna, "Signature Achievements")
    clients = {
        s["Client"]
        for s in stories
        if s.get("Client") and not is_generic_client(s["Client"])
    }
    named = sorted(c for c in clients if c in achievements)
    assert not named, f"Signature Achievements names clients: {named}"


# ---------------------------------------------------------------------------
# The block is derived from the corpus
# ---------------------------------------------------------------------------


def test_every_industry_listed_with_its_story_count(matt_dna, industry_counts):
    block = _block(matt_dna, "Industry Experience")
    for industry, n in industry_counts.items():
        unit = "story" if n == 1 else "stories"
        assert re.search(
            rf"^- {re.escape(industry)}: {n} {unit}\b", block, re.M
        ), f"Expected '- {industry}: {n} {unit}' in:\n{block}"


def test_cross_industry_is_not_listed_as_an_industry(matt_dna):
    assert CROSS_INDUSTRY not in _block(matt_dna, "Industry Experience")


def test_industries_ordered_by_story_count(matt_dna, industry_counts):
    block = _block(matt_dna, "Industry Experience")
    expected = sorted(industry_counts, key=lambda i: (-industry_counts[i], i))
    found = [i for i in sorted(industry_counts, key=lambda i: block.find(f"- {i}:"))]
    assert found == expected


def test_each_industry_lists_its_own_clients(matt_dna, stories, industry_counts):
    block = _block(matt_dna, "Industry Experience")
    for industry in industry_counts:
        line = _line_for(block, industry)
        clients = {
            s["Client"]
            for s in stories
            if s.get("Industry") == industry
            and s.get("Client")
            and not is_generic_client(s["Client"])
        }
        missing = sorted(c for c in clients if c not in line)
        assert not missing, f"{industry}: clients missing from its line: {missing}"


# ---------------------------------------------------------------------------
# Invented corpus: no hardcoded fallbacks; a new industry appears
# ---------------------------------------------------------------------------


def _story(industry, client, employer="Accenture"):
    return {
        "id": f"zzz-{client.lower().replace(' ', '-')}",
        "Title": f"ZZZ_SENTINEL story for {client}",
        "Employer": employer,
        "Client": client,
        "Industry": industry,
        "Theme": "Execution & Delivery",
    }


@pytest.fixture
def invented_dna():
    corpus = [
        _story("Financial Services / Banking", "ZZZ_SENTINEL Bank"),
        _story("ZZZ_SENTINEL Hospitality", "ZZZ_SENTINEL Hotels"),
    ]
    return bs.generate_dynamic_dna(corpus, {"ZZZ_SENTINEL Bank", "ZZZ_SENTINEL Hotels"})


@pytest.mark.parametrize("fallback", ["AT&T", "Norfolk Southern"])
def test_no_hardcoded_fallback_client(invented_dna, fallback):
    for heading in ("Industry Experience", "Signature Achievements"):
        assert fallback not in _block(
            invented_dna, heading
        ), f"{fallback!r} rendered in {heading} from a corpus that has no such client"


def test_a_new_industry_appears(invented_dna):
    block = _block(invented_dna, "Industry Experience")
    assert "- ZZZ_SENTINEL Hospitality: 1 story (ZZZ_SENTINEL Hotels)" in block
