"""
Stooq financial data format handler.
Stooq format: CSV with columns TICKER,PER,DATE,TIME,OPEN,HIGH,LOW,CLOSE,VOL,OPENINT
"""
import csv
from datetime import datetime
from typing import Any, Dict, List

from logger import get_logger

logger = get_logger()


class StooqFormatHandler:
    """Handler for Stooq financial data format."""
    
    @staticmethod
    def load_stooq(file_path: str) -> List[Dict[str, Any]]:
        """
        Load data from Stooq format file.
        
        Stooq format columns:
        - TICKER: Stock ticker symbol (e.g., 'AAPL.US')
        - PER: Period (e.g., 'D' for daily, '5' for 5-minute)
        - DATE: Date in YYYYMMDD format (e.g., '20210702')
        - TIME: Time in HHMMSS format (e.g., '153000' or '000000' for daily)
        - OPEN: Opening price
        - HIGH: Highest price
        - LOW: Lowest price
        - CLOSE: Closing price
        - VOL: Volume
        - OPENINT: Open interest (often 0)
        
        Args:
            file_path: Path to Stooq format file
            
        Returns:
            List of time-series records
        """
        try:
            records = []
            
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        # Extract ticker (series_id)
                        ticker = row.get("TICKER", "").strip()
                        if not ticker:
                            continue
                        
                        # Parse date (YYYYMMDD format)
                        date_str = row.get("DATE", "").strip()
                        if not date_str or len(date_str) != 8:
                            logger.warning(f"Invalid date format: {date_str}, skipping row")
                            continue
                        
                        # Parse time (HHMMSS format)
                        time_str = row.get("TIME", "000000").strip()
                        if len(time_str) != 6:
                            time_str = "000000"
                        
                        # Combine date and time into ISO timestamp
                        try:
                            date_obj = datetime.strptime(date_str, "%Y%m%d")
                            hour = int(time_str[0:2])
                            minute = int(time_str[2:4])
                            second = int(time_str[4:6])
                            timestamp = date_obj.replace(hour=hour, minute=minute, second=second)
                            timestamp_str = timestamp.isoformat()
                        except ValueError as e:
                            logger.warning(f"Error parsing date/time: {e}, skipping row")
                            continue
                        
                        # Extract OHLCV data
                        measurements = {}
                        
                        # Parse numeric values
                        for field in ["OPEN", "HIGH", "LOW", "CLOSE", "VOL", "OPENINT"]:
                            value_str = row.get(field, "").strip()
                            if value_str:
                                try:
                                    if field == "VOL" or field == "OPENINT":
                                        measurements[field.lower()] = int(float(value_str))
                                    else:
                                        measurements[field.lower()] = float(value_str)
                                except ValueError:
                                    logger.warning(f"Invalid {field} value: {value_str}")
                        
                        # Add period if present
                        per = row.get("PER", "").strip()
                        if per:
                            measurements["period"] = per
                        
                        # Create record
                        record = {
                            "series_id": ticker,
                            "timestamp": timestamp_str,
                            "measurements": measurements,
                            "metadata": {
                                "format": "stooq",
                                "ticker": ticker,
                                "period": per if per else None
                            }
                        }
                        
                        records.append(record)
                        
                    except Exception as e:
                        logger.warning(f"Error processing row: {e}, skipping")
                        continue
            
            logger.info(f"Loaded {len(records)} records from Stooq file: {file_path}")
            return records
            
        except FileNotFoundError:
            logger.error(f"Stooq file not found: {file_path}")
            return []
        except Exception as e:
            logger.error(f"Error loading Stooq file {file_path}: {e}")
            return []
    
    @staticmethod
    def _parse_timestamp(timestamp: Any) -> tuple:
        """
        Parse timestamp to extract date and time components.
        
        Returns:
            Tuple of (date_str: YYYYMMDD, time_str: HHMMSS)
        """
        try:
            if isinstance(timestamp, str):
                # Try ISO format first
                if "T" in timestamp:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                else:
                    # Try other common formats
                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y%m%d"]:
                        try:
                            dt = datetime.strptime(timestamp, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        raise ValueError(f"Unknown timestamp format: {timestamp}")
            elif isinstance(timestamp, (int, float)):
                # Unix timestamp
                dt = datetime.fromtimestamp(timestamp)
            else:
                dt = timestamp
            
            date_str = dt.strftime("%Y%m%d")
            time_str = dt.strftime("%H%M%S")
            return date_str, time_str
            
        except Exception as e:
            logger.warning(f"Error parsing timestamp {timestamp}: {e}")
            return datetime.now().strftime("%Y%m%d"), "000000"
    
    @staticmethod
    def _extract_ticker(record: Dict[str, Any]) -> str:
        """Extract ticker from record."""
        # Check metadata first
        if "metadata" in record and isinstance(record["metadata"], dict):
            ticker = record["metadata"].get("ticker")
            if ticker:
                return str(ticker)
        
        # Check series_id
        series_id = record.get("series_id", "")
        if series_id:
            return str(series_id)
        
        # Default fallback
        return "UNKNOWN"
    
    @staticmethod
    def _extract_period(record: Dict[str, Any]) -> str:
        """Extract period from record."""
        # Check measurements
        if "measurements" in record and isinstance(record["measurements"], dict):
            period = record["measurements"].get("period")
            if period:
                return str(period)
        
        # Check metadata
        if "metadata" in record and isinstance(record["metadata"], dict):
            period = record["metadata"].get("period")
            if period:
                return str(period)
        
        # Default to daily
        return "D"
    
    @staticmethod
    def _extract_ohlcv(record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract OHLCV values from record."""
        ohlcv = {
            "open": None,
            "high": None,
            "low": None,
            "close": None,
            "vol": 0,
            "openint": 0
        }
        
        if "measurements" in record and isinstance(record["measurements"], dict):
            measurements = record["measurements"]
            
            # Try various field name variations
            ohlcv["open"] = measurements.get("open") or measurements.get("OPEN") or measurements.get("o")
            ohlcv["high"] = measurements.get("high") or measurements.get("HIGH") or measurements.get("h")
            ohlcv["low"] = measurements.get("low") or measurements.get("LOW") or measurements.get("l")
            ohlcv["close"] = measurements.get("close") or measurements.get("CLOSE") or measurements.get("c")
            ohlcv["vol"] = measurements.get("vol") or measurements.get("VOL") or measurements.get("volume") or measurements.get("Volume") or 0
            ohlcv["openint"] = measurements.get("openint") or measurements.get("OPENINT") or measurements.get("open_interest") or 0
        
        return ohlcv
