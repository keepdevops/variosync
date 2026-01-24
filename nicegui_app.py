"""
VARIOSYNC NiceGUI Web Application
Modern web UI for time-series data processing and visualization.
"""
import os
import json
import tempfile
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Optional

from nicegui import ui
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from logger import get_logger
from main import VariosyncApp
from data_cleaner import DataCleaner
from file_loader import FileLoader

logger = get_logger()

# Matplotlib support
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    from io import BytesIO
    import base64
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("Matplotlib not available. Install with: pip install matplotlib")

# =============================================================================
# FAVICON CONFIGURATION
# =============================================================================
# Add custom favicon
# Option 1: Use a local favicon file (place favicon.ico in static/ directory)
# Option 2: Use an inline SVG favicon (current implementation)
# Option 3: Use a URL to an external favicon

# Create static directory if it doesn't exist
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Always serve static files
from nicegui import app
app.add_static_files("/static", str(STATIC_DIR))

# Check if custom favicon file exists
FAVICON_PATH = STATIC_DIR / "favicon.ico"
FAVICON_SVG_PATH = STATIC_DIR / "favicon.svg"

if FAVICON_PATH.exists():
    ui.add_head_html(f'''
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    <link rel="shortcut icon" type="image/x-icon" href="/static/favicon.ico">
    ''', shared=True)
elif FAVICON_SVG_PATH.exists():
    ui.add_head_html(f'''
    <link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
    <link rel="shortcut icon" type="image/svg+xml" href="/static/favicon.svg">
    ''', shared=True)
else:
    # Use inline SVG favicon as fallback (sync icon matching navbar)
    FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#3b82f6"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>"""
    encoded_svg = urllib.parse.quote(FAVICON_SVG)
    ui.add_head_html(f'''
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,{encoded_svg}">
    <link rel="shortcut icon" type="image/svg+xml" href="data:image/svg+xml,{encoded_svg}">
    ''', shared=True)

# Initialize app instance lazily
app_instance = None

def get_app_instance():
    """Get or create app instance."""
    global app_instance
    if app_instance is None:
        app_instance = VariosyncApp()
    return app_instance


# =============================================================================
# DESIGN TOKENS
# =============================================================================
PRIMARY_COLOR = "#3b82f6"
PRIMARY_DARK = "#1e40af"
SUCCESS_COLOR = "#10b981"
WARNING_COLOR = "#f59e0b"
DANGER_COLOR = "#ef4444"


# =============================================================================
# NAVBAR
# =============================================================================
# Import from nicegui_app.navbar module
from nicegui_app.navbar import create_navbar


# =============================================================================
# DASHBOARD PAGE
# =============================================================================
# Import visualization functions from nicegui_app.visualization
from nicegui_app.visualization import (
    load_timeseries_data,
    get_available_series,
    is_financial_data,
    get_available_metrics,
    extract_ohlcv_data,
    create_matplotlib_financial_plot,
    create_matplotlib_plot,
    matplotlib_figure_to_base64,
    create_financial_plot,
    create_plot,
)

# Import additional visualization libraries
# Import availability flags and wrapper functions
try:
    from nicegui_app import (
        ALTAIR_AVAILABLE,
        HIGHCHARTS_AVAILABLE,
        ECHARTS_AVAILABLE,
    )
    # Try to import wrapper functions - they may not exist if libraries aren't available
    try:
        from nicegui_app import create_altair_plot_wrapper, altair_chart_to_html
    except (ImportError, AttributeError):
        create_altair_plot_wrapper = None
        altair_chart_to_html = None
    
    try:
        from nicegui_app import create_highcharts_plot_wrapper, highcharts_config_to_html
    except (ImportError, AttributeError):
        create_highcharts_plot_wrapper = None
        highcharts_config_to_html = None
    
    try:
        from nicegui_app import create_echarts_plot_wrapper, echarts_config_to_html
    except (ImportError, AttributeError):
        create_echarts_plot_wrapper = None
        echarts_config_to_html = None
except ImportError:
    ALTAIR_AVAILABLE = False
    HIGHCHARTS_AVAILABLE = False
    ECHARTS_AVAILABLE = False
    create_altair_plot_wrapper = None
    altair_chart_to_html = None
    create_highcharts_plot_wrapper = None
    highcharts_config_to_html = None
    create_echarts_plot_wrapper = None
    echarts_config_to_html = None
# Import state management
from nicegui_app.state import get_state

# Helper function to render HTML with scripts (used by card modules)
def render_html_with_scripts(html_content: str, container_id: str = None):
    """Render HTML content that may contain script tags.
    Separates scripts and uses ui.add_body_html() for scripts, ui.html() for content.
    """
    import re
    
    script_pattern = r'<script[^>]*>.*?</script>'
    
    # Extract script tags
    scripts = re.findall(script_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    # Remove script tags from HTML content
    html_without_scripts = re.sub(script_pattern, '', html_content, flags=re.DOTALL | re.IGNORECASE).strip()
    
    # If no scripts found, just return the HTML container
    if not scripts:
        return ui.html(html_without_scripts, sanitize=False)
    
    # Create container for HTML (without scripts)
    container = ui.html(html_without_scripts, sanitize=False).classes("w-full").style("height: 600px;")
    
    # Add scripts to body using ui.add_body_html()
    for script in scripts:
        ui.add_body_html(script)
    
    return container

@ui.page("/", title="VARIOSYNC Dashboard")
def dashboard_page(client):
    """Main dashboard page - clean entry point."""
    from nicegui_app.navbar import create_navbar
    from nicegui_app.panel_styles import inject_panel_styles
    from nicegui_app.panel_interactions import inject_panel_interactions
    from nicegui_app.dashboard_layout import setup_dashboard_page, create_dashboard_layout
    from nicegui_app.cards import (
        create_live_sync_metrics_card,
        create_upload_card,
        create_storage_card,
    )
    
    # Setup dashboard page (styling, meta tags, etc.)
    setup_dashboard_page(client)
    
    # Inject panel styles (flexbox CSS)
    inject_panel_styles()
    
    # Inject panel interactions (JavaScript for drag/resize)
    inject_panel_interactions()
    
    # Create dashboard layout (flexbox container)
    main_container, panels_grid = create_dashboard_layout()
    
    # Prepare card initializers for navbar
    refresh_callbacks = {}
    
    def init_plot_card():
        """Initialize Live Sync Metrics card."""
        create_live_sync_metrics_card(panels_grid)
    
    def init_upload_card():
        """Initialize Upload card with refresh callbacks."""
        create_upload_card(panels_grid, refresh_callbacks)
    
    def init_storage_card():
        """Initialize Storage card."""
        create_storage_card(panels_grid)
        # Register storage refresh callback
        refresh_callbacks['storage'] = lambda: None  # Will be set by storage card
    
    card_initializers = {
        'plot': init_plot_card,
        'upload': init_upload_card,
        'storage': init_storage_card,
    }
    
    # Setup navbar with card initializers
    create_navbar(panels_grid=panels_grid, card_initializers=card_initializers)
    
    # Cards are now initialized from navbar buttons
    # No cards are created by default - user clicks navbar buttons to initialize them


# =============================================================================
