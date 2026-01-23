# File Formats vs Online/API Formats

## Overview

VARIOSYNC supports two different types of formats:

1. **File Formats (33 formats)** - Storage and export formats for data files
2. **Online/API Formats** - Data sources accessed via REST APIs

---

## 📁 File Formats (33 Supported Formats)

**What they are**: File storage and export formats - how data is stored on disk or exported from VARIOSYNC.

**Where they're used**:
- **Input**: Files you upload to VARIOSYNC
- **Output**: Files you export/download from VARIOSYNC
- **Storage**: How data is persisted internally

### Categories of File Formats:

#### 1. **Text Formats** (Human-readable)
- `json` - JSON files
- `jsonl` - JSON Lines (one JSON per line)
- `csv` - Comma-separated values
- `txt` - Tab-delimited text

#### 2. **Binary Formats** (Efficient storage)
- `parquet` - Apache Parquet (columnar, compressed)
- `feather` - Apache Feather (fast binary)
- `arrow` - Apache Arrow (in-memory columnar)
- `h5` - HDF5 (scientific data)
- `avro` - Apache Avro (schema-based)
- `orc` - Apache ORC (Hadoop ecosystem)
- `msgpack` - MessagePack (efficient binary JSON)

#### 3. **Database Formats** (Embedded databases)
- `duckdb` - DuckDB database files
- `sqlite` - SQLite database files
- `timescaledb` - TimescaleDB format
- `questdb` - QuestDB format

#### 4. **Excel Formats** (Spreadsheet)
- `xlsx` - Microsoft Excel (modern)
- `xls` - Microsoft Excel (legacy)

#### 5. **Compression Formats** (Archive/compress)
- `gzip` - Gzip compression
- `bzip2` - Bzip2 compression
- `zstandard` - Zstandard compression
- `zip` - ZIP archive
- `tar` - TAR archive

#### 6. **Time-Series Database Formats** (TSDB ingestion)
- `influxdb` - InfluxDB Line Protocol
- `opentsdb` - OpenTSDB format
- `prometheus` - Prometheus Remote Write
- `victoriametrics` - VictoriaMetrics format
- `tdengine` - TDengine format
- `tsfile` - Apache IoTDB TsFile format

#### 7. **Scientific Formats** (Research data)
- `netcdf` - NetCDF (climate/oceanography)
- `zarr` - Zarr (cloud-native arrays)
- `fits` - FITS (astronomy)

#### 8. **Protocol Formats** (Network serialization)
- `protobuf` - Protocol Buffers

#### 9. **Specialized Formats**
- `stooq` - Stooq.com financial data format

**Total: 33 file formats**

---

## 🌐 Online/API Formats (Data Sources)

**What they are**: External data sources accessed via REST APIs that provide time-series data.

**Where they're used**:
- **Download**: Use the "Download" button in VARIOSYNC to fetch data from APIs
- **Real-time**: Get live or recent data from online services
- **Historical**: Access historical data from API providers

### Categories of API Sources:

#### 1. **Financial APIs**
- Alpha Vantage (stocks, forex, crypto)
- Finnhub (global stocks, forex)
- Twelve Data (stocks, forex, crypto)
- Financial Modeling Prep (equities, fundamentals)
- Marketstack (global stocks)
- Polygon.io (US equities, tick data)
- IEX Cloud (US stock market)

#### 2. **Weather & Climate APIs**
- OpenWeatherMap (current weather, forecasts)
- Open-Meteo (historical + forecasts, no API key!)
- NOAA Climate Data Online (US weather stations)
- Visual Crossing (global weather)
- Meteostat (global historical weather)

#### 3. **Economic Data APIs**
- FRED (St. Louis Fed) - US economic indicators
- World Bank Open Data - Global economic data
- OECD Data - International statistics
- IMF Data - Global macro data

#### 4. **Cryptocurrency APIs**
- CoinGecko (crypto market data)
- CryptoCompare (crypto prices)

#### 5. **IoT & Metrics APIs**
- ThingSpeak (IoT sensor data)
- InfluxDB Cloud (time-series database API)
- Prometheus (monitoring data)

#### 6. **Open Data Platforms**
- data.gov (US government data)
- Kaggle Datasets (community datasets)
- Our World in Data (global trends)

**Total: 20+ API sources** (see `API_SOURCES.md` for full list)

---

## Key Differences

| Aspect | File Formats | Online/API Formats |
|--------|-------------|-------------------|
| **Purpose** | Storage & export | Data acquisition |
| **Location** | Local files or storage | Remote servers |
| **Access** | File system | HTTP/REST API |
| **Authentication** | File permissions | API keys |
| **Format** | File extension (.csv, .json) | API response format (JSON, CSV) |
| **Use Case** | Store/export processed data | Download fresh data |
| **Examples** | `data.csv`, `export.parquet` | Alpha Vantage API, OpenWeatherMap API |

---

## How They Work Together

### Typical Workflow:

1. **Download from API** (Online Format)
   ```
   Alpha Vantage API → JSON response → VARIOSYNC processes → Stores internally
   ```

2. **Export to File** (File Format)
   ```
   VARIOSYNC storage → Export as Parquet → data.parquet file
   ```

3. **Upload File** (File Format)
   ```
   CSV file → Upload to VARIOSYNC → Processes → Stores internally
   ```

4. **Convert Between Formats** (File Format)
   ```
   CSV file → VARIOSYNC → Export as JSON → JSON file
   ```

---

## Examples

### Example 1: Download from API → Export to File

```python
# 1. Download from Alpha Vantage API (Online Format)
# API returns JSON response

# 2. VARIOSYNC processes and stores internally

# 3. Export to Parquet file (File Format)
app.export_data("AAPL_data", "parquet", "aapl.parquet")
```

### Example 2: Upload File → Process → Export Different Format

```python
# 1. Upload CSV file (File Format)
app.process_data_file("weather_data.csv", record_type="time_series")

# 2. Export to JSON (File Format)
app.export_data("weather_data", "json", "weather.json")
```

### Example 3: API Response Format vs File Format

**API Response** (Online Format):
```json
{
  "Time Series (Daily)": {
    "2024-01-15": {
      "1. open": "185.50",
      "2. high": "186.20",
      "3. low": "185.10",
      "4. close": "185.85",
      "5. volume": "12345678"
    }
  }
}
```

**Exported File** (File Format - CSV):
```csv
timestamp,open,high,low,close,volume
2024-01-15,185.50,186.20,185.10,185.85,12345678
```

---

## Summary

- **33 File Formats**: How VARIOSYNC stores and exports data (CSV, JSON, Parquet, DuckDB, etc.)
- **20+ API Sources**: Where VARIOSYNC downloads data from (Alpha Vantage, OpenWeatherMap, FRED, etc.)

**File Formats** = Storage/Export formats  
**Online Formats** = Data source APIs

Both work together: Download from APIs → Process → Store/Export in file formats.

---

## Related Documentation

- **File Formats**: See `TIMESERIES_FORMATS.md` for detailed format documentation
- **API Sources**: See `API_SOURCES.md` for complete API source list
- **Free Data**: See `FREE_DATA_SOURCES.md` for downloadable datasets
