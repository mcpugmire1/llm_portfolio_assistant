"""eval_rag_quality.py --surgical runs to the end and writes no log rows (MATTGPT-274).

run_surgical_diagnostics() calls the router and agy_answer() live. Each can
write: log_query (the Sheet), log_offdomain (data/offdomain_queries.csv) and
the router's _log_borderline and _log_router_low_confidence CSVs. Here the
router and agy_answer() are fakes that call those four loggers the way the
real code does, so no model or Pinecone call is made, and the real loggers
are swapped for recorders.
"""

import pytest

import tests.eval_rag_quality as ev
from services import semantic_router
from ui.pages.ask_mattgpt import backend_service as bs

LOGGERS = (
    (bs, "log_query"),
    (bs, "log_offdomain"),
    (semantic_router, "_log_borderline"),
    (semantic_router, "_log_router_low_confidence"),
)


@pytest.fixture
def reached(monkeypatch):
    """Recorders in place of the four loggers, fakes for the router and
    agy_answer(), and one surgical query. Returns the recorder list."""
    calls = []
    for module, name in LOGGERS:
        monkeypatch.setattr(
            module, name, lambda *a, _name=name, **k: calls.append(_name)
        )

    def fake_router(query, *args, **kwargs):
        semantic_router._log_borderline(query, 0.5, "intent", "family")
        semantic_router._log_router_low_confidence(query, 0.5, "intent", "family")
        return True, 0.9, "matched intent", "family"

    def fake_agy_answer(question, stories, *args, **kwargs):
        bs.log_query(question, "Ask Agy")
        bs.log_offdomain(question, "rule:test")
        return {"answer_md": "", "sources": []}

    monkeypatch.setattr(semantic_router, "is_portfolio_query_semantic", fake_router)
    monkeypatch.setattr(bs, "agy_answer", fake_agy_answer)
    monkeypatch.setattr(
        ev, "GOLDEN_QUERIES", {"surgical": ev.GOLDEN_QUERIES["surgical"][:1]}
    )
    return calls


def test_surgical_run_returns_its_diagnostics(reached):
    """The run gets through its summary and returns one row per query."""
    diagnostics = ev.run_surgical_diagnostics()

    assert len(diagnostics) == 1


def test_surgical_run_reaches_no_logger(reached):
    """No logger is reached, whether or not the run gets to its summary."""
    try:
        ev.run_surgical_diagnostics()
    except Exception:
        pass  # completing is the other test's job; this one checks the recorders

    assert reached == [], f"Loggers reached during a surgical run: {reached}"
