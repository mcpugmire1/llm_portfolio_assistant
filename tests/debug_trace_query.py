"""Debug trace: run a single query through the full RAG pipeline with verbose logging."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

# Enable DEBUG
import config.debug

config.debug.DEBUG = True

# Mock Streamlit
mock_st = MagicMock()
mock_st.session_state = {}


def load_stories():
    """Load story corpus from JSONL file."""
    story_path = Path(__file__).parent.parent / "echo_star_stories_nlp.jsonl"
    stories = []
    with open(story_path) as f:
        for line in f:
            if line.strip():
                stories.append(json.loads(line))
    return stories


def trace_query(query: str):
    """Run query through full pipeline with instrumented logging."""
    print(f"\n{'='*70}")
    print(f"TRACE QUERY: \"{query}\"")
    print(f"{'='*70}\n")

    with patch("streamlit.session_state", mock_st.session_state):
        with patch("ui.pages.ask_mattgpt.backend_service.st", mock_st):
            with patch("services.rag_service.st", mock_st):
                # Load stories
                from ui.pages.ask_mattgpt.backend_service import (
                    rag_answer,
                    sync_portfolio_metadata,
                )

                stories = load_stories()
                print(f"[1] Loaded {len(stories)} stories")

                # Sync SYNTHESIS_THEMES and MATT_DNA from story data
                sync_portfolio_metadata(stories)
                print("    (portfolio metadata synced)\n")

                # --- STEP 2: Pinecone results ---
                from services.pinecone_service import SEARCH_TOP_K
                from services.rag_service import semantic_search

                search_result = semantic_search(
                    query, {}, stories=stories, top_k=SEARCH_TOP_K
                )
                pool = search_result["results"]
                print("[2] PINECONE RESULTS (top 5 with scores):")
                for i, s in enumerate(pool[:5]):
                    print(
                        f"    [{i+1}] pc={s.get('pc', 0.0):.4f} | {s.get('Title', '?')[:60]} | Theme={s.get('Theme', '?')}"
                    )
                print(
                    f"    confidence={search_result['confidence']}, top_score={search_result['top_score']:.4f}\n"
                )

                # --- STEP 3: Semantic router classification ---
                from services.semantic_router import is_portfolio_query_semantic

                semantic_valid, semantic_score, matched_intent, intent_family = (
                    is_portfolio_query_semantic(query)
                )
                print("[3] SEMANTIC ROUTER:")
                print(f"    valid={semantic_valid}, score={semantic_score:.4f}")
                print(f"    matched_intent=\"{matched_intent}\"")
                print(f"    intent_family=\"{intent_family}\"\n")

                # --- STEP 4: Entity detection ---
                from ui.pages.ask_mattgpt.backend_service import detect_entity

                entity_match = detect_entity(query, stories)
                print("[4] ENTITY DETECTION:")
                print(f"    entity_match={entity_match}\n")

                # --- STEP 5: Query intent classification ---
                from ui.pages.ask_mattgpt.backend_service import classify_query_intent

                query_intent = classify_query_intent(query, stories)
                print("[5] QUERY INTENT:")
                print(f"    query_intent=\"{query_intent}\"\n")

                # --- STEP 6: Which ranking branch? ---
                is_synthesis = query_intent == "synthesis"
                print("[6] RANKING BRANCH:")
                if is_synthesis:
                    print("    → SYNTHESIS mode")
                elif intent_family == "narrative" and pool:
                    first = pool[0]
                    if first.get("Theme") == "Professional Narrative":
                        print("    → NARRATIVE mode (Professional Narrative at #1)")
                    else:
                        print(
                            "    → NARRATIVE mode (pool[0] is not Professional Narrative → diversify)"
                        )
                else:
                    if entity_match:
                        print(
                            f"    → ENTITY PIN mode ({entity_match[0]}={entity_match[1]})"
                        )
                    elif query_intent == "narrative":
                        print(
                            "    → ELSE branch: query_intent=narrative → PC score sort (skip diversity)"
                        )
                    else:
                        print("    → ELSE branch: diversify_results()")
                print()

                # --- STEP 7: Full rag_answer call ---
                print("[7] FULL rag_answer() CALL:")
                print(
                    "    (running with DEBUG=True, check output above for full trace)"
                )
                result = rag_answer(query, {}, stories)

                print("\n[8] FINAL RESULT:")
                print(
                    f"    sources: {[s.get('title', '?')[:50] for s in result.get('sources', [])]}"
                )
                print(f"    default_mode: {result.get('default_mode')}")
                answer = result.get("answer_md", "")[:200]
                print(f"    answer (first 200 chars): {answer}")
                print(f"\n{'='*70}\n")


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Tell me about Matt"
    trace_query(query)
