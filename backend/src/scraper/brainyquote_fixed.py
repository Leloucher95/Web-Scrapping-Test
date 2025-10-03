from playwright.async_api import async_playwright, Browser, Page
from typing import List, Dict, Optional
import asyncio
import logging
import re
from src.core.config import settings

logger = logging.getLogger(__name__)

class BrainyQuoteScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.base_url = "https://www.brainyquote.com"

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=settings.PLAYWRIGHT_HEADLESS
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        await self.playwright.stop()

    async def scrape_topic(self, topic: str, max_pages: int = 5) -> List[Dict]:
        """
        Scrape quotes for a given topic from BrainyQuote

        Args:
            topic: The topic to scrape (e.g., 'motivational', 'love')
            max_pages: Maximum number of pages to scrape

        Returns:
            List of quote dictionaries with keys: author, text, link, image_url
        """
        quotes = []

        if not self.browser:
            raise RuntimeError("Browser not initialized. Use async context manager.")

        page = await self.browser.new_page()

        try:
            # Navigate to topic page
            topic_url = f"{self.base_url}/topics/{topic}-quotes"
            logger.info(f"Starting scraping for topic: {topic}")
            logger.info(f"URL: {topic_url}")

            await page.goto(topic_url, timeout=settings.PLAYWRIGHT_TIMEOUT)

            # Wait for quotes to load - using correct selector
            await page.wait_for_selector('.bqQt', timeout=10000)

            page_num = 1
            while page_num <= max_pages:
                logger.info(f"Scraping page {page_num}/{max_pages}")

                # Extract quotes from current page
                page_quotes = await self._extract_quotes_from_page(page)
                quotes.extend(page_quotes)

                logger.info(f"Found {len(page_quotes)} quotes on page {page_num}")

                # Try to go to next page
                if page_num < max_pages:
                    next_button = await page.query_selector('a[aria-label="Next page"]')
                    if next_button:
                        await next_button.click()
                        await page.wait_for_load_state('networkidle')
                        await asyncio.sleep(settings.REQUEST_DELAY / 1000)  # Rate limiting
                        page_num += 1
                    else:
                        logger.info("No more pages available")
                        break
                else:
                    break

        except Exception as e:
            logger.error(f"Error scraping topic {topic}: {str(e)}")
            raise
        finally:
            await page.close()

        logger.info(f"Scraping completed. Total quotes found: {len(quotes)}")
        return quotes

    async def _extract_quotes_from_page(self, page: Page) -> List[Dict]:
        """Extract quotes from the current page"""
        quotes = []

        # Wait for quotes container
        await page.wait_for_selector('.bqQt')

        # Get all quote elements - using the correct selector
        quote_elements = await page.query_selector_all('.bqQt')

        for quote_element in quote_elements:
            try:
                # Extract from the BrainyQuote structure based on analysis
                quote_text = ""
                author_name = "Unknown"
                quote_link = ""
                image_url = ""

                # Get the link element that contains quote info
                link_elem = await quote_element.query_selector('a[title="view quote"]')
                if link_elem:
                    # Extract quote link
                    relative_link = await link_elem.get_attribute('href')
                    if relative_link:
                        quote_link = f"{self.base_url}{relative_link}"

                    # Extract image
                    img_elem = await link_elem.query_selector('img')
                    if img_elem:
                        # Get quote text from alt attribute (BrainyQuote puts it there)
                        alt_text = await img_elem.get_attribute('alt')
                        if alt_text and len(alt_text) > 10:
                            quote_text = alt_text

                        # Get image URL
                        img_src = await img_elem.get_attribute('src')
                        if img_src:
                            image_url = f"{self.base_url}{img_src}" if not img_src.startswith('http') else img_src

                # If we couldn't get text from alt, try from element text
                if not quote_text:
                    element_text = await quote_element.inner_text()
                    if element_text and len(element_text.strip()) > 10:
                        quote_text = element_text.strip()

                # Try to extract author from the quote link or text
                if quote_link and "/quotes/" in quote_link:
                    # Extract author from URL pattern: /quotes/author_name_number
                    match = re.search(r'/quotes/([^_]+)_', quote_link)
                    if match:
                        author_name = match.group(1).replace('_', ' ').title()

                # Clean up quote text
                if quote_text:
                    # Remove common prefixes/suffixes and clean
                    quote_text = quote_text.strip()
                    if quote_text.endswith('...'):
                        quote_text = quote_text[:-3].strip()

                    # Only add quote if we have essential data
                    if len(quote_text) > 10:
                        quote_data = {
                            "text": quote_text,
                            "author": author_name,
                            "link": quote_link,
                            "image_url": image_url,
                        }
                        quotes.append(quote_data)

            except Exception as e:
                logger.warning(f"Error extracting quote: {str(e)}")
                continue

        return quotes

    async def test_scraping(self, topic: str = "motivational", limit: int = 5) -> List[Dict]:
        """Test method to scrape a small number of quotes"""
        async with self as scraper:
            quotes = await scraper.scrape_topic(topic, max_pages=1)
            return quotes[:limit]