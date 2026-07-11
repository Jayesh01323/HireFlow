"""
Browser Automation Manager Module

Manages browser instances for job scraping using Playwright.
Provides reusable browser sessions, tab management, and safe cleanup.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

logger = logging.getLogger(__name__)


class BrowserLaunchError(Exception):
    """Raised when browser fails to launch."""
    pass


class PageTimeoutError(Exception):
    """Raised when page load or operation times out."""
    pass


class SelectorNotFoundError(Exception):
    """Raised when a selector cannot be found on the page."""
    pass


class ExtractionError(Exception):
    """Raised when data extraction fails."""
    pass


class BrowserManager:
    """Manages browser instances for web scraping with Playwright."""
    
    def __init__(self, headless: bool = True) -> None:
        """Initialize browser manager.
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self._is_initialized = False
    
    async def initialize(self) -> None:
        """Initialize browser instance."""
        if self._is_initialized:
            logger.debug("Browser already initialized")
            return
        
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                ]
            )
            
            # Create context with realistic user agent
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
            )
            
            self._is_initialized = True
            logger.info("Browser initialized successfully")
            
        except Exception as e:
            logger.error(f"Browser launch failed: {type(e).__name__}: {e}")
            raise BrowserLaunchError(f"Failed to launch browser: {e}") from e
    
    async def get_page(self) -> Page:
        """Get a new page from the browser context.
        
        Returns:
            Page object for navigation and interaction
            
        Raises:
            BrowserLaunchError: If browser is not initialized
        """
        if not self._is_initialized or not self.context:
            raise BrowserLaunchError("Browser not initialized. Call initialize() first.")
        
        try:
            page = await self.context.new_page()
            logger.debug("Created new page")
            return page
        except Exception as e:
            logger.error(f"Failed to create new page: {e}")
            raise BrowserLaunchError(f"Failed to create new page: {e}") from e
    
    async def close_page(self, page: Page) -> None:
        """Close a page safely.
        
        Args:
            page: Page object to close
        """
        try:
            if page and not page.is_closed():
                await page.close()
                logger.debug("Page closed successfully")
        except Exception as e:
            logger.warning(f"Error closing page: {e}")
    
    async def navigate(
        self,
        page: Page,
        url: str,
        wait_until: str = "networkidle",
        timeout: int = 30000,
    ) -> None:
        """Navigate to a URL and wait for load.
        
        Args:
            page: Page object to navigate
            url: URL to navigate to
            wait_until: When to consider navigation complete ('load', 'networkidle', etc.)
            timeout: Maximum time to wait in milliseconds
            
        Raises:
            PageTimeoutError: If navigation times out
        """
        try:
            await page.goto(url, wait_until=wait_until, timeout=timeout)
            logger.debug(f"Navigated to {url}")
        except Exception as e:
            logger.error(f"Navigation to {url} failed: {type(e).__name__}: {e}")
            raise PageTimeoutError(f"Navigation to {url} timed out: {e}") from e
    
    async def wait_for_selector(
        self,
        page: Page,
        selector: str,
        timeout: int = 10000,
    ) -> None:
        """Wait for a selector to appear on the page.
        
        Args:
            page: Page object to wait on
            selector: CSS selector to wait for
            timeout: Maximum time to wait in milliseconds
            
        Raises:
            SelectorNotFoundError: If selector is not found within timeout
        """
        try:
            await page.wait_for_selector(selector, timeout=timeout)
            logger.debug(f"Selector {selector} found")
        except Exception as e:
            logger.error(f"Selector {selector} not found: {type(e).__name__}: {e}")
            raise SelectorNotFoundError(f"Selector '{selector}' not found within {timeout}ms: {e}") from e
    
    async def extract_text(
        self,
        page: Page,
        selector: str,
        timeout: int = 5000,
    ) -> Optional[str]:
        """Extract text content from a selector.
        
        Args:
            page: Page object to extract from
            selector: CSS selector to extract text from
            timeout: Maximum time to wait for selector
            
        Returns:
            Text content or None if not found
            
        Raises:
            ExtractionError: If extraction fails
        """
        try:
            await self.wait_for_selector(page, selector, timeout=timeout)
            element = await page.query_selector(selector)
            if element:
                text = await element.text_content()
                return text.strip() if text else None
            return None
        except SelectorNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Failed to extract text from {selector}: {e}")
            raise ExtractionError(f"Failed to extract text from '{selector}': {e}") from e
    
    async def extract_attribute(
        self,
        page: Page,
        selector: str,
        attribute: str,
        timeout: int = 5000,
    ) -> Optional[str]:
        """Extract an attribute value from a selector.
        
        Args:
            page: Page object to extract from
            selector: CSS selector to extract attribute from
            attribute: Attribute name to extract
            timeout: Maximum time to wait for selector
            
        Returns:
            Attribute value or None if not found
            
        Raises:
            ExtractionError: If extraction fails
        """
        try:
            await self.wait_for_selector(page, selector, timeout=timeout)
            element = await page.query_selector(selector)
            if element:
                value = await element.get_attribute(attribute)
                return value
            return None
        except SelectorNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Failed to extract attribute {attribute} from {selector}: {e}")
            raise ExtractionError(f"Failed to extract attribute from '{selector}': {e}") from e
    
    async def extract_multiple(
        self,
        page: Page,
        selector: str,
        timeout: int = 5000,
    ) -> list[str]:
        """Extract text from multiple matching selectors.
        
        Args:
            page: Page object to extract from
            selector: CSS selector to extract from
            timeout: Maximum time to wait for selector
            
        Returns:
            List of text content from matching elements
            
        Raises:
            ExtractionError: If extraction fails
        """
        try:
            await self.wait_for_selector(page, selector, timeout=timeout)
            elements = await page.query_selector_all(selector)
            texts = []
            for element in elements:
                text = await element.text_content()
                if text:
                    texts.append(text.strip())
            return texts
        except SelectorNotFoundError:
            return []
        except Exception as e:
            logger.error(f"Failed to extract multiple from {selector}: {e}")
            raise ExtractionError(f"Failed to extract multiple from '{selector}': {e}") from e
    
    async def close(self) -> None:
        """Close browser and cleanup resources."""
        try:
            if self.context:
                await self.context.close()
                logger.debug("Browser context closed")
            if self.browser:
                await self.browser.close()
                logger.debug("Browser closed")
            if self.playwright:
                await self.playwright.stop()
                logger.debug("Playwright stopped")
            self._is_initialized = False
            logger.info("Browser manager cleanup complete")
        except Exception as e:
            logger.warning(f"Error during browser cleanup: {e}")
    
    def __del__(self) -> None:
        """Cleanup on deletion."""
        if self._is_initialized:
            logger.warning("BrowserManager deleted without explicit close(). Resources may leak.")
