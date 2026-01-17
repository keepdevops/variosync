"""
Redis caching operations.
"""
from typing import Any, Optional
import json

from logger import get_logger

logger = get_logger()


class RedisCache:
    """Redis cache operations."""
    
    def __init__(self, client):
        """Initialize with Redis client."""
        self.client = client
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting key {key} from Redis: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            serialized = json.dumps(value)
            if ttl:
                return self.client.setex(key, ttl, serialized)
            else:
                return self.client.set(key, serialized)
        except Exception as e:
            logger.error(f"Error setting key {key} in Redis: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting key {key} from Redis: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Error checking key {key} in Redis: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter."""
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Error incrementing key {key} in Redis: {e}")
            return None
    
    def check_rate_limit(self, identifier: str, limit: int, window: int = 60) -> dict:
        """Check rate limit for identifier."""
        key = f"rate_limit:{identifier}"
        
        try:
            current = self.client.get(key)
            if current is None:
                self.client.setex(key, window, 1)
                return {"allowed": True, "remaining": limit - 1, "reset_in": window}
            
            current_count = int(current)
            if current_count >= limit:
                ttl = self.client.ttl(key)
                return {"allowed": False, "remaining": 0, "reset_in": ttl if ttl > 0 else window}
            
            new_count = self.client.incr(key)
            if new_count == 1:
                self.client.expire(key, window)
            
            return {
                "allowed": True,
                "remaining": limit - new_count,
                "reset_in": self.client.ttl(key) or window
            }
        except Exception as e:
            logger.error(f"Error checking rate limit for {identifier}: {e}")
            return {"allowed": True, "remaining": limit, "reset_in": window}
    
    def cache_query(self, query_key: str, query_func, ttl: int = 3600, *args, **kwargs) -> Any:
        """Cache result of a query function."""
        cached = self.get(query_key)
        if cached is not None:
            logger.debug(f"Cache hit for {query_key}")
            return cached
        
        logger.debug(f"Cache miss for {query_key}, executing query")
        result = query_func(*args, **kwargs)
        self.set(query_key, result, ttl)
        return result
