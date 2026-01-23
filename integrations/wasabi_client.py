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
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 library not installed")
        
        self.access_key_id = access_key_id or os.getenv("WASABI_ACCESS_KEY_ID") or os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_access_key = secret_access_key or os.getenv("WASABI_SECRET_ACCESS_KEY") or os.getenv("AWS_SECRET_ACCESS_KEY")
        self.endpoint_url = endpoint_url or os.getenv("WASABI_ENDPOINT") or os.getenv("AWS_ENDPOINT_URL")
        self.bucket_name = bucket_name or os.getenv("WASABI_BUCKET") or os.getenv("AWS_BUCKET_NAME")
        self.region = region
        
        if not all([self.access_key_id, self.secret_access_key, self.endpoint_url, self.bucket_name]):
            raise ValueError("Wasabi credentials must be provided")
        
        # Create S3 client with Wasabi endpoint
        self.s3 = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            config=Config(signature_version='s3v4', region_name=self.region)
        )
        
        logger.info(f"Wasabi client initialized for bucket: {self.bucket_name}")
    
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
        try:
            params = {
                'Bucket': self.bucket_name,
                'Key': key
            }
            
            if content_type:
                params['ContentType'] = content_type
            
            url = self.s3.generate_presigned_url(
                'put_object',
                Params=params,
                ExpiresIn=expires_in
            )
            
            logger.debug(f"Generated upload URL for {key}, expires in {expires_in}s")
            return url
        except Exception as e:
            logger.error(f"Error generating upload URL for {key}: {e}")
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
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expires_in
            )
            
            logger.debug(f"Generated download URL for {key}, expires in {expires_in}s")
            return url
        except Exception as e:
            logger.error(f"Error generating download URL for {key}: {e}")
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
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.s3.upload_file(local_path, self.bucket_name, key, ExtraArgs=extra_args)
            logger.info(f"Uploaded {local_path} to {key}")
            return True
        except Exception as e:
            logger.error(f"Error uploading {local_path} to {key}: {e}")
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
        try:
            self.s3.download_file(self.bucket_name, key, local_path)
            logger.info(f"Downloaded {key} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"Error downloading {key}: {e}")
            return False
    
    def delete_file(self, key: str) -> bool:
        """
        Delete file from Wasabi.
        
        Args:
            key: Object key in bucket
        
        Returns:
            True if successful
        """
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Deleted {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting {key}: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> list:
        """
        List files in bucket with prefix.
        
        Args:
            prefix: Key prefix to filter by
        
        Returns:
            List of object keys
        """
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            return [obj['Key'] for obj in response['Contents']]
        except Exception as e:
            logger.error(f"Error listing files with prefix {prefix}: {e}")
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
