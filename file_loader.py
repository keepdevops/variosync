"""
VARIOSYNC File Loader Module
Main file loader with format detection.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import tempfile
import os

from file_formats import FormatHandlers
from logger import get_logger

logger = get_logger()


class FileLoader:
    """Loads time-series data from various file formats."""
    
    @staticmethod
    def detect_format(file_path: str) -> Optional[str]:
        """
        Detect file format from extension using comprehensive format detection.
        
        Args:
            file_path: Path to file
            
        Returns:
            Format identifier or None if unknown
        """
        ext = Path(file_path).suffix.lower()
        
        # Comprehensive extension mapping (matching FileExporter supported formats)
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
            # Database export formats
            ".sql": "timescaledb",  # Could be TimescaleDB or QuestDB
            ".ilp": "questdb",
        }
        
        return format_map.get(ext)
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """
        Get list of formats that can be loaded.
        
        Returns:
            List of supported format identifiers
        """
        # Formats that can be directly loaded
        direct_load_formats = [
            "json", "jsonl", "csv", "txt", "stooq",
            "parquet", "feather", "duckdb", "arrow", "h5",
            "xlsx", "xls", "avro", "orc", "msgpack", "sqlite"
        ]
        
        # Formats that need conversion (compression/archive formats)
        # These are handled via FormatConverter
        conversion_formats = [
            "gzip", "bzip2", "zstandard", "zip", "tar"
        ]
        
        # TSDB formats (text-based, can be loaded)
        tsdb_formats = [
            "influxdb", "opentsdb", "prometheus"
        ]
        
        # Scientific formats
        scientific_formats = [
            "netcdf", "zarr", "fits"
        ]
        
        # Specialized TS formats (mostly export-only, but some can be loaded)
        specialized_ts_formats = [
            "tsfile", "tdengine", "victoriametrics"
        ]
        
        # Database formats
        database_formats = [
            "timescaledb", "questdb"
        ]
        
        # Protocol formats
        protocol_formats = [
            "protobuf"
        ]
        
        return (
            direct_load_formats +
            conversion_formats +
            tsdb_formats +
            scientific_formats +
            specialized_ts_formats +
            database_formats +
            protocol_formats
        )
    
    
    @staticmethod
    def load(file_path: str, file_format: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load data from file, auto-detecting format if not specified.
        Supports all formats that FileExporter supports.
        
        Args:
            file_path: Path to file
            file_format: Optional format override
            
        Returns:
            List of records
        """
        if file_format is None:
            file_format = FileLoader.detect_format(file_path)
        
        if file_format is None:
            logger.warning(f"Could not detect format for {file_path}, trying JSON")
            file_format = "json"
        
        logger.info(f"Loading {file_path} as {file_format} format")
        
        handlers = FormatHandlers()
        
        # Direct load formats
        if file_format == "json":
            return handlers.load_json(file_path)
        elif file_format == "jsonl" or file_format == "ndjson":
            # JSONL is one JSON object per line
            try:
                records = []
                with open(file_path, "r", encoding="utf-8") as f:
                    import json
                    for line in f:
                        line = line.strip()
                        if line:
                            records.append(json.loads(line))
                logger.info(f"Loaded {len(records)} records from JSONL file")
                return records
            except Exception as e:
                logger.error(f"Error loading JSONL file: {e}")
                return []
        elif file_format == "csv":
            return handlers.load_csv(file_path)
        elif file_format == "txt":
            return handlers.load_txt(file_path)
        elif file_format == "stooq":
            return handlers.load_stooq(file_path)
        elif file_format == "parquet":
            return handlers.load_parquet(file_path)
        elif file_format == "feather":
            return handlers.load_feather(file_path)
        elif file_format == "duckdb":
            return handlers.load_duckdb(file_path)
        elif file_format == "arrow":
            # Arrow format - try using pandas/pyarrow
            try:
                import pandas as pd
                df = pd.read_feather(file_path) if file_path.endswith('.arrow') else pd.read_parquet(file_path)
                records = df.to_dict('records')
                logger.info(f"Loaded {len(records)} records from Arrow format")
                return records
            except Exception as e:
                logger.error(f"Error loading Arrow format: {e}")
                return []
        elif file_format == "h5" or file_format == "hdf5":
            # HDF5 format - try using pandas
            try:
                import pandas as pd
                # Try to read first key/table
                with pd.HDFStore(file_path, 'r') as store:
                    keys = store.keys()
                    if keys:
                        df = pd.read_hdf(file_path, key=keys[0])
                        records = df.to_dict('records')
                        logger.info(f"Loaded {len(records)} records from HDF5 format")
                        return records
                return []
            except Exception as e:
                logger.error(f"Error loading HDF5 format: {e}")
                return []
        elif file_format == "xlsx":
            # Excel XLSX format
            try:
                import pandas as pd
                df = pd.read_excel(file_path, engine='openpyxl')
                records = df.to_dict('records')
                logger.info(f"Loaded {len(records)} records from XLSX format")
                return records
            except Exception as e:
                logger.error(f"Error loading XLSX format: {e}")
                return []
        elif file_format == "xls":
            # Excel XLS format
            try:
                import pandas as pd
                df = pd.read_excel(file_path, engine='xlrd')
                records = df.to_dict('records')
                logger.info(f"Loaded {len(records)} records from XLS format")
                return records
            except Exception as e:
                logger.error(f"Error loading XLS format: {e}")
                return []
        elif file_format == "sqlite":
            # SQLite format - try using pandas
            try:
                import pandas as pd
                import sqlite3
                conn = sqlite3.connect(file_path)
                # Try to read first table
                tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
                if not tables.empty:
                    table_name = tables.iloc[0]['name']
                    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                    records = df.to_dict('records')
                    conn.close()
                    logger.info(f"Loaded {len(records)} records from SQLite format")
                    return records
                conn.close()
                return []
            except Exception as e:
                logger.error(f"Error loading SQLite format: {e}")
                return []
        # Compression/archive formats - decompress first
        elif file_format in ["gzip", "gz", "bzip2", "bz2", "zstandard", "zst", "zstd", "zip", "tar"]:
            try:
                # Lazy import to avoid circular dependency
                from format_converter import FormatConverter
                
                # Use FormatConverter to handle decompression and conversion
                temp_json = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
                temp_json_path = temp_json.name
                temp_json.close()
                
                # Convert compressed file to JSON first, then load
                if FormatConverter.convert(file_path, temp_json_path, input_format=file_format, output_format="json"):
                    records = handlers.load_json(temp_json_path)
                    os.unlink(temp_json_path)
                    return records
                else:
                    logger.error(f"Failed to decompress/convert {file_format} file")
                    if os.path.exists(temp_json_path):
                        os.unlink(temp_json_path)
                    return []
            except Exception as e:
                logger.error(f"Error handling compressed file {file_format}: {e}")
                return []
        # TSDB formats - try to load as text first
        elif file_format in ["influxdb", "lp", "opentsdb", "tsdb", "prometheus", "prom"]:
            # These are mostly export formats, but we can try to parse them
            logger.warning(f"TSDB format {file_format} is primarily for export. Attempting to parse as text.")
            return handlers.load_txt(file_path, delimiter=",")
        # Scientific formats - try using specialized handlers if available
        elif file_format in ["netcdf", "nc", "zarr", "fits", "fit"]:
            logger.warning(f"Scientific format {file_format} may require specialized handling")
            # Try as text first, then fall back
            return handlers.load_txt(file_path)
        else:
            logger.warning(f"Unknown format {file_format}, trying JSON")
            return handlers.load_json(file_path)
