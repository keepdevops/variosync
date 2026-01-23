# VARIOSYNC Deployment Quick Reference

## 🚀 Quick Deploy Checklist

### 1. Build & Push Docker Image
```bash
./build_and_push_docker.sh 1.0.0 yourusername
```

### 2. Render Configuration
- **Image**: `docker.io/yourusername/variosync:1.0.0`
- **Port**: `8080`
- **Health Check**: `/health`

### 3. Required Environment Variables

```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Upstash Redis
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxx...

# Wasabi
WASABI_ACCESS_KEY_ID=xxx...
WASABI_SECRET_ACCESS_KEY=xxx...
WASABI_ENDPOINT=https://s3.us-east-1.wasabisys.com
WASABI_BUCKET=variosync-data

# NiceGUI
PORT=8080
HOST=0.0.0.0
NICEGUI_RELOAD=false
STORAGE_SECRET=$(openssl rand -hex 32)
```

## 📁 File Structure

```
variosync/
├── Dockerfile.production      # Multi-stage production build
├── render.docker.yaml          # Render deployment config
├── build_and_push_docker.sh   # Build & push script
├── integrations/
│   ├── upstash_client.py      # Upstash Redis client
│   ├── wasabi_client.py       # Wasabi S3 client
│   └── modal_client.py        # Modal serverless client
└── supabase_schema.sql         # Database schema
```

## 🔗 Integration Usage

### Supabase
```python
from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
```

### Upstash Redis
```python
from integrations.upstash_client import UpstashRedisFactory
redis = UpstashRedisFactory.create_from_env()
allowed, remaining = await redis.rate_limit("key", limit=10, window=60)
```

### Wasabi
```python
from integrations.wasabi_client import WasabiClientFactory
wasabi = WasabiClientFactory.create_from_env()
url = wasabi.get_upload_url("file.csv", expires_in=3600)
```

### Modal
```python
from integrations.modal_client import ModalClientFactory
modal = ModalClientFactory.create_from_env()
result = await modal.call_function_async("function_name", data={})
```

## 🐳 Docker Commands

```bash
# Build
docker build -f Dockerfile.production -t username/variosync:1.0.0 .

# Push
docker push username/variosync:1.0.0

# Test locally
docker run -p 8080:8080 \
  -e SUPABASE_URL=xxx \
  -e SUPABASE_ANON_KEY=xxx \
  username/variosync:1.0.0
```

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Image not found | Check Docker Hub URL format: `docker.io/username/repo:tag` |
| Port error | Set `PORT=8080` in environment variables |
| Connection errors | Verify all env vars are set in Render dashboard |
| Rate limit | Check Upstash Redis URL and token |
| Upload fails | Verify Wasabi credentials and bucket name |

## 📚 Documentation

- **Full Guide**: `DEPLOYMENT_DOCKER_HUB.md`
- **Supabase Setup**: `SUPABASE_SETUP.md`
- **Quick Start**: `SUPABASE_QUICK_START.md`
- **Example Usage**: `integrations/example_usage.py`

## 🆘 Support

- Render: https://render.com/docs
- Supabase: https://supabase.com/docs
- Upstash: https://docs.upstash.com
- Wasabi: https://wasabi.com/support/docs/
- Modal: https://modal.com/docs
