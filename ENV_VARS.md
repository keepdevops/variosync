# Environment Variables Reference

Complete list of environment variables used in VARIOSYNC cloud deployment.

## Required Variables

### Supabase Configuration
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key  # Optional, for admin operations
```

### Storage Configuration (Wasabi/S3)
```bash
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_ENDPOINT_URL=https://s3.us-east-1.wasabisys.com  # Wasabi endpoint
AWS_BUCKET_NAME=your-bucket-name
```

### Redis Configuration
```bash
REDIS_URL=redis://localhost:6379/0  # Local development
# Or for Upstash:
REDIS_URL=rediss://default:password@host.upstash.io:6379
# Or for Render Redis:
REDIS_URL=redis://host:port/0
```

### Modal Configuration
```bash
MODAL_TOKEN_ID=your-modal-token-id
MODAL_TOKEN_SECRET=your-modal-token-secret
```

## Optional Variables

### NiceGUI Configuration
```bash
NICEGUI_HOST=0.0.0.0  # Default: 0.0.0.0
NICEGUI_PORT=8000     # Default: 8000
NICEGUI_RELOAD=false  # Default: false (set to true for development)
```

### Application Configuration
```bash
PYTHON_VERSION=3.11.0  # Python version for Render.com
FLASK_ENV=production   # Environment mode
SECRET_KEY=your-secret-key  # For session management (if needed)
```

### Cloudflare Configuration (Optional)
```bash
CLOUDFLARE_API_TOKEN=your-api-token  # For programmatic DNS/CDN management
CLOUDFLARE_ZONE_ID=your-zone-id      # Cloudflare zone ID
```

### Logging Configuration
```bash
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=variosync.log
```

### Feature Flags
```bash
ENABLE_REDIS_CACHE=true      # Enable Redis caching
ENABLE_MODAL_FUNCTIONS=true  # Enable Modal function calls
ENABLE_RATE_LIMITING=true    # Enable rate limiting
REQUIRE_SUPABASE=true        # Require Supabase for operation
ENFORCE_PAYMENT=true         # Enforce hour-based payment system
```

## Render.com Specific

When deploying to Render.com, these variables are automatically available:
- `RENDER_SERVICE_ID`: Unique service identifier
- `RENDER_SERVICE_NAME`: Service name
- `RENDER_SERVICE_TYPE`: Service type (web, worker, etc.)
- `RENDER`: Always set to `true` when running on Render

## Modal.com Specific

Modal functions automatically have access to:
- Secrets configured in Modal dashboard
- Environment variables set in Modal app configuration
- AWS credentials (if configured as secrets)

## Setting Environment Variables

### Local Development
Create a `.env` file in the project root:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
# ... etc
```

Load with:
```bash
export $(cat .env | xargs)
```

### Render.com
1. Go to your service dashboard
2. Navigate to "Environment" tab
3. Add variables manually or sync from `render.yaml`

### Modal.com
1. Go to Modal dashboard
2. Navigate to "Secrets" section
3. Create secrets with required names:
   - `aws-credentials` (contains AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, etc.)
   - `supabase-credentials` (contains SUPABASE_URL, SUPABASE_KEY, etc.)

### Upstash Redis
1. Create Redis database in Upstash dashboard
2. Copy connection URL
3. Set as `REDIS_URL` environment variable

## Security Best Practices

1. **Never commit secrets**: Add `.env` to `.gitignore`
2. **Use environment-specific values**: Different values for dev/staging/prod
3. **Rotate keys regularly**: Especially for production environments
4. **Use least privilege**: Service role keys only where necessary
5. **Monitor access**: Review access logs regularly

## Validation

The application validates required environment variables on startup. Missing required variables will cause startup failures with clear error messages.

## Example .env File

```bash
# Supabase
SUPABASE_URL=https://abc123.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Wasabi Storage
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_ENDPOINT_URL=https://s3.us-east-1.wasabisys.com
AWS_BUCKET_NAME=variosync-data

# Redis (Upstash)
REDIS_URL=rediss://default:password@host.upstash.io:6379

# Modal
MODAL_TOKEN_ID=your-token-id
MODAL_TOKEN_SECRET=your-token-secret

# NiceGUI
NICEGUI_HOST=0.0.0.0
NICEGUI_PORT=8000
NICEGUI_RELOAD=false

# Feature Flags
ENABLE_REDIS_CACHE=true
ENABLE_MODAL_FUNCTIONS=true
ENABLE_RATE_LIMITING=true
```
