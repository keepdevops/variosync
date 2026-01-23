# TimescaleDB Compatibility with VARIOSYNC Services

This document explains how TimescaleDB works with Render, Supabase, Modal, Wasabi, and Redis in the VARIOSYNC architecture.

## Overview

TimescaleDB is a PostgreSQL extension optimized for time-series data. Your codebase currently includes TimescaleDB export functionality (`file_exporter/database.py`), but TimescaleDB can be integrated more deeply into your stack.

## Compatibility Matrix

| Service | TimescaleDB Support | Integration Method | Notes |
|---------|-------------------|-------------------|-------|
| **Supabase** | ✅ **Yes** | PostgreSQL extension | Can enable TimescaleDB extension on Supabase PostgreSQL |
| **Render** | ✅ **Yes** | Managed database service | Can host TimescaleDB as a PostgreSQL database |
| **Modal** | ✅ **Yes** | External connection | Modal functions can connect to external TimescaleDB |
| **Wasabi** | ✅ **Yes** | Backup/export storage | Can store TimescaleDB backups and exports |
| **Redis** | ✅ **Yes** | Complementary caching | Works alongside TimescaleDB for caching |

---

## 1. Supabase + TimescaleDB

### Compatibility: ✅ **Fully Compatible**

Supabase uses PostgreSQL, which TimescaleDB extends. You can enable TimescaleDB on your Supabase database.

### How to Enable TimescaleDB on Supabase

1. **Enable Extension in Supabase Dashboard:**
   - Go to your Supabase project dashboard
   - Navigate to Database → Extensions
   - Search for "timescaledb"
   - Click "Enable"

2. **Or via SQL Editor:**
   ```sql
   CREATE EXTENSION IF NOT EXISTS timescaledb;
   ```

3. **Verify Installation:**
   ```sql
   SELECT default_version, installed_version 
   FROM pg_available_extensions 
   WHERE name = 'timescaledb';
   ```

### Integration with VARIOSYNC

Your existing `export_to_timescaledb()` function in `file_exporter/database.py` can connect directly to Supabase:

```python
# Use Supabase connection string
connection_string = f"postgresql://postgres:{password}@{host}:5432/postgres"
DatabaseExporter.export_to_timescaledb(
    data=data,
    output_path="output.sql",
    connection_string=connection_string,
    create_hypertable=True
)
```

### Benefits
- ✅ Native PostgreSQL compatibility
- ✅ No additional database service needed
- ✅ Leverages Supabase's managed PostgreSQL infrastructure
- ✅ Can use Supabase's connection pooling
- ✅ Integrated with Supabase Auth and RLS policies

### Limitations
- ⚠️ Supabase free tier may have limitations on extension availability
- ⚠️ Check Supabase plan for TimescaleDB support (may require Pro plan)

---

## 2. Render + TimescaleDB

### Compatibility: ✅ **Fully Compatible**

Render.com can host TimescaleDB as a managed PostgreSQL database service.

### How to Set Up TimescaleDB on Render

1. **Create PostgreSQL Database:**
   - In Render dashboard, create a new PostgreSQL database
   - Select region close to your web service
   - Choose plan (TimescaleDB works on all plans)

2. **Enable TimescaleDB Extension:**
   ```sql
   CREATE EXTENSION IF NOT EXISTS timescaledb;
   ```

3. **Update `render.yaml`:**
   ```yaml
   databases:
     - name: variosync-timescaledb
       plan: starter  # or pro for production
       type: postgresql
       extensions:
         - timescaledb
   ```

4. **Connect from Your App:**
   - Render provides `DATABASE_URL` environment variable
   - Use this connection string in your TimescaleDB exporter

### Integration Points

- **Web Service:** Your Render web service can connect to TimescaleDB
- **Modal Functions:** Can connect to Render-hosted TimescaleDB
- **Backups:** Render provides automatic backups

### Benefits
- ✅ Managed service with automatic backups
- ✅ Scales with your application
- ✅ Integrated with Render's infrastructure
- ✅ Easy to configure via `render.yaml`

---

## 3. Modal + TimescaleDB

### Compatibility: ✅ **Fully Compatible**

Modal serverless functions can connect to external TimescaleDB instances (Supabase, Render, or self-hosted).

### Integration Pattern

Your Modal functions can connect to TimescaleDB for heavy data processing:

```python
# In modal_functions/data_processing.py
import modal
import psycopg2

app = modal.App("variosync-processing")

@app.function(
    secrets=[modal.Secret.from_name("timescaledb-credentials")],
    image=modal.Image.debian_slim(python_version="3.11")
    .pip_install("psycopg2-binary", "timescaledb")
)
def process_to_timescaledb(data_path: str, connection_string: str):
    """Process data and insert into TimescaleDB."""
    conn = psycopg2.connect(connection_string)
    # ... process and insert data
    conn.close()
```

### Configuration

1. **Create Modal Secret:**
   ```bash
   modal secret create timescaledb-credentials \
     TIMESCALEDB_URL=postgresql://user:pass@host:5432/db
   ```

2. **Use in Functions:**
   ```python
   connection_string = os.getenv("TIMESCALEDB_URL")
   ```

### Use Cases
- ✅ Heavy data processing and bulk inserts
- ✅ ML inference results storage
- ✅ Batch exports to TimescaleDB
- ✅ Time-series aggregation and analysis

### Benefits
- ✅ Serverless scaling for data processing
- ✅ Can handle large datasets
- ✅ Pay-per-use pricing
- ✅ Parallel processing capabilities

---

## 4. Wasabi + TimescaleDB

### Compatibility: ✅ **Fully Compatible**

Wasabi (S3-compatible storage) can store TimescaleDB backups, exports, and data files.

### Integration Patterns

1. **Backup Storage:**
   ```python
   # Backup TimescaleDB to Wasabi
   import boto3
   
   # Use pg_dump to create backup
   # Upload to Wasabi
   s3_client = boto3.client(
       's3',
       endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
       aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
       aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
   )
   
   s3_client.upload_file('timescaledb_backup.sql', 'bucket', 'backups/timescaledb.sql')
   ```

2. **Export Storage:**
   Your existing export functionality can upload to Wasabi:
   ```python
   # Export to TimescaleDB format, then upload to Wasabi
   DatabaseExporter.export_to_timescaledb(data, "local_file.sql")
   # Upload to Wasabi using storage.py
   ```

3. **Data Lake Pattern:**
   - Store raw time-series data in Wasabi
   - Process and load into TimescaleDB
   - Keep backups in Wasabi

### Benefits
- ✅ Cost-effective storage for backups
- ✅ S3-compatible API (works with existing code)
- ✅ Can store large datasets
- ✅ Good for data archival

---

## 5. Redis + TimescaleDB

### Compatibility: ✅ **Fully Compatible**

Redis and TimescaleDB work together as complementary services:
- **TimescaleDB:** Long-term time-series storage and queries
- **Redis:** Caching, rate limiting, and real-time data

### Integration Pattern

```python
from redis_client import RedisClientFactory
from file_exporter.database import DatabaseExporter

# Check cache before querying TimescaleDB
redis_client = RedisClientFactory.get_instance()

def get_time_series_data(series_id: str, start_time: str, end_time: str):
    cache_key = f"timeseries:{series_id}:{start_time}:{end_time}"
    
    # Check Redis cache first
    if redis_client:
        cached = redis_client.cache.get(cache_key)
        if cached:
            return cached
    
    # Query TimescaleDB
    # ... query TimescaleDB ...
    result = query_timescaledb(series_id, start_time, end_time)
    
    # Cache result in Redis
    if redis_client:
        redis_client.cache.set(cache_key, result, ttl=3600)
    
    return result
```

### Use Cases
- ✅ Cache frequent queries
- ✅ Rate limiting for TimescaleDB writes
- ✅ Pub/sub for real-time updates
- ✅ Session management

### Benefits
- ✅ Reduces load on TimescaleDB
- ✅ Faster response times for cached queries
- ✅ Your existing Redis infrastructure works as-is
- ✅ Complements TimescaleDB's strengths

---

## Recommended Architecture

### Option 1: Supabase + TimescaleDB (Simplest)
```
VARIOSYNC App (Render)
  ↓
Supabase PostgreSQL (with TimescaleDB extension)
  ↓
Redis (Upstash/Render) - Caching
  ↓
Wasabi - Backups & Exports
```

**Pros:** Single database, simpler architecture, integrated auth  
**Cons:** May require Supabase Pro plan for TimescaleDB

### Option 2: Render TimescaleDB (Dedicated)
```
VARIOSYNC App (Render)
  ↓
TimescaleDB (Render PostgreSQL)
  ↓
Supabase - Auth & Metadata
  ↓
Redis (Upstash/Render) - Caching
  ↓
Wasabi - Backups & Exports
```

**Pros:** Dedicated TimescaleDB instance, full control  
**Cons:** Additional database service to manage

### Option 3: Hybrid (Recommended for Scale)
```
VARIOSYNC App (Render)
  ↓
├── Supabase - Auth, metadata, user data
├── TimescaleDB (Render/Supabase) - Time-series data
├── Redis - Caching & rate limiting
├── Wasabi - Backups & data lake
└── Modal - Heavy processing → TimescaleDB
```

**Pros:** Optimized for each use case, scalable  
**Cons:** More complex, multiple services

---

## Implementation Steps

### 1. Enable TimescaleDB on Supabase
```sql
-- In Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

### 2. Update Environment Variables
Add to `env.example` and `render.yaml`:
```bash
TIMESCALEDB_URL=postgresql://user:pass@host:5432/db
# Or use Supabase connection string
```

### 3. Update Code to Use TimescaleDB
Modify `file_exporter/database.py` to use Supabase connection:
```python
# Get connection from Supabase client
connection_string = f"postgresql://postgres:{password}@{supabase_host}:5432/postgres"
```

### 4. Add Caching Layer
Integrate Redis caching for TimescaleDB queries (already implemented in `redis_client/`)

### 5. Set Up Backups
Configure Wasabi backups for TimescaleDB data

---

## Testing TimescaleDB Integration

### Test Connection
```python
from file_exporter.database import DatabaseExporter

# Test data
test_data = [{
    "timestamp": "2024-01-01T00:00:00Z",
    "series_id": "test-series",
    "measurements": {"temperature": 25.5, "humidity": 60.0},
    "metadata": {"sensor": "test"}
}]

# Export to TimescaleDB
success = DatabaseExporter.export_to_timescaledb(
    data=test_data,
    output_path="test.sql",
    connection_string=os.getenv("TIMESCALEDB_URL"),
    create_hypertable=True
)
```

### Verify Hypertable
```sql
SELECT * FROM timescaledb_information.hypertables;
```

---

## Cost Considerations

| Service | TimescaleDB Cost | Notes |
|---------|-----------------|-------|
| **Supabase** | Included (may require Pro plan) | Check if TimescaleDB extension available on your plan |
| **Render** | $7-25/month (PostgreSQL starter) | Scales with usage |
| **Modal** | Pay-per-use | Only when functions run |
| **Wasabi** | $5.99/TB/month | For backups/exports |
| **Redis** | $0-10/month | Already in use |

---

## Summary

✅ **All services are compatible with TimescaleDB:**
- **Supabase:** Enable TimescaleDB extension on PostgreSQL
- **Render:** Host TimescaleDB as PostgreSQL database
- **Modal:** Connect to external TimescaleDB instances
- **Wasabi:** Store backups and exports
- **Redis:** Cache queries and complement TimescaleDB

**Recommended Approach:** Enable TimescaleDB extension on Supabase PostgreSQL for the simplest integration, or use Render's PostgreSQL service for a dedicated TimescaleDB instance.

Your existing code in `file_exporter/database.py` already supports TimescaleDB exports - you just need to enable the extension and configure the connection string!
