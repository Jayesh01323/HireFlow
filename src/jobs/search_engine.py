"""
Job Search Engine Module

Provides advanced search capabilities for job postings.
Supports filtering, sorting, and relevance scoring with database integration.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from sqlalchemy.orm import Session

from src.database.job_repository import JobRepository
from src.database.models import Job
from src.jobs.freshness_scorer import JobFreshnessScorer
from src.jobs.schemas import Job as JobSchema

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a job search result with relevance score."""
    
    job: Job
    relevance_score: float
    match_reasons: List[str]


class JobSearchEngine:
    """Search engine for job postings with database integration."""
    
    def __init__(
        self,
        session: Optional[Session] = None,
        mock_jobs_path: Optional[str] = None,
        use_database: bool = True,
    ) -> None:
        """Initialize job search engine.
        
        Args:
            session: SQLAlchemy database session
            mock_jobs_path: Path to mock jobs JSON file (fallback)
            use_database: Whether to use database or mock data
        """
        self.session = session
        self.mock_jobs_path = mock_jobs_path or "src/jobs/mock_jobs.json"
        self.use_database = use_database and session is not None
        self.freshness_scorer = JobFreshnessScorer()
        
        if self.use_database:
            self.job_repository = JobRepository(session)
            logger.info("JobSearchEngine initialized with database integration")
        else:
            self.jobs: List[JobSchema] = []
            self._load_mock_jobs()
            logger.info("JobSearchEngine initialized with mock data")
    
    def _load_mock_jobs(self) -> None:
        """Load mock jobs from JSON file."""
        try:
            path = Path(self.mock_jobs_path)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    jobs_data = json.load(f)
                self.jobs = [JobSchema(**job) for job in jobs_data]
                logger.info(f"Loaded {len(self.jobs)} mock jobs from {self.mock_jobs_path}")
            else:
                logger.warning(f"Mock jobs file not found: {self.mock_jobs_path}")
        except Exception as e:
            logger.error(f"Error loading mock jobs: {e}")
            self.jobs = []
    
    def search_jobs(
        self,
        query: str = "",
        skills: Optional[List[str]] = None,
        company: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        remote: Optional[bool] = None,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        sources: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[SearchResult]:
        """Search jobs with multiple filters and relevance scoring.
        
        Args:
            query: Search query for title/company
            skills: Required skills
            company: Company name filter
            description: Description keywords
            location: Location filter
            remote: Remote jobs filter
            experience: Experience level filter
            salary_min: Minimum salary filter
            sources: Job sources to include
            limit: Maximum results
            
        Returns:
            List of SearchResult objects with relevance scores
        """
        if self.use_database:
            return self._search_database(
                query=query,
                skills=skills,
                company=company,
                description=description,
                location=location,
                remote=remote,
                experience=experience,
                salary_min=salary_min,
                sources=sources,
                limit=limit,
            )
        else:
            return self._search_mock(
                query=query,
                skills=skills,
                company=company,
                description=description,
                limit=limit,
            )
    
    def _search_database(
        self,
        query: Optional[str],
        skills: Optional[List[str]],
        company: Optional[str],
        description: Optional[str],
        location: Optional[str],
        remote: Optional[bool],
        experience: Optional[str],
        salary_min: Optional[int],
        sources: Optional[List[str]],
        limit: int,
    ) -> List[SearchResult]:
        """Search jobs in database with relevance scoring."""
        jobs = self.job_repository.search_jobs(
            query=query,
            location=location,
            remote=remote,
            experience_level=experience,
            sources=sources,
            salary_min=salary_min,
            limit=limit,
        )
        
        results = []
        for job in jobs:
            score, reasons = self._calculate_relevance(
                job,
                query=query,
                skills=skills,
                company=company,
                description=description,
            )
            results.append(SearchResult(job=job, relevance_score=score, match_reasons=reasons))
        
        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results[:limit]
    
    def _search_mock(
        self,
        query: str,
        skills: Optional[List[str]],
        company: Optional[str],
        description: Optional[str],
        limit: int,
    ) -> List[SearchResult]:
        """Search mock jobs with relevance scoring."""
        results = []
        query_lower = query.lower()
        skills_lower = [s.lower() for s in (skills or [])]
        company_lower = company.lower() if company else None
        description_lower = description.lower() if description else None
        
        for job in self.jobs:
            score, reasons = self._calculate_relevance(
                job,
                query=query_lower,
                skills=skills_lower,
                company=company_lower,
                description=description_lower,
            )
            if score > 0 or not query_lower:
                results.append(SearchResult(job=job, relevance_score=score, match_reasons=reasons))
        
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]
    
    def _calculate_relevance(
        self,
        job: Job | JobSchema,
        query: Optional[str],
        skills: Optional[List[str]],
        company: Optional[str],
        description: Optional[str],
    ) -> tuple[float, List[str]]:
        """Calculate relevance score for a job.
        
        Returns:
            Tuple of (score, list of match reasons)
        """
        score = 0.0
        reasons = []
        
        # Title match (40% weight)
        if query and query in job.title.lower():
            score += 0.4
            reasons.append("Title matches search query")
        
        # Company match (25% weight)
        if company and company in job.company.lower():
            score += 0.25
            reasons.append("Company matches search")
        
        # Skills match (20% weight)
        if skills:
            job_skills = getattr(job, 'skills', [])
            if isinstance(job_skills, str):
                job_skills = json.loads(job_skills) if job_skills else []
            job_skills_lower = [s.lower() for s in job_skills]
            matched_skills = set(skills) & set(job_skills_lower)
            if matched_skills:
                score += 0.2 * (len(matched_skills) / len(skills))
                reasons.append(f"Skills match: {', '.join(matched_skills)}")
        
        # Description match (15% weight)
        if description and job.description and description in job.description.lower():
            score += 0.15
            reasons.append("Description contains keywords")
        
        return score, reasons
    
    def filter_jobs(
        self,
        jobs: List[Job] | List[JobSchema],
        location: Optional[str] = None,
        remote: Optional[bool] = None,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
    ) -> List[Job] | List[JobSchema]:
        """Filter jobs by multiple criteria."""
        filtered = jobs
        
        if location:
            location_lower = location.lower()
            filtered = [j for j in filtered if location_lower in j.location.lower()]
        
        if remote is not None:
            if remote:
                filtered = [j for j in filtered if j.is_remote]
            else:
                filtered = [j for j in filtered if not j.is_remote]
        
        if experience:
            exp_lower = experience.lower()
            filtered = [j for j in filtered if j.experience_level and exp_lower in j.experience_level.lower()]
        
        if salary_min or salary_max:
            filtered = [j for j in filtered if self._salary_in_range(j.salary, salary_min, salary_max)]
        
        return filtered
    
    def _salary_in_range(self, salary_str: Optional[str], min_val: Optional[int], max_val: Optional[int]) -> bool:
        """Check if salary string falls within range."""
        if not salary_str:
            return True
        
        try:
            import re
            numbers = re.findall(r'[\d,]+', salary_str.replace('₹', '').replace(',', '').replace('$', ''))
            if not numbers:
                return True
            
            salary_num = int(numbers[0])
            
            if min_val and salary_num < min_val:
                return False
            if max_val and salary_num > max_val:
                return False
            
            return True
        except (ValueError, IndexError):
            return True
    
    def sort_jobs(
        self,
        jobs: List[Job] | List[JobSchema],
        sort_by: str = "relevance",
        descending: bool = True,
    ) -> List[Job] | List[JobSchema]:
        """Sort jobs by specified criteria."""
        if sort_by == "freshness":
            return self._sort_by_freshness(jobs, descending)
        elif sort_by == "salary":
            return self._sort_by_salary(jobs, descending)
        elif sort_by == "date":
            return self._sort_by_date(jobs, descending)
        elif sort_by == "title":
            return sorted(jobs, key=lambda x: x.title.lower(), reverse=descending)
        else:
            return jobs
    
    def _sort_by_freshness(self, jobs: List[Job] | List[JobSchema], descending: bool = True) -> List[Job] | List[JobSchema]:
        """Sort jobs by freshness score."""
        def get_freshness(job: Job | JobSchema) -> float:
            return self.freshness_scorer.calculate_freshness_score(job)
        
        return sorted(jobs, key=get_freshness, reverse=descending)
    
    def _sort_by_salary(self, jobs: List[Job] | List[JobSchema], descending: bool = True) -> List[Job] | List[JobSchema]:
        """Sort jobs by salary."""
        def extract_salary(job: Job | JobSchema) -> int:
            if not job.salary:
                return 0
            try:
                import re
                numbers = re.findall(r'[\d,]+', job.salary.replace('₹', '').replace(',', '').replace('$', ''))
                if numbers:
                    return int(numbers[0])
                return 0
            except (ValueError, IndexError):
                return 0
        
        return sorted(jobs, key=extract_salary, reverse=descending)
    
    def _sort_by_date(self, jobs: List[Job] | List[JobSchema], descending: bool = True) -> List[Job] | List[JobSchema]:
        """Sort jobs by posted date."""
        from datetime import datetime, timedelta
        
        def get_date(job: Job | JobSchema):
            return job.posted_date if job.posted_date else datetime.now() - timedelta(days=365)
        
        return sorted(jobs, key=get_date, reverse=descending)
    
    def get_all_jobs(self, limit: int = 100) -> List[Job]:
        """Get all jobs from database or mock data."""
        if self.use_database:
            return self.job_repository.search_jobs(limit=limit)
        else:
            return self.jobs[:limit]
