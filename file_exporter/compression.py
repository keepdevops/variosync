"""
Compression format exporters (Gzip, Bzip2, Zstandard).
These formats compress text-based data formats like JSON, CSV, TXT.
"""
import gzip
import bz2
import json
import csv
import io
from typing import Any, Dict, List, Optional, Callable

from logger import get_logger

logger = get_logger()


class CompressionExporter:
    """Compression format exporters."""
    
    @staticmethod
    def _prepare_json_data(data: List[Dict[str, Any]], indent: int = 2) -> str:
        """Prepare JSON string from data."""
        return json.dumps(data, indent=indent, default=str, ensure_ascii=False)
    
    @staticmethod
    def _prepare_jsonl_data(data: List[Dict[str, Any]]) -> str:
        """Prepare JSONL string from data."""
        lines = []
        for record in data:
            lines.append(json.dumps(record, default=str, ensure_ascii=False))
        return "\n".join(lines) + "\n"
    
    @staticmethod
    def _prepare_csv_data(data: List[Dict[str, Any]], flatten_measurements: bool = True) -> str:
        """Prepare CSV string from data."""
        if not data:
            return ""
        
        flattened_data = []
        if flatten_measurements:
            for record in data:
                flat_record = {k: v for k, v in record.items() if k != "measurements"}
                if "measurements" in record and isinstance(record["measurements"], dict):
                    for key, value in record["measurements"].items():
                        flat_record[f"measurement_{key}"] = value
                flattened_data.append(flat_record)
        else:
            flattened_data = data
        
        all_keys = set()
        for record in flattened_data:
            all_keys.update(record.keys())
        
        output = io.StringIO()
        fieldnames = sorted(all_keys)
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flattened_data)
        return output.getvalue()
    
    @staticmethod
    def _prepare_txt_data(data: List[Dict[str, Any]], delimiter: str = "\t") -> str:
        """Prepare TXT string from data."""
        flattened_data = []
        for record in data:
            flat_record = {k: v for k, v in record.items() if k != "measurements"}
            if "measurements" in record and isinstance(record["measurements"], dict):
                for key, value in record["measurements"].items():
                    flat_record[f"measurement_{key}"] = value
            flattened_data.append(flat_record)
        
        if not flattened_data:
            return ""
        
        all_keys = set()
        for record in flattened_data:
            all_keys.update(record.keys())
        
        fieldnames = sorted(all_keys)
        lines = [delimiter.join(fieldnames)]
        for record in flattened_data:
            row = [str(record.get(key, "")) for key in fieldnames]
            lines.append(delimiter.join(row))
        return "\n".join(lines) + "\n"
    
    @staticmethod
    def _get_format_data(data: List[Dict[str, Any]], base_format: str, **kwargs) -> str:
        """Get formatted data string based on base format."""
        base_format_lower = base_format.lower()
        
        if base_format_lower == "json":
            return CompressionExporter._prepare_json_data(data, kwargs.get("indent", 2))
        elif base_format_lower == "jsonl":
            return CompressionExporter._prepare_jsonl_data(data)
        elif base_format_lower == "csv":
            return CompressionExporter._prepare_csv_data(
                data, kwargs.get("flatten_measurements", True)
            )
        elif base_format_lower == "txt":
            return CompressionExporter._prepare_txt_data(
                data, kwargs.get("delimiter", "\t")
            )
        else:
            raise ValueError(f"Unsupported base format: {base_format}")
    
    @staticmethod
    def export_to_gzip(
        data: List[Dict[str, Any]], 
        output_path: str, 
        base_format: str = "json",
        **kwargs
    ) -> bool:
        """
        Export data to Gzip-compressed format.
        
        Args:
            data: List of data records
            output_path: Output file path (.gz)
            base_format: Base format to compress (json, csv, txt, jsonl)
            **kwargs: Format-specific options
        """
        try:
            formatted_data = CompressionExporter._get_format_data(data, base_format, **kwargs)
            with gzip.open(output_path, "wt", encoding="utf-8") as f:
                f.write(formatted_data)
            
            logger.info(f"Exported {len(data)} records to Gzip-compressed {base_format}: {output_path}")
            return True
        except ValueError as e:
            logger.error(str(e))
            return False
        except Exception as e:
            logger.error(f"Error exporting to Gzip: {e}")
            return False
    
    @staticmethod
    def export_to_bzip2(
        data: List[Dict[str, Any]], 
        output_path: str, 
        base_format: str = "json",
        **kwargs
    ) -> bool:
        """
        Export data to Bzip2-compressed format.
        
        Args:
            data: List of data records
            output_path: Output file path (.bz2)
            base_format: Base format to compress (json, csv, txt, jsonl)
            **kwargs: Format-specific options
        """
        try:
            formatted_data = CompressionExporter._get_format_data(data, base_format, **kwargs)
            with bz2.open(output_path, "wt", encoding="utf-8") as f:
                f.write(formatted_data)
            
            logger.info(f"Exported {len(data)} records to Bzip2-compressed {base_format}: {output_path}")
            return True
        except ValueError as e:
            logger.error(str(e))
            return False
        except Exception as e:
            logger.error(f"Error exporting to Bzip2: {e}")
            return False
    
    @staticmethod
    def export_to_zstandard(
        data: List[Dict[str, Any]], 
        output_path: str, 
        base_format: str = "json",
        compression_level: int = 3,
        **kwargs
    ) -> bool:
        """
        Export data to Zstandard-compressed format.
        
        Args:
            data: List of data records
            output_path: Output file path (.zst or .zstd)
            base_format: Base format to compress (json, csv, txt, jsonl)
            compression_level: Compression level (1-22, default 3)
            **kwargs: Format-specific options
        """
        try:
            import zstandard as zstd
            
            formatted_data = CompressionExporter._get_format_data(data, base_format, **kwargs)
            data_bytes = formatted_data.encode("utf-8")
            
            cctx = zstd.ZstdCompressor(level=compression_level)
            with open(output_path, "wb") as f:
                f.write(cctx.compress(data_bytes))
            
            logger.info(f"Exported {len(data)} records to Zstandard-compressed {base_format}: {output_path}")
            return True
        except ImportError:
            logger.error("zstandard required for Zstandard export. Install with: pip install zstandard")
            return False
        except ValueError as e:
            logger.error(str(e))
            return False
        except Exception as e:
            logger.error(f"Error exporting to Zstandard: {e}")
            return False
