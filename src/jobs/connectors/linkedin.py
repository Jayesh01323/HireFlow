"""
LinkedIn Job Connector

Implementation for LinkedIn job scraping using public job search API.
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


class LinkedInConnector(BaseJobConnector):
    """Connector for LinkedIn job postings."""
    
    def __init__(self) -> None:
        """Initialize LinkedIn connector."""
        super().__init__("linkedin")
        self.base_url = "https://www.linkedin.com/jobs/search"
        self.api_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    
    def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        limit: int = 50,
    ) -> List[JobPosting]:
        """Search for jobs on LinkedIn."""
        logger.info(f"Searching LinkedIn for: {query}, location: {location}, remote: {remote}")
        
        jobs: List[JobPosting] = []
        start = 0
        
        try:
            while len(jobs) < limit:
                params = self._build_search_params(query, location, remote, experience, salary_min, start)
                
                response = requests.get(
                    self.api_url,
                    params=params,
                    headers=self.session_headers,
                    timeout=10
                )
                
                if response.status_code != 200:
                    logger.warning(f"LinkedIn API returned status {response.status_code}")
                    break
                
                batch_jobs = self._parse_job_cards(response.text)
                if not batch_jobs:
                    break
                
                jobs.extend(batch_jobs)
                start += 25
                
                if len(batch_jobs) < 25:
                    break
            
            logger.info(f"Found {len(jobs)} jobs on LinkedIn")
            return jobs[:limit]
            
        except Exception as e:
            logger.error(f"Error searching LinkedIn jobs: {e}")
            return jobs
    
    def _build_search_params(
        self,
        query: str,
        location: Optional[str],
        remote: bool,
        experience: Optional[str],
        salary_min: Optional[int],
        start: int,
    ) -> Dict[str, str]:
        """Build search parameters for LinkedIn API."""
        params = {
            "keywords": query,
            "start": str(start),
            "f_LPR": "8",  # Remote jobs filter if remote=True
        }
        
        if location:
            params["location"] = location
        
        if not remote:
            params.pop("f_LPR", None)
        
        if experience:
            exp_map = {
                "entry": "1",
                "mid": "2",
                "senior": "3"
            }
            if experience in exp_map:
                params["f_E"] = exp_map[experience]
        
        return params
    
    def _parse_job_cards(self, html: str) -> List[JobPosting]:
        """Parse job cards from LinkedIn response HTML."""
        jobs: List[JobPosting] = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            job_cards = soup.find_all('li', class_='occludable-update')
            
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
        """Parse a single LinkedIn job card."""
        try:
            # Extract job title
            title_elem = card.find('h3', class_='base-search-card__title')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            # Extract company
            company_elem = card.find('h4', class_='base-search-card__subtitle')
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            # Extract location
            location_elem = card.find('span', class_='job-search-card__location')
            location = location_elem.get_text(strip=True) if location_elem else None
            
            # Extract URL
            link_elem = card.find('a', class_='base-card__full-link')
            url = link_elem.get('href', '') if link_elem else ""
            
            if not url:
                return None
            
            # Extract posted date
            time_elem = card.find('time', class_='job-search-card__listdate')
            posted_date = None
            if time_elem and time_elem.get('datetime'):
                try:
                    posted_date = datetime.fromisoformat(time_elem['datetime'].replace('Z', '+00:00'))
                except:
                    posted_date = datetime.utcnow() - timedelta(days=7)
            
            # Detect remote
            is_remote = self.detect_remote(location, None)
            
            return JobPosting(
                title=title,
                company=company,
                location=location,
                salary=None,
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
    
    def get_job_details(self, job_url: str) -> Optional[JobPosting]:
        """Get detailed information for a specific job."""
        try:
            response = requests.get(job_url, headers=self.session_headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch job details: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract description
            desc_elem = soup.find('div', class_='show-more-less-html__markup')
            description = desc_elem.get_text(strip=True) if desc_elem else None
            
            # Extract salary if available
            salary_elem = soup.find('span', class_='compensation__salary')
            salary = salary_elem.get_text(strip=True) if salary_elem else None
            
            # Extract other details from the page
            title_elem = soup.find('h1', class_='top-card-layout__title')
            title = title_elem.get_text(strip=True) if title_elem else None
            
            company_elem = soup.find('span', class_='topcard__flavor--company')
            company = company_elem.get_text(strip=True) if company_elem else None
            
            return JobPosting(
                title=title or "Unknown",
                company=company or "Unknown",
                location=None,
                salary=salary,
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
