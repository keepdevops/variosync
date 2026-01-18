"""
Example: Converting between file formats using FormatConverter.

This demonstrates how to convert time-series data between different formats.
"""
from format_converter import FormatConverter


def example_basic_conversion():
    """Basic conversion example."""
    print("Example 1: Basic CSV to Parquet conversion")
    success = FormatConverter.convert(
        input_path="data.csv",
        output_path="data.parquet"
    )
    print(f"Conversion successful: {success}\n")


def example_with_formats():
    """Conversion with explicit format specification."""
    print("Example 2: Explicit format specification")
    success = FormatConverter.convert(
        input_path="data.json",
        output_path="data.avro",
        input_format="json",
        output_format="avro"
    )
    print(f"Conversion successful: {success}\n")


def example_compression():
    """Convert to compressed format."""
    print("Example 3: Convert to compressed format")
    success = FormatConverter.convert(
        input_path="data.csv",
        output_path="data.csv.gz",
        output_format="gzip",
        base_format="csv"  # Compression formats need base_format
    )
    print(f"Conversion successful: {success}\n")


def example_tsdb_formats():
    """Convert to time-series database formats."""
    print("Example 4: Convert to InfluxDB Line Protocol")
    success = FormatConverter.convert(
        input_path="data.json",
        output_path="data.lp",
        output_format="influxdb"
    )
    print(f"Conversion successful: {success}\n")


def example_list_formats():
    """List all supported formats."""
    print("Example 5: List supported formats")
    formats = FormatConverter.get_supported_formats()
    for category, format_list in formats.items():
        print(f"{category}: {', '.join(format_list)}")
    print()


def example_check_support():
    """Check if conversion is supported."""
    print("Example 6: Check conversion support")
    supported = FormatConverter.is_conversion_supported("csv", "parquet")
    print(f"CSV -> Parquet supported: {supported}")
    
    supported = FormatConverter.is_conversion_supported("json", "netcdf")
    print(f"JSON -> NetCDF supported: {supported}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Format Conversion Examples")
    print("=" * 60)
    print()
    
    # Note: These examples show the API usage
    # Actual file conversion requires existing input files
    example_list_formats()
    example_check_support()
    
    print("To perform actual conversions:")
    print("  FormatConverter.convert('input.csv', 'output.parquet')")
    print("  FormatConverter.convert('data.json', 'data.gz', output_format='gzip', base_format='json')")
