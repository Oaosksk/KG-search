from supabase import create_client, Client
from ..core.config import settings
from typing import Optional

class SupabaseClient:
    def __init__(self):
        self.client: Optional[Client] = None
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                print("✅ Supabase connected")
            except Exception as e:
                print(f"⚠️ Supabase connection failed: {e}")
    
    @property
    def enabled(self):
        return self.client is not None

supabase_client = SupabaseClient()
