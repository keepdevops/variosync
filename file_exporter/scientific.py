"""
Scientific and specialized format exporters (NetCDF, Zarr, FITS).
These formats are commonly used in scientific data analysis.
"""
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import json

from logger import get_logger

logger = get_logger()


class ScientificExporter:
    """Scientific format exporters."""
    
    @staticmethod
    def _extract_timeseries_data(data: List[Dict[str, Any]]) -> Tuple[List[float], Dict[str, List[float]], List[str]]:
        """
        Extract timestamps, measurements, and series IDs from data.
        
        Returns:
            Tuple of (timestamps, measurements_dict, series_ids)
        """
        import numpy as np
        
        timestamps = []
        measurements_dict = {}
        series_ids = []
        
        for record in data:
            # Extract timestamp
            timestamp = record.get("timestamp", "")
            if isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    timestamps.append(dt.timestamp())
                except:
                    logger.warning(f"Invalid timestamp format: {timestamp}")
                    continue
            elif isinstance(timestamp, (int, float)):
                timestamps.append(float(timestamp))
            else:
                continue
            
            # Extract series_id
            series_ids.append(record.get("series_id", "unknown"))
            
            # Extract measurements
            if "measurements" in record and isinstance(record["measurements"], dict):
                for key, value in record["measurements"].items():
                    if key not in measurements_dict:
                        measurements_dict[key] = []
                    measurements_dict[key].append(float(value) if isinstance(value, (int, float)) else np.nan)
        
        return timestamps, measurements_dict, series_ids
    
    @staticmethod
    def _add_metadata_attributes(obj: Any, data: List[Dict[str, Any]], **kwargs) -> None:
        """Add metadata attributes to NetCDF/Zarr/FITS objects."""
        obj.title = kwargs.get("title", "Time-series data")
        obj.source = kwargs.get("source", "VARIOSYNC")
        obj.history = f"Created by VARIOSYNC on {datetime.now().isoformat()}"
        if data and "metadata" in data[0]:
            for key, value in data[0]["metadata"].items():
                if hasattr(obj, "setncattr"):
                    obj.setncattr(f"metadata_{key}", str(value))
                elif hasattr(obj, "__setitem__"):
                    obj.attrs[f"metadata_{key}"] = str(value)
    
    @staticmethod
    def export_to_netcdf(
        data: List[Dict[str, Any]], 
        output_path: str,
        variable_name: str = "time_series",
        **kwargs
    ) -> bool:
        """Export data to NetCDF format."""
        try:
            import netCDF4
            import numpy as np
            
            if not data:
                logger.warning("No data to export")
                return False
            
            timestamps, measurements_dict, series_ids = ScientificExporter._extract_timeseries_data(data)
            if not timestamps:
                logger.error("No valid timestamps found")
                return False
            
            with netCDF4.Dataset(output_path, "w", format="NETCDF4") as nc:
                nc.createDimension("time", len(timestamps))
                unique_series = list(set(series_ids))
                if len(unique_series) > 1:
                    nc.createDimension("series", len(unique_series))
                    series_var = nc.createVariable("series_id", str, ("series",))
                    series_var[:] = np.array(unique_series, dtype=object)
                
                time_var = nc.createVariable("time", "f8", ("time",))
                time_var.units = "seconds since 1970-01-01 00:00:00"
                time_var.long_name = "Time"
                time_var[:] = np.array(timestamps)
                
                for meas_name, meas_values in measurements_dict.items():
                    if len(meas_values) == len(timestamps):
                        var = nc.createVariable(meas_name, "f8", ("time",))
                        var.long_name = f"Measurement: {meas_name}"
                        var[:] = np.array(meas_values)
                
                ScientificExporter._add_metadata_attributes(nc, data, **kwargs)
            
            logger.info(f"Exported {len(data)} records to NetCDF: {output_path}")
            return True
        except ImportError:
            logger.error("netCDF4 and numpy required. Install with: pip install netCDF4 numpy")
            return False
        except Exception as e:
            logger.error(f"Error exporting to NetCDF: {e}")
            return False
    
    @staticmethod
    def export_to_zarr(
        data: List[Dict[str, Any]], 
        output_path: str,
        chunk_size: int = 1000,
        **kwargs
    ) -> bool:
        """Export data to Zarr format."""
        try:
            import zarr
            import numpy as np
            
            if not data:
                logger.warning("No data to export")
                return False
            
            timestamps, measurements_dict, _ = ScientificExporter._extract_timeseries_data(data)
            if not timestamps:
                logger.error("No valid timestamps found")
                return False
            
            root = zarr.open(output_path, mode="w")
            compressor = kwargs.get("compressor", zarr.Blosc(cname="lz4", clevel=5))
            
            time_array = np.array(timestamps, dtype=np.float64)
            root.create_dataset("time", data=time_array, chunks=(chunk_size,), compressor=compressor)
            root["time"].attrs["units"] = "seconds since 1970-01-01 00:00:00"
            root["time"].attrs["long_name"] = "Time"
            
            for meas_name, meas_values in measurements_dict.items():
                if len(meas_values) == len(timestamps):
                    meas_array = np.array(meas_values, dtype=np.float64)
                    root.create_dataset(meas_name, data=meas_array, chunks=(chunk_size,), compressor=compressor)
                    root[meas_name].attrs["long_name"] = f"Measurement: {meas_name}"
            
            ScientificExporter._add_metadata_attributes(root.attrs, data, **kwargs)
            if data and "metadata" in data[0]:
                root.attrs["metadata"] = json.dumps(data[0]["metadata"], default=str)
            
            logger.info(f"Exported {len(data)} records to Zarr: {output_path}")
            return True
        except ImportError:
            logger.error("zarr and numpy required. Install with: pip install zarr numpy")
            return False
        except Exception as e:
            logger.error(f"Error exporting to Zarr: {e}")
            return False
    
    @staticmethod
    def export_to_fits(
        data: List[Dict[str, Any]], 
        output_path: str,
        **kwargs
    ) -> bool:
        """Export data to FITS format."""
        try:
            from astropy.io import fits
            import numpy as np
            
            if not data:
                logger.warning("No data to export")
                return False
            
            timestamps, measurements_dict, _ = ScientificExporter._extract_timeseries_data(data)
            if not timestamps:
                logger.error("No valid timestamps found")
                return False
            
            time_array = np.array(timestamps, dtype=np.float64)
            primary_hdu = fits.PrimaryHDU(data=time_array)
            primary_hdu.header["EXTNAME"] = ("TIME", "Time extension")
            primary_hdu.header["BUNIT"] = ("s", "Time unit: seconds since 1970-01-01")
            primary_hdu.header["TITLE"] = (kwargs.get("title", "Time-series data"), "Dataset title")
            primary_hdu.header["SOURCE"] = (kwargs.get("source", "VARIOSYNC"), "Data source")
            primary_hdu.header["DATE"] = (datetime.now().isoformat(), "File creation date")
            
            if data and "metadata" in data[0]:
                for idx, (key, value) in enumerate(data[0]["metadata"].items(), start=1):
                    primary_hdu.header[f"META{idx:03d}"] = (str(value), f"Metadata: {key}")
            
            hdul = fits.HDUList([primary_hdu])
            for meas_name, meas_values in measurements_dict.items():
                if len(meas_values) == len(timestamps):
                    meas_array = np.array(meas_values, dtype=np.float64)
                    meas_hdu = fits.ImageHDU(data=meas_array)
                    meas_hdu.header["EXTNAME"] = (meas_name, f"Measurement: {meas_name}")
                    meas_hdu.header["BUNIT"] = ("value", "Measurement unit")
                    hdul.append(meas_hdu)
            
            hdul.writeto(output_path, overwrite=kwargs.get("overwrite", True))
            hdul.close()
            
            logger.info(f"Exported {len(data)} records to FITS: {output_path}")
            return True
        except ImportError:
            logger.error("astropy required. Install with: pip install astropy numpy")
            return False
        except Exception as e:
            logger.error(f"Error exporting to FITS: {e}")
            return False
