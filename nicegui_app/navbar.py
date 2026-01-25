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


def create_navbar(panels_grid=None, card_initializers=None):
    """
    Create navigation bar with status indicators and card initialization buttons.
    
    Args:
        panels_grid: The container where cards will be added.
        card_initializers: Dict with card initialization functions {'plot': func, 'upload': func, 'storage': func}.
    """
    # Track initialized cards
    initialized_cards = {}
    
    def initialize_card(card_type):
        """Initialize a card if not already initialized."""
        if card_type in initialized_cards:
            # Card already exists, scroll to it
            js_code = f'''
            (function() {{
                const card = document.querySelector('[data-section="{card_type}"]');
                const panel = card?.closest('.flexi-panel');
                if (panel) {{
                    panel.scrollIntoView({{behavior: "smooth", block: "center"}});
                    panel.style.boxShadow = '0 0 25px rgba(16, 185, 129, 0.9)';
                    setTimeout(() => {{
                        panel.style.boxShadow = '';
                    }}, 2500);
                }}
            }})();
            '''
            ui.run_javascript(js_code)
            ui.notify(f"{card_type.title()} card already open", type="info")
            return
        
        if card_initializers and card_type in card_initializers:
            try:
                card_initializers[card_type]()
                initialized_cards[card_type] = True
                ui.notify(f"{card_type.title()} card initialized", type="positive")
                
                # Scroll to the new card after a short delay
                ui.timer(0.5, lambda: ui.run_javascript(f'''
                    const card = document.querySelector('[data-section="{card_type}"]');
                    const panel = card?.closest('.flexi-panel');
                    if (panel) {{
                        panel.scrollIntoView({{behavior: "smooth", block: "center"}});
                    }}
                '''), once=True)
            except Exception as e:
                logger.error(f"Error initializing {card_type} card: {e}", exc_info=True)
                ui.notify(f"Error initializing {card_type} card: {str(e)}", type="negative")
        else:
            ui.notify(f"Card initializer not available for {card_type}", type="warning")
    
    with ui.header(fixed=True).classes("bg-blue-800 text-white p-4 shadow-lg").props('data-navbar="true"'):
        with ui.row().classes("w-full items-center justify-between").props('data-section="navbar-left"'):
            # Left: Logo/Brand and Functional buttons
            with ui.row().classes("gap-4 items-center"):
                # Brand/Logo image - click to refresh dashboard
                logo_icon = ui.image("/static/VS.png").classes("w-8 h-8 cursor-pointer hover:scale-110 transition-transform")
                logo_label = ui.label("VARIOSYNC").classes("text-xl font-bold cursor-pointer hover:text-blue-200")
                
                def refresh_dashboard():
                    """Refresh the entire dashboard."""
                    ui.notify("Refreshing dashboard...", type="info")
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
                    
                    # Live Sync Metrics - initialize or scroll to card
                    def init_live_sync_metrics():
                        initialize_card('plot')
                    
                    ui.button(icon="bar_chart", on_click=init_live_sync_metrics).tooltip("📊 Live Sync Metrics (Ctrl/Cmd+L)")
                    
                    # Upload - initialize or scroll to card
                    def init_upload():
                        initialize_card('upload')
                    
                    ui.button(icon="upload", on_click=init_upload).tooltip("📤 Upload & Process Files")
                    
                    # Storage - initialize or scroll to card
                    def init_storage():
                        initialize_card('storage')
                    
                    ui.button(icon="storage", on_click=init_storage).tooltip("💾 Storage Browser")
                    
                    # Plots - scroll to and focus plots section
                    def scroll_to_plots():
                        try:
                            app = get_app_instance()
                            # Show metrics info if available
                            if app.storage:
                                try:
                                    keys = app.storage.list_keys()
                                    if keys:
                                        ui.notify(f"Live Sync Metrics: {len(keys)} data series available", type="info")
                                except:
                                    pass
                            
                            # Scroll to Live Sync Metrics card and ensure it's visible
                            js_code = '''
                            (function() {
                                // Find the Live Sync Metrics card by data-section="plot" or by title
                                const plotSection = document.querySelector('[data-section="plot"]');
                                let targetPanel = plotSection?.closest('.flexi-panel');
                                
                                // Also try finding by title text
                                if (!targetPanel) {
                                    const allPanels = document.querySelectorAll('.flexi-panel');
                                    for (let panel of allPanels) {
                                        const title = panel.querySelector('.flexi-panel-title');
                                        if (title && title.textContent.includes('Live Sync Metrics')) {
                                            targetPanel = panel;
                                            break;
                                        }
                                    }
                                }
                                
                                if (targetPanel) {
                                    // Scroll to the panel
                                    targetPanel.scrollIntoView({behavior: "smooth", block: "center"});
                                    
                                    // If panel is minimized, restore it
                                    if (targetPanel.classList.contains('minimized')) {
                                        const minimizeBtn = targetPanel.querySelector('.flexi-panel-btn[data-action="minimize"]');
                                        if (minimizeBtn) minimizeBtn.click();
                                    }
                                    
                                    // If panel is closed, try to restore it
                                    if (targetPanel.style.display === 'none') {
                                        const restoreBtns = document.querySelectorAll('.restore-panel-btn');
                                        for (let btn of restoreBtns) {
                                            if (btn.textContent.includes('Live Sync Metrics')) {
                                                btn.click();
                                                break;
                                            }
                                        }
                                    }
                                    
                                    // Highlight the panel briefly with green glow
                                    targetPanel.style.boxShadow = '0 0 25px rgba(16, 185, 129, 0.9)';
                                    targetPanel.style.transition = 'box-shadow 0.3s ease';
                                    setTimeout(() => {
                                        targetPanel.style.boxShadow = '';
                                    }, 2500);
                                    
                                    return true;
                                } else if (plotSection) {
                                    plotSection.scrollIntoView({behavior: "smooth", block: "center"});
                                    return true;
                                }
                                return false;
                            })();
                            '''
                            ui.run_javascript(js_code)
                            ui.notify("Navigated to Live Sync Metrics", type="info")
                        except Exception as e:
                            logger.error(f"Error scrolling to Live Sync Metrics: {e}")
                            ui.notify("Error accessing Live Sync Metrics", type="negative")
                    
                    # API Keys
                    ui.button(icon="vpn_key", on_click=show_api_keys_dialog).tooltip("API Keys")
                    
                    # Search
                    ui.button(icon="search", on_click=show_search_dialog).tooltip("Search")
                    
                    # Payment
                    ui.button(icon="credit_card", on_click=show_payment_dialog).tooltip("Payment & Billing")
                    
                    # Settings
                    ui.button(icon="settings", on_click=show_settings_dialog).tooltip("Settings")
            
            # Center: Status indicators
            with ui.row().classes("gap-4 items-center flex-1 justify-center").props('data-section="navbar-center"'):
                ui.badge("33 file formats", color="info")
                with ui.row().classes("items-center gap-2"):
                    ui.icon("circle", color="green", size="sm")
                    ui.label("running")
                ui.badge("DB: available", color="success")
                ui.icon("description")
            
            # Right: Theme and usage
            with ui.row().classes("gap-4 items-center").props('data-section="navbar-right"'):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("palette")
                    ui.label("Dark")
                with ui.row().classes("items-center gap-2"):
                    ui.icon("schedule")
                    ui.label(f"{datetime.now().strftime('%H:%M')} 21s ago")
                with ui.row().classes("items-center gap-2"):
                    ui.icon("timer")
                    ui.label("Used: 0.47h")
