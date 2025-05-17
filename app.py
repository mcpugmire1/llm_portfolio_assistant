import streamlit as st
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from dotenv import load_dotenv
import os
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

# Load embedding model and FAISS index
model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("faiss_index/index.faiss")

# Load story metadata
with open("faiss_index/story_metadata.json", "r") as f:
    metadata = json.load(f)

# Streamlit UI setup
st.set_page_config(page_title="Echo – Matt's Career Assistant", page_icon="🧠")
st.title("🧠 Echo – Matt's LLM-Powered STAR Story Assistant")
st.markdown("Ask natural questions to explore real experiences from Matt's career.")

query = st.text_input("Ask about Matt's experience (e.g., 'cloud modernization', 'capability building', 'RBC')")
show_star = st.checkbox("Show full STAR details", value=True)

if query:
    with st.spinner("🔍 Retrieving best matches..."):
        query_embedding = model.encode([query])
        scores, indices = index.search(np.array(query_embedding), 4)

        matched_stories = []
        for idx in indices[0]:
            story = metadata[idx]
            title = story.get("Title", "Untitled")
            client_name = story.get("Client", "Unknown")
            role = story.get("Role", "Unknown")
            category = story.get("Category", "Uncategorized")
            use_cases = story.get("Use Case(s)", [])
            impact = story.get("Result", [])
            situation = story.get("Situation", [])
            task = story.get("Task", [])
            action = story.get("Action", [])
            result = story.get("Result", [])

            story_block = f"""📘 **{title}**  
**Client**: {client_name} | **Role**: {role} | **Category**: {category}  

🟦 **Situation**: {' '.join(situation) if isinstance(situation, list) else situation}  
🟨 **Task**: {' '.join(task) if isinstance(task, list) else task}  
🟧 **Action**: {' '.join(action) if isinstance(action, list) else action}  
🟩 **Result**: {' '.join(result) if isinstance(result, list) else result}
"""
            matched_stories.append(story_block.strip())

        full_prompt = f"""You are Matt Pugmire. Respond in first person using confident, natural language. These are your own STAR stories:

{chr(10).join(matched_stories)}

Now answer this question naturally and helpfully: {query}"""

        try:
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
            answer = response.choices[0].message.content
            st.markdown("---")
            st.subheader("🧠 Best Match:")
            st.markdown(answer)

            if show_star:
                st.markdown("---")
                st.subheader("📘 Full STAR Breakdowns:")
                for block in matched_stories:
                    st.markdown(block)

        except Exception as e:
            st.error(f"OpenAI API error: {e}")
