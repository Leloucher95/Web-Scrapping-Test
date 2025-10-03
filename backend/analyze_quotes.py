import asyncio
from playwright.async_api import async_playwright

async def analyze_quote_structure():
    """Analyze the exact structure of quotes on BrainyQuote"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            url = "https://www.brainyquote.com/topics/motivational-quotes"
            print(f"Navigating to: {url}")

            await page.goto(url, timeout=30000)
            await page.wait_for_load_state('networkidle')

            # Attendre que les citations se chargent
            await page.wait_for_selector('.grid-item', timeout=10000)

            # Prendre les premiers éléments de citation
            quote_elements = await page.query_selector_all('.grid-item .bqQt')

            print(f"Found {len(quote_elements)} quote elements")

            # Analyser les 3 premières citations en détail
            for i, quote_element in enumerate(quote_elements[:3]):
                print(f"\n=== QUOTE {i+1} ANALYSIS ===")

                # HTML complet de l'élément
                quote_html = await quote_element.inner_html()
                print(f"Full HTML:\n{quote_html}\n")

                # Texte brut
                quote_text = await quote_element.inner_text()
                print(f"Inner text: {quote_text}")

                # Analyser les liens
                links = await quote_element.query_selector_all('a')
                for j, link in enumerate(links):
                    href = await link.get_attribute('href')
                    title = await link.get_attribute('title')
                    link_text = await link.inner_text()
                    print(f"  Link {j+1}: href={href}, title={title}, text={link_text}")

                # Analyser les images
                images = await quote_element.query_selector_all('img')
                for j, img in enumerate(images):
                    src = await img.get_attribute('src')
                    alt = await img.get_attribute('alt')
                    print(f"  Image {j+1}: src={src}, alt={alt}")

                print("-" * 50)

            # Essayer de cliquer sur une citation pour voir la page de détail
            first_link = await page.query_selector('.grid-item .bqQt a[title="view quote"]')
            if first_link:
                print("\n=== CLICKING ON FIRST QUOTE ===")
                href = await first_link.get_attribute('href')
                print(f"Navigating to: https://www.brainyquote.com{href}")

                # Ouvrir dans un nouvel onglet
                new_page = await browser.new_page()
                await new_page.goto(f"https://www.brainyquote.com{href}")
                await new_page.wait_for_load_state('networkidle')

                # Analyser la page de citation individuelle
                quote_detail_html = await new_page.content()
                print(f"Quote detail page length: {len(quote_detail_html)}")

                # Chercher le texte de la citation sur la page de détail
                possible_selectors = [
                    '.b-qt',
                    '.quote-text',
                    '.quotetxt',
                    'h1',
                    '.qcontent'
                ]

                for selector in possible_selectors:
                    try:
                        element = await new_page.query_selector(selector)
                        if element:
                            text = await element.inner_text()
                            print(f"Selector '{selector}': {text[:100]}...")
                    except:
                        pass

                await new_page.close()

            await asyncio.sleep(5)

        except Exception as e:
            print(f"Error during analysis: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze_quote_structure())