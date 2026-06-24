"""
Application Workflow Service

Manages application workflow connecting Job Discovery with Application Tracker.
Provides status flow management, Kanban board support, and analytics integration.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.utils import get_env

logger = logging.getLogger(__name__)

DB_PATH = Path(get_env("DATABASE_PATH", "data/hireflow.db"))


class ApplicationStatus(Enum):
    """Application status enum with workflow order."""
    SAVED = "saved"
    APPLIED = "applied"
    ASSESSMENT = "assessment"
    INTERVIEW = "interview"
    OFFER = "offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

    @classmethod
    def get_workflow_order(cls) -> List["ApplicationStatus"]:
        """Return the workflow order."""
        return [
            cls.SAVED,
            cls.APPLIED,
            cls.ASSESSMENT,
            cls.INTERVIEW,
            cls.OFFER,
            cls.ACCEPTED,
        ]

    @classmethod
    def get_next_status(cls, current: str) -> Optional[str]:
        """Get the next status in the workflow."""
        try:
            current_status = cls(current.lower())
            order = cls.get_workflow_order()
            if current_status in order:
                idx = order.index(current_status)
                if idx + 1 < len(order):
                    return order[idx + 1].value
        except ValueError:
            pass
        return None

    @classmethod
    def get_previous_status(cls, current: str) -> Optional[str]:
        """Get the previous status in the workflow."""
        try:
            current_status = cls(current.lower())
            order = cls.get_workflow_order()
            if current_status in order:
                idx = order.index(current_status)
                if idx > 0:
                    return order[idx - 1].value
        except ValueError:
            pass
        return None


@dataclass
class Application:
    """Application data model."""
    
    id: Optional[int]
    job_id: str
    job_title: str
    company: str
    location: str
    salary: str
    source: str
    source_url: str
    status: str
    notes: str
    applied_date: Optional[str]
    created_at: str
    updated_at: str


@dataclass
class KanbanColumn:
    """Kanban column data."""
    
    status: str
    applications: List[Application]
    count: int


class ApplicationWorkflowService:
    """Service for managing application workflow and status transitions."""
    
    def __init__(self, db_path: Path = DB_PATH) -> None:
        """Initialize application workflow service."""
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self) -> None:
        """Ensure application tables exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    job_id TEXT NOT NULL,
                    job_title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    salary TEXT,
                    source TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'saved',
                    notes TEXT,
                    applied_date TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
                """
            )
            conn.commit()
    
    def create_application(
        self,
        job_id: str,
        job_title: str,
        company: str,
        location: str,
        salary: str,
        source: str,
        source_url: str,
        user_id: Optional[int] = None,
        status: str = "saved",
        notes: str = "",
    ) -> int:
        """
        Create a new application.
        
        Args:
            job_id: External job ID
            job_title: Job title
            company: Company name
            location: Job location
            salary: Salary information
            source: Job source
            source_url: Job URL
            user_id: User ID (optional)
            status: Initial status
            notes: Initial notes
            
        Returns:
            Application ID
        """
        created_at = datetime.utcnow().isoformat()
        updated_at = created_at
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO applications (
                    user_id, job_id, job_title, company, location, salary,
                    source, source_url, status, notes, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id, job_id, job_title, company, location, salary,
                    source, source_url, status, notes, created_at, updated_at,
                ),
            )
            conn.commit()
            return cursor.lastrowid
    
    def update_application_status(
        self,
        application_id: int,
        new_status: str,
        notes: Optional[str] = None,
    ) -> bool:
        """
        Update application status.
        
        Args:
            application_id: Application ID
            new_status: New status
            notes: Optional notes to add
            
        Returns:
            True if successful
        """
        updated_at = datetime.utcnow().isoformat()
        
        if notes:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE applications
                    SET status = ?, notes = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (new_status, notes, updated_at, application_id),
                )
                conn.commit()
        else:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE applications
                    SET status = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (new_status, updated_at, application_id),
                )
                conn.commit()
        
        return True
    
    def advance_application_status(
        self,
        application_id: int,
        notes: Optional[str] = None,
    ) -> Optional[str]:
        """
        Advance application to next status in workflow.
        
        Args:
            application_id: Application ID
            notes: Optional notes
            
        Returns:
            New status if successful, None otherwise
        """
        application = self.get_application(application_id)
        if not application:
            return None
        
        next_status = ApplicationStatus.get_next_status(application.status)
        if next_status:
            self.update_application_status(application_id, next_status, notes)
            return next_status
        return None
    
    def regress_application_status(
        self,
        application_id: int,
        notes: Optional[str] = None,
    ) -> Optional[str]:
        """
        Regress application to previous status in workflow.
        
        Args:
            application_id: Application ID
            notes: Optional notes
            
        Returns:
            New status if successful, None otherwise
        """
        application = self.get_application(application_id)
        if not application:
            return None
        
        previous_status = ApplicationStatus.get_previous_status(application.status)
        if previous_status:
            self.update_application_status(application_id, previous_status, notes)
            return previous_status
        return None
    
    def get_application(self, application_id: int) -> Optional[Application]:
        """Get application by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM applications WHERE id = ?",
                (application_id,),
            ).fetchone()
            
            if row:
                return Application(
                    id=row["id"],
                    job_id=row["job_id"],
                    job_title=row["job_title"],
                    company=row["company"],
                    location=row["location"],
                    salary=row["salary"],
                    source=row["source"],
                    source_url=row["source_url"],
                    status=row["status"],
                    notes=row["notes"] or "",
                    applied_date=row["applied_date"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
        return None
    
    def get_all_applications(
        self,
        user_id: Optional[int] = None,
        status_filter: Optional[str] = None,
    ) -> List[Application]:
        """
        Get all applications with optional filters.
        
        Args:
            user_id: Filter by user ID
            status_filter: Filter by status
            
        Returns:
            List of applications
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            query = "SELECT * FROM applications"
            params = []
            
            conditions = []
            if user_id is not None:
                conditions.append("user_id = ?")
                params.append(user_id)
            
            if status_filter:
                conditions.append("status = ?")
                params.append(status_filter)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY created_at DESC"
            
            rows = conn.execute(query, params).fetchall()
            
            applications = []
            for row in rows:
                applications.append(Application(
                    id=row["id"],
                    job_id=row["job_id"],
                    job_title=row["job_title"],
                    company=row["company"],
                    location=row["location"],
                    salary=row["salary"],
                    source=row["source"],
                    source_url=row["source_url"],
                    status=row["status"],
                    notes=row["notes"] or "",
                    applied_date=row["applied_date"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                ))
            
            return applications
    
    def get_kanban_board(
        self,
        user_id: Optional[int] = None,
    ) -> Dict[str, KanbanColumn]:
        """
        Get applications organized as Kanban board columns.
        
        Args:
            user_id: Filter by user ID
            
        Returns:
            Dictionary mapping status to KanbanColumn
        """
        all_applications = self.get_all_applications(user_id)
        
        # Group by status
        status_groups: Dict[str, List[Application]] = {}
        for status in ApplicationStatus:
            status_groups[status.value] = []
        
        for app in all_applications:
            if app.status in status_groups:
                status_groups[app.status].append(app)
        
        # Create Kanban columns
        kanban_board = {}
        for status, apps in status_groups.items():
            kanban_board[status] = KanbanColumn(
                status=status,
                applications=apps,
                count=len(apps),
            )
        
        return kanban_board
    
    def get_application_analytics(self) -> Dict[str, Any]:
        """
        Get application analytics for dashboard.
        
        Returns:
            Analytics data
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Total applications
            total_row = conn.execute("SELECT COUNT(*) as count FROM applications").fetchone()
            total = total_row["count"] if total_row else 0
            
            # Status breakdown
            status_breakdown = {}
            for status in ApplicationStatus:
                status_row = conn.execute(
                    "SELECT COUNT(*) as count FROM applications WHERE status = ?",
                    (status.value,),
                ).fetchone()
                status_breakdown[status.value] = status_row["count"] if status_row else 0
            
            # Applications by company
            company_row = conn.execute("""
                SELECT company, COUNT(*) as count
                FROM applications
                GROUP BY company
                ORDER BY count DESC
                LIMIT 10
            """).fetchall()
            
            top_companies = [
                {"company": row["company"], "count": row["count"]}
                for row in company_row
            ]
            
            # Calculate offer rate
            offers = status_breakdown.get("offer", 0) + status_breakdown.get("accepted", 0)
            offer_rate = (offers / total * 100) if total > 0 else 0
            
            # Calculate application rate (saved -> applied)
            saved = status_breakdown.get("saved", 0)
            applied = status_breakdown.get("applied", 0)
            application_rate = (applied / (saved + applied) * 100) if (saved + applied) > 0 else 0
            
            return {
                "total_applications": total,
                "status_breakdown": status_breakdown,
                "top_companies": top_companies,
                "offer_rate": round(offer_rate, 1),
                "application_rate": round(application_rate, 1),
            }
    
    def delete_application(self, application_id: int) -> bool:
        """Delete an application."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM applications WHERE id = ?",
                (application_id,),
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def add_application_note(self, application_id: int, note: str) -> bool:
        """Add a note to an application."""
        application = self.get_application(application_id)
        if not application:
            return False
        
        updated_notes = application.notes + "\n\n" + note if application.notes else note
        return self.update_application_status(application_id, application.status, updated_notes)
