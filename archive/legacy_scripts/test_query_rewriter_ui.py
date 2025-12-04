# test_query_rewriter_ui.py

import streamlit as st
from query_rewriter_llm import rewrite_query_with_llm

st.set_page_config(page_title="Query Rewriter Test", layout="centered")

st.title("🔍 LLM Query Rewriter Tester")
st.markdown("Enter a vague or high-level prompt below. The LLM will rewrite it into a precise semantic search query.")

user_input = st.text_input("Enter your prompt:", "")

if st.button("Rewrite Prompt") and user_input:
    with st.spinner("Rewriting..."):
        rewritten_query = rewrite_query_with_llm(user_input)
        st.success("✅ Rewritten Query")
        st.code(rewritten_query, language="markdown")