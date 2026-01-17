#!/usr/bin/env python3
"""
VARIOSYNC NiceGUI Application Launcher
Runs NiceGUI web server.
"""
import os
import sys

# Import the app to register routes
import nicegui_app

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
