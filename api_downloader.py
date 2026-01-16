"""
VARIOSYNC API Downloader Module
Handles downloading data from various APIs (financial, weather, metrics, etc.).
"""
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import requests

from config_validator import ConfigValidator
from data_processor import TimeSeriesProcessor
from logger import get_logger
from storage_base import StorageBackend

logger = get_logger()


class APIDownloader:
    """Generic API downloader for time-series data."""
    
    def __init__(self, config: Dict[str, Any], storage: Optional[StorageBackend] = None):
        """
        Initialize API downloader.
        
        Args:
            config: API downloader configuration
            storage: Optional storage backend
        """
        self.config = config
        self.storage = storage
        self.processor = TimeSeriesProcessor(storage)
        self.validator = ConfigValidator()
        
        # Validate required config fields
        required_fields = ["name", "base_url", "endpoint", "api_key"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required config field: {field}")
        
        self.name = config["name"]
        self.base_url = config["base_url"]
        self.endpoint = config["endpoint"]
        self.api_key = config["api_key"]
        self.api_key_param = config.get("api_key_param", "apikey")
        self.entity_param = config.get("entity_param", "symbol")
        self.start_date_param = config.get("start_date_param", "from")
        self.end_date_param = config.get("end_date_param", "to")
        self.date_format = config.get("date_format", "YYYY-MM-DD")
        self.response_format = config.get("response_format", "json")
        self.data_path = config.get("data_path", "data")
        self.column_mapping = config.get("column_mapping", {})
        self.api_client = APIClient(config)
        
        logger.info(f"Initialized API downloader: {self.name}")
    
    
    def _format_date(self, date: datetime) -> str:
        """
        Format date according to API requirements.
        
        Args:
            date: Datetime object
            
        Returns:
            Formatted date string
        """
        if self.date_format == "YYYY-MM-DD":
            return date.strftime("%Y-%m-%d")
        elif self.date_format == "unix":
            return str(int(date.timestamp()))
        elif self.date_format == "YYYYMMDD":
            return date.strftime("%Y%m%d")
        else:
            return date.isoformat()
    
    def _build_url(self, entity_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> str:
        """
        Build API request URL.
        
        Args:
            entity_id: Entity/series identifier
            start_date: Start date
            end_date: End date
            
        Returns:
            Complete API URL
        """
        params = {
            self.api_key_param: self.api_key,
            self.entity_param: entity_id
        }
        
        if start_date:
            params[self.start_date_param] = self._format_date(start_date)
        
        if end_date:
            params[self.end_date_param] = self._format_date(end_date)
        
        if self.response_format:
            params["format"] = self.response_format
        
        url = f"{self.base_url}{self.endpoint}?{urlencode(params)}"
        return url
    
    def _map_columns(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map API column names to standardized format.
        
        Args:
            record: API response record
            
        Returns:
            Mapped record
        """
        mapped = {}
        
        for api_key, std_key in self.column_mapping.items():
            if api_key in record:
                mapped[std_key] = record[api_key]
        
        # Include unmapped fields
        for key, value in record.items():
            if key not in self.column_mapping:
                mapped[key] = value
        
        return mapped
    
    def _extract_data(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract data array from API response.
        
        Args:
            response_data: API response dictionary
            
        Returns:
            List of data records
        """
        if not self.data_path or self.data_path == "data":
            # Try common data locations
            if "data" in response_data:
                return response_data["data"]
            elif "results" in response_data:
                return response_data["results"]
            elif "values" in response_data:
                return response_data["values"]
            else:
                # Return entire response if it's a list
                if isinstance(response_data, list):
                    return response_data
                else:
                    logger.warning("Could not find data array in response")
                    return []
        else:
            # Navigate nested path
            keys = self.data_path.split(".")
            current = response_data
            
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    logger.warning(f"Could not navigate path {self.data_path}")
                    return []
            
            if isinstance(current, list):
                return current
            else:
                return [current] if current else []
    
    def download(
        self,
        entity_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_retries: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Download data from API.
        
        Args:
            entity_id: Entity/series identifier
            start_date: Start date
            end_date: End date
            max_retries: Maximum retry attempts
            
        Returns:
            List of downloaded records
        """
        url = self._build_url(entity_id, start_date, end_date)
        
        logger.info(f"Downloading data for {entity_id}")
        data = self.api_client.get(url, max_retries)
        
        if not data:
            return []
        
        if self.response_format != "json":
            logger.error(f"Unsupported response format: {self.response_format}")
            return []
        
        # Extract data array
        records = self._extract_data(data)
        
        # Map columns
        mapped_records = []
        for record in records:
            mapped = self._map_columns(record)
            mapped_records.append(mapped)
        
        logger.info(f"Downloaded {len(mapped_records)} records for {entity_id}")
        return mapped_records
    
    def download_and_save(
        self,
        entity_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> bool:
        """
        Download data and save to storage.
        
        Args:
            entity_id: Entity/series identifier
            start_date: Start date
            end_date: End date
            
        Returns:
            True if successful
        """
        records = self.download(entity_id, start_date, end_date)
        
        if not records:
            logger.warning(f"No records downloaded for {entity_id}")
            return False
        
        # Process and save records
        processed = self.processor.process_batch(records, "time_series")
        
        success_count = 0
        for record in processed:
            if self.processor.save_record(record, f"api/{self.name}"):
                success_count += 1
        
        logger.info(f"Saved {success_count}/{len(processed)} records for {entity_id}")
        return success_count > 0
