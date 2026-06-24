"""
Analytics Dashboard Page

Streamlit page for visualizing career data, skill trends,
and job match analytics using Plotly charts.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from src.utils import get_env, load_env
from src.jobs.aggregator import JobAggregator
from src.services.application_workflow_service import ApplicationWorkflowService
from src.services.career_fit_score import CareerFitScoreEngine
from src.services.career_path_predictor import CareerPathPredictor
from src.services.skill_gap_engine import SkillGapEngine

logger = logging.getLogger(__name__)

load_env()

DB_PATH = Path(get_env("DATABASE_PATH", "data/hireflow.db"))

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        div[data-testid="stMetric"] {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1rem 1.25rem;
        }
        div[data-testid="stMetricLabel"] p {
            font-size: 0.9rem;
            color: #475569;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.75rem;
            color: #1e293b;
        }
        @media (prefers-color-scheme: dark) {
            div[data-testid="stMetric"] {
                background: #1e293b;
                border: 1px solid #334155;
            }
            div[data-testid="stMetricLabel"] p {
                color: #cbd5e1;
            }
            div[data-testid="stMetricValue"] {
                color: #f1f5f9;
            }
        }
        .dashboard-section {
            margin-top: 0.5rem;
            margin-bottom: 1.25rem;
        }
        .dashboard-caption {
            color: #64748b;
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Analytics Dashboard")
st.markdown(
    "Track resume parsing activity and skill insights from your HireFlow AI data.",
    help="Metrics and charts are computed from parsed resume JSON stored in SQLite.",
)


def get_db_cache_key(db_path: Path) -> str:
    """Return a cache-busting key based on database file state."""
    if not db_path.exists():
        return "missing"

    stat = db_path.stat()
    return f"{stat.st_mtime_ns}-{stat.st_size}"


@st.cache_data(show_spinner=False)
def load_resume_records(db_path: str, cache_key: str) -> list[dict[str, Any]]:
    """Load resume metadata and parsed JSON without fetching large raw_text blobs."""
    _ = cache_key
    path = Path(db_path)
    if not path.exists():
        return []

    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        # Check if parsed_json column exists
        cursor = conn.execute("PRAGMA table_info(resumes)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "parsed_json" in columns:
            query = """
                SELECT id, filename, parsed_json, created_at
                FROM resumes
                ORDER BY created_at DESC, id DESC
            """
        else:
            # Fallback for schema without parsed_json
            query = """
                SELECT id, filename, created_at
                FROM resumes
                ORDER BY created_at DESC, id DESC
            """
        
        rows = conn.execute(query).fetchall()

    records: list[dict[str, Any]] = []
    for row in rows:
        parsed = {}
        if "parsed_json" in row.keys() and row["parsed_json"]:
            try:
                parsed = json.loads(row["parsed_json"])
            except (json.JSONDecodeError, TypeError):
                parsed = {}

        records.append(
            {
                "id": row["id"],
                "filename": row["filename"],
                "created_at": row["created_at"],
                "parsed": parsed,
            }
        )

    return records


def parse_created_at(value: str | None) -> datetime | None:
    if not value:
        return None

    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return None


def extract_skill_names(parsed: dict[str, Any]) -> list[str]:
    skills = parsed.get("skills") or []
    names: list[str] = []

    for skill in skills:
        if isinstance(skill, str):
            name = skill.strip()
        elif isinstance(skill, dict):
            name = str(skill.get("name", "")).strip()
        else:
            continue

        if name:
            names.append(name)

    return names


def build_analytics(records: list[dict[str, Any]]) -> dict[str, Any]:
    total_resumes = len(records)
    parsed_dates = [parse_created_at(record["created_at"]) for record in records]
    valid_dates = [dt for dt in parsed_dates if dt is not None]
    latest_upload = max(valid_dates) if valid_dates else None

    skill_rows: list[dict[str, Any]] = []
    all_skill_names: list[str] = []

    for record in records:
        names = extract_skill_names(record["parsed"])
        all_skill_names.extend(names)

        skill_rows.append(
            {
                "resume_id": record["id"],
                "filename": record["filename"],
                "candidate": (
                    f"{record['parsed'].get('name') or record['filename']} (#{record['id']})"
                ),
                "skill_count": len(names),
                "education_count": len(record["parsed"].get("education") or []),
                "project_count": len(record["parsed"].get("projects") or []),
                "experience_count": len(record["parsed"].get("experience") or []),
                "created_at": record["created_at"],
            }
        )

    unique_skills = {
        name.casefold(): name for name in all_skill_names
    }
    total_unique_skills = len(unique_skills)
    average_skills = (
        len(all_skill_names) / total_resumes if total_resumes else 0.0
    )

    skill_frequency = Counter(name.casefold() for name in all_skill_names)
    top_skills = [
        {"skill": unique_skills[key], "count": count}
        for key, count in skill_frequency.most_common(15)
    ]

    upload_timeline = Counter()
    for record, parsed_dt in zip(records, parsed_dates):
        if parsed_dt is not None:
            upload_timeline[parsed_dt.date()] += 1
        else:
            upload_timeline[record["created_at"][:10]] += 1

    timeline_rows = [
        {"upload_date": str(day), "uploads": count}
        for day, count in sorted(upload_timeline.items(), key=lambda item: str(item[0]))
    ]

    # Job discovery metrics
    job_metrics = get_job_metrics()
    
    # Application analytics
    application_analytics = get_application_analytics()
    
    # Skill analytics
    skill_analytics = get_skill_analytics()
    
    # Career analytics
    career_analytics = get_career_analytics()
    
    # Phase 4 analytics
    phase4_analytics = get_phase4_analytics(records)

    return {
        "total_resumes": total_resumes,
        "latest_upload": latest_upload,
        "total_unique_skills": total_unique_skills,
        "average_skills": average_skills,
        "skill_rows": skill_rows,
        "top_skills": top_skills,
        "timeline_rows": timeline_rows,
        "job_metrics": job_metrics,
        "application_analytics": application_analytics,
        "skill_analytics": skill_analytics,
        "career_analytics": career_analytics,
        "phase4_analytics": phase4_analytics,
    }


def get_job_metrics() -> dict[str, Any]:
    """Get job discovery metrics from database using job aggregator."""
    try:
        # Use job aggregator to get real statistics
        aggregator = JobAggregator()
        stats = aggregator.get_job_statistics()
        
        # Get source statistics
        source_stats = aggregator.get_source_stats()
        
        # Get saved jobs count
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            saved_jobs_row = conn.execute("SELECT COUNT(*) as count FROM saved_jobs").fetchone()
            saved_jobs = saved_jobs_row["count"] if saved_jobs_row else 0
        
        # Calculate average salary from stats if available
        avg_salary = stats.get("average_salary", 0)
        
        # Get top source
        top_source = max(source_stats.items(), key=lambda x: x[1])[0] if source_stats else "N/A"
        
        return {
            "total_jobs": stats.get("total_jobs", 0),
            "saved_jobs": saved_jobs,
            "avg_match_score": stats.get("average_match_score", 0.0),
            "highest_match_score": stats.get("highest_match_score", 0.0),
            "lowest_match_score": stats.get("lowest_match_score", 0.0),
            "top_matching_role": stats.get("top_role", "N/A"),
            "average_salary": avg_salary,
            "top_source": top_source,
            "source_stats": source_stats,
        }
    except Exception as e:
        logger.error(f"Error getting job metrics: {e}")
        return {
            "total_jobs": 0,
            "saved_jobs": 0,
            "avg_match_score": 0.0,
            "highest_match_score": 0.0,
            "lowest_match_score": 0.0,
            "top_matching_role": "N/A",
            "average_salary": 0,
            "top_source": "N/A",
            "source_stats": {},
        }


def get_application_analytics() -> dict[str, Any]:
    """Get application analytics from workflow service."""
    try:
        workflow_service = ApplicationWorkflowService()
        return workflow_service.get_application_analytics()
    except Exception as e:
        logger.error(f"Error getting application analytics: {e}")
        return {
            "total_applications": 0,
            "status_breakdown": {},
            "top_companies": [],
            "offer_rate": 0.0,
            "application_rate": 0.0,
        }


def get_skill_analytics() -> dict[str, Any]:
    """Get skill analytics from job database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get top skills from job_skills table
            job_skills_data = conn.execute("""
                SELECT skill_name, COUNT(*) as count
                FROM job_skills
                GROUP BY skill_name
                ORDER BY count DESC
                LIMIT 10
            """).fetchall()
            
            most_requested = [
                {"skill": row["skill_name"], "count": row["count"]}
                for row in job_skills_data
            ]
            
            # Get top companies
            top_companies_data = conn.execute("""
                SELECT company, COUNT(*) as count
                FROM jobs
                GROUP BY company
                ORDER BY count DESC
                LIMIT 10
            """).fetchall()
            
            top_companies = [
                {"company": row["company"], "count": row["count"]}
                for row in top_companies_data
            ]
            
            # Get top locations
            top_locations_data = conn.execute("""
                SELECT location, COUNT(*) as count
                FROM jobs
                WHERE location IS NOT NULL
                GROUP BY location
                ORDER BY count DESC
                LIMIT 10
            """).fetchall()
            
            top_locations = [
                {"location": row["location"], "count": row["count"]}
                for row in top_locations_data
            ]
            
            return {
                "most_requested_skills": most_requested,
                "top_companies": top_companies,
                "top_locations": top_locations,
                "top_missing_skills": [],  # Would need match data
                "top_matched_skills": most_requested,  # Use requested as proxy
            }
    except Exception as e:
        logger.error(f"Error getting skill analytics: {e}")
        return {
            "top_missing_skills": [],
            "top_matched_skills": [],
            "most_requested_skills": [],
            "top_companies": [],
            "top_locations": [],
        }


def get_career_analytics() -> dict[str, Any]:
    """Get career analytics from career fits."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get career fit distribution
            career_fits_data = conn.execute("""
                SELECT career_name, score FROM career_fits
                ORDER BY score DESC
                LIMIT 10
            """).fetchall()
            
            career_distribution = [
                {"career": row["career_name"], "score": row["score"]}
                for row in career_fits_data
            ]
            
            # Get top career path
            top_career = career_fits_data[0]["career_name"] if career_fits_data else "N/A"
            
            return {
                "top_career_path": top_career,
                "career_fit_distribution": career_distribution,
                "learning_progress": 0.0,  # Placeholder for future implementation
            }
    except Exception as e:
        logger.error(f"Error getting career analytics: {e}")
        return {
            "top_career_path": "N/A",
            "career_fit_distribution": [],
            "learning_progress": 0.0,
        }


def get_phase4_analytics(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Get Phase 4 career intelligence analytics."""
    if not records:
        return {
            "skill_growth": [],
            "career_readiness_history": [],
            "missing_skills_trend": [],
            "top_career_path": "N/A",
        }
    
    # Initialize services
    career_fit_engine = CareerFitScoreEngine()
    career_predictor = CareerPathPredictor()
    skill_gap_engine = SkillGapEngine()
    
    # Sample job skills for gap analysis
    sample_job_skills = ["python", "javascript", "react", "django", "sql", "docker", "aws", "git"]
    
    skill_growth = []
    career_readiness_history = []
    missing_skills_trend = []
    
    for record in records:
        # Handle both old and new schema formats
        if "parsed" in record:
            parsed = record["parsed"]
        elif "parsed_json" in record and record["parsed_json"]:
            try:
                parsed = json.loads(record["parsed_json"])
            except (json.JSONDecodeError, TypeError):
                parsed = {}
        else:
            parsed = {}
        
        skills = [s.get("name", s) if isinstance(s, dict) else s for s in parsed.get("skills", [])]
        projects = parsed.get("projects", [])
        experience = parsed.get("experience", [])
        education = parsed.get("education", [])
        
        # Skill growth (skill count over time)
        skill_growth.append({
            "date": record["created_at"][:10],
            "skill_count": len(skills),
        })
        
        # Career readiness history
        fit_score = career_fit_engine.calculate_fit_score(
            skills=skills,
            projects=projects,
            experience=experience,
            education=education,
        )
        career_readiness_history.append({
            "date": record["created_at"][:10],
            "readiness_score": fit_score.overall_score,
            "readiness_level": fit_score.readiness_level,
        })
        
        # Missing skills trend
        skill_set = set([s.lower() for s in skills])
        gap_analysis = skill_gap_engine.analyze_gap(
            resume_skills=skill_set,
            job_skills=set(sample_job_skills),
        )
        missing_skills_trend.append({
            "date": record["created_at"][:10],
            "critical_gaps": len(gap_analysis.critical_gaps),
            "medium_gaps": len(gap_analysis.medium_gaps),
            "optional_gaps": len(gap_analysis.optional_gaps),
        })
    
    # Get top career path from latest resume
    # Handle both old and new schema formats
    if "parsed" in records[-1]:
        latest_parsed = records[-1]["parsed"]
    elif "parsed_json" in records[-1] and records[-1]["parsed_json"]:
        try:
            latest_parsed = json.loads(records[-1]["parsed_json"])
        except (json.JSONDecodeError, TypeError):
            latest_parsed = {}
    else:
        latest_parsed = {}
    
    latest_skills = [s.get("name", s) if isinstance(s, dict) else s for s in latest_parsed.get("skills", [])]
    latest_projects = latest_parsed.get("projects", [])
    latest_experience = latest_parsed.get("experience", [])
    
    career_prediction = career_predictor.predict_career_path(
        skills=latest_skills,
        projects=latest_projects,
        experience=latest_experience,
    )
    
    return {
        "skill_growth": skill_growth,
        "career_readiness_history": career_readiness_history,
        "missing_skills_trend": missing_skills_trend,
        "top_career_path": career_prediction.top_career_path,
    }


def format_datetime(value: datetime | None) -> str:
    if value is None:
        return "N/A"
    return value.strftime("%b %d, %Y %H:%M UTC")


def render_empty_state() -> None:
    st.markdown("---")
    empty_col1, empty_col2, empty_col3 = st.columns([1, 2, 1])

    with empty_col2:
        st.info(
            "No resume data found yet. Upload and parse resumes on the **Resume Parser** "
            "page to populate this dashboard.",
            icon="ℹ️",
        )
        st.markdown(
            """
            **What you'll see here once data is available**

            - Resume volume and latest upload activity
            - Unique skill coverage across candidates
            - Skill frequency and per-resume distribution charts
            """
        )


def render_overview_metrics(metrics: dict[str, Any]) -> None:
    st.markdown("### Overview")
    st.caption("Key metrics computed from parsed resume records and job discovery data.")

    col1, col2, col3, col4, col5, col6 = st.columns(6, gap="medium")

    col1.metric("Total Resumes", metrics["total_resumes"])
    col2.metric("Latest Upload", format_datetime(metrics["latest_upload"]))
    col3.metric("Unique Skills", metrics["total_unique_skills"])
    col4.metric("Avg Skills / Resume", f"{metrics['average_skills']:.1f}")
    col5.metric("Jobs Found", metrics["job_metrics"]["total_jobs"])
    col6.metric("Saved Jobs", metrics["job_metrics"]["saved_jobs"])


def render_charts(metrics: dict[str, Any]) -> None:
    st.markdown("### Insights")
    st.caption("Interactive charts built from the same parsed resume data.")

    skill_df = pd.DataFrame(metrics["skill_rows"])
    top_skills_df = pd.DataFrame(metrics["top_skills"])
    timeline_df = pd.DataFrame(metrics["timeline_rows"])

    chart_col1, chart_col2 = st.columns(2, gap="large")

    with chart_col1:
        st.markdown("##### Top Skills Across All Resumes")
        if top_skills_df.empty:
            st.caption("No skills found in parsed resumes.")
        else:
            fig_top = px.bar(
                top_skills_df,
                x="count",
                y="skill",
                orientation="h",
                color="count",
                color_continuous_scale="Blues",
                labels={"count": "Mentions", "skill": "Skill"},
            )
            fig_top.update_layout(
                height=400,
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis={"categoryorder": "total ascending"},
                margin={"l": 20, "r": 20, "t": 20, "b": 20},
            )
            st.plotly_chart(fig_top, width="stretch")

    with chart_col2:
        st.markdown("##### Upload Activity")
        if timeline_df.empty:
            st.caption("No upload timestamps available.")
        else:
            fig_timeline = px.bar(
                timeline_df,
                x="upload_date",
                y="uploads",
                text="uploads",
                color="uploads",
                color_continuous_scale="Teal",
                labels={"upload_date": "Date", "uploads": "Resumes Uploaded"},
            )
            fig_timeline.update_traces(textposition="outside")
            fig_timeline.update_layout(
                height=400,
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin={"l": 20, "r": 20, "t": 20, "b": 20},
            )
            st.plotly_chart(fig_timeline, width="stretch")

    st.markdown("")
    st.markdown("##### Skills per Resume")

    if skill_df.empty:
        st.caption("No resume records available for comparison.")
    else:
        fig_per_resume = px.bar(
            skill_df,
            x="candidate",
            y="skill_count",
            color="skill_count",
            color_continuous_scale="Purples",
            hover_data=["filename", "education_count", "project_count", "experience_count"],
            labels={
                "candidate": "Candidate",
                "skill_count": "Skills Listed",
            },
        )
        fig_per_resume.update_layout(
            height=400,
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis_tickangle=-25,
            margin={"l": 20, "r": 20, "t": 20, "b": 20},
        )
        st.plotly_chart(fig_per_resume, width="stretch")

    st.markdown("")
    st.markdown("##### Resume Section Coverage")

    if skill_df.empty:
        st.caption("No section coverage data available.")
    else:
        coverage_df = skill_df[
            ["candidate", "education_count", "project_count", "experience_count"]
        ].set_index("candidate")
        fig_coverage = px.imshow(
            coverage_df.T,
            aspect="auto",
            color_continuous_scale="Greens",
            labels={"x": "Candidate", "y": "Section", "color": "Items"},
        )
        fig_coverage.update_layout(
            height=300,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin={"l": 20, "r": 20, "t": 20, "b": 20},
        )
        st.plotly_chart(fig_coverage, width="stretch")


header_col, action_col = st.columns([5, 1])
with header_col:
    st.markdown(
        f'<p class="dashboard-caption">Database: <code>{DB_PATH}</code></p>',
        unsafe_allow_html=True,
    )
with action_col:
    if st.button("Refresh", help="Reload the latest data from SQLite", width="stretch"):
        load_resume_records.clear()
        st.rerun()

records = load_resume_records(str(DB_PATH), get_db_cache_key(DB_PATH))

if not records:
    render_empty_state()
else:
    metrics = build_analytics(records)

    render_overview_metrics(metrics)
    st.divider()
    
    # Job discovery metrics section
    st.markdown("### Job Discovery Metrics")
    st.caption("Insights from job search and matching activities.")
    
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    col1.metric("Total Jobs", metrics['job_metrics']['total_jobs'])
    col2.metric("Saved Jobs", metrics['job_metrics']['saved_jobs'])
    col3.metric("Top Source", metrics["job_metrics"]["top_source"])
    col4.metric("Avg Salary", f"₹{metrics['job_metrics']['average_salary']:,.0f}" if metrics['job_metrics']['average_salary'] > 0 else "N/A")
    
    st.divider()
    
    # Application Analytics Section
    st.markdown("### Application Analytics")
    st.caption("Track your job application progress and success rates.")
    
    app_analytics = metrics["application_analytics"]
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    col1.metric("Total Applications", app_analytics["total_applications"])
    col2.metric("Offer Rate", f"{app_analytics['offer_rate']}%")
    col3.metric("Application Rate", f"{app_analytics['application_rate']}%")
    col4.metric("Active", app_analytics["status_breakdown"].get("applied", 0) + app_analytics["status_breakdown"].get("interview", 0))
    
    # Application status breakdown chart
    if app_analytics["status_breakdown"]:
        st.write("**Application Status Distribution:**")
        status_df = pd.DataFrame([
            {"Status": status.title(), "Count": count}
            for status, count in app_analytics["status_breakdown"].items()
            if count > 0
        ])
        
        if not status_df.empty:
            fig_status = px.pie(
                status_df,
                values="Count",
                names="Status",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Blues,
            )
            fig_status.update_layout(
                height=400,
                showlegend=True,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f1f5f9"),
            )
            st.plotly_chart(fig_status, use_container_width=True)
    
    st.divider()
    
    # Skill Analytics Section
    st.markdown("### Skill Analytics")
    st.caption("Analyze your skill coverage and identify gaps.")
    
    skill_analytics = metrics["skill_analytics"]
    
    skill_col1, skill_col2 = st.columns(2, gap="large")
    
    with skill_col1:
        st.write("**Most Requested Skills:**")
        if skill_analytics["most_requested_skills"]:
            requested_df = pd.DataFrame(skill_analytics["most_requested_skills"])
            fig_requested = px.bar(
                requested_df,
                x="count",
                y="skill",
                orientation="h",
                color="count",
                color_continuous_scale="Blues",
                labels={"count": "Frequency", "skill": "Skill"},
            )
            fig_requested.update_layout(
                height=400,
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis={"categoryorder": "total ascending"},
                margin={"l": 20, "r": 20, "t": 20, "b": 20},
                font=dict(color="#f1f5f9"),
            )
            st.plotly_chart(fig_requested, use_container_width=True)
        else:
            st.info("No skill data available.")
    
    with skill_col2:
        st.write("**Top Companies Hiring:**")
        if skill_analytics["top_companies"]:
            companies_df = pd.DataFrame(skill_analytics["top_companies"])
            fig_companies = px.bar(
                companies_df,
                x="count",
                y="company",
                orientation="h",
                color="count",
                color_continuous_scale="Purples",
                labels={"count": "Job Count", "company": "Company"},
            )
            fig_companies.update_layout(
                height=400,
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis={"categoryorder": "total ascending"},
                margin={"l": 20, "r": 20, "t": 20, "b": 20},
                font=dict(color="#f1f5f9"),
            )
            st.plotly_chart(fig_companies, use_container_width=True)
        else:
            st.info("No company data available.")
    
    st.divider()
    
    # Location Analytics
    st.write("**Top Job Locations:**")
    if skill_analytics["top_locations"]:
        locations_df = pd.DataFrame(skill_analytics["top_locations"])
        fig_locations = px.bar(
            locations_df,
            x="count",
            y="location",
            orientation="h",
            color="count",
            color_continuous_scale="Teal",
            labels={"count": "Job Count", "location": "Location"},
        )
        fig_locations.update_layout(
            height=400,
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis={"categoryorder": "total ascending"},
            margin={"l": 20, "r": 20, "t": 20, "b": 20},
            font=dict(color="#f1f5f9"),
        )
        st.plotly_chart(fig_locations, use_container_width=True)
    else:
        st.info("No location data available.")
    
    st.divider()
    
    # Career Analytics Section
    st.markdown("### Career Analytics")
    st.caption("Your career fit analysis and recommendations.")
    
    career_analytics = metrics["career_analytics"]
    
    col1, col2, col3 = st.columns(3, gap="medium")
    col1.metric("Top Career Path", career_analytics["top_career_path"])
    col2.metric("Career Paths Analyzed", len(career_analytics["career_fit_distribution"]))
    col3.metric("Learning Progress", f"{career_analytics['learning_progress']:.0f}%")
    
    if career_analytics["career_fit_distribution"]:
        st.write("**Career Fit Distribution:**")
        career_df = pd.DataFrame(career_analytics["career_fit_distribution"])
        fig_career = px.bar(
            career_df,
            x="score",
            y="career",
            orientation="h",
            color="score",
            color_continuous_scale="Purples",
            labels={"score": "Fit Score (%)", "career": "Career Path"},
        )
        fig_career.update_layout(
            height=500,
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis={"categoryorder": "total ascending"},
            margin={"l": 20, "r": 20, "t": 20, "b": 20},
            font=dict(color="#f1f5f9"),
        )
        st.plotly_chart(fig_career, use_container_width=True)
    
    st.divider()
    
    # Phase 4 Career Intelligence Analytics Section
    st.markdown("### Career Intelligence Analytics")
    st.caption("Track your skill growth, career readiness, and learning progress over time.")
    
    phase4_analytics = metrics["phase4_analytics"]
    
    # Top Career Path
    col1, col2 = st.columns(2, gap="medium")
    col1.metric("Predicted Career Path", phase4_analytics["top_career_path"])
    col2.metric("Career Readiness", f"{phase4_analytics['career_readiness_history'][-1]['readiness_score']:.1f}%" if phase4_analytics["career_readiness_history"] else "N/A")
    
    st.divider()
    
    # Skill Growth Chart
    st.write("**Skill Growth Over Time:**")
    if phase4_analytics["skill_growth"]:
        growth_df = pd.DataFrame(phase4_analytics["skill_growth"])
        fig_growth = px.line(
            growth_df,
            x="date",
            y="skill_count",
            markers=True,
            title="Skills Acquired Over Time",
        )
        fig_growth.update_layout(
            height=400,
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f1f5f9"),
            xaxis_title="Date",
            yaxis_title="Number of Skills",
        )
        st.plotly_chart(fig_growth, use_container_width=True)
    else:
        st.info("No skill growth data available.")
    
    st.divider()
    
    # Career Readiness Chart
    st.write("**Career Readiness History:**")
    if phase4_analytics["career_readiness_history"]:
        readiness_df = pd.DataFrame(phase4_analytics["career_readiness_history"])
        fig_readiness = px.line(
            readiness_df,
            x="date",
            y="readiness_score",
            markers=True,
            title="Career Readiness Score Over Time",
        )
        fig_readiness.update_layout(
            height=400,
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f1f5f9"),
            xaxis_title="Date",
            yaxis_title="Readiness Score (%)",
        )
        st.plotly_chart(fig_readiness, use_container_width=True)
    else:
        st.info("No career readiness data available.")
    
    st.divider()
    
    # Missing Skills Trend Chart
    st.write("**Missing Skills Trend:**")
    if phase4_analytics["missing_skills_trend"]:
        trend_df = pd.DataFrame(phase4_analytics["missing_skills_trend"])
        fig_trend = px.line(
            trend_df,
            x="date",
            y=["critical_gaps", "medium_gaps", "optional_gaps"],
            markers=True,
            title="Skill Gaps Over Time",
        )
        fig_trend.update_layout(
            height=400,
            showlegend=True,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f1f5f9"),
            xaxis_title="Date",
            yaxis_title="Number of Gaps",
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No missing skills trend data available.")
    
    st.divider()
    render_charts(metrics)

    st.divider()
    with st.expander("Resume summary table", expanded=False):
        summary_df = pd.DataFrame(metrics["skill_rows"]).rename(
            columns={
                "candidate": "Name",
                "filename": "Filename",
                "skill_count": "Skills",
                "education_count": "Education Items",
                "project_count": "Projects",
                "experience_count": "Experience Items",
                "created_at": "Uploaded At",
            }
        )
        st.dataframe(
            summary_df[
                [
                    "Name",
                    "Filename",
                    "Skills",
                    "Education Items",
                    "Projects",
                    "Experience Items",
                    "Uploaded At",
                ]
            ],
            width="stretch",
            hide_index=True,
        )
