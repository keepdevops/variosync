#!/usr/bin/env python3
"""
Test script for Stooq format support.
"""
import tempfile
import os
from file_loader import FileLoader
from file_exporter import FileExporter

# Sample Stooq format data
stooq_data = """TICKER,PER,DATE,TIME,OPEN,HIGH,LOW,CLOSE,VOL,OPENINT
AAPL.US,D,20240115,000000,185.50,186.20,185.10,185.85,12345678,0
AAPL.US,D,20240116,000000,186.00,186.50,185.80,186.30,14567890,0
GOOGL.US,D,20240115,000000,142.50,143.20,142.30,142.95,9876543,0
GOOGL.US,D,20240116,000000,143.00,143.80,142.90,143.50,11234567,0"""

def test_stooq_loader():
    """Test loading Stooq format."""
    print("Testing Stooq format loader...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(stooq_data)
        temp_path = f.name
    
    try:
        # Load using FileLoader with stooq format
        loader = FileLoader()
        records = loader.load(temp_path, file_format="stooq")
        
        print(f"✅ Loaded {len(records)} records")
        
        if records:
            print(f"✅ First record: series_id={records[0].get('series_id')}, timestamp={records[0].get('timestamp')}")
            print(f"✅ Measurements: {records[0].get('measurements', {})}")
            return True
        else:
            print("❌ No records loaded")
            return False
            
    except Exception as e:
        print(f"❌ Error loading Stooq format: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.unlink(temp_path)

def test_stooq_exporter():
    """Test exporting to Stooq format."""
    print("\nTesting Stooq format exporter...")
    
    # Sample time-series data
    test_data = [
        {
            "series_id": "AAPL.US",
            "timestamp": "2024-01-15T00:00:00",
            "measurements": {
                "open": 185.50,
                "high": 186.20,
                "low": 185.10,
                "close": 185.85,
                "vol": 12345678,
                "openint": 0,
                "period": "D"
            },
            "metadata": {
                "format": "stooq",
                "ticker": "AAPL.US",
                "period": "D"
            }
        },
        {
            "series_id": "AAPL.US",
            "timestamp": "2024-01-16T00:00:00",
            "measurements": {
                "open": 186.00,
                "high": 186.50,
                "low": 185.80,
                "close": 186.30,
                "vol": 14567890,
                "openint": 0,
                "period": "D"
            },
            "metadata": {
                "format": "stooq",
                "ticker": "AAPL.US",
                "period": "D"
            }
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_path = f.name
    
    try:
        # Export using FileExporter
        exporter = FileExporter()
        success = exporter.export(test_data, temp_path, format="stooq")
        
        if success:
            print(f"✅ Exported to Stooq format: {temp_path}")
            
            # Read back and verify
            with open(temp_path, 'r') as f:
                content = f.read()
                print(f"✅ File content (first 200 chars):\n{content[:200]}")
            
            # Verify it can be loaded back
            loader = FileLoader()
            loaded = loader.load(temp_path, file_format="stooq")
            print(f"✅ Loaded back {len(loaded)} records")
            
            return True
        else:
            print("❌ Export failed")
            return False
            
    except Exception as e:
        print(f"❌ Error exporting Stooq format: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == "__main__":
    print("=" * 60)
    print("Stooq Format Support Test")
    print("=" * 60)
    
    loader_ok = test_stooq_loader()
    exporter_ok = test_stooq_exporter()
    
    print("\n" + "=" * 60)
    if loader_ok and exporter_ok:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("=" * 60)
