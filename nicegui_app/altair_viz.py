"""
NiceGUI App Altair Visualization Functions
Altair-based plotting functions for time-series and financial data.
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

# Altair imports
try:
    import altair as alt
    alt.data_transformers.disable_max_rows()  # Allow large datasets
    ALTAIR_AVAILABLE = True
except ImportError:
    ALTAIR_AVAILABLE = False
    logger.warning("Altair not available. Install with: pip install altair")


def create_altair_financial_plot(
    df: pd.DataFrame, 
    series_id: Optional[str] = None, 
    chart_type: str = "candlestick", 
    show_volume: bool = True
):
    """Create Altair financial chart (candlestick or OHLC) with optional volume subplot."""
    if not ALTAIR_AVAILABLE:
        return None
    
    ohlcv = extract_ohlcv_data(df, series_id)
    
    if len(ohlcv['timestamp']) == 0:
        return None
    
    # Convert to DataFrame for Altair
    chart_df = pd.DataFrame({
        'timestamp': pd.to_datetime(ohlcv['timestamp']),
        'open': ohlcv['open'],
        'high': ohlcv['high'],
        'low': ohlcv['low'],
        'close': ohlcv['close'],
        'volume': ohlcv['volume']
    })
    
    # Determine if price increased (for color coding)
    chart_df['is_increasing'] = chart_df['close'] >= chart_df['open']
    
    # Base chart configuration
    base = alt.Chart(chart_df).encode(
        x=alt.X('timestamp:T', title='Time', axis=alt.Axis(format='%Y-%m-%d'))
    )
    
    if chart_type == "candlestick":
        # Create candlestick chart
        # High-Low lines
        high_low = base.mark_rule(
            strokeWidth=1,
            color='gray'
        ).encode(
            y=alt.Y('low:Q', title='Price'),
            y2='high:Q'
        )
        
        # Open-Close rectangles
        body = base.mark_bar(
            width=8
        ).encode(
            y=alt.Y('open:Q', title='Price'),
            y2='close:Q',
            color=alt.condition(
                alt.datum.is_increasing,
                alt.value('#26a69a'),  # Green for up
                alt.value('#ef5350')   # Red for down
            )
        )
        
        price_chart = alt.layer(high_low, body).resolve_scale(color='independent')
        
    elif chart_type == "ohlc":
        # Create OHLC chart
        # High-Low lines
        high_low = base.mark_rule(
            strokeWidth=2
        ).encode(
            y=alt.Y('low:Q', title='Price'),
            y2='high:Q',
            color=alt.condition(
                alt.datum.is_increasing,
                alt.value('#26a69a'),
                alt.value('#ef5350')
            )
        )
        
        # Open ticks
        open_ticks = base.mark_tick(
            orient='left',
            thickness=2,
            size=20
        ).encode(
            y='open:Q',
            color=alt.condition(
                alt.datum.is_increasing,
                alt.value('#26a69a'),
                alt.value('#ef5350')
            )
        )
        
        # Close ticks
        close_ticks = base.mark_tick(
            orient='right',
            thickness=2,
            size=20
        ).encode(
            y='close:Q',
            color=alt.condition(
                alt.datum.is_increasing,
                alt.value('#26a69a'),
                alt.value('#ef5350')
            )
        )
        
        price_chart = alt.layer(high_low, open_ticks, close_ticks).resolve_scale(color='independent')
        
    else:  # line chart
        price_chart = base.mark_line(
            strokeWidth=2,
            color='#2196F3'
        ).encode(
            y=alt.Y('close:Q', title='Price')
        )
    
    # Add volume subplot if requested
    if show_volume and any(v > 0 for v in chart_df['volume']):
        volume_chart = base.mark_bar(
            width=8,
            opacity=0.7
        ).encode(
            y=alt.Y('volume:Q', title='Volume'),
            color=alt.condition(
                alt.datum.is_increasing,
                alt.value('#26a69a'),
                alt.value('#ef5350')
            )
        )
        
        # Combine price and volume charts
        combined = alt.vconcat(
            price_chart.properties(height=400, title='Price'),
            volume_chart.properties(height=150, title='Volume')
        ).resolve_scale(
            x='shared'
        )
        
        return combined.configure(
            background='#1e1e1e',
            view=alt.ViewConfig(stroke=None),
            axis=alt.AxisConfig(
                domainColor='white',
                gridColor='#333333',
                labelColor='white',
                titleColor='white'
            ),
            legend=alt.LegendConfig(
                labelColor='white',
                titleColor='white'
            )
        )
    else:
        return price_chart.configure(
            background='#1e1e1e',
            view=alt.ViewConfig(stroke=None),
            axis=alt.AxisConfig(
                domainColor='white',
                gridColor='#333333',
                labelColor='white',
                titleColor='white'
            ),
            legend=alt.LegendConfig(
                labelColor='white',
                titleColor='white'
            )
        )


def create_altair_plot(
    df: pd.DataFrame, 
    series_id: Optional[str] = None, 
    metric: Optional[str] = None
):
    """Create Altair time-series plot."""
    if not ALTAIR_AVAILABLE:
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
    
    charts = []
    
    # Plot data for each series
    for sid in unique_series:
        series_data = plot_df[plot_df['series_id'] == sid].copy()
        
        if metric:
            # Plot specific metric
            values = []
            for idx, row in series_data.iterrows():
                if 'measurements' in row and isinstance(row['measurements'], dict):
                    values.append(row['measurements'].get(metric))
                elif metric in row:
                    values.append(row[metric])
                else:
                    values.append(None)
            
            series_data['value'] = values
            series_data = series_data.dropna(subset=['value', 'timestamp'])
            
            if len(series_data) > 0:
                chart = alt.Chart(series_data).mark_line(
                    point=True,
                    strokeWidth=2
                ).encode(
                    x=alt.X('timestamp:T', title='Time', axis=alt.Axis(format='%Y-%m-%d')),
                    y=alt.Y('value:Q', title='Value'),
                    color=alt.value('#2196F3'),
                    tooltip=['timestamp:T', 'value:Q']
                ).properties(
                    title=f"{sid} - {metric}"
                )
                charts.append(chart)
        else:
            # Plot default metric
            default_metrics = ['close', 'value', 'temperature', 'price']
            metric_to_plot = None
            
            for m in default_metrics:
                if m in series_data.columns:
                    metric_to_plot = m
                    break
            
            if metric_to_plot:
                chart = alt.Chart(series_data).mark_line(
                    point=True,
                    strokeWidth=2
                ).encode(
                    x=alt.X('timestamp:T', title='Time', axis=alt.Axis(format='%Y-%m-%d')),
                    y=alt.Y(f'{metric_to_plot}:Q', title='Value'),
                    color=alt.value('#2196F3'),
                    tooltip=[f'{metric_to_plot}:Q']
                ).properties(
                    title=f"{sid} - {metric_to_plot}"
                )
                charts.append(chart)
    
    if not charts:
        return None
    
    # Combine charts
    if len(charts) == 1:
        combined = charts[0]
    else:
        combined = alt.vconcat(*charts)
    
    return combined.configure(
        background='#1e1e1e',
        view=alt.ViewConfig(stroke=None),
        axis=alt.AxisConfig(
            domainColor='white',
            gridColor='#333333',
            labelColor='white',
            titleColor='white'
        ),
        legend=alt.LegendConfig(
            labelColor='white',
            titleColor='white'
        ),
        title=alt.TitleConfig(
            color='white'
        )
    )


def altair_chart_to_dict(chart) -> Dict[str, Any]:
    """Convert Altair chart to dictionary for JSON serialization."""
    if not ALTAIR_AVAILABLE or chart is None:
        return {}
    
    try:
        # Convert chart to dictionary
        chart_dict = chart.to_dict()
        return chart_dict
    except Exception as e:
        logger.error(f"Error converting Altair chart to dict: {e}")
        return {}


def altair_chart_to_html(chart) -> str:
    """Convert Altair chart to HTML string."""
    if not ALTAIR_AVAILABLE or chart is None:
        return "<div>Chart not available</div>"
    
    try:
        html = chart.to_html()
        return html
    except Exception as e:
        logger.error(f"Error converting Altair chart to HTML: {e}")
        return f"<div>Error rendering chart: {str(e)}</div>"


def create_altair_plot_wrapper(
    df: pd.DataFrame, 
    series_id: Optional[str] = None, 
    metric: Optional[str] = None, 
    chart_type: str = "auto"
):
    """Wrapper function to create Altair plot, with financial chart support."""
    if df is None or len(df) == 0:
        return None
    
    # Check if this is financial data
    is_financial = is_financial_data(df, series_id)
    
    # Determine chart type
    if is_financial and (chart_type == "auto" or chart_type in ["candlestick", "ohlc"]):
        actual_chart_type = chart_type if chart_type != "auto" else "candlestick"
        return create_altair_financial_plot(df, series_id, actual_chart_type, show_volume=True)
    
    # Otherwise, use standard time-series plot
    return create_altair_plot(df, series_id, metric)
