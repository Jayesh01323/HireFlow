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
from src.services.match_engine import HIGH_PRIORITY_SKILLS, MEDIUM_PRIORITY_SKILLS, LOW_PRIORITY_SKILLS
from src.services.skill_categorizer import categorize_skill, SkillCategory
from src.utils import get_env, load_env

load_env()
init_db()

DB_PATH = Path(get_env("DATABASE_PATH", "data/hireflow.db"))


def get_priority_badge(skill: str) -> str:
    """Get priority badge for a skill."""
    skill_lower = skill.lower()
    if skill_lower in [s.lower() for s in HIGH_PRIORITY_SKILLS]:
        return ' <span style="background-color: #dc3545; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px; margin-left: 4px;">HIGH</span>'
    elif skill_lower in [s.lower() for s in MEDIUM_PRIORITY_SKILLS]:
        return ' <span style="background-color: #ffc107; color: #333; padding: 2px 6px; border-radius: 8px; font-size: 10px; margin-left: 4px;">MED</span>'
    elif skill_lower in [s.lower() for s in LOW_PRIORITY_SKILLS]:
        return ' <span style="background-color: #6c757d; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px; margin-left: 4px;">LOW</span>'
    return ''


def get_skill_color(skill: str, is_matched: bool) -> str:
    """Get background color for skill chip based on match status and category."""
    if not is_matched:
        return "#fff5f5"  # Light red for missing
    
    category = categorize_skill(skill)
    category_colors = {
        SkillCategory.PROGRAMMING_LANGUAGES: "#e3f2fd",
        SkillCategory.FRONTEND: "#f3e5f5",
        SkillCategory.BACKEND: "#e8f5e9",
        SkillCategory.DATABASES: "#fff3e0",
        SkillCategory.CLOUD: "#fce4ec",
        SkillCategory.DEVOPS: "#e0f2f1",
        SkillCategory.DATA_SCIENCE: "#f1f8e9",
        SkillCategory.TESTING: "#fff9c4",
        SkillCategory.MOBILE: "#e8eaf6",
        SkillCategory.TOOLS: "#f5f5f5",
        SkillCategory.SOFT_SKILLS: "#fce4ec",
        SkillCategory.OTHER: "#f5f5f5",
    }
    return category_colors.get(category, "#d4edda")


def get_skill_text_color(skill: str, is_matched: bool) -> str:
    """Get text color for skill chip based on match status and category."""
    if not is_matched:
        return "#c53030"  # Dark red for missing
    
    category = categorize_skill(skill)
    category_text_colors = {
        SkillCategory.PROGRAMMING_LANGUAGES: "#1565c0",
        SkillCategory.FRONTEND: "#7b1fa2",
        SkillCategory.BACKEND: "#2e7d32",
        SkillCategory.DATABASES: "#ef6c00",
        SkillCategory.CLOUD: "#c2185b",
        SkillCategory.DEVOPS: "#00695c",
        SkillCategory.DATA_SCIENCE: "#558b2f",
        SkillCategory.TESTING: "#f57f17",
        SkillCategory.MOBILE: "#283593",
        SkillCategory.TOOLS: "#424242",
        SkillCategory.SOFT_SKILLS: "#c2185b",
        SkillCategory.OTHER: "#424242",
    }
    return category_text_colors.get(category, "#155724")

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
                # Enhanced skill chips with priority indicators
                chips_html = " ".join([
                    f'<span style="background-color: {get_skill_color(skill, True)}; color: {get_skill_text_color(skill, True)}; padding: 6px 14px; border-radius: 20px; margin: 4px; display: inline-block; font-size: 13px; font-weight: 500; border: 1px solid rgba(0,0,0,0.1);">{skill}{get_priority_badge(skill)}</span>'
                    for skill in matched_skills_list
                ])
                st.markdown(chips_html, unsafe_allow_html=True)
            else:
                st.caption("No matching skills found")
        
        with col_b:
            st.markdown("### ❌ Missing Skills")
            if match_results["missing_skills"]:
                missing_skills_list = sorted(match_results["missing_skills"])
                # Enhanced skill chips with priority indicators
                chips_html = " ".join([
                    f'<span style="background-color: {get_skill_color(skill, False)}; color: {get_skill_text_color(skill, False)}; padding: 6px 14px; border-radius: 20px; margin: 4px; display: inline-block; font-size: 13px; font-weight: 500; border: 1px solid rgba(0,0,0,0.1);">{skill}{get_priority_badge(skill)}</span>'
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
            st.markdown("### Category Match Distribution")
            category_match = analysis["category_match"]
            
            if category_match:
                categories = list(category_match.keys())
                match_percentages = [category_match[cat]["match_percentage"] for cat in categories]
                
                # Category-wise match chart
                fig = go.Figure(data=[
                    go.Bar(name="Match %", x=categories, y=match_percentages, 
                           marker_color='rgba(76, 175, 80, 0.8)',
                           text=[f"{pct}%" for pct in match_percentages],
                           textposition='outside')
                ])
                fig.update_layout(
                    title="Match Percentage by Category",
                    yaxis_title="Match Percentage",
                    xaxis_title="Category",
                    yaxis_range=[0, 100],
                    height=500,
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed category breakdown
                st.markdown("#### Category Breakdown")
                category_data = []
                for cat in categories:
                    category_data.append({
                        "Category": cat,
                        "Match %": category_match[cat]["match_percentage"],
                        "Matched": category_match[cat]["matched_count"],
                        "Missing": category_match[cat]["missing_count"],
                        "Total": category_match[cat]["total_count"]
                    })
                
                category_df = __import__('pandas').DataFrame(category_data)
                st.dataframe(category_df, use_container_width=True, hide_index=True)
            else:
                st.caption("No category data available")
        
        with tab3:
            st.markdown("### Category Gap Analysis")
            category_match = analysis["category_match"]
            
            if category_match:
                categories = list(category_match.keys())
                match_percentages = [category_match[cat]["match_percentage"] for cat in categories]
                missing_counts = [category_match[cat]["missing_count"] for cat in categories]
                matched_counts = [category_match[cat]["matched_count"] for cat in categories]
                
                # Enhanced gap analysis chart
                fig = go.Figure()
                
                # Add match percentage bars
                fig.add_trace(go.Bar(
                    x=categories,
                    y=match_percentages,
                    name="Match %",
                    marker_color='rgba(76, 175, 80, 0.8)',
                    text=[f"{pct}%" for pct in match_percentages],
                    textposition='outside',
                ))
                
                # Add gap indicator
                fig.add_trace(go.Bar(
                    x=categories,
                    y=[100 - pct for pct in match_percentages],
                    name="Gap %",
                    marker_color='rgba(244, 67, 54, 0.6)',
                    text=[f"{100 - pct}%" for pct in match_percentages],
                    textposition='outside',
                ))
                
                fig.update_layout(
                    title="Category Match vs Gap Analysis",
                    barmode='stack',
                    yaxis_title="Percentage",
                    xaxis_title="Category",
                    yaxis_range=[0, 100],
                    height=500,
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed gap breakdown
                st.markdown("#### Detailed Gap Breakdown")
                gap_data = []
                for cat in categories:
                    gap_data.append({
                        "Category": cat,
                        "Matched": matched_counts[categories.index(cat)],
                        "Missing": missing_counts[categories.index(cat)],
                        "Match %": match_percentages[categories.index(cat)],
                        "Gap %": 100 - match_percentages[categories.index(cat)]
                    })
                
                gap_df = __import__('pandas').DataFrame(gap_data)
                st.dataframe(gap_df, use_container_width=True, hide_index=True)
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
