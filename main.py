"""
VARIOSYNC Main Application Entry Point
Orchestrates the VARIOSYNC time-series data processing system.
"""
# Import from new modular structure
from app import VariosyncApp
from app.cli import main

# Re-export for backward compatibility
__all__ = ['VariosyncApp', 'main']

# Keep old class name for backward compatibility
class VariosyncApp:
    """Main VARIOSYNC application class (backward compatibility wrapper)."""
    # Delegate to new implementation
    def __init__(self, *args, **kwargs):
        from app.core import VariosyncApp as CoreApp
        self._app = CoreApp(*args, **kwargs)
        # Copy attributes for backward compatibility
        self.config = self._app.config
        self.storage = self._app.storage
        self.auth_manager = self._app.auth_manager
        self.processor = self._app.processor
    
    def __getattr__(self, name):
        """Delegate method calls to core app."""
        return getattr(self._app, name)


if __name__ == "__main__":
    from app.cli import main as cli_main
    cli_main()
