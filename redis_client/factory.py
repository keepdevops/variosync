"""
Redis client factory.
"""
import os
from typing import Optional

from logger import get_logger
from . import RedisClient, REDIS_AVAILABLE

logger = get_logger()


class RedisClientFactory:
    """Factory for creating Redis clients."""
    
    _instance: Optional[RedisClient] = None
    
    @staticmethod
    def get_instance() -> Optional[RedisClient]:
        """Get singleton Redis client instance."""
        if RedisClientFactory._instance is None:
            try:
                RedisClientFactory._instance = RedisClient()
            except Exception as e:
                logger.warning(f"Could not create Redis client: {e}")
                return None
        return RedisClientFactory._instance
    
    @staticmethod
    def create_from_env() -> Optional[RedisClient]:
        """Create Redis client from environment variables."""
        if not REDIS_AVAILABLE:
            return None
        
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            logger.warning("REDIS_URL environment variable not set")
            return None
        
        try:
            return RedisClient(redis_url)
        except Exception as e:
            logger.error(f"Error creating Redis client from env: {e}")
            return None
