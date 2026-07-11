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
    
    def __init__(self, source: str = "apify") -> None:
        """Initialize Apify connector.
        
        Args:
            source: Source name to use for job postings (e.g., "apify", "wellfound")
        """
        super().__init__(source)
        self.api_key = get_env("APIFY_API_KEY", "")
        
        # Apify actor IDs for different job sources (full actor names from Apify Store)
        self.actors = {
            "linkedin": "automation-lab/linkedin-jobs-scraper",
            "indeed": "drobnikj/indeed-scraper",
            "glassdoor": "drobnikj/glassdoor-scraper",
            "wellfound": "gio21/wellfound-jobs-scraper",
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
        logger.info(f"Searching Apify for: {query}, location: {location}, remote: {remote}, source: {self.source_name}")
        
        if not self.api_key:
            logger.warning("APIFY_API_KEY not set, skipping Apify search")
            return []
        
        try:
            from apify_client import ApifyClient
            
            client = ApifyClient(self.api_key)
            jobs: List[JobPosting] = []
            
            # Select actor based on source
            if self.source_name == "wellfound":
                actor_id = self.actors.get("wellfound", "gio21/wellfound-jobs-scraper")
                # Wellfound actor uses different input format
                run_input = {
                    "query": query,
                    "maxItems": min(limit, 500),  # Cap at 500 per actor limits
                }
                if location:
                    run_input["location"] = location
            else:
                # Default to LinkedIn for general apify source
                actor_id = self.actors.get("linkedin", "drobnikj/linkedin-jobs-scraper")
                run_input = {
                    "searchQuery": query,
                    "maxJobs": limit,
                }
                if location:
                    run_input["location"] = location
            
            logger.info(f"Running Apify actor: {actor_id} with input: {run_input}")
            
            try:
                run = client.actor(actor_id).call(run_input=run_input)
                
                # Fetch results from the run
                dataset_id = run.get("defaultDatasetId")
                if dataset_id:
                    dataset_items = client.dataset(dataset_id).list_items(limit=limit)
                    
                    for item in dataset_items.items:
                        job = self._parse_apify_item(item)
                        if job:
                            jobs.append(job)
                
                logger.info(f"Found {len(jobs)} jobs via Apify from {self.source_name}")
                
            except Exception as e:
                logger.error(f"Error running Apify actor '{actor_id}': {e}")
            
            return jobs[:limit]
            
        except ImportError:
            logger.error("Apify client not installed. Run: pip install apify_client")
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
            
            # Extract posted date if available
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
        logger.info(f"Apify get_job_details not implemented for: {job_url}")
        return None