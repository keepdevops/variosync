# VARIOSYNC Cloud Deployment Guide

Complete guide for deploying VARIOSYNC to production cloud infrastructure.

## Prerequisites

Before deploying, ensure you have accounts for:
1. **Render.com** - Web service hosting
2. **Supabase** - Database, auth, and storage
3. **Wasabi** - Object storage (S3-compatible)
4. **Upstash** (or Render Redis) - Redis caching
5. **Modal.com** - Serverless functions (optional)
6. **Cloudflare** - DNS, CDN, and security (optional)

## Step-by-Step Deployment

### 1. Supabase Setup

#### 1.1 Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Note your project URL and API keys

#### 1.2 Set Up Database Schema
Run the following SQL in Supabase SQL Editor:

```sql
-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    email TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Hour balances table
CREATE TABLE IF NOT EXISTS public.hour_balances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    hours DECIMAL(10, 2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Data sources table
CREATE TABLE IF NOT EXISTS public.data_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    source_type TEXT,
    config JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Settings table
CREATE TABLE IF NOT EXISTS public.settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, key)
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id UUID,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hour_balances ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.data_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- Create policies (example - adjust based on your needs)
CREATE POLICY "Users can view own data"
    ON public.users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own data"
    ON public.users FOR UPDATE
    USING (auth.uid() = id);
```

#### 1.3 Configure Storage Buckets
1. Go to Storage in Supabase dashboard
2. Create bucket: `uploads` (public: false)
3. Create bucket: `exports` (public: false)
4. Set up bucket policies as needed

#### 1.4 Get API Keys
- Project URL: `https://your-project.supabase.co`
- Anon Key: Found in Settings > API
- Service Role Key: Found in Settings > API (keep secret!)

### 2. Wasabi Setup

#### 2.1 Create Wasabi Account
1. Go to [wasabi.com](https://wasabi.com)
2. Create account and select region (e.g., `us-east-1`)

#### 2.2 Create Bucket
1. Create a new bucket (e.g., `variosync-data`)
2. Note the endpoint URL: `https://s3.us-east-1.wasabisys.com`
3. Create access keys in Access Keys section

#### 2.3 Configure Bucket Policies
Set up bucket policy for your application:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::YOUR_ACCOUNT:user/YOUR_USER"
      },
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::variosync-data",
        "arn:aws:s3:::variosync-data/*"
      ]
    }
  ]
}
```

### 3. Redis Setup

#### Option A: Upstash Redis (Recommended)
1. Go to [upstash.com](https://upstash.com)
2. Create Redis database
3. Select region close to your Render.com service
4. Copy connection URL (format: `rediss://default:password@host.upstash.io:6379`)

#### Option B: Render Redis
1. In Render.com dashboard, create new Redis instance
2. Note connection URL from service dashboard

### 4. Modal.com Setup (Optional)

#### 4.1 Create Modal Account
1. Go to [modal.com](https://modal.com)
2. Sign up and install Modal CLI: `pip install modal`
3. Authenticate: `modal token new`

#### 4.2 Create Secrets
Create secrets in Modal dashboard:
- `aws-credentials`: Contains `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ENDPOINT_URL`, `AWS_BUCKET_NAME`
- `supabase-credentials`: Contains `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`

#### 4.3 Deploy Functions
```bash
cd modal_functions
modal deploy ml_inference.py
modal deploy data_processing.py
modal deploy batch_exports.py
```

### 5. Render.com Deployment

#### 5.1 Connect Repository
1. Go to [render.com](https://render.com)
2. Connect your Git repository
3. Render will detect `render.yaml` automatically

#### 5.2 Configure Environment Variables
In Render dashboard, add these environment variables:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Wasabi
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_ENDPOINT_URL=https://s3.us-east-1.wasabisys.com
AWS_BUCKET_NAME=variosync-data

# Redis
REDIS_URL=rediss://default:password@host.upstash.io:6379

# Modal (optional)
MODAL_TOKEN_ID=your-token-id
MODAL_TOKEN_SECRET=your-token-secret

# NiceGUI
NICEGUI_HOST=0.0.0.0
NICEGUI_PORT=8000
NICEGUI_RELOAD=false
```

#### 5.3 Deploy Service
1. Render will automatically deploy from `render.yaml`
2. Monitor deployment logs
3. Service will be available at `https://your-service.onrender.com`

### 6. Cloudflare Setup (Optional)

#### 6.1 Add Domain
1. Go to Cloudflare dashboard
2. Add your domain
3. Update nameservers at your domain registrar

#### 6.2 Configure DNS
1. Create CNAME record: `@` → `your-service.onrender.com`
2. Create CNAME record: `www` → `your-service.onrender.com`

#### 6.3 Enable Features
1. **CDN**: Automatic (enabled by default)
2. **WAF**: Enable in Security > WAF
3. **Rate Limiting**: Configure in Security > Rate Limiting
4. **DDoS Protection**: Automatic (enabled by default)

#### 6.4 SSL/TLS
- Set SSL/TLS mode to "Full" or "Full (strict)"
- Render.com provides SSL certificates automatically

### 7. Post-Deployment Verification

#### 7.1 Test Authentication
1. Visit your deployed URL
2. Try signing up/logging in via Supabase Auth
3. Verify user is created in Supabase dashboard

#### 7.2 Test File Upload
1. Upload a test file via NiceGUI interface
2. Verify file appears in Supabase Storage
3. Check Wasabi bucket for processed files

#### 7.3 Test Redis Caching
1. Perform a query that should be cached
2. Check Redis dashboard for cached keys
3. Verify subsequent queries are faster

#### 7.4 Test Modal Functions (if enabled)
1. Trigger ML inference or data processing
2. Check Modal dashboard for function execution
3. Verify results are stored correctly

### 8. Monitoring Setup

#### 8.1 Render.com Monitoring
- View logs in Render dashboard
- Set up alerts for service failures
- Monitor resource usage

#### 8.2 Supabase Monitoring
- Monitor database performance in Supabase dashboard
- Set up alerts for high connection counts
- Review query performance

#### 8.3 Application Logging
- Application logs are available in Render.com logs
- Configure log aggregation if needed
- Set up error tracking (e.g., Sentry)

## Troubleshooting

### Common Issues

#### Service Won't Start
- Check environment variables are set correctly
- Verify all required dependencies are in `requirements.txt`
- Check Render.com build logs for errors

#### Database Connection Errors
- Verify Supabase URL and keys are correct
- Check Supabase project is active
- Review Supabase connection pool settings

#### Redis Connection Errors
- Verify Redis URL format is correct
- Check Redis instance is running
- Review firewall/network settings

#### Storage Upload Failures
- Verify Wasabi credentials are correct
- Check bucket name and region match
- Review bucket policies and permissions

#### Modal Function Errors
- Verify Modal secrets are configured
- Check function logs in Modal dashboard
- Ensure dependencies are in function image

## Scaling Considerations

### Horizontal Scaling
- Render.com auto-scales based on traffic
- Supabase PostgreSQL scales automatically
- Upstash Redis scales serverlessly
- Modal functions scale on-demand

### Cost Optimization
- Use Wasabi for cost-effective storage
- Enable Redis caching to reduce database load
- Use Modal functions only for heavy processing
- Monitor and optimize resource usage

### Performance Tuning
- Configure Redis TTLs appropriately
- Use connection pooling for Supabase
- Enable CDN for static assets
- Optimize database queries

## Security Checklist

- [ ] All secrets stored as environment variables (not in code)
- [ ] Supabase RLS policies configured
- [ ] Wasabi bucket policies restrict access
- [ ] Redis password protected
- [ ] Cloudflare WAF enabled
- [ ] Rate limiting configured
- [ ] SSL/TLS enabled everywhere
- [ ] Regular security audits scheduled

## Backup and Recovery

### Database Backups
- Supabase provides automatic daily backups
- Configure additional backups if needed
- Test restore procedures regularly

### Storage Backups
- Wasabi provides versioning (enable if needed)
- Set up cross-region replication for critical data
- Regular backup verification

### Configuration Backups
- Version control all configuration files
- Document all environment variables
- Keep secure backup of secrets

## Support Resources

- **Render.com Docs**: https://render.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **Wasabi Docs**: https://wasabi.com/support/docs/
- **Upstash Docs**: https://docs.upstash.com
- **Modal Docs**: https://modal.com/docs
- **Cloudflare Docs**: https://developers.cloudflare.com

## Next Steps

After successful deployment:
1. Set up monitoring and alerts
2. Configure custom domain
3. Enable additional Cloudflare features
4. Set up CI/CD pipeline
5. Configure staging environment
6. Plan for scaling and optimization
