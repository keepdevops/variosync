# VARIOSYNC Docker Hub → Render Deployment Guide

Complete guide for deploying VARIOSYNC to Render using Docker Hub.

## Architecture Overview

```
┌─────────────────┐
│   Docker Hub    │  ← Custom image with dependencies
└────────┬────────┘
         │
         │ Pulls image
         ▼
┌─────────────────┐
│  Render.com     │  ← Hosts NiceGUI frontend
│  (Web Service)  │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼          ▼
┌─────────┐ ┌──────┐ ┌────────┐ ┌────────┐ ┌──────┐
│Supabase │ │Upstash│ │ Wasabi │ │ Modal  │ │Redis │
│(Postgres│ │ Redis │ │  (S3)  │ │(Server-│ │(Alt) │
│ + Auth) │ │       │ │        │ │  less) │ │      │
└─────────┘ └──────┘ └────────┘ └────────┘ └──────┘
```

## Prerequisites

1. **Docker Hub Account** - [hub.docker.com](https://hub.docker.com)
2. **Render Account** - [render.com](https://render.com)
3. **Supabase Project** - [supabase.com](https://supabase.com)
4. **Upstash Redis** - [upstash.com](https://upstash.com) (or Render Redis)
5. **Wasabi Account** - [wasabi.com](https://wasabi.com) (or AWS S3)
6. **Modal Account** - [modal.com](https://modal.com) (optional)

## Step 1: Build and Push Docker Image

### Option A: Multi-stage Production Build (Recommended)

```bash
# Build production image
docker build -f Dockerfile.production -t yourusername/variosync:1.0.0 .

# Tag as latest (optional)
docker tag yourusername/variosync:1.0.0 yourusername/variosync:latest

# Push to Docker Hub
docker push yourusername/variosync:1.0.0
docker push yourusername/variosync:latest
```

### Option B: Official NiceGUI + Code Mount

If you prefer to mount code dynamically:

```bash
# Use official NiceGUI image
# No build needed - Render will mount your code
```

**Note:** Use version tags (`:1.0.0`, `:2026-01`) for production stability. Avoid `:latest` in production.

## Step 2: Configure Supabase

### 2.1 Create Database Schema

1. Go to Supabase Dashboard → SQL Editor
2. Run `supabase_schema.sql` (see `SUPABASE_SETUP.md`)
3. Verify tables are created

### 2.2 Get API Keys

- **Project URL**: `https://your-project.supabase.co`
- **Anon Key**: Settings → API → `anon` `public` key (safe for frontend)
- **Service Role Key**: Settings → API → `service_role` `secret` key (server-only!)

### 2.3 Set Up Storage Buckets

Create these buckets in Supabase Storage:
- `uploads` (Private) - User file uploads
- `exports` (Private) - Exported files
- `processed` (Private) - Processed data files

## Step 3: Configure Upstash Redis

### 3.1 Create Upstash Redis Database

1. Go to [upstash.com](https://upstash.com)
2. Create Redis database
3. Select region close to your Render service
4. Copy connection details:
   - **REST URL**: `https://xxx.upstash.io`
   - **REST Token**: `xxx...`

### 3.2 Alternative: Render Redis

If using Render Redis:
1. Create Redis database in Render dashboard
2. Use `REDIS_URL` instead of Upstash env vars

## Step 4: Configure Wasabi

### 4.1 Create Wasabi Account

1. Go to [wasabi.com](https://wasabi.com)
2. Create account and select region (e.g., `us-east-1`)

### 4.2 Create Bucket

1. Create bucket: `variosync-data` (or your preferred name)
2. Note endpoint: `https://s3.us-east-1.wasabisys.com`
3. Create access keys in Access Keys section

### 4.3 Alternative: AWS S3

If using AWS S3 instead:
- Use `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ENDPOINT_URL`, `AWS_BUCKET_NAME`

## Step 5: Configure Modal (Optional)

### 5.1 Create Modal Account

1. Go to [modal.com](https://modal.com)
2. Sign up and install CLI: `pip install modal`
3. Authenticate: `modal token new`
4. Copy token ID and secret

### 5.2 Deploy Modal Functions

```bash
cd modal_functions
modal deploy ml_inference.py
modal deploy data_processing.py
modal deploy batch_exports.py
```

## Step 6: Deploy to Render

### 6.1 Create Web Service

1. Go to Render Dashboard → **New** → **Web Service**
2. Select **Existing Image**
3. Enter image URL: `docker.io/yourusername/variosync:1.0.0`
   - Or: `zauberzeug/nicegui:latest` (if using Option B)

### 6.2 Configure Service

**Basic Settings:**
- **Name**: `variosync-web`
- **Region**: `Oregon` (or closest to your users)
- **Branch**: `main` (if auto-deploy enabled)
- **Root Directory**: `/` (default)

**Port Configuration:**
- **Port**: `8080` (NiceGUI default)

**Health Check:**
- **Health Check Path**: `/health`

**Plan:**
- **Starter**: $7/month (for testing)
- **Standard**: $25/month (recommended for production)
- **Pro**: $85/month (high traffic)

### 6.3 Set Environment Variables

Add these in Render dashboard:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...           # Public key
SUPABASE_SERVICE_ROLE_KEY=eyJ...   # Private key (server-only!)

# Upstash Redis Configuration
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxx...

# Alternative: Render Redis
REDIS_URL=rediss://default:password@host.upstash.io:6379

# Wasabi Configuration
WASABI_ACCESS_KEY_ID=xxx...
WASABI_SECRET_ACCESS_KEY=xxx...
WASABI_ENDPOINT=https://s3.us-east-1.wasabisys.com
WASABI_BUCKET=variosync-data

# Alternative: AWS S3
AWS_ACCESS_KEY_ID=xxx...
AWS_SECRET_ACCESS_KEY=xxx...
AWS_ENDPOINT_URL=https://s3.us-east-1.amazonaws.com
AWS_BUCKET_NAME=variosync-data

# Modal Configuration (optional)
MODAL_TOKEN_ID=xxx...
MODAL_TOKEN_SECRET=xxx...

# NiceGUI Configuration
PORT=8080
HOST=0.0.0.0
PYTHONUNBUFFERED=1
NICEGUI_RELOAD=false
STORAGE_SECRET=your-random-secret-here  # Generate: openssl rand -hex 32

# Application Configuration
ENVIRONMENT=production
```

### 6.4 Configure Disk (Option B Only)

If using official NiceGUI image + code mount:

1. Go to **Advanced** → **Disks**
2. Add disk:
   - **Name**: `app-code`
   - **Mount Path**: `/app`
   - **Size**: 10 GB

### 6.5 Deploy

1. Click **Create Web Service**
2. Render will pull image from Docker Hub
3. Monitor deployment logs
4. Service will be available at `https://your-service.onrender.com`

## Step 7: Verify Deployment

### 7.1 Test Health Endpoint

```bash
curl https://your-service.onrender.com/health
```

### 7.2 Test Application

1. Visit `https://your-service.onrender.com`
2. Test authentication (Supabase Auth)
3. Test file upload (Supabase Storage)
4. Test data processing

### 7.3 Check Logs

- View logs in Render dashboard
- Check for connection errors
- Verify environment variables are set

## Step 8: Set Up Auto-Deploy (Optional)

### 8.1 Docker Hub Webhook

1. Go to Docker Hub → Your repository → **Webhooks**
2. Add webhook:
   - **Name**: `render-deploy`
   - **Webhook URL**: `https://api.render.com/deploy/srv/xxx?key=xxx`
   - Get deploy key from Render → Service → Manual Deploy

### 8.2 Enable Auto-Deploy

1. In Render dashboard → Service → Settings
2. Enable **Auto-Deploy**
3. Select branch: `main`

Now, when you push a new image tag to Docker Hub, Render will automatically deploy.

## Integration Examples

### Supabase Integration

```python
from supabase import create_client
import os

# Client-side (anon key)
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

# Server-side (service role key - privileged)
admin_supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)
```

### Upstash Redis Integration

```python
from integrations.upstash_client import UpstashRedisFactory

redis = UpstashRedisFactory.create_from_env()

# Rate limiting
async def limited_action():
    allowed, remaining = await redis.rate_limit(
        f"rate:{user_id}",
        limit=10,
        window=60
    )
    if not allowed:
        ui.notify("Rate limit exceeded")
        return
    # Proceed with action
```

### Wasabi Integration

```python
from integrations.wasabi_client import WasabiClientFactory

wasabi = WasabiClientFactory.create_from_env()

# Generate presigned upload URL
upload_url = wasabi.get_upload_url(
    key="user-uploads/file.csv",
    expires_in=3600
)

# In NiceGUI: user uploads directly to Wasabi
ui.button("Upload", on_click=lambda: ui.open(upload_url))
```

### Modal Integration

```python
from integrations.modal_client import ModalClientFactory

modal = ModalClientFactory.create_from_env()

# Trigger heavy processing
async def process_data():
    result = await modal.call_function_async(
        "heavy_process",
        data={"series_id": "AAPL"}
    )
    ui.notify(f"Processing complete: {result}")
```

## Troubleshooting

### Image Not Found

- Verify image name: `docker.io/username/repo:tag`
- Check Docker Hub repository is public (or add credentials)
- Verify tag exists: `docker pull yourusername/variosync:1.0.0`

### Service Won't Start

- Check logs in Render dashboard
- Verify `PORT=8080` is set
- Check health check endpoint exists: `/health`
- Verify all environment variables are set

### Database Connection Errors

- Verify Supabase URL and keys are correct
- Check Supabase project is active
- Review RLS policies (users can only access own data)

### Redis Connection Errors

- Verify Upstash URL and token format
- Check Redis database is active
- Test connection: `curl $UPSTASH_REDIS_REST_URL/ping`

### Wasabi Upload Failures

- Verify credentials are correct
- Check bucket name and region match
- Review bucket policies
- Test with AWS CLI: `aws --endpoint-url=$WASABI_ENDPOINT s3 ls`

### Modal Function Errors

- Verify Modal tokens are set
- Check function is deployed: `modal list`
- Review Modal logs: `modal logs`

## Cost Optimization

### Render

- **Free tier**: Spins down after inactivity (cold starts)
- **Starter**: $7/month (always on, 512MB RAM)
- **Standard**: $25/month (2GB RAM, better performance)

### Upstash Redis

- **Free tier**: 10K commands/day
- **Pay-as-you-go**: $0.20 per 100K commands

### Wasabi

- **Storage**: $5.99/TB/month
- **Egress**: $5.99/TB (first 1TB free)
- Much cheaper than Supabase Storage for bulk data

### Modal

- **Pay-per-use**: Only charged when functions run
- **GPU**: $0.0004/second for GPU instances

## Security Checklist

- [ ] All secrets stored as environment variables (not in code)
- [ ] `SUPABASE_SERVICE_ROLE_KEY` never exposed to frontend
- [ ] RLS policies configured in Supabase
- [ ] Wasabi bucket policies restrict access
- [ ] Redis password protected (Upstash handles this)
- [ ] `STORAGE_SECRET` is random and secure
- [ ] SSL/TLS enabled (Render provides automatically)
- [ ] Rate limiting enabled via Upstash Redis

## Scaling Considerations

### Horizontal Scaling

- Render auto-scales based on traffic
- Multiple instances → Use Upstash Redis for shared state
- NiceGUI WebSockets work across instances with Redis

### Performance

- Enable Redis caching for frequently accessed data
- Use Wasabi for large files (presigned URLs)
- Offload heavy processing to Modal

### Monitoring

- Set up Render alerts for service failures
- Monitor Supabase database performance
- Track Upstash Redis usage
- Review Modal function execution times

## Next Steps

1. **Set up monitoring**: Configure alerts and dashboards
2. **Enable CDN**: Use Cloudflare for static assets
3. **Set up CI/CD**: Automate Docker builds and deployments
4. **Configure backups**: Set up Supabase backups
5. **Load testing**: Test with realistic traffic

## Support Resources

- **Render Docs**: https://render.com/docs
- **Docker Hub Docs**: https://docs.docker.com/docker-hub/
- **Supabase Docs**: https://supabase.com/docs
- **Upstash Docs**: https://docs.upstash.com
- **Wasabi Docs**: https://wasabi.com/support/docs/
- **Modal Docs**: https://modal.com/docs
- **NiceGUI Docs**: https://nicegui.io/documentation
