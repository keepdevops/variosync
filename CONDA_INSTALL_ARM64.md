# VARIOSYNC Conda Installation Guide for ARM64 (Apple Silicon)

This guide provides conda installation instructions for VARIOSYNC and its visualization libraries on ARM64 architecture (Apple Silicon Macs).

## Quick Start (nicegui-env)

```bash
# Activate existing environment
conda activate nicegui-env

# Install core dependencies
conda install -c conda-forge pandas numpy pyarrow matplotlib plotly duckdb redis-py -y
pip install nicegui>=1.4.0 boto3>=1.28.0 supabase>=2.0.0

# Install visualization libraries
conda install -c conda-forge altair -y || pip install altair
pip install highcharts-core pyecharts
```

Or use the environment file:
```bash
conda env update -f environment-arm64.yml
conda activate nicegui-env
```

## Prerequisites

1. **Install Miniconda or Anaconda for ARM64:**
   ```bash
   # Download from: https://docs.conda.io/en/latest/miniconda.html
   # Select: macOS ARM64 (Apple Silicon) installer
   ```

2. **Activate the nicegui-env conda environment:**
   ```bash
   conda activate nicegui-env
   ```
   
   If the environment doesn't exist, create it:
   ```bash
   conda create -n nicegui-env python=3.12
   conda activate nicegui-env
   ```

## Core Dependencies

### Install Core VARIOSYNC Dependencies

```bash
# Core Python packages
conda install -c conda-forge \
    requests \
    pandas \
    numpy \
    pyarrow \
    matplotlib \
    plotly

# Web framework
pip install nicegui>=1.4.0

# Storage and cloud
pip install boto3>=1.28.0
pip install supabase>=2.0.0

# Database
conda install -c conda-forge duckdb

# Caching
conda install -c conda-forge redis-py
```

## Visualization Libraries (Optional)

### Altair

```bash
# Install Altair via conda-forge (recommended for ARM64)
conda install -c conda-forge altair

# Or via pip if conda package not available
pip install altair
```

**Note:** Altair works well on ARM64 as it's a pure Python library with JavaScript rendering.

### Highcharts

```bash
# Highcharts Python wrapper (highcharts-core is the correct package name)
pip install highcharts-core

# Note: Highcharts uses JavaScript libraries loaded from CDN,
# so it works on all architectures including ARM64
```

### ECharts (via PyECharts)

```bash
# Install PyECharts (ECharts Python wrapper)
pip install pyecharts

# Optional: Install additional dependencies for better performance
pip install pyecharts[all]

# Note: PyECharts works on ARM64, but some dependencies may need pip
```

## Complete Installation Script

Save this as `install_conda_arm64.sh`:

```bash
#!/bin/bash
# VARIOSYNC Conda Installation for ARM64

set -e

echo "🚀 Installing VARIOSYNC with Conda (ARM64)"

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Miniconda or Anaconda first."
    exit 1
fi

# Create environment if it doesn't exist
if ! conda env list | grep -q "nicegui-env"; then
    echo "📦 Creating conda environment 'nicegui-env'..."
    conda create -n nicegui-env python=3.12 -y
fi

# Activate environment
echo "🔧 Activating environment..."
eval "$(conda shell.bash hook)"
conda activate nicegui-env

# Install core dependencies from conda-forge
echo "📥 Installing core dependencies..."
conda install -c conda-forge \
    requests \
    pandas \
    numpy \
    pyarrow \
    matplotlib \
    plotly \
    duckdb \
    redis-py \
    -y

# Install web framework and cloud libraries via pip
echo "📥 Installing web and cloud dependencies..."
pip install \
    nicegui>=1.4.0 \
    boto3>=1.28.0 \
    supabase>=2.0.0

# Install visualization libraries (optional)
echo "📊 Installing visualization libraries..."
echo "  - Altair..."
conda install -c conda-forge altair -y || pip install altair

echo "  - Highcharts..."
pip install highcharts-core

echo "  - ECharts..."
pip install pyecharts

echo ""
echo "✅ Installation complete!"
echo ""
echo "To activate the environment:"
echo "  conda activate nicegui-env"
echo ""
echo "To run VARIOSYNC:"
echo "  python3 run_nicegui.py"
```

Make it executable:
```bash
chmod +x install_conda_arm64.sh
./install_conda_arm64.sh
```

## Manual Step-by-Step Installation

### 1. Activate Environment

```bash
conda activate nicegui-env
```

If the environment doesn't exist:
```bash
conda create -n nicegui-env python=3.12
conda activate nicegui-env
```

### 2. Install Core Packages

```bash
# From conda-forge (preferred for ARM64 compatibility)
conda install -c conda-forge \
    requests \
    pandas>=2.0.0 \
    numpy>=1.24.0 \
    pyarrow>=12.0.0 \
    matplotlib>=3.7.0 \
    plotly>=5.17.0 \
    duckdb>=0.9.0 \
    redis-py>=5.0.0
```

### 3. Install Web Framework

```bash
pip install nicegui>=1.4.0
```

### 4. Install Cloud Storage Libraries

```bash
pip install boto3>=1.28.0 supabase>=2.0.0
```

### 5. Install Visualization Libraries

**Altair:**
```bash
conda install -c conda-forge altair
# Or if not available:
pip install altair
```

**Highcharts:**
```bash
pip install highcharts-core
```

**ECharts:**
```bash
pip install pyecharts
# Optional: with all features
pip install pyecharts[all]
```

## ARM64-Specific Notes

### Why Use Conda on ARM64?

1. **Better Binary Compatibility**: Conda-forge provides pre-compiled ARM64 binaries for many packages
2. **Native Performance**: Avoids Rosetta 2 emulation overhead
3. **Dependency Management**: Better handling of system-level dependencies

### Common Issues and Solutions

**Issue: Package not available for ARM64**
```bash
# Solution: Use pip as fallback
pip install <package-name>
```

**Issue: NumPy/SciPy compilation errors**
```bash
# Solution: Use conda-forge which has pre-built ARM64 binaries
conda install -c conda-forge numpy scipy
```

**Issue: Matplotlib backend issues**
```bash
# Solution: Install system dependencies via conda
conda install -c conda-forge matplotlib
```

**Issue: DuckDB installation problems**
```bash
# Solution: Use conda-forge version
conda install -c conda-forge duckdb
```

## Verify Installation

After installation, verify all packages:

```bash
conda activate nicegui-env

# Check Python version (should be 3.12)
python --version

# Verify core packages
python -c "import pandas; import numpy; import plotly; print('✅ Core packages OK')"

# Verify visualization libraries
python -c "
try:
    import altair
    print('✅ Altair: Available')
except ImportError:
    print('❌ Altair: Not installed')

try:
    import highcharts_core
    print('✅ Highcharts: Available')
except ImportError:
    print('❌ Highcharts: Not installed')

try:
    import pyecharts
    print('✅ ECharts: Available')
except ImportError:
    print('❌ ECharts: Not installed')
"

# Test VARIOSYNC import
python -c "import nicegui_app; print('✅ VARIOSYNC imports OK')"
```

## Running VARIOSYNC

```bash
# Activate environment
conda activate nicegui-env

# Run NiceGUI dashboard
python3 run_nicegui.py

# Or run CLI
python3 main.py --help
```

## Updating Packages

```bash
conda activate nicegui-env

# Update conda packages
conda update -c conda-forge --all

# Update pip packages
pip install --upgrade nicegui boto3 supabase altair highcharts-core pyecharts
```

## Environment Export

To share your environment:

```bash
# Export conda environment
conda env export > environment.yml

# Export pip packages
pip freeze > requirements-conda.txt
```

## Troubleshooting

### Reset Environment

If you encounter issues, recreate the environment:

```bash
conda deactivate
conda env remove -n nicegui-env
# Then follow installation steps again
```

### Check Architecture

Verify you're using ARM64:

```bash
python -c "import platform; print(platform.machine())"
# Should output: arm64
```

### Mixed Conda/Pip Issues

If you have conflicts between conda and pip packages:

```bash
# Use conda for core scientific packages
conda install -c conda-forge pandas numpy matplotlib

# Use pip for pure Python packages
pip install nicegui boto3 supabase
```

## Additional Resources

- [Conda-forge ARM64 packages](https://conda-forge.org/)
- [Apple Silicon Python compatibility](https://github.com/conda-forge/miniforge)
- [VARIOSYNC Documentation](./README.md)
