"""
Unit tests for Pinecone query egress: pinecone_semantic_search()
requests ids and scores only.

Every story is uploaded with its full text as metadata (build_custom_embeddings.py),
so a top_k=25 query returns about 205 KB (one measured query, Oct 10, 2026).
The app reads only the match id (stories are looked up locally) and the
summary snippet, which is the story's own 5PSummary. These tests pin the
contract: queries pass include_metadata=False, the snippet comes from the
local story, and stories still resolve from the match id.
"""

from unittest.mock import MagicMock, patch


def _bare_match(sid, score):
    """A Pinecone match as returned with include_metadata=False: id and score only."""
    m = MagicMock()
    m.id = sid
    m.score = score
    m.metadata = None
    return m


class TestPineconeSemanticSearchEgress:
    @patch("services.pinecone_service._init_pinecone")
    @patch("services.pinecone_service._embed")
    @patch("services.pinecone_service.st")
    def test_query_requests_ids_and_scores_only(self, mock_st, mock_embed, mock_init):
        """The query must not ask Pinecone for metadata."""
        from services.pinecone_service import pinecone_semantic_search

        mock_st.session_state = {}
        mock_embed.return_value = [0.1] * 1536
        mock_idx = MagicMock()
        mock_idx.query.return_value = MagicMock(matches=[])
        mock_init.return_value = mock_idx

        pinecone_semantic_search("a query", {}, [])

        assert mock_idx.query.call_args.kwargs["include_metadata"] is False

    @patch("services.pinecone_service._init_pinecone")
    @patch("services.pinecone_service._embed")
    @patch("services.pinecone_service.st")
    def test_snippet_comes_from_local_story(self, mock_st, mock_embed, mock_init):
        """With no metadata on the match, the hit's snippet is the local story's 5PSummary."""
        from services.pinecone_service import pinecone_semantic_search

        mock_st.session_state = {}
        mock_embed.return_value = [0.1] * 1536
        mock_idx = MagicMock()
        mock_idx.query.return_value = MagicMock(matches=[_bare_match("story-1", 0.75)])
        mock_init.return_value = mock_idx

        stories = [{"id": "story-1", "Title": "Test", "5PSummary": "local summary"}]
        result = pinecone_semantic_search("a query", {}, stories)

        assert result[0]["story"]["id"] == "story-1"
        assert result[0]["snippet"] == "local summary"
