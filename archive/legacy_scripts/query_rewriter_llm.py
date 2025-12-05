from dotenv import load_dotenv
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()


@retry(wait=wait_random_exponential(min=1, max=4), stop=stop_after_attempt(3))
def rewrite_query_with_llm(user_prompt: str) -> str:
    """
    Rewrites vague or high-level prompts into precise semantic search queries
    suitable for STAR story retrieval.
    """
    base_prompt = (
        "You are a helpful assistant that rewrites vague user prompts into precise semantic search queries. "
        "The queries will be used to retrieve STAR-format interview stories from a semantic search system. "
        "Do not return a full answer, just rewrite the input prompt clearly and concisely as a search phrase."
    )

    messages = [
        {"role": "system", "content": base_prompt},
        {
            "role": "user",
            "content": f"Rewrite this prompt for semantic search: {user_prompt}",
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4", messages=messages, temperature=0.3, max_tokens=60
    )

    rewritten = response.choices[0].message.content.strip()
    if not rewritten or len(rewritten) < 3:
        raise ValueError("Invalid rewritten query returned from LLM.")
    return rewritten
