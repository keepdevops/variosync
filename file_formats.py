"""
VARIOSYNC File Format Handlers Module
Handles loading data from specific file formats.
"""
import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from logger import get_logger

logger = get_logger()


class FormatHandlers:
    """Handlers for different file formats."""
    
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
    def load_csv(file_path: str, has_header: bool = True) -> List[Dict[str, Any]]:
        """Load data from CSV file."""
        try:
            records = []
            
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f) if has_header else csv.reader(f)
                
                if has_header:
                    for row in reader:
                        records.append(dict(row))
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
                                try:
                                    record["measurements"][header] = float(value)
                                except ValueError:
                                    record["measurements"][header] = value
                            records.append(record)
            
            logger.info(f"Loaded {len(records)} records from CSV file")
            return records
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {e}")
            return []
    
    @staticmethod
    def load_txt(file_path: str, delimiter: str = "\t") -> List[Dict[str, Any]]:
        """Load data from TXT file."""
        try:
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
                                record = dict(zip(headers, parts))
                            else:
                                record = {
                                    "series_id": parts[0],
                                    "timestamp": parts[1],
                                    "measurements": {f"value_{i}": parts[i] for i in range(2, len(parts))}
                                }
                            records.append(record)
            
            logger.info(f"Loaded {len(records)} records from TXT file")
            return records
        except Exception as e:
            logger.error(f"Error loading TXT file {file_path}: {e}")
            return []
    
    @staticmethod
    def load_parquet(file_path: str) -> List[Dict[str, Any]]:
        """Load data from Parquet file."""
        try:
            import pandas as pd
            
            df = pd.read_parquet(file_path)
            records = df.to_dict("records")
            
            logger.info(f"Loaded {len(records)} records from Parquet file")
            return records
        except ImportError:
            logger.error("pandas is required for Parquet support. Install with: pip install pandas pyarrow")
            return []
        except Exception as e:
            logger.error(f"Error loading Parquet file {file_path}: {e}")
            return []
    
    @staticmethod
    def load_feather(file_path: str) -> List[Dict[str, Any]]:
        """Load data from Feather file."""
        try:
            import pandas as pd
            
            df = pd.read_feather(file_path)
            records = df.to_dict("records")
            
            logger.info(f"Loaded {len(records)} records from Feather file")
            return records
        except ImportError:
            logger.error("pandas is required for Feather support. Install with: pip install pandas pyarrow")
            return []
        except Exception as e:
            logger.error(f"Error loading Feather file {file_path}: {e}")
            return []
    
    @staticmethod
    def load_duckdb(file_path: str, table_name: str = "time_series_data") -> List[Dict[str, Any]]:
        """Load data from DuckDB file."""
        try:
            import duckdb
            
            conn = duckdb.connect(file_path)
            result = conn.execute(f"SELECT * FROM {table_name}").fetchall()
            columns = [desc[0] for desc in conn.execute(f"SELECT * FROM {table_name}").description]
            
            records = [dict(zip(columns, row)) for row in result]
            conn.close()
            
            logger.info(f"Loaded {len(records)} records from DuckDB file")
            return records
        except ImportError:
            logger.error("duckdb is required for DuckDB support. Install with: pip install duckdb")
            return []
        except Exception as e:
            logger.error(f"Error loading DuckDB file {file_path}: {e}")
            return []
    
    @staticmethod
    def convert_csv_to_duckdb(
        csv_file_path: str,
        duckdb_file_path: str,
        table_name: str = "time_series_data",
        has_header: bool = True,
        if_exists: str = "replace"
    ) -> bool:
        """
        Convert CSV file to DuckDB format.
        
        Args:
            csv_file_path: Path to input CSV file
            duckdb_file_path: Path to output DuckDB file
            table_name: Name of the table to create in DuckDB
            has_header: Whether CSV has header row
            if_exists: What to do if table exists ('replace', 'append', 'fail')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import duckdb
            import pandas as pd
            from pathlib import Path
            
            # Read CSV file
            logger.info(f"Reading CSV file: {csv_file_path}")
            df = pd.read_csv(csv_file_path, header=0 if has_header else None)
            
            if df.empty:
                logger.warning(f"CSV file {csv_file_path} is empty")
                return False
            
            logger.info(f"Loaded {len(df)} rows from CSV file")
            
            # Connect to DuckDB (create if doesn't exist)
            conn = duckdb.connect(duckdb_file_path)
            
            # Handle table existence
            if if_exists == "replace":
                conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            elif if_exists == "fail":
                # Check if table exists
                tables = conn.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
                ).fetchall()
                if any(table[0] == table_name for table in tables):
                    logger.error(f"Table {table_name} already exists and if_exists='fail'")
                    conn.close()
                    return False
            
            # Create table from DataFrame
            conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df")
            
            # If appending, insert data
            if if_exists == "append":
                conn.execute(f"INSERT INTO {table_name} SELECT * FROM df")
            
            # Verify the conversion
            count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            conn.close()
            
            logger.info(f"Successfully converted CSV to DuckDB: {count} rows in table '{table_name}'")
            return True
            
        except ImportError as e:
            logger.error(f"Required library not available: {e}. Install with: pip install duckdb pandas")
            return False
        except Exception as e:
            logger.error(f"Error converting CSV to DuckDB: {e}")
            return False
    
    @staticmethod
    def convert_to_plotly_format(
        input_file_path: str,
        output_file_path: str,
        output_format: str = "json",
        normalize_measurements: bool = True
    ) -> bool:
        """
        Convert any supported file format to a Plotly-friendly format.
        
        Plotly works best with:
        - JSON arrays of records
        - Parquet files (pandas DataFrame)
        - CSV files with normalized structure
        
        Args:
            input_file_path: Path to input file
            output_file_path: Path to output file
            output_format: Output format ('json', 'parquet', 'csv')
            normalize_measurements: Whether to flatten measurements dict into columns
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import pandas as pd
            from pathlib import Path
            from file_loader import FileLoader
            
            # Load data from any supported format
            logger.info(f"Loading data from {input_file_path}")
            loader = FileLoader()
            records = loader.load(input_file_path)
            
            if not records:
                logger.warning(f"No records loaded from {input_file_path}")
                return False
            
            logger.info(f"Loaded {len(records)} records")
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            # Normalize measurements if requested
            if normalize_measurements and 'measurements' in df.columns:
                # Expand measurements dict into separate columns
                measurements_df = pd.json_normalize(df['measurements'])
                # Add prefix to measurement columns
                measurements_df.columns = [f"measurement_{col}" for col in measurements_df.columns]
                # Drop original measurements column and join
                df = df.drop(columns=['measurements']).join(measurements_df)
            
            # Ensure timestamp is datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                df = df.dropna(subset=['timestamp'])
                df = df.sort_values('timestamp')
            
            # Save in requested format
            output_path = Path(output_file_path)
            
            if output_format.lower() == "json":
                # Save as JSON array (Plotly-friendly)
                df_dict = df.to_dict('records')
                import json
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    json.dump(df_dict, f, indent=2, default=str)
                logger.info(f"Saved {len(df_dict)} records as JSON to {output_file_path}")
                
            elif output_format.lower() == "parquet":
                # Save as Parquet (efficient for Plotly)
                df.to_parquet(output_file_path, index=False, engine='pyarrow')
                logger.info(f"Saved {len(df)} rows as Parquet to {output_file_path}")
                
            elif output_format.lower() == "csv":
                # Save as CSV (Plotly can read via pandas)
                df.to_csv(output_file_path, index=False)
                logger.info(f"Saved {len(df)} rows as CSV to {output_file_path}")
                
            else:
                logger.error(f"Unsupported output format: {output_format}")
                return False
            
            return True
            
        except ImportError as e:
            logger.error(f"Required library not available: {e}. Install with: pip install pandas pyarrow")
            return False
        except Exception as e:
            logger.error(f"Error converting to Plotly format: {e}")
            return False
