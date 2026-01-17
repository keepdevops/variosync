"""
VARIOSYNC Redis Client Module
Handles Redis caching, rate limiting, and pub/sub operations.
"""
import os
from typing import Any, Dict, List, Optional
import json
from datetime import timedelta

from logger import get_logger

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
            # Test connection
            self.client.ping()
            logger.info(f"Connected to Redis at {redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
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
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (None for no expiration)
        """
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
    
    def check_rate_limit(
        self,
        identifier: str,
        limit: int,
        window: int = 60
    ) -> Dict[str, Any]:
        """
        Check rate limit for identifier.
        
        Args:
            identifier: Unique identifier (user ID, IP address, etc.)
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            Dictionary with 'allowed' (bool) and 'remaining' (int) keys
        """
        key = f"rate_limit:{identifier}"
        
        try:
            current = self.client.get(key)
            if current is None:
                # First request in window
                self.client.setex(key, window, 1)
                return {
                    "allowed": True,
                    "remaining": limit - 1,
                    "reset_in": window
                }
            
            current_count = int(current)
            if current_count >= limit:
                ttl = self.client.ttl(key)
                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset_in": ttl if ttl > 0 else window
                }
            
            # Increment counter
            new_count = self.client.incr(key)
            if new_count == 1:
                # Set expiration if this was the first increment
                self.client.expire(key, window)
            
            return {
                "allowed": True,
                "remaining": limit - new_count,
                "reset_in": self.client.ttl(key) or window
            }
        except Exception as e:
            logger.error(f"Error checking rate limit for {identifier}: {e}")
            # Fail open - allow request if Redis fails
            return {
                "allowed": True,
                "remaining": limit,
                "reset_in": window
            }
    
    def cache_query(
        self,
        query_key: str,
        query_func,
        ttl: int = 3600,
        *args,
        **kwargs
    ) -> Any:
        """
        Cache result of a query function.
        
        Args:
            query_key: Cache key for query
            query_func: Function to execute if cache miss
            ttl: Time to live in seconds
            *args, **kwargs: Arguments to pass to query_func
            
        Returns:
            Cached or fresh result
        """
        # Check cache
        cached = self.get(query_key)
        if cached is not None:
            logger.debug(f"Cache hit for {query_key}")
            return cached
        
        # Execute query
        logger.debug(f"Cache miss for {query_key}, executing query")
        result = query_func(*args, **kwargs)
        
        # Cache result
        self.set(query_key, result, ttl)
        
        return result
    
    def publish(self, channel: str, message: Dict[str, Any]) -> int:
        """Publish message to channel."""
        try:
            serialized = json.dumps(message)
            return self.client.publish(channel, serialized)
        except Exception as e:
            logger.error(f"Error publishing to channel {channel}: {e}")
            return 0
    
    def subscribe(self, channel: str, handler):
        """
        Subscribe to channel and handle messages.
        
        Args:
            channel: Channel name
            handler: Function to handle messages (receives dict)
        """
        try:
            pubsub = self.client.pubsub()
            pubsub.subscribe(channel)
            
            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        handler(data)
                    except Exception as e:
                        logger.error(f"Error handling message: {e}")
        except Exception as e:
            logger.error(f"Error subscribing to channel {channel}: {e}")


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
