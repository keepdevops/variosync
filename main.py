"""
VARIOSYNC Main Application Entry Point
Orchestrates the VARIOSYNC time-series data processing system.
"""
import argparse
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
from supabase_client import SupabaseClient

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
            # Load data using FileLoader
            loader = FileLoader()
            records = loader.load(file_path, file_format)
            
            if not records:
                logger.error(f"No records loaded from {file_path}")
                return False
            
            # Process records
            processed = self.processor.process_batch(records, record_type)
            
            # Save processed records
            success_count = 0
            for record in processed:
                if self.processor.save_record(record):
                    success_count += 1
            
            logger.info(f"Processed {success_count}/{len(processed)} records from {file_path}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="VARIOSYNC Time-Series Data Processing System")
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--process-file",
        type=str,
        help="Process data from a JSON file"
    )
    parser.add_argument(
        "--record-type",
        type=str,
        default="time_series",
        choices=["time_series", "financial"],
        help="Type of records in file"
    )
    parser.add_argument(
        "--file-format",
        type=str,
        help="File format override (json, csv, txt, parquet, feather, duckdb). Auto-detected if not specified."
    )
    parser.add_argument(
        "--license-key",
        type=str,
        help="License key for authentication"
    )
    parser.add_argument(
        "--required-hours",
        type=float,
        default=0.0,
        help="Required hours for operation"
    )
    
    args = parser.parse_args()
    
    # Initialize application
    app = VariosyncApp(args.config)
    
    # Authenticate if license key provided
    user_id = None
    if args.license_key:
        user_id = app.authenticate_user(args.license_key, args.required_hours)
        if not user_id:
            logger.error("Authentication failed, exiting")
            sys.exit(1)
    
    # Process file if provided
    if args.process_file:
        success = app.process_data_file(args.process_file, args.record_type, args.file_format)
        if not success:
            logger.error("Failed to process file")
            sys.exit(1)
        
        # Consume hours if authenticated
        if user_id:
            # Estimate hours consumed (e.g., 0.1 hours per file)
            hours_consumed = 0.1
            app.auth_manager.consume_hours(user_id, hours_consumed)
            logger.info(f"Consumed {hours_consumed} hours for user {user_id}")
    
    logger.info("VARIOSYNC application completed successfully")


if __name__ == "__main__":
    main()
