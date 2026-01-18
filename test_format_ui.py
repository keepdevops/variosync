#!/usr/bin/env python3
"""
Test format conversion through the application API.
"""
import json
import tempfile
import os
from format_converter import FormatConverter
from file_exporter import FileExporter

def test_format_conversion_ui():
    """Test formats that would be used in the UI."""
    print("=" * 60)
    print("Testing Format Conversion for UI")
    print("=" * 60)
    
    # Sample data
    sample_data = [
        {
            "series_id": "TEST001",
            "timestamp": "2024-01-15T09:30:00Z",
            "measurements": {
                "temperature": 25.5,
                "humidity": 60.0,
                "pressure": 1013.25
            },
            "metadata": {"sensor": "SENSOR-01", "location": "Room A"}
        },
        {
            "series_id": "TEST001",
            "timestamp": "2024-01-15T10:00:00Z",
            "measurements": {
                "temperature": 26.0,
                "humidity": 58.0,
                "pressure": 1013.30
            },
            "metadata": {"sensor": "SENSOR-01", "location": "Room A"}
        }
    ]
    
    # Create test directory
    test_dir = tempfile.mkdtemp(prefix="variosync_ui_test_")
    print(f"\nTest directory: {test_dir}\n")
    
    # Test popular format conversions
    test_cases = [
        ("json", "csv", "CSV export"),
        ("json", "parquet", "Parquet export"),
        ("json", "jsonl", "JSONL export"),
        ("json", "xlsx", "Excel export"),
        ("json", "influxdb", "InfluxDB export"),
        ("json", "prometheus", "Prometheus export"),
        ("csv", "json", "JSON import"),
        ("json", "zip", "ZIP archive"),
        ("json", "gzip", "Gzip compression"),
    ]
    
    exporter = FileExporter()
    converter = FormatConverter()
    
    # Create initial JSON file
    json_file = os.path.join(test_dir, "data.json")
    with open(json_file, "w") as f:
        json.dump(sample_data, f, indent=2)
    
    print("Testing format conversions:\n")
    success = 0
    failed = 0
    
    for input_fmt, output_fmt, description in test_cases:
        try:
            input_file = json_file if input_fmt == "json" else None
            if input_file is None:
                # Create input in required format
                input_file = os.path.join(test_dir, f"data.{input_fmt}")
                exporter.export(sample_data, input_file, format=input_fmt)
            
            output_file = os.path.join(test_dir, f"data.{output_fmt}")
            
            # Handle compression formats
            kwargs = {}
            if output_fmt in ["gzip", "bzip2", "zstandard"]:
                kwargs["base_format"] = "json"
            
            result = converter.convert(
                input_file,
                output_file,
                input_format=input_fmt,
                output_format=output_fmt,
                **kwargs
            )
            
            if result and os.path.exists(output_file):
                size = os.path.getsize(output_file)
                print(f"  ✓ {description:25} ({input_fmt} -> {output_fmt}) - {size:6} bytes")
                success += 1
            else:
                print(f"  ✗ {description:25} ({input_fmt} -> {output_fmt}) - FAILED")
                failed += 1
        except Exception as e:
            print(f"  ✗ {description:25} ({input_fmt} -> {output_fmt}) - ERROR: {str(e)[:50]}")
            failed += 1
    
    # Test format list for UI
    print(f"\n{'=' * 60}")
    print("Format List for UI Export Dialog")
    print("=" * 60)
    all_formats = exporter.get_supported_formats()
    print(f"\nTotal formats available: {len(all_formats)}")
    print(f"\nFormats: {', '.join(sorted(all_formats))}")
    
    print(f"\n{'=' * 60}")
    print("Summary")
    print("=" * 60)
    print(f"Successful: {success}")
    print(f"Failed: {failed}")
    print(f"Total formats: {len(all_formats)}")
    print(f"\nTest files: {test_dir}")

if __name__ == "__main__":
    test_format_conversion_ui()
