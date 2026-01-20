"""
NiceGUI App Navigation Bar
Navigation bar component with buttons and status indicators.
"""
from datetime import datetime

from nicegui import ui
from logger import get_logger
from . import get_app_instance
from .dialogs import (
    show_download_dialog,
    show_user_info_dialog,
    show_api_keys_dialog,
    show_search_dialog,
    show_payment_dialog,
    show_settings_dialog,
)

logger = get_logger()


def create_navbar():
    """Create navigation bar with status indicators."""
    with ui.header(fixed=True).classes("bg-blue-800 text-white p-4 shadow-lg"):
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
                    ui.button(icon="person", on_click=show_user_info_dialog).tooltip("User Info")
                    
                    # Download
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
                    
                    ui.button(icon="upload", on_click=scroll_to_upload).tooltip("Upload File")
                    
                    # API Keys
                    ui.button(icon="vpn_key", on_click=show_api_keys_dialog).tooltip("API Keys")
                    
                    # Search
                    ui.button(icon="search", on_click=show_search_dialog).tooltip("Search")
                    
                    # Payment
                    ui.button(icon="credit_card", on_click=show_payment_dialog).tooltip("Payment & Billing")
                    
                    # Settings
                    ui.button(icon="settings", on_click=show_settings_dialog).tooltip("Settings")
            
            # Center: Status indicators
            with ui.row().classes("gap-4 items-center flex-1 justify-center"):
                ui.badge("33 file formats", color="info")
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
