"""
NiceGUI App Highcharts Visualization Functions
Highcharts-based plotting functions for time-series and financial data.
"""
import json
from typing import Optional, Tuple, List, Dict, Any

import pandas as pd

from logger import get_logger
from .visualization import (
    load_timeseries_data,
    get_available_series,
    is_financial_data,
    get_available_metrics,
    extract_ohlcv_data,
)

logger = get_logger()

# Helper function to safely convert values to float
def safe_float(value):
    """Safely convert a value to float, returning None if conversion fails."""
    if value is None:
        return None
    if pd.isna(value):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        logger.debug(f"Could not convert value to float: {value} (type: {type(value)})")
        return None

# Highcharts imports
try:
    import highcharts_core as highcharts
    HIGHCHARTS_AVAILABLE = True
except ImportError:
    HIGHCHARTS_AVAILABLE = False
    logger.warning("Highcharts not available. Install with: pip install highcharts-core")


def create_highcharts_financial_plot(
    df: pd.DataFrame, 
    series_id: Optional[str] = None, 
    chart_type: str = "candlestick", 
    show_volume: bool = True
) -> Optional[Dict[str, Any]]:
    """Create Highcharts financial chart configuration (candlestick or OHLC) with optional volume."""
    if not HIGHCHARTS_AVAILABLE:
        return None
    
    ohlcv = extract_ohlcv_data(df, series_id)
    
    if len(ohlcv['timestamp']) == 0:
        return None
    
    # Convert timestamps to milliseconds (Highcharts format)
    timestamps_ms = []
    for ts in ohlcv['timestamp']:
        try:
            dt = pd.to_datetime(ts)
            timestamps_ms.append(int(dt.timestamp() * 1000))
        except:
            continue
    
    # Prepare OHLC data
    ohlc_data = []
    for i in range(len(timestamps_ms)):
        if i < len(ohlcv['open']) and i < len(ohlcv['high']) and i < len(ohlcv['low']) and i < len(ohlcv['close']):
            ohlc_data.append([
                timestamps_ms[i],
                ohlcv['open'][i],
                ohlcv['high'][i],
                ohlcv['low'][i],
                ohlcv['close'][i]
            ])
    
    # Prepare volume data
    volume_data = []
    for i in range(len(timestamps_ms)):
        if i < len(ohlcv['volume']):
            volume_data.append([timestamps_ms[i], ohlcv['volume'][i]])
    
    # Determine series name
    if series_id:
        series_name = series_id
    elif 'series_id' in df.columns and len(df['series_id'].unique()) == 1:
        series_name = df['series_id'].iloc[0]
    else:
        series_name = "Financial Data"
    
    # Create chart configuration
    chart_config = {
        "chart": {
            "type": "candlestick" if chart_type == "candlestick" else "ohlc",
            "backgroundColor": "#1e1e1e",
            "style": {
                "fontFamily": "Arial, sans-serif"
            }
        },
        "title": {
            "text": f"{series_name} - {chart_type.upper()} Chart",
            "style": {
                "color": "#ffffff"
            }
        },
        "xAxis": {
            "type": "datetime",
            "labels": {
                "style": {
                    "color": "#ffffff"
                }
            },
            "gridLineColor": "#333333"
        },
        "yAxis": [
            {
                "title": {
                    "text": "Price",
                    "style": {
                        "color": "#ffffff"
                    }
                },
                "labels": {
                    "style": {
                        "color": "#ffffff"
                    }
                },
                "gridLineColor": "#333333",
                "height": "70%" if show_volume else "100%"
            }
        ],
        "series": [
            {
                "name": series_name,
                "data": ohlc_data,
                "upColor": "#26a69a",
                "color": "#ef5350",
                "lineColor": "#26a69a",
                "upLineColor": "#26a69a"
            }
        ],
        "legend": {
            "enabled": True,
            "itemStyle": {
                "color": "#ffffff"
            }
        },
        "plotOptions": {
            "candlestick" if chart_type == "candlestick" else "ohlc": {
                "color": "#ef5350",
                "upColor": "#26a69a",
                "lineColor": "#26a69a",
                "upLineColor": "#26a69a"
            }
        },
        "tooltip": {
            "backgroundColor": "#2d2d2d",
            "style": {
                "color": "#ffffff"
            }
        }
    }
    
    # Add volume subplot if requested
    if show_volume and any(v > 0 for v in ohlcv['volume']):
        chart_config["yAxis"].append({
            "title": {
                "text": "Volume",
                "style": {
                    "color": "#ffffff"
                }
            },
            "labels": {
                "style": {
                    "color": "#ffffff"
                }
            },
            "gridLineColor": "#333333",
            "top": "75%",
            "height": "25%",
            "offset": 0
        })
        
        chart_config["series"].append({
            "type": "column",
            "name": "Volume",
            "data": volume_data,
            "yAxis": 1,
            "color": "#26a69a",
            "borderColor": "#26a69a"
        })
    
    return chart_config


def create_highcharts_plot(
    df: pd.DataFrame, 
    series_id: Optional[str] = None, 
    metric: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Create Highcharts time-series plot configuration."""
    if not HIGHCHARTS_AVAILABLE:
        return None
    
    if df is None or len(df) == 0:
        return None
    
    # Filter by series if specified
    if series_id and 'series_id' in df.columns:
        plot_df = df[df['series_id'] == series_id].copy()
    else:
        plot_df = df.copy()
    
    # Ensure timestamp is datetime
    if 'timestamp' in plot_df.columns:
        plot_df['timestamp'] = pd.to_datetime(plot_df['timestamp'])
    else:
        return None
    
    # Get unique series
    if 'series_id' in plot_df.columns:
        unique_series = plot_df['series_id'].unique()
    else:
        unique_series = ['default']
        plot_df['series_id'] = 'default'
    
    series_list = []
    
    # Prepare data for each series
    for sid in unique_series:
        series_data = plot_df[plot_df['series_id'] == sid].copy()
        
        if metric:
            # Plot specific metric
            values = []
            timestamps = []
            skipped_count = 0
            for idx, row in series_data.iterrows():
                if 'measurements' in row and isinstance(row['measurements'], dict):
                    val = row['measurements'].get(metric)
                elif metric in row:
                    val = row[metric]
                else:
                    val = None
                
                # Safely convert to float and validate timestamp
                float_val = safe_float(val)
                if float_val is not None and pd.notna(row['timestamp']):
                    values.append(float_val)
                    timestamps.append(int(pd.to_datetime(row['timestamp']).timestamp() * 1000))
                elif val is not None:
                    skipped_count += 1
            
            if skipped_count > 0:
                logger.warning(f"Skipped {skipped_count} non-numeric values for metric '{metric}' in series '{sid}'")
            
            if len(values) > 0:
                data_points = [[ts, val] for ts, val in zip(timestamps, values)]
                series_list.append({
                    "name": f"{sid} - {metric}",
                    "data": data_points,
                    "color": "#2196F3",
                    "lineWidth": 2
                })
        else:
            # Plot default metric
            default_metrics = ['close', 'value', 'temperature', 'price']
            metric_to_plot = None
            
            for m in default_metrics:
                if m in series_data.columns:
                    metric_to_plot = m
                    break
            
            if metric_to_plot:
                values = []
                timestamps = []
                for idx, row in series_data.iterrows():
                    if pd.notna(row['timestamp']) and pd.notna(row[metric_to_plot]):
                        float_val = safe_float(row[metric_to_plot])
                        if float_val is not None:
                            values.append(float_val)
                        else:
                            values.append(None)
                        timestamps.append(int(pd.to_datetime(row['timestamp']).timestamp() * 1000))
                
                if len(values) > 0:
                    data_points = [[ts, val] for ts, val in zip(timestamps, values)]
                    series_list.append({
                        "name": f"{sid} - {metric_to_plot}",
                        "data": data_points,
                        "color": "#2196F3",
                        "lineWidth": 2
                    })
    
    if not series_list:
        return None
    
    # Create chart configuration
    chart_config = {
        "chart": {
            "type": "line",
            "backgroundColor": "#1e1e1e"
        },
        "title": {
            "text": "Time-Series Data",
            "style": {
                "color": "#ffffff"
            }
        },
        "xAxis": {
            "type": "datetime",
            "labels": {
                "style": {
                    "color": "#ffffff"
                }
            },
            "gridLineColor": "#333333"
        },
        "yAxis": {
            "title": {
                "text": "Value",
                "style": {
                    "color": "#ffffff"
                }
            },
            "labels": {
                "style": {
                    "color": "#ffffff"
                }
            },
            "gridLineColor": "#333333"
        },
        "series": series_list,
        "legend": {
            "enabled": True,
            "itemStyle": {
                "color": "#ffffff"
            }
        },
        "plotOptions": {
            "line": {
                "marker": {
                    "enabled": True,
                    "radius": 4
                }
            }
        },
        "tooltip": {
            "backgroundColor": "#2d2d2d",
            "style": {
                "color": "#ffffff"
            },
            "shared": True,
            "xDateFormat": "%Y-%m-%d %H:%M:%S"
        }
    }
    
    return chart_config


def highcharts_config_to_html(chart_config: Dict[str, Any], container_id: str = "highcharts-container") -> str:
    """Convert Highcharts configuration to HTML with embedded script."""
    if not HIGHCHARTS_AVAILABLE or chart_config is None:
        return f"<div id='{container_id}'>Highcharts not available</div>"
    
    config_json = json.dumps(chart_config, default=str)
    
    html = f"""
    <div id="{container_id}" style="width: 100%; height: 500px;"></div>
    <script src="https://code.highcharts.com/stock/highstock.js"></script>
    <script src="https://code.highcharts.com/stock/modules/exporting.js"></script>
    <script>
        Highcharts.stockChart('{container_id}', {config_json});
    </script>
    """
    
    return html


def create_highcharts_plot_wrapper(
    df: pd.DataFrame, 
    series_id: Optional[str] = None, 
    metric: Optional[str] = None, 
    chart_type: str = "auto"
) -> Optional[Dict[str, Any]]:
    """Wrapper function to create Highcharts plot, with financial chart support."""
    if df is None or len(df) == 0:
        return None
    
    # Check if this is financial data
    is_financial = is_financial_data(df, series_id)
    
    # Determine chart type
    if is_financial and (chart_type == "auto" or chart_type in ["candlestick", "ohlc"]):
        actual_chart_type = chart_type if chart_type != "auto" else "candlestick"
        return create_highcharts_financial_plot(df, series_id, actual_chart_type, show_volume=True)
    
    # Otherwise, use standard time-series plot
    return create_highcharts_plot(df, series_id, metric)
