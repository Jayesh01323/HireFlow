"""
Application Tracker Page

Streamlit page for tracking job applications through the hiring process.
Provides status updates, Kanban board view, and analytics.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.services.application_workflow_service import ApplicationWorkflowService, ApplicationStatus
from src.utils import get_env, load_env

load_env()

DB_PATH = Path(get_env("DATABASE_PATH", "data/hireflow.db"))

st.set_page_config(page_title="Application Tracker", page_icon="📋", layout="wide")

# Custom CSS for dark theme
st.markdown(
    """
    <style>
        .stApp {
            background-color: #0f172a;
        }
        .kanban-column {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border: 1px solid #475569;
            border-radius: 12px;
            padding: 1rem;
            min-height: 400px;
        }
        .application-card {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            transition: all 0.2s ease;
        }
        .application-card:hover {
            border-color: #3b82f6;
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
        }
        .status-saved { border-left: 4px solid #64748b; }
        .status-applied { border-left: 4px solid #3b82f6; }
        .status-assessment { border-left: 4px solid #f59e0b; }
        .status-interview { border-left: 4px solid #8b5cf6; }
        .status-offer { border-left: 4px solid #10b981; }
        .status-accepted { border-left: 4px solid #059669; }
        .status-rejected { border-left: 4px solid #ef4444; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📋 Application Tracker")
st.markdown("Track your job applications through the hiring pipeline.")

# Initialize application workflow service
@st.cache_resource
def get_application_workflow_service():
    return ApplicationWorkflowService()

workflow_service = get_application_workflow_service()

# View toggle
view_mode = st.radio(
    "View Mode",
    ["Kanban Board", "List View"],
    horizontal=True,
    label_visibility="collapsed",
)

st.divider()

if view_mode == "Kanban Board":
    st.subheader("📊 Kanban Board")
    
    # Get Kanban board data
    kanban_board = workflow_service.get_kanban_board()
    
    # Display columns
    cols = st.columns(6)
    
    workflow_order = ApplicationStatus.get_workflow_order()
    
    for idx, (col, status) in enumerate(zip(cols, workflow_order)):
        with col:
            column_data = kanban_board.get(status.value)
            if column_data:
                st.markdown(
                    f"""
                    <div class="kanban-column">
                        <h4 style="margin: 0 0 1rem 0; color: #f1f5f9;">
                            {status.value.title()} ({column_data.count})
                        </h4>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                for app in column_data.applications:
                    st.markdown(
                        f"""
                        <div class="application-card status-{status.value}">
                            <h5 style="margin: 0 0 0.5rem 0; color: #f1f5f9;">{app.job_title}</h5>
                            <p style="margin: 0; color: #94a3b8; font-size: 0.85rem;">{app.company}</p>
                            <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.75rem;">{app.location}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    
                    # Action buttons for each application
                    action_col1, action_col2, action_col3 = st.columns(3)
                    with action_col1:
                        if st.button("→", key=f"next_{app.id}", help="Advance status"):
                            new_status = workflow_service.advance_application_status(app.id)
                            if new_status:
                                st.success(f"Moved to {new_status.title()}")
                                st.rerun()
                    
                    with action_col2:
                        if st.button("←", key=f"prev_{app.id}", help="Regress status"):
                            new_status = workflow_service.regress_application_status(app.id)
                            if new_status:
                                st.success(f"Moved to {new_status.title()}")
                                st.rerun()
                    
                    with action_col3:
                        if st.button("🗑️", key=f"del_{app.id}", help="Delete"):
                            workflow_service.delete_application(app.id)
                            st.rerun()
            else:
                st.markdown(
                    f"""
                    <div class="kanban-column">
                        <h4 style="margin: 0 0 1rem 0; color: #f1f5f9;">
                            {status.value.title()} (0)
                        </h4>
                        <p style="color: #64748b; font-size: 0.85rem;">No applications</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

else:  # List View
    st.subheader("📋 Application List")
    
    # Filters
    col1, col2 = st.columns([2, 1])
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All"] + [status.value.title() for status in ApplicationStatus],
        )
    with col2:
        st.write("")  # Spacer
    
    # Get applications
    filter_status = status_filter.lower() if status_filter != "All" else None
    applications = workflow_service.get_all_applications(status_filter=filter_status)
    
    if applications:
        for app in applications:
            with st.expander(f"{app.job_title} @ {app.company}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**📍 Location:**", app.location)
                    st.write("**💰 Salary:**", app.salary)
                    st.write("**📅 Applied:**", app.applied_date or "N/A")
                
                with col2:
                    st.write("**🏢 Source:**", app.source)
                    st.write("**📊 Status:**", app.status.title())
                    st.write("**📝 Notes:**", app.notes or "None")
                
                with col3:
                    # Status management
                    st.write("**Actions:**")
                    
                    next_status = ApplicationStatus.get_next_status(app.status)
                    if next_status:
                        if st.button(f"Advance to {next_status.title()}", key=f"advance_{app.id}"):
                            workflow_service.advance_application_status(app.id)
                            st.rerun()
                    
                    prev_status = ApplicationStatus.get_previous_status(app.status)
                    if prev_status:
                        if st.button(f"Regress to {prev_status.title()}", key=f"regress_{app.id}"):
                            workflow_service.regress_application_status(app.id)
                            st.rerun()
                    
                    if st.button("Delete Application", key=f"delete_{app.id}"):
                        workflow_service.delete_application(app.id)
                        st.rerun()
                
                # Add note
                st.divider()
                new_note = st.text_input("Add Note", key=f"note_{app.id}")
                if st.button("Add Note", key=f"add_note_{app.id}"):
                    if new_note:
                        workflow_service.add_application_note(app.id, new_note)
                        st.success("Note added!")
                        st.rerun()
            
            st.divider()
    else:
        st.info("No applications found. Start by applying to jobs from the Job Discovery page.")

# Analytics Section
st.divider()
st.subheader("📈 Application Analytics")

analytics = workflow_service.get_application_analytics()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Applications", analytics["total_applications"])
col2.metric("Offer Rate", f"{analytics['offer_rate']}%")
col3.metric("Application Rate", f"{analytics['application_rate']}%")
col4.metric("Active Applications", analytics["status_breakdown"].get("applied", 0) + analytics["status_breakdown"].get("interview", 0))

st.divider()

# Status breakdown
st.write("**Status Breakdown:**")
status_breakdown = analytics["status_breakdown"]
if status_breakdown:
    for status, count in status_breakdown.items():
        if count > 0:
            st.write(f"• {status.title()}: {count}")
else:
    st.write("No status data available.")

# Top companies
if analytics["top_companies"]:
    st.divider()
    st.write("**Top Companies:**")
    for company_data in analytics["top_companies"]:
        st.write(f"• {company_data['company']}: {company_data['count']} applications")

# Footer
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.8rem;">
        <p>Powered by HireFlow AI • Application Workflow Integration</p>
    </div>
    """,
    unsafe_allow_html=True,
)
