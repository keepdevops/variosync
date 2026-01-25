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
        logger.debug("[SupabaseOperations.__init__] Initializing operations")
        if client is None:
            logger.error("[SupabaseOperations.__init__] Client is None")
            raise ValueError("Supabase client cannot be None")
        self.client = client
        logger.debug("[SupabaseOperations.__init__] Operations initialized")

    def get_user_hours(self, user_id: str) -> Optional[float]:
        """
        Get remaining hours for a user.

        Args:
            user_id: User UUID

        Returns:
            Remaining hours or None if error
        """
        logger.debug(f"[SupabaseOperations.get_user_hours] Getting hours for user: {user_id}")

        # Validate user_id
        if not user_id:
            logger.error("[SupabaseOperations.get_user_hours] Empty user_id provided")
            return None

        if not isinstance(user_id, str):
            logger.error(f"[SupabaseOperations.get_user_hours] user_id must be string, got: {type(user_id)}")
            return None

        try:
            response = self.client.table("user_hours").select("hours_remaining").eq("user_id", user_id).execute()

            if response.data and len(response.data) > 0:
                hours = response.data[0].get("hours_remaining", 0.0)
                logger.info(f"[SupabaseOperations.get_user_hours] User {user_id} has {hours} hours remaining")
                return float(hours)
            else:
                logger.warning(f"[SupabaseOperations.get_user_hours] No hours record found for user {user_id}")
                return None
        except Exception as e:
            logger.error(f"[SupabaseOperations.get_user_hours] Error getting user hours: {e}", exc_info=True)
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
        logger.debug(f"[SupabaseOperations.consume_hours] Consuming {hours} hours for user: {user_id}")

        # Validate user_id
        if not user_id:
            logger.error("[SupabaseOperations.consume_hours] Empty user_id provided")
            return False

        # Validate hours
        if not isinstance(hours, (int, float)):
            logger.error(f"[SupabaseOperations.consume_hours] hours must be numeric, got: {type(hours)}")
            return False

        if hours <= 0:
            logger.error(f"[SupabaseOperations.consume_hours] hours must be positive, got: {hours}")
            return False

        try:
            current_hours = self.get_user_hours(user_id)

            if current_hours is None:
                logger.error(f"[SupabaseOperations.consume_hours] Cannot consume hours: user {user_id} not found")
                return False

            if current_hours < hours:
                logger.warning(f"[SupabaseOperations.consume_hours] Insufficient hours: {current_hours} < {hours} for user {user_id}")
                return False

            new_hours = current_hours - hours
            response = self.client.table("user_hours").update({
                "hours_remaining": new_hours
            }).eq("user_id", user_id).execute()

            logger.info(f"[SupabaseOperations.consume_hours] Consumed {hours} hours for user {user_id}, {new_hours} remaining")
            return True
        except Exception as e:
            logger.error(f"[SupabaseOperations.consume_hours] Error consuming hours: {e}", exc_info=True)
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
        logger.debug(f"[SupabaseOperations.add_hours] Adding {hours} hours for user: {user_id}")

        # Validate user_id
        if not user_id:
            logger.error("[SupabaseOperations.add_hours] Empty user_id provided")
            return False

        # Validate hours
        if not isinstance(hours, (int, float)):
            logger.error(f"[SupabaseOperations.add_hours] hours must be numeric, got: {type(hours)}")
            return False

        if hours <= 0:
            logger.error(f"[SupabaseOperations.add_hours] hours must be positive, got: {hours}")
            return False

        try:
            current_hours = self.get_user_hours(user_id) or 0.0
            new_hours = current_hours + hours

            response = self.client.table("user_hours").upsert({
                "user_id": user_id,
                "hours_remaining": new_hours
            }).execute()

            logger.info(f"[SupabaseOperations.add_hours] Added {hours} hours to user {user_id}, total: {new_hours}")
            return True
        except Exception as e:
            logger.error(f"[SupabaseOperations.add_hours] Error adding hours: {e}", exc_info=True)
            return False
    
    def save_time_series_data(self, data: Dict[str, Any]) -> bool:
        """
        Save time-series data to Supabase.

        Args:
            data: Time-series data record

        Returns:
            True if successful
        """
        logger.debug(f"[SupabaseOperations.save_time_series_data] Saving time-series data")

        # Validate data
        if not data:
            logger.error("[SupabaseOperations.save_time_series_data] Empty data provided")
            return False

        if not isinstance(data, dict):
            logger.error(f"[SupabaseOperations.save_time_series_data] data must be dict, got: {type(data)}")
            return False

        # Validate required fields
        series_id = data.get('series_id')
        timestamp = data.get('timestamp')

        if not series_id:
            logger.warning("[SupabaseOperations.save_time_series_data] Missing series_id in data")

        if not timestamp:
            logger.warning("[SupabaseOperations.save_time_series_data] Missing timestamp in data")

        logger.debug(f"[SupabaseOperations.save_time_series_data] Data keys: {list(data.keys())}")

        try:
            response = self.client.table("time_series_data").insert(data).execute()
            logger.info(f"[SupabaseOperations.save_time_series_data] Saved time-series data for series: {series_id}")
            return True
        except Exception as e:
            logger.error(f"[SupabaseOperations.save_time_series_data] Error saving time-series data: {e}", exc_info=True)
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
        logger.debug(f"[SupabaseOperations.query_time_series] Querying series: {series_id}")

        # Validate series_id
        if not series_id:
            logger.error("[SupabaseOperations.query_time_series] Empty series_id provided")
            return []

        # Validate limit
        if limit <= 0:
            logger.warning(f"[SupabaseOperations.query_time_series] Invalid limit: {limit}, using default 1000")
            limit = 1000

        if limit > 10000:
            logger.warning(f"[SupabaseOperations.query_time_series] Limit {limit} exceeds max, capping at 10000")
            limit = 10000

        logger.debug(f"[SupabaseOperations.query_time_series] Query params - series: {series_id}, start: {start_time}, end: {end_time}, limit: {limit}")

        try:
            query = self.client.table("time_series_data").select("*").eq("series_id", series_id)

            if start_time:
                query = query.gte("timestamp", start_time)

            if end_time:
                query = query.lte("timestamp", end_time)

            query = query.order("timestamp", desc=False).limit(limit)

            response = query.execute()
            result = response.data if response.data else []

            logger.info(f"[SupabaseOperations.query_time_series] Retrieved {len(result)} records for series: {series_id}")
            return result
        except Exception as e:
            logger.error(f"[SupabaseOperations.query_time_series] Error querying time-series data: {e}", exc_info=True)
            return []
    
    def test_connection(self) -> bool:
        """
        Test Supabase connection.

        Returns:
            True if connection successful
        """
        logger.debug("[SupabaseOperations.test_connection] Testing Supabase connection")
        try:
            response = self.client.table("user_hours").select("count").limit(1).execute()
            logger.info("[SupabaseOperations.test_connection] Supabase connection test successful")
            return True
        except Exception as e:
            logger.error(f"[SupabaseOperations.test_connection] Supabase connection test failed: {e}", exc_info=True)
            return False
