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
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is required for S3 storage. Install with: pip install boto3")
        
        self.bucket_name = bucket_name
        
        # Get credentials from parameters or environment
        access_key = access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        
        # Create S3 client
        s3_config = {}
        if endpoint_url:
            s3_config["endpoint_url"] = endpoint_url
        elif os.getenv("AWS_ENDPOINT_URL"):
            s3_config["endpoint_url"] = os.getenv("AWS_ENDPOINT_URL")
        
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            **s3_config
        )
        
        logger.info(f"Initialized S3 storage for bucket {bucket_name}")
    
    def save(self, key: str, data: bytes, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Save data to S3."""
        try:
            extra_args = {}
            if metadata:
                extra_args["Metadata"] = {str(k): str(v) for k, v in metadata.items()}
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
                **extra_args
            )
            
            logger.debug(f"Saved {key} to S3")
            return True
        except ClientError as e:
            logger.error(f"Error saving {key} to S3: {e}")
            return False
    
    def load(self, key: str) -> Optional[bytes]:
        """Load data from S3."""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            data = response["Body"].read()
            
            logger.debug(f"Loaded {key} from S3")
            return data
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.warning(f"Key not found in S3: {key}")
            else:
                logger.error(f"Error loading {key} from S3: {e}")
            return None
    
    def exists(self, key: str) -> bool:
        """Check if key exists in S3."""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete data from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.debug(f"Deleted {key} from S3")
            return True
        except ClientError as e:
            logger.error(f"Error deleting {key} from S3: {e}")
            return False
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List keys with optional prefix."""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if "Contents" not in response:
                return []
            
            return [obj["Key"] for obj in response["Contents"]]
        except ClientError as e:
            logger.error(f"Error listing keys with prefix {prefix}: {e}")
            return []
