"""
Compression and archive format exporters (Gzip, Bzip2, Zstandard, ZIP, TAR).
These formats compress and archive text-based data formats like JSON, CSV, TXT.
"""
import gzip
import bz2
import json
import csv
import io
import zipfile
import tarfile
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path

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
    def _compress_with_gzip(data: str, output_path: str) -> None:
        """Compress data with gzip."""
        with gzip.open(output_path, "wt", encoding="utf-8") as f:
            f.write(data)
    
    @staticmethod
    def _compress_with_bzip2(data: str, output_path: str) -> None:
        """Compress data with bzip2."""
        with bz2.open(output_path, "wt", encoding="utf-8") as f:
            f.write(data)
    
    @staticmethod
    def export_to_gzip(
        data: List[Dict[str, Any]], 
        output_path: str, 
        base_format: str = "json",
        **kwargs
    ) -> bool:
        """Export data to Gzip-compressed format."""
        try:
            formatted_data = CompressionExporter._get_format_data(data, base_format, **kwargs)
            CompressionExporter._compress_with_gzip(formatted_data, output_path)
            logger.info(f"Exported {len(data)} records to Gzip-compressed {base_format}: {output_path}")
            return True
        except (ValueError, Exception) as e:
            logger.error(f"Error exporting to Gzip: {e}")
            return False
    
    @staticmethod
    def export_to_bzip2(
        data: List[Dict[str, Any]], 
        output_path: str, 
        base_format: str = "json",
        **kwargs
    ) -> bool:
        """Export data to Bzip2-compressed format."""
        try:
            formatted_data = CompressionExporter._get_format_data(data, base_format, **kwargs)
            CompressionExporter._compress_with_bzip2(formatted_data, output_path)
            logger.info(f"Exported {len(data)} records to Bzip2-compressed {base_format}: {output_path}")
            return True
        except (ValueError, Exception) as e:
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
        """Export data to Zstandard-compressed format."""
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
            logger.error("zstandard required. Install with: pip install zstandard")
            return False
        except (ValueError, Exception) as e:
            logger.error(f"Error exporting to Zstandard: {e}")
            return False
    
    @staticmethod
    def export_to_zip(
        data: List[Dict[str, Any]], 
        output_path: str, 
        base_format: str = "json",
        **kwargs
    ) -> bool:
        """Export data to ZIP archive format."""
        try:
            formatted_data = CompressionExporter._get_format_data(data, base_format, **kwargs)
            archive_name = kwargs.get("archive_name", f"data.{base_format}")
            
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr(archive_name, formatted_data.encode("utf-8"))
            
            logger.info(f"Exported {len(data)} records to ZIP archive ({base_format}): {output_path}")
            return True
        except (ValueError, Exception) as e:
            logger.error(f"Error exporting to ZIP: {e}")
            return False
    
    @staticmethod
    def export_to_tar(
        data: List[Dict[str, Any]], 
        output_path: str, 
        base_format: str = "json",
        compression: str = None,
        **kwargs
    ) -> bool:
        """Export data to TAR archive format."""
        try:
            formatted_data = CompressionExporter._get_format_data(data, base_format, **kwargs)
            archive_name = kwargs.get("archive_name", f"data.{base_format}")
            
            if compression == "gz" or output_path.endswith(".tar.gz"):
                mode = "w:gz"
            elif compression == "bz2" or output_path.endswith(".tar.bz2"):
                mode = "w:bz2"
            else:
                mode = "w"
            
            data_bytes = formatted_data.encode("utf-8")
            with tarfile.open(output_path, mode) as tarf:
                tarinfo = tarfile.TarInfo(name=archive_name)
                tarinfo.size = len(data_bytes)
                tarf.addfile(tarinfo, io.BytesIO(data_bytes))
            
            comp_str = f" ({compression})" if compression else ""
            logger.info(f"Exported {len(data)} records to TAR archive{comp_str} ({base_format}): {output_path}")
            return True
        except (ValueError, Exception) as e:
            logger.error(f"Error exporting to TAR: {e}")
            return False
