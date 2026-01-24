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

# Helper function to render HTML with scripts
def render_html_with_scripts(html_content: str, container_id: str = None):
    """Render HTML content that may contain script tags.
    Separates scripts and uses ui.add_body_html() for scripts, ui.html() for content.
    """
    import re
    
    # Extract script tags
    script_pattern = r'<script[^>]*>.*?</script>'
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
    """Main dashboard page."""
    create_navbar()
    
    # Get shared state instance
    state = get_state()
    
    ui.page_title("VARIOSYNC Dashboard")
    
    # Add cache-busting meta tag for Safari
    ui.add_head_html('<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">')
    ui.add_head_html('<meta http-equiv="Pragma" content="no-cache">')
    ui.add_head_html('<meta http-equiv="Expires" content="0">')
    
    # Remove default padding and add padding-top to account for fixed header
    client.content.classes(remove='q-pa-md')
    client.content.style('padding-top: 80px')

    # Add CSS for resizable split pane layout
    ui.add_head_html('''
    <style>
        /* Convert the main column into a resizable split layout */
        .split-layout {
            display: grid !important;
            grid-template-rows: 1fr 8px 1fr;
            height: calc(100vh - 100px) !important;
            gap: 0 !important;
            overflow: hidden !important;
            padding: 8px !important;
        }
        .split-layout > .q-card[data-section="plot"] {
            overflow: hidden;
            min-height: 0;
            display: flex;
            flex-direction: column;
        }
        /* Plotly container styling */
        .q-card[data-section="plot"] .js-plotly-plot,
        .q-card[data-section="plot"] .plotly,
        .q-card[data-section="plot"] .plot-container {
            width: 100% !important;
            min-height: 250px !important;
        }
        .q-card[data-section="plot"] nicegui-plotly,
        .q-card[data-section="plot"] .nicegui-plotly {
            display: block;
            width: 100%;
            min-height: 300px;
            height: auto;
        }
        .split-layout > .resize-handle {
            background: linear-gradient(to right, transparent 35%, #3b82f6 35%, #3b82f6 65%, transparent 65%);
            cursor: ns-resize;
            display: flex;
            align-items: center;
            justify-content: center;
            user-select: none;
        }
        .split-layout > .resize-handle:hover {
            background: linear-gradient(to right, transparent 25%, #1e40af 25%, #1e40af 75%, transparent 75%);
        }
        .split-layout > .resize-handle::after {
            content: "";
            width: 50px;
            height: 4px;
            background: rgba(255,255,255,0.4);
            border-radius: 2px;
        }
        .split-layout > .bottom-wrapper {
            overflow: auto;
            min-height: 0;
        }
    </style>
    ''')

    # Add JavaScript for dynamic resize handling
    ui.add_body_html('''
    <script>
    (function() {
        let initialized = false;

        function initSplitPane() {
            if (initialized) return;

            const container = document.querySelector('.split-layout');
            if (!container) {
                setTimeout(initSplitPane, 200);
                return;
            }

            // Find the plot card and bottom content
            const plotCard = container.querySelector('[data-section="plot"]');
            const uploadCard = container.querySelector('[data-section="upload"]');
            const storageCard = container.querySelector('[data-section="storage"]');

            if (!plotCard || !uploadCard) {
                setTimeout(initSplitPane, 200);
                return;
            }

            // Create resize handle if it doesn't exist
            let handle = container.querySelector('.resize-handle');
            if (!handle) {
                handle = document.createElement('div');
                handle.className = 'resize-handle';
                plotCard.insertAdjacentElement('afterend', handle);
            }

            // Create bottom wrapper and move cards into it
            let bottomWrapper = container.querySelector('.bottom-wrapper');
            if (!bottomWrapper) {
                bottomWrapper = document.createElement('div');
                bottomWrapper.className = 'bottom-wrapper';
                handle.insertAdjacentElement('afterend', bottomWrapper);

                // Move upload and storage cards into bottom wrapper
                if (uploadCard) bottomWrapper.appendChild(uploadCard);
                if (storageCard) bottomWrapper.appendChild(storageCard);
            }

            initialized = true;

            // Resize handling
            let isDragging = false;

            handle.addEventListener('mousedown', (e) => {
                isDragging = true;
                document.body.style.cursor = 'ns-resize';
                document.body.style.userSelect = 'none';
                e.preventDefault();
            });

            document.addEventListener('mousemove', (e) => {
                if (!isDragging) return;

                const rect = container.getBoundingClientRect();
                const containerHeight = rect.height - 8;
                let topHeight = e.clientY - rect.top;

                topHeight = Math.max(150, Math.min(topHeight, containerHeight - 150));
                const bottomHeight = containerHeight - topHeight;

                container.style.gridTemplateRows = topHeight + 'px 8px ' + bottomHeight + 'px';
                window.dispatchEvent(new Event('resize'));
            });

            document.addEventListener('mouseup', () => {
                if (isDragging) {
                    isDragging = false;
                    document.body.style.cursor = '';
                    document.body.style.userSelect = '';
                    window.dispatchEvent(new Event('resize'));
                }
            });
        }

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initSplitPane);
        } else {
            setTimeout(initSplitPane, 100);
        }
    })();
    </script>
    ''')

    with ui.column().classes("w-full p-4 split-layout"):
        # Page header
        ui.label("Time-Series Dashboard").classes("text-3xl font-bold mb-4")
        
        # Time-series visualization card (with data-section for scrolling)
        with ui.card().classes("w-full").props("data-section='plot'"):
            ui.label("📊 Live Sync Metrics").classes("text-xl font-semibold mb-4")
            
            # Controls row
            with ui.row().classes("w-full gap-4 items-center"):
                refresh_button = ui.button("🔄 Refresh Data", icon="refresh", color="primary")
                
                # Chart library selector - build options dynamically
                # Re-import availability flags to ensure they're current and in scope
                try:
                    from nicegui_app import ALTAIR_AVAILABLE as ALT_AVAIL, HIGHCHARTS_AVAILABLE as HC_AVAIL, ECHARTS_AVAILABLE as EC_AVAIL
                except ImportError:
                    ALT_AVAIL = False
                    HC_AVAIL = False
                    EC_AVAIL = False
                
                # Build options list
                chart_library_options = ["plotly"]
                if MATPLOTLIB_AVAILABLE:
                    chart_library_options.append("matplotlib")
                if ALT_AVAIL:
                    chart_library_options.append("altair")
                if HC_AVAIL:
                    chart_library_options.append("highcharts")
                if EC_AVAIL:
                    chart_library_options.append("echarts")
                
                # Debug logging - force output to stdout
                logger.info(f"Chart library options: {chart_library_options}")
                logger.info(f"Availability flags: Altair={ALT_AVAIL}, Highcharts={HC_AVAIL}, ECharts={EC_AVAIL}")
                print(f"[DEBUG] Chart library options: {chart_library_options}", flush=True)
                print(f"[DEBUG] Availability flags: Altair={ALT_AVAIL}, Highcharts={HC_AVAIL}, ECharts={EC_AVAIL}", flush=True)
                print(f"[DEBUG] Number of options: {len(chart_library_options)}", flush=True)
                
                # Create select with explicit options list and unique ID for reliable access
                chart_library_select = ui.select(
                    options=chart_library_options,
                    label="Chart Library",
                    value="plotly"
                ).classes("w-40").props('id="chart-library-select"')
                
                # Verify what was set
                print(f"[DEBUG] Select element created with options: {chart_library_options}", flush=True)
                
                # Force update options after a short delay to ensure DOM is ready
                # This works around browser caching and rendering timing issues
                def update_select_options():
                    try:
                        chart_library_select.options = chart_library_options
                        chart_library_select.update()
                        print(f"[DEBUG] Forced update of select options: {chart_library_options}", flush=True)
                    except Exception as e:
                        logger.warning(f"Error updating select options: {e}")
                
                # Update immediately and after DOM is ready
                # The ui.timer() calls handle the updates reliably without needing JavaScript fallback
                ui.timer(0.2, update_select_options, once=True)
                ui.timer(1.0, update_select_options, once=True)
                
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
            
            # Store UI components in shared state
            state.set_component("dashboard.chart_library_select", chart_library_select)
            state.set_component("dashboard.series_select", series_select)
            state.set_component("dashboard.metric_select", metric_select)
            state.set_component("dashboard.chart_type_select", chart_type_select)
            
            # Plot container - create empty plot initially
            plot_figure = go.Figure()
            plot_figure.add_annotation(
                text="Loading data...",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="gray")
            )
            plot_figure.update_layout(
                template="plotly_dark",  # Match NiceGUI dark theme
                autosize=True,
                margin=dict(l=40, r=20, t=20, b=40)
            )
            plot_container = ui.plotly(plot_figure).classes("w-full").style("min-height: 350px; height: auto;")
            plot_image = None  # For matplotlib charts
            
            # Store plot components in state
            state.set_component("dashboard.plot_container", plot_container)
            state.set_state("dashboard.plot_figure", plot_figure)
            state.set_state("dashboard.plot_image", plot_image)
            
            def update_plot():
                """Update the plot with current data and selections."""
                # Get components from shared state
                chart_library_select = state.get_component("dashboard.chart_library_select")
                series_select = state.get_component("dashboard.series_select")
                metric_select = state.get_component("dashboard.metric_select")
                chart_type_select = state.get_component("dashboard.chart_type_select")
                plot_container = state.get_component("dashboard.plot_container")
                plot_figure = state.get_state("dashboard.plot_figure")
                plot_image = state.get_state("dashboard.plot_image")
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
                            # Update state
                            state.set_component("dashboard.plot_container", plot_container)
                            state.set_state("dashboard.plot_image", plot_image)
                        else:
                            ui.notify("Failed to create Matplotlib chart", type="warning")
                    elif chart_library == "altair" and ALTAIR_AVAILABLE and create_altair_plot_wrapper:
                        # Use Altair
                        try:
                            logger.debug(f"Creating Altair chart: series={series_select.value}, metric={metric_select.value}, chart_type={chart_type}")
                            altair_chart = create_altair_plot_wrapper(df, series_select.value, metric_select.value, chart_type)
                            if altair_chart:
                                html_content = altair_chart_to_html(altair_chart)
                                try:
                                    plot_container.delete()
                                except:
                                    pass
                                plot_container = render_html_with_scripts(html_content)
                                state.set_component("dashboard.plot_container", plot_container)
                                logger.info(f"Successfully created Altair chart")
                            else:
                                logger.warning("Failed to create Altair chart: chart is None")
                                ui.notify("Failed to create Altair chart", type="warning")
                        except Exception as e:
                            logger.error(f"Error creating Altair chart: {e}", exc_info=True)
                            ui.notify(f"Altair chart error: {str(e)}", type="negative")
                    elif chart_library == "highcharts" and HIGHCHARTS_AVAILABLE and create_highcharts_plot_wrapper:
                        # Use Highcharts
                        try:
                            logger.debug(f"Creating Highcharts chart: series={series_select.value}, metric={metric_select.value}, chart_type={chart_type}")
                            hc_config = create_highcharts_plot_wrapper(df, series_select.value, metric_select.value, chart_type)
                            if hc_config:
                                html_content = highcharts_config_to_html(hc_config, container_id="highcharts-dashboard")
                                try:
                                    plot_container.delete()
                                except:
                                    pass
                                plot_container = render_html_with_scripts(html_content)
                                state.set_component("dashboard.plot_container", plot_container)
                                logger.info(f"Successfully created Highcharts chart")
                            else:
                                logger.warning("Failed to create Highcharts chart: config is None")
                                ui.notify("Failed to create Highcharts chart", type="warning")
                        except Exception as e:
                            logger.error(f"Error creating Highcharts chart: {e}", exc_info=True)
                            ui.notify(f"Highcharts chart error: {str(e)}", type="negative")
                    elif chart_library == "echarts" and ECHARTS_AVAILABLE and create_echarts_plot_wrapper:
                        # Use ECharts
                        try:
                            logger.debug(f"Creating ECharts chart: series={series_select.value}, metric={metric_select.value}, chart_type={chart_type}")
                            echarts_config = create_echarts_plot_wrapper(df, series_select.value, metric_select.value, chart_type)
                            if echarts_config:
                                html_content = echarts_config_to_html(echarts_config, container_id="echarts-dashboard")
                                try:
                                    plot_container.delete()
                                except:
                                    pass
                                plot_container = render_html_with_scripts(html_content)
                                state.set_component("dashboard.plot_container", plot_container)
                                logger.info(f"Successfully created ECharts chart")
                            else:
                                logger.warning("Failed to create ECharts chart: config is None")
                                ui.notify("Failed to create ECharts chart", type="warning")
                        except Exception as e:
                            logger.error(f"Error creating ECharts chart: {e}", exc_info=True)
                            ui.notify(f"ECharts chart error: {str(e)}", type="negative")
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
                            plot_container = ui.plotly(plot_figure).classes("w-full").style("min-height: 350px; height: auto;")
                            # Update state
                            state.set_component("dashboard.plot_container", plot_container)
                            state.set_state("dashboard.plot_figure", plot_figure)
                        else:
                            # For regular plots, update in place
                            plot_figure.data = []
                            plot_figure.add_traces(list(new_fig.data))
                            plot_figure.update_layout(new_fig.layout)
                            # Update state
                            state.set_state("dashboard.plot_figure", plot_figure)
                            
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
                                    plot_container = ui.plotly(plot_figure).classes("w-full").style("min-height: 350px; height: auto;")
                                    state.set_component("dashboard.plot_container", plot_container)
                            except Exception as update_error:
                                logger.warning(f"Error updating plot with set_figure, trying update(): {update_error}")
                                try:
                                    plot_container.update()
                                except Exception:
                                    # Final fallback: recreate
                                    plot_container.delete()
                                    plot_container = ui.plotly(plot_figure).classes("w-full").style("min-height: 350px; height: auto;")
                                    state.set_component("dashboard.plot_container", plot_container)
                    
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
                        
                        # Show format selector when file is uploaded
                        format_selector.visible = True
                        
                        # Auto-detect and set format if possible
                        detected_format = loader.detect_format(file_name)
                        if detected_format:
                            # Find matching option in format_selector
                            for i, opt in enumerate(format_options):
                                if opt == detected_format:
                                    format_selector.value = opt
                                    break
                        
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
                
                # Format selector (optional, for manual override)
                from file_loader import FileLoader
                loader = FileLoader()
                supported_formats = loader.get_supported_formats()
                format_options = ["Auto-detect"] + sorted(supported_formats)
                
                format_selector = ui.select(
                    format_options,
                    label="File Format (optional)",
                    value="Auto-detect"
                ).classes("w-full")
                format_selector.visible = False  # Hidden by default, shown when needed
                
                file_upload = ui.upload(
                    label=f"Drop file or click to browse (Supports: {len(supported_formats)} formats)",
                    auto_upload=False,
                    on_upload=handle_upload
                ).classes("w-full")
                
                # Show supported formats hint
                formats_list = sorted(supported_formats)
                formats_preview = ', '.join(formats_list[:8])
                formats_hint = ui.label(
                    f"📋 Supported formats ({len(supported_formats)}): {formats_preview}... (click to see all)"
                ).classes("text-xs text-gray-500 mt-1 cursor-pointer")
                
                # Expandable formats list
                formats_expanded = False
                def toggle_formats():
                    nonlocal formats_expanded
                    formats_expanded = not formats_expanded
                    if formats_expanded:
                        formats_hint.text = f"📋 Supported formats ({len(supported_formats)}): {', '.join(formats_list)}"
                    else:
                        formats_hint.text = f"📋 Supported formats ({len(supported_formats)}): {formats_preview}... (click to see all)"
                
                formats_hint.on('click', toggle_formats)
                
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
                        
                        # Get format if manually specified
                        file_format = None
                        if format_selector.value != "Auto-detect":
                            file_format = format_selector.value
                        
                        # Get processing stats by checking storage before/after
                        keys_before = set(app.storage.list_keys() if app.storage else [])
                        
                        success = app.process_data_file(temp_path, record_type.value, file_format=file_format)
                        
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
                            
                            # Format selector - get all supported formats dynamically
                            from file_exporter import FileExporter
                            exporter = FileExporter()
                            all_formats = exporter.get_supported_formats()
                            
                            format_select = ui.select(
                                all_formats,
                                label="Export Format",
                                value="json"
                            ).classes("w-full mb-4")
                            
                            # Format descriptions - comprehensive list
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
                                "influxdb": "InfluxDB Line Protocol - TSDB ingestion format",
                                "protobuf": "Protocol Buffers - Efficient binary serialization",
                                "opentsdb": "OpenTSDB - Time-series database format",
                                "prometheus": "Prometheus Remote Write - Monitoring format",
                                "gzip": "Gzip - Compressed format (specify base_format)",
                                "bzip2": "Bzip2 - Compressed format (specify base_format)",
                                "zstandard": "Zstandard - Modern compression (specify base_format)",
                                "netcdf": "NetCDF - Scientific data format",
                                "zarr": "Zarr - Chunked compressed arrays",
                                "fits": "FITS - Astronomy format",
                                "tsfile": "TsFile - Apache IoTDB format",
                                "tdengine": "TDengine - High-performance TSDB format",
                                "victoriametrics": "VictoriaMetrics - Prometheus-compatible format"
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
                                    
                                    # Handle compression formats that need base_format
                                    export_kwargs = {}
                                    if export_format in ["gzip", "bzip2", "zstandard"]:
                                        # For compression formats, default to JSON as base
                                        export_kwargs["base_format"] = "json"
                                    
                                    # Export data
                                    success = FileExporter.export(records, temp_output.name, export_format, **export_kwargs)
                                    
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
                                        
                                        # Show first 200 rows
                                        preview_table = ui.table(
                                            columns=[{"name": col, "label": col, "field": col} for col in preview_df.columns[:10]],
                                            rows=preview_df.head(200).to_dict('records'),
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
                        
                        # Expand measurements dict into columns for better visualization
                        expanded_records = []
                        for record in records:
                            expanded = {}
                            # Copy top-level fields
                            for key, value in record.items():
                                if key != "measurements":
                                    expanded[key] = value
                            
                            # Expand measurements dict into columns
                            if "measurements" in record and isinstance(record["measurements"], dict):
                                for m_key, m_value in record["measurements"].items():
                                    expanded[m_key] = m_value
                            else:
                                # If no measurements dict, try to use the record as-is
                                expanded.update(record)
                            
                            expanded_records.append(expanded)
                        
                        # Convert to DataFrame
                        df = pd.DataFrame(expanded_records)
                        
                        # Ensure timestamp column exists and is datetime
                        if 'timestamp' in df.columns:
                            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                            df = df.sort_values('timestamp')
                            # Remove rows with invalid timestamps
                            df = df.dropna(subset=['timestamp'])
                        
                        logger.info(f"Loaded {len(records)} records, expanded to {len(df)} rows with {len(df.columns)} columns for visualization")
                        
                        if len(df) == 0:
                            ui.notify("No valid data points found after processing", type="warning")
                            return
                        
                        if len(df) == 1:
                            logger.warning(f"Only 1 data point found. File may contain only one record or data format issue.")
                            ui.notify(f"Warning: Only 1 data point found. Check data format.", type="warning")
                        
                        with ui.dialog() as viz_dialog, ui.card().classes("w-full max-w-7xl max-h-[90vh] overflow-auto"):
                            ui.label(f"📊 Data Visualization: {Path(file_key).name}").classes("text-xl font-semibold mb-4")
                            
                            # Chart type selector
                            chart_type = ui.select(
                                ["line", "scatter", "bar", "area", "heatmap", "histogram", "box", "violin", "candlestick"],
                                label="Chart Type",
                                value="line"
                            ).classes("w-full mb-4")
                            
                            # Column selectors
                            # Filter out non-plottable columns for X axis
                            x_options = [col for col in df.columns if col not in ['series_id', 'metadata', 'format']]
                            x_col = ui.select(
                                x_options,
                                label="X Axis",
                                value="timestamp" if "timestamp" in x_options else (x_options[0] if x_options else None)
                            ).classes("w-full mb-2")
                            
                            # Get numeric columns for Y axis (exclude X axis column and non-numeric)
                            numeric_cols = list(df.select_dtypes(include=['number']).columns)
                            # Also include string columns that might be numeric (like 'close', 'open' from measurements)
                            for col in df.columns:
                                if col not in numeric_cols and col != x_col.value:
                                    # Check if column can be converted to numeric
                                    try:
                                        pd.to_numeric(df[col].dropna().head(10), errors='raise')
                                        if col not in numeric_cols:
                                            numeric_cols.append(col)
                                    except:
                                        pass
                            
                            # Remove X axis column from Y options
                            y_options = [col for col in numeric_cols if col != x_col.value]
                            if not y_options:
                                # Fallback: use all columns except X axis
                                y_options = [col for col in df.columns if col != x_col.value and col not in ['series_id', 'metadata', 'format']]
                            
                            y_cols = ui.select(
                                y_options,
                                label="Y Axis (select one or more)",
                                multiple=True,
                                value=y_options[:3] if len(y_options) >= 3 else y_options  # Auto-select first 3 or all if less
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
                                    
                                    # Prepare data - ensure we have all columns
                                    cols_to_plot = [x_col_val] + (y_cols_val if isinstance(y_cols_val, list) else [y_cols_val])
                                    cols_to_plot = [col for col in cols_to_plot if col in df.columns]
                                    
                                    if not cols_to_plot:
                                        ui.label("No valid columns selected for plotting").classes("text-red-500")
                                        return
                                    
                                    plot_df = df[cols_to_plot].copy()
                                    
                                    # Convert Y columns to numeric
                                    for col in y_cols_val:
                                        if col in plot_df.columns:
                                            plot_df[col] = pd.to_numeric(plot_df[col], errors='coerce')
                                    
                                    # Drop rows where X or all Y values are NaN
                                    plot_df = plot_df.dropna(subset=[x_col_val])
                                    # Keep rows where at least one Y column has a value
                                    y_has_data = plot_df[y_cols_val].notna().any(axis=1)
                                    plot_df = plot_df[y_has_data]
                                    
                                    if len(plot_df) == 0:
                                        ui.label("No data to plot after removing NaN values. Check column selections.").classes("text-red-500")
                                        return
                                    
                                    logger.info(f"Plotting {len(plot_df)} data points with X={x_col_val}, Y={y_cols_val}")
                                    
                                    if len(plot_df) == 0:
                                        ui.label("No data points to plot. Check column selections and data format.").classes("text-red-500")
                                        return
                                    
                                    # Create Plotly figure
                                    fig = go.Figure()
                                    
                                    if chart_type_val == "line":
                                        for col in y_cols_val:
                                            # Ensure data is sorted by X axis for proper line plotting
                                            sorted_df = plot_df.sort_values(x_col_val)
                                            fig.add_trace(go.Scatter(
                                                x=sorted_df[x_col_val],
                                                y=sorted_df[col],
                                                mode='lines+markers',
                                                name=col,
                                                line=dict(width=2),
                                                marker=dict(size=4 if len(sorted_df) > 100 else 6)  # Smaller markers for many points
                                            ))
                                    
                                    elif chart_type_val == "scatter":
                                        for col in y_cols_val:
                                            sorted_df = plot_df.sort_values(x_col_val)
                                            fig.add_trace(go.Scatter(
                                                x=sorted_df[x_col_val],
                                                y=sorted_df[col],
                                                mode='markers',
                                                name=col,
                                                marker=dict(size=5 if len(sorted_df) > 100 else 8)
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
                                        title=f"{title_input.value} ({len(plot_df)} data points)",
                                        width=int(width_input.value) if width_input.value.isdigit() else 1000,
                                        height=int(height_input.value) if height_input.value.isdigit() else 600,
                                        showlegend=show_legend.value,
                                        xaxis=dict(showgrid=show_grid.value, title=x_col_val),
                                        yaxis=dict(showgrid=show_grid.value, title=", ".join(y_cols_val) if len(y_cols_val) <= 2 else "Values"),
                                        template="plotly_dark",
                                        hovermode='x unified' if len(plot_df) > 10 else 'closest'
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
                                data_bytes = app.storage.load(key)
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
# Health endpoint is defined in nicegui_app/health.py
# Import it to register the route
from nicegui_app.health import health_check

# Favicon route handler - serve favicon to prevent 404 errors
from nicegui import app
from fastapi.responses import Response

@app.get("/favicon.ico")
def favicon():
    """Serve favicon to prevent 404 errors when browsers request /favicon.ico."""
    # Use the same SVG icon from the HTML head, served as SVG
    FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#3b82f6"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>"""
    return Response(content=FAVICON_SVG, media_type="image/svg+xml")


# Note: ui.run() is called from run_nicegui.py
