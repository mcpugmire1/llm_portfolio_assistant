"""Client attribution in the golden eval, from the answer's sources.

The expected client is attributed when it is the Client of one of the
answer's source stories, looked up by id; no list of name variants. The
bolding check passes when the answer bolds the client of one of its sources
as the answer writes it: a bold span whose words run inside that Client
value, or contain it. Pure functions and a fake rag_fn: no model or Pinecone
call.
"""

from tests.eval_rag_quality import evaluate_query


def _story(sid, client):
    return {
        "id": sid,
        "Client": client,
        "Era": "Era One",
        "Project": f"Project {sid}",
        "Theme": "Execution & Delivery",
    }


STORIES = [
    _story("j", "JP Morgan Chase"),
    _story("r", "RBC"),
    _story("a", "Accenture"),
    _story("m", "Multiple Clients"),
]


def _sources(*ids):
    return [{"id": i, "title": f"Title {i}", "client": ""} for i in ids]


def _run(spec, answer, sources):
    def rag_fn(query, filters, stories):
        return {"answer_md": answer, "sources": sources}

    return evaluate_query(spec, rag_fn, STORIES)


def _client_spec(expected, **extra):
    return {
        "id": 1,
        "query": "q",
        "category": "client",
        "expected_client": expected,
        **extra,
    }


class TestClientCategory:
    def test_shortened_name_bolded_passes(self):
        r = _run(
            _client_spec("JP Morgan Chase"),
            "At **JP Morgan** he rebuilt payments.",
            _sources("j"),
        )
        assert r.checks.get("client_attribution") is True
        assert r.checks.get("client_bolded") is True
        assert r.passed is True

    def test_full_name_bolded_passes(self):
        r = _run(
            _client_spec("JP Morgan Chase"),
            "At **JP Morgan Chase & Co.** he rebuilt payments.",
            _sources("j"),
        )
        assert r.passed is True

    def test_client_in_sources_but_not_bolded_fails(self):
        r = _run(
            _client_spec("JP Morgan Chase"),
            "At JP Morgan he rebuilt payments.",
            _sources("j"),
        )
        assert r.checks.get("client_attribution") is True
        assert r.checks.get("client_bolded") is False
        assert r.passed is False

    def test_expected_client_absent_from_sources_fails(self):
        r = _run(
            _client_spec("JP Morgan Chase"),
            "At **JP Morgan** he rebuilt payments.",
            _sources("r"),
        )
        assert r.checks.get("client_attribution") is False
        assert r.passed is False

    def test_bolded_client_of_another_source_counts(self):
        r = _run(
            _client_spec("JP Morgan Chase"),
            "He did similar work at **RBC**.",
            _sources("j", "r"),
        )
        assert r.checks.get("client_bolded") is True
        assert r.passed is True

    def test_bolded_name_of_no_source_client_does_not_count(self):
        r = _run(
            _client_spec("JP Morgan Chase"),
            "Unlike **Capital One**, JP Morgan moved fast.",
            _sources("j"),
        )
        assert r.checks.get("client_bolded") is False
        assert r.passed is False

    def test_multi_client_passes_without_bold(self):
        r = _run(
            _client_spec("Accenture", is_multi_client=True),
            "He scaled the CIC at Accenture.",
            _sources("a"),
        )
        assert r.passed is True

    def test_multi_client_passes_on_three_named_source_clients(self):
        r = _run(
            _client_spec("Fiserv", is_multi_client=True),
            "Work across several banks.",
            _sources("j", "r", "a"),
        )
        assert r.passed is True


class TestSurgicalAndEdge:
    def test_surgical_attribution_reads_sources(self):
        spec = {
            "id": 1,
            "query": "q",
            "category": "surgical",
            "expected_client": "JP Morgan Chase",
        }
        r = _run(spec, "At JP Morgan he aligned 3 regions.", _sources("j"))
        assert r.checks.get("client_attribution") is True

    def test_edge_combo_fails_when_sources_lack_the_client(self):
        spec = {
            "id": 1,
            "query": "q",
            "category": "edge",
            "expected_behavior": "synthesis_client_combo",
            "expected_client": "JP Morgan Chase",
        }
        r = _run(spec, "At **JP Morgan** delivery changed.", _sources("r"))
        assert r.checks.get("client_attribution") is False
        assert r.passed is False
