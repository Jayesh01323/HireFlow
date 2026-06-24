"""
Debug script for Job Discovery pipeline - tests each component systematically.
"""
import sys
import os
import json
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')

print("=" * 60)
print("JOB DISCOVERY DEBUG SCRIPT")
print("=" * 60)

# STEP 1: Check .env
print("\n[STEP 1] Environment Variables")
from src.utils import load_env, get_env
load_env()
print(f"  APIFY_API_KEY: {'SET' if get_env('APIFY_API_KEY') else 'NOT SET'}")
print(f"  DATABASE_PATH: {get_env('DATABASE_PATH', 'NOT SET')}")
print(f"  GEMINI_API_KEY: {'SET' if get_env('GEMINI_API_KEY') else 'NOT SET'}")

# STEP 2: Test imports
print("\n[STEP 2] Testing Imports")
failed_imports = []
try:
    from src.jobs.schemas import JobPosting, NormalizedJob, Job
    print("  ✅ src.jobs.schemas")
except Exception as e:
    failed_imports.append(f"schemas: {e}")
    print(f"  ❌ src.jobs.schemas: {e}")

try:
    from src.jobs.normalizer import JobNormalizer
    print("  ✅ src.jobs.normalizer")
except Exception as e:
    failed_imports.append(f"normalizer: {e}")
    print(f"  ❌ src.jobs.normalizer: {e}")

try:
    from src.jobs.deduplicator import JobDeduplicator
    print("  ✅ src.jobs.deduplicator")
except Exception as e:
    failed_imports.append(f"deduplicator: {e}")
    print(f"  ❌ src.jobs.deduplicator: {e}")

try:
    from src.jobs.freshness_scorer import JobFreshnessScorer
    print("  ✅ src.jobs.freshness_scorer")
except Exception as e:
    failed_imports.append(f"freshness_scorer: {e}")
    print(f"  ❌ src.jobs.freshness_scorer: {e}")

try:
    from src.jobs.ranking import JobRankingEngine
    print("  ✅ src.jobs.ranking")
except Exception as e:
    failed_imports.append(f"ranking: {e}")
    print(f"  ❌ src.jobs.ranking: {e}")

try:
    from src.jobs.repository import JobRepository
    print("  ✅ src.jobs.repository")
except Exception as e:
    failed_imports.append(f"repository: {e}")
    print(f"  ❌ src.jobs.repository: {e}")

try:
    from src.jobs.aggregator import JobAggregator
    print("  ✅ src.jobs.aggregator")
except Exception as e:
    failed_imports.append(f"aggregator: {e}")
    print(f"  ❌ src.jobs.aggregator: {e}")

# Connectors
for connector_name in ['apify', 'base', 'foundit', 'internshala', 'linkedin', 'naukri', 'wellfound', 'cutshort', 'glassdoor', 'indeed', 'unstop']:
    try:
        __import__(f'src.jobs.connectors.{connector_name}')
        print(f"  ✅ src.jobs.connectors.{connector_name}")
    except Exception as e:
        failed_imports.append(f"connectors.{connector_name}: {e}")
        print(f"  ❌ src.jobs.connectors.{connector_name}: {e}")

# Services used by discovery page
for svc in ['job_discovery_service', 'ranking_engine', 'saved_jobs_service', 'skill_gap_engine', 'roadmap_engine', 'job_intelligence_service', 'skill_categorizer']:
    try:
        __import__(f'src.services.{svc}')
        print(f"  ✅ src.services.{svc}")
    except Exception as e:
        failed_imports.append(f"services.{svc}: {e}")
        print(f"  ❌ src.services.{svc}: {e}")

if failed_imports:
    print(f"\n  FAILED IMPORTS: {len(failed_imports)}")
    for fi in failed_imports:
        print(f"    - {fi}")

# STEP 3: Initialize JobAggregator
print("\n[STEP 3] Initializing JobAggregator")
try:
    agg = JobAggregator()
    print(f"  ✅ Aggregator initialized")
    print(f"  Connectors: {list(agg.connectors.keys())}")
except Exception as e:
    print(f"  ❌ Aggregator init failed: {e}")
    import traceback
    traceback.print_exc()

# STEP 4: Test mock jobs loading
print("\n[STEP 4] Testing mock job loading")
try:
    mock_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'jobs', 'mock_jobs.json')
    print(f"  Mock file exists: {os.path.exists(mock_path)}")
    if os.path.exists(mock_path):
        with open(mock_path, 'r') as f:
            mock_data = json.load(f)
        print(f"  Mock jobs count: {len(mock_data)}")
        print(f"  First mock job: {mock_data[0]['title']} @ {mock_data[0]['company']}")
except Exception as e:
    print(f"  ❌ Mock job loading failed: {e}")

# STEP 5: Test Apify connector
print("\n[STEP 5] Testing Apify Connector")
try:
    from src.jobs.connectors.apify import ApifyConnector
    apify = ApifyConnector()
    print(f"  API Key set: {bool(apify.api_key)}")
    print(f"  Actors: {apify.actors}")
    
    apify_jobs = apify.search_jobs(query="Python Developer", location="India", limit=5)
    print(f"  Jobs returned: {len(apify_jobs)}")
    if apify_jobs:
        print(f"  First job: {apify_jobs[0].title} @ {apify_jobs[0].company}")
except Exception as e:
    print(f"  ❌ Apify connector: {e}")
    import traceback
    traceback.print_exc()

# STEP 6: Test overall search
print("\n[STEP 6] Testing full search pipeline")
try:
    results = agg.search_jobs(query="Python Developer", location="India", limit=10)
    print(f"  Total results: {len(results)}")
    if results:
        for i, r in enumerate(results[:3]):
            job = r["job"]
            print(f"  [{i+1}] {job.title} @ {job.company} ({job.source}) - Score: {r.get('overall_score', 'N/A')}")
    else:
        print("  ⚠️ No results returned")
except Exception as e:
    print(f"  ❌ Search failed: {e}")
    import traceback
    traceback.print_exc()

# STEP 7: Test saved jobs service
print("\n[STEP 7] Saved Jobs Service")
try:
    from src.services.saved_jobs_service import SavedJobsService
    svc = SavedJobsService()
    saved = svc.get_saved_jobs()
    print(f"  Saved jobs count: {len(saved)}")
    print(f"  Table exists and accessible")
except Exception as e:
    print(f"  ❌ Saved jobs service: {e}")
    import traceback
    traceback.print_exc()

# STEP 8: Check the Job schema vs what saved_jobs_service expects
print("\n[STEP 8] Schema Verification")
try:
    from src.jobs.schemas import Job, JobPosting, NormalizedJob
    print(f"  Job fields: {list(Job.model_fields.keys())}")
    print(f"  JobPosting fields: {list(JobPosting.model_fields.keys())}")
    print(f"  NormalizedJob fields: {list(NormalizedJob.model_fields.keys())}")
except Exception as e:
    print(f"  ❌ Schema verification: {e}")

# STEP 9: Verify what saved_jobs_service.save_job() actually needs
print("\n[STEP 9] SavedJobsService.save_job() signature check")
try:
    import inspect
    sig = inspect.signature(SavedJobsService.save_job)
    print(f"  Signature: {sig}")
    print(f"  Expected 'job' parameter type: Job (pydantic model with .id, .title, .company, etc.)")
except Exception as e:
    print(f"  ❌ Signature check: {e}")

print("\n" + "=" * 60)
print("DEBUG COMPLETE")
print("=" * 60)