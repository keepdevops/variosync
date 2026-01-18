"""
Text format loaders (JSON, CSV, TXT).
"""
import csv
import json
from typing import Any, Dict, List, Optional

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
    def _convert_to_numeric(value: str) -> Any:
        """Convert string to number if possible, otherwise return string."""
        if not value or value.strip() == "":
            return None
        try:
            # Try integer first
            if "." not in value:
                return int(value)
            # Try float
            return float(value)
        except ValueError:
            return value.strip()
    
    @staticmethod
    def _normalize_csv_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize CSV record to VARIOSYNC format.
        Converts flat CSV records to proper structure with measurements dict.
        Handles both time_series and financial formats.
        """
        # Check if already in correct format
        if "measurements" in record and isinstance(record["measurements"], dict):
            return record
        
        # Check if this looks like financial data (has OHLCV fields)
        financial_fields = {"open", "high", "low", "close", "volume", "vol"}
        has_financial_fields = any(field.lower() in {k.lower() for k in record.keys()} for field in financial_fields)
        
        # Identify key fields
        key_fields = {"series_id", "timestamp", "ticker", "date"}
        measurements = {}
        
        # Build normalized record
        normalized = {}
        
        # Handle series_id or ticker
        if "ticker" in record:
            normalized["ticker"] = str(record["ticker"])
            normalized["series_id"] = str(record["ticker"])
        elif "series_id" in record:
            normalized["series_id"] = str(record["series_id"])
        else:
            normalized["series_id"] = "UNKNOWN"
        
        # Handle timestamp or date
        if "timestamp" in record:
            normalized["timestamp"] = str(record["timestamp"])
        elif "date" in record:
            normalized["timestamp"] = str(record["date"])
        else:
            normalized["timestamp"] = ""
        
        # For financial data, keep OHLCV at top level as numbers
        if has_financial_fields:
            financial_top_level = {"open", "high", "low", "close", "volume", "vol", "openint"}
            for key, value in record.items():
                key_lower = key.lower()
                if key_lower in financial_top_level:
                    # Convert to numeric and keep at top level
                    num_value = TextFormatHandlers._convert_to_numeric(str(value))
                    if num_value is not None:
                        normalized[key_lower] = num_value
                elif key_lower not in key_fields:
                    # Other fields go to measurements
                    measurements[key] = TextFormatHandlers._convert_to_numeric(str(value))
        else:
            # For time-series data, put all non-key fields in measurements
            for key, value in record.items():
                if key.lower() not in key_fields:
                    measurements[key] = TextFormatHandlers._convert_to_numeric(str(value))
        
        # Add measurements (even if empty, it's required)
        normalized["measurements"] = measurements
        
        # Preserve other metadata
        for key in ["format", "metadata"]:
            if key in record:
                normalized[key] = record[key]
        
        return normalized
    
    @staticmethod
    def load_csv(file_path: str, has_header: bool = True) -> List[Dict[str, Any]]:
        """Load data from CSV file and normalize to VARIOSYNC format."""
        try:
            records = []
            
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f) if has_header else csv.reader(f)
                
                if has_header:
                    for row in reader:
                        # Convert flat CSV row to normalized format
                        normalized = TextFormatHandlers._normalize_csv_record(dict(row))
                        records.append(normalized)
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
                                record["measurements"][header] = TextFormatHandlers._convert_to_numeric(value)
                            records.append(record)
            
            logger.info(f"Loaded {len(records)} records from CSV file")
            return records
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {e}", exc_info=True)
            return []
    
    @staticmethod
    def _detect_delimiter(file_path: str) -> str:
        """Auto-detect delimiter in text file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                
            # Check for Stooq format (comma-separated with TICKER,PER,DATE columns)
            if "," in first_line:
                parts = first_line.split(",")
                if len(parts) >= 3:
                    headers = [p.strip().upper() for p in parts]
                    if "TICKER" in headers and "PER" in headers and "DATE" in headers:
                        logger.info("Detected Stooq format (comma-delimited)")
                        return ","
                # Check if comma-delimited CSV-like
                if len(parts) > 1:
                    return ","
            
            # Check for tab delimiter
            if "\t" in first_line:
                return "\t"
            
            # Check for semicolon
            if ";" in first_line:
                return ";"
            
            # Check for pipe
            if "|" in first_line:
                return "|"
            
            # Default to tab
            return "\t"
        except Exception as e:
            logger.warning(f"Error detecting delimiter: {e}, using tab")
            return "\t"
    
    @staticmethod
    def load_txt(file_path: str, delimiter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load data from TXT file with auto-detection of delimiter and format.
        
        Args:
            file_path: Path to TXT file
            delimiter: Optional delimiter override (auto-detected if None)
        """
        try:
            # Auto-detect delimiter if not provided
            if delimiter is None:
                delimiter = TextFormatHandlers._detect_delimiter(file_path)
            
            # Check if it's Stooq format
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    if delimiter == ",":
                        parts = first_line.split(",")
                        headers = [p.strip().upper() for p in parts]
                        if "TICKER" in headers and "PER" in headers and "DATE" in headers:
                            logger.info("Detected Stooq format, using Stooq loader")
                            try:
                                from file_formats.stooq import StooqFormatHandler
                                return StooqFormatHandler.load_stooq(file_path)
                            except ImportError:
                                logger.warning("Stooq format handler not available, falling back to regular txt loader")
                                pass
            except Exception:
                pass  # Continue with regular txt loading
            
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
                                # Convert to standard format
                                record = {
                                    "series_id": parts[headers.index(headers[0])] if headers else parts[0],
                                    "timestamp": parts[headers.index(headers[1])] if len(headers) > 1 else parts[1],
                                    "measurements": {}
                                }
                                # Add remaining fields as measurements
                                for i, header in enumerate(headers):
                                    if i >= 2:  # Skip series_id and timestamp
                                        try:
                                            value = parts[i] if i < len(parts) else ""
                                            # Try to convert to number
                                            try:
                                                if "." in value:
                                                    record["measurements"][header.lower()] = float(value)
                                                else:
                                                    record["measurements"][header.lower()] = int(value)
                                            except ValueError:
                                                record["measurements"][header.lower()] = value
                                        except IndexError:
                                            pass
                            else:
                                record = {
                                    "series_id": parts[0],
                                    "timestamp": parts[1] if len(parts) > 1 else "",
                                    "measurements": {f"value_{i}": parts[i] for i in range(2, len(parts))}
                                }
                            records.append(record)
            
            logger.info(f"Loaded {len(records)} records from TXT file (delimiter: {repr(delimiter)})")
            return records
        except Exception as e:
            logger.error(f"Error loading TXT file {file_path}: {e}", exc_info=True)
            return []
