"""
Test script to store quotes in Supabase database only (without image storage).
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from scraper.brainyquote_hybrid import HybridBrainyQuoteScraper
from database.supabase_storage import SupabaseQuoteStorage

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

async def test_database_only():
    """Test storing quotes in database without image upload."""
    logger.info("🔄 Testing database storage only...")

    # Use existing scraped results
    results_file = Path("enhanced_scraping_results_20251004_185159.json")

    if not results_file.exists():
        logger.error(f"❌ Results file not found: {results_file}")
        logger.info("🔄 Scraping new quotes...")

        # Quick scrape
        test_urls = [
            "https://www.brainyquote.com/quotes/confucius_106080",
            "https://www.brainyquote.com/quotes/sam_levenson_105237",
            "https://www.brainyquote.com/quotes/charles_r_swindoll_121806"
        ]

        async with HybridBrainyQuoteScraper() as scraper:
            results = await scraper.scrape_quotes(test_urls)
    else:
        logger.info(f"📖 Loading existing results from: {results_file}")
        with open(results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)

    if not results:
        logger.error("❌ No quotes to process")
        return

    logger.info(f"📊 Processing {len(results)} quotes...")

    try:
        storage = SupabaseQuoteStorage()

        # Test database connection
        db_ok = await storage.setup_database()
        if not db_ok:
            logger.error("❌ Database connection failed")
            return

        # Store quotes (without image upload)
        stored_count = 0
        errors = 0

        for i, quote in enumerate(results, 1):
            try:
                # Prepare quote data for database
                db_quote = {
                    "text": quote.get('text'),
                    "author": quote.get('author'),
                    "source_url": quote.get('link'),
                    "image_url": quote.get('image_url'),
                    "category": "motivational",  # Default category
                    "extracted_at": datetime.now().isoformat(),
                    "metadata": {
                        "index": quote.get('index'),
                        "original_image_url": quote.get('image_url'),
                        "image_size": quote.get('image_data', {}).get('size'),
                        "extraction_method": "hybrid_scraper"
                    }
                }

                # Insert quote into database
                result = storage.supabase.table("quotes").insert(db_quote).execute()

                if result.data:
                    quote_id = result.data[0]['id']
                    logger.info(f"✅ {i}/{len(results)} Stored: {quote.get('author')} - ID: {quote_id}")
                    stored_count += 1
                else:
                    logger.error(f"❌ {i}/{len(results)} Failed to store quote")
                    errors += 1

            except Exception as e:
                logger.error(f"❌ {i}/{len(results)} Error: {e}")
                errors += 1

        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 DATABASE STORAGE SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"✅ Quotes stored: {stored_count}/{len(results)}")
        logger.info(f"❌ Errors: {errors}")
        logger.info(f"📈 Success rate: {stored_count/len(results)*100:.1f}%")

        # Get stats
        stats = await storage.get_stats()
        logger.info(f"\n📊 Database stats:")
        logger.info(f"   Total quotes: {stats['total_quotes']}")
        logger.info(f"   Unique authors: {stats['unique_authors']}")
        logger.info(f"{'='*60}")

    except Exception as e:
        logger.error(f"❌ Storage error: {e}")

async def test_retrieval():
    """Test retrieving data from database."""
    logger.info("🔍 Testing data retrieval...")

    try:
        storage = SupabaseQuoteStorage()

        # Get recent quotes
        recent_quotes = await storage.get_recent_quotes(5)
        logger.info(f"📝 Retrieved {len(recent_quotes)} recent quotes:")

        for i, quote in enumerate(recent_quotes, 1):
            logger.info(f"  {i}. {quote.get('author', 'Unknown')}: {quote.get('text', 'N/A')[:50]}...")

        # Search by author
        confucius_quotes = await storage.get_quotes_by_author("Confucius")
        logger.info(f"🎯 Found {len(confucius_quotes)} quotes by Confucius")

    except Exception as e:
        logger.error(f"❌ Retrieval error: {e}")

def main():
    """Main function."""
    logger.info("🚀 Testing Supabase Database Storage (No Images)")

    try:
        asyncio.run(test_database_only())
        asyncio.run(test_retrieval())
        logger.info("✅ Database test completed!")

    except KeyboardInterrupt:
        logger.info("⏹️  Test interrupted by user")
    except Exception as e:
        logger.error(f"💥 Test error: {e}")

if __name__ == "__main__":
    main()