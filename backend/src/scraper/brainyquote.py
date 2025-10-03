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

    async def scrape_topic(self, topic: str, max_pages: int = 5) -> List[Dict]:
        quotes = []
        
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use async context manager.")
            
        # Configurer le contexte pour éviter la détection
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
        
        # Masquer les signaux d'automatisation
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
            logger.info(f"Starting scraping for topic: {topic}")
            logger.info(f"URL: {topic_url}")

            # Navigation avec retry
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
            
            # Attendre un peu plus pour éviter la détection
            await asyncio.sleep(5)
            
            # Vérifier si on a été bloqué
            page_content = await page.content()
            if "403" in page_content or "forbidden" in page_content.lower() or "blocked" in page_content.lower():
                raise Exception("Access blocked by website protection")
            
            selectors_to_try = ['.bqQt', '.grid-item', '.clearfix', '[class*="quote"]']
            quotes_selector = None
            
            for selector in selectors_to_try:
                try:
                    logger.info(f"Trying selector: {selector}")
                    await page.wait_for_selector(selector, timeout=10000)
                    elements = await page.query_selector_all(selector)
                    logger.info(f"Found {len(elements)} elements with selector '{selector}'")
                    if len(elements) > 3:  # Seuil plus bas
                        quotes_selector = selector
                        break
                except Exception as e:
                    logger.warning(f"Selector '{selector}' failed: {str(e)}")
                    continue
            
            if not quotes_selector:
                await page.screenshot(path="debug_failed_page.png")
                logger.error("No quotes found - saving screenshot")
                
                # Log du contenu de la page pour debug
                content = await page.content()
                logger.error(f"Page content preview: {content[:500]}...")
                
                raise Exception("Could not find quotes on the page")
            
            logger.info(f"Using selector: {quotes_selector}")
            page_quotes = await self._extract_quotes_from_page(page, quotes_selector)
            quotes.extend(page_quotes)
            logger.info(f"Found {len(page_quotes)} quotes")
                    
        except Exception as e:
            logger.error(f"Error scraping topic {topic}: {str(e)}")
            raise
        finally:
            await context.close()
            
        logger.info(f"Scraping completed. Total quotes found: {len(quotes)}")
        return quotes

    async def _extract_quotes_from_page(self, page: Page, quotes_selector: str = '.bqQt') -> List[Dict]:
        quotes = []

        if quotes_selector == '.bqQt':
            quote_elements = await page.query_selector_all('.bqQt')
        elif quotes_selector == '.grid-item':
            quote_elements = await page.query_selector_all('.grid-item')
        elif quotes_selector == '.clearfix':
            quote_elements = await page.query_selector_all('.clearfix')
        else:
            quote_elements = await page.query_selector_all(quotes_selector)

        logger.info(f"Processing {len(quote_elements)} quote elements")

        for quote_element in quote_elements:
            try:
                quote_text = ""
                author_name = "Unknown"
                quote_link = ""
                image_url = ""
                
                # Méthode 1: chercher les liens de citations
                link_elem = await quote_element.query_selector('a[title="view quote"]')
                if not link_elem:
                    link_elem = await quote_element.query_selector('a[href*="/quotes/"]')
                
                if link_elem:
                    relative_link = await link_elem.get_attribute('href')
                    if relative_link:
                        quote_link = f"{self.base_url}{relative_link}"
                    
                    img_elem = await link_elem.query_selector('img')
                    if img_elem:
                        alt_text = await img_elem.get_attribute('alt')
                        if alt_text and len(alt_text) > 10:
                            if ' - ' in alt_text:
                                parts = alt_text.rsplit(' - ', 1)
                                quote_text = parts[0].strip()
                                author_name = parts[1].strip()
                            else:
                                quote_text = alt_text.strip()
                        
                        img_src = await img_elem.get_attribute('src')
                        if img_src:
                            image_url = f"{self.base_url}{img_src}" if not img_src.startswith('http') else img_src
                
                # Méthode 2: extraction du texte si pas d'alt
                if not quote_text:
                    element_text = await quote_element.inner_text()
                    if element_text and len(element_text.strip()) > 10:
                        lines = element_text.strip().split('\n')
                        clean_lines = [line.strip() for line in lines if line.strip()]
                        if len(clean_lines) >= 2:
                            quote_text = clean_lines[0]
                            author_name = clean_lines[1]
                        elif len(clean_lines) == 1:
                            quote_text = clean_lines[0]
                
                # Méthode 3: extraction de l'auteur depuis l'URL
                if author_name == "Unknown" and quote_link and "/quotes/" in quote_link:
                    match = re.search(r'/quotes/([^_/]+)', quote_link)
                    if match:
                        author_name = match.group(1).replace('_', ' ').replace('-', ' ').title()
                
                # Nettoyage du texte
                if quote_text:
                    quote_text = quote_text.strip()
                    # Supprimer les points de suspension
                    if quote_text.endswith('...'):
                        quote_text = quote_text[:-3].strip()
                    # Supprimer les guillemets englobants
                    if quote_text.startswith('"') and quote_text.endswith('"'):
                        quote_text = quote_text[1:-1].strip()
                    
                    # Validation finale
                    if len(quote_text) > 10 and quote_text != author_name:
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
        async with self as scraper:
            quotes = await scraper.scrape_topic(topic, max_pages=1)
            return quotes[:limit]
