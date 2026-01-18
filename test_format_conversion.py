#!/usr/bin/env python3
"""
Test script for format conversion functionality.
Tests conversion between various formats.
"""
import json
import tempfile
import os
from pathlib import Path
from format_converter import FormatConverter
from file_exporter import FileExporter

def create_sample_data():
    """Create sample time-series data for testing."""
    return [
        {
            "series_id": "AAPL",
            "timestamp": "2024-01-15T09:30:00Z",
            "measurements": {
                "open": 150.25,
                "high": 152.30,
                "low": 149.80,
                "close": 151.50,
                "volume": 1000000
            },
            "metadata": {"exchange": "NASDAQ"}
        },
        {
            "series_id": "AAPL",
            "timestamp": "2024-01-15T10:00:00Z",
            "measurements": {
                "open": 151.50,
                "high": 153.20,
                "low": 151.00,
                "close": 152.75,
                "volume": 1200000
            },
            "metadata": {"exchange": "NASDAQ"}
        },
        {
            "series_id": "MSFT",
            "timestamp": "2024-01-15T09:30:00Z",
            "measurements": {
                "open": 380.50,
                "high": 382.00,
                "low": 379.25,
                "close": 381.00,
                "volume": 500000
            },
            "metadata": {"exchange": "NASDAQ"}
        }
    ]

def test_format_conversion():
    """Test format conversion between different formats."""
    print("=" * 60)
    print("Testing Format Conversion")
    print("=" * 60)
    
    # Create sample data
    sample_data = create_sample_data()
    
    # Create temporary directory for test files
    test_dir = tempfile.mkdtemp(prefix="variosync_test_")
    print(f"\nTest directory: {test_dir}\n")
    
    # Test formats to convert
    test_formats = [
        ("json", "csv"),
        ("json", "parquet"),
        ("json", "jsonl"),
        ("csv", "json"),
        ("json", "influxdb"),
        ("json", "opentsdb"),
    ]
    
    # First, create a JSON file
    json_file = os.path.join(test_dir, "test_data.json")
    with open(json_file, "w") as f:
        json.dump(sample_data, f, indent=2)
    print(f"✓ Created test JSON file: {json_file}")
    
    # Test conversions
    success_count = 0
    fail_count = 0
    
    for input_format, output_format in test_formats:
        try:
            input_file = json_file if input_format == "json" else None
            if input_file is None:
                # Create input file in the required format
                input_file = os.path.join(test_dir, f"test_data.{input_format}")
                exporter = FileExporter()
                exporter.export(sample_data, input_file, format=input_format)
            
            output_file = os.path.join(test_dir, f"test_data.{output_format}")
            
            print(f"\nTesting: {input_format} -> {output_format}")
            success = FormatConverter.convert(
                input_file,
                output_file,
                input_format=input_format,
                output_format=output_format
            )
            
            if success and os.path.exists(output_file):
                size = os.path.getsize(output_file)
                print(f"  ✓ Success! Output file: {output_file} ({size} bytes)")
                success_count += 1
            else:
                print(f"  ✗ Failed")
                fail_count += 1
        except Exception as e:
            print(f"  ✗ Error: {e}")
            fail_count += 1
    
    # Test format detection
    print(f"\n{'=' * 60}")
    print("Testing Format Detection")
    print("=" * 60)
    
    test_files = {
        "test.json": "json",
        "test.csv": "csv",
        "test.parquet": "parquet",
        "test.jsonl": "jsonl",
        "test.lp": "influxdb",
        "test.tsdb": "opentsdb",
        "test.pb": "protobuf",
        "test.gz": "gzip",
        "test.zip": "zip",
    }
    
    for filename, expected_format in test_files.items():
        detected = FormatConverter.detect_format_from_path(filename)
        detected_str = detected if detected else "None"
        status = "✓" if detected == expected_format else "✗"
        print(f"{status} {filename:20} -> {detected_str:15} (expected: {expected_format})")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("Test Summary")
    print("=" * 60)
    print(f"Successful conversions: {success_count}")
    print(f"Failed conversions: {fail_count}")
    print(f"Total formats supported: {len(FileExporter.get_supported_formats())}")
    print(f"\nTest files saved in: {test_dir}")
    print("(Clean up manually if needed)")

if __name__ == "__main__":
    test_format_conversion()
