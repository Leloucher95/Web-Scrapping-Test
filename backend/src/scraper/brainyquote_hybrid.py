from playwright.async_api import async_playwright, Browser, Page
from typing import List, Dict, Optional
import asyncio
import logging
import re
import httpx
import hashlib
from pathlib import Path
from core.config import settings

logger = logging.getLogger(__name__)

class HybridBrainyQuoteScraper:
    """
    Scraper hybride qui combine la simplicité du scraper de base
    avec l'extraction améliorée de texte et images
    """
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
        Scrape quotes for a specific topic with enhanced extraction
        """
        quotes = []

        if not self.browser:
            raise RuntimeError("Browser not initialized. Use async context manager.")

        # Configuration simple et discrète (comme le scraper qui fonctionnait)
        context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1366, 'height': 768},
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )

        page = await context.new_page()

        # Scripts anti-détection basiques (comme l'original)
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });

            window.chrome = {
                runtime: {},
            };
        """)

        try:
            topic_url = f"{self.base_url}/topics/{topic}-quotes"
            logger.info(f"🎯 Starting hybrid scraping for topic: {topic}")
            logger.info(f"📍 URL: {topic_url}")

            # Navigation simple (comme l'original)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await page.goto(topic_url, wait_until='networkidle', timeout=60000)
                    break
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(5)

            # Pause standard
            await asyncio.sleep(5)

            # Vérifier les blocages
            page_content = await page.content()
            if "403" in page_content or "forbidden" in page_content.lower() or "blocked" in page_content.lower():
                raise Exception("Access blocked by website protection")

            # Trouver les sélecteurs (comme l'original)
            selectors_to_try = ['.bqQt', '.grid-item', '.clearfix', '[class*="quote"]']
            quotes_selector = None

            for selector in selectors_to_try:
                try:
                    logger.info(f"🔍 Trying selector: {selector}")
                    await page.wait_for_selector(selector, timeout=10000)
                    elements = await page.query_selector_all(selector)
                    logger.info(f"📊 Found {len(elements)} elements with selector '{selector}'")
                    if len(elements) > 3:
                        quotes_selector = selector
                        break
                except Exception as e:
                    logger.warning(f"Selector '{selector}' failed: {str(e)}")
                    continue

            if not quotes_selector:
                await page.screenshot(path="debug_hybrid_failed.png")
                logger.error("No quotes found - saving screenshot")
                raise Exception("Could not find quotes on the page")

            logger.info(f"✅ Using selector: {quotes_selector}")

            # Extraction améliorée (nouvelle partie)
            page_quotes = await self._extract_quotes_enhanced(page, quotes_selector)
            quotes.extend(page_quotes)
            logger.info(f"📊 Found {len(page_quotes)} quotes")

        except Exception as e:
            logger.error(f"❌ Error scraping topic {topic}: {str(e)}")
            await page.screenshot(path=f"debug_hybrid_error_{topic}.png")
            raise
        finally:
            await context.close()

        # Limiter si nécessaire
        if max_quotes and len(quotes) > max_quotes:
            quotes = quotes[:max_quotes]

        logger.info(f"🏁 Hybrid scraping completed. Total quotes: {len(quotes)}")
        return quotes

    async def _extract_quotes_enhanced(self, page: Page, quotes_selector: str = '.bqQt') -> List[Dict]:
        """Extraction améliorée mais basée sur le code qui fonctionne"""
        quotes = []
        quote_elements = await page.query_selector_all(quotes_selector)

        logger.info(f"🔄 Processing {len(quote_elements)} quote elements with enhanced extraction")

        for idx, quote_element in enumerate(quote_elements):
            try:
                quote_text = ""
                author_name = "Unknown"
                quote_link = ""
                image_url = ""
                image_data = None

                # Étape 1: Chercher les liens de citations (comme l'original)
                link_elem = await quote_element.query_selector('a[title="view quote"]')
                if not link_elem:
                    link_elem = await quote_element.query_selector('a[href*="/quotes/"]')

                if link_elem:
                    relative_link = await link_elem.get_attribute('href')
                    if relative_link:
                        quote_link = f"{self.base_url}{relative_link}"

                    # Extraction d'image (nouveau)
                    img_elem = await link_elem.query_selector('img')
                    if img_elem:
                        img_src = await img_elem.get_attribute('src')
                        if img_src:
                            image_url = f"{self.base_url}{img_src}" if not img_src.startswith('http') else img_src

                        # Extraction améliorée du texte depuis l'alt
                        alt_text = await img_elem.get_attribute('alt')
                        if alt_text and len(alt_text) > 10:
                            if ' - ' in alt_text:
                                parts = alt_text.rsplit(' - ', 1)
                                quote_text = parts[0].strip()
                                author_name = parts[1].strip()
                            else:
                                quote_text = alt_text.strip()

                # Étape 2: Méthodes alternatives d'extraction (améliorées)
                if not quote_text or "share this quote" in quote_text.lower():
                    # Essayer d'autres sélecteurs de texte
                    text_selectors = ['.qtext', 'p', 'span']
                    for text_selector in text_selectors:
                        text_elem = await quote_element.query_selector(text_selector)
                        if text_elem:
                            text_content = await text_elem.inner_text()
                            if text_content and len(text_content.strip()) > 10:
                                lines = text_content.strip().split('\n')
                                clean_lines = [line.strip() for line in lines if line.strip()]
                                if clean_lines and "share this quote" not in clean_lines[0].lower():
                                    quote_text = clean_lines[0]
                                    if len(clean_lines) > 1:
                                        author_name = clean_lines[1]
                                    break

                # Étape 3: Extraction de l'auteur depuis l'URL (comme l'original)
                if author_name == "Unknown" and quote_link and "/quotes/" in quote_link:
                    match = re.search(r'/quotes/([^_/]+)', quote_link)
                    if match:
                        author_name = match.group(1).replace('_', ' ').replace('-', ' ').title()

                # Étape 4: Nettoyage (amélioré)
                quote_text = self._clean_quote_text(quote_text)
                author_name = self._clean_author_name(author_name)

                # Étape 5: Téléchargement d'image (nouveau)
                if image_url and self._is_valid_quote_data(quote_text, author_name):
                    try:
                        image_data = await self._download_image_simple(image_url, f"{author_name}_{idx}")
                    except Exception as e:
                        logger.debug(f"Could not download image: {str(e)}")

                # Validation et ajout
                if self._is_valid_quote_data(quote_text, author_name):
                    quote_data = {
                        "text": quote_text,
                        "author": author_name,
                        "link": quote_link,
                        "image_url": image_url,
                        "image_data": image_data,
                        "index": idx
                    }
                    quotes.append(quote_data)
                    logger.debug(f"✅ Quote {idx + 1}: {quote_text[:50]}...")
                else:
                    logger.debug(f"❌ Skipped invalid quote {idx + 1}")

            except Exception as e:
                logger.warning(f"⚠️  Error extracting quote {idx + 1}: {str(e)}")
                continue

        return quotes

    def _clean_quote_text(self, text: str) -> str:
        """Nettoyage du texte de citation"""
        if not text:
            return ""

        text = text.strip()

        # Supprimer les patterns indésirables
        if "share this quote" in text.lower():
            return ""

        # Supprimer les points de suspension
        if text.endswith('...'):
            text = text[:-3].strip()

        # Supprimer les guillemets englobants
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1].strip()

        return text

    def _clean_author_name(self, author: str) -> str:
        """Nettoyage du nom d'auteur"""
        if not author or author.lower() in ['unknown', 'share this quote', '']:
            return "Unknown"

        author = author.strip()

        # Supprimer les suffixes indésirables
        if "share this quote" in author.lower():
            return "Unknown"

        return author.title() if author else "Unknown"

    def _is_valid_quote_data(self, text: str, author: str) -> bool:
        """Validation des données de citation"""
        if not text or len(text) < 10:
            return False

        if "share this quote" in text.lower():
            return False

        if not author or author in ['Unknown', '', 'Share this Quote']:
            return False

        return True

    async def _download_image_simple(self, image_url: str, identifier: str) -> Optional[Dict]:
        """Téléchargement simple d'image"""
        try:
            safe_identifier = re.sub(r'[^\w\-_]', '_', identifier)
            url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
            filename = f"quote_{safe_identifier}_{url_hash}.jpg"

            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=30)
                response.raise_for_status()

                image_content = response.content
                content_type = response.headers.get('content-type', 'image/jpeg')

                # Sauvegarder localement
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
            logger.error(f"Failed to download image {image_url}: {str(e)}")
            return None

    async def test_scraping(self, topic: str = "motivational", max_quotes: int = 5) -> List[Dict]:
        """Test method for quick verification"""
        async with self as scraper:
            quotes = await scraper.scrape_topic(topic, max_pages=1, max_quotes=max_quotes)
            return quotes