import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create FastAPI app
app = FastAPI(
    title="BrainyQuote Scraper API - Test Mode",
    description="Web scraping API for BrainyQuote citations - Testing without database",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include test router
from src.api.test_scraping import router as test_router

app.include_router(test_router, prefix="/api", tags=["Test Scraping"])

@app.get("/")
async def root():
    return {
        "message": "BrainyQuote Scraper API - Test Mode",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "test_scraping": "/api/test/{topic}",
            "test_scraping_post": "/api/scrape/test",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "mode": "test"}

if __name__ == "__main__":
    uvicorn.run(
        "main_test:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )