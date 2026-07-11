"""
Tests for the Pipeline Logger instrumentation.

Verifies that every connector is tracked with:
- Invoked (Yes/No)
- Jobs Returned
- Failure Reason (if any)
- Used in Final Results (Yes/No)
- Freshness filter application
"""

from __future__ import annotations

import logging
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest

from src.jobs.pipeline_logger import (
    FailureReason,
    PipelineLogger,
    ConnectorResult,
    get_pipeline_logger,
    reset_pipeline_logger,
)
from src.jobs.schemas import JobPosting, NormalizedJob


# ──────────────────────────────────────────────
# PipelineLogger Unit Tests
# ──────────────────────────────────────────────


class TestFailureReason:
    """Test FailureReason enum values."""

    def test_all_reasons_defined(self) -> None:
        """Verify all expected failure reasons exist."""
        reasons = {r.value for r in FailureReason}
        expected = {
            "CAPTCHA", "HTTP_ERROR", "SELECTOR_MISMATCH", "TIMEOUT",
            "PARSING_ERROR", "MISSING_DEPENDENCY", "CONNECTION_ERROR",
            "AUTH_ERROR", "RATE_LIMIT", "UNKNOWN",
        }
        assert reasons == expected, f"Missing reasons: {expected - reasons}"


class TestPipelineLogger:
    """Test PipelineLogger core functionality."""

    def setup_method(self) -> None:
        """Reset the pipeline logger before each test."""
        self.pl = reset_pipeline_logger()

    def test_register_connector(self) -> None:
        """Test registering a connector."""
        self.pl.register_connector("linkedin")
        assert "linkedin" in self.pl.connector_results
        assert self.pl.connector_results["linkedin"].connector_name == "linkedin"
        assert self.pl.connector_results["linkedin"].invoked is False

    def test_log_start(self) -> None:
        """Test logging connector start."""
        self.pl.log_start("linkedin")
        result = self.pl.connector_results["linkedin"]
        assert result.invoked is True
        assert result.start_time is not None

    def test_log_success(self) -> None:
        """Test logging connector success."""
        self.pl.log_start("linkedin")
        time.sleep(0.01)  # Ensure measurable duration
        self.pl.log_success("linkedin", 25)
        result = self.pl.connector_results["linkedin"]
        assert result.success is True
        assert result.jobs_returned == 25
        assert result.duration_ms is not None
        assert result.duration_ms > 0

    def test_log_failure(self) -> None:
        """Test logging connector failure."""
        self.pl.log_start("naukri")
        self.pl.log_failure("naukri", FailureReason.HTTP_ERROR, "HTTP 429", "HTTPError")
        result = self.pl.connector_results["naukri"]
        assert result.success is False
        assert result.failure_reason == FailureReason.HTTP_ERROR
        assert result.failure_detail == "HTTP 429"
        assert result.error_type == "HTTPError"

    def test_log_skipped(self) -> None:
        """Test logging a skipped connector."""
        self.pl.log_skipped("wellfound", "Connector not in registry")
        result = self.pl.connector_results["wellfound"]
        assert result.invoked is False
        assert result.failure_reason == FailureReason.UNKNOWN
        assert "Skipped" in result.failure_detail

    def test_mark_used_in_final(self) -> None:
        """Test marking a connector as used in final results."""
        self.pl.register_connector("linkedin")
        self.pl.mark_used_in_final("linkedin")
        assert self.pl.connector_results["linkedin"].used_in_final is True

    def test_set_freshness_count(self) -> None:
        """Test setting freshness count per connector."""
        self.pl.register_connector("linkedin")
        self.pl.set_freshness_count("linkedin", 15)
        assert self.pl.connector_results["linkedin"].jobs_after_freshness == 15

    def test_pipeline_totals(self) -> None:
        """Test pipeline total tracking."""
        self.pl.total_jobs_before_dedup = 100
        self.pl.total_jobs_after_dedup = 80
        self.pl.total_jobs_after_freshness = 60
        self.pl.total_jobs_final = 50
        self.pl.used_mock_fallback = True
        self.pl.mock_fallback_reason = "All connectors failed"

        assert self.pl.total_jobs_before_dedup == 100
        assert self.pl.total_jobs_after_dedup == 80
        assert self.pl.total_jobs_after_freshness == 60
        assert self.pl.total_jobs_final == 50
        assert self.pl.used_mock_fallback is True

    def test_get_report(self) -> None:
        """Test getting the pipeline report."""
        self.pl.log_start("linkedin")
        self.pl.log_success("linkedin", 30)
        self.pl.mark_used_in_final("linkedin")

        self.pl.log_start("naukri")
        self.pl.log_failure("naukri", FailureReason.TIMEOUT, "Connection timed out", "TimeoutError")

        self.pl.log_skipped("wellfound", "Not configured")

        report = self.pl.get_report()
        assert len(report) == 3

        # Find linkedin
        linkedin = [r for r in report if r["connector_name"] == "linkedin"][0]
        assert linkedin["invoked"] == "Yes"
        assert linkedin["jobs_returned"] == 30
        assert linkedin["failure_reason"] == ""
        assert linkedin["used_in_final"] == "Yes"

        # Find naukri
        naukri = [r for r in report if r["connector_name"] == "naukri"][0]
        assert naukri["invoked"] == "Yes"
        assert naukri["jobs_returned"] == 0
        assert naukri["failure_reason"] == "TIMEOUT"
        assert naukri["used_in_final"] == "No"

        # Find wellfound
        wellfound = [r for r in report if r["connector_name"] == "wellfound"][0]
        assert wellfound["invoked"] == "No"
        assert wellfound["failure_reason"] == "UNKNOWN"
        assert wellfound["used_in_final"] == "No"

    def test_get_summary_table(self) -> None:
        """Test the summary table formatting."""
        self.pl.log_start("linkedin")
        self.pl.log_success("linkedin", 30)
        self.pl.mark_used_in_final("linkedin")

        self.pl.log_start("naukri")
        self.pl.log_failure("naukri", FailureReason.TIMEOUT, "timed out", "TimeoutError")

        table = self.pl.get_summary_table()
        assert "JOB DISCOVERY PIPELINE REPORT" in table
        assert "Connector Name" in table
        assert "linkedin" in table
        assert "naukri" in table
        assert "TIMEOUT" in table
        assert "Pipeline Totals" in table

    def test_log_pipeline_start_end(self) -> None:
        """Test pipeline start/end logging."""
        self.pl.log_pipeline_start()
        assert self.pl.pipeline_start_time is not None
        time.sleep(0.01)
        self.pl.log_pipeline_end()
        assert self.pl.pipeline_end_time is not None

    def test_singleton_behavior(self) -> None:
        """Test that get_pipeline_logger returns the same instance."""
        pl1 = get_pipeline_logger()
        pl2 = get_pipeline_logger()
        assert pl1 is pl2

    def test_reset_creates_new_instance(self) -> None:
        """Test that reset creates a new instance."""
        pl1 = get_pipeline_logger()
        pl1.register_connector("test")
        reset_pipeline_logger()
        pl2 = get_pipeline_logger()
        assert pl1 is not pl2
        assert "test" not in pl2.connector_results


class TestFailureClassification:
    """Test the classify_failure method."""

    def setup_method(self) -> None:
        self.pl = reset_pipeline_logger()

    def test_timeout(self) -> None:
        reason, detail = self.pl.classify_failure(TimeoutError("Request timed out"))
        assert reason == FailureReason.TIMEOUT

    def test_connection_error(self) -> None:
        reason, detail = self.pl.classify_failure(ConnectionError("Connection refused"))
        assert reason == FailureReason.CONNECTION_ERROR

    def test_import_error(self) -> None:
        reason, detail = self.pl.classify_failure(ImportError("No module named 'apify_client'"))
        assert reason == FailureReason.MISSING_DEPENDENCY

    def test_captcha_detection(self) -> None:
        reason, detail = self.pl.classify_failure(
            Exception("DataDome CAPTCHA protection detected")
        )
        assert reason == FailureReason.CAPTCHA

    def test_captcha_alternative_keywords(self) -> None:
        for keyword in ["recaptcha", "blocked", "unusual traffic", "please verify", "security check"]:
            reason, detail = self.pl.classify_failure(Exception(f"Error: {keyword}"))
            assert reason == FailureReason.CAPTCHA, f"Failed for keyword: {keyword}"

    def test_http_error(self) -> None:
        reason, detail = self.pl.classify_failure(Exception("HTTP 500 Internal Server Error"))
        assert reason == FailureReason.HTTP_ERROR

    def test_rate_limit(self) -> None:
        for keyword in ["rate limit", "too many requests", "429", "throttl"]:
            reason, detail = self.pl.classify_failure(Exception(f"Error: {keyword}"))
            assert reason == FailureReason.RATE_LIMIT, f"Failed for keyword: {keyword}"

    def test_parsing_error(self) -> None:
        reason, detail = self.pl.classify_failure(KeyError("'title'"))
        assert reason == FailureReason.PARSING_ERROR

    def test_selector_mismatch(self) -> None:
        for keyword in ["selector", "element not found", "no such element", "xpath", "css selector"]:
            reason, detail = self.pl.classify_failure(Exception(f"Error: {keyword}"))
            assert reason == FailureReason.SELECTOR_MISMATCH, f"Failed for keyword: {keyword}"

    def test_auth_error(self) -> None:
        for keyword in ["auth", "api key", "unauthorized", "forbidden", "403", "401"]:
            reason, detail = self.pl.classify_failure(Exception(f"Error: {keyword}"))
            assert reason == FailureReason.AUTH_ERROR, f"Failed for keyword: {keyword}"

    def test_unknown_failure(self) -> None:
        reason, detail = self.pl.classify_failure(Exception("Some random error"))
        assert reason == FailureReason.UNKNOWN


class TestConnectorResult:
    """Test ConnectorResult dataclass."""

    def test_default_values(self) -> None:
        """Test default values of ConnectorResult."""
        r = ConnectorResult(connector_name="test")
        assert r.connector_name == "test"
        assert r.invoked is False
        assert r.success is False
        assert r.jobs_returned == 0
        assert r.jobs_after_freshness == 0
        assert r.failure_reason is None
        assert r.failure_detail is None
        assert r.used_in_final is False
        assert r.error_type is None
        assert r.start_time is None
        assert r.end_time is None
        assert r.duration_ms is None


# ──────────────────────────────────────────────
# Integration Test: Full Pipeline with Mock Connectors
# ──────────────────────────────────────────────


class MockConnector:
    """A mock connector that simulates various outcomes."""

    def __init__(
        self,
        source_name: str,
        should_fail: bool = False,
        failure_exception: Optional[Exception] = None,
        jobs_to_return: int = 10,
        posted_days_ago: Optional[int] = None,
    ) -> None:
        self.source_name = source_name
        self.should_fail = should_fail
        self.failure_exception = failure_exception
        self.jobs_to_return = jobs_to_return
        self.posted_days_ago = posted_days_ago

    def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        limit: int = 50,
    ) -> List[JobPosting]:
        if self.should_fail:
            raise self.failure_exception or Exception("Generic error")

        posted_date = None
        if self.posted_days_ago is not None:
            from datetime import timedelta
            posted_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
                days=self.posted_days_ago
            )

        return [
            JobPosting(
                title=f"{self.source_name} Job {i}",
                company=f"Company {i}",
                location="Remote",
                description=f"Job {i} from {self.source_name}",
                url=f"https://example.com/{self.source_name}/{i}",
                source=self.source_name,
                external_id=f"{self.source_name}_{i}",
                is_remote=True,
                posted_date=posted_date,
            )
            for i in range(self.jobs_to_return)
        ]


class TestPipelineIntegration:
    """Integration test for the full instrumented pipeline."""

    def setup_method(self) -> None:
        reset_pipeline_logger()

    def _run_pipeline(
        self,
        connectors: Dict[str, MockConnector],
        query: str = "python",
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Simulate the aggregator's search_jobs with pipeline logging."""
        from src.jobs.pipeline_logger import get_pipeline_logger

        pl = get_pipeline_logger()
        pl.log_pipeline_start()

        search_sources = list(connectors.keys())
        for source in search_sources:
            pl.register_connector(source)

        all_jobs: List[JobPosting] = []
        for source in search_sources:
            connector = connectors[source]
            pl.log_start(source)
            try:
                jobs = connector.search_jobs(
                    query=query,
                    limit=limit // len(search_sources),
                )
                all_jobs.extend(jobs)
                pl.log_success(source, len(jobs))
            except Exception as e:
                reason, detail = pl.classify_failure(e)
                pl.log_failure(source, reason, detail, type(e).__name__)

        pl.total_jobs_before_dedup = len(all_jobs)

        # Simulate freshness filter
        from src.jobs.freshness_scorer import JobFreshnessScorer
        scorer = JobFreshnessScorer(max_age_days=30)
        fresh_jobs = [
            job for job in all_jobs
            if scorer.calculate_freshness_score(job) > 0.0
        ]
        pl.total_jobs_after_freshness = len(fresh_jobs)

        for source in search_sources:
            source_fresh = [j for j in fresh_jobs if j.source == source]
            pl.set_freshness_count(source, len(source_fresh))

        # Simulate final results
        final_results = [{"job": job, "overall_score": 0.5} for job in fresh_jobs[:limit]]
        pl.total_jobs_final = len(final_results)

        for result in final_results:
            job = result.get("job", result)
            source = getattr(job, "source", None)
            if source:
                pl.mark_used_in_final(source)

        pl.log_pipeline_end()
        return final_results

    def test_all_connectors_succeed(self) -> None:
        """Test when all connectors succeed."""
        connectors = {
            "linkedin": MockConnector("linkedin", jobs_to_return=15),
            "naukri": MockConnector("naukri", jobs_to_return=10),
            "indeed": MockConnector("indeed", jobs_to_return=8),
            "wellfound": MockConnector("wellfound", jobs_to_return=5),
        }
        results = self._run_pipeline(connectors)
        assert len(results) == 38  # 15 + 10 + 8 + 5

        pl = get_pipeline_logger()
        report = pl.get_report()

        for entry in report:
            assert entry["invoked"] == "Yes"
            assert entry["failure_reason"] == ""
            assert entry["used_in_final"] == "Yes"

        assert pl.total_jobs_before_dedup == 38
        assert pl.total_jobs_after_freshness == 38
        assert pl.total_jobs_final == 38

    def test_some_connectors_fail(self) -> None:
        """Test when some connectors fail."""
        connectors = {
            "linkedin": MockConnector("linkedin", jobs_to_return=15),
            "naukri": MockConnector(
                "naukri",
                should_fail=True,
                failure_exception=TimeoutError("Connection timed out"),
            ),
            "indeed": MockConnector(
                "indeed",
                should_fail=True,
                failure_exception=Exception("HTTP 429 Too Many Requests"),
            ),
            "wellfound": MockConnector("wellfound", jobs_to_return=5),
        }
        results = self._run_pipeline(connectors)
        assert len(results) == 20  # 15 + 5

        pl = get_pipeline_logger()
        report = pl.get_report()

        linkedin = [r for r in report if r["connector_name"] == "linkedin"][0]
        assert linkedin["jobs_returned"] == 15
        assert linkedin["failure_reason"] == ""
        assert linkedin["used_in_final"] == "Yes"

        naukri = [r for r in report if r["connector_name"] == "naukri"][0]
        assert naukri["jobs_returned"] == 0
        assert naukri["failure_reason"] == "TIMEOUT"
        assert naukri["used_in_final"] == "No"

        indeed = [r for r in report if r["connector_name"] == "indeed"][0]
        assert indeed["jobs_returned"] == 0
        assert indeed["failure_reason"] == "RATE_LIMIT"
        assert indeed["used_in_final"] == "No"

        wellfound = [r for r in report if r["connector_name"] == "wellfound"][0]
        assert wellfound["jobs_returned"] == 5
        assert wellfound["failure_reason"] == ""
        assert wellfound["used_in_final"] == "Yes"

    def test_all_connectors_fail(self) -> None:
        """Test when all connectors fail."""
        connectors = {
            "linkedin": MockConnector(
                "linkedin",
                should_fail=True,
                failure_exception=Exception("DataDome CAPTCHA protection"),
            ),
            "naukri": MockConnector(
                "naukri",
                should_fail=True,
                failure_exception=ImportError("No module named 'apify_client'"),
            ),
            "indeed": MockConnector(
                "indeed",
                should_fail=True,
                failure_exception=ConnectionError("Connection refused"),
            ),
        }
        results = self._run_pipeline(connectors)
        assert len(results) == 0

        pl = get_pipeline_logger()
        report = pl.get_report()

        linkedin = [r for r in report if r["connector_name"] == "linkedin"][0]
        assert linkedin["failure_reason"] == "CAPTCHA"

        naukri = [r for r in report if r["connector_name"] == "naukri"][0]
        assert naukri["failure_reason"] == "MISSING_DEPENDENCY"

        indeed = [r for r in report if r["connector_name"] == "indeed"][0]
        assert indeed["failure_reason"] == "CONNECTION_ERROR"

        for entry in report:
            assert entry["used_in_final"] == "No"

    def test_freshness_filter_removes_old_jobs(self) -> None:
        """Test that the freshness filter removes old jobs."""
        connectors = {
            "linkedin": MockConnector("linkedin", jobs_to_return=10, posted_days_ago=5),
            "naukri": MockConnector("naukri", jobs_to_return=10, posted_days_ago=60),  # Too old
            "indeed": MockConnector("indeed", jobs_to_return=10, posted_days_ago=15),
            "wellfound": MockConnector("wellfound", jobs_to_return=10, posted_days_ago=None),  # No date
        }
        results = self._run_pipeline(connectors)
        # linkedin (10 fresh) + indeed (10 fresh) + wellfound (10 no date = 0.5 score > 0) = 30
        # naukri (10 stale, 60 days > 30 max) = 0
        assert len(results) == 30

        pl = get_pipeline_logger()
        report = pl.get_report()

        linkedin = [r for r in report if r["connector_name"] == "linkedin"][0]
        assert linkedin["jobs_returned"] == 10
        assert linkedin["jobs_after_freshness"] == 10
        assert linkedin["used_in_final"] == "Yes"

        naukri = [r for r in report if r["connector_name"] == "naukri"][0]
        assert naukri["jobs_returned"] == 10
        assert naukri["jobs_after_freshness"] == 0  # All filtered out
        assert naukri["used_in_final"] == "No"

        indeed = [r for r in report if r["connector_name"] == "indeed"][0]
        assert indeed["jobs_returned"] == 10
        assert indeed["jobs_after_freshness"] == 10
        assert indeed["used_in_final"] == "Yes"

    def test_summary_table_after_pipeline(self) -> None:
        """Test the summary table after a full pipeline run."""
        connectors = {
            "linkedin": MockConnector("linkedin", jobs_to_return=15),
            "naukri": MockConnector(
                "naukri",
                should_fail=True,
                failure_exception=TimeoutError("timed out"),
            ),
            "wellfound": MockConnector("wellfound", jobs_to_return=5),
        }
        self._run_pipeline(connectors)

        pl = get_pipeline_logger()
        table = pl.get_summary_table()

        # Verify table structure
        assert "JOB DISCOVERY PIPELINE REPORT" in table
        assert "Connector Name" in table
        assert "linkedin" in table
        assert "naukri" in table
        assert "wellfound" in table
        assert "TIMEOUT" in table
        assert "Pipeline Totals" in table
        assert "Connectors supplying final results" in table

        # Verify the table is printed to stdout (for the user to see)
        print("\n" + table)

    def test_connector_not_in_registry(self) -> None:
        """Test when a connector is not in the registry."""
        pl = get_pipeline_logger()
        pl.log_skipped("unknown_source", "Connector not found in registry")
        report = pl.get_report()
        assert len(report) == 1
        assert report[0]["connector_name"] == "unknown_source"
        assert report[0]["invoked"] == "No"
        assert report[0]["failure_reason"] == "UNKNOWN"


if __name__ == "__main__":
    # Run tests with verbose output
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    pytest.main([__file__, "-v", "--tb=short"])