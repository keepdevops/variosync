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
        Validate financial data record.

        Accepts both flat format (ticker, open, high, low, close, vol)
        and time-series format (series_id, measurements: {open, high, low, close, vol})

        Args:
            record: Financial record to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(record, dict):
            return False, "Record must be a dictionary"

        # Accept either 'ticker' or 'series_id' as the identifier
        ticker = record.get("ticker") or record.get("series_id")
        if not ticker:
            return False, "Missing required field: ticker or series_id"

        if "timestamp" not in record:
            return False, "Missing required field: timestamp"

        if not isinstance(ticker, str) or not ticker:
            return False, "ticker/series_id must be a non-empty string"

        # Check for OHLCV data - can be at top level or in measurements dict
        measurements = record.get("measurements", {})

        def get_field(name):
            """Get field from record or measurements."""
            if name in record:
                return record[name]
            return measurements.get(name)

        # Check for numeric data - need at least one numeric measurement
        # Try common price field names
        price_field_aliases = {
            "close": ["close", "c", "adj_close", "adjclose", "adj close", "price", "last"],
            "open": ["open", "o"],
            "high": ["high", "h"],
            "low": ["low", "l"],
            "vol": ["vol", "volume", "v"],
        }

        def get_field_with_aliases(field_name):
            """Get field checking aliases."""
            aliases = price_field_aliases.get(field_name, [field_name])
            for alias in aliases:
                val = get_field(alias)
                if val is not None:
                    return val
                # Also check lowercase in measurements
                if measurements:
                    val = measurements.get(alias.lower())
                    if val is not None:
                        return val
            return None

        # Check for close price or any numeric value
        close_val = get_field_with_aliases("close")

        # If no close field, check if there are any numeric measurements
        has_numeric_data = False
        if measurements:
            for key, val in measurements.items():
                if isinstance(val, (int, float)):
                    has_numeric_data = True
                    if close_val is None:
                        close_val = val  # Use first numeric as close
                    break

        if close_val is None and not has_numeric_data:
            return False, "Missing required field: close (or any numeric measurement)"

        # Validate price fields if present
        for field in ["open", "high", "low", "close"]:
            value = get_field_with_aliases(field)
            if value is not None:
                if not isinstance(value, (int, float)):
                    return False, f"{field} must be a number"
                if value < 0:
                    return False, f"{field} must be non-negative"

        # Validate volume if present
        vol_val = get_field_with_aliases("vol")
        if vol_val is not None:
            if not isinstance(vol_val, (int, float)):
                return False, "vol must be a number"
            if vol_val < 0:
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
