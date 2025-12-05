import json

import streamlit as st


# -------------------
# Utility Functions
# -------------------
def load_star_stories(file_path):
    with open(file_path, encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f.readlines()]


def match_user_query(query, stories):
    return [story for story in stories if query.lower() in story['content'].lower()]


# -------------------
# Page Configuration
# -------------------
st.set_page_config(page_title="MattGPT – STAR Story Assistant", page_icon="🤖")

# -------------------
# Sidebar: Filters + Clickable Examples
# -------------------

# st.sidebar.markdown("### 🎯 Filter by Theme")

# Initialize previous_theme if it doesn't exist
# if "previous_theme" not in st.session_state:
#    st.session_state.previous_theme = "(All)"

# Sidebar Theme Selector
# selected_theme = st.sidebar.selectbox("Select a theme", ["(All)"] + list(THEME_TAG_MAP.keys()))

# Reset query if theme has changed
# if selected_theme != st.session_state.previous_theme:
#    st.session_state.query = ""
#    st.session_state.previous_theme = selected_theme


st.sidebar.markdown("### 💬 Example Questions")
examples = [
    "Tell me about a GenAI initiative you led.",
    "How did you modernize a global banking platform?",
    "What’s your leadership style?",
    "How have you enabled developer upskilling?",
]

for example in examples:
    if st.sidebar.button(example):
        st.session_state.query = example

# Ensure query is initialized in session_state
if "query" not in st.session_state:
    st.session_state.query = ""


# -------------------
# Hero Title & Summary
# -------------------
st.markdown("# 🤖 MattGPT – Matt's LLM-Powered STAR Story Assistant")

st.markdown(
    """
Welcome to **MattGPT** – my interactive portfolio assistant.

Use this tool to explore my STAR stories, technical projects, and leadership experiences.
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
""",
        unsafe_allow_html=True,
    )


with st.expander("🤖 How does MattGPT work?"):
    st.markdown(
        """
**MattGPT uses _Retrieval-Augmented Generation (RAG)_** – a technique that retrieves relevant examples from my actual experience before answering your question.
This means:

• You get responses grounded in real work I’ve done.
• The assistant can reference STAR stories aligned with your query.
• It behaves like the enterprise-grade GenAI tools I’ve helped architect.

Ask anything — from leadership in Agile transformations to global payments modernization.

"""
    )

# Load STAR stories dataset early so it's available for all logic
stories = load_star_stories("echo_star_stories.jsonl")

# -------------------
# Input + Prompt Guidance
# -------------------
st.markdown("### 💬 Try asking:")
st.markdown("**“Tell me about a time you led a global delivery.”**")

# Use the session_state value for input, so it reflects button clicks too
user_query = st.text_input(
    "Ask about Matt’s experience (e.g., 'cloud modernization', 'capability building', 'payments')",
    value=st.session_state.query,
    key="query",
)


# -------------------
# Query Handling + Story Display
# -------------------
# if user_query or selected_theme != "(All)":
if user_query or "(All)" != "(All)":
    matching_stories = match_user_query(user_query, stories) if user_query else stories

    # Replace category filtering with theme filtering
    # def story_matches_theme(story, selected_theme):
    # if selected_theme == "(All)":
    # return True
    # story_tags = [tag.strip() for tag in str(story.get("public_tags", "")).split(",")]
    # allowed_tags = THEME_TAG_MAP.get(selected_theme, [])
    # return any(tag in allowed_tags for tag in story_tags)

    # filtered_stories = [
    #     s for s in matching_stories
    #     if story_matches_theme(s, selected_theme)
    # ]

    filtered_stories = matching_stories

    for story in filtered_stories:
        with st.expander(f"{story['Title']} ({story['Client']})"):
            st.markdown(
                f"""
**📁 Client:** {story['Client']}
**🎓 Role:** {story['Role']}
**🏷️ Category:** {story['Category']} / {story['Sub-category']}

---

---

**🎯 Situation**
{story['Situation'][0] if isinstance(story['Situation'], list) else story['Situation']}

**🧭 Task**
{story['Task'][0] if isinstance(story['Task'], list) else story['Task']}

**⚙️ Action**
{story['Action'][0] if isinstance(story['Action'], list) else story['Action']}

**🏆 Result**
{story['Result'][0] if isinstance(story['Result'], list) else story['Result']}
""",
                unsafe_allow_html=True,
            )

    if not filtered_stories:
        st.warning(
            "⚠️ No stories matched this theme or query. Try another theme or enter a keyword."
        )
