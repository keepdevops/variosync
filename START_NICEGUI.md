# Running VARIOSYNC NiceGUI Dashboard on Localhost

## Quick Start

### Run NiceGUI Application

The NiceGUI dashboard provides a modern web interface:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the NiceGUI application
python3 run_nicegui.py
```

Then access:
- **Dashboard**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

## Environment Variables

Set these for custom configuration:

```bash
export PORT=8000
export HOST=0.0.0.0  # or localhost for local-only access
export VARIOSYNC_CONFIG=config.json
```

## Features

The NiceGUI dashboard includes:

1. **File Upload & Processing**
   - Upload JSON, CSV, TXT, Parquet, Feather files
   - Select record type (time_series or financial)
   - Real-time processing status and results
   - Detailed processing feedback

2. **Time-Series Visualization**
   - Interactive plots (coming soon)
   - Refresh data functionality

3. **Storage Browser**
   - Browse processed files
   - View file metadata
   - Refresh storage view

4. **Hourly Aggregates**
   - View aggregated statistics
   - Collapsible detailed view

## Troubleshooting

**Port already in use:**
```bash
PORT=8080 python3 run_nicegui.py
```

**Access from different machine:**
```bash
HOST=0.0.0.0 PORT=8000 python3 run_nicegui.py
```

**Missing dependencies:**
```bash
pip install nicegui pandas pyarrow plotly
```

## Docker

Run with Docker:
```bash
docker-compose up
```

Or build and run:
```bash
docker build -t variosync .
docker run -p 8000:8000 variosync
```
