# client_distribution.py
import json
from collections import Counter

JSONL_FILE = "echo_star_stories_nlp.jsonl"

stories = []
with open(JSONL_FILE, encoding="utf-8") as f:
    for line in f:
        if line.strip():
            stories.append(json.loads(line))

clients = [s.get("Client", "Unknown") for s in stories]
print(f"\n📊 Client Distribution ({len(stories)} stories):\n")
for client, count in Counter(clients).most_common(15):
    pct = count / len(stories) * 100
    print(f"{count:3d} ({pct:4.1f}%)  {client}")
