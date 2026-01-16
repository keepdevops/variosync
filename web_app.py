"""
VARIOSYNC FastAPI Web Application
REST API with Panel native FastAPI integration.
"""
import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from logger import get_logger
from supabase_client import SupabaseClientFactory
from web_routes import register_routes

logger = get_logger()

# Initialize FastAPI app
app = FastAPI(
    title="VARIOSYNC API",
    description="Time-Series Data Processing System",
    version="2.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:8080").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
register_routes(app)

# Panel Dashboard with native FastAPI integration
try:
    import panel as pn
    from panel.io.fastapi import add_application
    from panel_dashboard_fastapi import create_dashboard
    
    PANEL_AVAILABLE = True
    
    # Get Supabase client if available
    supabase_client = None
    try:
        supabase_client = SupabaseClientFactory.create_from_env()
        if not supabase_client:
            config_path = os.getenv("VARIOSYNC_CONFIG", "config.json")
            import json
            with open(config_path, "r") as f:
                config = json.load(f)
            supabase_client = SupabaseClientFactory.create_from_config(config)
    except Exception as e:
        logger.warning(f"Supabase not available: {e}")
    
    # Create dashboard function for Panel integration
    def get_dashboard():
        return create_dashboard(supabase_client)
    
    # Add Panel app at /dashboard route using native integration
    # In Panel 1.8.5, add_application is used as a decorator
    try:
        add_application('/dashboard', app=app, title="VARIOSYNC Dashboard")(get_dashboard)
        logger.info("Panel dashboard integrated at /dashboard using native FastAPI integration")
    except Exception as e:
        logger.error(f"Failed to integrate Panel dashboard: {e}")
        
except ImportError:
    PANEL_AVAILABLE = False
    logger.warning("Panel not available. Install with: pip install panel holoviews")
    
    @app.get("/dashboard")
    async def dashboard_placeholder():
        """Dashboard placeholder when Panel not available."""
        from fastapi.responses import HTMLResponse
        return HTMLResponse("""
        <html>
            <head><title>VARIOSYNC Dashboard</title></head>
            <body>
                <h1>VARIOSYNC Dashboard</h1>
                <p>Panel is not installed. Install with: <code>pip install panel holoviews</code></p>
                <p><a href="/docs">API Documentation</a></p>
            </body>
        </html>
        """)


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
