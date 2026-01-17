"""
Modal Functions: Data Transformations
Serverless functions for data cleaning and transformation.
"""
import os
from typing import Dict, List, Any
import pandas as pd

try:
    import modal
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False

if MODAL_AVAILABLE:
    try:
        from .conversions import app, processing_image
    except ImportError:
        # Fallback if conversions module not available
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
            
            s3_client.download_file(bucket, data_path, local_input)
            
            if data_path.endswith('.parquet'):
                df = pd.read_parquet(local_input)
            elif data_path.endswith('.csv'):
                df = pd.read_csv(local_input)
            else:
                raise ValueError(f"Unsupported file format: {data_path}")
            
            original_rows = len(df)
            
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
            
            if output_path.endswith('.parquet'):
                df.to_parquet(local_output, compression='snappy')
            elif output_path.endswith('.csv'):
                df.to_csv(local_output, index=False)
            else:
                raise ValueError(f"Unsupported output format: {output_path}")
            
            s3_client.upload_file(local_output, bucket, output_path)
            
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
        timeout=7200,
        memory=8192,
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
        from .conversions import convert_csv_to_parquet
        
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
