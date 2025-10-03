from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

router = APIRouter()

# Models
class ScrapingRequest(BaseModel):
    topic: str

class ScrapingResponse(BaseModel):
    job_id: str
    topic: str
    status: str
    message: str

class JobStatus(BaseModel):
    job_id: str
    topic: str
    status: str
    total_items: int
    processed_items: int
    created_at: datetime
    error_message: Optional[str] = None

# In-memory storage for demo (will be replaced with Supabase)
jobs_storage = {}

@router.post("/scrape/start", response_model=ScrapingResponse)
async def start_scraping(request: ScrapingRequest):
    """Start a new scraping job for the given topic"""
    job_id = str(uuid.uuid4())

    # Create job record
    job_data = {
        "job_id": job_id,
        "topic": request.topic,
        "status": "pending",
        "total_items": 0,
        "processed_items": 0,
        "created_at": datetime.now(),
        "error_message": None
    }

    jobs_storage[job_id] = job_data

    # TODO: Start actual scraping process here
    # For now, just return success response

    return ScrapingResponse(
        job_id=job_id,
        topic=request.topic,
        status="pending",
        message=f"Scraping job started for topic: {request.topic}"
    )

@router.get("/scrape/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get the status of a scraping job"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")

    job_data = jobs_storage[job_id]
    return JobStatus(**job_data)

@router.post("/scrape/stop/{job_id}")
async def stop_scraping(job_id: str):
    """Stop a running scraping job"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")

    job_data = jobs_storage[job_id]
    if job_data["status"] not in ["pending", "running"]:
        raise HTTPException(status_code=400, detail="Job cannot be stopped")

    job_data["status"] = "stopped"
    jobs_storage[job_id] = job_data

    return {"message": f"Job {job_id} stopped successfully"}

@router.get("/quotes")
async def get_quotes(topic: Optional[str] = None, limit: int = 50):
    """Get quotes from database (placeholder)"""
    # TODO: Query Supabase for quotes
    return {
        "quotes": [],
        "total": 0,
        "topic": topic,
        "message": "Quotes endpoint - Supabase integration pending"
    }