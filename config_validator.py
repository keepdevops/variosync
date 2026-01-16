"""
VARIOSYNC Configuration Validator Module
Validates configuration against schema requirements.
"""
from typing import Any, Dict, Optional


class ConfigValidator:
    """Validates configuration against schema requirements."""
    
    @staticmethod
    def validate_time_series_record(record: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate time-series data record.
        
        Args:
            record: Data record to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(record, dict):
            return False, "Record must be a dictionary"
        
        if "series_id" not in record:
            return False, "Missing required field: series_id"
        
        if "timestamp" not in record:
            return False, "Missing required field: timestamp"
        
        if "measurements" not in record:
            return False, "Missing required field: measurements"
        
        if not isinstance(record["series_id"], str) or not record["series_id"]:
            return False, "series_id must be a non-empty string"
        
        if not isinstance(record["timestamp"], str):
            return False, "timestamp must be a string"
        
        measurements = record["measurements"]
        if not isinstance(measurements, dict):
            return False, "measurements must be a dictionary"
        
        if len(measurements) == 0:
            return False, "measurements must contain at least one key-value pair"
        
        for key, value in measurements.items():
            if not isinstance(value, (int, float, str)):
                return False, f"Measurement '{key}' must be a number or string"
        
        return True, None
    
    @staticmethod
    def validate_financial_record(record: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate financial data record (legacy format).
        
        Args:
            record: Financial record to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(record, dict):
            return False, "Record must be a dictionary"
        
        if "ticker" not in record:
            return False, "Missing required field: ticker"
        
        if "timestamp" not in record:
            return False, "Missing required field: timestamp"
        
        if "close" not in record:
            return False, "Missing required field: close"
        
        if not isinstance(record["ticker"], str) or not record["ticker"]:
            return False, "ticker must be a non-empty string"
        
        price_fields = ["open", "high", "low", "close"]
        for field in price_fields:
            if field in record:
                value = record[field]
                if not isinstance(value, (int, float)):
                    return False, f"{field} must be a number"
                if value < 0:
                    return False, f"{field} must be non-negative"
        
        if "vol" in record:
            if not isinstance(record["vol"], int):
                return False, "vol must be an integer"
            if record["vol"] < 0:
                return False, "vol must be non-negative"
        
        return True, None
    
    @staticmethod
    def validate_supabase_config(config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate Supabase configuration.
        
        Args:
            config: Supabase config dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(config, dict):
            return False, "Config must be a dictionary"
        
        if "url" not in config:
            return False, "Missing required field: url"
        
        if "key" not in config:
            return False, "Missing required field: key"
        
        url = config["url"]
        if not isinstance(url, str) or not url.startswith("https://"):
            return False, "url must be a valid HTTPS URL"
        
        key = config["key"]
        if not isinstance(key, str) or not key:
            return False, "key must be a non-empty string"
        
        return True, None
