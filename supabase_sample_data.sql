-- ============================================================================
-- VARIOSYNC Supabase Sample Data
-- ============================================================================
-- This file contains sample data for testing the VARIOSYNC application.
-- Run this AFTER running supabase_schema.sql
-- 
-- NOTE: Replace 'your-user-id' with an actual user UUID from auth.users
-- ============================================================================

-- ============================================================================
-- SAMPLE DATA INSERTION
-- ============================================================================

-- First, get a user ID from auth.users (or create a test user)
-- Replace 'your-user-id' with actual UUID from: SELECT id FROM auth.users LIMIT 1;

-- ============================================================================
-- 1. Initialize User Hours (if not already done by trigger)
-- ============================================================================
-- Uncomment and replace 'your-user-id' with actual UUID
/*
INSERT INTO public.user_hours (user_id, hours_remaining)
VALUES ('your-user-id', 10.0)
ON CONFLICT (user_id) DO UPDATE SET hours_remaining = 10.0;
*/

-- ============================================================================
-- 2. Sample Time Series Data
-- ============================================================================
-- Financial data example (AAPL stock)
/*
INSERT INTO public.time_series_data (user_id, series_id, timestamp, measurements, metadata, format)
VALUES 
  ('your-user-id', 'AAPL', '2024-01-15T09:30:00Z', 
   '{"open": 150.25, "high": 151.50, "low": 149.80, "close": 151.20, "volume": 1000000}'::jsonb,
   '{"source": "yahoo", "exchange": "NASDAQ"}'::jsonb,
   'yahoo'),
  ('your-user-id', 'AAPL', '2024-01-15T10:00:00Z',
   '{"open": 151.20, "high": 152.00, "low": 150.90, "close": 151.75, "volume": 850000}'::jsonb,
   '{"source": "yahoo", "exchange": "NASDAQ"}'::jsonb,
   'yahoo'),
  ('your-user-id', 'AAPL', '2024-01-15T10:30:00Z',
   '{"open": 151.75, "high": 152.50, "low": 151.50, "close": 152.30, "volume": 920000}'::jsonb,
   '{"source": "yahoo", "exchange": "NASDAQ"}'::jsonb,
   'yahoo');
*/

-- IoT sensor data example
/*
INSERT INTO public.time_series_data (user_id, series_id, timestamp, measurements, metadata, format)
VALUES 
  ('your-user-id', 'TEMP-001', '2024-01-15T09:00:00Z',
   '{"temperature": 22.5, "humidity": 45.0, "pressure": 1013.25}'::jsonb,
   '{"location": "office", "unit": "celsius"}'::jsonb,
   'csv'),
  ('your-user-id', 'TEMP-001', '2024-01-15T10:00:00Z',
   '{"temperature": 23.1, "humidity": 46.2, "pressure": 1013.30}'::jsonb,
   '{"location": "office", "unit": "celsius"}'::jsonb,
   'csv'),
  ('your-user-id', 'TEMP-001', '2024-01-15T11:00:00Z',
   '{"temperature": 23.8, "humidity": 47.5, "pressure": 1013.20}'::jsonb,
   '{"location": "office", "unit": "celsius"}'::jsonb,
   'csv');
*/

-- Website analytics example
/*
INSERT INTO public.time_series_data (user_id, series_id, timestamp, measurements, metadata, format)
VALUES 
  ('your-user-id', 'example.com', '2024-01-15T00:00:00Z',
   '{"visitors": 1250, "pageviews": 3420, "bounce_rate": 0.35, "avg_session_duration": 180}'::jsonb,
   '{"source": "google_analytics"}'::jsonb,
   'json'),
  ('your-user-id', 'example.com', '2024-01-15T01:00:00Z',
   '{"visitors": 980, "pageviews": 2450, "bounce_rate": 0.32, "avg_session_duration": 195}'::jsonb,
   '{"source": "google_analytics"}'::jsonb,
   'json');
*/

-- ============================================================================
-- 3. Sample Data Sources
-- ============================================================================
/*
INSERT INTO public.data_sources (user_id, name, source_type, config)
VALUES 
  ('your-user-id', 'Yahoo Finance', 'yahoo',
   '{"api_key": "optional", "rate_limit": 100, "timeout": 30}'::jsonb),
  ('your-user-id', 'Alpha Vantage', 'alpha_vantage',
   '{"api_key": "demo", "rate_limit": 5, "premium": false}'::jsonb),
  ('your-user-id', 'Finnhub', 'finnhub',
   '{"api_key": "demo", "rate_limit": 60}'::jsonb);
*/

-- ============================================================================
-- 4. Sample Settings
-- ============================================================================
/*
INSERT INTO public.settings (user_id, key, value)
VALUES 
  ('your-user-id', 'default_export_format', '"parquet"'::jsonb),
  ('your-user-id', 'default_timezone', '"UTC"'::jsonb),
  ('your-user-id', 'preview_rows', '200'::jsonb),
  ('your-user-id', 'theme', '"dark"'::jsonb)
ON CONFLICT (user_id, key) DO UPDATE SET value = EXCLUDED.value;
*/

-- ============================================================================
-- 5. Sample Audit Logs
-- ============================================================================
/*
INSERT INTO public.audit_logs (user_id, action, resource_type, resource_id, metadata)
VALUES 
  ('your-user-id', 'data_upload', 'file', gen_random_uuid(),
   '{"filename": "test.csv", "size": 1024000, "format": "csv"}'::jsonb),
  ('your-user-id', 'data_export', 'time_series', gen_random_uuid(),
   '{"format": "parquet", "rows_exported": 1000, "series_id": "AAPL"}'::jsonb),
  ('your-user-id', 'hours_consumed', 'user_hours', gen_random_uuid(),
   '{"hours_used": 0.5, "operation": "data_processing"}'::jsonb);
*/

-- ============================================================================
-- QUERY EXAMPLES
-- ============================================================================

-- Get all time series for a user
-- SELECT * FROM time_series_data WHERE user_id = 'your-user-id' ORDER BY timestamp DESC LIMIT 10;

-- Get all unique series IDs for a user
-- SELECT DISTINCT series_id FROM time_series_data WHERE user_id = 'your-user-id';

-- Get time series data for a specific series in a date range
-- SELECT * FROM time_series_data 
-- WHERE user_id = 'your-user-id' 
--   AND series_id = 'AAPL'
--   AND timestamp >= '2024-01-15' 
--   AND timestamp < '2024-01-16'
-- ORDER BY timestamp;

-- Query JSONB measurements (get all records where close > 150)
-- SELECT * FROM time_series_data 
-- WHERE user_id = 'your-user-id'
--   AND series_id = 'AAPL'
--   AND (measurements->>'close')::numeric > 150.0
-- ORDER BY timestamp;

-- Get user hours
-- SELECT hours_remaining FROM user_hours WHERE user_id = 'your-user-id';

-- Get user settings
-- SELECT key, value FROM settings WHERE user_id = 'your-user-id';

-- Get audit logs for a user
-- SELECT * FROM audit_logs WHERE user_id = 'your-user-id' ORDER BY created_at DESC LIMIT 10;

-- ============================================================================
-- CLEANUP (if needed)
-- ============================================================================
-- Uncomment to delete sample data (be careful!)
/*
DELETE FROM audit_logs WHERE user_id = 'your-user-id';
DELETE FROM settings WHERE user_id = 'your-user-id';
DELETE FROM data_sources WHERE user_id = 'your-user-id';
DELETE FROM time_series_data WHERE user_id = 'your-user-id';
DELETE FROM user_hours WHERE user_id = 'your-user-id';
*/
