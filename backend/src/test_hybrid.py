# Test du scraper hybride
import asyncio
import logging
import json
from scraper.brainyquote_hybrid import HybridBrainyQuoteScraper

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

async def test_hybrid_scraper():
    """Test du scraper hybride (simplicité + extraction améliorée)"""
    logger.info("🚀 Testing Hybrid BrainyQuote Scraper")

    try:
        async with HybridBrainyQuoteScraper() as scraper:
            # Test avec 8 citations
            quotes = await scraper.scrape_topic("motivational", max_pages=1, max_quotes=8)

            print(f"\n📊 Successfully extracted {len(quotes)} quotes:")
            print("=" * 100)

            valid_quotes = 0
            quotes_with_images = 0

            for i, quote in enumerate(quotes, 1):
                print(f"\n📝 Quote {i}:")
                print(f"   Text: {quote['text']}")
                print(f"   Author: {quote['author']}")
                print(f"   Link: {quote['link']}")
                print(f"   Image URL: {quote['image_url'][:60]}..." if quote['image_url'] else "   Image URL: None")

                if quote.get('image_data'):
                    print(f"   Image Downloaded: ✅ ({quote['image_data']['filename']})")
                    quotes_with_images += 1
                else:
                    print(f"   Image Downloaded: ❌")

                if len(quote['text']) > 10 and quote['author'] != 'Unknown':
                    valid_quotes += 1

                print("-" * 80)

            # Statistiques
            print(f"\n📈 Hybrid Scraper Statistics:")
            print(f"   Total quotes extracted: {len(quotes)}")
            print(f"   Valid quotes (text >10 chars, known author): {valid_quotes}")
            print(f"   Quotes with downloaded images: {quotes_with_images}")
            print(f"   Text extraction success rate: {valid_quotes/len(quotes)*100:.1f}%")
            print(f"   Image download success rate: {quotes_with_images/len(quotes)*100:.1f}%")

            # Sauvegarder
            results = {
                'scraper_type': 'hybrid',
                'topic': 'motivational',
                'total_quotes': len(quotes),
                'valid_quotes': valid_quotes,
                'quotes_with_images': quotes_with_images,
                'quotes': quotes
            }

            with open('hybrid_scraping_results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)

            logger.info("✅ Results saved to hybrid_scraping_results.json")

            return quotes

    except Exception as e:
        logger.error(f"❌ Hybrid scraper test failed: {str(e)}")
        raise

if __name__ == "__main__":
    print("🎯 Hybrid BrainyQuote Scraper Test")
    print("Combines the reliability of the basic scraper with enhanced text and image extraction")

    asyncio.run(test_hybrid_scraper())