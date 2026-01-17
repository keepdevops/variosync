# Quick Start: Cloud Integration

This guide helps you quickly integrate Redis and Modal into your VARIOSYNC application.

## 1. Redis Integration (5 minutes)

### Add Redis Caching to Data Queries

Update `main.py` to use Redis for caching:

```python
from redis_client import RedisClientFactory

class VariosyncApp:
    def __init__(self, ...):
        # ... existing code ...
        self.redis = RedisClientFactory.get_instance()  # Optional
    
    def process_data_file(self, file_path: str, ...):
        # Check cache first
        cache_key = f"file:{file_path}:{record_type}"
        
        if self.redis:
            cached = self.redis.get(cache_key)
            if cached:
                logger.info("Returning cached result")
                return cached
        
        # Process file (existing logic)
        result = ...  # your processing logic
        
        # Cache result
        if self.redis:
            self.redis.set(cache_key, result, ttl=3600)  # 1 hour
        
        return result
```

### Add Rate Limiting to Upload Handler

Update `nicegui_app.py`:

```python
from rate_limiter import rate_limit, get_client_identifier

@rate_limit(limit=10, window=60)  # 10 uploads per minute
def handle_upload(e):
    # ... existing upload logic ...
    pass
```

## 2. Modal Integration (10 minutes)

### Add ML Forecast Feature

Update `nicegui_app.py` to add ML inference:

```python
from modal_client import ModalClientFactory

def dashboard_page():
    # ... existing code ...
    
    modal_client = ModalClientFactory.get_instance()
    
    if modal_client and modal_client.available:
        # Add ML forecast button
        forecast_button = ui.button("Generate Forecast", icon="trending_up")
        
        def generate_forecast():
            # Get current plot data
            # Call Modal function
            result = modal_client.prophet_forecast(data, periods=30)
            if result:
                # Update plot with forecast
                pass
```

## 3. Environment Setup

Create `.env` file:

```bash
# Redis
REDIS_URL=redis://localhost:6379/0

# Modal (optional)
MODAL_TOKEN_ID=your-token-id
MODAL_TOKEN_SECRET=your-token-secret

# Enable features
ENABLE_REDIS_CACHE=true
ENABLE_MODAL_FUNCTIONS=true
```

## 4. Test Locally

### Start Redis (Docker)

```bash
docker run -d -p 6379:6379 redis:alpine
```

### Test Redis Connection

```python
from redis_client import RedisClientFactory

redis = RedisClientFactory.get_instance()
if redis:
    redis.set("test", "value", ttl=60)
    print(redis.get("test"))  # Should print "value"
```

### Test Rate Limiting

```python
from rate_limiter import check_rate_limit

result = check_rate_limit("test_user", limit=5, window=60)
print(f"Allowed: {result['allowed']}, Remaining: {result['remaining']}")
```

## 5. Deploy to Cloud

### Deploy Modal Functions

```bash
cd modal_functions
modal deploy ml_inference.py
modal deploy data_processing.py
modal deploy batch_exports.py
```

### Configure Render.com

Add environment variables in Render.com dashboard:
- `REDIS_URL` - Your Upstash/Render Redis URL
- `MODAL_TOKEN_ID` - Your Modal token
- `MODAL_TOKEN_SECRET` - Your Modal secret

## Next Steps

1. ✅ Redis caching integrated
2. ✅ Rate limiting added
3. ⏭️ Add more caching points
4. ⏭️ Add ML features to UI
5. ⏭️ Deploy Modal functions
6. ⏭️ Test end-to-end

See `NEXT_STEPS.md` for complete roadmap.
