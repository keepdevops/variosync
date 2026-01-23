#!/usr/bin/env python3
"""
VARIOSYNC NiceGUI Application Launcher
Runs NiceGUI web server.
"""
import os
import sys
import platform

# Fix for macOS Apple Silicon (M1/M2/M3) - must be set before importing multiprocessing
# The default "fork" start method causes BrokenPipeError on macOS
if platform.system() == "Darwin":
    import multiprocessing
    try:
        multiprocessing.set_start_method("spawn", force=True)
    except RuntimeError:
        pass  # Already set

import importlib.util

# Import nicegui_app.py file directly (not the package)
# This ensures the @ui.page("/") route is registered
spec = importlib.util.spec_from_file_location("nicegui_app_module", "nicegui_app.py")
nicegui_app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nicegui_app_module)

from nicegui import ui

if __name__ in {"__main__", "__mp_main__"}:
    # Production configuration
    port = int(os.getenv("PORT", os.getenv("NICEGUI_PORT", 8080)))
    host = os.getenv("HOST", os.getenv("NICEGUI_HOST", "0.0.0.0"))
    reload = os.getenv("NICEGUI_RELOAD", "false").lower() == "true"
    storage_secret = os.getenv("STORAGE_SECRET")
    
    print(f"""
    ╔═══════════════════════════════════════════════════════╗
    ║          VARIOSYNC Web Application                    ║
    ║          Powered by NiceGUI                            ║
    ╚═══════════════════════════════════════════════════════╝
    
    🌐 Web UI:        http://{host}:{port}
    ❤️  Health Check:  http://{host}:{port}/health
    🔄 Reload:        {reload}
    🔐 Storage Secret: {'Set' if storage_secret else 'Not set'}
    
    Press CTRL+C to stop
    """)
    
    # Run NiceGUI (routes are registered via decorators in nicegui_app.py)
    # reload=False for production, prevents file watcher issues
    ui.run(
        title="VARIOSYNC Dashboard",
        port=port,
        host=host,
        dark=True,
        show_welcome_message=False,
        reload=reload,
        storage_secret=storage_secret,
    )
