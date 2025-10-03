from playwright.async_api import async_playwright, Browser, Page
from playwright_stealth import Stealth
from typing import List, Dict, Optional
import asyncio
import logging
import re
import random
from fake_useragent import UserAgent
from src.core.config import settings

logger = logging.getLogger(__name__)

class StealthBrainyQuoteScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.base_url = "https://www.brainyquote.com"
        self.ua = UserAgent()

        # Pool de User-Agents réalistes
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]

        # Pool de résolutions d'écran réalistes
        self.viewports = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1536, 'height': 864},
            {'width': 1440, 'height': 900},
            {'width': 1280, 'height': 720}
        ]

    async def __aenter__(self):
        self.playwright = await async_playwright().start()

        # Configuration browser ultra-réaliste
        self.browser = await self.playwright.chromium.launch(
            headless=True,  # Changeable à False pour debug
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor',
                '--disable-web-security',
                '--disable-dev-shm-usage',
                '--no-first-run',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-javascript-harmony-shipping',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-field-trial-config',
                '--disable-ipc-flooding-protection'
            ]
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        await self.playwright.stop()

    async def create_stealth_context(self):
        """Crée un contexte de navigation ultra-furtif"""
        user_agent = random.choice(self.user_agents)
        viewport = random.choice(self.viewports)

        context = await self.browser.new_context(
            user_agent=user_agent,
            viewport=viewport,
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},  # New York
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'max-age=0',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'DNT': '1',
                'Connection': 'keep-alive'
            }
        )

        page = await context.new_page()

        # Appliquer stealth (utiliser la méthode async)
        stealth = Stealth()
        await stealth.apply_stealth_async(page)

        # Scripts anti-détection avancés
        await page.add_init_script("""
            // Masquer l'automation
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            // Simuler plugins réalistes
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {name: 'Chrome PDF Plugin', description: 'Portable Document Format'},
                    {name: 'Chrome PDF Viewer', description: 'PDF Viewer'},
                    {name: 'Native Client', description: 'Native Client'}
                ],
            });

            // Langues réalistes
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });

            // Chrome object
            window.chrome = {
                runtime: {},
                app: {
                    isInstalled: false,
                },
                csi: function() {},
                loadTimes: function() {
                    return {
                        requestTime: performance.now() / 1000,
                        startLoadTime: performance.now() / 1000,
                        commitLoadTime: performance.now() / 1000,
                        finishDocumentLoadTime: performance.now() / 1000,
                        finishLoadTime: performance.now() / 1000,
                    };
                },
            };

            // Simuler WebGL
            const getParameter = WebGLRenderingContext.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel(R) Iris(TM) Graphics 6100';
                }
                return getParameter(parameter);
            };

            // Simuler la mémoire
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8,
            });

            // Simuler hardware concurrency
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 4,
            });
        """)

        return context, page

    async def human_like_navigation(self, page, url):
        """Navigation avec comportement humain"""
        # Délai aléatoire avant navigation
        await asyncio.sleep(random.uniform(2, 5))

        try:
            # Navigation en plusieurs étapes pour simuler un humain
            logger.info("Simulating human navigation via Google...")
            await page.goto('https://www.google.com', wait_until='networkidle')
            await asyncio.sleep(random.uniform(1, 3))

            # Simuler recherche sur Google
            try:
                search_box = await page.query_selector('input[name="q"]')
                if search_box:
                    await search_box.type('brainyquote motivational quotes', delay=random.randint(50, 150))
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    await page.keyboard.press('Enter')
                    await page.wait_for_load_state('networkidle', timeout=30000)
                    await asyncio.sleep(random.uniform(2, 4))
            except Exception as e:
                logger.warning(f"Google search simulation failed: {e}")

            # Navigation vers BrainyQuote
            logger.info(f"Navigating to target URL: {url}")
            await page.goto(url, wait_until='networkidle', timeout=60000)

        except Exception as e:
            logger.warning(f"Google navigation failed, trying direct access: {e}")
            await page.goto(url, wait_until='networkidle', timeout=60000)

    async def simulate_human_behavior(self, page):
        """Simuler un comportement humain sur la page"""
        logger.info("Simulating human behavior...")

        # Scroll aléatoire
        for _ in range(random.randint(2, 5)):
            await page.mouse.wheel(0, random.randint(200, 800))
            await asyncio.sleep(random.uniform(0.5, 2))

        # Mouvement de souris aléatoire
        viewport = page.viewport_size
        for _ in range(random.randint(3, 8)):
            x = random.randint(0, viewport['width'])
            y = random.randint(0, viewport['height'])
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.5))

    async def scrape_topic_stealth(self, topic: str, max_pages: int = 1):
        """Scraping furtif avec toutes les protections"""
        quotes = []

        if not self.browser:
            raise RuntimeError("Browser not initialized. Use async context manager.")

        context, page = await self.create_stealth_context()

        try:
            topic_url = f"{self.base_url}/topics/{topic}-quotes"
            logger.info(f"🥷 STEALTH scraping for topic: {topic}")
            logger.info(f"URL: {topic_url}")

            # Navigation humaine
            await self.human_like_navigation(page, topic_url)

            # Attendre le chargement complet
            await asyncio.sleep(random.uniform(3, 7))

            # Vérifier si bloqué
            page_content = await page.content()
            blocked_indicators = [
                "403", "forbidden", "blocked", "access denied",
                "cloudflare", "just a moment", "please wait",
                "checking your browser", "challenge"
            ]

            if any(indicator in page_content.lower() for indicator in blocked_indicators):
                await page.screenshot(path="blocked_page_stealth.png")
                raise Exception("Access blocked by website protection - stealth mode failed")

            # Simuler comportement humain
            await self.simulate_human_behavior(page)

            # Chercher les citations avec retry
            selectors_to_try = ['.bqQt', '.grid-item', '.clearfix', '[class*="quote"]']
            quotes_found = False

            for selector in selectors_to_try:
                try:
                    logger.info(f"Trying selector: {selector}")
                    await page.wait_for_selector(selector, timeout=15000)
                    elements = await page.query_selector_all(selector)

                    if len(elements) > 2:
                        logger.info(f"✅ Found {len(elements)} elements with selector '{selector}'")
                        page_quotes = await self._extract_quotes_stealth(page, selector)
                        quotes.extend(page_quotes)
                        quotes_found = True
                        break

                except Exception as e:
                    logger.warning(f"Selector '{selector}' failed: {str(e)}")
                    continue

            if not quotes_found:
                await page.screenshot(path="no_quotes_found_stealth.png")
                logger.error("No quotes found - screenshot saved")
                raise Exception("Could not find quotes on the page")

        except Exception as e:
            logger.error(f"🚨 Stealth scraping failed for {topic}: {str(e)}")
            raise
        finally:
            await context.close()

        logger.info(f"🎉 Stealth scraping completed! Total quotes: {len(quotes)}")
        return quotes

    async def _extract_quotes_stealth(self, page, selector):
        """Extraction avec simulation de comportement humain"""
        quotes = []

        elements = await page.query_selector_all(selector)
        logger.info(f"Processing {len(elements)} quote elements with stealth mode")

        for i, element in enumerate(elements):
            try:
                # Simuler lecture humaine
                if i % 3 == 0:  # Tous les 3 éléments
                    await page.mouse.wheel(0, random.randint(100, 300))
                    await asyncio.sleep(random.uniform(0.5, 1.5))

                quote_text = ""
                author_name = "Unknown"
                quote_link = ""
                image_url = ""

                # Chercher les liens de citations
                link_elem = await element.query_selector('a[title="view quote"]')
                if not link_elem:
                    link_elem = await element.query_selector('a[href*="/quotes/"]')

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

                # Extraction alternative du texte si pas d'alt
                if not quote_text:
                    element_text = await element.inner_text()
                    if element_text and len(element_text.strip()) > 10:
                        lines = element_text.strip().split('\n')
                        clean_lines = [line.strip() for line in lines if line.strip()]
                        if len(clean_lines) >= 2:
                            quote_text = clean_lines[0]
                            author_name = clean_lines[1]
                        elif len(clean_lines) == 1:
                            quote_text = clean_lines[0]

                # Extraction de l'auteur depuis l'URL
                if author_name == "Unknown" and quote_link and "/quotes/" in quote_link:
                    match = re.search(r'/quotes/([^_/]+)', quote_link)
                    if match:
                        author_name = match.group(1).replace('_', ' ').replace('-', ' ').title()

                # Nettoyage du texte
                if quote_text:
                    quote_text = quote_text.strip()
                    if quote_text.endswith('...'):
                        quote_text = quote_text[:-3].strip()
                    if quote_text.startswith('"') and quote_text.endswith('"'):
                        quote_text = quote_text[1:-1].strip()

                    # Validation finale
                    if len(quote_text) > 10 and quote_text != author_name and "share this quote" not in quote_text.lower():
                        quote_data = {
                            "text": quote_text,
                            "author": author_name,
                            "link": quote_link,
                            "image_url": image_url,
                        }
                        quotes.append(quote_data)

                # Petit délai entre chaque extraction
                await asyncio.sleep(random.uniform(0.1, 0.3))

            except Exception as e:
                logger.warning(f"Error extracting quote {i}: {str(e)}")
                continue

        return quotes

    async def test_scraping_stealth(self, topic: str = "motivational", limit: int = 5) -> List[Dict]:
        """Test method pour stealth scraping"""
        async with self as scraper:
            quotes = await scraper.scrape_topic_stealth(topic, max_pages=1)
            return quotes[:limit]