"""
VARIOSYNC API Client Module
HTTP client for API downloads with rate limiting.
"""
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import requests

from logger import get_logger

logger = get_logger()


class APIClient:
    """HTTP client for API requests with rate limiting."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize API client.
        
        Args:
            config: API configuration
        """
        self.timeout = config.get("timeout", 30)
        self.rate_limit_per_minute = config.get("rate_limit_per_minute", 60)
        self.last_request_time = 0.0
        self.request_count = 0
        self.request_window_start = time.time()
    
    def _rate_limit(self) -> None:
        """Apply rate limiting."""
        current_time = time.time()
        elapsed = current_time - self.request_window_start
        
        if elapsed >= 60:
            self.request_count = 0
            self.request_window_start = current_time
        
        if self.request_count >= self.rate_limit_per_minute:
            wait_time = 60 - elapsed
            if wait_time > 0:
                logger.debug(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)
                self.request_count = 0
                self.request_window_start = time.time()
        
        min_delay = 60.0 / self.rate_limit_per_minute
        time_since_last = current_time - self.last_request_time
        if time_since_last < min_delay:
            sleep_time = min_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def get(self, url: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Make GET request with retries.
        
        Args:
            url: Request URL
            max_retries: Maximum retry attempts
            
        Returns:
            Response data or None if failed
        """
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed after {max_retries} attempts")
                    return None
        
        return None
