"""
Learning Roadmap Page

Streamlit page for generating personalized learning roadmaps.
Creates structured learning paths with milestones and timelines.
"""

import streamlit as st

st.set_page_config(page_title="Learning Roadmap", page_icon="🗺️", layout="wide")

st.title("🗺️ Learning Roadmap")
st.markdown("Generate personalized learning roadmaps for your career goals.")

# Placeholder UI
st.selectbox("Select Resume", ["Resume 1", "Resume 2"])
st.text_input("Target Role", placeholder="e.g., Senior Software Engineer")
st.slider("Timeline (Weeks)", min_value=4, max_value=52, value=12)

st.button("Generate Roadmap", disabled=True)

st.divider()
st.subheader("Learning Roadmap")
st.info("Learning roadmap generation functionality coming soon.")
