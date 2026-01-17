"""
Binary format loaders (Parquet, Feather, DuckDB).
"""
from typing import Any, Dict, List

from logger import get_logger

logger = get_logger()


class BinaryFormatHandlers:
    """Binary format handlers."""
    
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
