"""
VARIOSYNC File Exporter Module
Exports time-series data to various file formats.
"""
from typing import Any, Dict, List, Optional

from .text import TextExporter
from .binary import BinaryExporter
from .specialized import SpecializedExporter

SUPPORTED_FORMATS = {
    "json": {"ext": ".json", "mime": "application/json"},
    "jsonl": {"ext": ".jsonl", "mime": "application/x-ndjson"},
    "csv": {"ext": ".csv", "mime": "text/csv"},
    "txt": {"ext": ".txt", "mime": "text/plain"},
    "parquet": {"ext": ".parquet", "mime": "application/octet-stream"},
    "feather": {"ext": ".feather", "mime": "application/octet-stream"},
    "duckdb": {"ext": ".duckdb", "mime": "application/octet-stream"},
    "xlsx": {"ext": ".xlsx", "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    "xls": {"ext": ".xls", "mime": "application/vnd.ms-excel"},
    "h5": {"ext": ".h5", "mime": "application/x-hdf"},
    "arrow": {"ext": ".arrow", "mime": "application/octet-stream"},
    "avro": {"ext": ".avro", "mime": "application/avro"},
    "orc": {"ext": ".orc", "mime": "application/octet-stream"},
    "msgpack": {"ext": ".msgpack", "mime": "application/x-msgpack"},
    "sqlite": {"ext": ".sqlite", "mime": "application/x-sqlite3"},
    "influxdb": {"ext": ".lp", "mime": "text/plain"},
}


class FileExporter:
    """Exports time-series data to various file formats."""
    
    SUPPORTED_FORMATS = SUPPORTED_FORMATS
    
    @staticmethod
    def get_format_info(format_name: str) -> Optional[Dict[str, str]]:
        """Get format information."""
        return SUPPORTED_FORMATS.get(format_name.lower())
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """Get list of supported export formats."""
        return list(SUPPORTED_FORMATS.keys())
    
    @staticmethod
    def export(data: List[Dict[str, Any]], output_path: str, format: str, **kwargs) -> bool:
        """
        Export data to specified format.
        
        Args:
            data: List of data records
            output_path: Output file path
            format: Export format
            **kwargs: Format-specific options
            
        Returns:
            True if successful
        """
        format_lower = format.lower()
        
        if format_lower in ["json"]:
            return TextExporter.export_to_json(data, output_path, **kwargs)
        elif format_lower in ["jsonl", "ndjson"]:
            return TextExporter.export_to_jsonl(data, output_path)
        elif format_lower == "csv":
            return TextExporter.export_to_csv(data, output_path, **kwargs)
        elif format_lower == "txt":
            return TextExporter.export_to_txt(data, output_path, **kwargs)
        elif format_lower == "parquet":
            return BinaryExporter.export_to_parquet(data, output_path)
        elif format_lower == "feather":
            return BinaryExporter.export_to_feather(data, output_path)
        elif format_lower == "duckdb":
            return BinaryExporter.export_to_duckdb(data, output_path, **kwargs)
        elif format_lower == "xlsx":
            return BinaryExporter.export_to_xlsx(data, output_path)
        elif format_lower == "xls":
            return BinaryExporter.export_to_xls(data, output_path)
        elif format_lower == "h5":
            return BinaryExporter.export_to_h5(data, output_path, **kwargs)
        elif format_lower == "arrow":
            return BinaryExporter.export_to_arrow(data, output_path)
        elif format_lower == "avro":
            return SpecializedExporter.export_to_avro(data, output_path, **kwargs)
        elif format_lower == "orc":
            return SpecializedExporter.export_to_orc(data, output_path)
        elif format_lower == "msgpack":
            return SpecializedExporter.export_to_msgpack(data, output_path)
        elif format_lower == "sqlite":
            return SpecializedExporter.export_to_sqlite(data, output_path, **kwargs)
        elif format_lower in ["influxdb", "lp"]:
            return SpecializedExporter.export_to_influxdb_lp(data, output_path, **kwargs)
        else:
            from logger import get_logger
            logger = get_logger()
            logger.error(f"Unsupported format: {format}")
            return False
