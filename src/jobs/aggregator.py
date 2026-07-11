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
from src.jobs.deduplicator import JobDeduplicator
from src.jobs.freshness_scorer import JobFreshnessScorer
from src.jobs.normalizer import JobNormalizer
from src.jobs.pipeline_logger import (
    FailureReason,
    get_pipeline_logger,
    PipelineLogger,
)
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
        from src.jobs.connectors.wellfound import WellfoundConnector
        self.connectors = {
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
        
        # Initialize pipeline logger for this search
        pl = get_pipeline_logger()
        pl.log_pipeline_start()
        
        # Determine which sources to use
        search_sources = sources if sources else list(self.connectors.keys())
        
        # Register all connectors in the pipeline logger
        for source in search_sources:
            pl.register_connector(source)
        
        # Aggregate jobs from all sources with instrumentation
        all_jobs: List[JobPosting] = []
        for source in search_sources:
            if source in self.connectors:
                pl.log_start(source)
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
                    pl.log_success(source, len(jobs))
                    logger.info(f"Found {len(jobs)} jobs from {source}")
                except ImportError as e:
                    reason, detail = pl.classify_failure(e)
                    pl.log_failure(source, reason, detail, type(e).__name__)
                    logger.error(f"Connector {source} missing dependencies: {e}")
                    logger.error(f"Install required packages for {source} connector")
                except ConnectionError as e:
                    reason, detail = pl.classify_failure(e)
                    pl.log_failure(source, reason, detail, type(e).__name__)
                    logger.error(f"Connector {source} connection failed: {e}")
                except TimeoutError as e:
                    reason, detail = pl.classify_failure(e)
                    pl.log_failure(source, reason, detail, type(e).__name__)
                    logger.error(f"Connector {source} timed out: {e}")
                except Exception as e:
                    reason, detail = pl.classify_failure(e)
                    pl.log_failure(source, reason, detail, type(e).__name__)
                    logger.error(f"Connector {source} failed: {type(e).__name__}: {e}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
            else:
                pl.log_skipped(source, f"Connector not found in registry")
        
        pl.total_jobs_before_dedup = len(all_jobs)
        
        # Fallback to mock jobs only if ENABLE_MOCK_DATA is true
        using_mock = False
        if not all_jobs:
            from src.utils import get_env
            enable_mock = get_env("ENABLE_MOCK_DATA", "false").lower() == "true"
            
            if enable_mock:
                logger.warning("⚠️ No jobs fetched from live connectors. Using mock/fallback job data.")
                logger.warning("⚠️ Set APIFY_API_KEY in .env for live job search.")
                all_jobs = self._load_mock_jobs()
                using_mock = True
                pl.used_mock_fallback = True
                pl.mock_fallback_reason = "All live connectors returned zero jobs"
            else:
                logger.error("❌ No jobs fetched from live connectors and ENABLE_MOCK_DATA is false.")
                logger.error("❌ Set APIFY_API_KEY in .env for live job search or set ENABLE_MOCK_DATA=true.")
                pl.used_mock_fallback = False
                pl.mock_fallback_reason = "No jobs from live connectors and ENABLE_MOCK_DATA is false"
        
        # Normalize jobs
        normalized_jobs = self.normalizer.batch_normalize(all_jobs)
        logger.info(f"Normalized {len(normalized_jobs)} jobs")
        
        # Deduplicate jobs
        unique_jobs = self.deduplicator.deduplicate_jobs(normalized_jobs)
        pl.total_jobs_after_dedup = len(unique_jobs)
        logger.info(f"Deduplicated to {len(unique_jobs)} unique jobs")
        
        # Apply freshness filter: reject jobs older than max_age_days (default 30)
        fresh_jobs = self.freshness_scorer.filter_by_freshness(
            unique_jobs,
            min_score=0.0,  # We use the filter to REMOVE stale jobs, not score them
        )
        # Actually filter out jobs with freshness score of 0.0 (older than max_age_days)
        fresh_jobs = [
            job for job in unique_jobs
            if self.freshness_scorer.calculate_freshness_score(job) > 0.0
        ]
        pl.total_jobs_after_freshness = len(fresh_jobs)
        
        # Track freshness counts per connector
        for source in search_sources:
            source_fresh = [j for j in fresh_jobs if j.source == source]
            pl.set_freshness_count(source, len(source_fresh))
        
        stale_count = len(unique_jobs) - len(fresh_jobs)
        if stale_count > 0:
            logger.info(
                f"🧹 Freshness filter removed {stale_count} stale jobs "
                f"(older than {self.freshness_scorer.max_age_days} days)"
            )
        
        # Store jobs in database
        try:
            save_results = self.repository.batch_save_jobs(fresh_jobs)
            logger.info(f"Saved {save_results['success']} jobs to database")
        except Exception as e:
            logger.error(f"Error saving jobs to database: {e}")
        
        # Update source statistics
        try:
            for source in search_sources:
                source_jobs = [j for j in fresh_jobs if j.source == source]
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
                total_results=len(fresh_jobs),
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
                fresh_jobs,
                resume_skills,
                user_preferences or {},
            )
            logger.info(f"Ranked {len(ranked_jobs)} jobs")
            final_results = ranked_jobs[:limit]
        else:
            # Return unranked jobs if no resume skills
            final_results = [{"job": job, "overall_score": 0.5} for job in fresh_jobs[:limit]]
        
        # Mark which connectors contributed to final results
        pl.total_jobs_final = len(final_results)
        for result in final_results:
            job = result.get("job", result)
            source = getattr(job, "source", None)
            if source:
                pl.mark_used_in_final(source)
        
        # Log pipeline end with summary
        pl.log_pipeline_end()
        
        return final_results
    
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
