"""
Modal Functions: ML Inference and Training
Serverless functions for time-series forecasting and ML model training.
"""
import os
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

try:
    import modal
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False
    print("Modal not available. Install with: pip install modal")

if MODAL_AVAILABLE:
    # Create Modal app
    app = modal.App("variosync-ml")
    
    # Define image with ML dependencies
    ml_image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install([
            "pandas>=2.0.0",
            "numpy>=1.24.0",
            "prophet>=1.1.5",
            "lightgbm>=4.0.0",
            "scikit-learn>=1.3.0",
            "boto3>=1.28.0",
        ])
    )
    
    @app.function(
        image=ml_image,
        secrets=[
            modal.Secret.from_name("aws-credentials"),
            modal.Secret.from_name("supabase-credentials"),
        ],
        timeout=3600,  # 1 hour timeout
        gpu="T4",  # Optional GPU for deep learning models
    )
    def prophet_forecast(
        data: Dict[str, Any],
        periods: int = 30,
        frequency: str = "D"
    ) -> Dict[str, Any]:
        """
        Generate Prophet forecast for time-series data.
        
        Args:
            data: Dictionary with 'ds' (dates) and 'y' (values) keys
            periods: Number of periods to forecast
            frequency: Frequency of data ('D', 'H', 'W', 'M', etc.)
            
        Returns:
            Dictionary with forecast results
        """
        try:
            from prophet import Prophet
            
            # Prepare data
            df = pd.DataFrame(data)
            df['ds'] = pd.to_datetime(df['ds'])
            
            # Fit model
            model = Prophet()
            model.fit(df)
            
            # Make future dataframe
            future = model.make_future_dataframe(periods=periods, freq=frequency)
            
            # Generate forecast
            forecast = model.predict(future)
            
            # Return results
            return {
                "success": True,
                "forecast": forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records'),
                "model_params": model.params,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @app.function(
        image=ml_image,
        secrets=[
            modal.Secret.from_name("aws-credentials"),
            modal.Secret.from_name("supabase-credentials"),
        ],
        timeout=3600,
    )
    def lightgbm_forecast(
        features: List[List[float]],
        targets: List[float],
        forecast_periods: int = 30,
        n_estimators: int = 100
    ) -> Dict[str, Any]:
        """
        Generate LightGBM forecast for time-series data.
        
        Args:
            features: Feature matrix (list of lists)
            targets: Target values (list)
            forecast_periods: Number of periods to forecast
            n_estimators: Number of boosting rounds
            
        Returns:
            Dictionary with forecast results
        """
        try:
            import lightgbm as lgb
            from sklearn.model_selection import train_test_split
            
            # Prepare data
            X = np.array(features)
            y = np.array(targets)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            train_data = lgb.Dataset(X_train, label=y_train)
            model = lgb.train(
                {
                    'objective': 'regression',
                    'metric': 'rmse',
                    'num_leaves': 31,
                    'learning_rate': 0.05,
                },
                train_data,
                num_boost_round=n_estimators,
            )
            
            # Evaluate
            predictions = model.predict(X_test)
            rmse = np.sqrt(np.mean((predictions - y_test) ** 2))
            
            # Generate forecast (using last features)
            last_features = X[-forecast_periods:]
            forecast = model.predict(last_features)
            
            return {
                "success": True,
                "forecast": forecast.tolist(),
                "rmse": float(rmse),
                "feature_importance": model.feature_importance().tolist(),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @app.function(
        image=ml_image,
        secrets=[
            modal.Secret.from_name("aws-credentials"),
            modal.Secret.from_name("supabase-credentials"),
        ],
        timeout=7200,  # 2 hours for training
        gpu="T4",
    )
    def train_tft_model(
        data_path: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Train Temporal Fusion Transformer (TFT) model.
        
        Args:
            data_path: Path to training data in Wasabi/S3
            config: Model configuration dictionary
            
        Returns:
            Dictionary with training results and model path
        """
        try:
            import boto3
            
            # Download data from Wasabi/S3
            s3_client = boto3.client(
                's3',
                endpoint_url=os.environ.get('AWS_ENDPOINT_URL'),
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            )
            
            bucket = os.environ.get('AWS_BUCKET_NAME')
            local_path = f"/tmp/{os.path.basename(data_path)}"
            
            s3_client.download_file(bucket, data_path, local_path)
            
            # Load data
            df = pd.read_parquet(local_path)
            
            # TODO: Implement TFT training
            # This would require pytorch-forecasting or similar library
            
            # For now, return placeholder
            return {
                "success": True,
                "message": "TFT training not yet implemented",
                "data_shape": df.shape,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
