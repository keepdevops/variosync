"""
General-purpose file format converter.
Converts time-series data between any supported formats.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional

from file_loader import FileLoader
from file_exporter import FileExporter
from logger import get_logger

logger = get_logger()


class FormatConverter:
    """Converts time-series data between different file formats."""
    
    @staticmethod
    def detect_format_from_path(file_path: str) -> Optional[str]:
        """
        Detect format from file extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            Format identifier or None if unknown
        """
        ext = Path(file_path).suffix.lower()
        
        # Comprehensive extension mapping
        format_map = {
            # Text formats
            ".json": "json",
            ".jsonl": "jsonl",
            ".ndjson": "jsonl",
            ".csv": "csv",
            ".txt": "txt",
            # Binary formats
            ".parquet": "parquet",
            ".pq": "parquet",
            ".feather": "feather",
            ".arrow": "arrow",
            ".h5": "h5",
            ".hdf5": "h5",
            # Database formats
            ".duckdb": "duckdb",
            ".sqlite": "sqlite",
            ".db": "sqlite",
            # Excel formats
            ".xlsx": "xlsx",
            ".xls": "xls",
            # Specialized formats
            ".avro": "avro",
            ".orc": "orc",
            ".msgpack": "msgpack",
            ".mp": "msgpack",
            # TSDB formats
            ".lp": "influxdb",
            ".tsdb": "opentsdb",
            ".prom": "prometheus",
            # Compression formats
            ".gz": "gzip",
            ".bz2": "bzip2",
            ".zst": "zstandard",
            ".zstd": "zstandard",
            # Archive formats
            ".zip": "zip",
            ".tar": "tar",
            ".tar.gz": "tar",
            ".tar.bz2": "tar",
            # Scientific formats
            ".nc": "netcdf",
            ".netcdf": "netcdf",
            ".cdf": "netcdf",
            ".zarr": "zarr",
            ".fits": "fits",
            ".fit": "fits",
            # Specialized TS formats
            ".tsfile": "tsfile",
            ".td": "tdengine",
            ".vm": "victoriametrics",
            # Protocol buffers
            ".pb": "protobuf",
            ".protobuf": "protobuf",
        }
        
        return format_map.get(ext)
    
    @staticmethod
    def convert(
        input_path: str,
        output_path: str,
        input_format: Optional[str] = None,
        output_format: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Convert file from one format to another.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file
            input_format: Input format (auto-detected if None)
            output_format: Output format (auto-detected from extension if None)
            **kwargs: Format-specific options passed to exporter
            
        Returns:
            True if successful, False otherwise
            
        Example:
            >>> FormatConverter.convert("data.csv", "data.parquet")
            >>> FormatConverter.convert("data.json", "data.gz", output_format="gzip", base_format="json")
        """
        try:
            # Detect input format if not provided
            if input_format is None:
                input_format = FormatConverter.detect_format_from_path(input_path)
                if input_format is None:
                    input_format = FileLoader.detect_format(input_path)
                    logger.warning(f"Could not detect input format from extension, using: {input_format}")
            
            # Detect output format if not provided
            if output_format is None:
                output_format = FormatConverter.detect_format_from_path(output_path)
                if output_format is None:
                    logger.error(f"Could not detect output format from extension: {output_path}")
                    return False
            
            logger.info(f"Converting {input_path} ({input_format}) -> {output_path} ({output_format})")
            
            # Load data from input format
            loader = FileLoader()
            data = loader.load(input_path, file_format=input_format)
            
            if not data:
                logger.warning(f"No data loaded from {input_path}")
                return False
            
            logger.info(f"Loaded {len(data)} records from {input_format} format")
            
            # Export data to output format
            exporter = FileExporter()
            success = exporter.export(data, output_path, format=output_format, **kwargs)
            
            if success:
                logger.info(f"Successfully converted {len(data)} records from {input_format} to {output_format}")
            else:
                logger.error(f"Failed to export data to {output_format} format")
            
            return success
            
        except Exception as e:
            logger.error(f"Error converting file formats: {e}")
            return False
    
    @staticmethod
    def get_supported_formats() -> Dict[str, List[str]]:
        """
        Get list of supported formats grouped by category.
        
        Returns:
            Dictionary mapping categories to format lists
        """
        exporter = FileExporter()
        all_formats = exporter.get_supported_formats()
        
        categories = {
            "text": ["json", "jsonl", "csv", "txt"],
            "binary": ["parquet", "feather", "arrow", "h5"],
            "database": ["duckdb", "sqlite"],
            "excel": ["xlsx", "xls"],
            "specialized": ["avro", "orc", "msgpack", "protobuf"],
            "tsdb": ["influxdb", "opentsdb", "prometheus"],
            "compression": ["gzip", "bzip2", "zstandard"],
            "scientific": ["netcdf", "zarr", "fits"],
            "specialized_ts": ["tsfile", "tdengine", "victoriametrics"]
        }
        
        result = {}
        for category, formats in categories.items():
            result[category] = [f for f in formats if f in all_formats]
        
        return result
    
    @staticmethod
    def is_conversion_supported(input_format: str, output_format: str) -> bool:
        """
        Check if conversion between two formats is supported.
        
        Args:
            input_format: Input format identifier
            output_format: Output format identifier
            
        Returns:
            True if conversion is supported
        """
        exporter = FileExporter()
        loader = FileLoader()
        
        supported_inputs = ["json", "csv", "txt", "parquet", "feather", "duckdb"]  # Formats FileLoader supports
        supported_outputs = exporter.get_supported_formats()
        
        return input_format.lower() in supported_inputs and output_format.lower() in supported_outputs
