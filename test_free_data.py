#!/usr/bin/env python3
"""
Test VARIOSYNC with free time-series data sources.
Downloads sample datasets and tests upload/processing/export functionality.
"""
import os
import sys
import tempfile
import requests
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from file_loader import FileLoader
from file_exporter import FileExporter
from app.core import VariosyncApp
from logger import get_logger

logger = get_logger()

# Free data sources with direct download URLs
FREE_DATASETS = {
    "world_bank_gdp": {
        "name": "World Bank GDP Data (Generated Sample)",
        "url": None,  # Will generate sample
        "format": "csv",
        "description": "Sample GDP data in VARIOSYNC format"
    },
    "sample_stock": {
        "name": "Sample Stock Data (Generated)",
        "url": None,  # Will generate
        "format": "csv",
        "description": "Generated sample stock data"
    },
    "sample_sensor": {
        "name": "Sample Sensor Data (Generated)",
        "url": None,  # Will generate
        "format": "json",
        "description": "Generated sample sensor data"
    }
}


def generate_sample_stock_data(output_path: str) -> str:
    """Generate sample stock market data in CSV format (VARIOSYNC compatible)."""
    import csv
    from datetime import datetime, timedelta
    
    data = []
    base_date = datetime(2024, 1, 1)
    base_price = 150.0
    ticker = "AAPL"
    
    for i in range(30):  # 30 days of data
        date = base_date + timedelta(days=i)
        open_price = base_price + (i * 0.5) + (i % 3) * 0.2
        high = open_price + 1.5
        low = open_price - 1.0
        close = open_price + 0.3
        volume = 1000000 + (i * 10000)
        
        data.append({
            "ticker": ticker,
            "timestamp": date.strftime("%Y-%m-%dT09:30:00"),
            "open": f"{open_price:.2f}",
            "high": f"{high:.2f}",
            "low": f"{low:.2f}",
            "close": f"{close:.2f}",
            "volume": str(volume)
        })
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["ticker", "timestamp", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        writer.writerows(data)
    
    return output_path


def generate_sample_sensor_data(output_path: str) -> str:
    """Generate sample sensor data in JSON format."""
    import json
    from datetime import datetime, timedelta
    
    data = []
    base_date = datetime(2024, 1, 1, 0, 0, 0)
    
    for i in range(24):  # 24 hours of data
        timestamp = base_date + timedelta(hours=i)
        data.append({
            "series_id": "SENSOR-001",
            "timestamp": timestamp.isoformat(),
            "measurements": {
                "temperature": round(20 + (i % 12) * 0.5, 1),
                "humidity": round(50 + (i % 8) * 2, 1),
                "pressure": round(1013 + (i % 5), 1)
            },
            "metadata": {
                "location": "Building A",
                "sensor_type": "environmental"
            }
        })
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return output_path


def generate_sample_gdp_data(output_path: str) -> str:
    """Generate sample GDP data in CSV format (VARIOSYNC compatible)."""
    import csv
    from datetime import datetime, timedelta
    
    countries = ["USA", "CHN", "JPN", "DEU", "GBR"]
    data = []
    base_date = datetime(2020, 1, 1)
    
    for country in countries:
        for year in range(4):  # 2020-2023
            date = base_date.replace(year=2020 + year)
            # Simulate GDP per capita growth
            gdp = 30000 + (year * 2000) + (hash(country) % 10000)
            
            data.append({
                "series_id": f"GDP-{country}",
                "timestamp": date.strftime("%Y-01-01T00:00:00"),
                "measurements": {
                    "gdp_per_capita": gdp,
                    "country_code": country
                }
            })
    
    # Convert to CSV format
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["series_id", "timestamp", "gdp_per_capita", "country_code"])
        writer.writeheader()
        for record in data:
            writer.writerow({
                "series_id": record["series_id"],
                "timestamp": record["timestamp"],
                "gdp_per_capita": record["measurements"]["gdp_per_capita"],
                "country_code": record["measurements"]["country_code"]
            })
    
    return output_path


def download_dataset(dataset_id: str, output_dir: Path) -> Optional[str]:
    """Download a dataset from FREE_DATASETS."""
    if dataset_id not in FREE_DATASETS:
        logger.error(f"Unknown dataset: {dataset_id}")
        return None
    
    dataset = FREE_DATASETS[dataset_id]
    
    # Generate sample data if no URL
    if dataset["url"] is None:
        if dataset_id == "sample_stock":
            output_path = output_dir / "sample_stock.csv"
            return generate_sample_stock_data(str(output_path))
        elif dataset_id == "sample_sensor":
            output_path = output_dir / "sample_sensor.json"
            return generate_sample_sensor_data(str(output_path))
        elif dataset_id == "world_bank_gdp":
            # Generate sample GDP data
            output_path = output_dir / "world_bank_gdp.csv"
            return generate_sample_gdp_data(str(output_path))
        return None
    
    try:
        output_path = output_dir / f"{dataset_id}.{dataset['format']}"
        
        logger.info(f"Downloading {dataset['name']}...")
        response = requests.get(dataset["url"], timeout=30, stream=True)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"✅ Downloaded to {output_path}")
        return str(output_path)
        
    except Exception as e:
        logger.error(f"❌ Error downloading {dataset_id}: {e}")
        return None


def test_format_loading(file_path: str, format_name: Optional[str] = None) -> bool:
    """Test loading a file in a specific format."""
    try:
        loader = FileLoader()
        records = loader.load(file_path, file_format=format_name)
        
        if records:
            logger.info(f"✅ Loaded {len(records)} records from {Path(file_path).name}")
            if len(records) > 0:
                logger.info(f"   First record keys: {list(records[0].keys())[:5]}")
            return True
        else:
            logger.warning(f"⚠️  No records loaded from {Path(file_path).name}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error loading {file_path}: {e}")
        return False


def test_format_export(data_file: str, export_format: str) -> bool:
    """Test exporting data to a specific format."""
    try:
        loader = FileLoader()
        records = loader.load(data_file)
        
        if not records:
            logger.warning(f"⚠️  No data to export from {data_file}")
            return False
        
        # Export to temp file
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=f".{export_format}")
        temp_output.close()
        
        exporter = FileExporter()
        success = exporter.export(records, temp_output.name, format=export_format)
        
        if success and Path(temp_output.name).exists():
            file_size = Path(temp_output.name).stat().st_size
            logger.info(f"✅ Exported to {export_format} ({file_size} bytes)")
            os.unlink(temp_output.name)
            return True
        else:
            logger.error(f"❌ Export to {export_format} failed")
            if Path(temp_output.name).exists():
                os.unlink(temp_output.name)
            return False
            
    except Exception as e:
        logger.error(f"❌ Error exporting to {export_format}: {e}")
        return False


def test_processing(file_path: str, record_type: str = "time_series") -> bool:
    """Test processing a file through VariosyncApp."""
    try:
        app = VariosyncApp()
        success = app.process_data_file(file_path, record_type=record_type)
        
        if success:
            logger.info(f"✅ Successfully processed {Path(file_path).name} as {record_type}")
            return True
        else:
            logger.warning(f"⚠️  Processing failed for {Path(file_path).name}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error processing {file_path}: {e}")
        return False


def main():
    """Main test function."""
    print("=" * 70)
    print("VARIOSYNC Free Data Test Suite")
    print("=" * 70)
    print()
    
    # Create temp directory for test data
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    results = {
        "downloads": [],
        "loads": [],
        "exports": [],
        "processing": []
    }
    
    # Test 1: Download free datasets
    print("📥 Step 1: Downloading Free Datasets")
    print("-" * 70)
    
    for dataset_id in FREE_DATASETS.keys():
        file_path = download_dataset(dataset_id, test_dir)
        if file_path:
            results["downloads"].append((dataset_id, file_path, True))
        else:
            results["downloads"].append((dataset_id, None, False))
    
    print()
    
    # Test 2: Test format loading
    print("📂 Step 2: Testing Format Loading")
    print("-" * 70)
    
    for dataset_id, file_path, downloaded in results["downloads"]:
        if downloaded and file_path:
            dataset = FREE_DATASETS[dataset_id]
            format_name = dataset.get("format")
            
            # Test auto-detection
            success = test_format_loading(file_path)
            results["loads"].append((dataset_id, format_name, "auto", success))
            
            # Test explicit format if specified
            if format_name:
                success = test_format_loading(file_path, format_name)
                results["loads"].append((dataset_id, format_name, format_name, success))
    
    print()
    
    # Test 3: Test format export
    print("📤 Step 3: Testing Format Export")
    print("-" * 70)
    
    # Use first successfully loaded file for export tests
    test_file = None
    for dataset_id, file_path, downloaded in results["downloads"]:
        if downloaded and file_path:
            test_file = file_path
            break
    
    if test_file:
        # Test exporting to various formats
        export_formats = ["json", "csv", "parquet", "jsonl", "stooq"]
        
        for fmt in export_formats:
            success = test_format_export(test_file, fmt)
            results["exports"].append((fmt, success))
    else:
        print("⚠️  No test file available for export testing")
    
    print()
    
    # Test 4: Test processing
    print("⚙️  Step 4: Testing Data Processing")
    print("-" * 70)
    
    for dataset_id, file_path, downloaded in results["downloads"]:
        if downloaded and file_path:
            dataset = FREE_DATASETS[dataset_id]
            record_type = "financial" if "stock" in dataset_id else "time_series"
            
            success = test_processing(file_path, record_type)
            results["processing"].append((dataset_id, record_type, success))
    
    print()
    
    # Summary
    print("=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    
    downloads_ok = sum(1 for _, _, ok in results["downloads"] if ok)
    loads_ok = sum(1 for _, _, _, ok in results["loads"] if ok)
    exports_ok = sum(1 for _, ok in results["exports"] if ok)
    processing_ok = sum(1 for _, _, ok in results["processing"] if ok)
    
    print(f"Downloads:  {downloads_ok}/{len(results['downloads'])} ✅")
    print(f"Loads:      {loads_ok}/{len(results['loads'])} ✅")
    print(f"Exports:    {exports_ok}/{len(results['exports'])} ✅")
    print(f"Processing: {processing_ok}/{len(results['processing'])} ✅")
    print()
    
    total_tests = len(results["downloads"]) + len(results["loads"]) + len(results["exports"]) + len(results["processing"])
    total_passed = downloads_ok + loads_ok + exports_ok + processing_ok
    
    print(f"Overall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check logs above for details.")
    
    print("=" * 70)
    print(f"\nTest data saved in: {test_dir.absolute()}")
    print("You can manually upload these files through the web UI for further testing.")


if __name__ == "__main__":
    main()
