"""
VARIOSYNC Supabase Client Module
Handles Supabase database and storage integration.
"""
import os
from typing import Any, Dict, List, Optional

from logger import get_logger
from supabase_operations import SupabaseOperations

logger = get_logger()

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("Supabase library not available. Install with: pip install supabase")


class SupabaseClient:
    """Client for Supabase operations."""
    
    def __init__(self, url: str, key: str, service_role_key: Optional[str] = None):
        """
        Initialize Supabase client.
        
        Args:
            url: Supabase project URL
            key: Supabase anon key
            service_role_key: Optional service role key for admin operations
        """
        if not SUPABASE_AVAILABLE:
            raise ImportError("Supabase library not installed")
        
        self.url = url
        self.key = key
        self.service_role_key = service_role_key
        
        # Create client with anon key
        self.client: Client = create_client(url, key)
        
        # Create admin client if service role key provided
        self.admin_client: Optional[Client] = None
        if service_role_key:
            self.admin_client = create_client(url, service_role_key)
        
        logger.info(f"Initialized Supabase client for {url}")
    
        self.operations = SupabaseOperations(self.client)
    
    def get_user_hours(self, user_id: str) -> Optional[float]:
        """Get remaining hours for a user."""
        return self.operations.get_user_hours(user_id)
    
    def consume_hours(self, user_id: str, hours: float) -> bool:
        """Consume hours for a user."""
        return self.operations.consume_hours(user_id, hours)
    
    def add_hours(self, user_id: str, hours: float) -> bool:
        """Add hours to a user account."""
        return self.operations.add_hours(user_id, hours)
    
    def save_time_series_data(self, data: Dict[str, Any]) -> bool:
        """Save time-series data to Supabase."""
        return self.operations.save_time_series_data(data)
    
    def query_time_series(
        self,
        series_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Query time-series data."""
        return self.operations.query_time_series(series_id, start_time, end_time, limit)
    
    def test_connection(self) -> bool:
        """Test Supabase connection."""
        return self.operations.test_connection()


class SupabaseClientFactory:
    """Factory for creating Supabase clients."""
    
    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> Optional[SupabaseClient]:
        """
        Create Supabase client from configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            SupabaseClient instance or None if config invalid
        """
        if not SUPABASE_AVAILABLE:
            logger.error("Supabase library not available")
            return None
        
        if "Supabase" not in config:
            logger.warning("Supabase configuration not found")
            return None
        
        supabase_config = config["Supabase"]
        
        if "url" not in supabase_config or "key" not in supabase_config:
            logger.error("Invalid Supabase configuration: missing url or key")
            return None
        
        url = supabase_config["url"]
        key = supabase_config["key"]
        service_role_key = supabase_config.get("service_role_key")
        
        try:
            return SupabaseClient(url, key, service_role_key)
        except Exception as e:
            logger.error(f"Error creating Supabase client: {e}")
            return None
    
    @staticmethod
    def create_from_env() -> Optional[SupabaseClient]:
        """
        Create Supabase client from environment variables.
        
        Returns:
            SupabaseClient instance or None if env vars not set
        """
        if not SUPABASE_AVAILABLE:
            return None
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            logger.warning("Supabase environment variables not set")
            return None
        
        service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        try:
            return SupabaseClient(url, key, service_role_key)
        except Exception as e:
            logger.error(f"Error creating Supabase client from env: {e}")
            return None
