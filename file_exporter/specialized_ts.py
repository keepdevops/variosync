"""
Specialized time-series database format exporters (TsFile, TDengine, VictoriaMetrics).
These formats are optimized for specific time-series database systems.
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import json

from logger import get_logger

logger = get_logger()


class SpecializedTSExporter:
    """Specialized time-series database format exporters."""
    
    @staticmethod
    def _parse_timestamp(timestamp: Any) -> Optional[int]:
        """Parse timestamp to milliseconds."""
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                return int(dt.timestamp() * 1000)
            except:
                return None
        elif isinstance(timestamp, (int, float)):
            return int(timestamp * 1000) if timestamp < 1e10 else int(timestamp)
        return None
    
    @staticmethod
    def _extract_measurements(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract measurements as flat records."""
        records = []
        for record in data:
            ts_ms = SpecializedTSExporter._parse_timestamp(record.get("timestamp", ""))
            if ts_ms is None:
                continue
            
            series_id = record.get("series_id", "default")
            if "measurements" in record and isinstance(record["measurements"], dict):
                for key, value in record["measurements"].items():
                    if isinstance(value, (int, float)):
                        records.append({
                            "timestamp": ts_ms,
                            "series_id": series_id,
                            "measurement": key,
                            "value": float(value)
                        })
        return records
    
    @staticmethod
    def export_to_tsfile(
        data: List[Dict[str, Any]], 
        output_path: str,
        **kwargs
    ) -> bool:
        """Export data to TsFile format (Apache IoTDB)."""
        try:
            try:
                from tsfile import write_tsfile
                import pandas as pd
                
                if not data:
                    logger.warning("No data to export")
                    return False
                
                records = SpecializedTSExporter._extract_measurements(data)
                if not records:
                    logger.error("No valid data records found")
                    return False
                
                df_records = [{
                    "time": r["timestamp"],
                    "device": r["series_id"],
                    "measurement": r["measurement"],
                    "value": r["value"]
                } for r in records]
                
                df = pd.DataFrame(df_records)
                write_tsfile(output_path, df, device_col="device", time_col="time", 
                           measurement_col="measurement", value_col="value")
                
                logger.info(f"Exported {len(data)} records to TsFile: {output_path}")
                return True
            except ImportError:
                logger.warning("tsfile library not available, using JSON-compatible format")
                tsfile_data = {
                    "metadata": {"format": "tsfile", "version": "1.0", "created_by": "VARIOSYNC"},
                    "timeseries": []
                }
                
                records = SpecializedTSExporter._extract_measurements(data)
                for r in records:
                    tsfile_data["timeseries"].append({
                        "device": r["series_id"],
                        "timestamp": r["timestamp"],
                        "measurement": r["measurement"],
                        "value": r["value"]
                    })
                
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(tsfile_data, f, indent=2, default=str)
                
                logger.info(f"Exported {len(data)} records to TsFile (JSON format): {output_path}")
                logger.warning("Install tsfile for full binary TsFile support: pip install tsfile")
                return True
        except Exception as e:
            logger.error(f"Error exporting to TsFile: {e}")
            return False
    
    @staticmethod
    def _format_tdengine_timestamp(timestamp_ms: int) -> str:
        """Format timestamp for TDengine SQL."""
        dt = datetime.fromtimestamp(timestamp_ms / 1000.0)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    @staticmethod
    def export_to_tdengine(
        data: List[Dict[str, Any]], 
        output_path: str,
        **kwargs
    ) -> bool:
        """Export data to TDengine format."""
        try:
            table_name = kwargs.get("table_name", "time_series_data")
            
            if not data:
                logger.warning("No data to export")
                return False
            
            records = SpecializedTSExporter._extract_measurements(data)
            if not records:
                logger.error("No valid data records found")
                return False
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"-- TDengine import file\n")
                f.write(f"-- Created by VARIOSYNC on {datetime.now().isoformat()}\n\n")
                
                for r in records:
                    ts_str = SpecializedTSExporter._format_tdengine_timestamp(r["timestamp"])
                    f.write(f"INSERT INTO {table_name} USING {table_name}_tags TAGS ('{r['measurement']}') VALUES ('{ts_str}', '{r['series_id']}', {r['value']});\n")
                
            logger.info(f"Exported {len(data)} records to TDengine format: {output_path}")
            logger.warning("Note: This creates SQL INSERT statements. For binary format, use TDengine's native client.")
            return True
        except Exception as e:
            logger.error(f"Error exporting to TDengine format: {e}")
            return False
    
    @staticmethod
    def export_to_victoriametrics(
        data: List[Dict[str, Any]], 
        output_path: str,
        **kwargs
    ) -> bool:
        """Export data to VictoriaMetrics format."""
        try:
            if not data:
                logger.warning("No data to export")
                return False
            
            vm_data = {
                "format": "victoriametrics",
                "version": "1.0",
                "timeseries": []
            }
            
            records = SpecializedTSExporter._extract_measurements(data)
            for r in records:
                metric_name = r["series_id"]
                labels = {"__name__": f"{metric_name}_{r['measurement']}"}
                
                # Find original record for metadata
                original_record = next((rec for rec in data if rec.get("series_id") == r["series_id"]), None)
                if original_record:
                    if "metadata" in original_record and isinstance(original_record["metadata"], dict):
                        for key, val in original_record["metadata"].items():
                            labels[str(key)] = str(val)
                
                vm_data["timeseries"].append({
                    "metric": labels,
                    "values": [r["value"]],
                    "timestamps": [r["timestamp"]]
                })
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(vm_data, f, indent=2, default=str)
            
            logger.info(f"Exported {len(data)} records to VictoriaMetrics format: {output_path}")
            logger.warning("Note: Use VictoriaMetrics API client for direct import. This creates JSON-compatible format.")
            return True
        except Exception as e:
            logger.error(f"Error exporting to VictoriaMetrics format: {e}")
            return False
