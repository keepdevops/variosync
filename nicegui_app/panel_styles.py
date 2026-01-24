"""
Panel Styles Module
Contains all CSS for flexbox-based independent card system.
Each card is an independent, moveable, resizable window.
"""
from nicegui import ui


def get_panel_styles() -> str:
    """
    Returns CSS styles for flexbox-based independent panel system.
    Each card is wrapped in a flexi-panel that can be dragged, resized, and floated.
    """
    return '''
    <style>
        /* 
         * INDEPENDENT WINDOW SYSTEM
         * Each card is wrapped in its own independent panel window:
         * - Plot card = Independent window for charts (Plotly/Matplotlib)
         * - Upload card = Independent window for file processing
         * - Storage card = Independent window for file browser
         * - Navbar cards = Independent windows for navigation components
         * 
         * When floating, each panel becomes completely independent,
         * similar to separate application windows.
         */
        
        /* Ensure navbar stays behind cards - prevent bleed-through */
        .q-header, header[data-navbar="true"], .q-header[data-navbar="true"],
        header.bg-blue-800, .q-header.bg-blue-800 {
            z-index: 5 !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            background: #1e3a8a !important;
            opacity: 1 !important;
            overflow: hidden !important;
        }
        
        /* Ensure navbar content doesn't bleed through */
        .q-header *, header[data-navbar="true"] * {
            position: relative;
            z-index: auto;
        }
        
        /* Global flexbox for all dashboard components */
        .q-page, .q-page-container, .q-page-sticky {
            display: flex;
            flex-direction: column;
        }
        
        /* Make all rows use flexbox */
        .q-row, .row, [class*="row"] {
            display: flex !important;
            flex-direction: row;
            flex-wrap: wrap;
            align-items: center;
        }
        
        /* Make all columns use flexbox */
        .q-column, .column, [class*="column"] {
            display: flex !important;
            flex-direction: column;
        }
        
        /* Dashboard cards use flexbox */
        .q-card {
            display: flex;
            flex-direction: column;
        }
        
        /* Main container - flexbox layout for panels */
        .panels-grid {
            display: flex;
            flex-wrap: wrap;
            flex-direction: row;
            gap: 12px;
            padding: 12px;
            align-content: flex-start;
            align-items: flex-start;
            height: calc(100vh - 90px);
            overflow-y: auto;
            overflow-x: hidden;
            position: relative;
        }
        
        /* When panels float, they're removed from flexbox flow */
        .panels-grid .flexi-panel.floating {
            position: fixed !important;
        }

        /* Panel wrapper - flexbox card - Each card is its own independent window */
        .flexi-panel {
            position: relative;
            display: flex;
            flex-direction: column;
            background: #1e1e2e !important;
            border: 2px solid #3b82f6;
            border-radius: 8px;
            overflow: hidden;
            min-width: 300px;
            min-height: 250px;
            flex: 1 1 300px;
            max-width: calc(50% - 6px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            transition: box-shadow 0.2s ease, transform 0.2s ease;
            isolation: isolate;
            contain: strict;
            z-index: 10;
            opacity: 1 !important;
        }
        
        /* Plotting Window - Independent window for charts */
        .flexi-panel[data-window-type="plotting"],
        .flexi-panel:has([data-section="plot"]) {
            border-color: #10b981;
        }
        
        /* Upload Window - Independent window for file processing */
        .flexi-panel[data-window-type="upload"],
        .flexi-panel:has([data-section="upload"]) {
            border-color: #f59e0b;
        }
        
        /* Storage Window - Independent window for file browser */
        .flexi-panel[data-window-type="storage"],
        .flexi-panel:has([data-section="storage"]) {
            border-color: #8b5cf6;
        }

        .flexi-panel:hover {
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }

        /* When floating, remove ALL flex constraints - truly independent window */
        .flexi-panel.floating {
            flex: none !important;
            max-width: none !important;
            position: fixed !important;
            z-index: 1000 !important;
            left: auto !important;
            top: auto !important;
            right: auto !important;
            bottom: auto !important;
            margin: 0 !important;
            isolation: isolate;
            contain: layout style paint;
        }

        /* Panel header - draggable handle */
        .flexi-panel-header {
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            padding: 8px 12px !important;
            background: linear-gradient(135deg, #3b82f6, #1e40af) !important;
            cursor: move !important;
            cursor: grab;
            user-select: none;
            flex-shrink: 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            position: relative;
            z-index: 10;
            min-height: 40px;
        }
        
        .flexi-panel-header {
            visibility: visible !important;
            display: flex !important;
        }
        
        .flexi-panel-header .flexi-panel-controls {
            display: flex !important;
            visibility: visible !important;
        }
        
        .flexi-panel-header .flexi-panel-btn {
            display: inline-flex !important;
            visibility: visible !important;
        }
        
        .flexi-panel-header:active {
            cursor: grabbing !important;
        }
        
        .flexi-panel {
            touch-action: none;
        }
        .flexi-panel-title {
            color: white;
            font-weight: 600;
            font-size: 14px;
            flex: 1;
        }
        .flexi-panel-controls {
            display: flex !important;
            gap: 6px;
            align-items: center;
            flex-shrink: 0;
            z-index: 100;
            position: relative;
        }
        .flexi-panel-btn {
            width: 40px !important;
            height: 40px !important;
            min-width: 40px !important;
            min-height: 40px !important;
            border: 3px solid white !important;
            border-radius: 8px !important;
            background: white !important;
            color: #1e1e2e !important;
            cursor: pointer !important;
            font-size: 22px !important;
            font-weight: bold !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.2s ease;
            flex-shrink: 0 !important;
            padding: 0 !important;
            margin: 0 3px !important;
            line-height: 1 !important;
            visibility: visible !important;
            opacity: 1 !important;
            pointer-events: auto !important;
            -webkit-user-select: none !important;
            user-select: none !important;
            box-shadow: 0 3px 8px rgba(0,0,0,0.4) !important;
            z-index: 1000 !important;
            position: relative !important;
        }
        .flexi-panel-btn:hover { 
            background: #f0f0f0 !important;
            border-color: #ffffff !important;
            transform: scale(1.1);
            box-shadow: 0 4px 8px rgba(0,0,0,0.4) !important;
        }
        .flexi-panel-btn:active {
            transform: scale(0.95);
            background: #e0e0e0 !important;
        }
        .flexi-panel-btn:focus {
            outline: 3px solid rgba(255,255,255,0.9);
            outline-offset: 2px;
        }
        
        .flexi-panel-header .flexi-panel-controls,
        .flexi-panel-header .flexi-panel-btn {
            visibility: visible !important;
            display: flex !important;
            opacity: 1 !important;
            pointer-events: auto !important;
        }
        
        .flexi-panel[data-window-type="plotting"] .flexi-panel-btn,
        .flexi-panel:has([data-section="plot"]) .flexi-panel-btn {
            visibility: visible !important;
            display: flex !important;
            opacity: 1 !important;
            pointer-events: auto !important;
            width: 36px !important;
            height: 36px !important;
            font-size: 20px !important;
            background: white !important;
            color: #1e1e2e !important;
            border: 2px solid white !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.4) !important;
        }
        
        .flexi-panel[data-window-type="plotting"] .flexi-panel-controls,
        .flexi-panel:has([data-section="plot"]) .flexi-panel-controls {
            visibility: visible !important;
            display: flex !important;
            opacity: 1 !important;
        }
        
        .flexi-panel.minimized .flexi-panel-btn[data-action="minimize"] {
            background: rgba(59, 130, 246, 0.4);
        }
        
        .flexi-panel.maximized .flexi-panel-btn[data-action="maximize"] {
            background: rgba(59, 130, 246, 0.4);
        }
        
        .flexi-panel.floating .flexi-panel-btn[data-action="float"] {
            background: rgba(59, 130, 246, 0.4);
        }

        /* Panel body - flex container - Each card content is isolated */
        .flexi-panel-body {
            flex: 1;
            overflow: auto;
            min-height: 0;
            display: flex;
            flex-direction: column;
            padding: 8px;
            isolation: isolate;
            position: relative;
        }
        .flexi-panel-body > .q-card {
            height: 100%;
            border: none;
            border-radius: 0;
            flex: 1;
            display: flex;
            flex-direction: column;
            isolation: isolate;
            position: relative;
        }
        
        .flexi-panel-body [data-section="plot"],
        .flexi-panel[data-window-type="plotting"] .flexi-panel-body {
            display: flex;
            flex-direction: column;
            flex: 1;
            min-height: 0;
            isolation: isolate;
            contain: layout style paint;
            background: #1e1e2e !important;
        }
        
        .flexi-panel[data-window-type="plotting"],
        .flexi-panel:has([data-section="plot"]) {
            background: #1e1e2e !important;
            z-index: 10 !important;
            position: relative !important;
            opacity: 1 !important;
            overflow: hidden !important;
            isolation: isolate !important;
            contain: strict !important;
        }
        
        .flexi-panel[data-window-type="plotting"] .flexi-panel-body,
        .flexi-panel:has([data-section="plot"]) .flexi-panel-body {
            background: #1e1e2e !important;
            opacity: 1 !important;
            overflow: auto !important;
        }
        
        .flexi-panel[data-window-type="plotting"] .q-card,
        .flexi-panel:has([data-section="plot"]) .q-card {
            background: #1e1e2e !important;
            opacity: 1 !important;
            overflow: visible !important;
        }
        
        .flexi-panel[data-window-type="plotting"] *,
        .flexi-panel:has([data-section="plot"]) * {
            position: relative;
            z-index: auto;
        }
        
        .panels-grid {
            z-index: 1;
            position: relative;
        }
        
        .flexi-panel {
            resize: none;
        }
        
        .flexi-panel::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            pointer-events: none;
            z-index: 1;
        }
        
        .flexi-panel:hover {
        }
        
        .flexi-panel[data-window-type="plotting"],
        .flexi-panel:has([data-section="plot"]) {
            min-width: 400px;
            min-height: 300px;
        }
        
        .flexi-panel-body [data-section="plot"] nicegui-plotly,
        .flexi-panel-body [data-section="plot"] .js-plotly-plot,
        .flexi-panel[data-window-type="plotting"] nicegui-plotly,
        .flexi-panel[data-window-type="plotting"] .js-plotly-plot {
            flex: 1;
            min-height: 300px;
            width: 100%;
            isolation: isolate;
        }
        
        .flexi-panel-body [data-section="upload"],
        .flexi-panel[data-window-type="upload"] .flexi-panel-body {
            display: flex;
            flex-direction: column;
            flex: 1;
            isolation: isolate;
            contain: layout style paint;
        }
        
        .flexi-panel-body [data-section="storage"],
        .flexi-panel[data-window-type="storage"] .flexi-panel-body {
            display: flex;
            flex-direction: column;
            flex: 1;
            isolation: isolate;
            contain: layout style paint;
        }
        
        .flexi-panel[data-window-type="plotting"] .flexi-panel-header {
            background: linear-gradient(135deg, #10b981, #059669);
        }
        
        .flexi-panel[data-window-type="upload"] .flexi-panel-header {
            background: linear-gradient(135deg, #f59e0b, #d97706);
        }
        
        .flexi-panel[data-window-type="storage"] .flexi-panel-header {
            background: linear-gradient(135deg, #8b5cf6, #7c3aed);
        }
        
        .flexi-panel-body .q-row,
        .flexi-panel-body .row,
        .flexi-panel-body .q-column,
        .flexi-panel-body .column {
            display: flex !important;
        }
        
        .flexi-panel-body .q-card > * {
            display: flex;
            flex-direction: column;
            flex: 1;
        }
        
        .flexi-panel-body .q-row.gap-4,
        .flexi-panel-body .row.gap-4 {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            align-items: center;
        }
        
        .flexi-panel-body .q-input,
        .flexi-panel-body .q-select,
        .flexi-panel-body .q-btn {
            flex: 0 0 auto;
        }
        
        .flexi-panel-body .flex-1 {
            flex: 1 1 0;
            min-width: 0;
        }
        
        .flexi-panel-body .w-full {
            width: 100%;
            flex: 1 1 100%;
        }

        .flexi-panel.floating {
            position: fixed !important;
            z-index: 1000;
            box-shadow: 0 10px 40px rgba(0,0,0,0.6);
            overflow: hidden;
            max-width: 90vw !important;
            max-height: 90vh !important;
            flex: none !important;
            resize: both;
        }
        
        .flexi-panel.floating .flexi-panel-body {
            overflow: auto;
        }

        .flexi-panel.minimized {
            height: 40px !important;
            min-height: 40px !important;
            overflow: hidden;
        }
        
        .flexi-panel.minimized .flexi-panel-body {
            display: none !important;
        }
        
        .flexi-panel.minimized .flexi-resize-handle {
            display: none;
        }
        
        .flexi-panel.maximized {
            position: fixed !important;
            top: 80px !important;
            left: 0 !important;
            width: 100vw !important;
            height: calc(100vh - 80px) !important;
            z-index: 999;
            border-radius: 0;
            border: none;
            max-width: 100vw !important;
            max-height: calc(100vh - 80px) !important;
        }
        
        .flexi-panel.maximized .flexi-resize-handle {
            display: none;
        }

        .flexi-panel.panel-wide { 
            flex: 1 1 100%;
            max-width: 100%;
        }

        .flexi-panel.navbar-panel {
            flex: 0 0 auto;
            min-width: 400px;
            max-width: 600px;
        }

        .flexi-resize-handle {
            position: absolute;
            bottom: 0;
            right: 0;
            width: 16px;
            height: 16px;
            cursor: nwse-resize;
            background: linear-gradient(135deg, transparent 50%, #3b82f6 50%);
            opacity: 0.6;
            transition: opacity 0.2s ease;
            z-index: 10;
            pointer-events: auto;
        }
        .flexi-panel:hover .flexi-resize-handle {
            opacity: 1;
        }
        
        .flexi-panel::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            pointer-events: none;
            border: 2px solid transparent;
            border-radius: 8px;
            transition: border-color 0.2s ease;
            z-index: 0;
        }
        
        .flexi-panel:hover::after {
            border-color: rgba(59, 130, 246, 0.3);
        }

        .flexi-panel-body .js-plotly-plot,
        .flexi-panel-body .plotly,
        .flexi-panel-body .plot-container {
            width: 100% !important;
            height: 100% !important;
        }
        .flexi-panel-body nicegui-plotly {
            display: block;
            width: 100%;
            min-height: 280px;
            flex: 1;
        }

        .flexi-panel-body > .q-card > .text-xl:first-child { display: none; }

        .navbar-card {
            display: flex;
            flex-direction: column;
            padding: 8px;
            background: rgba(59, 130, 246, 0.1);
            border-radius: 6px;
            margin: 4px;
        }

        .flexi-panel-body > * {
            flex-shrink: 0;
        }
        .flexi-panel-body > .q-card {
            flex-shrink: 1;
        }
        
        .q-page > .q-card,
        .panels-grid > .flexi-panel {
            display: flex;
            flex-direction: column;
        }
        
        [data-section="upload"] .q-row,
        [data-section="upload"] .row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            align-items: center;
        }
        
        [data-section="plot"] .q-row,
        [data-section="plot"] .row {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            align-items: center;
        }
        
        [data-section="plot"] .q-select,
        [data-section="plot"] .q-btn {
            flex: 0 0 auto;
        }
        
        [data-section="storage"] .q-column,
        [data-section="storage"] .column {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        [data-section^="navbar"] {
            display: flex;
            flex-direction: row;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }
        
        .restore-panels-container {
            position: fixed;
            top: 90px;
            right: 20px;
            z-index: 2000;
            background: rgba(30, 30, 46, 0.95);
            border: 2px solid #3b82f6;
            border-radius: 8px;
            padding: 12px;
            min-width: 200px;
            max-height: calc(100vh - 120px);
            overflow-y: auto;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }
        
        .restore-panels-container h3 {
            color: white;
            font-size: 14px;
            margin: 0 0 8px 0;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .restore-panel-btn {
            display: block;
            width: 100%;
            padding: 8px 12px;
            margin: 4px 0;
            background: rgba(59, 130, 246, 0.2);
            border: 1px solid rgba(59, 130, 246, 0.4);
            border-radius: 4px;
            color: white;
            cursor: pointer;
            text-align: left;
            font-size: 12px;
            transition: background 0.2s ease;
        }
        
        .restore-panel-btn:hover {
            background: rgba(59, 130, 246, 0.4);
        }
        
        .restore-panels-container.hidden {
            display: none;
        }
        
        @media (max-width: 768px) {
            .panels-grid {
                flex-direction: column;
            }
            .flexi-panel {
                max-width: 100% !important;
                flex: 1 1 100% !important;
            }
            .flexi-panel-body .q-row,
            .flexi-panel-body .row {
                flex-direction: column;
            }
        }
    </style>
    '''


def inject_panel_styles():
    """Inject panel styles into the page."""
    ui.add_head_html(get_panel_styles())
