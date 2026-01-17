"""
VARIOSYNC File Exporter Module
Exports time-series data to various file formats.
"""
import json
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

from logger import get_logger

logger = get_logger()


class FileExporter:
    """Exports time-series data to various file formats."""
    
    SUPPORTED_FORMATS = {
        "json": {"ext": ".json", "mime": "application/json"},
        "jsonl": {"ext": ".jsonl", "mime": "application/x-ndjson"},
        "csv": {"ext": ".csv", "mime": "text/csv"},
        "txt": {"ext": ".txt", "mime": "text/plain"},
        "parquet": {"ext": ".parquet", "mime": "application/octet-stream"},
        "feather": {"ext": ".feather", "mime": "application/octet-stream"},
        "duckdb": {"ext": ".duckdb", "mime": "application/octet-stream"},
        "xlsx": {"ext": ".xlsx", "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
        "xls": {"ext": ".xls", "mime": "application/vnd.ms-excel"},
        "h5": {"ext": ".h5", "mime": "application/x-hdf"},
        "arrow": {"ext": ".arrow", "mime": "application/octet-stream"},
        "avro": {"ext": ".avro", "mime": "application/avro"},
        "orc": {"ext": ".orc", "mime": "application/octet-stream"},
        "msgpack": {"ext": ".msgpack", "mime": "application/x-msgpack"},
        "sqlite": {"ext": ".sqlite", "mime": "application/x-sqlite3"},
        "influxdb": {"ext": ".lp", "mime": "text/plain"},
    }
    
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
    def export_to_csv(data: List[Dict[str, Any]], output_path: str, flatten_measurements: bool = True) -> bool:
        """Export data to CSV format."""
        try:
            if not data:
                logger.warning("No data to export")
                return False
            
            # Flatten measurements if needed
            if flatten_measurements:
                flattened_data = []
                for record in data:
                    flat_record = {k: v for k, v in record.items() if k != "measurements"}
                    if "measurements" in record and isinstance(record["measurements"], dict):
                        for key, value in record["measurements"].items():
                            flat_record[f"measurement_{key}"] = value
                    flattened_data.append(flat_record)
                data = flattened_data
            
            # Get all unique keys
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
            
            # Flatten measurements
            flattened_data = []
            for record in data:
                flat_record = {k: v for k, v in record.items() if k != "measurements"}
                if "measurements" in record and isinstance(record["measurements"], dict):
                    for key, value in record["measurements"].items():
                        flat_record[f"measurement_{key}"] = value
                flattened_data.append(flat_record)
            
            # Get all unique keys
            all_keys = set()
            for record in flattened_data:
                all_keys.update(record.keys())
            
            fieldnames = sorted(all_keys)
            
            with open(output_path, "w", encoding="utf-8") as f:
                # Write header
                f.write(delimiter.join(fieldnames) + "\n")
                # Write data
                for record in flattened_data:
                    row = [str(record.get(key, "")) for key in fieldnames]
                    f.write(delimiter.join(row) + "\n")
            
            logger.info(f"Exported {len(data)} records to TXT: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to TXT: {e}")
            return False
    
    @staticmethod
    def export_to_parquet(data: List[Dict[str, Any]], output_path: str) -> bool:
        """Export data to Parquet format."""
        try:
            import pandas as pd
            
            df = pd.DataFrame(data)
            
            # Flatten measurements column if present
            if "measurements" in df.columns:
                measurements_df = pd.json_normalize(df["measurements"])
                measurements_df.columns = [f"measurement_{col}" for col in measurements_df.columns]
                df = df.drop(columns=["measurements"]).join(measurements_df)
            
            df.to_parquet(output_path, index=False, engine="pyarrow")
            logger.info(f"Exported {len(data)} records to Parquet: {output_path}")
            return True
        except ImportError:
            logger.error("pandas and pyarrow required for Parquet export. Install with: pip install pandas pyarrow")
            return False
        except Exception as e:
            logger.error(f"Error exporting to Parquet: {e}")
            return False
    
    @staticmethod
    def export_to_feather(data: List[Dict[str, Any]], output_path: str) -> bool:
        """Export data to Feather format."""
        try:
            import pandas as pd
            
            df = pd.DataFrame(data)
            
            # Flatten measurements column if present
            if "measurements" in df.columns:
                measurements_df = pd.json_normalize(df["measurements"])
                measurements_df.columns = [f"measurement_{col}" for col in measurements_df.columns]
                df = df.drop(columns=["measurements"]).join(measurements_df)
            
            df.to_feather(output_path)
            logger.info(f"Exported {len(data)} records to Feather: {output_path}")
            return True
        except ImportError:
            logger.error("pandas and pyarrow required for Feather export. Install with: pip install pandas pyarrow")
            return False
        except Exception as e:
            logger.error(f"Error exporting to Feather: {e}")
            return False
    
    @staticmethod
    def export_to_duckdb(data: List[Dict[str, Any]], output_path: str, table_name: str = "time_series_data") -> bool:
        """Export data to DuckDB format."""
        try:
            import duckdb
            import pandas as pd
            
            df = pd.DataFrame(data)
            
            # Flatten measurements column if present
            if "measurements" in df.columns:
                measurements_df = pd.json_normalize(df["measurements"])
                measurements_df.columns = [f"measurement_{col}" for col in measurements_df.columns]
                df = df.drop(columns=["measurements"]).join(measurements_df)
            
            conn = duckdb.connect(output_path)
            conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df")
            conn.close()
            
            logger.info(f"Exported {len(data)} records to DuckDB: {output_path}")
            return True
        except ImportError:
            logger.error("duckdb and pandas required for DuckDB export. Install with: pip install duckdb pandas")
            return False
        except Exception as e:
            logger.error(f"Error exporting to DuckDB: {e}")
            return False
    
    @staticmethod
    def export_to_xlsx(data: List[Dict[str, Any]], output_path: str) -> bool:
        """Export data to Excel XLSX format."""
        try:
            import pandas as pd
            
            df = pd.DataFrame(data)
            
            # Flatten measurements column if present
            if "measurements" in df.columns:
                measurements_df = pd.json_normalize(df["measurements"])
                measurements_df.columns = [f"measurement_{col}" for col in measurements_df.columns]
                df = df.drop(columns=["measurements"]).join(measurements_df)
            
            df.to_excel(output_path, index=False, engine="openpyxl")
            logger.info(f"Exported {len(data)} records to Excel: {output_path}")
            return True
        except ImportError:
            logger.error("pandas and openpyxl required for Excel export. Install with: pip install pandas openpyxl")
            return False
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return False
    
    @staticmethod
    def export_to_xls(data: List[Dict[str, Any]], output_path: str) -> bool:
        """Export data to Excel XLS format."""
        try:
            import pandas as pd
            
            df = pd.DataFrame(data)
            
            # Flatten measurements column if present
            if "measurements" in df.columns:
                measurements_df = pd.json_normalize(df["measurements"])
                measurements_df.columns = [f"measurement_{col}" for col in measurements_df.columns]
                df = df.drop(columns=["measurements"]).join(measurements_df)
            
            df.to_excel(output_path, index=False, engine="xlwt")
            logger.info(f"Exported {len(data)} records to Excel XLS: {output_path}")
            return True
        except ImportError:
            logger.error("pandas and xlwt required for Excel XLS export. Install with: pip install pandas xlwt")
            return False
        except Exception as e:
            logger.error(f"Error exporting to Excel XLS: {e}")
            return False
    
    @staticmethod
    def export_to_h5(data: List[Dict[str, Any]], output_path: str, key: str = "data") -> bool:
        """Export data to HDF5 format."""
        try:
            import pandas as pd
            
            df = pd.DataFrame(data)
            
            # Flatten measurements column if present
            if "measurements" in df.columns:
                measurements_df = pd.json_normalize(df["measurements"])
                measurements_df.columns = [f"measurement_{col}" for col in measurements_df.columns]
                df = df.drop(columns=["measurements"]).join(measurements_df)
            
            df.to_hdf(output_path, key=key, mode="w", format="table")
            logger.info(f"Exported {len(data)} records to HDF5: {output_path}")
            return True
        except ImportError:
            logger.error("pandas and tables required for HDF5 export. Install with: pip install pandas tables")
            return False
        except Exception as e:
            logger.error(f"Error exporting to HDF5: {e}")
            return False
    
    @staticmethod
    def export_to_arrow(data: List[Dict[str, Any]], output_path: str) -> bool:
        """Export data to Apache Arrow format."""
        try:
            import pandas as pd
            import pyarrow as pa
            import pyarrow.parquet as pq
            
            df = pd.DataFrame(data)
            
            # Flatten measurements column if present
            if "measurements" in df.columns:
                measurements_df = pd.json_normalize(df["measurements"])
                measurements_df.columns = [f"measurement_{col}" for col in measurements_df.columns]
                df = df.drop(columns=["measurements"]).join(measurements_df)
            
            table = pa.Table.from_pandas(df)
            with pa.OSFile(output_path, "wb") as f:
                with pa.RecordBatchStreamWriter(f, table.schema) as writer:
                    writer.write_table(table)
            
            logger.info(f"Exported {len(data)} records to Arrow: {output_path}")
            return True
        except ImportError:
            logger.error("pandas and pyarrow required for Arrow export. Install with: pip install pandas pyarrow")
            return False
        except Exception as e:
            logger.error(f"Error exporting to Arrow: {e}")
            return False
    
    @staticmethod
    def export(data: List[Dict[str, Any]], output_path: str, format: str, **kwargs) -> bool:
        """
        Export data to specified format.
        
        Args:
            data: List of records to export
            output_path: Output file path
            format: Format name (json, csv, txt, parquet, feather, duckdb, xlsx, xls, h5, arrow)
            **kwargs: Additional format-specific arguments
            
        Returns:
            True if successful
        """
        format = format.lower()
        
        if format == "json":
            return FileExporter.export_to_json(data, output_path, **kwargs)
        elif format == "csv":
            return FileExporter.export_to_csv(data, output_path, **kwargs)
        elif format == "txt":
            return FileExporter.export_to_txt(data, output_path, **kwargs)
        elif format == "parquet":
            return FileExporter.export_to_parquet(data, output_path)
        elif format == "feather":
            return FileExporter.export_to_feather(data, output_path)
        elif format == "duckdb":
            return FileExporter.export_to_duckdb(data, output_path, **kwargs)
        elif format == "xlsx":
            return FileExporter.export_to_xlsx(data, output_path)
        elif format == "xls":
            return FileExporter.export_to_xls(data, output_path)
        elif format == "h5":
            return FileExporter.export_to_h5(data, output_path, **kwargs)
        elif format == "arrow":
            return FileExporter.export_to_arrow(data, output_path)
        elif format == "jsonl" or format == "ndjson":
            return FileExporter.export_to_jsonl(data, output_path)
        elif format == "avro":
            return FileExporter.export_to_avro(data, output_path, **kwargs)
        elif format == "orc":
            return FileExporter.export_to_orc(data, output_path)
        elif format == "msgpack":
            return FileExporter.export_to_msgpack(data, output_path)
        elif format == "sqlite":
            return FileExporter.export_to_sqlite(data, output_path, **kwargs)
        elif format == "influxdb" or format == "lp":
            return FileExporter.export_to_influxdb_lp(data, output_path, **kwargs)
        else:
            logger.error(f"Unsupported format: {format}")
            return False
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """Get list of supported export formats."""
        return list(FileExporter.SUPPORTED_FORMATS.keys())
    
    @staticmethod
    def get_format_info(format: str) -> Optional[Dict[str, str]]:
        """Get format information."""
        return FileExporter.SUPPORTED_FORMATS.get(format.lower())
    
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
    def export_to_avro(data: List[Dict[str, Any]], output_path: str, schema: Optional[Dict] = None) -> bool:
        """Export data to Apache Avro format."""
        try:
            import fastavro
            
            if not data:
                logger.warning("No data to export")
                return False
            
            # Generate schema if not provided
            if schema is None:
                # Infer schema from first record
                sample_record = data[0]
                schema = {
                    "type": "record",
                    "name": "TimeSeriesRecord",
                    "fields": []
                }
                
                for key, value in sample_record.items():
                    if key == "measurements" and isinstance(value, dict):
                        # Flatten measurements
                        for m_key, m_value in value.items():
                            field_type = "double" if isinstance(m_value, (int, float)) else "string"
                            schema["fields"].append({
                                "name": f"measurement_{m_key}",
                                "type": ["null", field_type],
                                "default": None
                            })
                    else:
                        field_type = "string"  # Default to string for flexibility
                        if isinstance(value, (int, float)):
                            field_type = "double"
                        elif isinstance(value, bool):
                            field_type = "boolean"
                        schema["fields"].append({
                            "name": key,
                            "type": ["null", field_type],
                            "default": None
                        })
            
            # Flatten measurements for Avro
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
            
            # Flatten measurements column if present
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
            
            # Flatten measurements column if present
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
            from datetime import datetime
            
            with open(output_path, "w", encoding="utf-8") as f:
                for record in data:
                    # Extract series_id as measurement or use default
                    series_id = record.get("series_id", measurement)
                    
                    # Extract timestamp
                    timestamp = record.get("timestamp", "")
                    if isinstance(timestamp, str):
                        # Try to parse timestamp
                        try:
                            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                            ts_ns = int(dt.timestamp() * 1e9)
                        except:
                            ts_ns = ""
                    elif isinstance(timestamp, (int, float)):
                        ts_ns = int(timestamp * 1e9) if timestamp < 1e10 else int(timestamp)
                    else:
                        ts_ns = ""
                    
                    # Extract measurements as fields
                    fields = []
                    if "measurements" in record and isinstance(record["measurements"], dict):
                        for key, value in record["measurements"].items():
                            if isinstance(value, (int, float)):
                                fields.append(f"{key}={value}")
                            elif isinstance(value, bool):
                                fields.append(f"{key}={str(value).lower()}")
                            else:
                                fields.append(f'{key}="{value}"')
                    
                    # Build line protocol: measurement,tag1=value1 field1=value1,field2=value2 timestamp
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
