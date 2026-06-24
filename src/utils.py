"""
Utilities Module

Shared helper functions for file handling, data formatting,
environment configuration, and common operations across the app.
"""

import json
import sqlite3
from pathlib import Path
from typing import Optional

import os
from dotenv import load_dotenv


def load_env() -> None:
    """Load environment variables from .env file."""
    load_dotenv()


def get_env(key: str, default: str = "") -> str:
    """Retrieve an environment variable with an optional default."""
    return os.getenv(key, default)




def get_latest_resume(db_path: Path) -> Optional[dict]:
    """
    Load the latest resume from the database.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        Parsed resume data as a dictionary, or None if no resume found
    """
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            # Check if parsed_json column exists
            cursor = conn.execute("PRAGMA table_info(resumes)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if "parsed_json" in columns:
                query = "SELECT parsed_json FROM resumes ORDER BY created_at DESC LIMIT 1"
            else:
                # Fallback for schema without parsed_json
                return None
            
            row = conn.execute(query).fetchone()
            if row and row["parsed_json"]:
                return json.loads(row["parsed_json"])
    except Exception:
        pass
    return None
def ensure_dir(path: Path) -> Path:
    """Create a directory if it does not exist and return the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path
