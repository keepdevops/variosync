#!/usr/bin/env python3
"""
Quick test to verify all formats are accessible through the application.
"""
import json
from file_exporter import FileExporter
from format_converter import FormatConverter

def test_all_formats():
    """Test that all formats are accessible."""
    print("=" * 60)
    print("Testing All Format Support")
    print("=" * 60)
    
    # Sample data
    sample_data = [
        {
            "series_id": "TEST",
            "timestamp": "2024-01-15T09:30:00Z",
            "measurements": {"value": 100.5, "count": 10}
        }
    ]
    
    exporter = FileExporter()
    all_formats = exporter.get_supported_formats()
    
    print(f"\nTotal formats supported: {len(all_formats)}")
    print(f"\nFormats: {', '.join(sorted(all_formats))}")
    
    # Test format info retrieval
    print("\n" + "=" * 60)
    print("Testing Format Info")
    print("=" * 60)
    
    test_formats = ["json", "csv", "parquet", "influxdb", "netcdf", "zip", "tar"]
    for fmt in test_formats:
        info = exporter.get_format_info(fmt)
        if info:
            print(f"✓ {fmt:15} -> {info['ext']:10} ({info['mime']})")
        else:
            print(f"✗ {fmt:15} -> Not found")
    
    # Test format detection
    print("\n" + "=" * 60)
    print("Testing Format Detection")
    print("=" * 60)
    
    test_files = [
        "data.json", "data.csv", "data.parquet", "data.jsonl",
        "data.lp", "data.tsdb", "data.prom", "data.pb",
        "data.gz", "data.bz2", "data.zst", "data.zip", "data.tar",
        "data.nc", "data.zarr", "data.fits", "data.tsfile", "data.td", "data.vm"
    ]
    
    for filename in test_files:
        detected = FormatConverter.detect_format_from_path(filename)
        status = "✓" if detected else "✗"
        print(f"{status} {filename:20} -> {detected or 'None':20}")
    
    # Test conversion support check
    print("\n" + "=" * 60)
    print("Testing Conversion Support")
    print("=" * 60)
    
    conversions = [
        ("json", "csv"),
        ("csv", "parquet"),
        ("json", "influxdb"),
        ("json", "netcdf"),
        ("csv", "zip"),
    ]
    
    for input_fmt, output_fmt in conversions:
        supported = FormatConverter.is_conversion_supported(input_fmt, output_fmt)
        status = "✓" if supported else "✗"
        print(f"{status} {input_fmt:10} -> {output_fmt:15} {'Supported' if supported else 'Not supported'}")
    
    print("\n" + "=" * 60)
    print("✓ All format tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_all_formats()
