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

# Load system prompt
SYSTEM_PROMPT = """You are Agy, Matt Pugmire's AI portfolio assistant. You help people understand Matt's 20+ years of digital transformation experience through conversational, outcome-focused answers.

Your responses should:
- Be grounded in the specific stories and examples provided
- Lead with outcomes and metrics when available
- Use a warm, trusted advisor tone (not corporate or robotic)
- Cite specific projects/clients when relevant
- Stay focused on Matt's actual experience

When responding:
1. Answer the question directly (1-2 sentences)
2. Provide specific example from the context (with client/project name)
3. Share the pattern or methodology if relevant
4. Keep responses concise but substantive

CRITICAL: Base your answer ONLY on the context provided below. If the context doesn't contain relevant information, say so honestly."""

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
        # Load nonsense filters from S3
        bucket = os.environ.get('STORIES_BUCKET')
        if not bucket:
            return None

        response = s3_client.get_object(Bucket=bucket, Key='nonsense_filters.jsonl')
        filters_data = response['Body'].read().decode('utf-8')

        query_lower = query.lower()

        for line in filters_data.strip().split('\n'):
            filter_obj = json.loads(line)
            patterns = filter_obj.get('patterns', [])
            category = filter_obj.get('category', 'general')

            for pattern in patterns:
                if pattern.lower() in query_lower:
                    return category

        return None

    except Exception as e:
        print(f"Error checking nonsense filter: {str(e)}")
        return None


def get_nonsense_response(category: str) -> str:
    """Return canned response for nonsense queries"""
    responses = {
        'greeting': "Hi there! 👋 I'm Agy, Matt's AI portfolio assistant. I can help you learn about Matt's 20+ years of experience in digital transformation, agile delivery, and enterprise leadership. What would you like to know?",
        'identity': "I'm Agy, an AI assistant that helps you explore Matt Pugmire's professional portfolio. I can share specific examples from his 115+ transformation projects across Fortune 500 companies. What aspect of his experience interests you?",
        'general': "I'm here to help you learn about Matt's professional experience! Try asking about specific capabilities like 'agile transformation', 'team scaling', or 'payments modernization'."
    }
    return responses.get(category, responses['general'])


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
