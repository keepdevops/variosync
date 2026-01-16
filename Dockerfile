FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional web dependencies including hvplot and bokeh-fastapi
RUN pip install --no-cache-dir \
    panel>=1.4.5 \
    holoviews>=1.17.0 \
    hvplot>=0.9.0 \
    pandas \
    pyarrow \
    plotly \
    bokeh>=3.0.0 \
    bokeh-fastapi \
    wsproto

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data

# Expose port (default 8000, can be overridden)
EXPOSE 8000

# Set environment variables
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the web application
CMD ["sh", "-c", "uvicorn web_app:app --host 0.0.0.0 --port ${PORT:-8000}"]
