"""
Panel Dashboard UI Components
Component factory functions for creating reusable UI elements.
"""
try:
    import panel as pn
    PANEL_AVAILABLE = True
except ImportError:
    PANEL_AVAILABLE = False

from .theme import DesignTokens, Icons


def create_modern_button(name: str, icon: str, button_type: str = "primary", width: int = None) -> pn.widgets.Button:
    """Create a modern styled button with icon."""
    if not PANEL_AVAILABLE:
        return None
    
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
    if not PANEL_AVAILABLE:
        return None
    
    return pn.pane.Markdown(
        f"### {icon} {title}",
        sizing_mode="stretch_width"
    )


def create_divider() -> pn.pane.HTML:
    """Create a styled divider."""
    if not PANEL_AVAILABLE:
        return None
    
    return pn.pane.HTML(
        '<hr style="border: none; height: 1px; background: linear-gradient(90deg, #334155, transparent); margin: 16px 0;">',
        sizing_mode="stretch_width"
    )


def create_navbar(app_instance=None) -> pn.pane.HTML:
    """Create a comprehensive navbar with icons, status, and controls."""
    if not PANEL_AVAILABLE:
        return None
    
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
