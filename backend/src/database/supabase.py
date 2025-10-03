from supabase import create_client, Client
from src.core.config import settings
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )

    async def create_scraping_job(self, topic: str, user_id: Optional[str] = None) -> str:
        """Create a new scraping job and return its ID"""
        job_id = str(uuid.uuid4())

        job_data = {
            "id": job_id,
            "topic": topic,
            "status": "running",
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "total_quotes": 0,
            "processed_quotes": 0
        }

        try:
            response = self.client.table("scraping_jobs").insert(job_data).execute()
            logger.info(f"Created scraping job: {job_id}")
            return job_id
        except Exception as e:
            logger.error(f"Error creating scraping job: {str(e)}")
            raise

    async def update_scraping_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Update a scraping job"""
        try:
            updates["updated_at"] = datetime.utcnow().isoformat()
            response = self.client.table("scraping_jobs").update(updates).eq("id", job_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating scraping job {job_id}: {str(e)}")
            return False

    async def get_scraping_job(self, job_id: str) -> Optional[Dict]:
        """Get scraping job by ID"""
        try:
            response = self.client.table("scraping_jobs").select("*").eq("id", job_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting scraping job {job_id}: {str(e)}")
            return None

    async def save_quotes(self, job_id: str, quotes: List[Dict]) -> bool:
        """Save quotes to database"""
        try:
            # Prepare quotes data
            quotes_data = []
            for quote in quotes:
                quote_data = {
                    "id": str(uuid.uuid4()),
                    "job_id": job_id,
                    "text": quote.get("text", ""),
                    "author": quote.get("author", ""),
                    "link": quote.get("link", ""),
                    "image_url": quote.get("image_url", ""),
                    "created_at": datetime.utcnow().isoformat()
                }
                quotes_data.append(quote_data)

            # Insert quotes in batches
            batch_size = 100
            for i in range(0, len(quotes_data), batch_size):
                batch = quotes_data[i:i + batch_size]
                response = self.client.table("quotes").insert(batch).execute()
                logger.info(f"Saved batch of {len(batch)} quotes")

            logger.info(f"Successfully saved {len(quotes)} quotes for job {job_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving quotes for job {job_id}: {str(e)}")
            return False

    async def get_quotes_by_job(self, job_id: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get quotes for a specific job"""
        try:
            response = (
                self.client.table("quotes")
                .select("*")
                .eq("job_id", job_id)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error getting quotes for job {job_id}: {str(e)}")
            return []

    async def get_all_jobs(self, user_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get all scraping jobs, optionally filtered by user"""
        try:
            query = self.client.table("scraping_jobs").select("*")

            if user_id:
                query = query.eq("user_id", user_id)

            response = query.order("created_at", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting jobs: {str(e)}")
            return []

    async def delete_job(self, job_id: str) -> bool:
        """Delete a scraping job and its quotes"""
        try:
            # Delete quotes first
            self.client.table("quotes").delete().eq("job_id", job_id).execute()

            # Delete job
            self.client.table("scraping_jobs").delete().eq("id", job_id).execute()

            logger.info(f"Deleted job {job_id} and its quotes")
            return True
        except Exception as e:
            logger.error(f"Error deleting job {job_id}: {str(e)}")
            return False

    async def export_quotes_to_json(self, job_id: str) -> Optional[List[Dict]]:
        """Export all quotes for a job as JSON"""
        try:
            all_quotes = []
            offset = 0
            limit = 1000

            while True:
                quotes = await self.get_quotes_by_job(job_id, limit, offset)
                if not quotes:
                    break
                all_quotes.extend(quotes)
                offset += limit

            return all_quotes
        except Exception as e:
            logger.error(f"Error exporting quotes for job {job_id}: {str(e)}")
            return None

    async def get_job_statistics(self, job_id: str) -> Dict[str, Any]:
        """Get statistics for a job"""
        try:
            # Get job info
            job = await self.get_scraping_job(job_id)
            if not job:
                return {}

            # Get quote count
            response = (
                self.client.table("quotes")
                .select("id", count="exact")
                .eq("job_id", job_id)
                .execute()
            )

            quote_count = len(response.data) if response.data else 0

            return {
                "job_id": job_id,
                "topic": job.get("topic", ""),
                "status": job.get("status", ""),
                "total_quotes": quote_count,
                "created_at": job.get("created_at", ""),
                "updated_at": job.get("updated_at", ""),
                "duration": self._calculate_duration(job.get("created_at"), job.get("updated_at"))
            }

        except Exception as e:
            logger.error(f"Error getting statistics for job {job_id}: {str(e)}")
            return {}

    def _calculate_duration(self, start_time: str, end_time: str) -> Optional[str]:
        """Calculate duration between start and end time"""
        try:
            if not start_time or not end_time:
                return None

            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            duration = end - start

            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"

        except Exception:
            return None

# Global instance
supabase_client = SupabaseClient()