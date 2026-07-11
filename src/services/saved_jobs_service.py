"""
Saved Jobs Service

Manages saving and retrieving saved jobs for users.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.utils import get_env, load_env

load_env()

DB_PATH = Path(get_env("DATABASE_PATH", "data/hireflow.db"))

logger = logging.getLogger(__name__)


class SavedJobsService:
    """Service for managing saved jobs."""
    
    def __init__(self, db_path: Optional[Path] = None) -> None:
        """Initialize saved jobs service."""
        self.db_path = db_path or DB_PATH
        self._ensure_table_exists()
    
    def _ensure_table_exists(self) -> None:
        """Ensure saved_jobs table exists in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS saved_jobs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        job_id TEXT NOT NULL,
                        job_title TEXT NOT NULL,
                        company TEXT NOT NULL,
                        location TEXT,
                        salary TEXT,
                        work_mode TEXT,
                        source TEXT NOT NULL,
                        source_url TEXT NOT NULL,
                        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_saved_jobs_user_id 
                    ON saved_jobs(user_id)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_saved_jobs_job_id 
                    ON saved_jobs(job_id)
                """)
                conn.commit()
                logger.info("Ensured saved_jobs table exists")
        except Exception as e:
            logger.error(f"Error creating saved_jobs table: {e}")
    
    def save_job(self, job: Dict[str, Any], user_id: Optional[int] = None) -> bool:
        """Save a job for a user.
        
        Args:
            job: Dictionary with job_id, job_title, company, location, salary, work_mode, source, source_url
            user_id: Optional user ID
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                job_id = job.get("job_id", "")
                # Check if job is already saved
                cursor = conn.execute(
                    "SELECT id FROM saved_jobs WHERE job_id = ? AND (user_id = ? OR user_id IS NULL)",
                    (job_id, user_id)
                )
                if cursor.fetchone():
                    logger.info(f"Job {job_id} already saved")
                    return False
                
                # Save the job
                conn.execute(
                    """
                    INSERT INTO saved_jobs 
                    (user_id, job_id, job_title, company, location, salary, work_mode, source, source_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        job_id,
                        job.get("job_title", "Unknown"),
                        job.get("company", "Unknown"),
                        job.get("location"),
                        job.get("salary"),
                        job.get("work_mode"),
                        job.get("source", ""),
                        job.get("source_url", ""),
                    )
                )
                conn.commit()
                logger.info(f"Saved job {job_id} for user {user_id}")
                return True
        except Exception as e:
            logger.error(f"Error saving job: {e}")
            return False
    
    def remove_saved_job(self, job_id: str, user_id: Optional[int] = None) -> bool:
        """Remove a saved job for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM saved_jobs WHERE job_id = ? AND (user_id = ? OR user_id IS NULL)",
                    (job_id, user_id)
                )
                conn.commit()
                removed = cursor.rowcount > 0
                if removed:
                    logger.info(f"Removed saved job {job_id} for user {user_id}")
                return removed
        except Exception as e:
            logger.error(f"Error removing saved job: {e}")
            return False
    
    def get_saved_jobs(self, user_id: Optional[int] = None) -> List[dict]:
        """Get all saved jobs for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                if user_id:
                    cursor = conn.execute(
                        "SELECT * FROM saved_jobs WHERE user_id = ? ORDER BY saved_at DESC",
                        (user_id,)
                    )
                else:
                    cursor = conn.execute(
                        "SELECT * FROM saved_jobs ORDER BY saved_at DESC"
                    )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting saved jobs: {e}")
            return []
    
    def is_job_saved(self, job_id: str, user_id: Optional[int] = None) -> bool:
        """Check if a job is saved for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT id FROM saved_jobs WHERE job_id = ? AND (user_id = ? OR user_id IS NULL)",
                    (job_id, user_id)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking if job is saved: {e}")
            return False
    
    def get_saved_job_count(self, user_id: Optional[int] = None) -> int:
        """Get count of saved jobs for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if user_id:
                    cursor = conn.execute(
                        "SELECT COUNT(*) FROM saved_jobs WHERE user_id = ?",
                        (user_id,)
                    )
                else:
                    cursor = conn.execute("SELECT COUNT(*) FROM saved_jobs")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting saved job count: {e}")
            return 0