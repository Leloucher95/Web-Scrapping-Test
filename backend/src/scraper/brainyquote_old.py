from playwright.async_api import async_playwright, Browser, Page
from typing import List, Dict, Optional
import asyncio
import logging
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
        await page.wait_for_selector('.grid-item')

        # Get all quote elements - using the correct selector from debug
        quote_elements = await page.query_selector_all('.grid-item .bqQt')

        for quote_element in quote_elements:
            try:
                # Extract quote text - BrainyQuote structure analysis needed
                quote_text_elem = await quote_element.query_selector('.qti-listm')
                if not quote_text_elem:
                    # Try alternative selectors
                    quote_text_elem = await quote_element.query_selector('.b-qt')

                quote_text = ""
                author_name = ""
                quote_link = ""
                image_url = ""

                # Extract from the qti-listm structure
                if quote_text_elem:
                    # Get the quote link first (contains quote ID)
                    link_elem = await quote_text_elem.query_selector('a[title="view quote"]')
                    if link_elem:
                        relative_link = await link_elem.get_attribute('href')
                        if relative_link:
                            quote_link = f"{self.base_url}{relative_link}"

                    # Get image
                    img_elem = await quote_text_elem.query_selector('img')
                    if img_elem:
                        image_url = await img_elem.get_attribute('src')
                        if image_url and not image_url.startswith('http'):
                            image_url = f"{self.base_url}{image_url}"

                # For BrainyQuote, we need to extract from the link or make another request
                # Let's try to get text content from the page structure
                text_elements = await quote_element.query_selector_all('text(), .b-qt, .qti-listm')

                # Try to find quote text in the HTML structure
                quote_html = await quote_element.inner_html()

                # Basic text extraction (this might need refinement)
                full_text = await quote_element.inner_text()
                if full_text:
                    # Clean up the text and try to separate quote from author
                    clean_text = full_text.strip()
                    # This is a basic approach - might need refinement based on actual structure
                    if len(clean_text) > 10:  # Basic validation
                        quote_text = clean_text
                        author_name = "Unknown"  # Will need to extract properly

                # Only add quote if we have essential data
                if quote_text and len(quote_text) > 10:
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
                image_url = ""
                if img_elem:
                    image_url = await img_elem.get_attribute('src')
                    if image_url and not image_url.startswith('http'):
                        image_url = f"{self.base_url}{image_url}"

                # Only add quote if we have essential data
                if quote_text and author_name:
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