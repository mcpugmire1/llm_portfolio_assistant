"""
Unit tests for services/pinecone_service.py -- _embed() and pinecone_semantic_search().

Covers MATTGPT-162: embedding-failure signal propagation.
Today _embed swallows OpenAI failures and returns a zero vector, which reaches
Pinecone and produces a spurious low_pinecone rejection. These tests pin the
contract: _embed raises, pinecone_semantic_search catches narrowly around the
_embed call, sets __embed_failure__ on session_state, and returns None.
Pinecone-side failures continue to return None WITHOUT setting the flag.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestEmbedRaisesOnFailure:
    """_embed() must propagate OpenAI failures rather than returning zeros."""

    @patch("services.pinecone_service._get_openai_client")
    def test_embed_raises_on_openai_failure(self, mock_get_client):
        from services.pinecone_service import _embed

        mock_client = MagicMock()
        mock_client.embeddings.create.side_effect = RuntimeError("openai boom")
        mock_get_client.return_value = mock_client

        with pytest.raises(RuntimeError, match="openai boom"):
            _embed("some query")

    def test_embed_empty_string_still_returns_zero_vector(self):
        """Empty-input early return must be preserved -- guards against overreach in Green."""
        from services.pinecone_service import _DEF_DIM, _embed

        result = _embed("")
        assert result == [0.0] * _DEF_DIM


class TestPineconeSemanticSearchEmbedFailure:
    """pinecone_semantic_search() must distinguish embed failure from Pinecone failure."""

    @patch("services.pinecone_service._init_pinecone")
    @patch("services.pinecone_service._embed")
    @patch("services.pinecone_service.st")
    def test_embed_failure_sets_flag_and_returns_none(
        self, mock_st, mock_embed, mock_init
    ):
        from services.pinecone_service import pinecone_semantic_search

        mock_st.session_state = {}
        mock_init.return_value = MagicMock()  # Pinecone index present
        mock_embed.side_effect = RuntimeError("openai boom")

        result = pinecone_semantic_search("a query", {}, [])

        assert result is None
        assert mock_st.session_state.get("__embed_failure__") is True

    @patch("services.pinecone_service._init_pinecone")
    @patch("services.pinecone_service._embed")
    @patch("services.pinecone_service.st")
    def test_pinecone_query_failure_does_not_set_embed_flag(
        self, mock_st, mock_embed, mock_init
    ):
        """Pinecone-side failure returns None without setting the embed flag -- regression guard."""
        from services.pinecone_service import pinecone_semantic_search

        mock_st.session_state = {}
        mock_embed.return_value = [0.1] * 1536  # valid vector
        mock_idx = MagicMock()
        mock_idx.query.side_effect = RuntimeError("pinecone boom")
        mock_init.return_value = mock_idx

        result = pinecone_semantic_search("a query", {}, [])

        assert result is None
        assert "__embed_failure__" not in mock_st.session_state

    @patch("services.pinecone_service._init_pinecone")
    @patch("services.pinecone_service._embed")
    @patch("services.pinecone_service.st")
    def test_normal_path_returns_hits_and_does_not_set_embed_flag(
        self, mock_st, mock_embed, mock_init
    ):
        """Successful search returns list of hit dicts with expected shape and does not set flag."""
        from services.pinecone_service import pinecone_semantic_search

        mock_st.session_state = {}
        mock_embed.return_value = [0.1] * 1536

        mock_match = MagicMock()
        mock_match.metadata = {"id": "story-1"}
        mock_match.score = 0.75
        mock_idx = MagicMock()
        mock_idx.query.return_value = MagicMock(matches=[mock_match])
        mock_init.return_value = mock_idx

        stories = [{"id": "story-1", "Title": "Test", "5PSummary": "s"}]
        result = pinecone_semantic_search("a query", {}, stories)

        assert isinstance(result, list)
        assert len(result) == 1
        hit = result[0]
        assert hit["story"]["id"] == "story-1"
        assert set(hit.keys()) >= {"story", "pc_score", "kw_score", "score", "snippet"}
        assert hit["pc_score"] == 0.75
        assert "__embed_failure__" not in mock_st.session_state
