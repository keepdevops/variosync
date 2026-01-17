"""
VARIOSYNC NiceGUI Web Application
Modern web UI for time-series data processing and visualization.
"""
import os
import urllib.parse
from pathlib import Path

from nicegui import ui, app
from logger import get_logger
from main import VariosyncApp

logger = get_logger()

# Matplotlib support
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    from io import BytesIO
    import base64
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("Matplotlib not available. Install with: pip install matplotlib")

# Favicon configuration
STATIC_DIR = Path(__file__).parent.parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

FAVICON_PATH = STATIC_DIR / "favicon.ico"
FAVICON_SVG_PATH = STATIC_DIR / "favicon.svg"

if FAVICON_PATH.exists():
    app.add_static_files("/static", str(STATIC_DIR))
    ui.add_head_html(f'''
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    <link rel="shortcut icon" type="image/x-icon" href="/static/favicon.ico">
    ''', shared=True)
elif FAVICON_SVG_PATH.exists():
    app.add_static_files("/static", str(STATIC_DIR))
    ui.add_head_html(f'''
    <link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
    <link rel="shortcut icon" type="image/svg+xml" href="/static/favicon.svg">
    ''', shared=True)
else:
    FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#3b82f6"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>"""
    encoded_svg = urllib.parse.quote(FAVICON_SVG)
    ui.add_head_html(f'''
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,{encoded_svg}">
    <link rel="shortcut icon" type="image/svg+xml" href="data:image/svg+xml,{encoded_svg}">
    ''', shared=True)

# Design tokens
PRIMARY_COLOR = "#3b82f6"
PRIMARY_DARK = "#1e40af"
SUCCESS_COLOR = "#10b981"
WARNING_COLOR = "#f59e0b"
DANGER_COLOR = "#ef4444"

# Initialize app instance lazily
app_instance = None

def get_app_instance():
    """Get or create app instance."""
    global app_instance
    if app_instance is None:
        app_instance = VariosyncApp()
    return app_instance

# Import and register components
from .navbar import create_navbar
# from .dashboard import dashboard_page  # TODO: Extract dashboard_page to dashboard.py
from .health import health_check
from .state import get_state, UIState
from .visualization import (
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

__all__ = [
    'create_navbar',
    # 'dashboard_page',  # TODO: Uncomment when dashboard.py is created
    'health_check',
    'get_app_instance',
    'get_state',
    'UIState',
    'MATPLOTLIB_AVAILABLE',
    'load_timeseries_data',
    'get_available_series',
    'is_financial_data',
    'get_available_metrics',
    'extract_ohlcv_data',
    'create_matplotlib_financial_plot',
    'create_matplotlib_plot',
    'matplotlib_figure_to_base64',
    'create_financial_plot',
    'create_plot',
]
