"""
Base Job Actor Module

Abstract base class for all job data acquisition actors.
Defines the interface that all job actors must implement.

Actors are self-contained units that encapsulate the complete logic
for extracting jobs from a single source. They are designed to be
independently removable without affecting the rest of HireFlow.

Architecture:
    BaseJobActor (abstract)
        ├── WellfoundActor
        ├── FutureActor1
        └── FutureActor2

Each actor:
    1. Accepts dynamic user input (keyword, location, remote, etc.)
    2. Extracts job data from its source
    3. Returns NormalizedJob objects
    4. Logs all operations with clear error messages
    5. Detects and reports CAPTCHA/access blocks
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.jobs.schemas import NormalizedJob

logger = logging.getLogger(__name__)


class ActorError(Exception):
    """Base exception for actor errors."""
    pass


class ActorConfigurationError(ActorError):
    """Raised when actor is misconfigured."""
    pass


class ActorSourceUnavailableError(ActorError):
    """Raised when the source site cannot be accessed."""
    pass


class ActorCAPTCHAError(ActorSourceUnavailableError):
    """Raised when CAPTCHA or other access protection is detected."""
    pass


class ActorExtractionError(ActorError):
    """Raised when job extraction fails."""
    pass


class BaseJobActor(ABC):
    """Abstract base class for job data acquisition actors.

    Each actor encapsulates the complete logic for extracting jobs
    from a single source. Actors are self-contained and independently
    removable.
    """

    def __init__(self, source_name: str) -> None:
        """Initialize base job actor.

        Args:
            source_name: Name of the job source (e.g., 'wellfound')
        """
        self.source_name = source_name
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the actor (browser, API client, etc.).

        Must be called before search_jobs.

        Raises:
            ActorConfigurationError: If initialization fails
        """
        pass

    @abstractmethod
    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        limit: int = 50,
    ) -> List[NormalizedJob]:
        """Search for jobs from this source.

        Args:
            query: Job search query (e.g., 'software engineer')
            location: Job location filter
            remote: Filter for remote jobs only
            experience: Experience level filter (entry, mid, senior)
            salary_min: Minimum salary filter
            limit: Maximum number of jobs to return

        Returns:
            List of NormalizedJob objects

        Raises:
            ActorCAPTCHAError: If CAPTCHA blocks access
            ActorSourceUnavailableError: If source cannot be reached
            ActorExtractionError: If extraction fails
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources (browser, connections, etc.).

        Must be called after search_jobs to release resources.
        """
        pass

    @abstractmethod
    def get_source_status(self) -> Dict[str, Any]:
        """Get the current status of this source.

        Returns:
            Dictionary with status information:
            - available: bool
            - message: str (reason if unavailable)
            - last_check: str (ISO timestamp)
        """
        pass

    def _make_external_id(self, url: str) -> str:
        """Generate external ID from job URL.

        Args:
            url: Job URL

        Returns:
            External ID string
        """
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:16]

    def _normalize_posted_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Normalize a posted date string to datetime.

        Args:
            date_str: Date string from source

        Returns:
            Datetime object or None
        """
        if not date_str:
            return None

        try:
            # Try ISO format
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            pass

        try:
            # Try common formats
            from dateutil import parser as dateparser
            return dateparser.parse(date_str)
        except (ImportError, ValueError, TypeError):
            pass

        return None

    def _now_utc(self) -> datetime:
        """Get current UTC datetime (naive for DB compatibility).

        Returns:
            Current UTC datetime
        """
        return datetime.now(timezone.utc).replace(tzinfo=None)