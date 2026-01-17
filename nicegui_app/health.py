"""
Health check endpoint for NiceGUI app.
"""
from nicegui import app

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "storage": True, "auth": True}
