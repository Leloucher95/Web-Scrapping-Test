from playwright.async_api import async_playwright, Browser, Page, Response
from typing import List, Dict, Optional, Tuple
import asyncio
import logging
import re
import httpx
import hashlib
import os
from pathlib import Path
from core.config import settings

logger = logging.getLogger(__name__)

class EnhancedBrainyQuoteScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.base_url = "https://www.brainyquote.com"
        self.image_cache_dir = Path("cached_images")
        self.image_cache_dir.mkdir(exist_ok=True)

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=settings.PLAYWRIGHT_HEADLESS,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        await self.playwright.stop()

    async def scrape_topic(self, topic: str, max_pages: int = 1, max_quotes: int = None) -> List[Dict]:
        """
        Scrape quotes for a specific topic

        Args:
            topic: The topic to scrape (e.g., 'motivational', 'love')
            max_pages: Maximum number of pages to scrape
            max_quotes: Maximum number of quotes to return (None for all)

        Returns:
            List of quote dictionaries with enhanced data
        """
        quotes = []

        if not self.browser:
            raise RuntimeError("Browser not initialized. Use async context manager.")

        # Enhanced browser context with better anti-detection
        context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )

        page = await context.new_page()

        # Enhanced anti-detection scripts
        await page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });

            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en', 'fr'],
            });

            // Mock chrome object
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
            };

            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        try:
            topic_url = f"{self.base_url}/topics/{topic}-quotes"
            logger.info(f"🎯 Starting enhanced scraping for topic: {topic}")
            logger.info(f"📍 URL: {topic_url}")

            # Navigate with retry mechanism
            await self._navigate_with_retry(page, topic_url)

            # Wait for content to load and check for blocks
            await self._wait_and_check_blocks(page)

            # Find the best selector for quotes
            quotes_selector = await self._find_best_quotes_selector(page)

            if not quotes_selector:
                await page.screenshot(path="debug_no_selector.png")
                raise Exception("Could not find any suitable quotes selector")

            logger.info(f"✅ Using selector: {quotes_selector}")

            # Extract quotes with enhanced method
            page_quotes = await self._extract_enhanced_quotes(page, quotes_selector)
            quotes.extend(page_quotes)

            logger.info(f"📊 Successfully extracted {len(page_quotes)} quotes")

        except Exception as e:
            logger.error(f"❌ Error scraping topic {topic}: {str(e)}")
            await page.screenshot(path=f"debug_error_{topic}.png")
            raise
        finally:
            await context.close()

        # Apply max_quotes limit if specified
        if max_quotes and len(quotes) > max_quotes:
            quotes = quotes[:max_quotes]

        logger.info(f"🏁 Scraping completed. Total quotes: {len(quotes)}")
        return quotes

    async def _navigate_with_retry(self, page: Page, url: str, max_retries: int = 3):
        """Navigate to URL with retry mechanism"""
        for attempt in range(max_retries):
            try:
                logger.info(f"🌐 Navigation attempt {attempt + 1}/{max_retries}")
                await page.goto(url, wait_until='networkidle', timeout=60000)
                return
            except Exception as e:
                logger.warning(f"⚠️  Navigation attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to navigate after {max_retries} attempts")
                await asyncio.sleep(5)

    async def _wait_and_check_blocks(self, page: Page):
        """Wait for content and check if we're blocked"""
        await asyncio.sleep(3)  # Give time for JS to load

        page_content = await page.content()
        page_title = await page.title()

        # Check for various block indicators
        block_indicators = [
            "403", "forbidden", "blocked", "access denied",
            "cloudflare", "security check", "captcha",
            "please wait", "checking your browser"
        ]

        content_lower = page_content.lower()
        title_lower = page_title.lower()

        for indicator in block_indicators:
            if indicator in content_lower or indicator in title_lower:
                await page.screenshot(path=f"debug_blocked_{indicator}.png")
                raise Exception(f"Access blocked by website protection: {indicator}")

    async def _find_best_quotes_selector(self, page: Page) -> Optional[str]:
        """Find the best CSS selector for quotes"""
        selectors_to_try = [
            '.bqQt',  # Primary BrainyQuote selector
            '.grid-item',
            '.clearfix',
            '[class*="quote"]',
            '.quote-card',
            '.quoteswan',
            'article',
            '.boxy'
        ]

        best_selector = None
        max_elements = 0

        for selector in selectors_to_try:
            try:
                logger.info(f"🔍 Testing selector: {selector}")
                await page.wait_for_selector(selector, timeout=5000)
                elements = await page.query_selector_all(selector)
                element_count = len(elements)

                logger.info(f"📊 Found {element_count} elements with '{selector}'")

                if element_count > max_elements and element_count >= 3:
                    max_elements = element_count
                    best_selector = selector

            except Exception as e:
                logger.debug(f"❌ Selector '{selector}' failed: {str(e)}")
                continue

        return best_selector

    async def _extract_enhanced_quotes(self, page: Page, quotes_selector: str) -> List[Dict]:
        """Enhanced quote extraction with better text and image handling"""
        quotes = []
        quote_elements = await page.query_selector_all(quotes_selector)

        logger.info(f"🔄 Processing {len(quote_elements)} quote elements")

        for idx, quote_element in enumerate(quote_elements):
            try:
                quote_data = await self._extract_single_quote(page, quote_element, idx)
                if quote_data and self._is_valid_quote(quote_data):
                    quotes.append(quote_data)
                    logger.debug(f"✅ Extracted quote {idx + 1}: {quote_data['text'][:50]}...")
                else:
                    logger.debug(f"❌ Skipped invalid quote {idx + 1}")

            except Exception as e:
                logger.warning(f"⚠️  Error extracting quote {idx + 1}: {str(e)}")
                continue

        return quotes

    async def _extract_single_quote(self, page: Page, quote_element, idx: int) -> Optional[Dict]:
        """Extract a single quote with all its data"""
        quote_text = ""
        author_name = "Unknown"
        quote_link = ""
        image_url = ""
        image_data = None

        try:
            # Method 1: Look for quote links first
            link_elem = await quote_element.query_selector('a[title="view quote"]')
            if not link_elem:
                link_elem = await quote_element.query_selector('a[href*="/quotes/"]')

            if link_elem:
                relative_link = await link_elem.get_attribute('href')
                if relative_link:
                    quote_link = f"{self.base_url}{relative_link}" if not relative_link.startswith('http') else relative_link

                # Enhanced image extraction
                img_elem = await link_elem.query_selector('img')
                if img_elem:
                    # Try to get image URL
                    img_src = await img_elem.get_attribute('src')
                    if img_src:
                        image_url = f"{self.base_url}{img_src}" if not img_src.startswith('http') else img_src

                    # Try to extract text from alt attribute
                    alt_text = await img_elem.get_attribute('alt')
                    if alt_text and len(alt_text) > 10 and 'share this quote' not in alt_text.lower():
                        if ' - ' in alt_text:
                            parts = alt_text.rsplit(' - ', 1)
                            quote_text = parts[0].strip()
                            author_name = parts[1].strip()
                        else:
                            quote_text = alt_text.strip()

            # Method 2: Direct text extraction if alt failed
            if not quote_text or quote_text == "Share this Quote":
                # Try different text extraction methods
                text_selectors = [
                    '.qtext', '.quote-text', '[class*="text"]',
                    'p', '.quotestext', 'span'
                ]

                for text_selector in text_selectors:
                    text_elem = await quote_element.query_selector(text_selector)
                    if text_elem:
                        text_content = await text_elem.inner_text()
                        if text_content and len(text_content.strip()) > 10:
                            quote_text = text_content.strip()
                            break

                # Try to find author separately
                author_selectors = [
                    '.qauth', '.author', '[class*="author"]',
                    'cite', '.citation', 'footer'
                ]

                for author_selector in author_selectors:
                    author_elem = await quote_element.query_selector(author_selector)
                    if author_elem:
                        author_content = await author_elem.inner_text()
                        if author_content and len(author_content.strip()) > 1:
                            author_name = author_content.strip()
                            break

            # Method 3: Fallback to element text parsing
            if not quote_text or quote_text == "Share this Quote":
                element_text = await quote_element.inner_text()
                if element_text:
                    lines = [line.strip() for line in element_text.strip().split('\n') if line.strip()]
                    clean_lines = [line for line in lines if 'share this quote' not in line.lower()]

                    if len(clean_lines) >= 2:
                        quote_text = clean_lines[0]
                        author_name = clean_lines[1]
                    elif len(clean_lines) == 1:
                        quote_text = clean_lines[0]

            # Extract author from URL if still unknown
            if author_name == "Unknown" and quote_link and "/quotes/" in quote_link:
                match = re.search(r'/quotes/([^_/]+)', quote_link)
                if match:
                    author_name = match.group(1).replace('_', ' ').replace('-', ' ').title()

            # Clean up the text
            quote_text = self._clean_quote_text(quote_text)
            author_name = self._clean_author_name(author_name)

            # Download image if available
            if image_url:
                try:
                    image_data = await self._download_image(image_url, f"{author_name}_{idx}")
                except Exception as e:
                    logger.warning(f"⚠️  Could not download image {image_url}: {str(e)}")

            return {
                "text": quote_text,
                "author": author_name,
                "link": quote_link,
                "image_url": image_url,
                "image_data": image_data,  # For Supabase upload
                "extraction_method": "enhanced",
                "index": idx
            }

        except Exception as e:
            logger.error(f"❌ Error in single quote extraction: {str(e)}")
            return None

    def _clean_quote_text(self, text: str) -> str:
        """Clean and normalize quote text"""
        if not text:
            return ""

        # Remove common unwanted patterns
        text = text.strip()

        # Remove ellipsis at the end
        if text.endswith('...'):
            text = text[:-3].strip()

        # Remove surrounding quotes
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1].strip()
        elif text.startswith("'") and text.endswith("'"):
            text = text[1:-1].strip()

        # Remove "Share this Quote" and similar patterns
        unwanted_patterns = [
            "share this quote", "view quote", "more quotes",
            "click to tweet", "copy link", "download image"
        ]

        for pattern in unwanted_patterns:
            if pattern in text.lower():
                return ""

        return text

    def _clean_author_name(self, author: str) -> str:
        """Clean and normalize author name"""
        if not author or author.lower() in ['unknown', 'share this quote', '']:
            return "Unknown"

        author = author.strip()

        # Remove extra qualifiers
        unwanted_suffixes = [
            "quotes", "more quotes", "view quotes",
            "share this quote", "(click to view)"
        ]

        for suffix in unwanted_suffixes:
            if suffix in author.lower():
                author = author.lower().replace(suffix, "").strip()

        return author.title() if author else "Unknown"

    def _is_valid_quote(self, quote_data: Dict) -> bool:
        """Validate if a quote is worth keeping"""
        if not quote_data:
            return False

        text = quote_data.get('text', '')
        author = quote_data.get('author', '')

        # Check minimum text length
        if len(text) < 10:
            return False

        # Check for unwanted content
        unwanted_content = [
            'share this quote', 'view quote', 'more quotes',
            'click here', 'download', 'copy link'
        ]

        text_lower = text.lower()
        for unwanted in unwanted_content:
            if unwanted in text_lower:
                return False

        # Author should not be empty or generic
        if not author or author in ['Unknown', '', 'Share this Quote']:
            return False

        return True

    async def _download_image(self, image_url: str, identifier: str) -> Optional[Dict]:
        """Download image and return metadata for Supabase upload"""
        try:
            # Create a safe filename
            safe_identifier = re.sub(r'[^\w\-_]', '_', identifier)
            url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
            filename = f"quote_{safe_identifier}_{url_hash}.jpg"

            # Download the image
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=30)
                response.raise_for_status()

                image_content = response.content
                content_type = response.headers.get('content-type', 'image/jpeg')

                # Save locally for now (will be uploaded to Supabase later)
                local_path = self.image_cache_dir / filename
                with open(local_path, 'wb') as f:
                    f.write(image_content)

                return {
                    'filename': filename,
                    'local_path': str(local_path),
                    'content_type': content_type,
                    'size': len(image_content),
                    'original_url': image_url
                }

        except Exception as e:
            logger.error(f"❌ Failed to download image {image_url}: {str(e)}")
            return None

    async def test_scraping(self, topic: str = "motivational", max_quotes: int = 5) -> List[Dict]:
        """Test method for quick verification"""
        async with self as scraper:
            quotes = await scraper.scrape_topic(topic, max_pages=1, max_quotes=max_quotes)
            return quotes