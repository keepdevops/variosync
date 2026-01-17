"""
VARIOSYNC API Keys Manager Module
Handles secure storage and retrieval of API keys.
"""
import os
import json
from typing import Dict, List, Optional
from pathlib import Path

from logger import get_logger
from supabase_client import SupabaseClientFactory

logger = get_logger()


class APIKeysManager:
    """Manager for API keys storage and retrieval."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize API keys manager.
        
        Args:
            config_path: Path to config file for storing keys (optional)
        """
        self.config_path = config_path or "config.json"
        self.keys_file = Path("api_keys.json")  # Separate file for keys
        self.supabase_client = SupabaseClientFactory.create_from_env()
    
    def get_keys(self) -> List[Dict[str, str]]:
        """
        Get all stored API keys.
        
        Returns:
            List of API key dictionaries (with masked values)
        """
        keys = []
        
        # Try to load from file
        if self.keys_file.exists():
            try:
                with open(self.keys_file, 'r') as f:
                    data = json.load(f)
                    keys = data.get('keys', [])
            except Exception as e:
                logger.error(f"Error loading API keys from file: {e}")
        
        # Also check environment variables
        env_keys = self._get_keys_from_env()
        keys.extend(env_keys)
        
        # Mask sensitive values
        for key in keys:
            if 'api_key' in key and key['api_key']:
                key['api_key'] = self._mask_key(key['api_key'])
        
        return keys
    
    def _get_keys_from_env(self) -> List[Dict[str, str]]:
        """Get API keys from environment variables."""
        keys = []
        
        # Check common API key env vars
        env_vars = {
            'ALPHA_VANTAGE_API_KEY': 'Alpha Vantage',
            'OPENWEATHER_API_KEY': 'OpenWeather',
            'AWS_ACCESS_KEY_ID': 'AWS/Wasabi',
        }
        
        for env_var, name in env_vars.items():
            value = os.getenv(env_var)
            if value:
                keys.append({
                    'name': name,
                    'api_key': value,
                    'source': 'environment',
                    'description': f'From {env_var}'
                })
        
        return keys
    
    def _mask_key(self, key: str) -> str:
        """Mask API key for display."""
        if len(key) <= 8:
            return "*" * len(key)
        return key[:4] + "*" * (len(key) - 8) + key[-4:]
    
    def add_key(self, name: str, api_key: str, description: str = "") -> bool:
        """
        Add a new API key.
        
        Args:
            name: API name/provider
            api_key: API key value
            description: Optional description
            
        Returns:
            True if successful
        """
        try:
            # Load existing keys
            keys = []
            if self.keys_file.exists():
                try:
                    with open(self.keys_file, 'r') as f:
                        data = json.load(f)
                        keys = data.get('keys', [])
                except:
                    keys = []
            
            # Add new key
            keys.append({
                'name': name,
                'api_key': api_key,
                'description': description,
                'source': 'file',
                'added_at': str(Path(__file__).stat().st_mtime)  # Simple timestamp
            })
            
            # Save to file
            with open(self.keys_file, 'w') as f:
                json.dump({'keys': keys}, f, indent=2)
            
            logger.info(f"Added API key: {name}")
            return True
        except Exception as e:
            logger.error(f"Error adding API key: {e}")
            return False
    
    def delete_key(self, name: str) -> bool:
        """
        Delete an API key.
        
        Args:
            name: API name/provider
            
        Returns:
            True if successful
        """
        try:
            if not self.keys_file.exists():
                return False
            
            with open(self.keys_file, 'r') as f:
                data = json.load(f)
                keys = data.get('keys', [])
            
            # Remove key
            keys = [k for k in keys if k.get('name') != name]
            
            # Save updated keys
            with open(self.keys_file, 'w') as f:
                json.dump({'keys': keys}, f, indent=2)
            
            logger.info(f"Deleted API key: {name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting API key: {e}")
            return False
