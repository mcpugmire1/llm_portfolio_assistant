import json

import streamlit as st


# Utility functions (replace with your actual loading and retrieval logic)
def load_star_stories(file_path):
    with open(file_path, encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f.readlines()]


def match_user_query(query, stories):
    # Replace this with your embedding + vector search logic
    return [story for story in stories if query.lower() in story['content'].lower()]


# -------------------
# Page Configuration
# -------------------
st.set_page_config(page_title="MattGPT – STAR Story Assistant", page_icon="🤖")

# -------------------
# Sidebar: Filters + Example Questions
# -------------------
with st.sidebar:
    stories = load_star_stories("echo_star_stories.jsonl")
    categories = sorted(
        set(story.get("category", "Uncategorized") for story in stories)
    )
    # selected_categories = st.multiselect("📂 Filter by Category", categories)
    selected_categories = st.multiselect(
        "📂 Filter by Category", categories, placeholder="Select categories"
    )

    st.markdown("---")

    st.markdown("### 💡 Example Questions")
    st.markdown(
        """
- What’s your experience with platform strategy?
- How did you lead a $500M payments transformation?
- Describe a GenAI project you led.
- How do you enable developer upskilling?
- What’s your leadership approach for tech teams?
    """
    )

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
# Expander – About Matt
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

Career highlights include launching platforms across 12+ countries, improving operational efficiency by 15%, and accelerating innovation cycles by 4x.
My expertise spans platform architecture, GenAI enablement, and scaling modern engineering practices in complex, regulated environments.

I’m currently exploring Director or VP-level opportunities where I can shape platform strategy, AI enablement, and enterprise modernization.
"""
    )

# -------------------
# Expander – How MattGPT Works
# -------------------
with st.expander("ℹ️ How MattGPT Works"):
    st.markdown(
        """
MattGPT uses **Retrieval-Augmented Generation (RAG)** — a method that retrieves STAR stories from my portfolio and uses them to answer your question.

It's the same principle behind enterprise-grade GenAI tools I've helped design.

You get responses grounded in real experience — not generic AI guesses.
"""
    )

# -------------------
# Example Prompt
# -------------------
st.markdown("### 💬 Try asking:")
st.markdown("**“Tell me about a time you led a global delivery.”**")

# -------------------
# Query Input
# -------------------
user_query = st.text_input(
    "Ask about Matt’s experience (e.g., 'cloud modernization', 'capability building', 'payments')"
)

# -------------------
# Load and Render STAR Stories
# -------------------
if user_query:
    stories = load_star_stories("echo_star_stories.jsonl")  # Adjust path as needed
    matching_stories = match_user_query(user_query, stories)

    if matching_stories:
        for story in matching_stories:
            with st.expander(f"{story['title']} ({story['client']})"):
                st.markdown(
                    f"""
**📁 Client:** {story['client']}
**🎓 Role:** {story['role']}
**🏷️ Category:** {story['category']} / {story['sub-category']}

---

**🎯 Situation**
{story['situation']}

**🧭 Task**
{story['task']}

**⚙️ Action**
{story['action']}

**🏆 Result**
{story['result']}
""",
                    unsafe_allow_html=True,
                )
    else:
        st.info(
            "No matching stories found. Try a broader keyword like 'cloud', 'GenAI', or 'payments'."
        )
