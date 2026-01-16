# Running VARIOSYNC Panel Dashboard on Localhost

## Quick Start

### Option 1: Run Web Application (Recommended)

The Panel dashboard is integrated with FastAPI and accessible at `/dashboard`:

```bash
# Install dependencies
pip install fastapi uvicorn panel[fastapi] holoviews pandas bokeh

# Run the web application
python3 run_web.py
```

Then access:
- **Dashboard**: http://localhost:8000/dashboard
- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

### Option 2: Standalone Panel Dashboard

Run Panel dashboard separately:

```bash
# Install Panel
pip install panel pandas holoviews bokeh

# Run standalone dashboard
python3 panel_dashboard.py
```

This opens Panel server on **http://localhost:5007**

### Option 3: Direct FastAPI with Panel

```bash
# Run FastAPI app directly
python3 web_app.py
```

Access dashboard at: **http://localhost:8000/dashboard**

## Environment Variables

Set these for custom configuration:

```bash
export PORT=8000
export HOST=0.0.0.0  # or localhost for local-only access
export CORS_ORIGINS=http://localhost:8080,http://localhost:3000
export VARIOSYNC_CONFIG=config.json
```

## Troubleshooting

**Panel not found:**
```bash
pip install panel[fastapi] holoviews pandas bokeh
```

**Port already in use:**
```bash
PORT=8080 python3 run_web.py
```

**Access from different machine:**
```bash
HOST=0.0.0.0 PORT=8000 python3 run_web.py
```
