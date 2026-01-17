"""
VARIOSYNC Data Cleaning Module
Provides data cleaning and transformation operations for time-series data.
"""
from typing import Any, Dict, List, Optional
import pandas as pd

from logger import get_logger
from .operations import DataCleanerOperations
from .summary import get_data_summary

logger = get_logger()


class DataCleaner:
    """Data cleaning and transformation operations."""
    
    @staticmethod
    def clean_dataframe(df: pd.DataFrame, operations: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Apply cleaning operations to a DataFrame.
        
        Args:
            df: Input DataFrame
            operations: List of cleaning operations
            
        Returns:
            Cleaned DataFrame
        """
        return DataCleanerOperations.apply_operations(df, operations)
    
    @staticmethod
    def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary statistics for a DataFrame.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        return get_data_summary(df)
