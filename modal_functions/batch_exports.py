"""
Modal Functions: Batch Exports
Serverless functions for generating reports and batch exports.
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
    app = modal.App("variosync-exports")
    
    # Define image with export dependencies
    export_image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install([
            "pandas>=2.0.0",
            "pyarrow>=12.0.0",
            "openpyxl>=3.1.0",
            "boto3>=1.28.0",
        ])
    )
    
    @app.function(
        image=export_image,
        secrets=[
            modal.Secret.from_name("aws-credentials"),
        ],
        timeout=3600,
        memory=2048,
    )
    def export_to_format(
        data_path: str,
        output_path: str,
        format: str = "csv",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Export data to various formats.
        
        Args:
            data_path: S3/Wasabi path to source data
            output_path: S3/Wasabi path for output
            format: Output format ('csv', 'excel', 'json', 'parquet')
            **kwargs: Format-specific options
            
        Returns:
            Dictionary with export results
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
            
            # Download source data
            s3_client.download_file(bucket, data_path, local_input)
            
            # Load data
            if data_path.endswith('.parquet'):
                df = pd.read_parquet(local_input)
            elif data_path.endswith('.csv'):
                df = pd.read_csv(local_input)
            else:
                raise ValueError(f"Unsupported input format: {data_path}")
            
            # Export to requested format
            if format == 'csv':
                df.to_csv(local_output, index=False, **kwargs)
            elif format == 'excel':
                df.to_excel(local_output, index=False, **kwargs)
            elif format == 'json':
                df.to_json(local_output, orient='records', **kwargs)
            elif format == 'parquet':
                df.to_parquet(local_output, compression='snappy', **kwargs)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            # Upload result
            s3_client.upload_file(local_output, bucket, output_path)
            
            # Cleanup
            os.remove(local_input)
            os.remove(local_output)
            
            return {
                "success": True,
                "rows_exported": len(df),
                "format": format,
                "output_path": output_path,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @app.function(
        image=export_image,
        secrets=[
            modal.Secret.from_name("aws-credentials"),
        ],
        timeout=3600,
        memory=2048,
    )
    def generate_report(
        data_paths: List[str],
        report_config: Dict[str, Any],
        output_path: str
    ) -> Dict[str, Any]:
        """
        Generate comprehensive report from multiple data sources.
        
        Args:
            data_paths: List of S3/Wasabi paths to data sources
            report_config: Report configuration (tables, charts, summaries)
            output_path: S3/Wasabi path for output report
            
        Returns:
            Dictionary with report generation results
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
            
            # Load all data sources
            dataframes = {}
            for path in data_paths:
                local_path = f"/tmp/{os.path.basename(path)}"
                s3_client.download_file(bucket, path, local_path)
                
                if path.endswith('.parquet'):
                    df = pd.read_parquet(local_path)
                elif path.endswith('.csv'):
                    df = pd.read_csv(local_path)
                else:
                    continue
                
                dataframes[path] = df
                os.remove(local_path)
            
            # Generate report (simplified - would use reportlab or similar)
            report_content = []
            report_content.append("# VARIOSYNC Data Report\n\n")
            
            # Add summaries
            if 'summaries' in report_config:
                for summary in report_config['summaries']:
                    source = summary.get('source')
                    if source in dataframes:
                        df = dataframes[source]
                        report_content.append(f"## Summary: {summary.get('title', source)}\n\n")
                        report_content.append(f"Rows: {len(df)}\n")
                        report_content.append(f"Columns: {len(df.columns)}\n\n")
                        report_content.append(df.describe().to_markdown())
                        report_content.append("\n\n")
            
            # Save report
            local_report = f"/tmp/{os.path.basename(output_path)}"
            with open(local_report, 'w') as f:
                f.write(''.join(report_content))
            
            # Upload report
            s3_client.upload_file(local_report, bucket, output_path)
            os.remove(local_report)
            
            return {
                "success": True,
                "sources_processed": len(data_paths),
                "output_path": output_path,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
