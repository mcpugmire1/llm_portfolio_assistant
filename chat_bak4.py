from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Strong, directive system prompt to force confident, first-person voice
SYSTEM_PROMPT = (
    "You are Matt Pugmire. Always respond in first person, using 'I', 'my', and 'me'. "
    "These are your own STAR stories and career experiences — never refer to 'Matt' or 'the user'. "
    "Summarize relevant stories naturally and confidently, as if you're talking to a hiring manager or recruiter. "
    "Blend insights from multiple roles when applicable. Lead with clarity, humility, and proof of impact."
)

# Load full structured STAR stories
with open("star_stories_llm_full_structure.json") as f:
    stories_data = json.load(f)

# Build LangChain documents with full context
documents = []
for story in stories_data:
    title = story.get("Title", "Untitled")
    role = story.get("Role", "")
    category = story.get("Category", "")
    sub_category = story.get("Sub-Category", "")
    use_cases = ", ".join(story.get("Use Case(s)", []))
    competencies = ", ".join(story.get("Competencies", []))
    keywords = ", ".join(story.get("Keywords", []))
    tagline = f"Title: {title}\nRole: {role}\nCategory: {category} / {sub_category}\nUse Cases: {use_cases}\nCompetencies: {competencies}\nKeywords: {keywords}"
    content = f"{tagline}\n\n{story['content']}"
    documents.append(Document(page_content=content, metadata={"title": title}))

# Initialize embeddings and LLM
embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model_name="gpt-3.5-turbo",
    temperature=0.3,
)

# Prompt setup
prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", "{question}\n\nHere are a few relevant STAR stories from your portfolio:\n\n{stories}")
])
output_parser = StrOutputParser()

def generate_chat_response(query):
    # Build and search FAISS vectorstore
    db = FAISS.from_documents(documents, embedding_model)
    retriever = db.as_retriever(search_kwargs={"k": 30})
    top_docs = retriever.get_relevant_documents(query)

    # Format retrieved stories
    story_text = ""
    for doc in top_docs:
        story_text += f"{doc.page_content}\n\n"

    # Build chain
    chain = prompt_template | llm | output_parser
    response = chain.invoke({ "question": query, "stories": story_text })

    return response
