"""
Ranking Engine Service

Ranks job opportunities based on resume match, skill gap, and other factors.
Provides personalized job recommendations with scoring.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.jobs.schemas import Job

logger = logging.getLogger(__name__)


@dataclass
class JobRanking:
    """Represents a ranked job opportunity."""
    
    job: Job
    match_score: float
    freshness_score: float
    experience_fit_score: float
    salary_score: float
    remote_preference_score: float
    overall_score: float
    rank: int


class RankingEngine:
    """Engine for ranking job opportunities based on multiple factors."""
    
    def __init__(self) -> None:
        """Initialize ranking engine with specified weights."""
        # Ranking formula as specified:
        # Resume Match Score = 40%
        # Freshness = 20%
        # Experience Fit = 15%
        # Salary = 15%
        # Remote Preference = 10%
        self.weights: Dict[str, float] = {
            "match_score": 0.40,
            "freshness": 0.20,
            "experience_fit": 0.15,
            "salary": 0.15,
            "remote_preference": 0.10,
        }
    
    def rank_jobs(
        self,
        jobs: List[Job],
        match_scores: Dict[str, float],
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> List[JobRanking]:
        """Rank job opportunities based on multiple factors."""
        user_prefs = user_preferences or {}
        
        rankings = []
        for job in jobs:
            match_score = match_scores.get(job.id, 0.0)
            
            # Calculate individual scores
            freshness_score = self._calculate_freshness_score(job.posted_date)
            experience_fit_score = self._calculate_experience_fit_score(
                job.experience, 
                user_prefs.get("preferred_experience")
            )
            salary_score = self._calculate_salary_score(
                job.salary,
                user_prefs.get("preferred_salary_min"),
                user_prefs.get("preferred_salary_max")
            )
            remote_preference_score = self._calculate_remote_preference_score(
                job.work_mode,
                user_prefs.get("prefer_remote", False)
            )
            
            # Calculate overall score
            overall_score = (
                match_score * self.weights["match_score"] +
                freshness_score * self.weights["freshness"] +
                experience_fit_score * self.weights["experience_fit"] +
                salary_score * self.weights["salary"] +
                remote_preference_score * self.weights["remote_preference"]
            )
            
            rankings.append(JobRanking(
                job=job,
                match_score=match_score,
                freshness_score=freshness_score,
                experience_fit_score=experience_fit_score,
                salary_score=salary_score,
                remote_preference_score=remote_preference_score,
                overall_score=round(overall_score, 2),
                rank=0,  # Will be assigned after sorting
            ))
        
        # Sort by overall score
        rankings.sort(key=lambda x: x.overall_score, reverse=True)
        
        # Assign ranks
        for idx, ranking in enumerate(rankings, 1):
            ranking.rank = idx
        
        return rankings
    
    def _calculate_freshness_score(self, posted_date: str) -> float:
        """Calculate freshness score based on posting date."""
        try:
            post_date = datetime.strptime(posted_date, "%Y-%m-%d")
            days_since_posted = (datetime.now() - post_date).days
            
            # Score decreases as job gets older
            # 0-7 days: 100
            # 8-30 days: 80
            # 31-60 days: 60
            # 61-90 days: 40
            # 90+ days: 20
            if days_since_posted <= 7:
                return 100.0
            elif days_since_posted <= 30:
                return 80.0
            elif days_since_posted <= 60:
                return 60.0
            elif days_since_posted <= 90:
                return 40.0
            else:
                return 20.0
        except (ValueError, TypeError):
            return 50.0  # Default score if date parsing fails
    
    def _calculate_experience_fit_score(self, job_experience: str, preferred_experience: Optional[str]) -> float:
        """Calculate experience fit score."""
        if not preferred_experience:
            return 50.0  # Neutral score if no preference
        
        job_exp_lower = job_experience.lower()
        pref_exp_lower = preferred_experience.lower()
        
        # Exact match
        if pref_exp_lower in job_exp_lower:
            return 100.0
        
        # Partial match based on years
        try:
            import re
            job_years = re.findall(r'\d+', job_exp_lower)
            pref_years = re.findall(r'\d+', pref_exp_lower)
            
            if job_years and pref_years:
                job_year = int(job_years[0])
                pref_year = int(pref_years[0])
                
                # Within 1 year
                if abs(job_year - pref_year) <= 1:
                    return 80.0
                # Within 2 years
                elif abs(job_year - pref_year) <= 2:
                    return 60.0
                else:
                    return 30.0
        except (ValueError, IndexError):
            pass
        
        return 40.0  # Default partial match score
    
    def _calculate_salary_score(self, job_salary: Optional[str], min_pref: Optional[int], max_pref: Optional[int]) -> float:
        """Calculate salary preference score."""
        if not job_salary or (not min_pref and not max_pref):
            return 50.0  # Neutral score
        
        try:
            import re
            numbers = re.findall(r'[\d,]+', job_salary.replace('₹', '').replace(',', ''))
            if not numbers:
                return 50.0
            
            # Use the first number as reference
            salary_num = int(numbers[0])
            
            # Check if salary is within preferred range
            if min_pref and max_pref:
                if min_pref <= salary_num <= max_pref:
                    return 100.0
                elif salary_num > max_pref:
                    return 80.0  # Above range is good
                else:
                    return 30.0  # Below range
            elif min_pref:
                return 100.0 if salary_num >= min_pref else 30.0
            elif max_pref:
                return 100.0 if salary_num <= max_pref else 80.0
            
        except (ValueError, IndexError):
            return 50.0
        
        return 50.0
    
    def _calculate_remote_preference_score(self, work_mode: str, prefer_remote: bool) -> float:
        """Calculate remote preference score."""
        work_mode_lower = work_mode.lower()
        
        if prefer_remote:
            if work_mode_lower == "remote":
                return 100.0
            elif work_mode_lower == "hybrid":
                return 70.0
            else:
                return 20.0
        else:
            if work_mode_lower == "on-site":
                return 100.0
            elif work_mode_lower == "hybrid":
                return 70.0
            else:
                return 30.0
