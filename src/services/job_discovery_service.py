"""
Job Discovery Service Module

Integrates the Job Discovery Engine with existing Resume Parser and Job Matcher.
Provides a unified interface for job search, matching, and recommendation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set

from src.jobs.aggregator import JobAggregator
from src.jobs.ranking import JobRankingEngine
from src.matcher import analyze_match
from src.parser import parse_resume
from src.services.skill_gap_engine import SkillGapEngine

logger = logging.getLogger(__name__)


class JobDiscoveryService:
    """Service for job discovery with resume integration."""
    
    def __init__(self) -> None:
        """Initialize job discovery service."""
        self.aggregator = JobAggregator()
        self.ranking_engine = JobRankingEngine()
        self.skill_gap_engine = SkillGapEngine()
    
    def search_jobs_with_resume(
        self,
        resume_text: str,
        query: str,
        location: Optional[str] = None,
        remote_only: bool = False,
        experience_level: Optional[str] = None,
        sources: Optional[List[str]] = None,
        limit: int = 100,
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Search jobs and match with resume.
        
        Args:
            resume_text: Raw resume text
            query: Job search query
            location: Location filter
            remote_only: Remote jobs filter
            experience_level: Experience level filter
            sources: Sources to search
            limit: Maximum results
            user_preferences: User preferences for ranking
            
        Returns:
            Dictionary with matched jobs and analysis
        """
        logger.info(f"Searching jobs with resume integration: {query}")
        
        # Parse resume to extract skills
        try:
            from src.schemas import Resume as ResumeSchema
            parsed_resume = parse_resume(resume_text)
            resume_skills = self._extract_resume_skills(parsed_resume)
            logger.info(f"Extracted {len(resume_skills)} skills from resume")
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            resume_skills = set()
        
        # Search jobs with resume skills for ranking
        ranked_jobs = self.aggregator.search_jobs(
            query=query,
            location=location,
            remote=remote_only,
            experience=experience_level,
            sources=sources,
            limit=limit,
            resume_skills=resume_skills,
            user_preferences=user_preferences,
        )
        
        # Generate skill gap analysis for top jobs
        for job_result in ranked_jobs[:10]:  # Top 10 jobs
            job = job_result["job"]
            job_skills = set(job.skills) if job.skills else set()
            
            try:
                gap_analysis = self.skill_gap_engine.analyze_skill_gap(resume_skills, job_skills)
                job_result["skill_gap_analysis"] = gap_analysis
            except Exception as e:
                logger.error(f"Error generating skill gap analysis: {e}")
                job_result["skill_gap_analysis"] = None
        
        return {
            "jobs": ranked_jobs,
            "resume_skills": list(resume_skills),
            "total_results": len(ranked_jobs),
            "search_params": {
                "query": query,
                "location": location,
                "remote_only": remote_only,
                "experience_level": experience_level,
                "sources": sources,
            },
        }
    
    def match_job_with_resume(
        self,
        resume_text: str,
        job_description: str,
    ) -> Dict[str, Any]:
        """Match a specific job with resume using existing matcher.
        
        Args:
            resume_text: Raw resume text
            job_description: Job description text
            
        Returns:
            Dictionary with match analysis
        """
        logger.info("Matching job with resume")
        
        try:
            from src.schemas import Resume as ResumeSchema
            parsed_resume = parse_resume(resume_text)
            
            # Use existing matcher
            match_analysis = analyze_match(parsed_resume.model_dump(), job_description)
            
            return match_analysis
        except Exception as e:
            logger.error(f"Error matching job with resume: {e}")
            return {
                "error": str(e),
                "match_results": {"match_percentage": 0.0},
                "recommendations": [],
            }
    
    def get_job_recommendations(
        self,
        resume_text: str,
        limit: int = 20,
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get personalized job recommendations based on resume.
        
        Args:
            resume_text: Raw resume text
            limit: Maximum recommendations
            user_preferences: User preferences
            
        Returns:
            Dictionary with recommended jobs
        """
        logger.info("Getting job recommendations based on resume")
        
        # Parse resume to extract skills and preferences
        try:
            from src.schemas import Resume as ResumeSchema
            parsed_resume = parse_resume(resume_text)
            resume_skills = self._extract_resume_skills(parsed_resume)
            
            # Infer search parameters from resume
            query = self._infer_search_query(parsed_resume)
            location = user_preferences.get("preferred_location") if user_preferences else None
            experience_level = self._infer_experience_level(parsed_resume)
            
            # Search for jobs
            results = self.search_jobs_with_resume(
                resume_text=resume_text,
                query=query,
                location=location,
                remote_only=user_preferences.get("remote_only", False) if user_preferences else False,
                experience_level=experience_level,
                limit=limit,
                user_preferences=user_preferences,
            )
            
            results["recommendation_type"] = "resume_based"
            return results
            
        except Exception as e:
            logger.error(f"Error getting job recommendations: {e}")
            return {
                "jobs": [],
                "error": str(e),
                "resume_skills": [],
            }
    
    def _extract_resume_skills(self, parsed_resume: Any) -> Set[str]:
        """Extract skills from parsed resume."""
        skills = set()
        
        if hasattr(parsed_resume, 'skills') and parsed_resume.skills:
            for skill_item in parsed_resume.skills:
                if hasattr(skill_item, 'name'):
                    skills.add(skill_item.name.lower())
                elif isinstance(skill_item, dict):
                    skills.add(skill_item.get('name', '').lower())
        
        return skills
    
    def _infer_search_query(self, parsed_resume: Any) -> str:
        """Infer search query from resume."""
        # Look for common role indicators in experience/projects
        query = "software"  # Default fallback
        
        if hasattr(parsed_resume, 'experience') and parsed_resume.experience:
            exp_text = ' '.join(parsed_resume.experience).lower()
            if 'developer' in exp_text or 'engineer' in exp_text:
                query = "software engineer"
            elif 'data' in exp_text or 'analyst' in exp_text:
                query = "data analyst"
            elif 'manager' in exp_text:
                query = "project manager"
        
        return query
    
    def _infer_experience_level(self, parsed_resume: Any) -> Optional[str]:
        """Infer experience level from resume."""
        # Count years of experience from experience section
        if hasattr(parsed_resume, 'experience') and parsed_resume.experience:
            exp_count = len(parsed_resume.experience)
            if exp_count <= 1:
                return "entry"
            elif exp_count <= 3:
                return "mid"
            elif exp_count <= 5:
                return "senior"
            else:
                return "lead"
        
        return None
    
    def get_job_statistics(self) -> Dict[str, Any]:
        """Get overall job statistics."""
        return self.aggregator.get_job_statistics()
    
    def get_source_statistics(self) -> Dict[str, int]:
        """Get job source statistics."""
        return self.aggregator.get_source_stats()
