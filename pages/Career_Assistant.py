"""
Career Assistant Page

Streamlit page for AI-powered career guidance and chat interface.
Provides context-aware career advice using Gemini AI.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import streamlit as st

from src.agents.career_copilot_agent import CareerCopilotAgent
from src.utils import get_env, load_env

load_env()

st.set_page_config(page_title="Career Assistant", page_icon="🤖", layout="wide")

# Custom CSS for dark theme
st.markdown(
    """
    <style>
        .stApp {
            background-color: #0f172a;
        }
        .chat-container {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border: 1px solid #475569;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        .user-message {
            background: #3b82f6;
            color: white;
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 0.5rem;
            max-width: 80%;
            margin-left: auto;
        }
        .ai-message {
            background: #1e40af;
            color: white;
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 0.5rem;
            max-width: 80%;
        }
        .suggestion-chip {
            background: #475569;
            color: #e2e8f0;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            margin: 0.25rem;
            display: inline-block;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .suggestion-chip:hover {
            background: #3b82f6;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🤖 AI Career Assistant")
st.markdown("Your personal AI career assistant for personalized guidance.")

# Initialize career copilot agent
@st.cache_resource
def get_career_copilot():
    return CareerCopilotAgent()

career_copilot = get_career_copilot()

# Get conversation context
context = career_copilot.get_conversation_context()

# Sidebar with context info
with st.sidebar:
    st.header("📊 Your Profile")
    
    if context.resume:
        skills = context.resume.get("skills", [])
        st.metric("Skills", len(skills))
        st.metric("Projects", len(context.resume.get("projects", [])))
        st.metric("Experience", len(context.resume.get("experience", [])))
    else:
        st.info("No resume data available.")
    
    st.divider()
    
    if context.top_career_path:
        st.subheader("🎯 Top Career Path")
        st.write(f"**{context.top_career_path}**")
    
    st.divider()
    
    if context.saved_jobs:
        st.metric("Saved Jobs", len(context.saved_jobs))
    
    if context.applications:
        st.metric("Applications", len(context.applications))
    
    st.divider()
    
    st.subheader("💡 Suggested Questions")
    suggestions = career_copilot.get_suggested_questions(context)
    for suggestion in suggestions:
        st.markdown(
            f'<div class="suggestion-chip">{suggestion}</div>',
            unsafe_allow_html=True,
        )

# Main chat interface
st.divider()

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
if st.session_state.chat_history:
    st.subheader("💬 Conversation History")
    
    for i, (question, answer, timestamp) in enumerate(st.session_state.chat_history):
        with st.container():
            st.markdown(
                f'<div class="user-message">👤 You: {question}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="ai-message">🤖 Copilot: {answer}</div>',
                unsafe_allow_html=True,
            )
            st.caption(f"{timestamp}")
            st.divider()

# Chat input
st.subheader("Ask Your Career Question")

col1, col2 = st.columns([4, 1])

with col1:
    user_question = st.text_input(
        "Type your question here...",
        placeholder="e.g., What should I learn next?",
        key="chat_input",
    )

with col2:
    send_button = st.button("Send", type="primary", use_container_width=True)

# Handle question submission
if send_button and user_question:
    with st.spinner("Thinking..."):
        # Get answer from copilot
        answer = career_copilot.ask_question(user_question, context)
        
        # Add to chat history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.chat_history.append((user_question, answer, timestamp))
        
        # Rerun to display the new message
        st.rerun()

# Quick action buttons
st.divider()
st.subheader("⚡ Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📋 Resume Tips", use_container_width=True):
        question = "How can I improve my resume?"
        answer = career_copilot.ask_question(question, context)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.chat_history.append((question, answer, timestamp))
        st.rerun()

with col2:
    if st.button("🎯 Career Advice", use_container_width=True):
        question = "Which career path suits me best?"
        answer = career_copilot.ask_question(question, context)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.chat_history.append((question, answer, timestamp))
        st.rerun()

with col3:
    if st.button("📚 Learning Plan", use_container_width=True):
        question = "What should I learn in the next 30 days?"
        answer = career_copilot.ask_question(question, context)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.chat_history.append((question, answer, timestamp))
        st.rerun()

with col4:
    if st.button("🚀 Project Ideas", use_container_width=True):
        question = "What project should I build next?"
        answer = career_copilot.ask_question(question, context)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.chat_history.append((question, answer, timestamp))
        st.rerun()

# Clear chat history
st.divider()
if st.button("🗑️ Clear Conversation History"):
    st.session_state.chat_history = []
    st.rerun()

# Footer
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.8rem;">
        <p>Powered by HireFlow AI • AI Career Assistant • Gemini Integration</p>
    </div>
    """,
    unsafe_allow_html=True,
)
