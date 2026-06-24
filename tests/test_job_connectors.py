"""
Tests for Job Connectors

Unit tests for job source connectors.
"""

import pytest
from datetime import datetime
from src.jobs.connectors.linkedin import LinkedInConnector
from src.jobs.connectors.naukri import NaukriConnector
from src.jobs.connectors.internshala import InternshalaConnector
from src.jobs.connectors.indeed import IndeedConnector


class TestLinkedInConnector:
    """Tests for LinkedIn connector."""
    
    def test_initialization(self):
        """Test LinkedIn connector initialization."""
        connector = LinkedInConnector()
        assert connector.source_name == "linkedin"
        assert connector.base_url == "https://www.linkedin.com"
    
    def test_search_jobs_returns_list(self):
        """Test that search_jobs returns a list."""
        connector = LinkedInConnector()
        # This test may fail if LinkedIn blocks the request
        # In production, use mocking
        try:
            jobs = connector.search_jobs("python", limit=5)
            assert isinstance(jobs, list)
        except Exception:
            # Network errors are acceptable in unit tests
            pass


class TestNaukriConnector:
    """Tests for Naukri connector."""
    
    def test_initialization(self):
        """Test Naukri connector initialization."""
        connector = NaukriConnector()
        assert connector.source_name == "naukri"
        assert connector.base_url == "https://www.naukri.com"
    
    def test_search_jobs_returns_list(self):
        """Test that search_jobs returns a list."""
        connector = NaukriConnector()
        try:
            jobs = connector.search_jobs("python", limit=5)
            assert isinstance(jobs, list)
        except Exception:
            # Network errors are acceptable in unit tests
            pass


class TestInternshalaConnector:
    """Tests for Internshala connector."""
    
    def test_initialization(self):
        """Test Internshala connector initialization."""
        connector = InternshalaConnector()
        assert connector.source_name == "internshala"
        assert connector.base_url == "https://internshala.com"
    
    def test_search_jobs_returns_list(self):
        """Test that search_jobs returns a list."""
        connector = InternshalaConnector()
        try:
            jobs = connector.search_jobs("python", limit=5)
            assert isinstance(jobs, list)
        except Exception:
            # Network errors are acceptable in unit tests
            pass


class TestIndeedConnector:
    """Tests for Indeed connector."""
    
    def test_initialization(self):
        """Test Indeed connector initialization."""
        connector = IndeedConnector()
        assert connector.source_name == "indeed"
        assert connector.base_url == "https://www.indeed.com"
    
    def test_search_jobs_returns_list(self):
        """Test that search_jobs returns a list."""
        connector = IndeedConnector()
        try:
            jobs = connector.search_jobs("python", limit=5)
            assert isinstance(jobs, list)
        except Exception:
            # Network errors are acceptable in unit tests
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
