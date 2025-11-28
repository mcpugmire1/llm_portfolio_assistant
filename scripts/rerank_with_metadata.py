def rerank_results_by_metadata(
    results: list[dict],
    user_query: str,
    expected_tags: list[str] = None,
    expected_subcategory: str = None,
    top_k: int = 3,
) -> list[dict]:
    """
    Reranks Pinecone results by matching public_tags and sub-category
    against expectations extracted from the rewritten query.

    Args:
        results (List[Dict]): Pinecone-matched documents with metadata.
        user_query (str): The rewritten semantic search query.
        expected_tags (List[str], optional): Expected tag list to boost.
        expected_subcategory (str, optional): Expected sub-category match.
        top_k (int): How many results to return.

    Returns:
        List[Dict]: Reranked and filtered results.
    """

    def score(result):
        score = result.get("score", 0)
        metadata = result.get("metadata", {})

        # Boost if public tags overlap
        tags = metadata.get("public_tags", [])
        if expected_tags:
            overlap = len(set(tags) & set(expected_tags))
            score += overlap * 0.3  # weight tag match

        # Boost if sub-category matches
        if (
            expected_subcategory
            and metadata.get("sub-category") == expected_subcategory
        ):
            score += 0.5  # weight sub-category match

        return score

    # Sort by composite score
    reranked = sorted(results, key=score, reverse=True)
    return reranked[:top_k]
