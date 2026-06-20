"""
Job Matcher Page

Streamlit page for matching parsed resume data against job openings.
Provides skill gap analysis between candidate profile and target roles.
"""

from __future__ import annotations

from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.database import get_all_resumes, init_db
from src.matcher import analyze_match
from src.utils import get_env, load_env

load_env()
init_db()

DB_PATH = Path(get_env("DATABASE_PATH", "data/hireflow.db"))

st.set_page_config(page_title="Job Matcher", page_icon="🎯", layout="wide")

st.title("🎯 Job Matcher v2")
st.markdown(
    "Compare your resume skills against job descriptions with intelligent skill gap analysis. "
    "Features weighted scoring, category-based insights, and contextual recommendations."
)

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
)
selected_resume = resume_options[selected_resume_label]

# Job description input
st.subheader("Job Description")
job_description = st.text_area(
    "Paste the job description here",
    height=200,
    placeholder="Paste the full job description including requirements, qualifications, and skills...",
    help="The more detailed the job description, the better the skill extraction will work",
)

# Analyze button
if st.button("Analyze Match", type="primary", disabled=not job_description):
    with st.spinner("Analyzing match..."):
        # Perform match analysis
        analysis = analyze_match(selected_resume["parsed"], job_description)
        
        match_results = analysis["match_results"]
        # Handle both old and new match result formats
        weighted_match_pct = match_results.get("weighted_match_percentage", match_results.get("match_percentage", 0.0))
        tech_vs_soft = analysis["technical_vs_soft"]
        
        # Display match score
        st.divider()
        st.subheader("Match Results")
        st.caption("Score calculated using weighted skill relevance based on priority.")
        
        # Color-coded match score
        if weighted_match_pct >= 70:
            score_color = "🟢"
        elif weighted_match_pct >= 40:
            score_color = "🟡"
        else:
            score_color = "🔴"
        
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Overall Match",
            f"{score_color} {weighted_match_pct}%",
            help="Weighted match percentage considering skill priority"
        )
        col2.metric(
            "Technical Match",
            f"{tech_vs_soft['technical_match_percentage']}%",
            help="Match percentage for technical skills"
        )
        col3.metric(
            "Soft Skill Match",
            f"{tech_vs_soft['soft_skill_match_percentage']}%",
            help="Match percentage for soft skills"
        )
        
        # Priority breakdown
        st.divider()
        col_a, col_b, col_c = st.columns(3)
        col_a.metric(
            "High Priority",
            f"{match_results['high_priority_match']}%",
            help="Match for critical technical skills"
        )
        col_b.metric(
            "Medium Priority",
            f"{match_results['medium_priority_match']}%",
            help="Match for important skills"
        )
        col_c.metric(
            "Low Priority",
            f"{match_results['low_priority_match']}%",
            help="Match for general skills"
        )
        
        # Matched skills with chips
        st.divider()
        st.subheader("Skill Match Analysis")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("### ✅ Matched Skills")
            if match_results["matched_skills"]:
                matched_skills_list = sorted(match_results["matched_skills"])
                chips_html = " ".join([
                    f'<span style="background-color: #d4edda; color: #155724; padding: 4px 12px; border-radius: 16px; margin: 4px; display: inline-block; font-size: 14px;">{skill}</span>'
                    for skill in matched_skills_list
                ])
                st.markdown(chips_html, unsafe_allow_html=True)
            else:
                st.caption("No matching skills found")
        
        with col_b:
            st.markdown("### ❌ Missing Skills")
            if match_results["missing_skills"]:
                missing_skills_list = sorted(match_results["missing_skills"])
                chips_html = " ".join([
                    f'<span style="background-color: #f8d7da; color: #721c24; padding: 4px 12px; border-radius: 16px; margin: 4px; display: inline-block; font-size: 14px;">{skill}</span>'
                    for skill in missing_skills_list
                ])
                st.markdown(chips_html, unsafe_allow_html=True)
            else:
                st.caption("All required skills found!")
        
        # Enhanced recommendations
        st.divider()
        st.subheader("💡 Recommendations")
        
        recommendations = analysis["recommendations"]
        
        # Top priority skills
        if recommendations.get("top_priority_skills"):
            st.markdown("#### 🎯 Top Priority Skills To Learn")
            priority_skills = recommendations["top_priority_skills"]
            priority_chips = " ".join([
                f'<span style="background-color: #fff3cd; color: #856404; padding: 6px 16px; border-radius: 20px; margin: 4px; display: inline-block; font-weight: bold; font-size: 15px;">{skill}</span>'
                for skill in priority_skills
            ])
            st.markdown(priority_chips, unsafe_allow_html=True)
        
        # Learning recommendations
        if recommendations.get("learning_recommendations"):
            st.markdown("#### 📚 Learning Recommendations")
            for rec in recommendations["learning_recommendations"]:
                st.info(rec, icon="📖")
        
        # Career direction
        if recommendations.get("career_direction"):
            st.markdown("#### 🧭 Suggested Career Direction")
            st.success(recommendations["career_direction"], icon="🧭")
        
        # Category insights
        if recommendations.get("category_insights"):
            st.markdown("#### 📊 Category Insights")
            for category, data in recommendations["category_insights"].items():
                with st.expander(f"{category} ({data['missing_count']} missing)", expanded=False):
                    st.markdown(f"**Skills:** {', '.join(data['skills'])}")
                    st.caption(data['recommendation'])
        
        # Visual Analytics with Plotly
        st.divider()
        st.subheader("📊 Visual Analytics")
        
        # Create tabs for different charts
        tab1, tab2, tab3 = st.tabs(["Skill Categories", "Match Distribution", "Category Gap Analysis"])
        
        with tab1:
            st.markdown("### Skill Category Breakdown")
            resume_breakdown = analysis["resume_category_breakdown"]
            job_breakdown = analysis["job_category_breakdown"]
            
            if resume_breakdown:
                categories = list(resume_breakdown.keys())
                resume_counts = [resume_breakdown[cat]["count"] for cat in categories]
                
                fig = px.pie(
                    values=resume_counts,
                    names=categories,
                    title="Your Skills by Category",
                    hole=0.4,
                )
                fig.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("No skill data available")
        
        with tab2:
            st.markdown("### Match Distribution")
            matched_count = match_results["matched_count"]
            missing_count = len(match_results["missing_skills"])
            
            fig = go.Figure(data=[
                go.Bar(name="Matched", x=["Skills"], y=[matched_count], marker_color="#28a745"),
                go.Bar(name="Missing", x=["Skills"], y=[missing_count], marker_color="#dc3545")
            ])
            fig.update_layout(
                title="Matched vs Missing Skills",
                barmode="stack",
                yaxis_title="Count",
                xaxis_title="",
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.markdown("### Category Gap Analysis")
            category_match = analysis["category_match"]
            
            if category_match:
                categories = list(category_match.keys())
                match_percentages = [category_match[cat]["match_percentage"] for cat in categories]
                
                fig = px.bar(
                    x=categories,
                    y=match_percentages,
                    title="Match Percentage by Category",
                    labels={"x": "Category", "y": "Match %"},
                    color=match_percentages,
                    color_continuous_scale="RdYlGn",
                )
                fig.update_layout(yaxis_title="Match Percentage")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("No category data available")
        
        # Detailed skill breakdown with categorization
        st.divider()
        st.subheader("📋 Detailed Skill Breakdown")
        
        tab4, tab5 = st.tabs(["Your Skills by Category", "Job Skills by Category"])
        
        with tab4:
            categorized_resume = analysis["categorized_resume"]
            if categorized_resume:
                for category, skills in categorized_resume.items():
                    with st.expander(f"{category} ({len(skills)} skills)", expanded=False):
                        chips_html = " ".join([
                            f'<span style="background-color: #e7f3ff; color: #0066cc; padding: 4px 12px; border-radius: 12px; margin: 4px; display: inline-block; font-size: 13px;">{skill}</span>'
                            for skill in skills
                        ])
                        st.markdown(chips_html, unsafe_allow_html=True)
            else:
                st.caption("No skills found in resume")
        
        with tab5:
            categorized_job = analysis["categorized_job"]
            if categorized_job:
                for category, skills in categorized_job.items():
                    with st.expander(f"{category} ({len(skills)} skills)", expanded=False):
                        chips_html = " ".join([
                            f'<span style="background-color: #fff8e1; color: #ff8f00; padding: 4px 12px; border-radius: 12px; margin: 4px; display: inline-block; font-size: 13px;">{skill}</span>'
                            for skill in skills
                        ])
                        st.markdown(chips_html, unsafe_allow_html=True)
            else:
                st.caption("No skills extracted from job description")
