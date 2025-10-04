"""
Enhanced main application with Supabase integration for storing quotes and images.
"""

import asyncio
import json
import time
import os
from pathlib import Path
from datetime import datetime
import logging
from dotenv import load_dotenv

from scraper.brainyquote_hybrid import HybridBrainyQuoteScraper
from database.supabase_storage import SupabaseQuoteStorage

# Load environment variables
load_dotenv()

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

async def test_supabase_connection():
    """Test Supabase connection and setup."""
    logger.info("🔗 Testing Supabase connection...")

    try:
        storage = SupabaseQuoteStorage()

        # Test database connection
        db_ok = await storage.setup_database()
        if not db_ok:
            logger.error("❌ Database connection failed")
            return False

        # Test storage setup
        storage_ok = await storage.setup_storage()
        if not storage_ok:
            logger.error("❌ Storage setup failed")
            return False

        # Get current stats
        stats = await storage.get_stats()
        logger.info(f"📊 Current database stats: {stats}")

        logger.info("✅ Supabase connection successful!")
        return True

    except Exception as e:
        logger.error(f"❌ Supabase connection error: {e}")
        return False

async def scrape_and_store_quotes():
    """Complete workflow: scrape quotes and store in Supabase."""
    logger.info("🚀 Starting complete scrape and store workflow...")

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

    # Step 1: Scrape quotes
    logger.info("📖 Step 1: Scraping quotes...")
    start_time = time.time()

    async with HybridBrainyQuoteScraper() as scraper:
        results = await scraper.scrape_quotes(test_urls)

    scrape_time = time.time() - start_time

    if not results:
        logger.error("❌ No quotes scraped. Aborting.")
        return

    logger.info(f"✅ Scraped {len(results)} quotes in {scrape_time:.2f} seconds")

    # Step 2: Store in Supabase
    logger.info("💾 Step 2: Storing in Supabase...")
    storage_start = time.time()

    try:
        storage = SupabaseQuoteStorage()

        # Setup database and storage
        await storage.setup_database()
        await storage.setup_storage()

        # Store quotes
        storage_results = await storage.store_quotes_batch(results)

        storage_time = time.time() - storage_start

        # Step 3: Final summary
        total_time = time.time() - start_time

        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 COMPLETE WORKFLOW RESULTS")
        logger.info(f"{'='*60}")
        logger.info(f"⏱️  Total time: {total_time:.2f} seconds")
        logger.info(f"📖 Scraping time: {scrape_time:.2f} seconds")
        logger.info(f"💾 Storage time: {storage_time:.2f} seconds")
        logger.info(f"📊 URLs processed: {len(test_urls)}")
        logger.info(f"✅ Quotes scraped: {len(results)}")
        logger.info(f"💽 Quotes stored: {storage_results['stored_quotes']}")
        logger.info(f"🖼️  Images uploaded: {storage_results['uploaded_images']}")
        logger.info(f"❌ Storage errors: {storage_results['errors']}")
        logger.info(f"📈 End-to-end success rate: {storage_results['stored_quotes']/len(test_urls)*100:.1f}%")

        # Get updated stats
        stats = await storage.get_stats()
        logger.info(f"\n📊 Updated database stats:")
        logger.info(f"   Total quotes: {stats['total_quotes']}")
        logger.info(f"   Quotes with images: {stats['quotes_with_images']}")
        logger.info(f"   Unique authors: {stats['unique_authors']}")
        logger.info(f"   Image coverage: {stats['image_percentage']:.1f}%")

        logger.info(f"{'='*60}")

        # Save local backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = Path(f"supabase_backup_{timestamp}.json")

        backup_data = {
            "workflow_results": storage_results,
            "scraped_quotes": results,
            "stats": stats,
            "timestamp": timestamp
        }

        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Backup saved: {backup_file}")

    except Exception as e:
        logger.error(f"❌ Storage error: {e}")
        raise

async def test_supabase_retrieval():
    """Test retrieving data from Supabase."""
    logger.info("🔍 Testing Supabase data retrieval...")

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

        return True

    except Exception as e:
        logger.error(f"❌ Retrieval test error: {e}")
        return False

async def quick_scrape_test():
    """Quick test of scraper only."""
    logger.info("⚡ Quick scraper test...")

    test_url = "https://www.brainyquote.com/quotes/confucius_106080"

    async with HybridBrainyQuoteScraper() as scraper:
        result = await scraper.scrape_single_quote(test_url)

        if result:
            logger.info(f"✅ Quick test successful:")
            logger.info(f"   Author: {result.get('author', 'N/A')}")
            logger.info(f"   Quote: {result.get('text', 'N/A')[:100]}...")
            logger.info(f"   Image: {'✅' if result.get('image_data') else '❌'}")
        else:
            logger.error("❌ Quick test failed")

def main():
    """Main application entry point."""
    logger.info("🎬 Starting Enhanced BrainyQuote Application with Supabase")

    # Check environment variables
    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_ANON_KEY'):
        logger.warning("⚠️  Supabase credentials not found in environment")
        logger.info("💡 Please create a .env file with SUPABASE_URL and SUPABASE_ANON_KEY")
        logger.info("📄 See supabase_config.env.example for reference")

        # Run scraper only mode
        logger.info("🔄 Running in scraper-only mode...")
        try:
            asyncio.run(quick_scrape_test())
        except KeyboardInterrupt:
            logger.info("⏹️  Interrupted by user")
        except Exception as e:
            logger.error(f"💥 Scraper error: {e}")
        return

    try:
        # Test Supabase connection first
        supabase_ok = asyncio.run(test_supabase_connection())

        if not supabase_ok:
            logger.error("❌ Cannot proceed without Supabase connection")
            return

        # Run complete workflow
        asyncio.run(scrape_and_store_quotes())

        # Test data retrieval
        asyncio.run(test_supabase_retrieval())

        logger.info("🎉 Application completed successfully!")

    except KeyboardInterrupt:
        logger.info("⏹️  Application interrupted by user")
    except Exception as e:
        logger.error(f"💥 Application error: {e}")
        raise

if __name__ == "__main__":
    main()