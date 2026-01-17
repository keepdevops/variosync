"""
VARIOSYNC Command Line Interface
"""
import argparse
import sys

from logger import get_logger
from .core import VariosyncApp

logger = get_logger()


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
            hours_consumed = 0.1
            app.auth_manager.consume_hours(user_id, hours_consumed)
            logger.info(f"Consumed {hours_consumed} hours for user {user_id}")
    
    logger.info("VARIOSYNC application completed successfully")


if __name__ == "__main__":
    main()
