"""
Panel Dashboard Main Dashboard Creation
Main dashboard function that assembles all components.
"""
import os
from typing import Optional

try:
    import panel as pn
    import pandas as pd
    PANEL_AVAILABLE = True
except ImportError:
    PANEL_AVAILABLE = False

from logger import get_logger
from main import VariosyncApp
from panel_timeseries import get_timeseries_plot

from .theme import DesignTokens, Icons, StatusMessages, ENHANCED_CSS
from .components import create_modern_button, create_section_header, create_divider, create_navbar

logger = get_logger()


# =============================================================================
# PANEL INITIALIZATION
# =============================================================================
if PANEL_AVAILABLE:
    pn.extension(
        "tabulator",
        "plotly",
        sizing_mode="stretch_width",
        loading_spinner="dots",
        loading_color=DesignTokens.PRIMARY
    )
    pn.config.sizing_mode = "stretch_width"


# =============================================================================
# MAIN DASHBOARD
# =============================================================================
def create_dashboard(supabase_client=None):
    """
    Create modern Panel dashboard with FastAPI native integration.

    Args:
        supabase_client: Optional Supabase client for realtime data

    Returns:
        Panel dashboard object (servable)
    """
    if not PANEL_AVAILABLE:
        return None

    app = VariosyncApp()

    # =========================================================================
    # TIME-SERIES VISUALIZATION
    # =========================================================================
    timeseries_plot = pn.pane.HoloViews(
        get_timeseries_plot(supabase_client),
        sizing_mode="stretch_width",
        height=DesignTokens.PLOT_HEIGHT
    )

    refresh_button = create_modern_button("Refresh Data", Icons.REFRESH, "primary")

    def refresh_plot(event):
        """Refresh the time-series plot with loading state."""
        refresh_button.loading = True
        try:
            timeseries_plot.object = get_timeseries_plot(supabase_client)
            logger.info("Dashboard refreshed")
        finally:
            refresh_button.loading = False

    refresh_button.on_click(refresh_plot)

    # =========================================================================
    # FILE UPLOAD SECTION
    # =========================================================================
    upload_widget = pn.widgets.FileInput(
        name="Drop file or click to browse",
        accept=".json,.csv,.txt,.parquet,.feather",
        height=DesignTokens.FILE_INPUT_HEIGHT,
        multiple=False
    )

    record_type_widget = pn.widgets.Select(
        name="Data Type",
        options=["time_series", "financial"],
        value="time_series",
        sizing_mode="stretch_width"
    )

    process_button = create_modern_button("Process File", Icons.PROCESS, "success")

    status_pane = pn.pane.Alert(
        StatusMessages.ready(),
        alert_type="info",
        sizing_mode="stretch_width"
    )

    def process_file(event):
        """Handle file processing with loading states."""
        if upload_widget.value is None:
            status_pane.alert_type = "warning"
            status_pane.object = StatusMessages.warning("Please select a file first")
            return

        process_button.loading = True
        status_pane.alert_type = "info"
        status_pane.object = StatusMessages.loading(upload_widget.filename)

        try:
            temp_path = f"/tmp/{upload_widget.filename}"
            with open(temp_path, "wb") as f:
                f.write(upload_widget.value)

            success = app.process_data_file(temp_path, record_type_widget.value)
            os.remove(temp_path)

            if success:
                status_pane.alert_type = "success"
                status_pane.object = StatusMessages.success(upload_widget.filename)
                # Refresh visualizations
                refresh_plot(None)
                refresh_aggregates(None)
            else:
                status_pane.alert_type = "danger"
                status_pane.object = StatusMessages.error("Processing failed. Check file format.")
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            status_pane.alert_type = "danger"
            status_pane.object = StatusMessages.error(str(e))
        finally:
            process_button.loading = False

    process_button.on_click(process_file)

    # =========================================================================
    # STORAGE BROWSER
    # =========================================================================
    storage_table = pn.widgets.Tabulator(
        value=pd.DataFrame(columns=["Key", "Size", "Type"]),
        pagination="local",
        page_size=20,
        height=DesignTokens.TABLE_HEIGHT,
        theme="midnight",
        selectable="checkbox",
        layout="fit_columns",
        sizing_mode="stretch_width",
        configuration={
            "columnDefaults": {
                "headerSort": True,
            }
        }
    )

    def refresh_storage(event):
        """Refresh storage browser with loading state."""
        refresh_storage_button.loading = True
        try:
            if app.storage:
                keys = app.storage.list_keys()[:100]
                df_data = []
                for k in keys:
                    file_type = k.split('.')[-1].upper() if '.' in k else 'DATA'
                    df_data.append({
                        "Key": k,
                        "Size": "N/A",
                        "Type": file_type
                    })
                storage_table.value = pd.DataFrame(df_data)
        except Exception as e:
            logger.error(f"Error refreshing storage: {e}")
        finally:
            refresh_storage_button.loading = False

    refresh_storage_button = create_modern_button("Refresh", Icons.REFRESH, "default", 150)
    refresh_storage_button.on_click(refresh_storage)

    # =========================================================================
    # AGGREGATE TABLE
    # =========================================================================
    aggregate_table = pn.widgets.Tabulator(
        value=pd.DataFrame(columns=["Hour", "Records", "Series"]),
        pagination="local",
        page_size=15,
        height=280,
        theme="midnight",
        layout="fit_columns",
        sizing_mode="stretch_width"
    )

    def refresh_aggregates(event=None):
        """Refresh aggregate table with hourly aggregates."""
        try:
            if app.storage:
                keys = app.storage.list_keys("data/")[:100]
                records = []
                for key in keys:
                    data_bytes = app.storage.load(key)
                    if data_bytes:
                        import json
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
                        df['hour'] = df['timestamp'].dt.floor('h')  # Use 'h' instead of deprecated 'H'

                        aggregates = []
                        for hour in sorted(df['hour'].unique(), reverse=True):
                            hour_data = df[df['hour'] == hour]
                            agg_row = {
                                'Hour': hour.strftime('%Y-%m-%d %H:00'),
                                'Records': len(hour_data),
                                'Series': hour_data.get('series_id', pd.Series()).nunique() if 'series_id' in hour_data.columns else 0
                            }
                            aggregates.append(agg_row)

                        aggregate_table.value = pd.DataFrame(aggregates)
                    else:
                        aggregate_table.value = pd.DataFrame(columns=["Hour", "Records", "Series"])
                else:
                    aggregate_table.value = pd.DataFrame(columns=["Hour", "Records", "Series"])
        except Exception as e:
            logger.error(f"Error refreshing aggregates: {e}")
            aggregate_table.value = pd.DataFrame(columns=["Hour", "Records", "Series"])

    # =========================================================================
    # SIDEBAR LAYOUT
    # =========================================================================
    sidebar_content = pn.Column(
        # Header
        pn.pane.Markdown("## Dashboard Controls", sizing_mode="stretch_width"),
        create_divider(),

        # Upload Section
        create_section_header("Upload Data", Icons.UPLOAD),
        pn.Spacer(height=8),
        upload_widget,
        pn.Spacer(height=12),
        record_type_widget,
        pn.Spacer(height=12),
        process_button,
        pn.Spacer(height=12),
        status_pane,

        pn.Spacer(height=24),
        create_divider(),

        # Storage Section
        create_section_header("Storage Browser", Icons.STORAGE),
        pn.Spacer(height=8),
        pn.Row(refresh_storage_button, sizing_mode="stretch_width"),
        pn.Spacer(height=12),
        storage_table,

        sizing_mode="stretch_width",
        margin=(0, 16)
    )

    # =========================================================================
    # TEMPLATE CONFIGURATION
    # =========================================================================
    # Create template with dark theme
    try:
        template = pn.template.FastListTemplate(
            site="VARIOSYNC",
            title="Time-Series Dashboard",
            header_background=DesignTokens.PRIMARY_DARK,
            accent_base_color=DesignTokens.PRIMARY,
            theme="dark",
            sidebar_width=DesignTokens.SIDEBAR_WIDTH
        )
    except Exception as e:
        # Fallback to default theme if custom theme fails
        logger.warning(f"Could not use custom theme: {e}, using default")
        template = pn.template.FastListTemplate(
            site="VARIOSYNC",
            title="Time-Series Dashboard",
            header_background=DesignTokens.PRIMARY_DARK,
            accent_base_color=DesignTokens.PRIMARY,
            sidebar_width=DesignTokens.SIDEBAR_WIDTH
        )

    # Apply enhanced CSS
    template.raw_css = [ENHANCED_CSS]

    # Add navbar - try header first, fallback to main if header doesn't work
    navbar = create_navbar(app)
    try:
        # Try adding to header
        if hasattr(template, 'header'):
            template.header.append(navbar)
        elif hasattr(template, 'header_content'):
            template.header_content.append(navbar)
        else:
            # Add as first element in main content
            template.main.insert(0, navbar)
    except Exception as e:
        logger.warning(f"Could not add navbar to header: {e}, adding to main content")
        template.main.insert(0, navbar)

    # Add sidebar
    template.sidebar.append(sidebar_content)

    # =========================================================================
    # MAIN CONTENT CARDS
    # =========================================================================

    # Metrics Chart Card
    chart_card = pn.Card(
        pn.Column(
            pn.Row(
                refresh_button,
                pn.Spacer(),
                sizing_mode="stretch_width"
            ),
            pn.Spacer(height=12),
            timeseries_plot,
            sizing_mode="stretch_both"
        ),
        title=f"{Icons.CHART} Live Sync Metrics",
        sizing_mode="stretch_both",
        margin=DesignTokens.CARD_MARGIN,
        collapsed=False
    )

    # Aggregates Card
    aggregates_card = pn.Card(
        aggregate_table,
        title=f"{Icons.CHART} Hourly Aggregates",
        sizing_mode="stretch_both",
        margin=DesignTokens.CARD_MARGIN,
        collapsed=True
    )

    # Add navbar as first element in main content
    template.main.insert(0, navbar)
    
    # Add main content cards
    template.main.extend([chart_card, aggregates_card])

    # =========================================================================
    # EVENT BINDING
    # =========================================================================
    def refresh_all(event):
        """Refresh all dashboard components."""
        refresh_plot(event)
        refresh_aggregates(event)

    # Override refresh button to refresh everything
    refresh_button.on_click(refresh_all)

    # =========================================================================
    # INITIAL DATA LOAD
    # =========================================================================
    refresh_storage(None)
    refresh_aggregates(None)

    return template.servable()
