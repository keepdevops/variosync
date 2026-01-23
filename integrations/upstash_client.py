"""
Upstash Redis Integration
Provides caching, rate limiting, and session management via Upstash Redis REST API.
"""
import os
from typing import Optional, Any, Dict
from logger import get_logger

logger = get_logger()

try:
    from upstash_redis import Redis
    UPSTASH_AVAILABLE = True
except ImportError:
    UPSTASH_AVAILABLE = False
    logger.warning("Upstash Redis not available. Install with: pip install upstash-redis")


class UpstashRedisClient:
    """Client for Upstash Redis operations."""
    
    def __init__(self, url: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize Upstash Redis client.
        
        Args:
            url: Upstash Redis REST URL (from env: UPSTASH_REDIS_REST_URL)
            token: Upstash Redis REST token (from env: UPSTASH_REDIS_REST_TOKEN)
        """
        if not UPSTASH_AVAILABLE:
            raise ImportError("Upstash Redis library not installed")
        
        self.url = url or os.getenv("UPSTASH_REDIS_REST_URL")
        self.token = token or os.getenv("UPSTASH_REDIS_REST_TOKEN")
        
        if not self.url or not self.token:
            raise ValueError("Upstash Redis URL and token must be provided")
        
        self.client = Redis(url=self.url, token=self.token)
        logger.info("Upstash Redis client initialized")
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            return None
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """
        Set value in Redis.
        
        Args:
            key: Redis key
            value: Value to set
            ex: Expiration time in seconds (optional)
        """
        try:
            if ex:
                await self.client.setex(key, ex, value)
            else:
                await self.client.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Error setting key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting key {key}: {e}")
            return False
    
    async def incr(self, key: str) -> int:
        """Increment counter."""
        try:
            return await self.client.incr(key)
        except Exception as e:
            logger.error(f"Error incrementing key {key}: {e}")
            return 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key."""
        try:
            await self.client.expire(key, seconds)
            return True
        except Exception as e:
            logger.error(f"Error setting expiration on key {key}: {e}")
            return False
    
    async def rate_limit(
        self, 
        key: str, 
        limit: int = 10, 
        window: int = 60
    ) -> tuple[bool, int]:
        """
        Rate limit check.
        
        Args:
            key: Rate limit key (e.g., f"rate:{user_id}" or f"rate:{ip}")
            limit: Maximum requests allowed
            window: Time window in seconds
        
        Returns:
            (allowed, remaining) - Whether request is allowed and remaining count
        """
        try:
            count = await self.incr(key)
            await self.expire(key, window)
            
            if count > limit:
                return False, 0
            
            remaining = limit - count
            return True, remaining
        except Exception as e:
            logger.error(f"Error checking rate limit for {key}: {e}")
            return True, limit  # Fail open
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """Get cached value (deserializes JSON)."""
        try:
            value = await self.get(key)
            if value:
                import json
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache {key}: {e}")
            return None
    
    async def cache_set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 3600
    ) -> bool:
        """
        Cache value (serializes to JSON).
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl: Time to live in seconds
        """
        try:
            import json
            serialized = json.dumps(value)
            return await self.set(key, serialized, ex=ttl)
        except Exception as e:
            logger.error(f"Error caching {key}: {e}")
            return False
    
    async def session_get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        return await self.cache_get(f"session:{session_id}")
    
    async def session_set(
        self, 
        session_id: str, 
        data: Dict[str, Any], 
        ttl: int = 86400
    ) -> bool:
        """Set session data (default 24 hours)."""
        return await self.cache_set(f"session:{session_id}", data, ttl=ttl)
    
    async def session_delete(self, session_id: str) -> bool:
        """Delete session."""
        return await self.delete(f"session:{session_id}")


class UpstashRedisFactory:
    """Factory for creating Upstash Redis clients."""
    
    @staticmethod
    def create_from_env() -> Optional[UpstashRedisClient]:
        """Create client from environment variables."""
        if not UPSTASH_AVAILABLE:
            logger.warning("Upstash Redis not available")
            return None
        
        url = os.getenv("UPSTASH_REDIS_REST_URL")
        token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
        
        if not url or not token:
            logger.warning("Upstash Redis environment variables not set")
            return None
        
        try:
            return UpstashRedisClient(url=url, token=token)
        except Exception as e:
            logger.error(f"Error creating Upstash Redis client: {e}")
            return None
