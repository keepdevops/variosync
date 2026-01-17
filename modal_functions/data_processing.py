"""
Modal Functions: Heavy Data Processing
Serverless functions for large-scale data processing tasks.
"""
import os
from typing import Dict, List, Optional, Any
import pandas as pd

try:
    import modal
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False
    print("Modal not available. Install with: pip install modal")

if MODAL_AVAILABLE:
    # Create Modal app
    app = modal.App("variosync-processing")
    
    # Define image with processing dependencies
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
        timeout=3600,  # 1 hour timeout
        memory=4096,  # 4GB RAM for large files
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
            
            # Download CSV
            s3_client.download_file(bucket, source_path, local_csv)
            
            # Convert in chunks
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
            
            # Upload Parquet
            s3_client.upload_file(local_parquet, bucket, destination_path)
            
            # Cleanup
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
    
    @app.function(
        image=processing_image,
        secrets=[
            modal.Secret.from_name("aws-credentials"),
        ],
        timeout=3600,
        memory=4096,
    )
    def clean_and_transform_data(
        data_path: str,
        output_path: str,
        transformations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Apply data cleaning and transformation operations.
        
        Args:
            data_path: S3/Wasabi path to source data
            output_path: S3/Wasabi path for output
            transformations: List of transformation operations
            
        Returns:
            Dictionary with processing results
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
            local_input = f"/tmp/{os.path.basename(data_path)}"
            local_output = f"/tmp/{os.path.basename(output_path)}"
            
            # Download data
            s3_client.download_file(bucket, data_path, local_input)
            
            # Load data
            if data_path.endswith('.parquet'):
                df = pd.read_parquet(local_input)
            elif data_path.endswith('.csv'):
                df = pd.read_csv(local_input)
            else:
                raise ValueError(f"Unsupported file format: {data_path}")
            
            original_rows = len(df)
            
            # Apply transformations
            for transform in transformations:
                op = transform.get('operation')
                params = transform.get('params', {})
                
                if op == 'drop_na':
                    df = df.dropna(**params)
                elif op == 'fill_na':
                    df = df.fillna(**params)
                elif op == 'filter':
                    column = params.get('column')
                    condition = params.get('condition')
                    if column and condition:
                        df = df.query(f"{column} {condition}")
                elif op == 'rename_columns':
                    df = df.rename(columns=params.get('mapping', {}))
                elif op == 'drop_columns':
                    df = df.drop(columns=params.get('columns', []))
                elif op == 'add_column':
                    column = params.get('column')
                    value = params.get('value')
                    if column:
                        df[column] = value
            
            # Save transformed data
            if output_path.endswith('.parquet'):
                df.to_parquet(local_output, compression='snappy')
            elif output_path.endswith('.csv'):
                df.to_csv(local_output, index=False)
            else:
                raise ValueError(f"Unsupported output format: {output_path}")
            
            # Upload result
            s3_client.upload_file(local_output, bucket, output_path)
            
            # Cleanup
            os.remove(local_input)
            os.remove(local_output)
            
            return {
                "success": True,
                "original_rows": original_rows,
                "final_rows": len(df),
                "rows_removed": original_rows - len(df),
                "transformations_applied": len(transformations),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @app.function(
        image=processing_image,
        secrets=[
            modal.Secret.from_name("aws-credentials"),
        ],
        timeout=7200,  # 2 hours for large batches
        memory=8192,  # 8GB RAM
    )
    def batch_process_files(
        file_paths: List[str],
        operation: str,
        output_prefix: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process multiple files in batch.
        
        Args:
            file_paths: List of S3/Wasabi paths to process
            operation: Operation to perform ('convert', 'clean', etc.)
            output_prefix: Prefix for output files
            **kwargs: Additional operation-specific parameters
            
        Returns:
            Dictionary with batch processing results
        """
        results = []
        success_count = 0
        error_count = 0
        
        for file_path in file_paths:
            try:
                if operation == 'convert':
                    output_path = f"{output_prefix}/{os.path.basename(file_path)}.parquet"
                    result = convert_csv_to_parquet.remote(
                        file_path,
                        output_path,
                        **kwargs
                    )
                elif operation == 'clean':
                    output_path = f"{output_prefix}/{os.path.basename(file_path)}"
                    result = clean_and_transform_data.remote(
                        file_path,
                        output_path,
                        kwargs.get('transformations', [])
                    )
                else:
                    result = {"success": False, "error": f"Unknown operation: {operation}"}
                
                results.append({
                    "file": file_path,
                    "result": result
                })
                
                if result.get("success"):
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                results.append({
                    "file": file_path,
                    "result": {"success": False, "error": str(e)}
                })
                error_count += 1
        
        return {
            "success": error_count == 0,
            "total_files": len(file_paths),
            "success_count": success_count,
            "error_count": error_count,
            "results": results,
        }
