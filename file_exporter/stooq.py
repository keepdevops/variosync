"""
Stooq financial data format exporter.
Exports time-series data to Stooq format (CSV with specific columns).
"""
import csv
from typing import Any, Dict, List

from logger import get_logger
from file_formats.stooq import StooqFormatHandler

logger = get_logger()


class StooqExporter:
    """Exporter for Stooq financial data format."""
    
    @staticmethod
    def export_to_stooq(data: List[Dict[str, Any]], output_path: str, **kwargs) -> bool:
        """
        Export data to Stooq format.
        
        Stooq format columns:
        TICKER,PER,DATE,TIME,OPEN,HIGH,LOW,CLOSE,VOL,OPENINT
        
        Args:
            data: List of time-series records
            output_path: Output file path
            **kwargs: Optional parameters
                - default_period: Default period if not found (default: "D")
                - default_ticker: Default ticker if not found (default: "UNKNOWN")
        
        Returns:
            True if successful
        """
        try:
            if not data:
                logger.warning("No data to export to Stooq format")
                return False
            
            default_period = kwargs.get("default_period", "D")
            default_ticker = kwargs.get("default_ticker", "UNKNOWN")
            
            # Stooq format columns
            fieldnames = ["TICKER", "PER", "DATE", "TIME", "OPEN", "HIGH", "LOW", "CLOSE", "VOL", "OPENINT"]
            
            with open(output_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for record in data:
                    try:
                        # Extract ticker
                        ticker = StooqFormatHandler._extract_ticker(record)
                        if ticker == "UNKNOWN" and default_ticker != "UNKNOWN":
                            ticker = default_ticker
                        
                        # Extract period
                        period = StooqFormatHandler._extract_period(record)
                        if not period:
                            period = default_period
                        
                        # Parse timestamp
                        timestamp = record.get("timestamp", "")
                        date_str, time_str = StooqFormatHandler._parse_timestamp(timestamp)
                        
                        # Extract OHLCV
                        ohlcv = StooqFormatHandler._extract_ohlcv(record)
                        
                        # Build row
                        row = {
                            "TICKER": ticker,
                            "PER": period,
                            "DATE": date_str,
                            "TIME": time_str,
                            "OPEN": StooqExporter._format_value(ohlcv["open"]),
                            "HIGH": StooqExporter._format_value(ohlcv["high"]),
                            "LOW": StooqExporter._format_value(ohlcv["low"]),
                            "CLOSE": StooqExporter._format_value(ohlcv["close"]),
                            "VOL": int(ohlcv["vol"]) if ohlcv["vol"] else 0,
                            "OPENINT": int(ohlcv["openint"]) if ohlcv["openint"] else 0
                        }
                        
                        writer.writerow(row)
                        
                    except Exception as e:
                        logger.warning(f"Error processing record for Stooq export: {e}, skipping")
                        continue
            
            logger.info(f"Exported {len(data)} records to Stooq format: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to Stooq format: {e}")
            return False
    
    @staticmethod
    def _format_value(value: Any) -> str:
        """Format numeric value for Stooq export (prices always use 2 decimal places)."""
        if value is None:
            return ""
        try:
            # Format as float with 2 decimal places for prices
            float_val = float(value)
            return f"{float_val:.2f}"
        except (ValueError, TypeError):
            return str(value) if value else ""
