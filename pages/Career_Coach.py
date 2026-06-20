"""
Career Coach Page

Streamlit page for AI-powered career guidance and advice.
Helps freshers plan their career path and make informed decisions.
"""

import streamlit as st

st.set_page_config(page_title="Career Coach", page_icon="💡", layout="wide")

st.title("💡 Career Coach")
st.markdown("Get personalized career advice powered by AI.")

# Placeholder UI
st.text_area("Ask your career question", placeholder="What skills should I learn for a backend role?")
st.button("Get Advice", disabled=True)
