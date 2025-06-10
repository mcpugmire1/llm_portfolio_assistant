import streamlit as st
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate API key
if not OPENAI_API_KEY:
    st.error("Missing OpenAI API key. Please set it in your .env file.")
    st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Determine vector backend
VECTOR_BACKEND = os.getenv("VECTOR_BACKEND", "faiss").lower()

if VECTOR_BACKEND == "pinecone":
    
    
    #from pinecone import Pinecone
    import pinecone

    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT")  # you need to add this in .env or Streamlit secrets
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
    pinecone_index = pinecone.Index(PINECONE_INDEX_NAME)
   # pinecone_index = pinecone.Index(PINECONE_INDEX_NAME)
    #PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    #PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

    #pc = Pinecone(api_key=PINECONE_API_KEY)
    #pinecone_index = pc.Index(PINECONE_INDEX_NAME)

    # Disable CUDA explicitly by setting device
    model = SentenceTransformer("models/all-MiniLM-L6-v2")
    metadata = None  # Will be loaded per query from Pinecone

else:
    import faiss
    import numpy as np


    model = SentenceTransformer("models/all-MiniLM-L6-v2")

    
    index = faiss.read_index("faiss_index/index.faiss")
    with open("faiss_index/story_metadata.json", "r") as f:
        metadata = json.load(f)

# Streamlit UI setup
st.set_page_config(page_title="MattGPT – Matt's Career Assistant", page_icon="🤖")
st.title("🤖 MattGPT – Matt's LLM-Powered STAR Story Assistant")
st.markdown("""
Welcome to **MattGPT** – my interactive portfolio assistant.

Use this tool to explore my STAR stories, technical projects, and leadership experiences.  
Ask a question like **“Tell me about a time you led a global delivery”** or browse by category.

This app was built using OpenAI + Pinecone to showcase my experience in a conversational, AI-powered format.
""")
# Optional RAG explainer
with st.expander("ℹ️ How does MattGPT work?"):
    st.markdown("""
    **MattGPT uses Retrieval-Augmented Generation (RAG)** – a technique that retrieves relevant examples from my actual experience before answering your question.

    This means:
    - You get responses grounded in real work I’ve done.
    - The assistant can reference STAR stories aligned with your query.
    - It behaves like the enterprise-grade GenAI tools I’ve helped architect.

    Ask anything — from leadership in Agile transformations to global payments modernization.
    """)

query = st.text_input("Ask about Matt's experience (e.g., 'cloud modernization', 'capability building', 'payments')")
show_star = st.checkbox("Show full STAR details", value=True)
# Sidebar display
st.sidebar.title("⚙️ Settings")
st.sidebar.info(f"Using backend: {VECTOR_BACKEND.upper()}")

if query:
    with st.spinner("🔍 Retrieving best matches..."):
        query_embedding = model.encode([query])
        matched_stories = []

        if VECTOR_BACKEND == "pinecone":
            st.write("🔍 Querying Pinecone...")
            search_results = pinecone_index.query(
                vector=query_embedding.tolist(),
                top_k=4,
                include_metadata=True
            )
            st.write("✅ Pinecone returned results.")
            for match in search_results["matches"]:
                story = match["metadata"]
                title = story.get("Title", "Untitled")
                client_name = story.get("Client", "Unknown")
                role = story.get("Role", "Unknown")
                category = story.get("Category", "Uncategorized")
                use_cases = story.get("Use Case(s)", [])
                situation = story.get("Situation", [])
                task = story.get("Task", [])
                action = story.get("Action", [])
                st.sidebar.write("DEBUG: Action field", action)
                result = story.get("Result", [])


                story_block = f"""
                    <div style="margin-bottom: 2rem; line-height: 1.6;">
                    <p>📘 <strong>{title}</strong><br>
                    <strong>Client</strong>: {client_name} | <strong>Role</strong>: {role} | <strong>Category</strong>: {category}</p> 
                    <p><strong>Use Cases</strong>: {', '.join(use_cases) if isinstance(use_cases, list) else use_cases}</p>             
                    <p>🟦 <strong>Situation</strong>: {' '.join(situation) if isinstance(situation, list) else situation}</p>
                    <p>🟨 <strong>Task</strong>: {' '.join(task) if isinstance(task, list) else task}</p>
                    <p>🟧 <strong>Action</strong>: {' '.join(action) if isinstance(action, list) else action}</p>
                    <p>🟩 <strong>Result</strong>: {' '.join(result) if isinstance(result, list) else result}</p>
                    </div>
                    """            
                matched_stories.append(story_block.strip())
                st.sidebar.write("DEBUG: Full story metadata", story)
            if not matched_stories:
                st.warning("No relevant stories found. Please try a different query.")
                st.stop()
        else:
            scores, indices = index.search(np.array(query_embedding), 4)
            for idx in indices[0]:
                story = metadata[idx]
                title = story.get("Title", "Untitled")
                client_name = story.get("Client", "Unknown")
                role = story.get("Role", "Unknown")
                category = story.get("Category", "Uncategorized")
                use_cases = story.get("Use Case(s)", [])
                situation = story.get("Situation", [])
                task = story.get("Task", [])
                action = story.get("Action", [])
                st.sidebar.write("DEBUG: Action field", action)
                result = story.get("Result", [])
                
                story_block = f"""
                    <div style="margin-bottom: 2rem; line-height: 1.6;">
                        <p>📘 <strong>{title}</strong><br>
                        <strong>Client</strong>: {client_name} | <strong>Role</strong>: {role} | <strong>Category</strong>: {category}</p>
                        <p><strong>Use Cases</strong>: {', '.join(use_cases) if isinstance(use_cases, list) else use_cases}</p>
                        <p>🟦 <strong>Situation</strong>: {' '.join(situation) if isinstance(situation, list) else situation}</p>
                        <p>🟨 <strong>Task</strong>: {' '.join(task) if isinstance(task, list) else task}</p>
                        <p>🟧 <strong>Action</strong>: {' '.join(action) if isinstance(action, list) else action}</p>
                        <p>🟩 <strong>Result</strong>: {' '.join(result) if isinstance(result, list) else result}</p>
                    </div>
                """
              
                matched_stories.append(story_block.strip())
                if not matched_stories:
                    st.warning("No relevant stories found. Please try a different query.")
                    st.stop()
        st.sidebar.write("DEBUG: First matched story", matched_stories[0] if matched_stories else "None")
        full_prompt = f"""You are Matt Pugmire. Respond in first person using confident, natural language. These are your own STAR stories:

{chr(10).join(matched_stories)}

Now answer this question naturally and helpfully: {query}"""

        try:
            st.write("🧠 Sending prompt to OpenAI...")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are Matt Pugmire. Always respond in first person. Use confident, natural language, and draw from your real career experiences."
                    },
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.3
            )
            st.write("✅ OpenAI responded.")
            answer = response.choices[0].message.content
            st.markdown("---")
            st.subheader("🧠 Best Match:")
            st.markdown(answer)

            if show_star:
                st.markdown("---")
                st.subheader("📘 Full STAR Breakdowns:")
                for block in matched_stories:
                    st.markdown(block, unsafe_allow_html=True)
                    

        except Exception as e:
            st.error(f"OpenAI API error: {e}")
