"""
VARIOSYNC Data Processor Module
Handles time-series data processing, validation, and transformation.
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from config_validator import ConfigValidator
from logger import get_logger
from storage_base import StorageBackend

logger = get_logger()


class TimeSeriesProcessor:
    """Processes time-series data records."""
    
    def __init__(self, storage: Optional[StorageBackend] = None):
        """
        Initialize data processor.
        
        Args:
            storage: Optional storage backend for saving data
        """
        self.storage = storage
        self.validator = ConfigValidator()
        logger.info("Initialized time-series processor")
    
    def validate_record(self, record: Dict[str, Any], record_type: str = "time_series") -> Tuple[bool, Optional[str]]:
        """
        Validate a data record.
        
        Args:
            record: Data record to validate
            record_type: Type of record (time_series or financial)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if record_type == "time_series":
            return self.validator.validate_time_series_record(record)
        elif record_type == "financial":
            return self.validator.validate_financial_record(record)
        else:
            return False, f"Unknown record type: {record_type}"
    
    def normalize_timestamp(self, timestamp: str) -> Optional[str]:
        """
        Normalize timestamp to ISO 8601 format.
        
        Args:
            timestamp: Timestamp string
            
        Returns:
            Normalized timestamp or None if invalid
        """
        try:
            # Try parsing various formats
            formats = [
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%Y%m%d"
            ]
            
            parsed_dt = None
            for fmt in formats:
                try:
                    parsed_dt = datetime.strptime(timestamp, fmt)
                    break
                except ValueError:
                    continue
            
            if parsed_dt is None:
                logger.warning(f"Could not parse timestamp: {timestamp}")
                return None
            
            # Return ISO format
            return parsed_dt.isoformat()
        except Exception as e:
            logger.error(f"Error normalizing timestamp {timestamp}: {e}")
            return None
    
    def convert_financial_to_time_series(self, financial_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert financial record to time-series format.
        
        Args:
            financial_record: Financial data record
            
        Returns:
            Time-series format record
        """
        # Validate financial record first
        is_valid, error = self.validate_record(financial_record, "financial")
        if not is_valid:
            raise ValueError(f"Invalid financial record: {error}")
        
        # Convert to time-series format
        time_series_record = {
            "series_id": financial_record["ticker"],
            "timestamp": financial_record["timestamp"],
            "measurements": {}
        }
        
        # Map OHLCV fields to measurements
        if "open" in financial_record:
            time_series_record["measurements"]["open"] = financial_record["open"]
        
        if "high" in financial_record:
            time_series_record["measurements"]["high"] = financial_record["high"]
        
        if "low" in financial_record:
            time_series_record["measurements"]["low"] = financial_record["low"]
        
        if "close" in financial_record:
            time_series_record["measurements"]["close"] = financial_record["close"]
        
        if "vol" in financial_record:
            time_series_record["measurements"]["vol"] = financial_record["vol"]
        
        if "openint" in financial_record:
            time_series_record["measurements"]["openint"] = financial_record["openint"]
        
        # Preserve format if present
        if "format" in financial_record:
            time_series_record["format"] = financial_record["format"]
        
        logger.debug(f"Converted financial record {financial_record['ticker']} to time-series format")
        return time_series_record
    
    def process_record(self, record: Dict[str, Any], record_type: str = "time_series") -> Optional[Dict[str, Any]]:
        """
        Process and normalize a data record.
        
        Args:
            record: Data record to process
            record_type: Type of record
            
        Returns:
            Processed record or None if invalid
        """
        # Convert financial to time-series if needed
        if record_type == "financial":
            record = self.convert_financial_to_time_series(record)
            record_type = "time_series"
        
        # Validate record
        is_valid, error = self.validate_record(record, record_type)
        if not is_valid:
            logger.error(f"Invalid record: {error}")
            return None
        
        # Normalize timestamp
        if "timestamp" in record:
            normalized_ts = self.normalize_timestamp(record["timestamp"])
            if normalized_ts:
                record["timestamp"] = normalized_ts
            else:
                logger.warning(f"Could not normalize timestamp: {record.get('timestamp')}")
        
        return record
    
    def save_record(self, record: Dict[str, Any], key_prefix: str = "data") -> bool:
        """
        Save processed record to storage.
        
        Args:
            record: Processed data record
            key_prefix: Key prefix for storage
            
        Returns:
            True if successful
        """
        if not self.storage:
            logger.warning("No storage backend configured, cannot save record")
            return False
        
        try:
            # Generate storage key
            series_id = record.get("series_id", "unknown")
            timestamp = record.get("timestamp", "unknown").replace(":", "-")
            key = f"{key_prefix}/{series_id}/{timestamp}.json"
            
            # Serialize to JSON
            data = json.dumps(record, indent=2).encode("utf-8")
            
            # Save to storage
            success = self.storage.save(key, data)
            
            if success:
                logger.debug(f"Saved record to {key}")
            
            return success
        except Exception as e:
            logger.error(f"Error saving record: {e}")
            return False
    
    def process_batch(self, records: List[Dict[str, Any]], record_type: str = "time_series") -> List[Dict[str, Any]]:
        """
        Process a batch of records.
        
        Args:
            records: List of records to process
            record_type: Type of records
            
        Returns:
            List of processed records
        """
        processed = []
        
        for i, record in enumerate(records):
            try:
                processed_record = self.process_record(record, record_type)
                if processed_record:
                    processed.append(processed_record)
                else:
                    logger.warning(f"Skipping invalid record at index {i}")
            except Exception as e:
                logger.error(f"Error processing record at index {i}: {e}")
        
        logger.info(f"Processed {len(processed)}/{len(records)} records")
        return processed
