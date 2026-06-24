"""
Database Package

Contains database models, repositories, and migrations for HireFlow.
Provides backward compatibility with legacy database functions.
"""

from src.database.models import Job, JobMatch, Resume, Application, Alert, SavedJob
from src.database.job_repository import JobRepository

# Backward compatibility: import legacy functions
from src.database_legacy import (
    get_connection,
    init_db,
    get_all_resumes,
    save_resume,
    delete_resume,
)

__all__ = [
    "Job",
    "JobMatch", 
    "Resume",
    "Application",
    "Alert",
    "SavedJob",
    "JobRepository",
    # Legacy functions for backward compatibility
    "get_connection",
    "init_db",
    "get_all_resumes",
    "save_resume",
    "delete_resume",
]
