"""
Wellfound Job Actor

Production-quality job data acquisition actor for Wellfound (formerly AngelList).

CURRENT STATUS: Wellfound uses DataDome CAPTCHA protection which blocks automated
browser access. This actor implements:

1. Browser-based extraction attempt with CAPTCHA detection
2. Clear error reporting when CAPTCHA blocks access
3. Source status reporting indicating availability limitations
4. Complete isolation from the rest of HireFlow

If Wellfound changes their protection in the future:
- Update CAPTCHA detection patterns in _check_for_captcha()
- Update selectors in _extract_job_cards_from_page()
- Update URL generation in _build_search_url()

Architecture:
    BaseJobActor
        └── WellfoundActor (self-contained, independently removable)
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.jobs.actors.base_actor import (
    ActorCAPTCHAError,
    ActorConfigurationError,
    ActorError,
    ActorExtractionError,
    ActorSourceUnavailableError,
    BaseJobActor,
)
from src.jobs.schemas import NormalizedJob

logger = logging.getLogger(__name__)

# CAPTCHA detection patterns - extract from saved page HTML for accuracy
CAPTCHA_INDICATORS: List[str] = [
    "datadome",
    "captcha-delivery.com",
    "geo.captcha-delivery.com",
    "data-cfasync",
    "challenge-platform",
]
DATA_DOME_DOMAIN = "geo.captcha-delivery.com"


class WellfoundActor(BaseJobActor):
    """Actor for Wellfound job postings.

    Wellfound uses DataDome CAPTCHA protection. This actor detects the
    CAPTCHA and reports it clearly, rather than attempting to bypass it.

    If Wellfound removes CAPTCHA or provides an official API in the future,
    update the extraction logic here.
    """

    def __init__(self) -> None:
        """Initialize Wellfound actor."""
        super().__init__("wellfound")
        self.base_url = "https://wellfound.com"
        self.search_url = "https://wellfound.com/jobs"
        self._browser_manager: Optional[Any] = None
        self._last_status: Dict[str, Any] = {
            "available": False,
            "message": "Not checked yet",
            "last_check": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
        }

    async def initialize(self) -> None:
        """Initialize the browser manager.

        Raises:
            ActorConfigurationError: If browser initialization fails
        """
        if self._initialized:
            logger.debug("WellfoundActor already initialized")
            return

        logger.info("WELLFOUND ACTOR: Initializing browser")
        try:
            from src.jobs.browser_manager import BrowserManager

            self._browser_manager = BrowserManager(headless=True)
            await self._browser_manager.initialize()
            self._initialized = True
            logger.info("WELLFOUND ACTOR: Browser initialized successfully")
        except ImportError as e:
            raise ActorConfigurationError(
                f"Missing Playwright dependency: {e}. Run: pip install playwright"
            ) from e
        except Exception as e:
            raise ActorConfigurationError(
                f"Browser initialization failed: {type(e).__name__}: {e}"
            ) from e

    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
        salary_min: Optional[int] = None,
        limit: int = 50,
    ) -> List[NormalizedJob]:
        """Search for jobs on Wellfound.

        NOTE: Wellfound uses DataDome CAPTCHA which blocks automated access.
        This method will detect the CAPTCHA and raise ActorCAPTCHAError.

        Args:
            query: Job search query
            location: Job location filter
            remote: Filter for remote jobs
            experience: Experience level filter
            salary_min: Minimum salary filter
            limit: Maximum number of jobs to return

        Returns:
            List of NormalizedJob objects

        Raises:
            ActorCAPTCHAError: When CAPTCHA is detected
            ActorSourceUnavailableError: When source cannot be reached
            ActorExtractionError: When extraction fails for other reasons
        """
        if not self._initialized:
            raise ActorConfigurationError(
                "Actor not initialized. Call initialize() before search_jobs()."
            )

        logger.info(f"WELLFOUND ACTOR: Searching jobs | query='{query}' location='{location}' "
                     f"remote={remote} experience={experience} limit={limit}")

        if not self._browser_manager:
            raise ActorConfigurationError("Browser manager not initialized")

        try:
            # Step 1: Build search URL
            search_url = self._build_search_url(query, location, remote, experience)
            logger.info(f"WELLFOUND ACTOR Step 1/3: Navigating to {search_url}")

            # Step 2: Navigate to Wellfound
            page = await self._browser_manager.get_page()
            try:
                await self._browser_manager.navigate(
                    page, search_url, wait_until="networkidle", timeout=30000
                )
            except Exception as e:
                logger.error(f"WELLFOUND ACTOR Step 2/3 FAILED: Navigation error: {e}")
                await self._browser_manager.close_page(page)
                raise ActorSourceUnavailableError(
                    f"Failed to navigate to Wellfound: {type(e).__name__}: {e}"
                ) from e

            logger.info("WELLFOUND ACTOR Step 2/3: Page loaded successfully")

            # Step 3: Check for CAPTCHA
            await asyncio.sleep(2)  # Allow dynamic content to load
            page_content = await page.content()
            captcha_info = self._check_for_captcha(page_content)

            if captcha_info["detected"]:
                logger.error(f"WELLFOUND ACTOR Step 3/3: CAPTCHA DETECTED - {captcha_info['provider']}")
                logger.error("WELLFOUND ACTOR: Automated access is blocked by DataDome CAPTCHA")
                logger.error("WELLFOUND ACTOR: Cannot extract jobs via browser automation")
                logger.error("WELLFOUND ACTOR: Wellfound does not provide a public API or Apify actor")
                logger.error("WELLFOUND ACTOR: Consider these alternatives:")
                logger.error("  - Use an official integration if Wellfound provides one in the future")
                logger.error("  - Use a different job source for startup/tech roles")
                logger.error("  - Visit https://wellfound.com/jobs manually")

                await self._browser_manager.close_page(page)

                self._last_status = {
                    "available": False,
                    "message": f"Blocked by {captcha_info['provider']}. "
                               f"Wellfound does not support automated access.",
                    "last_check": self._now_utc().isoformat(),
                }

                raise ActorCAPTCHAError(
                    f"WeLLFOUND ACCESS BLOCKED: {captcha_info['provider']} detected. "
                    f"Wellfound uses DataDome CAPTCHA protection which prevents automated "
                    f"browser-based job extraction. No public API or Apify actor is available. "
                    f"Workflow stopped at: page load complete → CAPTCHA check."
                )

            # Step 3b: If no CAPTCHA (unlikely), attempt extraction
            logger.info("WELLFOUND ACTOR Step 3/3: No CAPTCHA detected, attempting extraction")

            jobs = await self._extract_job_cards_from_page(page)
            logger.info(f"WELLFOUND ACTOR: Extracted {len(jobs)} jobs")

            await self._browser_manager.close_page(page)

            self._last_status = {
                "available": True,
                "message": f"Extracted {len(jobs)} jobs successfully",
                "last_check": self._now_utc().isoformat(),
            }

            return jobs[:limit]

        except ActorCAPTCHAError:
            raise
        except ActorSourceUnavailableError:
            raise
        except ActorError:
            raise
        except Exception as e:
            logger.error(f"WELLFOUND ACTOR: Unexpected error: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise ActorExtractionError(
                f"Unexpected error during Wellfound extraction: {type(e).__name__}: {e}"
            ) from e

    async def cleanup(self) -> None:
        """Clean up browser resources."""
        if self._browser_manager:
            logger.info("WELLFOUND ACTOR: Cleaning up browser")
            try:
                await self._browser_manager.close()
            except Exception as e:
                logger.warning(f"WELLFOUND ACTOR: Cleanup warning: {e}")
            self._browser_manager = None
            self._initialized = False
            logger.info("WELLFOUND ACTOR: Cleanup complete")

    def get_source_status(self) -> Dict[str, Any]:
        """Get the current status of Wellfound as a source.

        Returns:
            Dictionary with status information:
            - available: bool (always False for Wellfound due to CAPTCHA)
            - message: str explaining the limitation
            - last_check: ISO timestamp of last check
        """
        return self._last_status.copy()

    def _build_search_url(
        self,
        query: str,
        location: Optional[str] = None,
        remote: bool = False,
        experience: Optional[str] = None,
    ) -> str:
        """Build search URL for Wellfound.

        Wellfound uses URL path structure for search queries.

        Args:
            query: Job search query
            location: Location filter
            remote: Remote filter
            experience: Experience level filter

        Returns:
            Wellfound search URL with parameters
        """
        url_parts = [self.search_url]

        if query:
            query_slug = query.lower().replace(" ", "-")
            url_parts.append(query_slug)

        url = "/".join(url_parts)

        params: List[str] = []
        if location:
            params.append(f"l={location}")
        if remote:
            params.append("remote=true")
        if experience:
            exp_map = {"entry": "junior", "mid": "mid", "senior": "senior"}
            if experience in exp_map:
                params.append(f"experience={exp_map[experience]}")

        if params:
            url += "?" + "&".join(params)

        return url

    def _check_for_captcha(self, page_html: str) -> Dict[str, Any]:
        """Check page HTML for CAPTCHA indicators.

        Uses the actual CAPTCHA indicators observed from Wellfound's response.

        Args:
            page_html: Full page HTML content

        Returns:
            Dictionary with 'detected' (bool) and 'provider' (str)
        """
        html_lower = page_html.lower()

        for indicator in CAPTCHA_INDICATORS:
            if indicator in html_lower:
                if DATA_DOME_DOMAIN in html_lower:
                    return {
                        "detected": True,
                        "provider": "DataDome CAPTCHA",
                    }
                return {
                    "detected": True,
                    "provider": f"Unknown CAPTCHA (indicator: {indicator})",
                }

        # Check for Cloudflare challenge
        if "cf-browser-verification" in html_lower or "cloudflare" in html_lower:
            return {
                "detected": True,
                "provider": "Cloudflare Protection",
            }

        return {"detected": False, "provider": None}

    async def _extract_job_cards_from_page(self, page: Any) -> List[NormalizedJob]:
        """Extract job cards from a Wellfound page.

        This uses flexible selector strategies that should adapt to minor DOM changes.

        Args:
            page: Playwright Page object

        Returns:
            List of NormalizedJob objects
        """
        jobs: List[NormalizedJob] = []

        # Try multiple selectors for job card containers
        job_selectors = [
            'div[data-testid="job-item"]',
            "div.job-item",
            'div[class*="job"]',
            'article[class*="job"]',
            'a[href*="/jobs/"]',
            'a[href*="/role/"]',
        ]

        job_elements: List[Any] = []
        for selector in job_selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    job_elements = elements
                    logger.debug(f"WELLFOUND ACTOR: Found {len(elements)} elements with selector '{selector}'")
                    break
            except Exception:
                continue

        if not job_elements:
            logger.warning("WELLFOUND ACTOR: No job elements found on page")
            return jobs

        for element in job_elements:
            try:
                job = await self._extract_single_job_from_element(element)
                if job:
                    jobs.append(job)
            except Exception as e:
                logger.debug(f"WELLFOUND ACTOR: Error extracting single job: {e}")
                continue

        return jobs

    async def _extract_single_job_from_element(self, element: Any) -> Optional[NormalizedJob]:
        """Extract a single NormalizedJob from a page element.

        Args:
            element: Playwright element handle

        Returns:
            NormalizedJob or None if extraction fails
        """
        try:
            # Title extraction
            title = await self._extract_text_from_element(element, [
                "h3", "h2", "h4",
                '[class*="title"]',
                '[data-testid*="title"]',
            ])
            if not title:
                return None

            # Company extraction
            company = await self._extract_text_from_element(element, [
                '[class*="company"]',
                '[data-testid*="company"]',
                '[class*="name"]',
            ])
            company = company or "Unknown Company"

            # Location extraction
            location = await self._extract_text_from_element(element, [
                '[class*="location"]',
                '[data-testid*="location"]',
            ])

            # URL extraction
            url = await self._extract_href_from_element(element, ["a", '[href]'])
            if not url:
                return None
            if not url.startswith("http"):
                url = self.base_url + url

            # Salary extraction
            salary = await self._extract_text_from_element(element, [
                '[class*="salary"]',
                '[data-testid*="salary"]',
                '[class*="compensation"]',
            ])

            # Description extraction
            description = await self._extract_text_from_element(element, [
                '[class*="description"]',
                "p",
                '[data-testid*="description"]',
            ])
            if description:
                description = description[:1000]  # Reasonable preview

            # Remote detection
            is_remote = self._detect_remote_from_text(location, description)

            # Generate external ID
            external_id = self._make_external_id(url)

            now = self._now_utc()

            return NormalizedJob(
                title=title,
                company=company,
                location=location,
                salary=salary,
                description=description,
                url=url,
                source=self.source_name,
                external_id=external_id,
                is_remote=is_remote,
                experience_level=None,
                posted_date=now,
                normalized_at=now,
            )

        except Exception as e:
            logger.debug(f"WELLFOUND ACTOR: Element extraction error: {e}")
            return None

    async def _extract_text_from_element(
        self, element: Any, selectors: List[str]
    ) -> Optional[str]:
        """Try multiple selectors to extract text from an element.

        Args:
            element: Playwright element handle
            selectors: List of CSS selectors to try

        Returns:
            Text content or None
        """
        for selector in selectors:
            try:
                child = await element.query_selector(selector)
                if child:
                    text = await child.text_content()
                    if text and text.strip() and len(text.strip()) > 1:
                        return text.strip()
            except Exception:
                continue
        return None

    async def _extract_href_from_element(
        self, element: Any, selectors: List[str]
    ) -> Optional[str]:
        """Try multiple selectors to extract href from an element.

        Args:
            element: Playwright element handle
            selectors: List of CSS selectors to try

        Returns:
            URL string or None
        """
        for selector in selectors:
            try:
                child = await element.query_selector(selector)
                if child:
                    href = await child.get_attribute("href")
                    if href:
                        return href.strip()
            except Exception:
                continue
        return None

    @staticmethod
    def _detect_remote_from_text(
        location: Optional[str], description: Optional[str]
    ) -> bool:
        """Detect if a job is remote based on text content.

        Args:
            location: Location string
            description: Description string

        Returns:
            True if job appears remote
        """
        keywords = [
            "remote", "work from home", "wfh", "telecommute",
            "virtual", "distributed", "anywhere", "location independent",
        ]
        text = " ".join(filter(None, [location or "", description or ""])).lower()
        return any(k in text for k in keywords)