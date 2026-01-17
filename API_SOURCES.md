# Time-Series Data API Sources

Comprehensive guide to APIs available for time-series data that work with VARIOSYNC's generic API downloader.

## Table of Contents

- [Financial APIs](#financial-apis)
- [Weather & Climate APIs](#weather--climate-apis)
- [IoT & Metrics APIs](#iot--metrics-apis)
- [Economic Data APIs](#economic-data-apis)
- [Cryptocurrency APIs](#cryptocurrency-apis)
- [General Purpose APIs](#general-purpose-apis)
- [Quick Reference: API Comparison](#quick-reference-api-comparison)
- [Configuration Examples](#configuration-examples)

---

## Financial APIs

### 1. Alpha Vantage

**Description**: Stock market data, forex, cryptocurrencies, technical indicators, news, fundamentals

**Free Tier**: Generous free tier - 5 calls/minute, 500 calls/day

**Real-Time**: Delayed (premium real-time available)

**Historical Depth**: 20+ years

**Website**: https://www.alphavantage.co

**Notes**: Still one of the best free options; supports JSON/CSV formats

**Configuration**:
```json
{
  "name": "Alpha Vantage",
  "base_url": "https://www.alphavantage.co/query",
  "endpoint": "",
  "api_key": "YOUR_API_KEY",
  "api_key_param": "apikey",
  "entity_param": "symbol",
  "start_date_param": null,
  "end_date_param": null,
  "date_format": "YYYY-MM-DD",
  "response_format": "json",
  "data_path": "Time Series (Daily)",
  "column_mapping": {
    "1. open": "open",
    "2. high": "high",
    "3. low": "low",
    "4. close": "close",
    "5. volume": "volume"
  }
}
```

**Endpoints**:
- Daily: `function=TIME_SERIES_DAILY&symbol={symbol}`
- Intraday: `function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min`
- Weekly: `function=TIME_SERIES_WEEKLY&symbol={symbol}`

---

### 2. Twelve Data

**Description**: Stocks, forex, crypto, ETFs, fundamentals

**Free Tier**: Yes - very limited free tier

**Real-Time**: Yes (WebSocket)

**Historical Depth**: 20+ years

**Website**: https://twelvedata.com

**Notes**: Clean API; credit-based system

**Configuration**:
```json
{
  "name": "Twelve Data",
  "base_url": "https://api.twelvedata.com",
  "endpoint": "/time_series",
  "api_key": "YOUR_API_KEY",
  "api_key_param": "apikey",
  "entity_param": "symbol",
  "start_date_param": "start_date",
  "end_date_param": "end_date",
  "date_format": "YYYY-MM-DD",
  "response_format": "json",
  "data_path": "values",
  "column_mapping": {
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "volume": "volume"
  }
}
```

---

### 3. Finnhub

**Description**: Global stocks, forex, crypto, fundamentals, news/sentiment

**Free Tier**: Yes - limited calls free

**Real-Time**: Yes (WebSocket + REST)

**Historical Depth**: 20+ years

**Website**: https://finnhub.io

**Notes**: Very broad coverage; good WebSocket support

**Configuration**:
```json
{
  "name": "Finnhub",
  "base_url": "https://finnhub.io/api/v1",
  "endpoint": "/stock/candle",
  "api_key": "YOUR_API_KEY",
  "api_key_param": "token",
  "entity_param": "symbol",
  "start_date_param": "from",
  "end_date_param": "to",
  "date_format": "unix",
  "response_format": "json",
  "data_path": "c",
  "column_mapping": {
    "c": "close",
    "h": "high",
    "l": "low",
    "o": "open",
    "v": "volume"
  }
}
```

---

### 4. Financial Modeling Prep (FMP)

**Description**: Global equities, forex, crypto, fundamentals, estimates

**Free Tier**: Yes - usable free tier

**Real-Time**: Yes

**Historical Depth**: 30+ years

**Website**: https://financialmodelingprep.com

**Configuration**:
```json
{
  "name": "Financial Modeling Prep",
  "base_url": "https://financialmodelingprep.com/api/v3",
  "endpoint": "/historical-price-full/{symbol}",
  "api_key": "YOUR_API_KEY",
  "api_key_param": "apikey",
  "entity_param": "symbol",
  "start_date_param": "from",
  "end_date_param": "to",
  "date_format": "YYYY-MM-DD",
  "response_format": "json",
  "data_path": "historical",
  "column_mapping": {
    "date": "timestamp",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "volume": "volume"
  }
}
```

**Notes**: Fundamentals + pricing combo; transparent pricing

---

### 5. Marketstack

**Description**: Global stocks, intraday, end-of-day data

**Free Tier**: Yes - free tier (limited requests)

**Real-Time**: Delayed

**Historical Depth**: Varies

**Website**: https://marketstack.com

**Configuration**:
```json
{
  "name": "Marketstack",
  "base_url": "http://api.marketstack.com/v1",
  "endpoint": "/eod",
  "api_key": "YOUR_API_KEY",
  "api_key_param": "access_key",
  "entity_param": "symbols",
  "start_date_param": "date_from",
  "end_date_param": "date_to",
  "date_format": "YYYY-MM-DD",
  "response_format": "json",
  "data_path": "data",
  "column_mapping": {
    "date": "timestamp",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "volume": "volume"
  }
}
```

**Notes**: Simple, JSON format

---

### 6. StockData.org

**Description**: Stocks, forex, crypto, news

**Free Tier**: Yes - free tier

**Real-Time**: Yes

**Historical Depth**: Varies

**Website**: https://stockdata.org

**Configuration**:
```json
{
  "name": "StockData.org",
  "base_url": "https://api.stockdata.org/v1",
  "endpoint": "/data/quote",
  "api_key": "YOUR_API_KEY",
  "api_key_param": "api_token",
  "entity_param": "symbols",
  "start_date_param": null,
  "end_date_param": null,
  "date_format": "YYYY-MM-DD",
  "response_format": "json"
}
```

**Notes**: JSON format; easy to use

---

### 7. EODHD (End of Day Historical Data)

**Description**: Global stocks, ETFs, forex, crypto, fundamentals

**Free Tier**: Limited free trial/tier

**Real-Time**: Delayed + add-on real-time available

**Historical Depth**: 30+ years

**Website**: https://eodhd.com

**Configuration**:
```json
{
  "name": "EODHD",
  "base_url": "https://eodhistoricaldata.com/api",
  "endpoint": "/eod/{symbol}",
  "api_key": "YOUR_API_KEY",
  "api_key_param": "api_token",
  "entity_param": "symbol",
  "start_date_param": "from",
  "end_date_param": "to",
  "date_format": "YYYY-MM-DD",
  "response_format": "json",
  "data_path": null,
  "column_mapping": {
    "date": "timestamp",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "adjusted_close": "adjusted_close",
    "volume": "volume"
  }
}
```

**Notes**: Deep historical data; Excel add-on available

---

### 8. Polygon.io

**Description**: US equities, options, forex, crypto

**Free Tier**: Yes - limited free tier

**Real-Time**: Yes (tick-level)

**Historical Depth**: Full US history

**Website**: https://polygon.io

**Configuration**:
```json
{
  "name": "Polygon.io",
  "base_url": "https://api.polygon.io/v2",
  "endpoint": "/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{from}/{to}",
  "api_key": "YOUR_API_KEY",
  "api_key_param": "apiKey",
  "entity_param": "symbol",
  "start_date_param": "from",
  "end_date_param": "to",
  "date_format": "YYYY-MM-DD",
  "response_format": "json",
  "data_path": "results",
  "column_mapping": {
    "t": "timestamp",
    "o": "open",
    "h": "high",
    "l": "low",
    "c": "close",
    "v": "volume"
  }
}
```

**Notes**: Best tick data; US-focused; paid tier recommended for serious use

---

### 9. Yahoo Finance (via yfinance)

**Description**: Free stock data (unofficial, use with caution)

**Free Tier**: Unlimited (but rate-limited)

**Note**: Consider using Python `yfinance` library instead of direct API

---

### 10. IEX Cloud

**Description**: US stock market data, real-time and historical

**Free Tier**: 50,000 messages/month

**Website**: https://iexcloud.io

**Configuration**:
```json
{
  "name": "IEX Cloud",
  "base_url": "https://cloud.iexapis.com/stable",
  "endpoint": "/stock/{symbol}/chart/{range}",
  "api_key": "YOUR_API_KEY",
  "api_key_param": "token",
  "entity_param": "symbol",
  "start_date_param": null,
  "end_date_param": null,
  "date_format": "YYYY-MM-DD",
  "response_format": "json"
}
```

---

## Weather & Climate APIs

### 6. OpenWeatherMap

**Description**: Current weather, forecasts, historical data

**Free Tier**: 60 calls/minute, 1,000 calls/day

**Website**: https://openweathermap.org

**Configuration**:
```json
{
  "name": "OpenWeatherMap",
  "base_url": "https://api.openweathermap.org/data/2.5",
  "endpoint": "/history/city",
  "api_key": "YOUR_API_KEY",
  "api_key_param": "appid",
  "entity_param": "q",
  "start_date_param": "start",
  "end_date_param": "end",
  "date_format": "unix",
  "response_format": "json",
  "data_path": "list",
  "column_mapping": {
    "dt": "timestamp",
    "main.temp": "temperature",
    "main.humidity": "humidity",
    "main.pressure": "pressure",
    "wind.speed": "wind_speed"
  }
}
```

---

### 7. Open-Meteo

**Description**: Global weather forecasts + historical reanalysis

**Free Tier**: Completely free + no API key

**Real-Time**: Yes (forecasts)

**Historical Depth**: 70+ years (reanalysis)

**Website**: https://open-meteo.com

**Notes**: High-resolution; no rate limits; excellent

**Configuration**:
```json
{
  "name": "Open-Meteo",
  "base_url": "https://archive-api.open-meteo.com/v1",
  "endpoint": "/archive",
  "api_key": null,
  "api_key_param": null,
  "entity_param": "latitude,longitude",
  "start_date_param": "start_date",
  "end_date_param": "end_date",
  "date_format": "YYYY-MM-DD",
  "response_format": "json",
  "data_path": "hourly",
  "column_mapping": {
    "time": "timestamp",
    "temperature_2m": "temperature",
    "relativehumidity_2m": "humidity",
    "precipitation": "precipitation"
  }
}
```

---

### 8. Visual Crossing

**Description**: Global historical + forecast weather

**Free Tier**: Free tier (limited queries/day)

**Real-Time**: Yes (forecast)

**Historical Depth**: Decades

**Website**: https://www.visualcrossing.com

**Notes**: Easy API; good for location-based time series

**Configuration**:
```json
{
  "name": "Visual Crossing",
  "base_url": "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services",
  "endpoint": "/timeline/{location}/{start}/{end}",
  "api_key": "YOUR_API_KEY",
  "api_key_param": "key",
  "entity_param": "location",
  "start_date_param": "start",
  "end_date_param": "end",
  "date_format": "YYYY-MM-DD",
  "response_format": "json"
}
```

---

### 9. Tomorrow.io

**Description**: Weather + air quality, soil moisture, pollen data

**Free Tier**: Limited requests

**Website**: https://www.tomorrow.io

**Configuration**:
```json
{
  "name": "Tomorrow.io",
  "base_url": "https://api.tomorrow.io/v4",
  "endpoint": "/timelines",
  "api_key": "YOUR_API_KEY",
  "api_key_param": "apikey",
  "entity_param": "location",
  "start_date_param": "startTime",
  "end_date_param": "endTime",
  "date_format": "iso8601",
  "response_format": "json"
}
```

---

### 9. NOAA Climate Data Online (CDO)

**Description**: US weather stations, daily/monthly summaries

**Free Tier**: Free API + bulk download

**Real-Time**: No (delayed)

**Historical Depth**: 100+ years

**Website**: https://www.ncdc.noaa.gov/cdo-web

**Configuration**:
```json
{
  "name": "NOAA CDO",
  "base_url": "https://www.ncdc.noaa.gov/cdo-web/api/v2",
  "endpoint": "/data",
  "api_key": "YOUR_API_KEY",
  "api_key_param": "token",
  "entity_param": "stationid",
  "start_date_param": "startdate",
  "end_date_param": "enddate",
  "date_format": "YYYY-MM-DD",
  "response_format": "json",
  "data_path": "results",
  "column_mapping": {
    "date": "timestamp",
    "PRCP": "precipitation",
    "TMAX": "max_temperature",
    "TMIN": "min_temperature",
    "TAVG": "avg_temperature"
  }
}
```

**Notes**: Very long historical US data

---

### 10. Meteostat

**Description**: Global historical weather station data

**Free Tier**: Free API

**Real-Time**: No

**Historical Depth**: Decades

**Website**: https://meteostat.net

**Configuration**:
```json
{
  "name": "Meteostat",
  "base_url": "https://api.meteostat.net/v2",
  "endpoint": "/point/hourly",
  "api_key": null,
  "api_key_param": null,
  "entity_param": "lat,lon",
  "start_date_param": "start",
  "end_date_param": "end",
  "date_format": "YYYY-MM-DD",
  "response_format": "json",
  "data_path": "data",
  "column_mapping": {
    "time": "timestamp",
    "temp": "temperature",
    "rhum": "humidity",
    "prcp": "precipitation",
    "wspd": "wind_speed"
  }
}
```

**Notes**: Clean JSON; many stations

---

## IoT & Metrics APIs

### 11. ThingSpeak

**Description**: IoT platform for storing and retrieving sensor data

**Free Tier**: 3 million messages/year

**Website**: https://thingspeak.com

**Configuration**:
```json
{
  "name": "ThingSpeak",
  "base_url": "https://api.thingspeak.com",
  "endpoint": "/channels/{channel_id}/feeds.json",
  "api_key": "YOUR_READ_API_KEY",
  "api_key_param": "api_key",
  "entity_param": "channel_id",
  "start_date_param": "start",
  "end_date_param": "end",
  "date_format": "YYYY-MM-DD HH:NN:SS",
  "response_format": "json",
  "data_path": "feeds"
}
```

---

### 12. InfluxDB Cloud

**Description**: Time-series database with REST API

**Free Tier**: Free tier available

**Website**: https://www.influxdata.com

**Configuration**:
```json
{
  "name": "InfluxDB",
  "base_url": "https://your-instance.influxdata.com/api/v2",
  "endpoint": "/query",
  "api_key": "YOUR_API_TOKEN",
  "api_key_param": "Authorization",
  "entity_param": null,
  "start_date_param": "start",
  "end_date_param": "stop",
  "date_format": "rfc3339",
  "response_format": "json"
}
```

---

### 13. Prometheus

**Description**: Monitoring and alerting toolkit (self-hosted)

**Free Tier**: Open source

**Website**: https://prometheus.io

**Configuration**:
```json
{
  "name": "Prometheus",
  "base_url": "http://your-prometheus:9090/api/v1",
  "endpoint": "/query_range",
  "api_key": null,
  "api_key_param": null,
  "entity_param": "query",
  "start_date_param": "start",
  "end_date_param": "end",
  "date_format": "unix",
  "response_format": "json"
}
```

---

## Economic Data APIs

### 13. FRED (St. Louis Fed)

**Description**: US economic indicators (GDP, unemployment, CPI, interest rates, etc.)

**Free Tier**: Completely free + API

**Real-Time**: No (daily/weekly/monthly updates)

**Historical Depth**: Decades

**Website**: https://fred.stlouisfed.org

**Notes**: Gold standard for US macro data; very reliable

**Configuration**:
```json
{
  "name": "FRED",
  "base_url": "https://api.stlouisfed.org/fred",
  "endpoint": "/series/observations",
  "api_key": "YOUR_API_KEY",
  "api_key_param": "api_key",
  "entity_param": "series_id",
  "start_date_param": "observation_start",
  "end_date_param": "observation_end",
  "date_format": "YYYY-MM-DD",
  "response_format": "json",
  "data_path": "observations",
  "column_mapping": {
    "date": "timestamp",
    "value": "value"
  }
}
```

**Popular Series**:
- GDP: `GDP`
- Unemployment Rate: `UNRATE`
- Consumer Price Index: `CPIAUCSL`
- Federal Funds Rate: `FEDFUNDS`
- 10-Year Treasury Rate: `DGS10`

---

### 14. World Bank Open Data

**Description**: Global economic, development, poverty, health indicators

**Free Tier**: Completely free + API

**Real-Time**: No

**Historical Depth**: Decades

**Website**: https://data.worldbank.org

**Notes**: Excellent for cross-country comparisons

**Configuration**:
```json
{
  "name": "World Bank",
  "base_url": "https://api.worldbank.org/v2",
  "endpoint": "/country/{country}/indicator/{indicator}",
  "api_key": null,
  "api_key_param": null,
  "entity_param": "country,indicator",
  "start_date_param": "date",
  "end_date_param": null,
  "date_format": "YYYY",
  "response_format": "json",
  "data_path": "[1]",
  "column_mapping": {
    "date": "timestamp",
    "value": "value"
  }
}
```

**Popular Indicators**:
- GDP per capita: `NY.GDP.PCAP.CD`
- Population: `SP.POP.TOTL`
- Life expectancy: `SP.DYN.LE00.IN`
- Trade (% of GDP): `NE.TRD.GNFS.ZS`

**Example**: `/country/all/indicator/NY.GDP.PCAP.CD?format=json&date=2000:2023`

---

### 15. OECD Data

**Description**: Economic, education, health, environment data (OECD countries + partners)

**Free Tier**: Free API access

**Real-Time**: No

**Historical Depth**: Decades

**Website**: https://data.oecd.org

**Configuration**:
```json
{
  "name": "OECD Data",
  "base_url": "https://stats.oecd.org/SDMX-JSON/data",
  "endpoint": "/{dataset}/{filter}",
  "api_key": null,
  "api_key_param": null,
  "entity_param": "filter",
  "start_date_param": "startTime",
  "end_date_param": "endTime",
  "date_format": "YYYY-MM-DD",
  "response_format": "json",
  "note": "Use OECD SDMX format for queries"
}
```

**Notes**: High-quality international statistics

---

### 16. IMF Data

**Description**: Global macro, fiscal, balance of payments data

**Free Tier**: Free API

**Real-Time**: No

**Historical Depth**: Decades

**Website**: https://data.imf.org

**Configuration**:
```json
{
  "name": "IMF Data",
  "base_url": "https://www.imf.org/external/datamapper/api/v1",
  "endpoint": "/{indicator}/{country}",
  "api_key": null,
  "api_key_param": null,
  "entity_param": "country",
  "start_date_param": "period",
  "end_date_param": null,
  "date_format": "YYYY",
  "response_format": "json"
}
```

**Notes**: Very deep macroeconomic series

---

## Cryptocurrency APIs

### 17. CoinGecko

**Description**: Cryptocurrency market data

**Free Tier**: 10-50 calls/minute

**Website**: https://www.coingecko.com

**Configuration**:
```json
{
  "name": "CoinGecko",
  "base_url": "https://api.coingecko.com/api/v3",
  "endpoint": "/coins/{id}/market_chart",
  "api_key": null,
  "api_key_param": null,
  "entity_param": "id",
  "start_date_param": "from",
  "end_date_param": "to",
  "date_format": "unix",
  "response_format": "json",
  "data_path": "prices",
  "column_mapping": {
    "0": "timestamp",
    "1": "price"
  }
}
```

---

### 18. CryptoCompare

**Description**: Cryptocurrency data and news

**Free Tier**: 100,000 calls/month

**Website**: https://www.cryptocompare.com

**Configuration**:
```json
{
  "name": "CryptoCompare",
  "base_url": "https://min-api.cryptocompare.com/data",
  "endpoint": "/v2/histoday",
  "api_key": "YOUR_API_KEY",
  "api_key_param": "api_key",
  "entity_param": "fsym",
  "start_date_param": "toTs",
  "end_date_param": null,
  "date_format": "unix",
  "response_format": "json",
  "data_path": "Data.Data",
  "column_mapping": {
    "time": "timestamp",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "volumefrom": "volume"
  }
}
```

---

## Open Data & Dataset Platforms

### 19. Kaggle Datasets

**Description**: Thousands of time series datasets (finance, weather, energy, sales, IoT, etc.)

**Free Tier**: Free download + some APIs

**Real-Time**: Rarely

**Historical Depth**: Varies

**Website**: https://www.kaggle.com/datasets

**Notes**: Community datasets; great for practice

**Usage**: 
- Browse datasets at kaggle.com/datasets
- Download CSV/JSON files directly
- Some datasets have Kaggle API access
- Upload downloaded files to VARIOSYNC using the Upload button

**Note**: Not a direct API, but provides downloadable time-series datasets

---

### 20. Google Dataset Search

**Description**: Search engine pointing to millions of public time series datasets

**Free Tier**: Free search engine

**Real-Time**: Varies

**Historical Depth**: Varies

**Website**: https://datasetsearch.research.google.com

**Notes**: Aggregator — not an API itself

**Usage**:
- Search for time-series datasets
- Follow links to original data sources
- Download data from source providers
- Upload to VARIOSYNC using the Upload button

**Note**: This is a search aggregator, not a direct API. Use it to discover datasets, then download from the original sources.

---

### 21. data.gov

**Description**: US government open data (economic, weather, energy, health, etc.)

**Free Tier**: Free API

**Real-Time**: Varies

**Historical Depth**: Varies

**Website**: https://data.gov

**Configuration**:
```json
{
  "name": "data.gov",
  "base_url": "https://catalog.data.gov/api/3",
  "endpoint": "/action/datastore_search",
  "api_key": null,
  "api_key_param": null,
  "entity_param": "resource_id",
  "start_date_param": "filters",
  "end_date_param": null,
  "date_format": "YYYY-MM-DD",
  "response_format": "json",
  "note": "Massive US public data catalog; each dataset has its own resource_id"
}
```

**Notes**: Massive US public data catalog

**Popular Datasets**:
- Economic indicators
- Weather and climate data
- Energy consumption
- Health statistics
- Transportation data

---

### 22. Quandl (now Nasdaq Data Link)

**Description**: Financial, economic, alternative data

**Free Tier**: Limited free tier

**Real-Time**: Some

**Historical Depth**: Varies

**Website**: https://data.nasdaq.com

**Configuration**:
```json
{
  "name": "Nasdaq Data Link",
  "base_url": "https://data.nasdaq.com/api/v3",
  "endpoint": "/datasets/{database}/{dataset}",
  "api_key": "YOUR_API_KEY",
  "api_key_param": "api_key",
  "entity_param": "database,dataset",
  "start_date_param": "start_date",
  "end_date_param": "end_date",
  "date_format": "YYYY-MM-DD",
  "response_format": "json"
}
```

**Notes**: Was very popular; now more restricted free access

---

### 23. Our World in Data

**Description**: Global health, environment, economy, energy time series

**Free Tier**: Free download + charts API

**Real-Time**: No

**Historical Depth**: Centuries in some cases

**Website**: https://ourworldindata.org

**Configuration**:
```json
{
  "name": "Our World in Data",
  "base_url": "https://api.ourworldindata.org/v1",
  "endpoint": "/indicators/{indicator}",
  "api_key": null,
  "api_key_param": null,
  "entity_param": "indicator",
  "start_date_param": "startYear",
  "end_date_param": "endYear",
  "date_format": "YYYY",
  "response_format": "json"
}
```

**Notes**: Beautifully curated; excellent for global trends

**Usage**: 
- Download CSV files directly from any chart/dataset page
- Use the Upload button in VARIOSYNC to process downloaded files
- Some datasets available via API

---

## General Purpose APIs

### 24. REST Countries

**Description**: Country information and statistics

**Free Tier**: Free, no API key

**Website**: https://restcountries.com

**Note**: Not strictly time-series, but can be used for country-level metrics over time

---

### 18. NASA APIs

**Description**: Various NASA data APIs (asteroids, Earth observation, etc.)

**Free Tier**: Free, API key required

**Website**: https://api.nasa.gov

**Example - Near Earth Objects**:
```json
{
  "name": "NASA NEO",
  "base_url": "https://api.nasa.gov/neo/rest/v1",
  "endpoint": "/feed",
  "api_key": "YOUR_API_KEY",
  "api_key_param": "api_key",
  "entity_param": null,
  "start_date_param": "start_date",
  "end_date_param": "end_date",
  "date_format": "YYYY-MM-DD",
  "response_format": "json"
}
```

---

## Configuration Examples

### Adding an API to VARIOSYNC

1. **Get API Key**: Sign up for the API service and obtain your API key

2. **Add to API Keys Manager**: Use the navbar "API Keys" button to add your key

3. **Configure in Download Dialog**: Use the "Download" button to configure:
   - API Name
   - Base URL
   - Endpoint
   - Entity/Symbol parameter name
   - Date parameter names
   - Column mapping

4. **Save Configuration** (Optional): Add to `config.json` for persistence:

```json
{
  "API": {
    "name": "Alpha Vantage",
    "base_url": "https://www.alphavantage.co/query",
    "endpoint": "",
    "api_key": "YOUR_KEY",
    "api_key_param": "apikey",
    "entity_param": "symbol",
    "column_mapping": {
      "1. open": "open",
      "2. high": "high",
      "3. low": "low",
      "4. close": "close",
      "5. volume": "volume"
    }
  }
}
```

### Common Column Mappings

**Financial Data (OHLCV)**:
```json
{
  "open": "open",
  "high": "high",
  "low": "low",
  "close": "close",
  "volume": "volume",
  "timestamp": "timestamp"
}
```

**Weather Data**:
```json
{
  "dt": "timestamp",
  "main.temp": "temperature",
  "main.humidity": "humidity",
  "main.pressure": "pressure",
  "wind.speed": "wind_speed"
}
```

**Generic Metrics**:
```json
{
  "time": "timestamp",
  "value": "value",
  "metric": "metric_name"
}
```

---

## Rate Limits & Best Practices

### Rate Limiting

Most APIs have rate limits. VARIOSYNC's `APIDownloader` includes built-in rate limiting:

- Default: 60 requests/minute
- Configurable via `rate_limit_per_minute` in config
- Automatic retry with exponential backoff

### Caching

Use Redis caching (if configured) to cache API responses:
- Reduces API calls
- Faster response times
- Respects rate limits

### Error Handling

VARIOSYNC handles:
- Network errors (retries)
- Rate limit errors (waits)
- Invalid responses (logs and continues)

---

## Quick Reference: API Comparison

### Financial APIs with Free Tiers

| API | Free Tier Details | Data Types | Real-Time? | Historical Depth | Notes / Limitations | Website |
|-----|-------------------|------------|------------|------------------|---------------------|---------|
| **Alpha Vantage** | Yes — generous (5 calls/min, 500/day free) | Stocks, forex, crypto, indicators, news, fundamentals | Delayed (premium real-time) | 20+ years | Still one of the best free options; JSON/CSV | alphavantage.co |
| **Finnhub** | Yes — limited calls free | Global stocks, forex, crypto, fundamentals, news/sentiment | Yes (WebSocket + REST) | 20+ years | Very broad coverage; good websocket | finnhub.io |
| **Twelve Data** | Yes — very limited free tier | Stocks, forex, crypto, ETFs, fundamentals | Yes (WebSocket) | 20+ years | Clean API; credit-based system | twelvedata.com |
| **Financial Modeling Prep** | Yes — usable free tier | Global equities, forex, crypto, fundamentals, estimates | Yes | 30+ years | Fundamentals + pricing combo; transparent | financialmodelingprep.com |
| **Marketstack** | Yes — free tier (limited requests) | Global stocks, intraday, EOD | Delayed | Varies | Simple, JSON format | marketstack.com |
| **StockData.org** | Yes — free tier | Stocks, forex, crypto, news | Yes | Varies | JSON; easy to use | stockdata.org |
| **EODHD** | Limited free trial / tier | Global stocks, ETFs, forex, crypto, fundamentals | Delayed + add-on real-time | 30+ years | Deep historical; Excel add-on | eodhd.com |
| **Polygon.io** | Yes — limited free tier | US equities, options, forex, crypto | Yes (tick-level) | Full US history | Best tick data; US-focused; paid for serious use | polygon.io |

### Other API Types

### Economic Data APIs with Free Tiers

| API | Free Tier Details | Data Types | Real-Time? | Historical Depth | Notes | Website |
|-----|-------------------|------------|------------|------------------|-------|---------|
| **FRED (St. Louis Fed)** | Completely free + API | US economic indicators (GDP, unemployment, CPI, interest rates, etc.) | No (daily/weekly/monthly updates) | Decades | Gold standard for US macro data; very reliable | fred.stlouisfed.org |
| **World Bank Open Data** | Completely free + API | Global economic, development, poverty, health | No | Decades | Excellent for cross-country comparisons | data.worldbank.org |
| **OECD Data** | Free API access | Economic, education, health, environment (OECD countries + partners) | No | Decades | High-quality international stats | data.oecd.org |
| **IMF Data** | Free API | Global macro, fiscal, balance of payments | No | Decades | Very deep macroeconomic series | data.imf.org |

### Weather & Climate APIs with Free Tiers

| API | Free Tier Details | Data Types | Real-Time? | Historical Depth | Notes / Limitations | Website |
|-----|-------------------|------------|------------|------------------|---------------------|---------|
| **Open-Meteo** | Completely free + no API key | Global weather forecasts + historical reanalysis | Yes (forecasts) | 70+ years (reanalysis) | High-resolution; no rate limits; excellent | open-meteo.com |
| **NOAA Climate Data Online (CDO)** | Free API + bulk download | US weather stations, daily/monthly summaries | No (delayed) | 100+ years | Very long historical US data | ncdc.noaa.gov/cdo-web |
| **Visual Crossing** | Free tier (limited queries/day) | Global historical + forecast weather | Yes (forecast) | Decades | Easy API; good for location-based time series | visualcrossing.com |
| **Meteostat** | Free API | Global historical weather station data | No | Decades | Clean JSON; many stations | meteostat.net |
| **OpenWeatherMap** | 1000/day | Current weather, forecasts, historical | Yes | Limited | 60 calls/min rate limit | openweathermap.org |

### Open Data & Dataset Platforms

| API | Free Tier Details | Data Types | Real-Time? | Historical Depth | Notes | Website |
|-----|-------------------|------------|------------|------------------|-------|---------|
| **Kaggle Datasets** | Free download + some APIs | Thousands of time series (finance, weather, energy, sales, IoT, etc.) | Rarely | Varies | Community datasets; great for practice | kaggle.com/datasets |
| **Google Dataset Search** | Free search engine | Links to millions of public time series datasets | Varies | Varies | Aggregator — not an API itself | datasetsearch.research.google.com |
| **data.gov** | Free API | US government open data (economic, weather, energy, health, etc.) | Varies | Varies | Massive US public data catalog | data.gov |
| **Quandl (Nasdaq Data Link)** | Limited free tier | Financial, economic, alternative data | Some | Varies | Was very popular; now more restricted free access | data.nasdaq.com |
| **Our World in Data** | Free download + charts API | Global health, environment, economy, energy time series | No | Centuries in some cases | Beautifully curated; excellent for global trends | ourworldindata.org |

### Other API Types

| API | Type | Free Tier | Rate Limit | Best For |
|-----|------|-----------|------------|----------|
| CoinGecko | Crypto | Unlimited | 10-50/min | Crypto prices |
| ThingSpeak | IoT | 3M/year | Varies | Sensor data |

---

## Getting Started

1. Choose an API from the list above
2. Sign up and get your API key
3. Use the VARIOSYNC Download button to configure
4. Test with a small date range first
5. Download and process your data

For help with specific APIs, check their official documentation or contact support.
