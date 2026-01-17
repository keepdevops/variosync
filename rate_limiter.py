"""
VARIOSYNC Rate Limiter Module
Rate limiting middleware and utilities.
"""
import os
from typing import Optional, Callable, Any
from functools import wraps

from logger import get_logger
from redis_client import RedisClientFactory

logger = get_logger()


def rate_limit(
    limit: int = 60,
    window: int = 60,
    identifier_func: Optional[Callable] = None
):
    """
    Decorator for rate limiting functions.
    
    Args:
        limit: Maximum requests allowed
        window: Time window in seconds
        identifier_func: Function to get identifier (defaults to using function name)
    
    Example:
        @rate_limit(limit=10, window=60)
        def my_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get identifier
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            else:
                identifier = f"{func.__module__}.{func.__name__}"
            
            # Get Redis client
            redis_client = RedisClientFactory.get_instance()
            
            if redis_client:
                # Check rate limit
                result = redis_client.check_rate_limit(identifier, limit, window)
                
                if not result["allowed"]:
                    logger.warning(
                        f"Rate limit exceeded for {identifier}: "
                        f"{limit} requests per {window}s"
                    )
                    raise RateLimitError(
                        f"Rate limit exceeded. Try again in {result['reset_in']} seconds.",
                        reset_in=result["reset_in"]
                    )
            
            # Execute function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def get_client_identifier(request) -> str:
    """
    Get client identifier from request.
    
    Args:
        request: Request object (NiceGUI request or similar)
        
    Returns:
        Client identifier string
    """
    # Try to get IP address
    try:
        if hasattr(request, 'client'):
            return request.client.host
        elif hasattr(request, 'remote_addr'):
            return request.remote_addr
        elif hasattr(request, 'headers'):
            # Try X-Forwarded-For header
            forwarded = request.headers.get('X-Forwarded-For')
            if forwarded:
                return forwarded.split(',')[0].strip()
    except:
        pass
    
    # Fallback to default
    return "unknown"


class RateLimitError(Exception):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str, reset_in: int = 60):
        super().__init__(message)
        self.reset_in = reset_in


def check_rate_limit(
    identifier: str,
    limit: int = 60,
    window: int = 60
) -> dict:
    """
    Check rate limit for an identifier.
    
    Args:
        identifier: Unique identifier (user ID, IP, etc.)
        limit: Maximum requests allowed
        window: Time window in seconds
        
    Returns:
        Dictionary with 'allowed', 'remaining', 'reset_in' keys
    """
    redis_client = RedisClientFactory.get_instance()
    
    if not redis_client:
        # Fail open if Redis unavailable
        return {
            "allowed": True,
            "remaining": limit,
            "reset_in": window
        }
    
    return redis_client.check_rate_limit(identifier, limit, window)
