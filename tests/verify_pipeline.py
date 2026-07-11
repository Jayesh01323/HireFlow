"""
Final verification script for Job Discovery pipeline.
Tests each stage without emoji characters for Windows compatibility.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, force=True)

from src.jobs.aggregator import JobAggregator
from src.jobs.schemas import JobPosting, NormalizedJob
from src.jobs.pipeline_logger import get_pipeline_logger, reset_pipeline_logger
from src.jobs.freshness_scorer import JobFreshnessScorer
from src.jobs.deduplicator import JobDeduplicator
from src.jobs.normalizer import JobNormalizer
from src.jobs.ranking import JobRankingEngine
from datetime import datetime, timezone, timedelta

PASS = "[PASS]"
FAIL = "[FAIL]"
INFO = "[INFO]"

results = []

def check(description, condition, detail=""):
    if condition:
        results.append(f"  {PASS} {description}")
    else:
        results.append(f"  {FAIL} {description} - {detail}")

print("=" * 70)
print("JOB DISCOVERY FINAL VERIFICATION")
print("=" * 70)

# =============================================
# STAGE 1: Schema Validation
# =============================================
print("\n[STAGE 1] Schema Validation")
print("-" * 50)

# Test NormalizedJob creation
try:
    job = NormalizedJob(
        title="Software Engineer",
        company="Test Corp",
        location="Bangalore",
        salary="100000",
        salary_min=100000,
        salary_max=200000,
        description="Test description",
        url="https://example.com/job/1",
        source="linkedin",
        external_id="abc123",
        is_remote=False,
        experience_level="mid",
        experience_min=2,
        experience_max=5,
        skills=["Python", "Java"],
        posted_date=datetime.now(timezone.utc),
    )
    check("NormalizedJob created successfully", True)
    check("NormalizedJob has title", hasattr(job, 'title') and job.title == "Software Engineer")
    check("NormalizedJob has company", hasattr(job, 'company') and job.company == "Test Corp")
    check("NormalizedJob has location", hasattr(job, 'location') and job.location == "Bangalore")
    check("NormalizedJob has description", hasattr(job, 'description'))
    check("NormalizedJob has url", hasattr(job, 'url'))
    check("NormalizedJob has source", hasattr(job, 'source') and job.source == "linkedin")
    check("NormalizedJob has posted_date", hasattr(job, 'posted_date'))
    check("NormalizedJob has experience", hasattr(job, 'experience_min') and hasattr(job, 'experience_max'))
    check("NormalizedJob has salary", hasattr(job, 'salary_min') and hasattr(job, 'salary_max'))
    check("NormalizedJob has employment_type (is_remote)", hasattr(job, 'is_remote'))
    check("NormalizedJob has skills", hasattr(job, 'skills') and len(job.skills) == 2)
except Exception as e:
    check("NormalizedJob creation", False, str(e))

# Test JobPosting creation
try:
    jp = JobPosting(
        title="Test",
        company="Test",
        url="https://example.com",
        source="linkedin",
    )
    check("JobPosting created successfully", True)
except Exception as e:
    check("JobPosting creation", False, str(e))

# =============================================
# STAGE 2: Normalizer
# =============================================
print("\n[STAGE 2] Normalizer")
print("-" * 50)

normalizer = JobNormalizer()
try:
    jp = JobPosting(
        title="Senior Software Engineer",
        company="Google LLC",
        location="Bangalore",
        salary="1500000-2500000",
        description="We are looking for a senior software engineer with Python and Java skills.",
        url="https://example.com/job/1",
        source="linkedin",
        external_id="ext1",
        is_remote=False,
        experience_level="senior",
        posted_date=datetime.now(timezone.utc),
    )
    nj = normalizer.normalize_job(jp)
    check("Normalizer runs without error", True)
    check("Title normalized", nj.title is not None)
    check("Company normalized", nj.company is not None)
    check("Location normalized", nj.location is not None)
    check("Salary min extracted", nj.salary_min is not None)
    check("Salary max extracted", nj.salary_max is not None)
    check("Skills extracted", len(nj.skills) > 0)
    check("Experience level mapped", nj.experience_level is not None)
    check("Source preserved", nj.source == "linkedin")
except Exception as e:
    check("Normalizer", False, str(e))

# =============================================
# STAGE 3: Deduplicator
# =============================================
print("\n[STAGE 3] Deduplicator")
print("-" * 50)

dedup = JobDeduplicator()
try:
    job1 = NormalizedJob(
        title="Software Engineer", company="Google", location="Bangalore",
        description="Job 1", url="https://example.com/1", source="linkedin",
        external_id="1", posted_date=datetime.now(timezone.utc),
    )
    job2 = NormalizedJob(
        title="Software Engineer", company="Google", location="Bangalore",
        description="Job 2 (duplicate)", url="https://example.com/2", source="naukri",
        external_id="2", posted_date=datetime.now(timezone.utc),
    )
    job3 = NormalizedJob(
        title="Data Scientist", company="Google", location="Bangalore",
        description="Job 3", url="https://example.com/3", source="linkedin",
        external_id="3", posted_date=datetime.now(timezone.utc),
    )
    
    unique = dedup.deduplicate_jobs([job1, job2, job3])
    check("Deduplicator runs without error", True)
    check("Duplicates removed (3->2)", len(unique) == 2, f"Got {len(unique)}")
    check("Unique jobs preserved", any(j.title == "Data Scientist" for j in unique))
except Exception as e:
    check("Deduplicator", False, str(e))

# =============================================
# STAGE 4: Freshness Filter
# =============================================
print("\n[STAGE 4] Freshness Filter")
print("-" * 50)

freshness = JobFreshnessScorer(max_age_days=30)
try:
    fresh_job = NormalizedJob(
        title="Fresh Job", company="C1", location="L1",
        description="", url="https://example.com/f", source="linkedin",
        external_id="f", posted_date=datetime.now(timezone.utc),
    )
    old_job = NormalizedJob(
        title="Old Job", company="C2", location="L2",
        description="", url="https://example.com/o", source="linkedin",
        external_id="o", posted_date=datetime.now(timezone.utc) - timedelta(days=60),
    )
    
    fresh_score = freshness.calculate_freshness_score(fresh_job)
    old_score = freshness.calculate_freshness_score(old_job)
    
    check("Fresh job score > 0", fresh_score > 0.0, f"Score: {fresh_score}")
    check("Old job score = 0.0", old_score == 0.0, f"Score: {old_score}")
    check("Freshness filter removes old jobs", 
          len(freshness.filter_by_freshness([fresh_job, old_job], min_score=0.0)) == 1)
except Exception as e:
    check("Freshness filter", False, str(e))

# =============================================
# STAGE 5: Ranking Engine
# =============================================
print("\n[STAGE 5] Ranking Engine")
print("-" * 50)

ranking = JobRankingEngine()
try:
    ranked = ranking.rank_jobs(
        [NormalizedJob(
            title="Python Dev", company="C1", location="Bangalore",
            description="Python developer needed", url="https://example.com/1",
            source="linkedin", external_id="1",
            skills=["Python", "Django", "SQL"],
            posted_date=datetime.now(timezone.utc),
            salary_min=100000, salary_max=200000,
            experience_min=2, experience_max=5,
        )],
        resume_skills={"Python", "Django", "SQL", "Java"},
        user_preferences={
            "preferred_location": "Bangalore",
            "remote_only": False,
            "experience_years": 3,
            "expected_salary_min": 80000,
        }
    )
    check("Ranking runs without error", True)
    check("Ranked results have overall_score", len(ranked) > 0 and "overall_score" in ranked[0])
    check("Overall score is computed (not default 0.5)", 
          ranked[0]["overall_score"] != 0.5, f"Score: {ranked[0]['overall_score']}")
    check("Skill match score computed", ranked[0]["skill_match_score"] > 0.0, 
          f"Score: {ranked[0]['skill_match_score']}")
    check("Location match score computed", ranked[0]["location_match_score"] > 0.0,
          f"Score: {ranked[0]['location_match_score']}")
    check("Freshness score computed", ranked[0]["freshness_score"] > 0.0,
          f"Score: {ranked[0]['freshness_score']}")
    check("Experience fit score computed", ranked[0]["experience_fit_score"] > 0.0,
          f"Score: {ranked[0]['experience_fit_score']}")
    check("Matched skills present", len(ranked[0].get("matched_skills", [])) > 0)
    check("Missing skills present", len(ranked[0].get("missing_skills", [])) > 0)
    check("Skill coverage computed", ranked[0].get("skill_coverage", 0) > 0)
except Exception as e:
    check("Ranking engine", False, str(e))

# =============================================
# STAGE 6: Pipeline Logger
# =============================================
print("\n[STAGE 6] Pipeline Logger")
print("-" * 50)

reset_pipeline_logger()
pl = get_pipeline_logger()
try:
    pl.log_pipeline_start()
    pl.register_connector("linkedin")
    pl.register_connector("naukri")
    pl.register_connector("indeed")
    
    pl.log_start("linkedin")
    pl.log_success("linkedin", 5)
    
    pl.log_start("naukri")
    pl.log_failure("naukri", "HTTP_ERROR", "Status 403", "ConnectionError")
    
    pl.log_start("indeed")
    pl.log_success("indeed", 3)
    
    pl.set_freshness_count("linkedin", 4)
    pl.set_freshness_count("indeed", 2)
    
    pl.mark_used_in_final("linkedin")
    pl.mark_used_in_final("indeed")
    
    pl.total_jobs_before_dedup = 8
    pl.total_jobs_after_dedup = 6
    pl.total_jobs_after_freshness = 6
    pl.total_jobs_final = 6
    
    pl.log_pipeline_end()
    
    report = pl.get_report()
    check("Pipeline logger runs without error", True)
    check("Connector invoked logged", any(r["invoked"] == "Yes" for r in report))
    check("Connector success logged", any(r["success"] for r in report))
    check("Connector failure logged", any(not r["success"] for r in report))
    check("Jobs returned logged", any(r["jobs_returned"] > 0 for r in report))
    check("Jobs after freshness logged", any(r["jobs_after_freshness"] > 0 for r in report))
    check("Used in final logged", any(r["used_in_final"] == "Yes" for r in report))
    check("Failure reason logged", any(r["failure_reason"] for r in report if not r["success"]))
except Exception as e:
    check("Pipeline logger", False, str(e))

# =============================================
# STAGE 7: Aggregator Connector Mapping
# =============================================
print("\n[STAGE 7] Aggregator Connector Mapping")
print("-" * 50)

try:
    agg = JobAggregator()
    sources = agg.get_available_sources()
    check("Aggregator initializes", True)
    check("Connectors registered", len(sources) > 0, f"Found {len(sources)}")
    
    # Verify source mapping
    expected_sources = ["apify", "linkedin", "naukri", "internshala", "indeed", 
                        "foundit", "wellfound", "unstop", "cutshort", "glassdoor"]
    for s in expected_sources:
        check(f"Connector '{s}' registered", s in sources)
    
    # Check wellfound mapping
    wf_connector = agg.connectors.get("wellfound")
    check("Wellfound connector exists", wf_connector is not None)
    if wf_connector:
        check("Wellfound source_name is 'wellfound'", wf_connector.source_name == "wellfound")
    
    # Check linkedin mapping
    li_connector = agg.connectors.get("linkedin")
    check("LinkedIn connector exists", li_connector is not None)
    if li_connector:
        check("LinkedIn source_name is 'linkedin'", li_connector.source_name == "linkedin")
except Exception as e:
    check("Aggregator connector mapping", False, str(e))

# =============================================
# STAGE 8: Search Pipeline (without live API)
# =============================================
print("\n[STAGE 8] Search Pipeline (no live API)")
print("-" * 50)

try:
    reset_pipeline_logger()
    results_list = agg.search_jobs(
        query="Python Developer",
        location="Bangalore",
        remote=False,
        experience="entry",
        limit=10,
        resume_skills={"Python", "Django"},
        user_preferences={
            "preferred_location": "Bangalore",
            "remote_only": False,
            "experience_years": 1,
            "expected_salary_min": 50000,
        },
    )
    check("Search pipeline runs without error", True)
    check("Search returns results", len(results_list) > 0, f"Got {len(results_list)} results")
    
    if results_list:
        first = results_list[0]
        check("Result has 'job' key", "job" in first)
        check("Result has 'overall_score' key", "overall_score" in first)
        check("Result has 'skill_match_score' key", "skill_match_score" in first)
        
        job = first["job"]
        check("Job has title", hasattr(job, 'title') and job.title)
        check("Job has company", hasattr(job, 'company') and job.company)
        check("Job has location", hasattr(job, 'location'))
        check("Job has description", hasattr(job, 'description'))
        check("Job has url", hasattr(job, 'url') and job.url)
        check("Job has source", hasattr(job, 'source') and job.source)
        check("Job has posted_date", hasattr(job, 'posted_date'))
        check("Job has experience", hasattr(job, 'experience_min'))
        check("Job has salary", hasattr(job, 'salary_min'))
        check("Job has skills", hasattr(job, 'skills'))
    
    # Print pipeline report
    print(f"\n{INFO} Pipeline Report:")
    report = pl.get_report()
    for r in report:
        status = "OK" if r["success"] else f"FAIL({r['failure_reason']})"
        print(f"  {r['connector_name']:15s} invoked={r['invoked']:3s} jobs={r['jobs_returned']:3d} "
              f"fresh={r['jobs_after_freshness']:3d} final={r['used_in_final']:3s} {status}")
    
    print(f"\n{INFO} Totals: before_dedup={pl.total_jobs_before_dedup} "
          f"after_dedup={pl.total_jobs_after_dedup} "
          f"after_freshness={pl.total_jobs_after_freshness} "
          f"final={pl.total_jobs_final}")
    
except Exception as e:
    check("Search pipeline", False, str(e))
    import traceback
    traceback.print_exc()

# =============================================
# SUMMARY
# =============================================
print("\n" + "=" * 70)
print("VERIFICATION SUMMARY")
print("=" * 70)
for r in results:
    print(r)

passed = sum(1 for r in results if "[PASS]" in r)
failed = sum(1 for r in results if "[FAIL]" in r)
print(f"\nResults: {passed} passed, {failed} failed out of {len(results)} checks")