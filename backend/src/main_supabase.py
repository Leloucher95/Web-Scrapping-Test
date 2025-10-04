"""
Enhanced main application with Supabase integration for storing quotes and images.
Now with FastAPI API endpoints!
"""

import asyncio
import json
import time
import os
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

# FastAPI app
app = FastAPI(
    title="QuoteScrape API",
    description="Enhanced scraping API with Supabase integration",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for API
scraping_state = {
    "status": "idle",
    "current_topic": "",
    "progress": {"current": 0, "total": 0},
    "stats": {"extracted": 0, "images": 0, "errors": 0, "elapsed": 0},
    "start_time": None,
}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"📡 WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"📡 WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            logger.warning(f"📡 No WebSocket connections to broadcast to")
            return

        logger.info(f"📡 Broadcasting to {len(self.active_connections)} connections: {message[:100]}...")
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"📡 Failed to send to connection: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

# Pydantic models
class ScrapeRequest(BaseModel):
    topic: str
    max_quotes: int = 10
    include_images: bool = True
    store_in_database: bool = True

class ScrapeResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None

# FastAPI Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/scrape/status")
async def get_scraping_status():
    """Get current scraping status"""
    elapsed = 0
    if scraping_state["start_time"]:
        elapsed = int(time.time() - scraping_state["start_time"])

    return {
        "status": scraping_state["status"],
        "current_topic": scraping_state["current_topic"],
        "progress": scraping_state["progress"],
        "stats": scraping_state["stats"],
        "elapsed": elapsed
    }

@app.post("/api/scrape/start", response_model=ScrapeResponse)
async def start_scraping(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """Start scraping quotes"""

    if scraping_state["status"] in ["starting", "running"]:
        raise HTTPException(status_code=400, detail="Scraping already in progress")

    try:
        # Initialize scraping state
        scraping_state.update({
            "status": "starting",
            "current_topic": request.topic,
            "progress": {"current": 0, "total": request.max_quotes},
            "stats": {"extracted": 0, "images": 0, "errors": 0, "elapsed": 0},
            "start_time": time.time()
        })

        # Start background task using existing workflow
        background_tasks.add_task(
            api_scraping_workflow,
            request.topic,
            request.max_quotes,
            request.include_images,
            request.store_in_database
        )

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
        raise HTTPException(status_code=400, detail="No scraping in progress")

    scraping_state["status"] = "stopped"

    return ScrapeResponse(
        success=True,
        message="Scraping stopped successfully"
    )

@app.websocket("/ws/scraping")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time scraping updates"""
    await manager.connect(websocket)
    try:
        # Send initial status
        initial_status = {
            "type": "status",
            "status": scraping_state["status"],
            "progress": scraping_state["progress"],
            "stats": scraping_state["stats"],
            "elapsed": int(time.time() - scraping_state["start_time"]) if scraping_state["start_time"] else 0
        }
        await manager.send_personal_message(json.dumps(initial_status), websocket)

        # Keep connection alive
        while True:
            try:
                # Wait for ping/pong or other messages
                data = await websocket.receive_text()
                # Echo back or handle specific commands
                if data == "ping":
                    await manager.send_personal_message("pong", websocket)
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)

async def broadcast_update(update_type: str, data: Dict):
    """Helper function to broadcast updates to all connected clients"""
    message = {
        "type": update_type,
        "timestamp": datetime.now().isoformat(),
        **data
    }
    await manager.broadcast(json.dumps(message))

async def api_scraping_workflow(topic: str, max_quotes: int, include_images: bool, store_in_database: bool):
    """API version of the scraping workflow with WebSocket updates"""
    try:
        scraping_state["status"] = "running"
        logger.info(f"🚀 API: Starting scraping workflow for topic: {topic}")

        # Broadcast start
        await broadcast_update("status", {
            "status": "running",
            "message": f"Démarrage du scraping pour '{topic}'"
        })

        # Initialize storage component
        storage = None
        if store_in_database:
            # Check if environment variables are set
            if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_KEY") or not os.getenv("SUPABASE_ANON_KEY"):
                logger.warning("Supabase credentials not found. Using local storage only.")
                await broadcast_update("error", {
                    "message": "Clés Supabase manquantes - stockage local uniquement"
                })
                store_in_database = False
            else:
                storage = SupabaseQuoteStorage()

        # Use context manager for scraper
        async with HybridBrainyQuoteScraper() as scraper:
            # Phase 1: Scrape quotes
            await broadcast_update("progress", {
                "message": "Phase 1: Extraction des citations...",
                "current": 0,
                "total": max_quotes
            })

            quotes = await scraper.scrape_topic(topic, max_quotes=max_quotes)

            logger.info(f"Scraped {len(quotes)} quotes successfully")
            scraping_state["stats"]["extracted"] = len(quotes)
            scraping_state["progress"]["current"] = len(quotes)

            # Broadcast each quote as it's extracted
            for i, quote in enumerate(quotes):
                await broadcast_update("quote_extracted", {
                    "quote": {
                        "id": quote.get('index'),
                        "text": quote.get('text'),
                        "author": quote.get('author'),
                        "topic": topic
                    },
                    "progress": {"current": i + 1, "total": max_quotes}
                })

                # Update progress in real-time
                await broadcast_update("progress", {
                    "message": f"Citation {i + 1}/{max_quotes} extraite",
                    "current": i + 1,
                    "total": max_quotes
                })

            # Phase 2: Download images
            if include_images:
                await broadcast_update("progress", {
                    "message": "Phase 2: Téléchargement des images...",
                    "current": len(quotes),
                    "total": max_quotes
                })

                image_results = await scraper.download_images(quotes)
                successful_downloads = len([r for r in image_results if r.get("success")])
                scraping_state["stats"]["images"] = successful_downloads

                await broadcast_update("image_downloaded", {
                    "message": f"{successful_downloads}/{len(quotes)} images téléchargées"
                })

            # Phase 3: Store in database
            if store_in_database and storage:
                await broadcast_update("progress", {
                    "message": "Phase 3: Stockage en base de données...",
                    "current": len(quotes),
                    "total": max_quotes
                })

                try:
                    stored_quotes = await storage.store_quotes_batch(quotes)
                    logger.info(f"Stored {len(stored_quotes)} quotes in database")

                    await broadcast_update("database_stored", {
                        "message": f"{len(stored_quotes)} citations stockées en base"
                    })

                except Exception as e:
                    logger.error(f"Error storing in database: {e}")
                    scraping_state["stats"]["errors"] += 1
                    await broadcast_update("error", {
                        "message": f"Erreur stockage DB: {str(e)}"
                    })

            # Final state
            scraping_state["status"] = "completed"
            scraping_state["stats"]["elapsed"] = int(time.time() - scraping_state["start_time"])

            await broadcast_update("completed", {
                "message": "Scraping terminé avec succès!",
                "stats": scraping_state["stats"],
                "progress": {"current": len(quotes), "total": max_quotes}
            })

            logger.info(f"Scraping completed successfully. Stats: {scraping_state['stats']}")

    except Exception as e:
        logger.error(f"API scraping workflow error: {e}")
        scraping_state["status"] = "error"
        scraping_state["stats"]["errors"] += 1

        await broadcast_update("error", {
            "message": f"Erreur: {str(e)}",
            "status": "error"
        })

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