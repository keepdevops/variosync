"""
Binary format exporters (Parquet, Feather, DuckDB, Excel, H5, Arrow).
"""
from typing import Any, Dict, List

from logger import get_logger

logger = get_logger()


class BinaryExporter:
    """Binary format exporters."""
    
    @staticmethod
    def _flatten_dataframe(df):
        """Flatten measurements column in DataFrame."""
        if "measurements" in df.columns:
            import pandas as pd
            measurements_df = pd.json_normalize(df["measurements"])
            measurements_df.columns = [f"measurement_{col}" for col in measurements_df.columns]
            df = df.drop(columns=["measurements"]).join(measurements_df)
        return df
    
    @staticmethod
    def export_to_parquet(data: List[Dict[str, Any]], output_path: str) -> bool:
        """Export data to Parquet format."""
        try:
            import pandas as pd
            
            df = pd.DataFrame(data)
            df = BinaryExporter._flatten_dataframe(df)
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
            df = BinaryExporter._flatten_dataframe(df)
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
            df = BinaryExporter._flatten_dataframe(df)
            
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
            df = BinaryExporter._flatten_dataframe(df)
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
            df = BinaryExporter._flatten_dataframe(df)
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
            df = BinaryExporter._flatten_dataframe(df)
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
            
            df = pd.DataFrame(data)
            df = BinaryExporter._flatten_dataframe(df)
            
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
