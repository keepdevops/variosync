"""
Text format exporters (JSON, JSONL, CSV, TXT).
"""
import json
import csv
from typing import Any, Dict, List

from logger import get_logger

logger = get_logger()


class TextExporter:
    """Text format exporters."""
    
    @staticmethod
    def export_to_json(data: List[Dict[str, Any]], output_path: str, indent: int = 2) -> bool:
        """Export data to JSON format."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=indent, default=str, ensure_ascii=False)
            logger.info(f"Exported {len(data)} records to JSON: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False
    
    @staticmethod
    def export_to_jsonl(data: List[Dict[str, Any]], output_path: str) -> bool:
        """Export data to JSONL (JSON Lines) format."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                for record in data:
                    json.dump(record, f, default=str, ensure_ascii=False)
                    f.write("\n")
            logger.info(f"Exported {len(data)} records to JSONL: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to JSONL: {e}")
            return False
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], output_path: str, flatten_measurements: bool = True) -> bool:
        """Export data to CSV format."""
        try:
            if not data:
                logger.warning("No data to export")
                return False
            
            if flatten_measurements:
                flattened_data = []
                for record in data:
                    flat_record = {k: v for k, v in record.items() if k != "measurements"}
                    if "measurements" in record and isinstance(record["measurements"], dict):
                        for key, value in record["measurements"].items():
                            flat_record[f"measurement_{key}"] = value
                    flattened_data.append(flat_record)
                data = flattened_data
            
            all_keys = set()
            for record in data:
                all_keys.update(record.keys())
            
            fieldnames = sorted(all_keys)
            
            with open(output_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"Exported {len(data)} records to CSV: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def export_to_txt(data: List[Dict[str, Any]], output_path: str, delimiter: str = "\t") -> bool:
        """Export data to TXT format."""
        try:
            if not data:
                logger.warning("No data to export")
                return False
            
            flattened_data = []
            for record in data:
                flat_record = {k: v for k, v in record.items() if k != "measurements"}
                if "measurements" in record and isinstance(record["measurements"], dict):
                    for key, value in record["measurements"].items():
                        flat_record[f"measurement_{key}"] = value
                flattened_data.append(flat_record)
            
            all_keys = set()
            for record in flattened_data:
                all_keys.update(record.keys())
            
            fieldnames = sorted(all_keys)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(delimiter.join(fieldnames) + "\n")
                for record in flattened_data:
                    row = [str(record.get(key, "")) for key in fieldnames]
                    f.write(delimiter.join(row) + "\n")
            
            logger.info(f"Exported {len(data)} records to TXT: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to TXT: {e}")
            return False
