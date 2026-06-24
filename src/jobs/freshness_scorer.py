"""
Job Freshness Scorer Module

Calculates freshness scores for job postings based on posted date and other factors.
Helps prioritize newer and more relevant job listings.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional

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
    
    def calculate_freshness_score(self, job: NormalizedJob) -> float:
        """Calculate freshness score for a job (0.0 to 1.0).
        
        Args:
            job: Normalized job posting
            
        Returns:
            Freshness score between 0.0 (old) and 1.0 (very fresh)
        """
        if not job.posted_date:
            # If no posted date, give a neutral score
            return 0.5
        
        now = datetime.utcnow()
        age = now - job.posted_date
        age_days = age.total_seconds() / 86400  # Convert to days
        
        # Linear decay from 1.0 to 0.0 over max_age_days
        if age_days <= 0:
            return 1.0  # Posted today or in future
        elif age_days >= self.max_age_days:
            return 0.0  # Too old
        else:
            return 1.0 - (age_days / self.max_age_days)
    
    def calculate_weighted_freshness_score(
        self,
        job: NormalizedJob,
        source_weight: float = 1.0,
        skills_weight: float = 1.0,
    ) -> float:
        """Calculate weighted freshness score considering multiple factors.
        
        Args:
            job: Normalized job posting
            source_weight: Weight for source reliability (default 1.0)
            skills_weight: Weight for skill completeness (default 1.0)
            
        Returns:
            Weighted freshness score between 0.0 and 1.0
        """
        base_score = self.calculate_freshness_score(job)
        
        # Source reliability factor
        source_factor = self._get_source_reliability(job.source)
        
        # Skills completeness factor
        skills_factor = min(1.0, len(job.skills) / 10.0) if job.skills else 0.5
        
        # Calculate weighted score
        weighted_score = (
            base_score * 0.6 +
            source_factor * 0.2 * source_weight +
            skills_factor * 0.2 * skills_weight
        )
        
        return min(1.0, max(0.0, weighted_score))
    
    def _get_source_reliability(self, source: str) -> float:
        """Get source reliability score (0.0 to 1.0).
        
        Args:
            source: Job source name
            
        Returns:
            Reliability score for the source
        """
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
    
    def get_freshness_category(self, job: NormalizedJob) -> str:
        """Get freshness category for a job.
        
        Args:
            job: Normalized job posting
            
        Returns:
            Freshness category: 'very_fresh', 'fresh', 'moderate', 'stale'
        """
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
        jobs: list[NormalizedJob],
        min_score: float = 0.5,
    ) -> list[NormalizedJob]:
        """Filter jobs by minimum freshness score.
        
        Args:
            jobs: List of normalized job postings
            min_score: Minimum freshness score (default 0.5)
            
        Returns:
            Filtered list of jobs
        """
        return [job for job in jobs if self.calculate_freshness_score(job) >= min_score]
    
    def sort_by_freshness(
        self,
        jobs: list[NormalizedJob],
        descending: bool = True,
    ) -> list[NormalizedJob]:
        """Sort jobs by freshness score.
        
        Args:
            jobs: List of normalized job postings
            descending: Sort in descending order (default True)
            
        Returns:
            Sorted list of jobs
        """
        return sorted(
            jobs,
            key=lambda j: self.calculate_freshness_score(j),
            reverse=descending
        )
    
    def batch_score(self, jobs: list[NormalizedJob]) -> dict[str, float]:
        """Calculate freshness scores for a batch of jobs.
        
        Args:
            jobs: List of normalized job postings
            
        Returns:
            Dictionary mapping job URLs to freshness scores
        """
        scores = {}
        for job in jobs:
            scores[job.url] = self.calculate_freshness_score(job)
        return scores
