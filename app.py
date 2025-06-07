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
    from pinecone import Pinecone

    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

    pc = Pinecone(api_key=PINECONE_API_KEY)
    pinecone_index = pc.Index(PINECONE_INDEX_NAME)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    metadata = None  # Will be loaded per query from Pinecone

else:
    import faiss
    import numpy as np

    model = SentenceTransformer("all-MiniLM-L6-v2")
    index = faiss.read_index("faiss_index/index.faiss")
    with open("faiss_index/story_metadata.json", "r") as f:
        metadata = json.load(f)

# Streamlit UI setup
st.set_page_config(page_title="Echo – Matt's Career Assistant", page_icon="🧠")
st.title("🧠 Echo – Matt's LLM-Powered STAR Story Assistant")
st.markdown("Ask natural questions to explore real experiences from Matt's career.")

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
