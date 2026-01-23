#!/bin/bash
# ============================================================================
# VARIOSYNC Docker Multi-Stage Build and Push Script
# ============================================================================
# Builds production Docker image using multi-stage build and pushes to Docker Hub
#
# Usage:
#   ./build_and_push_docker.sh [version] [dockerhub-username] [options]
#
# Options:
#   --no-push          Build only, don't push to Docker Hub
#   --no-latest        Don't tag/push as :latest
#   --no-cache         Build without cache
#   --platform PLAT    Build for specific platform (linux/amd64, linux/arm64)
#   --multi-platform   Build for multiple platforms (requires buildx)
#
# Examples:
#   ./build_and_push_docker.sh 1.0.0 yourusername
#   ./build_and_push_docker.sh 1.0.0 yourusername --no-push
#   ./build_and_push_docker.sh 1.0.0 yourusername --platform linux/arm64
#   ./build_and_push_docker.sh 1.0.0 yourusername --multi-platform
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
VERSION=""
DOCKERHUB_USERNAME=""
NO_PUSH=false
NO_LATEST=false
NO_CACHE=false
PLATFORM=""
MULTI_PLATFORM=false
DOCKERFILE="Dockerfile.production"
BYTECODE=true

# Parse positional and optional arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-push)
            NO_PUSH=true
            shift
            ;;
        --no-latest)
            NO_LATEST=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --multi-platform)
            MULTI_PLATFORM=true
            shift
            ;;
        --dockerfile)
            DOCKERFILE="$2"
            shift 2
            ;;
        --no-bytecode)
            BYTECODE=false
            shift
            ;;
        *)
            if [ -z "$VERSION" ]; then
                VERSION="$1"
            elif [ -z "$DOCKERHUB_USERNAME" ]; then
                DOCKERHUB_USERNAME="$1"
            fi
            shift
            ;;
    esac
done

# Prompt for missing values
if [ -z "$VERSION" ]; then
    echo -e "${YELLOW}Enter version tag (e.g., 1.0.0):${NC}"
    read VERSION
fi

if [ -z "$DOCKERHUB_USERNAME" ]; then
    echo -e "${YELLOW}Enter Docker Hub username:${NC}"
    read DOCKERHUB_USERNAME
fi

IMAGE_NAME="${DOCKERHUB_USERNAME}/variosync"
IMAGE_TAG="${IMAGE_NAME}:${VERSION}"
IMAGE_LATEST="${IMAGE_NAME}:latest"

# Build cache options
CACHE_OPTS=""
if [ "$NO_CACHE" = true ]; then
    CACHE_OPTS="--no-cache"
    echo -e "${YELLOW}⚠️  Building without cache${NC}"
fi

# Platform options
PLATFORM_OPTS=""
if [ -n "$PLATFORM" ]; then
    PLATFORM_OPTS="--platform ${PLATFORM}"
    echo -e "${BLUE}📱 Building for platform: ${PLATFORM}${NC}"
fi

# Multi-platform build
if [ "$MULTI_PLATFORM" = true ]; then
    PLATFORM_OPTS="--platform linux/amd64,linux/arm64"
    echo -e "${BLUE}📱 Building for multiple platforms${NC}"
    
    # Check if buildx is available
    if ! docker buildx version > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker buildx not available. Install Docker Buildx for multi-platform builds.${NC}"
        exit 1
    fi
    
    # Create builder if it doesn't exist
    if ! docker buildx ls | grep -q "multiarch"; then
        echo "🔧 Creating buildx builder..."
        docker buildx create --name multiarch --use --bootstrap || true
    fi
    
    docker buildx use multiarch
fi

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║     VARIOSYNC Docker Multi-Stage Build               ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo "📦 Image: ${IMAGE_TAG}"
if [ "$NO_LATEST" = false ]; then
    echo "🏷️  Latest: ${IMAGE_LATEST}"
fi
echo "📄 Dockerfile: ${DOCKERFILE}"
if [ "$BYTECODE" = true ]; then
    echo -e "${BLUE}🔧 Bytecode compilation: Enabled${NC}"
else
    echo -e "${YELLOW}⚠️  Bytecode compilation: Disabled${NC}"
fi
if [ "$NO_PUSH" = true ]; then
    echo -e "${YELLOW}⚠️  Build only mode (no push)${NC}"
fi
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker daemon is not running.${NC}"
    echo "   Please start Docker Desktop or Docker daemon first."
    exit 1
fi

# Check if logged into Docker Hub (only if pushing)
if [ "$NO_PUSH" = false ]; then
    if ! docker info 2>/dev/null | grep -q "Username"; then
        echo -e "${YELLOW}⚠️  Not logged into Docker Hub.${NC}"
        echo "   Logging in..."
        docker login
    fi
fi

# Check if Dockerfile exists
if [ ! -f "$DOCKERFILE" ]; then
    echo -e "${RED}❌ Dockerfile not found: ${DOCKERFILE}${NC}"
    exit 1
fi

# Build production image (multi-stage)
echo "🔨 Building production image (multi-stage)..."
echo -e "${BLUE}   Stage 1: Builder (installing dependencies)${NC}"
echo -e "${BLUE}   Stage 2: Final (copying packages + app code)${NC}"
echo ""

# Show build stages
echo "🔨 Building production image (multi-stage)..."
echo -e "${BLUE}   Stage 1: Builder (installing dependencies)${NC}"
if [ "$BYTECODE" = true ]; then
    echo -e "${BLUE}   Stage 2: Bytecode Compiler (compiling Python code)${NC}"
    echo -e "${BLUE}   Stage 3: Final (copying packages + compiled bytecode)${NC}"
else
    echo -e "${BLUE}   Stage 2: Final (copying packages + app code)${NC}"
fi
echo ""

if [ "$MULTI_PLATFORM" = true ]; then
    # Multi-platform build with buildx
    BUILD_CMD="docker buildx build ${PLATFORM_OPTS} ${CACHE_OPTS} -f ${DOCKERFILE} -t ${IMAGE_TAG}"
    
    if [ "$NO_LATEST" = false ]; then
        BUILD_CMD="${BUILD_CMD} -t ${IMAGE_LATEST}"
    fi
    
    if [ "$NO_PUSH" = false ]; then
        BUILD_CMD="${BUILD_CMD} --push"
    else
        BUILD_CMD="${BUILD_CMD} --load"
    fi
    
    BUILD_CMD="${BUILD_CMD} ."
    
    eval $BUILD_CMD
else
    # Single platform build
    BUILD_CMD="docker build ${PLATFORM_OPTS} ${CACHE_OPTS} -f ${DOCKERFILE} -t ${IMAGE_TAG} ."
    
    eval $BUILD_CMD
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Build failed!${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Build successful!${NC}"
    
    # Tag as latest (if not disabled)
    if [ "$NO_LATEST" = false ]; then
        echo "🏷️  Tagging as latest..."
        docker tag ${IMAGE_TAG} ${IMAGE_LATEST}
    fi
    
    # Push to Docker Hub (if not disabled)
    if [ "$NO_PUSH" = false ]; then
        echo "📤 Pushing version tag..."
        docker push ${IMAGE_TAG}
        
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Push failed!${NC}"
            exit 1
        fi
        
        if [ "$NO_LATEST" = false ]; then
            echo "📤 Pushing latest tag..."
            docker push ${IMAGE_LATEST}
            
            if [ $? -ne 0 ]; then
                echo -e "${RED}❌ Push failed!${NC}"
                exit 1
            fi
        fi
    fi
fi

# Show image info
echo ""
if [ "$NO_PUSH" = false ]; then
    echo -e "${GREEN}✅ Successfully pushed to Docker Hub!${NC}"
else
    echo -e "${GREEN}✅ Build completed successfully!${NC}"
fi

echo ""
echo "📊 Image Information:"
docker images ${IMAGE_TAG} --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

echo ""
if [ "$NO_PUSH" = false ]; then
    echo "📋 Next steps:"
    echo "   1. Go to Render dashboard"
    echo "   2. Update service to use: docker.io/${IMAGE_TAG}"
    echo "   3. Or enable auto-deploy with webhook"
    echo ""
    echo "🔗 Image URL: https://hub.docker.com/r/${DOCKERHUB_USERNAME}/variosync"
else
    echo "📋 Next steps:"
    echo "   1. Test the image locally:"
    echo "      docker run -p 8080:8080 ${IMAGE_TAG}"
    echo "   2. When ready, push with:"
    echo "      docker push ${IMAGE_TAG}"
    if [ "$NO_LATEST" = false ]; then
        echo "      docker push ${IMAGE_LATEST}"
    fi
fi
echo ""
