"""
Skill Gap Page

Streamlit page for analyzing skill gaps between resume and job requirements.
Provides detailed gap analysis with learning recommendations using skill_gap_engine.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from src.database import get_all_resumes, init_db
from src.services.skill_gap_engine import SkillGapEngine
from src.services.skill_categorizer import categorize_skill, SkillCategory
from src.utils import get_env, load_env

load_env()
init_db()

DB_PATH = Path(get_env("DATABASE_PATH", "data/hireflow.db"))

st.set_page_config(page_title="Skill Gap Analysis", page_icon="📊", layout="wide")

# Custom CSS for dark theme
st.markdown(
    """
    <style>
        .stApp {
            background-color: #0f172a;
        }
        .gap-card {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border: 1px solid #475569;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        .critical-gap {
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }
        .medium-gap {
            background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%);
            color: #333;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }
        .optional-gap {
            background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }
        .skill-chip {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            margin: 4px;
            font-size: 13px;
            font-weight: 500;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Skill Gap Analysis")
st.markdown("Analyze skill gaps between your resume and job requirements with AI-powered learning recommendations.")

st.divider()

# Get all resumes from database
resumes = get_all_resumes()

# Handle empty database
if not resumes:
    st.info(
        "No resumes found in the database. Please upload and parse resumes on the **Resume Parser** page first.",
        icon="ℹ️",
    )
    st.stop()

# Resume selection
st.subheader("Select Resume")
resume_options = {
    f"{r['parsed'].get('name', r['filename'])} — {r['filename']} (#{r['id']})": r
    for r in resumes
}
selected_resume_label = st.selectbox(
    "Choose a resume to analyze",
    options=list(resume_options.keys()),
    help="Select a parsed resume from the database",
    key="skill_gap_resume",
)
selected_resume = resume_options[selected_resume_label]

# Job description input
st.subheader("Job Description")
job_description = st.text_area(
    "Paste the job description here",
    height=200,
    placeholder="Paste the full job description including requirements, qualifications, and skills...",
    help="The more detailed the job description, the better the skill gap analysis will work",
    key="skill_gap_jd_input",
)

# Analyze button
if st.button("Analyze Skill Gap", type="primary", disabled=not job_description, key="analyze_gap_btn"):
    # Initialize skill gap engine
    @st.cache_resource
    def get_skill_gap_engine():
        return SkillGapEngine()
    
    skill_gap_engine = get_skill_gap_engine()
    
    with st.spinner("Analyzing skill gaps..."):
        # Extract skills from resume
        resume_skills = set(selected_resume["parsed"].get("skills", []))
        
        # Extract skills from job description (simple keyword extraction)
        # In production, use the skill_extractor service
        job_skills_lower = job_description.lower()
        
        # Common skill keywords
        common_skills = [
            "python", "javascript", "java", "go", "rust", "typescript", "c++", "c#", "php",
            "django", "flask", "fastapi", "spring", "express", "node.js", "graphql", "rest", "microservices",
            "react", "vue", "angular", "html", "css", "next.js", "tailwind", "redux",
            "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
            "git", "ci/cd", "jenkins", "github actions",
            "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "machine learning",
        ]
        
        job_skills = set()
        for skill in common_skills:
            if skill in job_skills_lower:
                job_skills.add(skill)
        
        # Perform gap analysis
        analysis = skill_gap_engine.analyze_gap(
            resume_skills=resume_skills,
            job_skills=job_skills,
            job_description=job_description,
        )
    
    # Display results
    st.divider()
    st.subheader("Gap Analysis Results")
    
    # Overall metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Match Percentage", f"{analysis.match_percentage}%")
    col2.metric("Matched Skills", len(analysis.matched_skills))
    col3.metric("Missing Skills", len(analysis.missing_skills))
    
    # Gap severity
    severity_colors = {
        "low": "🟢",
        "medium": "🟡",
        "high": "🔴",
    }
    st.metric(
        "Gap Severity",
        f"{severity_colors.get(analysis.gap_severity, '⚪')} {analysis.gap_severity.upper()}",
        help="Overall severity of skill gaps based on critical and medium gaps"
    )
    
    st.divider()
    
    # Matched skills
    st.subheader("✅ Matched Skills")
    if analysis.matched_skills:
        matched_chips = " ".join([
            f'<span class="skill-chip" style="background-color: #d4edda; color: #155724;">{skill}</span>'
            for skill in analysis.matched_skills
        ])
        st.markdown(matched_chips, unsafe_allow_html=True)
    else:
        st.caption("No matching skills found")
    
    st.divider()
    
    # Critical gaps
    if analysis.critical_gaps:
        st.subheader("🔴 Critical Gaps (High Priority)")
        st.caption("These skills are critical for the role and should be learned first")
        for gap in analysis.critical_gaps:
            st.markdown(
                f'<div class="critical-gap"><strong>{gap}</strong> - High Priority</div>',
                unsafe_allow_html=True,
            )
    
    # Medium gaps
    if analysis.medium_gaps:
        st.subheader("🟡 Medium Gaps (Important)")
        st.caption("These skills are important but not critical")
        for gap in analysis.medium_gaps:
            st.markdown(
                f'<div class="medium-gap"><strong>{gap}</strong> - Medium Priority</div>',
                unsafe_allow_html=True,
            )
    
    # Optional gaps
    if analysis.optional_gaps:
        st.subheader("⚪ Optional Gaps (Nice to Have)")
        st.caption("These skills are beneficial but not required")
        for gap in analysis.optional_gaps:
            st.markdown(
                f'<div class="optional-gap"><strong>{gap}</strong> - Optional</div>',
                unsafe_allow_html=True,
            )
    
    st.divider()
    
    # Recommended learning order
    st.subheader("📚 Recommended Learning Order")
    st.caption("Skills are ordered by difficulty and dependencies")
    
    if analysis.recommended_learning_order:
        learning_order = analysis.recommended_learning_order
        for i, skill in enumerate(learning_order, 1):
            st.markdown(f"**{i}.** {skill}")
    else:
        st.info("No learning order recommendations available")
    
    st.divider()
    
    # Visual gap analysis
    st.subheader("📊 Visual Gap Analysis")
    
    # Create gap breakdown chart
    gap_categories = ["Critical", "Medium", "Optional"]
    gap_counts = [
        len(analysis.critical_gaps),
        len(analysis.medium_gaps),
        len(analysis.optional_gaps),
    ]
    
    fig = go.Figure(data=[
        go.Bar(
            name="Gap Count",
            x=gap_categories,
            y=gap_counts,
            marker_color=['#dc3545', '#ffc107', '#6c757d'],
            text=gap_counts,
            textposition='outside',
        )
    ])
    
    fig.update_layout(
        title="Skill Gap Breakdown by Priority",
        yaxis_title="Number of Skills",
        xaxis_title="Gap Priority",
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f1f5f9"),
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Detailed gap table
    st.subheader("📋 Detailed Gap Analysis")
    
    gap_data = []
    for skill in analysis.critical_gaps:
        gap_data.append({
            "Skill": skill,
            "Priority": "Critical",
            "Category": categorize_skill(skill).value,
        })
    for skill in analysis.medium_gaps:
        gap_data.append({
            "Skill": skill,
            "Priority": "Medium",
            "Category": categorize_skill(skill).value,
        })
    for skill in analysis.optional_gaps:
        gap_data.append({
            "Skill": skill,
            "Priority": "Optional",
            "Category": categorize_skill(skill).value,
        })
    
    if gap_data:
        st.dataframe(
            gap_data,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success("✅ No skill gaps found! You have all the required skills.")

# Footer
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.8rem;">
        <p>Powered by HireFlow AI • Skill Gap Analysis Engine</p>
    </div>
    """,
    unsafe_allow_html=True,
)
