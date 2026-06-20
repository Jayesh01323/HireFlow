"""
HireFlow AI - Main Application Entry Point

This is the primary Streamlit application for HireFlow AI, an AI-powered
career intelligence platform for freshers and entry-level software engineers.

Run with: streamlit run app.py
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="HireFlow AI",
    page_icon="🚀",
    layout="wide",
)

# Main page content
st.title("HireFlow AI")
st.subheader("AI-Powered Career Intelligence Platform")
st.markdown(
    """
    Welcome to HireFlow AI — your companion for resume parsing, job matching,
    skill gap analysis, career coaching, and interview preparation.

    Use the sidebar to navigate between features.
    """
)
