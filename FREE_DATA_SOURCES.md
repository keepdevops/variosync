# Free Time-Series Data Sources (No API Key Required)

Comprehensive list of free time-series datasets available for direct download (CSV, JSON, etc.) that work perfectly with VARIOSYNC. No API keys or registration required.

## Table of Contents

- [Economic & Financial Data](#economic--financial-data)
- [Weather & Climate Data](#weather--climate-data)
- [IoT & Sensor Data](#iot--sensor-data)
- [Health & Demographics](#health--demographics)
- [Energy & Environment](#energy--environment)
- [Transportation & Traffic](#transportation--traffic)
- [Machine Learning Datasets](#machine-learning-datasets)
- [How to Use](#how-to-use)

---

## Economic & Financial Data

### 1. World Bank Open Data

**Description**: 1,400+ time-series indicators (GDP, population, trade, etc.) for 217+ countries, 50+ years of data

**Format**: CSV, Excel

**Download**: https://datatopics.worldbank.org/world-development-indicators

**Direct CSV Download**: Available via DataBank interface (no API key needed)

**Example Indicators**:
- GDP per capita
- Population growth
- Trade balance
- Inflation rates
- Unemployment rates

**Usage**: Download CSV → Upload to VARIOSYNC → Process as time_series

---

### 2. FRED (Federal Reserve Economic Data)

**Description**: US economic time-series data (unemployment, inflation, interest rates, etc.)

**Format**: CSV (via web interface)

**Download**: https://fred.stlouisfed.org

**Note**: Web interface allows CSV downloads without API key. API access requires key.

**Popular Series**:
- Unemployment Rate (UNRATE)
- Consumer Price Index (CPIAUCSL)
- Federal Funds Rate (FEDFUNDS)
- GDP (GDP)

**Usage**: Search series → Download CSV → Upload to VARIOSYNC

---

### 3. Yahoo Finance Historical Data

**Description**: Stock market historical data (via yfinance Python library or direct CSV exports)

**Format**: CSV

**Download**: Use yfinance library or export from Yahoo Finance website

**Note**: Free, but rate-limited. No API key needed for historical data.

**Usage**: 
```python
import yfinance as yf
data = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
data.to_csv("aapl_data.csv")
# Then upload to VARIOSYNC
```

---

### 4. Quandl (now Nasdaq Data Link)

**Description**: Financial and economic datasets (some free, some paid)

**Format**: CSV

**Download**: https://data.nasdaq.com

**Free Datasets**: Many economic indicators available for free download

---

## Weather & Climate Data

### 5. NOAA Climate Data

**Description**: US weather and climate data, historical records

**Format**: CSV, TXT

**Download**: https://www.ncei.noaa.gov/data

**Direct Access**: 
- Daily Summaries: https://www.ncei.noaa.gov/data/daily-summaries/
- Global Summary of the Day: https://www.ncei.noaa.gov/data/gsod/

**No API Key**: Direct file downloads available

**Usage**: Download CSV → Upload to VARIOSYNC → Process as time_series

---

### 6. Open-Meteo Historical Weather

**Description**: 80+ years of historical weather data, no API key required

**Format**: JSON, CSV (via API, but no key needed)

**Download**: https://archive-api.open-meteo.com

**Direct CSV Export**: Available via web interface

**Coverage**: Global, hourly/daily data

**Usage**: Use Open-Meteo API (no key) or download pre-generated CSV files

---

### 7. Berkeley Earth

**Description**: Global temperature data, climate datasets

**Format**: CSV

**Download**: http://berkeleyearth.org/data

**No Registration**: Direct downloads available

---

## IoT & Sensor Data

### 8. UCI Machine Learning Repository

**Description**: Hundreds of time-series datasets for ML research

**Format**: CSV, ARFF

**Download**: https://archive.ics.uci.edu/ml/index.php

**Time-Series Datasets**:
- Air Quality
- Traffic Flow
- Sensor Readings
- Energy Consumption

**No API Key**: Direct file downloads

**Usage**: Download CSV → Upload to VARIOSYNC

---

### 9. Kaggle Datasets

**Description**: Thousands of time-series datasets (finance, weather, energy, sales, IoT, etc.)

**Format**: CSV, JSON, Parquet

**Download**: https://www.kaggle.com/datasets

**Free Account**: Required (free to sign up)

**Free Tier**: Free download + some APIs

**Real-Time**: Rarely

**Historical Depth**: Varies

**Notes**: Community datasets; great for practice

**Popular Time-Series Datasets**:
- Stock market data
- Weather data
- Sensor data
- Sales data
- Energy consumption
- IoT sensor readings

**Usage**: Download dataset → Upload CSV/JSON to VARIOSYNC

---

### 10. Time Series Data Library (TSDL)

**Description**: Curated collection of time-series datasets

**Format**: CSV

**Download**: https://robjhyndman.com/TSDL/

**No API Key**: Direct downloads

---

## Health & Demographics

### 11. WHO Global Health Observatory

**Description**: Global health statistics and indicators

**Format**: CSV, Excel

**Download**: https://www.who.int/data/gho

**No API Key**: Direct downloads available

**Data Types**:
- Disease prevalence
- Mortality rates
- Health indicators
- Demographics

---

### 12. Our World in Data

**Description**: Global health, environment, economy, energy time series

**Format**: CSV

**Download**: https://ourworldindata.org

**Direct CSV**: Available for all charts/datasets

**No Registration**: Free downloads

**Free Tier**: Free download + charts API

**Real-Time**: No

**Historical Depth**: Centuries in some cases

**Notes**: Beautifully curated; excellent for global trends

**Popular Datasets**:
- COVID-19 data
- Population growth
- Energy consumption
- Education metrics
- Climate change indicators
- Economic development

---

## Energy & Environment

### 13. EIA (US Energy Information Administration)

**Description**: US energy statistics and data

**Format**: CSV, Excel

**Download**: https://www.eia.gov

**No API Key**: Direct downloads available

**Data Types**:
- Electricity generation
- Petroleum consumption
- Natural gas prices
- Renewable energy

---

### 14. NASA Earth Observations

**Description**: Satellite and Earth observation data

**Format**: CSV, NetCDF (convertible to CSV)

**Download**: https://earthobservatory.nasa.gov

**Some datasets**: Available as CSV downloads

---

## Transportation & Traffic

### 15. NYC Open Data

**Description**: New York City open data portal (includes traffic, transit, etc.)

**Format**: CSV, JSON

**Download**: https://opendata.cityofnewyork.us

**No API Key**: Direct downloads

**Time-Series Data**:
- Traffic volumes
- Subway ridership
- Taxi trips
- Bike share usage

---

### 16. London Datastore

**Description**: London open data (transport, environment, etc.)

**Format**: CSV

**Download**: https://data.london.gov.uk

**No API Key**: Direct downloads

---

## Machine Learning Datasets

### 17. UCR Time Series Archive

**Description**: 128+ univariate time-series datasets for classification/forecasting

**Format**: CSV, TSV

**Download**: https://www.cs.ucr.edu/~eamonn/time_series_data_2018/

**No API Key**: Direct downloads

**Usage**: Perfect for ML forecasting experiments

---

### 18. Monash Time Series Forecasting Repository

**Description**: Large collection of time-series datasets for forecasting

**Format**: CSV

**Download**: https://forecastingdata.org/

**No API Key**: Direct downloads

---

### 19. GitHub: open-time-series-datasets

**Description**: Curated collection of public time-series datasets

**Format**: CSV

**Download**: https://github.com/liaoyuhua/open-time-series-datasets

**No API Key**: Direct GitHub downloads

**Categories**:
- Air pollution
- Traffic
- Disease indicators
- Financial data

---

### 20. Time Series Data Library (TSDL) by Rob Hyndman

**Description**: Comprehensive collection of time-series datasets

**Format**: CSV

**Download**: https://robjhyndman.com/TSDL/

**No API Key**: Direct downloads

---

## How to Use These Datasets

### Method 1: Direct Upload

1. Download the CSV/JSON file from the source
2. Use VARIOSYNC Upload button
3. Select file and record type
4. Process

### Method 2: Programmatic Download

```python
import requests
import pandas as pd

# Download CSV from URL
url = "https://example.com/data.csv"
response = requests.get(url)
with open("data.csv", "wb") as f:
    f.write(response.content)

# Process with VARIOSYNC
from main import VariosyncApp
app = VariosyncApp()
app.process_data_file("data.csv", record_type="time_series")
```

### Method 3: Using VARIOSYNC Download Feature

For sources that provide direct download URLs:
1. Use Download button
2. Configure as "Custom API" with direct CSV URL
3. Download and process

---

## Recommended Datasets for Testing

### Quick Start Datasets:

1. **World Bank GDP Data**
   - URL: https://datatopics.worldbank.org/world-development-indicators
   - Format: CSV
   - Size: Small to medium
   - Use Case: Economic analysis

2. **NOAA Daily Weather**
   - URL: https://www.ncei.noaa.gov/data/daily-summaries/
   - Format: CSV
   - Size: Medium
   - Use Case: Weather analysis, forecasting

3. **UCI Air Quality Dataset**
   - URL: https://archive.ics.uci.edu/ml/datasets/Air+Quality
   - Format: CSV
   - Size: Small
   - Use Case: Sensor data, anomaly detection

4. **Kaggle Store Sales**
   - URL: https://www.kaggle.com/datasets (search "store sales")
   - Format: CSV
   - Size: Medium to large
   - Use Case: Sales forecasting, trend analysis

---

## Data Format Requirements

VARIOSYNC accepts data in these formats:

### CSV Format:
```csv
series_id,timestamp,value,temperature,humidity
SENSOR-001,2024-01-15T09:00:00,25.5,22.3,60
SENSOR-001,2024-01-15T10:00:00,26.1,22.5,61
```

### JSON Format:
```json
[
  {
    "series_id": "SENSOR-001",
    "timestamp": "2024-01-15T09:00:00",
    "measurements": {
      "temperature": 22.3,
      "humidity": 60
    }
  }
]
```

### Financial CSV Format:
```csv
date,open,high,low,close,volume
2024-01-15,185.50,186.20,185.10,185.85,12345678
```

---

## Tips for Using Free Data

1. **Check License**: Ensure data license allows your use case
2. **Data Quality**: Verify data completeness and accuracy
3. **Update Frequency**: Check how often data is updated
4. **File Size**: Large datasets may need chunking
5. **Format Conversion**: Some sources provide multiple formats - CSV is easiest

---

## Additional Open Data Sources

### Google Dataset Search

**Description**: Search engine pointing to millions of public time-series datasets

**Website**: https://datasetsearch.research.google.com

**Notes**: Aggregator — not an API itself. Use to discover datasets, then download from original sources.

**Usage**: Search for time-series data → Follow links to original sources → Download and upload to VARIOSYNC

---

### data.gov

**Description**: US government open data (economic, weather, energy, health, etc.)

**Website**: https://data.gov

**Format**: Various (CSV, JSON, API)

**Free Tier**: Free API access

**Notes**: Massive US public data catalog

**Popular Categories**:
- Economic indicators
- Weather and climate
- Energy consumption
- Health statistics
- Transportation

**Usage**: Browse datasets → Download CSV/JSON or use API → Upload to VARIOSYNC

---

### Quandl (now Nasdaq Data Link)

**Description**: Financial, economic, alternative data

**Website**: https://data.nasdaq.com

**Format**: CSV, JSON (via API)

**Free Tier**: Limited free tier

**Notes**: Was very popular; now more restricted free access

**Usage**: Sign up for free account → Download datasets → Upload to VARIOSYNC

---

## Quick Links

- **World Bank**: https://datatopics.worldbank.org/world-development-indicators
- **FRED**: https://fred.stlouisfed.org
- **NOAA**: https://www.ncei.noaa.gov/data
- **Kaggle**: https://www.kaggle.com/datasets
- **UCI ML Repo**: https://archive.ics.uci.edu/ml/index.php
- **Our World in Data**: https://ourworldindata.org
- **Open-Meteo**: https://open-meteo.com
- **Google Dataset Search**: https://datasetsearch.research.google.com
- **data.gov**: https://data.gov
- **Nasdaq Data Link**: https://data.nasdaq.com

---

## Need Help?

If you need help finding specific time-series data:
1. Check `API_SOURCES.md` for API-based sources (some have free tiers)
2. Use VARIOSYNC Search to find data in your storage
3. Check dataset documentation for format specifications
