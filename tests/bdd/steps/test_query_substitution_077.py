"""
BDD step definitions for query_substitution_077.feature.

Pure unit tests -- no Playwright, no API calls, no Pinecone.
Tests _substitute_matt_subject() and _build_retrieval_query() in utils/scoring.py.
"""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/query_substitution_077.feature")


@pytest.fixture
def ctx():
    return {}


@given(parsers.parse('the query "{query}"'))
def given_query(ctx, query):
    ctx["query"] = query


@given(parsers.parse('the query "{query}" and intent family "{family}"'))
def given_query_and_family(ctx, query, family):
    ctx["query"] = query
    ctx["family"] = family


@when("_substitute_matt_subject is applied")
def when_substitute(ctx):
    from utils.scoring import _substitute_matt_subject

    ctx["result"] = _substitute_matt_subject(ctx["query"])


@when("_build_retrieval_query is called")
def when_build(ctx):
    from utils.scoring import _build_retrieval_query

    ctx["result"] = _build_retrieval_query(ctx["query"], ctx["family"])


@then(parsers.parse('the retrieval query does not contain "{token}"'))
def then_not_contains(ctx, token):
    assert token not in ctx["result"], (
        f"Expected retrieval query to not contain {token!r} "
        f"but got: {ctx['result']!r}"
    )


@then(parsers.parse('the retrieval query contains "{token}"'))
def then_contains(ctx, token):
    assert token in ctx["result"], (
        f"Expected retrieval query to contain {token!r} " f"but got: {ctx['result']!r}"
    )


@then(parsers.parse('the retrieval query equals "{expected}"'))
def then_equals(ctx, expected):
    assert ctx["result"] == expected, (
        f"Expected retrieval query to equal {expected!r} " f"but got: {ctx['result']!r}"
    )
