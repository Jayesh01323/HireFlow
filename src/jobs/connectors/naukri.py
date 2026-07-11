"""
Naukri Job Connector

Uses web scraping for Naukri job postings.
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
        self.search_url = "https://www.naukri.com/jobs"
    
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
            url = self._build_search_url(query, location, remote, experience, salary_min)
            
            response = requests.get(url, headers=self.session_headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Naukri returned status {response.status_code}")
                return jobs
            
            jobs = self._parse_job_cards(response.text)
            
            logger.info(f"Found {len(jobs)} jobs on Naukri")
            return jobs[:limit]
            
        except Exception as e:
            logger.error(f"Error searching Naukri jobs: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jobs
    
    def _build_search_url(
        self,
        query: str,
        location: Optional[str],
        remote: bool,
        experience: Optional[str],
        salary_min: Optional[int],
    ) -> str:
        """Build search URL for Naukri."""
        from urllib.parse import quote
        
        url = f"{self.search_url}/{quote(query)}"
        
        params = []
        
        if location:
            params.append(f"location={quote(location)}")
        
        if remote:
            params.append("remote=1")
        
        if experience:
            exp_map = {
                "entry": "0-1",
                "mid": "2-5",
                "senior": "5-10"
            }
            if experience in exp_map:
                params.append(f"experience={exp_map[experience]}")
        
        if salary_min:
            params.append(f"salary={salary_min}")
        
        if params:
            url += "?" + "&".join(params)
        
        return url
    
    def _parse_job_cards(self, html: str) -> List[JobPosting]:
        """Parse job cards from Naukri HTML response."""
        jobs: List[JobPosting] = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            job_cards = soup.find_all('div', class_='srp-jobtuple')
            
            if not job_cards:
                job_cards = soup.find_all('div', class_='jobTuple')
            
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
        """Parse a single Naukri job card."""
        try:
            title_elem = card.find('a', class_='title')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            company_elem = card.find('a', class_='subTitle')
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            location_elem = card.find('span', class_='locWdth')
            location = location_elem.get_text(strip=True) if location_elem else None
            
            link_elem = card.find('a', class_='title')
            url = link_elem.get('href', '') if link_elem else ""
            
            if not url:
                return None
            
            if url.startswith('/'):
                url = self.base_url + url
            
            experience_elem = card.find('span', class_='expwdth')
            experience_str = experience_elem.get_text(strip=True) if experience_elem else None
            experience_level = self.normalize_experience(experience_str)
            
            salary_elem = card.find('span', class_='salwdth')
            salary = salary_elem.get_text(strip=True) if salary_elem else None
            
            posted_date_elem = card.find('div', class_='job-post-day')
            posted_date_str = posted_date_elem.get_text(strip=True) if posted_date_elem else None
            posted_date = self._parse_posted_date(posted_date_str)
            
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
                experience_level=experience_level,
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
