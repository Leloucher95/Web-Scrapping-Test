from fastapi import APIRouter, HTTPException
import logging
from src.models import ScrapingRequest, ScrapingResponse, ScrapingStatus
from src.scraper.brainyquote_stealth import StealthBrainyQuoteScraper

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/test-stealth/{topic}")
async def test_stealth_scraping(topic: str):
    """Test endpoint avec scraping furtif ultra-avancé"""
    try:
        logger.info(f"🥷 Testing STEALTH scraping for topic: {topic}")

        async with StealthBrainyQuoteScraper() as scraper:
            quotes = await scraper.test_scraping_stealth(topic, limit=5)

        return {
            "topic": topic,
            "quotes_found": len(quotes),
            "quotes": quotes,
            "message": "🎉 Stealth scraping completed successfully!",
            "stealth_mode": True,
            "anti_detection": "Advanced anti-bot protection bypassed"
        }

    except Exception as e:
        logger.error(f"🚨 Stealth scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stealth scraping failed: {str(e)}")

@router.post("/scrape/stealth", response_model=dict)
async def stealth_scraping_with_request(request: ScrapingRequest):
    """Stealth scraping avec POST request"""
    try:
        logger.info(f"🥷 STEALTH scraping for topic: {request.topic}")

        async with StealthBrainyQuoteScraper() as scraper:
            quotes = await scraper.scrape_topic_stealth(request.topic, max_pages=1)

        return {
            "topic": request.topic,
            "max_pages_requested": request.max_pages,
            "quotes_found": len(quotes),
            "quotes": quotes[:10],  # Return first 10 quotes
            "message": "🎉 Stealth scraping completed successfully!",
            "stealth_mode": True,
            "protection_bypassed": True
        }

    except Exception as e:
        logger.error(f"🚨 Stealth scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stealth scraping failed: {str(e)}")

@router.get("/health-stealth")
async def stealth_health_check():
    """Health check pour mode stealth"""
    return {
        "status": "healthy",
        "message": "🥷 Stealth Scraping API is running",
        "mode": "stealth",
        "anti_detection": "enabled"
    }