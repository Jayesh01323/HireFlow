"""
Analytics Dashboard Page

Streamlit page for visualizing career data, skill trends,
and job match analytics using Plotly charts.
"""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from src.utils import get_env, load_env

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
        rows = conn.execute(
            """
            SELECT id, filename, parsed_json, created_at
            FROM resumes
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()

    records: list[dict[str, Any]] = []
    for row in rows:
        try:
            parsed = json.loads(row["parsed_json"])
        except json.JSONDecodeError:
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

    return {
        "total_resumes": total_resumes,
        "latest_upload": latest_upload,
        "total_unique_skills": total_unique_skills,
        "average_skills": average_skills,
        "skill_rows": skill_rows,
        "top_skills": top_skills,
        "timeline_rows": timeline_rows,
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
    st.caption("Key metrics computed from parsed resume records in SQLite.")

    col1, col2, col3, col4 = st.columns(4, gap="medium")

    col1.metric("Total Resumes", metrics["total_resumes"])
    col2.metric("Latest Upload", format_datetime(metrics["latest_upload"]))
    col3.metric("Unique Skills", metrics["total_unique_skills"])
    col4.metric("Avg Skills / Resume", f"{metrics['average_skills']:.1f}")


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
