# Rebuild Docker Image

## Quick Rebuild

To rebuild the Docker image with all latest updates (including Stooq format support and enhanced .txt file handling):

```bash
./rebuild_docker.sh
```

Or manually:

```bash
# Build the image
docker build -t variosync:latest --no-cache .

# Start with docker-compose
docker-compose up -d --build

# Or run directly
docker run -p 8000:8000 variosync:latest
```

## What's Included in This Build

### New Features:
- ✅ **Stooq Format Support** - Load and export Stooq financial data format (.txt files)
- ✅ **Enhanced .txt File Handling** - Auto-detects delimiters (comma, tab, semicolon, pipe)
- ✅ **Auto-format Detection** - Automatically detects Stooq format in .txt files
- ✅ **Improved Error Handling** - Better error messages for file processing issues
- ✅ **200 Row Preview** - Preview now shows 200 rows instead of 20

### Updated Files:
- `file_formats/stooq.py` - Stooq format loader (219 lines)
- `file_exporter/stooq.py` - Stooq format exporter (106 lines)
- `file_formats/text.py` - Enhanced with auto-delimiter detection (190 lines)
- `file_loader.py` - Added Stooq format support
- `file_exporter/__init__.py` - Added Stooq to supported formats
- `app/core.py` - Improved error handling
- `nicegui_app.py` - Updated preview to 200 rows

## Build Options

### Build with specific tag:
```bash
./rebuild_docker.sh v2.1.0
```

### Build without cache (recommended for clean rebuild):
```bash
docker build -t variosync:latest --no-cache .
```

### Build and start immediately:
```bash
docker-compose up -d --build
```

## Verify the Build

After building, verify the image includes the updates:

```bash
# Check image was created
docker images | grep variosync

# Test the container
docker run --rm variosync:latest python3 -c "
from file_formats.stooq import StooqFormatHandler
from file_exporter.stooq import StooqExporter
from file_exporter import FileExporter
formats = FileExporter.get_supported_formats()
print('✅ Stooq format supported:', 'stooq' in formats)
"
```

## Troubleshooting

### Docker daemon not running:
```bash
# macOS: Start Docker Desktop
# Linux: sudo systemctl start docker
```

### Build fails:
- Check Docker is running: `docker info`
- Check disk space: `docker system df`
- Clean up old images: `docker system prune -a`

### Container won't start:
- Check logs: `docker-compose logs`
- Check port availability: `lsof -i :8000`
- Verify environment variables in `docker-compose.yml`

## Production Deployment

For production, tag with a version:

```bash
docker build -t variosync:v2.1.0 .
docker tag variosync:v2.1.0 variosync:latest
```

Then push to your registry:
```bash
docker tag variosync:v2.1.0 your-registry/variosync:v2.1.0
docker push your-registry/variosync:v2.1.0
```
