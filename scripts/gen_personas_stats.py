import json
from collections import Counter

with open("echo_star_stories_nlp_with_personas.jsonl") as f:
    data = [json.loads(line) for line in f]

# Count persona frequency
all_personas = [p for story in data for p in story.get("personas", [])]
print(Counter(all_personas))
