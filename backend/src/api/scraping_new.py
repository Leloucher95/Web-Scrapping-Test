from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import asyncio
import logging
from src.models import (
    ScrapingRequest, ScrapingResponse, QuotesResponse, JobStatistics,
    QuoteModel, ScrapingJobModel, ScrapingStatus, ExportRequest
)
from src.scraper.brainyquote import BrainyQuoteScraper
from src.database.supabase import supabase_client

router = APIRouter()
logger = logging.getLogger(__name__)

async def background_scraping_task(job_id: str, topic: str, max_pages: int):
    """Background task to perform scraping"""
    try:
        logger.info(f"Starting background scraping for job {job_id}")

        # Update job status to running
        await supabase_client.update_scraping_job(job_id, {
            "status": ScrapingStatus.RUNNING.value
        })

        # Start scraping
        async with BrainyQuoteScraper() as scraper:
            quotes = await scraper.scrape_topic(topic, max_pages)

            # Save quotes to database
            if quotes:
                success = await supabase_client.save_quotes(job_id, quotes)
                if success:
                    await supabase_client.update_scraping_job(job_id, {
                        "status": ScrapingStatus.COMPLETED.value,
                        "total_quotes": len(quotes),
                        "processed_quotes": len(quotes)
                    })
                    logger.info(f"Scraping job {job_id} completed successfully with {len(quotes)} quotes")
                else:
                    raise Exception("Failed to save quotes to database")
            else:
                await supabase_client.update_scraping_job(job_id, {
                    "status": ScrapingStatus.COMPLETED.value,
                    "total_quotes": 0,
                    "processed_quotes": 0
                })
                logger.warning(f"Scraping job {job_id} completed but no quotes found")

    except Exception as e:
        logger.error(f"Scraping job {job_id} failed: {str(e)}")
        await supabase_client.update_scraping_job(job_id, {
            "status": ScrapingStatus.FAILED.value,
            "error_message": str(e)
        })

@router.post("/scrape/start", response_model=ScrapingResponse)
async def start_scraping(request: ScrapingRequest, background_tasks: BackgroundTasks):
    """Start a new scraping job for the given topic"""
    try:
        # Create scraping job in database
        job_id = await supabase_client.create_scraping_job(
            topic=request.topic,
            user_id=request.user_id
        )

        # Start background scraping task
        background_tasks.add_task(
            background_scraping_task,
            job_id,
            request.topic,
            request.max_pages
        )

        return ScrapingResponse(
            job_id=job_id,
            status=ScrapingStatus.PENDING,
            message=f"Scraping job started for topic: {request.topic}"
        )

    except Exception as e:
        logger.error(f"Failed to start scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start scraping: {str(e)}")

@router.get("/scrape/status/{job_id}", response_model=ScrapingJobModel)
async def get_scraping_status(job_id: str):
    """Get the status of a scraping job"""
    try:
        job = await supabase_client.get_scraping_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return ScrapingJobModel(**job)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@router.post("/scrape/stop/{job_id}")
async def stop_scraping(job_id: str):
    """Stop a running scraping job"""
    try:
        job = await supabase_client.get_scraping_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if job["status"] not in [ScrapingStatus.RUNNING.value, ScrapingStatus.PENDING.value]:
            raise HTTPException(status_code=400, detail="Job is not running")

        # Update job status to stopped
        success = await supabase_client.update_scraping_job(job_id, {
            "status": ScrapingStatus.STOPPED.value
        })

        if success:
            return {"message": "Scraping job stopped successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to stop scraping job")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop job: {str(e)}")

@router.get("/jobs", response_model=List[ScrapingJobModel])
async def get_all_jobs(user_id: str = None, limit: int = 50):
    """Get all scraping jobs"""
    try:
        jobs = await supabase_client.get_all_jobs(user_id, limit)
        return [ScrapingJobModel(**job) for job in jobs]

    except Exception as e:
        logger.error(f"Failed to get jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get jobs: {str(e)}")

@router.get("/quotes/{job_id}", response_model=QuotesResponse)
async def get_quotes(job_id: str, page: int = 1, per_page: int = 50):
    """Get quotes for a specific job"""
    try:
        offset = (page - 1) * per_page
        quotes_data = await supabase_client.get_quotes_by_job(job_id, per_page, offset)

        quotes = [QuoteModel(**quote) for quote in quotes_data]

        # Get total count for pagination
        job = await supabase_client.get_scraping_job(job_id)
        total = job.get("total_quotes", 0) if job else 0

        return QuotesResponse(
            quotes=quotes,
            total=total,
            page=page,
            per_page=per_page
        )

    except Exception as e:
        logger.error(f"Failed to get quotes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get quotes: {str(e)}")

@router.get("/jobs/{job_id}/statistics", response_model=JobStatistics)
async def get_job_statistics(job_id: str):
    """Get statistics for a specific job"""
    try:
        stats = await supabase_client.get_job_statistics(job_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Job not found")

        return JobStatistics(**stats)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get job statistics: {str(e)}")

@router.post("/jobs/{job_id}/export")
async def export_job_data(job_id: str, export_request: ExportRequest):
    """Export job data as JSON or CSV"""
    try:
        if export_request.format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")

        quotes = await supabase_client.export_quotes_to_json(job_id)
        if quotes is None:
            raise HTTPException(status_code=404, detail="Job not found or no quotes available")

        if export_request.format == "json":
            return {"data": quotes, "format": "json", "count": len(quotes)}
        else:
            # Convert to CSV format
            import csv
            import io

            if not quotes:
                return {"data": "", "format": "csv", "count": 0}

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["text", "author", "link", "image_url", "created_at"])
            writer.writeheader()

            for quote in quotes:
                writer.writerow({
                    "text": quote.get("text", ""),
                    "author": quote.get("author", ""),
                    "link": quote.get("link", ""),
                    "image_url": quote.get("image_url", ""),
                    "created_at": quote.get("created_at", "")
                })

            csv_data = output.getvalue()
            output.close()

            return {"data": csv_data, "format": "csv", "count": len(quotes)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export job data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export job data: {str(e)}")

@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a scraping job and all its quotes"""
    try:
        success = await supabase_client.delete_job(job_id)
        if success:
            return {"message": "Job deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete job")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete job: {str(e)}")

@router.get("/test/{topic}")
async def test_scraping(topic: str):
    """Test endpoint to scrape a few quotes"""
    try:
        async with BrainyQuoteScraper() as scraper:
            quotes = await scraper.test_scraping(topic, limit=3)
            return {
                "topic": topic,
                "quotes_found": len(quotes),
                "quotes": quotes
            }
    except Exception as e:
        logger.error(f"Test scraping failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test scraping failed: {str(e)}")