"""
Job Schemas Module

Pydantic models for job postings and job-related data structures.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class JobPosting(BaseModel):
    """Represents a job posting from any source."""
    
    title: str
    company: str
    location: Optional[str] = None
    salary: Optional[str] = None
    description: Optional[str] = None
    url: str
    source: str  # linkedin, internshala, naukri, etc.
    external_id: Optional[str] = None
    is_remote: bool = False
    experience_level: Optional[str] = None
    posted_date: Optional[datetime] = None
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "salary": "$100,000 - $150,000",
                "description": "We are looking for a software engineer...",
                "url": "https://example.com/job/123",
                "source": "linkedin",
                "external_id": "123456",
                "is_remote": False,
                "experience_level": "mid",
                "posted_date": "2024-01-15T00:00:00Z",
            }
        }


class JobSearchQuery(BaseModel):
    """Query parameters for job search."""
    
    query: str
    location: Optional[str] = None
    remote: bool = False
    experience: Optional[str] = None  # entry, mid, senior
    salary_min: Optional[int] = None
    sources: Optional[list[str]] = None
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "query": "software engineer",
                "location": "San Francisco",
                "remote": False,
                "experience": "mid",
                "salary_min": 100000,
                "sources": ["linkedin", "indeed"],
            }
        }


class NormalizedJob(BaseModel):
    """Normalized job posting after processing."""
    
    title: str
    company: str
    location: Optional[str] = None
    salary: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    description: Optional[str] = None
    url: str
    source: str
    external_id: Optional[str] = None
    is_remote: bool = False
    experience_level: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    posted_date: Optional[datetime] = None
    normalized_at: datetime = Field(default_factory=datetime.utcnow)


class JobDeduplicationKey(BaseModel):
    """Key for job deduplication."""
    
    title: str
    company: str
    location: Optional[str] = None
    
    def generate_hash(self) -> str:
        """Generate hash for deduplication."""
        # TODO: Implement hash generation
        return f"{self.title}_{self.company}_{self.location or 'remote'}"
