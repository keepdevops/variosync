"""
File format conversion utilities.
"""
from typing import Any, Dict, List
import json

from logger import get_logger

logger = get_logger()


class FormatConverters:
    """Format conversion utilities."""
    
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
            
            logger.info(f"Reading CSV file: {csv_file_path}")
            df = pd.read_csv(csv_file_path, header=0 if has_header else None)
            
            if df.empty:
                logger.warning(f"CSV file {csv_file_path} is empty")
                return False
            
            logger.info(f"Loaded {len(df)} rows from CSV file")
            
            conn = duckdb.connect(duckdb_file_path)
            
            if if_exists == "replace":
                conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            elif if_exists == "fail":
                tables = conn.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
                ).fetchall()
                if any(table[0] == table_name for table in tables):
                    logger.error(f"Table {table_name} already exists and if_exists='fail'")
                    conn.close()
                    return False
            
            conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df")
            
            if if_exists == "append":
                conn.execute(f"INSERT INTO {table_name} SELECT * FROM df")
            
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
            
            logger.info(f"Loading data from {input_file_path}")
            loader = FileLoader()
            records = loader.load(input_file_path)
            
            if not records:
                logger.warning(f"No records loaded from {input_file_path}")
                return False
            
            logger.info(f"Loaded {len(records)} records")
            
            df = pd.DataFrame(records)
            
            if normalize_measurements and 'measurements' in df.columns:
                measurements_df = pd.json_normalize(df['measurements'])
                measurements_df.columns = [f"measurement_{col}" for col in measurements_df.columns]
                df = df.drop(columns=['measurements']).join(measurements_df)
            
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                df = df.dropna(subset=['timestamp'])
                df = df.sort_values('timestamp')
            
            output_path = Path(output_file_path)
            
            if output_format.lower() == "json":
                df_dict = df.to_dict('records')
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    json.dump(df_dict, f, indent=2, default=str)
                logger.info(f"Saved {len(df_dict)} records as JSON to {output_file_path}")
                
            elif output_format.lower() == "parquet":
                df.to_parquet(output_file_path, index=False, engine='pyarrow')
                logger.info(f"Saved {len(df)} rows as Parquet to {output_file_path}")
                
            elif output_format.lower() == "csv":
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
