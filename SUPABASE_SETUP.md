# Supabase Database Setup Guide

This guide will help you set up the VARIOSYNC database schema in Supabase.

## Quick Start

1. **Open Supabase SQL Editor**
   - Go to your Supabase project dashboard
   - Navigate to SQL Editor (left sidebar)
   - Click "New Query"

2. **Run the Schema SQL**
   - Open `supabase_schema.sql` file
   - Copy the entire contents
   - Paste into the SQL Editor
   - Click "Run" or press `Ctrl+Enter` (Windows/Linux) or `Cmd+Enter` (Mac)

3. **Verify Tables Created**
   - Go to Table Editor (left sidebar)
   - You should see these tables:
     - `users`
     - `user_hours`
     - `hour_balances`
     - `time_series_data`
     - `data_sources`
     - `settings`
     - `audit_logs`

## Tables Overview

### 1. `users`
Extends Supabase's built-in `auth.users` table with application-specific user data.

**Columns:**
- `id` (UUID, Primary Key) - References `auth.users(id)`
- `email` (TEXT) - User email address
- `created_at` (TIMESTAMP) - Account creation time
- `updated_at` (TIMESTAMP) - Last update time

**Usage:** Stores user profile information linked to Supabase authentication.

---

### 2. `user_hours`
Tracks remaining processing hours for each user (hour-based payment system).

**Columns:**
- `id` (UUID, Primary Key)
- `user_id` (UUID) - References `users(id)`
- `hours_remaining` (DECIMAL) - Remaining processing hours
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**Usage:** 
- Used by `supabase_operations.py` to track user hours
- Automatically initialized when a user signs up (via trigger)
- Updated when hours are consumed or added

**Example Query:**
```sql
-- Get user hours
SELECT hours_remaining FROM user_hours WHERE user_id = 'user-uuid';

-- Add hours to user
UPDATE user_hours SET hours_remaining = hours_remaining + 10.0 WHERE user_id = 'user-uuid';
```

---

### 3. `hour_balances` (Alternative)
Alternative table name for hour tracking (kept for backward compatibility).

**Columns:**
- `id` (UUID, Primary Key)
- `user_id` (UUID) - References `users(id)`
- `hours` (DECIMAL) - Hour balance
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**Note:** The application primarily uses `user_hours` table, but this table is available if needed.

---

### 4. `time_series_data`
Stores time-series data records with flexible measurement schema.

**Columns:**
- `id` (UUID, Primary Key)
- `user_id` (UUID) - References `users(id)`
- `series_id` (TEXT) - Unique identifier for the time-series (e.g., stock ticker, sensor ID)
- `timestamp` (TIMESTAMP WITH TIME ZONE) - Data point timestamp
- `measurements` (JSONB) - Flexible key-value pairs of measurements
- `metadata` (JSONB, Optional) - Additional context
- `format` (TEXT, Optional) - Source format identifier
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**Indexes:**
- Index on `series_id` for fast series lookups
- Index on `timestamp` for time-range queries
- Index on `user_id` for user-specific queries
- Composite index on `(series_id, timestamp)` for efficient time-series queries
- GIN index on `measurements` for JSONB queries

**Usage:**
This is the main table for storing time-series data. The `measurements` column uses JSONB to support flexible schemas.

**Example Data:**
```json
{
  "series_id": "AAPL",
  "timestamp": "2024-01-15T09:30:00Z",
  "measurements": {
    "open": 150.25,
    "high": 151.50,
    "low": 149.80,
    "close": 151.20,
    "volume": 1000000
  },
  "metadata": {
    "source": "yahoo",
    "exchange": "NASDAQ"
  },
  "format": "yahoo"
}
```

**Example Queries:**
```sql
-- Get all data for a series
SELECT * FROM time_series_data 
WHERE series_id = 'AAPL' 
ORDER BY timestamp;

-- Get data in time range
SELECT * FROM time_series_data 
WHERE series_id = 'AAPL' 
  AND timestamp >= '2024-01-01' 
  AND timestamp <= '2024-01-31'
ORDER BY timestamp;

-- Query JSONB measurements
SELECT * FROM time_series_data 
WHERE measurements->>'close' > '150.0';
```

---

### 5. `data_sources`
Stores registered data sources and their configurations.

**Columns:**
- `id` (UUID, Primary Key)
- `user_id` (UUID) - References `users(id)`
- `name` (TEXT) - Data source name
- `source_type` (TEXT) - Type of data source (e.g., "yahoo", "alpha_vantage")
- `config` (JSONB) - Configuration settings
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**Usage:** Stores user-configured data sources (API keys, endpoints, etc.)

**Example Data:**
```json
{
  "name": "Yahoo Finance",
  "source_type": "yahoo",
  "config": {
    "api_key": "optional-key",
    "rate_limit": 100
  }
}
```

---

### 6. `settings`
User preferences and application settings.

**Columns:**
- `id` (UUID, Primary Key)
- `user_id` (UUID) - References `users(id)`
- `key` (TEXT) - Setting key
- `value` (JSONB) - Setting value
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)
- Unique constraint on `(user_id, key)`

**Usage:** Stores user preferences like default formats, display options, etc.

**Example Data:**
```json
{
  "key": "default_export_format",
  "value": "parquet"
}
```

---

### 7. `audit_logs`
Activity tracking and audit trail.

**Columns:**
- `id` (UUID, Primary Key)
- `user_id` (UUID) - References `users(id)`, nullable
- `action` (TEXT) - Action performed
- `resource_type` (TEXT) - Type of resource affected
- `resource_id` (UUID) - ID of resource affected
- `metadata` (JSONB) - Additional context
- `created_at` (TIMESTAMP)

**Usage:** Tracks user actions for auditing and debugging.

**Example Data:**
```json
{
  "action": "data_export",
  "resource_type": "time_series",
  "resource_id": "series-uuid",
  "metadata": {
    "format": "parquet",
    "rows_exported": 1000
  }
}
```

---

## Row Level Security (RLS)

All tables have Row Level Security enabled. This means:
- Users can only access their own data
- Each table has policies that check `auth.uid() = user_id`
- Prevents users from accessing other users' data

### Policy Types

1. **SELECT** - Users can view their own records
2. **INSERT** - Users can create records with their own `user_id`
3. **UPDATE** - Users can update their own records
4. **DELETE** - Users can delete their own records (where applicable)

---

## Automatic Features

### Triggers

1. **Timestamp Updates**
   - `updated_at` columns are automatically updated when records are modified
   - Uses `update_updated_at_column()` function

2. **User Initialization**
   - When a new user signs up via Supabase Auth, the `initialize_user_hours()` function:
     - Creates a record in `users` table
     - Creates a record in `user_hours` table with 0 hours
   - Trigger: `on_auth_user_created`

---

## Storage Buckets Setup

After creating tables, set up storage buckets:

1. Go to **Storage** in Supabase dashboard
2. Create these buckets:
   - `uploads` (Private) - For user file uploads
   - `exports` (Private) - For exported files
   - `processed` (Private) - For processed data files

3. Set bucket policies as needed (users can only access their own files)

---

## Testing the Schema

### Test User Creation
```sql
-- This will be handled automatically by Supabase Auth
-- When a user signs up, check that records are created:
SELECT * FROM users;
SELECT * FROM user_hours;
```

### Test Time Series Data
```sql
-- Insert test data (replace user_id with actual UUID)
INSERT INTO time_series_data (user_id, series_id, timestamp, measurements)
VALUES (
  'your-user-id',
  'TEST',
  NOW(),
  '{"value": 100, "metric": "test"}'::jsonb
);

-- Query test data
SELECT * FROM time_series_data WHERE series_id = 'TEST';
```

### Test Hours Management
```sql
-- Add hours to user
UPDATE user_hours 
SET hours_remaining = hours_remaining + 10.0 
WHERE user_id = 'your-user-id';

-- Check hours
SELECT hours_remaining FROM user_hours WHERE user_id = 'your-user-id';
```

---

## Troubleshooting

### Tables Not Created
- Check SQL Editor for error messages
- Ensure you have proper permissions in Supabase
- Try running sections of the SQL file individually

### RLS Policies Not Working
- Verify RLS is enabled: `ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;`
- Check policies exist: `SELECT * FROM pg_policies WHERE tablename = 'table_name';`
- Ensure user is authenticated when testing

### Triggers Not Firing
- Check trigger exists: `SELECT * FROM pg_trigger WHERE tgname = 'trigger_name';`
- Verify function exists: `SELECT * FROM pg_proc WHERE proname = 'function_name';`
- Test function manually: `SELECT function_name();`

### User Hours Not Initialized
- Check trigger exists on `auth.users` table
- Verify `initialize_user_hours()` function exists
- Check Supabase logs for errors

---

## Next Steps

After setting up the schema:

1. **Configure Environment Variables**
   - Set `SUPABASE_URL` in your application
   - Set `SUPABASE_KEY` (anon key)
   - Set `SUPABASE_SERVICE_ROLE_KEY` (for admin operations)

2. **Test Connection**
   - Use `supabase_client.py` to test connection
   - Verify tables are accessible

3. **Set Up Storage**
   - Create storage buckets
   - Configure bucket policies

4. **Configure Authentication**
   - Set up authentication providers in Supabase
   - Configure email templates if needed

5. **Monitor Usage**
   - Use Supabase dashboard to monitor database usage
   - Set up alerts for high usage

---

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL JSONB Guide](https://www.postgresql.org/docs/current/datatype-json.html)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Supabase Storage Guide](https://supabase.com/docs/guides/storage)

---

## Schema Version

**Version:** 2.1.0  
**Last Updated:** 2024  
**Compatible with:** VARIOSYNC v2.1.0+
