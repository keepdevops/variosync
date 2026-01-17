"""
Data summary statistics generation.
"""
from typing import Any, Dict
import pandas as pd

from logger import get_logger

logger = get_logger()


def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get summary statistics for a DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary with summary statistics
    """
    # Handle dict/list columns that can't be hashed for duplicate detection
    try:
        df_for_dup = df.copy()
        for col in df_for_dup.columns:
            if df_for_dup[col].dtype == 'object':
                non_null_vals = df_for_dup[col].dropna()
                if len(non_null_vals) > 0:
                    sample_val = non_null_vals.iloc[0]
                    if isinstance(sample_val, (dict, list)):
                        df_for_dup[col] = df_for_dup[col].apply(lambda x: str(x) if pd.notna(x) else x)
        
        duplicate_count = df_for_dup.duplicated().sum()
    except Exception as e:
        logger.warning(f"Could not calculate duplicate rows: {e}")
        duplicate_count = 0
    
    summary = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "dtypes": df.dtypes.to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "missing_percentage": (df.isnull().sum() / len(df) * 100).to_dict(),
        "duplicate_rows": duplicate_count,
    }
    
    # Add numeric statistics
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        summary["numeric_stats"] = df[numeric_cols].describe().to_dict()
    
    # Add datetime statistics
    datetime_cols = df.select_dtypes(include=['datetime64']).columns
    if len(datetime_cols) > 0:
        summary["datetime_stats"] = {}
        for col in datetime_cols:
            summary["datetime_stats"][col] = {
                "min": str(df[col].min()),
                "max": str(df[col].max()),
                "range": str(df[col].max() - df[col].min())
            }
    
    return summary
