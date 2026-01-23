# VARIOSYNC Docker Multi-Stage Build Guide

Complete guide for building and pushing VARIOSYNC Docker images to Docker Hub.

## 🚀 Quick Start

### Bash Script (Recommended)
```bash
./build_and_push_docker.sh 1.0.0 yourusername
```

### Python Script (Cross-platform)
```bash
python3 docker_build.py 1.0.0 yourusername
```

## 📋 Available Scripts

### 1. `build_and_push_docker.sh` (Bash)
Enhanced bash script with multi-stage build support.

**Features:**
- ✅ Multi-stage build optimization
- ✅ Build cache control
- ✅ Platform-specific builds
- ✅ Multi-platform builds (buildx)
- ✅ Build-only mode (no push)
- ✅ Skip latest tag option

### 2. `docker_build.py` (Python)
Cross-platform Python script with same features.

**Advantages:**
- Works on Windows, macOS, Linux
- Better error handling
- More structured output

## 🎯 Usage Examples

### Basic Build and Push
```bash
# Build version 1.0.0 and push to Docker Hub
./build_and_push_docker.sh 1.0.0 yourusername
```

### Build Only (No Push)
```bash
# Build locally without pushing
./build_and_push_docker.sh 1.0.0 yourusername --no-push
```

### Build Without Cache
```bash
# Fresh build without using cache
./build_and_push_docker.sh 1.0.0 yourusername --no-cache
```

### Build for Specific Platform
```bash
# Build for ARM64 (Apple Silicon, Raspberry Pi)
./build_and_push_docker.sh 1.0.0 yourusername --platform linux/arm64

# Build for AMD64 (Intel/AMD)
./build_and_push_docker.sh 1.0.0 yourusername --platform linux/amd64
```

### Multi-Platform Build
```bash
# Build for both AMD64 and ARM64 (requires Docker buildx)
./build_and_push_docker.sh 1.0.0 yourusername --multi-platform
```

### Skip Latest Tag
```bash
# Don't tag/push as :latest (useful for testing)
./build_and_push_docker.sh 1.0.0 yourusername --no-latest
```

### Custom Dockerfile
```bash
# Use a different Dockerfile
./build_and_push_docker.sh 1.0.0 yourusername --dockerfile Dockerfile.custom
```

## 🔧 Multi-Stage Build Process

The build uses a **two-stage** process:

### Stage 1: Builder
```dockerfile
FROM python:3.12-slim AS builder
# Installs all Python dependencies
# Compiles native extensions
# Creates optimized package cache
```

### Stage 2: Final
```dockerfile
FROM zauberzeug/nicegui:latest
# Copies only compiled packages from builder
# Copies application code
# Results in smaller final image
```

**Benefits:**
- ✅ Smaller final image (no build tools)
- ✅ Faster builds (cached dependencies)
- ✅ Better security (fewer packages)
- ✅ Optimized for production

## 📊 Build Options

| Option | Description | Example |
|--------|-------------|---------|
| `--no-push` | Build only, don't push | `--no-push` |
| `--no-latest` | Skip :latest tag | `--no-latest` |
| `--no-cache` | Build without cache | `--no-cache` |
| `--platform PLAT` | Build for platform | `--platform linux/arm64` |
| `--multi-platform` | Build for multiple platforms | `--multi-platform` |
| `--dockerfile FILE` | Use custom Dockerfile | `--dockerfile Dockerfile.custom` |

## 🐳 Docker Hub Setup

### 1. Create Docker Hub Account
- Go to [hub.docker.com](https://hub.docker.com)
- Sign up for free account

### 2. Create Repository
- Click **Create Repository**
- Name: `variosync`
- Visibility: **Public** (or Private)
- Click **Create**

### 3. Login
```bash
docker login
# Enter your Docker Hub username and password
```

## 🔍 Troubleshooting

### Docker Not Running
```bash
# Check Docker status
docker info

# Start Docker Desktop (macOS/Windows)
# Or: sudo systemctl start docker (Linux)
```

### Buildx Not Available
```bash
# Install Docker Buildx (if needed)
# Usually included with Docker Desktop

# Check version
docker buildx version

# Create builder
docker buildx create --name multiarch --use
```

### Authentication Failed
```bash
# Re-login to Docker Hub
docker logout
docker login

# Or use access token
echo "YOUR_TOKEN" | docker login --username YOUR_USERNAME --password-stdin
```

### Build Fails
```bash
# Check Dockerfile exists
ls -la Dockerfile.production

# Check for syntax errors
docker build -f Dockerfile.production --dry-run .

# Build with verbose output
docker build -f Dockerfile.production -t test . --progress=plain
```

### Push Fails
```bash
# Verify you're logged in
docker info | grep Username

# Check image exists locally
docker images | grep variosync

# Try pushing manually
docker push yourusername/variosync:1.0.0
```

## 📈 Build Performance Tips

### Use Build Cache
```bash
# Default: Uses cache (faster rebuilds)
./build_and_push_docker.sh 1.0.0 yourusername

# Only use --no-cache when needed
./build_and_push_docker.sh 1.0.0 yourusername --no-cache
```

### Optimize Dockerfile Order
The Dockerfile is already optimized:
1. Copy `requirements.txt` first (cached)
2. Install dependencies (cached if requirements.txt unchanged)
3. Copy application code last (changes frequently)

### Multi-Platform Builds
```bash
# Build for both platforms (slower but universal)
./build_and_push_docker.sh 1.0.0 yourusername --multi-platform

# Or build separately for each platform
./build_and_push_docker.sh 1.0.0 yourusername --platform linux/amd64
./build_and_push_docker.sh 1.0.0 yourusername --platform linux/arm64
```

## 🔐 Security Best Practices

### 1. Use Version Tags
```bash
# ✅ Good: Specific version
docker.io/yourusername/variosync:1.0.0

# ❌ Avoid: Latest tag in production
docker.io/yourusername/variosync:latest
```

### 2. Scan Images
```bash
# Scan for vulnerabilities (requires Docker Desktop)
docker scan yourusername/variosync:1.0.0
```

### 3. Use Private Repositories
- Create private repository for sensitive images
- Use Docker Hub access tokens instead of passwords

### 4. Minimize Image Size
- Multi-stage builds already optimize this
- Check image size: `docker images yourusername/variosync`

## 📝 Version Tagging Strategy

### Semantic Versioning
```bash
# Major.Minor.Patch
./build_and_push_docker.sh 1.0.0 yourusername  # Release
./build_and_push_docker.sh 1.0.1 yourusername  # Patch
./build_and_push_docker.sh 1.1.0 yourusername  # Minor
./build_and_push_docker.sh 2.0.0 yourusername  # Major
```

### Date-Based Tags
```bash
# YYYY-MM-DD format
./build_and_push_docker.sh 2026-01-15 yourusername
```

### Git Commit Tags
```bash
# Use git commit hash
VERSION=$(git rev-parse --short HEAD)
./build_and_push_docker.sh ${VERSION} yourusername
```

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
name: Build and Push Docker Image

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - name: Build and push
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          ./build_and_push_docker.sh ${VERSION} ${{ secrets.DOCKERHUB_USERNAME }}
```

## 📊 Image Size Comparison

| Build Type | Size | Notes |
|------------|------|-------|
| Single-stage | ~1.8GB | Includes build tools |
| Multi-stage | ~1.6GB | Optimized, no build tools |
| Multi-stage + Alpine | ~800MB | Smaller but may have compatibility issues |

Current setup uses multi-stage with `python:3.12-slim` base.

## 🔗 Related Files

- `Dockerfile.production` - Multi-stage production Dockerfile
- `build_and_push_docker.sh` - Bash build script
- `docker_build.py` - Python build script
- `DEPLOYMENT_DOCKER_HUB.md` - Complete deployment guide

## 📚 Additional Resources

- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Buildx](https://docs.docker.com/build/buildx/)
- [Docker Hub Documentation](https://docs.docker.com/docker-hub/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

## 🆘 Need Help?

1. Check build logs for errors
2. Verify Docker is running: `docker info`
3. Test Dockerfile locally: `docker build -f Dockerfile.production -t test .`
4. Review Docker Hub repository settings
5. Check Docker Hub quotas (free tier limits)

---

**Ready to build?** Run: `./build_and_push_docker.sh 1.0.0 yourusername`
