"""
NiceGUI App Visualization Functions
Plotting functions for time-series and financial data.
"""
import json
from typing import Optional, Tuple, List, Dict, Any

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from logger import get_logger
from . import get_app_instance, MATPLOTLIB_AVAILABLE

logger = get_logger()

# Matplotlib imports
if MATPLOTLIB_AVAILABLE:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from io import BytesIO
    import base64


def load_timeseries_data() -> Tuple[Optional[pd.DataFrame], List[Dict[str, Any]]]:
    """Load time-series data from storage."""
    logger.debug("[load_timeseries_data] Starting to load from storage")
    try:
        app = get_app_instance()
        if not app.storage:
            logger.warning("[load_timeseries_data] No storage instance available")
            return None, []

        # Load all records from storage
        keys = app.storage.list_keys("data/")[:10000]  # Increased limit for better visualization
        logger.info(f"[load_timeseries_data] Found {len(keys)} keys in storage with prefix 'data/'")

        if not keys:
            logger.warning("[load_timeseries_data] No keys found in storage")
            return None, []

        records = []
        load_errors = 0
        no_timestamp = 0

        for key in keys:
            try:
                data_bytes = app.storage.load(key)
                if data_bytes:
                    record = json.loads(data_bytes.decode('utf-8'))
                    if 'timestamp' in record:
                        records.append(record)
                    else:
                        no_timestamp += 1
                else:
                    load_errors += 1
            except Exception as e:
                logger.debug(f"[load_timeseries_data] Error loading record {key}: {e}")
                load_errors += 1
                continue

        logger.info(f"[load_timeseries_data] Loaded {len(records)} records with timestamps, {no_timestamp} without timestamp, {load_errors} errors")

        if not records:
            logger.warning("[load_timeseries_data] No records with timestamps found")
            return None, []

        # Convert to DataFrame
        df = pd.DataFrame(records)
        logger.debug(f"[load_timeseries_data] DataFrame created with shape: {df.shape}, columns: {list(df.columns)}")

        # Normalize timestamp - filter out synthetic row_N timestamps first
        valid_timestamp_mask = ~df['timestamp'].astype(str).str.match(r'^row_\d+$')
        synthetic_count = (~valid_timestamp_mask).sum()
        df = df[valid_timestamp_mask]

        if synthetic_count > 0:
            logger.debug(f"[load_timeseries_data] Filtered out {synthetic_count} synthetic row_N timestamps")

        if len(df) == 0:
            logger.warning("[load_timeseries_data] No valid timestamps found in data (only synthetic row_N identifiers)")
            return None, []

        df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', errors='coerce')
        invalid_ts_count = df['timestamp'].isna().sum()
        df = df.dropna(subset=['timestamp'])

        if invalid_ts_count > 0:
            logger.debug(f"[load_timeseries_data] Dropped {invalid_ts_count} records with invalid timestamps")

        if len(df) == 0:
            logger.warning("[load_timeseries_data] All timestamps were invalid after conversion")
            return None, []

        # Sort by timestamp
        df = df.sort_values('timestamp')
        logger.info(f"[load_timeseries_data] Successfully loaded {len(df)} records, date range: {df['timestamp'].min()} to {df['timestamp'].max()}")

        return df, records
    except Exception as e:
        logger.error(f"[load_timeseries_data] Error loading time-series data: {e}", exc_info=True)
        return None, []


def load_timeseries_from_storage_file(storage_key: str) -> Tuple[Optional[pd.DataFrame], List[Dict[str, Any]]]:
    """
    Load time-series data from a specific storage file.

    Loads data from a storage file by key, parses it using FileLoader,
    and returns a DataFrame suitable for visualization.

    Args:
        storage_key: The storage key for the file to load

    Returns:
        Tuple of (DataFrame, raw_records) or (None, []) if failed
    """
    import tempfile
    import os
    from pathlib import Path
    from file_loader import FileLoader

    logger.debug(f"[load_timeseries_from_storage_file] Starting load for storage key: {storage_key}")

    try:
        # Validate storage key
        if not storage_key:
            logger.error("[load_timeseries_from_storage_file] Empty storage key provided")
            return None, []

        app = get_app_instance()
        if not app or not app.storage:
            logger.error("[load_timeseries_from_storage_file] App or storage not available")
            return None, []

        # Load file data from storage
        file_data = app.storage.load(storage_key)
        if not file_data:
            logger.error(f"[load_timeseries_from_storage_file] Could not load file: {storage_key}")
            return None, []

        data_size = len(file_data)
        logger.info(f"[load_timeseries_from_storage_file] Loaded {data_size} bytes from storage for: {storage_key}")

        if data_size == 0:
            logger.warning(f"[load_timeseries_from_storage_file] File is empty: {storage_key}")
            return None, []

        # Create temp file for FileLoader
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(storage_key).suffix)
        temp_file.write(file_data)
        temp_file.close()
        logger.debug(f"[load_timeseries_from_storage_file] Created temp file: {temp_file.name}")

        try:
            loader = FileLoader()
            records = loader.load(temp_file.name)

            if records is None:
                logger.error(f"[load_timeseries_from_storage_file] FileLoader returned None for: {storage_key}")
                return None, []

            if not records:
                logger.warning(f"[load_timeseries_from_storage_file] No records found in file: {storage_key}")
                return None, []

            logger.info(f"[load_timeseries_from_storage_file] Loaded {len(records)} records from: {storage_key}")

            # Validate records structure
            if not isinstance(records, list):
                logger.error(f"[load_timeseries_from_storage_file] Records is not a list: {type(records)}")
                return None, []

            if len(records) > 0 and isinstance(records[0], dict):
                logger.debug(f"[load_timeseries_from_storage_file] Sample record keys: {list(records[0].keys())[:10]}")

            # Expand measurements if present
            expanded_records = []
            for record in records:
                try:
                    expanded = {}
                    for key, value in record.items():
                        if key != "measurements":
                            expanded[key] = value
                    if "measurements" in record and isinstance(record["measurements"], dict):
                        for m_key, m_value in record["measurements"].items():
                            expanded[m_key] = m_value
                    else:
                        expanded.update(record)
                    expanded_records.append(expanded)
                except Exception as e:
                    logger.debug(f"[load_timeseries_from_storage_file] Error expanding record: {e}")

            logger.debug(f"[load_timeseries_from_storage_file] Expanded {len(expanded_records)} records")

            # Convert to DataFrame
            df = pd.DataFrame(expanded_records)
            logger.debug(f"[load_timeseries_from_storage_file] DataFrame shape: {df.shape}, columns: {list(df.columns)}")

            # Process timestamps
            if 'timestamp' in df.columns:
                original_count = len(df)
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                df = df.sort_values('timestamp')
                invalid_count = df['timestamp'].isna().sum()
                df = df.dropna(subset=['timestamp'])
                logger.debug(f"[load_timeseries_from_storage_file] Timestamp processing: {original_count} -> {len(df)} records ({invalid_count} invalid)")
            else:
                logger.warning(f"[load_timeseries_from_storage_file] No 'timestamp' column in data")
                logger.debug(f"[load_timeseries_from_storage_file] Available columns: {list(df.columns)}")

            if len(df) == 0:
                logger.warning(f"[load_timeseries_from_storage_file] No valid data points after processing: {storage_key}")
                return None, []

            # Log available numeric columns for plotting
            numeric_cols = list(df.select_dtypes(include=['number']).columns)
            logger.debug(f"[load_timeseries_from_storage_file] Numeric columns available for plotting: {numeric_cols}")

            logger.info(f"[load_timeseries_from_storage_file] Ready to visualize {len(df)} data points")
            return df, records

        finally:
            try:
                os.unlink(temp_file.name)
            except:
                pass

    except Exception as e:
        logger.error(f"[load_timeseries_from_storage_file] Error loading from storage file {storage_key}: {e}", exc_info=True)
        return None, []


def load_timeseries_from_file(file_path: str) -> Tuple[Optional[pd.DataFrame], List[Dict[str, Any]]]:
    """
    Load all time-series records from a file directly.

    Supports JSON (array or single record), Parquet, CSV, and other formats
    that the FileLoader supports. This loads ALL records from the file,
    not just one.

    Args:
        file_path: Path to the file to load

    Returns:
        Tuple of (DataFrame, raw_records) or (None, []) if failed
    """
    logger.debug(f"[load_timeseries_from_file] Starting load from file: {file_path}")
    try:
        from pathlib import Path
        from file_loader import FileLoader

        # Validate file path
        if not file_path:
            logger.error("[load_timeseries_from_file] Empty file path provided")
            return None, []

        path_obj = Path(file_path)
        if not path_obj.exists():
            logger.error(f"[load_timeseries_from_file] File not found: {file_path}")
            return None, []

        if not path_obj.is_file():
            logger.error(f"[load_timeseries_from_file] Path is not a file: {file_path}")
            return None, []

        file_size = path_obj.stat().st_size
        logger.info(f"[load_timeseries_from_file] File: {file_path}, size: {file_size} bytes ({file_size / 1024:.2f} KB)")

        if file_size == 0:
            logger.warning(f"[load_timeseries_from_file] File is empty: {file_path}")
            return None, []

        # Load all records from file using FileLoader
        loader = FileLoader()
        records = loader.load(file_path)

        if records is None:
            logger.error(f"[load_timeseries_from_file] FileLoader returned None for: {file_path}")
            return None, []

        if not records:
            logger.warning(f"[load_timeseries_from_file] No records loaded from {file_path}")
            return None, []

        logger.info(f"[load_timeseries_from_file] Loaded {len(records)} records from file: {file_path}")

        # Validate records structure
        if not isinstance(records, list):
            logger.error(f"[load_timeseries_from_file] Records is not a list: {type(records)}")
            return None, []

        if len(records) > 0:
            sample = records[0]
            if isinstance(sample, dict):
                logger.debug(f"[load_timeseries_from_file] Sample record keys: {list(sample.keys())[:10]}")
            else:
                logger.warning(f"[load_timeseries_from_file] First record is not a dict: {type(sample)}")

        # Convert to DataFrame
        df = pd.DataFrame(records)
        logger.debug(f"[load_timeseries_from_file] DataFrame created with shape: {df.shape}")
        logger.debug(f"[load_timeseries_from_file] DataFrame columns: {list(df.columns)}")

        # Handle nested measurements if present - flatten for plotting
        if 'measurements' in df.columns:
            logger.debug("[load_timeseries_from_file] Found 'measurements' column, expanding nested structure")
            # Expand measurements dict into separate columns
            measurements_expanded = df['measurements'].apply(
                lambda x: x if isinstance(x, dict) else {}
            )
            measurements_df = pd.json_normalize(measurements_expanded)
            expanded_cols = list(measurements_df.columns)
            logger.debug(f"[load_timeseries_from_file] Expanded measurement columns: {expanded_cols}")
            # Join with original dataframe (keeping measurements column for reference)
            for col in measurements_df.columns:
                if col not in df.columns:
                    df[col] = measurements_df[col]

        # Normalize timestamp - filter out synthetic row_N timestamps first
        if 'timestamp' in df.columns:
            original_count = len(df)
            valid_timestamp_mask = ~df['timestamp'].astype(str).str.match(r'^row_\d+$')
            synthetic_count = (~valid_timestamp_mask).sum()
            df = df[valid_timestamp_mask]

            if synthetic_count > 0:
                logger.debug(f"[load_timeseries_from_file] Filtered out {synthetic_count} synthetic row_N timestamps")

            if len(df) == 0:
                logger.warning(f"[load_timeseries_from_file] No valid timestamps found in {file_path} (only synthetic row_N identifiers)")
                return None, []

            df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', errors='coerce')
            invalid_count = df['timestamp'].isna().sum()
            df = df.dropna(subset=['timestamp'])

            if invalid_count > 0:
                logger.debug(f"[load_timeseries_from_file] Dropped {invalid_count} records with invalid timestamps")

            df = df.sort_values('timestamp')
            logger.debug(f"[load_timeseries_from_file] After timestamp processing: {len(df)} records (from {original_count})")
        else:
            logger.warning(f"[load_timeseries_from_file] No 'timestamp' column found in {file_path}")
            logger.debug(f"[load_timeseries_from_file] Available columns: {list(df.columns)}")

        if len(df) == 0:
            logger.warning(f"[load_timeseries_from_file] No valid records with timestamps in {file_path}")
            return None, []

        # Log final result
        if 'timestamp' in df.columns:
            logger.info(f"[load_timeseries_from_file] Successfully loaded {len(df)} records, date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        else:
            logger.info(f"[load_timeseries_from_file] Successfully loaded {len(df)} records (no timestamp column)")

        # Log available numeric columns for plotting
        numeric_cols = list(df.select_dtypes(include=['number']).columns)
        logger.debug(f"[load_timeseries_from_file] Numeric columns available for plotting: {numeric_cols}")

        return df, records

    except Exception as e:
        logger.error(f"[load_timeseries_from_file] Error loading time-series data from file {file_path}: {e}", exc_info=True)
        return None, []


def get_available_series(df: Optional[pd.DataFrame]) -> List[str]:
    """Get list of available series IDs."""
    if df is None or len(df) == 0:
        return []
    return sorted(df['series_id'].unique().tolist() if 'series_id' in df.columns else [])


def is_financial_data(df: Optional[pd.DataFrame], series_id: Optional[str] = None) -> bool:
    """Check if data contains financial OHLCV fields."""
    if df is None or len(df) == 0:
        return False
    
    # Filter by series if specified
    if series_id and 'series_id' in df.columns:
        check_df = df[df['series_id'] == series_id]
    else:
        check_df = df
    
    if len(check_df) == 0:
        return False
    
    # Check for direct OHLCV columns
    ohlcv_cols = ['open', 'high', 'low', 'close']
    has_direct_ohlcv = all(col in check_df.columns for col in ohlcv_cols)
    
    # Check for OHLCV in measurements
    has_measurements_ohlcv = False
    for idx, row in check_df.head(10).iterrows():  # Check first 10 rows
        if 'measurements' in row and isinstance(row['measurements'], dict):
            measurements = row['measurements']
            if all(key in measurements for key in ohlcv_cols):
                has_measurements_ohlcv = True
                break
    
    return has_direct_ohlcv or has_measurements_ohlcv


def get_available_metrics(df: Optional[pd.DataFrame], series_id: Optional[str] = None) -> List[str]:
    """Get list of available metrics for a series."""
    if df is None or len(df) == 0:
        return []
    
    # Filter by series if specified
    if series_id and 'series_id' in df.columns:
        series_df = df[df['series_id'] == series_id]
    else:
        series_df = df
    
    # Extract metrics from measurements column
    metrics = set()
    for idx, row in series_df.iterrows():
        if 'measurements' in row and isinstance(row['measurements'], dict):
            metrics.update(row['measurements'].keys())
        # Also check for financial fields
        for field in ['open', 'high', 'low', 'close', 'vol', 'openint']:
            if field in row and pd.notna(row[field]):
                metrics.add(field)
    
    return sorted(list(metrics))


def extract_ohlcv_data(df: pd.DataFrame, series_id: Optional[str] = None) -> Dict[str, List]:
    """Extract OHLCV data from DataFrame, handling both direct columns and measurements dict."""
    if series_id and 'series_id' in df.columns:
        plot_df = df[df['series_id'] == series_id].copy()
    else:
        plot_df = df.copy()
    
    # Sort by timestamp
    if 'timestamp' in plot_df.columns:
        plot_df = plot_df.sort_values('timestamp')
    
    # Extract OHLCV values
    timestamps_raw = plot_df['timestamp'].tolist() if 'timestamp' in plot_df.columns else []
    # Convert timestamps to strings (handle pandas Timestamp, datetime, etc.)
    timestamps = []
    for ts in timestamps_raw:
        if pd.isna(ts):
            timestamps.append(None)
        elif isinstance(ts, pd.Timestamp):
            timestamps.append(ts.isoformat())
        elif hasattr(ts, 'isoformat'):
            timestamps.append(ts.isoformat())
        else:
            timestamps.append(str(ts))
    
    ohlcv_data = {
        'timestamp': timestamps,
        'open': [],
        'high': [],
        'low': [],
        'close': [],
        'volume': []
    }
    
    for idx, row in plot_df.iterrows():
        # Try direct columns first
        if all(col in plot_df.columns for col in ['open', 'high', 'low', 'close']):
            ohlcv_data['open'].append(row.get('open'))
            ohlcv_data['high'].append(row.get('high'))
            ohlcv_data['low'].append(row.get('low'))
            ohlcv_data['close'].append(row.get('close'))
            ohlcv_data['volume'].append(row.get('vol') or row.get('volume', 0))
        # Try measurements dict
        elif 'measurements' in row and isinstance(row['measurements'], dict):
            measurements = row['measurements']
            ohlcv_data['open'].append(measurements.get('open'))
            ohlcv_data['high'].append(measurements.get('high'))
            ohlcv_data['low'].append(measurements.get('low'))
            ohlcv_data['close'].append(measurements.get('close'))
            ohlcv_data['volume'].append(measurements.get('vol') or measurements.get('volume', 0))
        else:
            continue
    
    # Filter out rows with missing OHLC data
    valid_indices = [
        i for i in range(len(ohlcv_data['timestamp']))
        if all(ohlcv_data[key][i] is not None for key in ['open', 'high', 'low', 'close'])
    ]
    
    return {
        'timestamp': [ohlcv_data['timestamp'][i] for i in valid_indices],
        'open': [ohlcv_data['open'][i] for i in valid_indices],
        'high': [ohlcv_data['high'][i] for i in valid_indices],
        'low': [ohlcv_data['low'][i] for i in valid_indices],
        'close': [ohlcv_data['close'][i] for i in valid_indices],
        'volume': [ohlcv_data['volume'][i] for i in valid_indices]
    }


def create_matplotlib_financial_plot(df: pd.DataFrame, series_id: Optional[str] = None, chart_type: str = "candlestick", show_volume: bool = True):
    """Create Matplotlib financial chart (candlestick or OHLC) with optional volume subplot."""
    if not MATPLOTLIB_AVAILABLE:
        return None
    
    ohlcv = extract_ohlcv_data(df, series_id)
    
    if len(ohlcv['timestamp']) == 0:
        return None
    
    # Convert timestamps to datetime
    dates = [pd.to_datetime(ts) for ts in ohlcv['timestamp']]
    
    # Create figure
    if show_volume and any(v > 0 for v in ohlcv['volume']):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1], sharex=True)
    else:
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax2 = None
    
    # Set dark theme
    fig.patch.set_facecolor('#1e1e1e')
    ax1.set_facecolor('#1e1e1e')
    if ax2:
        ax2.set_facecolor('#1e1e1e')
    
    # Plot price chart
    if chart_type == "candlestick":
        from matplotlib.patches import Rectangle
        width = 0.6
        for i, date in enumerate(dates):
            open_price = ohlcv['open'][i]
            high_price = ohlcv['high'][i]
            low_price = ohlcv['low'][i]
            close_price = ohlcv['close'][i]
            
            color = '#26a69a' if close_price >= open_price else '#ef5350'
            
            # Draw high-low line
            ax1.plot([date, date], [low_price, high_price], color=color, linewidth=1)
            
            # Draw open-close rectangle
            body_low = min(open_price, close_price)
            body_high = max(open_price, close_price)
            rect = Rectangle((mdates.date2num(date) - width/2, body_low), 
                            width, body_high - body_low,
                            facecolor=color, edgecolor=color, linewidth=1)
            ax1.add_patch(rect)
    elif chart_type == "ohlc":
        # OHLC bars
        for i, date in enumerate(dates):
            open_price = ohlcv['open'][i]
            high_price = ohlcv['high'][i]
            low_price = ohlcv['low'][i]
            close_price = ohlcv['close'][i]
            
            color = '#26a69a' if close_price >= open_price else '#ef5350'
            
            # High-low line
            ax1.plot([date, date], [low_price, high_price], color=color, linewidth=2)
            
            # Open tick
            ax1.plot([date, date], [open_price, open_price], color=color, marker='|', markersize=8)
            # Close tick
            ax1.plot([date, date], [close_price, close_price], color=color, marker='|', markersize=8)
    else:  # line chart
        ax1.plot(dates, ohlcv['close'], color='#2196F3', linewidth=2, marker='o', markersize=4)
    
    ax1.set_ylabel('Price', color='white')
    ax1.tick_params(colors='white')
    ax1.grid(True, alpha=0.3, color='gray')
    
    # Plot volume if needed
    if ax2 and any(v > 0 for v in ohlcv['volume']):
        colors = ['#26a69a' if ohlcv['close'][i] >= ohlcv['open'][i] else '#ef5350' 
                 for i in range(len(ohlcv['close']))]
        ax2.bar(dates, ohlcv['volume'], color=colors, alpha=0.7, width=0.8)
        ax2.set_ylabel('Volume', color='white')
        ax2.tick_params(colors='white')
        ax2.grid(True, alpha=0.3, color='gray')
    
    # Format x-axis dates
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right', color='white')
    
    if ax2:
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right', color='white')
    
    plt.tight_layout()
    return fig


def create_matplotlib_plot(df: pd.DataFrame, series_id: Optional[str] = None, metric: Optional[str] = None):
    """Create Matplotlib time-series plot."""
    if not MATPLOTLIB_AVAILABLE:
        return None
    
    if df is None or len(df) == 0:
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor('#1e1e1e')
        ax.set_facecolor('#1e1e1e')
        ax.text(0.5, 0.5, 'No data available. Upload files to see time-series plots.',
               transform=ax.transAxes, ha='center', va='center', 
               fontsize=16, color='gray')
        ax.set_axis_off()
        return fig
    
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#1e1e1e')
    ax.set_facecolor('#1e1e1e')
    
    # Filter by series if specified
    if series_id and 'series_id' in df.columns:
        plot_df = df[df['series_id'] == series_id].copy()
    else:
        plot_df = df.copy()
    
    # Get unique series
    if 'series_id' in plot_df.columns:
        unique_series = plot_df['series_id'].unique()  # Show all series
    else:
        unique_series = ['default']
        plot_df['series_id'] = 'default'
    
    # Plot data
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
            series_data = series_data.dropna(subset=['value'])
            
            if len(series_data) > 0:
                dates = [pd.to_datetime(ts) for ts in series_data['timestamp']]
                ax.plot(dates, series_data['value'], label=f"{sid} - {metric}", linewidth=2, marker='o', markersize=4)
        else:
            # Plot default metric
            default_metrics = ['close', 'value', 'temperature', 'price']
            metric_to_plot = None
            
            for m in default_metrics:
                if m in series_data.columns:
                    metric_to_plot = m
                    break
            
            if metric_to_plot:
                dates = [pd.to_datetime(ts) for ts in series_data['timestamp']]
                ax.plot(dates, series_data[metric_to_plot], label=f"{sid} - {metric_to_plot}", linewidth=2, marker='o', markersize=4)
    
    ax.set_xlabel('Time', color='white')
    ax.set_ylabel('Value', color='white')
    ax.tick_params(colors='white')
    ax.grid(True, alpha=0.3, color='gray')
    ax.legend(loc='best', facecolor='#1e1e1e', edgecolor='gray', labelcolor='white')
    
    # Format dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', color='white')
    
    plt.tight_layout()
    return fig


def matplotlib_figure_to_base64(fig) -> str:
    """Convert matplotlib figure to base64 encoded image."""
    if not MATPLOTLIB_AVAILABLE:
        return ""
    
    buf = BytesIO()
    fig.savefig(buf, format='png', facecolor='#1e1e1e', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{img_base64}"


def create_financial_plot(df: pd.DataFrame, series_id: Optional[str] = None, chart_type: str = "candlestick", show_volume: bool = True) -> go.Figure:
    """Create financial chart (candlestick or OHLC) with optional volume subplot."""
    # Extract OHLCV data
    ohlcv = extract_ohlcv_data(df, series_id)
    
    if len(ohlcv['timestamp']) == 0:
        # Empty plot
        fig = go.Figure()
        fig.add_annotation(
            text="No financial data available. Ensure data contains OHLCV fields.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            template="plotly_dark",
            height=500,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        return fig
    
    # Create subplots if volume is shown
    if show_volume and any(v > 0 for v in ohlcv['volume']):
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=('Price', 'Volume')
        )
    else:
        fig = go.Figure()
    
    # Determine series name
    if series_id:
        series_name = series_id
    elif 'series_id' in df.columns and len(df['series_id'].unique()) == 1:
        series_name = df['series_id'].iloc[0]
    else:
        series_name = "Financial Data"
    
    # Add price chart
    if chart_type == "candlestick":
        trace = go.Candlestick(
            x=ohlcv['timestamp'],
            open=ohlcv['open'],
            high=ohlcv['high'],
            low=ohlcv['low'],
            close=ohlcv['close'],
            name=series_name,
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        )
    elif chart_type == "ohlc":
        trace = go.Ohlc(
            x=ohlcv['timestamp'],
            open=ohlcv['open'],
            high=ohlcv['high'],
            low=ohlcv['low'],
            close=ohlcv['close'],
            name=series_name,
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        )
    else:  # line chart
        trace = go.Scatter(
            x=ohlcv['timestamp'],
            y=ohlcv['close'],
            mode='lines+markers',
            name=f"{series_name} - Close",
            line=dict(width=2, color='#2196F3'),
            marker=dict(size=4)
        )
    
    if show_volume and any(v > 0 for v in ohlcv['volume']):
        fig.add_trace(trace, row=1, col=1)
        # Add volume bars
        colors = ['#26a69a' if ohlcv['close'][i] >= ohlcv['open'][i] else '#ef5350' 
                 for i in range(len(ohlcv['close']))]
        fig.add_trace(
            go.Bar(
                x=ohlcv['timestamp'],
                y=ohlcv['volume'],
                name='Volume',
                marker_color=colors,
                showlegend=False
            ),
            row=2, col=1
        )
        fig.update_yaxes(title_text="Volume", row=2, col=1)
    else:
        fig.add_trace(trace)
    
    # Update layout
    fig.update_layout(
        title=f"{series_name} - {chart_type.upper()} Chart",
        xaxis_title="Time",
        yaxis_title="Price" if show_volume else "Price",
        template="plotly_dark",
        height=600 if show_volume else 500,
        hovermode='x unified',
        xaxis_rangeslider_visible=False,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    if show_volume and any(v > 0 for v in ohlcv['volume']):
        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_yaxes(title_text="Price", row=1, col=1)
    
    return fig


def create_plot(df: pd.DataFrame, series_id: Optional[str] = None, metric: Optional[str] = None, chart_type: str = "auto") -> go.Figure:
    """Create Plotly time-series plot, with financial chart support."""
    if df is None or len(df) == 0:
        # Empty plot
        fig = go.Figure()
        fig.add_annotation(
            text="No data available. Upload files to see time-series plots.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Value",
            template="plotly_dark",  # Match NiceGUI dark theme
            height=500,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        return fig
    
    # Check if this is financial data and should use financial charts
    is_financial = is_financial_data(df, series_id)
    
    # Determine chart type
    if is_financial and (chart_type == "auto" or chart_type in ["candlestick", "ohlc"]):
        # Use financial chart
        actual_chart_type = chart_type if chart_type != "auto" else "candlestick"
        return create_financial_plot(df, series_id, actual_chart_type, show_volume=True)
    
    # Otherwise, use standard time-series plot
    fig = go.Figure()
    
    # Filter by series if specified
    if series_id and 'series_id' in df.columns:
        plot_df = df[df['series_id'] == series_id].copy()
    else:
        plot_df = df.copy()
    
    # Get unique series for plotting
    if 'series_id' in plot_df.columns:
        unique_series = plot_df['series_id'].unique()
    else:
        unique_series = ['default']
        plot_df['series_id'] = 'default'
    
    # Determine what to plot
    if metric:
        # Plot specific metric
        for sid in unique_series:
            series_data = plot_df[plot_df['series_id'] == sid].copy()
            
            # Extract metric values
            values = []
            for idx, row in series_data.iterrows():
                if 'measurements' in row and isinstance(row['measurements'], dict):
                    values.append(row['measurements'].get(metric))
                elif metric in row:
                    values.append(row[metric])
                else:
                    values.append(None)
            
            series_data['value'] = values
            series_data = series_data.dropna(subset=['value'])
            
            if len(series_data) > 0:
                # Convert timestamps to strings for JSON serialization
                timestamps = []
                for ts in series_data['timestamp']:
                    if pd.isna(ts):
                        timestamps.append(None)
                    elif isinstance(ts, pd.Timestamp):
                        timestamps.append(ts.isoformat())
                    elif hasattr(ts, 'isoformat'):
                        timestamps.append(ts.isoformat())
                    else:
                        timestamps.append(str(ts))
                
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=series_data['value'],
                    mode='lines+markers',
                    name=f"{sid} - {metric}",
                    line=dict(width=2),
                    marker=dict(size=4)
                ))
    else:
        # Plot all metrics for all series (or default to 'close' for financial)
        for sid in unique_series:  # Show all series
            series_data = plot_df[plot_df['series_id'] == sid].copy()
            
            # Try to find a default metric
            default_metrics = ['close', 'value', 'temperature', 'price']
            metric_to_plot = None
            
            for m in default_metrics:
                if m in series_data.columns:
                    metric_to_plot = m
                    break
                # Check in measurements
                for idx, row in series_data.iterrows():
                    if 'measurements' in row and isinstance(row['measurements'], dict):
                        if m in row['measurements']:
                            metric_to_plot = m
                            break
                if metric_to_plot:
                    break
            
            if not metric_to_plot and len(series_data) > 0:
                # Get first available metric
                first_row = series_data.iloc[0]
                if 'measurements' in first_row and isinstance(first_row['measurements'], dict):
                    metric_to_plot = list(first_row['measurements'].keys())[0] if first_row['measurements'] else None
            
            if metric_to_plot:
                values = []
                for idx, row in series_data.iterrows():
                    if 'measurements' in row and isinstance(row['measurements'], dict):
                        values.append(row['measurements'].get(metric_to_plot))
                    elif metric_to_plot in row:
                        values.append(row[metric_to_plot])
                    else:
                        values.append(None)
                
                series_data['value'] = values
                series_data = series_data.dropna(subset=['value'])
                
                if len(series_data) > 0:
                    # Convert timestamps to strings for JSON serialization
                    timestamps = []
                    for ts in series_data['timestamp']:
                        if pd.isna(ts):
                            timestamps.append(None)
                        elif isinstance(ts, pd.Timestamp):
                            timestamps.append(ts.isoformat())
                        elif hasattr(ts, 'isoformat'):
                            timestamps.append(ts.isoformat())
                        else:
                            timestamps.append(str(ts))
                    
                    fig.add_trace(go.Scatter(
                        x=timestamps,
                        y=series_data['value'],
                        mode='lines+markers',
                        name=f"{sid} - {metric_to_plot}",
                        line=dict(width=2),
                        marker=dict(size=4)
                    ))
    
    # Update layout - use dark theme to match NiceGUI dark mode
    fig.update_layout(
        title="Time-Series Data",
        xaxis_title="Time",
        yaxis_title="Value",
        template="plotly_dark",  # Match NiceGUI dark theme
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig
