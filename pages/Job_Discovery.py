"""
Job Discovery Page

Streamlit page for discovering job opportunities across multiple sources.
Search, filter, and save jobs from various job boards.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import streamlit as st

from src.jobs.aggregator import JobAggregator
from src.matcher import analyze_match
from src.services.job_discovery_service import JobDiscoveryService
from src.services.ranking_engine import RankingEngine
from src.services.saved_jobs_service import SavedJobsService
from src.services.skill_gap_engine import SkillGapEngine
from src.services.roadmap_engine import RoadmapEngine
from src.services.job_intelligence_service import JobIntelligenceService
from src.agents.resume_optimization_agent import ResumeOptimizationAgent
from src.services.application_workflow_service import ApplicationWorkflowService
from src.utils import get_env, get_latest_resume, load_env

load_env()

DB_PATH = Path(get_env("DATABASE_PATH", "data/hireflow.db"))

st.set_page_config(page_title="Job Discovery", page_icon="🔍", layout="wide")

# Custom CSS for dark theme matching HireFlow design
st.markdown(
    """
    <style>
        .stApp {
            background-color: #0f172a;
        }
        .job-card {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border: 1px solid #475569;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        .job-card:hover {
            border-color: #3b82f6;
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.2);
        }
        .rank-badge {
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.875rem;
        }
        .match-score-high {
            color: #10b981;
            font-weight: bold;
        }
        .match-score-medium {
            color: #f59e0b;
            font-weight: bold;
        }
        .match-score-low {
            color: #ef4444;
            font-weight: bold;
        }
        .skill-tag {
            background: #1e40af;
            color: #e0e7ff;
            padding: 0.25rem 0.5rem;
            border-radius: 6px;
            font-size: 0.75rem;
            margin: 0.125rem;
            display: inline-block;
        }
        div[data-testid="stExpanderToggleIcon"] {
            color: #3b82f6;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🔍 Job Discovery")
st.markdown("Discover job opportunities with AI-powered matching and ranking.")

# Initialize services
@st.cache_resource
def get_job_aggregator():
    return JobAggregator()

@st.cache_resource
def get_job_discovery_service():
    return JobDiscoveryService()

@st.cache_resource
def get_ranking_engine():
    return RankingEngine()

@st.cache_resource
def get_saved_jobs_service():
    return SavedJobsService()

@st.cache_resource
def get_skill_gap_engine():
    return SkillGapEngine()

@st.cache_resource
def get_roadmap_engine():
    return RoadmapEngine()

@st.cache_resource
def get_job_intelligence_service():
    return JobIntelligenceService()

@st.cache_resource
def get_resume_optimization_agent():
    return ResumeOptimizationAgent()

@st.cache_resource
def get_application_workflow_service():
    return ApplicationWorkflowService()

job_aggregator = get_job_aggregator()
job_discovery_service = get_job_discovery_service()
ranking_engine = get_ranking_engine()
saved_jobs_service = get_saved_jobs_service()
skill_gap_engine = get_skill_gap_engine()
roadmap_engine = get_roadmap_engine()
job_intelligence_service = get_job_intelligence_service()
resume_optimization_agent = get_resume_optimization_agent()
application_workflow_service = get_application_workflow_service()

# Load latest resume for matching
@st.cache_data
def load_latest_resume():
    return get_latest_resume(DB_PATH)

latest_resume = load_latest_resume()

# Sidebar for Saved Jobs
with st.sidebar:
    st.header("💾 Saved Jobs")
    saved_jobs = saved_jobs_service.get_saved_jobs()
    
    if saved_jobs:
        st.metric("Total Saved", len(saved_jobs))
        
        for job in saved_jobs[:5]:
            with st.expander(f"{job['job_title']} @ {job['company']}", expanded=False):
                st.write(f"**Location:** {job['location']}")
                st.write(f"**Salary:** {job['salary']}")
                st.write(f"**Work Mode:** {job['work_mode']}")
                
                if st.button("Remove", key=f"remove_{job['id']}", use_container_width=True):
                    saved_jobs_service.remove_saved_job(job['job_id'])
                    st.rerun()
        
        if len(saved_jobs) > 5:
            st.caption(f"And {len(saved_jobs) - 5} more saved jobs...")
    else:
        st.info("No saved jobs yet. Save jobs from the search results.")

# Main content
st.divider()

# Search and Filters Section
col1, col2, col3 = st.columns([3, 2, 2])
with col1:
    search_query = st.text_input("🔎 Search Jobs", placeholder="e.g., Python Developer, Backend Engineer")
with col2:
    location_filter = st.text_input("📍 Location", placeholder="e.g., Bangalore, Remote")
with col3:
    experience_filter = st.selectbox("💼 Experience Level", ["Any", "0-1 years", "1-3 years", "2-4 years", "3-5 years"])

col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    remote_filter = st.checkbox("🏠 Remote Only")
with col2:
    salary_min = st.number_input("💰 Min Salary (₹)", min_value=0, value=0, step=10000)
with col3:
    salary_max = st.number_input("💰 Max Salary (₹)", min_value=0, value=0, step=10000)

st.divider()

# Search button
search_col1, search_col2, search_col3 = st.columns([1, 1, 4])
with search_col1:
    search_button = st.button("🔍 Search Jobs", use_container_width=True, type="primary")
with search_col2:
    clear_button = st.button("🗑️ Clear Filters", use_container_width=True)

if clear_button:
    st.rerun()

# Perform search
if search_button or search_query:
    with st.spinner("Searching jobs from multiple sources..."):
        try:
            # Map experience filter to standard values
            exp_mapping = {
                "Any": None,
                "0-1 years": "entry",
                "1-3 years": "entry",
                "2-4 years": "mid",
                "3-5 years": "mid",
            }
            experience_level = exp_mapping.get(experience_filter, None)
            
            # Extract resume skills if available
            resume_skills = set()
            if latest_resume and hasattr(latest_resume, 'skills'):
                for skill_item in latest_resume.skills:
                    if hasattr(skill_item, 'name'):
                        resume_skills.add(skill_item.name.lower())
                    elif isinstance(skill_item, dict):
                        resume_skills.add(skill_item.get('name', '').lower())
            
            # Search jobs using aggregator
            ranked_jobs = job_aggregator.search_jobs(
                query=search_query,
                location=location_filter if location_filter else None,
                remote=remote_filter,
                experience=experience_level,
                salary_min=salary_min if salary_min > 0 else None,
                sources=None,  # All sources
                limit=50,
                resume_skills=resume_skills if resume_skills else None,
                user_preferences={
                    "preferred_location": location_filter if location_filter else None,
                    "remote_only": remote_filter,
                    "experience_years": 3,  # Default
                    "expected_salary_min": salary_min if salary_min > 0 else None,
                },
            )
            
            # Display results
            st.subheader(f"📊 Found {len(ranked_jobs)} Jobs")
            
            if not ranked_jobs:
                st.info("No jobs found matching your criteria. Try adjusting your filters or search terms.")
            else:
                for idx, job_result in enumerate(ranked_jobs[:20], 1):  # Show top 20
                    job = job_result["job"]
                    overall_score = job_result["overall_score"]
                    match_score = job_result.get("skill_match_score", 0.0)
                    matched_skills = job_result.get("matched_skills", [])
                    missing_skills = job_result.get("missing_skills", [])
                    skill_coverage = job_result.get("skill_coverage", 0.0)
                    
                    # Job card
                    with st.container():
                        st.markdown(f"""
                        <div class="job-card">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <div>
                                    <span class="rank-badge">Rank #{idx}</span>
                                    <h3 style="margin: 0.5rem 0 0.25rem 0; color: #f1f5f9;">{job.title}</h3>
                                    <p style="margin: 0; color: #94a3b8; font-size: 0.9rem;">{job.company} • {job.location or 'Various'}</p>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 1.5rem; font-weight: bold; color: #10b981;">{overall_score:.1f}</div>
                                    <div style="font-size: 0.75rem; color: #94a3b8;">Overall Score</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Job details expander
                        with st.expander("View Details", expanded=False):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write("**💰 Salary:**", f"₹{job.salary_min:,} - ₹{job.salary_max:,}" if job.salary_min else job.salary or "Not specified")
                                st.write("**💼 Experience:**", f"{job.experience_min}-{job.experience_max} years" if job.experience_min else "Not specified")
                                st.write("**🏠 Remote:**", "Yes" if job.is_remote else "No")
                            
                            with col2:
                                st.write("**📅 Posted:**", job.posted_date.strftime("%Y-%m-%d") if job.posted_date else "Recently")
                                st.write("**🔗 Source:**", job.source.capitalize())
                                st.write("**📊 Skill Coverage:**", f"{skill_coverage:.1f}%")
                            
                            with col3:
                                st.write("**🎯 Match Score:**", f"{match_score:.1f}%")
                                st.write("**⏰ Freshness:**", f"{job_result.get('freshness_score', 0.0):.1f}")
                                st.write("**📍 Experience Fit:**", f"{job_result.get('experience_fit_score', 0.0):.1f}")
                            
                            st.divider()
                            
                            # Description
                            st.write("**📝 Description:**")
                            st.write(job.description or "No description available")
                            
                            # Skills
                            st.write("**🛠️ Required Skills:**")
                            if job.skills:
                                skill_tags = " ".join([f'<span class="skill-tag">{skill}</span>' for skill in job.skills[:10]])
                                st.markdown(skill_tags, unsafe_allow_html=True)
                                if len(job.skills) > 10:
                                    st.caption(f"And {len(job.skills) - 10} more skills...")
                            else:
                                st.write("No skills specified")
                            
                            # Match analysis if resume available
                            if latest_resume and matched_skills is not None:
                                st.divider()
                                st.write("**🎯 Match Analysis:**")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**✅ Matched Skills ({len(matched_skills)}):**")
                                    if matched_skills:
                                        for skill in sorted(matched_skills)[:10]:
                                            st.write(f"  • {skill}")
                                        if len(matched_skills) > 10:
                                            st.caption(f"And {len(matched_skills) - 10} more...")
                                    else:
                                        st.write("  None")
                                
                                with col2:
                                    st.write(f"**❌ Missing Skills ({len(missing_skills)}):**")
                                    if missing_skills:
                                        for skill in sorted(missing_skills)[:10]:
                                            st.write(f"  • {skill}")
                                        if len(missing_skills) > 10:
                                            st.caption(f"And {len(missing_skills) - 10} more...")
                                    else:
                                        st.write("  None")
                                
                                # Skill gap analysis
                                if missing_skills and job_result.get("skill_gap_analysis"):
                                    st.divider()
                                    st.write("**📊 Skill Gap Analysis:**")
                                    gap = job_result["skill_gap_analysis"]
                                    st.write(f"**Gap Severity:** {gap.get('gap_severity', 'Unknown').upper()}")
                                    if gap.get("critical_skills"):
                                        st.write("**Critical Skills:**")
                                        for skill in gap["critical_skills"][:5]:
                                            st.write(f"  • {skill}")
                            else:
                                st.info("📄 Upload a resume on the Resume Parser page to see match analysis.")
                        
                        # Action buttons
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col1:
                            if st.button("❤️ Save Job", key=f"save_{job.source}_{job.external_id}", use_container_width=True):
                                try:
                                    saved_jobs_service.save_job({
                                        "job_id": f"{job.source}_{job.external_id}",
                                        "job_title": job.title,
                                        "company": job.company,
                                        "location": job.location,
                                        "salary": f"₹{job.salary_min:,} - ₹{job.salary_max:,}" if job.salary_min else job.salary,
                                        "work_mode": "Remote" if job.is_remote else "On-site",
                                        "source": job.source,
                                        "source_url": job.url,
                                    })
                                    st.success("Job saved successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error saving job: {e}")
                        
                        with col2:
                            if st.button("🔗 Apply", key=f"apply_{job.source}_{job.external_id}", use_container_width=True):
                                st.info(f"Opening application page for {job.title} at {job.company}...")
                                # In production, this would open the actual job URL
                        
                        with col3:
                            if st.button("📋 Copy Link", key=f"copy_{job.source}_{job.external_id}", use_container_width=True):
                                st.toast(f"Copied: {job.url}")
                        
                        st.divider()
        except Exception as e:
            st.error(f"Error searching jobs: {e}")
            st.info("Using database search as fallback...")
            
            # Fallback to database search
            try:
                db_jobs = job_aggregator.search_database_jobs(
                    keyword=search_query if search_query else None,
                    location=location_filter if location_filter else None,
                    remote_only=remote_filter,
                    experience_level=experience_level,
                    salary_min=salary_min if salary_min > 0 else None,
                    salary_max=salary_max if salary_max > 0 else None,
                    limit=20,
                )
                
                st.subheader(f"📊 Found {len(db_jobs)} Jobs (from database)")
                
                for job in db_jobs:
                    with st.container():
                        st.markdown(f"""
                        <div class="job-card">
                            <h3 style="margin: 0 0 0.25rem 0; color: #f1f5f9;">{job['title']}</h3>
                            <p style="margin: 0; color: #94a3b8; font-size: 0.9rem;">{job['company']} • {job['location'] or 'Various'}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        with st.expander("View Details", expanded=False):
                            st.write("**💰 Salary:**", f"₹{job['salary_min']:,} - ₹{job['salary_max']:,}" if job.get('salary_min') else "Not specified")
                            st.write("**🏠 Remote:**", "Yes" if job['remote'] else "No")
                            st.write("**🔗 Source:**", job['source'].capitalize())
                            st.write("**📅 Posted:**", job['posted_date'] if job.get('posted_date') else "Recently")
                            st.write("**📝 Description:**", job['description'] or "No description")
                            if job.get('skills'):
                                st.write("**🛠️ Skills:**", ", ".join(job['skills'][:10]))
                        st.divider()
            except Exception as db_e:
                st.error(f"Error loading jobs from database: {db_e}")
else:
    # Show recent jobs from database when no search
    st.subheader("📊 Recent Jobs")
    try:
        recent_jobs = job_aggregator.get_recent_jobs(days=7, limit=10)
        
        if not recent_jobs:
            st.info("No recent jobs found. Search for jobs to see results.")
        else:
            for job in recent_jobs:
                with st.container():
                    st.markdown(f"""
                    <div class="job-card">
                        <h3 style="margin: 0 0 0.25rem 0; color: #f1f5f9;">{job['title']}</h3>
                        <p style="margin: 0; color: #94a3b8; font-size: 0.9rem;">{job['company']} • {job['location'] or 'Various'}</p>
                        <p style="margin: 0.5rem 0 0 0; color: #cbd5e1; font-size: 0.85rem;">{job['source'].capitalize()} • {job['posted_date'] if job.get('posted_date') else 'Recently'}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("Quick View", expanded=False):
                        st.write(job['description'] or "No description")
                        if job.get('skills'):
                            st.write("**Skills:**", ", ".join(job['skills'][:10]))
                    
                    st.divider()
    except Exception as e:
        st.error(f"Error loading recent jobs: {e}")

# Footer
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.8rem;">
        <p>Powered by HireFlow AI • Live Job Discovery Engine</p>
    </div>
    """,
    unsafe_allow_html=True,
)
