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
        logger.debug("[ModalClient.__init__] Initializing Modal client")

        if not MODAL_AVAILABLE:
            logger.error("[ModalClient.__init__] Modal library not installed")
            raise ImportError("Modal library not installed")

        self.token_id = token_id or os.getenv("MODAL_TOKEN_ID")
        self.token_secret = token_secret or os.getenv("MODAL_TOKEN_SECRET")

        # Log configuration status (without exposing secrets)
        logger.debug(f"[ModalClient.__init__] Token ID configured: {bool(self.token_id)}")
        logger.debug(f"[ModalClient.__init__] Token secret configured: {bool(self.token_secret)}")

        # Validate credentials
        missing = []
        if not self.token_id:
            missing.append("token_id")
        if not self.token_secret:
            missing.append("token_secret")

        if missing:
            logger.error(f"[ModalClient.__init__] Missing Modal credentials: {missing}")
            raise ValueError(f"Modal credentials missing: {', '.join(missing)}")

        # Set Modal token
        os.environ["MODAL_TOKEN_ID"] = self.token_id
        os.environ["MODAL_TOKEN_SECRET"] = self.token_secret

        # Create Modal client
        try:
            self.app = modal.App("variosync")
            logger.info("[ModalClient.__init__] Modal client initialized successfully")
        except Exception as e:
            logger.error(f"[ModalClient.__init__] Error initializing Modal client: {e}", exc_info=True)
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
        logger.debug(f"[ModalClient.call_function] Calling function: {function_name}")

        # Validate function_name
        if not function_name:
            logger.error("[ModalClient.call_function] Empty function_name provided")
            raise ValueError("Function name cannot be empty")

        if not isinstance(function_name, str):
            logger.error(f"[ModalClient.call_function] function_name must be string, got: {type(function_name)}")
            raise TypeError("Function name must be a string")

        logger.debug(f"[ModalClient.call_function] Args count: {len(args)}, Kwargs: {list(kwargs.keys())}")

        try:
            # Get function reference
            func = getattr(self.app, function_name, None)
            if func is None:
                logger.error(f"[ModalClient.call_function] Function not found: {function_name}")
                raise ValueError(f"Function {function_name} not found")

            logger.info(f"[ModalClient.call_function] Invoking Modal function: {function_name}")

            # Call function
            with self.app.run():
                result = func.remote(*args, **kwargs)

            logger.info(f"[ModalClient.call_function] Function {function_name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"[ModalClient.call_function] Error calling Modal function {function_name}: {e}", exc_info=True)
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
        logger.debug(f"[ModalClient.call_function_async] Calling function async: {function_name}")

        # Validate function_name
        if not function_name:
            logger.error("[ModalClient.call_function_async] Empty function_name provided")
            raise ValueError("Function name cannot be empty")

        if not isinstance(function_name, str):
            logger.error(f"[ModalClient.call_function_async] function_name must be string, got: {type(function_name)}")
            raise TypeError("Function name must be a string")

        logger.debug(f"[ModalClient.call_function_async] Args count: {len(args)}, Kwargs: {list(kwargs.keys())}")

        try:
            # Get function reference
            func = getattr(self.app, function_name, None)
            if func is None:
                logger.error(f"[ModalClient.call_function_async] Function not found: {function_name}")
                raise ValueError(f"Function {function_name} not found")

            logger.info(f"[ModalClient.call_function_async] Invoking Modal function async: {function_name}")

            # Call function async
            async with self.app.run():
                result = await func.aio(*args, **kwargs)

            logger.info(f"[ModalClient.call_function_async] Function {function_name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"[ModalClient.call_function_async] Error calling Modal function {function_name}: {e}", exc_info=True)
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
        logger.debug(f"[ModalClient.trigger_webhook] Triggering webhook: {webhook_url}")

        # Validate webhook_url
        if not webhook_url:
            logger.error("[ModalClient.trigger_webhook] Empty webhook_url provided")
            return False

        if not isinstance(webhook_url, str):
            logger.error(f"[ModalClient.trigger_webhook] webhook_url must be string, got: {type(webhook_url)}")
            return False

        if not webhook_url.startswith("http"):
            logger.error(f"[ModalClient.trigger_webhook] Invalid webhook URL format: {webhook_url}")
            return False

        # Validate data
        if data is None:
            logger.warning("[ModalClient.trigger_webhook] data is None, using empty dict")
            data = {}

        if not isinstance(data, dict):
            logger.error(f"[ModalClient.trigger_webhook] data must be dict, got: {type(data)}")
            return False

        logger.debug(f"[ModalClient.trigger_webhook] Data keys: {list(data.keys())}")

        try:
            import requests
            logger.info(f"[ModalClient.trigger_webhook] Sending POST to: {webhook_url}")

            response = requests.post(webhook_url, json=data, timeout=30)
            response.raise_for_status()

            logger.info(f"[ModalClient.trigger_webhook] Webhook triggered successfully, status: {response.status_code}")
            return True
        except requests.exceptions.Timeout:
            logger.error(f"[ModalClient.trigger_webhook] Timeout triggering webhook: {webhook_url}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"[ModalClient.trigger_webhook] Request error triggering webhook: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"[ModalClient.trigger_webhook] Error triggering Modal webhook: {e}", exc_info=True)
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
