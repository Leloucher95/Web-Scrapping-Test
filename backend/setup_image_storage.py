"""
Create storage bucket and upload images to Supabase.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

async def setup_image_storage():
    """Setup image storage bucket and upload images."""
    logger.info("🖼️  Setting up image storage...")

    # Get credentials
    url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_KEY')

    if not url or not service_key:
        logger.error("❌ Missing Supabase credentials")
        return False

    try:
        # Create client with service role key
        supabase = create_client(url, service_key)

        # Check if bucket exists
        bucket_name = "quote-images"

        try:
            buckets = supabase.storage.list_buckets()
            bucket_names = [bucket.name for bucket in buckets]

            if bucket_name not in bucket_names:
                logger.info(f"📦 Creating bucket: {bucket_name}")

                # Create bucket
                result = supabase.storage.create_bucket(bucket_name)
                logger.info(f"✅ Created bucket: {bucket_name}")
            else:
                logger.info(f"✅ Bucket already exists: {bucket_name}")

        except Exception as e:
            logger.warning(f"⚠️  Bucket creation issue: {e}")
            # Check if bucket exists despite error
            buckets = supabase.storage.list_buckets()
            bucket_names = [bucket.name for bucket in buckets]
            if bucket_name in bucket_names:
                logger.info(f"✅ Bucket exists: {bucket_name}")
            else:
                logger.error(f"❌ Need to create bucket manually in Supabase dashboard")
                return False

        # Load quotes data
        results_file = Path("enhanced_scraping_results_20251004_185159.json")
        if not results_file.exists():
            logger.error(f"❌ Results file not found: {results_file}")
            return False

        with open(results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)

        logger.info(f"📊 Found {len(results)} quotes with potential images")

        # Upload images
        uploaded_count = 0
        updated_quotes = 0

        for i, quote in enumerate(results, 1):
            try:
                image_data = quote.get('image_data')
                if not image_data:
                    logger.info(f"⚠️  {i}/{len(results)} No image data for: {quote.get('author')}")
                    continue

                local_path = image_data.get('local_path')
                if not local_path or not Path(local_path).exists():
                    logger.warning(f"⚠️  {i}/{len(results)} Image file not found: {local_path}")
                    continue

                # Generate filename
                filename = image_data.get('filename', f"quote_{i}_{quote.get('author', 'unknown').replace(' ', '_')}.jpg")

                logger.info(f"📤 {i}/{len(results)} Uploading: {filename}")

                # Read image file
                with open(local_path, 'rb') as f:
                    image_bytes = f.read()

                # Upload to Supabase storage
                upload_result = supabase.storage.from_(bucket_name).upload(
                    filename,
                    image_bytes,
                    file_options={"content-type": image_data.get('content_type', 'image/jpeg')}
                )

                if upload_result:
                    # Get public URL
                    public_url = supabase.storage.from_(bucket_name).get_public_url(filename)

                    logger.info(f"✅ {i}/{len(results)} Uploaded: {filename}")
                    uploaded_count += 1

                    # Update quote in database with Supabase image URL
                    # Find quote by author and text
                    search_result = supabase.table("quotes").select("id").eq("author", quote.get('author')).eq("text", quote.get('text')).execute()

                    if search_result.data:
                        quote_id = search_result.data[0]['id']

                        update_result = supabase.table("quotes").update({
                            "supabase_image_url": public_url
                        }).eq("id", quote_id).execute()

                        if update_result.data:
                            logger.info(f"🔗 {i}/{len(results)} Updated quote {quote_id} with image URL")
                            updated_quotes += 1
                        else:
                            logger.warning(f"⚠️  {i}/{len(results)} Failed to update quote with image URL")
                    else:
                        logger.warning(f"⚠️  {i}/{len(results)} Quote not found in database")
                else:
                    logger.error(f"❌ {i}/{len(results)} Failed to upload: {filename}")

            except Exception as e:
                if "already exists" in str(e):
                    logger.info(f"ℹ️  {i}/{len(results)} Image already exists: {filename}")
                    uploaded_count += 1
                else:
                    logger.error(f"❌ {i}/{len(results)} Upload error: {e}")

        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"🖼️  IMAGE STORAGE SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"📤 Images uploaded: {uploaded_count}/{len(results)}")
        logger.info(f"🔗 Quotes updated with image URLs: {updated_quotes}")
        logger.info(f"📈 Upload success rate: {uploaded_count/len(results)*100:.1f}%")

        # Final database stats
        stats_result = supabase.table("quotes").select("id", count="exact").execute()
        total_quotes = stats_result.count

        images_result = supabase.table("quotes").select("id", count="exact").not_.is_("supabase_image_url", "null").execute()
        quotes_with_images = images_result.count

        logger.info(f"\n📊 Final database stats:")
        logger.info(f"   Total quotes: {total_quotes}")
        logger.info(f"   Quotes with Supabase images: {quotes_with_images}")
        logger.info(f"   Image coverage: {quotes_with_images/total_quotes*100:.1f}%")
        logger.info(f"{'='*60}")

        return True

    except Exception as e:
        logger.error(f"❌ Storage setup error: {e}")
        return False

def main():
    """Main function."""
    logger.info("🚀 Setting up Supabase Image Storage")

    try:
        success = asyncio.run(setup_image_storage())
        if success:
            logger.info("✅ Image storage setup completed!")
        else:
            logger.error("❌ Image storage setup failed!")

    except KeyboardInterrupt:
        logger.info("⏹️  Setup interrupted by user")
    except Exception as e:
        logger.error(f"💥 Setup error: {e}")

if __name__ == "__main__":
    main()