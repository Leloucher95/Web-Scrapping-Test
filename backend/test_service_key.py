"""
Test Supabase storage using service role key for admin operations.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

async def test_with_service_key():
    """Test using service role key for admin operations."""
    logger.info("🔑 Testing with Supabase service role key...")

    # Get service role credentials
    url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_KEY')

    if not url or not service_key:
        logger.error("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env file")
        return False

    logger.info(f"📍 URL: {url}")
    logger.info(f"🔑 Service Key: {service_key[:20]}...")

    try:
        # Create client with service role key
        supabase = create_client(url, service_key)
        logger.info("✅ Supabase service client created!")

        # Load existing results
        results_file = Path("enhanced_scraping_results_20251004_185159.json")

        if not results_file.exists():
            logger.error(f"❌ Results file not found: {results_file}")
            return False

        logger.info(f"📖 Loading results from: {results_file}")
        with open(results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)

        logger.info(f"📊 Processing {len(results)} quotes...")

        # Store quotes
        stored_count = 0
        errors = 0

        for i, quote in enumerate(results, 1):
            try:
                # Prepare quote data
                db_quote = {
                    "text": quote.get('text'),
                    "author": quote.get('author'),
                    "source_url": quote.get('link'),
                    "image_url": quote.get('image_url'),
                    "category": "motivational",
                    "extracted_at": datetime.now().isoformat(),
                    "metadata": {
                        "index": quote.get('index'),
                        "original_image_url": quote.get('image_url'),
                        "image_size": quote.get('image_data', {}).get('size'),
                        "extraction_method": "hybrid_scraper",
                        "local_image_path": quote.get('image_data', {}).get('local_path')
                    }
                }

                # Insert quote
                result = supabase.table("quotes").insert(db_quote).execute()

                if result.data:
                    quote_id = result.data[0]['id']
                    logger.info(f"✅ {i}/{len(results)} Stored: {quote.get('author')} - ID: {quote_id}")
                    stored_count += 1
                else:
                    logger.error(f"❌ {i}/{len(results)} Failed to store quote")
                    errors += 1

            except Exception as e:
                if "duplicate key value" in str(e):
                    logger.warning(f"⚠️  {i}/{len(results)} Quote already exists: {quote.get('author')}")
                else:
                    logger.error(f"❌ {i}/{len(results)} Error: {e}")
                errors += 1

        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 STORAGE RESULTS")
        logger.info(f"{'='*60}")
        logger.info(f"✅ Quotes stored: {stored_count}/{len(results)}")
        logger.info(f"❌ Errors: {errors}")
        logger.info(f"📈 Success rate: {stored_count/len(results)*100:.1f}%")

        # Get current stats
        stats_result = supabase.table("quotes").select("id", count="exact").execute()
        total_quotes = stats_result.count

        authors_result = supabase.table("quotes").select("author").execute()
        unique_authors = len(set(row['author'] for row in authors_result.data)) if authors_result.data else 0

        logger.info(f"\n📊 Database stats:")
        logger.info(f"   Total quotes: {total_quotes}")
        logger.info(f"   Unique authors: {unique_authors}")

        # Test retrieval
        logger.info(f"\n🔍 Testing retrieval...")
        recent_result = supabase.table("quotes").select("*").order("extracted_at", desc=True).limit(3).execute()

        if recent_result.data:
            logger.info(f"📝 Recent quotes:")
            for i, quote in enumerate(recent_result.data, 1):
                logger.info(f"  {i}. {quote.get('author')}: {quote.get('text')[:50]}...")

        logger.info(f"{'='*60}")

        return True

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

def main():
    """Main function."""
    logger.info("🚀 Testing Supabase with Service Role Key")

    try:
        success = asyncio.run(test_with_service_key())
        if success:
            logger.info("✅ Test completed successfully!")
        else:
            logger.error("❌ Test failed!")

    except KeyboardInterrupt:
        logger.info("⏹️  Test interrupted by user")
    except Exception as e:
        logger.error(f"💥 Test error: {e}")

if __name__ == "__main__":
    main()