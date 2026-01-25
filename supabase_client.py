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
        logger.debug("[SupabaseClient.__init__] Initializing Supabase client")

        if not SUPABASE_AVAILABLE:
            logger.error("[SupabaseClient.__init__] Supabase library not installed")
            raise ImportError("Supabase library not installed")

        # Validate URL
        if not url:
            logger.error("[SupabaseClient.__init__] Empty URL provided")
            raise ValueError("Supabase URL cannot be empty")

        if not url.startswith("http"):
            logger.error(f"[SupabaseClient.__init__] Invalid URL format: {url}")
            raise ValueError("Supabase URL must start with http:// or https://")

        # Validate key
        if not key:
            logger.error("[SupabaseClient.__init__] Empty anon key provided")
            raise ValueError("Supabase anon key cannot be empty")

        self.url = url
        self.key = key
        self.service_role_key = service_role_key

        logger.debug(f"[SupabaseClient.__init__] URL: {url}")
        logger.debug(f"[SupabaseClient.__init__] Anon key configured: {bool(key)}")
        logger.debug(f"[SupabaseClient.__init__] Service role key configured: {bool(service_role_key)}")

        # Create client with anon key
        try:
            self.client: Client = create_client(url, key)
            logger.debug("[SupabaseClient.__init__] Created anon client")
        except Exception as e:
            logger.error(f"[SupabaseClient.__init__] Failed to create anon client: {e}", exc_info=True)
            raise

        # Create admin client if service role key provided
        self.admin_client: Optional[Client] = None
        if service_role_key:
            try:
                self.admin_client = create_client(url, service_role_key)
                logger.debug("[SupabaseClient.__init__] Created admin client")
            except Exception as e:
                logger.error(f"[SupabaseClient.__init__] Failed to create admin client: {e}", exc_info=True)
                raise

        logger.info(f"[SupabaseClient.__init__] Initialized Supabase client for {url}")

        self.operations = SupabaseOperations(self.client)
    
    def get_user_hours(self, user_id: str) -> Optional[float]:
        """Get remaining hours for a user."""
        logger.debug(f"[SupabaseClient.get_user_hours] Getting hours for user: {user_id}")
        return self.operations.get_user_hours(user_id)

    def consume_hours(self, user_id: str, hours: float) -> bool:
        """Consume hours for a user."""
        logger.debug(f"[SupabaseClient.consume_hours] Consuming {hours} hours for user: {user_id}")
        return self.operations.consume_hours(user_id, hours)

    def add_hours(self, user_id: str, hours: float) -> bool:
        """Add hours to a user account."""
        logger.debug(f"[SupabaseClient.add_hours] Adding {hours} hours for user: {user_id}")
        return self.operations.add_hours(user_id, hours)

    def save_time_series_data(self, data: Dict[str, Any]) -> bool:
        """Save time-series data to Supabase."""
        logger.debug(f"[SupabaseClient.save_time_series_data] Saving data for series: {data.get('series_id', 'unknown')}")
        return self.operations.save_time_series_data(data)

    def query_time_series(
        self,
        series_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Query time-series data."""
        logger.debug(f"[SupabaseClient.query_time_series] Querying series: {series_id}, range: {start_time} to {end_time}, limit: {limit}")
        return self.operations.query_time_series(series_id, start_time, end_time, limit)

    def test_connection(self) -> bool:
        """Test Supabase connection."""
        logger.debug("[SupabaseClient.test_connection] Testing connection")
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
