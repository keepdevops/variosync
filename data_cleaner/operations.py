"""
Data cleaning operations implementation.
"""
from typing import Any, Dict, List
import pandas as pd

from logger import get_logger

logger = get_logger()


class DataCleanerOperations:
    """Data cleaning operations."""
    
    @staticmethod
    def apply_operations(df: pd.DataFrame, operations: List[Dict[str, Any]]) -> pd.DataFrame:
        """Apply cleaning operations to a DataFrame."""
        cleaned_df = df.copy()
        
        for op in operations:
            op_type = op.get("operation")
            params = op.get("params", {})
            
            try:
                if op_type == "drop_na":
                    cleaned_df = DataCleanerOperations._drop_na(cleaned_df, params)
                elif op_type == "fill_na":
                    cleaned_df = DataCleanerOperations._fill_na(cleaned_df, params)
                elif op_type == "remove_duplicates":
                    cleaned_df = DataCleanerOperations._remove_duplicates(cleaned_df, params)
                elif op_type == "remove_outliers":
                    cleaned_df = DataCleanerOperations._remove_outliers(cleaned_df, params)
                elif op_type == "normalize_timestamps":
                    cleaned_df = DataCleanerOperations._normalize_timestamps(cleaned_df, params)
                elif op_type == "filter_rows":
                    cleaned_df = DataCleanerOperations._filter_rows(cleaned_df, params)
                elif op_type == "rename_columns":
                    cleaned_df = DataCleanerOperations._rename_columns(cleaned_df, params)
                elif op_type == "drop_columns":
                    cleaned_df = DataCleanerOperations._drop_columns(cleaned_df, params)
                elif op_type == "add_column":
                    cleaned_df = DataCleanerOperations._add_column(cleaned_df, params)
                elif op_type == "convert_type":
                    cleaned_df = DataCleanerOperations._convert_type(cleaned_df, params)
                elif op_type == "resample":
                    cleaned_df = DataCleanerOperations._resample(cleaned_df, params)
                elif op_type == "interpolate":
                    cleaned_df = DataCleanerOperations._interpolate(cleaned_df, params)
                elif op_type == "clip_values":
                    cleaned_df = DataCleanerOperations._clip_values(cleaned_df, params)
                elif op_type == "round_values":
                    cleaned_df = DataCleanerOperations._round_values(cleaned_df, params)
                
                logger.info(f"Applied operation: {op_type}")
                
            except Exception as e:
                logger.error(f"Error applying operation {op_type}: {e}")
                continue
        
        return cleaned_df
    
    @staticmethod
    def _drop_na(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Drop rows with missing values."""
        subset = params.get("subset", None)
        how = params.get("how", "any")
        return df.dropna(subset=subset, how=how)
    
    @staticmethod
    def _fill_na(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Fill missing values."""
        method = params.get("method", "ffill")
        value = params.get("value", None)
        columns = params.get("columns", None)
        
        if method == "value" and value is not None:
            if columns:
                df[columns] = df[columns].fillna(value)
            else:
                df = df.fillna(value)
        elif method in ["mean", "median", "mode"]:
            if columns:
                for col in columns:
                    if method == "mean":
                        df[col].fillna(df[col].mean(), inplace=True)
                    elif method == "median":
                        df[col].fillna(df[col].median(), inplace=True)
                    elif method == "mode":
                        df[col].fillna(df[col].mode()[0] if len(df[col].mode()) > 0 else 0, inplace=True)
            else:
                numeric_cols = df.select_dtypes(include=['number']).columns
                for col in numeric_cols:
                    if method == "mean":
                        df[col].fillna(df[col].mean(), inplace=True)
                    elif method == "median":
                        df[col].fillna(df[col].median(), inplace=True)
        else:
            df = df.fillna(method=method)
        
        return df
    
    @staticmethod
    def _remove_duplicates(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Remove duplicate rows."""
        subset = params.get("subset", None)
        keep = params.get("keep", "first")
        return df.drop_duplicates(subset=subset, keep=keep)
    
    @staticmethod
    def _remove_outliers(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Remove outliers."""
        columns = params.get("columns", df.select_dtypes(include=['number']).columns.tolist())
        method = params.get("method", "iqr")
        
        if method == "iqr":
            for col in columns:
                if col in df.columns:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
        elif method == "zscore":
            threshold = params.get("threshold", 3)
            for col in columns:
                if col in df.columns:
                    z_scores = abs((df[col] - df[col].mean()) / df[col].std())
                    df = df[z_scores < threshold]
        
        return df
    
    @staticmethod
    def _normalize_timestamps(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Normalize timestamp column."""
        column = params.get("column", "timestamp")
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors='coerce')
            df = df.dropna(subset=[column])
            df = df.sort_values(by=column)
        return df
    
    @staticmethod
    def _filter_rows(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Filter rows based on condition."""
        column = params.get("column")
        condition = params.get("condition")
        if column and condition:
            try:
                df = df.query(f"{column} {condition}")
            except:
                logger.warning(f"Could not apply filter: {column} {condition}")
        return df
    
    @staticmethod
    def _rename_columns(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Rename columns."""
        mapping = params.get("mapping", {})
        return df.rename(columns=mapping)
    
    @staticmethod
    def _drop_columns(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Drop columns."""
        columns = params.get("columns", [])
        return df.drop(columns=[c for c in columns if c in df.columns], errors='ignore')
    
    @staticmethod
    def _add_column(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Add new column."""
        column = params.get("column")
        value = params.get("value")
        expression = params.get("expression")
        
        if column:
            if expression:
                try:
                    df[column] = df.eval(expression)
                except:
                    logger.warning(f"Could not evaluate expression: {expression}")
            elif value is not None:
                df[column] = value
        
        return df
    
    @staticmethod
    def _convert_type(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Convert column data type."""
        column = params.get("column")
        dtype = params.get("dtype", "float")
        
        if column and column in df.columns:
            try:
                if dtype == "float":
                    df[column] = pd.to_numeric(df[column], errors='coerce')
                elif dtype == "int":
                    df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
                elif dtype == "datetime":
                    df[column] = pd.to_datetime(df[column], errors='coerce')
                elif dtype == "string":
                    df[column] = df[column].astype(str)
            except Exception as e:
                logger.warning(f"Could not convert {column} to {dtype}: {e}")
        
        return df
    
    @staticmethod
    def _resample(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Resample time-series data."""
        column = params.get("column", "timestamp")
        freq = params.get("freq", "1H")
        method = params.get("method", "mean")
        
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors='coerce')
            df = df.set_index(column)
            df = df.resample(freq).agg(method)
            df = df.reset_index()
        
        return df
    
    @staticmethod
    def _interpolate(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Interpolate missing values."""
        method = params.get("method", "linear")
        columns = params.get("columns", None)
        
        if columns:
            for col in columns:
                if col in df.columns:
                    df[col] = df[col].interpolate(method=method)
        else:
            numeric_cols = df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                df[col] = df[col].interpolate(method=method)
        
        return df
    
    @staticmethod
    def _clip_values(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Clip values to range."""
        column = params.get("column")
        min_val = params.get("min", None)
        max_val = params.get("max", None)
        
        if column and column in df.columns:
            df[column] = df[column].clip(lower=min_val, upper=max_val)
        
        return df
    
    @staticmethod
    def _round_values(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Round numeric values."""
        columns = params.get("columns", df.select_dtypes(include=['number']).columns.tolist())
        decimals = params.get("decimals", 2)
        
        for col in columns:
            if col in df.columns:
                df[col] = df[col].round(decimals)
        
        return df
