"""
Storage Browser Card
Independent resizable window for browsing and managing stored files.
"""
import tempfile
import os
from pathlib import Path
from nicegui import ui
import pandas as pd
import plotly.graph_objects as go
from logger import get_logger
from file_loader import FileLoader
from data_cleaner import DataCleaner
from nicegui_app import get_app_instance

logger = get_logger()


def create_storage_card(panels_grid):
    """
    Create Storage Browser card.
    
    Args:
        panels_grid: The container where the card will be added.
    """
    with panels_grid:
        with ui.card().classes("w-full").props("data-section='storage'"):
            ui.label("💾 Storage Browser").classes("text-xl font-semibold mb-4")
            
            refresh_storage_button = ui.button("🔄 Refresh Storage", icon="refresh")
            
            storage_table = ui.table(
                columns=[
                    {"name": "key", "label": "Key", "field": "key", "required": True},
                    {"name": "size", "label": "Size", "field": "size"},
                    {"name": "type", "label": "Type", "field": "type"}
                ],
                rows=[],
                row_key="key"
            ).classes("w-full")
            
            storage_files_container = ui.column().classes("w-full gap-2 mt-4")
            
            def show_download_format_dialog(file_key: str):
                """Show dialog to download file in different formats."""
                logger.debug(f"[show_download_format_dialog] Opening dialog for: {file_key}")
                try:
                    # Validate file key
                    if not file_key:
                        logger.error("[show_download_format_dialog] Empty file key")
                        ui.notify("Invalid file key", type="negative")
                        return

                    app = get_app_instance()
                    if not app or not app.storage:
                        logger.error("[show_download_format_dialog] App or storage not available")
                        ui.notify("Storage not available", type="negative")
                        return

                    file_data = app.storage.load(file_key)
                    if not file_data:
                        logger.error(f"[show_download_format_dialog] Could not load file: {file_key}")
                        ui.notify(f"Could not load file: {file_key}", type="negative")
                        return

                    data_size = len(file_data)
                    logger.info(f"[show_download_format_dialog] Loaded {data_size} bytes for: {file_key}")

                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_key).suffix)
                    temp_file.write(file_data)
                    temp_file.close()
                    logger.debug(f"[show_download_format_dialog] Created temp file: {temp_file.name}")

                    try:
                        loader = FileLoader()
                        records = loader.load(temp_file.name)

                        if records is None:
                            logger.error(f"[show_download_format_dialog] FileLoader returned None for: {file_key}")
                            ui.notify("Failed to parse file", type="negative")
                            return

                        if not records:
                            logger.warning(f"[show_download_format_dialog] No records in file: {file_key}")
                            ui.notify("No data found in file", type="warning")
                            return

                        logger.info(f"[show_download_format_dialog] Loaded {len(records)} records for download")
                        
                        with ui.dialog() as download_dialog, ui.card().classes("w-full max-w-lg"):
                            ui.label(f"📥 Download: {Path(file_key).name}").classes("text-xl font-semibold mb-4")
                            ui.label(f"Found {len(records)} records. Choose export format:").classes("text-sm mb-4")
                            
                            from file_exporter import FileExporter
                            exporter = FileExporter()
                            all_formats = exporter.get_supported_formats()
                            
                            format_select = ui.select(
                                all_formats,
                                label="Export Format",
                                value="json"
                            ).classes("w-full mb-4")
                            
                            status_label = ui.label("Ready to download").classes("text-sm mb-4")
                            
                            def download_file():
                                try:
                                    export_format = format_select.value
                                    status_label.text = f"⏳ Exporting to {export_format.upper()}..."
                                    
                                    from file_exporter import FileExporter
                                    import base64
                                    
                                    original_name = Path(file_key).stem
                                    format_info = FileExporter.get_format_info(export_format)
                                    ext = format_info["ext"] if format_info else f".{export_format}"
                                    output_filename = f"{original_name}_export{ext}"
                                    
                                    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                                    temp_output.close()
                                    
                                    export_kwargs = {}
                                    if export_format in ["gzip", "bzip2", "zstandard"]:
                                        export_kwargs["base_format"] = "json"
                                    
                                    success = FileExporter.export(records, temp_output.name, export_format, **export_kwargs)
                                    
                                    if success:
                                        with open(temp_output.name, "rb") as f:
                                            export_data = f.read()
                                        
                                        b64_data = base64.b64encode(export_data).decode()
                                        mime_type = format_info["mime"] if format_info else "application/octet-stream"
                                        data_url = f"data:{mime_type};base64,{b64_data}"
                                        
                                        ui.run_javascript(f'''
                                            const link = document.createElement('a');
                                            link.href = '{data_url}';
                                            link.download = '{output_filename}';
                                            document.body.appendChild(link);
                                            link.click();
                                            document.body.removeChild(link);
                                        ''')
                                        
                                        status_label.text = f"✅ Downloaded as {output_filename}"
                                        ui.notify(f"Downloaded {output_filename}", type="positive")
                                        download_dialog.close()
                                    else:
                                        status_label.text = "❌ Export failed. Check logs."
                                        ui.notify("Export failed", type="negative")
                                    
                                    try:
                                        os.unlink(temp_output.name)
                                    except:
                                        pass
                                        
                                except Exception as e:
                                    logger.error(f"Error downloading file: {e}", exc_info=True)
                                    status_label.text = f"❌ Error: {str(e)}"
                                    ui.notify(f"Download error: {str(e)}", type="negative")
                            
                            with ui.row().classes("w-full gap-2"):
                                ui.button("Download", icon="download", color="primary", on_click=download_file)
                                ui.button("Cancel", on_click=download_dialog.close).props("flat")
                            
                            download_dialog.open()
                            
                    finally:
                        try:
                            os.unlink(temp_file.name)
                        except:
                            pass
                            
                except Exception as e:
                    logger.error(f"Error showing download dialog: {e}", exc_info=True)
                    ui.notify(f"Error: {str(e)}", type="negative")
            
            def show_data_editor(file_key: str):
                """Show data editor/cleaner dialog."""
                logger.debug(f"[show_data_editor] Opening editor for: {file_key}")
                try:
                    # Validate file key
                    if not file_key:
                        logger.error("[show_data_editor] Empty file key")
                        ui.notify("Invalid file key", type="negative")
                        return

                    app = get_app_instance()
                    if not app or not app.storage:
                        logger.error("[show_data_editor] App or storage not available")
                        ui.notify("Storage not available", type="negative")
                        return

                    file_data = app.storage.load(file_key)
                    if not file_data:
                        logger.error(f"[show_data_editor] Could not load file: {file_key}")
                        ui.notify(f"Could not load file: {file_key}", type="negative")
                        return

                    data_size = len(file_data)
                    logger.info(f"[show_data_editor] Loaded {data_size} bytes for: {file_key}")

                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_key).suffix)
                    temp_file.write(file_data)
                    temp_file.close()
                    logger.debug(f"[show_data_editor] Created temp file: {temp_file.name}")

                    try:
                        loader = FileLoader()
                        records = loader.load(temp_file.name)

                        if records is None:
                            logger.error(f"[show_data_editor] FileLoader returned None for: {file_key}")
                            ui.notify("Failed to parse file", type="negative")
                            return

                        if not records:
                            logger.warning(f"[show_data_editor] No records in file: {file_key}")
                            ui.notify("No data found in file", type="warning")
                            return

                        logger.info(f"[show_data_editor] Loaded {len(records)} records for editing")

                        df = pd.DataFrame(records)
                        logger.debug(f"[show_data_editor] DataFrame shape: {df.shape}, columns: {list(df.columns)}")
                        
                        with ui.dialog() as editor_dialog, ui.card().classes("w-full max-w-6xl max-h-[90vh] overflow-auto"):
                            ui.label(f"✏️ Data Editor: {Path(file_key).name}").classes("text-xl font-semibold mb-4")
                            
                            summary = DataCleaner.get_data_summary(df)
                            
                            with ui.expansion("📊 Data Summary", icon="info").classes("w-full mb-4"):
                                with ui.column().classes("gap-2 text-sm"):
                                    ui.label(f"Total Rows: {summary['total_rows']}").classes("font-semibold")
                                    ui.label(f"Total Columns: {summary['total_columns']}")
                                    ui.label(f"Duplicate Rows: {summary['duplicate_rows']}")
                            
                            ui.label("🧹 Cleaning Operations").classes("text-lg font-semibold mb-2")
                            
                            operations = []
                            operations_container = ui.column().classes("w-full gap-2 mb-4")
                            
                            def add_operation():
                                with operations_container:
                                    with ui.card().classes("w-full p-3 border") as card_element:
                                        with ui.row().classes("w-full items-center gap-2"):
                                            op_type = ui.select(
                                                ["drop_na", "fill_na", "remove_duplicates", "remove_outliers", 
                                                 "normalize_timestamps", "filter_rows", "rename_columns", 
                                                 "drop_columns", "add_column", "convert_type", "resample", 
                                                 "interpolate", "clip_values", "round_values"],
                                                label="Operation",
                                                value="drop_na"
                                            ).classes("flex-1")
                                            
                                            def remove_op():
                                                card_element.delete()
                                                if op in operations:
                                                    operations.remove(op)
                                            
                                            ui.button("❌", icon="close", on_click=remove_op).props("size=sm flat")
                                        
                                        op = {"operation": op_type.value, "params": {}}
                                        operations.append(op)
                            
                            with ui.row().classes("w-full gap-2 mb-2"):
                                ui.button("➕ Add Operation", icon="add", on_click=add_operation).props("outline")
                            
                            preview_df = df.copy()
                            preview_container = ui.column().classes("w-full")
                            save_btn = None
                            
                            def apply_operations():
                                nonlocal preview_df, save_btn
                                try:
                                    preview_df = DataCleaner.clean_dataframe(df.copy(), operations)
                                    preview_container.clear()
                                    with preview_container:
                                        ui.label(f"✅ Preview: {len(preview_df)} rows (was {len(df)} rows)").classes("text-sm font-semibold text-green-600 mb-2")
                                        preview_table = ui.table(
                                            columns=[{"name": col, "label": col, "field": col} for col in preview_df.columns[:10]],
                                            rows=preview_df.head(200).to_dict('records'),
                                            row_key="index"
                                        ).classes("w-full")
                                    
                                    if save_btn:
                                        save_btn.set_enabled(True)
                                    ui.notify("Operations applied. Review preview.", type="positive")
                                except Exception as e:
                                    logger.error(f"Error applying operations: {e}", exc_info=True)
                                    ui.notify(f"Error: {str(e)}", type="negative")
                            
                            def save_cleaned():
                                try:
                                    cleaned_records = preview_df.to_dict('records')
                                    import json
                                    cleaned_data = json.dumps(cleaned_records, indent=2, default=str).encode('utf-8')
                                    new_key = file_key.replace('.json', '_cleaned.json')
                                    app.storage.save(new_key, cleaned_data)
                                    ui.notify(f"Saved cleaned data to {new_key}", type="positive")
                                    editor_dialog.close()
                                    refresh_storage()
                                except Exception as e:
                                    logger.error(f"Error saving cleaned data: {e}")
                                    ui.notify(f"Error saving: {str(e)}", type="negative")
                            
                            with ui.row().classes("w-full gap-2 mb-4"):
                                ui.button("🔍 Preview", icon="preview", on_click=apply_operations).props("outline")
                                save_btn = ui.button("💾 Save Cleaned Data", icon="save", on_click=save_cleaned, color="primary")
                                save_btn.set_enabled(False)
                            
                            with ui.row().classes("w-full justify-end"):
                                ui.button("Close", on_click=editor_dialog.close).props("flat")
                            
                            editor_dialog.open()
                            
                    finally:
                        try:
                            os.unlink(temp_file.name)
                        except:
                            pass
                            
                except Exception as e:
                    logger.error(f"Error showing data editor: {e}", exc_info=True)
                    ui.notify(f"Error: {str(e)}", type="negative")
            
            # Track visualization cards
            viz_card_data = {}

            def show_data_visualizer(file_key: str):
                """Show enhanced data visualization in a movable, resizable card."""
                logger.debug(f"[show_data_visualizer] Starting visualization for file: {file_key}")
                try:
                    # Validate file key
                    if not file_key:
                        logger.error("[show_data_visualizer] Empty file key provided")
                        ui.notify("Invalid file key", type="negative")
                        return

                    app = get_app_instance()
                    if not app or not app.storage:
                        logger.error("[show_data_visualizer] App or storage not available")
                        ui.notify("Storage not available", type="negative")
                        return

                    logger.debug(f"[show_data_visualizer] Loading file from storage: {file_key}")
                    file_data = app.storage.load(file_key)

                    if not file_data:
                        logger.error(f"[show_data_visualizer] Could not load file data for: {file_key}")
                        ui.notify(f"Could not load file: {file_key}", type="negative")
                        return

                    # Log file data info
                    data_size = len(file_data) if file_data else 0
                    logger.info(f"[show_data_visualizer] Loaded {data_size} bytes from storage for: {file_key}")

                    if data_size == 0:
                        logger.warning(f"[show_data_visualizer] File is empty: {file_key}")
                        ui.notify("File is empty", type="warning")
                        return

                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_key).suffix)
                    temp_file.write(file_data)
                    temp_file.close()
                    logger.debug(f"[show_data_visualizer] Created temp file: {temp_file.name}")

                    try:
                        loader = FileLoader()
                        records = loader.load(temp_file.name)

                        if records is None:
                            logger.error(f"[show_data_visualizer] FileLoader returned None for: {file_key}")
                            ui.notify("Failed to parse file", type="negative")
                            return

                        if not records:
                            logger.warning(f"[show_data_visualizer] No records found in file: {file_key}")
                            ui.notify("No data found in file", type="warning")
                            return

                        logger.info(f"[show_data_visualizer] Loaded {len(records)} records from: {file_key}")

                        # Validate records structure
                        if not isinstance(records, list):
                            logger.error(f"[show_data_visualizer] Records is not a list: {type(records)}")
                            ui.notify("Invalid data format", type="negative")
                            return

                        # Log sample record
                        if len(records) > 0 and isinstance(records[0], dict):
                            sample_keys = list(records[0].keys())
                            logger.debug(f"[show_data_visualizer] Sample record keys: {sample_keys[:10]}")

                        expanded_records = []
                        expansion_errors = 0
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
                                expansion_errors += 1
                                logger.debug(f"[show_data_visualizer] Error expanding record: {e}")

                        if expansion_errors > 0:
                            logger.warning(f"[show_data_visualizer] {expansion_errors} records failed to expand")

                        logger.debug(f"[show_data_visualizer] Expanded {len(expanded_records)} records")

                        df = pd.DataFrame(expanded_records)
                        logger.debug(f"[show_data_visualizer] DataFrame shape: {df.shape}, columns: {list(df.columns)}")

                        if 'timestamp' in df.columns:
                            original_count = len(df)
                            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                            df = df.sort_values('timestamp')
                            invalid_count = df['timestamp'].isna().sum()
                            df = df.dropna(subset=['timestamp'])
                            logger.debug(f"[show_data_visualizer] Timestamp processing: {original_count} -> {len(df)} records ({invalid_count} invalid)")
                        else:
                            logger.warning(f"[show_data_visualizer] No 'timestamp' column in data")
                            logger.debug(f"[show_data_visualizer] Available columns: {list(df.columns)}")

                        if len(df) == 0:
                            logger.warning(f"[show_data_visualizer] No valid data points after processing: {file_key}")
                            ui.notify("No valid data points found after processing", type="warning")
                            return

                        logger.info(f"[show_data_visualizer] Ready to visualize {len(df)} data points")

                        # Generate unique card ID
                        import time
                        card_id = f"viz-{Path(file_key).stem}-{int(time.time() * 1000)}"
                        card_title = f"📈 {Path(file_key).name}"

                        # Store dataframe for this card
                        viz_card_data[card_id] = df.copy()

                        # Create the visualization card using JavaScript
                        ui.run_javascript(f'''
                            window.createVizCard("{card_id}", "{card_title}");
                        ''')

                        # Small delay to allow card creation, then populate
                        def populate_viz_card():
                            try:
                                # Create card content in panels_grid
                                with panels_grid:
                                    with ui.card().classes("w-full h-full").props(f'data-viz-card="{card_id}"').style("display: none;") as viz_card:
                                        # This hidden card holds our NiceGUI elements
                                        pass

                                # Get dataframe for this card
                                card_df = viz_card_data.get(card_id)
                                if card_df is None:
                                    return

                                x_options = [col for col in card_df.columns if col not in ['series_id', 'metadata', 'format']]
                                numeric_cols = list(card_df.select_dtypes(include=['number']).columns)
                                y_options = [col for col in numeric_cols if col != 'timestamp']
                                if not y_options:
                                    y_options = [col for col in card_df.columns if col != 'timestamp' and col not in ['series_id', 'metadata', 'format']]

                                # Create card content via JavaScript injection
                                x_opts_str = ','.join([f'"{opt}"' for opt in x_options])
                                y_opts_str = ','.join([f'"{opt}"' for opt in y_options])
                                default_y = y_options[:3] if len(y_options) >= 3 else y_options
                                default_y_str = ','.join([f'"{opt}"' for opt in default_y])
                                default_x = 'timestamp' if 'timestamp' in x_options else (x_options[0] if x_options else '')

                                # Prepare data for JavaScript
                                import json
                                chart_data = card_df.to_dict('list')
                                for key in chart_data:
                                    chart_data[key] = [str(v) if pd.notna(v) else None for v in chart_data[key]]
                                data_json = json.dumps(chart_data)

                                js_code = f'''
                                (function() {{
                                    const bodyEl = document.getElementById('viz-body-{card_id}');
                                    if (!bodyEl) {{
                                        console.error('Viz body not found: viz-body-{card_id}');
                                        return;
                                    }}

                                    // Store data globally for this card
                                    window.vizData = window.vizData || {{}};
                                    window.vizData['{card_id}'] = {data_json};

                                    // Create control panel
                                    const controlsDiv = document.createElement('div');
                                    controlsDiv.className = 'viz-controls';
                                    controlsDiv.style.cssText = 'padding: 8px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; background: #2d2d3d; border-radius: 4px; margin-bottom: 8px;';

                                    // Chart type selector
                                    const chartTypeLabel = document.createElement('label');
                                    chartTypeLabel.textContent = 'Chart: ';
                                    chartTypeLabel.style.color = 'white';
                                    const chartTypeSelect = document.createElement('select');
                                    chartTypeSelect.id = 'chart-type-{card_id}';
                                    chartTypeSelect.style.cssText = 'padding: 4px; border-radius: 4px; background: #1e1e2e; color: white; border: 1px solid #3b82f6;';
                                    ['line', 'scatter', 'bar', 'area'].forEach(t => {{
                                        const opt = document.createElement('option');
                                        opt.value = t;
                                        opt.textContent = t.charAt(0).toUpperCase() + t.slice(1);
                                        chartTypeSelect.appendChild(opt);
                                    }});

                                    // X-axis selector
                                    const xLabel = document.createElement('label');
                                    xLabel.textContent = 'X: ';
                                    xLabel.style.color = 'white';
                                    const xSelect = document.createElement('select');
                                    xSelect.id = 'x-axis-{card_id}';
                                    xSelect.style.cssText = 'padding: 4px; border-radius: 4px; background: #1e1e2e; color: white; border: 1px solid #3b82f6;';
                                    [{x_opts_str}].forEach(col => {{
                                        const opt = document.createElement('option');
                                        opt.value = col;
                                        opt.textContent = col;
                                        if (col === '{default_x}') opt.selected = true;
                                        xSelect.appendChild(opt);
                                    }});

                                    // Y-axis multi-select
                                    const yLabel = document.createElement('label');
                                    yLabel.textContent = 'Y: ';
                                    yLabel.style.color = 'white';
                                    const ySelect = document.createElement('select');
                                    ySelect.id = 'y-axis-{card_id}';
                                    ySelect.multiple = true;
                                    ySelect.style.cssText = 'padding: 4px; border-radius: 4px; background: #1e1e2e; color: white; border: 1px solid #3b82f6; min-width: 120px; max-height: 60px;';
                                    const defaultY = [{default_y_str}];
                                    [{y_opts_str}].forEach(col => {{
                                        const opt = document.createElement('option');
                                        opt.value = col;
                                        opt.textContent = col;
                                        if (defaultY.includes(col)) opt.selected = true;
                                        ySelect.appendChild(opt);
                                    }});

                                    // Update button
                                    const updateBtn = document.createElement('button');
                                    updateBtn.textContent = '🔄 Update';
                                    updateBtn.style.cssText = 'padding: 4px 12px; border-radius: 4px; background: #3b82f6; color: white; border: none; cursor: pointer;';
                                    updateBtn.onmouseover = () => updateBtn.style.background = '#2563eb';
                                    updateBtn.onmouseout = () => updateBtn.style.background = '#3b82f6';

                                    controlsDiv.appendChild(chartTypeLabel);
                                    controlsDiv.appendChild(chartTypeSelect);
                                    controlsDiv.appendChild(xLabel);
                                    controlsDiv.appendChild(xSelect);
                                    controlsDiv.appendChild(yLabel);
                                    controlsDiv.appendChild(ySelect);
                                    controlsDiv.appendChild(updateBtn);

                                    // Plot container
                                    const plotDiv = document.createElement('div');
                                    plotDiv.id = 'plot-{card_id}';
                                    plotDiv.style.cssText = 'flex: 1; min-height: 250px; width: 100%;';

                                    bodyEl.innerHTML = '';
                                    bodyEl.style.cssText = 'display: flex; flex-direction: column; height: 100%; padding: 8px;';
                                    bodyEl.appendChild(controlsDiv);
                                    bodyEl.appendChild(plotDiv);

                                    // Function to update plot
                                    function updatePlot() {{
                                        const data = window.vizData['{card_id}'];
                                        if (!data) return;

                                        const chartType = chartTypeSelect.value;
                                        const xCol = xSelect.value;
                                        const ySelected = Array.from(ySelect.selectedOptions).map(o => o.value);

                                        if (ySelected.length === 0) {{
                                            plotDiv.innerHTML = '<p style="color: #ef4444; padding: 20px;">Please select at least one Y axis column</p>';
                                            return;
                                        }}

                                        const traces = [];
                                        const xData = data[xCol] || [];

                                        ySelected.forEach((yCol, idx) => {{
                                            const yData = (data[yCol] || []).map(v => v === null ? null : parseFloat(v));
                                            const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'];

                                            if (chartType === 'line') {{
                                                traces.push({{
                                                    x: xData,
                                                    y: yData,
                                                    type: 'scatter',
                                                    mode: 'lines+markers',
                                                    name: yCol,
                                                    line: {{ width: 2, color: colors[idx % colors.length] }}
                                                }});
                                            }} else if (chartType === 'scatter') {{
                                                traces.push({{
                                                    x: xData,
                                                    y: yData,
                                                    type: 'scatter',
                                                    mode: 'markers',
                                                    name: yCol,
                                                    marker: {{ color: colors[idx % colors.length] }}
                                                }});
                                            }} else if (chartType === 'bar') {{
                                                traces.push({{
                                                    x: xData,
                                                    y: yData,
                                                    type: 'bar',
                                                    name: yCol,
                                                    marker: {{ color: colors[idx % colors.length] }}
                                                }});
                                            }} else if (chartType === 'area') {{
                                                traces.push({{
                                                    x: xData,
                                                    y: yData,
                                                    type: 'scatter',
                                                    mode: 'lines',
                                                    fill: 'tozeroy',
                                                    name: yCol,
                                                    line: {{ width: 2, color: colors[idx % colors.length] }}
                                                }});
                                            }}
                                        }});

                                        const layout = {{
                                            title: {{ text: '{Path(file_key).name}', font: {{ color: 'white' }} }},
                                            paper_bgcolor: '#1e1e2e',
                                            plot_bgcolor: '#1e1e2e',
                                            xaxis: {{
                                                title: {{ text: xCol, font: {{ color: 'white' }} }},
                                                gridcolor: '#374151',
                                                tickfont: {{ color: 'white' }}
                                            }},
                                            yaxis: {{
                                                title: {{ text: ySelected.length <= 2 ? ySelected.join(', ') : 'Values', font: {{ color: 'white' }} }},
                                                gridcolor: '#374151',
                                                tickfont: {{ color: 'white' }}
                                            }},
                                            legend: {{ font: {{ color: 'white' }} }},
                                            margin: {{ t: 40, b: 50, l: 60, r: 20 }},
                                            autosize: true
                                        }};

                                        Plotly.newPlot(plotDiv, traces, layout, {{ responsive: true }});
                                    }}

                                    // Bind update event
                                    updateBtn.onclick = updatePlot;
                                    chartTypeSelect.onchange = updatePlot;
                                    xSelect.onchange = updatePlot;
                                    ySelect.onchange = updatePlot;

                                    // Initial plot
                                    setTimeout(updatePlot, 100);

                                    // Handle resize
                                    const resizeObserver = new ResizeObserver(() => {{
                                        const plotEl = document.getElementById('plot-{card_id}');
                                        if (plotEl && plotEl.data) {{
                                            Plotly.Plots.resize(plotEl);
                                        }}
                                    }});
                                    resizeObserver.observe(bodyEl);
                                }})();
                                '''
                                ui.run_javascript(js_code)
                                ui.notify(f"Visualization card created for {Path(file_key).name}", type="positive")

                            except Exception as e:
                                logger.error(f"Error populating viz card: {e}", exc_info=True)

                        # Delay to allow JS card creation
                        ui.timer(0.3, populate_viz_card, once=True)

                    finally:
                        try:
                            os.unlink(temp_file.name)
                        except:
                            pass

                except Exception as e:
                    logger.error(f"Error showing visualizer: {e}", exc_info=True)
                    ui.notify(f"Error: {str(e)}", type="negative")
            
            def refresh_storage():
                """Refresh storage browser."""
                logger.debug("[refresh_storage] Starting storage refresh")
                try:
                    app = get_app_instance()
                    if not app:
                        logger.error("[refresh_storage] App instance not available")
                        ui.notify("App not available", type="negative")
                        return

                    if not app.storage:
                        logger.error("[refresh_storage] Storage not available")
                        ui.notify("Storage not configured", type="negative")
                        return

                    if app.storage:
                        keys = app.storage.list_keys()[:100]
                        logger.info(f"[refresh_storage] Found {len(keys)} files in storage")
                        rows = []

                        storage_files_container.clear()

                        if not keys:
                            logger.debug("[refresh_storage] Storage is empty")
                            with storage_files_container:
                                ui.label("No files in storage").classes("text-gray-500")
                        
                        for k in keys:
                            file_type = k.split('.')[-1].upper() if '.' in k else 'DATA'
                            
                            size_bytes = app.storage.get_size(k)
                            if size_bytes is not None:
                                if size_bytes >= 1024 * 1024 * 1024:
                                    size_str = f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
                                elif size_bytes >= 1024 * 1024:
                                    size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
                                elif size_bytes >= 1024:
                                    size_str = f"{size_bytes / 1024:.2f} KB"
                                else:
                                    size_str = f"{size_bytes} B"
                            else:
                                try:
                                    file_data = app.storage.load(k)
                                    size_bytes = len(file_data) if file_data else 0
                                    if size_bytes >= 1024 * 1024:
                                        size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
                                    elif size_bytes >= 1024:
                                        size_str = f"{size_bytes / 1024:.2f} KB"
                                    else:
                                        size_str = f"{size_bytes} B"
                                except:
                                    size_str = "N/A"
                            
                            rows.append({
                                "key": k,
                                "size": size_str,
                                "type": file_type
                            })
                            
                            with storage_files_container:
                                with ui.card().classes("w-full p-3 hover:bg-gray-50"):
                                    with ui.row().classes("w-full items-center justify-between"):
                                        with ui.column().classes("flex-1"):
                                            ui.label(Path(k).name).classes("font-semibold")
                                            with ui.row().classes("gap-4 text-xs text-gray-500 mt-1"):
                                                ui.label(f"Size: {size_str}")
                                                ui.label(f"Type: {file_type}")
                                                ui.label(f"Key: {k}").classes("text-xs font-mono")
                                        
                                        def make_download_handler(file_key=k):
                                            return lambda: show_download_format_dialog(file_key)

                                        def make_edit_handler(file_key=k):
                                            return lambda: show_data_editor(file_key)

                                        with ui.row().classes("gap-2"):
                                            ui.button("📥 Download", icon="download", on_click=make_download_handler(k)).props("size=sm color=primary")
                                            ui.button("✏️ Edit", icon="edit", on_click=make_edit_handler(k)).props("size=sm color=secondary")
                        
                        storage_table.rows = rows
                        ui.notify("Storage refreshed", type="info")
                except Exception as e:
                    logger.error(f"Error refreshing storage: {e}")
                    ui.notify(f"Error: {str(e)}", type="negative")
            
            refresh_storage_button.on_click(refresh_storage)
            refresh_storage()
