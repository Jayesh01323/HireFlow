"""
Job Discovery Module

Aggregates, normalizes, deduplicates, ranks, and stores job postings 
from multiple sources including Apify, LinkedIn, Naukri, and others.
"""

from src.jobs.aggregator import JobAggregator
from src.jobs.deduplicator import JobDeduplicator
from src.jobs.freshness_scorer import JobFreshnessScorer
from src.jobs.normalizer import JobNormalizer
from src.jobs.pipeline_logger import (
    FailureReason,
    PipelineLogger,
    get_pipeline_logger,
    reset_pipeline_logger,
)
from src.jobs.ranking import JobRankingEngine
from src.jobs.repository import JobRepository
from src.jobs.schemas import Job, JobPosting, NormalizedJob, JobSearchQuery, JobDeduplicationKey
from src.jobs.search_engine import JobSearchEngine, SearchResult

__all__ = [
    "JobAggregator",
    "JobDeduplicator",
    "JobFreshnessScorer",
    "JobNormalizer",
    "JobRankingEngine",
    "JobRepository",
    "Job",
    "JobPosting",
    "NormalizedJob",
    "JobSearchQuery",
    "JobDeduplicationKey",
    "JobSearchEngine",
    "SearchResult",
    "FailureReason",
    "PipelineLogger",
    "get_pipeline_logger",
    "reset_pipeline_logger",
]
