"""
Job Discovery Page

Streamlit page for discovering job opportunities across multiple sources.
Search, filter, and save jobs from various job boards.
"""

import streamlit as st

st.set_page_config(page_title="Job Discovery", page_icon="🔍", layout="wide")

st.title("🔍 Job Discovery")
st.markdown("Discover job opportunities from multiple sources.")

# Placeholder UI
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.text_input("Search Query", placeholder="e.g., software engineer")
with col2:
    st.text_input("Location", placeholder="e.g., San Francisco")
with col3:
    st.selectbox("Experience Level", ["Any", "Entry", "Mid", "Senior"])

st.checkbox("Remote Only")
st.multiselect("Sources", ["LinkedIn", "Internshala", "Naukri", "Indeed", "Glassdoor"])

st.button("Search Jobs", disabled=True)

st.divider()
st.subheader("Search Results")
st.info("Job search functionality coming soon.")
