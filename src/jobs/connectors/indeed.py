"""
Indeed Job Connector

Implementation for Indeed job scraping using web scraping.
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


class IndeedConnector(BaseJobConnector):
    """Connector for Indeed job postings."""
    
    def __init__(self) -> None:
        """Initialize Indeed connector."""
        super().__init__("indeed")
        self.base_url = "https://www.indeed.com"
        self.search_url = "https://www.indeed.com/jobs"
    
    def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        limit: int = 50,
    ) -> List[JobPosting]:
        """Search for jobs on Indeed."""
        logger.info(f"Searching Indeed for: {query}, location: {location}, remote: {remote}")
        
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
                logger.warning(f"Indeed returned status {response.status_code}")
                return jobs
            
            jobs = self._parse_job_cards(response.text)
            
            logger.info(f"Found {len(jobs)} jobs on Indeed")
            return jobs[:limit]
            
        except Exception as e:
            logger.error(f"Error searching Indeed jobs: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jobs
    
    def _build_search_params(
        self,
        query: str,
        location: Optional[str],
        remote: bool,
        experience: Optional[str],
        salary_min: Optional[int],
    ) -> Dict[str, str]:
        """Build search parameters for Indeed."""
        params = {
            "q": query,
        }
        
        if location:
            params["l"] = location
        
        if remote:
            params["remote"] = "1"
        
        if experience:
            exp_map = {
                "entry": "entry_level",
                "mid": "mid_level",
                "senior": "senior_level"
            }
            if experience in exp_map:
                params["explvl"] = exp_map[experience]
        
        if salary_min:
            params["salary"] = f"${salary_min}+"
        
        return params
    
    def _parse_job_cards(self, html: str) -> List[JobPosting]:
        """Parse job cards from Indeed response HTML."""
        jobs: List[JobPosting] = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            
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
        """Parse a single Indeed job card."""
        try:
            # Extract job title
            title_elem = card.find('h2', class_='jobTitle')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            # Extract company
            company_elem = card.find('span', {'data-testid': 'company-name'})
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            # Extract location
            location_elem = card.find('div', {'data-testid': 'text-location'})
            location = location_elem.get_text(strip=True) if location_elem else None
            
            # Extract URL
            link_elem = card.find('a', class_='jcs-JobTitle')
            url = link_elem.get('href', '') if link_elem else ""
            
            if url and not url.startswith('http'):
                url = self.base_url + url
            
            if not url:
                return None
            
            # Extract salary if available
            salary_elem = card.find('div', {'data-testid': 'salary-snippet-container'})
            salary = salary_elem.get_text(strip=True) if salary_elem else None
            
            # Extract posted date
            date_elem = card.find('span', {'data-testid': 'myJobsStateDate'})
            posted_date = self._parse_posted_date(date_elem.get_text(strip=True) if date_elem else None)
            
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
                posted_date=posted_date
            )
            
        except Exception as e:
            logger.debug(f"Error parsing single card: {e}")
            return None
    
    def _parse_posted_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse posted date string."""
        if not date_str:
            return None
        
        try:
            # Handle formats like "Posted 2 days ago", "Posted today"
            if "ago" in date_str.lower():
                if "day" in date_str.lower():
                    days = int(re.findall(r'\d+', date_str)[0])
                    return datetime.utcnow() - timedelta(days=days)
                elif "hour" in date_str.lower():
                    hours = int(re.findall(r'\d+', date_str)[0])
                    return datetime.utcnow() - timedelta(hours=hours)
            elif "today" in date_str.lower():
                return datetime.utcnow()
            
            return datetime.utcnow() - timedelta(days=7)
            
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
            desc_elem = soup.find('div', id='jobDescriptionText')
            description = desc_elem.get_text(strip=True) if desc_elem else None
            
            # Extract other details
            title_elem = soup.find('h1', class_='jobTitle')
            title = title_elem.get_text(strip=True) if title_elem else None
            
            company_elem = soup.find('div', {'data-testid': 'company-name'})
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
