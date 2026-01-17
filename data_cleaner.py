"""
VARIOSYNC Data Cleaning Module
Provides data cleaning and transformation operations for time-series data.
"""
from typing import Any, Dict, List, Optional
import pandas as pd
from datetime import datetime

from logger import get_logger

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
        cleaned_df = df.copy()
        
        for op in operations:
            op_type = op.get("operation")
            params = op.get("params", {})
            
            try:
                if op_type == "drop_na":
                    # Drop rows with missing values
                    subset = params.get("subset", None)
                    how = params.get("how", "any")  # 'any' or 'all'
                    cleaned_df = cleaned_df.dropna(subset=subset, how=how)
                    
                elif op_type == "fill_na":
                    # Fill missing values
                    method = params.get("method", "ffill")  # 'ffill', 'bfill', 'mean', 'median', 'mode', 'value'
                    value = params.get("value", None)
                    columns = params.get("columns", None)
                    
                    if method == "value" and value is not None:
                        if columns:
                            cleaned_df[columns] = cleaned_df[columns].fillna(value)
                        else:
                            cleaned_df = cleaned_df.fillna(value)
                    elif method in ["mean", "median", "mode"]:
                        if columns:
                            for col in columns:
                                if method == "mean":
                                    cleaned_df[col].fillna(cleaned_df[col].mean(), inplace=True)
                                elif method == "median":
                                    cleaned_df[col].fillna(cleaned_df[col].median(), inplace=True)
                                elif method == "mode":
                                    cleaned_df[col].fillna(cleaned_df[col].mode()[0] if len(cleaned_df[col].mode()) > 0 else 0, inplace=True)
                        else:
                            numeric_cols = cleaned_df.select_dtypes(include=['number']).columns
                            for col in numeric_cols:
                                if method == "mean":
                                    cleaned_df[col].fillna(cleaned_df[col].mean(), inplace=True)
                                elif method == "median":
                                    cleaned_df[col].fillna(cleaned_df[col].median(), inplace=True)
                    else:
                        # Forward fill or backward fill
                        cleaned_df = cleaned_df.fillna(method=method)
                        
                elif op_type == "remove_duplicates":
                    # Remove duplicate rows
                    subset = params.get("subset", None)
                    keep = params.get("keep", "first")  # 'first', 'last', False
                    cleaned_df = cleaned_df.drop_duplicates(subset=subset, keep=keep)
                    
                elif op_type == "remove_outliers":
                    # Remove outliers using IQR method
                    columns = params.get("columns", cleaned_df.select_dtypes(include=['number']).columns.tolist())
                    method = params.get("method", "iqr")  # 'iqr', 'zscore'
                    
                    if method == "iqr":
                        for col in columns:
                            if col in cleaned_df.columns:
                                Q1 = cleaned_df[col].quantile(0.25)
                                Q3 = cleaned_df[col].quantile(0.75)
                                IQR = Q3 - Q1
                                lower_bound = Q1 - 1.5 * IQR
                                upper_bound = Q3 + 1.5 * IQR
                                cleaned_df = cleaned_df[(cleaned_df[col] >= lower_bound) & (cleaned_df[col] <= upper_bound)]
                    elif method == "zscore":
                        threshold = params.get("threshold", 3)
                        for col in columns:
                            if col in cleaned_df.columns:
                                z_scores = abs((cleaned_df[col] - cleaned_df[col].mean()) / cleaned_df[col].std())
                                cleaned_df = cleaned_df[z_scores < threshold]
                                
                elif op_type == "normalize_timestamps":
                    # Normalize timestamp column
                    column = params.get("column", "timestamp")
                    if column in cleaned_df.columns:
                        cleaned_df[column] = pd.to_datetime(cleaned_df[column], errors='coerce')
                        cleaned_df = cleaned_df.dropna(subset=[column])
                        cleaned_df = cleaned_df.sort_values(by=column)
                        
                elif op_type == "filter_rows":
                    # Filter rows based on condition
                    column = params.get("column")
                    condition = params.get("condition")  # e.g., "> 100", "== 'value'"
                    if column and condition:
                        try:
                            cleaned_df = cleaned_df.query(f"{column} {condition}")
                        except:
                            logger.warning(f"Could not apply filter: {column} {condition}")
                            
                elif op_type == "rename_columns":
                    # Rename columns
                    mapping = params.get("mapping", {})
                    cleaned_df = cleaned_df.rename(columns=mapping)
                    
                elif op_type == "drop_columns":
                    # Drop columns
                    columns = params.get("columns", [])
                    cleaned_df = cleaned_df.drop(columns=[c for c in columns if c in cleaned_df.columns], errors='ignore')
                    
                elif op_type == "add_column":
                    # Add new column
                    column = params.get("column")
                    value = params.get("value")
                    expression = params.get("expression")  # e.g., "col1 + col2"
                    
                    if column:
                        if expression:
                            try:
                                cleaned_df[column] = cleaned_df.eval(expression)
                            except:
                                logger.warning(f"Could not evaluate expression: {expression}")
                        elif value is not None:
                            cleaned_df[column] = value
                            
                elif op_type == "convert_type":
                    # Convert column data type
                    column = params.get("column")
                    dtype = params.get("dtype", "float")
                    
                    if column and column in cleaned_df.columns:
                        try:
                            if dtype == "float":
                                cleaned_df[column] = pd.to_numeric(cleaned_df[column], errors='coerce')
                            elif dtype == "int":
                                cleaned_df[column] = pd.to_numeric(cleaned_df[column], errors='coerce').astype('Int64')
                            elif dtype == "datetime":
                                cleaned_df[column] = pd.to_datetime(cleaned_df[column], errors='coerce')
                            elif dtype == "string":
                                cleaned_df[column] = cleaned_df[column].astype(str)
                        except Exception as e:
                            logger.warning(f"Could not convert {column} to {dtype}: {e}")
                            
                elif op_type == "resample":
                    # Resample time-series data
                    column = params.get("column", "timestamp")
                    freq = params.get("freq", "1H")  # '1H', '1D', '1W', etc.
                    method = params.get("method", "mean")  # 'mean', 'sum', 'max', 'min', 'first', 'last'
                    
                    if column in cleaned_df.columns:
                        cleaned_df[column] = pd.to_datetime(cleaned_df[column], errors='coerce')
                        cleaned_df = cleaned_df.set_index(column)
                        cleaned_df = cleaned_df.resample(freq).agg(method)
                        cleaned_df = cleaned_df.reset_index()
                        
                elif op_type == "interpolate":
                    # Interpolate missing values
                    method = params.get("method", "linear")  # 'linear', 'polynomial', 'spline', etc.
                    columns = params.get("columns", None)
                    
                    if columns:
                        for col in columns:
                            if col in cleaned_df.columns:
                                cleaned_df[col] = cleaned_df[col].interpolate(method=method)
                    else:
                        numeric_cols = cleaned_df.select_dtypes(include=['number']).columns
                        for col in numeric_cols:
                            cleaned_df[col] = cleaned_df[col].interpolate(method=method)
                            
                elif op_type == "clip_values":
                    # Clip values to range
                    column = params.get("column")
                    min_val = params.get("min", None)
                    max_val = params.get("max", None)
                    
                    if column and column in cleaned_df.columns:
                        cleaned_df[column] = cleaned_df[column].clip(lower=min_val, upper=max_val)
                        
                elif op_type == "round_values":
                    # Round numeric values
                    columns = params.get("columns", cleaned_df.select_dtypes(include=['number']).columns.tolist())
                    decimals = params.get("decimals", 2)
                    
                    for col in columns:
                        if col in cleaned_df.columns:
                            cleaned_df[col] = cleaned_df[col].round(decimals)
                            
                logger.info(f"Applied operation: {op_type}")
                
            except Exception as e:
                logger.error(f"Error applying operation {op_type}: {e}")
                continue
        
        return cleaned_df
    
    @staticmethod
    def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary statistics for a DataFrame.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        # Handle dict/list columns that can't be hashed for duplicate detection
        # Convert dict/list columns to strings for duplicate checking
        try:
            df_for_dup = df.copy()
            for col in df_for_dup.columns:
                if df_for_dup[col].dtype == 'object':
                    # Check if column contains dicts or lists
                    non_null_vals = df_for_dup[col].dropna()
                    if len(non_null_vals) > 0:
                        sample_val = non_null_vals.iloc[0]
                        if isinstance(sample_val, (dict, list)):
                            # Convert to string representation for duplicate checking
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
