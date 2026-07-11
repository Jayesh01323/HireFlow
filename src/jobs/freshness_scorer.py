"""
Job Freshness Scorer Module

Calculates freshness scores for job postings based on posted date and other factors.
Helps prioritize newer and more relevant job listings.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from src.jobs.schemas import NormalizedJob

logger = logging.getLogger(__name__)


class JobFreshnessScorer:
    """Calculates freshness scores for job postings."""
    
    def __init__(self, max_age_days: int = 30) -> None:
        """Initialize job freshness scorer.
        
        Args:
            max_age_days: Maximum age in days for a job to be considered fresh
        """
        self.max_age_days = max_age_days
    
    def _get_posted_date(self, job: Any) -> Optional[datetime]:
        """Get posted date from job, handling both NormalizedJob and DB Job models."""
        if hasattr(job, 'posted_date'):
            return job.posted_date
        return None
    
    def _get_source(self, job: Any) -> str:
        """Get source from job, handling both NormalizedJob and DB Job models."""
        if hasattr(job, 'source'):
            return job.source
        return "unknown"
    
    def _get_skills(self, job: Any) -> list:
        """Get skills from job, handling both NormalizedJob and DB Job models."""
        if hasattr(job, 'skills') and job.skills:
            return job.skills
        return []
    
    def _get_url(self, job: Any) -> str:
        """Get URL from job, handling both NormalizedJob and DB Job models."""
        if hasattr(job, 'url'):
            return job.url
        return ""
    
    def calculate_freshness_score(self, job: Any) -> float:
        """Calculate freshness score for a job (0.0 to 1.0).
        
        Args:
            job: Normalized job posting or DB Job model
            
        Returns:
            Freshness score between 0.0 (old) and 1.0 (very fresh)
        """
        posted_date = self._get_posted_date(job)
        if not posted_date:
            return 0.5
        
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if isinstance(posted_date, datetime):
            age = now - posted_date
        else:
            return 0.5
        
        age_days = age.total_seconds() / 86400
        
        if age_days <= 0:
            return 1.0
        elif age_days >= self.max_age_days:
            return 0.0
        else:
            return 1.0 - (age_days / self.max_age_days)
    
    def calculate_weighted_freshness_score(
        self,
        job: Any,
        source_weight: float = 1.0,
        skills_weight: float = 1.0,
    ) -> float:
        """Calculate weighted freshness score considering multiple factors."""
        base_score = self.calculate_freshness_score(job)
        source_factor = self._get_source_reliability(self._get_source(job))
        skills = self._get_skills(job)
        skills_factor = min(1.0, len(skills) / 10.0) if skills else 0.5
        
        weighted_score = (
            base_score * 0.6 +
            source_factor * 0.2 * source_weight +
            skills_factor * 0.2 * skills_weight
        )
        
        return min(1.0, max(0.0, weighted_score))
    
    def _get_source_reliability(self, source: str) -> float:
        """Get source reliability score (0.0 to 1.0)."""
        source_scores = {
            "linkedin": 0.9,
            "naukri": 0.85,
            "indeed": 0.85,
            "internshala": 0.8,
            "wellfound": 0.85,
            "foundit": 0.75,
            "unstop": 0.7,
            "cutshort": 0.75,
            "glassdoor": 0.8,
            "company_careers": 0.9,
        }
        return source_scores.get(source.lower(), 0.7)
    
    def get_freshness_category(self, job: Any) -> str:
        """Get freshness category for a job."""
        score = self.calculate_freshness_score(job)
        if score >= 0.8:
            return "very_fresh"
        elif score >= 0.6:
            return "fresh"
        elif score >= 0.4:
            return "moderate"
        else:
            return "stale"
    
    def filter_by_freshness(
        self,
        jobs: list[Any],
        min_score: float = 0.5,
    ) -> list[Any]:
        """Filter jobs by minimum freshness score."""
        return [job for job in jobs if self.calculate_freshness_score(job) >= min_score]
    
    def sort_by_freshness(
        self,
        jobs: list[Any],
        descending: bool = True,
    ) -> list[Any]:
        """Sort jobs by freshness score."""
        return sorted(
            jobs,
            key=lambda j: self.calculate_freshness_score(j),
            reverse=descending
        )
    
    def batch_score(self, jobs: list[Any]) -> dict[str, float]:
        """Calculate freshness scores for a batch of jobs."""
        scores = {}
        for job in jobs:
            scores[self._get_url(job)] = self.calculate_freshness_score(job)
        return scores