# Test du scraper amélioré
import asyncio
import logging
import json
from scraper.brainyquote_enhanced import EnhancedBrainyQuoteScraper

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

async def test_enhanced_scraper():
    """Test du scraper amélioré"""
    logger.info("🚀 Testing Enhanced BrainyQuote Scraper")

    try:
        async with EnhancedBrainyQuoteScraper() as scraper:
            # Test avec 10 citations
            quotes = await scraper.scrape_topic("motivational", max_pages=1, max_quotes=10)

            print(f"\n📊 Successfully extracted {len(quotes)} quotes:")
            print("=" * 80)

            for i, quote in enumerate(quotes, 1):
                print(f"\n📝 Quote {i}:")
                print(f"   Text: {quote['text']}")
                print(f"   Author: {quote['author']}")
                print(f"   Link: {quote['link']}")
                print(f"   Image URL: {quote['image_url']}")
                if quote.get('image_data'):
                    print(f"   Image Downloaded: ✅ ({quote['image_data']['filename']})")
                else:
                    print(f"   Image Downloaded: ❌")
                print("-" * 60)

            # Statistiques
            valid_quotes = [q for q in quotes if q['text'] and len(q['text']) > 10]
            quotes_with_images = [q for q in quotes if q.get('image_data')]

            print(f"\n📈 Statistics:")
            print(f"   Total quotes extracted: {len(quotes)}")
            print(f"   Valid quotes (>10 chars): {len(valid_quotes)}")
            print(f"   Quotes with images: {len(quotes_with_images)}")
            print(f"   Success rate: {len(valid_quotes)/len(quotes)*100:.1f}%")

            # Sauvegarder les résultats
            results = {
                'topic': 'motivational',
                'total_quotes': len(quotes),
                'valid_quotes': len(valid_quotes),
                'quotes_with_images': len(quotes_with_images),
                'quotes': quotes
            }

            with open('enhanced_scraping_results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info("✅ Results saved to enhanced_scraping_results.json")

    except Exception as e:
        logger.error(f"❌ Enhanced scraper test failed: {str(e)}")
        raise

async def test_multiple_topics():
    """Test sur plusieurs sujets"""
    topics = ["motivational", "love", "success", "wisdom"]

    async with EnhancedBrainyQuoteScraper() as scraper:
        for topic in topics:
            logger.info(f"\n🎯 Testing topic: {topic}")
            try:
                quotes = await scraper.scrape_topic(topic, max_pages=1, max_quotes=3)
                print(f"✅ {topic}: {len(quotes)} quotes extracted")

                for quote in quotes:
                    print(f"   • \"{quote['text'][:50]}...\" - {quote['author']}")

            except Exception as e:
                logger.error(f"❌ Failed to scrape {topic}: {str(e)}")

            await asyncio.sleep(2)  # Pause entre les sujets

if __name__ == "__main__":
    print("🎯 Enhanced BrainyQuote Scraper Test")
    print("1. Test approfondi (10 quotes motivational)")
    print("2. Test multi-sujets (3 quotes par sujet)")

    choice = input("\nChoisir une option (1 ou 2): ").strip()

    if choice == "1":
        asyncio.run(test_enhanced_scraper())
    elif choice == "2":
        asyncio.run(test_multiple_topics())
    else:
        print("Option par défaut: test approfondi")
        asyncio.run(test_enhanced_scraper())