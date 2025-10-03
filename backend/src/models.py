from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class ScrapingStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

class QuoteModel(BaseModel):
    id: Optional[str] = None
    job_id: Optional[str] = None
    text: str
    author: str
    link: Optional[str] = ""
    image_url: Optional[str] = ""
    created_at: Optional[datetime] = None

class ScrapingJobModel(BaseModel):
    id: Optional[str] = None
    topic: str
    status: ScrapingStatus = ScrapingStatus.PENDING
    user_id: Optional[str] = None
    total_quotes: int = 0
    processed_quotes: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ScrapingRequest(BaseModel):
    topic: str
    max_pages: int = 5
    user_id: Optional[str] = None

class ScrapingResponse(BaseModel):
    job_id: str
    status: ScrapingStatus
    message: str

class QuotesResponse(BaseModel):
    quotes: List[QuoteModel]
    total: int
    page: int
    per_page: int

class JobStatistics(BaseModel):
    job_id: str
    topic: str
    status: ScrapingStatus
    total_quotes: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    duration: Optional[str] = None

class ExportRequest(BaseModel):
    format: str = "json"  # json or csv
    job_id: str

class ProgressUpdate(BaseModel):
    job_id: str
    status: ScrapingStatus
    current_page: int
    total_pages: int
    quotes_found: int
    message: str