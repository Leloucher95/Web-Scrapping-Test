from fastapi import APIRouter, HTTPException
import logging
from src.models import ScrapingRequest, ScrapingResponse, ScrapingStatus
from src.scraper.brainyquote import BrainyQuoteScraper

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/test/{topic}")
async def test_scraping(topic: str):
    """Test endpoint to scrape a few quotes without database"""
    try:
        logger.info(f"Testing scraping for topic: {topic}")

        async with BrainyQuoteScraper() as scraper:
            quotes = await scraper.test_scraping(topic, limit=5)

        return {
            "topic": topic,
            "quotes_found": len(quotes),
            "quotes": quotes,
            "message": "Test scraping completed successfully"
        }

    except Exception as e:
        logger.error(f"Test scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test scraping failed: {str(e)}")

@router.post("/scrape/test", response_model=dict)
async def test_scraping_with_request(request: ScrapingRequest):
    """Test scraping with a POST request"""
    try:
        logger.info(f"Testing scraping for topic: {request.topic}")

        async with BrainyQuoteScraper() as scraper:
            # Limit to 1 page for testing
            quotes = await scraper.scrape_topic(request.topic, max_pages=1)

        return {
            "topic": request.topic,
            "max_pages_requested": request.max_pages,
            "quotes_found": len(quotes),
            "quotes": quotes[:10],  # Return first 10 quotes
            "message": "Test scraping completed successfully"
        }

    except Exception as e:
        logger.error(f"Test scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test scraping failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Scraping API is running"}