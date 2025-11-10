"""
Streamlit approximation of the React drawer pattern for MattGPT source links.

Shows how source links would expand DOWN (not over) with full story details.
"""

import streamlit as st

# Page config
st.set_page_config(page_title="Ask MattGPT - Drawer Approximation", layout="wide")

# Custom CSS to match your purple branding
st.markdown("""
<style>
    /* Main container styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Chat container */
    .chat-container {
        background: white;
        border-radius: 12px;
        padding: 24px;
        margin: 20px auto;
        max-width: 900px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Message styling */
    .message-intro {
        color: #764ba2;
        font-weight: 600;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Source link buttons */
    div[data-testid="stButton"] button {
        background: #edf2f7;
        border: 2px solid #cbd5e0;
        color: #2d3748;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 14px;
        transition: all 0.2s;
    }
    
    div[data-testid="stButton"] button:hover {
        background: #764ba2;
        color: white;
        border-color: #764ba2;
        transform: translateY(-2px);
    }
    
    /* Expander styling */
    div[data-testid="stExpander"] {
        background: #f7fafc;
        border-left: 4px solid #764ba2;
        border-radius: 8px;
        margin-top: 16px;
    }
    
    div[data-testid="stExpander"] summary {
        font-weight: 600;
        color: #2d3748;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "expanded_story" not in st.session_state:
    st.session_state.expanded_story = None

# Sample stories data
STORIES = {
    "jpmorgan": {
        "title": "JPMorgan Chase - Agile Transformation",
        "tags": ["Agile Transformation", "Stakeholder Management", "Executive Leadership"],
        "person": "Matthew Pugmire, Program Director",
        "place": "JPMorgan Chase, Global Technology",
        "purpose": "Transform delivery methodology from waterfall to agile while building stakeholder confidence through transparent metrics",
        "performance": "$45M cost savings through improved velocity",
        "process": [
            "Created executive dashboards showing real-time velocity, defect rates, and business value",
            "Established monthly 'show and tell' sessions with VPs to demonstrate working software",
            "Built feedback loops with steering committee for clear decision points",
            "Translated technical delivery into business outcomes"
        ],
        "narrative": "When I joined the Global Payments modernization program, the leadership team was skeptical of agile. Previous attempts had failed, and there was institutional memory of 'agile chaos.' Rather than argue methodology, I focused on transparency and evidence. I built executive dashboards that translated sprint velocity into business metrics executives cared about: time-to-market, cost savings, risk reduction. Within three months, the same VPs who had been skeptical were asking 'how do we do more of this?' The key was speaking their language and building trust incrementally."
    },
    "rbc": {
        "title": "RBC - Global Payments & Treasury Solutions",
        "tags": ["Technical Leadership", "Cloud Migration", "Stakeholder Alignment"],
        "person": "Matthew Pugmire, Technical Architect",
        "place": "RBC, Corporate Treasury",
        "purpose": "Migrate legacy payments infrastructure to cloud while maintaining compliance and building stakeholder confidence",
        "performance": "99.97% platform uptime achieved",
        "process": [
            "Monthly stakeholder reviews with demos of working software",
            "Compliance co-design sessions to address concerns proactively",
            "Executive briefings focused on risk mitigation and business value",
            "Technical office hours for engineering teams"
        ],
        "narrative": "The RBC payments migration had a complex stakeholder map: engineering teams concerned about technical risk, compliance worried about regulatory requirements, and business stakeholders focused on uptime and customer impact. I established a rhythm of monthly stakeholder reviews that were less 'PowerPoint' and more 'working software demos.' Compliance teams could see their requirements implemented in real-time. This visibility eliminated surprises and built trust across all groups."
    }
}

# Header
st.markdown("### 🐾 Ask MattGPT")
st.markdown("*Streamlit approximation of React drawer pattern*")
st.divider()

# Simulated conversation message
with st.container():
    st.markdown("""
    <div class="message-intro">🐾 Great question!</div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    I've tracked down several relevant projects from Matt's work. Successful stakeholder management 
    in large organizations comes down to three key principles: **transparent communication**, 
    **data-driven decision making**, and **continuous alignment**.
    
    In my role at **JPMorgan Chase**, I navigated complex stakeholder ecosystems including senior 
    executives, product owners, compliance teams, and global delivery teams. When I faced resistance 
    from leadership skeptical of agile methodologies, I didn't argue philosophy — I showed evidence.
    
    I created **executive dashboards** displaying real-time velocity metrics, escaped defects, 
    deployment frequency, and business value delivered. This transparency transformed the conversation 
    from "should we do agile?" to "how do we scale what's working?"
    """)
    
    st.markdown("---")
    st.markdown("**📚 RELATED PROJECTS**")
    
    # Source link buttons in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔗 JPMorgan Chase", key="btn_jpmorgan"):
            st.session_state.expanded_story = "jpmorgan"
            st.rerun()
    
    with col2:
        if st.button("🔗 RBC Payments", key="btn_rbc"):
            st.session_state.expanded_story = "rbc"
            st.rerun()
    
    with col3:
        if st.button("🔗 Program Governance", key="btn_governance"):
            st.session_state.expanded_story = None  # Not implemented
            st.info("Story expansion demo - click JPMorgan or RBC")

# Show expanded story if one is selected
if st.session_state.expanded_story:
    story = STORIES.get(st.session_state.expanded_story)
    
    if story:
        # THIS IS THE KEY PART - expander opens DOWN below the buttons
        with st.expander(f"📖 {story['title']}", expanded=True):
            # Story details in clean format
            st.markdown(f"### {story['title']}")
            
            # Tags
            tag_html = " ".join([f"<span style='background: #edf2f7; padding: 4px 10px; border-radius: 4px; font-size: 12px; margin-right: 8px;'>{tag}</span>" for tag in story['tags']])
            st.markdown(tag_html, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 5P Framework
            st.markdown("#### 5P Framework")
            st.markdown(f"**Person:** {story['person']}")
            st.markdown(f"**Place:** {story['place']}")
            st.markdown(f"**Purpose:** {story['purpose']}")
            
            st.markdown("---")
            
            # Performance metric
            st.markdown("#### Performance")
            st.markdown(f"**{story['performance']}**")
            
            st.markdown("---")
            
            # Process
            st.markdown("#### Process / Approach")
            for item in story['process']:
                st.markdown(f"• {item}")
            
            st.markdown("---")
            
            # Full narrative
            st.markdown("#### Full Narrative")
            st.markdown(story['narrative'])
            
            # Close button
            if st.button("✕ Close", key="close_story"):
                st.session_state.expanded_story = None
                st.rerun()

# Instructions at bottom
st.markdown("---")
st.info("""
**How this works in Streamlit:**
- Click a source link → Expander opens **DOWN** below the buttons
- Content pushes everything underneath down (not overlay like React drawer)
- Click ✕ Close or collapse expander to hide
- React version will slide **OVER** from right instead
""")
