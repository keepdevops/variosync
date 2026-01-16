"""
VARIOSYNC File Loader Module
Main file loader with format detection.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional

from file_formats import FormatHandlers
from logger import get_logger

logger = get_logger()


class FileLoader:
    """Loads time-series data from various file formats."""
    
    @staticmethod
    def detect_format(file_path: str) -> str:
        """
        Detect file format from extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            Format identifier
        """
        ext = Path(file_path).suffix.lower()
        
        format_map = {
            ".json": "json",
            ".csv": "csv",
            ".txt": "txt",
            ".parquet": "parquet",
            ".feather": "feather",
            ".duckdb": "duckdb",
            ".pq": "parquet"
        }
        
        return format_map.get(ext, "json")  # Default to JSON
    
    
    @staticmethod
    def load(file_path: str, file_format: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load data from file, auto-detecting format if not specified.
        
        Args:
            file_path: Path to file
            file_format: Optional format override
            
        Returns:
            List of records
        """
        if file_format is None:
            file_format = FileLoader.detect_format(file_path)
        
        logger.info(f"Loading {file_path} as {file_format} format")
        
        handlers = FormatHandlers()
        
        if file_format == "json":
            return handlers.load_json(file_path)
        elif file_format == "csv":
            return handlers.load_csv(file_path)
        elif file_format == "txt":
            return handlers.load_txt(file_path)
        elif file_format == "parquet":
            return handlers.load_parquet(file_path)
        elif file_format == "feather":
            return handlers.load_feather(file_path)
        elif file_format == "duckdb":
            return handlers.load_duckdb(file_path)
        else:
            logger.warning(f"Unknown format {file_format}, trying JSON")
            return handlers.load_json(file_path)
