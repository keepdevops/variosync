#!/bin/bash
# ============================================================================
# VARIOSYNC Bytecode Compilation Script
# ============================================================================
# Pre-compiles Python bytecode for faster startup and better performance
# Can be run locally before building Docker image
#
# Usage:
#   ./compile_bytecode.sh [options]
#
# Options:
#   --optimize LEVEL    Optimization level (0, 1, or 2)
#   --remove-source     Remove .py files after compilation (bytecode-only)
#   --platform PLAT     Compile for specific platform (for testing)
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

OPTIMIZE=1
REMOVE_SOURCE=false
PLATFORM=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --optimize)
            OPTIMIZE="$2"
            shift 2
            ;;
        --remove-source)
            REMOVE_SOURCE=true
            shift
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║     VARIOSYNC Bytecode Compilation                   ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo -e "${BLUE}🔧 Optimization level: ${OPTIMIZE}${NC}"
if [ "$REMOVE_SOURCE" = true ]; then
    echo -e "${YELLOW}⚠️  Will remove source files after compilation${NC}"
fi
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "🐍 Python version: ${PYTHON_VERSION}"

# Compile bytecode
echo ""
echo "🔨 Compiling Python bytecode..."

# Use compileall with optimization
if [ "$OPTIMIZE" = "0" ]; then
    python3 -m compileall -f -q .
elif [ "$OPTIMIZE" = "1" ]; then
    python3 -m compileall -f -q -O .
elif [ "$OPTIMIZE" = "2" ]; then
    python3 -m compileall -f -q -OO .
else
    echo -e "${YELLOW}⚠️  Invalid optimization level, using 1${NC}"
    python3 -m compileall -f -q -O .
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Bytecode compilation successful!${NC}"
else
    echo -e "${YELLOW}⚠️  Some files may have compilation warnings${NC}"
fi

# Count compiled files
PYC_COUNT=$(find . -type f -name "*.pyc" -o -name "*.pyo" | wc -l | tr -d ' ')
echo "📊 Compiled ${PYC_COUNT} files"

# Show bytecode locations
echo ""
echo "📁 Bytecode locations:"
find . -type d -name "__pycache__" | head -5 | while read dir; do
    echo "   ${dir}"
done

# Remove source files if requested
if [ "$REMOVE_SOURCE" = true ]; then
    echo ""
    echo -e "${YELLOW}🗑️  Removing source files...${NC}"
    find . -type f -name "*.py" \
        -not -path "./venv/*" \
        -not -path "./.venv/*" \
        -not -path "./__pycache__/*" \
        -not -path "./.git/*" \
        -delete
    
    echo -e "${GREEN}✅ Source files removed${NC}"
fi

echo ""
echo -e "${GREEN}✅ Bytecode compilation complete!${NC}"
echo ""
echo "💡 Tips:"
echo "   - Bytecode files are in __pycache__ directories"
echo "   - Set PYTHONDONTWRITEBYTECODE=1 to use pre-compiled bytecode"
echo "   - Set PYTHONOPTIMIZE=1 for optimized bytecode"
echo ""
