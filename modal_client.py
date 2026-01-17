"""
VARIOSYNC Modal Client Module
Wrapper for calling Modal serverless functions.
"""
import os
from typing import Dict, List, Optional, Any

from logger import get_logger

logger = get_logger()

try:
    import modal
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False
    logger.warning("Modal library not available. Install with: pip install modal")


class ModalClient:
    """Client for calling Modal serverless functions."""
    
    def __init__(self):
        """Initialize Modal client."""
        if not MODAL_AVAILABLE:
            logger.warning("Modal not available. ML functions will not be available.")
            self.available = False
            return
        
        try:
            # Modal functions are deployed separately
            # We'll use Modal's HTTP API or direct function calls
            self.available = True
            logger.info("Modal client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Modal client: {e}")
            self.available = False
    
    def prophet_forecast(
        self,
        data: Dict[str, Any],
        periods: int = 30,
        frequency: str = "D"
    ) -> Optional[Dict[str, Any]]:
        """
        Generate Prophet forecast.
        
        Args:
            data: Dictionary with 'ds' (dates) and 'y' (values) keys
            periods: Number of periods to forecast
            frequency: Frequency of data
            
        Returns:
            Forecast results or None if unavailable
        """
        if not self.available:
            logger.warning("Modal functions not available")
            return None
        
        try:
            # Import Modal app and call function
            # Note: This requires Modal functions to be deployed
            from modal_functions.ml_inference import prophet_forecast
            
            # Call the Modal function
            # In production, this would be: prophet_forecast.remote(...)
            # For now, return None if Modal not configured
            logger.info("Prophet forecast requested via Modal")
            return None  # Placeholder - implement when Modal is deployed
        except Exception as e:
            logger.error(f"Error calling Prophet forecast: {e}")
            return None
    
    def convert_csv_to_parquet(
        self,
        source_path: str,
        destination_path: str,
        chunk_size: int = 100000
    ) -> Optional[Dict[str, Any]]:
        """
        Convert CSV to Parquet using Modal function.
        
        Args:
            source_path: S3/Wasabi path to source CSV
            destination_path: S3/Wasabi path for output Parquet
            chunk_size: Number of rows to process at a time
            
        Returns:
            Conversion results or None if unavailable
        """
        if not self.available:
            logger.warning("Modal functions not available")
            return None
        
        try:
            from modal_functions.data_processing import convert_csv_to_parquet
            
            logger.info(f"CSV to Parquet conversion requested: {source_path} -> {destination_path}")
            return None  # Placeholder - implement when Modal is deployed
        except Exception as e:
            logger.error(f"Error calling CSV conversion: {e}")
            return None
    
    def export_to_format(
        self,
        data_path: str,
        output_path: str,
        format: str = "csv"
    ) -> Optional[Dict[str, Any]]:
        """
        Export data to various formats.
        
        Args:
            data_path: S3/Wasabi path to source data
            output_path: S3/Wasabi path for output
            format: Output format ('csv', 'excel', 'json', 'parquet')
            
        Returns:
            Export results or None if unavailable
        """
        if not self.available:
            logger.warning("Modal functions not available")
            return None
        
        try:
            from modal_functions.batch_exports import export_to_format
            
            logger.info(f"Export requested: {data_path} -> {output_path} ({format})")
            return None  # Placeholder - implement when Modal is deployed
        except Exception as e:
            logger.error(f"Error calling export: {e}")
            return None


class ModalClientFactory:
    """Factory for creating Modal clients."""
    
    _instance: Optional[ModalClient] = None
    
    @staticmethod
    def get_instance() -> Optional[ModalClient]:
        """Get singleton Modal client instance."""
        if ModalClientFactory._instance is None:
            ModalClientFactory._instance = ModalClient()
        return ModalClientFactory._instance if ModalClientFactory._instance.available else None
    
    @staticmethod
    def is_available() -> bool:
        """Check if Modal is available."""
        if not MODAL_AVAILABLE:
            return False
        instance = ModalClientFactory.get_instance()
        return instance is not None and instance.available
