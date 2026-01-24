"""
VARIOSYNC Main Application Entry Point
Orchestrates the VARIOSYNC time-series data processing system.
"""
import os

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def test_database_connection():
    """
    Test database connection using environment variables.
    Only runs when this script is executed directly.
    """
    import psycopg2

    # Fetch variables (using DB_ prefix to avoid conflicts with system env vars)
    db_user = os.getenv("DB_USER") or os.getenv("user")
    db_password = os.getenv("DB_PASSWORD") or os.getenv("password")
    db_host = os.getenv("DB_HOST") or os.getenv("host")
    db_port = os.getenv("DB_PORT") or os.getenv("port")
    db_name = os.getenv("DB_NAME") or os.getenv("dbname")

    try:
        connection = psycopg2.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            dbname=db_name
        )
        print("Connection successful!")

        # Create a cursor to execute SQL queries
        cursor = connection.cursor()

        # Example query
        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()
        print("Current Time:", result)

        # Close the cursor and connection
        cursor.close()
        connection.close()
        print("Connection closed.")

    except Exception as e:
        print(f"Failed to connect: {e}")


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
    # Run database connection test if --test-db flag is provided
    import sys
    if "--test-db" in sys.argv:
        test_database_connection()
    else:
        from app.cli import main as cli_main
        cli_main()
