"""
VARIOSYNC Redis Client Module
Handles Redis caching, rate limiting, and pub/sub operations.
"""
import os
from typing import Any, Dict, List, Optional
import json
from datetime import timedelta

from logger import get_logger
from .cache import RedisCache
from .pubsub import RedisPubSub
from .factory import RedisClientFactory

logger = get_logger()

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis library not available. Install with: pip install redis")


class RedisClient:
    """Client for Redis operations."""
    
    def __init__(self, url: Optional[str] = None):
        """
        Initialize Redis client.
        
        Args:
            url: Redis connection URL (defaults to REDIS_URL env var)
        """
        if not REDIS_AVAILABLE:
            raise ImportError("Redis library not installed")
        
        redis_url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        try:
            self.client = redis.from_url(redis_url, decode_responses=True)
            self.client.ping()
            logger.info(f"Connected to Redis at {redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
        
        self.cache = RedisCache(self.client)
        self.pubsub = RedisPubSub(self.client)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        return self.cache.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        return self.cache.delete(key)
    
    def publish(self, channel: str, message: Any) -> int:
        """Publish message to channel."""
        return self.pubsub.publish(channel, message)
    
    def subscribe(self, channel: str, callback: callable) -> None:
        """Subscribe to channel."""
        return self.pubsub.subscribe(channel, callback)
