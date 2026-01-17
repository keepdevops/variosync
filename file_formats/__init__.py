"""
VARIOSYNC File Format Handlers Module
Handles loading data from specific file formats.
"""
from .text import TextFormatHandlers
from .binary import BinaryFormatHandlers
from .converters import FormatConverters

from logger import get_logger

logger = get_logger()


class FormatHandlers:
    """Handlers for different file formats."""
    
    @staticmethod
    def load_json(file_path: str) -> list:
        """Load data from JSON file."""
        return TextFormatHandlers.load_json(file_path)
    
    @staticmethod
    def load_csv(file_path: str, has_header: bool = True) -> list:
        """Load data from CSV file."""
        return TextFormatHandlers.load_csv(file_path, has_header)
    
    @staticmethod
    def load_txt(file_path: str, delimiter: str = "\t") -> list:
        """Load data from TXT file."""
        return TextFormatHandlers.load_txt(file_path, delimiter)
    
    @staticmethod
    def load_parquet(file_path: str) -> list:
        """Load data from Parquet file."""
        return BinaryFormatHandlers.load_parquet(file_path)
    
    @staticmethod
    def load_feather(file_path: str) -> list:
        """Load data from Feather file."""
        return BinaryFormatHandlers.load_feather(file_path)
    
    @staticmethod
    def load_duckdb(file_path: str, table_name: str = "time_series_data") -> list:
        """Load data from DuckDB file."""
        return BinaryFormatHandlers.load_duckdb(file_path, table_name)
    
    @staticmethod
    def convert_csv_to_duckdb(
        csv_file_path: str,
        duckdb_file_path: str,
        table_name: str = "time_series_data",
        has_header: bool = True,
        if_exists: str = "replace"
    ) -> bool:
        """Convert CSV file to DuckDB format."""
        return FormatConverters.convert_csv_to_duckdb(
            csv_file_path, duckdb_file_path, table_name, has_header, if_exists
        )
    
    @staticmethod
    def convert_to_plotly_format(
        input_file_path: str,
        output_file_path: str,
        output_format: str = "json",
        normalize_measurements: bool = True
    ) -> bool:
        """Convert any supported file format to a Plotly-friendly format."""
        return FormatConverters.convert_to_plotly_format(
            input_file_path, output_file_path, output_format, normalize_measurements
        )
