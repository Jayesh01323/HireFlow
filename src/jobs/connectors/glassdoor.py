"""
Glassdoor Job Connector

Uses Apify actor for reliable Glassdoor job scraping.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from src.jobs.connectors.base import BaseJobConnector
from src.jobs.schemas import JobPosting
from src.utils import get_env, load_env

load_env()

logger = logging.getLogger(__name__)


class GlassdoorConnector(BaseJobConnector):
    """Connector for Glassdoor job postings via Apify."""
    
    def __init__(self) -> None:
        """Initialize Glassdoor connector."""
        super().__init__("glassdoor")
        self.api_key = get_env("APIFY_API_KEY", "")
        self.actor_id = "drobnikj/glassdoor-scraper"
    
    def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        limit: int = 50,
    ) -> List[JobPosting]:
        """Search for jobs on Glassdoor via Apify."""
        logger.info(f"Searching Glassdoor via Apify for: {query}, location: {location}, remote: {remote}")
        
        if not self.api_key:
            logger.warning("APIFY_API_KEY not set, skipping Glassdoor search")
            return []
        
        jobs: List[JobPosting] = []
        
        try:
            from apify_client import ApifyClient
            
            client = ApifyClient(self.api_key)
            
            run_input = {
                "query": query,
                "maxItems": limit,
            }
            
            if location:
                run_input["location"] = location
            
            logger.info(f"Running Apify actor {self.actor_id} with input: {run_input}")
            
            run = client.actor(self.actor_id).call(run_input=run_input)
            
            dataset_id = run.get("defaultDatasetId")
            if dataset_id:
                dataset_items = client.dataset(dataset_id).list_items(limit=limit)
                
                for item in dataset_items.get("items", []):
                    job = self._parse_apify_item(item)
                    if job:
                        jobs.append(job)
            
            logger.info(f"Found {len(jobs)} jobs via Glassdoor Apify connector")
            return jobs[:limit]
            
        except ImportError:
            logger.error("Apify client not installed. Run: pip install apify_client")
            return []
        except Exception as e:
            logger.error(f"Error searching Glassdoor jobs via Apify: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def _parse_apify_item(self, item: Dict[str, Any]) -> Optional[JobPosting]:
        """Parse an Apify dataset item into JobPosting."""
        try:
            title = item.get("title") or item.get("positionName", "Unknown")
            company = item.get("company") or item.get("companyName", "Unknown")
            location = item.get("location") or item.get("jobLocation", "")
            url = item.get("url") or item.get("jobUrl", "")
            description = item.get("description") or item.get("jobDescription", "")
            
            salary = item.get("salary") or item.get("salaryText")
            
            is_remote = self.detect_remote(location, description)
            
            external_id = self.generate_external_id(url) if url else ""
            
            posted_date_str = item.get("postedDate") or item.get("postDate") or item.get("datePosted")
            posted_date = None
            if posted_date_str:
                try:
                    from datetime import datetime
                    posted_date = datetime.fromisoformat(posted_date_str.replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
            
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
                posted_date=posted_date,
            )
            
        except Exception as e:
            logger.debug(f"Error parsing Apify item: {e}")
            return None
    
    def get_job_details(self, job_url: str) -> Optional[JobPosting]:
        """Get detailed information for a specific job."""
        logger.info(f"Glassdoor get_job_details not implemented for: {job_url}")
        return None
