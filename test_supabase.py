import os
import sys
from database import Database

def test_supabase_connection():
    print("🧪 Testing Supabase Connection...")
    
    # Instantiate DB
    db = Database()
    
    # Check if client was loaded (if mock, test_supabase will notify)
    if not db.client:
        print("ℹ️ database.py is running in Mock Mode (no SUPABASE_URL/KEY env vars).")
        print("Testing mock database operations...")
        recent = db.get_recent_facts(limit=10)
        assert isinstance(recent, list), "Mock recent facts must be a list"
        
        saved = db.save_post("Test fact", "Test caption", "science")
        assert saved is True, "Mock save_post should return True"
        
        print("✅ Mock Database tests passed!")
        return True
        
    try:
        # Try a simple select to verify keys
        print("Fetching recent facts...")
        recent = db.get_recent_facts(limit=5)
        print(f"Recent facts fetched: {recent}")
        assert isinstance(recent, list)
        
        print("✅ Supabase integration tests passed!")
        return True
    except Exception as e:
        print(f"❌ Supabase test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    sys.exit(0 if success else 1)
