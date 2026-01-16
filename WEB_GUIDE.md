# VARIOSYNC Web Application Guide

## FastAPI + Panel Integration

VARIOSYNC now includes a full web application with REST API and interactive dashboard.

## Quick Start

### 1. Install Web Dependencies

```bash
pip install fastapi uvicorn python-multipart
pip install panel pandas  # For dashboard
```

Or install all dependencies:
```bash
pip install -r requirements.txt
pip install panel pandas plotly  # Optional: for advanced visualizations
```

### 2. Run the Web Application

```bash
python run_web.py
```

Or with custom port:
```bash
PORT=8080 python run_web.py
```

### 3. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Interactive Dashboard**: http://localhost:8000/dashboard
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Authentication
```bash
POST /api/auth
{
  "license_key": "your-uuid-key",
  "required_hours": 0.1
}
```

### Process Records
```bash
POST /api/process
{
  "records": [...],
  "record_type": "time_series"
}
```

### Upload File
```bash
POST /api/upload
Content-Type: multipart/form-data
- file: (file)
- record_type: "time_series"
- file_format: "csv" (optional)
```

### Download from API
```bash
POST /api/download
{
  "api_config": {
    "name": "Alpha Vantage",
    "base_url": "https://www.alphavantage.co/query",
    "endpoint": "",
    "api_key": "YOUR_KEY"
  },
  "entity_id": "AAPL",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

### List Storage
```bash
GET /api/storage/list?prefix=data/
```

## Panel Dashboard Features

The interactive dashboard includes:

1. **File Upload & Processing**
   - Upload JSON, CSV, TXT, Parquet, Feather files
   - Select record type (time_series or financial)
   - Auto-detect or specify file format
   - Real-time status updates

2. **API Download**
   - Configure API endpoints
   - Download data from external APIs
   - Support for multiple API formats

3. **Storage Browser**
   - Browse processed files
   - Filter by prefix
   - View file metadata

## Standalone Panel Dashboard

Run Panel dashboard separately:

```bash
python panel_dashboard.py
```

This opens a standalone Panel server on port 5007.

## Configuration

Set environment variables:

```bash
export PORT=8000
export HOST=0.0.0.0
export CORS_ORIGINS="http://localhost:8080,http://localhost:3000"
export VARIOSYNC_CONFIG="config.json"
```

## Development

### Run with Auto-reload

```bash
uvicorn web_app:app --reload --host 0.0.0.0 --port 8000
```

### Run Panel Dashboard Only

```python
from panel_dashboard import create_dashboard

dashboard = create_dashboard()
dashboard.serve(port=5007)
```

## Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install panel pandas

COPY . .

EXPOSE 8000
CMD ["python", "run_web.py"]
```

## Production Deployment

For production, use a production ASGI server:

```bash
gunicorn web_app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Or with uvicorn:
```bash
uvicorn web_app:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Client Examples

### Python
```python
import requests

# Upload file
with open("data.json", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/upload",
        files={"file": f},
        data={"record_type": "time_series"}
    )
print(response.json())
```

### cURL
```bash
# Upload file
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@data.json" \
  -F "record_type=time_series"

# Process records
curl -X POST "http://localhost:8000/api/process" \
  -H "Content-Type: application/json" \
  -d '{
    "records": [{"series_id": "AAPL", "timestamp": "2024-01-15T09:30:00", "measurements": {"close": 185.85}}],
    "record_type": "time_series"
  }'
```

## Troubleshooting

**Panel not showing:**
- Install Panel: `pip install panel pandas`
- Check browser console for errors

**CORS errors:**
- Set `CORS_ORIGINS` environment variable
- Or modify `web_app.py` CORS settings

**File upload fails:**
- Check file size limits
- Verify file format is supported
- Check server logs
