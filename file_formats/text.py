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
            # Read file content first
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.strip().split("\n")

            if not lines:
                logger.warning(f"Empty file: {file_path}")
                return []

            first_line = lines[0].strip()

            # Check if it's Stooq format (comma-delimited with specific headers)
            if "," in first_line:
                parts = first_line.split(",")
                headers_upper = [p.strip().upper() for p in parts]
                if "TICKER" in headers_upper and ("DATE" in headers_upper or "PER" in headers_upper):
                    logger.info("Detected Stooq format, using Stooq loader")
                    try:
                        from file_formats.stooq import StooqFormatHandler
                        return StooqFormatHandler.load_stooq(file_path)
                    except ImportError:
                        logger.warning("Stooq format handler not available")

            # Try to auto-detect delimiter if not provided
            if delimiter is None:
                # Try different delimiters and pick the one that gives most columns
                delimiters_to_try = [",", "\t", ";", "|", " "]
                best_delimiter = "\t"
                best_col_count = 0

                for delim in delimiters_to_try:
                    parts = first_line.split(delim)
                    if len(parts) > best_col_count:
                        best_col_count = len(parts)
                        best_delimiter = delim

                delimiter = best_delimiter
                logger.info(f"Auto-detected delimiter: {repr(delimiter)} ({best_col_count} columns)")

            records = []

            # Parse the first line for headers
            first_parts = first_line.split(delimiter)
            has_header = any(char.isalpha() for char in first_parts[0] if char.strip())

            start_idx = 1 if has_header else 0
            headers = [h.strip() for h in first_parts] if has_header else None

            # Try to identify column roles (date, ticker/series, OHLCV)
            date_col_idx = None
            series_col_idx = None
            ohlcv_cols = {}
            headers_clean = None

            if headers:
                # Strip angle brackets from headers (e.g., <TICKER> -> TICKER)
                headers_clean = [h.strip('<>') for h in headers]
                headers_upper = [h.upper() for h in headers_clean]

                # Check for header/data column mismatch (missing PER column in Stooq files)
                # If header count differs from first data row, try to detect and fix
                if len(lines) > start_idx:
                    first_data_parts = lines[start_idx].strip().split(delimiter)
                    if len(first_data_parts) > len(headers):
                        # Check if this looks like Stooq with missing PER header
                        # Data has extra column (period like 'D', '5', etc.) after ticker
                        if (len(first_data_parts) == len(headers) + 1 and
                            "TICKER" in headers_upper and
                            first_data_parts[1].strip() in ["D", "W", "M", "5", "15", "30", "60"]):
                            # Insert PER column at position 1
                            headers_clean.insert(1, "PER")
                            headers_upper.insert(1, "PER")
                            logger.info("Detected missing PER column in Stooq-style file, adjusting headers")

                # Look for date column (TIME alone is not a date - it's typically HHMMSS)
                for i, h in enumerate(headers_upper):
                    if h in ["DATE", "DATETIME", "TIMESTAMP", "DT"]:
                        date_col_idx = i
                        break

                # Look for series/ticker column
                for i, h in enumerate(headers_upper):
                    if h in ["TICKER", "SYMBOL", "SERIES", "SERIES_ID", "ID", "NAME"]:
                        series_col_idx = i
                        break

                # Look for OHLCV columns
                for i, h in enumerate(headers_upper):
                    if h in ["OPEN", "O"]:
                        ohlcv_cols["open"] = i
                    elif h in ["HIGH", "H"]:
                        ohlcv_cols["high"] = i
                    elif h in ["LOW", "L"]:
                        ohlcv_cols["low"] = i
                    elif h in ["CLOSE", "C", "ADJ CLOSE", "ADJ_CLOSE", "ADJCLOSE"]:
                        ohlcv_cols["close"] = i
                    elif h in ["VOLUME", "VOL", "V"]:
                        ohlcv_cols["vol"] = i

            # Process data lines
            for line_num, line in enumerate(lines[start_idx:], start=start_idx):
                line = line.strip()
                if not line:
                    continue

                parts = line.split(delimiter)
                if len(parts) < 1:
                    continue

                # Build record
                record = {
                    "measurements": {}
                }

                # Set series_id
                if series_col_idx is not None and series_col_idx < len(parts):
                    record["series_id"] = parts[series_col_idx].strip()
                else:
                    # Use filename as series_id if no series column
                    import os
                    record["series_id"] = os.path.splitext(os.path.basename(file_path))[0]

                # Set timestamp
                if date_col_idx is not None and date_col_idx < len(parts):
                    date_val = parts[date_col_idx].strip()
                    # Try to parse and normalize date
                    record["timestamp"] = TextFormatHandlers._parse_date(date_val)
                elif len(parts) > 0:
                    # Try first column as date
                    date_val = parts[0].strip()
                    parsed = TextFormatHandlers._parse_date(date_val)
                    if parsed != date_val:  # Date was successfully parsed
                        record["timestamp"] = parsed
                    else:
                        # No valid date found - use synthetic timestamp (won't plot)
                        record["timestamp"] = f"row_{line_num}"
                        if line_num == start_idx:
                            logger.warning(f"No date/timestamp column detected in file. First value '{date_val[:50]}' is not a recognized date format.")

                # Add OHLCV if detected - put at top level for financial chart support
                for field, idx in ohlcv_cols.items():
                    if idx < len(parts):
                        val = TextFormatHandlers._convert_to_numeric(parts[idx])
                        if val is not None:
                            record[field] = val  # Top level for financial charts
                            record["measurements"][field] = val  # Also in measurements for compatibility

                # Add other columns as measurements (use cleaned headers without angle brackets)
                if headers_clean:
                    for i, header in enumerate(headers_clean):
                        if i in [date_col_idx, series_col_idx] or i in ohlcv_cols.values():
                            continue
                        if i < len(parts):
                            val = TextFormatHandlers._convert_to_numeric(parts[i])
                            if val is not None:
                                record["measurements"][header.lower().replace(" ", "_")] = val
                else:
                    # No headers - add all columns as value_N
                    for i, part in enumerate(parts):
                        if i == 0 and date_col_idx is None:
                            continue  # Skip if used as timestamp
                        val = TextFormatHandlers._convert_to_numeric(part)
                        if val is not None:
                            record["measurements"][f"value_{i}"] = val

                # Only add record if it has some data
                if record.get("timestamp") and (record.get("measurements") or ohlcv_cols):
                    records.append(record)

            logger.info(f"Loaded {len(records)} records from TXT file (delimiter: {repr(delimiter)})")

            if len(records) == 0:
                logger.warning(f"No records loaded. File may have unsupported format. First line: {first_line[:100]}")

            return records
        except Exception as e:
            logger.error(f"Error loading TXT file {file_path}: {e}", exc_info=True)
            return []

    @staticmethod
    def _parse_date(date_str: str) -> str:
        """Try to parse various date formats and return ISO format."""
        from datetime import datetime

        date_str = date_str.strip()

        # Common date formats to try
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y%m%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%m-%d-%Y",
            "%m/%d/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y%m%d%H%M%S",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.isoformat()
            except ValueError:
                continue

        # Return original if no format matched
        return date_str
