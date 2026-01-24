"""
Upload & Process Files Card
Independent resizable window for file upload and processing.
"""
import tempfile
from pathlib import Path
from nicegui import ui
from logger import get_logger
from main import VariosyncApp
from nicegui_app import get_app_instance

logger = get_logger()


def create_upload_card(panels_grid, refresh_callbacks=None):
    """
    Create Upload & Process Files card.
    
    Args:
        panels_grid: The container where the card will be added.
        refresh_callbacks: Dict with 'plot' and 'storage' callback functions.
    """
    if refresh_callbacks is None:
        refresh_callbacks = {}
    
    with panels_grid:
        with ui.card().classes("w-full").props("data-section='upload'"):
            ui.label("📤 Upload & Process Files").classes("text-xl font-semibold mb-4")
            
            with ui.column().classes("w-full gap-4"):
                uploaded_file_info = {"name": None, "content": None, "temp_path": None}
                
                def handle_upload(e):
                    """Handle file upload."""
                    try:
                        if hasattr(e, 'file'):
                            file_content = e.file._data
                            file_name = e.file.name
                        else:
                            file_content = e.content.read() if hasattr(e, 'content') else None
                            file_name = e.name if hasattr(e, 'name') else "unknown"
                        
                        if file_content is None:
                            raise ValueError("Could not read file content from upload event")
                        
                        uploaded_file_info["name"] = file_name
                        uploaded_file_info["content"] = file_content
                        
                        temp_dir = Path(tempfile.gettempdir())
                        temp_file = temp_dir / f"variosync_{file_name}"
                        with open(temp_file, "wb") as f:
                            f.write(file_content)
                        uploaded_file_info["temp_path"] = str(temp_file)
                        
                        file_size = len(file_content)
                        file_size_mb = file_size / (1024 * 1024)
                        size_str = f"{file_size_mb:.2f} MB" if file_size_mb >= 1 else f"{file_size / 1024:.2f} KB"
                        
                        status_label.text = f"📁 File ready: {file_name} ({size_str})"
                        file_info_label.text = f"📄 {file_name} • {size_str} • Ready to process"
                        file_info_label.visible = True
                        format_selector.visible = True
                        
                        detected_format = loader.detect_format(file_name)
                        if detected_format:
                            for i, opt in enumerate(format_options):
                                if opt == detected_format:
                                    format_selector.value = opt
                                    break
                        
                        process_button.set_enabled(True)
                        plotly_button.set_enabled(True)
                        plotly_format_select.visible = True
                        if file_name.lower().endswith('.csv'):
                            convert_button.set_enabled(True)
                        else:
                            convert_button.set_enabled(False)
                        
                        logger.info(f"File uploaded: {file_name} ({size_str})")
                    except Exception as ex:
                        logger.error(f"Error handling upload: {ex}", exc_info=True)
                        status_label.text = f"❌ Upload error: {str(ex)}"
                        ui.notify(f"Upload error: {str(ex)}", type="negative")
                
                from file_loader import FileLoader
                loader = FileLoader()
                supported_formats = loader.get_supported_formats()
                format_options = ["Auto-detect"] + sorted(supported_formats)
                
                format_selector = ui.select(
                    format_options,
                    label="File Format (optional)",
                    value="Auto-detect"
                ).classes("w-full")
                format_selector.visible = False
                
                file_upload = ui.upload(
                    label=f"Drop file or click to browse (Supports: {len(supported_formats)} formats)",
                    auto_upload=False,
                    on_upload=handle_upload
                ).classes("w-full")
                
                formats_list = sorted(supported_formats)
                formats_preview = ', '.join(formats_list[:8])
                formats_hint = ui.label(
                    f"📋 Supported formats ({len(supported_formats)}): {formats_preview}... (click to see all)"
                ).classes("text-xs text-gray-500 mt-1 cursor-pointer")
                
                formats_expanded = False
                def toggle_formats():
                    nonlocal formats_expanded
                    formats_expanded = not formats_expanded
                    if formats_expanded:
                        formats_hint.text = f"📋 Supported formats ({len(supported_formats)}): {', '.join(formats_list)}"
                    else:
                        formats_hint.text = f"📋 Supported formats ({len(supported_formats)}): {formats_preview}... (click to see all)"
                
                formats_hint.on('click', toggle_formats)
                
                file_info_label = ui.label("").classes("text-sm text-gray-600")
                file_info_label.visible = False
                
                record_type = ui.select(
                    ["time_series", "financial"],
                    label="Record Type",
                    value="time_series"
                ).classes("w-full")
                
                plotly_format_select = ui.select(
                    ["json", "parquet", "csv"],
                    label="Plotly Format",
                    value="json"
                ).classes("w-full")
                plotly_format_select.visible = False
                
                with ui.row().classes("w-full gap-2"):
                    process_button = ui.button("⚡ Process File", icon="bolt", color="positive")
                    process_button.set_enabled(False)
                    
                    convert_button = ui.button("🔄 Convert CSV to DuckDB", icon="transform", color="primary")
                    convert_button.set_enabled(False)
                    
                    plotly_button = ui.button("📊 Convert to Plotly Format", icon="show_chart", color="secondary")
                    plotly_button.set_enabled(False)
                
                status_label = ui.label("✨ Ready to process files").classes("text-sm")
                
                results_card = None
                results_container_parent = None
                
                def show_results(success: bool, file_name: str, new_keys: list = None, error: str = None):
                    """Show processing results."""
                    nonlocal results_card, results_container_parent
                    
                    if results_card is not None:
                        try:
                            results_card.delete()
                        except:
                            pass
                    
                    if results_container_parent is None:
                        results_container_parent = ui.column().classes("w-full gap-2")
                    
                    if success:
                        with results_container_parent:
                            with ui.card().classes("w-full border-2 border-green-500") as results_card:
                                ui.label("✅ Processing Complete").classes("text-lg font-semibold text-green-600")
                                ui.label(f"📁 File: {file_name}").classes("text-sm")
                                if new_keys:
                                    ui.label(f"📊 Records saved: {len(new_keys)}").classes("text-sm")
                                ui.label(f"🏷️  Type: {record_type.value}").classes("text-sm")
                                
                                if new_keys and len(new_keys) > 0:
                                    with ui.expansion("📋 View saved records", icon="list").classes("w-full"):
                                        with ui.column().classes("gap-1"):
                                            for key in sorted(list(new_keys))[:20]:
                                                ui.label(f"• {key}").classes("text-xs font-mono")
                                            if len(new_keys) > 20:
                                                ui.label(f"... and {len(new_keys) - 20} more").classes("text-xs text-gray-500")
                    else:
                        with results_container_parent:
                            with ui.card().classes("w-full border-2 border-red-500") as results_card:
                                ui.label("❌ Processing Failed").classes("text-lg font-semibold text-red-600")
                                if error:
                                    ui.label(f"Error: {error}").classes("text-sm font-mono")
                                else:
                                    ui.label("Please check that the file format matches the selected record type.").classes("text-sm")
                
                def convert_csv_to_duckdb():
                    """Convert CSV file to DuckDB format."""
                    nonlocal results_card, results_container_parent
                    
                    if not uploaded_file_info["temp_path"]:
                        ui.notify("Please select a CSV file first", type="warning")
                        return
                    
                    file_name = uploaded_file_info["name"]
                    if not file_name.lower().endswith('.csv'):
                        ui.notify("Please select a CSV file", type="warning")
                        return
                    
                    status_label.text = "⏳ Converting CSV to DuckDB..."
                    convert_button.set_enabled(False)
                    process_button.set_enabled(False)
                    file_upload.set_enabled(False)
                    
                    if results_card is not None:
                        try:
                            results_card.delete()
                            results_card = None
                        except:
                            pass
                    
                    if results_container_parent is None:
                        results_container_parent = ui.column().classes("w-full gap-2")
                    with results_container_parent:
                        with ui.card().classes("w-full") as progress_card:
                            ui.label("⏳ Converting CSV to DuckDB...").classes("text-sm")
                    
                    try:
                        temp_path = uploaded_file_info["temp_path"]
                        csv_path = Path(temp_path)
                        duckdb_path = str(csv_path.with_suffix('.duckdb'))
                        
                        app = get_app_instance()
                        success = app.convert_csv_to_duckdb(
                            csv_file_path=temp_path,
                            duckdb_file_path=duckdb_path,
                            table_name="time_series_data",
                            has_header=True,
                            if_exists="replace"
                        )
                        
                        try:
                            progress_card.delete()
                        except:
                            pass
                        
                        if success:
                            with results_container_parent:
                                with ui.card().classes("w-full border-2 border-blue-500") as results_card:
                                    ui.label("✅ Conversion Complete").classes("text-lg font-semibold text-blue-600")
                                    ui.label(f"📁 Input: {file_name}").classes("text-sm")
                                    ui.label(f"💾 Output: {Path(duckdb_path).name}").classes("text-sm")
                                    ui.label(f"📊 Table: time_series_data").classes("text-sm")
                            
                            status_label.text = f"✅ Converted {file_name} to DuckDB"
                            ui.notify(f"Successfully converted {file_name} to DuckDB", type="positive")
                            logger.info(f"CSV to DuckDB conversion successful: {duckdb_path}")
                        else:
                            show_results(False, file_name, error="Conversion failed. Check logs for details.")
                            status_label.text = f"❌ Conversion failed"
                            ui.notify("CSV to DuckDB conversion failed", type="negative")
                    except Exception as e:
                        logger.error(f"Error converting CSV to DuckDB: {e}")
                        show_results(False, file_name, error=str(e))
                        status_label.text = f"❌ Conversion error: {str(e)}"
                        ui.notify(f"Conversion error: {str(e)}", type="negative")
                    finally:
                        convert_button.set_enabled(True)
                        process_button.set_enabled(True)
                        file_upload.set_enabled(True)
                
                def convert_to_plotly_format():
                    """Convert uploaded file to Plotly-friendly format."""
                    nonlocal results_card, results_container_parent
                    
                    if not uploaded_file_info["temp_path"]:
                        ui.notify("Please select a file first", type="warning")
                        return
                    
                    file_name = uploaded_file_info["name"]
                    output_format = plotly_format_select.value
                    
                    status_label.text = f"⏳ Converting to Plotly {output_format.upper()} format..."
                    plotly_button.set_enabled(False)
                    process_button.set_enabled(False)
                    convert_button.set_enabled(False)
                    file_upload.set_enabled(False)
                    
                    if results_card is not None:
                        try:
                            results_card.delete()
                            results_card = None
                        except:
                            pass
                    
                    if results_container_parent is None:
                        results_container_parent = ui.column().classes("w-full gap-2")
                    with results_container_parent:
                        with ui.card().classes("w-full") as progress_card:
                            ui.label(f"⏳ Converting to {output_format.upper()} format...").classes("text-sm")
                    
                    try:
                        temp_path = uploaded_file_info["temp_path"]
                        input_path = Path(temp_path)
                        ext_map = {"json": ".json", "parquet": ".parquet", "csv": ".csv"}
                        ext = ext_map.get(output_format.lower(), ".json")
                        output_path = str(input_path.parent / f"{input_path.stem}_plotly{ext}")
                        
                        app = get_app_instance()
                        success = app.convert_to_plotly_format(
                            input_file_path=temp_path,
                            output_file_path=output_path,
                            output_format=output_format,
                            normalize_measurements=True
                        )
                        
                        try:
                            progress_card.delete()
                        except:
                            pass
                        
                        if success:
                            with results_container_parent:
                                with ui.card().classes("w-full border-2 border-purple-500") as results_card:
                                    ui.label("✅ Plotly Conversion Complete").classes("text-lg font-semibold text-purple-600")
                                    ui.label(f"📁 Input: {file_name}").classes("text-sm")
                                    ui.label(f"📊 Output: {Path(output_path).name}").classes("text-sm")
                                    ui.label(f"📦 Format: {output_format.upper()}").classes("text-sm")
                            
                            status_label.text = f"✅ Converted {file_name} to Plotly {output_format.upper()} format"
                            ui.notify(f"Successfully converted to Plotly {output_format.upper()} format", type="positive")
                            logger.info(f"Plotly format conversion successful: {output_path}")
                        else:
                            show_results(False, file_name, error="Conversion failed. Check logs for details.")
                            status_label.text = f"❌ Conversion failed"
                            ui.notify("Plotly format conversion failed", type="negative")
                    except Exception as e:
                        logger.error(f"Error converting to Plotly format: {e}")
                        show_results(False, file_name, error=str(e))
                        status_label.text = f"❌ Conversion error: {str(e)}"
                        ui.notify(f"Conversion error: {str(e)}", type="negative")
                    finally:
                        plotly_button.set_enabled(True)
                        process_button.set_enabled(True)
                        convert_button.set_enabled(True)
                        file_upload.set_enabled(True)
                
                def process_file():
                    """Process uploaded file."""
                    nonlocal results_card, results_container_parent
                    
                    if not uploaded_file_info["temp_path"]:
                        ui.notify("Please select a file first", type="warning")
                        return
                    
                    status_label.text = "⏳ Processing file..."
                    process_button.set_enabled(False)
                    convert_button.set_enabled(False)
                    file_upload.set_enabled(False)
                    
                    if results_card is not None:
                        try:
                            results_card.delete()
                            results_card = None
                        except:
                            pass
                    
                    if results_container_parent is None:
                        results_container_parent = ui.column().classes("w-full gap-2")
                    with results_container_parent:
                        with ui.card().classes("w-full") as progress_card:
                            ui.label("⏳ Processing...").classes("text-sm")
                    
                    try:
                        temp_path = uploaded_file_info["temp_path"]
                        file_name = uploaded_file_info["name"]
                        
                        app = get_app_instance()
                        file_format = None
                        if format_selector.value != "Auto-detect":
                            file_format = format_selector.value
                        
                        keys_before = set(app.storage.list_keys() if app.storage else [])
                        logger.info(f"Processing file: {file_name}, type: {record_type.value}, format: {file_format}")
                        
                        success = app.process_data_file(temp_path, record_type.value, file_format=file_format)
                        
                        keys_after = set(app.storage.list_keys() if app.storage else [])
                        new_keys = list(keys_after - keys_before)
                        
                        progress_card.delete()
                        
                        if success:
                            show_results(True, file_name, new_keys)
                            status_label.text = f"✅ Successfully processed {file_name} ({len(new_keys)} records)"
                            ui.notify(f"Successfully processed {len(new_keys)} records", type="positive")
                            logger.info(f"Successfully processed {file_name}: {len(new_keys)} records saved")
                            
                            # Call refresh callbacks if available
                            if 'plot' in refresh_callbacks:
                                refresh_callbacks['plot']()
                            if 'storage' in refresh_callbacks:
                                refresh_callbacks['storage']()
                            
                            try:
                                if Path(temp_path).exists():
                                    Path(temp_path).unlink()
                            except:
                                pass
                            
                            uploaded_file_info["name"] = None
                            uploaded_file_info["content"] = None
                            uploaded_file_info["temp_path"] = None
                            file_info_label.visible = False
                            process_button.set_enabled(False)
                        else:
                            error_msg = f"Processing failed for {record_type.value} mode. Check file format and ensure it contains required fields."
                            if record_type.value == "financial":
                                error_msg += " Financial files need: ticker/series_id, timestamp, and OHLCV fields (open, high, low, close, vol)."
                            logger.error(f"Processing failed: {file_name}, type: {record_type.value}, format: {file_format}")
                            show_results(False, file_name, error=error_msg)
                            status_label.text = f"❌ Processing failed ({record_type.value} mode)"
                            ui.notify(error_msg, type="negative")
                    except Exception as e:
                        logger.error(f"Error processing file: {e}", exc_info=True)
                        if 'progress_card' in locals():
                            progress_card.delete()
                        show_results(False, uploaded_file_info.get("name", "Unknown"), error=str(e))
                        status_label.text = f"❌ Error: {str(e)}"
                        ui.notify(f"Error: {str(e)}", type="negative")
                    finally:
                        process_button.set_enabled(True)
                        convert_button.set_enabled(True)
                        plotly_button.set_enabled(True)
                        file_upload.set_enabled(True)
                
                process_button.on_click(process_file)
                convert_button.on_click(convert_csv_to_duckdb)
                plotly_button.on_click(convert_to_plotly_format)
