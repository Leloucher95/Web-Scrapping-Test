# src/main.py
import asyncio
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Import du scraper
from scraper.brainyquote import BrainyQuoteScraper

async def test_single_topic():
    """Test rapide sur un seul topic"""
    topic = "motivational"
    logger.info(f"🧪 Quick test for topic: {topic}")

    try:
        async with BrainyQuoteScraper() as scraper:
            quotes = await scraper.scrape_topic(topic, max_pages=1)

            print(f"\n📊 Found {len(quotes)} quotes for '{topic}':")
            print("-" * 60)

            for i, quote in enumerate(quotes[:5], 1):  # Limiter à 5 quotes pour l'affichage
                print(f"\n{i}. \"{quote['text']}\"")
                print(f"   Author: {quote['author']}")
                print(f"   Link: {quote['link']}")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

async def example():
    """Exemple simple d'utilisation"""
    print("🎯 Example: Scraping motivational quotes")

    async with BrainyQuoteScraper() as scraper:
        quotes = await scraper.scrape_topic("motivational", max_pages=1)
        for quote in quotes[:3]:  # Limiter à 3 quotes pour l'exemple
            print(f'"{quote["text"]}" - {quote["author"]}')

if __name__ == "__main__":
    print("🎯 BrainyQuote Scraper Test")
    print("1. Test rapide (5 quotes)")
    print("2. Exemple simple (3 quotes)")

    choice = input("\nChoisir une option (1 ou 2): ").strip()

    if choice == "1":
        asyncio.run(test_single_topic())
    elif choice == "2":
        asyncio.run(example())
    else:
        print("Option par défaut: test rapide")
        asyncio.run(test_single_topic())