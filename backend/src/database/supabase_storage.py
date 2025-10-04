"""
Database operations for storing quotes and images in Supabase.
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
import json
from datetime import datetime
import hashlib
import os

try:
    from supabase import create_client, Client
    import httpx
except ImportError:
    raise ImportError("Please install supabase and httpx: pip install supabase httpx")

logger = logging.getLogger(__name__)

class SupabaseQuoteStorage:
    """Handles storing quotes and images in Supabase."""

    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """Initialize Supabase client."""
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_ANON_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and key must be provided via parameters or environment variables")

        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.quotes_table = "quotes"
        self.storage_bucket = "quote-images"

    async def setup_database(self):
        """Create the quotes table if it doesn't exist."""
        try:
            # Test connection
            result = self.supabase.table(self.quotes_table).select("*").limit(1).execute()
            logger.info("✅ Connected to Supabase successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Supabase: {e}")
            return False

    async def setup_storage(self):
        """Create the storage bucket if it doesn't exist."""
        try:
            # Try to get bucket info
            buckets = self.supabase.storage.list_buckets()
            bucket_names = [bucket.name for bucket in buckets]

            if self.storage_bucket not in bucket_names:
                # Create bucket
                result = self.supabase.storage.create_bucket(
                    self.storage_bucket,
                    options={"public": True}
                )
                logger.info(f"✅ Created storage bucket: {self.storage_bucket}")
            else:
                logger.info(f"✅ Storage bucket exists: {self.storage_bucket}")
            return True
        except Exception as e:
            logger.warning(f"⚠️  Storage bucket creation issue: {e}")
            # Check if bucket exists despite the error
            try:
                buckets = self.supabase.storage.list_buckets()
                bucket_names = [bucket.name for bucket in buckets]
                if self.storage_bucket in bucket_names:
                    logger.info(f"✅ Storage bucket exists: {self.storage_bucket}")
                    return True
                else:
                    logger.error(f"❌ Bucket {self.storage_bucket} does not exist and cannot be created")
                    logger.info("💡 Please create the bucket manually in Supabase Dashboard:")
                    logger.info(f"   1. Go to Storage in Supabase Dashboard")
                    logger.info(f"   2. Create a new bucket named '{self.storage_bucket}'")
                    logger.info(f"   3. Make it public")
                    return False
            except Exception as e2:
                logger.error(f"❌ Failed to check bucket existence: {e2}")
                return False

    def generate_image_filename(self, author: str, index: int, original_url: str) -> str:
        """Generate a unique filename for the image."""
        # Create a hash from the original URL for uniqueness
        url_hash = hashlib.md5(original_url.encode()).hexdigest()[:8]

        # Clean author name for filename
        clean_author = "".join(c if c.isalnum() or c in " -_" else "" for c in author)
        clean_author = clean_author.replace(" ", "_").strip("_")

        return f"quote_{clean_author}_{index}_{url_hash}.jpg"

    async def upload_image_to_supabase(self, image_data: Dict, quote_id: str) -> Optional[str]:
        """Upload image to Supabase storage."""
        try:
            local_path = image_data.get('local_path')
            if not local_path or not Path(local_path).exists():
                logger.warning(f"⚠️  Image file not found: {local_path}")
                return None

            # Generate storage filename
            filename = image_data.get('filename')
            if not filename:
                filename = f"quote_{quote_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

            # Read image data
            with open(local_path, 'rb') as f:
                image_bytes = f.read()

            # Upload to Supabase storage
            result = self.supabase.storage.from_(self.storage_bucket).upload(
                filename,
                image_bytes,
                file_options={"content-type": image_data.get('content_type', 'image/jpeg')}
            )

            if result:
                # Get public URL
                public_url = self.supabase.storage.from_(self.storage_bucket).get_public_url(filename)
                logger.info(f"✅ Uploaded image: {filename}")
                return public_url
            else:
                logger.error(f"❌ Failed to upload image: {filename}")
                return None

        except Exception as e:
            logger.error(f"❌ Error uploading image: {e}")
            return None

    async def store_quote(self, quote_data: Dict) -> Optional[str]:
        """Store a single quote in Supabase."""
        try:
            # Prepare quote data for database
            db_quote = {
                "text": quote_data.get('text'),
                "author": quote_data.get('author'),
                "source_url": quote_data.get('link'),
                "image_url": quote_data.get('image_url'),
                "category": quote_data.get('category', 'general'),
                "extracted_at": datetime.now().isoformat(),
                "metadata": {
                    "index": quote_data.get('index'),
                    "original_image_url": quote_data.get('image_url'),
                    "image_size": quote_data.get('image_data', {}).get('size'),
                    "extraction_method": "hybrid_scraper"
                }
            }

            # Insert quote into database
            result = self.supabase.table(self.quotes_table).insert(db_quote).execute()

            if result.data:
                quote_id = result.data[0]['id']
                logger.info(f"✅ Stored quote: {quote_id} - {quote_data.get('author')}")

                # Upload image if available
                if quote_data.get('image_data'):
                    image_url = await self.upload_image_to_supabase(
                        quote_data['image_data'],
                        str(quote_id)
                    )

                    if image_url:
                        # Update quote with Supabase image URL
                        update_result = self.supabase.table(self.quotes_table).update({
                            "supabase_image_url": image_url
                        }).eq('id', quote_id).execute()

                        if update_result.data:
                            logger.info(f"✅ Updated quote {quote_id} with Supabase image URL")

                return str(quote_id)
            else:
                logger.error("❌ Failed to insert quote")
                return None

        except Exception as e:
            logger.error(f"❌ Error storing quote: {e}")
            return None

    async def store_quotes_batch(self, quotes: List[Dict]) -> Dict[str, Any]:
        """Store multiple quotes in Supabase."""
        results = {
            "stored_quotes": 0,
            "uploaded_images": 0,
            "errors": 0,
            "quote_ids": []
        }

        logger.info(f"🚀 Starting batch storage of {len(quotes)} quotes to Supabase...")

        for i, quote in enumerate(quotes, 1):
            try:
                logger.info(f"📝 Processing quote {i}/{len(quotes)}: {quote.get('author', 'Unknown')}")

                quote_id = await self.store_quote(quote)
                if quote_id:
                    results["stored_quotes"] += 1
                    results["quote_ids"].append(quote_id)

                    if quote.get('image_data'):
                        results["uploaded_images"] += 1
                else:
                    results["errors"] += 1

            except Exception as e:
                logger.error(f"❌ Error processing quote {i}: {e}")
                results["errors"] += 1

        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 SUPABASE STORAGE SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"✅ Quotes stored: {results['stored_quotes']}/{len(quotes)}")
        logger.info(f"🖼️  Images uploaded: {results['uploaded_images']}")
        logger.info(f"❌ Errors: {results['errors']}")
        logger.info(f"📈 Success rate: {results['stored_quotes']/len(quotes)*100:.1f}%")
        logger.info(f"{'='*60}")

        return results

    async def get_quotes_by_author(self, author: str) -> List[Dict]:
        """Retrieve quotes by author."""
        try:
            result = self.supabase.table(self.quotes_table).select("*").ilike('author', f'%{author}%').execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"❌ Error retrieving quotes by author: {e}")
            return []

    async def get_recent_quotes(self, limit: int = 10) -> List[Dict]:
        """Retrieve recent quotes."""
        try:
            result = self.supabase.table(self.quotes_table).select("*").order('extracted_at', desc=True).limit(limit).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"❌ Error retrieving recent quotes: {e}")
            return []

    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            # Total quotes
            total_result = self.supabase.table(self.quotes_table).select("id", count="exact").execute()
            total_quotes = total_result.count if total_result.count else 0

            # Quotes with images
            images_result = self.supabase.table(self.quotes_table).select("id", count="exact").not_.is_("supabase_image_url", "null").execute()
            quotes_with_images = images_result.count if images_result.count else 0

            # Unique authors
            authors_result = self.supabase.table(self.quotes_table).select("author").execute()
            unique_authors = len(set(row['author'] for row in authors_result.data)) if authors_result.data else 0

            return {
                "total_quotes": total_quotes,
                "quotes_with_images": quotes_with_images,
                "unique_authors": unique_authors,
                "image_percentage": (quotes_with_images / total_quotes * 100) if total_quotes > 0 else 0
            }
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {"error": str(e)}