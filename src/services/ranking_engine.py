"""
Ranking Engine Service

Ranks job opportunities based on resume match, skill gap, and other factors.
Provides personalized job recommendations with scoring.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.jobs.schemas import NormalizedJob

logger = logging.getLogger(__name__)


@dataclass
class JobRanking:
    """Represents a ranked job opportunity."""
    
    job: NormalizedJob
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
        self.weights: Dict[str, float] = {
            "match_score": 0.40,
            "freshness": 0.20,
            "experience_fit": 0.15,
            "salary": 0.15,
            "remote_preference": 0.10,
        }
    
    def rank_jobs(
        self,
        jobs: List[NormalizedJob],
        match_scores: Dict[str, float],
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> List[JobRanking]:
        """Rank job opportunities based on multiple factors."""
        user_prefs = user_preferences or {}
        
        rankings = []
        for job in jobs:
            match_score = match_scores.get(job.url, 0.0)
            
            # Calculate individual scores
            freshness_score = self._calculate_freshness_score(job.posted_date)
            experience_fit_score = self._calculate_experience_fit_score(
                job.experience_level or "", 
                user_prefs.get("preferred_experience")
            )
            salary_score = self._calculate_salary_score(
                job.salary_min,
                job.salary_max,
                user_prefs.get("preferred_salary_min"),
                user_prefs.get("preferred_salary_max")
            )
            remote_preference_score = self._calculate_remote_preference_score(
                job.is_remote,
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
                rank=0,
            ))
        
        # Sort by overall score
        rankings.sort(key=lambda x: x.overall_score, reverse=True)
        
        # Assign ranks
        for idx, ranking in enumerate(rankings, 1):
            ranking.rank = idx
        
        return rankings
    
    def _calculate_freshness_score(self, posted_date: Optional[datetime]) -> float:
        """Calculate freshness score based on posting date."""
        if not posted_date:
            return 50.0
        
        try:
            if isinstance(posted_date, str):
                post_date = datetime.fromisoformat(posted_date)
            else:
                post_date = posted_date
            days_since_posted = (datetime.now() - post_date).days
            
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
            return 50.0
    
    def _calculate_experience_fit_score(self, job_experience: str, preferred_experience: Optional[str]) -> float:
        """Calculate experience fit score."""
        if not preferred_experience:
            return 50.0
        
        job_exp_lower = job_experience.lower()
        pref_exp_lower = preferred_experience.lower()
        
        if pref_exp_lower in job_exp_lower:
            return 100.0
        
        try:
            job_years = re.findall(r'\d+', job_exp_lower)
            pref_years = re.findall(r'\d+', pref_exp_lower)
            
            if job_years and pref_years:
                job_year = int(job_years[0])
                pref_year = int(pref_years[0])
                
                if abs(job_year - pref_year) <= 1:
                    return 80.0
                elif abs(job_year - pref_year) <= 2:
                    return 60.0
                else:
                    return 30.0
        except (ValueError, IndexError):
            pass
        
        return 40.0
    
    def _calculate_salary_score(
        self, 
        salary_min: Optional[int], 
        salary_max: Optional[int],
        min_pref: Optional[int], 
        max_pref: Optional[int]
    ) -> float:
        """Calculate salary preference score."""
        if salary_min is None and salary_max is None:
            return 50.0
        
        if not min_pref and not max_pref:
            return 50.0
        
        # Use the midpoint of salary range
        if salary_min and salary_max:
            salary_mid = (salary_min + salary_max) / 2
        elif salary_min:
            salary_mid = salary_min
        elif salary_max:
            salary_mid = salary_max
        else:
            return 50.0
        
        if min_pref and max_pref:
            if min_pref <= salary_mid <= max_pref:
                return 100.0
            elif salary_mid > max_pref:
                return 80.0
            else:
                return 30.0
        elif min_pref:
            return 100.0 if salary_mid >= min_pref else 30.0
        elif max_pref:
            return 100.0 if salary_mid <= max_pref else 80.0
        
        return 50.0
    
    def _calculate_remote_preference_score(self, is_remote: bool, prefer_remote: bool) -> float:
        """Calculate remote preference score."""
        if prefer_remote:
            return 100.0 if is_remote else 20.0
        else:
            return 20.0 if is_remote else 100.0