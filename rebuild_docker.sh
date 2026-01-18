#!/bin/bash
# Rebuild VARIOSYNC Docker image with latest updates

set -e

echo "╔═══════════════════════════════════════════════════════╗"
echo "║     VARIOSYNC Docker Image Rebuild Script            ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker daemon is not running."
    echo "   Please start Docker Desktop or Docker daemon first."
    exit 1
fi

# Get image tag from argument or use default
IMAGE_TAG=${1:-latest}
IMAGE_NAME="variosync:${IMAGE_TAG}"

echo "📦 Building Docker image: ${IMAGE_NAME}"
echo ""

# Stop and remove existing containers if running
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Remove old image if it exists
if docker images -q ${IMAGE_NAME} > /dev/null 2>&1; then
    echo "🗑️  Removing old image..."
    docker rmi ${IMAGE_NAME} 2>/dev/null || true
fi

# Build new image
echo "🔨 Building new image (this may take a few minutes)..."
docker build -t ${IMAGE_NAME} --no-cache .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Image built successfully: ${IMAGE_NAME}"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Start the container:"
    echo "      docker-compose up -d"
    echo ""
    echo "   2. Or run directly:"
    echo "      docker run -p 8000:8000 ${IMAGE_NAME}"
    echo ""
    echo "   3. View logs:"
    echo "      docker-compose logs -f"
    echo ""
else
    echo ""
    echo "❌ Build failed. Check the error messages above."
    exit 1
fi
