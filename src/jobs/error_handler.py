"""
Job Discovery Error Handler Module

Provides comprehensive error handling and logging for job discovery operations.
"""

from __future__ import annotations

import logging
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar

from functools import wraps

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for job discovery."""
    NETWORK = "network"
    PARSING = "parsing"
    DATABASE = "database"
    VALIDATION = "validation"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    UNKNOWN = "unknown"


class JobDiscoveryError(Exception):
    """Base exception for job discovery errors."""
    
    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        source: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize job discovery error.
        
        Args:
            message: Error message
            severity: Error severity level
            category: Error category
            source: Error source (e.g., connector name)
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.category = category
        self.source = source
        self.details = details or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "source": self.source,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


class ErrorHandler:
    """Centralized error handler for job discovery operations."""
    
    def __init__(self) -> None:
        """Initialize error handler."""
        self.error_log: List[JobDiscoveryError] = []
        self.max_log_size = 1000
    
    def log_error(
        self,
        error: JobDiscoveryError,
    ) -> None:
        """Log an error to the error log.
        
        Args:
            error: Job discovery error to log
        """
        # Add to error log
        self.error_log.append(error)
        
        # Trim log if too large
        if len(self.error_log) > self.max_log_size:
            self.error_log = self.error_log[-self.max_log_size:]
        
        # Log to appropriate logger based on severity
        log_message = f"[{error.category.value.upper()}] {error.message}"
        if error.source:
            log_message += f" (Source: {error.source})"
        
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, extra=error.details)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(log_message, extra=error.details)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message, extra=error.details)
        else:
            logger.info(log_message, extra=error.details)
    
    def log_exception(
        self,
        exception: Exception,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        source: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> JobDiscoveryError:
        """Log a standard exception as a job discovery error.
        
        Args:
            exception: Exception to log
            severity: Error severity level
            category: Error category
            source: Error source
            details: Additional error details
            
        Returns:
            Created JobDiscoveryError
        """
        error_details = details or {}
        error_details["exception_type"] = type(exception).__name__
        error_details["traceback"] = traceback.format_exc()
        
        error = JobDiscoveryError(
            message=str(exception),
            severity=severity,
            category=category,
            source=source,
            details=error_details,
        )
        
        self.log_error(error)
        return error
    
    def get_recent_errors(
        self,
        limit: int = 50,
        severity: Optional[ErrorSeverity] = None,
        category: Optional[ErrorCategory] = None,
        source: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get recent errors from the error log.
        
        Args:
            limit: Maximum number of errors to return
            severity: Filter by severity
            category: Filter by category
            source: Filter by source
            
        Returns:
            List of error dictionaries
        """
        errors = self.error_log
        
        # Apply filters
        if severity:
            errors = [e for e in errors if e.severity == severity]
        if category:
            errors = [e for e in errors if e.category == category]
        if source:
            errors = [e for e in errors if e.source == source]
        
        # Get most recent
        errors = errors[-limit:]
        
        return [error.to_dict() for error in errors]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors in the log.
        
        Returns:
            Error summary dictionary
        """
        if not self.error_log:
            return {
                "total_errors": 0,
                "by_severity": {},
                "by_category": {},
                "by_source": {},
            }
        
        by_severity: Dict[str, int] = {}
        by_category: Dict[str, int] = {}
        by_source: Dict[str, int] = {}
        
        for error in self.error_log:
            by_severity[error.severity.value] = by_severity.get(error.severity.value, 0) + 1
            by_category[error.category.value] = by_category.get(error.category.value, 0) + 1
            if error.source:
                by_source[error.source] = by_source.get(error.source, 0) + 1
        
        return {
            "total_errors": len(self.error_log),
            "by_severity": by_severity,
            "by_category": by_category,
            "by_source": by_source,
        }
    
    def clear_errors(self) -> None:
        """Clear the error log."""
        self.error_log.clear()
        logger.info("Error log cleared")


# Global error handler instance
error_handler = ErrorHandler()


F = TypeVar('F')


def handle_job_discovery_errors(
    default_return: Any = None,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    log_exception: bool = True,
) -> Callable[[F], F]:
    """Decorator for handling job discovery errors.
    
    Args:
        default_return: Value to return on error
        severity: Error severity level
        category: Error category
        log_exception: Whether to log the exception
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):  # type: ignore
            try:
                return func(*args, **kwargs)
            except JobDiscoveryError as e:
                if log_exception:
                    error_handler.log_error(e)
                return default_return
            except Exception as e:
                if log_exception:
                    error_handler.log_exception(
                        exception=e,
                        severity=severity,
                        category=category,
                        source=func.__name__,
                    )
                return default_return
        return wrapper  # type: ignore
    return decorator  # type: ignore


def create_network_error(message: str, source: Optional[str] = None) -> JobDiscoveryError:
    """Create a network error.
    
    Args:
        message: Error message
        source: Error source
        
    Returns:
        JobDiscoveryError with NETWORK category
    """
    return JobDiscoveryError(
        message=message,
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.NETWORK,
        source=source,
    )


def create_parsing_error(message: str, source: Optional[str] = None) -> JobDiscoveryError:
    """Create a parsing error.
    
    Args:
        message: Error message
        source: Error source
        
    Returns:
        JobDiscoveryError with PARSING category
    """
    return JobDiscoveryError(
        message=message,
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.PARSING,
        source=source,
    )


def create_database_error(message: str, source: Optional[str] = None) -> JobDiscoveryError:
    """Create a database error.
    
    Args:
        message: Error message
        source: Error source
        
    Returns:
        JobDiscoveryError with DATABASE category
    """
    return JobDiscoveryError(
        message=message,
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.DATABASE,
        source=source,
    )


def create_rate_limit_error(message: str, source: Optional[str] = None) -> JobDiscoveryError:
    """Create a rate limit error.
    
    Args:
        message: Error message
        source: Error source
        
    Returns:
        JobDiscoveryError with RATE_LIMIT category
    """
    return JobDiscoveryError(
        message=message,
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.RATE_LIMIT,
        source=source,
    )
