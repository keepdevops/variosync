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
        logger.debug(f"[FileLoader.load] Starting load for file: {file_path}")

        # Validate file path
        if not file_path:
            logger.error("[FileLoader.load] Empty file path provided")
            return []

        # Check file existence
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            logger.error(f"[FileLoader.load] File does not exist: {file_path}")
            return []

        if not file_path_obj.is_file():
            logger.error(f"[FileLoader.load] Path is not a file: {file_path}")
            return []

        # Check file size
        file_size = file_path_obj.stat().st_size
        logger.info(f"[FileLoader.load] File size: {file_size} bytes ({file_size / 1024:.2f} KB)")

        if file_size == 0:
            logger.warning(f"[FileLoader.load] File is empty: {file_path}")
            return []

        if file_format is None:
            file_format = FileLoader.detect_format(file_path)
            logger.debug(f"[FileLoader.load] Auto-detected format: {file_format}")

        if file_format is None:
            logger.warning(f"[FileLoader.load] Could not detect format for {file_path}, trying JSON")
            file_format = "json"

        logger.info(f"[FileLoader.load] Loading {file_path} as {file_format} format")
        
        handlers = FormatHandlers()

        def validate_and_log_records(records: List[Dict[str, Any]], format_name: str) -> List[Dict[str, Any]]:
            """Validate loaded records and log details."""
            if records is None:
                logger.error(f"[FileLoader.load] {format_name} handler returned None")
                return []

            if not isinstance(records, list):
                logger.error(f"[FileLoader.load] {format_name} handler returned non-list: {type(records)}")
                return []

            logger.info(f"[FileLoader.load] Loaded {len(records)} records from {format_name} format")

            if len(records) == 0:
                logger.warning(f"[FileLoader.load] No records found in {format_name} file")
                return []

            # Log sample record structure
            sample = records[0]
            if isinstance(sample, dict):
                keys = list(sample.keys())
                logger.debug(f"[FileLoader.load] Sample record keys: {keys[:10]}{'...' if len(keys) > 10 else ''}")

                # Check for common required fields
                has_timestamp = 'timestamp' in sample or 'date' in sample or 'time' in sample
                has_measurements = 'measurements' in sample
                logger.debug(f"[FileLoader.load] Has timestamp field: {has_timestamp}, Has measurements: {has_measurements}")
            else:
                logger.warning(f"[FileLoader.load] First record is not a dict: {type(sample)}")

            return records

        # Direct load formats
        if file_format == "json":
            records = handlers.load_json(file_path)
            return validate_and_log_records(records, "JSON")
        elif file_format == "jsonl" or file_format == "ndjson":
            # JSONL is one JSON object per line
            try:
                records = []
                line_count = 0
                error_lines = []
                with open(file_path, "r", encoding="utf-8") as f:
                    import json
                    for line_num, line in enumerate(f, 1):
                        line_count += 1
                        line = line.strip()
                        if line:
                            try:
                                records.append(json.loads(line))
                            except json.JSONDecodeError as je:
                                error_lines.append(line_num)
                                logger.debug(f"[FileLoader.load] JSONL parse error at line {line_num}: {je}")

                logger.info(f"[FileLoader.load] JSONL: processed {line_count} lines, loaded {len(records)} records")
                if error_lines:
                    logger.warning(f"[FileLoader.load] JSONL: {len(error_lines)} lines failed to parse")
                return validate_and_log_records(records, "JSONL")
            except Exception as e:
                logger.error(f"[FileLoader.load] Error loading JSONL file: {e}", exc_info=True)
                return []
        elif file_format == "csv":
            records = handlers.load_csv(file_path)
            return validate_and_log_records(records, "CSV")
        elif file_format == "txt":
            records = handlers.load_txt(file_path)
            return validate_and_log_records(records, "TXT")
        elif file_format == "stooq":
            records = handlers.load_stooq(file_path)
            return validate_and_log_records(records, "Stooq")
        elif file_format == "parquet":
            records = handlers.load_parquet(file_path)
            return validate_and_log_records(records, "Parquet")
        elif file_format == "feather":
            records = handlers.load_feather(file_path)
            return validate_and_log_records(records, "Feather")
        elif file_format == "duckdb":
            records = handlers.load_duckdb(file_path)
            return validate_and_log_records(records, "DuckDB")
        elif file_format == "arrow":
            # Arrow format - try using pandas/pyarrow
            try:
                import pandas as pd
                logger.debug(f"[FileLoader.load] Loading Arrow format from {file_path}")
                df = pd.read_feather(file_path) if file_path.endswith('.arrow') else pd.read_parquet(file_path)
                logger.debug(f"[FileLoader.load] Arrow DataFrame shape: {df.shape}, columns: {list(df.columns)}")
                records = df.to_dict('records')
                return validate_and_log_records(records, "Arrow")
            except Exception as e:
                logger.error(f"[FileLoader.load] Error loading Arrow format: {e}", exc_info=True)
                return []
        elif file_format == "h5" or file_format == "hdf5":
            # HDF5 format - try using pandas
            try:
                import pandas as pd
                logger.debug(f"[FileLoader.load] Loading HDF5 format from {file_path}")
                # Try to read first key/table
                with pd.HDFStore(file_path, 'r') as store:
                    keys = store.keys()
                    logger.debug(f"[FileLoader.load] HDF5 keys found: {keys}")
                    if keys:
                        df = pd.read_hdf(file_path, key=keys[0])
                        logger.debug(f"[FileLoader.load] HDF5 DataFrame shape: {df.shape}")
                        records = df.to_dict('records')
                        return validate_and_log_records(records, "HDF5")
                logger.warning(f"[FileLoader.load] No keys found in HDF5 file")
                return []
            except Exception as e:
                logger.error(f"[FileLoader.load] Error loading HDF5 format: {e}", exc_info=True)
                return []
        elif file_format == "xlsx":
            # Excel XLSX format
            try:
                import pandas as pd
                logger.debug(f"[FileLoader.load] Loading XLSX format from {file_path}")
                df = pd.read_excel(file_path, engine='openpyxl')
                logger.debug(f"[FileLoader.load] XLSX DataFrame shape: {df.shape}, columns: {list(df.columns)}")
                records = df.to_dict('records')
                return validate_and_log_records(records, "XLSX")
            except Exception as e:
                logger.error(f"[FileLoader.load] Error loading XLSX format: {e}", exc_info=True)
                return []
        elif file_format == "xls":
            # Excel XLS format
            try:
                import pandas as pd
                logger.debug(f"[FileLoader.load] Loading XLS format from {file_path}")
                df = pd.read_excel(file_path, engine='xlrd')
                logger.debug(f"[FileLoader.load] XLS DataFrame shape: {df.shape}, columns: {list(df.columns)}")
                records = df.to_dict('records')
                return validate_and_log_records(records, "XLS")
            except Exception as e:
                logger.error(f"[FileLoader.load] Error loading XLS format: {e}", exc_info=True)
                return []
        elif file_format == "sqlite":
            # SQLite format - try using pandas
            try:
                import pandas as pd
                import sqlite3
                logger.debug(f"[FileLoader.load] Loading SQLite format from {file_path}")
                conn = sqlite3.connect(file_path)
                # Try to read first table
                tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
                logger.debug(f"[FileLoader.load] SQLite tables found: {list(tables['name']) if not tables.empty else []}")
                if not tables.empty:
                    table_name = tables.iloc[0]['name']
                    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                    logger.debug(f"[FileLoader.load] SQLite DataFrame shape: {df.shape}")
                    records = df.to_dict('records')
                    conn.close()
                    return validate_and_log_records(records, "SQLite")
                conn.close()
                logger.warning(f"[FileLoader.load] No tables found in SQLite database")
                return []
            except Exception as e:
                logger.error(f"[FileLoader.load] Error loading SQLite format: {e}", exc_info=True)
                return []
        # Compression/archive formats - decompress first
        elif file_format in ["gzip", "gz", "bzip2", "bz2", "zstandard", "zst", "zstd", "zip", "tar"]:
            try:
                logger.debug(f"[FileLoader.load] Handling compressed format: {file_format}")
                # Lazy import to avoid circular dependency
                from format_converter import FormatConverter

                # Use FormatConverter to handle decompression and conversion
                temp_json = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
                temp_json_path = temp_json.name
                temp_json.close()

                # Convert compressed file to JSON first, then load
                logger.debug(f"[FileLoader.load] Decompressing to temp file: {temp_json_path}")
                if FormatConverter.convert(file_path, temp_json_path, input_format=file_format, output_format="json"):
                    records = handlers.load_json(temp_json_path)
                    os.unlink(temp_json_path)
                    return validate_and_log_records(records, f"Compressed ({file_format})")
                else:
                    logger.error(f"[FileLoader.load] Failed to decompress/convert {file_format} file")
                    if os.path.exists(temp_json_path):
                        os.unlink(temp_json_path)
                    return []
            except Exception as e:
                logger.error(f"[FileLoader.load] Error handling compressed file {file_format}: {e}", exc_info=True)
                return []
        # TSDB formats - try to load as text first
        elif file_format in ["influxdb", "lp", "opentsdb", "tsdb", "prometheus", "prom"]:
            # These are mostly export formats, but we can try to parse them
            logger.warning(f"[FileLoader.load] TSDB format {file_format} is primarily for export. Attempting to parse as text.")
            records = handlers.load_txt(file_path, delimiter=",")
            return validate_and_log_records(records, f"TSDB ({file_format})")
        # Scientific formats - try using specialized handlers if available
        elif file_format in ["netcdf", "nc", "zarr", "fits", "fit"]:
            logger.warning(f"[FileLoader.load] Scientific format {file_format} may require specialized handling")
            # Try as text first, then fall back
            records = handlers.load_txt(file_path)
            return validate_and_log_records(records, f"Scientific ({file_format})")
        else:
            logger.warning(f"[FileLoader.load] Unknown format {file_format}, trying JSON")
            records = handlers.load_json(file_path)
            return validate_and_log_records(records, f"Unknown ({file_format})")
