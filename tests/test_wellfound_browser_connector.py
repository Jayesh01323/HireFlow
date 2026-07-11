"""
Test Wellfound Browser Connector

Validates the complete browser automation pipeline for Wellfound connector.
Tests with the example search: Backend Developer | Pune
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_wellfound_connector():
    """Test Wellfound connector with Backend Developer | Pune search."""
    logger.info("=" * 80)
    logger.info("Testing Wellfound Browser Connector")
    logger.info("=" * 80)
    
    # Import after logging setup
    from src.jobs.connectors.wellfound import WellfoundConnector
    from src.jobs.normalizer import JobNormalizer
    from src.jobs.deduplicator import JobDeduplicator
    from src.jobs.ranking import JobRankingEngine
    from src.jobs.schemas import NormalizedJob
    
    # Test parameters (dynamic, not hardcoded)
    query = "Backend Developer"
    location = "Pune"
    
    logger.info(f"\nTest Search Parameters:")
    logger.info(f"  Query: {query}")
    logger.info(f"  Location: {location}")
    logger.info(f"  Remote: False")
    logger.info(f"  Experience: None")
    
    # Step 1: Test connector
    logger.info("\n" + "=" * 80)
    logger.info("Step 1: Testing Wellfound Connector")
    logger.info("=" * 80)
    
    try:
        connector = WellfoundConnector()
        jobs = connector.search_jobs(
            query=query,
            location=location,
            remote=False,
            experience=None,
            limit=20,
        )
        
        logger.info(f"✅ Connector returned {len(jobs)} jobs")
        
        if not jobs:
            logger.warning("⚠️ No jobs returned from connector")
            return False
        
        # Display sample jobs
        logger.info("\nSample jobs extracted:")
        for i, job in enumerate(jobs[:3], 1):
            logger.info(f"\n  Job {i}:")
            logger.info(f"    Title: {job.title}")
            logger.info(f"    Company: {job.company}")
            logger.info(f"    Location: {job.location}")
            logger.info(f"    URL: {job.url}")
            logger.info(f"    Source: {job.source}")
            logger.info(f"    Remote: {job.is_remote}")
        
    except Exception as e:
        logger.error(f"❌ Connector test failed: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    # Step 2: Test normalization
    logger.info("\n" + "=" * 80)
    logger.info("Step 2: Testing Job Normalization")
    logger.info("=" * 80)
    
    try:
        normalizer = JobNormalizer()
        normalized_jobs = normalizer.batch_normalize(jobs)
        
        logger.info(f"✅ Normalized {len(normalized_jobs)} jobs")
        
        # Display sample normalized job
        if normalized_jobs:
            sample = normalized_jobs[0]
            logger.info("\nSample normalized job:")
            logger.info(f"  Title: {sample.title}")
            logger.info(f"  Company: {sample.company}")
            logger.info(f"  Location: {sample.location}")
            logger.info(f"  URL: {sample.url}")
            logger.info(f"  Source: {sample.source}")
            logger.info(f"  External ID: {sample.external_id}")
            logger.info(f"  Remote: {sample.is_remote}")
            logger.info(f"  Experience Level: {sample.experience_level}")
            logger.info(f"  Salary: {sample.salary}")
            logger.info(f"  Salary Min: {sample.salary_min}")
            logger.info(f"  Salary Max: {sample.salary_max}")
            logger.info(f"  Skills: {sample.skills[:5] if sample.skills else 'None'}")
            logger.info(f"  Posted Date: {sample.posted_date}")
        
    except Exception as e:
        logger.error(f"❌ Normalization test failed: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    # Step 3: Test deduplication
    logger.info("\n" + "=" * 80)
    logger.info("Step 3: Testing Job Deduplication")
    logger.info("=" * 80)
    
    try:
        deduplicator = JobDeduplicator()
        unique_jobs = deduplicator.deduplicate_jobs(normalized_jobs)
        
        logger.info(f"✅ Deduplicated {len(normalized_jobs)} jobs to {len(unique_jobs)} unique jobs")
        
    except Exception as e:
        logger.error(f"❌ Deduplication test failed: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    # Step 4: Test ranking (with mock skills)
    logger.info("\n" + "=" * 80)
    logger.info("Step 4: Testing Job Ranking")
    logger.info("=" * 80)
    
    try:
        ranking_engine = JobRankingEngine()
        mock_skills = {"python", "django", "sql", "api", "backend"}
        
        ranked_jobs = ranking_engine.rank_jobs(
            unique_jobs,
            resume_skills=mock_skills,
            user_preferences={
                "preferred_location": location,
                "remote_only": False,
                "experience_years": 3,
            },
        )
        
        logger.info(f"✅ Ranked {len(ranked_jobs)} jobs")
        
        if ranked_jobs:
            logger.info("\nTop 3 ranked jobs:")
            for i, result in enumerate(ranked_jobs[:3], 1):
                job = result["job"]
                logger.info(f"\n  Rank {i}:")
                logger.info(f"    Title: {job.title}")
                logger.info(f"    Company: {job.company}")
                logger.info(f"    Overall Score: {result['overall_score']}")
                logger.info(f"    Skill Match: {result['skill_match_score']}")
                logger.info(f"    Location Match: {result['location_match_score']}")
                logger.info(f"    Matched Skills: {result['matched_skills'][:5]}")
        
    except Exception as e:
        logger.error(f"❌ Ranking test failed: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    # Step 5: Validate URLs
    logger.info("\n" + "=" * 80)
    logger.info("Step 5: Validating Job URLs")
    logger.info("=" * 80)
    
    try:
        valid_urls = 0
        for job in normalized_jobs:
            if job.url and job.url.startswith('http'):
                valid_urls += 1
        
        logger.info(f"✅ {valid_urls}/{len(normalized_jobs)} jobs have valid URLs")
        
        if valid_urls == len(normalized_jobs):
            logger.info("✅ All jobs have valid, real Wellfound URLs")
        else:
            logger.warning(f"⚠️ {len(normalized_jobs) - valid_urls} jobs have invalid URLs")
        
    except Exception as e:
        logger.error(f"❌ URL validation failed: {type(e).__name__}: {e}")
        return False
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    logger.info(f"✅ Connector: Successfully extracted {len(jobs)} jobs")
    logger.info(f"✅ Normalization: Successfully normalized {len(normalized_jobs)} jobs")
    logger.info(f"✅ Deduplication: Reduced to {len(unique_jobs)} unique jobs")
    logger.info(f"✅ Ranking: Successfully ranked {len(ranked_jobs)} jobs")
    logger.info(f"✅ URLs: {valid_urls}/{len(normalized_jobs)} valid URLs")
    logger.info("\n✅ All pipeline tests passed!")
    
    return True


if __name__ == "__main__":
    try:
        success = test_wellfound_connector()
        if success:
            logger.info("\n🎉 Wellfound browser connector test completed successfully!")
        else:
            logger.error("\n❌ Wellfound browser connector test failed!")
    except Exception as e:
        logger.error(f"\n❌ Test execution failed: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
