"""
Supabase Client Singleton
Manages connection to Supabase database
"""
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    """Singleton class for Supabase connection"""
    _instance = None
    _client: Client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Supabase client"""
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        
        self._client = create_client(url, key)
    
    @property
    def client(self) -> Client:
        """Get Supabase client instance"""
        return self._client


# Create a global instance
supabase_client = SupabaseClient().client
