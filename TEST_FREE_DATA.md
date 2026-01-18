# Testing VARIOSYNC with Free Data

Quick guide to test VARIOSYNC with free time-series data sources.

## Quick Test Script

Run the automated test script:

```bash
python3 test_free_data.py
```

This will:
- ✅ Download/generate sample datasets
- ✅ Test format loading (CSV, JSON, etc.)
- ✅ Test format export (33 formats)
- ✅ Test data processing

## Manual Testing via Web UI

### Step 1: Generate Test Data

The test script creates sample data in `test_data/` directory:

- `sample_sensor.json` - Sensor data (24 records)
- `sample_stock.csv` - Stock market data (30 records)  
- `world_bank_gdp.csv` - GDP data (20 records)

### Step 2: Upload via Web UI

1. **Start the application**:
   ```bash
   python3 run_nicegui.py
   ```

2. **Open browser**: http://localhost:8000

3. **Upload a file**:
   - Click "Upload" button
   - Select a file from `test_data/` directory
   - Format will be auto-detected
   - Select record type (time_series or financial)
   - Click "Process File"

### Step 3: Test Format Conversion

1. **After processing**, click "Download" button
2. **Select export format** from dropdown (33 formats available)
3. **Download** and verify the file

## Testing with Real Free Data Sources

### Option 1: Download from Public Sources

#### World Bank Data
```bash
# Download GDP data
curl "https://api.worldbank.org/v2/en/country/all/indicator/NY.GDP.PCAP.CD?format=csv&date=2020:2023&per_page=100" -o world_bank_gdp.csv

# Upload via web UI
```

#### Sample Stock Data (Yahoo Finance)
```python
import yfinance as yf
data = yf.download("AAPL", start="2024-01-01", end="2024-01-31")
data.to_csv("aapl_data.csv")
# Upload via web UI
```

### Option 2: Use Pre-made Test Files

The test script generates properly formatted files:
- ✅ Correct field names (series_id, timestamp, measurements)
- ✅ Proper data types
- ✅ Multiple formats (CSV, JSON)

## Test Scenarios

### Scenario 1: Upload CSV → Export to Parquet
1. Upload `test_data/sample_stock.csv`
2. Process as "financial" record type
3. Download → Select "parquet" format
4. Verify file can be opened

### Scenario 2: Upload JSON → Export to Multiple Formats
1. Upload `test_data/sample_sensor.json`
2. Process as "time_series" record type
3. Test exporting to:
   - JSONL
   - CSV
   - Stooq format
   - InfluxDB Line Protocol
   - Parquet

### Scenario 3: Format Conversion Chain
1. Upload CSV
2. Export to Parquet
3. Upload Parquet
4. Export to JSON
5. Verify data integrity

## Expected Results

### ✅ Successful Tests Should Show:
- File uploads successfully
- Format auto-detected correctly
- Data loads (shows record count)
- Processing completes (shows success message)
- Export works (file downloads)
- All 33 formats available in export dropdown

### ⚠️ Common Issues:

1. **Processing fails**: Check record type matches data format
   - Financial data → Use "financial" record type
   - Sensor/time-series → Use "time_series" record type

2. **Format not detected**: Manually select format in dropdown

3. **Empty records**: Check data format matches VARIOSYNC schema:
   ```json
   {
     "series_id": "SENSOR-001",
     "timestamp": "2024-01-15T09:00:00",
     "measurements": {
       "temperature": 22.3
     }
   }
   ```

## Test Data Locations

After running `test_free_data.py`:
- **Test files**: `test_data/` directory
- **Logs**: Check console output
- **Processed data**: Stored in `data/` directory (local storage)

## Next Steps

1. ✅ Run automated test: `python3 test_free_data.py`
2. ✅ Test via web UI with generated files
3. ✅ Download real data from free sources
4. ✅ Test all 33 export formats
5. ✅ Verify data integrity through conversion chains

## Free Data Sources

See `FREE_DATA_SOURCES.md` for comprehensive list of free data sources:
- World Bank Open Data
- FRED Economic Data
- NOAA Weather Data
- Kaggle Datasets
- UCI Machine Learning Repository
- And many more...

## Troubleshooting

### Test script fails:
- Check internet connection (for downloads)
- Verify Python dependencies installed
- Check `test_data/` directory is writable

### Web UI upload fails:
- Check file format is supported (33 formats)
- Verify file isn't corrupted
- Check file size (very large files may timeout)
- Try manual format selection

### Processing fails:
- Verify data has required fields (series_id, timestamp)
- Check record type matches data structure
- Review error messages in console/logs
