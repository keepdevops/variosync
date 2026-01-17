"""
Modal Functions: File Format Conversions
Serverless functions for converting between file formats.
"""
import os
from typing import Dict, Any
import pandas as pd

try:
    import modal
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False
    app = None
    processing_image = None

if MODAL_AVAILABLE:
    app = modal.App("variosync-processing")
    
    processing_image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install([
            "pandas>=2.0.0",
            "pyarrow>=12.0.0",
            "fastparquet>=2023.8.0",
            "boto3>=1.28.0",
            "duckdb>=0.9.0",
        ])
    )
    
    @app.function(
        image=processing_image,
        secrets=[
            modal.Secret.from_name("aws-credentials"),
        ],
        timeout=3600,
        memory=4096,
    )
    def convert_csv_to_parquet(
        source_path: str,
        destination_path: str,
        chunk_size: int = 100000,
        compression: str = "snappy"
    ) -> Dict[str, Any]:
        """
        Convert large CSV file to Parquet format.
        
        Args:
            source_path: S3/Wasabi path to source CSV
            destination_path: S3/Wasabi path for output Parquet
            chunk_size: Number of rows to process at a time
            compression: Compression codec ('snappy', 'gzip', 'brotli', etc.)
            
        Returns:
            Dictionary with conversion results
        """
        try:
            import boto3
            
            s3_client = boto3.client(
                's3',
                endpoint_url=os.environ.get('AWS_ENDPOINT_URL'),
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            )
            
            bucket = os.environ.get('AWS_BUCKET_NAME')
            local_csv = f"/tmp/{os.path.basename(source_path)}"
            local_parquet = f"/tmp/{os.path.basename(destination_path)}"
            
            s3_client.download_file(bucket, source_path, local_csv)
            
            first_chunk = True
            total_rows = 0
            
            for chunk in pd.read_csv(local_csv, chunksize=chunk_size):
                total_rows += len(chunk)
                
                if first_chunk:
                    chunk.to_parquet(
                        local_parquet,
                        compression=compression,
                        engine='pyarrow'
                    )
                    first_chunk = False
                else:
                    chunk.to_parquet(
                        local_parquet,
                        compression=compression,
                        engine='pyarrow',
                        append=True
                    )
            
            s3_client.upload_file(local_parquet, bucket, destination_path)
            
            os.remove(local_csv)
            os.remove(local_parquet)
            
            return {
                "success": True,
                "rows_processed": total_rows,
                "source_path": source_path,
                "destination_path": destination_path,
                "compression": compression,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
