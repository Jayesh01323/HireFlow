"""
Internshala Job Connector

Implementation for Internshala job scraping using web scraping.
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


class InternshalaConnector(BaseJobConnector):
    """Connector for Internshala job postings."""
    
    def __init__(self) -> None:
        """Initialize Internshala connector."""
        super().__init__("internshala")
        self.base_url = "https://internshala.com"
        self.search_url = "https://internshala.com/internships"
    
    def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        limit: int = 50,
    ) -> List[JobPosting]:
        """Search for jobs on Internshala."""
        logger.info(f"Searching Internshala for: {query}, location: {location}, remote: {remote}")
        
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
                logger.warning(f"Internshala returned status {response.status_code}")
                return jobs
            
            jobs = self._parse_job_cards(response.text)
            
            logger.info(f"Found {len(jobs)} jobs on Internshala")
            return jobs[:limit]
            
        except Exception as e:
            logger.error(f"Error searching Internshala jobs: {e}")
            return jobs
    
    def _build_search_params(
        self,
        query: str,
        location: Optional[str],
        remote: bool,
        experience: Optional[str],
    ) -> Dict[str, str]:
        """Build search parameters for Internshala."""
        params = {
            "keywords": query,
        }
        
        if location:
            params["location"] = location
        
        if remote:
            params["work_from_home"] = "1"
        
        return params
    
    def _parse_job_cards(self, html: str) -> List[JobPosting]:
        """Parse job cards from Internshala response HTML."""
        jobs: List[JobPosting] = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            job_cards = soup.find_all('div', class_='individual_internship')
            
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
        """Parse a single Internshala job card."""
        try:
            # Extract job title
            title_elem = card.find('h3', class_='heading_4_5')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            # Extract company
            company_elem = card.find('a', class_='link_display_like_text')
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            # Extract location
            location_elem = card.find('a', id='location_names')
            location = location_elem.get_text(strip=True) if location_elem else None
            
            # Extract URL
            link_elem = card.find('a', class_='view_detail_button')
            url = link_elem.get('href', '') if link_elem else ""
            
            if url and not url.startswith('http'):
                url = self.base_url + url
            
            if not url:
                return None
            
            # Extract stipend (salary)
            stipend_elem = card.find('span', class_='stipend')
            salary = stipend_elem.get_text(strip=True) if stipend_elem else None
            
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
                experience_level="entry",  # Internships are typically entry-level
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
            desc_elem = soup.find('div', class_='internship_details')
            description = desc_elem.get_text(strip=True) if desc_elem else None
            
            # Extract other details
            title_elem = soup.find('h1', class_='heading_4_5')
            title = title_elem.get_text(strip=True) if title_elem else None
            
            company_elem = soup.find('a', class_='link_display_like_text')
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
                experience_level="entry",
                posted_date=None
            )
            
        except Exception as e:
            logger.error(f"Error fetching job details: {e}")
            return None
