#!/usr/bin/env python3
"""
VARIOSYNC Web Application Launcher
Runs FastAPI server with Panel dashboard integration.
"""
import os
import sys

import uvicorn

# Check if Panel is available
try:
    import panel as pn
    PANEL_AVAILABLE = True
except ImportError:
    PANEL_AVAILABLE = False
    print("Warning: Panel not installed. Dashboard will be limited.")
    print("Install with: pip install panel pandas")

from web_app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"""
    ╔═══════════════════════════════════════════════════════╗
    ║          VARIOSYNC Web Application                    ║
    ║          FastAPI + Panel Integration                  ║
    ╚═══════════════════════════════════════════════════════╝
    
    🌐 API Server:     http://{host}:{port}
    📚 API Docs:       http://{host}:{port}/docs
    📊 Dashboard:      http://{host}:{port}/dashboard
    ❤️  Health Check:   http://{host}:{port}/health
    
    Press CTRL+C to stop
    """)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
