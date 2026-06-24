"""
Job Matcher Module

Integrates resume matching with job discovery.
Matches user resumes against discovered jobs and provides match scores.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from src.database.job_repository import JobRepository
from src.database.models import Job
from src.jobs.schemas import NormalizedJob
from src.matcher import calculate_match, extract_job_skills, extract_resume_skills

logger = logging.getLogger(__name__)


class JobMatcher:
    """Matches resumes against discovered jobs."""
    
    def __init__(self, job_repository: Optional[JobRepository] = None) -> None:
        """Initialize job matcher.
        
        Args:
            job_repository: Job repository for database operations
        """
        self.job_repository = job_repository
    
    def match_resume_to_jobs(
        self,
        parsed_resume: Dict[str, Any],
        jobs: List[Job] | List[NormalizedJob],
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Match a resume against a list of jobs.
        
        Args:
            parsed_resume: Parsed resume data
            jobs: List of jobs to match against
            limit: Maximum number of results
            
        Returns:
            List of match results with scores and details
        """
        # Extract skills from resume
        resume_skills = extract_resume_skills(parsed_resume)
        
        match_results = []
        
        for job in jobs:
            # Extract job skills
            job_description = getattr(job, 'description', '')
            job_skills = extract_job_skills(job_description) if job_description else []
            
            # Calculate match
            match_data = calculate_match(resume_skills, job_skills)
            
            match_result = {
                "job_id": getattr(job, 'id', None),
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "url": job.url,
                "source": job.source,
                "match_percentage": match_data.get("match_percentage", 0),
                "weighted_match_percentage": match_data.get("weighted_match_percentage", 0),
                "technical_match_percentage": match_data.get("technical_match_percentage", 0),
                "soft_skill_match_percentage": match_data.get("soft_skill_match_percentage", 0),
                "matched_skills": match_data.get("matched_skills", []),
                "missing_skills": match_data.get("missing_skills", []),
                "recommendations": match_data.get("recommendations", {}),
            }
            
            match_results.append(match_result)
        
        # Sort by weighted match percentage
        match_results.sort(key=lambda x: x["weighted_match_percentage"], reverse=True)
        
        return match_results[:limit]
    
    def match_resume_to_discovered_jobs(
        self,
        parsed_resume: Dict[str, Any],
        query: str = "",
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        sources: Optional[List[str]] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Discover jobs and match resume against them.
        
        Args:
            parsed_resume: Parsed resume data
            query: Job search query
            location: Job location filter
            remote: Remote jobs filter
            experience: Experience level filter
            salary_min: Minimum salary filter
            sources: Job sources to include
            limit: Maximum number of results
            
        Returns:
            List of match results with scores and details
        """
        from src.jobs.aggregator import JobAggregator
        
        # Discover jobs
        aggregator = JobAggregator()
        jobs = aggregator.search_jobs(
            query=query,
            location=location,
            remote=remote,
            experience=experience,
            salary_min=salary_min,
            sources=sources,
            limit=limit * 2,  # Get more jobs for better matching
        )
        
        # Match resume to discovered jobs
        match_results = self.match_resume_to_jobs(parsed_resume, jobs, limit=limit)
        
        return match_results
    
    def get_top_matches_for_resume(
        self,
        parsed_resume: Dict[str, Any],
        min_match_percentage: float = 50.0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get top matching jobs for a resume from database.
        
        Args:
            parsed_resume: Parsed resume data
            min_match_percentage: Minimum match percentage threshold
            limit: Maximum number of results
            
        Returns:
            List of top match results
        """
        if not self.job_repository:
            logger.warning("Job repository not available, returning empty results")
            return []
        
        # Get recent jobs from database
        jobs = self.job_repository.get_recent_jobs(days=30, limit=100)
        
        # Match resume to jobs
        match_results = self.match_resume_to_jobs(parsed_resume, jobs, limit=limit * 2)
        
        # Filter by minimum match percentage
        filtered_results = [
            r for r in match_results
            if r["weighted_match_percentage"] >= min_match_percentage
        ]
        
        return filtered_results[:limit]
    
    def analyze_job_for_resume(
        self,
        parsed_resume: Dict[str, Any],
        job_description: str,
    ) -> Dict[str, Any]:
        """Analyze a specific job description against a resume.
        
        Args:
            parsed_resume: Parsed resume data
            job_description: Job description text
            
        Returns:
            Detailed match analysis
        """
        # Extract skills
        resume_skills = extract_resume_skills(parsed_resume)
        job_skills = extract_job_skills(job_description)
        
        # Calculate match
        match_data = calculate_match(resume_skills, job_skills)
        
        return {
            "match_percentage": match_data.get("match_percentage", 0),
            "weighted_match_percentage": match_data.get("weighted_match_percentage", 0),
            "technical_match_percentage": match_data.get("technical_match_percentage", 0),
            "soft_skill_match_percentage": match_data.get("soft_skill_match_percentage", 0),
            "matched_skills": match_data.get("matched_skills", []),
            "missing_skills": match_data.get("missing_skills", []),
            "recommendations": match_data.get("recommendations", {}),
            "resume_skills": list(resume_skills),
            "job_skills": job_skills,
        }
