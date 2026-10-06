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
