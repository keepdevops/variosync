"""
Panel Styles Module
Contains all CSS for gridstack-based dashboard card system.
Each card is a resizable, draggable grid item.
"""
from nicegui import ui


def get_panel_styles() -> str:
    """
    Returns CSS styles for gridstack-based dashboard panel system.
    """
    return '''
    <style>
        /* Ensure navbar stays on top */
        .q-header, header[data-navbar="true"], .q-header[data-navbar="true"],
        header.bg-blue-800, .q-header.bg-blue-800 {
            z-index: 1001 !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            background: #1e3a8a !important;
        }

        /* Main container */
        .panels-grid {
            padding: 8px;
            min-height: calc(100vh - 120px);
        }

        /* Gridstack overrides */
        .grid-stack {
            background: transparent !important;
        }

        .grid-stack-item {
            background: transparent;
        }

        .grid-stack-item-content {
            background: #1e1e2e !important;
            border: 2px solid #3b82f6;
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        /* Card type specific borders */
        .grid-stack-item-content[data-window-type="plotting"] {
            border-color: #10b981;
        }

        .grid-stack-item-content[data-window-type="upload"] {
            border-color: #f59e0b;
        }

        .grid-stack-item-content[data-window-type="storage"] {
            border-color: #8b5cf6;
        }

        /* Card header - drag handle */
        .gs-item-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            background: linear-gradient(135deg, #3b82f6, #1e40af);
            cursor: move;
            user-select: none;
            flex-shrink: 0;
            min-height: 40px;
        }

        .grid-stack-item-content[data-window-type="plotting"] .gs-item-header {
            background: linear-gradient(135deg, #10b981, #059669);
        }

        .grid-stack-item-content[data-window-type="upload"] .gs-item-header {
            background: linear-gradient(135deg, #f59e0b, #d97706);
        }

        .grid-stack-item-content[data-window-type="storage"] .gs-item-header {
            background: linear-gradient(135deg, #8b5cf6, #7c3aed);
        }

        .gs-item-title {
            color: white;
            font-weight: 600;
            font-size: 14px;
            flex: 1;
        }

        .gs-item-controls {
            display: flex;
            gap: 6px;
            align-items: center;
        }

        .gs-item-btn {
            width: 28px;
            height: 28px;
            border: 2px solid white;
            border-radius: 6px;
            background: white;
            color: #1e1e2e;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            padding: 0;
            line-height: 1;
        }

        .gs-item-btn:hover {
            background: #e0e0e0;
            transform: scale(1.1);
        }

        .gs-item-btn:active {
            transform: scale(0.95);
        }

        .gs-item-btn-close:hover {
            background: #ef4444;
            color: white;
            border-color: #ef4444;
        }

        /* Card body */
        .gs-item-body {
            flex: 1;
            overflow: auto;
            padding: 8px;
            background: #1e1e2e;
            min-height: 0;
        }

        .gs-item-body > .q-card {
            background: transparent !important;
            box-shadow: none !important;
            height: 100%;
        }

        /* Hide duplicate title in card body */
        .gs-item-body > .q-card > .text-xl:first-child {
            display: none;
        }

        /* Minimized state */
        .gs-minimized .gs-item-body {
            display: none !important;
        }

        .gs-minimized .grid-stack-item-content {
            min-height: auto !important;
        }

        /* Maximized state */
        .gs-maximized {
            z-index: 100 !important;
        }

        /* Plotly chart sizing */
        .gs-item-body nicegui-plotly,
        .gs-item-body .js-plotly-plot,
        .gs-item-body .plotly {
            width: 100% !important;
            height: 100% !important;
            min-height: 280px;
        }

        /* Resize handle styling */
        .grid-stack-item > .ui-resizable-handle {
            background: transparent;
        }

        .grid-stack-item > .ui-resizable-se {
            background: linear-gradient(135deg, transparent 50%, #3b82f6 50%);
            width: 16px;
            height: 16px;
            right: 0;
            bottom: 0;
            opacity: 0.6;
        }

        .grid-stack-item:hover > .ui-resizable-se {
            opacity: 1;
        }

        /* Placeholder styling */
        .grid-stack-placeholder > .placeholder-content {
            background: rgba(59, 130, 246, 0.2) !important;
            border: 2px dashed #3b82f6 !important;
            border-radius: 8px;
        }

        /* Closed panels container */
        .gs-closed-panels {
            display: none;
            position: fixed;
            top: 90px;
            right: 20px;
            z-index: 2000;
            background: rgba(30, 30, 46, 0.95);
            border: 2px solid #3b82f6;
            border-radius: 8px;
            padding: 12px;
            min-width: 200px;
        }

        .gs-closed-panels h4 {
            color: white;
            margin: 0 0 8px 0;
            font-size: 14px;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .grid-stack-item {
                width: 100% !important;
                left: 0 !important;
            }
        }

        /* Animation */
        .grid-stack-item {
            transition: left 0.3s, top 0.3s, width 0.3s, height 0.3s;
        }

        .grid-stack-item.ui-draggable-dragging,
        .grid-stack-item.ui-resizable-resizing {
            transition: none;
        }

        /* Fix for NiceGUI elements inside grid */
        .gs-item-body .row,
        .gs-item-body .q-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .gs-item-body .column,
        .gs-item-body .q-column {
            display: flex;
            flex-direction: column;
        }
    </style>
    '''


def inject_panel_styles():
    """Inject panel styles into the page."""
    ui.add_head_html(get_panel_styles())
