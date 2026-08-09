"""
BDD step definitions for query_strip_077.feature.

Pure unit tests -- no Playwright, no API calls, no Pinecone.
Tests _strip_matt_subject() and _build_retrieval_query() in utils/scoring.py.
"""

from pytest_bdd import scenarios

scenarios("../features/query_strip_077.feature")
