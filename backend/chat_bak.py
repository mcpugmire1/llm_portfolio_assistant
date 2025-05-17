from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# System prompt to shape assistant's personality
SYSTEM_PROMPT = (
    "You are Matt Pugmire. When answering, always speak in first person (using 'I', 'my', 'me'). "
    "Never refer to 'the context', 'the user', or 'provided examples'. These are your own experiences. "
    "If multiple STAR stories are relevant, summarize what you personally did across them. "
    "Always aim for clarity, humility, and confidence — like you're explaining your career to a recruiter who matters."
)

# Initialize models
embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model_name="gpt-3.5-turbo",
    temperature=0.2,
    max_tokens=800,
    streaming=False,
    system_message=SYSTEM_PROMPT  # 👈 Intended to inject identity
)

def generate_chat_response(query, stories):
    # Convert stories into LangChain documents
    documents = [
        Document(
            page_content=story["content"],
            metadata={"title": story.get("title", "Untitled")}
        )
        for story in stories
    ]

    # Build FAISS index
    db = FAISS.from_documents(documents, embedding_model)
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    # Retrieval + QA chain
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    result = qa.run(query)
    return result