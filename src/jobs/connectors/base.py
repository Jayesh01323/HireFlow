"""
Base Job Connector Module

Abstract base class for all job source connectors.
Defines the interface that all job connectors must implement.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.jobs.schemas import JobPosting

logger = logging.getLogger(__name__)


class BaseJobConnector(ABC):
    """Abstract base class for job source connectors."""
    
    def __init__(self, source_name: str) -> None:
        """Initialize base connector.
        
        Args:
            source_name: Name of the job source (e.g., 'linkedin', 'naukri')
        """
        self.source_name = source_name
        self.base_url: str = ""
        self.session_headers: Dict[str, str] = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    
    @abstractmethod
    def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        limit: int = 50,
    ) -> List[JobPosting]:
        """Search for jobs from this source.
        
        Args:
            query: Job search query (e.g., 'software engineer')
            location: Job location filter
            remote: Filter for remote jobs only
            experience: Experience level filter (entry, mid, senior)
            salary_min: Minimum salary filter
            limit: Maximum number of jobs to return
            
        Returns:
            List of JobPosting objects
        """
        pass
    
    @abstractmethod
    def get_job_details(self, job_url: str) -> Optional[JobPosting]:
        """Get detailed information for a specific job.
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            JobPosting object with full details or None if not found
        """
        pass
    
    def normalize_experience(self, experience: Optional[str]) -> Optional[str]:
        """Normalize experience level to standard values.
        
        Args:
            experience: Experience level string from source
            
        Returns:
            Normalized experience level (entry, mid, senior) or None
        """
        if not experience:
            return None
        
        exp_lower = experience.lower()
        
        # Entry level patterns
        if any(term in exp_lower for term in ['entry', 'junior', 'intern', 'trainee', '0-1', '0-2', 'fresher']):
            return 'entry'
        
        # Mid level patterns
        if any(term in exp_lower for term in ['mid', 'middle', 'intermediate', '2-5', '3-5', '1-3']):
            return 'mid'
        
        # Senior level patterns
        if any(term in exp_lower for term in ['senior', 'lead', 'principal', '5+', '5-10', '8+']):
            return 'senior'
        
        return None
    
    def extract_salary_range(self, salary_str: Optional[str]) -> tuple[Optional[int], Optional[int]]:
        """Extract minimum and maximum salary from salary string.
        
        Args:
            salary_str: Salary string from source
            
        Returns:
            Tuple of (salary_min, salary_max) or (None, None)
        """
        if not salary_str:
            return None, None
        
        import re
        
        # Remove currency symbols and extract numbers
        cleaned = re.sub(r'[^\d.,-]', ' ', salary_str)
        numbers = re.findall(r'[\d,]+', cleaned.replace(',', ''))
        
        if not numbers:
            return None, None
        
        nums = [int(n) for n in numbers]
        
        if len(nums) == 1:
            return nums[0], None
        elif len(nums) >= 2:
            return min(nums), max(nums)
        
        return None, None
    
    def detect_remote(self, location: Optional[str], description: Optional[str]) -> bool:
        """Detect if job is remote based on location and description.
        
        Args:
            location: Job location string
            description: Job description string
            
        Returns:
            True if job appears to be remote
        """
        if not location and not description:
            return False
        
        remote_keywords = [
            'remote', 'work from home', 'wfh', 'telecommute',
            'virtual', 'distributed', 'anywhere', 'location independent'
        ]
        
        text_to_check = ' '.join(filter(None, [location or '', description or '']))
        text_lower = text_to_check.lower()
        
        return any(keyword in text_lower for keyword in remote_keywords)
    
    def generate_external_id(self, url: str) -> str:
        """Generate external ID from job URL.
        
        Args:
            url: Job URL
            
        Returns:
            External ID string
        """
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:16]
    
    def clean_description(self, description: Optional[str]) -> Optional[str]:
        """Clean and normalize job description.
        
        Args:
            description: Raw description string
            
        Returns:
            Cleaned description string
        """
        if not description:
            return None
        
        # Remove excessive whitespace
        import re
        cleaned = re.sub(r'\s+', ' ', description).strip()
        
        # Limit length
        if len(cleaned) > 10000:
            cleaned = cleaned[:10000] + '...'
        
        return cleaned
