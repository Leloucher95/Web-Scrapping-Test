"""
Simple test script to verify Supabase connection.
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def test_basic_connection():
    """Test basic Supabase connection."""
    print("🔗 Testing basic Supabase connection...")

    # Get credentials
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')

    if not url or not key:
        print("❌ Missing Supabase credentials in .env file")
        return False

    print(f"📍 URL: {url}")
    print(f"🔑 Key: {key[:20]}...")

    try:
        # Create client
        supabase = create_client(url, key)
        print("✅ Supabase client created successfully!")

        # Try to list tables (this will fail if no tables exist, but connection is working)
        try:
            result = supabase.table('quotes').select('*').limit(1).execute()
            print("✅ Successfully connected to quotes table!")
            print(f"📊 Data: {result.data}")
        except Exception as e:
            if "Could not find the table" in str(e):
                print("⚠️  Table 'quotes' does not exist yet - need to run SQL setup script")
                print("✅ But connection to Supabase is working!")
                return True
            else:
                print(f"❌ Table access error: {e}")
                return False

        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_basic_connection()