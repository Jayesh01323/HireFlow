"""
Job Deduplicator Module

Identifies and removes duplicate job postings across sources.
Uses fuzzy matching and similarity algorithms to detect duplicates.
"""

from __future__ import annotations

import hashlib
import logging
from difflib import SequenceMatcher
from typing import Dict, List, Set

from src.jobs.schemas import JobDeduplicationKey, NormalizedJob

logger = logging.getLogger(__name__)


class JobDeduplicator:
    """Deduplicates job postings across sources."""
    
    def __init__(self, similarity_threshold: float = 0.85) -> None:
        """Initialize job deduplicator."""
        self.similarity_threshold = similarity_threshold
        self.seen_keys: Set[str] = set()
    
    def deduplicate_jobs(self, jobs: List[NormalizedJob]) -> List[NormalizedJob]:
        """Remove duplicate jobs from a list using fuzzy matching."""
        unique_jobs = []
        seen = set()
        duplicate_groups: Dict[str, List[NormalizedJob]] = {}
        
        for job in jobs:
            key = self._generate_deduplication_key(job)
            
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
            else:
                # Check if it's a fuzzy match with existing jobs
                is_duplicate, best_match_key = self._find_fuzzy_duplicate(job, unique_jobs)
                if is_duplicate and best_match_key:
                    if best_match_key not in duplicate_groups:
                        duplicate_groups[best_match_key] = []
                    duplicate_groups[best_match_key].append(job)
                    logger.info(f"Found duplicate: {job.title} at {job.company}")
                else:
                    # Not a true duplicate, add it
                    seen.add(key)
                    unique_jobs.append(job)
        
        # Merge information from duplicates
        for key, duplicates in duplicate_groups.items():
            if duplicates:
                # Find the original job
                original_job = next((j for j in unique_jobs if self._generate_deduplication_key(j) == key), None)
                if original_job:
                    merged_job = self._merge_duplicate_info([original_job] + duplicates)
                    # Replace original with merged
                    idx = next(i for i, j in enumerate(unique_jobs) if self._generate_deduplication_key(j) == key)
                    unique_jobs[idx] = merged_job
        
        logger.info(f"Deduplicated {len(jobs)} jobs to {len(unique_jobs)} unique jobs")
        return unique_jobs
    
    def _generate_deduplication_key(self, job: NormalizedJob) -> str:
        """Generate deduplication key for a job using title, company, and location."""
        dedup_key = JobDeduplicationKey(
            title=self._normalize_text(job.title),
            company=self._normalize_text(job.company),
            location=self._normalize_text(job.location) if job.location else None,
        )
        return dedup_key.generate_hash()
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        if not text:
            return ""
        return text.lower().strip()
    
    def _find_fuzzy_duplicate(self, job: NormalizedJob, existing_jobs: List[NormalizedJob]) -> tuple[bool, str]:
        """Find if job is a fuzzy duplicate of any existing job."""
        for existing_job in existing_jobs:
            similarity = self.calculate_similarity(job, existing_job)
            if similarity >= self.similarity_threshold:
                return True, self._generate_deduplication_key(existing_job)
        return False, None
    
    def calculate_similarity(self, job1: NormalizedJob, job2: NormalizedJob) -> float:
        """Calculate similarity score between two jobs using multiple factors."""
        # Title similarity (weighted 40%)
        title_sim = self._text_similarity(job1.title, job2.title)
        
        # Company similarity (weighted 30%)
        company_sim = self._text_similarity(job1.company, job2.company)
        
        # Location similarity (weighted 20%)
        loc1 = job1.location or ""
        loc2 = job2.location or ""
        location_sim = self._text_similarity(loc1, loc2)
        
        # URL similarity (weighted 10%)
        url_sim = self._url_similarity(job1.url, job2.url)
        
        # Weighted average
        overall_similarity = (
            title_sim * 0.4 +
            company_sim * 0.3 +
            location_sim * 0.2 +
            url_sim * 0.1
        )
        
        return overall_similarity
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using SequenceMatcher."""
        if not text1 or not text2:
            return 0.0
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _url_similarity(self, url1: str, url2: str) -> float:
        """Calculate URL similarity by comparing path components."""
        if not url1 or not url2:
            return 0.0
        
        # Extract path components
        path1 = url1.split('/')[-1] if '/' in url1 else url1
        path2 = url2.split('/')[-1] if '/' in url2 else url2
        
        # Remove query parameters
        path1 = path1.split('?')[0]
        path2 = path2.split('?')[0]
        
        if path1 == path2:
            return 1.0
        
        return SequenceMatcher(None, path1.lower(), path2.lower()).ratio()
    
    def find_duplicates(self, jobs: List[NormalizedJob]) -> Dict[str, List[NormalizedJob]]:
        """Find duplicate jobs and group them by similarity."""
        groups: Dict[str, List[NormalizedJob]] = {}
        processed = set()
        
        for i, job1 in enumerate(jobs):
            if i in processed:
                continue
            
            key = self._generate_deduplication_key(job1)
            groups[key] = [job1]
            processed.add(i)
            
            for j, job2 in enumerate(jobs[i+1:], start=i+1):
                if j in processed:
                    continue
                
                similarity = self.calculate_similarity(job1, job2)
                if similarity >= self.similarity_threshold:
                    groups[key].append(job2)
                    processed.add(j)
        
        # Filter out groups with only one job
        return {k: v for k, v in groups.items() if len(v) > 1}
    
    def merge_duplicate_info(self, jobs: List[NormalizedJob]) -> NormalizedJob:
        """Merge information from duplicate jobs, keeping the best quality data."""
        if not jobs:
            raise ValueError("Cannot merge empty job list")
        
        # Use the first job as base
        merged = jobs[0]
        
        # Merge skills (union of all skills)
        all_skills = set(merged.skills)
        for job in jobs[1:]:
            all_skills.update(job.skills)
        merged.skills = list(all_skills)
        
        # Use the job with the most complete description
        best_description = max(jobs, key=lambda j: len(j.description or ""))
        merged.description = best_description.description
        
        # Use the job with the most complete salary info
        best_salary = max(jobs, key=lambda j: (j.salary_min or 0) + (j.salary_max or 0))
        merged.salary_min = best_salary.salary_min
        merged.salary_max = best_salary.salary_max
        merged.salary = best_salary.salary
        
        # Use the most recent posted date
        best_date = max(jobs, key=lambda j: j.posted_date or "")
        merged.posted_date = best_date.posted_date
        
        return merged
    
    def _merge_duplicate_info(self, jobs: List[NormalizedJob]) -> NormalizedJob:
        """Internal method to merge duplicate information."""
        return self.merge_duplicate_info(jobs)
