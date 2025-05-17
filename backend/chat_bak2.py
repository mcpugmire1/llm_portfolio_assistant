from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Reinforced system prompt for natural first-person narrative
SYSTEM_PROMPT = (
    "You are Matt Pugmire. Speak in first person, using 'I', 'my', and 'me'. "
    "When asked about your experience, synthesize across multiple projects and describe what you did clearly. "
    "Always sound like a confident, thoughtful leader sharing your background with a potential employer. "
    "Avoid robotic language. Be human, be helpful, and refer to specific examples where appropriate."
)

# Initialize models
embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model_name="gpt-3.5-turbo",
    temperature=0.2,
)

# Prompt template combining query + multi-story context
prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", "{question}\\n\\nHere are a few examples from your STAR story portfolio:\\n\\n{stories}")
])

output_parser = StrOutputParser()

def generate_chat_response(query, stories):
    # Convert stories to documents
    documents = [
        Document(
            page_content=story["content"],
            metadata={
                "title": story.get("title", "Untitled"),
                "keywords": story.get("keywords", [])
            }
        ) for story in stories
    ]

    # Build FAISS index
    db = FAISS.from_documents(documents, embedding_model)
    retriever = db.as_retriever(search_kwargs={"k": 10})
    top_semantic_docs = retriever.get_relevant_documents(query)

    # Keyword match fallback (simple keyword scan)
    keywords = query.lower().split()
    keyword_matches = [doc for doc in documents if any(k in doc.page_content.lower() for k in keywords)]

    # Merge and dedupe results
    all_docs = {id(doc): doc for doc in top_semantic_docs + keyword_matches}
    selected_docs = list(all_docs.values())[:12]

    # Format for LLM
    story_text = ""
    for doc in selected_docs:
        title = doc.metadata.get("title", "Untitled")
        story_text += f"### {title}\\n{doc.page_content}\\n\\n"

    # Chain execution
    chain = prompt_template | llm | output_parser
    response = chain.invoke({ "question": query, "stories": story_text })

    return response