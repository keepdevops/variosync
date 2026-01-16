"""
VARIOSYNC Configuration Module
Handles configuration loading, validation, and management.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from config_validator import ConfigValidator
from logger import get_logger

logger = get_logger()


class Config:
    """Main configuration manager for VARIOSYNC."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to configuration JSON file
        """
        self.config_path = config_path or os.getenv("VARIOSYNC_CONFIG", "config.json")
        self.config: Dict[str, Any] = {}
        self.validator = ConfigValidator()
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file or environment."""
        config_file = Path(self.config_path)
        
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    self.config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in config file: {e}")
                self.config = {}
            except Exception as e:
                logger.error(f"Error loading config file: {e}")
                self.config = {}
        else:
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            self.config = self._get_default_config()
        
        # Override with environment variables
        self._load_from_env()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "Data": {
                "db_path": "variosync_data.duckdb",
                "csv_dir": "data",
                "json_dir": "data/json",
                "parquet_dir": "data/parquet",
                "cache_size": 1000,
                "thread_count": 4,
                "storage_backend": "local"
            },
            "Display": {
                "rows_per_page": 100,
                "auto_refresh": 0,
                "theme": "default",
                "font_size": 10
            },
            "Download": {
                "timeout": 30,
                "max_retries": 3,
                "rate_limit_delay": 1.0,
                "batch_size": 50
            },
            "Logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "variosync.log"
            },
            "Performance": {
                "enable_monitoring": True,
                "memory_limit": 1024,
                "cpu_limit": 80
            }
        }
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Supabase config
        if os.getenv("SUPABASE_URL"):
            if "Supabase" not in self.config:
                self.config["Supabase"] = {}
            self.config["Supabase"]["url"] = os.getenv("SUPABASE_URL")
        
        if os.getenv("SUPABASE_KEY"):
            if "Supabase" not in self.config:
                self.config["Supabase"] = {}
            self.config["Supabase"]["key"] = os.getenv("SUPABASE_KEY")
        
        # Storage config
        if os.getenv("AWS_BUCKET_NAME"):
            if "Data" not in self.config:
                self.config["Data"] = {}
            self.config["Data"]["storage_bucket"] = os.getenv("AWS_BUCKET_NAME")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate current configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate Supabase config if present
        if "Supabase" in self.config:
            is_valid, error = self.validator.validate_supabase_config(self.config["Supabase"])
            if not is_valid:
                return False, f"Invalid Supabase config: {error}"
        
        return True, None
