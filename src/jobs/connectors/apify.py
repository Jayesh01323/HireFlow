"""
Apify Job Connector

Uses Apify actors to scrape job postings from multiple sources.
Provides reliable job data extraction without manual web scraping.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from src.jobs.connectors.base import BaseJobConnector
from src.jobs.schemas import JobPosting
from src.utils import get_env, load_env

load_env()

logger = logging.getLogger(__name__)


class ApifyConnector(BaseJobConnector):
    """Connector for Apify-based job scraping."""
    
    def __init__(self) -> None:
        """Initialize Apify connector."""
        super().__init__("apify")
        self.api_key = get_env("APIFY_API_KEY", "")
        
        # Apify actor IDs for different job sources
        self.actors = {
            "linkedin": "linkedin-jobs-scraper",
            "indeed": "indeed-scraper",
            "glassdoor": "glassdoor-scraper",
        }
    
    def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        limit: int = 50,
    ) -> List[JobPosting]:
        """Search for jobs using Apify actors."""
        logger.info(f"Searching Apify for: {query}, location: {location}, remote: {remote}")
        
        if not self.api_key:
            logger.warning("APIFY_API_KEY not set, skipping Apify search")
            return []
        
        try:
            from apify_client import ApifyClient
            
            client = ApifyClient(self.api_key)
            jobs: List[JobPosting] = []
            
            # Use LinkedIn scraper as primary source
            actor_id = self.actors.get("linkedin", "linkedin-jobs-scraper")
            
            run_input = {
                "query": query,
                "maxItems": limit,
            }
            
            if location:
                run_input["location"] = location
            
            if remote:
                run_input["filters"] = ["remote"]
            
            logger.info(f"Running Apify actor: {actor_id} with input: {run_input}")
            
            try:
                run = client.actor(actor_id).call(run_input=run_input)
                
                # Fetch results from the run
                dataset_id = run.get("defaultDatasetId")
                if dataset_id:
                    dataset_items = client.dataset(dataset_id).list_items(limit=limit)
                    
                    for item in dataset_items.get("items", []):
                        job = self._parse_apify_item(item)
                        if job:
                            jobs.append(job)
                
                logger.info(f"Found {len(jobs)} jobs via Apify")
                
            except Exception as e:
                logger.error(f"Error running Apify actor: {e}")
            
            return jobs[:limit]
            
        except ImportError:
            logger.error("Apify client not installed. Run: pip install apify")
            return []
        except Exception as e:
            logger.error(f"Error searching Apify jobs: {e}")
            return []
    
    def _parse_apify_item(self, item: Dict[str, Any]) -> Optional[JobPosting]:
        """Parse an Apify dataset item into JobPosting."""
        try:
            # Extract common fields from Apify response
            title = item.get("title") or item.get("positionName", "Unknown")
            company = item.get("company") or item.get("companyName", "Unknown")
            location = item.get("location") or item.get("jobLocation", "")
            url = item.get("url") or item.get("jobUrl", "")
            description = item.get("description") or item.get("jobDescription", "")
            
            # Extract salary if available
            salary = item.get("salary") or item.get("salaryText")
            
            # Detect remote
            is_remote = self.detect_remote(location, description)
            
            # Generate external ID from URL
            external_id = self.generate_external_id(url) if url else ""
            
            return JobPosting(
                title=title,
                company=company,
                location=location,
                salary=salary,
                description=self.clean_description(description),
                url=url,
                source=self.source_name,
                external_id=external_id,
                is_remote=is_remote,
                experience_level=None,
                posted_date=None,
            )
            
        except Exception as e:
            logger.debug(f"Error parsing Apify item: {e}")
            return None
    
    def get_job_details(self, job_url: str) -> Optional[JobPosting]:
        """Get detailed information for a specific job."""
        # Apify scrapers typically return full details in search
        # This method can be implemented if needed for individual job fetching
        logger.info(f"Apify get_job_details not implemented for: {job_url}")
        return None
