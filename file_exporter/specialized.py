"""
Specialized format exporters (Avro, ORC, MessagePack, SQLite, InfluxDB).
"""
from typing import Any, Dict, List, Optional
from datetime import datetime

from logger import get_logger

logger = get_logger()


class SpecializedExporter:
    """Specialized format exporters."""
    
    @staticmethod
    def export_to_avro(data: List[Dict[str, Any]], output_path: str, schema: Optional[Dict] = None) -> bool:
        """Export data to Apache Avro format."""
        try:
            import fastavro
            
            if not data:
                logger.warning("No data to export")
                return False
            
            if schema is None:
                sample_record = data[0]
                schema = {
                    "type": "record",
                    "name": "TimeSeriesRecord",
                    "fields": []
                }
                
                for key, value in sample_record.items():
                    if key == "measurements" and isinstance(value, dict):
                        for m_key, m_value in value.items():
                            field_type = "double" if isinstance(m_value, (int, float)) else "string"
                            schema["fields"].append({
                                "name": f"measurement_{m_key}",
                                "type": ["null", field_type],
                                "default": None
                            })
                    else:
                        field_type = "string"
                        if isinstance(value, (int, float)):
                            field_type = "double"
                        elif isinstance(value, bool):
                            field_type = "boolean"
                        schema["fields"].append({
                            "name": key,
                            "type": ["null", field_type],
                            "default": None
                        })
            
            flattened_data = []
            for record in data:
                flat_record = {k: v for k, v in record.items() if k != "measurements"}
                if "measurements" in record and isinstance(record["measurements"], dict):
                    for key, value in record["measurements"].items():
                        flat_record[f"measurement_{key}"] = value
                flattened_data.append(flat_record)
            
            with open(output_path, "wb") as f:
                fastavro.writer(f, schema, flattened_data)
            
            logger.info(f"Exported {len(data)} records to Avro: {output_path}")
            return True
        except ImportError:
            logger.error("fastavro required for Avro export. Install with: pip install fastavro")
            return False
        except Exception as e:
            logger.error(f"Error exporting to Avro: {e}")
            return False
    
    @staticmethod
    def export_to_orc(data: List[Dict[str, Any]], output_path: str) -> bool:
        """Export data to Apache ORC format."""
        try:
            import pandas as pd
            import pyarrow as pa
            import pyarrow.orc as orc
            
            df = pd.DataFrame(data)
            if "measurements" in df.columns:
                measurements_df = pd.json_normalize(df["measurements"])
                measurements_df.columns = [f"measurement_{col}" for col in measurements_df.columns]
                df = df.drop(columns=["measurements"]).join(measurements_df)
            
            table = pa.Table.from_pandas(df)
            orc.write_table(table, output_path)
            
            logger.info(f"Exported {len(data)} records to ORC: {output_path}")
            return True
        except ImportError:
            logger.error("pandas and pyarrow required for ORC export. Install with: pip install pandas pyarrow")
            return False
        except Exception as e:
            logger.error(f"Error exporting to ORC: {e}")
            return False
    
    @staticmethod
    def export_to_msgpack(data: List[Dict[str, Any]], output_path: str) -> bool:
        """Export data to MessagePack format."""
        try:
            import msgpack
            
            with open(output_path, "wb") as f:
                msgpack.pack(data, f, use_bin_type=True)
            
            logger.info(f"Exported {len(data)} records to MessagePack: {output_path}")
            return True
        except ImportError:
            logger.error("msgpack required for MessagePack export. Install with: pip install msgpack")
            return False
        except Exception as e:
            logger.error(f"Error exporting to MessagePack: {e}")
            return False
    
    @staticmethod
    def export_to_sqlite(data: List[Dict[str, Any]], output_path: str, table_name: str = "time_series_data") -> bool:
        """Export data to SQLite database format."""
        try:
            import sqlite3
            import pandas as pd
            
            df = pd.DataFrame(data)
            if "measurements" in df.columns:
                measurements_df = pd.json_normalize(df["measurements"])
                measurements_df.columns = [f"measurement_{col}" for col in measurements_df.columns]
                df = df.drop(columns=["measurements"]).join(measurements_df)
            
            conn = sqlite3.connect(output_path)
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            conn.close()
            
            logger.info(f"Exported {len(data)} records to SQLite: {output_path}")
            return True
        except ImportError:
            logger.error("pandas required for SQLite export. Install with: pip install pandas")
            return False
        except Exception as e:
            logger.error(f"Error exporting to SQLite: {e}")
            return False
    
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
