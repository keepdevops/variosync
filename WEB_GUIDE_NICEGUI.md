# VARIOSYNC Web Application Guide - NiceGUI

VARIOSYNC now includes a full web application powered by NiceGUI with an interactive dashboard.

## Quick Start

### 1. Install Web Dependencies

```bash
pip install -r requirements.txt
```

The requirements include:
- `nicegui>=1.4.0` - Modern Python web UI framework
- `pandas>=2.0.0` - Data processing
- `pyarrow>=12.0.0` - File format support
- `plotly>=5.17.0` - Visualizations

### 2. Run the Web Application

```bash
python3 run_nicegui.py
```

Or with custom port:
```bash
PORT=8080 python3 run_nicegui.py
```

### 3. Access the Application

- **Dashboard**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

## Dashboard Features

The interactive NiceGUI dashboard includes:

1. **File Upload & Processing**
   - Upload JSON, CSV, TXT, Parquet, Feather files
   - Select record type (time_series or financial)
   - Auto-detect file format
   - Real-time status updates and detailed results
   - Shows number of records processed
   - Lists saved record keys

2. **Time-Series Visualization**
   - Interactive plots (Plotly integration)
   - Refresh data functionality
   - Live sync metrics display

3. **Storage Browser**
   - Browse processed files
   - View file metadata (key, size, type)
   - Filter and search capabilities
   - Refresh storage view

4. **Hourly Aggregates**
   - View aggregated statistics by hour
   - Records count per hour
   - Series count per hour
   - Collapsible detailed view

## API Endpoints

NiceGUI uses FastAPI under the hood, so you can also access:

### Health Check
```bash
GET /health
```

Returns:
```json
{
  "status": "healthy",
  "storage": true,
  "auth": true
}
```

## Architecture

- **Frontend**: NiceGUI (Vue.js + Quasar components)
- **Backend**: FastAPI (used by NiceGUI internally)
- **Data Processing**: VariosyncApp (main.py)
- **Storage**: Supports Local, S3, Wasabi, Supabase Storage

## Development

### File Structure
- `nicegui_app.py` - Main NiceGUI application and UI
- `run_nicegui.py` - Application launcher
- `main.py` - Core VariosyncApp logic
- `requirements.txt` - Python dependencies

### Adding New Features

To add new features to the dashboard:

1. Edit `nicegui_app.py` to add UI components
2. Use NiceGUI components: `ui.button()`, `ui.card()`, `ui.table()`, etc.
3. Connect to `VariosyncApp` via `get_app_instance()`
4. Restart the server to see changes

## Docker Deployment

### Build and Run
```bash
docker build -t variosync .
docker run -p 8000:8000 variosync
```

### Docker Compose
```bash
docker-compose up
```

The Dockerfile includes:
- Python 3.12
- All dependencies from requirements.txt
- NiceGUI and visualization libraries
- Health check endpoint
- Runs `run_nicegui.py` on startup

## Troubleshooting

**Dashboard not loading:**
- Check that port 8000 is available
- Verify dependencies are installed: `pip install -r requirements.txt`
- Check logs for errors

**File upload not working:**
- Ensure file format is supported (JSON, CSV, TXT, Parquet, Feather)
- Check that storage backend is configured correctly
- Verify file permissions

**Health check failing:**
- Ensure the server is running
- Check that storage backend is accessible
- Verify configuration file exists

## Migration from Panel

If you were using the old Panel dashboard:
- The new NiceGUI dashboard provides similar functionality
- File upload and processing workflow is improved
- UI is more modern and responsive
- See `START_NICEGUI.md` for migration guide
