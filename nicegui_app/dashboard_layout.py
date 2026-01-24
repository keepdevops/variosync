"""
Dashboard Layout Module
Contains the main flexbox layout structure for the dashboard.
Each card is independent and moveable within the browser.
"""
from nicegui import ui
from nicegui_app.state import get_state


def create_dashboard_layout():
    """
    Creates the main flexbox container for all dashboard panels.
    Returns the panels grid container where cards will be added.
    """
    state = get_state()
    
    # Main flexbox container for all panels
    main_container = ui.column().classes("w-full").style("display: flex; flex-direction: column; height: calc(100vh - 80px);")
    
    # Panels grid container - flexbox layout
    with main_container:
        panels_grid = ui.column().classes("w-full panels-grid").style("flex: 1; overflow-y: auto;")
        
        # Page header
        with panels_grid:
            ui.label("Time-Series Dashboard").classes("text-3xl font-bold mb-4")
    
    return main_container, panels_grid


def setup_dashboard_page(client):
    """
    Sets up the dashboard page with proper styling and layout.
    Called from the main dashboard_page function.
    """
    # Remove default padding and set up for panel system
    client.content.classes(remove='q-pa-md')
    client.content.style('padding-top: 80px; overflow: hidden;')
    
    # Add cache-busting meta tags for Safari
    ui.add_head_html('<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">')
    ui.add_head_html('<meta http-equiv="Pragma" content="no-cache">')
    ui.add_head_html('<meta http-equiv="Expires" content="0">')
    
    ui.page_title("VARIOSYNC Dashboard")
