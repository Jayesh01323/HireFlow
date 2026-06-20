"""
Database Module

Handles SQLite database connections, schema initialization,
and CRUD operations for resumes, jobs, and user data.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.schemas import Resume
from src.utils import get_env

DEFAULT_DB_PATH = Path(get_env("DATABASE_PATH", "data/hireflow.db"))


def get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Return a SQLite connection to the application database."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Initialize database tables."""
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                raw_text TEXT NOT NULL,
                parsed_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()


def save_resume(
    filename: str,
    raw_text: str,
    parsed: Resume,
    db_path: Path = DEFAULT_DB_PATH,
) -> int:
    """Persist raw resume text and validated parsed JSON to SQLite."""
    created_at = datetime.now(timezone.utc).isoformat()
    parsed_json = parsed.model_dump_json()

    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO resumes (filename, raw_text, parsed_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (filename, raw_text, parsed_json, created_at),
        )
        conn.commit()
        resume_id = cursor.lastrowid

    if resume_id is None:
        raise RuntimeError("Failed to save resume record.")

    return resume_id


def get_resume(resume_id: int, db_path: Path = DEFAULT_DB_PATH) -> dict[str, Any] | None:
    """Fetch a single resume record by ID."""
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM resumes WHERE id = ?",
            (resume_id,),
        ).fetchone()

    if row is None:
        return None

    return _row_to_dict(row)


def get_all_resumes(db_path: Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    """Return all stored resume records, newest first."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM resumes ORDER BY id DESC"
        ).fetchall()

    return [_row_to_dict(row) for row in rows]


def delete_resume(resume_id: int, db_path: Path = DEFAULT_DB_PATH) -> bool:
    """Delete a resume record. Returns True if a row was removed."""
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "DELETE FROM resumes WHERE id = ?",
            (resume_id,),
        )
        conn.commit()
        return cursor.rowcount > 0


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    parsed_data = json.loads(row["parsed_json"])
    return {
        "id": row["id"],
        "filename": row["filename"],
        "raw_text": row["raw_text"],
        "parsed_json": row["parsed_json"],
        "parsed": parsed_data,
        "created_at": row["created_at"],
    }
