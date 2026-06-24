"""
Unit Tests for Job Discovery Engine

Comprehensive tests for the job discovery engine components including:
- Job Normalizer
- Job Deduplicator
- Job Ranking Engine
- Job Repository
- Job Aggregator
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.jobs.deduplicator import JobDeduplicator
from src.jobs.normalizer import JobNormalizer
from src.jobs.ranking import JobRankingEngine
from src.jobs.repository import JobRepository
from src.jobs.schemas import JobPosting, NormalizedJob


class TestJobNormalizer:
    """Test cases for JobNormalizer."""
    
    def test_initialization(self):
        """Test normalizer initialization."""
        normalizer = JobNormalizer()
        assert normalizer is not None
        assert hasattr(normalizer, 'company_aliases')
        assert hasattr(normalizer, 'location_mappings')
    
    def test_normalize_title(self):
        """Test job title normalization."""
        normalizer = JobNormalizer()
        
        # Test various title formats
        assert normalizer.normalize_title("Sr. Software Engineer") == "Senior Software Engineer"
        assert normalizer.normalize_title("Jr. Developer") == "Junior Developer"
        assert normalizer.normalize_title("Full Stack Dev") == "Full Stack Developer"
    
    def test_normalize_company(self):
        """Test company name normalization."""
        normalizer = JobNormalizer()
        
        # Test company alias mapping
        assert normalizer.normalize_company("Google LLC") == "Google"
        assert normalizer.normalize_company("Amazon.com") == "Amazon"
    
    def test_normalize_location(self):
        """Test location normalization."""
        normalizer = JobNormalizer()
        
        # Test location mapping
        assert normalizer.normalize_location("Bengaluru") == "Bangalore"
        assert normalizer.normalize_location("NYC") == "New York"
    
    def test_normalize_experience(self):
        """Test experience level normalization."""
        normalizer = JobNormalizer()
        
        assert normalizer.normalize_experience("0-1 years") == "entry"
        assert normalizer.normalize_experience("2-5 years") == "mid"
        assert normalizer.normalize_experience("5+ years") == "senior"
    
    def test_extract_salary_range(self):
        """Test salary range extraction."""
        normalizer = JobNormalizer()
        
        # Test various salary formats
        min_sal, max_sal = normalizer.extract_salary_range("₹10,00,000 - ₹15,00,000")
        assert min_sal == 1000000
        assert max_sal == 1500000
        
        min_sal, max_sal = normalizer.extract_salary_range("$80,000 - $120,000")
        assert min_sal == 80000
        assert max_sal == 1200000  # Converted to INR
    
    def test_extract_skills(self):
        """Test skill extraction from description."""
        normalizer = JobNormalizer()
        
        description = "We are looking for a Python developer with experience in Django, React, and SQL."
        skills = normalizer.extract_skills(description)
        
        assert "python" in skills
        assert "django" in skills
        assert "react" in skills
        assert "sql" in skills
    
    def test_detect_remote(self):
        """Test remote job detection."""
        normalizer = JobNormalizer()
        
        assert normalizer.detect_remote("Remote", None) == True
        assert normalizer.detect_remote("Bangalore", None) == False
        assert normalizer.detect_remote(None, "Work from home") == True
    
    def test_batch_normalize(self):
        """Test batch normalization of jobs."""
        normalizer = JobNormalizer()
        
        job_postings = [
            JobPosting(
                title="Sr. Software Engineer",
                company="Google LLC",
                location="Bengaluru",
                salary="₹20,00,000",
                description="Python developer role",
                url="https://example.com/job1",
                source="linkedin",
                external_id="123",
                is_remote=False,
                experience_level="senior",
                posted_date=datetime.utcnow(),
            )
        ]
        
        normalized = normalizer.batch_normalize(job_postings)
        
        assert len(normalized) == 1
        assert normalized[0].title == "Senior Software Engineer"
        assert normalized[0].company == "Google"
        assert normalized[0].location == "Bangalore"


class TestJobDeduplicator:
    """Test cases for JobDeduplicator."""
    
    def test_initialization(self):
        """Test deduplicator initialization."""
        deduplicator = JobDeduplicator()
        assert deduplicator is not None
        assert deduplicator.similarity_threshold == 0.85
    
    def test_deduplicate_jobs(self):
        """Test job deduplication."""
        deduplicator = JobDeduplicator()
        
        jobs = [
            NormalizedJob(
                title="Software Engineer",
                company="Google",
                location="Bangalore",
                salary="₹10,00,000",
                description="Python developer role",
                url="https://example.com/job1",
                source="linkedin",
                external_id="123",
                is_remote=False,
                experience_level="mid",
                posted_date=datetime.utcnow(),
                skills=["python", "django"],
            ),
            NormalizedJob(
                title="Software Engineer",
                company="Google",
                location="Bangalore",
                salary="₹10,00,000",
                description="Python developer role",
                url="https://example.com/job2",
                source="naukri",
                external_id="456",
                is_remote=False,
                experience_level="mid",
                posted_date=datetime.utcnow(),
                skills=["python", "django"],
            ),
        ]
        
        unique_jobs = deduplicator.deduplicate_jobs(jobs)
        
        # Should deduplicate to 1 job
        assert len(unique_jobs) == 1
    
    def test_calculate_similarity(self):
        """Test similarity calculation between jobs."""
        deduplicator = JobDeduplicator()
        
        job1 = NormalizedJob(
            title="Software Engineer",
            company="Google",
            location="Bangalore",
            salary="₹10,00,000",
            description="Python developer role",
            url="https://example.com/job1",
            source="linkedin",
            external_id="123",
            is_remote=False,
            experience_level="mid",
            posted_date=datetime.utcnow(),
            skills=["python", "django"],
        )
        
        job2 = NormalizedJob(
            title="Software Engineer",
            company="Google",
            location="Bangalore",
            salary="₹10,00,000",
            description="Python developer role",
            url="https://example.com/job2",
            source="naukri",
            external_id="456",
            is_remote=False,
            experience_level="mid",
            posted_date=datetime.utcnow(),
            skills=["python", "django"],
        )
        
        similarity = deduplicator.calculate_similarity(job1, job2)
        
        # Should be very similar
        assert similarity > 0.8
    
    def test_find_duplicates(self):
        """Test finding duplicate jobs."""
        deduplicator = JobDeduplicator()
        
        jobs = [
            NormalizedJob(
                title="Software Engineer",
                company="Google",
                location="Bangalore",
                salary="₹10,00,000",
                description="Python developer role",
                url="https://example.com/job1",
                source="linkedin",
                external_id="123",
                is_remote=False,
                experience_level="mid",
                posted_date=datetime.utcnow(),
                skills=["python", "django"],
            ),
            NormalizedJob(
                title="Software Engineer",
                company="Google",
                location="Bangalore",
                salary="₹10,00,000",
                description="Python developer role",
                url="https://example.com/job2",
                source="naukri",
                external_id="456",
                is_remote=False,
                experience_level="mid",
                posted_date=datetime.utcnow(),
                skills=["python", "django"],
            ),
        ]
        
        duplicates = deduplicator.find_duplicates(jobs)
        
        # Should find 1 group of duplicates
        assert len(duplicates) == 1
    
    def test_merge_duplicate_info(self):
        """Test merging duplicate job information."""
        deduplicator = JobDeduplicator()
        
        jobs = [
            NormalizedJob(
                title="Software Engineer",
                company="Google",
                location="Bangalore",
                salary="₹10,00,000",
                description="Python developer role",
                url="https://example.com/job1",
                source="linkedin",
                external_id="123",
                is_remote=False,
                experience_level="mid",
                posted_date=datetime.utcnow(),
                skills=["python"],
            ),
            NormalizedJob(
                title="Software Engineer",
                company="Google",
                location="Bangalore",
                salary="₹12,00,000",
                description="Python developer with Django experience",
                url="https://example.com/job2",
                source="naukri",
                external_id="456",
                is_remote=False,
                experience_level="mid",
                posted_date=datetime.utcnow(),
                skills=["django"],
            ),
        ]
        
        merged = deduplicator.merge_duplicate_info(jobs)
        
        # Should merge skills
        assert "python" in merged.skills
        assert "django" in merged.skills
        # Should use higher salary
        assert merged.salary_max == 1200000


class TestJobRankingEngine:
    """Test cases for JobRankingEngine."""
    
    def test_initialization(self):
        """Test ranking engine initialization."""
        ranking_engine = JobRankingEngine()
        assert ranking_engine is not None
        assert hasattr(ranking_engine, 'skill_gap_engine')
    
    def test_calculate_job_score(self):
        """Test job score calculation."""
        ranking_engine = JobRankingEngine()
        
        job = NormalizedJob(
            title="Software Engineer",
            company="Google",
            location="Bangalore",
            salary="₹10,00,000",
            description="Python developer role",
            url="https://example.com/job1",
            source="linkedin",
            external_id="123",
            is_remote=False,
            experience_level="mid",
            posted_date=datetime.utcnow(),
            skills=["python", "django"],
        )
        
        resume_skills = {"python", "django", "sql"}
        user_preferences = {
            "preferred_location": "Bangalore",
            "remote_only": False,
            "experience_years": 3,
            "expected_salary_min": 800000,
        }
        
        score = ranking_engine.calculate_job_score(job, resume_skills, user_preferences)
        
        assert "overall_score" in score
        assert "skill_match_score" in score
        assert "location_match_score" in score
        assert "salary_score" in score
        assert "freshness_score" in score
        assert "experience_fit_score" in score
        assert 0 <= score["overall_score"] <= 1
    
    def test_rank_jobs(self):
        """Test job ranking."""
        ranking_engine = JobRankingEngine()
        
        jobs = [
            NormalizedJob(
                title="Software Engineer",
                company="Google",
                location="Bangalore",
                salary="₹10,00,000",
                description="Python developer role",
                url="https://example.com/job1",
                source="linkedin",
                external_id="123",
                is_remote=False,
                experience_level="mid",
                posted_date=datetime.utcnow(),
                skills=["python", "django"],
            ),
            NormalizedJob(
                title="Data Scientist",
                company="Amazon",
                location="Bangalore",
                salary="₹12,00,000",
                description="Machine learning role",
                url="https://example.com/job2",
                source="naukri",
                external_id="456",
                is_remote=False,
                experience_level="mid",
                posted_date=datetime.utcnow(),
                skills=["python", "ml"],
            ),
        ]
        
        resume_skills = {"python", "django", "sql"}
        user_preferences = {}
        
        ranked = ranking_engine.rank_jobs(jobs, resume_skills, user_preferences)
        
        assert len(ranked) == 2
        # Should be sorted by overall score
        assert ranked[0]["overall_score"] >= ranked[1]["overall_score"]
    
    def test_get_top_jobs(self):
        """Test getting top N jobs."""
        ranking_engine = JobRankingEngine()
        
        jobs = [
            NormalizedJob(
                title=f"Software Engineer {i}",
                company="Google",
                location="Bangalore",
                salary="₹10,00,000",
                description="Python developer role",
                url=f"https://example.com/job{i}",
                source="linkedin",
                external_id=str(i),
                is_remote=False,
                experience_level="mid",
                posted_date=datetime.utcnow(),
                skills=["python"],
            )
            for i in range(10)
        ]
        
        resume_skills = {"python"}
        ranked = ranking_engine.rank_jobs(jobs, resume_skills, {})
        
        top_jobs = ranking_engine.get_top_jobs(ranked, limit=5, min_score=0.0)
        
        assert len(top_jobs) == 5


class TestJobRepository:
    """Test cases for JobRepository."""
    
    @pytest.fixture
    def repository(self):
        """Create a repository instance for testing."""
        # Use in-memory database for testing
        import os
        os.environ["DATABASE_PATH"] = ":memory:"
        return JobRepository()
    
    def test_initialization(self, repository):
        """Test repository initialization."""
        assert repository is not None
        assert hasattr(repository, 'session')
    
    def test_save_job(self, repository):
        """Test saving a single job."""
        job = NormalizedJob(
            title="Software Engineer",
            company="Google",
            location="Bangalore",
            salary="₹10,00,000",
            description="Python developer role",
            url="https://example.com/job1",
            source="linkedin",
            external_id="123",
            is_remote=False,
            experience_level="mid",
            posted_date=datetime.utcnow(),
            skills=["python", "django"],
        )
        
        result = repository.save_job(job)
        
        assert result is not None
        assert result["success"] == True
    
    def test_batch_save_jobs(self, repository):
        """Test batch saving jobs."""
        jobs = [
            NormalizedJob(
                title=f"Software Engineer {i}",
                company="Google",
                location="Bangalore",
                salary="₹10,00,000",
                description="Python developer role",
                url=f"https://example.com/job{i}",
                source="linkedin",
                external_id=str(i),
                is_remote=False,
                experience_level="mid",
                posted_date=datetime.utcnow(),
                skills=["python"],
            )
            for i in range(5)
        ]
        
        result = repository.batch_save_jobs(jobs)
        
        assert result["success"] == 5
        assert result["failed"] == 0
    
    def test_search_jobs(self, repository):
        """Test searching jobs."""
        # First save some jobs
        jobs = [
            NormalizedJob(
                title="Software Engineer",
                company="Google",
                location="Bangalore",
                salary="₹10,00,000",
                description="Python developer role",
                url="https://example.com/job1",
                source="linkedin",
                external_id="123",
                is_remote=False,
                experience_level="mid",
                posted_date=datetime.utcnow(),
                skills=["python", "django"],
            ),
            NormalizedJob(
                title="Data Scientist",
                company="Amazon",
                location="Mumbai",
                salary="₹12,00,000",
                description="Machine learning role",
                url="https://example.com/job2",
                source="naukri",
                external_id="456",
                is_remote=False,
                experience_level="mid",
                posted_date=datetime.utcnow(),
                skills=["python", "ml"],
            ),
        ]
        
        repository.batch_save_jobs(jobs)
        
        # Search for Python jobs
        results = repository.search_jobs(keyword="python")
        
        assert len(results) >= 1
    
    def test_get_job_statistics(self, repository):
        """Test getting job statistics."""
        # Save some jobs first
        jobs = [
            NormalizedJob(
                title="Software Engineer",
                company="Google",
                location="Bangalore",
                salary="₹10,00,000",
                description="Python developer role",
                url="https://example.com/job1",
                source="linkedin",
                external_id="123",
                is_remote=False,
                experience_level="mid",
                posted_date=datetime.utcnow(),
                skills=["python", "django"],
            )
        ]
        
        repository.batch_save_jobs(jobs)
        
        stats = repository.get_job_statistics()
        
        assert "total_jobs" in stats
        assert stats["total_jobs"] >= 1


class TestJobAggregator:
    """Test cases for JobAggregator."""
    
    @pytest.fixture
    def aggregator(self):
        """Create an aggregator instance for testing."""
        return JobAggregator()
    
    def test_initialization(self, aggregator):
        """Test aggregator initialization."""
        assert aggregator is not None
        assert hasattr(aggregator, 'connectors')
        assert hasattr(aggregator, 'normalizer')
        assert hasattr(aggregator, 'deduplicator')
        assert hasattr(aggregator, 'ranking_engine')
        assert hasattr(aggregator, 'repository')
    
    def test_get_available_sources(self, aggregator):
        """Test getting available sources."""
        sources = aggregator.get_available_sources()
        
        assert len(sources) > 0
        assert "linkedin" in sources
        assert "naukri" in sources
        assert "internshala" in sources
    
    def test_search_database_jobs(self, aggregator):
        """Test searching jobs from database."""
        # This test requires database setup
        # For now, just test that the method exists
        results = aggregator.search_database_jobs(limit=10)
        
        assert isinstance(results, list)
    
    def test_get_job_statistics(self, aggregator):
        """Test getting job statistics."""
        stats = aggregator.get_job_statistics()
        
        assert isinstance(stats, dict)
        assert "total_jobs" in stats
    
    def test_get_source_stats(self, aggregator):
        """Test getting source statistics."""
        stats = aggregator.get_source_stats()
        
        assert isinstance(stats, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
