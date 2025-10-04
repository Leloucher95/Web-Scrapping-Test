"""
Main application file for testing the BrainyQuote scraper with enhanced anti-detection.
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
import logging
from scraper.brainyquote_hybrid import HybridBrainyQuoteScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def test_enhanced_scraper():
    """Test the hybrid scraper with enhanced anti-detection parameters."""
    logger.info("🚀 Starting enhanced BrainyQuote scraper test...")

    # Test URLs for different categories
    test_urls = [
        "https://www.brainyquote.com/quotes/confucius_106080",
        "https://www.brainyquote.com/quotes/sam_levenson_105237",
        "https://www.brainyquote.com/quotes/charles_r_swindoll_121806",
        "https://www.brainyquote.com/quotes/william_james_150068",
        "https://www.brainyquote.com/quotes/tony_robbins_122103",
        "https://www.brainyquote.com/quotes/julie_andrews_138194",
        "https://www.brainyquote.com/quotes/bo_jackson_455548",
        "https://www.brainyquote.com/quotes/pope_john_xxiii_157881"
    ]

    async with HybridBrainyQuoteScraper() as scraper:
        # Test batch scraping with enhanced parameters
        start_time = time.time()
        results = await scraper.scrape_quotes(test_urls)
        end_time = time.time()

        # Print results summary
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 ENHANCED SCRAPER TEST RESULTS")
        logger.info(f"{'='*60}")
        logger.info(f"⏱️  Total execution time: {end_time - start_time:.2f} seconds")
        logger.info(f"📊 URLs processed: {len(test_urls)}")
        logger.info(f"✅ Successful extractions: {len(results)}")
        logger.info(f"📈 Success rate: {len(results)/len(test_urls)*100:.1f}%")

        # Save results to JSON with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"enhanced_scraping_results_{timestamp}.json")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Results saved to: {output_file}")

        # Display sample quotes
        logger.info(f"\n{'='*60}")
        logger.info(f"📝 SAMPLE EXTRACTED QUOTES")
        logger.info(f"{'='*60}")

        for i, quote in enumerate(results[:3], 1):
            logger.info(f"\n{i}. Author: {quote.get('author', 'N/A')}")
            logger.info(f"   Quote: {quote.get('text', 'N/A')[:100]}...")
            logger.info(f"   URL: {quote.get('url', 'N/A')}")
            logger.info(f"   Image: {'✅' if quote.get('image_path') else '❌'}")

        # Image download summary
        images_downloaded = sum(1 for quote in results if quote.get('image_path'))
        logger.info(f"\n🖼️  Images downloaded: {images_downloaded}/{len(results)}")

        if images_downloaded > 0:
            images_dir = Path("cached_images")
            if images_dir.exists():
                image_files = list(images_dir.glob("*.jpg"))
                logger.info(f"📁 Total cached images: {len(image_files)}")

        logger.info(f"\n{'='*60}")
        logger.info(f"✨ Enhanced scraper test completed successfully!")
        logger.info(f"{'='*60}")

async def test_single_quote():
    """Test scraping a single quote with detailed output."""
    logger.info("🔍 Testing single quote extraction...")

    test_url = "https://www.brainyquote.com/quotes/confucius_106080"

    async with HybridBrainyQuoteScraper() as scraper:
        result = await scraper.scrape_single_quote(test_url)

        if result:
            logger.info(f"\n{'='*50}")
            logger.info(f"📖 SINGLE QUOTE TEST RESULT")
            logger.info(f"{'='*50}")
            logger.info(f"👤 Author: {result.get('author', 'N/A')}")
            logger.info(f"💬 Quote: {result.get('text', 'N/A')}")
            logger.info(f"🔗 URL: {result.get('url', 'N/A')}")
            logger.info(f"🖼️  Image: {result.get('image_path', 'N/A')}")
            logger.info(f"⏰ Extracted at: {result.get('extracted_at', 'N/A')}")
            logger.info(f"{'='*50}")
        else:
            logger.error("❌ Failed to extract single quote")

def main():
    """Main function to run the scraper tests."""
    logger.info("🎬 Starting BrainyQuote Enhanced Scraper Application")

    try:
        # Test single quote first
        asyncio.run(test_single_quote())

        # Then test batch scraping
        asyncio.run(test_enhanced_scraper())

    except KeyboardInterrupt:
        logger.info("⏹️  Scraping interrupted by user")
    except Exception as e:
        logger.error(f"💥 Application error: {e}")
        raise

if __name__ == "__main__":
    main()