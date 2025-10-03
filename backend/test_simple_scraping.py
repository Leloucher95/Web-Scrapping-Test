import asyncio
from playwright.async_api import async_playwright

async def test_simple_scraping():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            url = "https://www.brainyquote.com/topics/motivational-quotes"
            print(f"Going to: {url}")

            await page.goto(url)
            await page.wait_for_load_state('networkidle')
            print("Page loaded")

            # Try different selectors
            selectors = ['.bqQt', '.grid-item', '.clearfix', 'img[alt*="quote"]']

            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    print(f"Selector '{selector}': {len(elements)} elements")

                    if elements and len(elements) > 10:
                        print(f"Using selector: {selector}")

                        # Get first few quotes
                        for i, element in enumerate(elements[:3]):
                            text = await element.inner_text()
                            html = await element.inner_html()

                            print(f"\n--- Element {i+1} ---")
                            print(f"Text: {text[:100]}...")

                            # Look for links
                            links = await element.query_selector_all('a')
                            for link in links:
                                href = await link.get_attribute('href')
                                if href and '/quotes/' in href:
                                    print(f"Quote link: {href}")

                            # Look for images
                            images = await element.query_selector_all('img')
                            for img in images:
                                alt = await img.get_attribute('alt')
                                src = await img.get_attribute('src')
                                if alt and len(alt) > 20:
                                    print(f"Quote from alt: {alt[:100]}...")
                                    print(f"Image: {src}")
                        break

                except Exception as e:
                    print(f"Error with {selector}: {e}")

            await asyncio.sleep(3)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_simple_scraping())