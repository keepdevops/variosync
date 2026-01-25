"""
VARIOSYNC Storage Implementation Module
Concrete storage backend implementations.
"""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from logger import get_logger
from storage_base import StorageBackend

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

logger = get_logger()


class LocalStorage(StorageBackend):
    """Local filesystem storage backend."""
    
    def __init__(self, base_path: str = "data"):
        """
        Initialize local storage.
        
        Args:
            base_path: Base directory path
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized local storage at {self.base_path}")
    
    def save(self, key: str, data: bytes, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Save data to local filesystem."""
        try:
            file_path = self.base_path / key
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "wb") as f:
                f.write(data)
            
            logger.debug(f"Saved {key} to local storage")
            return True
        except Exception as e:
            logger.error(f"Error saving {key} to local storage: {e}")
            return False
    
    def load(self, key: str) -> Optional[bytes]:
        """Load data from local filesystem."""
        try:
            file_path = self.base_path / key
            
            if not file_path.exists():
                logger.warning(f"File not found: {key}")
                return None
            
            with open(file_path, "rb") as f:
                data = f.read()
            
            logger.debug(f"Loaded {key} from local storage")
            return data
        except Exception as e:
            logger.error(f"Error loading {key} from local storage: {e}")
            return None
    
    def exists(self, key: str) -> bool:
        """Check if file exists."""
        file_path = self.base_path / key
        return file_path.exists()
    
    def delete(self, key: str) -> bool:
        """Delete file from local filesystem."""
        try:
            file_path = self.base_path / key
            
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted {key} from local storage")
                return True
            else:
                logger.warning(f"File not found for deletion: {key}")
                return False
        except Exception as e:
            logger.error(f"Error deleting {key} from local storage: {e}")
            return False
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List files with optional prefix."""
        try:
            prefix_path = self.base_path / prefix if prefix else self.base_path
            keys = []
            
            if prefix_path.exists() and prefix_path.is_dir():
                for file_path in prefix_path.rglob("*"):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(self.base_path)
                        keys.append(str(rel_path))
            
            return keys
        except Exception as e:
            logger.error(f"Error listing keys with prefix {prefix}: {e}")
            return []
    
    def get_size(self, key: str) -> Optional[int]:
        """Get file size in bytes."""
        try:
            file_path = self.base_path / key
            if file_path.exists() and file_path.is_file():
                return file_path.stat().st_size
            return None
        except Exception as e:
            logger.error(f"Error getting size for {key}: {e}")
            return None


class S3Storage(StorageBackend):
    """S3-compatible storage backend (AWS S3, Wasabi, etc.)."""

    def __init__(
        self,
        bucket_name: str,
        endpoint_url: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None
    ):
        """
        Initialize S3 storage.

        Args:
            bucket_name: S3 bucket name
            endpoint_url: Custom endpoint URL (for Wasabi, etc.)
            access_key_id: AWS access key ID
            secret_access_key: AWS secret access key
        """
        logger.debug("[S3Storage.__init__] Initializing S3 storage")

        if not BOTO3_AVAILABLE:
            logger.error("[S3Storage.__init__] boto3 library not available")
            raise ImportError("boto3 is required for S3 storage. Install with: pip install boto3")

        # Validate bucket_name
        if not bucket_name:
            logger.error("[S3Storage.__init__] Empty bucket_name provided")
            raise ValueError("Bucket name cannot be empty")

        self.bucket_name = bucket_name

        # Get credentials from parameters or environment
        access_key = access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")

        # Log configuration status
        logger.debug(f"[S3Storage.__init__] Bucket name: {bucket_name}")
        logger.debug(f"[S3Storage.__init__] Access key configured: {bool(access_key)}")
        logger.debug(f"[S3Storage.__init__] Secret key configured: {bool(secret_key)}")

        # Create S3 client
        s3_config = {}
        if endpoint_url:
            s3_config["endpoint_url"] = endpoint_url
            logger.debug(f"[S3Storage.__init__] Using custom endpoint: {endpoint_url}")
        elif os.getenv("AWS_ENDPOINT_URL"):
            s3_config["endpoint_url"] = os.getenv("AWS_ENDPOINT_URL")
            logger.debug(f"[S3Storage.__init__] Using endpoint from env: {s3_config['endpoint_url']}")

        try:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                **s3_config
            )
            logger.info(f"[S3Storage.__init__] Initialized S3 storage for bucket: {bucket_name}")
        except Exception as e:
            logger.error(f"[S3Storage.__init__] Failed to create S3 client: {e}", exc_info=True)
            raise
    
    def save(self, key: str, data: bytes, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Save data to S3."""
        logger.debug(f"[S3Storage.save] Saving key: {key}")

        # Validate key
        if not key:
            logger.error("[S3Storage.save] Empty key provided")
            return False

        # Validate data
        if data is None:
            logger.error("[S3Storage.save] Data is None")
            return False

        if not isinstance(data, bytes):
            logger.error(f"[S3Storage.save] Data must be bytes, got: {type(data)}")
            return False

        data_size = len(data)
        logger.debug(f"[S3Storage.save] Data size: {data_size} bytes ({data_size / 1024:.2f} KB)")

        try:
            extra_args = {}
            if metadata:
                extra_args["Metadata"] = {str(k): str(v) for k, v in metadata.items()}
                logger.debug(f"[S3Storage.save] Metadata keys: {list(metadata.keys())}")

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
                **extra_args
            )

            logger.info(f"[S3Storage.save] Successfully saved {key} to S3 ({data_size} bytes)")
            return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"[S3Storage.save] Error saving {key} to S3 (code: {error_code}): {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"[S3Storage.save] Unexpected error saving {key}: {e}", exc_info=True)
            return False
    
    def load(self, key: str) -> Optional[bytes]:
        """Load data from S3."""
        logger.debug(f"[S3Storage.load] Loading key: {key}")

        # Validate key
        if not key:
            logger.error("[S3Storage.load] Empty key provided")
            return None

        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            data = response["Body"].read()

            data_size = len(data) if data else 0
            content_type = response.get("ContentType", "unknown")
            logger.info(f"[S3Storage.load] Successfully loaded {key} from S3 ({data_size} bytes, type: {content_type})")
            return data
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "NoSuchKey":
                logger.warning(f"[S3Storage.load] Key not found in S3: {key}")
            else:
                logger.error(f"[S3Storage.load] Error loading {key} from S3 (code: {error_code}): {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"[S3Storage.load] Unexpected error loading {key}: {e}", exc_info=True)
            return None
    
    def exists(self, key: str) -> bool:
        """Check if key exists in S3."""
        logger.debug(f"[S3Storage.exists] Checking key: {key}")

        if not key:
            logger.error("[S3Storage.exists] Empty key provided")
            return False

        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            logger.debug(f"[S3Storage.exists] Key exists: {key}")
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "404":
                logger.debug(f"[S3Storage.exists] Key does not exist: {key}")
            else:
                logger.debug(f"[S3Storage.exists] Error checking key {key}: {error_code}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete data from S3."""
        logger.debug(f"[S3Storage.delete] Deleting key: {key}")

        if not key:
            logger.error("[S3Storage.delete] Empty key provided")
            return False

        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"[S3Storage.delete] Successfully deleted {key} from S3")
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(f"[S3Storage.delete] Error deleting {key} from S3 (code: {error_code}): {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"[S3Storage.delete] Unexpected error deleting {key}: {e}", exc_info=True)
            return False
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List keys with optional prefix."""
        logger.debug(f"[S3Storage.list_keys] Listing keys with prefix: '{prefix}'")

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )

            if "Contents" not in response:
                logger.debug(f"[S3Storage.list_keys] No keys found with prefix: '{prefix}'")
                return []

            keys = [obj["Key"] for obj in response["Contents"]]
            total_size = sum(obj.get("Size", 0) for obj in response["Contents"])

            logger.info(f"[S3Storage.list_keys] Found {len(keys)} keys with prefix '{prefix}' (total size: {total_size} bytes)")

            if response.get("IsTruncated"):
                logger.warning(f"[S3Storage.list_keys] Results truncated, more keys exist")

            return keys
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(f"[S3Storage.list_keys] Error listing keys with prefix '{prefix}' (code: {error_code}): {e}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"[S3Storage.list_keys] Unexpected error: {e}", exc_info=True)
            return []
    
    def get_size(self, key: str) -> Optional[int]:
        """Get object size in bytes."""
        logger.debug(f"[S3Storage.get_size] Getting size for key: {key}")

        if not key:
            logger.error("[S3Storage.get_size] Empty key provided")
            return None

        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            size = response.get("ContentLength")
            logger.debug(f"[S3Storage.get_size] Size of {key}: {size} bytes")
            return size
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "404":
                logger.debug(f"[S3Storage.get_size] Key not found: {key}")
                return None
            logger.error(f"[S3Storage.get_size] Error getting size for {key} (code: {error_code}): {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"[S3Storage.get_size] Unexpected error: {e}", exc_info=True)
            return None
