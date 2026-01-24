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
                try:
                    app = get_app_instance()
                    file_data = app.storage.load(file_key)
                    if not file_data:
                        ui.notify(f"Could not load file: {file_key}", type="negative")
                        return
                    
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_key).suffix)
                    temp_file.write(file_data)
                    temp_file.close()
                    
                    try:
                        loader = FileLoader()
                        records = loader.load(temp_file.name)
                        
                        if not records:
                            ui.notify("No data found in file", type="warning")
                            return
                        
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
                try:
                    app = get_app_instance()
                    file_data = app.storage.load(file_key)
                    if not file_data:
                        ui.notify(f"Could not load file: {file_key}", type="negative")
                        return
                    
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_key).suffix)
                    temp_file.write(file_data)
                    temp_file.close()
                    
                    try:
                        loader = FileLoader()
                        records = loader.load(temp_file.name)
                        
                        if not records:
                            ui.notify("No data found in file", type="warning")
                            return
                        
                        df = pd.DataFrame(records)
                        
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
            
            def show_data_visualizer(file_key: str):
                """Show enhanced data visualization dialog."""
                try:
                    app = get_app_instance()
                    file_data = app.storage.load(file_key)
                    if not file_data:
                        ui.notify(f"Could not load file: {file_key}", type="negative")
                        return
                    
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_key).suffix)
                    temp_file.write(file_data)
                    temp_file.close()
                    
                    try:
                        loader = FileLoader()
                        records = loader.load(temp_file.name)
                        
                        if not records:
                            ui.notify("No data found in file", type="warning")
                            return
                        
                        expanded_records = []
                        for record in records:
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
                        
                        df = pd.DataFrame(expanded_records)
                        
                        if 'timestamp' in df.columns:
                            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                            df = df.sort_values('timestamp')
                            df = df.dropna(subset=['timestamp'])
                        
                        if len(df) == 0:
                            ui.notify("No valid data points found after processing", type="warning")
                            return
                        
                        with ui.dialog() as viz_dialog, ui.card().classes("w-full max-w-7xl max-h-[90vh] overflow-auto"):
                            ui.label(f"📊 Data Visualization: {Path(file_key).name}").classes("text-xl font-semibold mb-4")
                            
                            chart_type = ui.select(
                                ["line", "scatter", "bar", "area", "heatmap", "histogram", "box", "violin", "candlestick"],
                                label="Chart Type",
                                value="line"
                            ).classes("w-full mb-4")
                            
                            x_options = [col for col in df.columns if col not in ['series_id', 'metadata', 'format']]
                            x_col = ui.select(
                                x_options,
                                label="X Axis",
                                value="timestamp" if "timestamp" in x_options else (x_options[0] if x_options else None)
                            ).classes("w-full mb-2")
                            
                            numeric_cols = list(df.select_dtypes(include=['number']).columns)
                            y_options = [col for col in numeric_cols if col != x_col.value]
                            if not y_options:
                                y_options = [col for col in df.columns if col != x_col.value and col not in ['series_id', 'metadata', 'format']]
                            
                            y_cols = ui.select(
                                y_options,
                                label="Y Axis (select one or more)",
                                multiple=True,
                                value=y_options[:3] if len(y_options) >= 3 else y_options
                            ).classes("w-full mb-2")
                            
                            plot_container = ui.column().classes("w-full")
                            
                            def update_plot():
                                try:
                                    plot_container.clear()
                                    chart_type_val = chart_type.value
                                    x_col_val = x_col.value
                                    y_cols_val = y_cols.value if y_cols.value else [y_cols.options[0]] if y_cols.options else []
                                    
                                    if not y_cols_val:
                                        ui.label("Please select at least one Y axis column").classes("text-red-500")
                                        return
                                    
                                    cols_to_plot = [x_col_val] + (y_cols_val if isinstance(y_cols_val, list) else [y_cols_val])
                                    cols_to_plot = [col for col in cols_to_plot if col in df.columns]
                                    
                                    if not cols_to_plot:
                                        ui.label("No valid columns selected for plotting").classes("text-red-500")
                                        return
                                    
                                    plot_df = df[cols_to_plot].copy()
                                    
                                    for col in y_cols_val:
                                        if col in plot_df.columns:
                                            plot_df[col] = pd.to_numeric(plot_df[col], errors='coerce')
                                    
                                    plot_df = plot_df.dropna(subset=[x_col_val])
                                    y_has_data = plot_df[y_cols_val].notna().any(axis=1)
                                    plot_df = plot_df[y_has_data]
                                    
                                    if len(plot_df) == 0:
                                        ui.label("No data to plot after removing NaN values.").classes("text-red-500")
                                        return
                                    
                                    fig = go.Figure()
                                    
                                    if chart_type_val == "line":
                                        for col in y_cols_val:
                                            sorted_df = plot_df.sort_values(x_col_val)
                                            fig.add_trace(go.Scatter(
                                                x=sorted_df[x_col_val],
                                                y=sorted_df[col],
                                                mode='lines+markers',
                                                name=col,
                                                line=dict(width=2)
                                            ))
                                    elif chart_type_val == "scatter":
                                        for col in y_cols_val:
                                            sorted_df = plot_df.sort_values(x_col_val)
                                            fig.add_trace(go.Scatter(
                                                x=sorted_df[x_col_val],
                                                y=sorted_df[col],
                                                mode='markers',
                                                name=col
                                            ))
                                    elif chart_type_val == "bar":
                                        for col in y_cols_val:
                                            fig.add_trace(go.Bar(x=plot_df[x_col_val], y=plot_df[col], name=col))
                                    
                                    fig.update_layout(
                                        title=f"Visualization: {Path(file_key).name} ({len(plot_df)} data points)",
                                        template="plotly_dark",
                                        xaxis=dict(title=x_col_val),
                                        yaxis=dict(title=", ".join(y_cols_val) if len(y_cols_val) <= 2 else "Values")
                                    )
                                    
                                    with plot_container:
                                        ui.plotly(fig).classes("w-full")
                                        
                                except Exception as e:
                                    logger.error(f"Error creating plot: {e}", exc_info=True)
                                    with plot_container:
                                        ui.label(f"Error creating plot: {str(e)}").classes("text-red-500")
                            
                            chart_type.on('update:modelValue', update_plot)
                            x_col.on('update:modelValue', update_plot)
                            y_cols.on('update:modelValue', update_plot)
                            
                            with ui.row().classes("w-full gap-2 mb-4"):
                                ui.button("🔄 Update Plot", icon="refresh", on_click=update_plot, color="primary")
                            
                            update_plot()
                            
                            with ui.row().classes("w-full justify-end mt-4"):
                                ui.button("Close", on_click=viz_dialog.close).props("flat")
                            
                            viz_dialog.open()
                            
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
                try:
                    app = get_app_instance()
                    if app.storage:
                        keys = app.storage.list_keys()[:100]
                        rows = []
                        
                        storage_files_container.clear()
                        
                        if not keys:
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
                                        
                                        def make_visualize_handler(file_key=k):
                                            return lambda: show_data_visualizer(file_key)
                                        
                                        with ui.row().classes("gap-2"):
                                            ui.button("📥 Download", icon="download", on_click=make_download_handler(k)).props("size=sm color=primary")
                                            ui.button("✏️ Edit", icon="edit", on_click=make_edit_handler(k)).props("size=sm color=secondary")
                                            ui.button("📊 Visualize", icon="show_chart", on_click=make_visualize_handler(k)).props("size=sm color=accent")
                        
                        storage_table.rows = rows
                        ui.notify("Storage refreshed", type="info")
                except Exception as e:
                    logger.error(f"Error refreshing storage: {e}")
                    ui.notify(f"Error: {str(e)}", type="negative")
            
            refresh_storage_button.on_click(refresh_storage)
            refresh_storage()
