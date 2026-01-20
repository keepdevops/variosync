"""
NiceGUI App ECharts Visualization Functions
ECharts-based plotting functions for time-series and financial data.
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

# ECharts imports - Note: ECharts is typically used via JavaScript, but we can use pyecharts
try:
    from pyecharts import options as opts
    from pyecharts.charts import Kline, Line, Bar
    from pyecharts.globals import ThemeType
    ECHARTS_AVAILABLE = True
except ImportError:
    try:
        # Alternative: use echarts-python if pyecharts not available
        import echarts
        ECHARTS_AVAILABLE = True
    except ImportError:
        ECHARTS_AVAILABLE = False
        logger.warning("ECharts not available. Install with: pip install pyecharts")


def create_echarts_financial_plot(
    df: pd.DataFrame, 
    series_id: Optional[str] = None, 
    chart_type: str = "candlestick", 
    show_volume: bool = True
) -> Optional[Dict[str, Any]]:
    """Create ECharts financial chart configuration (candlestick/K-line or OHLC) with optional volume."""
    if not ECHARTS_AVAILABLE:
        return None
    
    ohlcv = extract_ohlcv_data(df, series_id)
    
    if len(ohlcv['timestamp']) == 0:
        return None
    
    # Convert timestamps to strings for ECharts
    timestamps = []
    for ts in ohlcv['timestamp']:
        try:
            dt = pd.to_datetime(ts)
            timestamps.append(dt.strftime('%Y-%m-%d'))
        except:
            timestamps.append(str(ts))
    
    # Prepare OHLC data for candlestick
    ohlc_data = []
    for i in range(len(timestamps)):
        if (i < len(ohlcv['open']) and i < len(ohlcv['high']) and 
            i < len(ohlcv['low']) and i < len(ohlcv['close'])):
            ohlc_data.append([
                ohlcv['open'][i],
                ohlcv['close'][i],
                ohlcv['low'][i],
                ohlcv['high'][i]
            ])
    
    # Prepare volume data
    volume_data = []
    for i in range(len(timestamps)):
        if i < len(ohlcv['volume']):
            volume_data.append(ohlcv['volume'][i])
    
    # Determine series name
    if series_id:
        series_name = series_id
    elif 'series_id' in df.columns and len(df['series_id'].unique()) == 1:
        series_name = df['series_id'].iloc[0]
    else:
        series_name = "Financial Data"
    
    # Create ECharts option configuration
    option = {
        "backgroundColor": "#1e1e1e",
        "title": {
            "text": f"{series_name} - {chart_type.upper()} Chart",
            "left": "center",
            "textStyle": {
                "color": "#ffffff"
            }
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "cross"
            },
            "backgroundColor": "#2d2d2d",
            "textStyle": {
                "color": "#ffffff"
            }
        },
        "legend": {
            "data": ["Price", "Volume"] if show_volume else ["Price"],
            "textStyle": {
                "color": "#ffffff"
            },
            "top": 30
        },
        "grid": [
            {
                "left": "10%",
                "right": "8%",
                "top": "15%",
                "height": "60%" if show_volume else "70%"
            },
            {
                "left": "10%",
                "right": "8%",
                "top": "80%",
                "height": "15%"
            } if show_volume else None
        ],
        "xAxis": [
            {
                "type": "category",
                "data": timestamps,
                "scale": True,
                "boundaryGap": False,
                "axisLine": {"onZero": False},
                "splitLine": {"show": False},
                "min": "dataMin",
                "max": "dataMax",
                "axisLabel": {
                    "color": "#ffffff"
                }
            },
            {
                "type": "category",
                "gridIndex": 1,
                "data": timestamps,
                "scale": True,
                "boundaryGap": False,
                "axisLine": {"onZero": False},
                "axisTick": {"show": False},
                "splitLine": {"show": False},
                "axisLabel": {"show": False},
                "min": "dataMin",
                "max": "dataMax"
            } if show_volume else None
        ],
        "yAxis": [
            {
                "scale": True,
                "splitArea": {
                    "show": True,
                    "areaStyle": {
                        "color": ["rgba(250,250,250,0.05)", "rgba(200,200,200,0.02)"]
                    }
                },
                "axisLabel": {
                    "color": "#ffffff"
                },
                "splitLine": {
                    "show": True,
                    "lineStyle": {
                        "color": "#333333"
                    }
                }
            },
            {
                "scale": True,
                "gridIndex": 1,
                "splitNumber": 2,
                "axisLabel": {"show": False},
                "axisLine": {"show": False},
                "axisTick": {"show": False},
                "splitLine": {"show": False}
            } if show_volume else None
        ],
        "dataZoom": [
            {
                "type": "inside",
                "xAxisIndex": [0, 1] if show_volume else [0],
                "start": 0,
                "end": 100
            },
            {
                "show": True,
                "xAxisIndex": [0, 1] if show_volume else [0],
                "type": "slider",
                "top": "90%",
                "start": 0,
                "end": 100
            }
        ],
        "series": [
            {
                "name": "Price",
                "type": "candlestick" if chart_type == "candlestick" else "line",
                "data": ohlc_data if chart_type == "candlestick" else [
                    [ohlcv['open'][i], ohlcv['high'][i], ohlcv['low'][i], ohlcv['close'][i]]
                    for i in range(len(timestamps)) if i < len(ohlcv['open'])
                ],
                "itemStyle": {
                    "color": "#26a69a",
                    "color0": "#ef5350",
                    "borderColor": "#26a69a",
                    "borderColor0": "#ef5350"
                }
            }
        ]
    }
    
    # Add volume series if requested
    if show_volume and any(v > 0 for v in volume_data):
        option["series"].append({
            "name": "Volume",
            "type": "bar",
            "xAxisIndex": 1,
            "yAxisIndex": 1,
            "data": volume_data,
            "itemStyle": {
                "color": "#26a69a"
            }
        })
    
    # Remove None values from grid and axes
    option["grid"] = [g for g in option["grid"] if g is not None]
    option["xAxis"] = [x for x in option["xAxis"] if x is not None]
    option["yAxis"] = [y for y in option["yAxis"] if y is not None]
    
    return option


def create_echarts_plot(
    df: pd.DataFrame, 
    series_id: Optional[str] = None, 
    metric: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Create ECharts time-series plot configuration."""
    if not ECHARTS_AVAILABLE:
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
    timestamps = None
    
    # Prepare data for each series
    for sid in unique_series:
        series_data = plot_df[plot_df['series_id'] == sid].copy()
        series_data = series_data.sort_values('timestamp')
        
        if timestamps is None:
            timestamps = [ts.strftime('%Y-%m-%d %H:%M:%S') for ts in series_data['timestamp']]
        
        if metric:
            # Plot specific metric
            values = []
            skipped_count = 0
            for idx, row in series_data.iterrows():
                if 'measurements' in row and isinstance(row['measurements'], dict):
                    val = row['measurements'].get(metric)
                elif metric in row:
                    val = row[metric]
                else:
                    val = None
                
                # Safely convert to float
                float_val = safe_float(val)
                if float_val is not None:
                    values.append(float_val)
                else:
                    values.append(None)
                    if val is not None:
                        skipped_count += 1
            
            if skipped_count > 0:
                logger.warning(f"Skipped {skipped_count} non-numeric values for metric '{metric}' in series '{sid}'")
            
            if len(values) > 0:
                series_list.append({
                    "name": f"{sid} - {metric}",
                    "type": "line",
                    "data": values,
                    "smooth": True,
                    "lineStyle": {
                        "width": 2
                    },
                    "itemStyle": {
                        "color": "#2196F3"
                    }
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
                for idx, row in series_data.iterrows():
                    if pd.notna(row[metric_to_plot]):
                        float_val = safe_float(row[metric_to_plot])
                        if float_val is not None:
                            values.append(float_val)
                        else:
                            values.append(None)
                    else:
                        values.append(None)
                
                if len(values) > 0:
                    series_list.append({
                        "name": f"{sid} - {metric_to_plot}",
                        "type": "line",
                        "data": values,
                        "smooth": True,
                        "lineStyle": {
                            "width": 2
                        },
                        "itemStyle": {
                            "color": "#2196F3"
                        }
                    })
    
    if not series_list or timestamps is None:
        return None
    
    # Create ECharts option configuration
    option = {
        "backgroundColor": "#1e1e1e",
        "title": {
            "text": "Time-Series Data",
            "left": "center",
            "textStyle": {
                "color": "#ffffff"
            }
        },
        "tooltip": {
            "trigger": "axis",
            "backgroundColor": "#2d2d2d",
            "textStyle": {
                "color": "#ffffff"
            }
        },
        "legend": {
            "data": [s["name"] for s in series_list],
            "textStyle": {
                "color": "#ffffff"
            },
            "top": 30
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        },
        "xAxis": {
            "type": "category",
            "boundaryGap": False,
            "data": timestamps,
            "axisLabel": {
                "color": "#ffffff",
                "rotate": 45
            },
            "splitLine": {
                "show": True,
                "lineStyle": {
                    "color": "#333333"
                }
            }
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {
                "color": "#ffffff"
            },
            "splitLine": {
                "show": True,
                "lineStyle": {
                    "color": "#333333"
                }
            }
        },
        "series": series_list
    }
    
    return option


def echarts_config_to_html(chart_config: Dict[str, Any], container_id: str = "echarts-container") -> str:
    """Convert ECharts configuration to HTML with embedded script."""
    if not ECHARTS_AVAILABLE or chart_config is None:
        return f"<div id='{container_id}'>ECharts not available</div>"
    
    config_json = json.dumps(chart_config, default=str, ensure_ascii=False)
    
    html = f"""
    <div id="{container_id}" style="width: 100%; height: 500px;"></div>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
    <script>
        var chartDom = document.getElementById('{container_id}');
        var myChart = echarts.init(chartDom, 'dark');
        var option = {config_json};
        myChart.setOption(option);
        window.addEventListener('resize', function() {{
            myChart.resize();
        }});
    </script>
    """
    
    return html


def create_echarts_plot_wrapper(
    df: pd.DataFrame, 
    series_id: Optional[str] = None, 
    metric: Optional[str] = None, 
    chart_type: str = "auto"
) -> Optional[Dict[str, Any]]:
    """Wrapper function to create ECharts plot, with financial chart support."""
    if df is None or len(df) == 0:
        return None
    
    # Check if this is financial data
    is_financial = is_financial_data(df, series_id)
    
    # Determine chart type
    if is_financial and (chart_type == "auto" or chart_type in ["candlestick", "ohlc"]):
        actual_chart_type = chart_type if chart_type != "auto" else "candlestick"
        return create_echarts_financial_plot(df, series_id, actual_chart_type, show_volume=True)
    
    # Otherwise, use standard time-series plot
    return create_echarts_plot(df, series_id, metric)
