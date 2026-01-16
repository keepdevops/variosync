# VARIOSYNC

VARIOSYNC is a scalable time-series data processing system designed for cloud-native SaaS deployment with Supabase, Docker, and modern authentication.

## Features

- **Flexible Data Models**: Supports both financial (OHLCV) and generic time-series data
- **Multiple Storage Backends**: Local filesystem, S3, Wasabi, and Supabase Storage
- **API Integration**: Generic API downloader for various data sources
- **Authentication & Payment**: Supabase-based authentication with hour-based payment system
- **Scalable Architecture**: Modular design with files under 200 LOC each
- **Comprehensive Logging**: Centralized logging with file and console output
- **Configuration Validation**: JSON schema-based configuration validation

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables (optional):
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_BUCKET_NAME="your-bucket-name"
```

3. Create a configuration file (see `config.example.json`)

## Usage

### Basic Usage

Process a data file:
```bash
python main.py --process-file data.json --record-type time_series
```

With authentication:
```bash
python main.py --process-file data.json --license-key "your-license-key" --required-hours 0.1
```

### Programmatic Usage

```python
from main import VariosyncApp

# Initialize application
app = VariosyncApp("config.json")

# Authenticate user
user_id = app.authenticate_user("license-key", required_hours=0.1)

# Process data file
app.process_data_file("data.json", record_type="time_series")
```

## Architecture

The application is organized into logical modules:

- **logger.py**: Centralized logging configuration
- **config.py**: Configuration loading and validation
- **storage.py**: Storage backend abstraction (local, S3, Wasabi)
- **supabase_client.py**: Supabase database and storage integration
- **auth.py**: Authentication and payment validation
- **data_processor.py**: Time-series data processing and transformation
- **api_downloader.py**: Generic API downloader with rate limiting
- **main.py**: Application entry point and orchestration

## Configuration

See `variosync.json` for the complete JSON schema. A minimal configuration:

```json
{
  "Data": {
    "storage_backend": "local",
    "csv_dir": "data"
  },
  "Logging": {
    "level": "INFO",
    "file": "variosync.log"
  },
  "Supabase": {
    "url": "https://your-project.supabase.co",
    "key": "your-anon-key"
  },
  "Authentication": {
    "method": "supabase",
    "license_key_format": "uuid",
    "enforce_payment": true
  }
}
```

## License

Copyright (c) 2024 VARIOSYNC
# variosync
