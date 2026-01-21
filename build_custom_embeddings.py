"""
build_custom_embeddings.py

Reads enriched STAR story data from a JSONL file, generates embeddings using
OpenAI's text-embedding-3-small (1536 dims), and upserts them into Pinecone.

Updated 12.05.25:
- Switched from MiniLM (384 dims) to OpenAI text-embedding-3-small (1536 dims)
- Better semantic matching for behavioral interview questions

Env (via .env or shell):
  STORIES_JSONL=echo_star_stories_nlp.jsonl
  OPENAI_API_KEY=...
  PINECONE_API_KEY=...
  PINECONE_INDEX_NAME=matt-portfolio-v2
  PINECONE_NAMESPACE=default
"""

import json
import logging
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s"
)
load_dotenv()

STORIES_JSONL = os.getenv("STORIES_JSONL", "echo_star_stories_nlp.jsonl")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "default")

EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dims


# ---------------------------
# Helpers
# ---------------------------
def _as_list(v) -> list[str]:
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    s = str(v).strip()
    if not s:
        return []
    if ";" in s:
        return [x.strip() for x in s.split(";") if x.strip()]
    if "," in s:
        return [x.strip() for x in s.split(",") if x.strip()]
    return [s]


def build_embedding_text(story: dict[str, Any]) -> str:
    """
    Build a rich, behavior-aware text representation for embeddings.
    """

    def _to_text(val, max_items: int = 3) -> str:
        if not val:
            return ""
        if isinstance(val, list):
            return " ".join(str(p).strip() for p in val[:max_items] if str(p).strip())
        return str(val).strip()

    theme = (
        story.get("Theme", "").strip() if isinstance(story.get("Theme"), str) else ""
    )
    industry = (
        story.get("Industry", "").strip()
        if isinstance(story.get("Industry"), str)
        else ""
    )
    sub_category = (
        story.get("Sub-category", "").strip()
        if isinstance(story.get("Sub-category"), str)
        else ""
    )

    summary_5p = (
        story.get("5PSummary", "").strip()
        if isinstance(story.get("5PSummary"), str)
        else ""
    )
    situation = _to_text(story.get("Situation"), max_items=2)
    task = _to_text(story.get("Task"), max_items=2)
    action = _to_text(story.get("Action"), max_items=3)
    result = _to_text(story.get("Result"), max_items=2)
    process_text = _to_text(story.get("Process"), max_items=3)

    tags = story.get("public_tags", "")
    if isinstance(tags, list):
        tags = ", ".join(tags)
    tags = tags.strip() if tags else ""

    parts: list[str] = []

    header_bits = []
    if theme:
        header_bits.append(f"[{theme}]")
    if industry:
        header_bits.append(f"in {industry}")
    if sub_category:
        header_bits.append(f"({sub_category})")

    if header_bits:
        parts.append(" ".join(header_bits))

    if summary_5p:
        parts.append(f"Summary: {summary_5p}")

    if situation:
        parts.append(f"Situation: {situation}")
    if task:
        parts.append(f"Task: {task}")
    if action:
        parts.append(f"Action: {action}")
    if result:
        parts.append(f"Result: {result}")

    if process_text:
        parts.append(f"Process: {process_text}")

    if tags:
        parts.append(f"Keywords: {tags}")

    return " ".join(p for p in parts if p)


def build_metadata(story: dict[str, Any]) -> dict[str, Any]:
    """Compact but rich metadata for UI/snippets + Pinecone filters."""
    cat = story.get("Category", "")
    sub = story.get("Sub-category", "")
    theme = story.get("Theme", "")
    domain = " / ".join([x for x in [cat, sub] if x])

    tags_list = _as_list(story.get("public_tags"))

    industry = story.get("Industry", "").strip()
    division = story.get("Division", "").strip()
    employer = story.get("Employer", "").strip()
    project = story.get("Project", "").strip()
    complexity = story.get("Project Scope / Complexity", "").strip()

    meta = {
        # CANONICAL FIELDS
        "id": story.get("id"),
        "Title": story.get("Title", "Untitled"),
        "Employer": employer,
        "Division": division,
        "Role": story.get("Role", "Unknown"),
        "Client": story.get("Client", "Unknown"),
        "Project": project,
        "Start_Date": story.get("Start_Date", ""),
        "End_Date": story.get("End_Date", ""),
        "Industry": industry,
        "Project Scope / Complexity": complexity,
        "Category": cat,
        "Sub-category": sub,
        "Theme": theme,
        "Era": story.get("Era", "").strip(),
        "Use Case(s)": _as_list(story.get("Use Case(s)")),
        "Competencies": _as_list(story.get("Competencies")),
        "Situation": _as_list(story.get("Situation")),
        "Task": _as_list(story.get("Task")),
        "Action": _as_list(story.get("Action")),
        "Result": _as_list(story.get("Result")),
        "Purpose": story.get("Purpose", ""),
        "Performance": _as_list(story.get("Performance")),
        "Process": _as_list(story.get("Process")),
        "5PSummary": story.get("5PSummary", ""),
        "public_tags": tags_list,
        # UI-FRIENDLY DUPLICATES
        "title": story.get("Title", "Untitled"),
        "employer": employer.lower() if employer else "",
        "division": division.lower() if division else "",
        "client": story.get("Client", "Unknown"),
        "role": story.get("Role", "Unknown"),
        "project": project.lower() if project else "",
        "industry": industry.lower() if industry else "",
        "complexity": complexity.lower() if complexity else "",
        "domain": domain,
        "tags": tags_list,
        "summary": story.get("5PSummary", ""),
    }
    return meta


def get_openai_embeddings(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """Generate embeddings using OpenAI API in batches."""
    client = OpenAI(api_key=OPENAI_API_KEY)
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        logging.info(
            f"📤 Embedding batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1} ({len(batch)} texts)"
        )

        response = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)

        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)

    return all_embeddings


# ---------------------------
# Load data
# ---------------------------
stories: list[dict[str, Any]] = []
with open(STORIES_JSONL) as f:
    for line in f:
        if line.strip():
            stories.append(json.loads(line))
logging.info(f"🔎 Loaded {len(stories)} stories from {STORIES_JSONL}")

# ---------------------------
# Build embedding texts
# ---------------------------
texts = [build_embedding_text(s) for s in stories]

if texts:
    logging.info("📝 Sample embedding text (first story):")
    logging.info(f"   {texts[0][:500]}...")

    # Check the failure story
    fail_idx = next(
        (i for i, s in enumerate(stories) if 'assumptions' in s.get('id', '')),
        None,
    )
    if fail_idx:
        logging.info("📝 Failure story embedding text:")
        logging.info(f"   {texts[fail_idx][:300]}...")

# ---------------------------
# Generate embeddings via OpenAI
# ---------------------------
logging.info(f"🤖 Generating embeddings with {EMBEDDING_MODEL}...")
embeddings = get_openai_embeddings(texts)
logging.info(f"✅ Generated {len(embeddings)} embeddings (dim={len(embeddings[0])})")

# ---------------------------
# Upsert to Pinecone
# ---------------------------
if not (PINECONE_API_KEY and PINECONE_INDEX_NAME):
    raise RuntimeError("PINECONE_API_KEY or PINECONE_INDEX_NAME is missing.")

pc = Pinecone(api_key=PINECONE_API_KEY)
logging.info(
    f"[INFO] Using Pinecone index='{PINECONE_INDEX_NAME}', namespace='{PINECONE_NAMESPACE}'"
)

existing = [i.name for i in pc.list_indexes()]
if PINECONE_INDEX_NAME not in existing:
    raise ValueError(
        f"Index '{PINECONE_INDEX_NAME}' does not exist. Available: {existing}"
    )

index = pc.Index(PINECONE_INDEX_NAME)

# Purge namespace
logging.info("🧹 Purging namespace (delete_all=True)…")
try:
    index.delete(delete_all=True, namespace=PINECONE_NAMESPACE)
except Exception as e:
    logging.warning(f"Purge warning: {e}")

# Upsert in batches
batch = 100
upserted = 0
for start in range(0, len(stories), batch):
    items = []
    for i in range(start, min(start + batch, len(stories))):
        vec = embeddings[i]
        meta = build_metadata(stories[i])
        vec_id = str(meta.get("id") or f"story-{i}")
        meta["id"] = vec_id
        items.append((vec_id, vec, meta))

    if items:
        index.upsert(vectors=items, namespace=PINECONE_NAMESPACE)
        upserted += len(items)
        logging.info(f"⬆️ Upserted {upserted}/{len(stories)}")

logging.info("✅ Pinecone index updated successfully.")

# ---------------------------
# Derive Intent Families from Story Data
# ---------------------------
# logging.info("🧠 Deriving intent families from story data...")

# derived_intents = {
#     "background": [
#         "Tell me about Matt's background",
#         "Who is Matt Pugmire?",
#         "Walk me through Matt's career",
#         "What's Matt's professional experience?",
#         "Give me a quick overview of Matt's experience",
#     ],
#     "synthesis": [
#         # Recruiter synthesis questions - static, always needed
#         "What problems does Matt solve?",
#         "What are Matt's strengths?",
#         "What patterns in Matt's work?",
#         "What evidence of Director level experience?",
#         "What evidence shows Matt can operate at VP level?",
#         "What makes Matt different from other candidates?",
#         "How does Matt handle failure?",
#         "How does Matt handle resistance?",
#         "What transformation problems does Matt consistently solve?",
#     ],
#     "behavioral": [
#         "Tell me about a time Matt failed",
#         "Tell me about a time you failed",
#         "Describe a situation where Matt had to influence stakeholders",
#         "How do you handle conflict?",
#         "Give me an example of leadership",
#         "Tell me about a difficult situation you handled",
#         "Tell me about a challenge Matt overcame",
#     ],
#     "leadership": [
#         "What's Matt's leadership style?",
#         "How does Matt lead teams?",
#         "What's Matt's management philosophy?",
#         "How does Matt coach and develop people?",
#         "How did Matt scale teams?",
#         "How did Matt build high-performing teams?",
#     ],
# }

# # Extract unique Themes
# themes = set()
# for s in stories:
#     theme = s.get("Theme", "").strip()
#     if theme and theme != "Career Narrative":
#         themes.add(theme)

# # Generate theme-based intents
# derived_intents["themes"] = []
# for theme in sorted(themes):
#     derived_intents["themes"].extend(
#         [
#             f"Tell me about Matt's {theme} experience",
#             f"Show me {theme} projects",
#             f"Matt's {theme} work",
#         ]
#     )

# # Extract unique Clients (exclude generic ones)
# clients = set()
# skip_clients = {
#     "Multiple Clients",
#     "Accenture",
#     "Career Narrative",
#     "Independent",
#     "Multiple Financial Services Clients",
# }
# for s in stories:
#     client = s.get("Client", "").strip()
#     if client and client not in skip_clients:
#         clients.add(client)

# # Generate client-based intents
# derived_intents["clients"] = []
# for client in sorted(clients):
#     derived_intents["clients"].extend(
#         [
#             f"Tell me about Matt's work at {client}",
#             f"Show me {client} projects",
#             f"Matt's {client} experience",
#         ]
#     )

# # Extract unique Industries
# industries = set()
# for s in stories:
#     industry = s.get("Industry", "").strip()
#     if (
#         industry and "/" not in industry
#     ):  # Skip compound like "Financial Services / Banking"
#         industries.add(industry)
#     elif industry and "/" in industry:
#         # Split compound industries
#         for ind in industry.split("/"):
#             ind = ind.strip()
#             if ind:
#                 industries.add(ind)

# # Generate industry-based intents
# derived_intents["industries"] = []
# for industry in sorted(industries):
#     derived_intents["industries"].extend(
#         [
#             f"Tell me about Matt's {industry} experience",
#             f"Show me {industry} projects",
#             f"Matt's work in {industry}",
#         ]
#     )

# # Technical intents from common tags
# derived_intents["technical"] = [
#     "What is Matt's experience with cloud platforms?",
#     "Show me Matt's platform engineering work",
#     "Tell me about Matt's cloud modernization projects",
#     "What's Matt's experience with microservices?",
#     "Show me Matt's GenAI work",
#     "What's Matt's technical background?",
#     "Tell me about Matt's architecture experience",
#     "Show me Matt's DevOps experience",
#     "Tell me about Matt's CI/CD work",
#     "What's Matt's experience with agile transformation?",
# ]

# # Innovation intents
# derived_intents["innovation"] = [
#     "What's Matt's approach to innovation?",
#     "Tell me about Matt's innovation center work",
#     "How does Matt drive innovation?",
#     "Tell me about the Cloud Innovation Center",
#     "Where has Matt scaled innovation to production?",
# ]

# # Delivery intents
# derived_intents["delivery"] = [
#     "How did Matt achieve faster delivery?",
#     "How does Matt ensure teams deliver with quality?",
#     "Show me Matt's biggest delivery wins",
#     "What results has Matt achieved?",
#     "How did Matt accelerate team delivery?",
# ]

# # Stakeholder intents
# derived_intents["stakeholders"] = [
#     "How does Matt handle difficult stakeholders?",
#     "Tell me about Matt's stakeholder management",
#     "How does Matt work with executives?",
#     "How does Matt manage up?",
# ]

# # Flatten for embedding generation
# all_derived_intents = []
# intent_to_family = {}
# for family, intents in derived_intents.items():
#     for intent in intents:
#         if intent not in all_derived_intents:  # Dedupe
#             all_derived_intents.append(intent)
#             intent_to_family[intent] = family

# logging.info(
#     f"📊 Derived {len(all_derived_intents)} intents across {len(derived_intents)} families"
# )

# # Generate intent embeddings
# logging.info("🤖 Generating intent embeddings...")
# intent_texts = all_derived_intents
# intent_embeddings = get_openai_embeddings(intent_texts)

# # Build intent data structure
# intent_data = {
#     "families": derived_intents,
#     "intent_to_family": intent_to_family,
#     "embeddings": {
#         intent: emb
#         for intent, emb in zip(all_derived_intents, intent_embeddings, strict=False)
#     },
# }

# # Save to data/intent_embeddings.json
# os.makedirs("data", exist_ok=True)
# intent_cache_path = "data/intent_embeddings.json"
# with open(intent_cache_path, 'w') as f:
#     json.dump(intent_data, f)
# logging.info(f"💾 Saved intent embeddings to {intent_cache_path}")
