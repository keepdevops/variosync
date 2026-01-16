# VARIOSYNC Docker Deployment Guide

## Quick Start

### Build and Run

```bash
# Build the Docker image
docker build -t variosync:latest .

# Run the container
docker run -p 8000:8000 variosync:latest
```

### Using Docker Compose

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

## Environment Variables

Set these in your `.env` file or docker-compose.yml:

```bash
PORT=8000
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_BUCKET_NAME=your-bucket-name
CORS_ORIGINS=http://localhost:8080,http://localhost:3000
```

## Production Deployment

### Build for Production

```bash
docker build -t variosync:v2.1.0 .
```

### Run with Environment Variables

```bash
docker run -d \
  --name variosync \
  -p 8000:8000 \
  -e PORT=8000 \
  -e SUPABASE_URL=https://your-project.supabase.co \
  -e SUPABASE_KEY=your-key \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config.json:/app/config.json:ro \
  variosync:v2.1.0
```

### Health Check

The container includes a health check:
```bash
docker ps  # Check health status
```

## Volumes

- `/app/data` - Data storage directory
- `/app/config.json` - Configuration file (read-only)
- `/app/variosync.log` - Log file

## Ports

- `8000` - FastAPI web application (configurable via PORT env var)

## Access the Application

Once running:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8000/dashboard
- **Health**: http://localhost:8000/health

## Troubleshooting

### View Logs
```bash
docker logs variosync-app
docker logs -f variosync-app  # Follow logs
```

### Execute Commands in Container
```bash
docker exec -it variosync-app bash
```

### Rebuild After Code Changes
```bash
docker-compose build --no-cache
docker-compose up -d
```
