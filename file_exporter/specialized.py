"""
Specialized format exporters (Avro, ORC, MessagePack, SQLite, Protocol Buffers).
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import json

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
    def export_to_protobuf(data: List[Dict[str, Any]], output_path: str, schema_path: Optional[str] = None) -> bool:
        """Export data to Protocol Buffers format."""
        try:
            from google.protobuf import message
            from google.protobuf import json_format
            import google.protobuf.descriptor_pb2 as descriptor_pb2
            
            if not data:
                logger.warning("No data to export")
                return False
            
            # For simplicity, we'll use JSON encoding with protobuf structure
            # Full protobuf implementation would require .proto schema files
            # This is a simplified approach that creates a protobuf-compatible JSON structure
            protobuf_data = {
                "records": []
            }
            
            for record in data:
                pb_record = {}
                
                # Add series_id
                if "series_id" in record:
                    pb_record["series_id"] = str(record["series_id"])
                
                # Add timestamp
                if "timestamp" in record:
                    timestamp = record["timestamp"]
                    if isinstance(timestamp, str):
                        try:
                            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                            pb_record["timestamp"] = int(dt.timestamp() * 1e9)
                        except:
                            pb_record["timestamp"] = str(timestamp)
                    elif isinstance(timestamp, (int, float)):
                        pb_record["timestamp"] = int(timestamp * 1e9) if timestamp < 1e10 else int(timestamp)
                    else:
                        pb_record["timestamp"] = str(timestamp)
                
                # Add measurements as fields
                if "measurements" in record and isinstance(record["measurements"], dict):
                    pb_record["fields"] = {}
                    for key, value in record["measurements"].items():
                        if isinstance(value, (int, float)):
                            pb_record["fields"][key] = float(value)
                        elif isinstance(value, bool):
                            pb_record["fields"][key] = bool(value)
                        else:
                            pb_record["fields"][key] = str(value)
                
                # Add metadata if present
                if "metadata" in record:
                    pb_record["metadata"] = record["metadata"]
                
                protobuf_data["records"].append(pb_record)
            
            # Write as JSON (protobuf-compatible structure)
            # For full protobuf binary format, would need .proto schema compilation
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(protobuf_data, f, indent=2, default=str)
            
            logger.info(f"Exported {len(data)} records to Protocol Buffers JSON format: {output_path}")
            logger.warning("Note: Full binary protobuf requires .proto schema files. Using JSON-compatible format.")
            return True
        except ImportError:
            logger.error("protobuf required for Protocol Buffers export. Install with: pip install protobuf")
            return False
        except Exception as e:
            logger.error(f"Error exporting to Protocol Buffers: {e}")
            return False
