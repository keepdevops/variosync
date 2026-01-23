"""
Modal Integration
Provides client for triggering serverless functions on Modal.
"""
import os
from typing import Optional, Dict, Any
from logger import get_logger

logger = get_logger()

try:
    import modal
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False
    logger.warning("Modal not available. Install with: pip install modal")


class ModalClient:
    """Client for Modal serverless functions."""
    
    def __init__(
        self,
        token_id: Optional[str] = None,
        token_secret: Optional[str] = None
    ):
        """
        Initialize Modal client.
        
        Args:
            token_id: Modal token ID (from env: MODAL_TOKEN_ID)
            token_secret: Modal token secret (from env: MODAL_TOKEN_SECRET)
        """
        if not MODAL_AVAILABLE:
            raise ImportError("Modal library not installed")
        
        self.token_id = token_id or os.getenv("MODAL_TOKEN_ID")
        self.token_secret = token_secret or os.getenv("MODAL_TOKEN_SECRET")
        
        if not self.token_id or not self.token_secret:
            raise ValueError("Modal token ID and secret must be provided")
        
        # Set Modal token
        os.environ["MODAL_TOKEN_ID"] = self.token_id
        os.environ["MODAL_TOKEN_SECRET"] = self.token_secret
        
        # Create Modal client
        try:
            self.app = modal.App("variosync")
            logger.info("Modal client initialized")
        except Exception as e:
            logger.error(f"Error initializing Modal client: {e}")
            raise
    
    def call_function(
        self,
        function_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Call a Modal function synchronously.
        
        Args:
            function_name: Name of the function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Function result
        """
        try:
            # Get function reference
            func = getattr(self.app, function_name, None)
            if func is None:
                raise ValueError(f"Function {function_name} not found")
            
            # Call function
            with self.app.run():
                result = func.remote(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Error calling Modal function {function_name}: {e}")
            raise
    
    async def call_function_async(
        self,
        function_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Call a Modal function asynchronously.
        
        Args:
            function_name: Name of the function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Function result
        """
        try:
            # Get function reference
            func = getattr(self.app, function_name, None)
            if func is None:
                raise ValueError(f"Function {function_name} not found")
            
            # Call function async
            async with self.app.run():
                result = await func.aio(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Error calling Modal function {function_name}: {e}")
            raise
    
    def trigger_webhook(
        self,
        webhook_url: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Trigger Modal webhook (HTTP POST).
        
        Args:
            webhook_url: Modal webhook URL
            data: Data to send
        
        Returns:
            True if successful
        """
        try:
            import requests
            response = requests.post(webhook_url, json=data, timeout=30)
            response.raise_for_status()
            logger.info(f"Triggered Modal webhook: {webhook_url}")
            return True
        except Exception as e:
            logger.error(f"Error triggering Modal webhook: {e}")
            return False


class ModalClientFactory:
    """Factory for creating Modal clients."""
    
    @staticmethod
    def create_from_env() -> Optional[ModalClient]:
        """Create client from environment variables."""
        if not MODAL_AVAILABLE:
            logger.warning("Modal not available")
            return None
        
        token_id = os.getenv("MODAL_TOKEN_ID")
        token_secret = os.getenv("MODAL_TOKEN_SECRET")
        
        if not token_id or not token_secret:
            logger.warning("Modal environment variables not set")
            return None
        
        try:
            return ModalClient(token_id=token_id, token_secret=token_secret)
        except Exception as e:
            logger.error(f"Error creating Modal client: {e}")
            return None
