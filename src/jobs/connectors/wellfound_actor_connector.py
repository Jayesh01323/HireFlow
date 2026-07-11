"""
Wellfound Actor Connector

Minimal integration layer between the WellfoundActor and the existing
HireFlow connector architecture.

This is the ONLY file that connects the actor to the rest of HireFlow.
To completely remove the Wellfound actor:
1. Delete this file
2. Delete src/jobs/actors/wellfound_actor.py
3. Remove the import from src/jobs/actors/__init__.py
4. Remove the registration from src/jobs/aggregator.py (if added)

No other files need to be modified.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from src.jobs.actors.wellfound_actor import WellfoundActor
from src.jobs.connectors.base import BaseJobConnector
from src.jobs.schemas import JobPosting, NormalizedJob

logger = logging.getLogger(__name__)


class WellfoundActorConnector(BaseJobConnector):
    """Minimal connector that wraps WellfoundActor for HireFlow integration.

    This connector translates between the existing BaseJobConnector interface
    and the new WellfoundActor. It handles:
    - Actor lifecycle (initialize, search, cleanup)
    - Error translation (ActorError → connector logging)
    - JobPosting → NormalizedJob conversion (actor already returns NormalizedJob)

    To remove Wellfound support entirely:
    1. Delete this file
    2. Delete src/jobs/actors/ directory
    3. Remove "wellfound" from aggregator connectors
    """

    def __init__(self) -> None:
        """Initialize the Wellfound actor connector."""
        super().__init__("wellfound")
        self._actor: Optional[WellfoundActor] = None
        self._initialized = False

    def _get_actor(self) -> WellfoundActor:
        """Get or create the WellfoundActor instance.

        Returns:
            WellfoundActor instance
        """
        if self._actor is None:
            self._actor = WellfoundActor()
        return self._actor

    def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        limit: int = 50,
    ) -> List[JobPosting]:
        """Search for jobs on Wellfound via the actor.

        This is a synchronous wrapper that manages the async actor lifecycle.

        Args:
            query: Job search query
            location: Job location filter
            remote: Filter for remote jobs
            experience: Experience level filter
            salary_min: Minimum salary filter
            limit: Maximum number of jobs to return

        Returns:
            List of JobPosting objects (empty if CAPTCHA blocks access)
        """
        logger.info(f"WellfoundActorConnector: Searching | query='{query}' location='{location}'")

        try:
            jobs = asyncio.run(self._search_async(
                query=query,
                location=location,
                remote=remote,
                experience=experience,
                salary_min=salary_min,
                limit=limit,
            ))
            return jobs
        except Exception as e:
            logger.error(f"WellfoundActorConnector: Search failed: {type(e).__name__}: {e}")
            return []

    async def _search_async(
        self,
        query: str,
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        limit: int = 50,
    ) -> List[JobPosting]:
        """Async implementation of job search.

        Args:
            query: Job search query
            location: Job location filter
            remote: Filter for remote jobs
            experience: Experience level filter
            salary_min: Minimum salary filter
            limit: Maximum number of jobs to return

        Returns:
            List of JobPosting objects
        """
        actor = self._get_actor()

        try:
            # Initialize actor
            await actor.initialize()

            # Search for jobs
            normalized_jobs = await actor.search_jobs(
                query=query,
                location=location,
                remote=remote,
                experience=experience,
                salary_min=salary_min,
                limit=limit,
            )

            # Convert NormalizedJob → JobPosting for pipeline compatibility
            job_postings = [self._normalized_to_posting(job) for job in normalized_jobs]

            logger.info(f"WellfoundActorConnector: Returning {len(job_postings)} jobs")
            return job_postings

        except Exception as e:
            logger.error(f"WellfoundActorConnector: Actor error: {type(e).__name__}: {e}")
            return []
        finally:
            # Always clean up
            await actor.cleanup()

    def get_job_details(self, job_url: str) -> Optional[JobPosting]:
        """Get detailed information for a specific job.

        Not implemented for Wellfound due to CAPTCHA restrictions.

        Args:
            job_url: URL of the job posting

        Returns:
            None (not supported)
        """
        logger.warning(f"WellfoundActorConnector: get_job_details not supported for {job_url}")
        return None

    def get_source_status(self) -> Dict[str, Any]:
        """Get the current status of Wellfound as a source.

        Returns:
            Dictionary with status information
        """
        actor = self._get_actor()
        return actor.get_source_status()

    @staticmethod
    def _normalized_to_posting(job: NormalizedJob) -> JobPosting:
        """Convert a NormalizedJob to a JobPosting for pipeline compatibility.

        Args:
            job: NormalizedJob from the actor

        Returns:
            JobPosting for the existing pipeline
        """
        return JobPosting(
            title=job.title,
            company=job.company,
            location=job.location,
            salary=job.salary,
            description=job.description,
            url=job.url,
            source=job.source,
            external_id=job.external_id,
            is_remote=job.is_remote,
            experience_level=job.experience_level,
            posted_date=job.posted_date,
        )