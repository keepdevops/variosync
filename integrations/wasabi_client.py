"""
Wasabi (S3-compatible) Integration
Provides presigned URL generation for large file uploads/downloads.
"""
import os
from typing import Optional
from datetime import timedelta
from logger import get_logger

logger = get_logger()

try:
    import boto3
    from botocore.client import Config
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logger.warning("boto3 not available. Install with: pip install boto3")


class WasabiClient:
    """Client for Wasabi (S3-compatible) operations."""
    
    def __init__(
        self,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        bucket_name: Optional[str] = None,
        region: str = "us-east-1"
    ):
        """
        Initialize Wasabi client.

        Args:
            access_key_id: Wasabi access key (from env: WASABI_ACCESS_KEY_ID)
            secret_access_key: Wasabi secret key (from env: WASABI_SECRET_ACCESS_KEY)
            endpoint_url: Wasabi endpoint (from env: WASABI_ENDPOINT)
            bucket_name: Bucket name (from env: WASABI_BUCKET)
            region: AWS region (default: us-east-1)
        """
        logger.debug("[WasabiClient.__init__] Initializing Wasabi client")

        if not BOTO3_AVAILABLE:
            logger.error("[WasabiClient.__init__] boto3 library not installed")
            raise ImportError("boto3 library not installed")

        self.access_key_id = access_key_id or os.getenv("WASABI_ACCESS_KEY_ID") or os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_access_key = secret_access_key or os.getenv("WASABI_SECRET_ACCESS_KEY") or os.getenv("AWS_SECRET_ACCESS_KEY")
        self.endpoint_url = endpoint_url or os.getenv("WASABI_ENDPOINT") or os.getenv("AWS_ENDPOINT_URL")
        self.bucket_name = bucket_name or os.getenv("WASABI_BUCKET") or os.getenv("AWS_BUCKET_NAME")
        self.region = region

        # Log configuration status (without exposing secrets)
        logger.debug(f"[WasabiClient.__init__] Access key configured: {bool(self.access_key_id)}")
        logger.debug(f"[WasabiClient.__init__] Secret key configured: {bool(self.secret_access_key)}")
        logger.debug(f"[WasabiClient.__init__] Endpoint URL: {self.endpoint_url}")
        logger.debug(f"[WasabiClient.__init__] Bucket name: {self.bucket_name}")
        logger.debug(f"[WasabiClient.__init__] Region: {self.region}")

        # Validate required credentials
        missing = []
        if not self.access_key_id:
            missing.append("access_key_id")
        if not self.secret_access_key:
            missing.append("secret_access_key")
        if not self.endpoint_url:
            missing.append("endpoint_url")
        if not self.bucket_name:
            missing.append("bucket_name")

        if missing:
            logger.error(f"[WasabiClient.__init__] Missing required credentials: {missing}")
            raise ValueError(f"Wasabi credentials missing: {', '.join(missing)}")

        # Create S3 client with Wasabi endpoint
        try:
            self.s3 = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                config=Config(signature_version='s3v4', region_name=self.region)
            )
            logger.info(f"[WasabiClient.__init__] Wasabi client initialized for bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"[WasabiClient.__init__] Failed to create S3 client: {e}", exc_info=True)
            raise
    
    def get_upload_url(
        self,
        key: str,
        expires_in: int = 3600,
        content_type: Optional[str] = None
    ) -> str:
        """
        Generate presigned URL for file upload.

        Args:
            key: Object key (filename/path in bucket)
            expires_in: URL expiration time in seconds (default: 1 hour)
            content_type: Content type (optional)

        Returns:
            Presigned URL for PUT operation
        """
        logger.debug(f"[WasabiClient.get_upload_url] Generating upload URL for key: {key}")

        # Validate key
        if not key:
            logger.error("[WasabiClient.get_upload_url] Empty key provided")
            raise ValueError("Object key cannot be empty")

        if not isinstance(key, str):
            logger.error(f"[WasabiClient.get_upload_url] Key must be string, got: {type(key)}")
            raise TypeError("Object key must be a string")

        # Validate expires_in
        if expires_in <= 0:
            logger.warning(f"[WasabiClient.get_upload_url] Invalid expires_in: {expires_in}, using default 3600")
            expires_in = 3600

        if expires_in > 604800:  # 7 days max for S3
            logger.warning(f"[WasabiClient.get_upload_url] expires_in exceeds max (604800), capping")
            expires_in = 604800

        try:
            params = {
                'Bucket': self.bucket_name,
                'Key': key
            }

            if content_type:
                params['ContentType'] = content_type
                logger.debug(f"[WasabiClient.get_upload_url] Content-Type: {content_type}")

            url = self.s3.generate_presigned_url(
                'put_object',
                Params=params,
                ExpiresIn=expires_in
            )

            logger.info(f"[WasabiClient.get_upload_url] Generated upload URL for {key}, expires in {expires_in}s")
            return url
        except Exception as e:
            logger.error(f"[WasabiClient.get_upload_url] Error generating upload URL for {key}: {e}", exc_info=True)
            raise
    
    def get_download_url(
        self,
        key: str,
        expires_in: int = 3600
    ) -> str:
        """
        Generate presigned URL for file download.

        Args:
            key: Object key (filename/path in bucket)
            expires_in: URL expiration time in seconds (default: 1 hour)

        Returns:
            Presigned URL for GET operation
        """
        logger.debug(f"[WasabiClient.get_download_url] Generating download URL for key: {key}")

        # Validate key
        if not key:
            logger.error("[WasabiClient.get_download_url] Empty key provided")
            raise ValueError("Object key cannot be empty")

        if not isinstance(key, str):
            logger.error(f"[WasabiClient.get_download_url] Key must be string, got: {type(key)}")
            raise TypeError("Object key must be a string")

        # Validate expires_in
        if expires_in <= 0:
            logger.warning(f"[WasabiClient.get_download_url] Invalid expires_in: {expires_in}, using default 3600")
            expires_in = 3600

        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expires_in
            )

            logger.info(f"[WasabiClient.get_download_url] Generated download URL for {key}, expires in {expires_in}s")
            return url
        except Exception as e:
            logger.error(f"[WasabiClient.get_download_url] Error generating download URL for {key}: {e}", exc_info=True)
            raise
    
    def upload_file(self, local_path: str, key: str, content_type: Optional[str] = None) -> bool:
        """
        Upload file directly to Wasabi.

        Args:
            local_path: Local file path
            key: Object key in bucket
            content_type: Content type (optional)

        Returns:
            True if successful
        """
        logger.debug(f"[WasabiClient.upload_file] Starting upload: {local_path} -> {key}")

        # Validate local_path
        if not local_path:
            logger.error("[WasabiClient.upload_file] Empty local_path provided")
            return False

        from pathlib import Path
        path_obj = Path(local_path)

        if not path_obj.exists():
            logger.error(f"[WasabiClient.upload_file] Local file not found: {local_path}")
            return False

        if not path_obj.is_file():
            logger.error(f"[WasabiClient.upload_file] Path is not a file: {local_path}")
            return False

        file_size = path_obj.stat().st_size
        logger.debug(f"[WasabiClient.upload_file] File size: {file_size} bytes ({file_size / 1024:.2f} KB)")

        # Validate key
        if not key:
            logger.error("[WasabiClient.upload_file] Empty key provided")
            return False

        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
                logger.debug(f"[WasabiClient.upload_file] Content-Type: {content_type}")

            self.s3.upload_file(local_path, self.bucket_name, key, ExtraArgs=extra_args if extra_args else None)
            logger.info(f"[WasabiClient.upload_file] Successfully uploaded {local_path} to {key} ({file_size} bytes)")
            return True
        except Exception as e:
            logger.error(f"[WasabiClient.upload_file] Error uploading {local_path} to {key}: {e}", exc_info=True)
            return False
    
    def download_file(self, key: str, local_path: str) -> bool:
        """
        Download file directly from Wasabi.

        Args:
            key: Object key in bucket
            local_path: Local file path to save to

        Returns:
            True if successful
        """
        logger.debug(f"[WasabiClient.download_file] Starting download: {key} -> {local_path}")

        # Validate key
        if not key:
            logger.error("[WasabiClient.download_file] Empty key provided")
            return False

        # Validate local_path
        if not local_path:
            logger.error("[WasabiClient.download_file] Empty local_path provided")
            return False

        from pathlib import Path
        path_obj = Path(local_path)

        # Ensure parent directory exists
        try:
            path_obj.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"[WasabiClient.download_file] Cannot create parent directory: {e}")
            return False

        try:
            self.s3.download_file(self.bucket_name, key, local_path)

            # Verify download
            if path_obj.exists():
                file_size = path_obj.stat().st_size
                logger.info(f"[WasabiClient.download_file] Successfully downloaded {key} to {local_path} ({file_size} bytes)")
                return True
            else:
                logger.error(f"[WasabiClient.download_file] Download completed but file not found: {local_path}")
                return False
        except Exception as e:
            logger.error(f"[WasabiClient.download_file] Error downloading {key}: {e}", exc_info=True)
            return False
    
    def delete_file(self, key: str) -> bool:
        """
        Delete file from Wasabi.

        Args:
            key: Object key in bucket

        Returns:
            True if successful
        """
        logger.debug(f"[WasabiClient.delete_file] Deleting key: {key}")

        # Validate key
        if not key:
            logger.error("[WasabiClient.delete_file] Empty key provided")
            return False

        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"[WasabiClient.delete_file] Successfully deleted {key}")
            return True
        except Exception as e:
            logger.error(f"[WasabiClient.delete_file] Error deleting {key}: {e}", exc_info=True)
            return False
    
    def list_files(self, prefix: str = "", max_keys: int = 1000) -> list:
        """
        List files in bucket with prefix.

        Args:
            prefix: Key prefix to filter by
            max_keys: Maximum number of keys to return (default: 1000)

        Returns:
            List of object keys
        """
        logger.debug(f"[WasabiClient.list_files] Listing files with prefix: '{prefix}'")

        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )

            if 'Contents' not in response:
                logger.debug(f"[WasabiClient.list_files] No files found with prefix: '{prefix}'")
                return []

            keys = [obj['Key'] for obj in response['Contents']]
            total_size = sum(obj.get('Size', 0) for obj in response['Contents'])

            logger.info(f"[WasabiClient.list_files] Found {len(keys)} files with prefix '{prefix}' (total size: {total_size} bytes)")

            if response.get('IsTruncated'):
                logger.warning(f"[WasabiClient.list_files] Results truncated, more files exist beyond {max_keys}")

            return keys
        except Exception as e:
            logger.error(f"[WasabiClient.list_files] Error listing files with prefix '{prefix}': {e}", exc_info=True)
            return []


class WasabiClientFactory:
    """Factory for creating Wasabi clients."""
    
    @staticmethod
    def create_from_env() -> Optional[WasabiClient]:
        """Create client from environment variables."""
        if not BOTO3_AVAILABLE:
            logger.warning("boto3 not available")
            return None
        
        try:
            return WasabiClient()
        except Exception as e:
            logger.error(f"Error creating Wasabi client: {e}")
            return None
