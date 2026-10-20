"""Breadth counts and skip accounting in the golden eval (MATTGPT-338).

Eras, projects and named clients are counted from the answer's source
stories, looked up by id, leaving out Professional Narrative stories (Theme).
Named clients are the distinct non-generic Client values of those stories, so
an answer that calls a client by another name still counts it. A skipped query is reported as skipped, not passed. Pure functions
and a fake rag_fn: no model or Pinecone call.
"""

from tests.eval_rag_quality import (
    EvalResult,
    count_eras,
    count_named_clients,
    count_projects,
    evaluate_query,
    fs_era_present,
    generate_report,
)

FS_ERA = "Financial Services Platform Modernization"


def _story(sid, client, era, project, theme="Execution & Delivery"):
    return {
        "id": sid,
        "Client": client,
        "Era": era,
        "Project": project,
        "Theme": theme,
    }


STORIES = [
    _story("a", "JP Morgan Chase", "Era One", "Project A"),
    _story("b", "Accenture", "Era One", "Project B"),
    _story("c", "Fortune 500 Clients", "Era Two", "Project B"),
    _story("d", "Independent Project", "Era Three", "Project C"),
    _story("e", "Accenture", "Era Four", "Project D", "Professional Narrative"),
    _story("f", "RBC", FS_ERA, "Project E"),
    _story("g", "Accenture", FS_ERA, "Project F", "Professional Narrative"),
    _story("h", "JP Morgan Chase", FS_ERA, "Project G"),
]


def _sources(*ids):
    return [{"id": i, "title": f"Title {i}", "client": ""} for i in ids]


class TestCountEras:
    def test_distinct_eras_of_sources(self):
        assert count_eras(_sources("a", "b", "c"), STORIES) == 2

    def test_repeated_source_counts_once(self):
        assert count_eras(_sources("a", "a"), STORIES) == 1

    def test_unknown_id_is_ignored(self):
        assert count_eras(_sources("a", "zzz"), STORIES) == 1

    def test_no_sources_is_zero(self):
        assert count_eras([], STORIES) == 0

    def test_professional_narrative_source_is_excluded(self):
        assert count_eras(_sources("a", "e"), STORIES) == 1
        assert count_eras(_sources("e"), STORIES) == 0


class TestCountProjects:
    def test_distinct_projects_of_sources(self):
        assert count_projects(_sources("a", "b", "c", "d"), STORIES) == 3

    def test_unknown_id_is_ignored(self):
        assert count_projects(_sources("b", "zzz"), STORIES) == 1

    def test_professional_narrative_source_is_excluded(self):
        assert count_projects(_sources("a", "e"), STORIES) == 1
        assert count_projects(_sources("e"), STORIES) == 0


class TestFsEraPresent:
    def test_true_when_a_source_has_the_fs_era(self):
        assert fs_era_present(_sources("a", "f"), STORIES) is True

    def test_false_when_no_source_has_it(self):
        assert fs_era_present(_sources("a", "b"), STORIES) is False

    def test_professional_narrative_source_does_not_count(self):
        assert fs_era_present(_sources("g"), STORIES) is False

    def test_no_sources_is_false(self):
        assert fs_era_present([], STORIES) is False


class TestCountNamedClients:
    def test_every_named_client_counts_including_accenture(self):
        assert count_named_clients(_sources("a", "b", "f"), STORIES) == 3

    def test_one_client_across_several_stories_counts_once(self):
        assert count_named_clients(_sources("a", "h"), STORIES) == 1

    def test_generic_clients_are_not_counted(self):
        assert count_named_clients(_sources("c", "d"), STORIES) == 0

    def test_repeated_client_counts_once(self):
        assert count_named_clients(_sources("f", "f"), STORIES) == 1

    def test_unknown_id_is_ignored(self):
        assert count_named_clients(_sources("f", "zzz"), STORIES) == 1

    def test_professional_narrative_source_is_excluded(self):
        assert count_named_clients(_sources("e"), STORIES) == 0
        assert count_named_clients(_sources("e", "b"), STORIES) == 1

    def test_no_sources_is_zero(self):
        assert count_named_clients([], STORIES) == 0


def _rag_fn(answer_md, sources):
    return lambda query, filters, stories: {"answer_md": answer_md, "sources": sources}


class TestEvaluateQuery:
    def test_breadth_lands_in_details(self):
        spec = {"id": 1, "query": "q", "category": "marketing"}
        answer = "Work at JP Morgan and Accenture."
        result = evaluate_query(spec, _rag_fn(answer, _sources("a", "c")), STORIES)

        assert result.details.get("eras") == 2
        assert result.details.get("projects") == 2
        # "a" is JP Morgan Chase, "c" is generic: Accenture is named in the
        # text but is no source's client.
        assert result.details.get("named_clients") == 1

    def test_a_client_called_by_another_name_counts_from_its_sources(self):
        # The text says only "JP Morgan"; the sources are JP Morgan Chase and
        # RBC, so both count and the text's wording does not.
        spec = {"id": 1, "query": "q", "category": "marketing"}
        answer = "At JP Morgan he rebuilt the identity platform."
        result = evaluate_query(spec, _rag_fn(answer, _sources("h", "f")), STORIES)

        assert result.details.get("named_clients") == 2

    def test_counts_over_all_sources_and_shown_cards(self):
        spec = {"id": 1, "query": "q", "category": "marketing"}
        sources = _sources("a", "b", "c", "f")
        result = evaluate_query(spec, _rag_fn("Work at JP Morgan.", sources), STORIES)
        d = result.details

        assert d.get("eras") == 3
        assert d.get("eras_shown") == 2
        assert d.get("projects") == 3
        assert d.get("projects_shown") == 2
        assert d.get("fs_era_present") is True
        assert d.get("fs_era_present_shown") is False
        assert d.get("named_clients") == 3
        assert "named_clients_shown" not in d

    def test_synthesis_answer_uses_the_synthesis_card_cap(self, monkeypatch):
        # agy_answer() leaves the card layout in __ask_query_intent__; the
        # fake sets it the way the UI reads it.
        state = {}
        monkeypatch.setattr("streamlit.session_state", state)
        sources = _sources("a", "b", "c", "f", "d")

        def rag_fn(query, filters, stories):
            state["__ask_query_intent__"] = "synthesis"
            return {"answer_md": "An answer.", "sources": sources}

        spec = {"id": 1, "query": "q", "category": "marketing"}
        d = evaluate_query(spec, rag_fn, STORIES).details

        assert d.get("eras_shown") == 4
        assert d.get("projects_shown") == 4
        assert d.get("fs_era_present_shown") is True

    def test_entity_detection_is_skipped_not_passed(self):
        spec = {"id": 1, "query": "q", "category": "entity_detection"}
        result = evaluate_query(spec, _rag_fn("An answer.", _sources("a")), STORIES)

        assert getattr(result, "skipped", False) is True
        assert result.passed is False


def _result(category, passed, skipped=False, details=None):
    r = EvalResult(query_id=1, query="q", category=category, passed=passed)
    r.details = details or {}
    # Set after construction so Red fails on assertions, not a TypeError.
    r.skipped = skipped
    return r


class TestGenerateReport:
    def test_skipped_is_neither_passed_nor_failed(self):
        report = generate_report(
            [
                _result("narrative", True),
                _result("narrative", False),
                _result("entity_detection", False, skipped=True),
            ]
        )

        assert report.get("skipped") == 1
        assert report["passed"] == 1
        assert report["failed"] == 1
        assert report["pass_rate"] == 50.0
        assert report["by_category"]["entity_detection"].get("skipped") == 1

    def test_category_breadth_min_and_mean(self):
        low = {"eras": 1, "projects": 2, "named_clients": 0}
        high = {"eras": 3, "projects": 4, "named_clients": 2}
        report = generate_report(
            [
                _result("narrative", True, details=low),
                _result("narrative", True, details=high),
            ]
        )
        cat = report["by_category"]["narrative"]

        assert cat.get("eras_min") == 1
        assert cat.get("eras_mean") == 2.0
        assert cat.get("projects_min") == 2
        assert cat.get("projects_mean") == 3.0
        assert cat.get("named_clients_min") == 0
        assert cat.get("named_clients_mean") == 1.0

    def test_category_shown_breadth_and_fs_era_counts(self):
        low = {"eras_shown": 1, "projects_shown": 1}
        low.update(fs_era_present=True, fs_era_present_shown=False)
        high = {"eras_shown": 3, "projects_shown": 2}
        high.update(fs_era_present=False, fs_era_present_shown=False)
        report = generate_report(
            [
                _result("narrative", True, details=low),
                _result("narrative", True, details=high),
            ]
        )
        cat = report["by_category"]["narrative"]

        assert cat.get("eras_shown_min") == 1
        assert cat.get("eras_shown_mean") == 2.0
        assert cat.get("projects_shown_min") == 1
        assert cat.get("projects_shown_mean") == 1.5
        assert cat.get("fs_era_present_count") == 1
        assert cat.get("fs_era_present_shown_count") == 0
