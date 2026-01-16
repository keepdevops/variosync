"""
VARIOSYNC Storage Base Module
Abstract base class for storage backends.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def save(self, key: str, data: bytes, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save data to storage.
        
        Args:
            key: Storage key/path
            data: Data to save
            metadata: Optional metadata
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[bytes]:
        """
        Load data from storage.
        
        Args:
            key: Storage key/path
            
        Returns:
            Data bytes or None if not found
        """
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if key exists in storage.
        
        Args:
            key: Storage key/path
            
        Returns:
            True if exists
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete data from storage.
        
        Args:
            key: Storage key/path
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def list_keys(self, prefix: str = "") -> List[str]:
        """
        List all keys with optional prefix.
        
        Args:
            prefix: Key prefix filter
            
        Returns:
            List of keys
        """
        pass
