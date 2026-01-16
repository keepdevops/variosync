"""
VARIOSYNC Web Routes Module
FastAPI route handlers.
"""
import os
from datetime import datetime
from typing import List, Optional

from fastapi import File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from auth import AuthenticationError, PaymentError
from logger import get_logger
from main import VariosyncApp

logger = get_logger()


# Pydantic models
class TimeSeriesRecord(BaseModel):
    """Time-series data record model."""
    series_id: str
    timestamp: str
    measurements: dict
    metadata: Optional[dict] = None
    format: Optional[str] = None


class FinancialRecord(BaseModel):
    """Financial data record model."""
    ticker: str
    timestamp: str
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: float
    vol: Optional[int] = None
    format: Optional[str] = None


class ProcessRequest(BaseModel):
    """Process data request model."""
    records: List[dict]
    record_type: str = "time_series"


class AuthRequest(BaseModel):
    """Authentication request model."""
    license_key: str
    required_hours: float = 0.0


class APIRequest(BaseModel):
    """API download request model."""
    api_config: dict
    entity_id: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


_variosync_app = None


def get_app():
    """Get or create VARIOSYNC app instance."""
    global _variosync_app
    if _variosync_app is None:
        config_path = os.getenv("VARIOSYNC_CONFIG", "config.json")
        _variosync_app = VariosyncApp(config_path)
    return _variosync_app


def register_routes(app):
    """Register all API routes."""
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "VARIOSYNC API",
            "version": "2.1.0",
            "status": "running",
            "endpoints": {
                "health": "/health",
                "api_docs": "/docs",
                "dashboard": "/dashboard"
            }
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        app_instance = get_app()
        return {
            "status": "healthy",
            "storage": app_instance.storage is not None,
            "auth": app_instance.auth_manager is not None
        }
    
    @app.post("/api/auth")
    async def authenticate(request: AuthRequest):
        """Authenticate user."""
        try:
            app_instance = get_app()
            user_id, hours = app_instance.authenticate_user(
                request.license_key,
                request.required_hours
            )
            return {
                "success": True,
                "user_id": user_id,
                "hours_remaining": hours
            }
        except (AuthenticationError, PaymentError) as e:
            raise HTTPException(status_code=401, detail=str(e))
    
    @app.post("/api/process")
    async def process_records(request: ProcessRequest):
        """Process time-series records."""
        try:
            app_instance = get_app()
            processed = app_instance.processor.process_batch(
                request.records,
                request.record_type
            )
            
            saved_count = 0
            for record in processed:
                if app_instance.processor.save_record(record):
                    saved_count += 1
            
            return {
                "success": True,
                "processed": len(processed),
                "saved": saved_count
            }
        except Exception as e:
            logger.error(f"Error processing records: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/upload")
    async def upload_file(
        file: UploadFile = File(...),
        record_type: str = Form("time_series"),
        file_format: Optional[str] = Form(None)
    ):
        """Upload and process a file."""
        try:
            temp_path = f"/tmp/{file.filename}"
            with open(temp_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            app_instance = get_app()
            success = app_instance.process_data_file(
                temp_path,
                record_type,
                file_format
            )
            
            os.remove(temp_path)
            
            if success:
                return {"success": True, "message": f"Processed {file.filename}"}
            else:
                raise HTTPException(status_code=400, detail="Failed to process file")
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/download")
    async def download_from_api(request: APIRequest):
        """Download data from API."""
        try:
            app_instance = get_app()
            
            start_date = None
            end_date = None
            
            if request.start_date:
                start_date = datetime.fromisoformat(request.start_date)
            if request.end_date:
                end_date = datetime.fromisoformat(request.end_date)
            
            success = app_instance.download_from_api(
                request.api_config,
                request.entity_id,
                start_date,
                end_date
            )
            
            return {"success": success}
        except Exception as e:
            logger.error(f"Error downloading from API: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/storage/list")
    async def list_storage_keys(prefix: str = ""):
        """List storage keys."""
        try:
            app_instance = get_app()
            if app_instance.storage:
                keys = app_instance.storage.list_keys(prefix)
                return {"keys": keys}
            else:
                return {"keys": []}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
