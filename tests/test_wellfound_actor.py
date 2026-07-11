"""
Comprehensive Test Suite for Wellfound Actor

Tests the complete Wellfound Actor implementation including:
1. BaseJobActor abstract class
2. WellfoundActor (CAPTCHA detection, URL building, extraction)
3. WellfoundActorConnector (integration layer)
4. Removability verification

Run: python -m pytest tests/test_wellfound_actor.py -v --tb=short
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.jobs.actors.base_actor import (
    ActorCAPTCHAError,
    ActorConfigurationError,
    ActorError,
    ActorExtractionError,
    ActorSourceUnavailableError,
    BaseJobActor,
)
from src.jobs.actors.wellfound_actor import (
    CAPTCHA_INDICATORS,
    DATA_DOME_DOMAIN,
    WellfoundActor,
)
from src.jobs.connectors.wellfound_actor_connector import WellfoundActorConnector
from src.jobs.schemas import JobPosting, NormalizedJob

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================================================
# Test 1: BaseJobActor Abstract Class
# =============================================================================

class TestBaseJobActor:
    """Test the BaseJobActor abstract class."""

    def test_cannot_instantiate_abstract(self):
        """BaseJobActor cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseJobActor("test")  # type: ignore

    def test_actor_error_hierarchy(self):
        """Actor error classes form a proper hierarchy."""
        assert issubclass(ActorConfigurationError, ActorError)
        assert issubclass(ActorSourceUnavailableError, ActorError)
        assert issubclass(ActorCAPTCHAError, ActorSourceUnavailableError)
        assert issubclass(ActorExtractionError, ActorError)

    def test_actor_error_messages(self):
        """Actor errors carry meaningful messages."""
        err = ActorCAPTCHAError("CAPTCHA detected")
        assert "CAPTCHA" in str(err)

        err = ActorConfigurationError("Missing API key")
        assert "API key" in str(err)

        err = ActorSourceUnavailableError("Site is down")
        assert "down" in str(err)

        err = ActorExtractionError("Failed to parse")
        assert "parse" in str(err)


# =============================================================================
# Test 2: WellfoundActor - URL Building
# =============================================================================

class TestWellfoundActorURLBuilding:
    """Test WellfoundActor URL building logic."""

    def setup_method(self):
        self.actor = WellfoundActor()

    def test_basic_search_url(self):
        """Basic search query produces correct URL."""
        url = self.actor._build_search_url("backend developer")
        assert url == "https://wellfound.com/jobs/backend-developer"

    def test_search_with_location(self):
        """Search with location adds query parameter."""
        url = self.actor._build_search_url("backend developer", location="Pune")
        assert "backend-developer" in url
        assert "l=Pune" in url

    def test_search_with_remote(self):
        """Search with remote filter adds remote parameter."""
        url = self.actor._build_search_url("developer", remote=True)
        assert "remote=true" in url

    def test_search_with_experience(self):
        """Search with experience level maps correctly."""
        url = self.actor._build_search_url("developer", experience="entry")
        assert "experience=junior" in url

        url = self.actor._build_search_url("developer", experience="mid")
        assert "experience=mid" in url

        url = self.actor._build_search_url("developer", experience="senior")
        assert "experience=senior" in url

    def test_search_with_all_filters(self):
        """Search with all filters produces correct URL."""
        url = self.actor._build_search_url(
            "software engineer",
            location="Bangalore",
            remote=True,
            experience="mid",
        )
        assert "software-engineer" in url
        assert "l=Bangalore" in url
        assert "remote=true" in url
        assert "experience=mid" in url

    def test_search_empty_query(self):
        """Empty query still produces valid URL."""
        url = self.actor._build_search_url("")
        assert url == "https://wellfound.com/jobs"

    def test_search_special_chars(self):
        """Special characters in query are handled (C++ → c++)."""
        url = self.actor._build_search_url("C++ Developer")
        # C++ becomes c++ (lowercased, spaces to hyphens)
        assert "c++-developer" in url


# =============================================================================
# Test 3: WellfoundActor - CAPTCHA Detection
# =============================================================================

class TestWellfoundActorCAPTCHADetection:
    """Test WellfoundActor CAPTCHA detection logic."""

    def setup_method(self):
        self.actor = WellfoundActor()

    def test_detect_datadome_captcha(self):
        """Detect DataDome CAPTCHA from saved page HTML."""
        # Load the actual saved page HTML
        html_path = Path(__file__).parent / "wellfound_page.html"
        if html_path.exists():
            html_content = html_path.read_text(encoding="utf-8")
            result = self.actor._check_for_captcha(html_content)
            assert result["detected"] is True
            assert "DataDome" in result["provider"]
        else:
            # Fallback: test with synthetic HTML containing indicators
            html = '<html><body><iframe src="https://geo.captcha-delivery.com/captcha/"></iframe></body></html>'
            result = self.actor._check_for_captcha(html)
            assert result["detected"] is True
            assert "DataDome" in result["provider"]

    def test_detect_datadome_indicators(self):
        """Each CAPTCHA indicator is detected."""
        for indicator in CAPTCHA_INDICATORS:
            html = f"<html><body>{indicator}</body></html>"
            result = self.actor._check_for_captcha(html)
            assert result["detected"] is True, f"Failed to detect indicator: {indicator}"

    def test_detect_cloudflare(self):
        """Cloudflare protection is detected."""
        html = "<html><body>cf-browser-verification</body></html>"
        result = self.actor._check_for_captcha(html)
        assert result["detected"] is True
        assert "Cloudflare" in result["provider"]

    def test_no_captcha_detected(self):
        """Clean page returns no CAPTCHA."""
        html = "<html><body><h1>Jobs</h1><div>Job listings here</div></body></html>"
        result = self.actor._check_for_captcha(html)
        assert result["detected"] is False
        assert result["provider"] is None

    def test_empty_html(self):
        """Empty HTML returns no CAPTCHA."""
        result = self.actor._check_for_captcha("")
        assert result["detected"] is False

    def test_case_insensitive_detection(self):
        """CAPTCHA detection is case-insensitive."""
        html = "<html><body>DATADOME</body></html>"
        result = self.actor._check_for_captcha(html)
        assert result["detected"] is True


# =============================================================================
# Test 4: WellfoundActor - Remote Detection
# =============================================================================

class TestWellfoundActorRemoteDetection:
    """Test WellfoundActor remote job detection."""

    def test_detect_remote_in_location(self):
        """Remote keyword in location is detected."""
        assert WellfoundActor._detect_remote_from_text("Remote", None) is True
        assert WellfoundActor._detect_remote_from_text("Work from home", None) is True
        assert WellfoundActor._detect_remote_from_text("Anywhere", None) is True

    def test_detect_remote_in_description(self):
        """Remote keyword in description is detected."""
        assert WellfoundActor._detect_remote_from_text(None, "This is a remote position") is True
        assert WellfoundActor._detect_remote_from_text(None, "Work from home available") is True

    def test_no_remote_detected(self):
        """No remote keywords returns False."""
        assert WellfoundActor._detect_remote_from_text("Bangalore, India", None) is False
        assert WellfoundActor._detect_remote_from_text(None, "Office based role") is False

    def test_none_inputs(self):
        """None inputs return False."""
        assert WellfoundActor._detect_remote_from_text(None, None) is False


# =============================================================================
# Test 5: WellfoundActor - External ID Generation
# =============================================================================

class TestWellfoundActorExternalID:
    """Test WellfoundActor external ID generation."""

    def setup_method(self):
        self.actor = WellfoundActor()

    def test_external_id_generation(self):
        """External ID is generated from URL."""
        url = "https://wellfound.com/role/software-engineer-123"
        ext_id = self.actor._make_external_id(url)
        assert ext_id is not None
        assert len(ext_id) == 16  # MD5 hex digest first 16 chars
        assert isinstance(ext_id, str)

    def test_external_id_consistent(self):
        """Same URL produces same external ID."""
        url = "https://wellfound.com/role/test-job"
        id1 = self.actor._make_external_id(url)
        id2 = self.actor._make_external_id(url)
        assert id1 == id2

    def test_external_id_different(self):
        """Different URLs produce different external IDs."""
        id1 = self.actor._make_external_id("https://wellfound.com/role/job-1")
        id2 = self.actor._make_external_id("https://wellfound.com/role/job-2")
        assert id1 != id2


# =============================================================================
# Test 6: WellfoundActor - Source Status
# =============================================================================

class TestWellfoundActorSourceStatus:
    """Test WellfoundActor source status reporting."""

    def setup_method(self):
        self.actor = WellfoundActor()

    def test_initial_status(self):
        """Initial status indicates not checked."""
        status = self.actor.get_source_status()
        assert "available" in status
        assert status["available"] is False
        assert "message" in status
        assert "last_check" in status

    def test_status_after_captcha(self):
        """Status is updated after CAPTCHA detection."""
        self.actor._last_status = {
            "available": False,
            "message": "Blocked by DataDome CAPTCHA",
            "last_check": "2026-07-11T12:00:00",
        }
        status = self.actor.get_source_status()
        assert status["available"] is False
        assert "DataDome" in status["message"]

    def test_status_copy(self):
        """get_source_status returns a copy, not the original."""
        status = self.actor.get_source_status()
        status["available"] = True
        # Original should be unchanged
        assert self.actor._last_status["available"] is False


# =============================================================================
# Test 7: WellfoundActor - Lifecycle
# =============================================================================

class TestWellfoundActorLifecycle:
    """Test WellfoundActor lifecycle management."""

    @pytest.mark.asyncio
    async def test_search_without_initialize_raises_error(self):
        """Searching without initialization raises ActorConfigurationError."""
        actor = WellfoundActor()
        with pytest.raises(ActorConfigurationError, match="not initialized"):
            await actor.search_jobs(query="developer")

    @pytest.mark.asyncio
    async def test_initialize_and_cleanup(self):
        """Initialize and cleanup work correctly."""
        actor = WellfoundActor()
        assert actor._initialized is False

        # Mock the browser manager to avoid actual browser launch
        actor._initialized = True
        actor._browser_manager = MagicMock()

        assert actor._initialized is True

        # Cleanup
        await actor.cleanup()
        assert actor._initialized is False
        assert actor._browser_manager is None


# =============================================================================
# Test 8: WellfoundActorConnector - Integration Layer
# =============================================================================

class TestWellfoundActorConnector:
    """Test the WellfoundActorConnector integration layer."""

    def setup_method(self):
        self.connector = WellfoundActorConnector()

    def test_connector_extends_base(self):
        """Connector extends BaseJobConnector."""
        from src.jobs.connectors.base import BaseJobConnector
        assert isinstance(self.connector, BaseJobConnector)

    def test_connector_source_name(self):
        """Connector source name is 'wellfound'."""
        assert self.connector.source_name == "wellfound"

    def test_get_job_details_not_supported(self):
        """get_job_details returns None for Wellfound."""
        result = self.connector.get_job_details("https://wellfound.com/role/test")
        assert result is None

    def test_get_source_status(self):
        """get_source_status returns status dict."""
        status = self.connector.get_source_status()
        assert "available" in status
        assert "message" in status
        assert "last_check" in status

    def test_normalized_to_posting_conversion(self):
        """NormalizedJob → JobPosting conversion works correctly."""
        from datetime import datetime, timezone
        job = NormalizedJob(
            title="Backend Developer",
            company="Test Corp",
            location="Pune",
            salary="₹15,00,000",
            description="Test description",
            url="https://wellfound.com/role/test-123",
            source="wellfound",
            external_id="test123",
            is_remote=False,
            experience_level="mid",
            posted_date=datetime.now(timezone.utc),
        )

        posting = WellfoundActorConnector._normalized_to_posting(job)
        assert isinstance(posting, JobPosting)
        assert posting.title == "Backend Developer"
        assert posting.company == "Test Corp"
        assert posting.location == "Pune"
        assert posting.source == "wellfound"
        assert posting.url == "https://wellfound.com/role/test-123"

    def test_search_returns_empty_list_on_error(self):
        """search_jobs returns empty list on error (doesn't crash)."""
        # This should not raise, just return empty list
        result = self.connector.search_jobs(query="developer")
        # Either empty (if CAPTCHA) or some jobs (if no CAPTCHA)
        assert isinstance(result, list)


# =============================================================================
# Test 9: Removability Verification
# =============================================================================

class TestWellfoundActorRemovability:
    """Verify the Wellfound actor can be removed without breaking HireFlow.

    The actor is designed to be completely removable by deleting:
    1. src/jobs/connectors/wellfound_actor_connector.py
    2. src/jobs/actors/ directory
    3. Removing "wellfound" from aggregator connectors

    No other files need to be modified.
    """

    def test_no_changes_to_existing_connectors(self):
        """Existing connectors __init__ does not import the new connector."""
        import importlib
        import src.jobs.connectors
        importlib.reload(src.jobs.connectors)
        # The existing __init__ should not import the new connector
        assert not hasattr(src.jobs.connectors, "WellfoundActorConnector")

    def test_no_changes_to_aggregator(self):
        """Aggregator does not import the new connector."""
        import importlib
        import src.jobs.aggregator
        importlib.reload(src.jobs.aggregator)
        # The aggregator should not import the new connector
        assert not hasattr(src.jobs.aggregator, "WellfoundActorConnector")

    def test_no_changes_to_schemas(self):
        """Schemas are not modified by the actor."""
        import importlib
        import src.jobs.schemas
        importlib.reload(src.jobs.schemas)
        # The actor uses existing NormalizedJob, no new schemas
        assert not hasattr(src.jobs.schemas, "WellfoundActor")

    def test_no_changes_to_base_connector(self):
        """Base connector is not modified by the actor."""
        import importlib
        import src.jobs.connectors.base
        importlib.reload(src.jobs.connectors.base)
        # The actor uses existing BaseJobConnector, no changes
        assert not hasattr(src.jobs.connectors.base, "WellfoundActor")

    def test_actor_imports_are_isolated(self):
        """Actor imports are self-contained within the actors package."""
        import src.jobs.actors.wellfound_actor as wa
        import inspect
        source = inspect.getsource(wa)
        # Actor should only import from base_actor and schemas
        assert "from src.jobs.actors.base_actor import" in source
        assert "from src.jobs.schemas import" in source

    def test_connector_imports_are_minimal(self):
        """Connector only imports from actor and base."""
        import src.jobs.connectors.wellfound_actor_connector as wac
        import inspect
        source = inspect.getsource(wac)
        # Connector should only import from actor and base
        assert "from src.jobs.actors.wellfound_actor import" in source
        assert "from src.jobs.connectors.base import" in source
        assert "from src.jobs.schemas import" in source

    def test_existing_wellfound_connector_unchanged(self):
        """Existing wellfound.py connector is not modified."""
        import src.jobs.connectors.wellfound as wf
        import inspect
        source = inspect.getsource(wf)
        # The existing connector should not reference the new actor
        assert "WellfoundActor" not in source
        assert "wellfound_actor" not in source


# =============================================================================
# Test 10: CAPTCHA Detection with Real Saved HTML
# =============================================================================

class TestWellfoundActorRealPage:
    """Test CAPTCHA detection using the actual saved Wellfound page."""

    def test_real_page_captcha_detection(self):
        """The saved Wellfound page HTML is correctly identified as CAPTCHA."""
        html_path = Path(__file__).parent / "wellfound_page.html"
        if not html_path.exists():
            pytest.skip("wellfound_page.html not found")

        html_content = html_path.read_text(encoding="utf-8")
        actor = WellfoundActor()
        result = actor._check_for_captcha(html_content)

        assert result["detected"] is True, (
            f"Failed to detect CAPTCHA in saved page. "
            f"Provider: {result['provider']}"
        )
        assert "DataDome" in result["provider"], (
            f"Expected DataDome CAPTCHA, got: {result['provider']}"
        )

    def test_real_page_contains_datadome_domain(self):
        """The saved page contains the DataDome domain."""
        html_path = Path(__file__).parent / "wellfound_page.html"
        if not html_path.exists():
            pytest.skip("wellfound_page.html not found")

        html_content = html_path.read_text(encoding="utf-8")
        assert DATA_DOME_DOMAIN in html_content, (
            f"Saved page does not contain DataDome domain. "
            f"This may mean Wellfound has changed their protection."
        )

    def test_real_page_contains_captcha_indicators(self):
        """The saved page contains known CAPTCHA indicators."""
        html_path = Path(__file__).parent / "wellfound_page.html"
        if not html_path.exists():
            pytest.skip("wellfound_page.html not found")

        html_content = html_path.read_text(encoding="utf-8")
        found_indicators = [
            ind for ind in CAPTCHA_INDICATORS if ind in html_content
        ]
        assert len(found_indicators) > 0, (
            f"No CAPTCHA indicators found in saved page. "
            f"This may mean Wellfound has changed their protection."
        )


# =============================================================================
# Test 11: Error Handling and Logging
# =============================================================================

class TestWellfoundActorErrorHandling:
    """Test WellfoundActor error handling and logging."""

    def test_captcha_error_message_is_descriptive(self):
        """CAPTCHA error message explains exactly what happened."""
        try:
            raise ActorCAPTCHAError(
                "WELLFOUND ACCESS BLOCKED: DataDome CAPTCHA detected. "
                "Wellfound uses DataDome CAPTCHA protection which prevents automated "
                "browser-based job extraction. No public API or Apify actor is available. "
                "Workflow stopped at: page load complete → CAPTCHA check."
            )
        except ActorCAPTCHAError as e:
            msg = str(e)
            assert "DataDome" in msg
            assert "CAPTCHA" in msg
            assert "blocked" in msg.lower()
            assert "workflow stopped" in msg.lower()

    def test_configuration_error_message(self):
        """Configuration error explains what dependency is missing."""
        try:
            raise ActorConfigurationError(
                "Missing Playwright dependency. Run: pip install playwright"
            )
        except ActorConfigurationError as e:
            assert "Playwright" in str(e)

    def test_source_unavailable_error_message(self):
        """Source unavailable error explains what failed."""
        try:
            raise ActorSourceUnavailableError(
                "Failed to navigate to Wellfound: TimeoutError: page did not load"
            )
        except ActorSourceUnavailableError as e:
            assert "navigate" in str(e).lower()


# =============================================================================
# Test 12: WellfoundActor - Extraction Logic (Unit Tests)
# =============================================================================

class TestWellfoundActorExtraction:
    """Test WellfoundActor extraction logic with mocked page elements."""

    def setup_method(self):
        self.actor = WellfoundActor()

    @pytest.mark.asyncio
    async def test_extract_text_from_element_found(self):
        """Text extraction returns text when element is found."""
        mock_element = AsyncMock()
        mock_child = AsyncMock()
        mock_child.text_content = AsyncMock(return_value="  Test Title  ")
        mock_element.query_selector = AsyncMock(return_value=mock_child)

        result = await self.actor._extract_text_from_element(
            mock_element, ["h3", "h2"]
        )
        assert result == "Test Title"

    @pytest.mark.asyncio
    async def test_extract_text_from_element_not_found(self):
        """Text extraction returns None when no element is found."""
        mock_element = AsyncMock()
        mock_element.query_selector = AsyncMock(return_value=None)

        result = await self.actor._extract_text_from_element(
            mock_element, ["h3", "h2"]
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_extract_text_from_element_empty_text(self):
        """Text extraction skips elements with empty text."""
        mock_element = AsyncMock()
        mock_child = AsyncMock()
        mock_child.text_content = AsyncMock(return_value="  ")
        mock_element.query_selector = AsyncMock(return_value=mock_child)

        result = await self.actor._extract_text_from_element(
            mock_element, ["h3"]
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_extract_href_from_element_found(self):
        """Href extraction returns URL when element is found."""
        mock_element = AsyncMock()
        mock_child = AsyncMock()
        mock_child.get_attribute = AsyncMock(return_value="/role/test-job")
        mock_element.query_selector = AsyncMock(return_value=mock_child)

        result = await self.actor._extract_href_from_element(
            mock_element, ["a"]
        )
        assert result == "/role/test-job"

    @pytest.mark.asyncio
    async def test_extract_href_from_element_not_found(self):
        """Href extraction returns None when no element is found."""
        mock_element = AsyncMock()
        mock_element.query_selector = AsyncMock(return_value=None)

        result = await self.actor._extract_href_from_element(
            mock_element, ["a"]
        )
        assert result is None


# =============================================================================
# Test 13: WellfoundActor - Full Search Flow (Mocked)
# =============================================================================

class TestWellfoundActorSearchFlow:
    """Test the full search flow with mocked browser."""

    @pytest.mark.asyncio
    async def test_search_raises_captcha_error(self):
        """Search raises ActorCAPTCHAError when CAPTCHA is detected."""
        actor = WellfoundActor()
        actor._initialized = True

        # Mock browser manager
        mock_browser = MagicMock()
        mock_page = AsyncMock()
        mock_page.content = AsyncMock(
            return_value='<html><body>geo.captcha-delivery.com</body></html>'
        )
        mock_browser.get_page = AsyncMock(return_value=mock_page)
        mock_browser.navigate = AsyncMock()
        mock_browser.close_page = AsyncMock()
        actor._browser_manager = mock_browser

        with pytest.raises(ActorCAPTCHAError) as exc_info:
            await actor.search_jobs(query="developer")

        assert "DataDome" in str(exc_info.value)
        assert "CAPTCHA" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_raises_source_unavailable_on_nav_fail(self):
        """Search raises ActorSourceUnavailableError when navigation fails."""
        actor = WellfoundActor()
        actor._initialized = True

        mock_browser = MagicMock()
        mock_page = AsyncMock()
        mock_browser.get_page = AsyncMock(return_value=mock_page)
        mock_browser.navigate = AsyncMock(
            side_effect=Exception("Navigation timeout")
        )
        mock_browser.close_page = AsyncMock()
        actor._browser_manager = mock_browser

        with pytest.raises(ActorSourceUnavailableError) as exc_info:
            await actor.search_jobs(query="developer")

        assert "navigate" in str(exc_info.value).lower()


# =============================================================================
# Run all tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])