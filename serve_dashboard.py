#!/usr/bin/env python3
"""
Simple Panel dashboard launcher for development.
"""
import panel as pn

# Initialize Panel extensions
pn.extension("tabulator", "plotly", sizing_mode="stretch_width")

# Import and create dashboard
from panel_dashboard_fastapi import create_dashboard

# Create the dashboard (returns a servable template)
dashboard = create_dashboard()

# Make it servable
if dashboard:
    dashboard.servable()
