"""
Job Aggregator Module

Aggregates job postings from multiple sources into a unified collection.
Coordinates job scraping and collection from various platforms.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from src.jobs.connectors.apify import ApifyConnector
from src.jobs.connectors.base import BaseJobConnector
from src.jobs.connectors.cutshort import CutshortConnector
from src.jobs.connectors.foundit import FounditConnector
from src.jobs.connectors.glassdoor import GlassdoorConnector
from src.jobs.connectors.indeed import IndeedConnector
from src.jobs.ranking import JobRankingEngine
from src.jobs.connectors.internshala import InternshalaConnector
from src.jobs.connectors.linkedin import LinkedInConnector
from src.jobs.connectors.naukri import NaukriConnector
from src.jobs.connectors.unstop import UnstopConnector
from src.jobs.connectors.wellfound import WellfoundConnector
from src.jobs.deduplicator import JobDeduplicator
from src.jobs.freshness_scorer import JobFreshnessScorer
from src.jobs.normalizer import JobNormalizer
from src.jobs.schemas import JobPosting, NormalizedJob

logger = logging.getLogger(__name__)


class JobAggregator:
    """Aggregates jobs from multiple sources."""
    
    def __init__(self) -> None:
        """Initialize job aggregator with all connectors."""
        self.connectors: Dict[str, BaseJobConnector] = {}
        self.normalizer = JobNormalizer()
        self.deduplicator = JobDeduplicator()
        self.freshness_scorer = JobFreshnessScorer()
        self.ranking_engine = JobRankingEngine()
        from src.jobs.repository import JobRepository
        self.repository = JobRepository()
        self._initialize_connectors()
    
    def _initialize_connectors(self) -> None:
        """Initialize all job source connectors."""
        self.connectors = {
            "apify": ApifyConnector(),
            "linkedin": LinkedInConnector(),
            "naukri": NaukriConnector(),
            "internshala": InternshalaConnector(),
            "indeed": IndeedConnector(),
            "foundit": FounditConnector(),
            "wellfound": WellfoundConnector(),
            "unstop": UnstopConnector(),
            "cutshort": CutshortConnector(),
            "glassdoor": GlassdoorConnector(),
        }
        logger.info(f"Initialized {len(self.connectors)} job connectors")
    
    def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        sources: Optional[List[str]] = None,
        limit: int = 100,
        resume_skills: Optional[set[str]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for jobs across all configured sources with full pipeline.
        
        Args:
            query: Job search query
            location: Job location filter
            remote: Remote jobs filter
            experience: Experience level filter
            salary_min: Minimum salary filter
            sources: List of sources to search (None = all)
            limit: Maximum number of jobs to return
            resume_skills: User's resume skills for ranking
            user_preferences: User preferences for ranking
            
        Returns:
            List of ranked job dictionaries with scores
        """
        logger.info(f"Searching jobs: query={query}, location={location}, remote={remote}")
        
        # Determine which sources to use
        search_sources = sources if sources else list(self.connectors.keys())
        
        # Aggregate jobs from all sources
        all_jobs: List[JobPosting] = []
        for source in search_sources:
            if source in self.connectors:
                try:
                    jobs = self.connectors[source].search_jobs(
                        query=query,
                        location=location,
                        remote=remote,
                        experience=experience,
                        salary_min=salary_min,
                        limit=limit // len(search_sources),
                    )
                    all_jobs.extend(jobs)
                    logger.info(f"Found {len(jobs)} jobs from {source}")
                except Exception as e:
                    logger.error(f"Error searching {source}: {e}")
        
        # Fallback to mock jobs if no jobs found
        if not all_jobs:
            logger.info("No jobs from connectors, loading mock jobs")
            all_jobs = self._load_mock_jobs()
        
        # Normalize jobs
        normalized_jobs = self.normalizer.batch_normalize(all_jobs)
        logger.info(f"Normalized {len(normalized_jobs)} jobs")
        
        # Deduplicate jobs
        unique_jobs = self.deduplicator.deduplicate_jobs(normalized_jobs)
        logger.info(f"Deduplicated to {len(unique_jobs)} unique jobs")
        
        # Store jobs in database
        try:
            save_results = self.repository.batch_save_jobs(unique_jobs)
            logger.info(f"Saved {save_results['success']} jobs to database")
        except Exception as e:
            logger.error(f"Error saving jobs to database: {e}")
        
        # Update source statistics
        try:
            for source in search_sources:
                source_jobs = [j for j in unique_jobs if j.source == source]
                self.repository.update_job_source_stats(
                    source,
                    jobs_fetched=len(source_jobs),
                    jobs_stored=len(source_jobs),
                )
        except Exception as e:
            logger.error(f"Error updating source stats: {e}")
        
        # Save search history
        try:
            self.repository.save_search_history(
                query=query,
                location=location,
                total_results=len(unique_jobs),
                filters={
                    "remote": remote,
                    "experience": experience,
                    "sources": search_sources,
                },
            )
        except Exception as e:
            logger.error(f"Error saving search history: {e}")
        
        # Rank jobs if resume skills provided
        if resume_skills:
            ranked_jobs = self.ranking_engine.rank_jobs(
                unique_jobs,
                resume_skills,
                user_preferences or {},
            )
            logger.info(f"Ranked {len(ranked_jobs)} jobs")
            return ranked_jobs[:limit]
        
        # Return unranked jobs if no resume skills
        return [{"job": job, "overall_score": 0.5} for job in unique_jobs[:limit]]
    
    def _load_mock_jobs(self) -> List[JobPosting]:
        """Load mock jobs from JSON file for testing."""
        import json
        from pathlib import Path
        
        mock_jobs_path = Path(__file__).parent / "mock_jobs.json"
        if not mock_jobs_path.exists():
            logger.warning(f"Mock jobs file not found at {mock_jobs_path}")
            return []
        
        try:
            with open(mock_jobs_path, 'r') as f:
                mock_data = json.load(f)
            
            jobs = []
            for job_data in mock_data:
                # Convert mock job to JobPosting
                job = JobPosting(
                    title=job_data.get("title", "Unknown"),
                    company=job_data.get("company", "Unknown"),
                    location=job_data.get("location"),
                    salary=job_data.get("salary"),
                    description=job_data.get("description"),
                    url=job_data.get("source_url", ""),
                    source=job_data.get("source", "Mock"),
                    external_id=job_data.get("id", ""),
                    is_remote=job_data.get("work_mode", "").lower() == "remote",
                    experience_level=job_data.get("experience"),
                    posted_date=None,
                )
                jobs.append(job)
            
            logger.info(f"Loaded {len(jobs)} mock jobs")
            return jobs
        except Exception as e:
            logger.error(f"Error loading mock jobs: {e}")
            return []
    
    def aggregate_from_sources(
        self,
        sources: List[str],
        query: str,
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        limit: int = 100,
    ) -> List[NormalizedJob]:
        """Aggregate jobs from specific sources.
        
        Args:
            sources: List of source names
            query: Job search query
            location: Job location filter
            remote: Remote jobs filter
            experience: Experience level filter
            salary_min: Minimum salary filter
            limit: Maximum number of jobs to return
            
        Returns:
            List of normalized and deduplicated job postings
        """
        return self.search_jobs(
            query=query,
            location=location,
            remote=remote,
            experience=experience,
            salary_min=salary_min,
            sources=sources,
            limit=limit,
        )
    
    def search_from_source(
        self,
        source: str,
        query: str,
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        limit: int = 50,
    ) -> List[NormalizedJob]:
        """Search jobs from a specific source.
        
        Args:
            source: Source name
            query: Job search query
            location: Job location filter
            remote: Remote jobs filter
            experience: Experience level filter
            salary_min: Minimum salary filter
            limit: Maximum number of jobs to return
            
        Returns:
            List of normalized job postings from the source
        """
        logger.info(f"Searching {source} for: {query}")
        
        if source not in self.connectors:
            logger.warning(f"Source {source} not available")
            return []
        
        try:
            jobs = self.connectors[source].search_jobs(
                query=query,
                location=location,
                remote=remote,
                experience=experience,
                salary_min=salary_min,
                limit=limit,
            )
            
            # Normalize jobs
            normalized_jobs = self.normalizer.batch_normalize(jobs)
            
            logger.info(f"Found {len(normalized_jobs)} jobs from {source}")
            return normalized_jobs
            
        except Exception as e:
            logger.error(f"Error searching {source}: {e}")
            return []
    
    def add_connector(self, source: str, connector: BaseJobConnector) -> None:
        """Add a job connector for a source.
        
        Args:
            source: Source name
            connector: Connector instance
        """
        self.connectors[source] = connector
        logger.info(f"Added connector for {source}")
    
    def get_available_sources(self) -> List[str]:
        """Get list of available job sources."""
        return list(self.connectors.keys())
    
    def get_source_stats(self) -> Dict[str, int]:
        """Get statistics for each source from database.
        
        Returns:
            Dictionary mapping source names to job counts
        """
        try:
            sources = self.repository.get_job_sources()
            return {s["source_name"]: s["jobs_stored"] for s in sources}
        except Exception as e:
            logger.error(f"Error getting source stats: {e}")
            return {}
    
    def get_job_statistics(self) -> Dict[str, Any]:
        """Get overall job statistics from database.
        
        Returns:
            Dictionary with job statistics
        """
        try:
            return self.repository.get_job_statistics()
        except Exception as e:
            logger.error(f"Error getting job statistics: {e}")
            return {}
    
    def search_database_jobs(
        self,
        keyword: Optional[str] = None,
        location: Optional[str] = None,
        remote_only: bool = False,
        experience_level: Optional[str] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        sources: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search jobs from database without fetching from sources.
        
        Args:
            keyword: Search keyword
            location: Location filter
            remote_only: Remote jobs filter
            experience_level: Experience level filter
            salary_min: Minimum salary filter
            salary_max: Maximum salary filter
            sources: Source filter
            limit: Maximum results
            
        Returns:
            List of job dictionaries from database
        """
        return self.repository.search_jobs(
            keyword=keyword,
            location=location,
            remote_only=remote_only,
            experience_level=experience_level,
            salary_min=salary_min,
            salary_max=salary_max,
            sources=sources,
            limit=limit,
        )
    
    def get_recent_jobs(self, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent jobs from database.
        
        Args:
            days: Number of days to look back
            limit: Maximum results
            
        Returns:
            List of recent job dictionaries
        """
        return self.repository.get_recent_jobs(days=days, limit=limit)
    
    def get_search_history(self, user_id: Optional[int] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get search history from database.
        
        Args:
            user_id: User ID filter
            limit: Maximum results
            
        Returns:
            List of search history dictionaries
        """
        return self.repository.get_search_history(user_id=user_id, limit=limit)
