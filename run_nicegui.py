#!/usr/bin/env python3
"""
VARIOSYNC NiceGUI Application Launcher
Runs NiceGUI web server.
"""
import os
import sys
import importlib.util

# Import nicegui_app.py file directly (not the package)
# This ensures the @ui.page("/") route is registered
spec = importlib.util.spec_from_file_location("nicegui_app_module", "nicegui_app.py")
nicegui_app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nicegui_app_module)

from nicegui import ui

if __name__ in {"__main__", "__mp_main__"}:
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"""
    ╔═══════════════════════════════════════════════════════╗
    ║          VARIOSYNC Web Application                    ║
    ║          Powered by NiceGUI                            ║
    ╚═══════════════════════════════════════════════════════╝
    
    🌐 Web UI:        http://{host}:{port}
    ❤️  Health Check:  http://{host}:{port}/health
    
    Press CTRL+C to stop
    """)
    
    # Run NiceGUI (routes are registered via decorators in nicegui_app.py)
    ui.run(
        title="VARIOSYNC Dashboard",
        port=port,
        host=host,
        dark=True,
        show_welcome_message=False
    )
