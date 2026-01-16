"""
VARIOSYNC Supabase Operations Module
Database operations for Supabase.
"""
from typing import Any, Dict, List, Optional

from logger import get_logger

logger = get_logger()

try:
    from supabase import Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


class SupabaseOperations:
    """Supabase database operations."""
    
    def __init__(self, client: 'Client'):
        """
        Initialize operations.
        
        Args:
            client: Supabase client instance
        """
        self.client = client
    
    def get_user_hours(self, user_id: str) -> Optional[float]:
        """
        Get remaining hours for a user.
        
        Args:
            user_id: User UUID
            
        Returns:
            Remaining hours or None if error
        """
        try:
            response = self.client.table("user_hours").select("hours_remaining").eq("user_id", user_id).execute()
            
            if response.data and len(response.data) > 0:
                hours = response.data[0].get("hours_remaining", 0.0)
                logger.debug(f"User {user_id} has {hours} hours remaining")
                return float(hours)
            else:
                logger.warning(f"No hours record found for user {user_id}")
                return None
        except Exception as e:
            logger.error(f"Error getting user hours: {e}")
            return None
    
    def consume_hours(self, user_id: str, hours: float) -> bool:
        """
        Consume hours for a user.
        
        Args:
            user_id: User UUID
            hours: Hours to consume
            
        Returns:
            True if successful
        """
        try:
            current_hours = self.get_user_hours(user_id)
            
            if current_hours is None:
                logger.error(f"Cannot consume hours: user {user_id} not found")
                return False
            
            if current_hours < hours:
                logger.warning(f"Insufficient hours: {current_hours} < {hours}")
                return False
            
            new_hours = current_hours - hours
            response = self.client.table("user_hours").update({
                "hours_remaining": new_hours
            }).eq("user_id", user_id).execute()
            
            logger.info(f"Consumed {hours} hours for user {user_id}, {new_hours} remaining")
            return True
        except Exception as e:
            logger.error(f"Error consuming hours: {e}")
            return False
    
    def add_hours(self, user_id: str, hours: float) -> bool:
        """
        Add hours to a user account.
        
        Args:
            user_id: User UUID
            hours: Hours to add
            
        Returns:
            True if successful
        """
        try:
            current_hours = self.get_user_hours(user_id) or 0.0
            new_hours = current_hours + hours
            
            response = self.client.table("user_hours").upsert({
                "user_id": user_id,
                "hours_remaining": new_hours
            }).execute()
            
            logger.info(f"Added {hours} hours to user {user_id}, total: {new_hours}")
            return True
        except Exception as e:
            logger.error(f"Error adding hours: {e}")
            return False
    
    def save_time_series_data(self, data: Dict[str, Any]) -> bool:
        """
        Save time-series data to Supabase.
        
        Args:
            data: Time-series data record
            
        Returns:
            True if successful
        """
        try:
            response = self.client.table("time_series_data").insert(data).execute()
            logger.debug(f"Saved time-series data: {data.get('series_id')}")
            return True
        except Exception as e:
            logger.error(f"Error saving time-series data: {e}")
            return False
    
    def query_time_series(
        self,
        series_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Query time-series data.
        
        Args:
            series_id: Series identifier
            start_time: Start timestamp (ISO format)
            end_time: End timestamp (ISO format)
            limit: Maximum number of records
            
        Returns:
            List of time-series records
        """
        try:
            query = self.client.table("time_series_data").select("*").eq("series_id", series_id)
            
            if start_time:
                query = query.gte("timestamp", start_time)
            
            if end_time:
                query = query.lte("timestamp", end_time)
            
            query = query.order("timestamp", desc=False).limit(limit)
            
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error querying time-series data: {e}")
            return []
    
    def test_connection(self) -> bool:
        """
        Test Supabase connection.
        
        Returns:
            True if connection successful
        """
        try:
            response = self.client.table("user_hours").select("count").limit(1).execute()
            logger.info("Supabase connection test successful")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False
