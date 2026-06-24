"""
Jobs API Module

FastAPI router for job-related endpoints.
Provides endpoints for job search, retrieval, and management.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.job_repository import JobRepository
from src.jobs.aggregator import JobAggregator
from src.jobs.schemas import JobPosting
from src.matcher import analyze_match

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/search")
async def search_jobs(
    query: str = Query(..., description="Job search query"),
    location: Optional[str] = Query(None, description="Job location"),
    remote: bool = Query(False, description="Remote jobs only"),
    experience: Optional[str] = Query(None, description="Experience level"),
    salary_min: Optional[int] = Query(None, description="Minimum salary"),
    sources: Optional[List[str]] = Query(None, description="Job sources"),
    limit: int = Query(100, description="Maximum number of results"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Search for jobs across multiple sources with live aggregation."""
    try:
        logger.info(f"Searching jobs: query={query}, location={location}, remote={remote}")
        
        # Use job aggregator for live search
        aggregator = JobAggregator()
        jobs = aggregator.search_jobs(
            query=query,
            location=location,
            remote=remote,
            experience=experience,
            salary_min=salary_min,
            sources=sources,
            limit=limit,
        )
        
        # Convert to dict format
        job_dicts = [
            {
                "id": job.external_id or str(i),
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "salary": job.salary,
                "description": job.description,
                "url": job.url,
                "source": job.source,
                "is_remote": job.is_remote,
                "experience_level": job.experience_level,
                "skills": job.skills,
                "posted_date": job.posted_date.isoformat() if job.posted_date else None,
            }
            for i, job in enumerate(jobs)
        ]
        
        return {
            "jobs": job_dicts,
            "total": len(job_dicts),
            "query": query,
            "filters": {
                "location": location,
                "remote": remote,
                "experience": experience,
                "salary_min": salary_min,
                "sources": sources,
            },
        }
        
    except Exception as e:
        logger.error(f"Error searching jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}")
async def get_job(job_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get detailed information for a specific job from database."""
    try:
        logger.info(f"Getting job: {job_id}")
        
        job_repository = JobRepository(db)
        job = job_repository.get_job_by_id(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "salary": job.salary,
            "description": job.description,
            "url": job.url,
            "source": job.source,
            "is_remote": job.is_remote,
            "experience_level": job.experience_level,
            "posted_date": job.posted_date.isoformat() if job.posted_date else None,
            "scraped_at": job.scraped_at.isoformat() if job.scraped_at else None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save")
async def save_job(job: JobPosting, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Save a job to the database."""
    try:
        logger.info(f"Saving job: {job.title} at {job.company}")
        
        job_repository = JobRepository(db)
        
        # Check if job already exists
        existing_job = job_repository.get_job_by_url(job.url)
        if existing_job:
            return {
                "success": True,
                "job_id": existing_job.id,
                "message": "Job already exists in database",
            }
        
        # Create new job
        created_job = job_repository.create_job_from_posting(job)
        
        return {
            "success": True,
            "job_id": created_job.id,
            "message": "Job saved successfully",
        }
        
    except Exception as e:
        logger.error(f"Error saving job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{job_id}")
async def delete_job(job_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Delete a saved job."""
    try:
        logger.info(f"Deleting job: {job_id}")
        
        job_repository = JobRepository(db)
        success = job_repository.delete_job(job_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "success": True,
            "message": "Job deleted successfully",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_job(job_description: str) -> Dict[str, Any]:
    """Analyze a job description and extract key information."""
    try:
        logger.info("Analyzing job description")
        
        # Use matcher to analyze job description
        analysis = analyze_match(
            parsed_resume={"skills": [], "experience": []},
            job_description=job_description,
        )
        
        return {
            "skills": analysis.get("job_skills", []),
            "experience_level": analysis.get("job_experience_level", "mid"),
            "key_requirements": analysis.get("recommendations", {}).get("improvements", []),
            "summary": analysis.get("recommendations", {}).get("summary", ""),
        }
        
    except Exception as e:
        logger.error(f"Error analyzing job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources")
async def get_available_sources() -> Dict[str, List[str]]:
    """Get list of available job sources."""
    aggregator = JobAggregator()
    sources = aggregator.get_available_sources()
    
    return {
        "sources": sources,
        "total": len(sources),
    }


@router.get("/recent")
async def get_recent_jobs(
    days: int = Query(7, description="Number of days to look back"),
    limit: int = Query(50, description="Maximum number of results"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get recent jobs from the database."""
    try:
        logger.info(f"Getting recent jobs from last {days} days")
        
        job_repository = JobRepository(db)
        jobs = job_repository.get_recent_jobs(days=days, limit=limit)
        
        job_dicts = [
            {
                "job_id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "salary": job.salary,
                "url": job.url,
                "source": job.source,
                "posted_date": job.posted_date.isoformat() if job.posted_date else None,
            }
            for job in jobs
        ]
        
        return {
            "jobs": job_dicts,
            "total": len(job_dicts),
            "days": days,
        }
        
    except Exception as e:
        logger.error(f"Error getting recent jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
