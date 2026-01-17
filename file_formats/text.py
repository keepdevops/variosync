"""
Text format loaders (JSON, CSV, TXT).
"""
import csv
import json
from typing import Any, Dict, List

from logger import get_logger

logger = get_logger()


class TextFormatHandlers:
    """Text format handlers."""
    
    @staticmethod
    def load_json(file_path: str) -> List[Dict[str, Any]]:
        """Load data from JSON file."""
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            else:
                logger.error(f"Invalid JSON structure in {file_path}")
                return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error loading JSON file {file_path}: {e}")
            return []
    
    @staticmethod
    def load_csv(file_path: str, has_header: bool = True) -> List[Dict[str, Any]]:
        """Load data from CSV file."""
        try:
            records = []
            
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f) if has_header else csv.reader(f)
                
                if has_header:
                    for row in reader:
                        records.append(dict(row))
                else:
                    headers = ["series_id", "timestamp"]
                    for row in reader:
                        if len(row) >= 2:
                            record = {
                                "series_id": row[0],
                                "timestamp": row[1],
                                "measurements": {}
                            }
                            for i, value in enumerate(row[2:], start=2):
                                header = f"col_{i}" if i < len(headers) else f"measurement_{i-2}"
                                try:
                                    record["measurements"][header] = float(value)
                                except ValueError:
                                    record["measurements"][header] = value
                            records.append(record)
            
            logger.info(f"Loaded {len(records)} records from CSV file")
            return records
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {e}")
            return []
    
    @staticmethod
    def load_txt(file_path: str, delimiter: str = "\t") -> List[Dict[str, Any]]:
        """Load data from TXT file."""
        try:
            records = []
            
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
                if len(lines) > 0:
                    first_line = lines[0].strip().split(delimiter)
                    has_header = any(char.isalpha() for char in first_line[0])
                    
                    start_idx = 1 if has_header else 0
                    headers = first_line if has_header else None
                    
                    for line in lines[start_idx:]:
                        parts = line.strip().split(delimiter)
                        if len(parts) >= 2:
                            if headers and len(headers) == len(parts):
                                record = dict(zip(headers, parts))
                            else:
                                record = {
                                    "series_id": parts[0],
                                    "timestamp": parts[1],
                                    "measurements": {f"value_{i}": parts[i] for i in range(2, len(parts))}
                                }
                            records.append(record)
            
            logger.info(f"Loaded {len(records)} records from TXT file")
            return records
        except Exception as e:
            logger.error(f"Error loading TXT file {file_path}: {e}")
            return []
