"""
Interview Preparation Page

Streamlit page for interview practice with AI-generated questions
and feedback tailored to the candidate's profile and target role.
"""

import streamlit as st

st.set_page_config(page_title="Interview Prep", page_icon="🎤", layout="wide")

st.title("🎤 Interview Preparation")
st.markdown("Practice interview questions and receive AI feedback.")

# Placeholder UI
st.selectbox("Interview Type", ["Technical", "Behavioral", "System Design"])
st.button("Start Practice", disabled=True)
