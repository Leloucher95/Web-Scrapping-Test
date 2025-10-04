""""""

FastAPI application for QuoteScrape - Web scraping API with Supabase integrationMain application file for testing the BrainyQuote scraper with enhanced anti-detection.

IMPORTANT: Uses environment variables for Supabase credentials (no hardcoded keys!)"""

"""

import asyncio

import asyncioimport json

import jsonimport time

import timefrom pathlib import Path

import osfrom datetime import datetime

from pathlib import Pathimport logging

from datetime import datetimefrom scraper.brainyquote_hybrid import HybridBrainyQuoteScraper

import logging

from typing import Dict, List, Optional# Configure logging

from fastapi import FastAPI, HTTPException, BackgroundTaskslogging.basicConfig(

from fastapi.middleware.cors import CORSMiddleware    level=logging.INFO,

from pydantic import BaseModel    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',

from dotenv import load_dotenv    handlers=[

        logging.FileHandler('scraper.log'),

from scraper.brainyquote_hybrid import HybridBrainyQuoteScraper        logging.StreamHandler()

from database.supabase_storage import SupabaseQuoteStorage    ]

)

# Load environment variables

load_dotenv()logger = logging.getLogger(__name__)



# Configure loggingasync def test_enhanced_scraper():

logging.basicConfig(    """Test the hybrid scraper with enhanced anti-detection parameters."""

    level=logging.INFO,    logger.info("🚀 Starting enhanced BrainyQuote scraper test...")

    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',

    handlers=[    # Test URLs for different categories

        logging.FileHandler('scraper.log'),    test_urls = [

        logging.StreamHandler()        "https://www.brainyquote.com/quotes/confucius_106080",

    ]        "https://www.brainyquote.com/quotes/sam_levenson_105237",

)        "https://www.brainyquote.com/quotes/charles_r_swindoll_121806",

        "https://www.brainyquote.com/quotes/william_james_150068",

logger = logging.getLogger(__name__)        "https://www.brainyquote.com/quotes/tony_robbins_122103",

        "https://www.brainyquote.com/quotes/julie_andrews_138194",

# FastAPI app        "https://www.brainyquote.com/quotes/bo_jackson_455548",

app = FastAPI(        "https://www.brainyquote.com/quotes/pope_john_xxiii_157881"

    title="QuoteScrape API",    ]

    description="API for scraping quotes from BrainyQuote with Supabase storage",

    version="1.0.0"    async with HybridBrainyQuoteScraper() as scraper:

)        # Test batch scraping with enhanced parameters

        start_time = time.time()

# CORS configuration        results = await scraper.scrape_quotes(test_urls)

app.add_middleware(        end_time = time.time()

    CORSMiddleware,

    allow_origins=["http://localhost:3000"],  # Frontend URL        # Print results summary

    allow_credentials=True,        logger.info(f"\n{'='*60}")

    allow_methods=["*"],        logger.info(f"🎯 ENHANCED SCRAPER TEST RESULTS")

    allow_headers=["*"],        logger.info(f"{'='*60}")

)        logger.info(f"⏱️  Total execution time: {end_time - start_time:.2f} seconds")

        logger.info(f"📊 URLs processed: {len(test_urls)}")

# Global state for scraping        logger.info(f"✅ Successful extractions: {len(results)}")

scraping_state = {        logger.info(f"📈 Success rate: {len(results)/len(test_urls)*100:.1f}%")

    "status": "idle",  # idle, starting, running, completed, error

    "current_topic": "",        # Save results to JSON with timestamp

    "progress": {"current": 0, "total": 0},        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    "stats": {"extracted": 0, "images": 0, "errors": 0, "elapsed": 0},        output_file = Path(f"enhanced_scraping_results_{timestamp}.json")

    "start_time": None,

    "task": None        with open(output_file, 'w', encoding='utf-8') as f:

}            json.dump(results, f, indent=2, ensure_ascii=False)



# Pydantic models        logger.info(f"💾 Results saved to: {output_file}")

class ScrapeRequest(BaseModel):

    topic: str        # Display sample quotes

    max_quotes: int = 10        logger.info(f"\n{'='*60}")

    include_images: bool = True        logger.info(f"📝 SAMPLE EXTRACTED QUOTES")

    store_in_database: bool = True        logger.info(f"{'='*60}")



class ScrapeResponse(BaseModel):        for i, quote in enumerate(results[:3], 1):

    success: bool            logger.info(f"\n{i}. Author: {quote.get('author', 'N/A')}")

    message: str            logger.info(f"   Quote: {quote.get('text', 'N/A')[:100]}...")

    data: Optional[Dict] = None            logger.info(f"   URL: {quote.get('url', 'N/A')}")

            logger.info(f"   Image: {'✅' if quote.get('image_path') else '❌'}")

class StatusResponse(BaseModel):

    status: str        # Image download summary

    current_topic: str        images_downloaded = sum(1 for quote in results if quote.get('image_path'))

    progress: Dict[str, int]        logger.info(f"\n🖼️  Images downloaded: {images_downloaded}/{len(results)}")

    stats: Dict[str, int]

    elapsed: int        if images_downloaded > 0:

            images_dir = Path("cached_images")

# Routes            if images_dir.exists():

@app.get("/health")                image_files = list(images_dir.glob("*.jpg"))

async def health_check():                logger.info(f"📁 Total cached images: {len(image_files)}")

    """Health check endpoint"""

    return {"status": "healthy", "timestamp": datetime.now().isoformat()}        logger.info(f"\n{'='*60}")

        logger.info(f"✨ Enhanced scraper test completed successfully!")

@app.get("/api/scrape/status", response_model=StatusResponse)        logger.info(f"{'='*60}")

async def get_scraping_status():

    """Get current scraping status"""async def test_single_quote():

    elapsed = 0    """Test scraping a single quote with detailed output."""

    if scraping_state["start_time"]:    logger.info("🔍 Testing single quote extraction...")

        elapsed = int(time.time() - scraping_state["start_time"])

        test_url = "https://www.brainyquote.com/quotes/confucius_106080"

    return StatusResponse(

        status=scraping_state["status"],    async with HybridBrainyQuoteScraper() as scraper:

        current_topic=scraping_state["current_topic"],        result = await scraper.scrape_single_quote(test_url)

        progress=scraping_state["progress"],

        stats=scraping_state["stats"],        if result:

        elapsed=elapsed            logger.info(f"\n{'='*50}")

    )            logger.info(f"📖 SINGLE QUOTE TEST RESULT")

            logger.info(f"{'='*50}")

@app.post("/api/scrape/start", response_model=ScrapeResponse)            logger.info(f"👤 Author: {result.get('author', 'N/A')}")

async def start_scraping(request: ScrapeRequest, background_tasks: BackgroundTasks):            logger.info(f"💬 Quote: {result.get('text', 'N/A')}")

    """Start scraping quotes"""            logger.info(f"🔗 URL: {result.get('url', 'N/A')}")

                logger.info(f"🖼️  Image: {result.get('image_path', 'N/A')}")

    if scraping_state["status"] in ["starting", "running"]:            logger.info(f"⏰ Extracted at: {result.get('extracted_at', 'N/A')}")

        raise HTTPException(            logger.info(f"{'='*50}")

            status_code=400,         else:

            detail="Scraping already in progress"            logger.error("❌ Failed to extract single quote")

        )

    def main():

    try:    """Main function to run the scraper tests."""

        # Initialize scraping state    logger.info("🎬 Starting BrainyQuote Enhanced Scraper Application")

        scraping_state.update({

            "status": "starting",    try:

            "current_topic": request.topic,        # Test single quote first

            "progress": {"current": 0, "total": request.max_quotes},        asyncio.run(test_single_quote())

            "stats": {"extracted": 0, "images": 0, "errors": 0, "elapsed": 0},

            "start_time": time.time()        # Then test batch scraping

        })        asyncio.run(test_enhanced_scraper())



        # Start background task    except KeyboardInterrupt:

        background_tasks.add_task(        logger.info("⏹️  Scraping interrupted by user")

            run_scraping_task,    except Exception as e:

            request.topic,        logger.error(f"💥 Application error: {e}")

            request.max_quotes,        raise

            request.include_images,

            request.store_in_databaseif __name__ == "__main__":

        )    main()

        return ScrapeResponse(
            success=True,
            message=f"Scraping started for topic: {request.topic}",
            data={"topic": request.topic, "max_quotes": request.max_quotes}
        )

    except Exception as e:
        logger.error(f"Error starting scraping: {e}")
        scraping_state["status"] = "error"
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scrape/stop", response_model=ScrapeResponse)
async def stop_scraping():
    """Stop current scraping"""

    if scraping_state["status"] not in ["starting", "running"]:
        raise HTTPException(
            status_code=400,
            detail="No scraping in progress"
        )

    try:
        # Cancel the task if it exists
        if scraping_state["task"]:
            scraping_state["task"].cancel()

        scraping_state["status"] = "stopped"

        return ScrapeResponse(
            success=True,
            message="Scraping stopped successfully"
        )

    except Exception as e:
        logger.error(f"Error stopping scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_scraping_task(topic: str, max_quotes: int, include_images: bool, store_in_database: bool):
    """Background task for scraping"""

    try:
        scraping_state["status"] = "running"
        logger.info(f"Starting scraping task for topic: {topic}")

        # Initialize components
        scraper = HybridBrainyQuoteScraper()
        storage = None

        if store_in_database:
            # Check if environment variables are set
            if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
                logger.warning("Supabase credentials not found. Using local storage only.")
                store_in_database = False
            else:
                storage = SupabaseQuoteStorage()

        # Scrape quotes
        quotes = await scraper.scrape_quotes(topic, max_quotes)

        logger.info(f"Scraped {len(quotes)} quotes successfully")
        scraping_state["stats"]["extracted"] = len(quotes)
        scraping_state["progress"]["current"] = len(quotes)

        # Download images if requested
        if include_images:
            logger.info("Starting image downloads...")
            image_results = await scraper.download_images(quotes)
            scraping_state["stats"]["images"] = len([r for r in image_results if r.get("success")])

        # Store in database if requested
        if store_in_database and storage:
            logger.info("Storing quotes in Supabase...")
            try:
                stored_quotes = await storage.store_quotes_batch(quotes)
                logger.info(f"Stored {len(stored_quotes)} quotes in database")

                if include_images:
                    logger.info("Uploading images to Supabase...")
                    uploaded_count = 0
                    for quote in quotes:
                        if hasattr(quote, 'local_image_path') and quote.local_image_path:
                            try:
                                image_url = await storage.upload_image(quote.local_image_path, quote.id)
                                if image_url:
                                    uploaded_count += 1
                            except Exception as e:
                                logger.error(f"Error uploading image for quote {quote.id}: {e}")
                                scraping_state["stats"]["errors"] += 1

                    logger.info(f"Uploaded {uploaded_count} images to Supabase")

            except Exception as e:
                logger.error(f"Error storing in database: {e}")
                scraping_state["stats"]["errors"] += 1

        # Update final state
        scraping_state["status"] = "completed"
        scraping_state["stats"]["elapsed"] = int(time.time() - scraping_state["start_time"])

        logger.info(f"Scraping completed successfully. Stats: {scraping_state['stats']}")

    except asyncio.CancelledError:
        logger.info("Scraping task was cancelled")
        scraping_state["status"] = "stopped"
    except Exception as e:
        logger.error(f"Error in scraping task: {e}")
        scraping_state["status"] = "error"
        scraping_state["stats"]["errors"] += 1
    finally:
        # Clean up
        if 'scraper' in locals():
            await scraper.close()

if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))

    logger.info(f"Starting FastAPI server on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )