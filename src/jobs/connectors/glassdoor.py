"""
Glassdoor Job Connector

Finds Glassdoor job postings through Google Jobs, using the Apify actor
johnvc/Google-Jobs-Scraper. Google lists every place a job can be applied to;
this connector keeps the jobs that can be applied to on Glassdoor and links to
the Glassdoor posting.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from src.jobs.connectors.base import BaseJobConnector
from src.jobs.schemas import JobPosting
from src.utils import get_env, load_env

load_env()

logger = logging.getLogger(__name__)


class GlassdoorConnector(BaseJobConnector):
    """Connector for Glassdoor job postings via Apify (Google Jobs)."""
    
    def __init__(self) -> None:
        """Initialize Glassdoor connector."""
        super().__init__("glassdoor")
        self.api_key = get_env("APIFY_API_KEY", "")
        self.actor_id = "johnvc/Google-Jobs-Scraper"
    
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
            
            # Roughly a quarter of Google Jobs results can be applied to on Glassdoor
            run_input = {
                "query": query,
                "num_results": min(limit * 4, 100),
            }
            
            if location:
                run_input["location"] = location
            
            logger.info(f"Running Apify actor {self.actor_id} with input: {run_input}")
            
            run = client.actor(self.actor_id).call(run_input=run_input)
            if not isinstance(run, dict):  # apify-client 3.x returns a model
                run = run.model_dump(by_alias=True)
            
            dataset_id = run.get("defaultDatasetId")
            if dataset_id:
                dataset_items = client.dataset(dataset_id).list_items()
                
                for item in dataset_items.items:
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
        """Parse a Google Jobs row into JobPosting, if the job can be applied to on Glassdoor."""
        try:
            url = next(
                (
                    option.get("link")
                    for option in item.get("apply_options") or []
                    if "glassdoor." in (option.get("link") or "")
                ),
                None,
            )
            if not url:
                return None
            
            title = item.get("title") or "Unknown"
            company = item.get("company_name") or "Unknown"
            location = item.get("location") or ""
            description = item.get("description") or ""
            
            # Google Jobs puts salary, age and job type in "extensions",
            # e.g. ["3 days ago", "₹15L–₹21L a year", "Full–time"]
            extensions = [str(e) for e in item.get("extensions") or []]
            posted_ago = next((e for e in extensions if e.endswith(" ago")), None)
            salary = next(
                (e for e in extensions if e != posted_ago and re.search(r"\b(a|an) (year|month|week|day|hour)\b", e)),
                None,
            )
            
            is_remote = "Work from home" in extensions or self.detect_remote(location, description)
            
            external_id = self.generate_external_id(url)
            
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
                posted_date=self._parse_posted_ago(posted_ago),
            )
            
        except Exception as e:
            logger.debug(f"Error parsing Apify item: {e}")
            return None
    
    @staticmethod
    def _parse_posted_ago(text: Optional[str]) -> Optional[datetime]:
        """Turn a Google Jobs age such as "3 days ago" into a naive UTC datetime."""
        match = re.match(r"(\d+)\+?\s+(hour|day|week|month)s?\s+ago", text or "")
        if not match:
            return None
        days_per_unit = {"hour": 1 / 24, "day": 1, "week": 7, "month": 30}[match.group(2)]
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return now - timedelta(days=int(match.group(1)) * days_per_unit)
    
    def get_job_details(self, job_url: str) -> Optional[JobPosting]:
        """Get detailed information for a specific job."""
        logger.info(f"Glassdoor get_job_details not implemented for: {job_url}")
        return None
