"""
VARIOSYNC Panel Dashboard with FastAPI Native Integration
Modern UI with glass-morphism, loading states, and responsive design.

⚠️ DEPRECATED: This file is no longer used. 
The application has been migrated to NiceGUI.
See nicegui_app.py for the current implementation.

This file is kept for reference only and may be removed in future versions.
"""
# Import from new modular structure
from panel_dashboard import (
    DesignTokens,
    Icons,
    StatusMessages,
    ProDarkTheme,
    ENHANCED_CSS,
    create_modern_button,
    create_section_header,
    create_divider,
    create_navbar,
    create_dashboard,
)

# Re-export for backward compatibility
__all__ = [
    'DesignTokens',
    'Icons',
    'StatusMessages',
    'ProDarkTheme',
    'ENHANCED_CSS',
    'create_modern_button',
    'create_section_header',
    'create_divider',
    'create_navbar',
    'create_dashboard',
]


# Backward compatibility - all functionality moved to panel_dashboard package
# The rest of this file is kept for reference but functionality is imported above

# =============================================================================
# DESIGN TOKENS - Centralized styling configuration (DEPRECATED - use panel_dashboard.DesignTokens)
# =============================================================================
class DesignTokens:
    """Centralized design system tokens for consistent styling."""

    # Colors
    PRIMARY = "#3b82f6"
    PRIMARY_DARK = "#1e40af"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"

    # Layout
    SIDEBAR_WIDTH = 380
    CARD_MARGIN = 12
    BUTTON_WIDTH = 200
    INPUT_WIDTH = None  # stretch

    # Sizing
    PLOT_HEIGHT = 500
    TABLE_HEIGHT = 350
    FILE_INPUT_HEIGHT = 60


# =============================================================================
# ICONS - SVG icons for consistent UI (inline for performance)
# =============================================================================
class Icons:
    """SVG icons as data URIs for modern iconography."""

    # Using simple Unicode symbols that render well in all browsers
    REFRESH = "\u21BB"      # Refresh arrow
    UPLOAD = "\u2912"       # Upload arrow
    PROCESS = "\u26A1"      # Lightning bolt
    STORAGE = "\u2601"      # Cloud
    CHART = "\u2636"        # Chart
    CHECK = "\u2714"        # Checkmark
    WARNING = "\u26A0"      # Warning triangle
    ERROR = "\u2716"        # X mark
    LOADING = "\u23F3"      # Hourglass
    INFO = "\u2139"         # Info
    
    # Navbar icons (using Unicode/emoji directly)
    USER = "👤"
    DASHBOARD = "📊"
    DATABASE = "💿"
    MENU = "☰"
    BRAIN = "🧠"
    DOWNLOAD = "⬇"
    SYNC = "⇄"
    KEY = "🔑"
    SEARCH = "🔍"
    PAYMENT = "💳"
    SETTINGS = "⚙"
    THEME = "🎨"
    CLOCK = "🕐"


# =============================================================================
# STATUS MESSAGES - Consistent status feedback
# =============================================================================
class StatusMessages:
    """Standardized status messages with icons."""

    @staticmethod
    def ready():
        return f"{Icons.INFO} Ready to process files. Drop or select a data file to begin."

    @staticmethod
    def loading(filename: str):
        return f"{Icons.LOADING} Processing {filename}..."

    @staticmethod
    def success(filename: str):
        return f"{Icons.CHECK} Successfully processed {filename}"

    @staticmethod
    def error(message: str):
        return f"{Icons.ERROR} Error: {message}"

    @staticmethod
    def warning(message: str):
        return f"{Icons.WARNING} {message}"


# =============================================================================
# CUSTOM THEME
# =============================================================================
class ProDarkTheme(DarkTheme):
    """Custom professional dark theme for VARIOSYNC dashboard."""
    base_css = str(Path(__file__).parent / "custom-dark-theme.css")


# =============================================================================
# ENHANCED CSS - Additional runtime styling
# =============================================================================
ENHANCED_CSS = """
/* Import Inter font for modern typography */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Card enhancements */
.card {
    border-radius: 16px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
    transform: translateY(-2px);
}

/* Button group styling */
.button-group {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

/* Status indicator animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-4px); }
    to { opacity: 1; transform: translateY(0); }
}

.bk-Alert {
    animation: fadeIn 0.2s ease-out;
}

/* Sidebar section styling */
.sidebar-section {
    padding: 16px;
    margin-bottom: 8px;
    border-radius: 12px;
    background: rgba(30, 41, 59, 0.5);
}

/* Loading state */
.loading-state {
    opacity: 0.6;
    pointer-events: none;
}

/* Metric card */
.metric-card {
    text-align: center;
    padding: 20px;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #3b82f6;
}

.metric-label {
    font-size: 0.875rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
"""


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
# COMPONENT FACTORY
# =============================================================================
def create_modern_button(name: str, icon: str, button_type: str = "primary", width: int = None) -> pn.widgets.Button:
    """Create a modern styled button with icon."""
    if width:
        # Fixed width: set both width and height
        return pn.widgets.Button(
            name=f"{icon} {name}",
            button_type=button_type,
            width=width,
            height=40,  # Set height for fixed sizing mode
            sizing_mode="fixed"
        )
    else:
        # Stretch width: don't set width at all
        return pn.widgets.Button(
            name=f"{icon} {name}",
            button_type=button_type,
            sizing_mode="stretch_width"
        )


def create_section_header(title: str, icon: str) -> pn.pane.Markdown:
    """Create a styled section header."""
    return pn.pane.Markdown(
        f"### {icon} {title}",
        sizing_mode="stretch_width"
    )


def create_divider() -> pn.pane.HTML:
    """Create a styled divider."""
    return pn.pane.HTML(
        '<hr style="border: none; height: 1px; background: linear-gradient(90deg, #334155, transparent); margin: 16px 0;">',
        sizing_mode="stretch_width"
    )


def create_navbar(app_instance=None) -> pn.pane.HTML:
    """Create a comprehensive navbar with icons, status, and controls."""
    import datetime
    
    # Get current time for display
    current_time = datetime.datetime.now().strftime("%H:%M")
    
    # Get app stats if available
    if app_instance:
        try:
            storage_keys = app_instance.storage.list_keys() if app_instance.storage else []
            format_count = len(set([k.split('.')[-1] for k in storage_keys if '.' in k]))
            format_count = max(format_count, 10)  # Default to 10 formats
        except:
            format_count = 10
    else:
        format_count = 10
    
    navbar_html = f"""
    <style>
        .variosync-navbar {{
            background: linear-gradient(135deg, {DesignTokens.PRIMARY_DARK} 0%, {DesignTokens.PRIMARY} 100%);
            padding: 12px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            font-family: var(--font-sans, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif);
            color: white;
            flex-wrap: wrap;
            gap: 16px;
        }}
        
        .navbar-left {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }}
        
        .navbar-center {{
            display: flex;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
            flex: 1;
            justify-content: center;
        }}
        
        .navbar-right {{
            display: flex;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
        }}
        
        .nav-icon {{
            font-size: 20px;
            cursor: pointer;
            padding: 8px;
            border-radius: 6px;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 36px;
            height: 36px;
        }}
        
        .nav-icon:hover {{
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-1px);
        }}
        
        .nav-status {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            padding: 6px 12px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            backdrop-filter: blur(10px);
        }}
        
        .status-indicator {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }}
        
        .status-online {{
            background: {DesignTokens.SUCCESS};
            box-shadow: 0 0 8px {DesignTokens.SUCCESS};
        }}
        
        .status-running {{
            background: {DesignTokens.SUCCESS};
            animation: pulse 2s ease-in-out infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .theme-indicator {{
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .theme-indicator:hover {{
            background: rgba(255, 255, 255, 0.15);
        }}
        
        .usage-info {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            color: rgba(255, 255, 255, 0.9);
        }}
        
        .nav-text {{
            font-size: 13px;
            font-weight: 500;
        }}
    </style>
    
    <div class="variosync-navbar">
        <!-- Left: Functional Icons -->
        <div class="navbar-left">
            <span class="nav-icon" title="User Management">👤</span>
            <span class="nav-icon" title="Dashboard">📊</span>
            <span class="nav-icon" title="Database">💿</span>
            <span class="nav-icon" title="Menu">☰</span>
            <span class="nav-icon" title="AI/Analytics">🧠</span>
            <span class="nav-icon" title="Download">⬇</span>
            <span class="nav-icon" title="Upload">⬆</span>
            <span class="nav-icon" title="Sync">⇄</span>
            <span class="nav-icon" title="API Keys">🔑</span>
            <span class="nav-icon" title="Search">🔍</span>
            <span class="nav-icon" title="Payment">💳</span>
            <span class="nav-icon" title="Settings">⚙</span>
        </div>
        
        <!-- Center: Status Indicators -->
        <div class="navbar-center">
            <div class="nav-status">
                <span>ℹ️</span>
                <span class="nav-text">Online {format_count} formats</span>
            </div>
            <div class="nav-status">
                <span class="status-indicator status-running"></span>
                <span class="nav-text">running</span>
            </div>
            <div class="nav-status">
                <span>💿</span>
                <span class="nav-text">DB: available</span>
            </div>
            <div class="nav-status">
                <span>📄</span>
            </div>
        </div>
        
        <!-- Right: Theme & Usage -->
        <div class="navbar-right">
            <div class="theme-indicator" title="Dark Theme">
                <span>🎨</span>
                <span class="nav-text">Dark</span>
            </div>
            <div class="usage-info">
                <span>🕐</span>
                <span class="nav-text">{current_time} 21s ago</span>
            </div>
            <div class="usage-info">
                <span class="nav-text">Used: 0.47h</span>
            </div>
        </div>
    </div>
    """
    
    return pn.pane.HTML(navbar_html, sizing_mode="stretch_width", height=60)


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
