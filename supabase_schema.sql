-- ============================================================================
-- VARIOSYNC Supabase Database Schema
-- ============================================================================
-- This file contains all database tables needed for the VARIOSYNC application.
-- Run this SQL in the Supabase SQL Editor to set up your database.
-- ============================================================================

-- ============================================================================
-- 1. USERS TABLE
-- ============================================================================
-- Extends Supabase auth.users with application-specific user data
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 2. USER HOURS TABLE
-- ============================================================================
-- Tracks remaining processing hours for each user (hour-based payment system)
-- Note: Code references this as "user_hours" table
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.user_hours (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    hours_remaining DECIMAL(10, 2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- ============================================================================
-- 3. HOUR BALANCES TABLE (Alternative/Backup)
-- ============================================================================
-- Alternative table name used in some documentation
-- Keeping for backward compatibility
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.hour_balances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    hours DECIMAL(10, 2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- ============================================================================
-- 4. TIME SERIES DATA TABLE
-- ============================================================================
-- Stores time-series data records with flexible measurement schema
-- Supports arbitrary key-value pairs in measurements column
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.time_series_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    series_id TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    measurements JSONB NOT NULL,
    metadata JSONB,
    format TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for time-series queries
CREATE INDEX IF NOT EXISTS idx_time_series_data_series_id ON public.time_series_data(series_id);
CREATE INDEX IF NOT EXISTS idx_time_series_data_timestamp ON public.time_series_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_time_series_data_user_id ON public.time_series_data(user_id);
CREATE INDEX IF NOT EXISTS idx_time_series_data_series_timestamp ON public.time_series_data(series_id, timestamp);

-- GIN index for JSONB measurements column (enables efficient JSON queries)
CREATE INDEX IF NOT EXISTS idx_time_series_data_measurements ON public.time_series_data USING GIN(measurements);

-- ============================================================================
-- 5. DATA SOURCES TABLE
-- ============================================================================
-- Stores registered data sources and their configurations
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.data_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    source_type TEXT,
    config JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_data_sources_user_id ON public.data_sources(user_id);

-- ============================================================================
-- 6. SETTINGS TABLE
-- ============================================================================
-- User preferences and application settings
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, key)
);

CREATE INDEX IF NOT EXISTS idx_settings_user_id ON public.settings(user_id);

-- ============================================================================
-- 7. AUDIT LOGS TABLE
-- ============================================================================
-- Activity tracking and audit trail
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id UUID,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON public.audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at);

-- ============================================================================
-- 8. ROW LEVEL SECURITY (RLS)
-- ============================================================================
-- Enable RLS on all tables for security
-- ============================================================================
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_hours ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hour_balances ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.time_series_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.data_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 9. RLS POLICIES
-- ============================================================================
-- Users can only access their own data
-- ============================================================================

-- Users table policies
DROP POLICY IF EXISTS "Users can view own data" ON public.users;
CREATE POLICY "Users can view own data"
    ON public.users FOR SELECT
    USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own data" ON public.users;
CREATE POLICY "Users can update own data"
    ON public.users FOR UPDATE
    USING (auth.uid() = id);

-- User hours policies
DROP POLICY IF EXISTS "Users can view own hours" ON public.user_hours;
CREATE POLICY "Users can view own hours"
    ON public.user_hours FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own hours" ON public.user_hours;
CREATE POLICY "Users can update own hours"
    ON public.user_hours FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own hours" ON public.user_hours;
CREATE POLICY "Users can insert own hours"
    ON public.user_hours FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Hour balances policies
DROP POLICY IF EXISTS "Users can view own hour balances" ON public.hour_balances;
CREATE POLICY "Users can view own hour balances"
    ON public.hour_balances FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own hour balances" ON public.hour_balances;
CREATE POLICY "Users can update own hour balances"
    ON public.hour_balances FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own hour balances" ON public.hour_balances;
CREATE POLICY "Users can insert own hour balances"
    ON public.hour_balances FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Time series data policies
DROP POLICY IF EXISTS "Users can view own time series data" ON public.time_series_data;
CREATE POLICY "Users can view own time series data"
    ON public.time_series_data FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own time series data" ON public.time_series_data;
CREATE POLICY "Users can insert own time series data"
    ON public.time_series_data FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own time series data" ON public.time_series_data;
CREATE POLICY "Users can update own time series data"
    ON public.time_series_data FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own time series data" ON public.time_series_data;
CREATE POLICY "Users can delete own time series data"
    ON public.time_series_data FOR DELETE
    USING (auth.uid() = user_id);

-- Data sources policies
DROP POLICY IF EXISTS "Users can view own data sources" ON public.data_sources;
CREATE POLICY "Users can view own data sources"
    ON public.data_sources FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own data sources" ON public.data_sources;
CREATE POLICY "Users can insert own data sources"
    ON public.data_sources FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own data sources" ON public.data_sources;
CREATE POLICY "Users can update own data sources"
    ON public.data_sources FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own data sources" ON public.data_sources;
CREATE POLICY "Users can delete own data sources"
    ON public.data_sources FOR DELETE
    USING (auth.uid() = user_id);

-- Settings policies
DROP POLICY IF EXISTS "Users can view own settings" ON public.settings;
CREATE POLICY "Users can view own settings"
    ON public.settings FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own settings" ON public.settings;
CREATE POLICY "Users can insert own settings"
    ON public.settings FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own settings" ON public.settings;
CREATE POLICY "Users can update own settings"
    ON public.settings FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own settings" ON public.settings;
CREATE POLICY "Users can delete own settings"
    ON public.settings FOR DELETE
    USING (auth.uid() = user_id);

-- Audit logs policies (users can view their own logs)
DROP POLICY IF EXISTS "Users can view own audit logs" ON public.audit_logs;
CREATE POLICY "Users can view own audit logs"
    ON public.audit_logs FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own audit logs" ON public.audit_logs;
CREATE POLICY "Users can insert own audit logs"
    ON public.audit_logs FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ============================================================================
-- 10. FUNCTIONS AND TRIGGERS
-- ============================================================================
-- Helper functions for automatic timestamp updates
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at columns
DROP TRIGGER IF EXISTS update_users_updated_at ON public.users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_hours_updated_at ON public.user_hours;
CREATE TRIGGER update_user_hours_updated_at
    BEFORE UPDATE ON public.user_hours
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_hour_balances_updated_at ON public.hour_balances;
CREATE TRIGGER update_hour_balances_updated_at
    BEFORE UPDATE ON public.hour_balances
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_time_series_data_updated_at ON public.time_series_data;
CREATE TRIGGER update_time_series_data_updated_at
    BEFORE UPDATE ON public.time_series_data
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_data_sources_updated_at ON public.data_sources;
CREATE TRIGGER update_data_sources_updated_at
    BEFORE UPDATE ON public.data_sources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_settings_updated_at ON public.settings;
CREATE TRIGGER update_settings_updated_at
    BEFORE UPDATE ON public.settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 11. INITIAL DATA (Optional)
-- ============================================================================
-- You can add initial data here if needed
-- ============================================================================

-- Example: Create a function to initialize user hours when a user signs up
CREATE OR REPLACE FUNCTION initialize_user_hours()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert default hours record for new user
    INSERT INTO public.user_hours (user_id, hours_remaining)
    VALUES (NEW.id, 0.0)
    ON CONFLICT (user_id) DO NOTHING;
    
    -- Also insert into users table
    INSERT INTO public.users (id, email)
    VALUES (NEW.id, NEW.email)
    ON CONFLICT (id) DO UPDATE SET email = NEW.email;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to initialize user hours when auth user is created
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION initialize_user_hours();

-- ============================================================================
-- SCHEMA CREATION COMPLETE
-- ============================================================================
-- All tables, indexes, RLS policies, and triggers have been created.
-- Your VARIOSYNC application is now ready to use these tables.
-- ============================================================================
