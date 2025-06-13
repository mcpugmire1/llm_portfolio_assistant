import subprocess

import streamlit as st
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
from openai import OpenAI

FAISS_INDEX_PATH = Path("faiss_index/index.faiss")

def ensure_faiss_index():
    """
    Guarantee that faiss_index/index.faiss and story_metadata.json exist.
    If they don't, rebuild them by calling scripts/build_custom_embeddings.py.
    """
    if FAISS_INDEX_PATH.exists():
        return  # Nothing to do

    st.warning("🔨 FAISS index missing – building once. This may take ≈45 s.")
    try:
        subprocess.check_call(
            ["python", "scripts/build_custom_embeddings.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError:
        st.error("Failed to build FAISS index. Check the server log.")
        st.stop()

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
print(f"[INFO] Using vector backend: {VECTOR_BACKEND.upper()}")

if VECTOR_BACKEND == "pinecone":
    
    #from pinecone import Pinecone
    from pinecone import Pinecone          # 0.8.x+

    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

    pc = Pinecone(api_key=PINECONE_API_KEY)
    pinecone_index = pc.Index(PINECONE_INDEX_NAME)
   
    # Disable CUDA explicitly by setting device
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    metadata = None  # Will be loaded per query from Pinecone

else:
    import faiss
    import numpy as np


    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    ensure_faiss_index()                      # ← NEW LINE

    
    index = faiss.read_index("faiss_index/index.faiss")
    with open("faiss_index/story_metadata.json", "r") as f:
        metadata = json.load(f)

# -------------------
# Utility Functions
# -------------------
def load_star_stories(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f.readlines()]

def match_user_query(query, stories):
    return [story for story in stories if query.lower() in story['content'].lower()]

def fmt(value):
    return ', '.join(value) if isinstance(value, list) else value

def render_story_block(story):
    title = story.get("Title", "Untitled")
    client = story.get("Client", "Unknown")
    role = story.get("Role", "Unknown")
    category = story.get("Category", "Uncategorized")
    use_cases = story.get("Use Case(s)", [])
    situation = story.get("Situation", [])
    task = story.get("Task", [])
    action = story.get("Action", [])
    result = story.get("Result", [])

    return f"""
        <div style="margin-bottom: 2rem; line-height: 1.6;">
            <p>📘 <strong>{title}</strong><br>
            <strong>Client</strong>: {client} | <strong>Role</strong>: {role} | <strong>Category</strong>: {category}</p>
            <p><strong>Use Cases</strong>: {fmt(use_cases)}</p>
            <p>🟦 <strong>Situation</strong>: {fmt(situation)}</p>
            <p>🟨 <strong>Task</strong>: {fmt(task)}</p>
            <p>🟧 <strong>Action</strong>: {fmt(action)}</p>
            <p>🟩 <strong>Result</strong>: {fmt(result)}</p>
        </div>
    """.strip()

# Streamlit UI setup

# -------------------
# Page Configuration
# -------------------
st.set_page_config(
    page_title="MattGPT – STAR Story Assistant",
    page_icon="🤖"
)

if "query" not in st.session_state:
    st.session_state.query = ""

# -------------------
# Hero Title & Summary
# -------------------
st.markdown("# 🤖 MattGPT – Matt's LLM-Powered STAR Story Assistant")

st.markdown("""
Welcome to **MattGPT** – my interactive portfolio assistant.

Use this tool to explore my STAR stories, technical projects, and leadership experiences.  
Ask a question like “Tell me about a time you led a global delivery” or browse by category.

This app was built using **OpenAI + Pinecone** to showcase my experience in a conversational, AI-powered format.
""", unsafe_allow_html=True)

# -------------------
# Expanders for About + How it Works
# -------------------
with st.expander("👋 About Matt"):
    st.markdown("""
Technology isn’t just a tool—it’s a force for unlocking entirely new possibilities.  
I believe in harnessing cloud-native platforms, applied AI, and product-centric delivery to drive transformation that creates meaningful, measurable outcomes for organizations navigating disruption and scale.

As a technology leader, I focus on aligning digital strategy with business growth—whether that means accelerating time-to-market, enabling responsible GenAI experimentation, or scaling modern engineering practices across global teams.  
I bridge execution and strategy to build secure, scalable platforms designed for change.

I help organizations move faster and smarter by:  
🔹 Architecting cloud platforms that fuel innovation and global reach  
🔹 Shaping technology strategy to align with customer needs and business priorities  
🔹 Advancing agility through Lean delivery, scaled DevOps, and intelligent automation  
🔹 Driving product transformations while mentoring high-performing, cross-functional teams

Career highlights include launching platforms across 12+ countries, improving operational efficiency by 15%, and accelerating innovation cycles by 4x.  My expertise spans platform architecture, GenAI enablement, and scaling modern engineering practices in complex, regulated environments.

I’m currently exploring Director or VP-level opportunities where I can shape platform strategy, AI enablement, and enterprise modernization.
                
**Matt Pugmire**  
Technology & Transformation Leader | Platform Strategy | AI-Enabled Product Innovation | Driving Cloud-Native Transformation

---

**Contact**  
📧 [mcpugmire@gmail.com](mailto:mcpugmire@gmail.com)  
🔗 [linkedin.com/in/matt-pugmire](https://www.linkedin.com/in/matt-pugmire)    
""", unsafe_allow_html=True)
    
with st.expander("🤖 How does MattGPT work?"):
    st.markdown("""
**MattGPT uses _Retrieval-Augmented Generation (RAG)_** – a technique that retrieves relevant examples from my actual experience before answering your question.
This means:
                
• You get responses grounded in real work I’ve done.  
• The assistant can reference STAR stories aligned with your query.  
• It behaves like the enterprise-grade GenAI tools I’ve helped architect.

Ask anything — from leadership in Agile transformations to global payments modernization.

""")

# Load STAR stories dataset early so it's available for all logic
stories = load_star_stories("echo_star_stories.jsonl")

# -------------------
# Sidebar: Filters + Clickable Sample Questions
# -------------------
# Sidebar styling to enhance sample question button layout
st.markdown("""
    <style>
    section[data-testid="stSidebar"] button {
        width: 100% !important;
        white-space: normal !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 6px !important;
        padding: 0.5rem 0.75rem !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.25rem !important;
    }

    /* Highlight selected button */
    .selected-sample-question {
        background-color: #e0f0ff !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

#st.sidebar.markdown("### 💬 Sample Questions")

#st.sidebar.markdown("### 🤔 Curious where to start?")
#st.sidebar.markdown("Here are a few sample questions to try:")
st.sidebar.markdown("""
### 💬 Sample Questions  
<span style='font-weight: 600; font-size: 0.9rem;'>🤔 Curious where to start?</span><br>
<span style='font-size: 0.85rem;'>Here are a few sample questions to try:</span>
""", unsafe_allow_html=True)


sample_questions = [
    "What’s your experience with platform strategy?",
    "How did you lead a $500M payments transformation?",
    "Describe a GenAI project you led.",
    "How do you enable developer upskilling?",
    "What’s your leadership approach for tech teams?"
]

# 1. Initialize it if missing
if "selected_sample_index" not in st.session_state:
    st.session_state.selected_sample_index = None

# 2. Render sidebar buttons with tracking
for i, question in enumerate(sample_questions):
    button_label = question
    is_selected = st.session_state.selected_sample_index == i

    # Create a unique container so we can wrap with a div
    with st.sidebar.container():
        html_id = f"sample-question-{i}"
        st.markdown(
            f"""<div id="{html_id}" class="{'selected-sample-question' if is_selected else ''}">""",
            unsafe_allow_html=True,
        )
        if st.button(button_label, key=f"sample_question_{i}"):
            st.session_state.query = question
            st.session_state.selected_sample_index = i
        st.markdown("</div>", unsafe_allow_html=True)

# -------------------
# Input + Prompt Guidance
# -------------------
st.markdown("### 💬 Try asking:")
st.markdown("**“Tell me about a time you led a global delivery.”**")

# Then render the input field (no conflict)
user_query = st.text_input(
    "Ask about Matt’s experience (e.g., 'cloud modernization', 'capability building', 'payments')",
    key="query"
)
# -------------------
# Query Handling + Story Display
# -------------------

#query = st.text_input("Ask about Matt's experience (e.g., 'cloud modernization', 'capability building', 'payments')")
show_star = st.checkbox("Show full STAR details", value=True)


if user_query:
    with st.spinner("🔍 Retrieving best matches..."):
        query_embedding = model.encode([user_query])
        matched_stories = []

        if VECTOR_BACKEND == "pinecone":
            search_results = pinecone_index.query(
                vector=query_embedding.tolist(),
                top_k=4,
                include_metadata=True
            )
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
                result = story.get("Result", [])
                          
                story_block = render_story_block(story)          
                matched_stories.append(story_block.strip())
            if not matched_stories:
                st.warning("No relevant stories found. Please try a different query.")
                st.stop()
        else:
            scores, indices = index.search(np.array(query_embedding), 4)
            for idx in indices[0]:
                story = metadata[idx]
                title = story.get("Title", "Untitled")
                client = story.get("Client", "Unknown")
                role = story.get("Role", "Unknown")
                category = story.get("Category", "Uncategorized")
                use_cases = story.get("Use Case(s)", [])
                situation = story.get("Situation", [])
                task = story.get("Task", [])
                action = story.get("Action", [])
                result = story.get("Result", [])
                
                story_block = render_story_block(story)
                matched_stories.append(story_block.strip())
            if not matched_stories:
                st.warning("No relevant stories found. Please try a different query.")
                st.stop()

        full_prompt = f"""You are Matt Pugmire. Respond in first person using confident, natural language. These are your own STAR stories:


{chr(10).join(matched_stories)}

Now answer this question naturally and helpfully: {user_query}"""

        try:
            with st.spinner("🧠 Sending prompt to OpenAI..."):
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
                    st.markdown(block, unsafe_allow_html=True)
                    

        except Exception as e:
            st.error(f"OpenAI API error: {e}")
