"""
BDD step definitions for cluster_promotion_kw.feature (MATTGPT-074 refinement).

Tests that the entity cluster promotion gate strips entity tokens (canonical
value + matched alias key) from the retrieval query, recomputes content-kw
per entity story, and uses uniformity of that recomputed array to decide
whether to promote.

Stored kw values on fixture stories represent what the OLD gate read.
New-behavior scenarios set stored kw to dispersed values so the OLD gate
suppresses (Red fails), while the recomputed content-kw is uniform so the
NEW gate promotes (Green passes).
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pytest_bdd import given, scenarios, then, when

if "streamlit" not in sys.modules:
    _st_mock = MagicMock()
    _st_mock.session_state = {}
    _st_mock.secrets = {}
    sys.modules["streamlit"] = _st_mock
    sys.modules["streamlit.components"] = MagicMock()
    sys.modules["streamlit.components.v1"] = MagicMock()

scenarios("../features/cluster_promotion_kw.feature")


# =============================================================================
# Story factories
# =============================================================================


def _make_story(
    i, entity_field, entity_value, employer, kw, *, title=None, five_p=None
):
    # five_p: sets "5PSummary" directly. build_5p_summary reads 5PSummary/why/how/what,
    # NOT Situation/Task/Action/Result, so STAR fields do not reach _keyword_score_for_story.
    slug = entity_value.lower().replace(" ", "-").replace("&", "").replace("'", "")
    s = {
        "id": f"{slug}-story-{i}|{slug}",
        "Title": title or f"{entity_value} Story {i}",
        "Client": entity_value if entity_field == "Client" else "Accenture",
        "Employer": employer,
        "Division": entity_value if entity_field == "Division" else "Technology",
        "Role": "Delivery Lead",
        "Sub-category": "Program Delivery",
        "Theme": "Execution & Delivery",
        "Category": "Execution & Delivery",
        "pc": 0.5,
        "kw": kw,
        "blend": 0.5,
        "_search_score": 0.5,
        "Situation": "A situation.",
        "Task": "A task.",
        "Action": ["An action."],
        "Result": ["A result."],
        "Process": [],
        "Performance": [],
        "Competencies": [],
        "public_tags": [],
    }
    if five_p:
        s["5PSummary"] = five_p
    return s


def _non_entity_story():
    return {
        "id": "other-story-0|accenture",
        "Title": "Other Story",
        "Client": "Accenture",
        "Employer": "Accenture",
        "Division": "Technology",
        "Role": "Delivery Lead",
        "Sub-category": "Program Delivery",
        "Theme": "Execution & Delivery",
        "Category": "Execution & Delivery",
        "pc": 0.4,
        "kw": 0.0,
        "blend": 0.4,
        "_search_score": 0.4,
        "Situation": "A situation.",
        "Task": "A task.",
        "Action": ["An action."],
        "Result": ["A result."],
        "Process": [],
        "Performance": [],
        "Competencies": [],
        "public_tags": [],
    }


# =============================================================================
# Shared fixture
# =============================================================================


@pytest.fixture
def ctx():
    return {}


# =============================================================================
# Given steps
# =============================================================================


@given("a pool of 3 Liquid Studio stories where one title contains the entity name")
def given_ls_entity_in_title(ctx):
    # Old gate: stored kw dispersed [0.667, 0, 0] -> suppresses.
    # New gate: family=background (not SUBSTITUTION_FAMILIES) -> no substitution.
    # entity_toks = {atlanta, liquid, studio}; content_toks = {matt} after strip.
    # "matt" absent from every haystack -> kw=[0,0,0] -> uniform -> triggers.
    ctx["entity_field"] = "Division"
    ctx["entity_value"] = "Atlanta Liquid Studio"
    ctx["query"] = "What did Matt do at Liquid Studio?"
    ctx["intent_family"] = "background"
    ctx["pool"] = [
        _make_story(
            0,
            "Division",
            "Atlanta Liquid Studio",
            "Accenture",
            0.667,
            title="Building at Atlanta Liquid Studio",
        ),
        _make_story(1, "Division", "Atlanta Liquid Studio", "Accenture", 0.0),
        _make_story(2, "Division", "Atlanta Liquid Studio", "Accenture", 0.0),
        _non_entity_story(),
    ]


@given(
    "a pool of 3 AT&T stories where one title contains production incident vocabulary"
)
def given_att_production_incident(ctx):
    # entity_toks = {} (AT&T splits on & into 2-char / 1-char tokens, both dropped).
    # content_toks = {tell, production, incident}. Story 0 title matches production+incident
    # -> kw high; others 0 -> dispersed -> suppressed. Old gate also suppresses.
    ctx["entity_field"] = "Client"
    ctx["entity_value"] = "AT&T"
    ctx["query"] = "Tell me about a production incident at AT&T"
    ctx["intent_family"] = "background"
    ctx["pool"] = [
        _make_story(
            0, "Client", "AT&T", "AT&T", 0.667, title="Production Incident Response"
        ),
        _make_story(1, "Client", "AT&T", "AT&T", 0.0),
        _make_story(2, "Client", "AT&T", "AT&T", 0.0),
        _non_entity_story(),
    ]


@given(
    "a pool of 3 CIC stories where one title contains the alias cic"
    " and the query resolves via alias to Division Cloud Innovation Center"
)
def given_cic_alias_in_title(ctx):
    # canonical entity_toks = {cloud, innovation, center}; alias key "cic" also stripped.
    # query_toks = {matt, cic} -> content_toks = {matt} after strip.
    # "matt" absent from all haystacks -> kw=[0,0,0] -> uniform -> triggers.
    # Falsifies alias stripping: if alias not stripped, content_toks = {matt, cic},
    # story 0 title "Building Products at CIC" matches "cic" -> dispersed -> suppressed.
    ctx["entity_field"] = "Division"
    ctx["entity_value"] = "Cloud Innovation Center"
    ctx["query"] = "What did Matt do at CIC?"
    ctx["intent_family"] = "background"
    ctx["pool"] = [
        _make_story(
            0,
            "Division",
            "Cloud Innovation Center",
            "Accenture",
            0.667,
            title="Building Products at CIC",
        ),
        _make_story(1, "Division", "Cloud Innovation Center", "Accenture", 0.0),
        _make_story(2, "Division", "Cloud Innovation Center", "Accenture", 0.0),
        _non_entity_story(),
    ]


@given(
    "a pool of 3 American Express stories where one title contains"
    " production incident vocabulary"
)
def given_amex_production_incident(ctx):
    # canonical entity_toks = {american, express}; alias "amex" also stripped.
    # content_toks = {production, incident}. Story 0 title matches both -> dispersed
    # -> suppressed. Regression protection: specific tokens still disperse even with alias.
    ctx["entity_field"] = "Client"
    ctx["entity_value"] = "American Express"
    ctx["query"] = "amex production incident"
    ctx["intent_family"] = "background"
    ctx["pool"] = [
        _make_story(
            0,
            "Client",
            "American Express",
            "American Express",
            0.667,
            title="Production Incident Recovery at American Express",
        ),
        _make_story(1, "Client", "American Express", "American Express", 0.0),
        _make_story(2, "Client", "American Express", "American Express", 0.0),
        _non_entity_story(),
    ]


@given("a pool of 3 RBC stories with no content tokens in the query")
def given_rbc_bare_entity(ctx):
    # family=team_scaling (SUBSTITUTION_FAMILIES) -> "Matt" -> "he" (2 chars, filtered).
    # retrieval_q = "What did he do at RBC?" -> tokens = {rbc} after stopwords + length.
    # Strip entity_toks = {rbc} -> content_toks = {} -> trivially uniform -> triggers.
    ctx["entity_field"] = "Client"
    ctx["entity_value"] = "RBC"
    ctx["query"] = "What did Matt do at RBC?"
    ctx["intent_family"] = "team_scaling"
    ctx["pool"] = [
        _make_story(0, "Client", "RBC", "RBC", 0.5),
        _make_story(1, "Client", "RBC", "RBC", 0.0),
        _make_story(2, "Client", "RBC", "RBC", 0.0),
        _non_entity_story(),
    ]


@given("a pool of 3 Fiserv stories where no story field contains the word work")
def given_fiserv_no_work(ctx):
    # Corpus-dependent: promotes because "work" is absent from all Fiserv haystack
    # fields. See MATTGPT-074.
    # family=narrative (not SUBSTITUTION_FAMILIES) -> retrieval_q = original.
    # content_toks = {tell, matt, work} after strip. None appear in fixture titles or
    # the "Impact-focused delivery across stakeholders." fallback -> kw=[0,0,0] -> triggers.
    ctx["entity_field"] = "Client"
    ctx["entity_value"] = "Fiserv"
    ctx["query"] = "Tell me about Matt's work at Fiserv"
    ctx["intent_family"] = "narrative"
    ctx["pool"] = [
        _make_story(
            0, "Client", "Fiserv", "Fiserv", 1.0, title="Recovering the Fiserv Portal"
        ),
        _make_story(
            1,
            "Client",
            "Fiserv",
            "Fiserv",
            0.0,
            title="Delivering Compliance for the Card Portal",
        ),
        _make_story(
            2,
            "Client",
            "Fiserv",
            "Fiserv",
            0.0,
            title="Driving Adoption of the Fiserv Platform",
        ),
        _non_entity_story(),
    ]


@given("a pool of 3 CIC stories where one story summary mentions Matt by name")
def given_cic_matt_in_summary(ctx):
    # Pinning scenario. family=technical (SUBSTITUTION_FAMILIES) -> substitution fires.
    #
    # retrieval_q ("What did he do at CIC?"): {he} dropped, {cic} is entity_tok ->
    #   content_toks = {} -> trivially uniform -> triggered.
    # question ("What did Matt do at CIC?"): content_toks = {matt}. Story 0's 5PSummary
    #   contains "matt" -> hits=1, td_hits=0 -> kw=0.5. Others have empty 5PSummary,
    #   fallback text does not contain "matt" -> kw=0. Array=[0.5,0,0] -> dispersed
    #   -> suppressed.
    # If gate accidentally uses original question, this scenario fails at Green.
    ctx["entity_field"] = "Division"
    ctx["entity_value"] = "Cloud Innovation Center"
    ctx["query"] = "What did Matt do at CIC?"
    ctx["intent_family"] = "technical"
    ctx["pool"] = [
        _make_story(
            0,
            "Division",
            "Cloud Innovation Center",
            "Accenture",
            1.0,
            five_p="Matt led the CIC innovation program.",
        ),
        _make_story(1, "Division", "Cloud Innovation Center", "Accenture", 0.0),
        _make_story(2, "Division", "Cloud Innovation Center", "Accenture", 0.0),
        _non_entity_story(),
    ]


@given("a pool of 2 Liquid Studio stories where no title contains the entity name")
def given_ls_2_stories(ctx):
    # Count gate: 2 entity stories < 3 -> no promotion regardless of kw uniformity.
    # Stored kw uniform (0.333) to isolate the count check from the kw gate.
    ctx["entity_field"] = "Division"
    ctx["entity_value"] = "Atlanta Liquid Studio"
    ctx["query"] = "What did Matt do at Liquid Studio?"
    ctx["intent_family"] = "background"
    ctx["pool"] = [
        _make_story(0, "Division", "Atlanta Liquid Studio", "Accenture", 0.333),
        _make_story(1, "Division", "Atlanta Liquid Studio", "Accenture", 0.333),
        _non_entity_story(),
    ]


# =============================================================================
# Shared when executor
# =============================================================================


def _run_rag_answer(ctx):
    from dotenv import load_dotenv

    load_dotenv(Path(".env"))

    _st_mock = sys.modules["streamlit"]
    _st_mock.session_state.clear()
    _st_mock.session_state["__suppress_logging__"] = True

    from ui.pages.ask_mattgpt.backend_service import rag_answer

    pool = ctx["pool"]
    entity_field = ctx["entity_field"]
    entity_value = ctx["entity_value"]
    entity_stories = [s for s in pool if s.get(entity_field) == entity_value]
    synthesis_spy = MagicMock(return_value=entity_stories)

    with (
        patch(
            "ui.pages.ask_mattgpt.backend_service.semantic_search",
            return_value={"results": pool, "confidence": "high", "top_score": 0.5},
        ),
        patch(
            "ui.pages.ask_mattgpt.backend_service.detect_entity",
            return_value=(entity_field, entity_value),
        ),
        patch(
            "ui.pages.ask_mattgpt.backend_service.is_portfolio_query_semantic",
            return_value=(True, 0.7, ctx["intent_family"], ctx["intent_family"]),
        ),
        patch(
            "ui.pages.ask_mattgpt.backend_service.get_synthesis_stories",
            synthesis_spy,
        ),
        patch(
            "ui.pages.ask_mattgpt.backend_service._generate_agy_response",
            return_value="Test response",
        ),
        patch("ui.pages.ask_mattgpt.backend_service.log_query"),
    ):
        ctx["result"] = rag_answer(ctx["query"], {"q": ctx["query"]}, [])

    ctx["synthesis_called"] = synthesis_spy.called


# =============================================================================
# When steps
# =============================================================================


@when("rag_answer is called with a broad Liquid Studio query")
def when_broad_ls(ctx):
    _run_rag_answer(ctx)


@when("rag_answer is called with a production incident AT&T query")
def when_att_incident(ctx):
    _run_rag_answer(ctx)


@when("rag_answer is called with a broad CIC query using the alias")
def when_cic_alias(ctx):
    _run_rag_answer(ctx)


@when("rag_answer is called with an amex production incident query")
def when_amex_incident(ctx):
    _run_rag_answer(ctx)


@when("rag_answer is called with a bare entity-only RBC query")
def when_rbc_bare(ctx):
    _run_rag_answer(ctx)


@when("rag_answer is called with a possessive Fiserv query")
def when_fiserv_possessive(ctx):
    _run_rag_answer(ctx)


@when("rag_answer is called with a broad CIC query in the technical intent family")
def when_cic_technical(ctx):
    _run_rag_answer(ctx)


# =============================================================================
# Then steps
# =============================================================================


@then("synthesis mode is triggered")
def then_synthesis_triggered(ctx):
    assert ctx.get(
        "synthesis_called"
    ), "Expected get_synthesis_stories to be called (synthesis mode) but it was not."


@then("synthesis mode is suppressed")
def then_synthesis_suppressed(ctx):
    assert not ctx.get(
        "synthesis_called"
    ), "Expected get_synthesis_stories NOT to be called (standard mode) but it was."
