"""
Job Repository Module

Handles database operations for job postings, job skills, search history, and job sources.
Provides CRUD operations and query methods for the job discovery engine.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.orm import Session

from src.database.models import Job, JobSearchHistory, JobSkill, JobSource
from src.jobs.schemas import NormalizedJob
from src.utils import get_env

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path(get_env("DATABASE_PATH", "data/hireflow.db"))


class JobRepository:
    """Repository for job-related database operations."""
    
    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        """Initialize job repository with database path."""
        self.db_path = db_path
        self._ensure_database()
    
    def _ensure_database(self) -> None:
        """Ensure database exists and tables are created."""
        from src.database.models import Base
        from sqlalchemy import create_engine
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(engine)
        logger.info(f"Database ensured at {self.db_path}")
    
    def _get_session(self) -> Session:
        """Get a database session."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine(f"sqlite:///{self.db_path}")
        SessionLocal = sessionmaker(bind=engine)
        return SessionLocal()
    
    def save_job(self, job: NormalizedJob) -> Optional[int]:
        """Save a normalized job to the database."""
        session = self._get_session()
        try:
            # Check if job already exists
            existing = session.query(Job).filter(
                Job.source == job.source,
                Job.source_job_id == job.external_id
            ).first()
            
            if existing:
                logger.info(f"Job already exists: {job.source}:{job.external_id}")
                return existing.id
            
            # Create new job
            db_job = Job(
                title=job.title,
                company=job.company,
                location=job.location,
                remote=job.is_remote,
                salary_min=job.salary_min,
                salary_max=job.salary_max,
                experience_min=self._parse_experience_min(job.experience_level),
                experience_max=self._parse_experience_max(job.experience_level),
                required_skills=json.dumps(job.skills) if job.skills else None,
                description=job.description,
                source=job.source,
                source_job_id=job.external_id,
                apply_url=job.url,
                posted_date=job.posted_date,
                fetched_at=job.normalized_at,
                # Legacy fields
                salary=job.salary,
                url=job.url,
                external_id=job.external_id,
                is_remote=job.is_remote,
                experience_level=job.experience_level,
                scraped_at=job.normalized_at,
            )
            
            session.add(db_job)
            session.commit()
            session.refresh(db_job)
            
            # Save job skills
            if job.skills:
                for skill in job.skills:
                    job_skill = JobSkill(job_id=db_job.id, skill=skill)
                    session.add(job_skill)
                session.commit()
            
            logger.info(f"Saved job: {db_job.id} - {job.title} at {job.company}")
            return db_job.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving job: {e}")
            return None
        finally:
            session.close()
    
    def batch_save_jobs(self, jobs: List[NormalizedJob]) -> Dict[str, int]:
        """Save multiple jobs to the database."""
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        for job in jobs:
            try:
                job_id = self.save_job(job)
                if job_id:
                    results["success"] += 1
                else:
                    results["skipped"] += 1
            except Exception as e:
                logger.error(f"Error saving job batch: {e}")
                results["failed"] += 1
        
        logger.info(f"Batch save results: {results}")
        return results
    
    def get_job_by_id(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get a job by ID."""
        session = self._get_session()
        try:
            job = session.query(Job).filter(Job.id == job_id).first()
            if not job:
                return None
            
            # Get job skills
            skills = session.query(JobSkill.skill).filter(JobSkill.job_id == job_id).all()
            skill_list = [s[0] for s in skills]
            
            return self._job_to_dict(job, skill_list)
        finally:
            session.close()
    
    def search_jobs(
        self,
        keyword: Optional[str] = None,
        location: Optional[str] = None,
        remote_only: bool = False,
        experience_level: Optional[str] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        sources: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Search jobs with filters."""
        session = self._get_session()
        try:
            query = session.query(Job)
            
            # Keyword search
            if keyword:
                keyword_filter = or_(
                    Job.title.ilike(f"%{keyword}%"),
                    Job.company.ilike(f"%{keyword}%"),
                    Job.description.ilike(f"%{keyword}%"),
                )
                query = query.filter(keyword_filter)
            
            # Location filter
            if location:
                query = query.filter(Job.location.ilike(f"%{location}%"))
            
            # Remote filter
            if remote_only:
                query = query.filter(Job.remote == True)
            
            # Experience filter
            if experience_level:
                query = query.filter(Job.experience_level == experience_level)
            
            # Salary filter
            if salary_min:
                query = query.filter(Job.salary_min >= salary_min)
            if salary_max:
                query = query.filter(Job.salary_max <= salary_max)
            
            # Source filter
            if sources:
                query = query.filter(Job.source.in_(sources))
            
            # Order by posted date (newest first)
            query = query.order_by(desc(Job.posted_date))
            
            # Pagination
            jobs = query.limit(limit).offset(offset).all()
            
            # Get skills for each job
            results = []
            for job in jobs:
                skills = session.query(JobSkill.skill).filter(JobSkill.job_id == job.id).all()
                skill_list = [s[0] for s in skills]
                results.append(self._job_to_dict(job, skill_list))
            
            return results
        finally:
            session.close()
    
    def get_jobs_by_source(self, source: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get jobs by source."""
        return self.search_jobs(sources=[source], limit=limit)
    
    def get_recent_jobs(self, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent jobs posted within specified days."""
        session = self._get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            jobs = session.query(Job).filter(
                Job.posted_date >= cutoff_date
            ).order_by(desc(Job.posted_date)).limit(limit).all()
            
            results = []
            for job in jobs:
                skills = session.query(JobSkill.skill).filter(JobSkill.job_id == job.id).all()
                skill_list = [s[0] for s in skills]
                results.append(self._job_to_dict(job, skill_list))
            
            return results
        finally:
            session.close()
    
    def save_search_history(
        self,
        query: str,
        location: Optional[str] = None,
        total_results: int = 0,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
    ) -> Optional[int]:
        """Save job search history."""
        session = self._get_session()
        try:
            history = JobSearchHistory(
                user_id=user_id,
                query=query,
                location=location,
                total_results=total_results,
                filters=json.dumps(filters) if filters else None,
            )
            session.add(history)
            session.commit()
            session.refresh(history)
            logger.info(f"Saved search history: {history.id}")
            return history.id
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving search history: {e}")
            return None
        finally:
            session.close()
    
    def get_search_history(self, user_id: Optional[int] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get search history."""
        session = self._get_session()
        try:
            query = session.query(JobSearchHistory)
            if user_id:
                query = query.filter(JobSearchHistory.user_id == user_id)
            
            history = query.order_by(desc(JobSearchHistory.created_at)).limit(limit).all()
            
            results = []
            for h in history:
                results.append({
                    "id": h.id,
                    "query": h.query,
                    "location": h.location,
                    "total_results": h.total_results,
                    "filters": json.loads(h.filters) if h.filters else None,
                    "created_at": h.created_at.isoformat() if h.created_at else None,
                })
            
            return results
        finally:
            session.close()
    
    def update_job_source_stats(
        self,
        source: str,
        jobs_fetched: int = 0,
        jobs_stored: int = 0,
    ) -> None:
        """Update job source statistics."""
        session = self._get_session()
        try:
            job_source = session.query(JobSource).filter(JobSource.source_name == source).first()
            
            if job_source:
                job_source.jobs_fetched += jobs_fetched
                job_source.jobs_stored += jobs_stored
                job_source.last_sync = datetime.utcnow()
                job_source.updated_at = datetime.utcnow()
            else:
                job_source = JobSource(
                    source_name=source,
                    jobs_fetched=jobs_fetched,
                    jobs_stored=jobs_stored,
                    last_sync=datetime.utcnow(),
                )
                session.add(job_source)
            
            session.commit()
            logger.info(f"Updated source stats for {source}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating source stats: {e}")
        finally:
            session.close()
    
    def get_job_sources(self) -> List[Dict[str, Any]]:
        """Get all job sources with statistics."""
        session = self._get_session()
        try:
            sources = session.query(JobSource).all()
            
            results = []
            for s in sources:
                results.append({
                    "id": s.id,
                    "source_name": s.source_name,
                    "jobs_fetched": s.jobs_fetched,
                    "jobs_stored": s.jobs_stored,
                    "last_sync": s.last_sync.isoformat() if s.last_sync else None,
                    "is_active": s.is_active,
                    "api_endpoint": s.api_endpoint,
                    "rate_limit": s.rate_limit,
                })
            
            return results
        finally:
            session.close()
    
    def get_job_statistics(self) -> Dict[str, Any]:
        """Get overall job statistics."""
        session = self._get_session()
        try:
            total_jobs = session.query(func.count(Job.id)).scalar()
            remote_jobs = session.query(func.count(Job.id)).filter(Job.remote == True).scalar()
            
            # Jobs by source
            jobs_by_source = session.query(
                Job.source,
                func.count(Job.id).label('count')
            ).group_by(Job.source).all()
            
            source_stats = {source: count for source, count in jobs_by_source}
            
            # Recent jobs (last 7 days)
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            recent_jobs = session.query(func.count(Job.id)).filter(
                Job.posted_date >= cutoff_date
            ).scalar()
            
            return {
                "total_jobs": total_jobs,
                "remote_jobs": remote_jobs,
                "recent_jobs": recent_jobs,
                "jobs_by_source": source_stats,
            }
        finally:
            session.close()
    
    def delete_old_jobs(self, days: int = 30) -> int:
        """Delete jobs older than specified days."""
        session = self._get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Delete job skills first
            deleted_skills = session.query(JobSkill).filter(
                JobSkill.job_id.in_(
                    session.query(Job.id).filter(Job.posted_date < cutoff_date)
                )
            ).delete(synchronize_session=False)
            
            # Delete jobs
            deleted_jobs = session.query(Job).filter(Job.posted_date < cutoff_date).delete()
            
            session.commit()
            logger.info(f"Deleted {deleted_jobs} jobs and {deleted_skills} skills older than {days} days")
            return deleted_jobs
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting old jobs: {e}")
            return 0
        finally:
            session.close()
    
    def _job_to_dict(self, job: Job, skills: List[str]) -> Dict[str, Any]:
        """Convert job model to dictionary."""
        return {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "remote": job.remote,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "experience_min": job.experience_min,
            "experience_max": job.experience_max,
            "required_skills": json.loads(job.required_skills) if job.required_skills else skills,
            "description": job.description,
            "source": job.source,
            "source_job_id": job.source_job_id,
            "apply_url": job.apply_url,
            "posted_date": job.posted_date.isoformat() if job.posted_date else None,
            "fetched_at": job.fetched_at.isoformat() if job.fetched_at else None,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "skills": skills,
        }
    
    def _parse_experience_min(self, experience_level: Optional[str]) -> Optional[int]:
        """Parse minimum experience from experience level."""
        if not experience_level:
            return None
        
        level_map = {
            "entry": 0,
            "mid": 3,
            "senior": 5,
            "lead": 7,
            "principal": 10,
        }
        
        return level_map.get(experience_level.lower())
    
    def _parse_experience_max(self, experience_level: Optional[str]) -> Optional[int]:
        """Parse maximum experience from experience level."""
        if not experience_level:
            return None
        
        level_map = {
            "entry": 2,
            "mid": 5,
            "senior": 8,
            "lead": 10,
            "principal": 15,
        }
        
        return level_map.get(experience_level.lower())
