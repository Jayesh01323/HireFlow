"""
Pipeline Logger Module

Centralized logging for the Job Discovery search pipeline.
Tracks every connector invocation, its result, failure reason,
and whether its jobs ultimately appear in the final UI results.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FailureReason(str, Enum):
    """Classification of connector failure reasons."""
    CAPTCHA = "CAPTCHA"
    HTTP_ERROR = "HTTP_ERROR"
    SELECTOR_MISMATCH = "SELECTOR_MISMATCH"
    TIMEOUT = "TIMEOUT"
    PARSING_ERROR = "PARSING_ERROR"
    MISSING_DEPENDENCY = "MISSING_DEPENDENCY"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
    UNKNOWN = "UNKNOWN"


@dataclass
class ConnectorResult:
    """Result of a single connector invocation."""
    connector_name: str
    invoked: bool = False
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    success: bool = False
    jobs_returned: int = 0
    jobs_after_freshness: int = 0
    failure_reason: Optional[FailureReason] = None
    failure_detail: Optional[str] = None
    used_in_final: bool = False
    error_type: Optional[str] = None  # The Python exception type name
    http_status: Optional[int] = None  # HTTP status code returned by the source
    actual_url: Optional[str] = None  # The actual URL that was visited


class PipelineLogger:
    """Tracks detailed logging for the entire job search pipeline."""
    
    def __init__(self) -> None:
        """Initialize pipeline logger."""
        self.connector_results: Dict[str, ConnectorResult] = {}
        self.pipeline_start_time: Optional[float] = None
        self.pipeline_end_time: Optional[float] = None
        self.total_jobs_before_dedup: int = 0
        self.total_jobs_after_dedup: int = 0
        self.total_jobs_after_freshness: int = 0
        self.total_jobs_final: int = 0
        self.used_mock_fallback: bool = False
        self.mock_fallback_reason: Optional[str] = None
    
    def register_connector(self, connector_name: str) -> None:
        """Register a connector for tracking.
        
        Args:
            connector_name: Name of the connector
        """
        if connector_name not in self.connector_results:
            self.connector_results[connector_name] = ConnectorResult(
                connector_name=connector_name
            )
    
    def log_start(self, connector_name: str) -> None:
        """Log that a connector has started searching.
        
        Args:
            connector_name: Name of the connector
        """
        self.register_connector(connector_name)
        self.connector_results[connector_name].invoked = True
        self.connector_results[connector_name].start_time = time.time()
        logger.info(f"🔍 PIPELINE: Starting connector '{connector_name}'")
    
    def log_success(
        self,
        connector_name: str,
        jobs_returned: int,
    ) -> None:
        """Log that a connector succeeded.
        
        Args:
            connector_name: Name of the connector
            jobs_returned: Number of jobs returned
        """
        self.register_connector(connector_name)
        result = self.connector_results[connector_name]
        result.success = True
        result.jobs_returned = jobs_returned
        result.end_time = time.time()
        result.duration_ms = (
            (result.end_time - result.start_time) * 1000
            if result.start_time
            else None
        )
        if result.duration_ms is not None:
            logger.info(
                f"✅ PIPELINE: Connector '{connector_name}' succeeded — "
                f"{jobs_returned} jobs returned "
                f"({result.duration_ms:.0f}ms)"
            )
        else:
            logger.info(
                f"✅ PIPELINE: Connector '{connector_name}' succeeded — "
                f"{jobs_returned} jobs returned"
            )
    
    def log_failure(
        self,
        connector_name: str,
        reason: FailureReason,
        detail: Optional[str] = None,
        error_type: Optional[str] = None,
    ) -> None:
        """Log that a connector failed.
        
        Args:
            connector_name: Name of the connector
            reason: Classification of the failure
            detail: Detailed error message
            error_type: Python exception type name
        """
        self.register_connector(connector_name)
        result = self.connector_results[connector_name]
        result.success = False
        result.failure_reason = reason
        result.failure_detail = detail
        result.error_type = error_type
        result.end_time = time.time()
        result.duration_ms = (
            (result.end_time - result.start_time) * 1000
            if result.start_time
            else None
        )
        logger.warning(
            f"❌ PIPELINE: Connector '{connector_name}' FAILED — "
            f"reason={reason.value}, detail={detail}, "
            f"error_type={error_type}"
        )
    
    def log_skipped(self, connector_name: str, reason: str) -> None:
        """Log that a connector was skipped (not invoked).
        
        Args:
            connector_name: Name of the connector
            reason: Why it was skipped
        """
        self.register_connector(connector_name)
        result = self.connector_results[connector_name]
        result.invoked = False
        result.failure_reason = FailureReason.UNKNOWN
        result.failure_detail = f"Skipped: {reason}"
        logger.info(f"⏭️ PIPELINE: Connector '{connector_name}' skipped — {reason}")
    
    def mark_used_in_final(self, connector_name: str) -> None:
        """Mark a connector as having jobs in the final results.
        
        Args:
            connector_name: Name of the connector
        """
        self.register_connector(connector_name)
        self.connector_results[connector_name].used_in_final = True
    
    def set_freshness_count(self, connector_name: str, count: int) -> None:
        """Set the number of jobs that passed the freshness filter.
        
        Args:
            connector_name: Name of the connector
            count: Number of jobs after freshness filtering
        """
        self.register_connector(connector_name)
        self.connector_results[connector_name].jobs_after_freshness = count
    
    def set_http_status(self, connector_name: str, status: int) -> None:
        """Set the HTTP status code returned by the source.
        
        Args:
            connector_name: Name of the connector
            status: HTTP status code
        """
        self.register_connector(connector_name)
        self.connector_results[connector_name].http_status = status
    
    def set_actual_url(self, connector_name: str, url: str) -> None:
        """Set the actual URL that was visited.
        
        Args:
            connector_name: Name of the connector
            url: The URL that was actually visited
        """
        self.register_connector(connector_name)
        self.connector_results[connector_name].actual_url = url
    
    def classify_failure(
        self,
        exception: Exception,
    ) -> tuple[FailureReason, str]:
        """Classify an exception into a FailureReason.
        
        Args:
            exception: The exception to classify
            
        Returns:
            Tuple of (FailureReason, detail string)
        """
        exc_name = type(exception).__name__
        exc_msg = str(exception)
        
        # Timeout
        if isinstance(exception, TimeoutError):
            return FailureReason.TIMEOUT, exc_msg
        
        # Connection / network errors
        if isinstance(exception, ConnectionError):
            return FailureReason.CONNECTION_ERROR, exc_msg
        
        # ImportError / ModuleNotFoundError
        if isinstance(exception, ImportError):
            return FailureReason.MISSING_DEPENDENCY, exc_msg
        
        # CAPTCHA detection (check message content)
        msg_lower = exc_msg.lower()
        if any(
            keyword in msg_lower
            for keyword in [
                "captcha", "recaptcha", "datadome", "blocked",
                "automated access", "unusual traffic",
                "please verify", "security check",
            ]
        ):
            return FailureReason.CAPTCHA, exc_msg
        
        # Rate limiting (check before general HTTP errors for specific status codes)
        if any(
            keyword in msg_lower
            for keyword in ["rate limit", "too many requests", "429", "throttl"]
        ):
            return FailureReason.RATE_LIMIT, exc_msg
        
        # HTTP errors
        if "http" in exc_name.lower() or "status" in msg_lower or "http" in msg_lower:
            return FailureReason.HTTP_ERROR, exc_msg
        
        # Parsing errors
        if any(
            keyword in exc_name.lower()
            for keyword in ["parse", "decode", "json", "keyerror", "attributeerror"]
        ):
            return FailureReason.PARSING_ERROR, exc_msg
        
        # Selector mismatch (common in browser-based scraping)
        if any(
            keyword in msg_lower
            for keyword in [
                "selector", "element not found", "no such element",
                "xpath", "css selector",
            ]
        ):
            return FailureReason.SELECTOR_MISMATCH, exc_msg
        
        # Authentication errors
        if any(
            keyword in msg_lower
            for keyword in ["auth", "api key", "unauthorized", "forbidden", "403", "401"]
        ):
            return FailureReason.AUTH_ERROR, exc_msg
        
        return FailureReason.UNKNOWN, exc_msg
    
    def get_report(self) -> List[Dict[str, Any]]:
        """Get the full pipeline report as a list of dicts.
        
        Returns:
            List of connector result dictionaries
        """
        report = []
        for name in sorted(self.connector_results.keys()):
            r = self.connector_results[name]
            report.append({
                "connector_name": r.connector_name,
                "invoked": "Yes" if r.invoked else "No",
                "success": r.success,
                "jobs_returned": r.jobs_returned,
                "jobs_after_freshness": r.jobs_after_freshness,
                "failure_reason": r.failure_reason.value if r.failure_reason and not r.success else "",
                "failure_detail": r.failure_detail if r.failure_detail and not r.success else "",
                "error_type": r.error_type if r.error_type and not r.success else "",
                "used_in_final": "Yes" if r.used_in_final else "No",
                "duration_ms": round(r.duration_ms, 1) if r.duration_ms is not None else None,
                "http_status": r.http_status,
                "actual_url": r.actual_url,
            })
        return report
    
    def get_summary_table(self) -> str:
        """Get a formatted summary table string.
        
        Returns:
            Formatted table as a string
        """
        lines = []
        lines.append("=" * 120)
        lines.append("JOB DISCOVERY PIPELINE REPORT")
        lines.append("=" * 120)
        
        # Header
        lines.append(
            f"{'Connector Name':<20} {'Invoked':<10} {'Jobs Returned':<15} "
            f"{'After Freshness':<16} {'Failure Reason':<25} {'Used in Final':<15}"
        )
        lines.append("-" * 120)
        
        for entry in self.get_report():
            failure = (
                entry["failure_reason"]
                if entry["failure_reason"]
                else ("N/A" if entry["success"] else "UNKNOWN")
            )
            lines.append(
                f"{entry['connector_name']:<20} "
                f"{entry['invoked']:<10} "
                f"{entry['jobs_returned']:<15} "
                f"{entry['jobs_after_freshness']:<16} "
                f"{failure:<25} "
                f"{entry['used_in_final']:<15}"
            )
        
        lines.append("-" * 120)
        lines.append(f"\nPipeline Totals:")
        lines.append(f"  Total jobs before dedup:    {self.total_jobs_before_dedup}")
        lines.append(f"  Total jobs after dedup:     {self.total_jobs_after_dedup}")
        lines.append(f"  Total jobs after freshness: {self.total_jobs_after_freshness}")
        lines.append(f"  Total jobs in final result: {self.total_jobs_final}")
        lines.append(f"  Used mock fallback:         {self.used_mock_fallback}")
        if self.mock_fallback_reason:
            lines.append(f"  Mock fallback reason:       {self.mock_fallback_reason}")
        
        # List which connectors contributed to final results
        used_connectors = [
            r.connector_name
            for r in self.connector_results.values()
            if r.used_in_final
        ]
        if used_connectors:
            lines.append(f"\nConnectors supplying final results: {', '.join(used_connectors)}")
        else:
            lines.append("\nNo connectors supplied final results.")
        
        lines.append("=" * 120)
        return "\n".join(lines)
    
    def log_pipeline_start(self) -> None:
        """Log the start of the entire pipeline."""
        self.pipeline_start_time = time.time()
        logger.info("=" * 60)
        logger.info("🚀 PIPELINE: Job Discovery search started")
        logger.info("=" * 60)
    
    def log_pipeline_end(self) -> None:
        """Log the end of the entire pipeline."""
        self.pipeline_end_time = time.time()
        total_duration = (
            (self.pipeline_end_time - self.pipeline_start_time) * 1000
            if self.pipeline_start_time
            else 0
        )
        logger.info("=" * 60)
        logger.info(
            f"🏁 PIPELINE: Job Discovery search completed in {total_duration:.0f}ms"
        )
        logger.info("=" * 60)
        
        # Log the summary table
        summary = self.get_summary_table()
        for line in summary.split("\n"):
            logger.info(line)


# Global singleton instance
_pipeline_logger: Optional[PipelineLogger] = None


def get_pipeline_logger() -> PipelineLogger:
    """Get or create the global pipeline logger singleton.
    
    Returns:
        PipelineLogger instance
    """
    global _pipeline_logger
    if _pipeline_logger is None:
        _pipeline_logger = PipelineLogger()
    return _pipeline_logger


def reset_pipeline_logger() -> PipelineLogger:
    """Reset the global pipeline logger (for testing).
    
    Returns:
        New PipelineLogger instance
    """
    global _pipeline_logger
    _pipeline_logger = PipelineLogger()
    return _pipeline_logger