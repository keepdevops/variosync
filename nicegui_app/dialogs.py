"""
NiceGUI App Dialog Functions
All dialog functions for download, search, payment, settings, API keys, user info.
"""
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

from nicegui import ui
from logger import get_logger
from . import get_app_instance

logger = get_logger()


def get_api_presets():
    """Get API presets dictionary."""
    return {
        "Custom API": None,
        "Alpha Vantage": {
            "base_url": "https://www.alphavantage.co/query",
            "endpoint": "",
            "api_key_param": "apikey",
            "entity_param": "symbol",
            "note": "5 calls/min, 500/day free. Use function=TIME_SERIES_DAILY&symbol={symbol} in endpoint"
        },
        "Finnhub": {
            "base_url": "https://finnhub.io/api/v1",
            "endpoint": "/stock/candle",
            "api_key_param": "token",
            "entity_param": "symbol",
            "start_date_param": "from",
            "end_date_param": "to",
            "date_format": "unix",
            "note": "Real-time + WebSocket, 20+ years history"
        },
        "Twelve Data": {
            "base_url": "https://api.twelvedata.com",
            "endpoint": "/time_series",
            "api_key_param": "apikey",
            "entity_param": "symbol",
            "start_date_param": "start_date",
            "end_date_param": "end_date",
            "note": "Very limited free tier, credit-based"
        },
        "Financial Modeling Prep": {
            "base_url": "https://financialmodelingprep.com/api/v3",
            "endpoint": "/historical-price-full/{symbol}",
            "api_key_param": "apikey",
            "entity_param": "symbol",
            "start_date_param": "from",
            "end_date_param": "to",
            "note": "30+ years history, fundamentals + pricing"
        },
        "Marketstack": {
            "base_url": "http://api.marketstack.com/v1",
            "endpoint": "/eod",
            "api_key_param": "access_key",
            "entity_param": "symbols",
            "start_date_param": "date_from",
            "end_date_param": "date_to",
            "note": "Simple JSON format, global stocks"
        },
        "StockData.org": {
            "base_url": "https://api.stockdata.org/v1",
            "endpoint": "/data/quote",
            "api_key_param": "api_token",
            "entity_param": "symbols",
            "note": "Easy to use, stocks/forex/crypto"
        },
        "EODHD": {
            "base_url": "https://eodhistoricaldata.com/api",
            "endpoint": "/eod/{symbol}",
            "api_key_param": "api_token",
            "entity_param": "symbol",
            "start_date_param": "from",
            "end_date_param": "to",
            "note": "30+ years history, Excel add-on available"
        },
        "Polygon.io": {
            "base_url": "https://api.polygon.io/v2",
            "endpoint": "/aggs/ticker/{symbol}/range/1/day/{from}/{to}",
            "api_key_param": "apiKey",
            "entity_param": "symbol",
            "start_date_param": "from",
            "end_date_param": "to",
            "note": "Best tick data, US-focused, limited free tier"
        },
        "Open-Meteo": {
            "base_url": "https://archive-api.open-meteo.com/v1",
            "endpoint": "/archive",
            "api_key_param": None,
            "entity_param": "latitude,longitude",
            "start_date_param": "start_date",
            "end_date_param": "end_date",
            "note": "Completely free, no API key, 70+ years history, high-resolution"
        },
        "NOAA Climate Data Online": {
            "base_url": "https://www.ncdc.noaa.gov/cdo-web/api/v2",
            "endpoint": "/data",
            "api_key_param": "token",
            "entity_param": "stationid",
            "start_date_param": "startdate",
            "end_date_param": "enddate",
            "note": "Free API, 100+ years US weather data, very long historical"
        },
        "Visual Crossing": {
            "base_url": "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services",
            "endpoint": "/timeline/{location}/{start}/{end}",
            "api_key_param": "key",
            "entity_param": "location",
            "start_date_param": "start",
            "end_date_param": "end",
            "note": "Free tier available, easy API, good for location-based time series"
        },
        "Meteostat": {
            "base_url": "https://api.meteostat.net/v2",
            "endpoint": "/point/hourly",
            "api_key_param": None,
            "entity_param": "lat,lon",
            "start_date_param": "start",
            "end_date_param": "end",
            "note": "Free API, clean JSON, many stations globally"
        },
        "OpenWeatherMap": {
            "base_url": "https://api.openweathermap.org/data/2.5",
            "endpoint": "/history/city",
            "api_key_param": "appid",
            "entity_param": "q",
            "start_date_param": "start",
            "end_date_param": "end",
            "date_format": "unix",
            "note": "1000 calls/day free, 60 calls/min rate limit"
        },
        "FRED (St. Louis Fed)": {
            "base_url": "https://api.stlouisfed.org/fred",
            "endpoint": "/series/observations",
            "api_key_param": "api_key",
            "entity_param": "series_id",
            "start_date_param": "observation_start",
            "end_date_param": "observation_end",
            "note": "Gold standard for US macro data; completely free"
        },
        "World Bank Open Data": {
            "base_url": "https://api.worldbank.org/v2",
            "endpoint": "/country/{country}/indicator/{indicator}",
            "api_key_param": None,
            "entity_param": "country,indicator",
            "start_date_param": "date",
            "end_date_param": None,
            "date_format": "YYYY",
            "note": "Excellent for cross-country comparisons; completely free"
        },
        "OECD Data": {
            "base_url": "https://stats.oecd.org/SDMX-JSON/data",
            "endpoint": "/{dataset}/{filter}",
            "api_key_param": None,
            "entity_param": "filter",
            "start_date_param": "startTime",
            "end_date_param": "endTime",
            "note": "High-quality international statistics; free API access"
        },
        "IMF Data": {
            "base_url": "https://www.imf.org/external/datamapper/api/v1",
            "endpoint": "/{indicator}/{country}",
            "api_key_param": None,
            "entity_param": "country",
            "start_date_param": "period",
            "date_format": "YYYY",
            "note": "Very deep macroeconomic series; free API"
        },
        "CoinGecko": {
            "base_url": "https://api.coingecko.com/api/v3",
            "endpoint": "/coins/{id}/market_chart",
            "api_key_param": None,
            "entity_param": "id",
            "start_date_param": "from",
            "end_date_param": "to",
            "date_format": "unix"
        },
        "data.gov": {
            "base_url": "https://catalog.data.gov/api/3",
            "endpoint": "/action/datastore_search",
            "api_key_param": None,
            "entity_param": "resource_id",
            "start_date_param": "filters",
            "note": "Massive US public data catalog; each dataset has its own resource_id"
        },
        "Nasdaq Data Link (Quandl)": {
            "base_url": "https://data.nasdaq.com/api/v3",
            "endpoint": "/datasets/{database}/{dataset}",
            "api_key_param": "api_key",
            "entity_param": "database,dataset",
            "start_date_param": "start_date",
            "end_date_param": "end_date",
            "note": "Limited free tier; was very popular, now more restricted"
        },
        "Our World in Data": {
            "base_url": "https://api.ourworldindata.org/v1",
            "endpoint": "/indicators/{indicator}",
            "api_key_param": None,
            "entity_param": "indicator",
            "start_date_param": "startYear",
            "end_date_param": "endYear",
            "date_format": "YYYY",
            "note": "Beautifully curated; excellent for global trends; download CSV from website"
        }
    }


def get_api_categories():
    """Get API categories dictionary."""
    return {
        "Financial APIs": [
            {"name": "Alpha Vantage", "free_tier": "5 calls/min, 500/day", "data_types": "Stocks, forex, crypto, indicators", "realtime": "Delayed", "history": "20+ years", "website": "alphavantage.co", "note": "Still one of the best free options"},
            {"name": "Finnhub", "free_tier": "Limited calls", "data_types": "Global stocks, forex, crypto", "realtime": "Yes (WebSocket)", "history": "20+ years", "website": "finnhub.io", "note": "Very broad coverage"},
            {"name": "Twelve Data", "free_tier": "Very limited", "data_types": "Stocks, forex, crypto, ETFs", "realtime": "Yes (WebSocket)", "history": "20+ years", "website": "twelvedata.com", "note": "Clean API; credit-based"},
            {"name": "Financial Modeling Prep", "free_tier": "Usable free tier", "data_types": "Global equities, forex, crypto", "realtime": "Yes", "history": "30+ years", "website": "financialmodelingprep.com", "note": "Fundamentals + pricing"},
            {"name": "Marketstack", "free_tier": "Limited requests", "data_types": "Global stocks, intraday, EOD", "realtime": "Delayed", "history": "Varies", "website": "marketstack.com", "note": "Simple JSON format"},
            {"name": "StockData.org", "free_tier": "Free tier", "data_types": "Stocks, forex, crypto, news", "realtime": "Yes", "history": "Varies", "website": "stockdata.org", "note": "Easy to use"},
            {"name": "EODHD", "free_tier": "Limited trial", "data_types": "Global stocks, ETFs, forex, crypto", "realtime": "Delayed + add-on", "history": "30+ years", "website": "eodhd.com", "note": "Deep historical; Excel add-on"},
            {"name": "Polygon.io", "free_tier": "Limited free tier", "data_types": "US equities, options, forex, crypto", "realtime": "Yes (tick-level)", "history": "Full US history", "website": "polygon.io", "note": "Best tick data; US-focused"},
        ],
        "Weather & Climate APIs": [
            {"name": "Open-Meteo", "free_tier": "Completely free, no API key", "data_types": "Global weather forecasts + reanalysis", "realtime": "Yes (forecasts)", "history": "70+ years", "website": "open-meteo.com", "note": "High-resolution; no rate limits"},
            {"name": "NOAA Climate Data Online", "free_tier": "Free API + bulk download", "data_types": "US weather stations, summaries", "realtime": "No (delayed)", "history": "100+ years", "website": "ncdc.noaa.gov/cdo-web", "note": "Very long historical US data"},
            {"name": "Visual Crossing", "free_tier": "Free tier (limited queries)", "data_types": "Global historical + forecast", "realtime": "Yes (forecast)", "history": "Decades", "website": "visualcrossing.com", "note": "Easy API; location-based"},
            {"name": "Meteostat", "free_tier": "Free API", "data_types": "Global historical weather stations", "realtime": "No", "history": "Decades", "website": "meteostat.net", "note": "Clean JSON; many stations"},
            {"name": "OpenWeatherMap", "free_tier": "1000/day", "data_types": "Current weather, forecasts, historical", "realtime": "Yes", "history": "Limited", "website": "openweathermap.org", "note": "60 calls/min rate limit"},
        ],
        "Economic Data APIs": [
            {"name": "FRED (St. Louis Fed)", "free_tier": "Completely free + API", "data_types": "US economic indicators", "realtime": "No (daily/weekly/monthly)", "history": "Decades", "website": "fred.stlouisfed.org", "note": "Gold standard for US macro data"},
            {"name": "World Bank Open Data", "free_tier": "Completely free + API", "data_types": "Global economic, development, health", "realtime": "No", "history": "Decades", "website": "data.worldbank.org", "note": "Excellent for cross-country comparisons"},
            {"name": "OECD Data", "free_tier": "Free API access", "data_types": "Economic, education, health, environment", "realtime": "No", "history": "Decades", "website": "data.oecd.org", "note": "High-quality international stats"},
            {"name": "IMF Data", "free_tier": "Free API", "data_types": "Global macro, fiscal, balance of payments", "realtime": "No", "history": "Decades", "website": "data.imf.org", "note": "Very deep macroeconomic series"},
        ],
        "Cryptocurrency APIs": [
            {"name": "CoinGecko", "free_tier": "Unlimited", "data_types": "Cryptocurrency market data", "realtime": "Yes", "history": "Varies", "website": "coingecko.com", "note": "10-50 calls/min rate limit"},
        ],
        "Open Data Platforms": [
            {"name": "Kaggle Datasets", "free_tier": "Free download + some APIs", "data_types": "Thousands of time series", "realtime": "Rarely", "history": "Varies", "website": "kaggle.com/datasets", "note": "Community datasets; great for practice"},
            {"name": "data.gov", "free_tier": "Free API", "data_types": "US government open data", "realtime": "Varies", "history": "Varies", "website": "data.gov", "note": "Massive US public data catalog"},
            {"name": "Nasdaq Data Link (Quandl)", "free_tier": "Limited free tier", "data_types": "Financial, economic, alternative", "realtime": "Some", "history": "Varies", "website": "data.nasdaq.com", "note": "Was very popular; now more restricted"},
            {"name": "Our World in Data", "free_tier": "Free download + charts API", "data_types": "Global health, environment, economy", "realtime": "No", "history": "Centuries in some cases", "website": "ourworldindata.org", "note": "Beautifully curated; global trends"},
        ],
    }


def show_download_dialog():
    """Show download from API dialog."""
    try:
        app = get_app_instance()
        api_presets = get_api_presets()
        api_categories = get_api_categories()
        
        with ui.dialog() as download_dialog, ui.card().classes("w-full max-w-2xl"):
            ui.label("⬇️ Download from API").classes("text-xl font-semibold mb-2")
            
            # Help text
            with ui.card().classes("w-full p-3 mb-4 bg-blue-50 border-l-4 border-blue-500"):
                ui.label("💡 Getting Started").classes("font-semibold text-blue-800 mb-1")
                ui.label("Choose a data source type above. Use 'Browse All APIs' to discover available APIs, or select 'API (Requires Key)' to configure a specific API. For free datasets without API keys, select 'Free Dataset (No Key)'.").classes("text-sm text-blue-700")
            
            # Data source type selector
            with ui.column().classes("w-full mb-4"):
                source_type_select = ui.select(
                    ["API (Requires Key)", "Free Dataset (No Key)", "Browse All APIs"],
                    label="Data Source Type",
                    value="API (Requires Key)"
                ).classes("w-full")
                ui.label("Select how you want to download data: API with key, free datasets, or browse all available APIs").classes("text-xs text-gray-500 mt-1")
            
            # API Browser section
            with ui.column().classes("w-full") as api_browser_container:
                api_browser_container.visible = False
                
                ui.label("📚 Time-Series API Catalog").classes("text-xl font-semibold mb-2")
                ui.label("Browse all available time-series APIs organized by category").classes("text-sm text-gray-500 mb-2")
                
                with ui.card().classes("w-full p-3 mb-4 bg-green-50 border-l-4 border-green-500"):
                    ui.label("ℹ️ How to Use").classes("font-semibold text-green-800 mb-1")
                    ui.label("Browse APIs by category using the tabs below. Each API card shows free tier limits, real-time capabilities, historical depth, and data types. Click 'Use This API' to automatically configure the API preset in the form.").classes("text-sm text-green-700")
                
                # Category tabs
                with ui.tabs().classes("w-full mb-4") as category_tabs:
                    financial_tab = ui.tab("Financial")
                    weather_tab = ui.tab("Weather")
                    economic_tab = ui.tab("Economic")
                    crypto_tab = ui.tab("Crypto")
                    open_data_tab = ui.tab("Open Data")
                
                with ui.tab_panels(category_tabs, value=financial_tab).classes("w-full"):
                    # Financial APIs panel
                    with ui.tab_panel(financial_tab):
                        with ui.column().classes("w-full gap-3"):
                            for api in api_categories["Financial APIs"]:
                                with ui.card().classes("w-full p-4 hover:bg-gray-50 cursor-pointer"):
                                    ui.label(api["name"]).classes("text-lg font-semibold")
                                    with ui.row().classes("w-full gap-4 text-sm mt-2"):
                                        ui.label(f"Free Tier: {api['free_tier']}").classes("text-blue-600")
                                        ui.label(f"Real-Time: {api['realtime']}").classes("text-green-600")
                                        ui.label(f"History: {api['history']}").classes("text-purple-600")
                                    ui.label(f"Data Types: {api['data_types']}").classes("text-sm text-gray-600 mt-1")
                                    ui.label(f"Note: {api['note']}").classes("text-xs text-gray-500 mt-1")
                                    ui.label(f"Website: {api['website']}").classes("text-xs text-blue-500 mt-1")
                                    def make_select_handler(api_name):
                                        def handler():
                                            source_type_select.value = "API (Requires Key)"
                                            if api_name in api_presets:
                                                api_preset_select.value = api_name
                                                apply_preset()
                                            api_browser_container.visible = False
                                            api_form_container.visible = True
                                        return handler
                                    ui.button("Use This API", icon="arrow_forward", on_click=make_select_handler(api["name"])).classes("mt-2").props("flat size=sm")
                    
                    # Weather APIs panel
                    with ui.tab_panel(weather_tab):
                        with ui.column().classes("w-full gap-3"):
                            for api in api_categories["Weather & Climate APIs"]:
                                with ui.card().classes("w-full p-4 hover:bg-gray-50 cursor-pointer"):
                                    ui.label(api["name"]).classes("text-lg font-semibold")
                                    with ui.row().classes("w-full gap-4 text-sm mt-2"):
                                        ui.label(f"Free Tier: {api['free_tier']}").classes("text-blue-600")
                                        ui.label(f"Real-Time: {api['realtime']}").classes("text-green-600")
                                        ui.label(f"History: {api['history']}").classes("text-purple-600")
                                    ui.label(f"Data Types: {api['data_types']}").classes("text-sm text-gray-600 mt-1")
                                    ui.label(f"Note: {api['note']}").classes("text-xs text-gray-500 mt-1")
                                    ui.label(f"Website: {api['website']}").classes("text-xs text-blue-500 mt-1")
                                    def make_select_handler(api_name):
                                        def handler():
                                            source_type_select.value = "API (Requires Key)"
                                            if api_name in api_presets:
                                                api_preset_select.value = api_name
                                                apply_preset()
                                            api_browser_container.visible = False
                                            api_form_container.visible = True
                                        return handler
                                    ui.button("Use This API", icon="arrow_forward", on_click=make_select_handler(api["name"])).classes("mt-2").props("flat size=sm")
                    
                    # Economic APIs panel
                    with ui.tab_panel(economic_tab):
                        with ui.column().classes("w-full gap-3"):
                            for api in api_categories["Economic Data APIs"]:
                                with ui.card().classes("w-full p-4 hover:bg-gray-50 cursor-pointer"):
                                    ui.label(api["name"]).classes("text-lg font-semibold")
                                    with ui.row().classes("w-full gap-4 text-sm mt-2"):
                                        ui.label(f"Free Tier: {api['free_tier']}").classes("text-blue-600")
                                        ui.label(f"Real-Time: {api['realtime']}").classes("text-green-600")
                                        ui.label(f"History: {api['history']}").classes("text-purple-600")
                                    ui.label(f"Data Types: {api['data_types']}").classes("text-sm text-gray-600 mt-1")
                                    ui.label(f"Note: {api['note']}").classes("text-xs text-gray-500 mt-1")
                                    ui.label(f"Website: {api['website']}").classes("text-xs text-blue-500 mt-1")
                                    def make_select_handler(api_name):
                                        def handler():
                                            source_type_select.value = "API (Requires Key)"
                                            if api_name in api_presets:
                                                api_preset_select.value = api_name
                                                apply_preset()
                                            api_browser_container.visible = False
                                            api_form_container.visible = True
                                        return handler
                                    ui.button("Use This API", icon="arrow_forward", on_click=make_select_handler(api["name"])).classes("mt-2").props("flat size=sm")
                    
                    # Crypto APIs panel
                    with ui.tab_panel(crypto_tab):
                        with ui.column().classes("w-full gap-3"):
                            for api in api_categories["Cryptocurrency APIs"]:
                                with ui.card().classes("w-full p-4 hover:bg-gray-50 cursor-pointer"):
                                    ui.label(api["name"]).classes("text-lg font-semibold")
                                    with ui.row().classes("w-full gap-4 text-sm mt-2"):
                                        ui.label(f"Free Tier: {api['free_tier']}").classes("text-blue-600")
                                        ui.label(f"Real-Time: {api['realtime']}").classes("text-green-600")
                                        ui.label(f"History: {api['history']}").classes("text-purple-600")
                                    ui.label(f"Data Types: {api['data_types']}").classes("text-sm text-gray-600 mt-1")
                                    ui.label(f"Note: {api['note']}").classes("text-xs text-gray-500 mt-1")
                                    ui.label(f"Website: {api['website']}").classes("text-xs text-blue-500 mt-1")
                                    def make_select_handler(api_name):
                                        def handler():
                                            source_type_select.value = "API (Requires Key)"
                                            if api_name in api_presets:
                                                api_preset_select.value = api_name
                                                apply_preset()
                                            api_browser_container.visible = False
                                            api_form_container.visible = True
                                        return handler
                                    ui.button("Use This API", icon="arrow_forward", on_click=make_select_handler(api["name"])).classes("mt-2").props("flat size=sm")
                    
                    # Open Data Platforms panel
                    with ui.tab_panel(open_data_tab):
                        with ui.column().classes("w-full gap-3"):
                            for api in api_categories["Open Data Platforms"]:
                                with ui.card().classes("w-full p-4 hover:bg-gray-50 cursor-pointer"):
                                    ui.label(api["name"]).classes("text-lg font-semibold")
                                    with ui.row().classes("w-full gap-4 text-sm mt-2"):
                                        ui.label(f"Free Tier: {api['free_tier']}").classes("text-blue-600")
                                        ui.label(f"Real-Time: {api['realtime']}").classes("text-green-600")
                                        ui.label(f"History: {api['history']}").classes("text-purple-600")
                                    ui.label(f"Data Types: {api['data_types']}").classes("text-sm text-gray-600 mt-1")
                                    ui.label(f"Note: {api['note']}").classes("text-xs text-gray-500 mt-1")
                                    ui.label(f"Website: {api['website']}").classes("text-xs text-blue-500 mt-1")
                                    def select_api(api_name=api["name"]):
                                        source_type_select.value = "API (Requires Key)"
                                        if api_name in api_presets:
                                            api_preset_select.value = api_name
                                            apply_preset()
                                        api_browser_container.visible = False
                                        api_form_container.visible = True
                                    ui.button("Use This API", icon="arrow_forward", on_click=lambda n=api["name"]: select_api(n)).classes("mt-2").props("flat size=sm")
                
                ui.separator().classes("my-4")
                ui.label("💡 Tip: Click 'Use This API' to automatically configure the API preset, or see API_SOURCES.md for detailed documentation.").classes("text-sm text-blue-600")
            
            # Free datasets section
            with ui.column().classes("w-full") as free_datasets_container:
                free_datasets_container.visible = False
                
                ui.label("📥 Free Time-Series Datasets").classes("text-lg font-semibold mb-2")
                ui.label("Download free datasets without API keys").classes("text-sm text-gray-500 mb-2")
                
                with ui.card().classes("w-full p-3 mb-4 bg-purple-50 border-l-4 border-purple-500"):
                    ui.label("ℹ️ How to Use").classes("font-semibold text-purple-800 mb-1")
                    ui.label("These sources provide direct CSV/JSON downloads. Visit the website, download the file, then use the Upload button in VARIOSYNC to process it. No API keys required!").classes("text-sm text-purple-700")
                
                # List of free data sources
                free_sources = [
                    {
                        "name": "World Bank Open Data",
                        "description": "1,400+ economic indicators, 217+ countries",
                        "url": "https://datatopics.worldbank.org/world-development-indicators",
                        "format": "CSV",
                        "action": "Visit website to download CSV"
                    },
                    {
                        "name": "FRED Economic Data",
                        "description": "US economic time-series (unemployment, GDP, etc.)",
                        "url": "https://fred.stlouisfed.org",
                        "format": "CSV",
                        "action": "Search and download CSV from website"
                    },
                    {
                        "name": "NOAA Climate Data",
                        "description": "US weather and climate historical data",
                        "url": "https://www.ncei.noaa.gov/data/daily-summaries/",
                        "format": "CSV",
                        "action": "Download CSV files directly"
                    },
                    {
                        "name": "Kaggle Datasets",
                        "description": "Thousands of time-series datasets",
                        "url": "https://www.kaggle.com/datasets",
                        "format": "CSV, JSON, Parquet",
                        "action": "Free account required, then download"
                    },
                    {
                        "name": "UCI ML Repository",
                        "description": "Time-series datasets for ML research",
                        "url": "https://archive.ics.uci.edu/ml/index.php",
                        "format": "CSV",
                        "action": "Direct CSV downloads available"
                    },
                    {
                        "name": "Our World in Data",
                        "description": "Global development data (health, environment, etc.)",
                        "url": "https://ourworldindata.org",
                        "format": "CSV",
                        "action": "Download CSV from any chart/dataset"
                    }
                ]
                
                for source in free_sources:
                    with ui.card().classes("w-full p-3 mb-2"):
                        ui.label(source["name"]).classes("font-semibold")
                        ui.label(source["description"]).classes("text-sm text-gray-600")
                        ui.label(f"Format: {source['format']}").classes("text-xs text-gray-500")
                        ui.label(f"Action: {source['action']}").classes("text-xs text-blue-600 mt-1")
                
                ui.separator().classes("my-4")
                
                with ui.card().classes("w-full p-3 bg-yellow-50 border-l-4 border-yellow-500"):
                    ui.label("📋 Instructions").classes("font-semibold text-yellow-800 mb-1")
                    ui.label("1. Visit the website link for your chosen data source").classes("text-sm text-yellow-700")
                    ui.label("2. Download the CSV/JSON file from their website").classes("text-sm text-yellow-700")
                    ui.label("3. Use the Upload button in VARIOSYNC to process the downloaded file").classes("text-sm text-yellow-700")
                    ui.label("4. See FREE_DATA_SOURCES.md for detailed instructions and more sources").classes("text-sm text-yellow-700 mt-2")
            
            # API form fields container
            with ui.column().classes("w-full") as api_form_container:
                api_form_container.visible = True
                
                # API preset selector
                with ui.column().classes("w-full"):
                    api_preset_select = ui.select(
                        list(api_presets.keys()),
                        label="API Preset",
                        value="Custom API"
                    ).classes("w-full")
                    ui.label("Select a pre-configured API or choose 'Custom API' to configure manually").classes("text-xs text-gray-500 mt-1")
                
                # Form fields with help text
                api_name_input = ui.input(label="API Name", placeholder="e.g., Alpha Vantage, OpenWeather").classes("w-full")
                ui.label("A friendly name to identify this API configuration").classes("text-xs text-gray-500 mb-2")
                
                base_url_input = ui.input(label="Base URL", placeholder="https://api.example.com").classes("w-full")
                ui.label("The base URL of the API (without endpoint path)").classes("text-xs text-gray-500 mb-2")
                
                endpoint_input = ui.input(label="Endpoint", placeholder="/data/history").classes("w-full")
                ui.label("The API endpoint path (e.g., /time_series, /stock/candle)").classes("text-xs text-gray-500 mb-2")
                
                api_key_input = ui.input(label="API Key", password=True, placeholder="Your API key").classes("w-full")
                ui.label("Your API key from the service provider. Get it from their website after signing up.").classes("text-xs text-gray-500 mb-2")
                
                entity_input = ui.input(label="Entity/Symbol", placeholder="e.g., AAPL, NYC, latitude,longitude").classes("w-full")
                ui.label("The identifier for the data you want (stock symbol, city name, coordinates, etc.)").classes("text-xs text-gray-500 mb-2")
                
                with ui.row().classes("w-full gap-2"):
                    with ui.column().classes("flex-1"):
                        ui.label("Start Date").classes("text-sm mb-1")
                        start_date_input = ui.date().classes("w-full")
                        ui.label("Beginning of date range").classes("text-xs text-gray-500 mt-1")
                    with ui.column().classes("flex-1"):
                        ui.label("End Date").classes("text-sm mb-1")
                        end_date_input = ui.date().classes("w-full")
                        ui.label("End of date range").classes("text-xs text-gray-500 mt-1")
                
                record_type_select = ui.select(
                    ["time_series", "financial"],
                    label="Record Type",
                    value="time_series"
                ).classes("w-full")
                ui.label("Choose 'time_series' for general data or 'financial' for stock/market data").classes("text-xs text-gray-500 mb-2")
                
                status_label = ui.label("Ready to download").classes("text-sm")
                
                with ui.column().classes("w-full mt-2"):
                    download_button = ui.button("Download", icon="download", color="primary")
                    ui.label("Click to download data from the configured API. Make sure all required fields are filled.").classes("text-xs text-gray-500 mt-1")
            
            def toggle_source_type():
                if source_type_select.value == "Free Dataset (No Key)":
                    api_form_container.visible = False
                    free_datasets_container.visible = True
                    api_browser_container.visible = False
                elif source_type_select.value == "Browse All APIs":
                    api_form_container.visible = False
                    free_datasets_container.visible = False
                    api_browser_container.visible = True
                else:
                    api_form_container.visible = True
                    free_datasets_container.visible = False
                    api_browser_container.visible = False
            
            source_type_select.on('update:modelValue', toggle_source_type)
            
            # Helper function to populate fields from preset
            def apply_preset():
                preset_name = api_preset_select.value
                if preset_name != "Custom API" and preset_name in api_presets:
                    preset = api_presets[preset_name]
                    api_name_input.value = preset_name
                    base_url_input.value = preset.get("base_url", "")
                    endpoint_input.value = preset.get("endpoint", "")
                    api_key_input.value = ""  # User must enter their own key
                    if preset.get("note"):
                        ui.notify(preset["note"], type="info")
            
            api_preset_select.on('update:modelValue', apply_preset)
            
            # Load saved API keys
            try:
                from api_keys_manager import APIKeysManager
                keys_manager = APIKeysManager()
                saved_keys = keys_manager.get_keys()
                if saved_keys:
                    api_key_select = ui.select(
                        [k['name'] for k in saved_keys],
                        label="Use Saved API Key",
                        value=None
                    ).classes("w-full")
                    
                    def use_saved_key():
                        selected = api_key_select.value
                        if selected:
                            key_data = next((k for k in saved_keys if k['name'] == selected), None)
                            if key_data:
                                try:
                                    keys_file = Path("api_keys.json")
                                    if keys_file.exists():
                                        with open(keys_file, 'r') as f:
                                            keys_data = json.load(f)
                                            for k in keys_data.get('keys', []):
                                                if k.get('name') == selected:
                                                    api_key_input.value = k.get('api_key', '')
                                                    ui.notify(f"Loaded API key for {selected}", type="positive")
                                                    return
                                except:
                                    pass
                                ui.notify(f"Select {selected} and enter key manually (keys are stored securely)", type="info")
                    api_key_select.on('update:modelValue', use_saved_key)
            except:
                pass
            
            def execute_download():
                try:
                    download_button.set_enabled(False)
                    status_label.text = "⏳ Downloading..."
                    
                    # Get preset config if selected
                    preset_name = api_preset_select.value
                    preset_config = api_presets.get(preset_name) if preset_name != "Custom API" else {}
                    
                    # Build API config (use preset values as defaults)
                    api_config = {
                        "name": api_name_input.value or preset_name or "Custom API",
                        "base_url": base_url_input.value or preset_config.get("base_url", ""),
                        "endpoint": endpoint_input.value or preset_config.get("endpoint", ""),
                        "api_key": api_key_input.value,
                        "api_key_param": preset_config.get("api_key_param", "apikey"),
                        "entity_param": preset_config.get("entity_param", "symbol"),
                        "start_date_param": preset_config.get("start_date_param", "from"),
                        "end_date_param": preset_config.get("end_date_param", "to"),
                        "date_format": preset_config.get("date_format", "YYYY-MM-DD"),
                        "response_format": "json"
                    }
                    
                    # Validate required fields
                    if not all([base_url_input.value, endpoint_input.value, api_key_input.value, entity_input.value]):
                        status_label.text = "❌ Please fill in all required fields"
                        download_button.set_enabled(True)
                        return
                    
                    # Import and use APIDownloader
                    from api_downloader import APIDownloader
                    from datetime import datetime as dt
                    
                    downloader = APIDownloader(api_config, app.storage)
                    
                    start_date = None
                    end_date = None
                    if start_date_input.value:
                        if isinstance(start_date_input.value, str):
                            start_date = dt.fromisoformat(start_date_input.value)
                        else:
                            start_date = dt.combine(start_date_input.value, dt.min.time())
                    if end_date_input.value:
                        if isinstance(end_date_input.value, str):
                            end_date = dt.fromisoformat(end_date_input.value)
                        else:
                            end_date = dt.combine(end_date_input.value, dt.max.time())
                    
                    # Download and save
                    success = downloader.download_and_save(
                        entity_input.value,
                        start_date,
                        end_date
                    )
                    
                    if success:
                        status_label.text = "✅ Download completed successfully!"
                        ui.notify("Download completed", type="positive")
                        # Refresh storage browser
                        ui.run_javascript('document.querySelector("[data-section=\\"storage\\"]")?.scrollIntoView({behavior: "smooth"})')
                    else:
                        status_label.text = "❌ Download failed. Check API configuration."
                        ui.notify("Download failed", type="negative")
                    
                    download_button.set_enabled(True)
                except Exception as e:
                    logger.error(f"Error downloading from API: {e}", exc_info=True)
                    status_label.text = f"❌ Error: {str(e)}"
                    ui.notify(f"Download error: {str(e)}", type="negative")
                    download_button.set_enabled(True)
            
            download_button.on_click(execute_download)
            
            with ui.column().classes("w-full gap-2 mt-4"):
                with ui.card().classes("w-full p-3 bg-gray-50"):
                    ui.label("📖 Additional Resources").classes("font-semibold text-gray-800 mb-2")
                    ui.label("• API_SOURCES.md - Complete API documentation with configuration examples").classes("text-xs text-gray-600 mb-1")
                    ui.label("• FREE_DATA_SOURCES.md - List of free datasets (no API keys required)").classes("text-xs text-gray-600 mb-1")
                    ui.label("• Configure persistent API sources in config.json for reuse").classes("text-xs text-gray-600 mb-2")
                    
                    with ui.row().classes("w-full gap-2"):
                        def open_api_docs():
                            ui.notify("See API_SOURCES.md file for complete API documentation", type="info")
                        
                        def open_free_data_docs():
                            ui.notify("See FREE_DATA_SOURCES.md for free datasets (no API keys)", type="info")
                        
                        ui.button("📚 View API Docs", icon="book", on_click=open_api_docs).props("flat size=sm")
                        ui.button("📥 View Free Data", icon="download", on_click=open_free_data_docs).props("flat size=sm")
            
            with ui.row().classes("w-full justify-end mt-4"):
                ui.button("Close", on_click=download_dialog.close).props("flat")
        
        download_dialog.open()
    except Exception as e:
        logger.error(f"Error showing download dialog: {e}", exc_info=True)
        ui.notify(f"Error: {str(e)}", type="negative")


def show_user_info_dialog():
    """Show user information dialog."""
    try:
        app = get_app_instance()
        with ui.dialog() as user_dialog, ui.card().classes("w-full max-w-2xl"):
            ui.label("👤 User Information").classes("text-xl font-semibold mb-4")
            
            # Get user info from Supabase if available
            user_id = None
            user_email = None
            hours_remaining = None
            account_status = "Not authenticated"
            data_sources_count = 0
            
            if app.auth_manager and app.auth_manager.supabase_client:
                try:
                    supabase_client = app.auth_manager.supabase_client
                    account_status = "Connected to Supabase"
                except Exception as e:
                    logger.debug(f"Could not get user info: {e}")
            
            with ui.column().classes("w-full gap-3"):
                # Account Status
                with ui.card().classes("w-full p-4"):
                    ui.label("Account Status").classes("text-sm font-semibold mb-2")
                    ui.label(f"Status: {account_status}").classes("text-sm")
                    if user_email:
                        ui.label(f"Email: {user_email}").classes("text-sm")
                    if user_id:
                        ui.label(f"User ID: {user_id[:8]}...").classes("text-sm text-gray-500")
                
                # Hours Balance
                with ui.card().classes("w-full p-4"):
                    ui.label("Hours Balance").classes("text-sm font-semibold mb-2")
                    if hours_remaining is not None:
                        ui.label(f"Remaining: {hours_remaining:.2f} hours").classes("text-lg font-bold text-green-600")
                    else:
                        ui.label("Hours balance not available").classes("text-sm text-gray-500")
                        ui.label("Connect to Supabase and authenticate to view balance").classes("text-xs text-gray-400")
                
                # System Status
                with ui.card().classes("w-full p-4"):
                    ui.label("System Status").classes("text-sm font-semibold mb-2")
                    ui.label(f"Storage: {'✅ Available' if app.storage else '❌ Not configured'}").classes("text-sm")
                    ui.label(f"Auth Manager: {'✅ Available' if app.auth_manager else '❌ Not configured'}").classes("text-sm")
                    if app.storage:
                        try:
                            keys = app.storage.list_keys()
                            ui.label(f"Data Sources: {len(keys)} files").classes("text-sm")
                        except:
                            ui.label("Data Sources: Unable to count").classes("text-sm")
                
                # Configuration Info
                with ui.card().classes("w-full p-4"):
                    ui.label("Configuration").classes("text-sm font-semibold mb-2")
                    storage_backend = app.config.get('Data', {}).get('storage_backend', 'local')
                    ui.label(f"Storage Backend: {storage_backend}").classes("text-sm")
                    if app.auth_manager:
                        enforce_payment = app.config.get('Authentication', {}).get('enforce_payment', False)
                        ui.label(f"Payment Enforcement: {'Enabled' if enforce_payment else 'Disabled'}").classes("text-sm")
            
            with ui.row().classes("w-full justify-end mt-4"):
                ui.button("Close", on_click=user_dialog.close).props("flat")
        
        user_dialog.open()
    except Exception as e:
        logger.error(f"Error showing user info dialog: {e}", exc_info=True)
        ui.notify(f"Error: {str(e)}", type="negative")


def show_api_keys_dialog():
    """Show API keys management dialog."""
    try:
        app = get_app_instance()
        with ui.dialog() as keys_dialog, ui.card().classes("w-full max-w-4xl"):
            ui.label("🔑 API Keys Management").classes("text-xl font-semibold mb-4")
            
            try:
                from api_keys_manager import APIKeysManager
                keys_manager = APIKeysManager()
                
                # Keys table
                keys_table = ui.table(
                    columns=[
                        {"name": "name", "label": "Name", "field": "name", "required": True},
                        {"name": "api_key", "label": "API Key", "field": "api_key"},
                        {"name": "created", "label": "Created", "field": "created"}
                    ],
                    rows=[],
                    row_key="name"
                ).classes("w-full")
                
                def refresh_keys_table():
                    try:
                        keys = keys_manager.get_keys()
                        # Mask API keys for display
                        display_keys = []
                        for k in keys:
                            masked_key = k.get('api_key', '')
                            if len(masked_key) > 8:
                                masked_key = masked_key[:4] + "..." + masked_key[-4:]
                            display_keys.append({
                                "name": k.get('name', ''),
                                "api_key": masked_key,
                                "created": k.get('created_at', 'N/A')
                            })
                        keys_table.rows = display_keys
                    except Exception as e:
                        logger.error(f"Error refreshing keys table: {e}")
                        ui.notify(f"Error: {str(e)}", type="negative")
                
                refresh_keys_table()
                
                # Add new key form
                with ui.card().classes("w-full p-4 mt-4"):
                    ui.label("Add New API Key").classes("text-lg font-semibold mb-2")
                    
                    new_key_name = ui.input(label="Key Name", placeholder="e.g., Alpha Vantage Production").classes("w-full")
                    new_key_value = ui.input(label="API Key", password=True, placeholder="Enter API key").classes("w-full")
                    
                    def add_key():
                        try:
                            if not new_key_name.value or not new_key_value.value:
                                ui.notify("Please fill in both name and key", type="warning")
                                return
                            
                            keys_manager.add_key(new_key_name.value, new_key_value.value)
                            ui.notify(f"Added API key: {new_key_name.value}", type="positive")
                            new_key_name.value = ""
                            new_key_value.value = ""
                            refresh_keys_table()
                        except Exception as e:
                            logger.error(f"Error adding key: {e}")
                            ui.notify(f"Error: {str(e)}", type="negative")
                    
                    ui.button("Add Key", icon="add", color="primary", on_click=add_key).classes("mt-2")
                
            except ImportError:
                ui.label("API Keys Manager not available. Install required dependencies.").classes("text-red-500")
            except Exception as e:
                logger.error(f"Error loading API keys manager: {e}")
                ui.label(f"Error: {str(e)}").classes("text-red-500")
            
            with ui.row().classes("w-full justify-end mt-4"):
                ui.button("Close", on_click=keys_dialog.close).props("flat")
        
        keys_dialog.open()
    except Exception as e:
        logger.error(f"Error showing API keys dialog: {e}", exc_info=True)
        ui.notify(f"Error: {str(e)}", type="negative")


def show_search_dialog():
    """Show search dialog."""
    try:
        app = get_app_instance()
        with ui.dialog() as search_dialog, ui.card().classes("w-full max-w-4xl"):
            ui.label("🔍 Search").classes("text-xl font-semibold mb-4")
            
            search_input = ui.input(placeholder="Search records, series, metrics...").classes("w-full")
            
            # Filters - get all supported formats dynamically
            from file_exporter import FileExporter
            exporter = FileExporter()
            all_formats = exporter.get_supported_formats()
            file_type_options = ["All"] + sorted(all_formats)
            
            with ui.row().classes("w-full gap-2"):
                file_type_filter = ui.select(
                    file_type_options,
                    label="File Type",
                    value="All"
                ).classes("flex-1")
                
                series_filter = ui.input(label="Series ID", placeholder="Filter by series...").classes("flex-1")
            
            with ui.row().classes("w-full gap-2"):
                with ui.column().classes("flex-1"):
                    ui.label("Start Date").classes("text-sm mb-1")
                    start_date_filter = ui.date().classes("w-full")
                with ui.column().classes("flex-1"):
                    ui.label("End Date").classes("text-sm mb-1")
                    end_date_filter = ui.date().classes("w-full")
            
            search_button = ui.button("Search", icon="search", color="primary")
            
            # Results table
            results_table = ui.table(
                columns=[
                    {"name": "key", "label": "Key", "field": "key", "required": True},
                    {"name": "type", "label": "Type", "field": "type"},
                    {"name": "size", "label": "Size", "field": "size"}
                ],
                rows=[],
                row_key="key"
            ).classes("w-full mt-4")
            
            results_count_label = ui.label("No results").classes("text-sm text-gray-500")
            
            def perform_search():
                try:
                    search_button.set_enabled(False)
                    query = search_input.value.lower() if search_input.value else ""
                    
                    if not app.storage:
                        ui.notify("Storage not available", type="warning")
                        return
                    
                    # Get all keys
                    all_keys = app.storage.list_keys()
                    
                    # Apply filters
                    filtered_keys = []
                    for key in all_keys:
                        # File type filter
                        if file_type_filter.value != "All":
                            if not key.lower().endswith(f".{file_type_filter.value.lower()}"):
                                continue
                        
                        # Text search
                        if query:
                            if query not in key.lower():
                                continue
                        
                        # Series filter
                        if series_filter.value:
                            if series_filter.value.lower() not in key.lower():
                                continue
                        
                        filtered_keys.append(key)
                    
                    # Build results
                    results = []
                    for key in filtered_keys[:100]:  # Limit to 100 results
                        file_type = key.split('.')[-1].upper() if '.' in key else 'DATA'
                        size_bytes = app.storage.get_size(key)
                        
                        if size_bytes is not None:
                            if size_bytes >= 1024 * 1024:
                                size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
                            elif size_bytes >= 1024:
                                size_str = f"{size_bytes / 1024:.2f} KB"
                            else:
                                size_str = f"{size_bytes} B"
                        else:
                            size_str = "N/A"
                        
                        results.append({
                            "key": key,
                            "type": file_type,
                            "size": size_str
                        })
                    
                    results_table.rows = results
                    results_count_label.text = f"Found {len(results)} result(s)"
                    
                    if len(results) == 0:
                        ui.notify("No results found", type="info")
                    else:
                        ui.notify(f"Found {len(results)} results", type="positive")
                    
                    search_button.set_enabled(True)
                except Exception as e:
                    logger.error(f"Error performing search: {e}", exc_info=True)
                    ui.notify(f"Search error: {str(e)}", type="negative")
                    search_button.set_enabled(True)
            
            search_button.on_click(perform_search)
            search_input.on('keydown.enter', perform_search)
            
            # Cache search in Redis if available
            def cache_search_results(query, results):
                try:
                    from redis_client import RedisClientFactory
                    redis_client = RedisClientFactory.get_instance()
                    if redis_client:
                        redis_client.set(f"search:{query}", results, ttl=3600)
                except:
                    pass
            
            with ui.row().classes("w-full justify-end mt-4"):
                ui.button("Close", on_click=search_dialog.close).props("flat")
        
        search_dialog.open()
    except Exception as e:
        logger.error(f"Error showing search dialog: {e}", exc_info=True)
        ui.notify(f"Error: {str(e)}", type="negative")


def show_payment_dialog():
    """Show payment dialog."""
    try:
        app = get_app_instance()
        with ui.dialog() as payment_dialog, ui.card().classes("w-full max-w-2xl"):
            ui.label("💳 Payment & Billing").classes("text-xl font-semibold mb-4")
            
            hours_remaining = None
            hours_used = 0.0
            
            # Try to get hours from Supabase
            if app.auth_manager and app.auth_manager.supabase_client:
                try:
                    supabase_client = app.auth_manager.supabase_client
                    if hasattr(supabase_client, 'operations'):
                        pass
                except Exception as e:
                    logger.debug(f"Could not get payment info: {e}")
            
            with ui.column().classes("w-full gap-4"):
                # Current Balance
                with ui.card().classes("w-full p-4 bg-blue-50 dark:bg-blue-900"):
                    ui.label("Current Balance").classes("text-sm font-semibold mb-2")
                    if hours_remaining is not None:
                        ui.label(f"{hours_remaining:.2f} hours remaining").classes("text-2xl font-bold text-green-600")
                    else:
                        ui.label("Hours balance not available").classes("text-lg text-gray-500")
                        ui.label("Connect to Supabase and authenticate to view balance").classes("text-xs text-gray-400 mt-1")
                
                # Usage Information
                with ui.card().classes("w-full p-4"):
                    ui.label("Usage Information").classes("text-sm font-semibold mb-2")
                    ui.label(f"Hours Used: {hours_used:.2f}h").classes("text-sm")
                    if hours_remaining is not None:
                        total_hours = hours_remaining + hours_used
                        if total_hours > 0:
                            usage_percent = (hours_used / total_hours) * 100
                            ui.label(f"Usage: {usage_percent:.1f}%").classes("text-sm")
                
                # Hour Packages
                with ui.card().classes("w-full p-4"):
                    ui.label("Purchase Hours").classes("text-sm font-semibold mb-3")
                    packages = [
                        {"hours": 5, "price": 25, "name": "5 Hours Pack"},
                        {"hours": 10, "price": 45, "name": "10 Hours Pack"},
                        {"hours": 20, "price": 80, "name": "20 Hours Pack"},
                        {"hours": 50, "price": 180, "name": "50 Hours Pack"}
                    ]
                    
                    with ui.grid(columns=2).classes("w-full gap-2"):
                        for pkg in packages:
                            with ui.card().classes("p-3 cursor-pointer hover:bg-gray-100"):
                                ui.label(pkg["name"]).classes("font-semibold")
                                ui.label(f"{pkg['hours']} hours").classes("text-sm")
                                ui.label(f"${pkg['price']}").classes("text-lg font-bold text-blue-600")
                    
                    ui.label("Payment integration coming soon").classes("text-xs text-gray-400 mt-2")
                
                # Billing History
                with ui.card().classes("w-full p-4"):
                    ui.label("Billing History").classes("text-sm font-semibold mb-2")
                    ui.label("No billing history available").classes("text-sm text-gray-500")
            
            with ui.row().classes("w-full justify-end mt-4"):
                ui.button("Close", on_click=payment_dialog.close).props("flat")
        
        payment_dialog.open()
    except Exception as e:
        logger.error(f"Error showing payment info: {e}", exc_info=True)
        ui.notify(f"Error: {str(e)}", type="negative")


def show_settings_dialog():
    """Show settings dialog."""
    try:
        app = get_app_instance()
        with ui.dialog() as settings_dialog, ui.card().classes("w-full max-w-3xl"):
            ui.label("⚙️ Settings").classes("text-xl font-semibold mb-4")
            
            # Create tabs
            with ui.tabs().classes("w-full") as tabs:
                general_tab = ui.tab("General")
                api_tab = ui.tab("API")
                display_tab = ui.tab("Display")
                performance_tab = ui.tab("Performance")
            
            with ui.tab_panels(tabs, value=general_tab).classes("w-full"):
                # General Settings
                with ui.tab_panel(general_tab):
                    with ui.column().classes("w-full gap-4"):
                        storage_backend_select = ui.select(
                            ["local", "s3", "wasabi", "supabase"],
                            label="Storage Backend",
                            value=app.config.get('Data', {}).get('storage_backend', 'local')
                        ).classes("w-full")
                        
                        storage_path_input = ui.input(
                            label="Storage Path",
                            value=app.config.get('Data', {}).get('csv_dir', 'data')
                        ).classes("w-full")
                        
                        log_level_select = ui.select(
                            ["DEBUG", "INFO", "WARNING", "ERROR"],
                            label="Log Level",
                            value=app.config.get('Logging', {}).get('level', 'INFO')
                        ).classes("w-full")
                        
                        log_file_input = ui.input(
                            label="Log File",
                            value=app.config.get('Logging', {}).get('file', 'variosync.log')
                        ).classes("w-full")
                
                # API Settings
                with ui.tab_panel(api_tab):
                    with ui.column().classes("w-full gap-4"):
                        timeout_input = ui.number(
                            label="API Timeout (seconds)",
                            value=app.config.get('Download', {}).get('timeout', 30),
                            min=1,
                            max=300
                        ).classes("w-full")
                        
                        max_retries_input = ui.number(
                            label="Max Retries",
                            value=app.config.get('Download', {}).get('max_retries', 3),
                            min=0,
                            max=10
                        ).classes("w-full")
                        
                        rate_limit_input = ui.number(
                            label="Rate Limit Delay (seconds)",
                            value=app.config.get('Download', {}).get('rate_limit_delay', 1.0),
                            min=0.1,
                            max=60.0,
                            step=0.1
                        ).classes("w-full")
                
                # Display Settings
                with ui.tab_panel(display_tab):
                    with ui.column().classes("w-full gap-4"):
                        rows_per_page_input = ui.number(
                            label="Rows Per Page",
                            value=app.config.get('Display', {}).get('rows_per_page', 100),
                            min=10,
                            max=1000
                        ).classes("w-full")
                        
                        theme_select = ui.select(
                            ["default", "dark", "light"],
                            label="Theme",
                            value=app.config.get('Display', {}).get('theme', 'default')
                        ).classes("w-full")
                        
                        font_size_input = ui.number(
                            label="Font Size",
                            value=app.config.get('Display', {}).get('font_size', 10),
                            min=8,
                            max=20
                        ).classes("w-full")
                
                # Performance Settings
                with ui.tab_panel(performance_tab):
                    with ui.column().classes("w-full gap-4"):
                        cache_size_input = ui.number(
                            label="Cache Size",
                            value=app.config.get('Data', {}).get('cache_size', 1000),
                            min=100,
                            max=10000
                        ).classes("w-full")
                        
                        thread_count_input = ui.number(
                            label="Thread Count",
                            value=app.config.get('Data', {}).get('thread_count', 4),
                            min=1,
                            max=16
                        ).classes("w-full")
                        
                        memory_limit_input = ui.number(
                            label="Memory Limit (MB)",
                            value=app.config.get('Performance', {}).get('memory_limit', 1024),
                            min=256,
                            max=8192
                        ).classes("w-full")
            
            # Save button
            def save_settings():
                try:
                    # Build updated config
                    updated_config = app.config.config.copy()
                    
                    # Update Data section
                    if 'Data' not in updated_config:
                        updated_config['Data'] = {}
                    updated_config['Data']['storage_backend'] = storage_backend_select.value
                    updated_config['Data']['csv_dir'] = storage_path_input.value
                    updated_config['Data']['cache_size'] = int(cache_size_input.value)
                    updated_config['Data']['thread_count'] = int(thread_count_input.value)
                    
                    # Update Logging section
                    if 'Logging' not in updated_config:
                        updated_config['Logging'] = {}
                    updated_config['Logging']['level'] = log_level_select.value
                    updated_config['Logging']['file'] = log_file_input.value
                    
                    # Update Download section
                    if 'Download' not in updated_config:
                        updated_config['Download'] = {}
                    updated_config['Download']['timeout'] = int(timeout_input.value)
                    updated_config['Download']['max_retries'] = int(max_retries_input.value)
                    updated_config['Download']['rate_limit_delay'] = float(rate_limit_input.value)
                    
                    # Update Display section
                    if 'Display' not in updated_config:
                        updated_config['Display'] = {}
                    updated_config['Display']['rows_per_page'] = int(rows_per_page_input.value)
                    updated_config['Display']['theme'] = theme_select.value
                    updated_config['Display']['font_size'] = int(font_size_input.value)
                    
                    # Update Performance section
                    if 'Performance' not in updated_config:
                        updated_config['Performance'] = {}
                    updated_config['Performance']['memory_limit'] = int(memory_limit_input.value)
                    
                    # Save to config file
                    config_path = getattr(app.config, 'config_path', 'config.json')
                    with open(config_path, 'w') as f:
                        json.dump(updated_config, f, indent=2)
                    
                    ui.notify("Settings saved successfully. Restart application to apply changes.", type="positive")
                    settings_dialog.close()
                except Exception as e:
                    logger.error(f"Error saving settings: {e}", exc_info=True)
                    ui.notify(f"Error saving settings: {str(e)}", type="negative")
            
            with ui.row().classes("w-full justify-between mt-4"):
                ui.button("Reset to Defaults", icon="refresh", on_click=lambda: ui.notify("Reset functionality coming soon", type="info"))
                with ui.row().classes("gap-2"):
                    ui.button("Cancel", on_click=settings_dialog.close).props("flat")
                    ui.button("Save", icon="save", color="primary", on_click=save_settings)
        
        settings_dialog.open()
    except Exception as e:
        logger.error(f"Error showing settings: {e}", exc_info=True)
        ui.notify(f"Error: {str(e)}", type="negative")
