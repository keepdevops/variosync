"""
VARIOSYNC Authentication Module
Main authentication manager.
"""
import os
from typing import Optional, Tuple

from auth_validator import AuthValidator, AuthenticationError, PaymentError
from logger import get_logger
from supabase_client import SupabaseClientFactory

logger = get_logger()

# Re-export exceptions
__all__ = ["AuthManager", "AuthenticationError", "PaymentError"]


class AuthManager:
    """Main authentication manager."""
    
    def __init__(self, config: dict):
        """
        Initialize authentication manager from config.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Get Supabase client
        self.supabase_client = None
        if "Supabase" in config:
            self.supabase_client = SupabaseClientFactory.create_from_config(config)
        else:
            self.supabase_client = SupabaseClientFactory.create_from_env()
        
        # Get auth config
        auth_config = config.get("Authentication", {})
        
        self.validator = AuthValidator(
            supabase_client=self.supabase_client,
            enforce_payment=auth_config.get("enforce_payment", True),
            require_license_validation=auth_config.get("require_license_validation", False),
            development_mode=auth_config.get("development_mode", False)
        )
        
        self.license_format = auth_config.get("license_key_format", "uuid")
        
        logger.info("Initialized authentication manager")
    
    def authenticate(self, license_key: str, required_hours: float = 0.0) -> Tuple[str, float]:
        """
        Authenticate user and check hours.
        
        Args:
            license_key: User license key
            required_hours: Hours required for operation
            
        Returns:
            Tuple of (user_id, hours_remaining)
        """
        is_valid, user_id, hours_remaining = self.validator.validate_access(
            license_key,
            self.license_format,
            required_hours
        )
        
        return user_id, hours_remaining or 0.0
    
    def consume_hours(self, user_id: str, hours: float) -> bool:
        """
        Consume hours from user account.
        
        Args:
            user_id: User identifier
            hours: Hours to consume
            
        Returns:
            True if successful
        """
        return self.validator.consume_user_hours(user_id, hours)
