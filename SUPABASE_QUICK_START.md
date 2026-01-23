# Supabase Quick Start Guide

## 🚀 Setup in 3 Steps

### Step 1: Run Schema SQL
1. Open Supabase Dashboard → SQL Editor
2. Copy contents of `supabase_schema.sql`
3. Paste and Run (Ctrl/Cmd + Enter)

### Step 2: Verify Tables
Go to Table Editor and verify these tables exist:
- ✅ `users`
- ✅ `user_hours`
- ✅ `time_series_data`
- ✅ `data_sources`
- ✅ `settings`
- ✅ `audit_logs`

### Step 3: Set Up Storage Buckets
Go to Storage and create:
- `uploads` (Private)
- `exports` (Private)
- `processed` (Private)

## 📊 Tables Summary

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `users` | User profiles | `id`, `email` |
| `user_hours` | Hour tracking | `user_id`, `hours_remaining` |
| `time_series_data` | Time-series data | `series_id`, `timestamp`, `measurements` (JSONB) |
| `data_sources` | Data source configs | `name`, `source_type`, `config` (JSONB) |
| `settings` | User preferences | `key`, `value` (JSONB) |
| `audit_logs` | Activity logs | `action`, `resource_type`, `metadata` (JSONB) |

## 🔐 Security

- ✅ Row Level Security (RLS) enabled on all tables
- ✅ Users can only access their own data
- ✅ Automatic user initialization on signup

## 📝 Next Steps

1. **Get User ID**: After a user signs up, get their UUID:
   ```sql
   SELECT id FROM auth.users LIMIT 1;
   ```

2. **Add Sample Data** (optional):
   - Open `supabase_sample_data.sql`
   - Replace `'your-user-id'` with actual UUID
   - Run the INSERT statements

3. **Test Connection**:
   ```python
   from supabase_client import SupabaseClientFactory
   client = SupabaseClientFactory.create_from_env()
   client.test_connection()
   ```

## 🔗 Files Created

- `supabase_schema.sql` - Complete database schema
- `supabase_sample_data.sql` - Sample data for testing
- `SUPABASE_SETUP.md` - Detailed documentation
- `SUPABASE_QUICK_START.md` - This file

## ⚠️ Important Notes

- The application uses `user_hours` table (not `hour_balances`)
- `time_series_data.measurements` is JSONB for flexibility
- All timestamps use `TIMESTAMP WITH TIME ZONE`
- RLS policies prevent cross-user data access

## 🆘 Troubleshooting

**Tables not created?**
- Check SQL Editor for errors
- Ensure you have proper permissions

**RLS blocking queries?**
- Verify user is authenticated
- Check `auth.uid()` matches `user_id`

**Need help?**
- See `SUPABASE_SETUP.md` for detailed docs
- Check Supabase logs in dashboard
