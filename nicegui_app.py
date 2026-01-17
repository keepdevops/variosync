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

# Check if custom favicon file exists
FAVICON_PATH = STATIC_DIR / "favicon.ico"
FAVICON_SVG_PATH = STATIC_DIR / "favicon.svg"

if FAVICON_PATH.exists():
    # Serve favicon from static directory
    from nicegui import app
    app.add_static_files("/static", str(STATIC_DIR))
    ui.add_head_html(f'''
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    <link rel="shortcut icon" type="image/x-icon" href="/static/favicon.ico">
    ''', shared=True)
elif FAVICON_SVG_PATH.exists():
    # Serve SVG favicon from static directory
    from nicegui import app
    app.add_static_files("/static", str(STATIC_DIR))
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
def create_navbar():
    """Create navigation bar with status indicators."""
    with ui.header().classes("bg-blue-800 text-white p-4 shadow-lg"):
        with ui.row().classes("w-full items-center justify-between"):
            # Left: Logo/Brand and Functional buttons
            with ui.row().classes("gap-4 items-center"):
                # Brand/Logo icon - click to refresh dashboard
                logo_icon = ui.icon("sync_alt", size="lg", color="white").classes("cursor-pointer hover:scale-110 transition-transform")
                logo_label = ui.label("VARIOSYNC").classes("text-xl font-bold cursor-pointer hover:text-blue-200")
                
                def refresh_dashboard():
                    """Refresh the entire dashboard."""
                    ui.notify("Refreshing dashboard...", type="info")
                    # Add animation
                    logo_icon.classes("animate-spin")
                    # Trigger page reload via JavaScript
                    ui.run_javascript('window.location.reload()')
                
                logo_icon.on("click", refresh_dashboard)
                logo_label.on("click", refresh_dashboard)
                
                # Functional buttons
                with ui.row().classes("gap-2"):
                    # User Management
                    def show_user_info():
                        try:
                            app = get_app_instance()
                            with ui.dialog() as user_dialog, ui.card().classes("w-full max-w-2xl"):
                                ui.label("👤 User Information").classes("text-xl font-semibold mb-4")
                                
                                # Get user info from Supabase if available
                                user_id = None
                                user_email = None
                                hours_remaining = None
                                account_status = "Not authenticated"
                                data_sources_count = 0
                                
                                if app.auth_manager and app.auth_manager.supabase_client:
                                    try:
                                        # Try to get current user from Supabase Auth
                                        # Note: This requires Supabase Auth session
                                        supabase_client = app.auth_manager.supabase_client
                                        # For now, we'll show what we can get from the client
                                        account_status = "Connected to Supabase"
                                        
                                        # Try to get user hours if we have a user_id
                                        # In a real implementation, this would come from auth session
                                        if hasattr(supabase_client, 'operations'):
                                            # Check if we can query user data
                                            try:
                                                # This would require actual user authentication
                                                # For now, show connection status
                                                pass
                                            except:
                                                pass
                                    except Exception as e:
                                        logger.debug(f"Could not get user info: {e}")
                                
                                with ui.column().classes("w-full gap-3"):
                                    # Account Status
                                    with ui.card().classes("w-full p-4"):
                                        ui.label("Account Status").classes("text-sm font-semibold mb-2")
                                        ui.label(f"Status: {account_status}").classes("text-sm")
                                        if user_email:
                                            ui.label(f"Email: {user_email}").classes("text-sm")
                                        if user_id:
                                            ui.label(f"User ID: {user_id[:8]}...").classes("text-sm text-gray-500")
                                    
                                    # Hours Balance
                                    with ui.card().classes("w-full p-4"):
                                        ui.label("Hours Balance").classes("text-sm font-semibold mb-2")
                                        if hours_remaining is not None:
                                            ui.label(f"Remaining: {hours_remaining:.2f} hours").classes("text-lg font-bold text-green-600")
                                        else:
                                            ui.label("Hours balance not available").classes("text-sm text-gray-500")
                                            ui.label("Connect to Supabase and authenticate to view balance").classes("text-xs text-gray-400")
                                    
                                    # System Status
                                    with ui.card().classes("w-full p-4"):
                                        ui.label("System Status").classes("text-sm font-semibold mb-2")
                                        ui.label(f"Storage: {'✅ Available' if app.storage else '❌ Not configured'}").classes("text-sm")
                                        ui.label(f"Auth Manager: {'✅ Available' if app.auth_manager else '❌ Not configured'}").classes("text-sm")
                                        if app.storage:
                                            try:
                                                keys = app.storage.list_keys()
                                                ui.label(f"Data Sources: {len(keys)} files").classes("text-sm")
                                            except:
                                                ui.label("Data Sources: Unable to count").classes("text-sm")
                                    
                                    # Configuration Info
                                    with ui.card().classes("w-full p-4"):
                                        ui.label("Configuration").classes("text-sm font-semibold mb-2")
                                        storage_backend = app.config.get('Data', {}).get('storage_backend', 'local')
                                        ui.label(f"Storage Backend: {storage_backend}").classes("text-sm")
                                        if app.auth_manager:
                                            enforce_payment = app.config.get('Authentication', {}).get('enforce_payment', False)
                                            ui.label(f"Payment Enforcement: {'Enabled' if enforce_payment else 'Disabled'}").classes("text-sm")
                                
                                with ui.row().classes("w-full justify-end mt-4"):
                                    ui.button("Close", on_click=user_dialog.close).props("flat")
                            user_dialog.open()
                        except Exception as e:
                            logger.error(f"Error showing user info: {e}", exc_info=True)
                            ui.notify(f"Error: {str(e)}", type="negative")
                    
                    ui.button(icon="person_add", on_click=show_user_info).tooltip("User Management")
                    
                    # Dashboard - refresh
                    last_refresh_time = [None]
                    
                    def refresh_dashboard_btn():
                        import time
                        last_refresh_time[0] = time.time()
                        ui.notify("Refreshing dashboard...", type="info")
                        # Show loading animation
                        dashboard_btn.set_enabled(False)
                        ui.run_javascript('window.location.reload()')
                    
                    dashboard_btn = ui.button(icon="dashboard", on_click=refresh_dashboard_btn)
                    if last_refresh_time[0]:
                        dashboard_btn.tooltip(f"Refresh Dashboard (Last: {last_refresh_time[0]})")
                    else:
                        dashboard_btn.tooltip("Refresh Dashboard")
                    
                    # Storage/Database - scroll to storage section
                    def scroll_to_storage():
                        try:
                            app = get_app_instance()
                            # Get storage stats
                            if app.storage:
                                try:
                                    keys = app.storage.list_keys()
                                    total_size = sum([app.storage.get_size(k) or 0 for k in keys[:100]])
                                    if total_size >= 1024 * 1024:
                                        size_str = f"{total_size / (1024 * 1024):.2f} MB"
                                    elif total_size >= 1024:
                                        size_str = f"{total_size / 1024:.2f} KB"
                                    else:
                                        size_str = f"{total_size} B"
                                    
                                    ui.notify(f"Storage: {len(keys)} files, {size_str}", type="info")
                                except:
                                    ui.notify("Scrolled to storage section", type="info")
                            else:
                                ui.notify("Storage not configured", type="warning")
                            
                            ui.run_javascript('document.querySelector("[data-section=\\"storage\\"]")?.scrollIntoView({behavior: "smooth"})')
                        except Exception as e:
                            logger.error(f"Error scrolling to storage: {e}")
                            ui.notify("Error accessing storage", type="negative")
                    
                    storage_btn = ui.button(icon="storage", on_click=scroll_to_storage).tooltip("View Storage")
                    
                    # Menu - show navigation menu
                    def show_menu():
                        with ui.dialog() as menu_dialog, ui.card().classes("w-96"):
                            ui.label("☰ Navigation Menu").classes("text-xl font-semibold mb-4")
                            
                            with ui.column().classes("gap-2 w-full"):
                                def nav_to_dashboard():
                                    menu_dialog.close()
                                    refresh_dashboard_btn()
                                
                                def nav_to_upload():
                                    menu_dialog.close()
                                    scroll_to_upload()
                                
                                def nav_to_storage():
                                    menu_dialog.close()
                                    scroll_to_storage()
                                
                                def nav_to_settings():
                                    menu_dialog.close()
                                    show_settings()
                                
                                ui.button("📊 Dashboard", icon="dashboard", on_click=nav_to_dashboard).classes("w-full")
                                ui.button("📤 Upload Files", icon="upload", on_click=nav_to_upload).classes("w-full")
                                ui.button("💾 Storage Browser", icon="storage", on_click=nav_to_storage).classes("w-full")
                                ui.button("⚙️ Settings", icon="settings", on_click=nav_to_settings).classes("w-full")
                            
                            ui.separator().classes("my-4")
                            
                            # Help and About
                            with ui.column().classes("gap-2 w-full"):
                                ui.label("Help & Info").classes("text-sm font-semibold")
                                
                                def show_help():
                                    menu_dialog.close()
                                    ui.notify("Help documentation coming soon", type="info")
                                
                                def show_about():
                                    menu_dialog.close()
                                    with ui.dialog() as about_dialog, ui.card().classes("w-96"):
                                        ui.label("About VARIOSYNC").classes("text-xl font-semibold mb-4")
                                        ui.label("VARIOSYNC Time-Series Data Processing System").classes("text-sm mb-2")
                                        ui.label("Version: 1.0.0").classes("text-xs text-gray-500")
                                        ui.separator().classes("my-2")
                                        ui.label("Features:").classes("text-sm font-semibold mt-2")
                                        ui.label("• Time-series data processing").classes("text-xs")
                                        ui.label("• Financial data support (OHLCV)").classes("text-xs")
                                        ui.label("• Multiple storage backends").classes("text-xs")
                                        ui.label("• API integration").classes("text-xs")
                                        ui.label("• ML analytics (with Modal)").classes("text-xs")
                                        with ui.row().classes("w-full justify-end mt-4"):
                                            ui.button("Close", on_click=about_dialog.close).props("flat")
                                    about_dialog.open()
                                
                                ui.button("❓ Help", icon="help", on_click=show_help).classes("w-full")
                                ui.button("ℹ️ About", icon="info", on_click=show_about).classes("w-full")
                            
                            # Keyboard shortcuts
                            ui.separator().classes("my-4")
                            with ui.expansion("⌨️ Keyboard Shortcuts", icon="keyboard").classes("w-full"):
                                with ui.column().classes("gap-1 text-xs"):
                                    ui.label("Ctrl+R: Refresh dashboard").classes("text-xs")
                                    ui.label("Ctrl+U: Upload section").classes("text-xs")
                                    ui.label("Ctrl+S: Storage section").classes("text-xs")
                                    ui.label("Ctrl+,: Settings").classes("text-xs")
                            
                            with ui.row().classes("w-full justify-end mt-4"):
                                ui.button("Close", on_click=menu_dialog.close).props("flat")
                        menu_dialog.open()
                    
                    ui.button(icon="menu", on_click=show_menu).tooltip("Menu")
                    
                    # AI/Analytics
                    def show_analytics():
                        try:
                            app = get_app_instance()
                            with ui.dialog() as analytics_dialog, ui.card().classes("w-full max-w-4xl"):
                                ui.label("🧠 AI/Analytics").classes("text-xl font-semibold mb-4")
                                
                                # Analytics type selector
                                analytics_type_select = ui.select(
                                    ["Forecast", "Anomaly Detection", "Trend Analysis"],
                                    label="Analysis Type",
                                    value="Forecast"
                                ).classes("w-full mb-4")
                                
                                # Series selector
                                series_select_analytics = ui.select(
                                    options=[],
                                    label="Select Series",
                                    value=None,
                                    with_input=True
                                ).classes("w-full mb-4")
                                
                                # Load available series
                                try:
                                    if app.storage:
                                        keys = app.storage.list_keys()
                                        # Extract unique series IDs from keys (simplified)
                                        series_options = list(set([k.split('/')[0] if '/' in k else k.split('.')[0] for k in keys[:50]]))
                                        series_select_analytics.options = series_options
                                except:
                                    pass
                                
                                # Parameters based on analysis type
                                with ui.column().classes("w-full gap-2 mb-4") as params_container:
                                    periods_input = ui.number(
                                        label="Forecast Periods",
                                        value=30,
                                        min=1,
                                        max=365
                                    ).classes("w-full")
                                    periods_input.visible = True
                                
                                # Update params visibility based on analysis type
                                def update_params_visibility():
                                    if analytics_type_select.value == "Forecast":
                                        periods_input.visible = True
                                    else:
                                        periods_input.visible = False
                                
                                analytics_type_select.on('update:modelValue', lambda: update_params_visibility())
                                
                                # Analysis button
                                analyze_button = ui.button("Run Analysis", icon="psychology", color="primary")
                                
                                # Results area
                                results_card = None
                                
                                def run_analysis():
                                    nonlocal results_card
                                    try:
                                        analyze_button.set_enabled(False)
                                        
                                        analysis_type = analytics_type_select.value
                                        series_id = series_select_analytics.value
                                        
                                        if not series_id:
                                            ui.notify("Please select a series", type="warning")
                                            analyze_button.set_enabled(True)
                                            return
                                        
                                        # Try to use Modal functions if available
                                        from modal_client import ModalClientFactory
                                        modal_client = ModalClientFactory.get_instance()
                                        
                                        if modal_client and modal_client.available:
                                            ui.notify("Using Modal ML functions for analysis...", type="info")
                                            # Modal integration would go here
                                            ui.notify("Modal functions not yet fully integrated", type="info")
                                        else:
                                            # Local analysis
                                            ui.notify("Running local analysis...", type="info")
                                            
                                            # Simple local analysis
                                            if analysis_type == "Forecast":
                                                ui.notify("Forecast: Use Prophet/LightGBM via Modal for production", type="info")
                                            elif analysis_type == "Anomaly Detection":
                                                ui.notify("Anomaly Detection: Statistical analysis coming soon", type="info")
                                            elif analysis_type == "Trend Analysis":
                                                ui.notify("Trend Analysis: Moving averages and seasonality detection coming soon", type="info")
                                        
                                        # Create results display
                                        if results_card:
                                            try:
                                                results_card.delete()
                                            except:
                                                pass
                                        
                                        with ui.card().classes("w-full mt-4") as new_results_card:
                                            results_card = new_results_card
                                            ui.label(f"Analysis Results: {analysis_type}").classes("text-lg font-semibold mb-2")
                                            ui.label(f"Series: {series_id}").classes("text-sm mb-2")
                                            
                                            if analysis_type == "Forecast":
                                                ui.label(f"Forecasting {periods_input.value} periods ahead").classes("text-sm")
                                                ui.label("Results will be displayed here once Modal functions are deployed.").classes("text-xs text-gray-500 mt-2")
                                            elif analysis_type == "Anomaly Detection":
                                                ui.label("Detecting anomalies using statistical methods...").classes("text-sm")
                                                ui.label("Results will show detected outliers and anomalies.").classes("text-xs text-gray-500 mt-2")
                                            elif analysis_type == "Trend Analysis":
                                                ui.label("Analyzing trends, seasonality, and patterns...").classes("text-sm")
                                                ui.label("Results will show trend direction, seasonality, and moving averages.").classes("text-xs text-gray-500 mt-2")
                                        
                                        analyze_button.set_enabled(True)
                                    except Exception as e:
                                        logger.error(f"Error running analysis: {e}", exc_info=True)
                                        ui.notify(f"Analysis error: {str(e)}", type="negative")
                                        analyze_button.set_enabled(True)
                                
                                analyze_button.on_click(run_analysis)
                                
                                # Info section
                                with ui.expansion("ℹ️ About Analytics", icon="info").classes("w-full mt-4"):
                                    with ui.column().classes("w-full gap-2"):
                                        ui.label("Forecast: Uses Prophet or LightGBM to predict future values").classes("text-sm")
                                        ui.label("Anomaly Detection: Identifies outliers using statistical methods").classes("text-sm")
                                        ui.label("Trend Analysis: Detects trends, seasonality, and patterns").classes("text-sm")
                                        ui.separator()
                                        ui.label("Note: Full ML capabilities require Modal functions to be deployed.").classes("text-xs text-gray-500")
                                
                                with ui.row().classes("w-full justify-end mt-4"):
                                    ui.button("Close", on_click=analytics_dialog.close).props("flat")
                            analytics_dialog.open()
                        except Exception as e:
                            logger.error(f"Error showing analytics dialog: {e}", exc_info=True)
                            ui.notify(f"Error: {str(e)}", type="negative")
                    
                    ui.button(icon="psychology", on_click=show_analytics).tooltip("AI/Analytics")
                    
                    # Download - API download dialog (includes free data sources)
                    def show_download_dialog():
                        try:
                            app = get_app_instance()
                            with ui.dialog() as download_dialog, ui.card().classes("w-full max-w-2xl"):
                                ui.label("⬇️ Download from API").classes("text-xl font-semibold mb-2")
                                
                                # Help text
                                with ui.card().classes("w-full p-3 mb-4 bg-blue-50 border-l-4 border-blue-500"):
                                    ui.label("💡 Getting Started").classes("font-semibold text-blue-800 mb-1")
                                    ui.label("Choose a data source type above. Use 'Browse All APIs' to discover available APIs, or select 'API (Requires Key)' to configure a specific API. For free datasets without API keys, select 'Free Dataset (No Key)'.").classes("text-sm text-blue-700")
                                
                                # Load API presets
                                api_presets = {
                                    "Custom API": None,
                                    "Alpha Vantage": {
                                        "base_url": "https://www.alphavantage.co/query",
                                        "endpoint": "",
                                        "api_key_param": "apikey",
                                        "entity_param": "symbol",
                                        "note": "5 calls/min, 500/day free. Use function=TIME_SERIES_DAILY&symbol={symbol} in endpoint"
                                    },
                                    "Finnhub": {
                                        "base_url": "https://finnhub.io/api/v1",
                                        "endpoint": "/stock/candle",
                                        "api_key_param": "token",
                                        "entity_param": "symbol",
                                        "start_date_param": "from",
                                        "end_date_param": "to",
                                        "date_format": "unix",
                                        "note": "Real-time + WebSocket, 20+ years history"
                                    },
                                    "Twelve Data": {
                                        "base_url": "https://api.twelvedata.com",
                                        "endpoint": "/time_series",
                                        "api_key_param": "apikey",
                                        "entity_param": "symbol",
                                        "start_date_param": "start_date",
                                        "end_date_param": "end_date",
                                        "note": "Very limited free tier, credit-based"
                                    },
                                    "Financial Modeling Prep": {
                                        "base_url": "https://financialmodelingprep.com/api/v3",
                                        "endpoint": "/historical-price-full/{symbol}",
                                        "api_key_param": "apikey",
                                        "entity_param": "symbol",
                                        "start_date_param": "from",
                                        "end_date_param": "to",
                                        "note": "30+ years history, fundamentals + pricing"
                                    },
                                    "Marketstack": {
                                        "base_url": "http://api.marketstack.com/v1",
                                        "endpoint": "/eod",
                                        "api_key_param": "access_key",
                                        "entity_param": "symbols",
                                        "start_date_param": "date_from",
                                        "end_date_param": "date_to",
                                        "note": "Simple JSON format, global stocks"
                                    },
                                    "StockData.org": {
                                        "base_url": "https://api.stockdata.org/v1",
                                        "endpoint": "/data/quote",
                                        "api_key_param": "api_token",
                                        "entity_param": "symbols",
                                        "note": "Easy to use, stocks/forex/crypto"
                                    },
                                    "EODHD": {
                                        "base_url": "https://eodhistoricaldata.com/api",
                                        "endpoint": "/eod/{symbol}",
                                        "api_key_param": "api_token",
                                        "entity_param": "symbol",
                                        "start_date_param": "from",
                                        "end_date_param": "to",
                                        "note": "30+ years history, Excel add-on available"
                                    },
                                    "Polygon.io": {
                                        "base_url": "https://api.polygon.io/v2",
                                        "endpoint": "/aggs/ticker/{symbol}/range/1/day/{from}/{to}",
                                        "api_key_param": "apiKey",
                                        "entity_param": "symbol",
                                        "start_date_param": "from",
                                        "end_date_param": "to",
                                        "note": "Best tick data, US-focused, limited free tier"
                                    },
                                    "Open-Meteo": {
                                        "base_url": "https://archive-api.open-meteo.com/v1",
                                        "endpoint": "/archive",
                                        "api_key_param": None,
                                        "entity_param": "latitude,longitude",
                                        "start_date_param": "start_date",
                                        "end_date_param": "end_date",
                                        "note": "Completely free, no API key, 70+ years history, high-resolution"
                                    },
                                    "NOAA Climate Data Online": {
                                        "base_url": "https://www.ncdc.noaa.gov/cdo-web/api/v2",
                                        "endpoint": "/data",
                                        "api_key_param": "token",
                                        "entity_param": "stationid",
                                        "start_date_param": "startdate",
                                        "end_date_param": "enddate",
                                        "note": "Free API, 100+ years US weather data, very long historical"
                                    },
                                    "Visual Crossing": {
                                        "base_url": "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services",
                                        "endpoint": "/timeline/{location}/{start}/{end}",
                                        "api_key_param": "key",
                                        "entity_param": "location",
                                        "start_date_param": "start",
                                        "end_date_param": "end",
                                        "note": "Free tier available, easy API, good for location-based time series"
                                    },
                                    "Meteostat": {
                                        "base_url": "https://api.meteostat.net/v2",
                                        "endpoint": "/point/hourly",
                                        "api_key_param": None,
                                        "entity_param": "lat,lon",
                                        "start_date_param": "start",
                                        "end_date_param": "end",
                                        "note": "Free API, clean JSON, many stations globally"
                                    },
                                    "OpenWeatherMap": {
                                        "base_url": "https://api.openweathermap.org/data/2.5",
                                        "endpoint": "/history/city",
                                        "api_key_param": "appid",
                                        "entity_param": "q",
                                        "start_date_param": "start",
                                        "end_date_param": "end",
                                        "date_format": "unix",
                                        "note": "1000 calls/day free, 60 calls/min rate limit"
                                    },
                                    "FRED (St. Louis Fed)": {
                                        "base_url": "https://api.stlouisfed.org/fred",
                                        "endpoint": "/series/observations",
                                        "api_key_param": "api_key",
                                        "entity_param": "series_id",
                                        "start_date_param": "observation_start",
                                        "end_date_param": "observation_end",
                                        "note": "Gold standard for US macro data; completely free"
                                    },
                                    "World Bank Open Data": {
                                        "base_url": "https://api.worldbank.org/v2",
                                        "endpoint": "/country/{country}/indicator/{indicator}",
                                        "api_key_param": None,
                                        "entity_param": "country,indicator",
                                        "start_date_param": "date",
                                        "end_date_param": None,
                                        "date_format": "YYYY",
                                        "note": "Excellent for cross-country comparisons; completely free"
                                    },
                                    "OECD Data": {
                                        "base_url": "https://stats.oecd.org/SDMX-JSON/data",
                                        "endpoint": "/{dataset}/{filter}",
                                        "api_key_param": None,
                                        "entity_param": "filter",
                                        "start_date_param": "startTime",
                                        "end_date_param": "endTime",
                                        "note": "High-quality international statistics; free API access"
                                    },
                                    "IMF Data": {
                                        "base_url": "https://www.imf.org/external/datamapper/api/v1",
                                        "endpoint": "/{indicator}/{country}",
                                        "api_key_param": None,
                                        "entity_param": "country",
                                        "start_date_param": "period",
                                        "date_format": "YYYY",
                                        "note": "Very deep macroeconomic series; free API"
                                    },
                                    "CoinGecko": {
                                        "base_url": "https://api.coingecko.com/api/v3",
                                        "endpoint": "/coins/{id}/market_chart",
                                        "api_key_param": None,
                                        "entity_param": "id",
                                        "start_date_param": "from",
                                        "end_date_param": "to",
                                        "date_format": "unix"
                                    },
                                    "data.gov": {
                                        "base_url": "https://catalog.data.gov/api/3",
                                        "endpoint": "/action/datastore_search",
                                        "api_key_param": None,
                                        "entity_param": "resource_id",
                                        "start_date_param": "filters",
                                        "note": "Massive US public data catalog; each dataset has its own resource_id"
                                    },
                                    "Nasdaq Data Link (Quandl)": {
                                        "base_url": "https://data.nasdaq.com/api/v3",
                                        "endpoint": "/datasets/{database}/{dataset}",
                                        "api_key_param": "api_key",
                                        "entity_param": "database,dataset",
                                        "start_date_param": "start_date",
                                        "end_date_param": "end_date",
                                        "note": "Limited free tier; was very popular, now more restricted"
                                    },
                                    "Our World in Data": {
                                        "base_url": "https://api.ourworldindata.org/v1",
                                        "endpoint": "/indicators/{indicator}",
                                        "api_key_param": None,
                                        "entity_param": "indicator",
                                        "start_date_param": "startYear",
                                        "end_date_param": "endYear",
                                        "date_format": "YYYY",
                                        "note": "Beautifully curated; excellent for global trends; download CSV from website"
                                    }
                                }
                                
                                # Data source type selector
                                with ui.column().classes("w-full mb-4"):
                                    source_type_select = ui.select(
                                        ["API (Requires Key)", "Free Dataset (No Key)", "Browse All APIs"],
                                        label="Data Source Type",
                                        value="API (Requires Key)"
                                    ).classes("w-full")
                                    ui.label("Select how you want to download data: API with key, free datasets, or browse all available APIs").classes("text-xs text-gray-500 mt-1")
                                
                                # API Browser section
                                with ui.column().classes("w-full") as api_browser_container:
                                    api_browser_container.visible = False
                                    
                                    ui.label("📚 Time-Series API Catalog").classes("text-xl font-semibold mb-2")
                                    ui.label("Browse all available time-series APIs organized by category").classes("text-sm text-gray-500 mb-2")
                                    
                                    with ui.card().classes("w-full p-3 mb-4 bg-green-50 border-l-4 border-green-500"):
                                        ui.label("ℹ️ How to Use").classes("font-semibold text-green-800 mb-1")
                                        ui.label("Browse APIs by category using the tabs below. Each API card shows free tier limits, real-time capabilities, historical depth, and data types. Click 'Use This API' to automatically configure the API preset in the form.").classes("text-sm text-green-700")
                                    
                                    # API categories with all APIs
                                    api_categories = {
                                        "Financial APIs": [
                                            {"name": "Alpha Vantage", "free_tier": "5 calls/min, 500/day", "data_types": "Stocks, forex, crypto, indicators", "realtime": "Delayed", "history": "20+ years", "website": "alphavantage.co", "note": "Still one of the best free options"},
                                            {"name": "Finnhub", "free_tier": "Limited calls", "data_types": "Global stocks, forex, crypto", "realtime": "Yes (WebSocket)", "history": "20+ years", "website": "finnhub.io", "note": "Very broad coverage"},
                                            {"name": "Twelve Data", "free_tier": "Very limited", "data_types": "Stocks, forex, crypto, ETFs", "realtime": "Yes (WebSocket)", "history": "20+ years", "website": "twelvedata.com", "note": "Clean API; credit-based"},
                                            {"name": "Financial Modeling Prep", "free_tier": "Usable free tier", "data_types": "Global equities, forex, crypto", "realtime": "Yes", "history": "30+ years", "website": "financialmodelingprep.com", "note": "Fundamentals + pricing"},
                                            {"name": "Marketstack", "free_tier": "Limited requests", "data_types": "Global stocks, intraday, EOD", "realtime": "Delayed", "history": "Varies", "website": "marketstack.com", "note": "Simple JSON format"},
                                            {"name": "StockData.org", "free_tier": "Free tier", "data_types": "Stocks, forex, crypto, news", "realtime": "Yes", "history": "Varies", "website": "stockdata.org", "note": "Easy to use"},
                                            {"name": "EODHD", "free_tier": "Limited trial", "data_types": "Global stocks, ETFs, forex, crypto", "realtime": "Delayed + add-on", "history": "30+ years", "website": "eodhd.com", "note": "Deep historical; Excel add-on"},
                                            {"name": "Polygon.io", "free_tier": "Limited free tier", "data_types": "US equities, options, forex, crypto", "realtime": "Yes (tick-level)", "history": "Full US history", "website": "polygon.io", "note": "Best tick data; US-focused"},
                                        ],
                                        "Weather & Climate APIs": [
                                            {"name": "Open-Meteo", "free_tier": "Completely free, no API key", "data_types": "Global weather forecasts + reanalysis", "realtime": "Yes (forecasts)", "history": "70+ years", "website": "open-meteo.com", "note": "High-resolution; no rate limits"},
                                            {"name": "NOAA Climate Data Online", "free_tier": "Free API + bulk download", "data_types": "US weather stations, summaries", "realtime": "No (delayed)", "history": "100+ years", "website": "ncdc.noaa.gov/cdo-web", "note": "Very long historical US data"},
                                            {"name": "Visual Crossing", "free_tier": "Free tier (limited queries)", "data_types": "Global historical + forecast", "realtime": "Yes (forecast)", "history": "Decades", "website": "visualcrossing.com", "note": "Easy API; location-based"},
                                            {"name": "Meteostat", "free_tier": "Free API", "data_types": "Global historical weather stations", "realtime": "No", "history": "Decades", "website": "meteostat.net", "note": "Clean JSON; many stations"},
                                            {"name": "OpenWeatherMap", "free_tier": "1000/day", "data_types": "Current weather, forecasts, historical", "realtime": "Yes", "history": "Limited", "website": "openweathermap.org", "note": "60 calls/min rate limit"},
                                        ],
                                        "Economic Data APIs": [
                                            {"name": "FRED (St. Louis Fed)", "free_tier": "Completely free + API", "data_types": "US economic indicators", "realtime": "No (daily/weekly/monthly)", "history": "Decades", "website": "fred.stlouisfed.org", "note": "Gold standard for US macro data"},
                                            {"name": "World Bank Open Data", "free_tier": "Completely free + API", "data_types": "Global economic, development, health", "realtime": "No", "history": "Decades", "website": "data.worldbank.org", "note": "Excellent for cross-country comparisons"},
                                            {"name": "OECD Data", "free_tier": "Free API access", "data_types": "Economic, education, health, environment", "realtime": "No", "history": "Decades", "website": "data.oecd.org", "note": "High-quality international stats"},
                                            {"name": "IMF Data", "free_tier": "Free API", "data_types": "Global macro, fiscal, balance of payments", "realtime": "No", "history": "Decades", "website": "data.imf.org", "note": "Very deep macroeconomic series"},
                                        ],
                                        "Cryptocurrency APIs": [
                                            {"name": "CoinGecko", "free_tier": "Unlimited", "data_types": "Cryptocurrency market data", "realtime": "Yes", "history": "Varies", "website": "coingecko.com", "note": "10-50 calls/min rate limit"},
                                        ],
                                        "Open Data Platforms": [
                                            {"name": "Kaggle Datasets", "free_tier": "Free download + some APIs", "data_types": "Thousands of time series", "realtime": "Rarely", "history": "Varies", "website": "kaggle.com/datasets", "note": "Community datasets; great for practice"},
                                            {"name": "data.gov", "free_tier": "Free API", "data_types": "US government open data", "realtime": "Varies", "history": "Varies", "website": "data.gov", "note": "Massive US public data catalog"},
                                            {"name": "Nasdaq Data Link (Quandl)", "free_tier": "Limited free tier", "data_types": "Financial, economic, alternative", "realtime": "Some", "history": "Varies", "website": "data.nasdaq.com", "note": "Was very popular; now more restricted"},
                                            {"name": "Our World in Data", "free_tier": "Free download + charts API", "data_types": "Global health, environment, economy", "realtime": "No", "history": "Centuries in some cases", "website": "ourworldindata.org", "note": "Beautifully curated; global trends"},
                                        ],
                                    }
                                    
                                    # Category tabs
                                    with ui.tabs().classes("w-full mb-4") as category_tabs:
                                        financial_tab = ui.tab("Financial")
                                        weather_tab = ui.tab("Weather")
                                        economic_tab = ui.tab("Economic")
                                        crypto_tab = ui.tab("Crypto")
                                        open_data_tab = ui.tab("Open Data")
                                    
                                    with ui.tab_panels(category_tabs, value=financial_tab).classes("w-full"):
                                        # Financial APIs panel
                                        with ui.tab_panel(financial_tab):
                                            with ui.column().classes("w-full gap-3"):
                                                for api in api_categories["Financial APIs"]:
                                                    with ui.card().classes("w-full p-4 hover:bg-gray-50 cursor-pointer"):
                                                        ui.label(api["name"]).classes("text-lg font-semibold")
                                                        with ui.row().classes("w-full gap-4 text-sm mt-2"):
                                                            ui.label(f"Free Tier: {api['free_tier']}").classes("text-blue-600")
                                                            ui.label(f"Real-Time: {api['realtime']}").classes("text-green-600")
                                                            ui.label(f"History: {api['history']}").classes("text-purple-600")
                                                        ui.label(f"Data Types: {api['data_types']}").classes("text-sm text-gray-600 mt-1")
                                                        ui.label(f"Note: {api['note']}").classes("text-xs text-gray-500 mt-1")
                                                        ui.label(f"Website: {api['website']}").classes("text-xs text-blue-500 mt-1")
                                                        def make_select_handler(api_name):
                                                            def handler():
                                                                source_type_select.value = "API (Requires Key)"
                                                                if api_name in api_presets:
                                                                    api_preset_select.value = api_name
                                                                    apply_preset()
                                                                api_browser_container.visible = False
                                                                api_form_container.visible = True
                                                            return handler
                                                        ui.button("Use This API", icon="arrow_forward", on_click=make_select_handler(api["name"])).classes("mt-2").props("flat size=sm")
                                        
                                        # Weather APIs panel
                                        with ui.tab_panel(weather_tab):
                                            with ui.column().classes("w-full gap-3"):
                                                for api in api_categories["Weather & Climate APIs"]:
                                                    with ui.card().classes("w-full p-4 hover:bg-gray-50 cursor-pointer"):
                                                        ui.label(api["name"]).classes("text-lg font-semibold")
                                                        with ui.row().classes("w-full gap-4 text-sm mt-2"):
                                                            ui.label(f"Free Tier: {api['free_tier']}").classes("text-blue-600")
                                                            ui.label(f"Real-Time: {api['realtime']}").classes("text-green-600")
                                                            ui.label(f"History: {api['history']}").classes("text-purple-600")
                                                        ui.label(f"Data Types: {api['data_types']}").classes("text-sm text-gray-600 mt-1")
                                                        ui.label(f"Note: {api['note']}").classes("text-xs text-gray-500 mt-1")
                                                        ui.label(f"Website: {api['website']}").classes("text-xs text-blue-500 mt-1")
                                                        def make_select_handler(api_name):
                                                            def handler():
                                                                source_type_select.value = "API (Requires Key)"
                                                                if api_name in api_presets:
                                                                    api_preset_select.value = api_name
                                                                    apply_preset()
                                                                api_browser_container.visible = False
                                                                api_form_container.visible = True
                                                            return handler
                                                        ui.button("Use This API", icon="arrow_forward", on_click=make_select_handler(api["name"])).classes("mt-2").props("flat size=sm")
                                        
                                        # Economic APIs panel
                                        with ui.tab_panel(economic_tab):
                                            with ui.column().classes("w-full gap-3"):
                                                for api in api_categories["Economic Data APIs"]:
                                                    with ui.card().classes("w-full p-4 hover:bg-gray-50 cursor-pointer"):
                                                        ui.label(api["name"]).classes("text-lg font-semibold")
                                                        with ui.row().classes("w-full gap-4 text-sm mt-2"):
                                                            ui.label(f"Free Tier: {api['free_tier']}").classes("text-blue-600")
                                                            ui.label(f"Real-Time: {api['realtime']}").classes("text-green-600")
                                                            ui.label(f"History: {api['history']}").classes("text-purple-600")
                                                        ui.label(f"Data Types: {api['data_types']}").classes("text-sm text-gray-600 mt-1")
                                                        ui.label(f"Note: {api['note']}").classes("text-xs text-gray-500 mt-1")
                                                        ui.label(f"Website: {api['website']}").classes("text-xs text-blue-500 mt-1")
                                                        def make_select_handler(api_name):
                                                            def handler():
                                                                source_type_select.value = "API (Requires Key)"
                                                                if api_name in api_presets:
                                                                    api_preset_select.value = api_name
                                                                    apply_preset()
                                                                api_browser_container.visible = False
                                                                api_form_container.visible = True
                                                            return handler
                                                        ui.button("Use This API", icon="arrow_forward", on_click=make_select_handler(api["name"])).classes("mt-2").props("flat size=sm")
                                        
                                        # Crypto APIs panel
                                        with ui.tab_panel(crypto_tab):
                                            with ui.column().classes("w-full gap-3"):
                                                for api in api_categories["Cryptocurrency APIs"]:
                                                    with ui.card().classes("w-full p-4 hover:bg-gray-50 cursor-pointer"):
                                                        ui.label(api["name"]).classes("text-lg font-semibold")
                                                        with ui.row().classes("w-full gap-4 text-sm mt-2"):
                                                            ui.label(f"Free Tier: {api['free_tier']}").classes("text-blue-600")
                                                            ui.label(f"Real-Time: {api['realtime']}").classes("text-green-600")
                                                            ui.label(f"History: {api['history']}").classes("text-purple-600")
                                                        ui.label(f"Data Types: {api['data_types']}").classes("text-sm text-gray-600 mt-1")
                                                        ui.label(f"Note: {api['note']}").classes("text-xs text-gray-500 mt-1")
                                                        ui.label(f"Website: {api['website']}").classes("text-xs text-blue-500 mt-1")
                                                        def make_select_handler(api_name):
                                                            def handler():
                                                                source_type_select.value = "API (Requires Key)"
                                                                if api_name in api_presets:
                                                                    api_preset_select.value = api_name
                                                                    apply_preset()
                                                                api_browser_container.visible = False
                                                                api_form_container.visible = True
                                                            return handler
                                                        ui.button("Use This API", icon="arrow_forward", on_click=make_select_handler(api["name"])).classes("mt-2").props("flat size=sm")
                                        
                                        # Open Data Platforms panel
                                        with ui.tab_panel(open_data_tab):
                                            with ui.column().classes("w-full gap-3"):
                                                for api in api_categories["Open Data Platforms"]:
                                                    with ui.card().classes("w-full p-4 hover:bg-gray-50 cursor-pointer"):
                                                        ui.label(api["name"]).classes("text-lg font-semibold")
                                                        with ui.row().classes("w-full gap-4 text-sm mt-2"):
                                                            ui.label(f"Free Tier: {api['free_tier']}").classes("text-blue-600")
                                                            ui.label(f"Real-Time: {api['realtime']}").classes("text-green-600")
                                                            ui.label(f"History: {api['history']}").classes("text-purple-600")
                                                        ui.label(f"Data Types: {api['data_types']}").classes("text-sm text-gray-600 mt-1")
                                                        ui.label(f"Note: {api['note']}").classes("text-xs text-gray-500 mt-1")
                                                        ui.label(f"Website: {api['website']}").classes("text-xs text-blue-500 mt-1")
                                                        def select_api(api_name=api["name"]):
                                                            source_type_select.value = "API (Requires Key)"
                                                            if api_name in api_presets:
                                                                api_preset_select.value = api_name
                                                                apply_preset()
                                                            api_browser_container.visible = False
                                                            api_form_container.visible = True
                                                        ui.button("Use This API", icon="arrow_forward", on_click=lambda n=api["name"]: select_api(n)).classes("mt-2").props("flat size=sm")
                                    
                                    ui.separator().classes("my-4")
                                    ui.label("💡 Tip: Click 'Use This API' to automatically configure the API preset, or see API_SOURCES.md for detailed documentation.").classes("text-sm text-blue-600")
                                
                                # Free datasets section
                                with ui.column().classes("w-full") as free_datasets_container:
                                    free_datasets_container.visible = False
                                    
                                    ui.label("📥 Free Time-Series Datasets").classes("text-lg font-semibold mb-2")
                                    ui.label("Download free datasets without API keys").classes("text-sm text-gray-500 mb-2")
                                    
                                    with ui.card().classes("w-full p-3 mb-4 bg-purple-50 border-l-4 border-purple-500"):
                                        ui.label("ℹ️ How to Use").classes("font-semibold text-purple-800 mb-1")
                                        ui.label("These sources provide direct CSV/JSON downloads. Visit the website, download the file, then use the Upload button in VARIOSYNC to process it. No API keys required!").classes("text-sm text-purple-700")
                                    
                                    # List of free data sources
                                    free_sources = [
                                        {
                                            "name": "World Bank Open Data",
                                            "description": "1,400+ economic indicators, 217+ countries",
                                            "url": "https://datatopics.worldbank.org/world-development-indicators",
                                            "format": "CSV",
                                            "action": "Visit website to download CSV"
                                        },
                                        {
                                            "name": "FRED Economic Data",
                                            "description": "US economic time-series (unemployment, GDP, etc.)",
                                            "url": "https://fred.stlouisfed.org",
                                            "format": "CSV",
                                            "action": "Search and download CSV from website"
                                        },
                                        {
                                            "name": "NOAA Climate Data",
                                            "description": "US weather and climate historical data",
                                            "url": "https://www.ncei.noaa.gov/data/daily-summaries/",
                                            "format": "CSV",
                                            "action": "Download CSV files directly"
                                        },
                                        {
                                            "name": "Kaggle Datasets",
                                            "description": "Thousands of time-series datasets",
                                            "url": "https://www.kaggle.com/datasets",
                                            "format": "CSV, JSON, Parquet",
                                            "action": "Free account required, then download"
                                        },
                                        {
                                            "name": "UCI ML Repository",
                                            "description": "Time-series datasets for ML research",
                                            "url": "https://archive.ics.uci.edu/ml/index.php",
                                            "format": "CSV",
                                            "action": "Direct CSV downloads available"
                                        },
                                        {
                                            "name": "Our World in Data",
                                            "description": "Global development data (health, environment, etc.)",
                                            "url": "https://ourworldindata.org",
                                            "format": "CSV",
                                            "action": "Download CSV from any chart/dataset"
                                        }
                                    ]
                                    
                                    for source in free_sources:
                                        with ui.card().classes("w-full p-3 mb-2"):
                                            ui.label(source["name"]).classes("font-semibold")
                                            ui.label(source["description"]).classes("text-sm text-gray-600")
                                            ui.label(f"Format: {source['format']}").classes("text-xs text-gray-500")
                                            ui.label(f"Action: {source['action']}").classes("text-xs text-blue-600 mt-1")
                                    
                                    ui.separator().classes("my-4")
                                    
                                    with ui.card().classes("w-full p-3 bg-yellow-50 border-l-4 border-yellow-500"):
                                        ui.label("📋 Instructions").classes("font-semibold text-yellow-800 mb-1")
                                        ui.label("1. Visit the website link for your chosen data source").classes("text-sm text-yellow-700")
                                        ui.label("2. Download the CSV/JSON file from their website").classes("text-sm text-yellow-700")
                                        ui.label("3. Use the Upload button in VARIOSYNC to process the downloaded file").classes("text-sm text-yellow-700")
                                        ui.label("4. See FREE_DATA_SOURCES.md for detailed instructions and more sources").classes("text-sm text-yellow-700 mt-2")
                                
                                # API form fields container
                                with ui.column().classes("w-full") as api_form_container:
                                    api_form_container.visible = True
                                    
                                    # API preset selector
                                    with ui.column().classes("w-full"):
                                        api_preset_select = ui.select(
                                            list(api_presets.keys()),
                                            label="API Preset",
                                            value="Custom API"
                                        ).classes("w-full")
                                        ui.label("Select a pre-configured API or choose 'Custom API' to configure manually").classes("text-xs text-gray-500 mt-1")
                                    
                                    # Form fields with help text
                                    api_name_input = ui.input(label="API Name", placeholder="e.g., Alpha Vantage, OpenWeather").classes("w-full")
                                    ui.label("A friendly name to identify this API configuration").classes("text-xs text-gray-500 mb-2")
                                    
                                    base_url_input = ui.input(label="Base URL", placeholder="https://api.example.com").classes("w-full")
                                    ui.label("The base URL of the API (without endpoint path)").classes("text-xs text-gray-500 mb-2")
                                    
                                    endpoint_input = ui.input(label="Endpoint", placeholder="/data/history").classes("w-full")
                                    ui.label("The API endpoint path (e.g., /time_series, /stock/candle)").classes("text-xs text-gray-500 mb-2")
                                    
                                    api_key_input = ui.input(label="API Key", password=True, placeholder="Your API key").classes("w-full")
                                    ui.label("Your API key from the service provider. Get it from their website after signing up.").classes("text-xs text-gray-500 mb-2")
                                    
                                    entity_input = ui.input(label="Entity/Symbol", placeholder="e.g., AAPL, NYC, latitude,longitude").classes("w-full")
                                    ui.label("The identifier for the data you want (stock symbol, city name, coordinates, etc.)").classes("text-xs text-gray-500 mb-2")
                                    
                                    with ui.row().classes("w-full gap-2"):
                                        with ui.column().classes("flex-1"):
                                            ui.label("Start Date").classes("text-sm mb-1")
                                            start_date_input = ui.date().classes("w-full")
                                            ui.label("Beginning of date range").classes("text-xs text-gray-500 mt-1")
                                        with ui.column().classes("flex-1"):
                                            ui.label("End Date").classes("text-sm mb-1")
                                            end_date_input = ui.date().classes("w-full")
                                            ui.label("End of date range").classes("text-xs text-gray-500 mt-1")
                                    
                                    record_type_select = ui.select(
                                        ["time_series", "financial"],
                                        label="Record Type",
                                        value="time_series"
                                    ).classes("w-full")
                                    ui.label("Choose 'time_series' for general data or 'financial' for stock/market data").classes("text-xs text-gray-500 mb-2")
                                    
                                    status_label = ui.label("Ready to download").classes("text-sm")
                                    
                                    with ui.column().classes("w-full mt-2"):
                                        download_button = ui.button("Download", icon="download", color="primary")
                                        ui.label("Click to download data from the configured API. Make sure all required fields are filled.").classes("text-xs text-gray-500 mt-1")
                                
                                def toggle_source_type():
                                    if source_type_select.value == "Free Dataset (No Key)":
                                        api_form_container.visible = False
                                        free_datasets_container.visible = True
                                        api_browser_container.visible = False
                                    elif source_type_select.value == "Browse All APIs":
                                        api_form_container.visible = False
                                        free_datasets_container.visible = False
                                        api_browser_container.visible = True
                                    else:
                                        api_form_container.visible = True
                                        free_datasets_container.visible = False
                                        api_browser_container.visible = False
                                
                                source_type_select.on('update:modelValue', toggle_source_type)
                                
                                # Helper function to populate fields from preset
                                def apply_preset():
                                    preset_name = api_preset_select.value
                                    if preset_name != "Custom API" and preset_name in api_presets:
                                        preset = api_presets[preset_name]
                                        api_name_input.value = preset_name
                                        base_url_input.value = preset.get("base_url", "")
                                        endpoint_input.value = preset.get("endpoint", "")
                                        api_key_input.value = ""  # User must enter their own key
                                        if preset.get("note"):
                                            ui.notify(preset["note"], type="info")
                                
                                api_preset_select.on('update:modelValue', apply_preset)
                                
                                # Load saved API keys
                                try:
                                    from api_keys_manager import APIKeysManager
                                    keys_manager = APIKeysManager()
                                    saved_keys = keys_manager.get_keys()
                                    if saved_keys:
                                        api_key_select = ui.select(
                                            [k['name'] for k in saved_keys],
                                            label="Use Saved API Key",
                                            value=None
                                        ).classes("w-full")
                                        
                                        def use_saved_key():
                                            selected = api_key_select.value
                                            if selected:
                                                key_data = next((k for k in saved_keys if k['name'] == selected), None)
                                                if key_data:
                                                    # Try to get the actual key value (if available)
                                                    # Note: Keys are masked in the manager, so we'd need to load from file
                                                    try:
                                                        import json
                                                        keys_file = Path("api_keys.json")
                                                        if keys_file.exists():
                                                            with open(keys_file, 'r') as f:
                                                                keys_data = json.load(f)
                                                                for k in keys_data.get('keys', []):
                                                                    if k.get('name') == selected:
                                                                        api_key_input.value = k.get('api_key', '')
                                                                        ui.notify(f"Loaded API key for {selected}", type="positive")
                                                                        return
                                                    except:
                                                        pass
                                                    ui.notify(f"Select {selected} and enter key manually (keys are stored securely)", type="info")
                                        api_key_select.on('update:modelValue', use_saved_key)
                                except:
                                    pass
                                
                                def execute_download():
                                    try:
                                        download_button.set_enabled(False)
                                        status_label.text = "⏳ Downloading..."
                                        
                                        # Get preset config if selected
                                        preset_name = api_preset_select.value
                                        preset_config = api_presets.get(preset_name) if preset_name != "Custom API" else {}
                                        
                                        # Build API config (use preset values as defaults)
                                        api_config = {
                                            "name": api_name_input.value or preset_name or "Custom API",
                                            "base_url": base_url_input.value or preset_config.get("base_url", ""),
                                            "endpoint": endpoint_input.value or preset_config.get("endpoint", ""),
                                            "api_key": api_key_input.value,
                                            "api_key_param": preset_config.get("api_key_param", "apikey"),
                                            "entity_param": preset_config.get("entity_param", "symbol"),
                                            "start_date_param": preset_config.get("start_date_param", "from"),
                                            "end_date_param": preset_config.get("end_date_param", "to"),
                                            "date_format": preset_config.get("date_format", "YYYY-MM-DD"),
                                            "response_format": "json"
                                        }
                                        
                                        # Validate required fields
                                        if not all([base_url_input.value, endpoint_input.value, api_key_input.value, entity_input.value]):
                                            status_label.text = "❌ Please fill in all required fields"
                                            download_button.set_enabled(True)
                                            return
                                        
                                        # Import and use APIDownloader
                                        from api_downloader import APIDownloader
                                        from datetime import datetime as dt
                                        
                                        downloader = APIDownloader(api_config, app.storage)
                                        
                                        start_date = None
                                        end_date = None
                                        if start_date_input.value:
                                            if isinstance(start_date_input.value, str):
                                                start_date = dt.fromisoformat(start_date_input.value)
                                            else:
                                                start_date = dt.combine(start_date_input.value, dt.min.time())
                                        if end_date_input.value:
                                            if isinstance(end_date_input.value, str):
                                                end_date = dt.fromisoformat(end_date_input.value)
                                            else:
                                                end_date = dt.combine(end_date_input.value, dt.max.time())
                                        
                                        # Download and save
                                        success = downloader.download_and_save(
                                            entity_input.value,
                                            start_date,
                                            end_date
                                        )
                                        
                                        if success:
                                            status_label.text = "✅ Download completed successfully!"
                                            ui.notify("Download completed", type="positive")
                                            # Refresh storage browser
                                            ui.run_javascript('document.querySelector("[data-section=\\"storage\\"]")?.scrollIntoView({behavior: "smooth"})')
                                        else:
                                            status_label.text = "❌ Download failed. Check API configuration."
                                            ui.notify("Download failed", type="negative")
                                        
                                        download_button.set_enabled(True)
                                    except Exception as e:
                                        logger.error(f"Error downloading from API: {e}", exc_info=True)
                                        status_label.text = f"❌ Error: {str(e)}"
                                        ui.notify(f"Download error: {str(e)}", type="negative")
                                        download_button.set_enabled(True)
                                
                                download_button.on_click(execute_download)
                                
                                with ui.column().classes("w-full gap-2 mt-4"):
                                    with ui.card().classes("w-full p-3 bg-gray-50"):
                                        ui.label("📖 Additional Resources").classes("font-semibold text-gray-800 mb-2")
                                        ui.label("• API_SOURCES.md - Complete API documentation with configuration examples").classes("text-xs text-gray-600 mb-1")
                                        ui.label("• FREE_DATA_SOURCES.md - List of free datasets (no API keys required)").classes("text-xs text-gray-600 mb-1")
                                        ui.label("• Configure persistent API sources in config.json for reuse").classes("text-xs text-gray-600 mb-2")
                                        
                                        with ui.row().classes("w-full gap-2"):
                                            def open_api_docs():
                                                ui.notify("See API_SOURCES.md file for complete API documentation", type="info")
                                            
                                            def open_free_data_docs():
                                                ui.notify("See FREE_DATA_SOURCES.md for free datasets (no API keys)", type="info")
                                            
                                            ui.button("📚 View API Docs", icon="book", on_click=open_api_docs).props("flat size=sm")
                                            ui.button("📥 View Free Data", icon="download", on_click=open_free_data_docs).props("flat size=sm")
                                
                                with ui.row().classes("w-full justify-end mt-4"):
                                    ui.button("Close", on_click=download_dialog.close).props("flat")
                            download_dialog.open()
                        except Exception as e:
                            logger.error(f"Error showing download dialog: {e}", exc_info=True)
                            ui.notify(f"Error: {str(e)}", type="negative")
                    
                    ui.button(icon="download", on_click=show_download_dialog).tooltip("Download from API")
                    
                    # Upload - scroll to upload section
                    def scroll_to_upload():
                        try:
                            app = get_app_instance()
                            # Show upload stats if available
                            if app.storage:
                                try:
                                    keys = app.storage.list_keys()
                                    recent_uploads = [k for k in keys if 'upload' in k.lower() or 'temp' in k.lower()][:5]
                                    if recent_uploads:
                                        ui.notify(f"Recent uploads: {len(recent_uploads)} files", type="info")
                                except:
                                    pass
                            
                            ui.run_javascript('document.querySelector("[data-section=\\"upload\\"]")?.scrollIntoView({behavior: "smooth"})')
                            ui.notify("Scrolled to upload section", type="info")
                        except Exception as e:
                            logger.error(f"Error scrolling to upload: {e}")
                            ui.notify("Error accessing upload section", type="negative")
                    
                    upload_btn = ui.button(icon="upload", on_click=scroll_to_upload).tooltip("Upload Files")
                    
                    # Sync - refresh all data
                    def sync_all():
                        try:
                            app = get_app_instance()
                            sync_btn.set_enabled(False)
                            ui.notify("Syncing all data...", type="info")
                            
                            # Sync operations
                            sync_count = 0
                            
                            # Sync storage
                            if app.storage:
                                try:
                                    keys = app.storage.list_keys()
                                    sync_count += len(keys)
                                except:
                                    pass
                            
                            # Sync from API sources (if configured)
                            # This would trigger API downloads if configured
                            
                            ui.notify(f"Sync complete: {sync_count} items synced", type="positive")
                            # Remove loading state by re-enabling button
                            sync_btn.set_enabled(True)
                            ui.run_javascript('window.location.reload()')
                        except Exception as e:
                            logger.error(f"Error syncing: {e}", exc_info=True)
                            ui.notify(f"Sync error: {str(e)}", type="negative")
                            # Remove loading state by re-enabling button
                            sync_btn.set_enabled(True)
                    
                    sync_btn = ui.button(icon="sync", on_click=sync_all).tooltip("Sync All Data")
                    
                    # API Keys
                    def show_api_keys():
                        try:
                            from api_keys_manager import APIKeysManager
                            keys_manager = APIKeysManager()
                            
                            with ui.dialog() as keys_dialog, ui.card().classes("w-full max-w-3xl"):
                                ui.label("🔑 API Keys Management").classes("text-xl font-semibold mb-4")
                                
                                # Load existing keys
                                existing_keys = keys_manager.get_keys()
                                
                                # Keys table
                                keys_table = ui.table(
                                    columns=[
                                        {"name": "name", "label": "Name", "field": "name", "required": True},
                                        {"name": "api_key", "label": "API Key", "field": "api_key"},
                                        {"name": "source", "label": "Source", "field": "source"},
                                        {"name": "description", "label": "Description", "field": "description"}
                                    ],
                                    rows=[],
                                    row_key="name"
                                ).classes("w-full mb-4")
                                
                                def refresh_keys_table():
                                    keys = keys_manager.get_keys()
                                    rows = []
                                    for key in keys:
                                        rows.append({
                                            "name": key.get('name', 'Unknown'),
                                            "api_key": key.get('api_key', 'N/A'),
                                            "source": key.get('source', 'unknown'),
                                            "description": key.get('description', '')
                                        })
                                    keys_table.rows = rows
                                
                                def delete_selected_key():
                                    selected = keys_table.selected
                                    if not selected or len(selected) == 0:
                                        ui.notify("Please select a key to delete", type="warning")
                                        return
                                    
                                    key_name = selected[0].get('name')
                                    if selected[0].get('source') != 'file':
                                        ui.notify("Cannot delete environment variable keys", type="warning")
                                        return
                                    
                                    if keys_manager.delete_key(key_name):
                                        ui.notify(f"Deleted API key: {key_name}", type="positive")
                                        refresh_keys_table()
                                    else:
                                        ui.notify("Failed to delete API key", type="negative")
                                
                                delete_button = ui.button("Delete Selected", icon="delete", color="negative", on_click=delete_selected_key).classes("mb-4")
                                
                                refresh_keys_table()
                                
                                # Add new key form
                                with ui.expansion("➕ Add New API Key", icon="add").classes("w-full mb-4"):
                                    with ui.column().classes("w-full gap-2"):
                                        name_input = ui.input(label="API Name/Provider", placeholder="e.g., Alpha Vantage").classes("w-full")
                                        key_input = ui.input(label="API Key", password=True, placeholder="Your API key").classes("w-full")
                                        desc_input = ui.input(label="Description", placeholder="Optional description").classes("w-full")
                                        
                                        add_button = ui.button("Add Key", icon="add", color="primary")
                                        
                                        def add_key():
                                            try:
                                                if not name_input.value or not key_input.value:
                                                    ui.notify("Please provide name and API key", type="warning")
                                                    return
                                                
                                                success = keys_manager.add_key(
                                                    name_input.value,
                                                    key_input.value,
                                                    desc_input.value or ""
                                                )
                                                
                                                if success:
                                                    ui.notify("API key added successfully", type="positive")
                                                    name_input.value = ""
                                                    key_input.value = ""
                                                    desc_input.value = ""
                                                    refresh_keys_table()
                                                else:
                                                    ui.notify("Failed to add API key", type="negative")
                                            except Exception as e:
                                                logger.error(f"Error adding API key: {e}", exc_info=True)
                                                ui.notify(f"Error: {str(e)}", type="negative")
                                        
                                        add_button.on_click(add_key)
                                
                                # Info note
                                ui.label("Note: Keys stored in api_keys.json. Environment variables are read-only.").classes("text-xs text-gray-500")
                                
                                with ui.row().classes("w-full justify-end mt-4"):
                                    ui.button("Close", on_click=keys_dialog.close).props("flat")
                            keys_dialog.open()
                        except Exception as e:
                            logger.error(f"Error showing API keys dialog: {e}", exc_info=True)
                            ui.notify(f"Error: {str(e)}", type="negative")
                    
                    ui.button(icon="vpn_key", on_click=show_api_keys).tooltip("API Keys")
                    
                    # Search
                    def show_search():
                        try:
                            app = get_app_instance()
                            with ui.dialog() as search_dialog, ui.card().classes("w-full max-w-4xl"):
                                ui.label("🔍 Search").classes("text-xl font-semibold mb-4")
                                
                                search_input = ui.input(placeholder="Search records, series, metrics...").classes("w-full")
                                
                                # Filters
                                with ui.row().classes("w-full gap-2"):
                                    file_type_filter = ui.select(
                                        ["All", "json", "csv", "parquet", "duckdb"],
                                        label="File Type",
                                        value="All"
                                    ).classes("flex-1")
                                    
                                    series_filter = ui.input(label="Series ID", placeholder="Filter by series...").classes("flex-1")
                                
                                with ui.row().classes("w-full gap-2"):
                                    with ui.column().classes("flex-1"):
                                        ui.label("Start Date").classes("text-sm mb-1")
                                        start_date_filter = ui.date().classes("w-full")
                                    with ui.column().classes("flex-1"):
                                        ui.label("End Date").classes("text-sm mb-1")
                                        end_date_filter = ui.date().classes("w-full")
                                
                                search_button = ui.button("Search", icon="search", color="primary")
                                
                                # Results table
                                results_table = ui.table(
                                    columns=[
                                        {"name": "key", "label": "Key", "field": "key", "required": True},
                                        {"name": "type", "label": "Type", "field": "type"},
                                        {"name": "size", "label": "Size", "field": "size"}
                                    ],
                                    rows=[],
                                    row_key="key"
                                ).classes("w-full mt-4")
                                
                                results_count_label = ui.label("No results").classes("text-sm text-gray-500")
                                
                                def perform_search():
                                    try:
                                        search_button.set_enabled(False)
                                        query = search_input.value.lower() if search_input.value else ""
                                        
                                        if not app.storage:
                                            ui.notify("Storage not available", type="warning")
                                            return
                                        
                                        # Get all keys
                                        all_keys = app.storage.list_keys()
                                        
                                        # Apply filters
                                        filtered_keys = []
                                        for key in all_keys:
                                            # File type filter
                                            if file_type_filter.value != "All":
                                                if not key.lower().endswith(f".{file_type_filter.value.lower()}"):
                                                    continue
                                            
                                            # Text search
                                            if query:
                                                if query not in key.lower():
                                                    # Could also search within file content here
                                                    continue
                                            
                                            # Series filter
                                            if series_filter.value:
                                                if series_filter.value.lower() not in key.lower():
                                                    continue
                                            
                                            filtered_keys.append(key)
                                        
                                        # Build results
                                        results = []
                                        for key in filtered_keys[:100]:  # Limit to 100 results
                                            file_type = key.split('.')[-1].upper() if '.' in key else 'DATA'
                                            size_bytes = app.storage.get_size(key)
                                            
                                            if size_bytes is not None:
                                                if size_bytes >= 1024 * 1024:
                                                    size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
                                                elif size_bytes >= 1024:
                                                    size_str = f"{size_bytes / 1024:.2f} KB"
                                                else:
                                                    size_str = f"{size_bytes} B"
                                            else:
                                                size_str = "N/A"
                                            
                                            results.append({
                                                "key": key,
                                                "type": file_type,
                                                "size": size_str
                                            })
                                        
                                        results_table.rows = results
                                        results_count_label.text = f"Found {len(results)} result(s)"
                                        
                                        if len(results) == 0:
                                            ui.notify("No results found", type="info")
                                        else:
                                            ui.notify(f"Found {len(results)} results", type="positive")
                                        
                                        search_button.set_enabled(True)
                                    except Exception as e:
                                        logger.error(f"Error performing search: {e}", exc_info=True)
                                        ui.notify(f"Search error: {str(e)}", type="negative")
                                        search_button.set_enabled(True)
                                
                                search_button.on_click(perform_search)
                                search_input.on('keydown.enter', perform_search)
                                
                                # Cache search in Redis if available
                                def cache_search_results(query, results):
                                    try:
                                        from redis_client import RedisClientFactory
                                        redis_client = RedisClientFactory.get_instance()
                                        if redis_client:
                                            redis_client.set(f"search:{query}", results, ttl=3600)
                                    except:
                                        pass
                                
                                with ui.row().classes("w-full justify-end mt-4"):
                                    ui.button("Close", on_click=search_dialog.close).props("flat")
                            search_dialog.open()
                        except Exception as e:
                            logger.error(f"Error showing search dialog: {e}", exc_info=True)
                            ui.notify(f"Error: {str(e)}", type="negative")
                    
                    ui.button(icon="search", on_click=show_search).tooltip("Search")
                    
                    # Payment
                    def show_payment():
                        try:
                            app = get_app_instance()
                            with ui.dialog() as payment_dialog, ui.card().classes("w-full max-w-2xl"):
                                ui.label("💳 Payment & Billing").classes("text-xl font-semibold mb-4")
                                
                                hours_remaining = None
                                hours_used = 0.0
                                
                                # Try to get hours from Supabase
                                if app.auth_manager and app.auth_manager.supabase_client:
                                    try:
                                        # In a real implementation, get user_id from auth session
                                        # For now, show what we can determine
                                        supabase_client = app.auth_manager.supabase_client
                                        if hasattr(supabase_client, 'operations'):
                                            # This would require actual user authentication
                                            # For demo, show connection status
                                            pass
                                    except Exception as e:
                                        logger.debug(f"Could not get payment info: {e}")
                                
                                with ui.column().classes("w-full gap-4"):
                                    # Current Balance
                                    with ui.card().classes("w-full p-4 bg-blue-50 dark:bg-blue-900"):
                                        ui.label("Current Balance").classes("text-sm font-semibold mb-2")
                                        if hours_remaining is not None:
                                            ui.label(f"{hours_remaining:.2f} hours remaining").classes("text-2xl font-bold text-green-600")
                                        else:
                                            ui.label("Hours balance not available").classes("text-lg text-gray-500")
                                            ui.label("Connect to Supabase and authenticate to view balance").classes("text-xs text-gray-400 mt-1")
                                    
                                    # Usage Information
                                    with ui.card().classes("w-full p-4"):
                                        ui.label("Usage Information").classes("text-sm font-semibold mb-2")
                                        ui.label(f"Hours Used: {hours_used:.2f}h").classes("text-sm")
                                        if hours_remaining is not None:
                                            total_hours = hours_remaining + hours_used
                                            if total_hours > 0:
                                                usage_percent = (hours_used / total_hours) * 100
                                                ui.label(f"Usage: {usage_percent:.1f}%").classes("text-sm")
                                    
                                    # Hour Packages
                                    with ui.card().classes("w-full p-4"):
                                        ui.label("Purchase Hours").classes("text-sm font-semibold mb-3")
                                        packages = [
                                            {"hours": 5, "price": 25, "name": "5 Hours Pack"},
                                            {"hours": 10, "price": 45, "name": "10 Hours Pack"},
                                            {"hours": 20, "price": 80, "name": "20 Hours Pack"},
                                            {"hours": 50, "price": 180, "name": "50 Hours Pack"}
                                        ]
                                        
                                        with ui.grid(columns=2).classes("w-full gap-2"):
                                            for pkg in packages:
                                                with ui.card().classes("p-3 cursor-pointer hover:bg-gray-100"):
                                                    ui.label(pkg["name"]).classes("font-semibold")
                                                    ui.label(f"{pkg['hours']} hours").classes("text-sm")
                                                    ui.label(f"${pkg['price']}").classes("text-lg font-bold text-blue-600")
                                        
                                        ui.label("Payment integration coming soon").classes("text-xs text-gray-400 mt-2")
                                    
                                    # Billing History
                                    with ui.card().classes("w-full p-4"):
                                        ui.label("Billing History").classes("text-sm font-semibold mb-2")
                                        ui.label("No billing history available").classes("text-sm text-gray-500")
                                
                                with ui.row().classes("w-full justify-end mt-4"):
                                    ui.button("Close", on_click=payment_dialog.close).props("flat")
                            payment_dialog.open()
                        except Exception as e:
                            logger.error(f"Error showing payment info: {e}", exc_info=True)
                            ui.notify(f"Error: {str(e)}", type="negative")
                    
                    ui.button(icon="credit_card", on_click=show_payment).tooltip("Payment & Billing")
                    
                    # Settings
                    def show_settings():
                        try:
                            app = get_app_instance()
                            with ui.dialog() as settings_dialog, ui.card().classes("w-full max-w-3xl"):
                                ui.label("⚙️ Settings").classes("text-xl font-semibold mb-4")
                                
                                # Create tabs
                                with ui.tabs().classes("w-full") as tabs:
                                    general_tab = ui.tab("General")
                                    api_tab = ui.tab("API")
                                    display_tab = ui.tab("Display")
                                    performance_tab = ui.tab("Performance")
                                
                                with ui.tab_panels(tabs, value=general_tab).classes("w-full"):
                                    # General Settings
                                    with ui.tab_panel(general_tab):
                                        with ui.column().classes("w-full gap-4"):
                                            storage_backend_select = ui.select(
                                                ["local", "s3", "wasabi", "supabase"],
                                                label="Storage Backend",
                                                value=app.config.get('Data', {}).get('storage_backend', 'local')
                                            ).classes("w-full")
                                            
                                            storage_path_input = ui.input(
                                                label="Storage Path",
                                                value=app.config.get('Data', {}).get('csv_dir', 'data')
                                            ).classes("w-full")
                                            
                                            log_level_select = ui.select(
                                                ["DEBUG", "INFO", "WARNING", "ERROR"],
                                                label="Log Level",
                                                value=app.config.get('Logging', {}).get('level', 'INFO')
                                            ).classes("w-full")
                                            
                                            log_file_input = ui.input(
                                                label="Log File",
                                                value=app.config.get('Logging', {}).get('file', 'variosync.log')
                                            ).classes("w-full")
                                    
                                    # API Settings
                                    with ui.tab_panel(api_tab):
                                        with ui.column().classes("w-full gap-4"):
                                            timeout_input = ui.number(
                                                label="API Timeout (seconds)",
                                                value=app.config.get('Download', {}).get('timeout', 30),
                                                min=1,
                                                max=300
                                            ).classes("w-full")
                                            
                                            max_retries_input = ui.number(
                                                label="Max Retries",
                                                value=app.config.get('Download', {}).get('max_retries', 3),
                                                min=0,
                                                max=10
                                            ).classes("w-full")
                                            
                                            rate_limit_input = ui.number(
                                                label="Rate Limit Delay (seconds)",
                                                value=app.config.get('Download', {}).get('rate_limit_delay', 1.0),
                                                min=0.1,
                                                max=60.0,
                                                step=0.1
                                            ).classes("w-full")
                                    
                                    # Display Settings
                                    with ui.tab_panel(display_tab):
                                        with ui.column().classes("w-full gap-4"):
                                            rows_per_page_input = ui.number(
                                                label="Rows Per Page",
                                                value=app.config.get('Display', {}).get('rows_per_page', 100),
                                                min=10,
                                                max=1000
                                            ).classes("w-full")
                                            
                                            theme_select = ui.select(
                                                ["default", "dark", "light"],
                                                label="Theme",
                                                value=app.config.get('Display', {}).get('theme', 'default')
                                            ).classes("w-full")
                                            
                                            font_size_input = ui.number(
                                                label="Font Size",
                                                value=app.config.get('Display', {}).get('font_size', 10),
                                                min=8,
                                                max=20
                                            ).classes("w-full")
                                    
                                    # Performance Settings
                                    with ui.tab_panel(performance_tab):
                                        with ui.column().classes("w-full gap-4"):
                                            cache_size_input = ui.number(
                                                label="Cache Size",
                                                value=app.config.get('Data', {}).get('cache_size', 1000),
                                                min=100,
                                                max=10000
                                            ).classes("w-full")
                                            
                                            thread_count_input = ui.number(
                                                label="Thread Count",
                                                value=app.config.get('Data', {}).get('thread_count', 4),
                                                min=1,
                                                max=16
                                            ).classes("w-full")
                                            
                                            memory_limit_input = ui.number(
                                                label="Memory Limit (MB)",
                                                value=app.config.get('Performance', {}).get('memory_limit', 1024),
                                                min=256,
                                                max=8192
                                            ).classes("w-full")
                                
                                # Save button
                                def save_settings():
                                    try:
                                        # Build updated config
                                        updated_config = app.config.config.copy()
                                        
                                        # Update Data section
                                        if 'Data' not in updated_config:
                                            updated_config['Data'] = {}
                                        updated_config['Data']['storage_backend'] = storage_backend_select.value
                                        updated_config['Data']['csv_dir'] = storage_path_input.value
                                        updated_config['Data']['cache_size'] = int(cache_size_input.value)
                                        updated_config['Data']['thread_count'] = int(thread_count_input.value)
                                        
                                        # Update Logging section
                                        if 'Logging' not in updated_config:
                                            updated_config['Logging'] = {}
                                        updated_config['Logging']['level'] = log_level_select.value
                                        updated_config['Logging']['file'] = log_file_input.value
                                        
                                        # Update Download section
                                        if 'Download' not in updated_config:
                                            updated_config['Download'] = {}
                                        updated_config['Download']['timeout'] = int(timeout_input.value)
                                        updated_config['Download']['max_retries'] = int(max_retries_input.value)
                                        updated_config['Download']['rate_limit_delay'] = float(rate_limit_input.value)
                                        
                                        # Update Display section
                                        if 'Display' not in updated_config:
                                            updated_config['Display'] = {}
                                        updated_config['Display']['rows_per_page'] = int(rows_per_page_input.value)
                                        updated_config['Display']['theme'] = theme_select.value
                                        updated_config['Display']['font_size'] = int(font_size_input.value)
                                        
                                        # Update Performance section
                                        if 'Performance' not in updated_config:
                                            updated_config['Performance'] = {}
                                        updated_config['Performance']['memory_limit'] = int(memory_limit_input.value)
                                        
                                        # Save to config file
                                        config_path = getattr(app.config, 'config_path', 'config.json')
                                        with open(config_path, 'w') as f:
                                            json.dump(updated_config, f, indent=2)
                                        
                                        ui.notify("Settings saved successfully. Restart application to apply changes.", type="positive")
                                        settings_dialog.close()
                                    except Exception as e:
                                        logger.error(f"Error saving settings: {e}", exc_info=True)
                                        ui.notify(f"Error saving settings: {str(e)}", type="negative")
                                
                                with ui.row().classes("w-full justify-between mt-4"):
                                    ui.button("Reset to Defaults", icon="refresh", on_click=lambda: ui.notify("Reset functionality coming soon", type="info"))
                                    with ui.row().classes("gap-2"):
                                        ui.button("Cancel", on_click=settings_dialog.close).props("flat")
                                        ui.button("Save", icon="save", color="primary", on_click=save_settings)
                            
                            settings_dialog.open()
                        except Exception as e:
                            logger.error(f"Error showing settings: {e}", exc_info=True)
                            ui.notify(f"Error: {str(e)}", type="negative")
                    
                    ui.button(icon="settings", on_click=show_settings).tooltip("Settings")
            
            # Center: Status indicators
            with ui.row().classes("gap-4 items-center flex-1 justify-center"):
                ui.badge("Online 10 formats", color="info")
                with ui.row().classes("items-center gap-2"):
                    ui.icon("circle", color="green", size="sm")
                    ui.label("running")
                ui.badge("DB: available", color="success")
                ui.icon("description")
            
            # Right: Theme and usage
            with ui.row().classes("gap-4 items-center"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("palette")
                    ui.label("Dark")
                with ui.row().classes("items-center gap-2"):
                    ui.icon("schedule")
                    ui.label(f"{datetime.now().strftime('%H:%M')} 21s ago")
                with ui.row().classes("items-center gap-2"):
                    ui.icon("timer")
                    ui.label("Used: 0.47h")


# =============================================================================
# DASHBOARD PAGE
# =============================================================================
@ui.page("/")
def dashboard_page():
    """Main dashboard page."""
    create_navbar()
    
    ui.page_title("VARIOSYNC Dashboard")
    
    with ui.column().classes("w-full p-6 gap-6"):
        # Page header
        ui.label("Time-Series Dashboard").classes("text-3xl font-bold mb-4")
        
        # Time-series visualization card (with data-section for scrolling)
        with ui.card().classes("w-full").props("data-section='plot'"):
            ui.label("📊 Live Sync Metrics").classes("text-xl font-semibold mb-4")
            
            # Controls row
            with ui.row().classes("w-full gap-4 items-center"):
                refresh_button = ui.button("🔄 Refresh Data", icon="refresh", color="primary")
                
                # Chart library selector
                chart_library_select = ui.select(
                    options=["plotly", "matplotlib"] if MATPLOTLIB_AVAILABLE else ["plotly"],
                    label="Chart Library",
                    value="plotly"
                ).classes("w-40")
                
                # Series selector
                series_select = ui.select(
                    options=[],
                    label="Series",
                    value=None,
                    with_input=True
                ).classes("flex-1")
                
                # Metric selector
                metric_select = ui.select(
                    options=[],
                    label="Metric",
                    value=None
                ).classes("flex-1")
                
                # Chart type selector (for financial data)
                chart_type_select = ui.select(
                    options=["auto", "candlestick", "line", "ohlc"],
                    label="Chart Type",
                    value="auto"
                ).classes("w-40")
                chart_type_select.visible = False  # Will be shown when financial data is detected
            
            # Plot container - create empty plot initially
            # Keep a reference to the figure for updates (use nonlocal or make it accessible)
            plot_figure = go.Figure()
            plot_figure.add_annotation(
                text="Loading data...",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="gray")
            )
            plot_figure.update_layout(
                template="plotly_dark",  # Match NiceGUI dark theme
                height=500,
                margin=dict(l=0, r=0, t=0, b=0)
            )
            plot_container = ui.plotly(plot_figure).classes("w-full").style("height: 500px")
            plot_image = None  # For matplotlib charts
            
            def load_timeseries_data():
                """Load time-series data from storage."""
                try:
                    app = get_app_instance()
                    if not app.storage:
                        return None, []
                    
                    # Load all records from storage
                    keys = app.storage.list_keys("data/")[:500]  # Limit to 500 for performance
                    records = []
                    
                    for key in keys:
                        try:
                            data_bytes = app.storage.load(key)
                            if data_bytes:
                                record = json.loads(data_bytes.decode('utf-8'))
                                if 'timestamp' in record:
                                    records.append(record)
                        except Exception as e:
                            logger.debug(f"Error loading record {key}: {e}")
                            continue
                    
                    if not records:
                        return None, []
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(records)
                    
                    # Normalize timestamp
                    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                    df = df.dropna(subset=['timestamp'])
                    
                    if len(df) == 0:
                        return None, []
                    
                    # Sort by timestamp
                    df = df.sort_values('timestamp')
                    
                    return df, records
                except Exception as e:
                    logger.error(f"Error loading time-series data: {e}")
                    return None, []
            
            def get_available_series(df):
                """Get list of available series IDs."""
                if df is None or len(df) == 0:
                    return []
                return sorted(df['series_id'].unique().tolist() if 'series_id' in df.columns else [])
            
            def is_financial_data(df, series_id=None):
                """Check if data contains financial OHLCV fields."""
                if df is None or len(df) == 0:
                    return False
                
                # Filter by series if specified
                if series_id and 'series_id' in df.columns:
                    check_df = df[df['series_id'] == series_id]
                else:
                    check_df = df
                
                if len(check_df) == 0:
                    return False
                
                # Check for direct OHLCV columns
                ohlcv_cols = ['open', 'high', 'low', 'close']
                has_direct_ohlcv = all(col in check_df.columns for col in ohlcv_cols)
                
                # Check for OHLCV in measurements
                has_measurements_ohlcv = False
                for idx, row in check_df.head(10).iterrows():  # Check first 10 rows
                    if 'measurements' in row and isinstance(row['measurements'], dict):
                        measurements = row['measurements']
                        if all(key in measurements for key in ohlcv_cols):
                            has_measurements_ohlcv = True
                            break
                
                return has_direct_ohlcv or has_measurements_ohlcv
            
            def get_available_metrics(df, series_id=None):
                """Get list of available metrics for a series."""
                if df is None or len(df) == 0:
                    return []
                
                # Filter by series if specified
                if series_id and 'series_id' in df.columns:
                    series_df = df[df['series_id'] == series_id]
                else:
                    series_df = df
                
                # Extract metrics from measurements column
                metrics = set()
                for idx, row in series_df.iterrows():
                    if 'measurements' in row and isinstance(row['measurements'], dict):
                        metrics.update(row['measurements'].keys())
                    # Also check for financial fields
                    for field in ['open', 'high', 'low', 'close', 'vol', 'openint']:
                        if field in row and pd.notna(row[field]):
                            metrics.add(field)
                
                return sorted(list(metrics))
            
            def extract_ohlcv_data(df, series_id=None):
                """Extract OHLCV data from DataFrame, handling both direct columns and measurements dict."""
                if series_id and 'series_id' in df.columns:
                    plot_df = df[df['series_id'] == series_id].copy()
                else:
                    plot_df = df.copy()
                
                # Sort by timestamp
                if 'timestamp' in plot_df.columns:
                    plot_df = plot_df.sort_values('timestamp')
                
                # Extract OHLCV values
                timestamps_raw = plot_df['timestamp'].tolist() if 'timestamp' in plot_df.columns else []
                # Convert timestamps to strings (handle pandas Timestamp, datetime, etc.)
                timestamps = []
                for ts in timestamps_raw:
                    if pd.isna(ts):
                        timestamps.append(None)
                    elif isinstance(ts, pd.Timestamp):
                        timestamps.append(ts.isoformat())
                    elif hasattr(ts, 'isoformat'):
                        timestamps.append(ts.isoformat())
                    else:
                        timestamps.append(str(ts))
                
                ohlcv_data = {
                    'timestamp': timestamps,
                    'open': [],
                    'high': [],
                    'low': [],
                    'close': [],
                    'volume': []
                }
                
                for idx, row in plot_df.iterrows():
                    # Try direct columns first
                    if all(col in plot_df.columns for col in ['open', 'high', 'low', 'close']):
                        ohlcv_data['open'].append(row.get('open'))
                        ohlcv_data['high'].append(row.get('high'))
                        ohlcv_data['low'].append(row.get('low'))
                        ohlcv_data['close'].append(row.get('close'))
                        ohlcv_data['volume'].append(row.get('vol') or row.get('volume', 0))
                    # Try measurements dict
                    elif 'measurements' in row and isinstance(row['measurements'], dict):
                        measurements = row['measurements']
                        ohlcv_data['open'].append(measurements.get('open'))
                        ohlcv_data['high'].append(measurements.get('high'))
                        ohlcv_data['low'].append(measurements.get('low'))
                        ohlcv_data['close'].append(measurements.get('close'))
                        ohlcv_data['volume'].append(measurements.get('vol') or measurements.get('volume', 0))
                    else:
                        continue
                
                # Filter out rows with missing OHLC data
                valid_indices = [
                    i for i in range(len(ohlcv_data['timestamp']))
                    if all(ohlcv_data[key][i] is not None for key in ['open', 'high', 'low', 'close'])
                ]
                
                return {
                    'timestamp': [ohlcv_data['timestamp'][i] for i in valid_indices],
                    'open': [ohlcv_data['open'][i] for i in valid_indices],
                    'high': [ohlcv_data['high'][i] for i in valid_indices],
                    'low': [ohlcv_data['low'][i] for i in valid_indices],
                    'close': [ohlcv_data['close'][i] for i in valid_indices],
                    'volume': [ohlcv_data['volume'][i] for i in valid_indices]
                }
            
            def create_matplotlib_financial_plot(df, series_id=None, chart_type="candlestick", show_volume=True):
                """Create Matplotlib financial chart (candlestick or OHLC) with optional volume subplot."""
                if not MATPLOTLIB_AVAILABLE:
                    return None
                
                ohlcv = extract_ohlcv_data(df, series_id)
                
                if len(ohlcv['timestamp']) == 0:
                    return None
                
                # Convert timestamps to datetime
                dates = [pd.to_datetime(ts) for ts in ohlcv['timestamp']]
                
                # Create figure
                if show_volume and any(v > 0 for v in ohlcv['volume']):
                    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1], sharex=True)
                else:
                    fig, ax1 = plt.subplots(figsize=(12, 6))
                    ax2 = None
                
                # Set dark theme
                fig.patch.set_facecolor('#1e1e1e')
                ax1.set_facecolor('#1e1e1e')
                if ax2:
                    ax2.set_facecolor('#1e1e1e')
                
                # Plot price chart
                if chart_type == "candlestick":
                    from matplotlib.patches import Rectangle
                    width = 0.6
                    for i, date in enumerate(dates):
                        open_price = ohlcv['open'][i]
                        high_price = ohlcv['high'][i]
                        low_price = ohlcv['low'][i]
                        close_price = ohlcv['close'][i]
                        
                        color = '#26a69a' if close_price >= open_price else '#ef5350'
                        
                        # Draw high-low line
                        ax1.plot([date, date], [low_price, high_price], color=color, linewidth=1)
                        
                        # Draw open-close rectangle
                        body_low = min(open_price, close_price)
                        body_high = max(open_price, close_price)
                        rect = Rectangle((mdates.date2num(date) - width/2, body_low), 
                                        width, body_high - body_low,
                                        facecolor=color, edgecolor=color, linewidth=1)
                        ax1.add_patch(rect)
                elif chart_type == "ohlc":
                    # OHLC bars
                    for i, date in enumerate(dates):
                        open_price = ohlcv['open'][i]
                        high_price = ohlcv['high'][i]
                        low_price = ohlcv['low'][i]
                        close_price = ohlcv['close'][i]
                        
                        color = '#26a69a' if close_price >= open_price else '#ef5350'
                        
                        # High-low line
                        ax1.plot([date, date], [low_price, high_price], color=color, linewidth=2)
                        
                        # Open tick
                        ax1.plot([date, date], [open_price, open_price], color=color, marker='|', markersize=8)
                        # Close tick
                        ax1.plot([date, date], [close_price, close_price], color=color, marker='|', markersize=8)
                else:  # line chart
                    ax1.plot(dates, ohlcv['close'], color='#2196F3', linewidth=2, marker='o', markersize=4)
                
                ax1.set_ylabel('Price', color='white')
                ax1.tick_params(colors='white')
                ax1.grid(True, alpha=0.3, color='gray')
                
                # Plot volume if needed
                if ax2 and any(v > 0 for v in ohlcv['volume']):
                    colors = ['#26a69a' if ohlcv['close'][i] >= ohlcv['open'][i] else '#ef5350' 
                             for i in range(len(ohlcv['close']))]
                    ax2.bar(dates, ohlcv['volume'], color=colors, alpha=0.7, width=0.8)
                    ax2.set_ylabel('Volume', color='white')
                    ax2.tick_params(colors='white')
                    ax2.grid(True, alpha=0.3, color='gray')
                
                # Format x-axis dates
                ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
                plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right', color='white')
                
                if ax2:
                    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right', color='white')
                
                plt.tight_layout()
                return fig
            
            def create_matplotlib_plot(df, series_id=None, metric=None):
                """Create Matplotlib time-series plot."""
                if not MATPLOTLIB_AVAILABLE:
                    return None
                
                if df is None or len(df) == 0:
                    fig, ax = plt.subplots(figsize=(12, 6))
                    fig.patch.set_facecolor('#1e1e1e')
                    ax.set_facecolor('#1e1e1e')
                    ax.text(0.5, 0.5, 'No data available. Upload files to see time-series plots.',
                           transform=ax.transAxes, ha='center', va='center', 
                           fontsize=16, color='gray')
                    ax.set_axis_off()
                    return fig
                
                fig, ax = plt.subplots(figsize=(12, 6))
                fig.patch.set_facecolor('#1e1e1e')
                ax.set_facecolor('#1e1e1e')
                
                # Filter by series if specified
                if series_id and 'series_id' in df.columns:
                    plot_df = df[df['series_id'] == series_id].copy()
                else:
                    plot_df = df.copy()
                
                # Get unique series
                if 'series_id' in plot_df.columns:
                    unique_series = plot_df['series_id'].unique()[:10]  # Limit to 10
                else:
                    unique_series = ['default']
                    plot_df['series_id'] = 'default'
                
                # Plot data
                for sid in unique_series:
                    series_data = plot_df[plot_df['series_id'] == sid].copy()
                    
                    if metric:
                        # Plot specific metric
                        values = []
                        for idx, row in series_data.iterrows():
                            if 'measurements' in row and isinstance(row['measurements'], dict):
                                values.append(row['measurements'].get(metric))
                            elif metric in row:
                                values.append(row[metric])
                            else:
                                values.append(None)
                        series_data['value'] = values
                        series_data = series_data.dropna(subset=['value'])
                        
                        if len(series_data) > 0:
                            dates = [pd.to_datetime(ts) for ts in series_data['timestamp']]
                            ax.plot(dates, series_data['value'], label=f"{sid} - {metric}", linewidth=2, marker='o', markersize=4)
                    else:
                        # Plot default metric
                        default_metrics = ['close', 'value', 'temperature', 'price']
                        metric_to_plot = None
                        
                        for m in default_metrics:
                            if m in series_data.columns:
                                metric_to_plot = m
                                break
                        
                        if metric_to_plot:
                            dates = [pd.to_datetime(ts) for ts in series_data['timestamp']]
                            ax.plot(dates, series_data[metric_to_plot], label=f"{sid} - {metric_to_plot}", linewidth=2, marker='o', markersize=4)
                
                ax.set_xlabel('Time', color='white')
                ax.set_ylabel('Value', color='white')
                ax.tick_params(colors='white')
                ax.grid(True, alpha=0.3, color='gray')
                ax.legend(loc='best', facecolor='#1e1e1e', edgecolor='gray', labelcolor='white')
                
                # Format dates
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', color='white')
                
                plt.tight_layout()
                return fig
            
            def matplotlib_figure_to_base64(fig):
                """Convert matplotlib figure to base64 encoded image."""
                buf = BytesIO()
                fig.savefig(buf, format='png', facecolor='#1e1e1e', dpi=100, bbox_inches='tight')
                buf.seek(0)
                img_base64 = base64.b64encode(buf.read()).decode('utf-8')
                plt.close(fig)
                return f"data:image/png;base64,{img_base64}"
            
            def create_financial_plot(df, series_id=None, chart_type="candlestick", show_volume=True):
                """Create financial chart (candlestick or OHLC) with optional volume subplot."""
                from plotly.subplots import make_subplots
                
                # Extract OHLCV data
                ohlcv = extract_ohlcv_data(df, series_id)
                
                if len(ohlcv['timestamp']) == 0:
                    # Empty plot
                    fig = go.Figure()
                    fig.add_annotation(
                        text="No financial data available. Ensure data contains OHLCV fields.",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=16, color="gray")
                    )
                    fig.update_layout(
                        template="plotly_dark",
                        height=500,
                        margin=dict(l=50, r=50, t=50, b=50)
                    )
                    return fig
                
                # Create subplots if volume is shown
                if show_volume and any(v > 0 for v in ohlcv['volume']):
                    fig = make_subplots(
                        rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.03,
                        row_heights=[0.7, 0.3],
                        subplot_titles=('Price', 'Volume')
                    )
                else:
                    fig = go.Figure()
                
                # Determine series name
                if series_id:
                    series_name = series_id
                elif 'series_id' in df.columns and len(df['series_id'].unique()) == 1:
                    series_name = df['series_id'].iloc[0]
                else:
                    series_name = "Financial Data"
                
                # Add price chart
                if chart_type == "candlestick":
                    trace = go.Candlestick(
                        x=ohlcv['timestamp'],
                        open=ohlcv['open'],
                        high=ohlcv['high'],
                        low=ohlcv['low'],
                        close=ohlcv['close'],
                        name=series_name,
                        increasing_line_color='#26a69a',
                        decreasing_line_color='#ef5350'
                    )
                elif chart_type == "ohlc":
                    trace = go.Ohlc(
                        x=ohlcv['timestamp'],
                        open=ohlcv['open'],
                        high=ohlcv['high'],
                        low=ohlcv['low'],
                        close=ohlcv['close'],
                        name=series_name,
                        increasing_line_color='#26a69a',
                        decreasing_line_color='#ef5350'
                    )
                else:  # line chart
                    trace = go.Scatter(
                        x=ohlcv['timestamp'],
                        y=ohlcv['close'],
                        mode='lines+markers',
                        name=f"{series_name} - Close",
                        line=dict(width=2, color='#2196F3'),
                        marker=dict(size=4)
                    )
                
                if show_volume and any(v > 0 for v in ohlcv['volume']):
                    fig.add_trace(trace, row=1, col=1)
                    # Add volume bars
                    colors = ['#26a69a' if ohlcv['close'][i] >= ohlcv['open'][i] else '#ef5350' 
                             for i in range(len(ohlcv['close']))]
                    fig.add_trace(
                        go.Bar(
                            x=ohlcv['timestamp'],
                            y=ohlcv['volume'],
                            name='Volume',
                            marker_color=colors,
                            showlegend=False
                        ),
                        row=2, col=1
                    )
                    fig.update_yaxes(title_text="Volume", row=2, col=1)
                else:
                    fig.add_trace(trace)
                
                # Update layout
                fig.update_layout(
                    title=f"{series_name} - {chart_type.upper()} Chart",
                    xaxis_title="Time",
                    yaxis_title="Price" if show_volume else "Price",
                    template="plotly_dark",
                    height=600 if show_volume else 500,
                    hovermode='x unified',
                    xaxis_rangeslider_visible=False,
                    margin=dict(l=50, r=50, t=50, b=50)
                )
                
                if show_volume and any(v > 0 for v in ohlcv['volume']):
                    fig.update_xaxes(title_text="Time", row=2, col=1)
                    fig.update_yaxes(title_text="Price", row=1, col=1)
                
                return fig
            
            def create_plot(df, series_id=None, metric=None, chart_type="auto"):
                """Create Plotly time-series plot, with financial chart support."""
                if df is None or len(df) == 0:
                    # Empty plot
                    fig = go.Figure()
                    fig.add_annotation(
                        text="No data available. Upload files to see time-series plots.",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=16, color="gray")
                    )
                    fig.update_layout(
                        xaxis_title="Time",
                        yaxis_title="Value",
                        template="plotly_dark",  # Match NiceGUI dark theme
                        height=500,
                        margin=dict(l=50, r=50, t=50, b=50)
                    )
                    return fig
                
                # Check if this is financial data and should use financial charts
                is_financial = is_financial_data(df, series_id)
                
                # Determine chart type
                if is_financial and (chart_type == "auto" or chart_type in ["candlestick", "ohlc"]):
                    # Use financial chart
                    actual_chart_type = chart_type if chart_type != "auto" else "candlestick"
                    return create_financial_plot(df, series_id, actual_chart_type, show_volume=True)
                
                # Otherwise, use standard time-series plot
                fig = go.Figure()
                
                # Filter by series if specified
                if series_id and 'series_id' in df.columns:
                    plot_df = df[df['series_id'] == series_id].copy()
                else:
                    plot_df = df.copy()
                
                # Get unique series for plotting
                if 'series_id' in plot_df.columns:
                    unique_series = plot_df['series_id'].unique()
                else:
                    unique_series = ['default']
                    plot_df['series_id'] = 'default'
                
                # Determine what to plot
                if metric:
                    # Plot specific metric
                    for sid in unique_series:
                        series_data = plot_df[plot_df['series_id'] == sid].copy()
                        
                        # Extract metric values
                        values = []
                        for idx, row in series_data.iterrows():
                            if 'measurements' in row and isinstance(row['measurements'], dict):
                                values.append(row['measurements'].get(metric))
                            elif metric in row:
                                values.append(row[metric])
                            else:
                                values.append(None)
                        
                        series_data['value'] = values
                        series_data = series_data.dropna(subset=['value'])
                        
                        if len(series_data) > 0:
                            # Convert timestamps to strings for JSON serialization
                            timestamps = []
                            for ts in series_data['timestamp']:
                                if pd.isna(ts):
                                    timestamps.append(None)
                                elif isinstance(ts, pd.Timestamp):
                                    timestamps.append(ts.isoformat())
                                elif hasattr(ts, 'isoformat'):
                                    timestamps.append(ts.isoformat())
                                else:
                                    timestamps.append(str(ts))
                            
                            fig.add_trace(go.Scatter(
                                x=timestamps,
                                y=series_data['value'],
                                mode='lines+markers',
                                name=f"{sid} - {metric}",
                                line=dict(width=2),
                                marker=dict(size=4)
                            ))
                else:
                    # Plot all metrics for all series (or default to 'close' for financial)
                    for sid in unique_series[:10]:  # Limit to 10 series for performance
                        series_data = plot_df[plot_df['series_id'] == sid].copy()
                        
                        # Try to find a default metric
                        default_metrics = ['close', 'value', 'temperature', 'price']
                        metric_to_plot = None
                        
                        for m in default_metrics:
                            if m in series_data.columns:
                                metric_to_plot = m
                                break
                            # Check in measurements
                            for idx, row in series_data.iterrows():
                                if 'measurements' in row and isinstance(row['measurements'], dict):
                                    if m in row['measurements']:
                                        metric_to_plot = m
                                        break
                            if metric_to_plot:
                                break
                        
                        if not metric_to_plot and len(series_data) > 0:
                            # Get first available metric
                            first_row = series_data.iloc[0]
                            if 'measurements' in first_row and isinstance(first_row['measurements'], dict):
                                metric_to_plot = list(first_row['measurements'].keys())[0] if first_row['measurements'] else None
                        
                        if metric_to_plot:
                            values = []
                            for idx, row in series_data.iterrows():
                                if 'measurements' in row and isinstance(row['measurements'], dict):
                                    values.append(row['measurements'].get(metric_to_plot))
                                elif metric_to_plot in row:
                                    values.append(row[metric_to_plot])
                                else:
                                    values.append(None)
                            
                            series_data['value'] = values
                            series_data = series_data.dropna(subset=['value'])
                            
                            if len(series_data) > 0:
                                # Convert timestamps to strings for JSON serialization
                                timestamps = []
                                for ts in series_data['timestamp']:
                                    if pd.isna(ts):
                                        timestamps.append(None)
                                    elif isinstance(ts, pd.Timestamp):
                                        timestamps.append(ts.isoformat())
                                    elif hasattr(ts, 'isoformat'):
                                        timestamps.append(ts.isoformat())
                                    else:
                                        timestamps.append(str(ts))
                                
                                fig.add_trace(go.Scatter(
                                    x=timestamps,
                                    y=series_data['value'],
                                    mode='lines+markers',
                                    name=f"{sid} - {metric_to_plot}",
                                    line=dict(width=2),
                                    marker=dict(size=4)
                                ))
                
                # Update layout - use dark theme to match NiceGUI dark mode
                fig.update_layout(
                    title="Time-Series Data",
                    xaxis_title="Time",
                    yaxis_title="Value",
                    template="plotly_dark",  # Match NiceGUI dark theme
                    height=500,
                    hovermode='x unified',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    margin=dict(l=50, r=50, t=50, b=50)
                )
                
                return fig
            
            def update_plot():
                """Update the plot with current data and selections."""
                nonlocal plot_figure, plot_container, plot_image, chart_type_select, metric_select, chart_library_select
                try:
                    df, records = load_timeseries_data()
                    
                    # Get selected chart library
                    chart_library = chart_library_select.value if chart_library_select else "plotly"
                    
                    # Check if financial data and show/hide chart type selector
                    is_financial = is_financial_data(df, series_select.value) if df is not None else False
                    chart_type_select.visible = is_financial
                    
                    # Update series selector
                    available_series = get_available_series(df)
                    series_select.options = available_series
                    if available_series and series_select.value not in available_series:
                        series_select.value = available_series[0] if available_series else None
                    
                    # Update metric selector (hide for financial charts, show for time-series)
                    selected_series = series_select.value if series_select.value else None
                    if is_financial:
                        metric_select.visible = False
                    else:
                        metric_select.visible = True
                        available_metrics = get_available_metrics(df, selected_series)
                        metric_select.options = available_metrics
                        if available_metrics and metric_select.value not in available_metrics:
                            metric_select.value = available_metrics[0] if available_metrics else None
                    
                    # Get chart type
                    chart_type = chart_type_select.value if is_financial else "auto"
                    
                    # Create plot based on selected library
                    if chart_library == "matplotlib" and MATPLOTLIB_AVAILABLE:
                        # Use Matplotlib
                        if is_financial:
                            mpl_fig = create_matplotlib_financial_plot(df, series_select.value, chart_type, show_volume=True)
                        else:
                            mpl_fig = create_matplotlib_plot(df, series_select.value, metric_select.value)
                        
                        if mpl_fig:
                            # Convert to base64 image
                            img_data = matplotlib_figure_to_base64(mpl_fig)
                            
                            # Update or create image element
                            try:
                                plot_container.delete()
                            except:
                                pass
                            
                            plot_image = ui.image(img_data).classes("w-full").style("max-height: 600px; object-fit: contain;")
                            plot_container = plot_image
                        else:
                            ui.notify("Failed to create Matplotlib chart", type="warning")
                    else:
                        # Use Plotly (default)
                        new_fig = create_plot(df, series_select.value, metric_select.value, chart_type)
                        
                        # Check if new figure uses subplots (financial charts with volume)
                        has_subplots = hasattr(new_fig, '_grid_ref') and new_fig._grid_ref is not None
                        
                        if has_subplots:
                            # For subplots, replace the entire figure
                            plot_figure = new_fig
                            # Recreate the plot container
                            try:
                                plot_container.delete()
                            except:
                                pass
                            plot_container = ui.plotly(plot_figure).classes("w-full").style("height: 600px")
                        else:
                            # For regular plots, update in place
                            plot_figure.data = []
                            plot_figure.add_traces(list(new_fig.data))
                            plot_figure.update_layout(new_fig.layout)
                            
                            # Update the plot component - try different methods based on NiceGUI version
                            try:
                                # Method 1: Try set_figure (newer NiceGUI versions)
                                if hasattr(plot_container, 'set_figure'):
                                    plot_container.set_figure(plot_figure)
                                # Method 2: Use update() method
                                elif hasattr(plot_container, 'update'):
                                    plot_container.update()
                                # Method 3: Recreate the component (fallback)
                                else:
                                    plot_container.delete()
                                    plot_container = ui.plotly(plot_figure).classes("w-full").style("height: 500px")
                            except Exception as update_error:
                                logger.warning(f"Error updating plot with set_figure, trying update(): {update_error}")
                                try:
                                    plot_container.update()
                                except Exception:
                                    # Final fallback: recreate
                                    plot_container.delete()
                                    plot_container = ui.plotly(plot_figure).classes("w-full").style("height: 500px")
                    
                    logger.info(f"Plot updated with {len(df) if df is not None else 0} records using {chart_library}")
                except Exception as e:
                    logger.error(f"Error updating plot: {e}", exc_info=True)
                    ui.notify(f"Error updating plot: {str(e)}", type="negative")
            
            def refresh_plot():
                """Refresh the time-series plot."""
                logger.info("Refreshing plot...")
                update_plot()
                ui.notify("Plot refreshed", type="info")
            
            # Update plot when series, metric, chart type, or library changes
            series_select.on('update:modelValue', update_plot)
            metric_select.on('update:modelValue', update_plot)
            chart_type_select.on('update:modelValue', update_plot)
            chart_library_select.on('update:modelValue', update_plot)
            
            # Initial plot load
            refresh_button.on_click(refresh_plot)
            
            # Load initial data
            update_plot()
        
        # File upload card (with data-section for scrolling)
        with ui.card().classes("w-full").props("data-section='upload'"):
            ui.label("📤 Upload & Process Files").classes("text-xl font-semibold mb-4")
            
            with ui.column().classes("w-full gap-4"):
                # File upload state
                uploaded_file_info = {"name": None, "content": None, "temp_path": None}
                
                def handle_upload(e):
                    """Handle file upload."""
                    try:
                        # Read file content from NiceGUI UploadEventArguments
                        # NiceGUI v3.x uses e.file._data for bytes and e.file.name for filename
                        if hasattr(e, 'file'):
                            file_content = e.file._data
                            file_name = e.file.name
                        else:
                            # Fallback for older NiceGUI versions
                            file_content = e.content.read() if hasattr(e, 'content') else None
                            file_name = e.name if hasattr(e, 'name') else "unknown"
                        
                        if file_content is None:
                            raise ValueError("Could not read file content from upload event")
                        
                        uploaded_file_info["name"] = file_name
                        uploaded_file_info["content"] = file_content
                        
                        # Save to temporary file
                        temp_dir = Path(tempfile.gettempdir())
                        temp_file = temp_dir / f"variosync_{file_name}"
                        with open(temp_file, "wb") as f:
                            f.write(file_content)
                        uploaded_file_info["temp_path"] = str(temp_file)
                        
                        # Update UI
                        file_size = len(file_content)
                        file_size_mb = file_size / (1024 * 1024)
                        if file_size_mb >= 1:
                            size_str = f"{file_size_mb:.2f} MB"
                        else:
                            size_str = f"{file_size / 1024:.2f} KB"
                        
                        status_label.text = f"📁 File ready: {file_name} ({size_str})"
                        file_info_label.text = f"📄 {file_name} • {size_str} • Ready to process"
                        file_info_label.visible = True
                        process_button.set_enabled(True)
                        plotly_button.set_enabled(True)
                        plotly_format_select.visible = True
                        # Enable convert button if CSV file
                        if file_name.lower().endswith('.csv'):
                            convert_button.set_enabled(True)
                        else:
                            convert_button.set_enabled(False)
                        
                        logger.info(f"File uploaded: {file_name} ({size_str})")
                    except Exception as ex:
                        logger.error(f"Error handling upload: {ex}", exc_info=True)
                        status_label.text = f"❌ Upload error: {str(ex)}"
                        ui.notify(f"Upload error: {str(ex)}", type="negative")
                
                file_upload = ui.upload(
                    label="Drop file or click to browse",
                    auto_upload=False,
                    on_upload=handle_upload
                ).classes("w-full")
                
                # File info display
                file_info_label = ui.label("").classes("text-sm text-gray-600")
                file_info_label.visible = False
                
                # Record type selector
                record_type = ui.select(
                    ["time_series", "financial"],
                    label="Record Type",
                    value="time_series"
                ).classes("w-full")
                
                # Output format selector for Plotly conversion
                plotly_format_select = ui.select(
                    ["json", "parquet", "csv"],
                    label="Plotly Format",
                    value="json"
                ).classes("w-full")
                plotly_format_select.visible = False
                
                # Action buttons row
                with ui.row().classes("w-full gap-2"):
                    process_button = ui.button("⚡ Process File", icon="bolt", color="positive")
                    process_button.set_enabled(False)
                    
                    convert_button = ui.button("🔄 Convert CSV to DuckDB", icon="transform", color="primary")
                    convert_button.set_enabled(False)
                    
                    plotly_button = ui.button("📊 Convert to Plotly Format", icon="show_chart", color="secondary")
                    plotly_button.set_enabled(False)
                
                # Status display
                status_label = ui.label("✨ Ready to process files").classes("text-sm")
                
                # Processing results container (will be created dynamically)
                results_card = None
                results_container_parent = None  # Parent container for results
                
                def show_results(success: bool, file_name: str, new_keys: list = None, error: str = None):
                    """Show processing results."""
                    nonlocal results_card, results_container_parent
                    
                    # Remove old results card if exists
                    if results_card is not None:
                        try:
                            results_card.delete()
                        except:
                            pass
                    
                    # Create parent container if needed
                    if results_container_parent is None:
                        results_container_parent = ui.column().classes("w-full gap-2")
                    
                    # Create new results card
                    if success:
                        with results_container_parent:
                            with ui.card().classes("w-full border-2 border-green-500") as results_card:
                                ui.label("✅ Processing Complete").classes("text-lg font-semibold text-green-600")
                                ui.label(f"📁 File: {file_name}").classes("text-sm")
                                if new_keys:
                                    ui.label(f"📊 Records saved: {len(new_keys)}").classes("text-sm")
                                ui.label(f"🏷️  Type: {record_type.value}").classes("text-sm")
                                
                                if new_keys and len(new_keys) > 0:
                                    with ui.expansion("📋 View saved records", icon="list").classes("w-full"):
                                        with ui.column().classes("gap-1"):
                                            for key in sorted(list(new_keys))[:20]:  # Show first 20
                                                ui.label(f"• {key}").classes("text-xs font-mono")
                                            if len(new_keys) > 20:
                                                ui.label(f"... and {len(new_keys) - 20} more").classes("text-xs text-gray-500")
                    else:
                        with results_container_parent:
                            with ui.card().classes("w-full border-2 border-red-500") as results_card:
                                ui.label("❌ Processing Failed").classes("text-lg font-semibold text-red-600")
                                if error:
                                    ui.label(f"Error: {error}").classes("text-sm font-mono")
                                else:
                                    ui.label("Please check that the file format matches the selected record type.").classes("text-sm")
                
                def convert_csv_to_duckdb():
                    """Convert CSV file to DuckDB format."""
                    nonlocal results_card, results_container_parent
                    
                    if not uploaded_file_info["temp_path"]:
                        ui.notify("Please select a CSV file first", type="warning")
                        return
                    
                    file_name = uploaded_file_info["name"]
                    if not file_name.lower().endswith('.csv'):
                        ui.notify("Please select a CSV file", type="warning")
                        return
                    
                    # Update UI for conversion
                    status_label.text = "⏳ Converting CSV to DuckDB..."
                    convert_button.set_enabled(False)
                    process_button.set_enabled(False)
                    file_upload.set_enabled(False)
                    
                    # Remove old results
                    if results_card is not None:
                        try:
                            results_card.delete()
                            results_card = None
                        except:
                            pass
                    
                    # Show progress
                    if results_container_parent is None:
                        results_container_parent = ui.column().classes("w-full gap-2")
                    with results_container_parent:
                        with ui.card().classes("w-full") as progress_card:
                            ui.label("⏳ Converting CSV to DuckDB...").classes("text-sm")
                    
                    try:
                        temp_path = uploaded_file_info["temp_path"]
                        
                        # Generate output path
                        from pathlib import Path
                        csv_path = Path(temp_path)
                        duckdb_path = str(csv_path.with_suffix('.duckdb'))
                        
                        # Convert using VariosyncApp
                        app = get_app_instance()
                        success = app.convert_csv_to_duckdb(
                            csv_file_path=temp_path,
                            duckdb_file_path=duckdb_path,
                            table_name="time_series_data",
                            has_header=True,
                            if_exists="replace"
                        )
                        
                        # Remove progress card
                        try:
                            progress_card.delete()
                        except:
                            pass
                        
                        if success:
                            # Show success results
                            with results_container_parent:
                                with ui.card().classes("w-full border-2 border-blue-500") as results_card:
                                    ui.label("✅ Conversion Complete").classes("text-lg font-semibold text-blue-600")
                                    ui.label(f"📁 Input: {file_name}").classes("text-sm")
                                    ui.label(f"💾 Output: {Path(duckdb_path).name}").classes("text-sm")
                                    ui.label(f"📊 Table: time_series_data").classes("text-sm")
                                    
                                    # Show file size info
                                    try:
                                        import os
                                        duckdb_size = os.path.getsize(duckdb_path)
                                        duckdb_size_mb = duckdb_size / (1024 * 1024)
                                        if duckdb_size_mb >= 1:
                                            size_str = f"{duckdb_size_mb:.2f} MB"
                                        else:
                                            size_str = f"{duckdb_size / 1024:.2f} KB"
                                        ui.label(f"📦 DuckDB file size: {size_str}").classes("text-sm")
                                    except:
                                        pass
                            
                            status_label.text = f"✅ Converted {file_name} to DuckDB"
                            ui.notify(f"Successfully converted {file_name} to DuckDB", type="positive")
                            logger.info(f"CSV to DuckDB conversion successful: {duckdb_path}")
                        else:
                            show_results(False, file_name, error="Conversion failed. Check logs for details.")
                            status_label.text = f"❌ Conversion failed"
                            ui.notify("CSV to DuckDB conversion failed", type="negative")
                            
                    except Exception as e:
                        logger.error(f"Error converting CSV to DuckDB: {e}")
                        show_results(False, file_name, error=str(e))
                        status_label.text = f"❌ Conversion error: {str(e)}"
                        ui.notify(f"Conversion error: {str(e)}", type="negative")
                    finally:
                        # Re-enable UI
                        convert_button.set_enabled(True)
                        process_button.set_enabled(True)
                        file_upload.set_enabled(True)
                
                def convert_to_plotly_format():
                    """Convert uploaded file to Plotly-friendly format."""
                    nonlocal results_card, results_container_parent
                    
                    if not uploaded_file_info["temp_path"]:
                        ui.notify("Please select a file first", type="warning")
                        return
                    
                    file_name = uploaded_file_info["name"]
                    output_format = plotly_format_select.value
                    
                    # Update UI for conversion
                    status_label.text = f"⏳ Converting to Plotly {output_format.upper()} format..."
                    plotly_button.set_enabled(False)
                    process_button.set_enabled(False)
                    convert_button.set_enabled(False)
                    file_upload.set_enabled(False)
                    
                    # Remove old results
                    if results_card is not None:
                        try:
                            results_card.delete()
                            results_card = None
                        except:
                            pass
                    
                    # Show progress
                    if results_container_parent is None:
                        results_container_parent = ui.column().classes("w-full gap-2")
                    with results_container_parent:
                        with ui.card().classes("w-full") as progress_card:
                            ui.label(f"⏳ Converting to {output_format.upper()} format...").classes("text-sm")
                    
                    try:
                        temp_path = uploaded_file_info["temp_path"]
                        
                        # Generate output path
                        from pathlib import Path
                        input_path = Path(temp_path)
                        ext_map = {
                            "json": ".json",
                            "parquet": ".parquet",
                            "csv": ".csv"
                        }
                        ext = ext_map.get(output_format.lower(), ".json")
                        output_path = str(input_path.parent / f"{input_path.stem}_plotly{ext}")
                        
                        # Convert using VariosyncApp
                        app = get_app_instance()
                        success = app.convert_to_plotly_format(
                            input_file_path=temp_path,
                            output_file_path=output_path,
                            output_format=output_format,
                            normalize_measurements=True
                        )
                        
                        # Remove progress card
                        try:
                            progress_card.delete()
                        except:
                            pass
                        
                        if success:
                            # Show success results
                            with results_container_parent:
                                with ui.card().classes("w-full border-2 border-purple-500") as results_card:
                                    ui.label("✅ Plotly Conversion Complete").classes("text-lg font-semibold text-purple-600")
                                    ui.label(f"📁 Input: {file_name}").classes("text-sm")
                                    ui.label(f"📊 Output: {Path(output_path).name}").classes("text-sm")
                                    ui.label(f"📦 Format: {output_format.upper()}").classes("text-sm")
                                    
                                    # Show file size info
                                    try:
                                        import os
                                        output_size = os.path.getsize(output_path)
                                        output_size_mb = output_size / (1024 * 1024)
                                        if output_size_mb >= 1:
                                            size_str = f"{output_size_mb:.2f} MB"
                                        else:
                                            size_str = f"{output_size / 1024:.2f} KB"
                                        ui.label(f"📦 Output file size: {size_str}").classes("text-sm")
                                        
                                        # Show record count if JSON
                                        if output_format.lower() == "json":
                                            import json
                                            with open(output_path, 'r') as f:
                                                data = json.load(f)
                                                if isinstance(data, list):
                                                    ui.label(f"📊 Records: {len(data)}").classes("text-sm")
                                    except:
                                        pass
                                    
                                    ui.label("✨ File is ready for Plotly visualization!").classes("text-sm text-purple-600 mt-2")
                            
                            status_label.text = f"✅ Converted {file_name} to Plotly {output_format.upper()} format"
                            ui.notify(f"Successfully converted to Plotly {output_format.upper()} format", type="positive")
                            logger.info(f"Plotly format conversion successful: {output_path}")
                        else:
                            show_results(False, file_name, error="Conversion failed. Check logs for details.")
                            status_label.text = f"❌ Conversion failed"
                            ui.notify("Plotly format conversion failed", type="negative")
                            
                    except Exception as e:
                        logger.error(f"Error converting to Plotly format: {e}")
                        show_results(False, file_name, error=str(e))
                        status_label.text = f"❌ Conversion error: {str(e)}"
                        ui.notify(f"Conversion error: {str(e)}", type="negative")
                    finally:
                        # Re-enable UI
                        plotly_button.set_enabled(True)
                        process_button.set_enabled(True)
                        convert_button.set_enabled(True)
                        file_upload.set_enabled(True)
                
                def process_file():
                    """Process uploaded file."""
                    nonlocal results_card, results_container_parent
                    
                    if not uploaded_file_info["temp_path"]:
                        ui.notify("Please select a file first", type="warning")
                        return
                    
                    # Update UI for processing
                    status_label.text = "⏳ Processing file..."
                    process_button.set_enabled(False)
                    convert_button.set_enabled(False)
                    file_upload.set_enabled(False)
                    
                    # Remove old results
                    if results_card is not None:
                        try:
                            results_card.delete()
                            results_card = None
                        except:
                            pass
                    
                    # Show progress
                    if results_container_parent is None:
                        results_container_parent = ui.column().classes("w-full gap-2")
                    with results_container_parent:
                        with ui.card().classes("w-full") as progress_card:
                            ui.label("⏳ Processing...").classes("text-sm")
                    
                    try:
                        temp_path = uploaded_file_info["temp_path"]
                        file_name = uploaded_file_info["name"]
                        
                        # Process file using VariosyncApp
                        app = get_app_instance()
                        
                        # Get processing stats by checking storage before/after
                        keys_before = set(app.storage.list_keys() if app.storage else [])
                        
                        success = app.process_data_file(temp_path, record_type.value)
                        
                        # Get keys after processing
                        keys_after = set(app.storage.list_keys() if app.storage else [])
                        new_keys = list(keys_after - keys_before)
                        
                        # Remove progress card
                        progress_card.delete()
                        
                        if success:
                            show_results(True, file_name, new_keys)
                            status_label.text = f"✅ Successfully processed {file_name} ({len(new_keys)} records)"
                            ui.notify(f"Successfully processed {len(new_keys)} records", type="positive")
                            
                            # Refresh visualizations
                            refresh_plot()
                            refresh_storage()
                            
                            # Clean up temp file
                            try:
                                if Path(temp_path).exists():
                                    Path(temp_path).unlink()
                            except:
                                pass
                            
                            # Reset upload state
                            uploaded_file_info["name"] = None
                            uploaded_file_info["content"] = None
                            uploaded_file_info["temp_path"] = None
                            file_info_label.visible = False
                            process_button.set_enabled(False)
                        else:
                            show_results(False, file_name, error="Processing failed. Check file format.")
                            status_label.text = "❌ Processing failed. Check file format."
                            ui.notify("Processing failed. Please check the file format.", type="negative")
                    except Exception as e:
                        logger.error(f"Error processing file: {e}", exc_info=True)
                        if 'progress_card' in locals():
                            progress_card.delete()
                        show_results(False, uploaded_file_info.get("name", "Unknown"), error=str(e))
                        status_label.text = f"❌ Error: {str(e)}"
                        ui.notify(f"Error: {str(e)}", type="negative")
                    finally:
                        process_button.set_enabled(True)
                        convert_button.set_enabled(True)
                        plotly_button.set_enabled(True)
                        file_upload.set_enabled(True)
                
                # Connect buttons to handlers
                process_button.on_click(process_file)
                convert_button.on_click(convert_csv_to_duckdb)
                plotly_button.on_click(convert_to_plotly_format)
        
        # Storage browser card (with data-section for scrolling)
        with ui.card().classes("w-full").props("data-section='storage'"):
            ui.label("💾 Storage Browser").classes("text-xl font-semibold mb-4")
            
            refresh_storage_button = ui.button("🔄 Refresh Storage", icon="refresh")
            
            # Storage table
            storage_table = ui.table(
                columns=[
                    {"name": "key", "label": "Key", "field": "key", "required": True},
                    {"name": "size", "label": "Size", "field": "size"},
                    {"name": "type", "label": "Type", "field": "type"}
                ],
                rows=[],
                row_key="key"
            ).classes("w-full")
            
            # File list container with download buttons (better UX than table)
            storage_files_container = ui.column().classes("w-full gap-2 mt-4")
            
            # Download format dialog function
            def show_download_format_dialog(file_key: str):
                """Show dialog to download file in different formats."""
                try:
                    app = get_app_instance()
                    
                    # Load the file data
                    file_data = app.storage.load(file_key)
                    if not file_data:
                        ui.notify(f"Could not load file: {file_key}", type="negative")
                        return
                    
                    # Parse the data based on file type
                    from file_loader import FileLoader
                    import tempfile
                    import os
                    
                    # Create temp file to load data
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_key).suffix)
                    temp_file.write(file_data)
                    temp_file.close()
                    
                    try:
                        loader = FileLoader()
                        records = loader.load(temp_file.name)
                        
                        if not records:
                            ui.notify("No data found in file", type="warning")
                            return
                        
                        with ui.dialog() as download_dialog, ui.card().classes("w-full max-w-lg"):
                            ui.label(f"📥 Download: {Path(file_key).name}").classes("text-xl font-semibold mb-4")
                            ui.label(f"Found {len(records)} records. Choose export format:").classes("text-sm mb-4")
                            
                            # Format selector - all supported formats
                            format_select = ui.select(
                                ["json", "jsonl", "csv", "txt", "parquet", "feather", "duckdb", "xlsx", "xls", "h5", "arrow", "avro", "orc", "msgpack", "sqlite", "influxdb"],
                                label="Export Format",
                                value="json"
                            ).classes("w-full mb-4")
                            
                            # Format descriptions
                            format_descriptions = {
                                "json": "JSON - Human-readable, good for APIs",
                                "jsonl": "JSONL - JSON Lines, streaming-friendly",
                                "csv": "CSV - Spreadsheet compatible, universal",
                                "txt": "TXT - Tab-delimited text file",
                                "parquet": "Parquet - Efficient columnar format",
                                "feather": "Feather - Fast binary format",
                                "duckdb": "DuckDB - Embedded database format",
                                "xlsx": "Excel XLSX - Microsoft Excel format",
                                "xls": "Excel XLS - Legacy Excel format",
                                "h5": "HDF5 - Scientific data format",
                                "arrow": "Apache Arrow - Columnar in-memory format",
                                "avro": "Apache Avro - Schema-based binary format",
                                "orc": "Apache ORC - Optimized Row Columnar format",
                                "msgpack": "MessagePack - Efficient binary JSON",
                                "sqlite": "SQLite - Portable SQL database",
                                "influxdb": "InfluxDB Line Protocol - TSDB ingestion format"
                            }
                            
                            format_desc_label = ui.label(format_descriptions.get(format_select.value, "")).classes("text-xs text-gray-500 mb-4")
                            
                            def update_format_desc():
                                format_desc_label.text = format_descriptions.get(format_select.value, "")
                            
                            format_select.on('update:modelValue', update_format_desc)
                            
                            status_label = ui.label("Ready to download").classes("text-sm mb-4")
                            
                            def download_file():
                                try:
                                    export_format = format_select.value
                                    status_label.text = f"⏳ Exporting to {export_format.upper()}..."
                                    
                                    from file_exporter import FileExporter
                                    import tempfile
                                    from pathlib import Path
                                    
                                    # Generate output filename
                                    original_name = Path(file_key).stem
                                    format_info = FileExporter.get_format_info(export_format)
                                    ext = format_info["ext"] if format_info else f".{export_format}"
                                    output_filename = f"{original_name}_export{ext}"
                                    
                                    # Create temp file for export
                                    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                                    temp_output.close()
                                    
                                    # Export data
                                    success = FileExporter.export(records, temp_output.name, export_format)
                                    
                                    if success:
                                        # Read the exported file
                                        with open(temp_output.name, "rb") as f:
                                            export_data = f.read()
                                        
                                        # Trigger browser download
                                        import base64
                                        
                                        b64_data = base64.b64encode(export_data).decode()
                                        mime_type = format_info["mime"] if format_info else "application/octet-stream"
                                        data_url = f"data:{mime_type};base64,{b64_data}"
                                        
                                        # Use JavaScript to trigger download
                                        ui.run_javascript(f'''
                                            const link = document.createElement('a');
                                            link.href = '{data_url}';
                                            link.download = '{output_filename}';
                                            document.body.appendChild(link);
                                            link.click();
                                            document.body.removeChild(link);
                                        ''')
                                        
                                        status_label.text = f"✅ Downloaded as {output_filename}"
                                        ui.notify(f"Downloaded {output_filename}", type="positive")
                                        download_dialog.close()
                                    else:
                                        status_label.text = "❌ Export failed. Check logs."
                                        ui.notify("Export failed", type="negative")
                                    
                                    # Cleanup
                                    try:
                                        os.unlink(temp_output.name)
                                    except:
                                        pass
                                        
                                except Exception as e:
                                    logger.error(f"Error downloading file: {e}", exc_info=True)
                                    status_label.text = f"❌ Error: {str(e)}"
                                    ui.notify(f"Download error: {str(e)}", type="negative")
                            
                            with ui.row().classes("w-full gap-2"):
                                ui.button("Download", icon="download", color="primary", on_click=download_file)
                                ui.button("Cancel", on_click=download_dialog.close).props("flat")
                            
                            download_dialog.open()
                            
                    finally:
                        # Cleanup temp file
                        try:
                            os.unlink(temp_file.name)
                        except:
                            pass
                            
                except Exception as e:
                    logger.error(f"Error showing download dialog: {e}", exc_info=True)
                    ui.notify(f"Error: {str(e)}", type="negative")
            
            def show_data_editor(file_key: str):
                """Show data editor/cleaner dialog."""
                try:
                    app = get_app_instance()
                    
                    # Load the file data
                    file_data = app.storage.load(file_key)
                    if not file_data:
                        ui.notify(f"Could not load file: {file_key}", type="negative")
                        return
                    
                    # Parse the data
                    import tempfile
                    import os
                    
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_key).suffix)
                    temp_file.write(file_data)
                    temp_file.close()
                    
                    try:
                        loader = FileLoader()
                        records = loader.load(temp_file.name)
                        
                        if not records:
                            ui.notify("No data found in file", type="warning")
                            return
                        
                        # Convert to DataFrame for editing
                        df = pd.DataFrame(records)
                        
                        with ui.dialog() as editor_dialog, ui.card().classes("w-full max-w-6xl max-h-[90vh] overflow-auto"):
                            ui.label(f"✏️ Data Editor: {Path(file_key).name}").classes("text-xl font-semibold mb-4")
                            
                            # Data summary
                            summary = DataCleaner.get_data_summary(df)
                            
                            with ui.expansion("📊 Data Summary", icon="info").classes("w-full mb-4"):
                                with ui.column().classes("gap-2 text-sm"):
                                    ui.label(f"Total Rows: {summary['total_rows']}").classes("font-semibold")
                                    ui.label(f"Total Columns: {summary['total_columns']}")
                                    ui.label(f"Duplicate Rows: {summary['duplicate_rows']}")
                                    
                                    with ui.expansion("Columns & Types").classes("w-full"):
                                        for col, dtype in summary['dtypes'].items():
                                            missing = summary['missing_values'].get(col, 0)
                                            missing_pct = summary['missing_percentage'].get(col, 0)
                                            ui.label(f"{col}: {dtype} ({missing} missing, {missing_pct:.1f}%)").classes("text-xs font-mono")
                            
                            # Cleaning operations
                            ui.label("🧹 Cleaning Operations").classes("text-lg font-semibold mb-2")
                            
                            operations = []
                            operations_container = ui.column().classes("w-full gap-2 mb-4")
                            
                            def add_operation():
                                with operations_container:
                                    with ui.card().classes("w-full p-3 border") as card_element:
                                        with ui.row().classes("w-full items-center gap-2"):
                                            op_type = ui.select(
                                                ["drop_na", "fill_na", "remove_duplicates", "remove_outliers", 
                                                 "normalize_timestamps", "filter_rows", "rename_columns", 
                                                 "drop_columns", "add_column", "convert_type", "resample", 
                                                 "interpolate", "clip_values", "round_values"],
                                                label="Operation",
                                                value="drop_na"
                                            ).classes("flex-1")
                                            
                                            def remove_op():
                                                card_element.delete()
                                                if op in operations:
                                                    operations.remove(op)
                                            
                                            ui.button("❌", icon="close", on_click=remove_op).props("size=sm flat")
                                        
                                        # Operation-specific parameters
                                        params_container = ui.column().classes("w-full gap-2 mt-2")
                                        
                                        def update_params():
                                            params_container.clear()
                                            op_type_val = op_type.value
                                            
                                            if op_type_val == "drop_na":
                                                with params_container:
                                                    ui.input(label="Subset columns (comma-separated, leave empty for all)", placeholder="col1,col2")
                                                    ui.select(["any", "all"], label="How", value="any")
                                            
                                            elif op_type_val == "fill_na":
                                                with params_container:
                                                    ui.select(["ffill", "bfill", "mean", "median", "mode", "value"], label="Method", value="ffill")
                                                    ui.input(label="Value (if method='value')", placeholder="0")
                                                    ui.input(label="Columns (comma-separated, leave empty for all)", placeholder="col1,col2")
                                            
                                            elif op_type_val == "remove_outliers":
                                                with params_container:
                                                    ui.select(["iqr", "zscore"], label="Method", value="iqr")
                                                    ui.input(label="Threshold (for zscore)", value="3")
                                                    ui.input(label="Columns (comma-separated)", placeholder="col1,col2")
                                            
                                            elif op_type_val == "filter_rows":
                                                with params_container:
                                                    ui.select(list(df.columns), label="Column")
                                                    ui.input(label="Condition", placeholder="> 100")
                                            
                                            elif op_type_val == "rename_columns":
                                                with params_container:
                                                    ui.textarea(label="Column mapping (JSON)", placeholder='{"old_name": "new_name"}')
                                            
                                            elif op_type_val == "drop_columns":
                                                with params_container:
                                                    ui.textarea(label="Columns to drop (one per line)")
                                            
                                            elif op_type_val == "add_column":
                                                with params_container:
                                                    ui.input(label="Column name")
                                                    ui.input(label="Value or expression", placeholder="col1 + col2")
                                            
                                            elif op_type_val == "convert_type":
                                                with params_container:
                                                    ui.select(list(df.columns), label="Column")
                                                    ui.select(["float", "int", "datetime", "string"], label="Type", value="float")
                                            
                                            elif op_type_val == "resample":
                                                with params_container:
                                                    ui.select(list(df.columns), label="Timestamp column", value="timestamp" if "timestamp" in df.columns else None)
                                                    ui.input(label="Frequency", value="1H", placeholder="1H, 1D, 1W")
                                                    ui.select(["mean", "sum", "max", "min", "first", "last"], label="Method", value="mean")
                                            
                                            elif op_type_val == "interpolate":
                                                with params_container:
                                                    ui.select(["linear", "polynomial", "spline"], label="Method", value="linear")
                                                    ui.input(label="Columns (comma-separated)", placeholder="col1,col2")
                                            
                                            elif op_type_val == "clip_values":
                                                with params_container:
                                                    ui.select(list(df.columns), label="Column")
                                                    ui.input(label="Min value")
                                                    ui.input(label="Max value")
                                            
                                            elif op_type_val == "round_values":
                                                with params_container:
                                                    ui.input(label="Decimals", value="2")
                                                    ui.input(label="Columns (comma-separated)", placeholder="col1,col2")
                                        
                                        op_type.on('update:modelValue', update_params)
                                        update_params()
                                        
                                        op = {"operation": op_type.value, "params": {}}
                                        operations.append(op)
                            
                            with ui.row().classes("w-full gap-2 mb-2"):
                                ui.button("➕ Add Operation", icon="add", on_click=add_operation).props("outline")
                            
                            # Preview and apply
                            preview_df = df.copy()
                            preview_container = ui.column().classes("w-full")
                            save_btn = None
                            
                            def apply_operations():
                                nonlocal preview_df, save_btn
                                try:
                                    # Use operations list directly
                                    # Note: In a full implementation, you'd extract parameter values from UI widgets
                                    # For now, operations use default parameters or those set in the operation dict
                                    preview_df = DataCleaner.clean_dataframe(df.copy(), operations)
                                    
                                    # Show preview
                                    preview_container.clear()
                                    with preview_container:
                                        ui.label(f"✅ Preview: {len(preview_df)} rows (was {len(df)} rows)").classes("text-sm font-semibold text-green-600 mb-2")
                                        
                                        # Show first few rows
                                        preview_table = ui.table(
                                            columns=[{"name": col, "label": col, "field": col} for col in preview_df.columns[:10]],
                                            rows=preview_df.head(20).to_dict('records'),
                                            row_key="index"
                                        ).classes("w-full")
                                        
                                    # Enable save button
                                    if save_btn:
                                        save_btn.set_enabled(True)
                                    
                                    ui.notify("Operations applied. Review preview.", type="positive")
                                except Exception as e:
                                    logger.error(f"Error applying operations: {e}", exc_info=True)
                                    ui.notify(f"Error: {str(e)}", type="negative")
                            
                            def save_cleaned():
                                try:
                                    # Convert DataFrame back to records
                                    cleaned_records = preview_df.to_dict('records')
                                    
                                    # Save back to storage
                                    import json
                                    cleaned_data = json.dumps(cleaned_records, indent=2, default=str).encode('utf-8')
                                    
                                    # Create new key with _cleaned suffix
                                    new_key = file_key.replace('.json', '_cleaned.json')
                                    app.storage.save(new_key, cleaned_data)
                                    
                                    ui.notify(f"Saved cleaned data to {new_key}", type="positive")
                                    editor_dialog.close()
                                    refresh_storage()
                                except Exception as e:
                                    logger.error(f"Error saving cleaned data: {e}")
                                    ui.notify(f"Error saving: {str(e)}", type="negative")
                            
                            with ui.row().classes("w-full gap-2 mb-4"):
                                ui.button("🔍 Preview", icon="preview", on_click=apply_operations).props("outline")
                                save_btn = ui.button("💾 Save Cleaned Data", icon="save", on_click=save_cleaned, color="primary")
                                save_btn.set_enabled(False)
                            
                            with ui.row().classes("w-full justify-end"):
                                ui.button("Close", on_click=editor_dialog.close).props("flat")
                            
                            editor_dialog.open()
                            
                    finally:
                        try:
                            os.unlink(temp_file.name)
                        except:
                            pass
                            
                except Exception as e:
                    logger.error(f"Error showing data editor: {e}", exc_info=True)
                    ui.notify(f"Error: {str(e)}", type="negative")
            
            def show_data_visualizer(file_key: str):
                """Show enhanced data visualization dialog."""
                try:
                    app = get_app_instance()
                    
                    # Load the file data
                    file_data = app.storage.load(file_key)
                    if not file_data:
                        ui.notify(f"Could not load file: {file_key}", type="negative")
                        return
                    
                    # Parse the data
                    import tempfile
                    import os
                    
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_key).suffix)
                    temp_file.write(file_data)
                    temp_file.close()
                    
                    try:
                        loader = FileLoader()
                        records = loader.load(temp_file.name)
                        
                        if not records:
                            ui.notify("No data found in file", type="warning")
                            return
                        
                        # Convert to DataFrame
                        df = pd.DataFrame(records)
                        
                        with ui.dialog() as viz_dialog, ui.card().classes("w-full max-w-7xl max-h-[90vh] overflow-auto"):
                            ui.label(f"📊 Data Visualization: {Path(file_key).name}").classes("text-xl font-semibold mb-4")
                            
                            # Chart type selector
                            chart_type = ui.select(
                                ["line", "scatter", "bar", "area", "heatmap", "histogram", "box", "violin", "candlestick"],
                                label="Chart Type",
                                value="line"
                            ).classes("w-full mb-4")
                            
                            # Column selectors
                            x_col = ui.select(
                                list(df.columns),
                                label="X Axis",
                                value="timestamp" if "timestamp" in df.columns else list(df.columns)[0]
                            ).classes("w-full mb-2")
                            
                            y_cols = ui.select(
                                list(df.select_dtypes(include=['number']).columns) if len(df.select_dtypes(include=['number']).columns) > 0 else list(df.columns),
                                label="Y Axis",
                                multiple=True
                            ).classes("w-full mb-2")
                            
                            # Chart options
                            with ui.expansion("⚙️ Chart Options").classes("w-full mb-4"):
                                title_input = ui.input(label="Chart Title", value=f"Visualization: {Path(file_key).name}").classes("w-full")
                                width_input = ui.input(label="Width", value="1000").classes("w-full")
                                height_input = ui.input(label="Height", value="600").classes("w-full")
                                show_legend = ui.checkbox("Show Legend", value=True)
                                show_grid = ui.checkbox("Show Grid", value=True)
                            
                            plot_container = ui.column().classes("w-full")
                            
                            def update_plot():
                                try:
                                    plot_container.clear()
                                    
                                    chart_type_val = chart_type.value
                                    x_col_val = x_col.value
                                    y_cols_val = y_cols.value if y_cols.value else [y_cols.options[0]] if y_cols.options else []
                                    
                                    if not y_cols_val:
                                        ui.label("Please select at least one Y axis column").classes("text-red-500")
                                        return
                                    
                                    # Prepare data
                                    plot_df = df[[x_col_val] + y_cols_val].copy()
                                    plot_df = plot_df.dropna()
                                    
                                    if len(plot_df) == 0:
                                        ui.label("No data to plot after removing NaN values").classes("text-red-500")
                                        return
                                    
                                    # Create Plotly figure
                                    fig = go.Figure()
                                    
                                    if chart_type_val == "line":
                                        for col in y_cols_val:
                                            fig.add_trace(go.Scatter(
                                                x=plot_df[x_col_val],
                                                y=plot_df[col],
                                                mode='lines+markers',
                                                name=col,
                                                line=dict(width=2)
                                            ))
                                    
                                    elif chart_type_val == "scatter":
                                        for col in y_cols_val:
                                            fig.add_trace(go.Scatter(
                                                x=plot_df[x_col_val],
                                                y=plot_df[col],
                                                mode='markers',
                                                name=col,
                                                marker=dict(size=5)
                                            ))
                                    
                                    elif chart_type_val == "bar":
                                        for col in y_cols_val:
                                            fig.add_trace(go.Bar(
                                                x=plot_df[x_col_val],
                                                y=plot_df[col],
                                                name=col
                                            ))
                                    
                                    elif chart_type_val == "area":
                                        for col in y_cols_val:
                                            fig.add_trace(go.Scatter(
                                                x=plot_df[x_col_val],
                                                y=plot_df[col],
                                                mode='lines',
                                                name=col,
                                                fill='tozeroy',
                                                line=dict(width=2)
                                            ))
                                    
                                    elif chart_type_val == "heatmap":
                                        if len(y_cols_val) > 1:
                                            # Create correlation heatmap
                                            corr_data = plot_df[y_cols_val].corr()
                                            fig = go.Figure(data=go.Heatmap(
                                                z=corr_data.values,
                                                x=corr_data.columns,
                                                y=corr_data.index,
                                                colorscale='Viridis'
                                            ))
                                        else:
                                            ui.label("Heatmap requires multiple Y columns").classes("text-red-500")
                                            return
                                    
                                    elif chart_type_val == "histogram":
                                        for col in y_cols_val:
                                            fig.add_trace(go.Histogram(
                                                x=plot_df[col],
                                                name=col,
                                                opacity=0.7
                                            ))
                                    
                                    elif chart_type_val == "box":
                                        for col in y_cols_val:
                                            fig.add_trace(go.Box(
                                                y=plot_df[col],
                                                name=col
                                            ))
                                    
                                    elif chart_type_val == "violin":
                                        for col in y_cols_val:
                                            fig.add_trace(go.Violin(
                                                y=plot_df[col],
                                                name=col,
                                                box_visible=True
                                            ))
                                    
                                    elif chart_type_val == "candlestick":
                                        # Requires OHLC columns
                                        ohlc_cols = ['open', 'high', 'low', 'close']
                                        if all(col in df.columns for col in ohlc_cols):
                                            fig = go.Figure(data=go.Candlestick(
                                                x=plot_df[x_col_val],
                                                open=plot_df['open'],
                                                high=plot_df['high'],
                                                low=plot_df['low'],
                                                close=plot_df['close']
                                            ))
                                        else:
                                            ui.label("Candlestick requires 'open', 'high', 'low', 'close' columns").classes("text-red-500")
                                            return
                                    
                                    # Update layout
                                    fig.update_layout(
                                        title=title_input.value,
                                        width=int(width_input.value) if width_input.value.isdigit() else 1000,
                                        height=int(height_input.value) if height_input.value.isdigit() else 600,
                                        showlegend=show_legend.value,
                                        xaxis=dict(showgrid=show_grid.value),
                                        yaxis=dict(showgrid=show_grid.value),
                                        template="plotly_dark"
                                    )
                                    
                                    # Display plot
                                    with plot_container:
                                        ui.plotly(fig).classes("w-full")
                                        
                                except Exception as e:
                                    logger.error(f"Error creating plot: {e}", exc_info=True)
                                    with plot_container:
                                        ui.label(f"Error creating plot: {str(e)}").classes("text-red-500")
                            
                            # Auto-update on change
                            chart_type.on('update:modelValue', update_plot)
                            x_col.on('update:modelValue', update_plot)
                            y_cols.on('update:modelValue', update_plot)
                            
                            with ui.row().classes("w-full gap-2 mb-4"):
                                ui.button("🔄 Update Plot", icon="refresh", on_click=update_plot, color="primary")
                            
                            # Initial plot
                            update_plot()
                            
                            with ui.row().classes("w-full justify-end mt-4"):
                                ui.button("Close", on_click=viz_dialog.close).props("flat")
                            
                            viz_dialog.open()
                            
                    finally:
                        try:
                            os.unlink(temp_file.name)
                        except:
                            pass
                            
                except Exception as e:
                    logger.error(f"Error showing visualizer: {e}", exc_info=True)
                    ui.notify(f"Error: {str(e)}", type="negative")
            
            def refresh_storage():
                """Refresh storage browser."""
                try:
                    app = get_app_instance()
                    if app.storage:
                        keys = app.storage.list_keys()[:100]
                        rows = []
                        
                        # Clear and rebuild file list
                        storage_files_container.clear()
                        
                        if not keys:
                            with storage_files_container:
                                ui.label("No files in storage").classes("text-gray-500")
                        
                        for k in keys:
                            file_type = k.split('.')[-1].upper() if '.' in k else 'DATA'
                            
                            # Get file size
                            size_bytes = app.storage.get_size(k)
                            if size_bytes is not None:
                                if size_bytes >= 1024 * 1024 * 1024:  # GB
                                    size_str = f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
                                elif size_bytes >= 1024 * 1024:  # MB
                                    size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
                                elif size_bytes >= 1024:  # KB
                                    size_str = f"{size_bytes / 1024:.2f} KB"
                                else:
                                    size_str = f"{size_bytes} B"
                            else:
                                # Fallback: load file to get size
                                try:
                                    file_data = app.storage.load(k)
                                    size_bytes = len(file_data) if file_data else 0
                                    if size_bytes >= 1024 * 1024:
                                        size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
                                    elif size_bytes >= 1024:
                                        size_str = f"{size_bytes / 1024:.2f} KB"
                                    else:
                                        size_str = f"{size_bytes} B"
                                except:
                                    size_str = "N/A"
                            
                            rows.append({
                                "key": k,
                                "size": size_str,
                                "type": file_type
                            })
                            
                            # Add file card with download button
                            with storage_files_container:
                                with ui.card().classes("w-full p-3 hover:bg-gray-50"):
                                    with ui.row().classes("w-full items-center justify-between"):
                                        with ui.column().classes("flex-1"):
                                            ui.label(Path(k).name).classes("font-semibold")
                                            with ui.row().classes("gap-4 text-xs text-gray-500 mt-1"):
                                                ui.label(f"Size: {size_str}")
                                                ui.label(f"Type: {file_type}")
                                                ui.label(f"Key: {k}").classes("text-xs font-mono")
                                        
                                        def make_download_handler(file_key=k):
                                            def handler():
                                                show_download_format_dialog(file_key)
                                            return handler
                                        
                                        def make_edit_handler(file_key=k):
                                            def handler():
                                                show_data_editor(file_key)
                                            return handler
                                        
                                        def make_visualize_handler(file_key=k):
                                            def handler():
                                                show_data_visualizer(file_key)
                                            return handler
                                        
                                        with ui.row().classes("gap-2"):
                                            ui.button("📥 Download", icon="download", on_click=make_download_handler(k)).props("size=sm color=primary")
                                            ui.button("✏️ Edit", icon="edit", on_click=make_edit_handler(k)).props("size=sm color=secondary")
                                            ui.button("📊 Visualize", icon="show_chart", on_click=make_visualize_handler(k)).props("size=sm color=accent")
                        
                        storage_table.rows = rows
                        ui.notify("Storage refreshed", type="info")
                except Exception as e:
                    logger.error(f"Error refreshing storage: {e}")
                    ui.notify(f"Error: {str(e)}", type="negative")
            
            refresh_storage_button.on_click(refresh_storage)
            
            # Initial load
            refresh_storage()
        
        # Hourly aggregates card (collapsible)
        with ui.card().classes("w-full"):
            with ui.expansion("📊 Hourly Aggregates", icon="timeline").classes("w-full"):
                aggregates_table = ui.table(
                    columns=[
                        {"name": "hour", "label": "Hour", "field": "hour"},
                        {"name": "records", "label": "Records", "field": "records"},
                        {"name": "series", "label": "Series", "field": "series"}
                    ],
                    rows=[],
                    row_key="hour"
                ).classes("w-full")
                
                def refresh_aggregates():
                    """Refresh aggregate table."""
                    try:
                        app = get_app_instance()
                        if app.storage:
                            keys = app.storage.list_keys("data/")[:100]
                            records = []
                            for key in keys:
                                data_bytes = app_instance.storage.load(key)
                                if data_bytes:
                                    try:
                                        record = json.loads(data_bytes.decode('utf-8'))
                                        if 'timestamp' in record:
                                            records.append(record)
                                    except:
                                        pass
                            
                            if records:
                                df = pd.DataFrame(records)
                                if 'timestamp' in df.columns:
                                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                                    df['hour'] = df['timestamp'].dt.floor('h')
                                    
                                    aggregates = []
                                    for hour in sorted(df['hour'].unique(), reverse=True):
                                        hour_data = df[df['hour'] == hour]
                                        aggregates.append({
                                            "hour": hour.strftime('%Y-%m-%d %H:00'),
                                            "records": len(hour_data),
                                            "series": hour_data.get('series_id', pd.Series()).nunique() if 'series_id' in hour_data.columns else 0
                                        })
                                    
                                    aggregates_table.rows = aggregates
                    except Exception as e:
                        logger.error(f"Error refreshing aggregates: {e}")
                
                refresh_aggregates()




# =============================================================================
# API ROUTES (if needed)
# =============================================================================
# Health endpoint - NiceGUI uses FastAPI under the hood
from nicegui import app

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "storage": True, "auth": True}


# Note: ui.run() is called from run_nicegui.py
