"""
Panel Dashboard Theme and Design Tokens
Centralized styling configuration, icons, and CSS.
"""
from pathlib import Path

try:
    from panel.template import DarkTheme
    PANEL_AVAILABLE = True
except ImportError:
    PANEL_AVAILABLE = False
    DarkTheme = None


# =============================================================================
# DESIGN TOKENS - Centralized styling configuration
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
if PANEL_AVAILABLE and DarkTheme:
    class ProDarkTheme(DarkTheme):
        """Custom professional dark theme for VARIOSYNC dashboard."""
        base_css = str(Path(__file__).parent.parent / "custom-dark-theme.css")
else:
    ProDarkTheme = None


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
