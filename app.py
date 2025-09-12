import subprocess

import streamlit as st
import json
from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI

try:
    from query_rewriter_llm import rewrite_query_with_llm
except Exception as e:
    print(f"[WARN] query_rewriter_llm import failed: {e}")

    def rewrite_query_with_llm(q: str) -> str:
        return q  # fallback: pass-through if import hiccups


from vector_search import embed_query, search, rerank_by_metadata

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

    # from pinecone import Pinecone
    from pinecone import Pinecone  # 0.8.x+

    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

    pc = Pinecone(api_key=PINECONE_API_KEY)
    pinecone_index = pc.Index(PINECONE_INDEX_NAME)

    # Disable CUDA explicitly by setting device
    metadata = None  # Will be loaded per query from Pinecone

else:
    import faiss
    import numpy as np

    ensure_faiss_index()  # ← NEW LINE

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
    return [story for story in stories if query.lower() in story["content"].lower()]


def fmt(value):
    return ", ".join(value) if isinstance(value, list) else value


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
st.set_page_config(page_title="MattGPT – Career Story Assistant", page_icon="🤖")

if "query" not in st.session_state:
    st.session_state.query = ""

# -------------------
# Hero Title & Summary
# -------------------
st.markdown("# 🤖 MattGPT – Matt's LLM-Powered Career Story Assistant")

st.markdown(
    """
Welcome to **MattGPT** – my interactive portfolio assistant.

Use this tool to explore my career stories, technical projects, and leadership experiences.  
Ask a question like “Tell me about a time you led a global delivery” or browse by category.

This app was built using **OpenAI + Pinecone** to showcase my experience in a conversational, AI-powered format.
""",
    unsafe_allow_html=True,
)

# -------------------
# Expanders for About + How it Works
# -------------------
with st.expander("👋 About Matt"):
    st.markdown(
        """
Digital transformation isn’t just about shipping code faster — it’s about building the right thing, the right way, with the right people. I help tech leaders modernize legacy platforms and launch innovative, 
cloud-native products that scale — all while nurturing cross-functional teams grounded in empathy, authenticity, and purpose.

As a technology leader, I focus on aligning digital strategy with business growth — whether that means accelerating time-to-market, enabling responsible experimentation with GenAI, or scaling modern engineering practices across global teams. I bridge strategy and execution to build secure, scalable platforms designed for change.

With 20+ years at the intersection of platform strategy, product innovation, and cloud modernization, I lead with a builder’s mindset and a coach’s heart. I’ve helped Fortune 500 organizations:

🔹 Architect cloud platforms that fuel innovation and global reach  
🔹 Shape technology strategy around customer needs and business goals  
🔹 Advance agility through Lean delivery, DevOps at scale, and automation  
🔹 Drive product transformation while mentoring high-performing teams  

Career highlights include launching platforms across 12+ countries, improving operational efficiency by 15%, and accelerating innovation cycles by 4x. My expertise spans platform architecture, GenAI enablement, and modern engineering practices in complex, regulated environments.

My approach blends platform architecture, product thinking, and a deep focus on customer experience — all grounded in empathy, lean practices, and iterative delivery.

If you’re navigating legacy constraints, siloed teams, or the pressure to modernize, let’s talk. I’m exploring Director or VP-level roles where I can shape platform strategy, enterprise modernization, and AI-enabled delivery.
                
**Matt Pugmire**  
Technology & Transformation Leader | Platform Strategy | AI-Enabled Product Innovation | Driving Cloud-Native Transformation

---

**Contact**  
📧 [mcpugmire@gmail.com](mailto:mcpugmire@gmail.com)  
🔗 [linkedin.com/in/matt-pugmire](https://www.linkedin.com/in/matt-pugmire)    
""",
        unsafe_allow_html=True,
    )

with st.expander("🤖 How does MattGPT work?"):
    st.markdown(
        """
**MattGPT uses Retrieval-Augmented Generation (RAG) with semantic search** — meaning it understands the intent behind your question and retrieves real examples from my experience to answer it.

This means:  
✅ Real experiences from my work inform each response  
📘 Relevant career stories are retrieved based on intent  
🏗️ Mirrors the enterprise-grade GenAI tools I’ve helped architect

Ask anything — from leading Agile transformations to modernizing global payments platforms.

"""
    )

# 📘 Sidebar filter pointer banner (restore this)
# st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    """
<div style="background-color: #1e1e1e; padding: 0.75rem 1rem; border-left: 4px solid #2e8bff; border-radius: 6px; margin: 0.5rem 0 0.75rem;">
🔍 <strong>Pro Tip for Mobile:</strong> Tap the sidebar ➤ icon on the left to filter career stories by <strong>domain</strong> or <strong>skill area</strong>.
</div>
""",
    unsafe_allow_html=True,
)

# st.markdown("<br>", unsafe_allow_html=True)

# --- Add custom CSS for sample question buttons just before the block that begins with "### 🤔 Curious where to start?"
# --- Custom CSS for styling sample question buttons (main and sidebar)
st.markdown(
    """
<style>
/* Reduce excessive spacing under expanders (About Matt, How it Works) */
.element-container:has(> details) {
    margin-bottom: 0.5rem !important;
}

/* Style for sample question buttons in main area */
.sample-question-btn, button[data-testid^="sample_question_"] {
    display: block;
    background-color: #2e8bff !important;
    color: white !important;
    padding: 0.75rem 1rem !important;
    margin-bottom: 0.5rem !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    cursor: pointer;
    border: none;
    text-align: left !important;
    transition: background-color 0.2s ease;
    white-space: normal !important;
    word-break: break-word !important;
    max-width: 100% !important;        
}
.sample-question-btn:hover, button[data-testid^="sample_question_"]:hover {
    background-color: #1e6fd6 !important;
    padding-top: 1rem !important;
}

/* Sidebar sample button styling */
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

/* Highlight selected question */
.selected-sample-question {
    background-color: #e0f0ff !important;
    font-weight: 600 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<h2 style='margin-top: -0.5rem; margin-bottom: 0.25rem;'>🤔 Curious where to start?</h2>
""",
    unsafe_allow_html=True,
)
st.markdown("Here are a few sample questions you can click on:")

sample_questions = [
    "Tell me about leading a global payments transformation.",
    "How did you apply GenAI in a healthcare project?",
    "What’s your experience with cloud-native architecture?",
    "How do you help teams adopt modern engineering practices?",
    "Describe how you scale agile and DevOps in enterprise environments.",
]

# 1. Initialize it if missing
if "selected_sample_index" not in st.session_state:
    st.session_state.selected_sample_index = None

icon_map = ["🧭", "🏥", "⚙️", "🔧", "🚀"]
# Use Streamlit buttons with improved sidebar style
for i, question in enumerate(sample_questions):
    label = f"{icon_map[i]} {question}"
    is_selected = st.session_state.selected_sample_index == i
    if st.button(label, key=f"sample_question_{i}"):
        st.session_state.query = question
        st.session_state.selected_sample_index = i
        st.rerun()  # <-- ensure the next run picks up the new query

# Load STAR stories dataset early so it's available for all logic
stories = load_star_stories("echo_star_stories.jsonl")

# Extract available sub-categories for dropdown
available_domains = sorted(
    set(story.get("Sub-category", "") for story in stories if story.get("Sub-category"))
)

# -------------------
# Sidebar: Filters + Clickable Sample Questions
# -------------------
# Sidebar styling to enhance sample question button layout

# 🔽 Domain Filter (from story metadata)
available_domains = sorted(
    set(story.get("Sub-category", "") for story in stories if story.get("Sub-category"))
)
selected_domain = st.sidebar.selectbox(
    "🗂️ Filter by Domain", options=["(All)"] + available_domains
)


# Extract unique tags from comma-separated public_tags field
all_tags = sorted(
    {
        tag.strip()
        for story in stories
        for tag in story.get("public_tags", "").split(",")
        if tag.strip()
    }
)
selected_tags = st.sidebar.multiselect("🎯 Filter by Skill Area", all_tags)

# 1. Initialize it if missing
if "selected_sample_index" not in st.session_state:
    st.session_state.selected_sample_index = None

# -------------------
# Input + Prompt Guidance
# -------------------
st.markdown("### 💬 Try asking:")
st.markdown("**“Tell me about a time you led a global delivery.”**")

# Then render the input field (no conflict)
st.markdown(
    """
<div style="background-color: #262730; border: 1px solid #4a4a4a; padding: 1rem; border-radius: 8px; margin-top: 1rem; margin-bottom: 1.5rem;">
    📝 <strong>Or ask your own question</strong><br>
    <span style='font-size: 0.9rem; color: #ccc;'>Describe a topic or experience you'd like to explore (e.g., 'Tell me about leading a global delivery')</span>
    """,
    unsafe_allow_html=True,
)
user_query = st.text_input(
    "Ask about Matt’s experience (e.g., 'cloud modernization', 'capability building', 'payments')",
    key="query",
)
# -------------------
# Query Handling + Story Display
# -------------------
st.markdown(
    """
</div>
""",
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

# query = st.text_input("Ask about Matt's experience (e.g., 'cloud modernization', 'capability building', 'payments')")
show_star = st.checkbox("Include detailed career story breakdowns", value=True)

if user_query:
    with st.spinner("🔍 Retrieving best matches..."):
        rewritten_query = rewrite_query_with_llm(user_query)
        st.write("🧠 Original query:", user_query)
        st.write("🔁 Rewritten query:", rewritten_query)

        query_embedding = embed_query(rewritten_query)
        search_results = search(query_embedding, top_k=5)

        # Re-rank or filter using domain metadata
        print("[DEBUG] Filtered search results after domain filter:")
        for s in search_results:
            print(s.get("Title"), "—", s.get("Sub-category"))
            print(f"[DEBUG] Selected domain: {selected_domain}")
            print(f"[DEBUG] Selected tags: {selected_tags}")

        print(f"[DEBUG] Selected domain: {selected_domain}")
        print(f"[DEBUG] Selected tags: {selected_tags}")
        search_results = rerank_by_metadata(
            search_results,
            domain_filter=selected_domain,
            competency_filter=selected_tags,
        )

        matched_stories = []

        st.write(f"🔎 {len(search_results)} match(es) found")
        st.write("📎 Top match titles:")
        for i, story in enumerate(search_results):
            st.write(f"{i+1}. {story.get('Title')} — Client: {story.get('Client')}")
        for story in search_results:
            # your display logic
            story_block = render_story_block(story)
            matched_stories.append(story_block.strip())

        if not matched_stories:
            st.warning("No relevant stories found. Please try a different query.")
            st.stop()

        # Construct prompt from matched stories and user query
        full_prompt = f"""Relevant STAR stories:

        {chr(10).join(matched_stories)}
        Question: {user_query}"""

        try:
            with st.spinner("🧠 Sending prompt to OpenAI..."):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": f"""You are Matt Pugmire, a seasoned technology leader. Always respond in first person using confident, conversational language drawn from your real STAR experiences.
        Answer the user's question clearly and concisely by focusing on:
        - The problem or opportunity
        - The actions you took (product, people, or process)
        - The value created or business impact

        Be outcome-oriented — as if preparing for a leadership interview.""",
                        },
                        {"role": "user", "content": full_prompt},
                    ],
                    temperature=0.3,
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
