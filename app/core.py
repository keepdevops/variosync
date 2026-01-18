"""
VARIOSYNC Core Application Class
"""
import sys
from datetime import datetime
from typing import Optional

from api_downloader import APIDownloader
from auth import AuthManager, AuthenticationError, PaymentError
from config import Config
from data_processor import TimeSeriesProcessor
from file_loader import FileLoader
from logger import VariosyncLogger, get_logger
from storage import StorageFactory

logger = get_logger()


class VariosyncApp:
    """Main VARIOSYNC application class."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize VARIOSYNC application.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = Config(config_path)
        
        # Validate configuration
        is_valid, error = self.config.validate()
        if not is_valid:
            logger.error(f"Invalid configuration: {error}")
            sys.exit(1)
        
        # Setup logger from config
        logging_config = self.config.get("Logging", {})
        VariosyncLogger.setup_logger(
            log_level=logging_config.get("level", "INFO"),
            log_format=logging_config.get("format"),
            log_file=logging_config.get("file", "variosync.log")
        )
        
        # Initialize storage
        data_config = self.config.get("Data", {})
        storage_backend = data_config.get("storage_backend", "local")
        storage_bucket = data_config.get("storage_bucket")
        storage_base_path = data_config.get("csv_dir", "data")
        
        self.storage = StorageFactory.create(
            backend_type=storage_backend,
            base_path=storage_base_path,
            bucket_name=storage_bucket
        )
        
        # Initialize authentication
        self.auth_manager = AuthManager(self.config.config)
        
        # Initialize data processor
        self.processor = TimeSeriesProcessor(self.storage)
        
        logger.info("VARIOSYNC application initialized")
    
    def process_data_file(self, file_path: str, record_type: str = "time_series", file_format: Optional[str] = None) -> bool:
        """
        Process data from a file.
        
        Args:
            file_path: Path to data file
            record_type: Type of records in file
            file_format: Optional file format override (auto-detected if None)
            
        Returns:
            True if successful
        """
        try:
            from pathlib import Path
            
            # Check if file exists
            if not Path(file_path).exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            loader = FileLoader()
            records = loader.load(file_path, file_format)
            
            if not records:
                # Try to provide more helpful error message
                ext = Path(file_path).suffix.lower()
                if ext == ".txt":
                    logger.error(f"No records loaded from {file_path}. File might be empty, have wrong delimiter, or invalid format. Try specifying format='stooq' for Stooq format files.")
                else:
                    logger.error(f"No records loaded from {file_path}. File might be empty or have invalid format.")
                return False
            
            processed = self.processor.process_batch(records, record_type)
            
            if not processed:
                logger.error(f"No records processed from {file_path} (loaded {len(records)} but processing failed)")
                return False
            
            success_count = 0
            for record in processed:
                if self.processor.save_record(record):
                    success_count += 1
            
            logger.info(f"Processed {success_count}/{len(processed)} records from {file_path}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
            return False
    
    def convert_csv_to_duckdb(
        self,
        csv_file_path: str,
        duckdb_file_path: Optional[str] = None,
        table_name: str = "time_series_data",
        has_header: bool = True,
        if_exists: str = "replace"
    ) -> bool:
        """
        Convert CSV file to DuckDB format.
        
        Args:
            csv_file_path: Path to input CSV file
            duckdb_file_path: Path to output DuckDB file (defaults to CSV path with .duckdb extension)
            table_name: Name of the table to create in DuckDB
            has_header: Whether CSV has header row
            if_exists: What to do if table exists ('replace', 'append', 'fail')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from pathlib import Path
            from file_formats import FormatHandlers
            
            if duckdb_file_path is None:
                csv_path = Path(csv_file_path)
                duckdb_file_path = str(csv_path.with_suffix('.duckdb'))
            
            handlers = FormatHandlers()
            success = handlers.convert_csv_to_duckdb(
                csv_file_path=csv_file_path,
                duckdb_file_path=duckdb_file_path,
                table_name=table_name,
                has_header=has_header,
                if_exists=if_exists
            )
            
            if success:
                logger.info(f"Successfully converted {csv_file_path} to {duckdb_file_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error converting CSV to DuckDB: {e}")
            return False
    
    def convert_to_plotly_format(
        self,
        input_file_path: str,
        output_file_path: Optional[str] = None,
        output_format: str = "json",
        normalize_measurements: bool = True
    ) -> bool:
        """
        Convert any supported file format to a Plotly-friendly format.
        
        Args:
            input_file_path: Path to input file
            output_file_path: Path to output file (defaults to input path with new extension)
            output_format: Output format ('json', 'parquet', 'csv')
            normalize_measurements: Whether to flatten measurements dict into columns
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from pathlib import Path
            from file_formats import FormatHandlers
            
            if output_file_path is None:
                input_path = Path(input_file_path)
                ext_map = {
                    "json": ".json",
                    "parquet": ".parquet",
                    "csv": ".csv"
                }
                ext = ext_map.get(output_format.lower(), ".json")
                output_file_path = str(input_path.with_suffix(ext))
            
            handlers = FormatHandlers()
            success = handlers.convert_to_plotly_format(
                input_file_path=input_file_path,
                output_file_path=output_file_path,
                output_format=output_format,
                normalize_measurements=normalize_measurements
            )
            
            if success:
                logger.info(f"Successfully converted {input_file_path} to Plotly format: {output_file_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error converting to Plotly format: {e}")
            return False
    
    def download_from_api(
        self,
        api_config: dict,
        entity_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> bool:
        """
        Download data from an API.
        
        Args:
            api_config: API downloader configuration
            entity_id: Entity identifier
            start_date: Start date
            end_date: End date
            
        Returns:
            True if successful
        """
        try:
            downloader = APIDownloader(api_config, self.storage)
            return downloader.download_and_save(entity_id, start_date, end_date)
        except Exception as e:
            logger.error(f"Error downloading from API: {e}")
            return False
    
    def authenticate_user(self, license_key: str, required_hours: float = 0.0) -> Optional[str]:
        """
        Authenticate user and check hours.
        
        Args:
            license_key: User license key
            required_hours: Required hours for operation
            
        Returns:
            User ID if successful, None otherwise
        """
        try:
            user_id, hours_remaining = self.auth_manager.authenticate(license_key, required_hours)
            logger.info(f"User {user_id} authenticated, {hours_remaining} hours remaining")
            return user_id
        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            return None
        except PaymentError as e:
            logger.error(f"Payment check failed: {e}")
            return None
