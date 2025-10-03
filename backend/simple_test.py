import asyncio
from playwright.async_api import async_playwright

async def simple_structure_test():
    """Test simple pour identifier la structure"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            url = "https://www.brainyquote.com/topics/motivational-quotes"
            print(f"Navigating to: {url}")

            await page.goto(url, timeout=30000)
            await page.wait_for_load_state('networkidle')

            # Test différents sélecteurs individuellement
            selectors = ['.bqQt', '.grid-item', '.clearfix', '.m-brick']

            for selector in selectors:
                elements = await page.query_selector_all(selector)
                print(f"Selector '{selector}': {len(elements)} elements")

                if elements and len(elements) > 0:
                    first_html = await elements[0].inner_html()
                    first_text = await elements[0].inner_text()
                    print(f"  First element HTML: {first_html[:300]}...")
                    print(f"  First element text: {first_text[:100]}...")
                    print()

            await asyncio.sleep(3)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(simple_structure_test())