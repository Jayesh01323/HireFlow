"""
Naukri Job Connector

Implementation for Naukri job scraping using web scraping.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from src.jobs.connectors.base import BaseJobConnector
from src.jobs.schemas import JobPosting

logger = logging.getLogger(__name__)


class NaukriConnector(BaseJobConnector):
    """Connector for Naukri job postings."""
    
    def __init__(self) -> None:
        """Initialize Naukri connector."""
        super().__init__("naukri")
        self.base_url = "https://www.naukri.com"
        self.search_url = "https://www.naukri.com/jobapi/v3/search"
    
    def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        limit: int = 50,
    ) -> List[JobPosting]:
        """Search for jobs on Naukri."""
        logger.info(f"Searching Naukri for: {query}, location: {location}, remote: {remote}")
        
        jobs: List[JobPosting] = []
        
        try:
            params = self._build_search_params(query, location, remote, experience, salary_min)
            
            response = requests.get(
                self.search_url,
                params=params,
                headers=self.session_headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.warning(f"Naukri API returned status {response.status_code}")
                return jobs
            
            data = response.json()
            jobs = self._parse_job_data(data)
            
            logger.info(f"Found {len(jobs)} jobs on Naukri")
            return jobs[:limit]
            
        except Exception as e:
            logger.error(f"Error searching Naukri jobs: {e}")
            return jobs
    
    def _build_search_params(
        self,
        query: str,
        location: Optional[str],
        remote: bool,
        experience: Optional[str],
        salary_min: Optional[int],
    ) -> Dict[str, Any]:
        """Build search parameters for Naukri API."""
        params = {
            "keyword": query,
            "limit": 50,
        }
        
        if location:
            params["location"] = location
        
        if remote:
            params["workMode"] = "1"  # Remote filter
        
        if experience:
            exp_map = {
                "entry": "0-1",
                "mid": "2-5",
                "senior": "5-10"
            }
            if experience in exp_map:
                params["experience"] = exp_map[experience]
        
        if salary_min:
            params["minSalary"] = str(salary_min)
        
        return params
    
    def _parse_job_data(self, data: Dict[str, Any]) -> List[JobPosting]:
        """Parse job data from Naukri API response."""
        jobs: List[JobPosting] = []
        
        try:
            job_list = data.get("jobDetails", [])
            
            for job_data in job_list:
                try:
                    job = self._parse_single_job(job_data)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.debug(f"Error parsing job: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing job data: {e}")
        
        return jobs
    
    def _parse_single_job(self, job_data: Dict[str, Any]) -> Optional[JobPosting]:
        """Parse a single job from Naukri data."""
        try:
            title = job_data.get("title", "Unknown")
            company = job_data.get("companyName", "Unknown")
            location = job_data.get("location", {}).get("label")
            url = job_data.get("jdURL", "")
            
            if not url:
                return None
            
            # Extract salary
            salary = job_data.get("salary", {}).get("label")
            
            # Extract experience
            exp_data = job_data.get("experience", {})
            experience_str = exp_data.get("label") if exp_data else None
            experience_level = self.normalize_experience(experience_str)
            
            # Extract posted date
            posted_date_str = job_data.get("postedDate")
            posted_date = self._parse_posted_date(posted_date_str)
            
            # Detect remote
            is_remote = self.detect_remote(location, job_data.get("jobDescription"))
            
            return JobPosting(
                title=title,
                company=company,
                location=location,
                salary=salary,
                description=job_data.get("jobDescription"),
                url=url,
                source=self.source_name,
                external_id=self.generate_external_id(url),
                is_remote=is_remote,
                experience_level=experience_level,
                posted_date=posted_date
            )
            
        except Exception as e:
            logger.debug(f"Error parsing single job: {e}")
            return None
    
    def _parse_posted_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse posted date string."""
        if not date_str:
            return None
        
        try:
            # Handle formats like "2 days ago", "1 week ago"
            if "ago" in date_str.lower():
                if "day" in date_str.lower():
                    days = int(re.findall(r'\d+', date_str)[0])
                    return datetime.utcnow() - timedelta(days=days)
                elif "week" in date_str.lower():
                    weeks = int(re.findall(r'\d+', date_str)[0])
                    return datetime.utcnow() - timedelta(weeks=weeks)
                elif "hour" in date_str.lower():
                    hours = int(re.findall(r'\d+', date_str)[0])
                    return datetime.utcnow() - timedelta(hours=hours)
            
            return datetime.utcnow()
            
        except Exception:
            return datetime.utcnow() - timedelta(days=7)
    
    def get_job_details(self, job_url: str) -> Optional[JobPosting]:
        """Get detailed information for a specific job."""
        try:
            response = requests.get(job_url, headers=self.session_headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch job details: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract description
            desc_elem = soup.find('div', class_='job-desc')
            description = desc_elem.get_text(strip=True) if desc_elem else None
            
            # Extract other details
            title_elem = soup.find('h1', class_='header')
            title = title_elem.get_text(strip=True) if title_elem else None
            
            company_elem = soup.find('a', class_='subTitle')
            company = company_elem.get_text(strip=True) if company_elem else None
            
            return JobPosting(
                title=title or "Unknown",
                company=company or "Unknown",
                location=None,
                salary=None,
                description=self.clean_description(description),
                url=job_url,
                source=self.source_name,
                external_id=self.generate_external_id(job_url),
                is_remote=False,
                experience_level=None,
                posted_date=None
            )
            
        except Exception as e:
            logger.error(f"Error fetching job details: {e}")
            return None
