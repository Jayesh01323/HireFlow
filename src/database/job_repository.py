"""
Job Repository Module

Database repository for job-related operations.
Provides CRUD operations for jobs, job matches, and related entities.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from src.database.models import Job, JobMatch, Resume
from src.jobs.schemas import JobPosting, NormalizedJob

logger = logging.getLogger(__name__)


class JobRepository:
    """Repository for job-related database operations."""
    
    def __init__(self, session: Session) -> None:
        """Initialize job repository with database session.
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session
    
    def create_job_from_posting(self, posting: JobPosting) -> Job:
        """Create a Job entity from a JobPosting.
        
        Args:
            posting: JobPosting schema object
            
        Returns:
            Created Job entity
        """
        job = Job(
            title=posting.title,
            company=posting.company,
            location=posting.location,
            salary=posting.salary,
            description=posting.description,
            url=posting.url,
            source=posting.source,
            external_id=posting.external_id,
            is_remote=posting.is_remote,
            experience_level=posting.experience_level,
            posted_date=posting.posted_date,
            scraped_at=datetime.utcnow(),
        )
        
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        
        logger.info(f"Created job: {job.title} at {job.company}")
        return job
    
    def create_job_from_normalized(self, normalized: NormalizedJob) -> Job:
        """Create a Job entity from a NormalizedJob.
        
        Args:
            normalized: NormalizedJob schema object
            
        Returns:
            Created Job entity
        """
        job = Job(
            title=normalized.title,
            company=normalized.company,
            location=normalized.location,
            salary=normalized.salary,
            description=normalized.description,
            url=normalized.url,
            source=normalized.source,
            external_id=normalized.external_id,
            is_remote=normalized.is_remote,
            experience_level=normalized.experience_level,
            posted_date=normalized.posted_date,
            scraped_at=datetime.utcnow(),
        )
        
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        
        logger.info(f"Created job from normalized: {job.title} at {job.company}")
        return job
    
    def get_job_by_id(self, job_id: int) -> Optional[Job]:
        """Get a job by its ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job entity or None
        """
        return self.session.get(Job, job_id)
    
    def get_job_by_external_id(self, external_id: str, source: str) -> Optional[Job]:
        """Get a job by its external ID and source.
        
        Args:
            external_id: External job ID
            source: Job source
            
        Returns:
            Job entity or None
        """
        stmt = select(Job).where(
            and_(Job.external_id == external_id, Job.source == source)
        )
        result = self.session.execute(stmt).scalar_one_or_none()
        return result
    
    def get_job_by_url(self, url: str) -> Optional[Job]:
        """Get a job by its URL.
        
        Args:
            url: Job URL
            
        Returns:
            Job entity or None
        """
        stmt = select(Job).where(Job.url == url)
        result = self.session.execute(stmt).scalar_one_or_none()
        return result
    
    def search_jobs(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        remote: Optional[bool] = None,
        experience_level: Optional[str] = None,
        sources: Optional[List[str]] = None,
        salary_min: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Job]:
        """Search for jobs with filters.
        
        Args:
            query: Search query for title/company
            location: Job location filter
            remote: Remote jobs filter
            experience_level: Experience level filter
            sources: List of sources to include
            salary_min: Minimum salary filter
            limit: Maximum number of results
            offset: Result offset for pagination
            
        Returns:
            List of Job entities
        """
        stmt = select(Job)
        
        conditions = []
        
        if query:
            conditions.append(
                or_(
                    Job.title.ilike(f"%{query}%"),
                    Job.company.ilike(f"%{query}%"),
                    Job.description.ilike(f"%{query}%"),
                )
            )
        
        if location:
            conditions.append(Job.location.ilike(f"%{location}%"))
        
        if remote is not None:
            conditions.append(Job.is_remote == remote)
        
        if experience_level:
            conditions.append(Job.experience_level == experience_level)
        
        if sources:
            conditions.append(Job.source.in_(sources))
        
        if salary_min:
            # This is a simple filter on the salary string
            # In production, you'd want to parse the salary properly
            conditions.append(Job.salary.isnot(None))
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.order_by(Job.posted_date.desc()).limit(limit).offset(offset)
        
        result = self.session.execute(stmt).scalars().all()
        return list(result)
    
    def get_recent_jobs(self, days: int = 7, limit: int = 50) -> List[Job]:
        """Get jobs posted in the last N days.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of results
            
        Returns:
            List of recent Job entities
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        stmt = select(Job).where(
            Job.posted_date >= cutoff_date
        ).order_by(Job.posted_date.desc()).limit(limit)
        
        result = self.session.execute(stmt).scalars().all()
        return list(result)
    
    def get_jobs_by_source(self, source: str, limit: int = 100) -> List[Job]:
        """Get jobs from a specific source.
        
        Args:
            source: Job source name
            limit: Maximum number of results
            
        Returns:
            List of Job entities from the source
        """
        stmt = select(Job).where(
            Job.source == source
        ).order_by(Job.posted_date.desc()).limit(limit)
        
        result = self.session.execute(stmt).scalars().all()
        return list(result)
    
    def update_job(self, job: Job) -> Job:
        """Update an existing job.
        
        Args:
            job: Job entity with updated values
            
        Returns:
            Updated Job entity
        """
        job.updated_at = datetime.utcnow()
        self.session.commit()
        self.session.refresh(job)
        
        logger.info(f"Updated job: {job.title} at {job.company}")
        return job
    
    def delete_job(self, job_id: int) -> bool:
        """Delete a job by ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            True if deleted, False if not found
        """
        job = self.get_job_by_id(job_id)
        if not job:
            return False
        
        self.session.delete(job)
        self.session.commit()
        
        logger.info(f"Deleted job: {job.title} at {job.company}")
        return True
    
    def create_job_match(
        self,
        resume_id: int,
        job_id: int,
        match_percentage: float,
        weighted_match_percentage: float,
        technical_match_percentage: float,
        soft_skill_match_percentage: float,
        matched_skills: List[str],
        missing_skills: List[str],
        recommendations: dict,
    ) -> JobMatch:
        """Create a job match record.
        
        Args:
            resume_id: Resume ID
            job_id: Job ID
            match_percentage: Overall match percentage
            weighted_match_percentage: Weighted match percentage
            technical_match_percentage: Technical skills match percentage
            soft_skill_match_percentage: Soft skills match percentage
            matched_skills: List of matched skills
            missing_skills: List of missing skills
            recommendations: Recommendations dictionary
            
        Returns:
            Created JobMatch entity
        """
        import json
        
        job_match = JobMatch(
            resume_id=resume_id,
            job_id=job_id,
            match_percentage=match_percentage,
            weighted_match_percentage=weighted_match_percentage,
            technical_match_percentage=technical_match_percentage,
            soft_skill_match_percentage=soft_skill_match_percentage,
            matched_skills=json.dumps(matched_skills),
            missing_skills=json.dumps(missing_skills),
            recommendations=json.dumps(recommendations),
        )
        
        self.session.add(job_match)
        self.session.commit()
        self.session.refresh(job_match)
        
        logger.info(f"Created job match: resume {resume_id} -> job {job_id}")
        return job_match
    
    def get_job_matches_for_resume(self, resume_id: int, limit: int = 50) -> List[JobMatch]:
        """Get job matches for a resume.
        
        Args:
            resume_id: Resume ID
            limit: Maximum number of results
            
        Returns:
            List of JobMatch entities
        """
        stmt = select(JobMatch).where(
            JobMatch.resume_id == resume_id
        ).order_by(JobMatch.weighted_match_percentage.desc()).limit(limit)
        
        result = self.session.execute(stmt).scalars().all()
        return list(result)
    
    def get_job_matches_for_job(self, job_id: int, limit: int = 50) -> List[JobMatch]:
        """Get resume matches for a job.
        
        Args:
            job_id: Job ID
            limit: Maximum number of results
            
        Returns:
            List of JobMatch entities
        """
        stmt = select(JobMatch).where(
            JobMatch.job_id == job_id
        ).order_by(JobMatch.weighted_match_percentage.desc()).limit(limit)
        
        result = self.session.execute(stmt).scalars().all()
        return list(result)
    
    def cleanup_old_jobs(self, days: int = 90) -> int:
        """Delete jobs older than N days.
        
        Args:
            days: Age threshold in days
            
        Returns:
            Number of jobs deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        stmt = select(Job).where(Job.posted_date < cutoff_date)
        old_jobs = self.session.execute(stmt).scalars().all()
        
        count = len(old_jobs)
        for job in old_jobs:
            self.session.delete(job)
        
        self.session.commit()
        
        logger.info(f"Cleaned up {count} old jobs")
        return count
