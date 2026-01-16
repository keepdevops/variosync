"""
VARIOSYNC Authentication Validator Module
Handles license key validation and payment checking.
"""
import uuid
from typing import Optional, Tuple

from logger import get_logger
from supabase_client import SupabaseClient

logger = get_logger()


class AuthenticationError(Exception):
    """Authentication-related exception."""
    pass


class PaymentError(Exception):
    """Payment-related exception."""
    pass


class AuthValidator:
    """Validates authentication and payment requirements."""
    
    def __init__(
        self,
        supabase_client: Optional[SupabaseClient] = None,
        enforce_payment: bool = True,
        require_license_validation: bool = False,
        development_mode: bool = False
    ):
        """
        Initialize authentication validator.
        
        Args:
            supabase_client: Supabase client instance
            enforce_payment: Whether to enforce payment/hour checking
            require_license_validation: Whether to require license validation
            development_mode: Development mode (bypasses validation)
        """
        self.supabase_client = supabase_client
        self.enforce_payment = enforce_payment
        self.require_license_validation = require_license_validation
        self.development_mode = development_mode
    
    def validate_license_key(self, license_key: str, license_format: str = "uuid") -> Tuple[bool, Optional[str]]:
        """
        Validate license key format.
        
        Args:
            license_key: License key to validate
            license_format: Expected format (uuid, email, custom)
            
        Returns:
            Tuple of (is_valid, user_id or error_message)
        """
        if self.development_mode:
            logger.debug("Development mode: skipping license validation")
            return True, "dev-user"
        
        if not license_key:
            return False, "License key is required"
        
        if license_format == "uuid":
            try:
                uuid.UUID(license_key)
                return True, license_key
            except ValueError:
                return False, "Invalid UUID format"
        
        elif license_format == "email":
            if "@" in license_key and "." in license_key:
                return True, license_key
            else:
                return False, "Invalid email format"
        
        elif license_format == "custom":
            if len(license_key) > 0:
                return True, license_key
            else:
                return False, "License key cannot be empty"
        
        else:
            return False, f"Unknown license format: {license_format}"
    
    def check_user_hours(self, user_id: str) -> Tuple[bool, Optional[float]]:
        """
        Check if user has sufficient hours remaining.
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (has_hours, hours_remaining)
        """
        if not self.enforce_payment:
            logger.debug("Payment enforcement disabled")
            return True, None
        
        if self.development_mode:
            logger.debug("Development mode: skipping hour check")
            return True, None
        
        if not self.supabase_client:
            if self.require_license_validation:
                logger.error("Supabase client not available but license validation required")
                return False, None
            else:
                logger.warning("Supabase client not available, allowing access")
                return True, None
        
        hours = self.supabase_client.get_user_hours(user_id)
        
        if hours is None:
            if self.require_license_validation:
                logger.error(f"Could not retrieve hours for user {user_id}")
                return False, None
            else:
                logger.warning(f"Could not retrieve hours for user {user_id}, allowing access")
                return True, None
        
        if hours <= 0:
            logger.warning(f"User {user_id} has no hours remaining")
            return False, 0.0
        
        return True, hours
    
    def consume_user_hours(self, user_id: str, hours: float) -> bool:
        """
        Consume hours from user account.
        
        Args:
            user_id: User identifier
            hours: Hours to consume
            
        Returns:
            True if successful
        """
        if not self.enforce_payment:
            return True
        
        if self.development_mode:
            logger.debug("Development mode: skipping hour consumption")
            return True
        
        if not self.supabase_client:
            logger.warning("Supabase client not available, cannot consume hours")
            return False
        
        return self.supabase_client.consume_hours(user_id, hours)
    
    def validate_access(
        self,
        license_key: str,
        license_format: str = "uuid",
        required_hours: float = 0.0
    ) -> Tuple[bool, Optional[str], Optional[float]]:
        """
        Validate user access (license + hours).
        
        Args:
            license_key: User license key
            license_format: License key format
            required_hours: Hours required for operation
            
        Returns:
            Tuple of (is_valid, user_id, hours_remaining)
        """
        is_valid, user_id_or_error = self.validate_license_key(license_key, license_format)
        
        if not is_valid:
            logger.error(f"License validation failed: {user_id_or_error}")
            raise AuthenticationError(f"Invalid license key: {user_id_or_error}")
        
        user_id = user_id_or_error
        
        has_hours, hours_remaining = self.check_user_hours(user_id)
        
        if not has_hours:
            logger.error(f"User {user_id} does not have sufficient hours")
            raise PaymentError(f"Insufficient hours remaining: {hours_remaining}")
        
        if hours_remaining is not None and hours_remaining < required_hours:
            logger.error(f"User {user_id} requires {required_hours} hours but has {hours_remaining}")
            raise PaymentError(f"Insufficient hours: {hours_remaining} < {required_hours}")
        
        logger.info(f"Access validated for user {user_id}, hours remaining: {hours_remaining}")
        return True, user_id, hours_remaining
