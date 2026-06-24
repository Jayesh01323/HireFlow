"""
Learning Dashboard Page

Comprehensive dashboard for learning and career development.
Integrates skill gap analysis, learning roadmaps, course recommendations,
career path prediction, and career fit scoring.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

import streamlit as st

from src.services.career_fit_score import CareerFitScoreEngine
from src.services.career_path_predictor import CareerPathPredictor
from src.services.course_recommender import CourseRecommender
from src.services.roadmap_generator import RoadmapGenerator
from src.services.skill_gap_engine import SkillGapEngine
from src.utils import get_env, load_env

load_env()

DB_PATH = Path(get_env("DATABASE_PATH", "data/hireflow.db"))

st.set_page_config(page_title="Learning Dashboard", page_icon="📚", layout="wide")

# Custom CSS for dark theme
st.markdown(
    """
    <style>
        .stApp {
            background-color: #0f172a;
        }
        .metric-card {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border: 1px solid #475569;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        .score-high {
            color: #10b981;
            font-weight: bold;
            font-size: 2rem;
        }
        .score-medium {
            color: #f59e0b;
            font-weight: bold;
            font-size: 2rem;
        }
        .score-low {
            color: #ef4444;
            font-weight: bold;
            font-size: 2rem;
        }
        .critical-badge {
            background-color: #ef4444;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
        }
        .medium-badge {
            background-color: #f59e0b;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
        }
        .optional-badge {
            background-color: #3b82f6;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📚 Learning Dashboard")
st.markdown("Your personalized learning and career development hub.")

# Initialize services
@st.cache_resource
def get_services():
    return {
        "skill_gap": SkillGapEngine(),
        "roadmap": RoadmapGenerator(),
        "course_recommender": CourseRecommender(),
        "career_predictor": CareerPathPredictor(),
        "career_fit_score": CareerFitScoreEngine(),
    }

services = get_services()

# Load latest resume
@st.cache_data
def load_latest_resume():
    return get_latest_resume(DB_PATH)

latest_resume = load_latest_resume()

if not latest_resume:
    st.warning("⚠️ No resume found. Please upload and parse a resume on the Resume Parser page.")
    st.info("Once you upload a resume, this dashboard will provide personalized learning recommendations.")
else:
    # Extract resume data
    skills = latest_resume.get("skills", [])
    projects = latest_resume.get("projects", [])
    experience = latest_resume.get("experience", [])
    education = latest_resume.get("education", [])
    
    # Normalize skills
    skill_names = [s.get("name", s) if isinstance(s, dict) else s for s in skills]
    skill_set = set(skill_names)
    
    st.divider()
    
    # Section 1: Career Fit Score
    st.subheader("🎯 Career Readiness Score")
    
    with st.spinner("Calculating career readiness..."):
        fit_score = services["career_fit_score"].calculate_fit_score(
            skills=skill_names,
            projects=projects,
            experience=experience,
            education=education,
        )
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        score_class = "score-high" if fit_score.overall_score >= 80 else "score-medium" if fit_score.overall_score >= 60 else "score-low"
        st.markdown(f'<div class="metric-card"><div class="{score_class}">{fit_score.overall_score}%</div><small>Overall</small></div>', unsafe_allow_html=True)
    
    with col2:
        st.metric("Skills", f"{fit_score.skills_score}%")
    
    with col3:
        st.metric("Projects", f"{fit_score.projects_score}%")
    
    with col4:
        st.metric("Experience", f"{fit_score.experience_score}%")
    
    with col5:
        st.metric("Education", f"{fit_score.education_score}%")
    
    st.divider()
    
    # Section 2: Skill Gap Analysis
    st.subheader("📊 Skill Gap Analysis")
    
    # Use a sample job description for gap analysis
    sample_job_skills = ["python", "javascript", "react", "django", "sql", "docker", "aws", "git"]
    
    with st.spinner("Analyzing skill gaps..."):
        gap_analysis = services["skill_gap"].analyze_gap(
            resume_skills=skill_set,
            job_skills=set(sample_job_skills),
        )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔴 Critical Gaps")
        if gap_analysis.critical_gaps:
            for skill in gap_analysis.critical_gaps:
                st.markdown(f'<span class="critical-badge">{skill.title()}</span>', unsafe_allow_html=True)
        else:
            st.success("✅ No critical gaps!")
    
    with col2:
        st.markdown("### 🟡 Medium Gaps")
        if gap_analysis.medium_gaps:
            for skill in gap_analysis.medium_gaps:
                st.markdown(f'<span class="medium-badge">{skill.title()}</span>', unsafe_allow_html=True)
        else:
            st.success("✅ No medium gaps!")
    
    with col3:
        st.markdown("### 🔵 Optional Gaps")
        if gap_analysis.optional_gaps:
            for skill in gap_analysis.optional_gaps:
                st.markdown(f'<span class="optional-badge">{skill.title()}</span>', unsafe_allow_html=True)
        else:
            st.success("✅ No optional gaps!")
    
    st.divider()
    
    # Section 3: Learning Roadmap
    st.subheader("🗺️ Learning Roadmap")
    
    timeline = st.selectbox("Select Timeline", ["7 Day Plan", "30 Day Plan", "90 Day Plan"])
    
    timeline_key = timeline.lower().replace(" ", "_")
    
    with st.spinner("Generating learning roadmap..."):
        roadmap = services["roadmap"].generate_roadmap(
            missing_skills=gap_analysis.missing_skills,
            target_role="Software Developer",
        )
    
    if timeline_key in roadmap:
        plan = roadmap[timeline_key]
        st.markdown(f"**{plan.total_duration} Plan**")
        st.markdown(f"*{plan.start_date.strftime('%Y-%m-%d')} to {plan.end_date.strftime('%Y-%m-%d')}*")
        
        for milestone in plan.milestones:
            with st.expander(f"📌 {milestone.title}"):
                st.write(milestone.description)
                st.markdown("**Skills:** " + ", ".join(milestone.skills))
                st.markdown("**Duration:** " + milestone.estimated_duration)
                st.markdown("**Resources:**")
                for resource in milestone.resources:
                    st.write(f"• {resource}")
    
    st.divider()
    
    # Section 4: Course Recommendations
    st.subheader("📖 Course Recommendations")
    
    with st.spinner("Finding courses for you..."):
        courses = services["course_recommender"].recommend_courses(
            skills=gap_analysis.missing_skills,
            free_only=True,
            limit=5,
        )
    
    if courses:
        for course in courses:
            with st.expander(f"🎓 {course.title}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Platform:** {course.platform}")
                    st.write(f"**Duration:** {course.duration}")
                    st.write(f"**Difficulty:** {course.difficulty}")
                    st.write(f"**Skills:** {', '.join(course.skills)}")
                    st.write(f"**Rating:** ⭐ {course.rating}")
                with col2:
                    if course.is_free:
                        st.success("FREE")
                    else:
                        st.warning("PAID")
                st.markdown(f"[View Course]({course.url})")
    else:
        st.info("No courses found for your current skill gaps.")
    
    st.divider()
    
    # Section 5: Career Path Prediction
    st.subheader("🚀 Career Path Prediction")
    
    with st.spinner("Predicting career paths..."):
        career_prediction = services["career_predictor"].predict_career_path(
            skills=skill_names,
            projects=projects,
            experience=experience,
        )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### 🎯 Top Career Path: {career_prediction.top_career_path}")
        
        st.markdown("### Alternative Paths")
        for path in career_prediction.alternative_paths[:3]:
            st.write(f"• **{path.title}** - Fit: {path.fit_score}%")
    
    with col2:
        st.markdown("### 💡 Growth Opportunities")
        for opp in career_prediction.growth_opportunities:
            st.write(f"• {opp}")
    
    st.divider()
    
    # Section 6: Recommendations
    st.subheader("💡 Personalized Recommendations")
    
    for rec in fit_score.recommendations:
        st.write(f"• {rec}")
    
    st.divider()
    
    # Section 7: Career Trajectory
    st.subheader("📈 Career Trajectory")
    
    for stage in career_prediction.career_trajectory:
        st.write(f"• {stage}")

# Footer
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.8rem;">
        <p>Powered by HireFlow AI • Career Intelligence Engine</p>
    </div>
    """,
    unsafe_allow_html=True,
)
