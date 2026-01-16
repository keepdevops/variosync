"""
VARIOSYNC Panel Time-Series Visualization Module
HoloViews plotting and data loading for time-series visualization.
"""
from datetime import datetime
from typing import Optional

try:
    import panel as pn
    import pandas as pd
    import holoviews as hv
    import hvplot.pandas
    hv.extension('bokeh')
    PANEL_AVAILABLE = True
    HVPLOT_AVAILABLE = True
except ImportError:
    PANEL_AVAILABLE = False
    HVPLOT_AVAILABLE = False

from logger import get_logger
from main import VariosyncApp
from supabase_client import SupabaseClient

logger = get_logger()


def load_timeseries_data(supabase_client=None, limit: int = 1000):
    """
    Load time-series data from Supabase or storage.
    
    Args:
        supabase_client: Optional Supabase client
        limit: Maximum records to load
        
    Returns:
        DataFrame with time-series data
    """
    try:
        if supabase_client:
            data = supabase_client.query_time_series(
                series_id="*",
                limit=limit
            )
            if data:
                return pd.DataFrame(data)
        
        # Fallback to local storage
        app = VariosyncApp()
        if app.storage:
            keys = app.storage.list_keys("data/")[:limit]
            records = []
            for key in keys:
                data_bytes = app.storage.load(key)
                if data_bytes:
                    import json
                    try:
                        record = json.loads(data_bytes.decode('utf-8'))
                        records.append(record)
                    except:
                        pass
            
            if records:
                return pd.DataFrame(records)
        
        return pd.DataFrame({
            'timestamp': [],
            'series_id': [],
            'value': []
        })
    except Exception as e:
        logger.error(f"Error loading time-series data: {e}")
        return pd.DataFrame()


@pn.cache
def get_timeseries_plot(supabase_client=None):
    """
    Create hvplot time-series plot.
    
    Args:
        supabase_client: Optional Supabase client
        
    Returns:
        HoloViews plot object
    """
    if not PANEL_AVAILABLE or not HVPLOT_AVAILABLE:
        return None
    
    df = load_timeseries_data(supabase_client)
    
    # Prepare data for plotting
    if 'timestamp' in df.columns and 'measurements' in df.columns:
        plot_data = []
        for _, row in df.iterrows():
            timestamp = pd.to_datetime(row['timestamp'])
            if isinstance(row['measurements'], dict):
                for key, value in row['measurements'].items():
                    if isinstance(value, (int, float)):
                        plot_data.append({
                            'time': timestamp,
                            'series': row.get('series_id', 'unknown'),
                            'metric': key,
                            'value': value
                        })
        
        plot_df = pd.DataFrame(plot_data)
        
        if not plot_df.empty:
            # Aggregate by time if multiple series exist, or use single series
            if plot_df['series'].nunique() > 1:
                # Aggregate values by time (mean)
                plot_df_agg = plot_df.groupby('time')['value'].mean().reset_index()
                plot_df_agg.columns = ['time', 'value']
            else:
                # Use single series data
                plot_df_agg = plot_df[['time', 'value']].copy()
            
            # Use hvplot for cleaner, more modern plotting
            plot = plot_df_agg.hvplot.line(
                x="time", y="value",
                responsive=True, min_height=450,
                line_width=2.5, color="#3b82f6",
                title="",
                xlabel="", ylabel="Metric Value",
                grid=True,
                tools=["hover", "pan", "box_zoom", "reset", "save"]
            ).opts(
                fontscale=1.1,
                toolbar="above"
            )
            return plot
    
    # Return empty plot if no data
    empty_df = pd.DataFrame({'time': [], 'value': []})
    return empty_df.hvplot.line(
        x="time", y="value",
        responsive=True, min_height=450,
        line_width=2.5, color="#3b82f6",
        title="",
        xlabel="", ylabel="Metric Value",
        grid=True,
        tools=["hover", "pan", "box_zoom", "reset", "save"]
    ).opts(
        fontscale=1.1,
        toolbar="above"
    )
