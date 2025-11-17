"""
MattGPT RAG Handler Lambda
Processes user queries through nonsense filtering, vector search, and LLM generation
"""
import json
import os
from typing import Dict, List, Optional
import boto3
from pinecone import Pinecone
from openai import OpenAI

# Initialize clients
s3_client = boto3.client('s3')
openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
index = pc.Index(os.environ['PINECONE_INDEX'])

# Load system prompt from file
def load_system_prompt():
    """Load Agy system prompt from file"""
    try:
        # Try to load from local file (packaged with Lambda)
        prompt_path = os.path.join(os.path.dirname(__file__), 'agy_system.txt')
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r') as f:
                return f.read()
    except Exception as e:
        print(f"Warning: Could not load system prompt from file: {e}")

    # Fallback prompt if file not found
    return """You are Agy 🐾 — Matt Pugmire's professional portfolio assistant.

You ONLY answer questions about Matt's transformation work. For off-topic queries, respond:
"🐾 I can only discuss Matt's transformation experience. Ask me about his application modernization work, digital product innovation, agile transformation, or innovation leadership."

CRITICAL: Base your answer ONLY on the context provided. If the context doesn't contain relevant information, say so honestly."""

SYSTEM_PROMPT = load_system_prompt()

def lambda_handler(event, context):
    """Main Lambda handler for RAG queries"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        query = body.get('query', '').strip()

        if not query:
            return create_response(400, {'error': 'Query is required'})

        # Step 1: Check nonsense filter
        nonsense_category = check_nonsense_filter(query)
        if nonsense_category:
            return create_response(200, {
                'answer': get_nonsense_response(nonsense_category),
                'sources': [],
                'isNonsense': True
            })

        # Step 2: Search Pinecone for relevant stories
        search_results = search_pinecone(query, top_k=7)

        if not search_results:
            return create_response(200, {
                'answer': "I don't have specific information about that in Matt's portfolio. His experience is primarily in enterprise digital transformation, agile delivery, and financial services. Want to explore what he has worked on?",
                'sources': [],
                'isNonsense': False
            })

        # Step 3: Format context from top 3 results
        context = format_context(search_results[:3])
        sources = extract_sources(search_results[:3])

        # Step 4: Generate answer using OpenAI
        answer = generate_answer(query, context)

        return create_response(200, {
            'answer': answer,
            'sources': sources,
            'isNonsense': False
        })

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})


def check_nonsense_filter(query: str) -> Optional[str]:
    """Check if query matches nonsense patterns"""
    try:
        import re

        # Load nonsense filters from S3
        bucket = os.environ.get('STORIES_BUCKET')
        if not bucket:
            return None

        response = s3_client.get_object(Bucket=bucket, Key='nonsense_filters.jsonl')
        filters_data = response['Body'].read().decode('utf-8')

        for line in filters_data.strip().split('\n'):
            if not line.strip():
                continue

            filter_obj = json.loads(line)
            pattern = filter_obj.get('pattern', '')
            category = filter_obj.get('category', 'general')

            if pattern:
                # Use regex pattern matching (case-insensitive)
                if re.search(pattern, query, re.IGNORECASE):
                    return category

        return None

    except Exception as e:
        print(f"Error checking nonsense filter: {str(e)}")
        return None


def get_nonsense_response(category: str) -> str:
    """Return canned response for nonsense queries"""
    # Per Agy system prompt: strict off-topic handling
    return "🐾 I can only discuss Matt's transformation experience. Ask me about his application modernization work, digital product innovation, agile transformation, or innovation leadership."


def search_pinecone(query: str, top_k: int = 7) -> List[Dict]:
    """Search Pinecone index for relevant stories"""
    try:
        from sentence_transformers import SentenceTransformer

        # Load embedding model (should be in Lambda layer)
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Generate query embedding
        query_embedding = model.encode(query).tolist()

        # Search Pinecone
        namespace = os.environ.get('PINECONE_NAMESPACE', 'default')
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace=namespace,
            include_metadata=True
        )

        return [match for match in results.get('matches', [])]

    except Exception as e:
        print(f"Error searching Pinecone: {str(e)}")
        return []


def format_context(matches: List[Dict]) -> str:
    """Format top matches into context for LLM"""
    context_parts = []

    for i, match in enumerate(matches, 1):
        metadata = match.get('metadata', {})

        story_context = f"""
Story {i}:
Title: {metadata.get('title', 'N/A')}
Client: {metadata.get('client', 'N/A')}
Role: {metadata.get('role', 'N/A')}
Industry: {metadata.get('industry', 'N/A')}

Situation: {metadata.get('situation', 'N/A')}
Task: {metadata.get('task', 'N/A')}
Action: {metadata.get('action', 'N/A')}
Result: {metadata.get('result', 'N/A')}

Key Metrics: {metadata.get('performance', 'N/A')}
"""
        context_parts.append(story_context.strip())

    return "\n\n---\n\n".join(context_parts)


def extract_sources(matches: List[Dict]) -> List[Dict]:
    """Extract source information from matches"""
    sources = []

    for match in matches:
        metadata = match.get('metadata', {})
        sources.append({
            'id': match.get('id', ''),
            'title': metadata.get('title', 'Untitled Project'),
            'client': metadata.get('client', 'Confidential'),
            'score': round(match.get('score', 0), 2)
        })

    return sources


def generate_answer(query: str, context: str) -> str:
    """Generate answer using OpenAI GPT-4"""
    try:
        messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': f"Context from Matt's portfolio:\n\n{context}\n\nUser Question: {query}\n\nProvide a conversational answer based on the context above."}
        ]

        response = openai_client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error generating answer: {str(e)}")
        return "I encountered an error generating a response. Please try again."


def create_response(status_code: int, body: Dict) -> Dict:
    """Create API Gateway response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps(body)
    }
