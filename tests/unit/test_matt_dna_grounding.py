"""MATTGPT-269 Red: MATT_DNA carries no figure that a story or the profile does not back.

In a design where the model can answer directly from its context, every fact
in MATT_DNA is authoritative. These four figures are in no story: removed.
The backed figures on the same lines stay, so the edit cannot over-delete:
4X faster velocity, zero defects and $100M+ repeat business, and the CIC
claim that 10-person balanced teams delivered the output of 20-person teams
(Building Cloud Innovation Centers story, Result field).
"""

import logging

import pytest

from ui.pages.ask_mattgpt import backend_service as bs
from utils.corpus_loader import load_stories

logging.getLogger("streamlit").setLevel(logging.ERROR)

UNBACKED = ["$300M", "$189M", "30-60%", "MVP in 3 weeks"]
BACKED = ["4X faster velocity", "zero defects", "$100M+", "teams of 10", "teams of 20"]


@pytest.fixture(scope="module")
def matt_dna():
    bs.sync_portfolio_metadata(load_stories("echo_star_stories_nlp.jsonl"))
    return bs.MATT_DNA


@pytest.mark.parametrize("figure", UNBACKED)
def test_unbacked_figure_absent(matt_dna, figure):
    assert (
        figure.lower() not in matt_dna.lower()
    ), f"{figure!r} is in MATT_DNA but in no story or profile field"


@pytest.mark.parametrize("figure", BACKED)
def test_backed_figure_kept(matt_dna, figure):
    assert (
        figure.lower() in matt_dna.lower()
    ), f"{figure!r} is backed by a story and should stay in MATT_DNA"


def test_no_payments_platform_attributed_by_alphabetical_order(matt_dna):
    """The 12-country payments platform is JP Morgan's (Building JP Morgan's
    Global Payments Gateway Across 12 Countries). MATT_DNA attributed it to
    whichever banking client sorted first; the story carries the fact."""
    assert "payments platform across 12 countries" not in matt_dna.lower()


def test_startups_not_listed_as_outside_matts_industries(matt_dna):
    """The Sparkfly story (a founder's startup, 2000-2001) contradicts
    "NOT Matt's industries: ... early-stage startups"."""
    assert "early-stage startups" not in matt_dna.lower()


def test_rest_of_not_industries_line_kept(matt_dna):
    assert "NOT Matt's industries: Consumer products, retail" in matt_dna


# Self-description: Matt's own words, rendered for Ask Agy under a label that
# says they are not independently verified. Role Match's grounding does not
# carry them (they would read as evidence for leadership requirements).
SELF_DESCRIPTION_LABEL = (
    "Matt's attested self-description (his own words, not independently verified)"
)
SELF_DESCRIPTION_PHRASES = [
    "I build what's next",
    "coach's heart",
    "Teaches teams to fish",
    "Authenticity, Curiosity",
]


def _split_self_description(matt_dna):
    """Return (labeled block, rest of MATT_DNA). The block runs from the
    label heading to the next blank line before a bold heading."""
    start = matt_dna.find(f"**{SELF_DESCRIPTION_LABEL}:**")
    if start == -1:
        return "", matt_dna
    end = matt_dna.find("\n\n**", start + 1)
    end = len(matt_dna) if end == -1 else end
    return matt_dna[start:end], matt_dna[:start] + matt_dna[end:]


def test_profile_holds_self_description_with_label():
    from services.matt_profile import load_profile_dict

    entry = load_profile_dict().get("self_description") or {}
    assert entry.get("label") == SELF_DESCRIPTION_LABEL
    statements = " ".join(entry.get("statements") or [])
    for phrase in SELF_DESCRIPTION_PHRASES:
        assert phrase in statements, f"{phrase!r} missing from self_description"


@pytest.mark.parametrize("phrase", SELF_DESCRIPTION_PHRASES)
def test_self_description_only_under_its_label(matt_dna, phrase):
    block, rest = _split_self_description(matt_dna)
    assert phrase in block, f"{phrase!r} is not under the self-description label"
    assert phrase not in rest, f"{phrase!r} appears in MATT_DNA outside the label"


def test_role_match_grounding_has_no_self_description():
    from services.jd_assessor import load_matt_profile

    grounding = load_matt_profile()
    assert SELF_DESCRIPTION_LABEL not in grounding
    for phrase in SELF_DESCRIPTION_PHRASES:
        assert phrase not in grounding


# Theme and industry claims must match the corpus: Execution & Delivery is
# the largest theme but 59 of 123 stories (not a majority); Talent &
# Enablement is tagged on 12; no story is in a Regulatory industry.
OVERSTATED = [
    "the majority of his work",
    "runs through most engagements",
    "Regulatory (one engagement)",
]


@pytest.mark.parametrize("claim", OVERSTATED)
def test_overstated_claim_absent(matt_dna, claim):
    assert claim.lower() not in matt_dna.lower()


@pytest.mark.parametrize(
    "kept",
    [
        "Execution & Delivery is Matt's primary strength",
        "Limited: Healthcare (one engagement)",
    ],
)
def test_supported_part_of_line_kept(matt_dna, kept):
    assert kept in matt_dna


def _theme_strengths(matt_dna):
    start = matt_dna.find("**Theme Strengths:**")
    end = matt_dna.find("\n\n**", start + 1)
    return matt_dna[start:end]


def test_talent_and_enablement_listed_with_its_peers(matt_dna):
    """Talent & Enablement ties Strategic & Advisory at 12 stories; both sit
    in the narrower tier, below Org Transformation (19)."""
    strengths = _theme_strengths(matt_dna)
    narrower = next((line for line in strengths.splitlines() if "narrower" in line), "")
    assert "Talent & Enablement" in narrower
    assert "Strategic" in narrower


def test_no_evaluative_builds_people_claim(matt_dna):
    assert "builds people" not in matt_dna.lower()


def test_no_hardcoded_career_eras_block(matt_dna):
    """The hardcoded era block dated Liquid Studio 2018-2019 (its stories
    start 2016-09) and repeated the Career Arc. The Timeline reads each
    story's own Era field, not MATT_DNA."""
    assert "Career Eras" not in matt_dna


@pytest.mark.parametrize(
    "arc_line",
    [
        "Wellfound Technology: 2000-2001, 2002-2003",
        "Accenture: March 2005 - September 2023",
        "Currently: Sabbatical, building MattGPT",
    ],
)
def test_career_arc_kept(matt_dna, arc_line):
    assert arc_line in matt_dna
