import asyncio
from playwright.async_api import async_playwright

async def debug_brainyquote_selectors():
    """Debug script to analyze BrainyQuote page structure"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible pour debug
        page = await browser.new_page()

        try:
            url = "https://www.brainyquote.com/topics/motivational-quotes"
            print(f"Navigating to: {url}")

            await page.goto(url, timeout=30000)
            await page.wait_for_load_state('networkidle')

            # Prendre une capture d'écran
            await page.screenshot(path="debug_brainyquote.png")
            print("Screenshot saved as debug_brainyquote.png")

            # Analyser la structure HTML
            print("\n=== Analyzing page structure ===")

            # Chercher différents sélecteurs possibles pour les citations
            selectors_to_test = [
                ".quotelist",
                ".quote-wrapper",
                ".quote",
                ".grid-item",
                "[data-testid*='quote']",
                ".clearfix",
                "article",
                ".bqQt",
                ".m-brick",
                ".gridI"
            ]

            for selector in selectors_to_test:
                try:
                    elements = await page.query_selector_all(selector)
                    print(f"Selector '{selector}': {len(elements)} elements found")

                    if elements and len(elements) > 0:
                        # Analyser le premier élément trouvé
                        first_element = elements[0]
                        html_content = await first_element.inner_html()
                        print(f"  First element HTML preview: {html_content[:200]}...")

                except Exception as e:
                    print(f"Selector '{selector}': Error - {e}")

            # Obtenir le HTML de la page entière (limité)
            page_content = await page.content()
            print(f"\nPage content length: {len(page_content)} characters")

            # Chercher des patterns de citations dans le contenu
            quote_patterns = ["quote", "author", "citation"]
            for pattern in quote_patterns:
                if pattern.lower() in page_content.lower():
                    print(f"Pattern '{pattern}' found in page content")

            await asyncio.sleep(5)  # Temps pour examiner la page

        except Exception as e:
            print(f"Error during debug: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_brainyquote_selectors())