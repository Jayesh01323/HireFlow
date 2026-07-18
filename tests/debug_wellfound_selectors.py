"""
Debug Wellfound Selectors

Investigate the actual DOM structure of Wellfound to find correct selectors.
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


async def debug_wellfound():
    """Debug Wellfound page structure."""
    from src.jobs.browser_manager import BrowserManager
    
    # Try the main jobs page first
    search_url = "https://wellfound.com/jobs"
    logger.info(f"Navigating to: {search_url}")
    
    browser_manager = None
    
    try:
        browser_manager = BrowserManager(headless=False)  # Run visible to see
        await browser_manager.initialize()
        
        page = await browser_manager.get_page()
        await browser_manager.navigate(page, search_url, wait_until="networkidle", timeout=30000)
        
        # Wait for content to load
        await asyncio.sleep(5)
        
        # Get page HTML
        html = await page.content()
        
        # Save HTML for inspection
        html_file = Path(__file__).parent / "wellfound_page.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"Page HTML saved to: {html_file}")
        
        # Try to find any job-related elements
        logger.info("\nSearching for job-related elements...")
        
        # Common patterns
        selectors_to_try = [
            'div[class*="job"]',
            'div[class*="listing"]',
            'div[class*="card"]',
            'article',
            'div[class*="item"]',
            'li[class*="job"]',
            'a[href*="/job"]',
            'a[href*="/role"]',
        ]
        
        for selector in selectors_to_try:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    logger.info(f"Found {len(elements)} elements with selector: {selector}")
                    
                    # Get first element's HTML
                    if elements:
                        first_html = await elements[0].inner_html()
                        logger.info(f"First element HTML (first 500 chars):\n{first_html[:500]}")
                        break
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
        
        # Get all text content
        body_text = await page.inner_text('body')
        logger.info(f"\nPage text length: {len(body_text)} characters")
        logger.info(f"First 1000 characters of page text:\n{body_text[:1000]}")
        
        # Look for specific keywords
        keywords = ['backend', 'developer', 'pune', 'company', 'salary', 'remote']
        logger.info("\nSearching for keywords in page:")
        for keyword in keywords:
            count = body_text.lower().count(keyword)
            if count > 0:
                logger.info(f"  '{keyword}': found {count} times")
        
        # Wait a bit for visual inspection
        await asyncio.sleep(3)
        
    except Exception as e:
        logger.error(f"Error: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        if browser_manager:
            await browser_manager.close()


if __name__ == "__main__":
    asyncio.run(debug_wellfound())
