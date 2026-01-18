"""
Database format exporters (TimescaleDB, QuestDB).
SQLite and DuckDB are already implemented in specialized.py and binary.py.
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import json

from logger import get_logger

logger = get_logger()


class DatabaseExporter:
    """Database format exporters."""
    
    @staticmethod
    def _parse_timestamp(timestamp: Any) -> Optional[datetime]:
        """Parse timestamp to datetime object."""
        if isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except:
                return None
        elif isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp if timestamp < 1e10 else timestamp / 1e9)
        return None
    
    @staticmethod
    def _extract_timescaledb_records(data: List[Dict[str, Any]]) -> List[Tuple]:
        """Extract records for TimescaleDB insertion."""
        records = []
        for record in data:
            dt = DatabaseExporter._parse_timestamp(record.get("timestamp", ""))
            if dt is None:
                continue
            
            series_id = record.get("series_id", "default")
            metadata = json.dumps(record.get("metadata", {}))
            
            if "measurements" in record and isinstance(record["measurements"], dict):
                for key, value in record["measurements"].items():
                    if isinstance(value, (int, float)):
                        records.append((dt, series_id, key, float(value), metadata))
        return records
    
    @staticmethod
    def export_to_timescaledb(
        data: List[Dict[str, Any]], 
        output_path: str,
        table_name: str = "time_series_data",
        **kwargs
    ) -> bool:
        """Export data to TimescaleDB format."""
        try:
            connection_string = kwargs.get("connection_string")
            create_hypertable = kwargs.get("create_hypertable", True)
            
            if not data:
                logger.warning("No data to export")
                return False
            
            # Try direct connection if connection_string provided
            if connection_string:
                try:
                    import psycopg2
                    from psycopg2.extras import execute_values
                    
                    conn = psycopg2.connect(connection_string)
                    cur = conn.cursor()
                    
                    cur.execute(f"""
                        CREATE TABLE IF NOT EXISTS {table_name} (
                            time TIMESTAMPTZ NOT NULL,
                            series_id TEXT,
                            measurement_name TEXT,
                            value DOUBLE PRECISION,
                            metadata JSONB
                        )
                    """)
                    
                    if create_hypertable:
                        try:
                            cur.execute(f"SELECT create_hypertable('{table_name}', 'time', if_not_exists => TRUE)")
                        except:
                            logger.warning("Could not create hypertable. TimescaleDB extension may not be enabled.")
                    
                    records = DatabaseExporter._extract_timescaledb_records(data)
                    if records:
                        execute_values(
                            cur,
                            f"INSERT INTO {table_name} (time, series_id, measurement_name, value, metadata) VALUES %s",
                            records
                        )
                    
                    conn.commit()
                    cur.close()
                    conn.close()
                    
                    logger.info(f"Exported {len(data)} records to TimescaleDB table '{table_name}'")
                    return True
                except ImportError:
                    logger.warning("psycopg2 not available, creating SQL file instead")
                except Exception as e:
                    logger.warning(f"Direct connection failed: {e}, creating SQL file instead")
            
            # Create SQL file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"-- TimescaleDB Import File\n")
                f.write(f"-- Created by VARIOSYNC on {datetime.now().isoformat()}\n\n")
                f.write(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
                f.write(f"    time TIMESTAMPTZ NOT NULL,\n")
                f.write(f"    series_id TEXT,\n")
                f.write(f"    measurement_name TEXT,\n")
                f.write(f"    value DOUBLE PRECISION,\n")
                f.write(f"    metadata JSONB\n")
                f.write(f");\n\n")
                
                if create_hypertable:
                    f.write(f"SELECT create_hypertable('{table_name}', 'time', if_not_exists => TRUE);\n\n")
                
                f.write(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_series ON {table_name} (series_id);\n")
                f.write(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_measurement ON {table_name} (measurement_name);\n\n")
                f.write(f"-- Data inserts\n")
                
                for record in data:
                    dt = DatabaseExporter._parse_timestamp(record.get("timestamp", ""))
                    if dt is None:
                        continue
                    
                    ts_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                    series_id = record.get("series_id", "default").replace("'", "''")
                    metadata = json.dumps(record.get("metadata", {})).replace("'", "''")
                    
                    if "measurements" in record and isinstance(record["measurements"], dict):
                        for key, value in record["measurements"].items():
                            if isinstance(value, (int, float)):
                                key_escaped = key.replace("'", "''")
                                f.write(f"INSERT INTO {table_name} (time, series_id, measurement_name, value, metadata) VALUES ('{ts_str}', '{series_id}', '{key_escaped}', {float(value)}, '{metadata}');\n")
            
            logger.info(f"Exported {len(data)} records to TimescaleDB SQL format: {output_path}")
            logger.warning("Note: For direct import, provide connection_string parameter. Otherwise, use psql to import the SQL file.")
            return True
        except Exception as e:
            logger.error(f"Error exporting to TimescaleDB format: {e}")
            return False
    
    @staticmethod
    def _parse_timestamp_ns(timestamp: Any) -> Optional[int]:
        """Parse timestamp to nanoseconds."""
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                return int(dt.timestamp() * 1e9)
            except:
                return None
        elif isinstance(timestamp, (int, float)):
            return int(timestamp * 1e9) if timestamp < 1e10 else int(timestamp)
        return None
    
    @staticmethod
    def _build_ilp_line(table_name: str, record: Dict[str, Any]) -> Optional[str]:
        """Build ILP (InfluxDB Line Protocol) line for QuestDB."""
        ts_ns = DatabaseExporter._parse_timestamp_ns(record.get("timestamp", ""))
        if ts_ns is None:
            return None
        
        series_id = record.get("series_id", table_name)
        tags = [f"series_id={series_id}"]
        
        if "metadata" in record and isinstance(record["metadata"], dict):
            for key, value in record["metadata"].items():
                tags.append(f"{key}={value}")
        
        fields = []
        if "measurements" in record and isinstance(record["measurements"], dict):
            for key, value in record["measurements"].items():
                if isinstance(value, (int, float)):
                    fields.append(f"{key}={value}")
                elif isinstance(value, bool):
                    fields.append(f"{key}={str(value).lower()}")
                else:
                    fields.append(f'{key}="{value}"')
        
        if fields:
            return f"{table_name},{','.join(tags)} {','.join(fields)} {ts_ns}"
        return None
    
    @staticmethod
    def export_to_questdb(
        data: List[Dict[str, Any]], 
        output_path: str,
        table_name: str = "time_series_data",
        **kwargs
    ) -> bool:
        """Export data to QuestDB format (ILP)."""
        try:
            host = kwargs.get("host")
            port = kwargs.get("port", 9000)
            
            if not data:
                logger.warning("No data to export")
                return False
            
            # Build ILP lines
            ilp_lines = []
            for record in data:
                line = DatabaseExporter._build_ilp_line(table_name, record)
                if line:
                    ilp_lines.append(line)
            
            if not ilp_lines:
                logger.error("No valid records to export")
                return False
            
            # Try direct import if host provided
            if host:
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((host, port))
                    sock.sendall('\n'.join(ilp_lines).encode('utf-8'))
                    sock.close()
                    logger.info(f"Exported {len(data)} records to QuestDB via ILP")
                    return True
                except ImportError:
                    logger.warning("Socket not available, creating ILP file instead")
                except Exception as e:
                    logger.warning(f"Direct import failed: {e}, creating ILP file instead")
            
            # Create ILP file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write('\n'.join(ilp_lines) + '\n')
            
            logger.info(f"Exported {len(data)} records to QuestDB ILP format: {output_path}")
            logger.warning("Note: For direct import, provide host parameter. Otherwise, use: cat file.ilp | nc localhost 9000")
            return True
        except Exception as e:
            logger.error(f"Error exporting to QuestDB format: {e}")
            return False
