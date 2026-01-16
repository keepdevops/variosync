"""
VARIOSYNC Panel Components Module
Modern, reusable Panel dashboard components with design system integration.
"""
import os
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

try:
    import panel as pn
    import pandas as pd
    PANEL_AVAILABLE = True
except ImportError:
    PANEL_AVAILABLE = False

from logger import get_logger

logger = get_logger()


# =============================================================================
# DESIGN SYSTEM
# =============================================================================
@dataclass(frozen=True)
class ColorPalette:
    """Design system color palette."""
    # Primary
    primary_50: str = "#eff6ff"
    primary_100: str = "#dbeafe"
    primary_200: str = "#bfdbfe"
    primary_300: str = "#93c5fd"
    primary_400: str = "#60a5fa"
    primary_500: str = "#3b82f6"
    primary_600: str = "#2563eb"
    primary_700: str = "#1d4ed8"
    primary_800: str = "#1e40af"
    primary_900: str = "#1e3a8a"

    # Surface (dark theme)
    surface_50: str = "#f8fafc"
    surface_100: str = "#f1f5f9"
    surface_200: str = "#e2e8f0"
    surface_300: str = "#cbd5e1"
    surface_400: str = "#94a3b8"
    surface_500: str = "#64748b"
    surface_600: str = "#475569"
    surface_700: str = "#334155"
    surface_800: str = "#1e293b"
    surface_900: str = "#0f172a"

    # Semantic
    success: str = "#10b981"
    warning: str = "#f59e0b"
    danger: str = "#ef4444"
    info: str = "#3b82f6"


@dataclass(frozen=True)
class Spacing:
    """Design system spacing scale."""
    xs: int = 4
    sm: int = 8
    md: int = 16
    lg: int = 24
    xl: int = 32
    xxl: int = 48


@dataclass(frozen=True)
class ComponentSizes:
    """Standard component sizing."""
    button_width: int = 180
    button_width_sm: int = 120
    button_width_lg: int = 240
    input_height: int = 40
    file_input_height: int = 60
    table_height: int = 400
    table_height_sm: int = 280
    card_margin: int = 12


# Design system instances
colors = ColorPalette()
spacing = Spacing()
sizes = ComponentSizes()


# =============================================================================
# ICON SYSTEM
# =============================================================================
class Icons:
    """Unicode icons for consistent UI iconography."""
    # Actions
    REFRESH = "\u21BB"
    UPLOAD = "\u2912"
    DOWNLOAD = "\u2913"
    PROCESS = "\u26A1"
    SEARCH = "\u2315"
    SETTINGS = "\u2699"
    EDIT = "\u270E"
    DELETE = "\u2716"
    ADD = "\u271A"

    # Status
    CHECK = "\u2714"
    WARNING = "\u26A0"
    ERROR = "\u2716"
    INFO = "\u2139"
    LOADING = "\u23F3"

    # Objects
    FILE = "\u25A0"
    FOLDER = "\u25B6"
    STORAGE = "\u2601"
    DATABASE = "\u25A3"
    CHART = "\u2636"
    TABLE = "\u2637"
    USER = "\u263A"
    KEY = "\u26BF"


# =============================================================================
# BASE COMPONENT FACTORY
# =============================================================================
class ComponentFactory:
    """Factory for creating styled Panel components."""

    def __init__(self):
        if not PANEL_AVAILABLE:
            raise ImportError("Panel required. Install with: pip install panel pandas")

    # -------------------------------------------------------------------------
    # BUTTONS
    # -------------------------------------------------------------------------
    def button(
        self,
        label: str,
        icon: str = None,
        variant: str = "primary",
        size: str = "md",
        on_click: Callable = None,
        disabled: bool = False
    ) -> pn.widgets.Button:
        """
        Create a styled button.

        Args:
            label: Button text
            icon: Optional icon from Icons class
            variant: primary, success, warning, danger, default
            size: sm, md, lg
            on_click: Click handler callback
            disabled: Whether button is disabled
        """
        width_map = {
            "sm": sizes.button_width_sm,
            "md": sizes.button_width,
            "lg": sizes.button_width_lg
        }

        name = f"{icon} {label}" if icon else label

        button = pn.widgets.Button(
            name=name,
            button_type=variant,
            width=width_map.get(size, sizes.button_width),
            disabled=disabled
        )

        if on_click:
            button.on_click(on_click)

        return button

    def icon_button(
        self,
        icon: str,
        tooltip: str = None,
        variant: str = "default",
        on_click: Callable = None
    ) -> pn.widgets.Button:
        """Create a compact icon-only button."""
        button = pn.widgets.Button(
            name=icon,
            button_type=variant,
            width=40,
            height=40
        )
        if on_click:
            button.on_click(on_click)
        return button

    # -------------------------------------------------------------------------
    # INPUTS
    # -------------------------------------------------------------------------
    def text_input(
        self,
        label: str,
        placeholder: str = "",
        value: str = "",
        width: int = None
    ) -> pn.widgets.TextInput:
        """Create a styled text input."""
        return pn.widgets.TextInput(
            name=label,
            placeholder=placeholder,
            value=value,
            width=width,
            sizing_mode="stretch_width" if width is None else "fixed"
        )

    def password_input(
        self,
        label: str,
        placeholder: str = "",
        width: int = None
    ) -> pn.widgets.PasswordInput:
        """Create a styled password input."""
        return pn.widgets.PasswordInput(
            name=label,
            placeholder=placeholder,
            width=width,
            sizing_mode="stretch_width" if width is None else "fixed"
        )

    def select(
        self,
        label: str,
        options: list,
        value: str = None,
        width: int = None
    ) -> pn.widgets.Select:
        """Create a styled select dropdown."""
        return pn.widgets.Select(
            name=label,
            options=options,
            value=value or (options[0] if options else None),
            width=width,
            sizing_mode="stretch_width" if width is None else "fixed"
        )

    def file_input(
        self,
        label: str = "Choose file",
        accept: str = ".json,.csv,.txt,.parquet,.feather",
        multiple: bool = False
    ) -> pn.widgets.FileInput:
        """Create a styled file input."""
        return pn.widgets.FileInput(
            name=label,
            accept=accept,
            multiple=multiple,
            height=sizes.file_input_height
        )

    # -------------------------------------------------------------------------
    # DISPLAY
    # -------------------------------------------------------------------------
    def alert(
        self,
        message: str,
        variant: str = "info"
    ) -> pn.pane.Alert:
        """
        Create a styled alert.

        Args:
            message: Alert message
            variant: info, success, warning, danger
        """
        return pn.pane.Alert(
            message,
            alert_type=variant,
            sizing_mode="stretch_width"
        )

    def table(
        self,
        data: pd.DataFrame = None,
        height: int = None,
        page_size: int = 25,
        selectable: str = None,
        theme: str = "midnight"
    ) -> pn.widgets.Tabulator:
        """
        Create a styled data table.

        Args:
            data: DataFrame to display
            height: Table height in pixels
            page_size: Rows per page
            selectable: None, "checkbox", or True
            theme: Tabulator theme
        """
        if data is None:
            data = pd.DataFrame()

        return pn.widgets.Tabulator(
            value=data,
            pagination="local",
            page_size=page_size,
            height=height or sizes.table_height,
            theme=theme,
            selectable=selectable,
            layout="fit_columns",
            sizing_mode="stretch_width",
            configuration={
                "columnDefaults": {
                    "headerSort": True,
                }
            }
        )

    def markdown(
        self,
        content: str,
        **kwargs
    ) -> pn.pane.Markdown:
        """Create a markdown pane."""
        return pn.pane.Markdown(
            content,
            sizing_mode="stretch_width",
            **kwargs
        )

    # -------------------------------------------------------------------------
    # LAYOUT
    # -------------------------------------------------------------------------
    def card(
        self,
        *content,
        title: str = None,
        icon: str = None,
        collapsed: bool = False,
        margin: int = None
    ) -> pn.Card:
        """Create a styled card container."""
        card_title = f"{icon} {title}" if icon and title else title

        return pn.Card(
            *content,
            title=card_title,
            collapsed=collapsed,
            sizing_mode="stretch_both",
            margin=margin or sizes.card_margin
        )

    def section_header(
        self,
        title: str,
        icon: str = None
    ) -> pn.pane.Markdown:
        """Create a section header."""
        text = f"### {icon} {title}" if icon else f"### {title}"
        return pn.pane.Markdown(text, sizing_mode="stretch_width")

    def divider(self) -> pn.pane.HTML:
        """Create a styled horizontal divider."""
        return pn.pane.HTML(
            '<hr style="border: none; height: 1px; background: linear-gradient(90deg, #334155, transparent); margin: 16px 0;">',
            sizing_mode="stretch_width"
        )

    def spacer(self, height: int = None, width: int = None) -> pn.Spacer:
        """Create a spacer element."""
        return pn.Spacer(height=height, width=width)


# =============================================================================
# DASHBOARD COMPONENTS (Legacy API - Enhanced)
# =============================================================================
class DashboardComponents:
    """
    Reusable Panel dashboard components.
    Enhanced with design system integration.
    """

    def __init__(self):
        """Initialize components."""
        if not PANEL_AVAILABLE:
            raise ImportError("Panel required. Install with: pip install panel pandas")
        self.factory = ComponentFactory()

    def create_upload_section(self) -> Dict[str, Any]:
        """Create file upload section with modern styling."""
        upload_widget = self.factory.file_input(
            label="Drop file or click to browse"
        )

        record_type_widget = self.factory.select(
            label="Data Type",
            options=["time_series", "financial"],
            value="time_series"
        )

        file_format_widget = self.factory.select(
            label="File Format",
            options=["auto", "json", "csv", "txt", "parquet", "feather"],
            value="auto"
        )

        process_button = self.factory.button(
            label="Process File",
            icon=Icons.PROCESS,
            variant="success"
        )

        status_pane = self.factory.alert(
            f"{Icons.INFO} Ready to process files",
            variant="info"
        )

        return {
            "upload": upload_widget,
            "record_type": record_type_widget,
            "file_format": file_format_widget,
            "process_button": process_button,
            "status": status_pane
        }

    def create_api_section(self) -> Dict[str, Any]:
        """Create API download section with modern styling."""
        api_name_widget = self.factory.text_input(
            label="API Name",
            placeholder="e.g., Alpha Vantage"
        )

        api_url_widget = self.factory.text_input(
            label="API Base URL",
            placeholder="https://api.example.com"
        )

        api_key_widget = self.factory.password_input(
            label="API Key"
        )

        entity_id_widget = self.factory.text_input(
            label="Entity ID",
            placeholder="AAPL, WEATHER-001, etc."
        )

        download_button = self.factory.button(
            label="Download",
            icon=Icons.DOWNLOAD,
            variant="success"
        )

        return {
            "api_name": api_name_widget,
            "api_url": api_url_widget,
            "api_key": api_key_widget,
            "entity_id": entity_id_widget,
            "download_button": download_button
        }

    def create_storage_section(self) -> Dict[str, Any]:
        """Create storage browser section with modern styling."""
        storage_prefix_widget = self.factory.text_input(
            label="Storage Prefix",
            placeholder="data/",
            value=""
        )

        refresh_button = self.factory.button(
            label="Refresh",
            icon=Icons.REFRESH,
            variant="default",
            size="sm"
        )

        data_table = self.factory.table(
            data=pd.DataFrame(columns=["Key", "Size", "Type"]),
            height=sizes.table_height,
            selectable="checkbox"
        )

        return {
            "prefix": storage_prefix_widget,
            "refresh_button": refresh_button,
            "data_table": data_table
        }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================
def create_metric_card(
    value: str,
    label: str,
    icon: str = None,
    color: str = None
) -> pn.pane.HTML:
    """Create a metric display card."""
    icon_html = f'<span style="font-size: 1.5rem; margin-right: 8px;">{icon}</span>' if icon else ''
    color_style = f'color: {color};' if color else f'color: {colors.primary_500};'

    return pn.pane.HTML(f'''
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 2.5rem; font-weight: 700; {color_style}">
                {icon_html}{value}
            </div>
            <div style="font-size: 0.875rem; color: {colors.surface_400}; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 8px;">
                {label}
            </div>
        </div>
    ''', sizing_mode="stretch_width")


def create_status_badge(
    status: str,
    variant: str = "info"
) -> pn.pane.HTML:
    """Create a status badge."""
    color_map = {
        "info": colors.info,
        "success": colors.success,
        "warning": colors.warning,
        "danger": colors.danger
    }
    bg_color = color_map.get(variant, colors.info)

    return pn.pane.HTML(f'''
        <span style="
            display: inline-block;
            padding: 4px 12px;
            border-radius: 9999px;
            background: {bg_color}22;
            color: {bg_color};
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        ">{status}</span>
    ''')
