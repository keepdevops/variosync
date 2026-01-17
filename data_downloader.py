"""
VARIOSYNC Free Data Downloader Module
Downloads free time-series datasets from public sources without API keys.
"""
import os
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from logger import get_logger

logger = get_logger()


class FreeDataDownloader:
    """Downloader for free time-series datasets (no API key required)."""
    
    FREE_DATASETS = {
        "world_bank_gdp": {
            "name": "World Bank GDP Data",
            "description": "GDP per capita for all countries",
            "url": "https://api.worldbank.org/v2/en/country/all/indicator/NY.GDP.PCAP.CD?format=csv&date=1960:2023",
            "format": "csv",
            "source": "World Bank"
        },
        "noaa_weather_sample": {
            "name": "NOAA Weather Sample",
            "description": "Sample weather data from NOAA",
            "url": "https://www.ncei.noaa.gov/data/gsod/access/2023/722860-13904-2023.op.gz",
            "format": "csv",
            "source": "NOAA",
            "note": "Requires decompression"
        },
        "example_stock_data": {
            "name": "Example Stock Data",
            "description": "Sample stock market data",
            "url": None,  # Would be a direct download URL
            "format": "csv",
            "source": "Example"
        }
    }
    
    @staticmethod
    def download_dataset(dataset_id: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Download a free dataset.
        
        Args:
            dataset_id: Dataset identifier from FREE_DATASETS
            output_path: Optional output path (defaults to data/ directory)
            
        Returns:
            Path to downloaded file or None if failed
        """
        if dataset_id not in FreeDataDownloader.FREE_DATASETS:
            logger.error(f"Unknown dataset: {dataset_id}")
            return None
        
        dataset = FreeDataDownloader.FREE_DATASETS[dataset_id]
        
        if not dataset.get("url"):
            logger.warning(f"Dataset {dataset_id} has no direct download URL")
            return None
        
        try:
            # Determine output path
            if output_path is None:
                data_dir = Path("data")
                data_dir.mkdir(exist_ok=True)
                url_path = Path(urlparse(dataset["url"]).path)
                filename = url_path.name or f"{dataset_id}.{dataset['format']}"
                output_path = str(data_dir / filename)
            
            # Download file
            logger.info(f"Downloading {dataset['name']} from {dataset['url']}")
            response = requests.get(dataset["url"], timeout=30, stream=True)
            response.raise_for_status()
            
            # Save file
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded {dataset['name']} to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error downloading dataset {dataset_id}: {e}")
            return None
    
    @staticmethod
    def list_available_datasets() -> Dict[str, Dict[str, Any]]:
        """
        List all available free datasets.
        
        Returns:
            Dictionary of dataset_id -> dataset_info
        """
        return FreeDataDownloader.FREE_DATASETS.copy()
    
    @staticmethod
    def get_dataset_info(dataset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a dataset.
        
        Args:
            dataset_id: Dataset identifier
            
        Returns:
            Dataset information dictionary or None
        """
        return FreeDataDownloader.FREE_DATASETS.get(dataset_id)
