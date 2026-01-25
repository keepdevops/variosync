"""
Live Sync Metrics Card
Independent resizable window for time-series visualization.
"""
from nicegui import ui
import plotly.graph_objects as go
from logger import get_logger
from nicegui_app.state import get_state
from nicegui_app.visualization import (
    load_timeseries_data,
    load_timeseries_from_file,
    get_available_series,
    is_financial_data,
    get_available_metrics,
    create_matplotlib_financial_plot,
    create_matplotlib_plot,
    matplotlib_figure_to_base64,
    create_plot,
)

logger = get_logger()

# Import availability flags
try:
    from nicegui_app import (
        MATPLOTLIB_AVAILABLE,
        ALTAIR_AVAILABLE,
        HIGHCHARTS_AVAILABLE,
        ECHARTS_AVAILABLE,
    )
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
    MATPLOTLIB_AVAILABLE = False
    ALTAIR_AVAILABLE = False
    HIGHCHARTS_AVAILABLE = False
    ECHARTS_AVAILABLE = False
    create_altair_plot_wrapper = None
    altair_chart_to_html = None
    create_highcharts_plot_wrapper = None
    highcharts_config_to_html = None
    create_echarts_plot_wrapper = None
    echarts_config_to_html = None

# Helper function to render HTML with scripts
def render_html_with_scripts(html_content: str, container_id: str = None):
    """Render HTML content that may contain script tags."""
    import re
    script_pattern = r'<script[^>]*>.*?</script>'
    
    scripts = re.findall(script_pattern, html_content, re.DOTALL | re.IGNORECASE)
    html_without_scripts = re.sub(script_pattern, '', html_content, flags=re.DOTALL | re.IGNORECASE).strip()
    
    if not scripts:
        return ui.html(html_without_scripts, sanitize=False)
    
    container = ui.html(html_without_scripts, sanitize=False).classes("w-full").style("height: 600px;")
    
    for script in scripts:
        ui.add_body_html(script)
    
    return container


def create_live_sync_metrics_card(panels_grid):
    """
    Create Live Sync Metrics card.
    
    Args:
        panels_grid: The container where the card will be added.
    """
    state = get_state()
    
    with panels_grid:
        with ui.card().classes("w-full").props("data-section='plot'"):
            ui.label("📊 Live Sync Metrics").classes("text-xl font-semibold mb-4")
            
            # Data source controls
            with ui.row().classes("w-full gap-4 items-center mb-2"):
                data_source_select = ui.select(
                    options=["storage", "file"],
                    label="Data Source",
                    value="storage"
                ).classes("w-32")

                file_path_input = ui.input(
                    label="File Path (JSON, Parquet, CSV)",
                    placeholder="/path/to/data.json"
                ).classes("flex-1")
                file_path_input.visible = False

                load_file_button = ui.button("📂 Load File", icon="folder_open", color="secondary")
                load_file_button.visible = False

                def on_data_source_change():
                    is_file = data_source_select.value == "file"
                    file_path_input.visible = is_file
                    load_file_button.visible = is_file

                data_source_select.on('update:modelValue', on_data_source_change)

            # Store data source components in state
            state.set_component("dashboard.data_source_select", data_source_select)
            state.set_component("dashboard.file_path_input", file_path_input)
            state.set_state("dashboard.loaded_file_path", None)

            # Controls row
            with ui.row().classes("w-full gap-4 items-center"):
                refresh_button = ui.button("🔄 Refresh Data", icon="refresh", color="primary")
                
                # Chart library selector
                chart_library_options = ["plotly"]
                if MATPLOTLIB_AVAILABLE:
                    chart_library_options.append("matplotlib")
                if ALTAIR_AVAILABLE:
                    chart_library_options.append("altair")
                if HIGHCHARTS_AVAILABLE:
                    chart_library_options.append("highcharts")
                if ECHARTS_AVAILABLE:
                    chart_library_options.append("echarts")
                
                chart_library_select = ui.select(
                    options=chart_library_options,
                    label="Chart Library",
                    value="plotly"
                ).classes("w-40").props('id="chart-library-select"')
                
                def update_select_options():
                    try:
                        chart_library_select.options = chart_library_options
                        chart_library_select.update()
                    except Exception as e:
                        logger.warning(f"Error updating select options: {e}")
                
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
                chart_type_select.visible = False
            
            # Store UI components in shared state
            state.set_component("dashboard.chart_library_select", chart_library_select)
            state.set_component("dashboard.series_select", series_select)
            state.set_component("dashboard.metric_select", metric_select)
            state.set_component("dashboard.chart_type_select", chart_type_select)
            
            # Plot container
            plot_figure = go.Figure()
            plot_figure.add_annotation(
                text="Loading data...",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="gray")
            )
            plot_figure.update_layout(
                template="plotly_dark",
                autosize=True,
                margin=dict(l=40, r=20, t=20, b=40)
            )
            plot_container = ui.plotly(plot_figure).classes("w-full").style("min-height: 350px; height: auto;")
            plot_image = None
            
            state.set_component("dashboard.plot_container", plot_container)
            state.set_state("dashboard.plot_figure", plot_figure)
            state.set_state("dashboard.plot_image", plot_image)
            
            def update_plot():
                """Update the plot with current data and selections."""
                logger.debug("[update_plot] Starting plot update")

                chart_library_select = state.get_component("dashboard.chart_library_select")
                series_select = state.get_component("dashboard.series_select")
                metric_select = state.get_component("dashboard.metric_select")
                chart_type_select = state.get_component("dashboard.chart_type_select")
                plot_container = state.get_component("dashboard.plot_container")
                plot_figure = state.get_state("dashboard.plot_figure")
                plot_image = state.get_state("dashboard.plot_image")
                data_source = state.get_component("dashboard.data_source_select")
                file_path_input = state.get_component("dashboard.file_path_input")
                loaded_file_path = state.get_state("dashboard.loaded_file_path")

                # Log component states
                logger.debug(f"[update_plot] Data source: {data_source.value if data_source else 'N/A'}")
                logger.debug(f"[update_plot] Loaded file path: {loaded_file_path}")
                logger.debug(f"[update_plot] Chart library: {chart_library_select.value if chart_library_select else 'N/A'}")

                try:
                    # Load data based on selected source
                    df = None
                    records = []

                    if data_source and data_source.value == "file" and loaded_file_path:
                        logger.info(f"[update_plot] Loading from file: {loaded_file_path}")
                        df, records = load_timeseries_from_file(loaded_file_path)
                        if df is not None:
                            logger.info(f"[update_plot] Loaded {len(df)} records from file: {loaded_file_path}")
                        else:
                            logger.warning(f"[update_plot] Failed to load data from file: {loaded_file_path}")
                    else:
                        logger.debug("[update_plot] Loading from storage")
                        df, records = load_timeseries_data()
                        if df is not None:
                            logger.info(f"[update_plot] Loaded {len(df)} records from storage")
                        else:
                            logger.debug("[update_plot] No data loaded from storage")

                    # Log DataFrame info
                    if df is not None:
                        logger.debug(f"[update_plot] DataFrame shape: {df.shape}")
                        logger.debug(f"[update_plot] DataFrame columns: {list(df.columns)}")
                        numeric_cols = list(df.select_dtypes(include=['number']).columns)
                        logger.debug(f"[update_plot] Numeric columns: {numeric_cols}")
                    else:
                        logger.warning("[update_plot] DataFrame is None - no data to plot")

                    chart_library = chart_library_select.value if chart_library_select else "plotly"
                    is_financial = is_financial_data(df, series_select.value) if df is not None else False
                    logger.debug(f"[update_plot] Is financial data: {is_financial}")
                    chart_type_select.visible = is_financial
                    
                    available_series = get_available_series(df)
                    logger.debug(f"[update_plot] Available series: {available_series}")
                    series_select.options = available_series
                    if available_series and series_select.value not in available_series:
                        series_select.value = available_series[0] if available_series else None
                        logger.debug(f"[update_plot] Auto-selected series: {series_select.value}")

                    selected_series = series_select.value if series_select.value else None
                    logger.debug(f"[update_plot] Selected series: {selected_series}")

                    if is_financial:
                        metric_select.visible = False
                        logger.debug("[update_plot] Financial data detected, hiding metric selector")
                    else:
                        metric_select.visible = True
                        available_metrics = get_available_metrics(df, selected_series)
                        logger.debug(f"[update_plot] Available metrics: {available_metrics}")
                        metric_select.options = available_metrics
                        if available_metrics and metric_select.value not in available_metrics:
                            metric_select.value = available_metrics[0] if available_metrics else None
                            logger.debug(f"[update_plot] Auto-selected metric: {metric_select.value}")

                    chart_type = chart_type_select.value if is_financial else "auto"
                    logger.debug(f"[update_plot] Chart type: {chart_type}")
                    
                    # Create plot based on selected library
                    logger.debug(f"[update_plot] Creating plot with library: {chart_library}")

                    if chart_library == "matplotlib" and MATPLOTLIB_AVAILABLE:
                        logger.debug("[update_plot] Using Matplotlib for plotting")
                        if is_financial:
                            logger.debug(f"[update_plot] Creating Matplotlib financial plot, chart_type: {chart_type}")
                            mpl_fig = create_matplotlib_financial_plot(df, series_select.value, chart_type, show_volume=True)
                        else:
                            logger.debug(f"[update_plot] Creating Matplotlib plot, metric: {metric_select.value}")
                            mpl_fig = create_matplotlib_plot(df, series_select.value, metric_select.value)

                        if mpl_fig:
                            logger.debug("[update_plot] Matplotlib figure created successfully")
                            img_data = matplotlib_figure_to_base64(mpl_fig)
                            try:
                                plot_container.delete()
                            except:
                                pass
                            plot_image = ui.image(img_data).classes("w-full").style("max-height: 600px; object-fit: contain;")
                            plot_container = plot_image
                            state.set_component("dashboard.plot_container", plot_container)
                            state.set_state("dashboard.plot_image", plot_image)
                        else:
                            logger.warning("[update_plot] Matplotlib figure creation returned None")
                    elif chart_library == "altair" and ALTAIR_AVAILABLE and create_altair_plot_wrapper:
                        try:
                            altair_chart = create_altair_plot_wrapper(df, series_select.value, metric_select.value, chart_type)
                            if altair_chart:
                                html_content = altair_chart_to_html(altair_chart)
                                try:
                                    plot_container.delete()
                                except:
                                    pass
                                plot_container = render_html_with_scripts(html_content)
                                state.set_component("dashboard.plot_container", plot_container)
                        except Exception as e:
                            logger.error(f"Error creating Altair chart: {e}", exc_info=True)
                            ui.notify(f"Altair chart error: {str(e)}", type="negative")
                    elif chart_library == "highcharts" and HIGHCHARTS_AVAILABLE and create_highcharts_plot_wrapper:
                        try:
                            hc_config = create_highcharts_plot_wrapper(df, series_select.value, metric_select.value, chart_type)
                            if hc_config:
                                html_content = highcharts_config_to_html(hc_config, container_id="highcharts-dashboard")
                                try:
                                    plot_container.delete()
                                except:
                                    pass
                                plot_container = render_html_with_scripts(html_content)
                                state.set_component("dashboard.plot_container", plot_container)
                        except Exception as e:
                            logger.error(f"Error creating Highcharts chart: {e}", exc_info=True)
                            ui.notify(f"Highcharts chart error: {str(e)}", type="negative")
                    elif chart_library == "echarts" and ECHARTS_AVAILABLE and create_echarts_plot_wrapper:
                        try:
                            echarts_config = create_echarts_plot_wrapper(df, series_select.value, metric_select.value, chart_type)
                            if echarts_config:
                                html_content = echarts_config_to_html(echarts_config, container_id="echarts-dashboard")
                                try:
                                    plot_container.delete()
                                except:
                                    pass
                                plot_container = render_html_with_scripts(html_content)
                                state.set_component("dashboard.plot_container", plot_container)
                        except Exception as e:
                            logger.error(f"Error creating ECharts chart: {e}", exc_info=True)
                            ui.notify(f"ECharts chart error: {str(e)}", type="negative")
                    else:
                        # Use Plotly (default)
                        logger.debug("[update_plot] Using Plotly for plotting")
                        logger.debug(f"[update_plot] Plotly params - series: {series_select.value}, metric: {metric_select.value}, chart_type: {chart_type}")
                        new_fig = create_plot(df, series_select.value, metric_select.value, chart_type)

                        if new_fig is None:
                            logger.error("[update_plot] Plotly create_plot returned None")
                        else:
                            trace_count = len(new_fig.data) if hasattr(new_fig, 'data') else 0
                            logger.debug(f"[update_plot] Plotly figure created with {trace_count} traces")

                        has_subplots = hasattr(new_fig, '_grid_ref') and new_fig._grid_ref is not None
                        logger.debug(f"[update_plot] Has subplots: {has_subplots}")

                        if has_subplots:
                            plot_figure = new_fig
                            try:
                                plot_container.delete()
                            except:
                                pass
                            plot_container = ui.plotly(plot_figure).classes("w-full").style("min-height: 350px; height: auto;")
                            state.set_component("dashboard.plot_container", plot_container)
                            state.set_state("dashboard.plot_figure", plot_figure)
                        else:
                            plot_figure.data = []
                            plot_figure.add_traces(list(new_fig.data))
                            plot_figure.update_layout(new_fig.layout)
                            state.set_state("dashboard.plot_figure", plot_figure)
                            
                            try:
                                if hasattr(plot_container, 'set_figure'):
                                    plot_container.set_figure(plot_figure)
                                elif hasattr(plot_container, 'update'):
                                    plot_container.update()
                                else:
                                    plot_container.delete()
                                    plot_container = ui.plotly(plot_figure).classes("w-full").style("min-height: 350px; height: auto;")
                                    state.set_component("dashboard.plot_container", plot_container)
                            except Exception:
                                plot_container.delete()
                                plot_container = ui.plotly(plot_figure).classes("w-full").style("min-height: 350px; height: auto;")
                                state.set_component("dashboard.plot_container", plot_container)
                    
                    record_count = len(df) if df is not None else 0
                    logger.info(f"[update_plot] Plot updated successfully with {record_count} records using {chart_library}")
                except Exception as e:
                    logger.error(f"[update_plot] Error updating plot: {e}", exc_info=True)
                    ui.notify(f"Error updating plot: {str(e)}", type="negative")
            
            def refresh_plot():
                """Refresh the time-series plot."""
                logger.info("Refreshing plot...")
                update_plot()
                ui.notify("Plot refreshed", type="info")

            def load_from_file():
                """Load data from the specified file path."""
                logger.debug("[load_from_file] Starting file load")

                file_path = file_path_input.value if file_path_input else None

                # Validate file path
                if not file_path:
                    logger.warning("[load_from_file] Empty file path")
                    ui.notify("Please enter a file path", type="warning")
                    return

                file_path = file_path.strip()
                logger.info(f"[load_from_file] Attempting to load: {file_path}")

                from pathlib import Path
                path_obj = Path(file_path)

                if not path_obj.exists():
                    logger.error(f"[load_from_file] File not found: {file_path}")
                    ui.notify(f"File not found: {file_path}", type="negative")
                    return

                if not path_obj.is_file():
                    logger.error(f"[load_from_file] Path is not a file: {file_path}")
                    ui.notify(f"Path is not a file: {file_path}", type="negative")
                    return

                # Log file info
                file_size = path_obj.stat().st_size
                logger.info(f"[load_from_file] File: {file_path}, size: {file_size} bytes ({file_size / 1024:.2f} KB)")

                if file_size == 0:
                    logger.warning(f"[load_from_file] File is empty: {file_path}")
                    ui.notify("File is empty", type="warning")
                    return

                # Store the file path and update plot
                state.set_state("dashboard.loaded_file_path", file_path)
                logger.info(f"[load_from_file] Set loaded file path in state: {file_path}")

                # Load and display record count
                df, records = load_timeseries_from_file(file_path)

                if df is None:
                    logger.error(f"[load_from_file] Failed to load DataFrame from: {file_path}")
                    ui.notify("Failed to parse file", type="negative")
                    return

                if len(df) == 0:
                    logger.warning(f"[load_from_file] No valid records in file: {file_path}")
                    ui.notify("No valid records found in file", type="warning")
                    return

                logger.info(f"[load_from_file] Successfully loaded {len(df)} records")
                logger.debug(f"[load_from_file] Columns: {list(df.columns)}")

                ui.notify(f"Loaded {len(df)} records from file", type="positive")
                update_plot()

            load_file_button.on_click(load_from_file)

            # Update plot when selections change
            series_select.on('update:modelValue', update_plot)
            metric_select.on('update:modelValue', update_plot)
            chart_type_select.on('update:modelValue', update_plot)
            chart_library_select.on('update:modelValue', update_plot)
            
            refresh_button.on_click(refresh_plot)
            update_plot()
