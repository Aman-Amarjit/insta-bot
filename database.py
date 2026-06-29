from supabase import create_client, Client
import config

class Database:
    def __init__(self):
        self.url = config.SUPABASE_URL
        self.key = config.SUPABASE_KEY
        self.client = None
        
        if not self.url or not self.key:
            print("⚠️ Database warning: SUPABASE_URL or SUPABASE_KEY is missing in configuration.")
            print("Running database operations in Mock Mode.")
        else:
            try:
                self.client = create_client(self.url, self.key)
                print("✅ Supabase client initialized successfully.")
            except Exception as e:
                print(f"❌ Failed to initialize Supabase client: {e}")
                print("Falling back to Mock database mode.")

    def get_recent_facts(self, limit: int = 100) -> list:
        """
        Retrieves the last N fact texts from the database for duplicate check.
        """
        if not self.client:
            print("Mock DB: Returning empty list for recent facts.")
            return []
            
        try:
            # Query posts table, selecting only fact_text
            response = self.client.table("posts") \
                .select("fact_text") \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            # Extract list of facts from response data
            records = response.data or []
            return [r.get("fact_text") for r in records if r.get("fact_text")]
        except Exception as e:
            print(f"⚠️ Error fetching recent facts from Supabase: {e}")
            return []

    def get_recent_categories(self, limit: int = 10) -> list:
        """
        Retrieves the last N categories posted for rotation variety balance.
        """
        if not self.client:
            print("Mock DB: Returning empty list for recent categories.")
            return []
            
        try:
            response = self.client.table("posts") \
                .select("category") \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            records = response.data or []
            return [r.get("category") for r in records if r.get("category")]
        except Exception as e:
            print(f"⚠️ Error fetching recent categories from Supabase: {e}")
            return []

    def save_post(self, fact_text: str, caption: str, category: str, instagram_id: str = None) -> bool:
        """
        Saves a successfully posted fact to the Supabase database.
        """
        if not self.client:
            print(f"Mock DB: Saved post '{fact_text[:30]}' to console log.")
            return True
            
        try:
            data = {
                "fact_text": fact_text,
                "caption": caption,
                "category": category,
                "instagram_id": instagram_id
            }
            response = self.client.table("posts").insert(data).execute()
            if response.data:
                print("💾 Saved post metadata to Supabase successfully.")
                return True
            else:
                print(f"⚠️ Insertion response was empty: {response}")
                return False
        except Exception as e:
            print(f"❌ Error inserting post to Supabase: {e}")
            return False
