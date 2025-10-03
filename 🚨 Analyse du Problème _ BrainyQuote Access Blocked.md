<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# 🚨 Analyse du Problème : BrainyQuote Access Blocked

Basé sur ton dépôt GitHub et les logs d'erreur, le problème est clair : **BrainyQuote utilise une protection anti-bot avancée** (probablement Cloudflare ou similaire) qui détecte et bloque ton scraper.[^1][^2][^3]

## 🔍 Diagnostic du Code Actuel

En analysant ton [`brainyquote.py`](https://github.com/Leloucher95/Web-Scrapping-Test/blob/main/backend/src/scraper/brainyquote.py), je vois que tu as déjà implémenté plusieurs techniques anti-détection, mais elles ne suffisent plus.[^2][^1]

### Problèmes Identifiés

1. **User-Agent trop générique** : `Mozilla/5.0 (X11; Linux x86_64)` est facilement détectable
2. **Headers incomplets** : Manque de headers essentiels pour la crédibilité
3. **Timing prévisible** : Délais fixes et comportement non-humain
4. **TLS Fingerprinting** : Playwright laisse des empreintes détectables[^1]
5. **JavaScript challenges** : BrainyQuote utilise probablement des défis JS[^4][^2]

## 🛠️ Solutions Recommandées

### Solution 1 : Playwright Stealth + Proxies[^3][^5]

```python
# backend/src/scraper/brainyquote_stealth.py
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import asyncio
import random
import logging

logger = logging.getLogger(__name__)

class StealthBrainyQuoteScraper:
    def __init__(self):
        self.browser = None
        self.base_url = "https://www.brainyquote.com"
        
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
                '--disable-images',  # Performance boost
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
        
        # Appliquer stealth
        await stealth_async(page)
        
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
            await page.goto('https://www.google.com', wait_until='networkidle')
            await asyncio.sleep(random.uniform(1, 3))
            
            # Simuler recherche sur Google (optionnel)
            search_box = await page.query_selector('input[name="q"]')
            if search_box:
                await search_box.type('brainyquote motivational quotes', delay=random.randint(50, 150))
                await asyncio.sleep(random.uniform(0.5, 1.5))
                await page.keyboard.press('Enter')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(random.uniform(2, 4))
            
            # Navigation vers BrainyQuote
            await page.goto(url, wait_until='networkidle', timeout=60000)
            
        except Exception as e:
            logger.warning(f"Google navigation failed, direct access: {e}")
            await page.goto(url, wait_until='networkidle', timeout=60000)

    async def simulate_human_behavior(self, page):
        """Simuler un comportement humain sur la page"""
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
            logger.info(f"Stealth scraping for topic: {topic}")
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
                await page.screenshot(path="blocked_page.png")
                raise Exception("Access blocked by website protection - screenshot saved")
            
            # Simuler comportement humain
            await self.simulate_human_behavior(page)
            
            # Chercher les citations avec retry
            selectors_to_try = ['.bqQt', '.grid-item', '.clearfix', '[class*="quote"]']
            quotes_found = False
            
            for selector in selectors_to_try:
                try:
                    await page.wait_for_selector(selector, timeout=15000)
                    elements = await page.query_selector_all(selector)
                    
                    if len(elements) > 2:
                        logger.info(f"Found {len(elements)} elements with selector '{selector}'")
                        page_quotes = await self._extract_quotes_stealth(page, selector)
                        quotes.extend(page_quotes)
                        quotes_found = True
                        break
                        
                except Exception as e:
                    logger.warning(f"Selector '{selector}' failed: {str(e)}")
                    continue
            
            if not quotes_found:
                await page.screenshot(path="no_quotes_found.png")
                logger.error("No quotes found - screenshot saved")
                raise Exception("Could not find quotes on the page")
                
        except Exception as e:
            logger.error(f"Stealth scraping failed for {topic}: {str(e)}")
            raise
        finally:
            await context.close()
        
        logger.info(f"Stealth scraping completed. Total quotes: {len(quotes)}")
        return quotes

    async def _extract_quotes_stealth(self, page, selector):
        """Extraction avec simulation de comportement humain"""
        quotes = []
        
        elements = await page.query_selector_all(selector)
        logger.info(f"Processing {len(elements)} quote elements with stealth")
        
        for i, element in enumerate(elements):
            try:
                # Simuler lecture humaine
                if i % 3 == 0:  # Tous les 3 éléments
                    await page.mouse.wheel(0, random.randint(100, 300))
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                
                # Extraction similaire au code original mais avec délais
                quote_text = ""
                author_name = "Unknown"
                quote_link = ""
                image_url = ""
                
                # Logique d'extraction (simplifiée pour l'exemple)
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
                                quote_text = parts[^0].strip()
                                author_name = parts[^1].strip()
                            else:
                                quote_text = alt_text.strip()
                
                if quote_text and len(quote_text) > 10:
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
```


### Solution 2 : Installation Playwright Stealth

```bash
# Dans backend/
pip install playwright-stealth
pip install fake-useragent
```

```python
# requirements.txt - Ajouter ces lignes
playwright-stealth==1.0.6
fake-useragent==1.4.0
```


### Solution 3 : Alternative avec Proxies Rotatifs[^6][^7]

```python
# backend/src/scraper/brainyquote_proxy.py
import asyncio
import random
from playwright.async_api import async_playwright

class ProxyBrainyQuoteScraper:
    def __init__(self):
        # Liste de proxies résidentiels (à obtenir d'un service)
        self.proxy_list = [
            "http://username:password@proxy1.example.com:8000",
            "http://username:password@proxy2.example.com:8000",
            # Ajouter plus de proxies
        ]
    
    async def scrape_with_proxy_rotation(self, topic: str):
        """Scraping avec rotation de proxies"""
        for proxy in self.proxy_list:
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(
                        headless=True,
                        proxy={'server': proxy}
                    )
                    
                    context = await browser.new_context()
                    page = await context.new_page()
                    
                    # Test du proxy
                    await page.goto('https://httpbin.org/ip', timeout=30000)
                    ip_info = await page.text_content('body')
                    logger.info(f"Using proxy IP: {ip_info}")
                    
                    # Tentative de scraping
                    result = await self._attempt_scraping(page, topic)
                    
                    await browser.close()
                    return result
                    
            except Exception as e:
                logger.warning(f"Proxy {proxy} failed: {e}")
                continue
        
        raise Exception("All proxies failed")
```


### Solution 4 : Mise à Jour de l'API

```python
# backend/src/api/test_scraping_stealth.py
from fastapi import APIRouter, HTTPException
import logging
from src.scraper.brainyquote_stealth import StealthBrainyQuoteScraper

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/test-stealth/{topic}")
async def test_stealth_scraping(topic: str):
    """Test endpoint avec scraping furtif"""
    try:
        logger.info(f"Testing stealth scraping for topic: {topic}")

        async with StealthBrainyQuoteScraper() as scraper:
            quotes = await scraper.scrape_topic_stealth(topic, max_pages=1)

        return {
            "topic": topic,
            "quotes_found": len(quotes),
            "quotes": quotes[:5],  # Limiter à 5 pour test
            "message": "Stealth scraping completed successfully",
            "stealth_mode": True
        }

    except Exception as e:
        logger.error(f"Stealth scraping failed: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Stealth scraping failed: {str(e)}"
        )
```


## 🚀 Plan d'Implémentation Immédiat

### Étape 1 : Installation

```bash
cd backend
pip install playwright-stealth fake-useragent
```


### Étape 2 : Créer le scraper furtif

Copie le code `StealthBrainyQuoteScraper` dans `backend/src/scraper/brainyquote_stealth.py`

### Étape 3 : Tester

```bash
curl "http://localhost:8000/api/test-stealth/motivational"
```


### Étape 4 : Si ça échoue encore

- Utiliser des **proxies résidentiels** payants[^7][^6]
- Implémenter **CAPTCHA solving** avec services comme 2captcha
- Considérer l'utilisation d'**API alternatives** ou de **services de scraping** professionnels


## 🔍 Monitoring et Debug

```python
# backend/src/core/anti_detection.py
class AntiDetectionMonitor:
    @staticmethod
    async def check_if_blocked(page):
        """Vérifier si la page est bloquée"""
        content = await page.content()
        title = await page.title()
        
        blocked_indicators = [
            "cloudflare", "403", "forbidden", "blocked",
            "just a moment", "checking your browser",
            "access denied", "captcha"
        ]
        
        return any(indicator in content.lower() or indicator in title.lower() 
                  for indicator in blocked_indicators)
    
    @staticmethod
    async def save_debug_info(page, reason="debug"):
        """Sauvegarder info de debug"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        await page.screenshot(path=f"debug_{reason}_{timestamp}.png")
        
        with open(f"debug_{reason}_{timestamp}.html", "w") as f:
            f.write(await page.content())
```

Cette approche multi-couches devrait considérablement améliorer tes chances de succès contre les protections BrainyQuote.[^2][^3][^1]
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^21][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://scrapfly.io/blog/posts/how-to-bypass-cloudflare-anti-scraping

[^2]: https://www.browserless.io/blog/bypass-cloudflare-with-playwright

[^3]: https://www.scrapeless.com/en/blog/avoid-bot-detection-with-playwright-stealth

[^4]: https://dicloak.com/blog-detail/how-to-bypass-cloudflare-bot-protection-in-2024-top-web-scraping-services

[^5]: https://blog.minamino.io.vn/2025/strategies-to-make-playwright-undetectable/

[^6]: https://moldstud.com/articles/p-expert-techniques-to-combat-ip-blocking-when-web-scraping

[^7]: https://www.octoparse.com/blog/how-do-proxies-prevent-ip-bans-in-web-scraping

[^8]: https://github.com/Leloucher95/Web-Scrapping-Test

[^9]: https://scrape.do/blog/bypass-cloudflare/

[^10]: https://www.cnbc.com/2025/07/01/cloudflare-to-block-ai-firms-from-scraping-content-without-consent.html

[^11]: https://trajectdata.com/how-to-bypass-bot-detection-web-scraping-2025/

[^12]: https://www.cloudflare.com/the-net/building-cyber-resilience/regain-control-ai-crawlers/

[^13]: https://github.com/berstend/puppeteer-extra/discussions/754

[^14]: https://brightdata.fr/blog/donnees-web/web-scraping-without-getting-blocked

[^15]: https://brightdata.com/blog/web-data/bypass-cloudflare

[^16]: https://github.com/berstend/puppeteer-extra/issues/898

[^17]: https://www.scrapingdog.com/blog/how-to-avoid-getting-blocked-while-scraping/

[^18]: https://kameleo.io/blog/how-to-bypass-cloudflare-turnstile-with-scrapy

[^19]: https://scrapeops.io/playwright-web-scraping-playbook/nodejs-playwright-extra/

[^20]: https://www.browse.ai/blog/what-is-web-scraping-complete-guide-for-2025

[^21]: https://blog.froxy.com/en/bypass-cloudflare

