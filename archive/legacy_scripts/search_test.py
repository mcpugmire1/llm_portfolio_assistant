# search_test.py
from app_next import (
    _KNOWN_VOCAB,
    STORIES,
    is_nonsense,
    semantic_search,
    token_overlap_ratio,
)

print(f"Loaded {len(STORIES)} stories")

# A relevant query
query1 = "payments modernization"
res1 = semantic_search(
    query1,
    {
        "q": query1,
        "personas": [],
        "clients": [],
        "domains": [],
        "roles": [],
        "tags": [],
        "has_metric": False,
    },
)
print("\nQuery 1:", query1)
print("Results:", [s["title"] for s in res1])
print("Count:", len(res1))
print("Nonsense reason:", is_nonsense(query1))
print("Overlap ratio:", token_overlap_ratio(query1, _KNOWN_VOCAB))

# An irrelevant query
query2 = "baseball caps at Walmart"
res2 = semantic_search(
    query2,
    {
        "q": query2,
        "personas": [],
        "clients": [],
        "domains": [],
        "roles": [],
        "tags": [],
        "has_metric": False,
    },
)
print("\nQuery 2:", query2)
print("Results:", [s["title"] for s in res2])
print("Count:", len(res2))
print("Nonsense reason:", is_nonsense(query2))
print("Overlap ratio:", token_overlap_ratio(query2, _KNOWN_VOCAB))
