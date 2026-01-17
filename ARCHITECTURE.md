# VARIOSYNC Cloud Architecture

## Overview

VARIOSYNC is designed as a cloud-native SaaS application with a scalable, multi-service architecture optimized for production deployment.

## Architecture Diagram

```
NiceGUI Frontend (Python)
  ↓ WebSocket + HTTP
Render.com (Web Service – autoscaling)
  ↓ environment variables / secrets
├── Supabase
│   ├── Auth (email, OAuth, magic links)
│   ├── PostgreSQL (users, data_sources, settings, audit logs)
│   ├── Storage (temporary user uploads)
│   └── Realtime (live updates, presence)
├── Modal Functions
│   ├── ML inference/training (Prophet, LightGBM, TFT)
│   ├── Heavy data processing (large CSV → Parquet conversion)
│   └── Batch exports / background jobs
├── Wasabi (S3-compatible)
│   └── Long-term storage: cleaned datasets, exports, backups
├── Redis (Upstash or Render Redis)
│   └── Cache (recent queries), rate limiting, pub/sub
└── Cloudflare
    ├── DNS
    ├── CDN (static assets)
    ├── WAF & DDoS protection
    └── Rate limiting / bot protection
```

## Component Details

### 1. Frontend: NiceGUI (Python)

**Location**: `nicegui_app.py`, `run_nicegui.py`

**Responsibilities**:
- WebSocket-based real-time UI
- File upload and processing interface
- Time-series and financial data visualization (Plotly)
- User authentication UI
- Dashboard and analytics views

**Deployment**: Runs on Render.com web service

**Dependencies**:
- `nicegui>=1.4.0`
- `plotly>=5.17.0`
- `pandas>=2.0.0`

### 2. Backend: Render.com Web Service

**Configuration**: `render.yaml`

**Features**:
- Auto-scaling based on traffic
- Environment variable management
- Health checks and zero-downtime deployments
- WebSocket support for NiceGUI

**Environment Variables**:
- `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- `REDIS_URL` (Upstash or Render Redis)
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ENDPOINT_URL`, `AWS_BUCKET_NAME`
- `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET`
- `CLOUDFLARE_API_TOKEN` (optional)

### 3. Supabase

**Services Used**:

#### 3.1 Authentication
- **Email/Password**: Standard email authentication
- **OAuth**: Google, GitHub, etc.
- **Magic Links**: Passwordless authentication
- **JWT Tokens**: Secure session management

**Implementation**: `auth.py`, `auth_validator.py`, `supabase_client.py`

#### 3.2 PostgreSQL Database
**Tables**:
- `users`: User accounts and metadata
- `data_sources`: Registered data sources
- `settings`: User preferences
- `audit_logs`: Activity tracking
- `hour_balances`: Hour-based payment system

**Implementation**: `supabase_operations.py`

#### 3.3 Storage
- Temporary file uploads
- User-generated content
- Processed data staging

**Implementation**: Uses Supabase Storage API

#### 3.4 Realtime
- Live data updates
- Presence tracking
- Collaborative features

**Implementation**: Supabase Realtime subscriptions

### 4. Modal Functions

**Purpose**: Serverless functions for compute-intensive tasks

**Functions**:

#### 4.1 ML Inference/Training
- **Prophet**: Time-series forecasting
- **LightGBM**: Gradient boosting for predictions
- **TFT (Temporal Fusion Transformer)**: Deep learning forecasting

**Location**: `modal_functions/ml_inference.py`

#### 4.2 Heavy Data Processing
- Large CSV → Parquet conversion
- Data cleaning and transformation
- Batch processing jobs

**Location**: `modal_functions/data_processing.py`

#### 4.3 Batch Exports
- Generate reports
- Export to various formats
- Background job processing

**Location**: `modal_functions/batch_exports.py`

**Deployment**: Uses Modal.com serverless platform

### 5. Wasabi (S3-compatible Storage)

**Purpose**: Long-term, cost-effective object storage

**Use Cases**:
- Cleaned and processed datasets
- User exports and reports
- System backups
- Archive storage

**Implementation**: `storage_impl.py` (S3Storage class)

**Configuration**:
- Endpoint: `https://s3.{region}.wasabisys.com`
- Bucket: Configured via `AWS_BUCKET_NAME`
- Access via `boto3` with Wasabi endpoint override

### 6. Redis (Upstash/Render Redis)

**Purpose**: Caching and rate limiting

**Use Cases**:
- **Cache**: Recent queries, processed data, API responses
- **Rate Limiting**: Per-user and per-IP rate limits
- **Pub/Sub**: Real-time notifications and updates
- **Session Storage**: Temporary session data

**Implementation**: `redis_client.py` (to be created)

**Providers**:
- **Upstash**: Serverless Redis (recommended for autoscaling)
- **Render Redis**: Managed Redis on Render.com

### 7. Cloudflare

**Services**:

#### 7.1 DNS
- Domain management
- DNS record configuration

#### 7.2 CDN
- Static asset caching
- Global content delivery
- Image optimization

#### 7.3 WAF (Web Application Firewall)
- SQL injection protection
- XSS protection
- DDoS mitigation

#### 7.4 Rate Limiting
- Bot protection
- API rate limiting
- Abuse prevention

**Configuration**: Managed via Cloudflare dashboard or API

## Data Flow

### File Upload Flow
1. User uploads file via NiceGUI frontend
2. File temporarily stored in Supabase Storage
3. Render.com web service processes file metadata
4. For large files: Modal function handles processing
5. Processed data stored in Wasabi
6. Metadata and references stored in Supabase PostgreSQL
7. Results cached in Redis
8. UI updated via WebSocket

### ML Inference Flow
1. User requests forecast/prediction
2. Render.com web service queues job
3. Modal function receives job
4. Function loads data from Wasabi
5. ML model inference/training
6. Results stored in Wasabi
7. Metadata updated in Supabase
8. Results cached in Redis
9. User notified via Supabase Realtime

### Authentication Flow
1. User authenticates via Supabase Auth
2. JWT token issued
3. Token validated on each request
4. User session cached in Redis
5. Hour balance checked from Supabase
6. Access granted/denied based on balance

## Security

### Authentication & Authorization
- Supabase Auth handles all authentication
- JWT tokens for API access
- Row-level security (RLS) in PostgreSQL
- Service role key for admin operations (kept secret)

### Data Protection
- Encryption at rest (Supabase, Wasabi)
- Encryption in transit (TLS/HTTPS)
- Environment variables for secrets
- No secrets in code or config files

### Rate Limiting
- Cloudflare rate limiting at edge
- Redis-based rate limiting per user
- Modal function rate limits

## Scalability

### Horizontal Scaling
- Render.com auto-scales web services
- Modal functions scale automatically
- Redis (Upstash) scales serverlessly
- Supabase scales PostgreSQL automatically

### Caching Strategy
- Redis for hot data (recent queries)
- Cloudflare CDN for static assets
- Supabase connection pooling

### Cost Optimization
- Wasabi for cost-effective storage
- Modal functions only run when needed
- Redis caching reduces database load
- Auto-scaling prevents over-provisioning

## Monitoring & Observability

### Logging
- Application logs: Render.com logs
- Function logs: Modal.com logs
- Database logs: Supabase dashboard
- Error tracking: Integrated logging system

### Metrics
- Render.com metrics dashboard
- Supabase database metrics
- Modal function execution metrics
- Redis performance metrics

### Alerts
- Render.com health checks
- Supabase database alerts
- Modal function error alerts
- Redis connection alerts

## Deployment

### Prerequisites
1. Supabase project created
2. Wasabi account and bucket created
3. Upstash Redis instance (or Render Redis)
4. Modal.com account
5. Cloudflare account
6. Render.com account

### Deployment Steps
1. Configure environment variables in Render.com
2. Deploy web service from `render.yaml`
3. Deploy Modal functions
4. Configure Cloudflare DNS and CDN
5. Set up Supabase database schema
6. Configure Wasabi bucket policies
7. Test authentication flow
8. Monitor initial deployment

See `DEPLOYMENT.md` for detailed deployment instructions.

## Environment Variables Reference

See `ENV_VARS.md` for complete list of required and optional environment variables.

## Cost Estimation

### Monthly Costs (Approximate)
- **Render.com**: $7-25/month (web service, scales with usage)
- **Supabase**: $0-25/month (free tier available, scales with usage)
- **Wasabi**: $5.99/TB/month (storage) + $0.0059/GB egress
- **Upstash Redis**: $0.20/100K commands/month (free tier: 10K commands/day)
- **Modal**: Pay-per-use (typically $0.10-1.00/hour for GPU functions)
- **Cloudflare**: Free tier available, Pro $20/month for advanced features

**Total**: ~$30-100/month for small-medium scale, scales with usage

## Future Enhancements

- [ ] GraphQL API layer
- [ ] Webhook support for external integrations
- [ ] Advanced ML model training pipeline
- [ ] Multi-region deployment
- [ ] Enhanced monitoring and alerting
- [ ] Automated backup and disaster recovery
