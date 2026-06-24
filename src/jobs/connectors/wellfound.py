"""
Wellfound Job Connector

Implementation for Wellfound (formerly AngelList) job scraping using web scraping.
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


class WellfoundConnector(BaseJobConnector):
    """Connector for Wellfound job postings."""
    
    def __init__(self) -> None:
        """Initialize Wellfound connector."""
        super().__init__("wellfound")
        self.base_url = "https://wellfound.com"
        self.search_url = "https://wellfound.com/jobs"
    
    def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        limit: int = 50,
    ) -> List[JobPosting]:
        """Search for jobs on Wellfound."""
        logger.info(f"Searching Wellfound for: {query}, location: {location}, remote: {remote}")
        
        jobs: List[JobPosting] = []
        
        try:
            params = self._build_search_params(query, location, remote, experience)
            
            response = requests.get(
                self.search_url,
                params=params,
                headers=self.session_headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.warning(f"Wellfound returned status {response.status_code}")
                return jobs
            
            jobs = self._parse_job_cards(response.text)
            
            logger.info(f"Found {len(jobs)} jobs on Wellfound")
            return jobs[:limit]
            
        except Exception as e:
            logger.error(f"Error searching Wellfound jobs: {e}")
            return jobs
    
    def _build_search_params(
        self,
        query: str,
        location: Optional[str],
        remote: bool,
        experience: Optional[str],
    ) -> Dict[str, str]:
        """Build search parameters for Wellfound."""
        params = {
            "q": query,
        }
        
        if location:
            params["l"] = location
        
        if remote:
            params["remote"] = "1"
        
        if experience:
            exp_map = {
                "entry": "junior",
                "mid": "mid",
                "senior": "senior"
            }
            if experience in exp_map:
                params["experience"] = exp_map[experience]
        
        return params
    
    def _parse_job_cards(self, html: str) -> List[JobPosting]:
        """Parse job cards from Wellfound response HTML."""
        jobs: List[JobPosting] = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            job_cards = soup.find_all('div', class_='job-item')
            
            for card in job_cards:
                try:
                    job = self._parse_single_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.debug(f"Error parsing job card: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing job cards: {e}")
        
        return jobs
    
    def _parse_single_card(self, card: Any) -> Optional[JobPosting]:
        """Parse a single Wellfound job card."""
        try:
            # Extract job title
            title_elem = card.find('h3', class_='job-title')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            # Extract company
            company_elem = card.find('span', class_='company-name')
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            # Extract location
            location_elem = card.find('span', class_='location')
            location = location_elem.get_text(strip=True) if location_elem else None
            
            # Extract URL
            link_elem = card.find('a', class_='job-link')
            url = link_elem.get('href', '') if link_elem else ""
            
            if url and not url.startswith('http'):
                url = self.base_url + url
            
            if not url:
                return None
            
            # Extract salary if available
            salary_elem = card.find('span', class_='salary')
            salary = salary_elem.get_text(strip=True) if salary_elem else None
            
            # Detect remote
            is_remote = self.detect_remote(location, None)
            
            return JobPosting(
                title=title,
                company=company,
                location=location,
                salary=salary,
                description=None,
                url=url,
                source=self.source_name,
                external_id=self.generate_external_id(url),
                is_remote=is_remote,
                experience_level=None,
                posted_date=datetime.utcnow()
            )
            
        except Exception as e:
            logger.debug(f"Error parsing single card: {e}")
            return None
    
    def get_job_details(self, job_url: str) -> Optional[JobPosting]:
        """Get detailed information for a specific job."""
        try:
            response = requests.get(job_url, headers=self.session_headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch job details: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract description
            desc_elem = soup.find('div', class_='job-description')
            description = desc_elem.get_text(strip=True) if desc_elem else None
            
            # Extract other details
            title_elem = soup.find('h1', class_='job-title')
            title = title_elem.get_text(strip=True) if title_elem else None
            
            company_elem = soup.find('span', class_='company-name')
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
