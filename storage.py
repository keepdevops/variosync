"""
VARIOSYNC Storage Module
Factory for creating storage backends.
"""
import os
from typing import Optional

import os
from typing import Optional

from logger import get_logger
from storage_base import StorageBackend
from storage_impl import LocalStorage, S3Storage

logger = get_logger()


class StorageFactory:
    """Factory for creating storage backends."""
    
    @staticmethod
    def create(
        backend_type: str,
        base_path: Optional[str] = None,
        bucket_name: Optional[str] = None,
        endpoint_url: Optional[str] = None
    ) -> StorageBackend:
        """
        Create storage backend instance.
        
        Args:
            backend_type: Storage backend type (local, s3, wasabi)
            base_path: Base path for local storage
            bucket_name: Bucket name for S3/Wasabi
            endpoint_url: Endpoint URL for S3-compatible storage
            
        Returns:
            Storage backend instance
        """
        if backend_type == "local":
            path = base_path or "data"
            return LocalStorage(path)
        elif backend_type in ["s3", "wasabi"]:
            if not bucket_name:
                bucket_name = os.getenv("AWS_BUCKET_NAME", "variosync-data")
            return S3Storage(bucket_name, endpoint_url)
        else:
            logger.warning(f"Unknown storage backend: {backend_type}, using local")
            return LocalStorage(base_path or "data")
