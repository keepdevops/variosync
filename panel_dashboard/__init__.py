"""
VARIOSYNC Panel Dashboard with FastAPI Native Integration
Modern UI with glass-morphism, loading states, and responsive design.

⚠️ DEPRECATED: This file is no longer used. 
The application has been migrated to NiceGUI.
See nicegui_app.py for the current implementation.

This file is kept for reference only and may be removed in future versions.
"""
from .theme import DesignTokens, Icons, StatusMessages, ProDarkTheme, ENHANCED_CSS
from .components import create_modern_button, create_section_header, create_divider, create_navbar
from .dashboard import create_dashboard

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
