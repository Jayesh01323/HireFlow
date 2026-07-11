"""
Job Ranking Engine Module

Ranks job postings based on multiple factors including skill match,
location match, remote preference, salary score, freshness, and experience fit.
Integrates with existing HireFlow scoring mechanisms.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from src.jobs.schemas import NormalizedJob
from src.matcher import calculate_match
from src.services.skill_gap_engine import SkillGapEngine

logger = logging.getLogger(__name__)


class JobRankingEngine:
    """Ranks job postings using multi-factor scoring."""
    
    def __init__(self) -> None:
        """Initialize job ranking engine."""
        self.skill_gap_engine = SkillGapEngine()
    
    def rank_jobs(
        self,
        jobs: List[NormalizedJob],
        resume_skills: set[str],
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Rank jobs based on multiple factors and return sorted list with scores."""
        ranked_jobs = []
        
        for job in jobs:
            job_score = self.calculate_job_score(job, resume_skills, user_preferences)
            ranked_jobs.append({
                "job": job,
                "overall_score": job_score["overall_score"],
                "skill_match_score": job_score["skill_match_score"],
                "location_match_score": job_score["location_match_score"],
                "salary_score": job_score["salary_score"],
                "freshness_score": job_score["freshness_score"],
                "experience_fit_score": job_score["experience_fit_score"],
                "matched_skills": job_score["matched_skills"],
                "missing_skills": job_score["missing_skills"],
                "skill_coverage": job_score["skill_coverage"],
            })
        
        # Sort by overall score descending
        ranked_jobs.sort(key=lambda x: x["overall_score"], reverse=True)
        
        logger.info(f"Ranked {len(ranked_jobs)} jobs")
        return ranked_jobs
    
    def calculate_job_score(
        self,
        job: NormalizedJob,
        resume_skills: set[str],
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Calculate comprehensive score for a single job."""
        user_prefs = user_preferences or {}
        
        # Calculate individual scores
        skill_match_score = self._calculate_skill_match_score(job, resume_skills)
        location_match_score = self._calculate_location_match_score(job, user_prefs)
        salary_score = self._calculate_salary_score(job, user_prefs)
        freshness_score = self._calculate_freshness_score(job)
        experience_fit_score = self._calculate_experience_fit_score(job, user_prefs)
        
        # Calculate weighted overall score
        overall_score = (
            skill_match_score * 0.35 +      # 35% weight for skill match
            location_match_score * 0.15 +   # 15% weight for location
            salary_score * 0.20 +           # 20% weight for salary
            freshness_score * 0.15 +        # 15% weight for freshness
            experience_fit_score * 0.15    # 15% weight for experience fit
        )
        
        # Get matched and missing skills
        job_skills = set(job.skills) if job.skills else set()
        matched_skills = resume_skills & job_skills
        missing_skills = job_skills - resume_skills
        
        # Calculate skill coverage percentage
        skill_coverage = len(matched_skills) / len(job_skills) if job_skills else 0.0
        
        return {
            "overall_score": round(overall_score, 2),
            "skill_match_score": round(skill_match_score, 2),
            "location_match_score": round(location_match_score, 2),
            "salary_score": round(salary_score, 2),
            "freshness_score": round(freshness_score, 2),
            "experience_fit_score": round(experience_fit_score, 2),
            "matched_skills": list(matched_skills),
            "missing_skills": list(missing_skills),
            "skill_coverage": round(skill_coverage * 100, 2),
        }
    
    def _calculate_skill_match_score(self, job: NormalizedJob, resume_skills: set[str]) -> float:
        """Calculate skill match score using existing matcher."""
        job_skills = set(job.skills) if job.skills else set()
        
        if not job_skills:
            return 0.0
        
        # Use existing match engine
        match_result = calculate_match(resume_skills, job_skills)
        match_percentage = match_result.get("match_percentage", 0.0) / 100.0
        
        return match_percentage
    
    def _calculate_location_match_score(self, job: NormalizedJob, user_preferences: Dict[str, Any]) -> float:
        """Calculate location match score based on user preferences."""
        preferred_location = user_preferences.get("preferred_location", "").lower()
        remote_only = user_preferences.get("remote_only", False)
        
        # If user wants remote only
        if remote_only:
            if job.is_remote or (job.location and "remote" in job.location.lower()):
                return 1.0
            return 0.0
        
        # If user has preferred location
        if preferred_location and job.location:
            job_location = job.location.lower()
            if preferred_location in job_location:
                return 1.0
            # Partial match for same city/region
            if any(loc in job_location for loc in preferred_location.split()):
                return 0.7
        
        # If job is remote and user is flexible
        if job.is_remote:
            return 0.8
        
        # Default score if no preferences
        return 0.5
    
    def _calculate_salary_score(self, job: NormalizedJob, user_preferences: Dict[str, Any]) -> float:
        """Calculate salary score based on user expectations."""
        expected_salary_min = user_preferences.get("expected_salary_min", 0)
        expected_salary_max = user_preferences.get("expected_salary_max", float('inf'))
        
        if not job.salary_min and not job.salary_max:
            return 0.5  # Neutral score if no salary info
        
        # Use salary_min if available, otherwise salary_max
        job_salary = job.salary_min or job.salary_max or 0
        
        if job_salary == 0:
            return 0.5
        
        # If salary meets or exceeds expectations
        if job_salary >= expected_salary_min:
            # Bonus for exceeding expectations
            if job_salary >= expected_salary_max:
                return 1.0
            # Linear scaling between min and max
            if expected_salary_max > expected_salary_min:
                return 0.7 + 0.3 * ((job_salary - expected_salary_min) / (expected_salary_max - expected_salary_min))
            return 0.8
        
        # Penalty for below expectations
        if expected_salary_min > 0:
            ratio = job_salary / expected_salary_min
            return max(0.3, ratio * 0.7)
        
        return 0.5
    
    def _calculate_freshness_score(self, job: NormalizedJob) -> float:
        """Calculate freshness score based on posting date."""
        if not job.posted_date:
            return 0.5  # Neutral score if no date
        
        posted_date = job.posted_date if isinstance(job.posted_date, datetime) else datetime.fromisoformat(str(job.posted_date))
        
        # Use timezone-aware now for comparison
        now = datetime.now(timezone.utc)
        
        # Make posted_date timezone-aware if it's naive
        if posted_date.tzinfo is None:
            posted_date = posted_date.replace(tzinfo=timezone.utc)
        
        days_old = (now - posted_date).days
        
        # Decay function: newer jobs get higher scores
        if days_old <= 1:
            return 1.0
        elif days_old <= 3:
            return 0.9
        elif days_old <= 7:
            return 0.8
        elif days_old <= 14:
            return 0.6
        elif days_old <= 30:
            return 0.4
        elif days_old <= 60:
            return 0.2
        else:
            return 0.1
    
    def _calculate_experience_fit_score(self, job: NormalizedJob, user_preferences: Dict[str, Any]) -> float:
        """Calculate experience fit score based on user's experience level."""
        user_experience_years = user_preferences.get("experience_years", 0)
        
        if not job.experience_min and not job.experience_max:
            return 0.5  # Neutral score if no experience requirements
        
        job_exp_min = job.experience_min or 0
        job_exp_max = job.experience_max or 10
        
        # Perfect fit: user experience within job range
        if job_exp_min <= user_experience_years <= job_exp_max:
            # Bonus for being closer to middle of range
            if job_exp_max > job_exp_min:
                range_mid = (job_exp_min + job_exp_max) / 2
                distance = abs(user_experience_years - range_mid)
                max_distance = (job_exp_max - job_exp_min) / 2
                return 1.0 - (distance / max_distance) * 0.2
            return 1.0
        
        # Overqualified: user has more experience than required
        if user_experience_years > job_exp_max:
            # Slight penalty for being overqualified
            overqualification = user_experience_years - job_exp_max
            return max(0.6, 1.0 - (overqualification * 0.05))
        
        # Underqualified: user has less experience than required
        if user_experience_years < job_exp_min:
            gap = job_exp_min - user_experience_years
            # Small gap is acceptable
            if gap <= 1:
                return 0.8
            elif gap <= 2:
                return 0.6
            elif gap <= 3:
                return 0.4
            else:
                return 0.2
        
        return 0.5
    
    def generate_skill_gap_analysis(
        self,
        job: NormalizedJob,
        resume_skills: set[str],
    ) -> Dict[str, Any]:
        """Generate skill gap analysis using existing skill gap engine."""
        job_skills = set(job.skills) if job.skills else set()
        
        try:
            gap_analysis = self.skill_gap_engine.analyze_skill_gap(resume_skills, job_skills)
            return gap_analysis
        except Exception as e:
            logger.error(f"Error generating skill gap analysis: {e}")
            return {
                "missing_skills": list(job_skills - resume_skills),
                "critical_skills": [],
                "recommended_learning_order": [],
            }
    
    def get_top_jobs(
        self,
        ranked_jobs: List[Dict[str, Any]],
        limit: int = 10,
        min_score: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Get top N jobs above minimum score threshold."""
        filtered = [j for j in ranked_jobs if j["overall_score"] >= min_score]
        return filtered[:limit]
    
    def filter_jobs_by_score(
        self,
        ranked_jobs: List[Dict[str, Any]],
        score_range: tuple[float, float],
    ) -> List[Dict[str, Any]]:
        """Filter jobs by score range."""
        min_score, max_score = score_range
        return [j for j in ranked_jobs if min_score <= j["overall_score"] <= max_score]
