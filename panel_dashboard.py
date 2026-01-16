"""
VARIOSYNC Panel Dashboard Module
Advanced interactive dashboard for time-series data visualization.
"""
import os
from datetime import datetime, timedelta
from typing import List, Optional

try:
    import panel as pn
    import pandas as pd
    PANEL_AVAILABLE = True
except ImportError:
    PANEL_AVAILABLE = False

from logger import get_logger
from main import VariosyncApp
from panel_components import DashboardComponents

logger = get_logger()

if PANEL_AVAILABLE:
    pn.extension("tabulator", "plotly", sizing_mode="stretch_width")


class VariosyncDashboard:
    """Interactive Panel dashboard for VARIOSYNC."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize dashboard.
        
        Args:
            config_path: Path to configuration file
        """
        if not PANEL_AVAILABLE:
            raise ImportError("Panel and pandas required. Install with: pip install panel pandas")
        
        self.app = VariosyncApp(config_path)
        self._create_dashboard()
    
    def _create_dashboard(self):
        """Create dashboard components."""
        components = DashboardComponents()
        
        # Create sections
        upload_section = components.create_upload_section()
        api_section = components.create_api_section()
        storage_section = components.create_storage_section()
        
        # Assign to instance
        self.upload_widget = upload_section["upload"]
        self.record_type_widget = upload_section["record_type"]
        self.file_format_widget = upload_section["file_format"]
        self.process_button = upload_section["process_button"]
        self.status_pane = upload_section["status"]
        
        self.api_name_widget = api_section["api_name"]
        self.api_url_widget = api_section["api_url"]
        self.api_key_widget = api_section["api_key"]
        self.entity_id_widget = api_section["entity_id"]
        self.download_button = api_section["download_button"]
        
        self.storage_prefix_widget = storage_section["prefix"]
        self.refresh_button = storage_section["refresh_button"]
        self.data_table = storage_section["data_table"]
        
        # Bind events
        self.process_button.on_click(self._handle_process)
        self.download_button.on_click(self._handle_download)
        self.refresh_button.on_click(self._handle_refresh)
        
        # Create layout
        self._create_layout()
    
    def _create_layout(self):
        """Create dashboard layout."""
        upload_section = pn.Column(
            pn.pane.Markdown("## 📤 Upload & Process Files"),
            pn.Row(
                self.upload_widget,
                self.record_type_widget,
                self.file_format_widget,
                self.process_button
            ),
            self.status_pane,
            margin=(10, 10)
        )
        
        api_section = pn.Column(
            pn.pane.Markdown("## 🌐 Download from API"),
            pn.Row(
                self.api_name_widget,
                self.api_url_widget,
                self.api_key_widget
            ),
            pn.Row(
                self.entity_id_widget,
                self.download_button
            ),
            margin=(10, 10)
        )
        
        storage_section = pn.Column(
            pn.pane.Markdown("## 💾 Storage Browser"),
            pn.Row(
                self.storage_prefix_widget,
                self.refresh_button
            ),
            self.data_table,
            margin=(10, 10)
        )
        
        self.dashboard = pn.Column(
            pn.pane.Markdown("# 🚀 VARIOSYNC Dashboard", style={"font-size": "2em"}),
            upload_section,
            api_section,
            storage_section,
            sizing_mode="stretch_width",
            margin=(20, 20)
        )
    
    def _handle_process(self, event):
        """Handle file processing."""
        if self.upload_widget.value is None:
            self.status_pane.alert_type = "warning"
            self.status_pane.object = "⚠️ No file selected"
            return
        
        try:
            # Save uploaded file
            temp_path = f"/tmp/{self.upload_widget.filename}"
            with open(temp_path, "wb") as f:
                f.write(self.upload_widget.value)
            
            file_format = None if self.file_format_widget.value == "auto" else self.file_format_widget.value
            
            success = self.app.process_data_file(
                temp_path,
                self.record_type_widget.value,
                file_format
            )
            
            os.remove(temp_path)
            
            if success:
                self.status_pane.alert_type = "success"
                self.status_pane.object = f"✅ Successfully processed {self.upload_widget.filename}"
                self._handle_refresh(None)
            else:
                self.status_pane.alert_type = "danger"
                self.status_pane.object = "❌ Processing failed"
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            self.status_pane.alert_type = "danger"
            self.status_pane.object = f"❌ Error: {str(e)}"
    
    def _handle_download(self, event):
        """Handle API download."""
        if not all([self.api_name_widget.value, self.api_url_widget.value, 
                   self.api_key_widget.value, self.entity_id_widget.value]):
            self.status_pane.alert_type = "warning"
            self.status_pane.object = "⚠️ Please fill all API fields"
            return
        
        try:
            api_config = {
                "name": self.api_name_widget.value,
                "base_url": self.api_url_widget.value,
                "endpoint": "/query",
                "api_key": self.api_key_widget.value,
                "entity_param": "symbol"
            }
            
            success = self.app.download_from_api(
                api_config,
                self.entity_id_widget.value
            )
            
            if success:
                self.status_pane.alert_type = "success"
                self.status_pane.object = f"✅ Downloaded data for {self.entity_id_widget.value}"
                self._handle_refresh(None)
            else:
                self.status_pane.alert_type = "danger"
                self.status_pane.object = "❌ Download failed"
        except Exception as e:
            logger.error(f"Error downloading from API: {e}")
            self.status_pane.alert_type = "danger"
            self.status_pane.object = f"❌ Error: {str(e)}"
    
    def _handle_refresh(self, event):
        """Refresh storage browser."""
        try:
            if self.app.storage:
                prefix = self.storage_prefix_widget.value or ""
                keys = self.app.storage.list_keys(prefix)
                
                # Create DataFrame
                df_data = []
                for key in keys[:1000]:  # Limit to 1000 for performance
                    df_data.append({
                        "Key": key,
                        "Size": "N/A",
                        "Modified": "N/A"
                    })
                
                self.data_table.value = pd.DataFrame(df_data)
                self.status_pane.alert_type = "info"
                self.status_pane.object = f"📊 Showing {len(df_data)} items"
            else:
                self.data_table.value = pd.DataFrame()
        except Exception as e:
            logger.error(f"Error refreshing storage: {e}")
            self.status_pane.alert_type = "danger"
            self.status_pane.object = f"❌ Error refreshing: {str(e)}"
    
    def serve(self, port: int = 5007, show: bool = True):
        """
        Serve the dashboard.
        
        Args:
            port: Port to serve on
            show: Whether to open browser automatically
        """
        self.dashboard.servable()
        self.dashboard.show(port=port, show=show)


def create_dashboard(config_path: Optional[str] = None) -> VariosyncDashboard:
    """
    Create and return dashboard instance.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dashboard instance
    """
    return VariosyncDashboard(config_path)


if __name__ == "__main__":
    dashboard = create_dashboard()
    dashboard.serve(port=5007)
