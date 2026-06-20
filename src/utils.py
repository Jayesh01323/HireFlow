"""
Utilities Module

Shared helper functions for file handling, data formatting,
environment configuration, and common operations across the app.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_env() -> None:
    """Load environment variables from .env file."""
    load_dotenv()


def get_env(key: str, default: str = "") -> str:
    """Retrieve an environment variable with an optional default."""
    return os.getenv(key, default)


def ensure_dir(path: Path) -> Path:
    """Create a directory if it does not exist and return the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path
