"""
BDD step definitions for matt_dna_grounding_drift.feature (MATTGPT-207).

Guards MATT_DNA against corpus drift: every Employer and every non-generic
Client in the corpus must be reachable through the grounding. Also asserts
the "What Matt is NOT" block is removed (it went stale against the corpus
and overrode evidence on hardware/embedded and early-stage-startup queries)
while the "NOT Matt's Clients" block stays (it names specific companies
the model actually confabulated in January 2026).
"""

import sys
from unittest.mock import MagicMock

if "streamlit" not in sys.modules:
    _st_mock = MagicMock()
    _st_mock.session_state = {}
    _st_mock.secrets = {}
    sys.modules["streamlit"] = _st_mock
    sys.modules["streamlit.components"] = MagicMock()
    sys.modules["streamlit.components.v1"] = MagicMock()

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/matt_dna_grounding_drift.feature")


@pytest.fixture
def ctx():
    return {}


@pytest.fixture(autouse=True)
def restore_backend_service_globals():
    """Snapshot/restore backend_service module-level globals mutated by
    sync_portfolio_metadata so scenario state does not leak. Same shape as
    tests/bdd/steps/test_matt_dna_career_span.py's fixture (MATTGPT-161)."""
    from ui.pages.ask_mattgpt import backend_service

    _MISSING = object()
    tracked = (
        "MATT_DNA",
        "SYNTHESIS_THEMES",
        "_KNOWN_CLIENTS",
        "_CAREER_START_YEAR",
        "_CAREER_END_YEAR",
        "_CAREER_SPAN_YEARS",
    )
    snapshot = {name: getattr(backend_service, name, _MISSING) for name in tracked}
    yield
    for name, value in snapshot.items():
        if value is _MISSING:
            if hasattr(backend_service, name):
                delattr(backend_service, name)
        else:
            setattr(backend_service, name, value)


@given("the current production story corpus is loaded")
def given_production_corpus(ctx):
    from utils.corpus_loader import load_stories

    ctx["stories"] = load_stories("echo_star_stories_nlp.jsonl")


@when("sync_portfolio_metadata is called with the production stories")
def when_sync(ctx):
    from ui.pages.ask_mattgpt import backend_service

    backend_service.sync_portfolio_metadata(ctx["stories"])
    ctx["backend_service"] = backend_service


@then("every distinct Employer value from the corpus appears literally in MATT_DNA")
def then_every_employer_in_dna(ctx):
    bs = ctx["backend_service"]
    employers = {s["Employer"] for s in ctx["stories"] if s.get("Employer")}
    missing = [e for e in sorted(employers) if e not in bs.MATT_DNA]
    assert not missing, (
        f"Employers present in the corpus but absent from MATT_DNA: {missing}."
        f" MATT_DNA is anti-hallucination grounding; an Employer that appears in"
        f" the corpus but not in MATT_DNA lets the model reconcile that employer's"
        f" stories against a stale timeline (Aug 20 2026 Sparkfly incident:"
        f" WellFound Technology missing, model asserted AT&T-before-Accenture)."
        f" Add the Employer to Career Arc and Career Eras in generate_dynamic_dna."
    )


@then("every non-generic Client value from the corpus appears in _KNOWN_CLIENTS")
def then_every_client_in_known(ctx):
    from utils.client_utils import is_generic_client

    bs = ctx["backend_service"]
    corpus_specific_clients = {
        s["Client"]
        for s in ctx["stories"]
        if s.get("Client") and not is_generic_client(s["Client"])
    }
    known = set(bs._KNOWN_CLIENTS or set())
    missing = corpus_specific_clients - known
    assert not missing, (
        f"Non-generic Clients present in the corpus but missing from"
        f" _KNOWN_CLIENTS (which feeds the MATT_DNA client list): {sorted(missing)}."
        f" Generic values like 'Fortune 500 Clients' and 'Independent Project'"
        f" are intentionally filtered by is_generic_client and are exempt from"
        f" this check. Any specific Client that shows up here means the derivation"
        f" in get_known_clients dropped a value it should have kept."
    )


@then(parsers.parse('MATT_DNA contains no "{substring}" heading'))
def then_matt_dna_no_heading(ctx, substring):
    bs = ctx["backend_service"]
    assert substring not in bs.MATT_DNA, (
        f"MATT_DNA still contains the {substring!r} heading. The block was"
        f" removed for MATTGPT-207 because it had gone stale against the corpus"
        f" (claimed 'Not early-stage startups' while Sparkfly is present;"
        f" claimed 'Not hardware/embedded systems' while Liquid Studio IoT is"
        f" present). Grounding rule 1 ('ONLY cite clients, projects, and metrics"
        f" that appear in the stories below') covers every case the block was"
        f" trying to enumerate. Remove the block and its heading from"
        f" generate_dynamic_dna."
    )


@then(parsers.parse('MATT_DNA contains "{substring}"'))
def then_matt_dna_contains(ctx, substring):
    bs = ctx["backend_service"]
    assert substring in bs.MATT_DNA, (
        f"MATT_DNA does not contain {substring!r}. This block names specific"
        f" companies the model confabulated in January 2026 (Kaiser and a"
        f" JPMorgan '4x faster delivery' metric that did not exist). It must"
        f" stay in MATT_DNA even after MATTGPT-207 removes the 'What Matt is"
        f" NOT' block, because the two blocks do different jobs -- one guards"
        f" against confabulated CLIENTS by name, the other was enumerating"
        f" categorical exclusions and went stale against the corpus."
    )
