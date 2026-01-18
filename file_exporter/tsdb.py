"""
Time-series database format exporters (InfluxDB, OpenTSDB, Prometheus).
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import json

from logger import get_logger

logger = get_logger()


class TSDBExporter:
    """Time-series database format exporters."""
    
    @staticmethod
    def export_to_influxdb_lp(data: List[Dict[str, Any]], output_path: str, measurement: str = "time_series") -> bool:
        """Export data to InfluxDB Line Protocol format."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                for record in data:
                    series_id = record.get("series_id", measurement)
                    
                    timestamp = record.get("timestamp", "")
                    if isinstance(timestamp, str):
                        try:
                            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                            ts_ns = int(dt.timestamp() * 1e9)
                        except:
                            ts_ns = ""
                    elif isinstance(timestamp, (int, float)):
                        ts_ns = int(timestamp * 1e9) if timestamp < 1e10 else int(timestamp)
                    else:
                        ts_ns = ""
                    
                    fields = []
                    if "measurements" in record and isinstance(record["measurements"], dict):
                        for key, value in record["measurements"].items():
                            if isinstance(value, (int, float)):
                                fields.append(f"{key}={value}")
                            elif isinstance(value, bool):
                                fields.append(f"{key}={str(value).lower()}")
                            else:
                                fields.append(f'{key}="{value}"')
                    
                    line = f"{series_id}"
                    if fields:
                        line += f" {','.join(fields)}"
                    if ts_ns:
                        line += f" {ts_ns}"
                    
                    f.write(line + "\n")
            
            logger.info(f"Exported {len(data)} records to InfluxDB Line Protocol: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to InfluxDB Line Protocol: {e}")
            return False
    
    @staticmethod
    def export_to_opentsdb(data: List[Dict[str, Any]], output_path: str, metric_name: Optional[str] = None) -> bool:
        """Export data to OpenTSDB format."""
        try:
            if not data:
                logger.warning("No data to export")
                return False
            
            with open(output_path, "w", encoding="utf-8") as f:
                for record in data:
                    # Extract metric name (use series_id or provided metric_name)
                    metric = metric_name or record.get("series_id", "metric")
                    
                    # Extract timestamp
                    timestamp = record.get("timestamp", "")
                    if isinstance(timestamp, str):
                        try:
                            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                            ts = int(dt.timestamp())
                        except:
                            logger.warning(f"Invalid timestamp format: {timestamp}")
                            continue
                    elif isinstance(timestamp, (int, float)):
                        ts = int(timestamp) if timestamp < 1e10 else int(timestamp / 1e9)
                    else:
                        logger.warning(f"Invalid timestamp type: {type(timestamp)}")
                        continue
                    
                    # Extract measurements - OpenTSDB typically has one value per line
                    # We'll create multiple lines if there are multiple measurements
                    if "measurements" in record and isinstance(record["measurements"], dict):
                        # Build tags from metadata or series_id
                        tags = []
                        if "series_id" in record and record["series_id"] != metric:
                            tags.append(f"series_id={record['series_id']}")
                        
                        if "metadata" in record and isinstance(record["metadata"], dict):
                            for key, value in record["metadata"].items():
                                tags.append(f"{key}={value}")
                        
                        tags_str = " " + " ".join(tags) if tags else ""
                        
                        # Write one line per measurement
                        for key, value in record["measurements"].items():
                            if isinstance(value, (int, float)):
                                # Format: metric timestamp value tag1=value1 tag2=value2
                                line = f"put {metric}.{key} {ts} {value}{tags_str}\n"
                                f.write(line)
                            else:
                                # Non-numeric values as tags
                                line = f"put {metric}.{key} {ts} 0 {key}={value}{tags_str}\n"
                                f.write(line)
                    else:
                        # No measurements, write empty metric
                        tags_str = ""
                        if "series_id" in record:
                            tags_str = f" series_id={record['series_id']}"
                        line = f"put {metric} {ts} 0{tags_str}\n"
                        f.write(line)
            
            logger.info(f"Exported {len(data)} records to OpenTSDB format: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to OpenTSDB format: {e}")
            return False
    
    @staticmethod
    def export_to_prometheus_remote_write(data: List[Dict[str, Any]], output_path: str) -> bool:
        """Export data to Prometheus Remote Write format."""
        try:
            # Prometheus Remote Write uses protobuf, but we'll create a JSON-compatible structure
            # that can be converted to protobuf using prometheus_client or similar libraries
            if not data:
                logger.warning("No data to export")
                return False
            
            prometheus_data = {
                "timeseries": []
            }
            
            for record in data:
                # Extract series_id as metric name
                metric_name = record.get("series_id", "metric")
                
                # Extract timestamp
                timestamp_ms = None
                timestamp = record.get("timestamp", "")
                if isinstance(timestamp, str):
                    try:
                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        timestamp_ms = int(dt.timestamp() * 1000)
                    except:
                        logger.warning(f"Invalid timestamp format: {timestamp}")
                        continue
                elif isinstance(timestamp, (int, float)):
                    timestamp_ms = int(timestamp * 1000) if timestamp < 1e10 else int(timestamp / 1e6)
                else:
                    logger.warning(f"Invalid timestamp type: {type(timestamp)}")
                    continue
                
                # Extract measurements and create time series
                if "measurements" in record and isinstance(record["measurements"], dict):
                    for measurement_name, value in record["measurements"].items():
                        if not isinstance(value, (int, float)):
                            continue
                        
                        # Build labels
                        labels = [
                            {"name": "__name__", "value": f"{metric_name}_{measurement_name}"}
                        ]
                        
                        # Add series_id as label if different from metric
                        if "series_id" in record:
                            labels.append({"name": "series_id", "value": str(record["series_id"])})
                        
                        # Add metadata as labels
                        if "metadata" in record and isinstance(record["metadata"], dict):
                            for key, val in record["metadata"].items():
                                labels.append({"name": str(key), "value": str(val)})
                        
                        # Create time series entry
                        timeseries = {
                            "labels": labels,
                            "samples": [
                                {
                                    "value": float(value),
                                    "timestamp": timestamp_ms
                                }
                            ]
                        }
                        
                        prometheus_data["timeseries"].append(timeseries)
            
            # Write as JSON (can be converted to protobuf using prometheus_client)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(prometheus_data, f, indent=2, default=str)
            
            logger.info(f"Exported {len(data)} records to Prometheus Remote Write format: {output_path}")
            logger.warning("Note: Full binary protobuf requires prometheus_client. Using JSON-compatible format.")
            return True
        except Exception as e:
            logger.error(f"Error exporting to Prometheus Remote Write format: {e}")
            return False
